"""Balanced numeric controls on the discovery-only varied-copy routing bank.

Initial algebraic relations are between literal values: the program still only
copies values. Oracle and generator labels are TARGETS, never model features.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
from itertools import product
import json
import random

from . import relationship_programs as routing
from .competition import alpha_skeleton
from .datasets import digest
from .interpreter import execute
from .programs import rename
from .published_benchmarks import immutable
from .registry import code_identity

ROLE = 'discovery_algebraic_relationship_routing_v1'
STRATA = ('distinct_uniform', 'additive_triplet', 'equal_pair')
LIMITATIONS = [
    'Source and oracle numeric controls only; no model responses, activations, training or decoded relations.',
    'Discovery preparation, not confirmatory evidence, independent seed replications or new-family qualification.',
    'The body only copies values; a+b=c is a relation among initial literals, not an arithmetic execution task.',
    'One final v0 query, fixed canonical destination order, neutral names and four scalar variables only.',
    'The 81 routing graphs are reused from the structural bank; numeric strata do not add new topologies.',
    'All strata, numeric draws, lexical forms and first-copy rewirings stay in their structural component.',
    'Distinct-uniform draws may accidentally satisfy a+b=c; stratum membership is generator metadata, not an exhaustive algebraic label.',
    'Equal numeric states may recur across components; numeric rows are not independent graph replications.',
    'Oracle traces, values, answers, topology, strata and numeric draws are targets, never readout features.',
    'Full-program oracle targets contain future information; prefix labels must hide future assignments and output relevance.',
    'Disjoint full graphs do not imply disjoint visible-prefix graphs or prove relational information is encoded.',
]


def _config(config):
    if not isinstance(config, dict) or config.get('evaluation_role') != ROLE:
        raise ValueError('explicit discovery algebraic relationship role required')
    translated = dict(config, evaluation_role=routing.ROLE,
                      numeric_instances=config.get('numeric_instances', 4))
    return routing._config(translated)


def _draws(seed, digits, n):
    pool = tuple(i for i in range(-9, 10) if i)
    additive = [(a, b, a + b, d) for a, b in product(range(-6, 7), repeat=2)
                if a and b and a + b and len({a, b, a + b}) == 3
                for d in pool if d not in {a, b, a + b}]
    seen, result = set(), {}
    for stratum in STRATA:
        rng = random.Random(digest([ROLE, seed, list(digits), stratum]))
        selected = []
        while len(selected) < n:
            if stratum == 'distinct_uniform': values = tuple(rng.sample(pool, 4))
            elif stratum == 'additive_triplet': values = rng.choice(additive)
            else:
                a, b, d = rng.sample(pool, 3)
                values = (a, b, b, d)
            if values not in seen:
                seen.add(values)
                selected.append(values)
        result[stratum] = selected
    return result


def make_rows(config):
    n, _ = _config(config)
    rows = []
    for digits in product(range(3), repeat=3):
        component = 'relationship-routing:' + ''.join(map(str, digits))
        split = 'development' if sum(digits) % 3 == 0 else 'train'
        remaining = {name: tuple(other for other in routing.VARIABLES if other != name)[digit]
                     for name, digit in zip(routing.VARIABLES[1:], digits)}
        for stratum, draws in _draws(config['seed'], digits, n).items():
            for numeric, values in enumerate(draws):
                base = f'algebraic:{component}:seed{config["seed"]}:{stratum}:numeric{numeric}'
                for parent in routing.VARIABLES[1:]:
                    parents = {'v0': parent, **remaining}
                    source = '\n'.join([f'{name} = {value}' for name, value in zip(routing.VARIABLES, values)]
                        + [f'{name} = {parents[name]}' for name in routing.VARIABLES] + ['v0'])
                    truth = execute(source)
                    for lexical in (0, 1):
                        mapping = routing._mapping(split, lexical)
                        rendered = rename(source, mapping)
                        offset, spans = 0, []
                        for i, line in enumerate(rendered.splitlines()):
                            spans.append({'statement': i, 'start': offset, 'end': offset + len(line)})
                            offset += len(line) + 1
                        rows.append({'schema_version': 1, 'evaluation_role': ROLE,
                            'id': 'algebraic-routing:' + digest([config['seed'], stratum, rendered])[:24],
                            'base_id': base, 'paired_group_id': base, 'counterfactual_group_id': base,
                            'component_id': component, 'cluster_id': component, 'template_id': component,
                            'split': split, 'family': 'algebraic_copy_routing', 'control_kind': 'primary',
                            'condition': 'neutral', 'lexical_realization': lexical,
                            'source': rendered, 'canonical_source': source, 'rename_map': mapping,
                            'variable_slots': {name: i for i, name in enumerate(routing.VARIABLES)},
                            'statement_spans': spans, 'query_role': 'v0', 'query_count': 1,
                            'targets': {'numeric_stratum': stratum, 'numeric_draw': numeric,
                                'initial_values': list(values), 'parent_by_destination': parents,
                                'component_digits': list(digits)}, **truth})
    return rows


def validate_rows(config, rows, independent=False):
    n, _ = _config(config)
    if rows != make_rows(config):
        raise ValueError('algebraic rows differ from the fixed source/target factorial')
    if len(rows) != 486 * n or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('algebraic factorial coverage or row IDs differ')
    fingerprints = {key: defaultdict(set) for key in ('source', 'canonical_ast', 'alpha_structure')}
    graphs, components, balance, twins = defaultdict(set), defaultdict(set), Counter(), defaultdict(dict)
    programs, numeric_groups, accidental = set(), set(), set()
    for row in rows:
        source, surface = row['canonical_source'], row['source']
        truth, actual = execute(source), execute(surface)
        if (execute(rename(surface, {v: k for k, v in row['rename_map'].items()})) != truth
                or actual['expected_answer'] != row['expected_answer']):
            raise ValueError('canonical/surface execution differs')
        a, b, c, d = row['targets']['initial_values']
        stratum = row['targets']['numeric_stratum']
        if (not all(type(v) is int and v and abs(v) <= 12 for v in (a, b, c, d))
                or stratum == 'distinct_uniform' and len({a, b, c, d}) != 4
                or stratum == 'additive_triplet' and (a + b != c or len({a, b, c, d}) != 4 or not (-6 <= a <= 6 and -6 <= b <= 6))
                or stratum == 'equal_pair' and (b != c or len({a, b, d}) != 3)):
            raise ValueError('invalid numeric stratum')
        graph = tuple(sorted(tuple(edge) for edge in truth['dependency_edges'] if edge[1] != 'output'))
        if len(truth['execution_trace']) != 8 or len(graph) != 4:
            raise ValueError('expected four roots and four copies')
        graphs[row['split']].add(graph); components[row['split']].add(row['component_id'])
        balance[row['component_id'], stratum] += 1
        numeric_groups.add(row['base_id'])
        if stratum == 'distinct_uniform' and a + b == c: accidental.add(row['base_id'])
        twins[row['base_id'], row['lexical_realization']][row['targets']['parent_by_destination']['v0']] = row
        for key, value in (('source', surface), ('canonical_ast', ast.dump(ast.parse(source))),
                           ('alpha_structure', alpha_skeleton(source))):
            fingerprints[key][value].add(row['split'])
        programs.update((source, surface))
    overlap = {key: sum(len(splits) > 1 for splits in groups.values()) for key, groups in fingerprints.items()}
    if (any(overlap.values()) or graphs['train'] & graphs['development']
            or {key: len(value) for key, value in graphs.items()} != {'development': 27, 'train': 54}
            or {key: len(value) for key, value in components.items()} != {'development': 9, 'train': 18}
            or len(balance) != 81 or set(balance.values()) != {6 * n}):
        raise ValueError('algebraic structural split or stratum balance differs')
    matched = 0
    for variants in twins.values():
        if set(variants) != {'v1', 'v2', 'v3'}: raise ValueError('incomplete rewiring group')
        left, right = variants['v1'], variants['v2']
        if left['targets']['numeric_stratum'] == 'equal_pair':
            if ([p['values'] for p in left['execution_trace']] != [p['values'] for p in right['execution_trace']]
                    or left['dependency_edges'] == right['dependency_edges']
                    or left['expected_answer'] != right['expected_answer']):
                raise ValueError('equal-pair graph controls differ')
            matched += 1
    return {'rows': len(rows), 'split_rows': dict(Counter(r['split'] for r in rows)),
        'structural_components': 27, 'split_components': {k: len(v) for k, v in components.items()},
        'distinct_definition_graphs': 81, 'split_definition_graphs': {k: len(v) for k, v in graphs.items()},
        'numeric_instances_per_stratum_per_component': n, 'numeric_groups': len(numeric_groups),
        'numeric_stratum_rows': dict(Counter(r['targets']['numeric_stratum'] for r in rows)),
        'split_numeric_stratum_rows': {split: dict(Counter(r['targets']['numeric_stratum'] for r in rows if r['split'] == split))
                                      for split in ('train', 'development')},
        'uniform_accidental_additive_numeric_groups': len(accidental),
        'equal_pair_same_values_different_graph': matched, 'cross_split_overlap': overlap,
        'cross_split_definition_graph_overlap': 0,
        'independent_python_programs': routing._python_validate(programs) if independent else 0,
        'independent_python_passed': bool(independent)}


def build(config):
    _, paths = _config(config)
    rows = make_rows(config)
    result = validate_rows(config, rows, independent=True)
    payload = ''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows).encode()
    if len(payload) > 128 * 1024**2: raise ValueError('bounded algebraic source bank exceeded')
    result.update(status='passed', evaluation_role=ROLE, config_hash=digest(config), config=config,
        dataset=str(paths['dataset']), dataset_sha256=hashlib.sha256(payload).hexdigest(), source=code_identity(),
        new_model_queries=0, model_or_tokenizer_loaded=False, activation_arrays_read=False,
        relation_decoding_performed=False, generated_holdouts_opened=False, limitations=LIMITATIONS)
    report = '\n'.join(['# Algebraic relationship source controls', '',
        f"Prepared {result['rows']:,} source rows: {result['split_rows']['train']:,} training and {result['split_rows']['development']:,} development, across 18/9 components and 54/27 full definition graphs.",
        f"Each of three numeric strata has {162 * result['numeric_instances_per_stratum_per_component']:,} rows, with the same topology/lexical factorial.",
        'Strata: four distinct uniform nonzero literals; a+b=c with four distinct nonzero literals; and initial v1=v2 with v0/v3 distinct.',
        f"Equal-pair controls: {result['equal_pair_same_values_different_graph']:,} value-matched lexical graph pairs. Distinct-uniform accidental a+b=c numeric groups: {result['uniform_accidental_additive_numeric_groups']}.",
        f"Cross-split exact source/canonical AST/alpha/full-graph overlap: zero. Independent Python full-trace checks: {result['independent_python_programs']:,} distinct canonical/surface programs.",
        f"Dataset SHA256: `{result['dataset_sha256']}`. Review: `{config['review']}`.", '',
        '## Scope', '', *['- ' + limitation for limitation in LIMITATIONS], '']).encode()
    result['report'] = {'path': str(paths['report']), 'sha256': hashlib.sha256(report).hexdigest()}
    manifest = {'schema_version': 1, 'status': 'complete', 'evaluation_role': ROLE, 'role': ROLE,
        'sha256': result['dataset_sha256'], 'rows': len(rows), 'generation_config': config,
        'generation_config_hash': digest(config), 'split_rows': result['split_rows'],
        'numeric_stratum_rows': result['numeric_stratum_rows'], 'structural_components': 27,
        'distinct_definition_graphs': 81, 'independent_python_passed': True,
        'generated_holdouts_opened': False, 'source': result['source'], 'review': str(paths['review'])}
    outputs = [(paths['dataset'], payload), (paths['manifest'], routing._json_bytes(manifest)),
               (paths['report'], report), (paths['review'], routing._json_bytes(result))]
    for path, data in outputs:
        if path.exists() and (path.stat().st_size != len(data) or path.read_bytes() != data):
            raise ValueError('immutable algebraic artifact already differs: ' + str(path))
    for path, data in outputs: immutable(path, data)
    from .experiment_log import note_artifact
    note_artifact(paths['review'].resolve())
    return result
