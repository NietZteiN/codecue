"""Scientific boundary checks for the one-state, all-variable assay."""
from copy import deepcopy
import numpy as np
import pytest
from codecue.binding import arithmetic_global_state as study
from codecue.binding import arithmetic_semantic_audit as semantic_audit
from codecue.binding import arithmetic_semantic_controls as semantic
from codecue.binding import arithmetic_numeric_exploration as numeric


def test_all_four_target_layout_and_perfect_decode():
    values = np.asarray([[-96, -2, 0, 96], [1, 2, 3, -1], [0, 0, 0, 0]])
    scores = study.targets(values)
    assert scores.shape == (3, 824)
    guessed = study.predictions(scores)
    assert np.array_equal(guessed['scalar'], values)
    assert np.array_equal(guessed['categorical'], values)
    assert np.array_equal(guessed['relations'], study.relations(values))
    assert np.array_equal(scores[:, 776:], study.relations(values))


def test_relation_coordinates_are_unique_and_have_expected_arithmetic():
    assert len(set(study.COORDINATES)) == 48
    assert [sum(c[0] == kind for c in study.COORDINATES) for kind in study.TYPES] == [6, 6, 12, 24]
    v = np.asarray([[2, 3, 5, -1]])
    truth = study.relations(v)[0]
    for j, (kind, *slots) in enumerate(study.COORDINATES):
        numbers = [int(v[0, i]) for i in slots]
        expected = numbers[0] == numbers[1] if kind == 'eq' else numbers[0] < numbers[1] if kind == 'lt' else (
            numbers[0] + numbers[1] == numbers[2] if kind == 'sum' else numbers[0] - numbers[1] == numbers[2])
        assert truth[j] == expected
    assert truth[study.COORDINATES.index(('sum', 0, 1, 2))]
    assert truth[study.COORDINATES.index(('difference', 0, 1, 3))]


@pytest.mark.parametrize('bad', [np.zeros((2, 3), int), np.zeros((2, 4), float), np.full((2, 4), 97), np.full((2, 4), -97)])
def test_value_domain_rejects_bad_targets(bad):
    with pytest.raises(ValueError): study.targets(bad)


@pytest.mark.parametrize('bad', [np.zeros((2, 823)), np.full((2, 824), np.nan), np.full((2, 824), np.inf)])
def test_prediction_layout_and_finiteness(bad):
    with pytest.raises(ValueError): study.predictions(bad)


def test_support_deduplicates_lexical_realizations():
    truth = np.repeat(np.asarray([[True] * 48, [False] * 48]), 30, axis=0)
    bodies = np.repeat(['positive', 'negative'], 30)
    support = study.eligibility(truth, bodies)
    assert support['positive_bodies'] == [1] * 48
    assert support['negative_bodies'] == [1] * 48
    assert not any(support['eligible'])
    assert all(study.eligibility(truth, bodies, minimum=1)['eligible'])


def test_inconsistent_body_truth_fails():
    with pytest.raises(ValueError, match='inconsistent'):
        study.eligibility(np.asarray([[True] * 48, [False] * 48]), ['same', 'same'])


def test_rare_cells_and_missing_evaluation_classes_are_explicit():
    truth = np.zeros((3, 48), bool)
    panel = study.relation_metrics(truth, truth, ['a', 'b', 'c'], [True] * 48)
    assert panel['type_macro_balanced_accuracy'] is None
    assert all(c['positive'] == 0 and c['balanced_accuracy'] is None for c in panel['cells'])
    assert all(p['supported_heads'] == 0 for p in panel['by_type'].values())


def test_type_macro_and_family_class_weighting():
    truth = np.repeat(np.asarray([[True] * 48, [True] * 48, [False] * 48]), [1, 3, 2], axis=0)
    guess = truth.copy(); guess[0] = False
    panel = study.relation_metrics(guess, truth, ['a', 'b', 'b', 'b', 'a', 'b'], [True] * 48)
    assert panel['type_macro_balanced_accuracy'] == .75
    assert [p['supported_heads'] for p in panel['by_type'].values()] == [6, 6, 12, 24]


def test_prevalence_threshold_not_point_five_and_prior_balanced():
    values = np.asarray([[0, 0, 0, 0], [1, 2, 3, 4], [0, 1, 1, 2], [-1, 0, 1, 2]])
    scores = study.targets(values)
    prevalence = np.full(48, .1)
    scores[:, 776:] = .2
    support = dict(eligible=[True] * 48)
    panel = study.score(scores, values, np.asarray(['a', 'a', 'b', 'b']), support, prevalence)
    for c in panel['direct_relations']['cells']:
        if c['balanced_accuracy'] is not None: assert c['balanced_accuracy'] == .5
    scores[:, 776:] = prevalence
    assert study.score(scores, values, np.asarray(['a', 'a', 'b', 'b']), support, prevalence)['direct_relations'] == panel['direct_relations']


