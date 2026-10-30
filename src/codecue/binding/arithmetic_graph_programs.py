"""Discovery sources with two-input arithmetic and versioned def-use labels.

All numeric, lexical and query relatives stay in their canonical structural
family. This is source preparation, never an opening of sealed evaluation data.
"""
from __future__ import annotations

import ast
from collections import Counter
from functools import lru_cache
from itertools import permutations
import json
import random

from .datasets import digest
from .interpreter import execute
from .programs import rename
from .relationship_capture import _publish, _sha

ROLE = 'discovery_arithmetic_graph_sources_v1'
SEEDS = (1103, 1201, 1301)
FAMILIES = 48
ROWS = FAMILIES * len(SEEDS) * 4 * 2 * 4
SLOTS = {f'v{i}': i for i in range(4)}
MAPS = (SLOTS, dict(zip(SLOTS, ('amber', 'birch', 'cedar', 'dune'))))


def oracle(source, stop=7):
    """Independent AST evaluator; parents refer to definitions at READ time."""
    tree = ast.parse(source)
    if len(tree.body) != 9:
        raise ValueError('eight assignments and one query required')
    values, definitions, versions, writes = {}, {}, Counter(), []
    for index, node in enumerate(tree.body[:stop+1]):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            raise ValueError('simple assignments required')
        name = node.targets[0].id
        def value(expr):
            if isinstance(expr, ast.Name):
                return values[expr.id]
            if isinstance(expr, ast.Constant) and type(expr.value) is int:
                return expr.value
            if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):
                return -value(expr.operand)
            if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Sub)):
                a, b = value(expr.left), value(expr.right)
                return a+b if isinstance(expr.op, ast.Add) else a-b
            raise ValueError('integer/name/add/subtract only')
        parents = [definitions[part.id] for part in ast.walk(node.value) if isinstance(part, ast.Name)]
        result = value(node.value)  # Evaluate BEFORE updating the destination.
        versions[name] += 1
        values[name], definitions[name] = result, index
        writes.append(dict(statement=index, slot=SLOTS[name], version=versions[name],
                           parents=parents, value=result))
    return dict(values=[values[name] for name in SLOTS],
                definitions=[definitions[name] for name in SLOTS],
                versions=[versions[name] for name in SLOTS], writes=writes,
                parents=[parent for write in writes[4:] for parent in write['parents']])


def canonical_key(updates):
    """Quotient slot names; retain ordered operators, operands and write order."""
    return min(tuple((p[d], p[a], p[b], op) for d, a, b, op in updates)
               for p in permutations(range(4)))


@lru_cache(maxsize=1)
def structures():
    rng = random.Random(291029)
    banks, seen = {0: [], 1: [], 2: []}, set()
    for _ in range(50000):
        updates = []
        for _ in range(4):
            a, b = rng.sample(range(4), 2)
            updates.append((rng.randrange(4), a, b, rng.choice(('+', '-'))))
        key = canonical_key(updates)
        kind = 0 if all(u[3] == '+' for u in updates) else 1 if all(u[3] == '-' for u in updates) else 2
        if key in seen or len(banks[kind]) == 16:
            continue
        seen.add(key)
        banks[kind].append(tuple(updates))
        if all(len(bank) == 16 for bank in banks.values()):
            break
    if any(len(bank) != 16 for bank in banks.values()):
        raise ValueError('finite source search exhausted')
    return tuple((kind, j, updates) for kind, bank in banks.items() for j, updates in enumerate(bank))


