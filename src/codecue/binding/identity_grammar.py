"""Exact, source-free copy-grammar decoding of saved identity score tables.

Inputs are the four write and four parent 16-class tables only.  A class is
``4 * owner + version - 1``.  Four known roots start at version 1; a read uses
the version before its event writes.  The version-4 cap belongs to this fixed
codebook.  No source, target, profile, family or per-case grammar is accepted.

Every objective is an exact sum of the supplied floating-point numbers.  The
owner-marginal view sums the four version scores exactly, without rounding a
new marginal table to float.  Numerator/exponent pairs mean ``n * 2**e``.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product

import numpy as np

MAX_ROWS = 5760
EVIDENCE = ("joint", "owner_marginal")
TIE_BREAK = "lexicographic interleaved owners (d0,p0,...,d3,p3); base16 digit=4*d+p"


def _boolean(value):
    if type(value) is not bool:
        raise ValueError("allow_self must be a boolean")


def _scores(write_joint, parent_joint, evidence):
    if evidence not in EVIDENCE:
        raise ValueError("evidence must be joint or owner_marginal")
    values = []
    for supplied in (write_joint, parent_joint):
        value = np.asarray(supplied)
        if (np.ma.isMaskedArray(supplied) or value.ndim != 3 or value.shape[1:] != (4,16)
                or not 0 <= len(value) <= MAX_ROWS or value.dtype.kind != "f"
                or value.dtype.itemsize > 8):
            raise ValueError("bounded N by 4 by 16 floating score tables required")
        values.append(np.asarray(value, dtype=np.float64))
    if values[0].shape != values[1].shape:
        raise ValueError("write and parent score tables must align")
    return values[0], values[1]


def _ids(write_ids, parent_ids, *, owners=False):
    values = []
    for supplied in (write_ids, parent_ids):
        value = np.asarray(supplied)
        if (np.ma.isMaskedArray(supplied) or value.ndim != 2 or value.shape[1:] != (4,)
                or not 0 <= len(value) <= MAX_ROWS or value.dtype.kind not in "iu"
                or (value.dtype.kind == "u" and value.size and value.max() > np.iinfo(np.int64).max)):
            raise ValueError("bounded aligned N by 4 integer owner paths" if owners
                             else "bounded aligned N by 4 integer identity paths")
        values.append(np.asarray(value, dtype=np.int64))
    if values[0].shape != values[1].shape:
        raise ValueError("write and parent paths must align")
    return values[0], values[1]


def _key(numerator, exponent):
    numerator = int(numerator)
    if numerator == 0:
        return "0", 0
    shift = (abs(numerator) & -abs(numerator)).bit_length() - 1
    return str(numerator >> shift), int(exponent) + shift


def _integers(rows, evidence):
    """Exact dyadics in a shared per-row unit; object integers cannot overflow."""
    result = np.empty(rows.shape, dtype=object)
    exponents = []
    for row_index, row in enumerate(rows):
        ratios = [float(value).as_integer_ratio() for value in row]
        powers = [-(denominator.bit_length()-1) for _, denominator in ratios]
        exponent = min(powers)
        result[row_index] = [numerator << (power-exponent)
                             for (numerator,_),power in zip(ratios,powers)]
        exponents.append(exponent)
    write, parent = result[:,:64].reshape(-1,4,16), result[:,64:].reshape(-1,4,16)
    if evidence == "owner_marginal":
        write = np.repeat(write.reshape(-1,4,4,4).sum(axis=3), 4, axis=2)
        parent = np.repeat(parent.reshape(-1,4,4,4).sum(axis=3), 4, axis=2)
    return write, parent, exponents


@lru_cache(maxsize=2)
def _topology(allow_self):
    levels = [tuple(state for state in product(range(1,5), repeat=4)
                    if sum(state) == 4+depth) for depth in range(5)]
    stages = []
    for depth in range(4):
        destinations = {state:index for index,state in enumerate(levels[depth+1])}
        incoming = [[] for _ in levels[depth+1]]
        for previous,state in enumerate(levels[depth]):
            for destination in range(4):
                if state[destination] == 4:
                    continue
                updated = list(state); updated[destination] += 1
                for parent in range(4):
                    if not allow_self and destination == parent:
                        continue
                    incoming[destinations[tuple(updated)]].append((previous,
                        4*destination+state[destination],
                        4*parent+state[parent]-1, 4*destination+parent))
        stages.append(tuple(tuple(edges) for edges in incoming))
    return tuple(stages)


def _batch(write, parent, allow_self):
    n = len(write)
    scores = np.zeros((n,1), dtype=object)
    codes = np.zeros((n,1), dtype=np.int32)
    for event,stage in enumerate(_topology(allow_self)):
        next_scores = np.empty((n,len(stage)), dtype=object)
        next_codes = np.empty((n,len(stage)), dtype=np.int32)
        for state,edges in enumerate(stage):
            candidates = np.stack([scores[:,previous] + write[:,event,write_id]
                                   + parent[:,event,parent_id]
                                   for previous,write_id,parent_id,_ in edges], axis=1)
            paths = np.stack([codes[:,previous]*16 + digit
                              for previous,_,_,digit in edges], axis=1)
            best = candidates.max(axis=1)
            next_scores[:,state] = best
            next_codes[:,state] = np.where(candidates == best[:,None], paths, 65536).min(axis=1)
        scores, codes = next_scores, next_codes
    best = scores.max(axis=1)
    paths = np.where(scores == best[:,None], codes, 65536).min(axis=1)
    return best, paths.astype(np.int32)


def owners_to_identities(write_owners, parent_owners):
    """Count known owner paths; no source parser or version target is involved.

    Return N-by-4 identities, a valid-row mask, and per-event version-cap flags.
    Any missing/out-of-domain owner or version-cap excess makes the whole row
    missing.  Self-copy reads its preceding version and then defines the next.
    """
    write, parent = _ids(write_owners, parent_owners, owners=True)
    n = len(write); in_domain = ((write>=0)&(write<4)&(parent>=0)&(parent<4)).all(axis=1)
    write_ids = np.full((n,4), -1, dtype=np.int16)
    parent_ids = np.full_like(write_ids, -1)
    counts = np.ones((n,4), dtype=np.int16); cap = np.zeros((n,4), dtype=bool)
    rows = np.flatnonzero(in_domain)
    for event in range(4):
        d, p = write[rows,event], parent[rows,event]
        parent_ids[rows,event] = 4*p + counts[rows,p]-1
        cap[rows,event] = counts[rows,d] >= 4
        write_ids[rows,event] = 4*d + counts[rows,d]
        counts[rows,d] += 1
    valid = in_domain & ~cap.any(axis=1)
    write_ids[~valid] = -1; parent_ids[~valid] = -1
    return dict(write_ids=write_ids, parent_ids=parent_ids, valid=valid,
                version_cap_exceeded=cap, missing_or_invalid_owner=~in_domain)


def validate_paths(write_ids, parent_ids, *, allow_self=True):
    """Check identities against their predicted owner history, never true source.

    A wrong version still increments that predicted write owner.  An unknown
    write owner makes later history undefined instead of inventing an owner.
    All flag tables have shape N-by-4; ``lawful`` requires no flagged event.
    """
    _boolean(allow_self)
    write, parent = _ids(write_ids, parent_ids)
    n = len(write); known_write = (write>=0)&(write<16); known_parent = (parent>=0)&(parent<16)
    flags = {name:np.zeros((n,4), dtype=bool) for name in (
        "missing_id", "invalid_id", "unknown_owner_history", "parent_version_mismatch",
        "write_version_mismatch", "version_cap_exceeded", "self_copy_forbidden")}
    flags["missing_id"] = (write == -1)|(parent == -1)
    flags["invalid_id"] = ((~known_write)&(write != -1))|((~known_parent)&(parent != -1))
    counts = np.ones((n,4), dtype=np.int16); history = np.ones(n, dtype=bool)
    for event in range(4):
        flags["unknown_owner_history"][:,event] = ~history
        rows = np.flatnonzero(history & known_parent[:,event])
        p = parent[rows,event]//4
        flags["parent_version_mismatch"][rows,event] = parent[rows,event]%4+1 != counts[rows,p]
        rows = np.flatnonzero(history & known_write[:,event])
        d = write[rows,event]//4
        flags["write_version_mismatch"][rows,event] = write[rows,event]%4+1 != counts[rows,d]+1
        flags["version_cap_exceeded"][rows,event] = counts[rows,d] >= 4
        if not allow_self:
            rows_self = np.flatnonzero(known_write[:,event] & known_parent[:,event])
            flags["self_copy_forbidden"][rows_self,event] = write[rows_self,event]//4 == parent[rows_self,event]//4
        counts[rows,d] += 1
        history &= known_write[:,event]
    violations = np.logical_or.reduce(list(flags.values()))
    lawful = ~violations.any(axis=1)
    first = np.full(n, -1, dtype=np.int16)
    bad = np.flatnonzero(~lawful)
    first[bad] = np.argmax(violations[bad], axis=1)
    return dict(lawful=lawful, complete=(known_write&known_parent).all(axis=1),
                flags=flags, first_violation=first)


def score_paths(write_joint, parent_joint, write_ids, parent_ids, *, evidence="joint"):
    """Exact objective for supplied identities, whether lawful or unlawful."""
    write, parent = _scores(write_joint,parent_joint,evidence)
    wi, pi = _ids(write_ids,parent_ids)
    if len(wi) != len(write):
        raise ValueError("score rows and identity paths must align")
    finite = np.isfinite(write).all(axis=(1,2)) & np.isfinite(parent).all(axis=(1,2))
    valid = finite & ((wi>=0)&(wi<16)&(pi>=0)&(pi<16)).all(axis=1)
    numerators = [None]*len(write); exponents = [None]*len(write)
    rows = np.flatnonzero(valid)
    for first in range(0,len(rows),256):
        selected = rows[first:first+256]
        w, p, scales = _integers(np.concatenate((write[selected].reshape(-1,64),
                                                parent[selected].reshape(-1,64)),axis=1),evidence)
        local = np.arange(len(selected))[:,None]; events = np.arange(4)
        totals = (w[local,events,wi[selected]].sum(axis=1)
                  + p[local,events,pi[selected]].sum(axis=1))
        for index,row in enumerate(selected):
            numerators[row], exponents[row] = _key(totals[index],scales[index])
    return dict(finite=finite, valid=valid, score_numerators=tuple(numerators),
                score_exponents=tuple(exponents))


def decode(write_joint, parent_joint, *, evidence="joint", allow_self=True, batch_size=256):
    """Maximize eight exact evidence terms over the fixed copy grammar.

    Lexicographic ties compare event-interleaved (write owner, read owner)
    pairs, encoded by four base16 digits.  A lower prefix score is never tied
    through floating-point cancellation: all DP comparisons use exact integer
    sums.  Identical finite score rows share computation, with no metadata key.
    Every nonfinite cell makes its entire case missing; no candidate is pruned.
    """
    _boolean(allow_self)
    if type(batch_size) is not int or not 1 <= batch_size <= MAX_ROWS:
        raise ValueError("positive bounded batch_size required")
    write, parent = _scores(write_joint,parent_joint,evidence)
    n = len(write)
    finite = np.isfinite(write).all(axis=(1,2)) & np.isfinite(parent).all(axis=(1,2))
    path_codes = np.full(n, -1, dtype=np.int32)
    pairs = {prefix:([None]*n,[None]*n) for prefix in ("score","free_upper_bound","projection_penalty")}
    selected = np.flatnonzero(finite)
    rows = np.concatenate((write[selected].reshape(-1,64),parent[selected].reshape(-1,64)), axis=1)
    unique, inverse = np.unique(rows,axis=0,return_inverse=True)
    unique_codes = np.empty(len(unique),dtype=np.int32)
    unique_free_write = np.empty((len(unique),4),dtype=np.int16)
    unique_free_parent = np.empty_like(unique_free_write)
    keys = {prefix:[] for prefix in pairs}
    for first in range(0,len(unique),batch_size):
        w, p, scales = _integers(unique[first:first+batch_size],evidence)
        best, codes = _batch(w,p,allow_self)
        upper = w.max(axis=2).sum(axis=1) + p.max(axis=2).sum(axis=1)
        unique_codes[first:first+len(codes)] = codes
        unique_free_write[first:first+len(codes)] = w.argmax(axis=2)
        unique_free_parent[first:first+len(codes)] = p.argmax(axis=2)
        for row in range(len(codes)):
            if upper[row] < best[row]:
                raise AssertionError("constrained objective exceeded the free upper bound")
            for prefix,value in (("score",best[row]),("free_upper_bound",upper[row]),
                                 ("projection_penalty",upper[row]-best[row])):
                keys[prefix].append(_key(value,scales[row]))
    path_codes[selected] = unique_codes[inverse]
    free_write = np.full((n,4),-1,dtype=np.int16)
    free_parent = np.full_like(free_write,-1)
    free_write[selected] = unique_free_write[inverse]
    free_parent[selected] = unique_free_parent[inverse]
    for row, which in zip(selected,inverse):
        for prefix in pairs:
            pairs[prefix][0][row], pairs[prefix][1][row] = keys[prefix][which]
    digits = np.full((n,4), -1,dtype=np.int16)
    for event in range(4):
        digits[selected,event] = (path_codes[selected] >> (4*(3-event))) & 15
    owners = owners_to_identities(np.where(digits>=0,digits//4,-1),np.where(digits>=0,digits%4,-1))
    valid = finite & owners["valid"]
    if not np.array_equal(valid,finite) or not validate_paths(
            owners["write_ids"][valid],owners["parent_ids"][valid],allow_self=allow_self)["lawful"].all():
        raise AssertionError("decoder produced an invalid grammar path")
    result = dict(write_ids=owners["write_ids"],parent_ids=owners["parent_ids"],finite=finite,valid=valid,
                  free_write_ids=free_write,free_parent_ids=free_parent,
                  path_code=path_codes,evidence=evidence,allow_self=allow_self,tie_break=TIE_BREAK,
                  unique_finite_rows=len(unique))
    for prefix,(numerators,exponents) in pairs.items():
        result[prefix+"_numerators"] = tuple(numerators)
        result[prefix+"_exponents"] = tuple(exponents)
    return result
