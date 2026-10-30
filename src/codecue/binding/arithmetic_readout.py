"""Fresh numeric arithmetic/readout calibration, with grouped sign relatives.

All eight forms for a numeric tuple have the same answer. Folded intermediate
pairs, rather than numeric renderings, define the split groups: the nonzero-op
forms therefore have distinct prompts in training and numeric development.
The two zero-op controls intentionally repeat answer literals. This is numeric
calibration on shared forms, never a structural generalization experiment.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from itertools import permutations
import json
from pathlib import Path

from .datasets import digest
from .interpreter import execute, python_oracle
from .program_diagnostics import oracle_source
from .published_benchmarks import immutable, sha

ROLE = 'arithmetic_readout_feasibility_discovery_v1'
FORMS = {
    'literal_output': 0,
    'stored_output': 0,
    'literal_one': 1,
    'bound_one': 1,
    'stored_result_one': 1,
    'literal_three': 3,
    'bound_three': 3,
    'stored_intermediates_three': 3,
}
SIGN_STRATA = ((-1, -1, -1), (-1, -1, 1), (-1, 1, -1),
               (1, -1, 1), (1, 1, -1), (1, 1, 1))


def _sign(value):
    return (value > 0) - (value < 0)


def _stratum(r, s):
    return (_sign(r), _sign(s), _sign(r - s))


def _mirror(values):
    a, b, c, d = values
    return b, a, d, c


def _options(config):
    count = config.get('tuples_per_stratum', config.get('numeric_per_stratum', 64))
    if ('tuples_per_stratum' in config and 'numeric_per_stratum' in config
            and config['tuples_per_stratum'] != config['numeric_per_stratum']):
        raise ValueError('conflicting per-stratum numeric counts')
    if type(count) is not int or count < 2 or count % 2:
        raise ValueError('per-stratum numeric count must be positive, even and at least two')
    seed = config.get('seed', 20261028)
    maximum = config.get('operand_max', 17)
    if type(seed) is not int:
        raise ValueError('integer generation seed required')
    if type(maximum) is not int or not 4 <= maximum <= 64:
        raise ValueError('operand_max must be an integer in [4,64]')
    excluded = set()
    for values in config.get('excluded_numeric_values', []):
        if (not isinstance(values, (list, tuple)) or len(values) != 4
                or any(type(v) is not int or not 1 <= v <= 64 for v in values)
                or len(set(values)) != 4):
            raise ValueError('excluded numeric values must be distinct positive integer quadruples')
        excluded.add(tuple(values))
    return count, seed, maximum, excluded


def _sources(values):
    a, b, c, d = values
    r, s = a - b, c - d
    y = r - s
    # Parentheses make negative intermediate constants explicit in the prompt.
    one = f'({r}) - ({s})'
    three = f'({a} - {b}) - ({c} - {d})'
    return {
        'literal_output': str(y),
        'stored_output': f'result = {y}\nresult',
        'literal_one': one,
        'bound_one': f'left = {r}\nright = {s}\nleft - right',
        'stored_result_one': f'result = {one}\nresult',
        'literal_three': three,
        'bound_three': f'a = {a}\nb = {b}\nc = {c}\nd = {d}\n(a - b) - (c - d)',
        'stored_intermediates_three': f'left = {a} - {b}\nright = {c} - {d}\nleft - right',
    }


def _identities(values, form, source):
    a, b, c, d = values
    folded = (a - b, c - d)
    canonical = min(folded, tuple(-v for v in folded))
    base = 'arithmetic-tuple:' + digest(list(values))[:24]
    group = 'arithmetic-pair:' + digest(list(canonical))[:24]
    row_id = 'arithmetic-readout:' + digest([ROLE, list(values), form, source])[:24]
    return row_id, base, group


def make_rows(config):
    """Select fresh folded pairs and one representative tuple without model scores."""
    count, seed, maximum, excluded = _options(config)
    representatives = {}
    for values in permutations(range(1, maximum + 1), 4):
        a, b, c, d = values
        r, s = a - b, c - d
        if r == s or abs(r - s) > 64:
            continue
        folded = (r, s)
        if folded != min(folded, (-r, -s)):
            continue
        if values in excluded or _mirror(values) in excluded:
            continue
        rank = digest([seed, 'numeric_representative', list(values)])
        if folded not in representatives or rank < representatives[folded][0]:
            representatives[folded] = (rank, values)
    buckets = defaultdict(list)
    for folded in representatives:
        buckets[_stratum(*folded)].append(folded)
    rows = []
    # Each canonical bucket has its sign-reversed counterpart. One folded pair
    # contributes one tuple to each stratum and keeps both in the same split.
    for stratum in SIGN_STRATA[:3]:
        candidates = sorted(buckets[stratum], key=lambda p: digest([seed, 'folded_pair', list(p)]))
        if len(candidates) < count:
            raise ValueError(f'insufficient unique fresh folded pairs in sign stratum {stratum}: '
                             f'{len(candidates)} available, {count} required')
        for index, folded in enumerate(candidates[:count]):
            canonical_values = representatives[folded][1]
            split = 'train' if index < count // 2 else 'development'
            for values in (canonical_values, _mirror(canonical_values)):
                a, b, c, d = values
                r, s = a - b, c - d
                for form, source in _sources(values).items():
                    validated = oracle_source(source)
                    truth = execute(validated)
                    row_id, base, group = _identities(values, form, source)
                    rows.append(dict(id=row_id, base_id=base, tuple_id=base,
                        template_id='arithmetic-readout-form:' + form,
                        paired_group_id=group, split=split, evaluation_role=ROLE,
                        family='arithmetic_readout', form=form, operation_count=FORMS[form],
                        seed=seed, operand_max=maximum, generation_config_hash=digest(config),
                        source=source, oracle_source=validated,
                        expected_answer=truth['expected_answer'], execution_trace=truth['execution_trace'],
                        numeric_values=list(values), r=r, s=s, sign_stratum=list(_stratum(r, s))))
    return rows


def validate_rows(rows, generation=None, independent=False):
    """Validate semantic identities, complete relatives, sign balance and split access."""
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('missing or duplicate arithmetic-readout row identities')
    groups = defaultdict(list)
    bases = defaultdict(list)
    folded_splits = defaultdict(set)
    prompts = defaultdict(list)
    for row in rows:
        if row['evaluation_role'] != ROLE or row['split'] not in ('train', 'development'):
            raise ValueError('arithmetic readout is numeric calibration/development only; final outcomes are sealed')
        form = row['form']
        if form not in FORMS:
            raise ValueError('unknown arithmetic-readout form')
        values = row['numeric_values']
        maximum = row.get('operand_max', 17)
        if (type(maximum) is not int or not 4 <= maximum <= 64 or len(values) != 4
                or len(set(values)) != 4 or any(type(v) is not int or not 1 <= v <= maximum for v in values)):
            raise ValueError('invalid distinct positive numeric tuple or operand range')
        a, b, c, d = values
        r, s = a - b, c - d
        if r == 0 or s == 0 or r == s or abs(r - s) > 64:
            raise ValueError('nonzero bounded intermediate and output values required')
        source = _sources(values)[form]
        validated = oracle_source(source)
        truth = execute(validated)
        if (row['source'] != source or row.get('oracle_source') != validated
                or row['expected_answer'] != r - s or truth['expected_answer'] != r - s
                or row['execution_trace'] != truth['execution_trace']):
            raise ValueError('arithmetic-readout source, answer or execution trace differs')
        operations = sum(isinstance(node, ast.BinOp) for node in ast.walk(ast.parse(source)))
        if row['operation_count'] != FORMS[form] or operations != FORMS[form]:
            raise ValueError('arithmetic operation count differs')
        if row['r'] != r or row['s'] != s or row['sign_stratum'] != list(_stratum(r, s)):
            raise ValueError('intermediate values or sign stratum differs')
        row_id, base, group = _identities(values, form, source)
        if (row['id'] != row_id or row['base_id'] != base or row.get('tuple_id') != base
                or row['paired_group_id'] != group or row['template_id'] != 'arithmetic-readout-form:' + form):
            raise ValueError('arithmetic-readout stable identity differs')
        groups[group].append(row)
        bases[base].append(row)
        folded_splits[min((r, s), (-r, -s))].add(row['split'])
        if FORMS[form]:
            prompts[form, ast.dump(ast.parse(source), include_attributes=False)].append(row)
    if any(len(splits) != 1 for splits in folded_splits.values()):
        raise ValueError('folded sign-pair relatives cross train/development splits')
    for group in groups.values():
        tuples = {tuple(row['numeric_values']) for row in group}
        if (len(group) != 2 * len(FORMS) or len(tuples) != 2
                or _mirror(next(iter(tuples))) not in tuples or len({r['split'] for r in group}) != 1):
            raise ValueError('incomplete or split sign-reversal relatives')
    for group in bases.values():
        if len(group) != len(FORMS) or {r['form'] for r in group} != set(FORMS):
            raise ValueError('incomplete arithmetic-readout forms')
    if any(len(group) != 1 for group in prompts.values()):
        raise ValueError('nonzero-operation prompts duplicate within or across splits')
    counts = Counter((tuple(r['sign_stratum']), r['split'], r['form']) for r in rows)
    required = {(stratum, split, form) for stratum in SIGN_STRATA
                for split in ('train', 'development') for form in FORMS}
    if set(counts) != required or len(set(counts.values())) != 1:
        raise ValueError('sign-stratum, form and numeric split balance differs')
    if generation is not None and rows != make_rows(generation):
        raise ValueError('arithmetic-readout dataset differs from registered generation or exclusions')
    if independent:
        for start in range(0, len(rows), 128):
            batch = rows[start:start + 128]
            observed = python_oracle([r['oracle_source'] for r in batch])
            for row, truth in zip(batch, observed):
                if (row['expected_answer'] != truth['answer']
                        or [p['values'] for p in row['execution_trace']] != truth['trace']):
                    raise ValueError('independent Python arithmetic-readout trace differs')
    return rows


def build(config):
    """Write immutable, independently audited discovery/calibration metadata."""
    generation = config['generation']
    rows = make_rows(generation)
    validate_rows(rows, independent=True)
    count, seed, maximum, excluded = _options(generation)
    path = Path(config['dataset'])
    content = ''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows).encode()
    immutable(path, content)
    duplicate_sources = {}
    cross_split_sources = {}
    unique_prompt_cells = {}
    for form in FORMS:
        grouped = defaultdict(set)
        selected = [r for r in rows if r['form'] == form]
        for row in selected:
            grouped[ast.dump(ast.parse(row['source']), include_attributes=False)].add(row['split'])
        duplicate_sources[form] = len(selected) - len(grouped)
        cross_split_sources[form] = sum(len(splits) > 1 for splits in grouped.values())
        for stratum in SIGN_STRATA:
            for split in ('train', 'development'):
                values = {ast.dump(ast.parse(r['source']), include_attributes=False) for r in selected
                          if tuple(r['sign_stratum']) == stratum and r['split'] == split}
                unique_prompt_cells[form + ':' + ','.join(map(str, stratum)) + ':' + split] = len(values)
    manifest = dict(schema_version=1, status='validated', sha256=sha(path), rows=len(rows),
        evaluation_role=ROLE, generation=generation, generation_config_hash=digest(generation),
        seed=seed, operand_max=maximum, tuples_per_stratum=count, numeric_tuples=len(rows) // len(FORMS),
        folded_sign_pairs=len(rows) // (2 * len(FORMS)),
        counts=dict(Counter(r['form'] for r in rows)), split_counts=dict(Counter(r['split'] for r in rows)),
        sign_stratum_counts={','.join(map(str, key)): value for key, value in
                            Counter(tuple(r['sign_stratum']) for r in rows).items()},
        excluded_numeric_tuple_count=len(excluded), excluded_numeric_values_sha256=digest(sorted(excluded)),
        independent_python_traces_passed=True, nonzero_prompts_unique_and_split_disjoint=True,
        minimum_nonzero_cell_unique_prompts=min(value for key, value in unique_prompt_cells.items()
                                               if FORMS[key.split(':')[0]]),
        unique_prompt_counts_by_form_sign_split=unique_prompt_cells,
        duplicate_source_counts=duplicate_sources, cross_split_shared_source_counts=cross_split_sources,
        zero_operation_controls_eligible_for_gate=False, generated_holdouts_opened=False,
        limitation='Fresh numeric calibration shares eight fixed forms across training/development; '
                   'no structural generalization claim. Operand range is explicitly expanded from the prior '
                   'single-digit bank. Zero-operation answer controls intentionally repeat prompts and are '
                   'excluded from qualification gates.')
    immutable(path.with_suffix('.manifest.json'), (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode())
    return manifest
