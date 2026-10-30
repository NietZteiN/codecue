"""Group-weighted support audit for numeric relationship TARGETS, never features."""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import json
from pathlib import Path

from . import algebraic_relationships as algebraic, relationship_audit as structural
from .datasets import digest
from .published_benchmarks import immutable
from .registry import code_identity

ROLE = 'discovery_algebraic_relationship_target_audit_v1'
LIMITATION = (
    'Prepared numeric oracle targets only; no decoder, activations, model response '
    'or new model query. Only current values after each visible assignment are '
    'used; hidden outputs, future assignments and output relevance are excluded. '
    'Equality/order and additive/subtractive identities are boolean tasks; signed '
    'difference is a separate numeric regression target. Constant/all-false '
    'boolean cells can be solved by a trivial prior and do not establish a useful '
    'decoding task. Each structural group has equal weight after deduplicating '
    'current numeric states within that group; numeric/naming relatives are not '
    'independent replications. A later direct relation probe must be compared '
    'with relations derived from independently decoded values. Relation recovery '
    'alone cannot establish a dedicated relational code, causal use, ownership '
    'or mechanism C. Numeric oracle values and all relations here are TARGETS, '
    'not readout/prediction features.'
)


def _metadata(config):
    if (not isinstance(config, dict) or set(config) != {'evaluation_role', 'dataset', 'dataset_sha256', 'output', 'report'}
            or config.get('evaluation_role') != ROLE):
        raise ValueError('explicit discovery algebraic-target audit role/configuration required')
    return structural._metadata({**config, 'evaluation_role': structural.ROLE})


def _check(labels, checkpoint, expected):
    if (not isinstance(labels, dict) or set(labels) != {'schema_version', 'checkpoint', 'target_semantics',
            'current_slots', 'ordered_pairs', 'ordered_triples'} or labels.get('schema_version') != 1
            or type(labels.get('checkpoint')) is not int or labels['checkpoint'] != checkpoint
            or labels.get('target_semantics') != 'numeric_oracle_targets_not_model_features'
            or labels.get('current_slots') != expected):
        raise ValueError('current numeric TARGET state differs from independent visible-prefix execution')
    if any(type(item[key]) is not int for item in labels['current_slots'] for key in ('slot', 'version', 'statement', 'value')):
        raise ValueError('strict integer current numeric TARGET metadata required')
    state = {item['canonical_name']: item['value'] for item in expected}
    pairs = labels['ordered_pairs']; triple_rows = labels['ordered_triples']
    expected_pairs = {(a, b) for a in state for b in state if a != b}
    expected_triples = {(a, b, c) for a in state for b in state for c in state if len({a, b, c}) == 3}
    if not isinstance(pairs, list) or not isinstance(triple_rows, list): raise ValueError('complete numeric relation target lists required')
    pair_lookup = {}; triples = {}
    for item in pairs:
        if not isinstance(item, dict) or set(item) != {'left', 'right', 'equal', 'less_than', 'difference'}:
            raise ValueError('exact ordered-pair numeric target schema required')
        key = item['left'], item['right']
        if (key not in expected_pairs or key in pair_lookup or type(item['equal']) is not bool
                or type(item['less_than']) is not bool or type(item['difference']) is not int
                or item['equal'] != (state[key[0]] == state[key[1]])
                or item['less_than'] != (state[key[0]] < state[key[1]])
                or item['difference'] != state[key[0]]-state[key[1]]):
            raise ValueError('ordered-pair equality/order/difference targets differ')
        pair_lookup[key] = item
    for item in triple_rows:
        if not isinstance(item, dict) or set(item) != {'first', 'second', 'third', 'sum_equals_third', 'difference_equals_third'}:
            raise ValueError('exact distinct-slot triple target schema required')
        key = item['first'], item['second'], item['third']
        if (key not in expected_triples or key in triples or type(item['sum_equals_third']) is not bool
                or type(item['difference_equals_third']) is not bool
                or item['sum_equals_third'] != (state[key[0]]+state[key[1]] == state[key[2]])
                or item['difference_equals_third'] != (state[key[0]]-state[key[1]] == state[key[2]])):
            raise ValueError('distinct-slot additive/subtractive targets differ')
        triples[key] = item
    if set(pair_lookup) != expected_pairs or set(triples) != expected_triples:
        raise ValueError('complete ordered pair/triple target coverage required')
    for (a, b), item in pair_lookup.items():
        reverse = pair_lookup[b, a]
        if (item['equal'] != reverse['equal'] or item['difference'] != -reverse['difference']
                or int(item['equal'])+int(item['less_than'])+int(reverse['less_than']) != 1):
            raise ValueError('pair symmetry/order/difference antisymmetry failed')
    if any(item['sum_equals_third'] != triples[b, a, c]['sum_equals_third'] for (a, b, c), item in triples.items()):
        raise ValueError('sum target commutativity failed')


