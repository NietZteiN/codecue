"""More diverse arithmetic discovery sources and causal token-span targets."""
import ast
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
import random
from copy import deepcopy

from . import arithmetic_graph_programs as old
from .datasets import digest
from .interpreter import execute
from .programs import rename
from . import relationship_capture as base

ROLE = 'discovery_arithmetic_local_sources_v1'
SEEDS = (1103, 1201, 1301)
MAX_POINTS = 23  # four roots, six * (two uses + definition end), answer
INSTRUCTIONS = (
    base.INSTRUCTION,
    'Execute the assignments in order and report the integer printed by the last line. Return only that signed integer.',
    'Track the current value of each variable, including overwrites. What integer does print output? Reply with only the signed integer.',
)
LEXICAL_MAPS = ({name: name for name in old.SLOTS}, dict(zip(old.SLOTS, ('amber', 'birch', 'cedar', 'dune'))))


@lru_cache(maxsize=1)
def structures():
    excluded = {old.canonical_key(updates) for _, _, updates in old.structures()}
    seen = set(excluded)
    result = []
    rng = random.Random(301030)
    for depth in (2, 4, 6):
        for kind in ('addition', 'subtraction', 'mixed'):
            bank = []
            for _ in range(200000):
                operations = ['+' if kind == 'addition' else '-' for _ in range(depth)]
                if kind == 'mixed':
                    operations = [rng.choice(('+', '-')) for _ in range(depth)]
                    if len(set(operations)) < 2:
                        continue
                updates = []
                for op in operations:
                    a, b = rng.sample(range(4), 2)
                    updates.append((rng.randrange(4), a, b, op))
                key = old.canonical_key(updates)
                if key in seen:
                    continue
                seen.add(key)
                bank.append(tuple(updates))
                if len(bank) == 32:
                    break
            if len(bank) != 32:
                raise ValueError('finite canonical source search exhausted')
            for index, updates in enumerate(bank):
                result.append((depth, kind, 'train' if index < 24 else 'development', updates))
    # All six one-update structures modulo variable renaming, outside probe fits.
    seen_calibration = set()
    for op in ('+', '-'):
        for destination in range(3):
            updates = ((destination, 0, 1, op),)
            key = old.canonical_key(updates)
            if key in seen_calibration:
                raise ValueError('calibration structures should be unique')
            seen_calibration.add(key)
            result.append((1, 'addition' if op == '+' else 'subtraction', 'calibration', updates))
    return tuple(result)


def truth(bare_source):
    trace = execute(bare_source, bound=96)
    definition_ids, writes = {}, []
    for item in trace['execution_trace']:
        parents = [definition_ids[u['definition']] for u in item['uses']]
        statement = item['statement']
        name, version = item['definition'].split('@')
        writes.append(dict(statement=statement, slot=old.SLOTS[name], version=int(version),
            value=item['value'], parents=parents))
        definition_ids[item['definition']] = statement
    last = trace['execution_trace'][-1]
    return dict(writes=writes, expected_answer=trace['expected_answer'],
        values=[last['values'][name] for name in old.SLOTS],
        definitions=[definition_ids[last['versions'][name]] for name in old.SLOTS])


@lru_cache(maxsize=1)
def _make_rows():
    rows, used_states = [], set()
    for depth, kind, split, updates in structures():
        key = old.canonical_key(updates)
        group = 'arithmetic-local:' + digest(key)[:24]
        computed = sorted({u[0] for u in updates})
        untouched = sorted(set(range(4)) - set(computed))
        for seed_index, seed in enumerate(SEEDS):
            for draw in range(3):
                query_pool = computed if split == 'calibration' or (seed_index + draw) % 2 == 0 or not untouched else untouched
                query = query_pool[(seed_index + draw) % len(query_pool)]
                for attempt in range(10000):
                    rng = random.Random(digest([group, seed, draw, attempt]))
                    roots = [rng.randrange(-6, 7) for _ in range(4)]
                    if draw == 1:
                        roots[1] = roots[0]
                    if draw == 2:
                        roots[2] = roots[0] + roots[1]
                    if max(map(abs, roots)) > 6 or tuple(roots) in used_states:
                        continue
                    body = '\n'.join([*(f'v{i} = {v}' for i, v in enumerate(roots)),
                        *(f'v{d} = v{a} {op} v{b}' for d, a, b, op in updates)])
                    bare = body + f'\nv{query}'
                    try:
                        oracle = truth(bare)
                    except ValueError:
                        continue
                    used_states.add(tuple(roots))
                    break
                else:
                    raise ValueError('finite numeric state search exhausted')
                for lexical, mapping in enumerate(LEXICAL_MAPS):
                    canonical = body + f'\nprint(v{query})'
                    renamed_body, renamed_query = rename(bare, mapping).rsplit('\n', 1)
                    surface = renamed_body + '\nprint(' + renamed_query + ')'
                    rows.append(dict(id='local-case:' + digest([group, seed, draw, lexical])[:24],
                        evaluation_role=ROLE, component_id=group, split=split,
                        operation_family=kind, depth=depth, family_stratum=f'depth{depth}_{kind}',
                        numeric_seed=seed, numeric_draw=draw, lexical_realization=lexical,
                        numeric_stratum=('uniform', 'equal_roots', 'additive_roots')[draw],
                        query_slot=query, query_kind='arithmetic_written' if query in computed else 'untouched_literal',
                        condition='neutral', source=surface, canonical_source=canonical,
                        bare_canonical_source=bare, rename_map=mapping,
                        initial_state_id=digest(roots), body_id=digest(body),
                        expected_answer=oracle['expected_answer'], oracle=oracle))
    return rows


