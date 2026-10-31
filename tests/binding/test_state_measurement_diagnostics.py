"""Scientific invariants for the saved-result exploratory diagnostic."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location('state_diagnostic', Path(__file__).parents[2] / 'scripts/190_binding_state_diagnostics.py')
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


def test_bootstrap_uses_families_not_observation_counts():
    result = diagnostic.family_summary([0., 0., 0., 1.], ['a', 'a', 'a', 'b'])
    assert result['mean'] == .5
    assert result['families'] == 2
    assert result['interval95'] == [0., 1.]


def test_seeds_are_averaged_inside_the_family():
    first = diagnostic.family_summary([[0., 1.], [1., 0.], [1., 1.]], ['a', 'b'])
    second = diagnostic.family_summary([[2/3, 2/3]], ['a', 'b'])
    assert first['mean'] == second['mean']
    assert first['interval95'] == second['interval95']
    assert first['fitting_seeds'] == 3


def test_family_duplication_does_not_create_independent_observations():
    a = diagnostic.family_summary([0., 1.], ['a', 'b'])
    b = diagnostic.family_summary([0., 0., 1., 1.], ['a', 'a', 'b', 'b'])
    assert a['mean'] == b['mean']
    assert a['interval95'] == b['interval95']


@pytest.mark.parametrize('scores,groups', [([], []), ([float('nan')], ['a']), ([1., 0.], ['a'])])
def test_malformed_bootstrap_input_rejected(scores, groups):
    with pytest.raises(ValueError):
        diagnostic.family_summary(scores, groups)


def test_oracle_values_can_hide_an_incorrect_binding():
    rows = [dict(oracle=dict(writes=[dict(value=2), dict(value=2), dict(value=7), dict(value=9)]))]
    predicted = diagnostic.oracle_numeric_route(np.asarray([[1, 0, 2, 3]]), rows)
    assert predicted.tolist() == [[2, 2, 7, 9]]


@pytest.mark.parametrize('pointers', [[[0, 1, 2, 4]], [[0, 1, 2, -1]], [[0., 1., 2., 3.]]])
def test_invalid_oracle_pointer_rejected(pointers):
    rows = [dict(oracle=dict(writes=[dict(value=2)] * 4))]
    with pytest.raises(ValueError):
        diagnostic.oracle_numeric_route(np.asarray(pointers), rows)


def test_control_accuracy_uses_control_task_truth():
    real_truth = np.asarray([2, 3])
    control_truth = np.asarray([5, 6])
    prediction = np.asarray([5, 6])
    assert diagnostic.exact_scores(prediction, control_truth).all()
    assert not diagnostic.exact_scores(prediction, real_truth).any()


def test_numeric_panel_compares_each_task_to_its_own_labels(monkeypatch):
    rows = [dict(oracle=dict(writes=[dict(value=0)] * 4), component_id='family' + str(i // 2),
        split='train' if i < 2 else 'development', depth=2) for i in range(6)]
    cases = [dict(descriptors=[dict(kind='definition', statement=4, value=i)]) for i in range(6)]
    data = dict(row_indices=np.arange(6), point_indices=np.zeros(6, dtype=int), truth=np.arange(6),
        predicted=np.arange(6), shuffled=np.arange(6) + 1, shuffle_truth=np.arange(6) + 1)
    monkeypatch.setattr(diagnostic, 'arrays', lambda entry: data)
    model = dict(fits=[dict(backend=b, format=f, seed=s, artifacts=dict(scores={}))
        for b in ('hidden', 'source') for f in ('regression', 'categorical') for s in (11, 29, 47)])
    output = diagnostic.numeric_diagnostics(model, rows, cases, 100)
    for panel in output.values():
        assert panel['all']['exact']['mean'] == 1.
        assert panel['all']['real_minus_shuffled_exact']['mean'] == 0.


def test_paired_dependency_comparison_requires_same_structural_families():
    a = [dict(seed=s, development=dict(family_metrics={'a': .8, 'b': .4})) for s in (11, 29, 47)]
    b = [dict(seed=s, development=dict(family_metrics={'a': .6, 'b': .2})) for s in (11, 29, 47)]
    result = diagnostic.matched_difference(a, b, 'family_metrics', 2000)
    assert result['mean'] == pytest.approx(.2)
    b[-1]['development']['family_metrics'] = {'a': .6, 'c': .2}
    with pytest.raises(ValueError):
        diagnostic.matched_difference(a, b, 'family_metrics', 2000)
