"""Value-free tiny discovery corpora; no model or activation access."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from codecue.binding import relationship_audit as audit, relationships
from codecue.binding.interpreter import execute
from codecue.binding.programs import rename

PROGRAM = 'v0 = 1\nv1 = 2\nv2 = v0\nv0 = v1\nv2'
REWIRED = 'v0 = 1\nv1 = 2\nv2 = v1\nv0 = v1\nv2'


def row(source=PROGRAM, *, split='train', base='base1', group='group1', condition='neutral', lexical=0, identity=None):
    names = sorted({node.id for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Name)})
    mapping = {name: f'{split}_{condition}_{lexical}_{name}' for name in names}
    truth = execute(source)
    return dict(evaluation_role=audit.ROLE, id=identity or f'{base}:{condition}:{lexical}',
        base_id=base, template_id=group+':template', cluster_id=group, family='tiny', split=split,
        control_kind='primary', condition=condition, lexical_realization=lexical,
        canonical_source=source, source=rename(source, mapping), rename_map=mapping,
        variable_slots={name: index for index, name in enumerate(names)},
        execution_trace=[{key: point[key] for key in ('statement', 'definition', 'uses')} for point in truth['execution_trace']])


def config(tmp_path, rows):
    path = tmp_path/'sources.jsonl'
    path.write_text(''.join(json.dumps(value, sort_keys=True)+'\n' for value in rows))
    return dict(evaluation_role=audit.ROLE, dataset=str(path), dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        output=str(tmp_path/'target_audit_review.json'), report=str(tmp_path/'target_audit.md'))


def test_complete_prefix_audit_retains_obsolete_definitions_and_no_hidden_output(tmp_path):
    rows = [row(), row(condition='informative', lexical=1),
        row(REWIRED, split='development', base='dev1', group='devgroup')]
    result = audit.run(config(tmp_path, rows))
    assert result['status'] == 'prepared_targets_only'
    assert result['rows'] == 3 and result['source_bases'] == result['structural_groups'] == 2
    assert result['assignment_checkpoint_views'] == 12 and result['final_output_checkpoint_views'] == 3
    assert result['graph_views'] == 15
    assert result['learned_relationship_decoder_fitted'] is False
    assert result['training_ready_relation_matrix_exported'] is False
    assert result['new_model_queries'] == 0 and result['expected_answers_used_as_features'] is False
    assert result['activation_arrays_opened'] is result['model_responses_opened'] is False
    assert result['version_node_observations']['obsolete'] > 0
    assert result['relation_structural_group_support']['version_succession']['positive_groups'] == 2
    assert result['prefix_only_output_labels'] is None
    assert all('output' not in graph for graph in result['semantic_graph_catalog'].values() if not graph['output_visible'])
    assert all(cell['output_visible'] for cell in result['current_slot_pair_support'] if cell['relation'] == 'output_ancestor')
    assert any(cell['shared_semantic_graphs'] > 0 and not cell['output_visible'] for cell in result['cross_split_semantic_graph_overlap_by_prefix'])
    assert all(value == 0 for value in result['split_group_overlap'].values())
    assert audit.run(config(tmp_path, rows)) == result


def test_numeric_naming_relatives_do_not_inflate_structural_support(tmp_path):
    first = row(); other = row(REWIRED, base='base2', group='group2')
    # Config writer deliberately keeps fixture directories explicit.
    (tmp_path/'small').mkdir(); (tmp_path/'large').mkdir()
    small = audit.run(config(tmp_path/'small', [first, other]))
    copies = [row(condition=condition, lexical=lexical) for condition in ('neutral', 'informative', 'misleading') for lexical in (0, 1)]
    large = audit.run(config(tmp_path/'large', copies+[other]))
    assert large['rows'] > small['rows']
    assert large['structural_groups'] == small['structural_groups'] == 2
    assert large['current_slot_pair_support'] == small['current_slot_pair_support']
    assert large['graph_variation_by_visible_prefix'] == small['graph_variation_by_visible_prefix']
    assert large['nontrivial_current_slot_pair_cells'] > 0


def test_same_numeric_base_can_have_explicit_counterfactual_rewirings(tmp_path):
    first = row(identity='variant0'); second = row(REWIRED, identity='variant1')
    result = audit.run(config(tmp_path, [first, second]))
    assert result['source_bases'] == result['structural_groups'] == 1
    assert result['matched_condition_and_lexical_graphs_consistent'] is True
    assert any(cell['mixed_label_groups'] == 1 for cell in result['current_slot_pair_support'])
    assert any(cell['distinct_graphs'] == 2 for cell in result['graph_variation_by_visible_prefix'])


def test_independent_assignment_order_is_not_new_semantic_graph_variation(tmp_path):
    reordered = 'v1 = 2\nv0 = 1\nv2 = v0\nv0 = v1\nv2'
    result = audit.run(config(tmp_path, [row(identity='order0'), row(reordered, identity='order1')]))
    final = [cell for cell in result['graph_variation_by_visible_prefix'] if cell['prefix_assignments'] == 4 and not cell['output_visible']]
    assert len(final) == 1
    assert final[0]['distinct_graphs'] == 1 and final[0]['distinct_position_labeled_graphs'] == 2


def test_changed_future_and_output_leave_prefix_targets_unchanged(tmp_path):
    future = 'v0 = 1\nv1 = 2\nv2 = v0\nv0 = v0\nv1'
    result = audit.run(config(tmp_path, [row(identity='future0'), row(future, identity='future1')]))
    for cell in result['graph_variation_by_visible_prefix']:
        if cell['prefix_assignments'] <= 3: assert cell['distinct_graphs'] == 1
    output_only = PROGRAM.rsplit('\n', 1)[0]+'\nv1'
    (tmp_path/'output').mkdir()
    other = audit.run(config(tmp_path/'output', [row(identity='query0'), row(output_only, identity='query1')]))
    final = [cell for cell in other['graph_variation_by_visible_prefix'] if cell['prefix_assignments'] == 4]
    assert {cell['output_visible']: cell['distinct_graphs'] for cell in final} == {False: 1, True: 2}


def test_explicit_slot_maps_do_not_false_collide_for_identical_ast_prefix(tmp_path):
    first = row(identity='map0'); second = row(identity='map1')
    second['variable_slots'] = {'v0': 1, 'v1': 0, 'v2': 2}
    result = audit.run(config(tmp_path, [first, second]))
    assert result['exact_duplicate_prefix_graphs_consistent'] is True


@pytest.mark.parametrize('change', ['role', 'sha', 'reserved_source', 'reserved_output', 'unknown_config'])
def test_config_role_paths_and_checksum_fail_before_labels(tmp_path, monkeypatch, change):
    cfg = config(tmp_path, [row()])
    if change == 'role': cfg['evaluation_role'] = 'final_evaluation'
    elif change == 'sha': cfg['dataset_sha256'] = '0'*64
    elif change == 'reserved_source': cfg['dataset'] = '/tmp/final/source.jsonl'
    elif change == 'reserved_output': cfg['output'] = '/tmp/final/audit.json'
    else: cfg['use_expected_answers'] = True
    monkeypatch.setattr(relationships, 'labels_at', lambda *a, **k: pytest.fail('labels precede source role/SHA guard'))
    with pytest.raises(ValueError): audit.run(cfg)
    assert not Path(cfg['report']).exists()


@pytest.mark.parametrize('change', ['late_test', 'base_overlap', 'template_overlap', 'cluster_overlap',
    'row_role', 'nonprimary', 'oracle', 'nested_oracle', 'trace_values', 'duplicate_id'])
def test_all_rows_and_group_overlap_are_checked_before_any_graph_label(tmp_path, monkeypatch, change):
    first = row(); second = row(REWIRED, split='development', base='dev1', group='devgroup')
    if change == 'late_test': second['split'] = 'test'
    elif change == 'base_overlap': second['base_id'] = first['base_id']
    elif change == 'template_overlap': second['template_id'] = first['template_id']
    elif change == 'cluster_overlap': second['cluster_id'] = first['cluster_id']
    elif change == 'row_role': second['evaluation_role'] = 'final_evaluation'
    elif change == 'nonprimary': second['control_kind'] = 'binding_swap'
    elif change == 'oracle': second['expected_answer'] = 1
    elif change == 'nested_oracle': second['extra_targets'] = {'expected_answer': 1}
    elif change == 'trace_values': second['execution_trace'][0]['value'] = 1
    else: second['id'] = first['id']
    cfg = config(tmp_path, [first, second])
    monkeypatch.setattr(relationships, 'labels_at', lambda *a, **k: pytest.fail('labels precede complete corpus metadata guard'))
    with pytest.raises(ValueError): audit.run(cfg)
    assert not Path(cfg['output']).exists()


@pytest.mark.parametrize('change', ['inverse_map', 'trace_definition', 'trace_use', 'trace_length'])
def test_surface_prefix_and_stripped_trace_are_independently_checked(tmp_path, monkeypatch, change):
    value = row()
    if change == 'inverse_map': value['rename_map']['v0'], value['rename_map']['v1'] = value['rename_map']['v1'], value['rename_map']['v0']
    elif change == 'trace_definition': value['execution_trace'][0]['definition'] = 'v0@2'
    elif change == 'trace_use': value['execution_trace'][2]['uses'][0]['definition'] = 'v1@1'
    else: value['execution_trace'].pop()
    monkeypatch.setattr(relationships, 'labels_at', lambda *a, **k: pytest.fail('invalid visible source/trace precedes graph labels'))
    with pytest.raises(ValueError): audit.run(config(tmp_path, [value]))


@pytest.mark.parametrize('change', ['drop_occurrence', 'wrong_output', 'future_edge', 'inconsistent_duplicate'])
def test_independent_graph_checks_reject_wrong_use_and_future_targets(tmp_path, monkeypatch, change):
    source = 'v0 = 1\nv1 = 2\nv2 = v0 - v0\nv0 = v1\nv2'
    values = [row(source, identity='first'), row(source, condition='informative', identity='second')]
    original = relationships.labels_at
    calls = []
    def broken(program, checkpoint, canonical_slots=None, *, output_visible=False):
        result = original(program, checkpoint, canonical_slots, output_visible=output_visible); calls.append(True)
        if change == 'drop_occurrence' and checkpoint >= 2: result['uses'].pop()
        elif change == 'wrong_output' and output_visible:
            result['output']['direct_referents'] = ['v1@1']; result['output']['structural_ancestors'] = ['v1@1']
        elif change == 'future_edge' and checkpoint == 0: result['direct_def_use_edges'].append(['v0@1', 'v0@2'])
        elif change == 'inconsistent_duplicate' and len(calls) > 2: result['checkpoint'] += 1
        return result
    monkeypatch.setattr(relationships, 'labels_at', broken)
    cfg = config(tmp_path, values)
    with pytest.raises(ValueError): audit.run(cfg)
    assert not Path(cfg['output']).exists()


def test_outputs_are_immutable_and_status_stays_target_preparation(tmp_path):
    cfg = config(tmp_path, [row()]); result = audit.run(cfg)
    assert json.loads(Path(cfg['output']).read_text()) == result
    assert 'not measured decoding performance' in Path(cfg['report']).read_text()
    Path(cfg['output']).write_text('{}')
    with pytest.raises(ValueError, match='immutable'): audit.run(cfg)