def audit_rows(rows):
    cells = defaultdict(lambda: defaultdict(dict)); cache = {}; views = 0
    state_groups = defaultdict(set); mapping_frames = set()
    for row in rows:
        tree, slots, surface_slots, _ = structural._source(row)
        group = row.get('cluster_id', row['template_id']); state = {}; versions = Counter(); locations = {}
        for index, assignment in enumerate(tree.body[:-1]):
            # The restricted AST allowlist excludes calls/imports/attributes;
            # ordinary Python arithmetic provides an independent numeric check.
            value = eval(compile(ast.Expression(assignment.value), '<visible relationship prefix>', 'eval'), {'__builtins__': {}}, state)
            if type(value) is not int or abs(value) > 64: raise ValueError('visible current numeric state exceeds declared target bounds')
            name = assignment.targets[0].id; state[name] = value; versions[name] += 1; locations[name] = index
            expected = [dict(canonical_name=f'v{slots[name]}', slot=slots[name], version=versions[name],
                definition=f'v{slots[name]}@{versions[name]}', statement=locations[name], value=state[name])
                for name in sorted(state, key=slots.__getitem__)]
            key = row['canonical_source'], tuple(sorted(slots.items())), index
            if key not in cache: cache[key] = algebraic.labels_at(row['canonical_source'], index, slots)
            labels = cache[key]
            if labels != algebraic.labels_at(row['source'], index, surface_slots):
                raise ValueError('canonical/surface current algebraic targets differ')
            _check(labels, index, expected)
            frame = tuple(item['slot'] for item in expected)
            mapping_hash = digest(sorted((name, slots[name]) for name in state)); mapping_frames.add(mapping_hash)
            context = (row['split'], row['family'], index+1, frame, mapping_hash)
            numeric_state = digest([(item['slot'], item['value']) for item in expected])
            state_groups[(*context, group)].add(numeric_state); views += 1
            for pair in labels['ordered_pairs']:
                identities = (pair['left'], pair['right'])
                for target in ('equal', 'less_than', 'difference'):
                    cells[(*context, target, identities)][group][numeric_state] = pair[target]
            for triple in labels['ordered_triples']:
                identities = (triple['first'], triple['second'], triple['third'])
                for target in ('sum_equals_third', 'difference_equals_third'):
                    cells[(*context, target, identities)][group][numeric_state] = triple[target]
    boolean = []; difference = []
    for key, groups in sorted(cells.items(), key=lambda item: str(item[0])):
        split, family, length, frame, mapping_hash, target, identities = key
        base = dict(split=split, family=family, prefix_assignments=length, visible_slot_ids=list(frame),
            canonical_slot_mapping_sha256=mapping_hash, target=target, ordered_slots=list(identities), structural_groups=len(groups))
        if target == 'difference':
            classes = sorted({value for observed in groups.values() for value in observed.values()})
            histogram = {str(value): sum(sum(item == value for item in observed.values())/len(observed)
                for observed in groups.values())/len(groups) for value in classes}
            difference.append({**base, 'target_type': 'signed_integer_regression_target', 'difference_classes': classes,
                'group_weighted_class_histogram': histogram,
                'groups_supporting_class': {str(value): sum(value in observed.values() for observed in groups.values()) for value in classes}})
        else:
            true_groups = sum(any(observed.values()) for observed in groups.values())
            false_groups = sum(not all(observed.values()) for observed in groups.values())
            prevalence = sum(sum(observed.values())/len(observed) for observed in groups.values())/len(groups)
            boolean.append({**base, 'target_type': 'boolean_relation_target', 'true_groups': true_groups,
                'false_groups': false_groups, 'mixed_groups': sum(len(set(observed.values())) == 2 for observed in groups.values()),
                'minority_support_groups': min(true_groups, false_groups),
                'nontrivial_class_support': true_groups > 0 and false_groups > 0,
                'all_false': true_groups == 0, 'all_true': false_groups == 0,
                'group_weighted_true_fraction': prevalence, 'group_weighted_majority_prior': max(prevalence, 1-prevalence)})
    return dict(assignment_prefix_views=views, distinct_group_numeric_states=sum(map(len, state_groups.values())),
        canonical_slot_mapping_frames=len(mapping_frames), boolean_target_cells=boolean, difference_target_cells=difference,
        nontrivial_boolean_cells=sum(item['nontrivial_class_support'] for item in boolean),
        all_false_boolean_cells=sum(item['all_false'] for item in boolean),
        all_true_boolean_cells=sum(item['all_true'] for item in boolean),
        equality_symmetry_checked=True, less_than_reverse_checked=True, difference_antisymmetry_checked=True,
        sum_commutativity_checked=True, canonical_surface_prefix_equivalence_checked=True,
        independent_python_prefix_values_checked=True, output_targets=None,
        statistical_unit='Equal-weight structural groups; deduplicated current numeric states within each group/context.')


