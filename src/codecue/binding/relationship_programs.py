"""Discovery-only copy routing with value-matched, differently wired graphs.

This module builds source programs and oracle TARGETS, never model features,
responses, captures or learned graph predictions. Structural components keep all
three first-copy rewirings, numeric draws and lexical renderings together.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
from itertools import product
import json
from pathlib import Path
import random

from .competition import alpha_skeleton
from .datasets import digest
from .interpreter import execute, python_oracle, substituted_source
from .programs import rename
from .published_benchmarks import immutable
from .registry import code_identity

ROLE = 'discovery_relationship_routing_v1'
VARIABLES = ('v0', 'v1', 'v2', 'v3')
MAX_NUMERIC_INSTANCES = 64
LIMITATIONS = [
    'Source and oracle-target preparation only: no model responses, activations, probes or decoded graphs.',
    'Adaptive discovery bank, not confirmatory evidence or qualification of a new model family.',
    'Copy-only programs with four scalar variables and one final query, v0; no broad query replication.',
    'Canonical destination order is fixed: four initializations followed by v0, v1, v2, v3 copies.',
    'Numeric draws and lexical forms repeat a topology; they are not independent graph replications.',
    'Equal numeric states may occur across components; structural components, not numeric uniqueness, define the split.',
    'All oracle values, versions, dependencies, topology and counterfactual labels are targets, never readout features.',
    'Full-program oracle targets include future information; a prefix study must mask unseen definitions and output relevance.',
    'Syntactic ancestry and functional intervention effects are distinct; descendants can later be overwritten.',
]


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def _safe_path(value, suffix):
    from .experiment_log import _protected_outcome
    if not isinstance(value, str) or not value or len(value) > 1024 or '\x00' in value:
        raise ValueError('bounded explicit output paths required')
    path = Path(value)
    if path.suffix != suffix:
        raise ValueError('output path extension differs: ' + suffix)
    if _protected_outcome(path) or _protected_outcome(path.resolve()):
        raise ValueError('reserved test/final/holdout paths are excluded')
    if path.exists() and not path.is_file():
        raise ValueError('output path must be a regular file')
    return path


def _config(config):
    required = {'evaluation_role', 'seed', 'dataset', 'review', 'report'}
    if (not isinstance(config, dict) or config.get('evaluation_role') != ROLE
            or required - set(config) or set(config) - required - {'numeric_instances'}):
        raise ValueError('explicit discovery relationship role and exact configuration fields required')
    try:
        size = len(json.dumps(config, allow_nan=False).encode())
    except (TypeError, ValueError) as exc:
        raise ValueError('bounded JSON configuration required') from exc
    if size > 16 * 1024:
        raise ValueError('bounded JSON configuration required')
    if type(config['seed']) is not int or not 0 <= config['seed'] < 2**63:
        raise ValueError('seed must be a bounded nonnegative integer')
    n = config.get('numeric_instances', 8)
    if type(n) is not int or not 1 <= n <= MAX_NUMERIC_INSTANCES:
        raise ValueError('numeric_instances must be an integer in [1, 64]')
    paths = {name: _safe_path(config[name], suffix) for name, suffix in
             (('dataset', '.jsonl'), ('review', '.json'), ('report', '.md'))}
    paths['manifest'] = _safe_path(str(paths['dataset'].with_suffix('.manifest.json')), '.json')
    resolved = [p.resolve() for p in paths.values()]
    if len(set(resolved)) != len(resolved) or any(a in b.parents for a in resolved for b in resolved if a != b):
        raise ValueError('output artifacts must use distinct nonoverlapping paths')
    return n, paths


def _mapping(split, lexical):
    prefix = 'dev_' if split == 'development' else ''
    stem = 'item' if lexical == 0 else 'cell'
    return {name: f'{prefix}{stem}_{i}' for i, name in enumerate(VARIABLES)}


def _source(values, parents):
    a, b, c = values
    return '\n'.join([f'v0 = {a}', f'v1 = {b}', f'v2 = {b}', f'v3 = {c}']
                     + [f'{name} = {parents[name]}' for name in VARIABLES] + ['v0'])


def _counterfactuals(source, truth, b):
    result = []
    for root in ('v1@1', 'v2@1'):
        alternate = execute(source, {root: b + 1})
        descendants = [p['definition'] for p, q in zip(truth['execution_trace'], alternate['execution_trace'])
                       if p['definition'] != root and p['value'] != q['value']]
        final = alternate['execution_trace'][-1]['values']
        baseline = truth['execution_trace'][-1]['values']
        result.append({'definition': root, 'replacement': b + 1,
                       'changed_descendant_definitions': descendants,
                       'changed_final_variables': [name for name in VARIABLES if final[name] != baseline[name]],
                       'final_values': final, 'expected_answer': alternate['expected_answer']})
    return result


def make_rows(config):
    """Deterministically construct the complete grouped discovery factorial."""
    n, _ = _config(config)
    rows = []
    pool = tuple(i for i in range(-9, 10) if i)
    for digits in product(range(3), repeat=3):
        component = 'relationship-routing:' + ''.join(map(str, digits))
        split = 'development' if sum(digits) % 3 == 0 else 'train'
        rng = random.Random(digest([ROLE, config['seed'], list(digits)]))
        draws = []
        while len(draws) < n:
            values = tuple(rng.sample(pool, 3))
            if values not in draws:
                draws.append(values)
        remaining = {name: tuple(other for other in VARIABLES if other != name)[digit]
                     for name, digit in zip(VARIABLES[1:], digits)}
        for numeric, values in enumerate(draws):
            base = f'{component}:seed{config["seed"]}:numeric{numeric}'
            for parent in VARIABLES[1:]:
                parents = {'v0': parent, **remaining}
                source = _source(values, parents)
                truth = execute(source)
                targets = {'canonical_oracle': truth, 'parent_by_destination': parents,
                           'component_digits': list(digits), 'initial_values': dict(zip(('a', 'b', 'c'), values)),
                           'functional_counterfactuals': _counterfactuals(source, truth, values[1])}
                for lexical in (0, 1):
                    mapping = _mapping(split, lexical)
                    rendered = rename(source, mapping)
                    offset = 0
                    spans = []
                    for i, line in enumerate(rendered.splitlines()):
                        spans.append({'statement': i, 'start': offset, 'end': offset + len(line)})
                        offset += len(line) + 1
                    rows.append({'schema_version': 1, 'evaluation_role': ROLE,
                        'id': 'relationship-routing:' + digest([config['seed'], rendered])[:24],
                        'base_id': base, 'paired_group_id': base, 'counterfactual_group_id': base,
                        'component_id': component, 'cluster_id': component, 'template_id': component,
                        'split': split, 'family': 'varied_copy_routing', 'control_kind': 'primary',
                        'condition': 'neutral', 'lexical_realization': lexical,
                        'source': rendered, 'canonical_source': source, 'rename_map': mapping,
                        'variable_slots': {name: i for i, name in enumerate(VARIABLES)},
                        'statement_spans': spans, 'query_role': 'v0', 'query_count': 1,
                        'expected_answer': truth['expected_answer'], 'targets': targets})
    return rows


def _python_validate(programs):
    """Check full traces against ordinary Python for each distinct program."""
    sources = sorted(programs)
    for start in range(0, len(sources), 128):
        batch = sources[start:start + 128]
        for source, ordinary in zip(batch, python_oracle(batch)):
            truth = execute(source)
            if (ordinary['answer'] != truth['expected_answer']
                    or ordinary['trace'] != [p['values'] for p in truth['execution_trace']]):
                raise ValueError('independent Python full trace disagrees')
    return len(sources)


def validate_rows(config, rows, independent=False):
    """Validate complete coverage, grouping, graph variation and functional twins."""
    n, _ = _config(config)
    if rows != make_rows(config):
        raise ValueError('relationship rows differ from the fixed source/target factorial')
    if len({row['id'] for row in rows}) != len(rows):
        raise ValueError('duplicate relationship row IDs')
    fingerprints = {key: defaultdict(set) for key in ('source', 'canonical_ast', 'alpha_structure')}
    graphs, components, paired = defaultdict(set), defaultdict(set), defaultdict(dict)
    programs = set()
    for row in rows:
        canonical, surface = row['canonical_source'], row['source']
        truth, actual = execute(canonical), execute(surface)
        reverse = {value: key for key, value in row['rename_map'].items()}
        if execute(rename(surface, reverse)) != truth or actual['expected_answer'] != row['expected_answer']:
            raise ValueError('canonical/surface execution differs')
        graph = tuple(sorted(tuple(edge) for edge in truth['dependency_edges'] if edge[1] != 'output'))
        if len(truth['execution_trace']) != 8 or len(graph) != 4:
            raise ValueError('expected four roots and four directed copies')
        graphs[row['split']].add(graph)
        components[row['split']].add(row['component_id'])
        paired[row['base_id'], row['lexical_realization']][row['targets']['parent_by_destination']['v0']] = row
        for key, value in (('source', surface), ('canonical_ast', ast.dump(ast.parse(canonical))),
                           ('alpha_structure', alpha_skeleton(canonical))):
            fingerprints[key][value].add(row['split'])
        programs.update((canonical, surface))
        b = row['targets']['initial_values']['b']
        for root in ('v1@1', 'v2@1'):
            programs.add(substituted_source(canonical, root, b + 1))
    overlap = {key: sum(len(splits) > 1 for splits in groups.values())
               for key, groups in fingerprints.items()}
    if any(overlap.values()) or graphs['train'] & graphs['development']:
        raise ValueError('relationship structural split leakage')
    matched, descendant_checks, differing_final_states = 0, 0, 0
    for variants in paired.values():
        if set(variants) != {'v1', 'v2', 'v3'}:
            raise ValueError('incomplete first-copy rewiring group')
        left, right = variants['v1'], variants['v2']
        ltruth, rtruth = [row['targets']['canonical_oracle'] for row in (left, right)]
        if ([p['values'] for p in ltruth['execution_trace']] != [p['values'] for p in rtruth['execution_trace']]
                or left['expected_answer'] != right['expected_answer']
                or ltruth['dependency_edges'] == rtruth['dependency_edges']):
            raise ValueError('rewired twins must have equal states and answers but different graphs')
        if variants['v3']['expected_answer'] == left['expected_answer']:
            raise ValueError('different-value first-copy control must change the v0 answer')
        matched += 1
        for root in ('v1@1', 'v2@1'):
            alternates = [execute(row['canonical_source'], {root: row['targets']['initial_values']['b'] + 1})
                          for row in (left, right)]
            if alternates[0]['execution_trace'][4]['value'] == alternates[1]['execution_trace'][4]['value']:
                raise ValueError('rewiring must change descendant sensitivity at the first copy')
            descendant_checks += 1
            differing_final_states += (alternates[0]['execution_trace'][-1]['values']
                                       != alternates[1]['execution_trace'][-1]['values'])
    if ({key: len(value) for key, value in graphs.items()} != {'development': 27, 'train': 54}
            or {key: len(value) for key, value in components.items()} != {'development': 9, 'train': 18}
            or len(rows) != 162 * n or matched != 54 * n):
        raise ValueError('fixed relationship bank counts differ')
    return {'rows': len(rows), 'split_rows': dict(Counter(row['split'] for row in rows)),
        'structural_components': 27, 'split_components': {key: len(value) for key, value in components.items()},
        'distinct_definition_graphs': 81, 'split_definition_graphs': {key: len(value) for key, value in graphs.items()},
        'numeric_draws_per_component': n, 'numeric_groups': 27 * n,
        'lexical_realizations': 2, 'first_copy_variants_per_group': 3,
        'paired_same_values_different_graph': matched, 'paired_same_values_all_checkpoints': True,
        'different_value_controls': matched, 'paired_descendant_sensitivity_checks': descendant_checks,
        'paired_counterfactual_final_state_differences': differing_final_states,
        'cross_split_overlap': overlap, 'cross_split_definition_graph_overlap': 0,
        'independent_python_programs': _python_validate(programs) if independent else 0,
        'independent_python_passed': bool(independent)}


def _report(config, result):
    return '\n'.join([
        '# Varied copy relationship source bank', '',
        f"Prepared {result['rows']:,} discovery-only source rows across 27 structural components and 81 directed definition graphs.",
        f"Training: {result['split_rows']['train']:,} rows / 18 components / 54 graphs. Development: {result['split_rows']['development']:,} rows / 9 components / 27 graphs.",
        f"Each component retains {result['numeric_draws_per_component']} numeric draws, all three first-copy parents and both neutral lexical forms.", '',
        f"The {result['paired_same_values_different_graph']:,} lexical pairs with first parent v1 versus v2 have identical numeric states at every checkpoint and identical answers, but distinct versioned graphs.",
        'The v3 first-parent control has a different value and v0 answer. Replacing initial v1 versus v2 with b+1 distinguishes the rewired first-copy descendants; all final variables are also compared without using final survival as the validity criterion.', '',
        f"Cross-split exact source, canonical AST, alpha structure and definition-graph overlap: zero. Independent Python full-trace checks: {result['independent_python_programs']:,} distinct baseline/counterfactual programs.",
        f"Dataset SHA256: `{result['dataset_sha256']}`. Review: `{config['review']}`.", '',
        '## Scope', '', *['- ' + item for item in LIMITATIONS], ''])


def build(config):
    """Write one immutable source bank, manifest, review and scope report."""
    _, paths = _config(config)
    rows = make_rows(config)
    result = validate_rows(config, rows, independent=True)
    payload = ''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows).encode()
    if len(payload) > 128 * 1024**2:
        raise ValueError('bounded relationship source bank exceeded')
    result.update(status='passed', evaluation_role=ROLE, config_hash=digest(config), config=config,
        dataset=str(paths['dataset']), dataset_sha256=hashlib.sha256(payload).hexdigest(),
        source=code_identity(), new_model_queries=0, model_or_tokenizer_loaded=False,
        activation_arrays_read=False, graph_decoding_performed=False,
        generated_holdouts_opened=False, limitations=LIMITATIONS)
    report = _report(config, result).encode()
    result['report'] = {'path': str(paths['report']), 'sha256': hashlib.sha256(report).hexdigest()}
    manifest = {'schema_version': 1, 'status': 'complete', 'evaluation_role': ROLE, 'role': ROLE,
        'sha256': result['dataset_sha256'], 'rows': result['rows'], 'generation_config_hash': digest(config),
        'generation_config': config, 'split_rows': result['split_rows'],
        'structural_components': 27, 'distinct_definition_graphs': 81,
        'independent_python_passed': True, 'generated_holdouts_opened': False,
        'source': result['source'], 'review': str(paths['review'])}
    outputs = [(paths['dataset'], payload), (paths['manifest'], _json_bytes(manifest)),
               (paths['report'], report), (paths['review'], _json_bytes(result))]
    # Refuse all incompatible existing artifacts before creating any new output.
    for path, data in outputs:
        if path.exists() and (path.stat().st_size != len(data) or path.read_bytes() != data):
            raise ValueError('immutable relationship artifact already differs: ' + str(path))
    for path, data in outputs:
        immutable(path, data)
    from .experiment_log import note_artifact
    note_artifact(paths['review'].resolve())
    return result
