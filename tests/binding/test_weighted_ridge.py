"""Independent weighted-ridge objectives and persistence, synthetic data only."""
from copy import deepcopy
import io

import numpy as np
import pytest
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from codecue.binding import weighted_ridge as ridge


def fixture(n=37, d=9, k=8):
    rng = np.random.default_rng(136)
    x = rng.normal(size=(n, d))
    x[:, 0] = 7.
    if d > 2: x[:, 2] = .9*x[:, 1]+.01*x[:, 2]
    y = rng.normal(size=(n, k))+x@rng.normal(size=(d, k))
    weights = np.exp(rng.normal(size=n)*.5)
    ids = [f'neutral-train:{index}' for index in range(n)]
    return x, y, weights, ids


def fit(values, alpha=100.):
    x, y, weights, ids = values
    return ridge.fit(x, y, weights, ids, 'train', alpha)


@pytest.mark.parametrize('n,d', [(37, 9), (21, 55), (24, 24)])
@pytest.mark.parametrize('alpha', [0.1, 100.])
def test_matches_standardscaler_then_sample_weighted_sklearn_ridge(n, d, alpha):
    x, y, weights, ids = fixture(n, d)
    model = ridge.fit(x, y, weights, ids, ['train']*n, alpha)
    scaler = StandardScaler().fit(x)
    reference = Ridge(alpha=alpha, solver='cholesky', fit_intercept=True).fit(scaler.transform(x), y, sample_weight=weights)
    probe = np.random.default_rng(47).normal(size=(17, d))
    np.testing.assert_array_equal(model.mean, scaler.mean_)
    np.testing.assert_array_equal(model.scale, scaler.scale_)
    np.testing.assert_allclose(model.coef, reference.coef_.T, rtol=1e-10, atol=2e-11)
    np.testing.assert_allclose(model.intercept, reference.intercept_, rtol=1e-10, atol=2e-11)
    np.testing.assert_allclose(model.predict(probe), reference.predict(scaler.transform(probe)), rtol=1e-10, atol=2e-11)
    assert model.scale[0] == 1.
    assert model.metadata['mode'] == ('dual_cholesky' if d > n else 'primal_cholesky')
    assert model.metadata['factorizations'] == 1
    assert model.metadata['heldout_rows_used_for_fit'] == 0
    assert model.train_ids == tuple(ids)
    # Unequal weights must not silently change the original unweighted scaler.
    assert not np.allclose(model.mean[1:], np.average(x, axis=0, weights=weights)[1:])
    z = scaler.transform(x)
    np.testing.assert_array_equal(model.weighted_feature_mean, np.average(z, axis=0, weights=weights))
    np.testing.assert_array_equal(model.weighted_target_mean, np.average(y, axis=0, weights=weights))


def test_primal_and_dual_solve_identical_weighted_centered_objective():
    x, y, weights, ids = fixture(29, 12)
    z = StandardScaler().fit_transform(x)
    zmean = np.average(z, axis=0, weights=weights)
    ymean = np.average(y, axis=0, weights=weights)
    primal = ridge._solve(z-zmean, y-ymean, weights, 100., 'primal_cholesky')
    dual = ridge._solve(z-zmean, y-ymean, weights, 100., 'dual_cholesky')
    np.testing.assert_allclose(primal, dual, rtol=1e-12, atol=2e-14)
    with pytest.raises(ValueError, match='mode'):
        ridge._solve(z-zmean, y-ymean, weights, 100., 'other')


def test_all_128_targets_share_one_factorization_and_heads_stay_independent(monkeypatch):
    from scipy import linalg
    x, _, weights, ids = fixture(33, 80, 1)
    rng = np.random.default_rng(11)
    targets = np.concatenate([np.eye(32)[rng.integers(0, 32, len(x))] for _ in range(4)], axis=1)
    calls = []
    original = linalg.cho_factor
    def counting(*args, **kwargs):
        calls.append(args[0].shape)
        return original(*args, **kwargs)
    monkeypatch.setattr(linalg, 'cho_factor', counting)
    joint = ridge.fit(x, targets, weights, ids, 'train')
    assert calls == [(33, 33)]
    assert joint.coef.shape == (80, 128)
    for index in range(4):
        individual = ridge.fit(x, targets[:, index*32:(index+1)*32], weights, ids, 'train')
        np.testing.assert_allclose(joint.coef[:, index*32:(index+1)*32], individual.coef, rtol=1e-12, atol=2e-14)
        np.testing.assert_allclose(joint.intercept[index*32:(index+1)*32], individual.intercept, rtol=1e-12, atol=2e-14)
    changed = targets.copy(); changed[:, 32:] = rng.normal(size=changed[:, 32:].shape)
    other = ridge.fit(x, changed, weights, ids, 'train')
    np.testing.assert_allclose(joint.coef[:, :32], other.coef[:, :32], rtol=1e-12, atol=2e-14)
    np.testing.assert_allclose(joint.intercept[:32], other.intercept[:32], rtol=1e-12, atol=2e-14)


