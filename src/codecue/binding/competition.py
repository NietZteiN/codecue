"""Discovery-only arithmetic-free ownership and assignment-version contrasts."""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import itertools
import json
from pathlib import Path
import random

from .datasets import digest, read_jsonl, write_json
from .interpreter import execute, python_oracle
from .programs import rename
from .published_benchmarks import immutable, sha

ROLE = 'binding_competition_discovery_v1'


def alpha_skeleton(source):
    """Remove literal values and consistently rename by first occurrence."""
    class Canonical(ast.NodeTransformer):
        def __init__(self):self.names = {}
        def visit_Name(self, node):
            name = self.names.setdefault(node.id, f'slot{len(self.names)}')
            return ast.copy_location(ast.Name(id=name, ctx=node.ctx), node)
        def visit_Constant(self, node):return ast.copy_location(ast.Constant(value=0), node)
        def visit_UnaryOp(self, node):return ast.copy_location(ast.Constant(value=0), node)
    return ast.dump(Canonical().visit(ast.parse(source)), include_attributes=False)


def assign_splits(rows):
    """Union all structural and counterfactual relatives before assigning splits."""
    parent = {r['structural_group']: r['structural_group'] for r in rows}
    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    seen = {}
    for row in rows:
        structure = alpha_skeleton(row['canonical_source'])
        group = row['structural_group']
        if structure in seen:parent[root(group)] = root(seen[structure])
        else:seen[structure] = group
    groups = defaultdict(list)
    for group in parent:groups[root(group)].append(group)
    identifiers = {group: digest(sorted(members))[:24] for group, members in groups.items()}
    order = sorted(identifiers, key=lambda group: identifiers[group])
    # No final test exists in this discovery bank. Component assignment is
    # independent of labels, scores, numeric draws and surface identifiers.
    ndev = max(1, len(order) // 4) if len(order) > 1 else 0
    dev = set(order[:ndev])
    for row in rows:
        group = root(row['structural_group'])
        row.update(template_id=identifiers[group], split='development' if group in dev else 'train')
    return len(groups)


def names_for(row, condition, lexical):
    names = sorted({n.id for n in ast.walk(ast.parse(row['canonical_source'])) if isinstance(n, ast.Name)})
    prefix = 'dev_' if row['split'] == 'development' else 'train_'
    if condition == 'neutral':
        return {name: prefix + ('item_' if lexical == 0 else 'cell_') + chr(97 + index)
                for index, name in enumerate(names)}
    role = {'v0': 'current_value' if lexical == 0 else 'new_value',
            'saved': 'saved_value' if lexical == 0 else 'old_value',
            'buffer': 'temp_value', 'v1': 'other_value', 'v2': 'spare_left', 'v3': 'spare_right'}
    if condition == 'misleading':role['v0'], role['saved'] = role['saved'], role['v0']
    return {name: prefix + role[name] for name in names}


def error_alternatives(source):
    truth = execute(source)
    query = ast.parse(source).body[-1].value.id
    trace = truth['execution_trace']
    alternatives = [{'label': 'competing_binding:' + name, 'value': value}
                    for name, value in trace[-1]['values'].items() if name != query]
    definitions = [p for p in trace if p['definition'].split('@')[0] == query]
    alternatives += [{'label': 'obsolete_assignment:' + p['definition'], 'value': p['value']}
                     for p in definitions[:-1]]
    alternatives.append({'label': 'last_assignment_value', 'value': trace[-1]['value']})
    return alternatives


def canonical_rows(config):
    rng = random.Random(config['seed'])
    rows = []
    used = set()
    for available in (2, 4):
        slots = [f'v{i}' for i in range(available)]
        for family in ('ownership', 'versions'):
            steps = slots + ['buffer'] + (['saved'] if family == 'versions' else [])
            orders = [p for p in itertools.permutations(steps)
                      if family == 'ownership' or p.index('v0') < p.index('saved')]
            rng.shuffle(orders)
            orders = orders[:6 if family == 'ownership' else 12]
            for index, order in enumerate(orders):
                for numeric in range(config['numeric_per_template']):
                    while True:
                        values = rng.sample([i for i in range(-16, 17) if i], available + 3)
                        draw = (tuple(sorted(values[:2])) + tuple(values[2:available])
                                if family == 'ownership' else tuple(values))
                        key = family, available, index, draw
                        if key not in used:
                            used.add(key)
                            break
                    base = f'{family}:{available}:{index}:{numeric}'
                    init = {slot: value for slot, value in zip(slots, values)}
                    if family == 'ownership':
                        for swapped in (False, True):
                            effective = dict(init)
                            if swapped:effective['v0'], effective['v1'] = effective['v1'], effective['v0']
                            prefix = [f'{slot} = {effective[slot]}' if slot != 'buffer' else 'buffer = 0' for slot in order]
                            for query in ('v0', 'v1'):
                                rows.append(dict(family=family, available_bindings=available, updates=0,
                                    query_role=query, ownership_swapped=swapped, tail_placement='none',
                                    base_id=base, structural_group=f'{family}:{available}:{index}',
                                    canonical_source='\n'.join(prefix + [query])))
                    else:
                        c, d, final = values[available:]
                        prefix = [f'{slot} = {init[slot]}' if slot in init else
                                  'saved = v0' if slot == 'saved' else 'buffer = 0' for slot in order]
                        tail = ['buffer = v1', 'buffer = 0'] * 2
                        for updates in (1, 3):
                            owner = 'v0' if updates == 3 else 'buffer'
                            block = [f'{owner} = {c}', f'{owner} = {d}', 'buffer = 0']
                            for placement in ('before', 'after'):
                                program = prefix + block + (tail if placement == 'before' else []) + [f'v0 = {final}']
                                if placement == 'after':program += tail
                                for query in ('v0', 'saved'):
                                    rows.append(dict(family=family, available_bindings=available, updates=updates,
                                        query_role='current' if query == 'v0' else 'saved', ownership_swapped=False,
                                        tail_placement=placement, base_id=base,
                                        structural_group=f'{family}:{available}:{index}',
                                        canonical_source='\n'.join(program + [query])))
    return rows


def validate_rows(rows, independent=False):
    if not rows or len({r['id'] for r in rows}) != len(rows):raise ValueError('competition IDs missing or duplicated')
    groups, structures, prefixes = defaultdict(list), defaultdict(set), defaultdict(set)
    for row in rows:
        if row['evaluation_role'] != ROLE or row['split'] not in ('train', 'development'):
            raise ValueError('competition cannot include final-test outcomes')
        if any(isinstance(n, ast.BinOp) for n in ast.walk(ast.parse(row['source']))):
            raise ValueError('arithmetic-free competition contains arithmetic')
        if (row['id'] != 'competition:' + digest([row['source'], row['family']])[:24]
                or row['rename_map'] != names_for(row, row['condition'], row['lexical_realization'])):
            raise ValueError('competition ID or semantic naming role differs')
        if rename(row['canonical_source'], row['rename_map']) != row['source']:
            raise ValueError('competition renaming differs')
        truth = execute(row['source'])
        if truth['expected_answer'] != row['expected_answer'] or truth['execution_trace'] != row['execution_trace']:
            raise ValueError('competition oracle differs')
        if row['family'] == 'versions':
            definitions = execute(row['canonical_source'])['execution_trace']
            if sum(p['definition'].split('@')[0] == 'v0' for p in definitions) - 1 != row['updates']:
                raise ValueError('target assignment-version count differs')
        if row['error_alternatives'] != error_alternatives(row['source']):
            raise ValueError('competition error alternatives differ')
        structures[alpha_skeleton(row['canonical_source'])].add(row['split'])
        prefixes[row['base_id']].add(row['split'])
        groups[row['base_id'], row['condition'], row['lexical_realization']].append(row)
    if any(len(s) != 1 for s in [*structures.values(), *prefixes.values()]):
        raise ValueError('competition structural/counterfactual split leakage')
    for group in groups.values():
        if group[0]['family'] == 'ownership':
            if len(group) != 4:raise ValueError('ownership pair coverage differs')
            states = {tuple(sorted(execute(r['canonical_source'])['execution_trace'][-1]['values'].values())) for r in group}
            if len(states) != 1:raise ValueError('ownership value multisets differ')
            for query in ('v0', 'v1'):
                pair = [r for r in group if r['query_role'] == query]
                if len({r['expected_answer'] for r in pair}) != 2:raise ValueError('ownership swap must change the answer')
        else:
            if len(group) != 8:raise ValueError('version-factor coverage differs')
            for query in ('current', 'saved'):
                subset = [r for r in group if r['query_role'] == query]
                if len({r['expected_answer'] for r in subset}) != 1:raise ValueError('version/tail contrast changed answer')
                states = {digest(execute(r['canonical_source'])['execution_trace'][-1]['values']) for r in subset}
                literals = {tuple(sorted(n.value for n in ast.walk(ast.parse(r['canonical_source'])) if isinstance(n, ast.Constant))) for r in subset}
                counts = {len(ast.parse(r['canonical_source']).body) for r in subset}
                if len(states) != 1 or len(literals) != 1 or len(counts) != 1:
                    raise ValueError('version controls differ in final state, literal exposure or statement count')
    if independent:
        for start in range(0, len(rows), 128):
            batch = rows[start:start + 128]
            oracle = python_oracle([r['source'] for r in batch])
            if any(r['expected_answer'] != o['answer'] or [p['values'] for p in r['execution_trace']] != o['trace']
                   for r, o in zip(batch, oracle)):
                raise ValueError('independent competition oracle mismatch')
    return rows


def build(config):
    raw = canonical_rows(config)
    components = assign_splits(raw)
    rows = []
    for base in raw:
        conditions = ('neutral',) if base['family'] == 'ownership' else ('informative', 'neutral', 'misleading')
        for condition in conditions:
            for lexical in (0, 1):
                mapping = names_for(base, condition, lexical)
                source = rename(base['canonical_source'], mapping)
                truth = execute(source)
                rows.append(dict(base, id='competition:' + digest([source, base['family']])[:24],
                    evaluation_role=ROLE, source=source, oracle_source=source, rename_map=mapping,
                    condition=condition, lexical_realization=lexical, paired_group_id=base['base_id'],
                    expected_answer=truth['expected_answer'], execution_trace=truth['execution_trace'],
                    error_alternatives=error_alternatives(source)))
    validate_rows(rows, independent=True)
    path = Path(config['dataset'])
    immutable(path, ''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows).encode())
    manifest = dict(status='validated', sha256=sha(path), rows=len(rows), evaluation_role=ROLE, seed=config['seed'],
                    generation_config_hash=digest(config), independent_python_programs=len(rows),
                    structural_components=components, split_rows=dict(Counter(r['split'] for r in rows)),
                    family_counts=dict(Counter(r['family'] for r in rows)),
                    limitations='Discovery only. Available bindings include irrelevant competitors; this is not a manipulation of the number of live output dependencies. Literal values and final states are matched within version/tail contrasts.')
    immutable(path.with_suffix('.manifest.json'), (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode())
    return manifest
