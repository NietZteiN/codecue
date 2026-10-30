"""Discovery-only varied copy schedules and actual prefix-visible SSA targets.

No tokenizer, model, activation array or learned readout is used.  The existing
relationships.labels_at supplies every structural target.  Slot-canonical graph
families, including commuting schedules, stay together across numeric, lexical
and query relatives.  This source bank does not qualify a scientific model family.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import hashlib
from itertools import permutations
import json
from pathlib import Path
import random

from . import relationships
from .competition import alpha_skeleton
from .datasets import digest
from .interpreter import execute, python_oracle
from .programs import rename
from .registry import code_identity
from .relationship_capture import _publish, _safe

ROLE = 'discovery_relationship_schedule_targets_v1'
VARIABLES = ('v0', 'v1', 'v2', 'v3')
SLOTS = dict(zip(VARIABLES, range(4)))
SLOT_PERMUTATIONS = tuple(permutations(range(4)))
REPEATED_SCHEDULES = ((0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1), (0, 1, 1, 0))
PARENT_PATTERNS = {'ring_successor': 1, 'opposite': 2, 'ring_predecessor': 3}
N_ROWS = 28 * 3 * 3 * 2 * 4
MAX_BYTES = 128 * 1024**2
LIMITATIONS = [
    'Source and oracle targets only; no model/tokenizer queries, activations, fits or decoded graphs.',
    'Adaptive discovery preparation; no independent confirmation or qualification of a new scientific family.',
    'Four literal roots and four copies, three declared parent patterns, two lexical forms and four final queries.',
    'Raw schedule counts overstate independent units: slot-equivalent and commuting SSA graph relatives share a split.',
    'Numeric seeds, lexical forms and query variants are related cases, not independent graph replications.',
    'Scheduling changes definition age, source position and dependency depth; these factors are not isolated.',
    'All versions, graphs, traces and answers are oracle targets, never readout features.',
    'Syntactic ancestors do not identify functional influence or natural causal use.',
    'The existing fixed-schedule learned targets/readouts are incompatible; a new readout design is required.',
]


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def _config(config):
    required = {'evaluation_role', 'numeric_seeds', 'dataset', 'review', 'report'}
    if (not isinstance(config, dict) or set(config) - required - {'overlap_sources'}
            or not required <= set(config) or config['evaluation_role'] != ROLE):
        raise ValueError('exact discovery-only schedule configuration required')
    try:
        if len(_json_bytes(config)) > 16 * 1024:
            raise ValueError('bounded schedule configuration required')
    except (TypeError, ValueError) as exc:
        raise ValueError('bounded JSON schedule configuration required') from exc
    seeds = config['numeric_seeds']
    if (not isinstance(seeds, list) or len(seeds) != 3
            or any(type(seed) is not int or not 0 <= seed < 2**63 for seed in seeds)
            or len(set(seeds)) != 3):
        raise ValueError('three distinct bounded integer numeric seeds required')
    paths = {}
    for name, suffix in (('dataset', '.jsonl'), ('review', '.json'), ('report', '.md')):
        value = config[name]
        if not isinstance(value, str): raise ValueError('explicit output path strings required')
        path = _safe(value)
        if (path.suffix != suffix or path.is_symlink()
                or (path.exists() and not path.is_file())):
            raise ValueError('regular, nonsymlink output with declared suffix required')
        paths[name] = path
    paths['manifest'] = _safe(paths['dataset'].with_suffix('.manifest.json'))
    if paths['manifest'].is_symlink() or (paths['manifest'].exists() and not paths['manifest'].is_file()):
        raise ValueError('regular nonsymlink source manifest required')
    resolved = [path.resolve() for path in paths.values()]
    if (len(set(resolved)) != len(resolved)
            or any(a in b.parents or b in a.parents for a, b in permutations(resolved, 2))):
        raise ValueError('distinct nonoverlapping output files required')
    previous = config.get('overlap_sources', [])
    if not isinstance(previous, list) or len(previous) > 2:
        raise ValueError('at most two pinned old discovery source banks permitted')
    prior_paths = set()
    for entry in previous:
        if not isinstance(entry, dict) or set(entry) != {'path', 'sha256'}:
            raise ValueError('exact source-only overlap pins required')
        path = _safe(entry['path'])
        checksum = entry['sha256']
        if (not isinstance(entry['path'], str) or path.suffix != '.jsonl'
                or not isinstance(checksum, str) or len(checksum) != 64
                or any(c not in '0123456789abcdef' for c in checksum)
                or path.resolve() in prior_paths
                or any(path.resolve() == p or path.resolve() in p.parents or p in path.resolve().parents
                       for p in resolved)):
            raise ValueError('distinct pinned discovery source banks required')
        prior_paths.add(path.resolve())
    return paths


def _node(node, permutation):
    name, version = node.split('@')
    return f'v{permutation[int(name[1:])]}@{version}'


def _canonical_graph(labels):
    """Canonicalize existing oracle labels, ignoring legal execution ordering."""
    choices = []
    for permutation in SLOT_PERMUTATIONS:
        choices.append((tuple(sorted(_node(item['id'], permutation) for item in labels['version_nodes'])),
            tuple(sorted((_node(a, permutation), _node(b, permutation))
                         for a, b in labels['direct_def_use_edges'])),
            tuple(sorted((_node(a, permutation), _node(b, permutation))
                         for a, b in labels['succession_edges']))))
    best = min(choices)
    return best, SLOT_PERMUTATIONS[choices.index(best)]


def _source(values, destinations, parents, query):
    return '\n'.join([f'v{i} = {value}' for i, value in enumerate(values)]
        + [f'v{dest} = v{parent}' for dest, parent in zip(destinations, parents)] + [f'v{query}'])


@lru_cache(maxsize=1)
def _templates():
    result = []
    for index, destinations in enumerate((*SLOT_PERMUTATIONS, *REPEATED_SCHEDULES)):
        for pattern, offset in PARENT_PATTERNS.items():
            parents = tuple((dest + offset) % 4 for dest in destinations)
            source = _source((1, 2, 3, 4), destinations, parents, 0)
            prefix = [relationships.labels_at(source, i, SLOTS) for i in range(8)]
            graph, mapping = _canonical_graph(prefix[-1])
            ordered = min(tuple((p[d], p[a]) for d, a in zip(destinations, parents))
                          for p in SLOT_PERMUTATIONS)
            component = 'schedule-graph:' + digest(graph)[:24]
            result.append(dict(schedule_id=('permutation:' if index < 24 else 'repeated:')
                + ''.join(map(str, destinations)), schedule_kind='permutation' if index < 24 else 'repeated',
                destinations=destinations, parents=parents, parent_pattern=pattern,
                component_id=component, canonical_slot_mapping=mapping,
                ordered_schedule_canonical_id='schedule-order:' + digest(ordered)[:24],
                prefix_relationships=prefix,
                final_query_relationships=[relationships.labels_at(
                    _source((1, 2, 3, 4), destinations, parents, q), 7, SLOTS, output_visible=True)
                    for q in range(4)]))
    units = sorted({item['component_id'] for item in result})
    splits = {unit: 'development' if i % 3 == 0 else 'train' for i, unit in enumerate(units)}
    for item in result: item['split'] = splits[item['component_id']]
    return tuple(result)


def _numeric_states(config):
    result = {}; seen = set()
    pool = tuple(i for i in range(-12, 13) if i)
    for component in sorted({item['component_id'] for item in _templates()}):
        for seed in config['numeric_seeds']:
            rng = random.Random(digest([ROLE, component, seed]))
            values = tuple(rng.sample(pool, 4))
            while values in seen: values = tuple(rng.sample(pool, 4))
            seen.add(values); result[component, seed] = values
    return result


def make_rows(config):
    """Construct the fixed 2,016-case factorial, without any external execution."""
    _config(config)
    numeric = _numeric_states(config)
    rows = []
    for template in _templates():
        component = template['component_id']; split = template['split']
        for seed in config['numeric_seeds']:
            unit_values = numeric[component, seed]
            values = tuple(unit_values[slot] for slot in template['canonical_slot_mapping'])
            base = f'{component}:numeric{seed}'
            for lexical in (0, 1):
                stem = 'item' if lexical == 0 else 'cell'
                mapping = {name: f'{stem}_{i}' for i, name in enumerate(VARIABLES)}
                for query in range(4):
                    canonical = _source(values, template['destinations'], template['parents'], query)
                    source = rename(canonical, mapping)
                    oracle = execute(canonical)
                    offset = 0; spans = []
                    for statement, line in enumerate(source.splitlines()):
                        spans.append(dict(statement=statement, start=offset, end=offset+len(line)))
                        offset += len(line)+1
                    rows.append(dict(schema_version=1, evaluation_role=ROLE,
                        id='relationship-schedule:' + digest([seed, source])[:24],
                        source=source, canonical_source=canonical, split=split, condition='neutral',
                        family='varied_copy_overwrite_schedule', control_kind='targets_prepared_only',
                        base_id=base, paired_group_id=base, component_id=component, cluster_id=component,
                        template_id=component, raw_template_id=template['schedule_id']+':'+template['parent_pattern'],
                        numeric_seed=seed, lexical_realization=lexical, rename_map=mapping,
                        variable_slots=SLOTS.copy(), query_slot=query, query_role=f'v{query}', query_count=1,
                        source_form='literal', schedule_id=template['schedule_id'],
                        schedule_kind=template['schedule_kind'], destination_schedule=list(template['destinations']),
                        parent_pattern=template['parent_pattern'], copy_parent_slots=list(template['parents']),
                        ordered_schedule_canonical_id=template['ordered_schedule_canonical_id'],
                        ssa_graph_canonical_id=component, statement_spans=spans,
                        expected_answer=oracle['expected_answer'],
                        targets=dict(prefix_relationships=deepcopy(template['prefix_relationships']),
                            final_query_relationships=deepcopy(template['final_query_relationships'][query]),
                            canonical_execution_trace=oracle['execution_trace'])))
    return rows


def _check_oracle_labels(row, oracle):
    """Validate stored generic labels against the existing interpreter trace."""
    trace = oracle['execution_trace']
    prefix_targets = row['targets']['prefix_relationships']
    if len(prefix_targets) != 8 or len(trace) != 8:
        raise ValueError('eight assignment checkpoints required')
    for checkpoint, labels in enumerate(prefix_targets):
        visible = {point['definition'] for point in trace[:checkpoint+1]}
        current = set(trace[checkpoint]['versions'].values())
        nodes = {node['id']: node for node in labels['version_nodes']}
        direct = {tuple(edge) for edge in oracle['dependency_edges'] if edge[1] in visible}
        transitive = {(parent, child) for child in visible for parent in oracle['transitive_dependencies'][child]}
        if (set(nodes) != visible
                or {key for key, node in nodes.items() if node['status'] == 'current'} != current
                or {tuple(edge) for edge in labels['direct_def_use_edges']} != direct
                or {tuple(edge) for edge in labels['strict_ancestor_edges']} != transitive
                or labels.get('output_visible') is not False or 'output' in labels):
            raise ValueError('prefix definitions, current versions or dependency labels differ')
        prefix = '\n'.join(row['canonical_source'].splitlines()[:checkpoint+1]) + '\n0'
        if relationships.labels_at(prefix, checkpoint, SLOTS) != labels:
            raise ValueError('prefix targets expose unseen assignments or output')
    final = row['targets']['final_query_relationships']
    if (final != relationships.labels_at(row['canonical_source'], 7, SLOTS, output_visible=True)
            or final['output']['structural_ancestors'] != oracle['transitive_dependencies']['output']):
        raise ValueError('actual query ancestry differs')


def _python_validate(sources):
    sources = sorted(sources)
    for start in range(0, len(sources), 128):
        batch = sources[start:start+128]
        ordinary = python_oracle(batch)
        if len(ordinary) != len(batch): raise ValueError('independent Python coverage differs')
        for source, actual in zip(batch, ordinary):
            oracle = execute(source)
            if (actual['answer'] != oracle['expected_answer']
                    or actual['trace'] != [point['values'] for point in oracle['execution_trace']]):
                raise ValueError('independent Python full trace differs')
    return len(sources)


def _overlap(config, rows):
    result = []
    new_source = {row['source'] for row in rows}
    new_canonical = {ast.dump(ast.parse(row['canonical_source'])) for row in rows}
    new_alpha = {alpha_skeleton(row['canonical_source']) for row in rows}
    for entry in config.get('overlap_sources', []):
        path = _safe(entry['path'])
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError('bounded old discovery source bank required')
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry['sha256']:
            raise ValueError('old source overlap checksum differs')
        previous = [json.loads(line) for line in payload.splitlines() if line.strip()]
        if (not previous or len(previous) > 25_000 or any(
                not isinstance(row, dict) or row.get('split') not in ('train', 'development')
                or row.get('evaluation_role') not in ('discovery_relationship_routing_v1',
                    'overnight_relationship_discovery_v1') for row in previous)):
            raise ValueError('only bounded old discovery relationship source rows permitted')
        old_source = {row['source'] for row in previous}
        old_canonical = {ast.dump(ast.parse(row['canonical_source'])) for row in previous}
        old_alpha = {alpha_skeleton(row['canonical_source']) for row in previous}
        result.append(dict(path=str(path), sha256=entry['sha256'], rows=len(previous),
            exact_surface_sources=len(new_source & old_source),
            canonical_ast_sources=len(new_canonical & old_canonical),
            alpha_structures=len(new_alpha & old_alpha), metadata_only=True))
    return result


def validate_rows(config, rows, independent=False):
    """Check complete grouping, actual version targets and independent traces."""
    _config(config)
    if type(independent) is not bool or not isinstance(rows, list) or rows != make_rows(config):
        raise ValueError('complete exact declared schedule source/target factorial required')
    if len(rows) != N_ROWS or len({row['id'] for row in rows}) != N_ROWS:
        raise ValueError('unique fixed 2,016-case schedule bank required')
    fingerprints = {name: defaultdict(set) for name in ('surface_source', 'canonical_ast', 'alpha_structure',
        'ordered_schedule', 'canonical_ssa_graph')}
    split_groups = defaultdict(set); prefix_groups = {}; numeric = defaultdict(set)
    programs = set(); obsolete_copies = set(); max_version = 0; prefix_checks = 0
    final_graphs = set()
    for row in rows:
        oracle = execute(row['canonical_source']); actual = execute(row['source'])
        if (oracle['execution_trace'] != row['targets']['canonical_execution_trace']
                or oracle['expected_answer'] != row['expected_answer']
                or actual['expected_answer'] != oracle['expected_answer']):
            raise ValueError('canonical/surface trace or answer differs')
        _check_oracle_labels(row, oracle)
        split = row['split']; split_groups[split].add(row['component_id'])
        graph = row['targets']['prefix_relationships'][-1]
        canonical, _ = _canonical_graph(graph)
        if 'schedule-graph:'+digest(canonical)[:24] != row['component_id']:
            raise ValueError('actual SSA graph does not match declared grouping')
        final_graphs.add(digest(graph))
        numeric[row['component_id']].add(row['numeric_seed'])
        for name, key in (('surface_source', row['source']),
                ('canonical_ast', ast.dump(ast.parse(row['canonical_source']))),
                ('alpha_structure', alpha_skeleton(row['canonical_source'])),
                ('ordered_schedule', row['ordered_schedule_canonical_id']),
                ('canonical_ssa_graph', row['component_id'])):
            fingerprints[name][key].add(split)
        slots = {row['rename_map'][name]: slot for name, slot in SLOTS.items()}
        for checkpoint, labels in enumerate(row['targets']['prefix_relationships']):
            prefix = '\n'.join(row['source'].splitlines()[:checkpoint+1])
            identity = (prefix, checkpoint)
            proof = digest(labels)
            if identity in prefix_groups and prefix_groups[identity] != proof:
                raise ValueError('identical visible source prefixes have inconsistent labels')
            prefix_groups[identity] = proof
            if relationships.labels_at(row['source'], checkpoint, slots) != labels:
                raise ValueError('canonical/surface prefix labels differ')
            prefix_checks += 1
        if relationships.labels_at(row['source'], 7, slots, output_visible=True) != row['targets']['final_query_relationships']:
            raise ValueError('canonical/surface output labels differ')
        for node in graph['version_nodes']:
            max_version = max(max_version, node['version'])
            if node['statement'] >= 4 and node['status'] == 'obsolete':
                obsolete_copies.add((row['raw_template_id'], node['id']))
        programs.update((row['canonical_source'], row['source']))
    overlap = {name: sum(len(splits) > 1 for splits in values.values())
               for name, values in fingerprints.items()}
    if (any(overlap.values()) or split_groups['train'] & split_groups['development']
            or not split_groups['train'] or not split_groups['development']
            or any(seeds != set(config['numeric_seeds']) for seeds in numeric.values())):
        raise ValueError('split leakage or incomplete numeric relatives')
    templates = _templates()
    example = next(row for row in rows if row['destination_schedule'] == [0, 0, 1, 0])
    return dict(rows=len(rows), split_rows=dict(Counter(row['split'] for row in rows)),
        raw_schedule_count=28, permutation_schedules=24, repeated_destination_schedules=4,
        repeated_destination_sequences=[list(item) for item in REPEATED_SCHEDULES],
        parent_patterns=list(PARENT_PATTERNS), raw_schedule_parent_templates=len(templates),
        effective_ordered_schedule_units=len({item['ordered_schedule_canonical_id'] for item in templates}),
        effective_canonical_graph_units=len(numeric),
        split_canonical_graph_units={key: len(value) for key, value in split_groups.items()},
        raw_templates_per_canonical_graph=dict(sorted(Counter(item['component_id'] for item in templates).items())),
        distinct_labeled_definition_graphs=len(final_graphs), numeric_seeds=list(config['numeric_seeds']),
        numeric_groups=len(numeric)*3, lexical_realizations=2, query_slots=list(range(4)),
        maximum_assignment_version=max_version, obsolete_copy_definitions_across_templates=len(obsolete_copies),
        prefix_label_checks=prefix_checks, distinct_visible_prefix_groups=len(prefix_groups),
        prefix_future_information_excluded=True, cross_split_overlap=overlap,
        independent_python_programs=_python_validate(programs) if independent else 0,
        independent_python_passed=independent, old_source_overlap=_overlap(config, rows),
        fixed_schedule_counterexample=dict(destination_schedule=example['destination_schedule'],
            actual_definitions=[point['definition'] for point in example['targets']['canonical_execution_trace']],
            statement_5_read_from=example['targets']['prefix_relationships'][5]['uses'][-1]['referent'],
            prior_fixed_scaffold_expected_definition_at_statement_5='v1@2',
            semantics='Actual repeated copies create v0@3 and v0@4; never coerce to fixed v0,v1,v2,v3 destinations.'))


def _report(config, result):
    return '\n'.join(['# Varied copy and overwrite schedule target preparation', '',
        f"Prepared {result['rows']:,} source rows: {result['split_rows']['train']:,} TRAIN and "
        f"{result['split_rows']['development']:,} DEV. No model or tokenizer was queried.", '',
        f"All {result['permutation_schedules']} destination permutations and {result['repeated_destination_schedules']} "
        f"explicit repeated schedules × three parent patterns produce {result['raw_schedule_parent_templates']} raw templates. "
        f"These collapse to {result['effective_ordered_schedule_units']} slot-canonical ordered units and "
        f"{result['effective_canonical_graph_units']} canonical SSA graph families. "
        f"Splits contain {result['split_canonical_graph_units']['train']} TRAIN and "
        f"{result['split_canonical_graph_units']['development']} DEV graph families; every numeric, lexical, "
        'query and equivalent-graph relative stays with its family.', '',
        f"Each source has four literal roots and four copies. Repeated destinations reach assignment version "
        f"{result['maximum_assignment_version']}; obsolete copied definitions are retained. "
        'The existing generic `relationships.labels_at` supplies all eight assignment-prefix targets and the actual final-query ancestry.', '',
        f"All cross-split source/AST/alpha/schedule/graph overlap counts are zero. "
        f"Checked {result['prefix_label_checks']:,} surface-prefix labels and "
        f"{result['independent_python_programs']:,} distinct full ordinary-Python program traces. "
        'No learned target/readout compatibility is asserted.', '',
        'For destination sequence 0,0,1,0, assignment 5 creates v0@3; the old fixed scaffold expects v1@2. '
        'Reusing that scaffold would label a different program.', '',
        f"Optional old discovery-bank overlap audits: {json.dumps(result['old_source_overlap'], sort_keys=True)}.", '',
        f"Dataset SHA256: `{result['dataset_sha256']}`. Review: `{config['review']}`.", '',
        '## Scope', '', *['- '+item for item in LIMITATIONS], ''])


def build(config):
    """Independently validate and immutably publish only this new source bank."""
    paths = _config(config)
    rows = make_rows(config)
    result = validate_rows(config, rows, independent=True)
    payload = ''.join(json.dumps(row, sort_keys=True, allow_nan=False)+'\n' for row in rows).encode()
    if len(payload) > MAX_BYTES: raise ValueError('bounded schedule bank exceeded')
    result.update(status='passed', evaluation_role=ROLE, config_hash=digest(config), config=config,
        dataset=str(paths['dataset']), dataset_sha256=hashlib.sha256(payload).hexdigest(), source=code_identity(),
        model_queries=0, new_model_queries=0, new_fits=0, targets_prepared_only=True,
        learned_readout_compatible=False, model_or_tokenizer_loaded=False, activation_arrays_read=False,
        graph_decoding_performed=False, generated_holdouts_opened=False, limitations=LIMITATIONS)
    report = _report(config, result).encode()
    result['report'] = dict(path=str(paths['report']), sha256=hashlib.sha256(report).hexdigest())
    manifest = dict(schema_version=1, status='complete', evaluation_role=ROLE, role=ROLE,
        sha256=result['dataset_sha256'], rows=result['rows'], split_rows=result['split_rows'],
        generation_config_hash=digest(config), generation_config=config, source=result['source'],
        review=str(paths['review']), independent_python_passed=True, model_queries=0, new_model_queries=0,
        targets_prepared_only=True, learned_readout_compatible=False, generated_holdouts_opened=False,
        raw_schedule_count=result['raw_schedule_count'], raw_schedule_parent_templates=result['raw_schedule_parent_templates'],
        effective_ordered_schedule_units=result['effective_ordered_schedule_units'],
        effective_canonical_graph_units=result['effective_canonical_graph_units'],
        split_canonical_graph_units=result['split_canonical_graph_units'],
        maximum_assignment_version=result['maximum_assignment_version'], cross_split_overlap=result['cross_split_overlap'])
    outputs = [(paths['dataset'], payload), (paths['manifest'], _json_bytes(manifest)),
        (paths['report'], report), (paths['review'], _json_bytes(result))]
    for path, data in outputs:
        if path.exists() and path.read_bytes() != data:
            raise ValueError('immutable schedule artifact already differs: '+str(path))
    for path, data in outputs: _publish(path, data)
    from .experiment_log import note_artifact
    note_artifact(paths['review'].resolve())
    return result