def run(config):
    dataset = _metadata(config); rows, splits = structural._rows(dataset)
    audited = audit_rows(rows)
    result = dict(status='prepared_targets_only', evaluation_role=ROLE, config_hash=digest(config), analysis_source=code_identity(),
        dataset=str(dataset), dataset_sha256=config['dataset_sha256'], rows=len(rows),
        split_rows=dict(Counter(row['split'] for row in rows)),
        structural_groups=len({row.get('cluster_id', row['template_id']) for row in rows}),
        split_group_overlap={name: 0 for name in splits}, **audited,
        learned_relationship_decoder_fitted=False, numeric_values_are_targets_not_features=True,
        training_ready_relation_matrix_exported=False, independent_value_probe_baseline_required=True,
        activation_arrays_opened=False, model_responses_opened=False, new_model_queries=0,
        generated_holdouts_opened=False, mechanism_C_fitted=False, limitation=LIMITATION)
    lines = ['# Prefix-visible algebraic relationship TARGET audit', '', LIMITATION, '',
        f"{result['rows']:,} value-free source rows and {result['structural_groups']} structural groups; {audited['assignment_prefix_views']:,} assignment-prefix views. No group crosses training/development.", '',
        f"Boolean cells: {len(audited['boolean_target_cells']):,}; both-class support: {audited['nontrivial_boolean_cells']:,}; all false: {audited['all_false_boolean_cells']:,}; all true: {audited['all_true_boolean_cells']:,}.", '',
        f"Signed-difference cells: {len(audited['difference_target_cells']):,}. Their integer target distributions are reported separately from boolean classification.", '',
        'Every ordered slot-pair/triple, split, visible slot frame and prefix length remains in the compact JSON. Support/prior weights are over structural groups, not row counts. Repeated naming and numeric states are deduplicated within each group.', '',
        'This is target preparation. Later direct relation probes require a matched comparison with relationships derived from independently decoded values; success alone would not identify a dedicated relational representation.', '']
    payloads = {Path(config['output']): (json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n').encode(),
        Path(config['report']): '\n'.join(lines).encode()}
    if len(payloads[Path(config['output'])]) > structural.MAX_METADATA_BYTES: raise ValueError('compact algebraic audit exceeds metadata byte limit')
    for path, content in payloads.items():
        if path.exists() and path.read_bytes() != content: raise ValueError('immutable algebraic target audit differs: '+str(path))
    for path, content in payloads.items(): immutable(path, content)
    return result
