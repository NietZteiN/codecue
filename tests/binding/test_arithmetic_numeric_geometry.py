"""Scientific controls, bounded decoding and actual query-point extraction."""
from copy import deepcopy
import numpy as np
import pytest
from codecue.binding import arithmetic_numeric_geometry as study
from codecue.binding import arithmetic_numeric_exploration as baseline
from codecue.binding.weighted_ridge import fit


def test_perfect_codes_roundtrip_every_signed_domain_value():
    values = np.arange(-96, 97)
    scores = study.targets(values)
    assert scores.shape == (193, 214)
    for result in study.predictions(scores).values(): assert np.array_equal(result, values)
    result = study.score_heads(scores, values, np.asarray(['family'] * len(values)))
    assert all(v == dict(exact=1., mae=0.) for v in result.values())


@pytest.mark.parametrize('pair', [('decimal_circle', 'decimal_permuted'), ('crt_circle', 'crt_permuted')])
def test_permutations_match_dimension_and_norm_but_change_geometry(pair):
    first, second = map(study.template, pair)
    assert first.shape == second.shape
    assert np.allclose(np.square(first).sum(axis=1), np.square(second).sum(axis=1))
    assert not np.allclose(first @ first.T, second @ second.T)
    assert len(np.unique(np.round(first, 9), axis=0)) == 193
    assert len(np.unique(np.round(second, 9), axis=0)) == 193


def test_signed_residues_wrap_and_do_not_alias_in_declared_domain():
    code = study.template('crt_circle')
    for value in (-96, -19, -1, 0, 1, 19, 96):
        expected = np.concatenate([[np.cos(2*np.pi*(value % p)/p), np.sin(2*np.pi*(value % p)/p)] for p in (17, 19)])
        assert np.allclose(code[value + 96], expected)
    assert len(np.unique(np.round(code, 9), axis=0)) == len(study.VALUES)


def test_ordinal_nearest_code_includes_candidate_norm():
    # An uncorrected dot product ties at, and above, the true value.
    scores = study.targets(np.asarray([-96, -17, 0, 41, 96]))
    assert study.predictions(scores)['ordinal'].tolist() == [-96, -17, 0, 41, 96]
    for name in study.FORMATS:
        with pytest.raises(ValueError): study.template(name)[0, 0] = 4


@pytest.mark.parametrize('values', [np.asarray([97]), np.asarray([-97]), np.asarray([np.iinfo(np.int64).min]),
    np.asarray([1.5]), np.asarray([[1]])])
def test_invalid_integer_targets_rejected(values):
    with pytest.raises(ValueError): study.targets(values)


@pytest.mark.parametrize('scores', [np.zeros((2, 213)), np.full((1, 214), np.inf)])
def test_invalid_scores_rejected(scores):
    with pytest.raises(ValueError): study.predictions(scores)


def test_geometry_engine_isolated_from_completed_baselines():
    assert baseline.FIT != study._CORE.FIT == study.FIT
    assert baseline.HEAD_WIDTH != study._CORE.HEAD_WIDTH == 214
    assert baseline.targets is not study._CORE.targets
    assert 'scalar' in baseline.FORMATS and 'ordinal' not in baseline.FORMATS


def test_exact_selection_uses_complete_train_grid_and_stronger_alpha_ties():
    panel = study.score_heads(study.targets(np.asarray([1])), np.asarray([1]), np.asarray(['a']))
    records = [dict(seed=s, fold=f, alpha=a, validation=deepcopy(panel))
        for s in baseline.SEEDS for f in range(3) for a in baseline.ALPHAS]
    assert set(study._CORE.select(records).values()) == {10000.}
    for r in records: r['validation']['ordinal']['exact'] = float(r['alpha'] == 100)
    assert study._CORE.select(records)['ordinal'] == 100
    with pytest.raises(ValueError): study._CORE.select(records[:-1])


def test_actual_variable_length_answer_point_not_padded_last_slot():
    features = np.arange(2*23*4*5).reshape(2, 23, 4, 5)
    cases = [dict(point_count=n, descriptors=[dict(kind='definition')]*(n-1) + [dict(kind='answer')]) for n in (8, 17)]
    selected = study.query_values(features, cases)
    assert np.array_equal(selected, features[[0, 1], [7, 16]])
    assert not np.array_equal(selected, features[:, -1])
    cases[0]['point_count'] = 23
    with pytest.raises(ValueError): study.query_values(features, cases)


def test_geometry_positive_control_serialization_and_coherent_label_outputs(tmp_path):
    values = np.arange(-9, 10)
    targets = np.concatenate((study.targets(values), study.targets(values[::-1])), axis=1)
    model = fit(np.eye(len(values)), targets, np.ones(len(values)), [str(i) for i in values], 'train', 1.)
    replay, _ = study._CORE.save_model(tmp_path, 'positive', model)
    scores = replay.predict(np.eye(len(values)))
    assert np.array_equal(scores, model.predict(np.eye(len(values))))
    real, control = np.split(scores, 2, axis=1)
    # Decimal/circular templates can contract toward the mean under ridge.
    # Identity features should nevertheless retain sign and exact ordinals.
    for name in ('decimal_circle', 'decimal_permuted', 'ordinal'):
        assert study.score_heads(real, values, np.asarray(['a'] * len(values)))[name]['exact'] == 1
        assert study.score_heads(control, values[::-1], np.asarray(['a'] * len(values)))[name]['exact'] == 1


def test_family_macro_metrics_do_not_overweight_repeated_relatives():
    truth = np.asarray([1, 1, 1, 2]); guessed = np.asarray([1, 1, 1, 3])
    result = study.score_heads(study.targets(guessed), truth, np.asarray(['a', 'a', 'a', 'b']))
    assert all(panel == dict(exact=.5, mae=.5) for panel in result.values())


def test_complete_geometry_worker_train_only_selection_replay_and_resume(tmp_path, monkeypatch):
    # Reuse the established tiny end-to-end assay with the actual new engine,
    # exercising all 214 outputs and its saved selected/control score banks.
    import importlib.util
    from pathlib import Path
    path = Path(__file__).with_name('test_arithmetic_numeric_exploration.py')
    spec = importlib.util.spec_from_file_location('geometry_worker_fixture', path)
    fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
    fixture.study = study._CORE
    fixture.test_complete_small_worker_keeps_dev_out_of_fits_and_reuses_saved_completion(tmp_path, monkeypatch)
    worker = tmp_path / 'worker_config.json'
    study.base._put(worker, dict(run_dir=str(tmp_path / 'worker')))
    result = study.report(dict(evaluation_role=study.REPORT, run_dir=str(tmp_path / 'report'),
        report=str(tmp_path / 'report.md'), workers=[study.storage._pin(worker)]))
    assert len(result['paired_family_contrasts']) == 2
    assert all(c['families'] == 3 for c in result['paired_family_contrasts'])


def test_paired_family_bootstrap_does_not_count_seeds_as_families():
    first = np.asarray([[1, 0, 1], [0, 1, 1], [1, 1, 0]], float)
    result = study.paired_family_interval(first, first)
    assert result['families'] == 3
    assert result['delta'] == result['lower'] == result['upper'] == 0
    assert study.paired_family_interval(first, first - .1)['delta'] == pytest.approx(.1)
    with pytest.raises(ValueError): study.paired_family_interval(first, first[:, :2])
