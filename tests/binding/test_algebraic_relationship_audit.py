"""Finite synthetic numeric TARGET audits; no learned decoding/model calls."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from codecue.binding import algebraic_relationship_audit as audit, algebraic_relationships as labels
from test_relationship_audit import row, config as structural_config

ADDITIVE = 'v0 = 2\nv1 = 3\nv2 = v0 + v1\nv0 = v0\nv2'
EQUAL = 'v0 = 2\nv1 = 2\nv2 = v0 + v1\nv0 = v0\nv2'


def config(tmp_path, rows):
    result = structural_config(tmp_path, rows); result['evaluation_role'] = audit.ROLE
    return result


def test_prefix_targets_group_support_and_regression_are_separate(tmp_path):
    rows = [row(ADDITIVE, identity='numeric0'), row(EQUAL, identity='numeric1'),
        row(ADDITIVE, split='development', base='dev1', group='dev1')]
    result = audit.run(config(tmp_path, rows))
    assert result['status'] == 'prepared_targets_only'
    assert result['rows'] == 3 and result['structural_groups'] == 2
    assert result['assignment_prefix_views'] == 12
    assert result['learned_relationship_decoder_fitted'] is False
    assert result['numeric_values_are_targets_not_features'] is True
    assert result['independent_value_probe_baseline_required'] is True
    assert result['new_model_queries'] == 0 and result['output_targets'] is None
    assert result['activation_arrays_opened'] is result['model_responses_opened'] is False
    assert result['equality_symmetry_checked'] and result['less_than_reverse_checked']
    assert result['difference_antisymmetry_checked'] and result['sum_commutativity_checked']
    assert result['independent_python_prefix_values_checked']
    selected = [cell for cell in result['boolean_target_cells'] if cell['split'] == 'train'
        and cell['prefix_assignments'] == 4 and cell['target'] == 'equal' and cell['ordered_slots'] == ['v0', 'v1']]
    assert len(selected) == 1
    assert selected[0]['true_groups'] == selected[0]['false_groups'] == selected[0]['mixed_groups'] == 1
    assert selected[0]['group_weighted_true_fraction'] == .5
    assert selected[0]['group_weighted_majority_prior'] == .5
    assert any(cell['all_false'] for cell in result['boolean_target_cells'])
    for cell in result['difference_target_cells']:
        assert cell['target_type'] == 'signed_integer_regression_target'
        assert sum(cell['group_weighted_class_histogram'].values()) == pytest.approx(1.)
        assert all(type(value) is int for value in cell['difference_classes'])


def test_duplicate_numeric_states_and_naming_relatives_do_not_add_group_weight(tmp_path):
    (tmp_path/'small').mkdir(); (tmp_path/'large').mkdir()
    base = row(ADDITIVE, identity='state0'); other = row(EQUAL, identity='state1')
    small = audit.run(config(tmp_path/'small', [base, other]))
    copies = [row(ADDITIVE, condition=condition, lexical=lexical) for condition in
        ('neutral', 'informative', 'misleading') for lexical in (0, 1)]
    large = audit.run(config(tmp_path/'large', copies+[other]))
    assert large['assignment_prefix_views'] > small['assignment_prefix_views']
    assert large['distinct_group_numeric_states'] == small['distinct_group_numeric_states']
    assert large['boolean_target_cells'] == small['boolean_target_cells']
    assert large['difference_target_cells'] == small['difference_target_cells']


def test_future_assignments_and_hidden_output_are_not_current_numeric_targets(tmp_path):
    future = 'v0 = 2\nv1 = 3\nv2 = v0 - v1\nv0 = 4\nv1'
    rows = [row(ADDITIVE, identity='past0'), row(future, identity='past1')]
    result = audit.run(config(tmp_path, rows))
    assert result['output_targets'] is None
    early = [cell for cell in result['boolean_target_cells'] if cell['prefix_assignments'] == 2]
    assert early and all(cell['mixed_groups'] == 0 for cell in early)
    assert any(cell['mixed_groups'] for cell in result['boolean_target_cells'] if cell['prefix_assignments'] >= 3)


@pytest.mark.parametrize('change', ['role', 'sha', 'reserved_source', 'reserved_output', 'unknown_key'])
def test_config_guards_precede_every_algebraic_label(tmp_path, monkeypatch, change):
    cfg = config(tmp_path, [row(ADDITIVE)])
    if change == 'role': cfg['evaluation_role'] = 'final_evaluation'
    elif change == 'sha': cfg['dataset_sha256'] = '0'*64
    elif change == 'reserved_source': cfg['dataset'] = '/tmp/final/sources.jsonl'
    elif change == 'reserved_output': cfg['output'] = '/tmp/final/audit.json'
    else: cfg['expected_answer_feature'] = True
    monkeypatch.setattr(labels, 'labels_at', lambda *a, **k: pytest.fail('role/path/SHA guard must precede labels'))
    with pytest.raises(ValueError): audit.run(cfg)


@pytest.mark.parametrize('change', ['test', 'group_overlap', 'oracle_field', 'trace_values'])
def test_whole_corpus_split_and_value_free_schema_guards_precede_labels(tmp_path, monkeypatch, change):
    first = row(ADDITIVE); second = row(EQUAL, split='development', base='dev1', group='dev1')
    if change == 'test': second['split'] = 'test'
    elif change == 'group_overlap': second['cluster_id'] = first['cluster_id']
    elif change == 'oracle_field': second['expected_answer'] = 4
    else: second['execution_trace'][0]['value'] = 2
    monkeypatch.setattr(labels, 'labels_at', lambda *a, **k: pytest.fail('all corpus guards must precede labels'))
    with pytest.raises(ValueError): audit.run(config(tmp_path, [first, second]))


@pytest.mark.parametrize('change', ['numeric_value', 'numeric_boolean', 'difference', 'equality', 'less_than',
    'missing_pair', 'sum', 'subtraction', 'missing_triple'])
def test_independent_numeric_execution_and_relation_invariants_reject_tampering(tmp_path, monkeypatch, change):
    original = labels.labels_at
    def broken(source, statement, canonical_slots=None):
        result = original(source, statement, canonical_slots)
        if change == 'numeric_value': result['current_slots'][0]['value'] += 1
        elif change == 'numeric_boolean': result['current_slots'][0]['value'] = 2.0
        elif len(result['ordered_pairs']) and change in ('difference', 'equality', 'less_than', 'missing_pair'):
            if change == 'difference': result['ordered_pairs'][0]['difference'] += 1
            elif change == 'equality': result['ordered_pairs'][0]['equal'] = not result['ordered_pairs'][0]['equal']
            elif change == 'less_than': result['ordered_pairs'][0]['less_than'] = not result['ordered_pairs'][0]['less_than']
            else: result['ordered_pairs'].pop()
        elif len(result['ordered_triples']) and change in ('sum', 'subtraction', 'missing_triple'):
            if change == 'sum': result['ordered_triples'][0]['sum_equals_third'] = not result['ordered_triples'][0]['sum_equals_third']
            elif change == 'subtraction': result['ordered_triples'][0]['difference_equals_third'] = not result['ordered_triples'][0]['difference_equals_third']
            else: result['ordered_triples'].pop()
        return result
    monkeypatch.setattr(labels, 'labels_at', broken)
    cfg = config(tmp_path, [row(ADDITIVE)])
    with pytest.raises(ValueError): audit.run(cfg)
    assert not Path(cfg['output']).exists()


def test_artifacts_remain_immutable_and_do_not_claim_a_learned_decoder(tmp_path):
    cfg = config(tmp_path, [row(ADDITIVE)])
    first = audit.run(cfg)
    assert audit.run(cfg) == first
    saved = json.loads(Path(cfg['output']).read_text())
    assert saved['training_ready_relation_matrix_exported'] is False
    assert 'independently decoded values' in Path(cfg['report']).read_text()
    Path(cfg['output']).write_text('{}')
    with pytest.raises(ValueError, match='immutable'): audit.run(cfg)