def test_saved_parameters_roundtrip_predicts_exactly_and_cannot_be_mutated():
    values = fixture(19, 40); model = fit(values)
    probe = np.random.default_rng(17).normal(size=(31, 40))
    expected = model.predict(probe)
    stream = io.BytesIO(); np.savez_compressed(stream, **model.parameters); stream.seek(0)
    with np.load(stream, allow_pickle=False) as saved:
        reloaded = ridge.from_parameters(model.metadata, {name: saved[name] for name in saved.files})
    np.testing.assert_array_equal(reloaded.predict(probe), expected)
    assert reloaded.metadata == model.metadata
    before = model.metadata
    model.metadata['training_ids'].clear()
    assert model.metadata == before
    for array in model.parameters.values():
        with pytest.raises(ValueError): array.flat[0] = 10.
        with pytest.raises(ValueError): array.setflags(write=True)
    values[0][:] = 1e6; values[1][:] = -1e6; values[2][:] = 2.
    np.testing.assert_array_equal(model.predict(probe), expected)
    # Prediction batches never fit or modify the saved training parameters.
    changed = probe.copy(); changed[1:] = 1e5
    np.testing.assert_allclose(model.predict(changed)[0], expected[0], rtol=0, atol=1e-13)
    assert model.metadata == before


def test_constant_targets_predict_weighted_target_mean():
    x, y, weights, ids = fixture(17, 30)
    y[:] = np.arange(y.shape[1])+2.
    model = ridge.fit(x, y, weights, ids, 'train')
    np.testing.assert_allclose(model.coef, 0, atol=1e-15)
    np.testing.assert_allclose(model.predict(x), y, atol=1e-13)


@pytest.mark.parametrize('split', ['development', 'test', 'final', 'train+development', None,
    ['train'], ['train']*36+['development'], [['train']]*37])
def test_development_and_nonmatching_split_declarations_are_rejected(split):
    x, y, weights, ids = fixture()
    with pytest.raises(ValueError, match='training rows only'): ridge.fit(x, y, weights, ids, split)


@pytest.mark.parametrize('change', ['duplicate_ids', 'missing_id', 'blank_id', 'scalar_ids', 'bad_id',
    'weight_zero', 'weight_negative', 'weight_nan', 'weight_count', 'weight_matrix',
    'x_nan', 'x_inf', 'x_dimension', 'x_empty_columns', 'x_one_row',
    'y_nan', 'y_count', 'y_vector', 'y_no_columns', 'alpha_zero', 'alpha_negative', 'alpha_inf', 'alpha_bool'])
def test_invalid_shapes_labels_weights_and_training_identities_fail(change):
    x, y, weights, ids = fixture(); alpha = 100.
    if change == 'duplicate_ids': ids[0] = ids[1]
    elif change == 'missing_id': ids.pop()
    elif change == 'blank_id': ids[0] = ' '
    elif change == 'scalar_ids': ids = 'one-string'
    elif change == 'bad_id': ids[0] = 9
    elif change == 'weight_zero': weights[0] = 0
    elif change == 'weight_negative': weights[0] = -1
    elif change == 'weight_nan': weights[0] = np.nan
    elif change == 'weight_count': weights = weights[:-1]
    elif change == 'weight_matrix': weights = weights[:, None]
    elif change == 'x_nan': x[0, 1] = np.nan
    elif change == 'x_inf': x[0, 1] = np.inf
    elif change == 'x_dimension': x = x[:, 0]
    elif change == 'x_empty_columns': x = x[:, :0]
    elif change == 'x_one_row': x, y, weights, ids = x[:1], y[:1], weights[:1], ids[:1]
    elif change == 'y_nan': y[0, 0] = np.nan
    elif change == 'y_count': y = y[:-1]
    elif change == 'y_vector': y = y[:, 0]
    elif change == 'y_no_columns': y = y[:, :0]
    elif change == 'alpha_zero': alpha = 0.
    elif change == 'alpha_negative': alpha = -1.
    elif change == 'alpha_inf': alpha = np.inf
    else: alpha = True
    with pytest.raises(ValueError): ridge.fit(x, y, weights, ids, 'train', alpha)


@pytest.mark.parametrize('change', ['role', 'split', 'heldout', 'dimensions', 'ids', 'mode', 'config',
    'input_hashes', 'weight_sum', 'parameter_hashes', 'missing_parameter', 'extra_parameter', 'shape', 'value', 'nonfinite'])
def test_saved_parameter_identity_and_training_policy_are_checked(change):
    model = fit(fixture()); metadata = deepcopy(model.metadata)
    parameters = {key: value.copy() for key, value in model.parameters.items()}
    if change == 'role': metadata['evaluation_role'] = 'final_evaluation'
    elif change == 'split': metadata['fit_split'] = 'development'
    elif change == 'heldout': metadata['heldout_rows_used_for_fit'] = 1
    elif change == 'dimensions': metadata['features'] += 1
    elif change == 'ids': metadata['training_ids'][0] = 'different'
    elif change == 'mode': metadata['mode'] = 'dual_cholesky'
    elif change == 'config': metadata['config']['sample_weight'] = 'renormalized'
    elif change == 'input_hashes': metadata['training_input_sha256'].pop('targets')
    elif change == 'weight_sum': metadata['sample_weight_sum'] = 0.
    elif change == 'parameter_hashes': metadata['parameters_sha256'].pop('coef')
    elif change == 'missing_parameter': parameters.pop('coef')
    elif change == 'extra_parameter': parameters['other'] = np.ones(3)
    elif change == 'shape': parameters['coef'] = parameters['coef'][:-1]
    elif change == 'value': parameters['coef'][0, 0] += 1.
    else: parameters['intercept'][0] = np.nan
    with pytest.raises(ValueError): ridge.from_parameters(metadata, parameters)


def test_prediction_width_shape_and_finiteness_are_guarded():
    model = fit(fixture())
    for value in (np.zeros((3, 8)), np.zeros(9), np.full((3, 9), np.nan)):
        with pytest.raises(ValueError): model.predict(value)
    assert model.predict(np.empty((0, 9))).shape == (0, 8)