def test_external_relation_arithmetic_is_distinct_from_direct_heads():
    values = np.asarray([[0, 0, 0, 0], [1, 2, 3, 4], [0, 1, 1, 2], [-1, 0, 1, 2]])
    scores = study.targets(values); scores[:, 776:] = .7
    p = study.score(scores, values, np.asarray(['a', 'a', 'b', 'b']), dict(eligible=[True] * 48), np.full(48, .2))
    assert p['scalar']['all_four_exact'] == p['categorical']['all_four_exact'] == 1
    assert p['derived_scalar_relations']['type_macro_balanced_accuracy'] == 1
    assert p['derived_categorical_relations']['type_macro_balanced_accuracy'] == 1
    assert p['direct_relations']['type_macro_balanced_accuracy'] == .5


def test_family_macro_and_four_slot_joint_differ_from_row_mean():
    values = np.zeros((4, 4), int); scores = study.targets(values); scores[0, 0] = 1
    panel = study.score(scores, values, np.asarray(['a', 'b', 'b', 'b']), dict(eligible=[False] * 48), np.zeros(48))
    assert panel['scalar']['slot_macro_exact'] == .875
    assert panel['scalar']['all_four_exact'] == .5


def records():
    return [dict(seed=s, fold=f, alpha=a, validation=dict(scalar=dict(slot_macro_mae=1.),
        categorical=dict(slot_macro_exact=.5), direct_relations=dict(type_macro_balanced_accuracy=.5)))
        for s in numeric.SEEDS for f in range(3) for a in numeric.ALPHAS]


def test_train_grid_tie_break_and_incomplete_grid():
    rows = records()
    assert study.select(rows) == dict(scalar=10000., categorical=10000., relations=10000.)
    with pytest.raises(ValueError): study.select(rows[:-1])
    with pytest.raises(ValueError): study.select(rows[:-1] + [rows[0]])


def test_group_selection_independent_and_no_dev_keys_used():
    rows = records()
    for r in rows:
        r['validation']['scalar']['slot_macro_mae'] = 0 if r['alpha'] == 1 else 1
        r['validation']['categorical']['slot_macro_exact'] = 1 if r['alpha'] == 100 else 0
        r['development'] = dict(scalar='must never be read')
    assert study.select(rows) == dict(scalar=1., categorical=100., relations=10000.)


def test_unsupported_relation_selection_never_falls_back_to_dev():
    rows = records()
    for r in rows: r['validation']['direct_relations']['type_macro_balanced_accuracy'] = None
    assert study.select(rows)['relations'] is None


def test_query_and_computation_are_annotations_only():
    rows = [dict(query_slot=2, oracle=dict(definitions=[0, 4, 2, 7])), dict(query_slot=0, oracle=dict(definitions=[5, 1, 6, 3]))]
    a = study.annotation(rows)
    assert np.array_equal(a['queried'], [[False, False, True, False], [True, False, False, False]])
    assert np.array_equal(a['computed'], [[False, True, False, True], [True, False, True, False]])
    donor = study.annotation(rows, [1, 0])
    assert np.array_equal(donor['computed'], a['computed'][[1, 0]])


def test_feature_design_has_exact_width_without_annotations(monkeypatch):
    x = np.arange(16, dtype=np.float32).reshape(2, 8)
    monkeypatch.setattr(numeric, 'load_features', lambda entry: x)
    cache = dict(features=dict(source={}, llama8b_raw={}, llama8b_seed11={}))
    assert study.features(dict(backend='hidden', alias='llama8b', width=8, full_width=8), cache, 11) is x
    folded = study.features(dict(backend='source', alias='source', width=4, full_width=8), cache, 11)
    assert folded.shape == (2, 4)
    assert np.array_equal(folded, x[:, :4] + x[:, 4:])
    with pytest.raises(ValueError): study.features(dict(backend='hidden', alias='llama8b', width=4, full_width=8), cache, 11)


@pytest.mark.parametrize('seed', [11, 29, 47])
def test_independent_semantic_metric_audit(seed):
    truth = np.arange(-15, 16); groups = np.asarray(['a', 'b', 'c', 'd'] * 8)[:len(truth)]
    scores = np.random.default_rng(seed).normal(size=(len(truth), 11))
    assert semantic_audit.equal(semantic.score_heads(scores, truth, groups), semantic_audit.independent_metrics(scores, truth, groups))


def test_semantic_metric_audit_detects_changes():
    truth = np.asarray([1, -2, 0]); groups = np.asarray(['a', 'a', 'b'])
    a = semantic_audit.independent_metrics(semantic.targets(truth), truth, groups)
    b = deepcopy(a); b['scalar']['mae'] += .01
    assert not semantic_audit.equal(a, b)


def test_global_controller_isolated_from_existing_suite():
    from codecue.binding import arithmetic_global_state_suite as global_suite
    from codecue.binding import arithmetic_semantic_controls_suite as old_suite
    assert global_suite._CORE is not old_suite._CORE
    assert global_suite._CORE.ROLE == global_suite.ROLE
    assert old_suite._CORE.ROLE == old_suite.ROLE
    assert global_suite._CORE.SCRIPTS == {'scripts/206_binding_global_state.py'}