def make_rows():
    return deepcopy(_make_rows())


def points(row):
    """Source spans and read-time candidates; no future definition is eligible."""
    source = row['source']
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    starts, cursor = [], 0
    for line in lines:
        starts.append(cursor)
        cursor += len(line)
    result, definition_points = [], {}
    for statement, node in enumerate(tree.body[:-1]):
        if statement >= 4:
            write = row['oracle']['writes'][statement]
            for side, expr, parent in zip(('left', 'right'), (node.value.left, node.value.right), write['parents']):
                start = starts[expr.lineno - 1] + expr.col_offset
                stop = starts[expr.end_lineno - 1] + expr.end_col_offset
                if source[start:stop] != expr.id or parent >= statement:
                    raise ValueError('operand span or causal parent differs')
                result.append(dict(kind='use', statement=statement, side=side,
                    start=start, stop=stop, name=expr.id, parent=parent,
                    candidate_definitions=list(range(statement)),
                    candidate_points=[definition_points[i] for i in range(statement)]))
        stop = starts[node.end_lineno - 1] + node.end_col_offset
        definition_points[statement] = len(result)
        result.append(dict(kind='definition', statement=statement, start=stop - 1, stop=stop,
            name=node.targets[0].id, value=row['oracle']['writes'][statement]['value']))
    if len(result) + 1 > MAX_POINTS:
        raise ValueError('source exceeds declared capture point bound')
    result.append(dict(kind='answer', start=len(source) - 1, stop=len(source),
        value=row['expected_answer']))
    return result


def validate(rows, independent=True):
    if rows != make_rows() or len(rows) != 5292 or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('complete deterministic local source cohort required')
    groups, keys, bodies = {}, {}, {}
    for row in rows:
        group, split = row['component_id'], row['split']
        if group in groups and groups[group] != split:
            raise ValueError('structural relatives leaked across splits')
        groups[group] = split
        body = row['bare_canonical_source'].rsplit('\n', 1)[0]
        if body in bodies and bodies[body] != split:
            raise ValueError('exact body leaked across splits')
        bodies[body] = split
        if truth(row['bare_canonical_source']) != row['oracle']:
            raise ValueError('read-time trace differs')
        if independent:
            scope = {}
            for index, node in enumerate(ast.parse(body).body):
                exec(compile(ast.Module(body=[node], type_ignores=[]), '<local-generated>', 'exec'), {'__builtins__': {}}, scope)
                name = node.targets[0].id
                if scope[name] != row['oracle']['writes'][index]['value']:
                    raise ValueError('independent Python assignment value differs')
            if [scope[name] for name in old.SLOTS] != row['oracle']['values']:
                raise ValueError('independent Python final state differs')
            surface_scope = {}
            exec(compile('\n'.join(row['source'].splitlines()[:-1]), '<local-surface>', 'exec'), {'__builtins__': {}}, surface_scope)
            query_name = ast.parse(row['source']).body[-1].value.args[0].id
            if surface_scope[query_name] != row['expected_answer']:
                raise ValueError('surface renaming changes answer')
        points(row)
    for depth, kind, split, updates in structures():
        key = old.canonical_key(updates)
        if key in keys and keys[key] != split:
            raise ValueError('canonical slot-renaming equivalence leaked')
        keys[key] = split
    return dict(status='passed', evaluation_role=ROLE, rows=len(rows),
        split_rows=dict(Counter(r['split'] for r in rows)), split_families=dict(Counter(groups.values())),
        family_strata=dict(Counter(r['family_stratum'] for r in rows)),
        independent_python_passed=independent, original_canonical_overlap=0,
        canonical_split_overlap=0, exact_body_overlap=0, generated_holdouts_opened=False,
        limitations='Adaptive discovery. Canonical grouping quotients slot renaming, not every semantic equivalence. '
            'One-update calibration is excluded from all probe fits; supplied source spans do not establish node discovery.')


def build(path):
    path = Path(path)
    rows = make_rows()
    review = validate(rows)
    payload = ''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows).encode()
    base._publish(path, payload)
    manifest = dict(review, sha256=base._sha(path))
    base._put(path.with_suffix('.manifest.json'), manifest)
    return manifest