@lru_cache(maxsize=1)
def make_rows():
    rows = []
    seen_roots = set()
    for kind, family_index, updates in structures():
        group = 'arithmetic-graph:' + digest(canonical_key(updates))[:24]
        split = 'train' if family_index < 12 else 'development'
        for seed in SEEDS:
            for draw in range(4):
                for attempt in range(10000):
                    rng = random.Random(digest([group, seed, draw, attempt]))
                    roots = [rng.randrange(-6, 7) for _ in range(4)]
                    if draw == 1:
                        roots[1] = roots[0]  # Equal values, distinct provenance.
                    if draw == 2:
                        roots[2] = roots[0] + roots[1]
                    if max(map(abs, roots)) <= 6 and tuple(roots) not in seen_roots:
                        seen_roots.add(tuple(roots))
                        break
                else:
                    raise ValueError('finite initial-state uniqueness search exhausted')
                body = '\n'.join([*(f'v{i} = {v}' for i, v in enumerate(roots)),
                    *(f'v{d} = v{a} {op} v{b}' for d, a, b, op in updates)])
                for lexical, mapping0 in enumerate(MAPS):
                    mapping = {k: (k if lexical == 0 else mapping0[k]) for k in SLOTS}
                    for query in range(4):
                        canonical = body + f'\nv{query}'
                        surface = rename(canonical, mapping)
                        identity = 'arithmetic-case:' + digest([group, seed, draw, lexical, query])[:24]
                        truth = oracle(canonical)
                        if max(map(abs, truth['values'])) > 96:
                            raise ValueError('declared categorical numeric domain exceeded')
                        rows.append(dict(id=identity, evaluation_role=ROLE, split=split,
                            template_id=group, component_id=group, cluster_id=group,
                            base_id=digest([group, seed, draw]), paired_group_id=group,
                            family='two_input_arithmetic', operation_family=('addition', 'subtraction', 'mixed')[kind],
                            condition='neutral', control_kind='primary', source_form='arithmetic',
                            source=surface, canonical_source=canonical, rename_map=mapping,
                            variable_slots=SLOTS, lexical_realization=lexical, query_slot=query,
                            query_role=f'v{query}', query_count=1, numeric_seed=seed,
                            numeric_draw=draw, numeric_stratum=('uniform', 'equal_roots', 'additive_roots', 'uniform')[draw],
                            body_id=digest(body), surface_body_id=digest(surface.rsplit('\n', 1)[0]),
                            format_pair_id=digest([group, seed, draw, lexical, query]),
                            initial_state_id=digest(roots), cohorts=['arithmetic_graph'],
                            numeric_rejection_attempts=attempt,
                            expected_answer=truth['values'][query], oracle=truth))
    return rows


def validate(rows, independent=True):
    if rows != make_rows() or len(rows) != ROWS or len({r['id'] for r in rows}) != ROWS:
        raise ValueError('complete deterministic arithmetic cohort required')
    families, bodies, keys = {}, {}, {'train': set(), 'development': set()}
    for row in rows:
        group = row['component_id']
        if group in families and families[group] != row['split']:
            raise ValueError('structural family leaked across splits')
        families[group] = row['split']
        body = row['canonical_source'].rsplit('\n', 1)[0]
        if body in bodies and bodies[body] != row['split']:
            raise ValueError('program body leaked across splits')
        bodies[body] = row['split']
        updates = []
        for node in ast.parse(body).body[4:]:
            updates.append((SLOTS[node.targets[0].id], SLOTS[node.value.left.id],
                            SLOTS[node.value.right.id], '+' if isinstance(node.value.op, ast.Add) else '-'))
        keys[row['split']].add(canonical_key(updates))
        if oracle(row['canonical_source']) != row['oracle']:
            raise ValueError('versioned source oracle differs')
        if independent:
            scope = {}
            exec(compile(body, '<generated-arithmetic>', 'exec'), {'__builtins__': {}}, scope)
            if [scope[k] for k in SLOTS] != row['oracle']['values']:
                raise ValueError('ordinary Python and AST oracle disagree')
            if execute(row['source'])['expected_answer'] != row['expected_answer']:
                raise ValueError('existing interpreter/surface truth differs')
    if keys['train'] & keys['development']:
        raise ValueError('alpha-equivalent structural family leaked')
    return dict(rows=len(rows), components=dict(Counter(families.values())),
                split_rows=dict(Counter(r['split'] for r in rows)),
                canonical_family_overlap=0, exact_body_overlap=0,
                unique_numeric_bodies=len(bodies), independent_python_passed=independent)


def build(path):
    from pathlib import Path
    rows = make_rows()
    review = validate(rows)
    payload = ''.join(json.dumps(r, sort_keys=True)+'\n' for r in rows).encode()
    _publish(path, payload)
    manifest = dict(status='complete', evaluation_role=ROLE, role=ROLE,
                    sha256=_sha(path), generated_holdouts_opened=False, **review,
                    limitations=[
                        'Adaptive discovery; ordered execution skeletons supplied, not arbitrary node discovery.',
                        'Structural grouping quotients slot renaming, not all commuting schedules or semantic equivalence.',
                        'Numeric draws, lexical forms and query twins are relatives, not replications.',
                        'Def-use labels are syntactic provenance, not functional causal influence.',
                        'Only fixed checkpoints and exploratory TRAIN/DEV data; sealed outcomes remain unopened.'])
    _publish(Path(path).with_suffix('.manifest.json'), (json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode())
    return manifest
