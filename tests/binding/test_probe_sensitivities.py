"""Synthetic checks for frozen train-only alignment and complete-target ridge."""
from copy import deepcopy
import json

import numpy as np
import pytest

from codecue.binding import probe_sensitivities as probes


PROVENANCE = {'kind': 'synthetic_test', 'dataset_sha256': 'not-a-study-dataset'}


def data():
    rng = np.random.default_rng(125)
    x = rng.normal(size=(37, 6))
    x[:, 1] = .9*x[:, 0]+.15*x[:, 1]
    y = rng.normal(size=(37, 4))+x @ rng.normal(size=(6, 4))
    return x, y, [f'train:{index}' for index in range(len(x))]


def align(x, y, ids, **options):
    return probes.fit_alignment(x, y, source_ids=ids, target_ids=ids,
        split='train', provenance=PROVENANCE, **options)


def ridge(x, y, ids, **options):
    return probes.fit_reduced_rank_ridge(x, y, train_ids=ids, split='train',
        provenance=PROVENANCE, alpha=options.pop('alpha', 11.),
        rank=options.pop('rank', 2), **options)


def test_alignment_recovers_known_orthogonal_map_and_training_centers():
    x, _, ids = data()
    q, _ = np.linalg.qr(np.random.default_rng(9).normal(size=(6, 6)))
    y = x @ q+np.arange(6)*3.
    model = align(x, y, ids, config={'anchor_kind': 'fixed_train'})
    assert np.allclose(model.rotation, q, atol=1e-12)
    assert np.allclose(model.rotation.T @ model.rotation, np.eye(6), atol=1e-12)
    assert np.allclose(probes.transform_alignment(model, x), y, atol=1e-12)
    assert np.allclose(model.source_mean, x.mean(axis=0))
    assert model.training_ids == tuple(ids)
    assert model.metadata['training_ids'] == ids
    assert model.metadata['provenance'] == PROVENANCE
    assert model.metadata['config']['user_config'] == {'anchor_kind': 'fixed_train'}
    assert model.metadata['heldout_rows_used_for_fit'] == 0


@pytest.mark.parametrize('rank', [1, 2, 4])
def test_reduced_rank_ridge_attains_global_rank_constrained_objective(rank):
    x, y, ids = data()
    alpha = 11.
    model = ridge(x, y, ids, alpha=alpha, rank=rank)
    z = (x-x.mean(axis=0))/x.std(axis=0)
    yc = y-y.mean(axis=0)
    gram = z.T @ z+alpha*np.eye(x.shape[1])
    c = np.linalg.solve(np.linalg.cholesky(gram), z.T @ yc)
    singular = np.linalg.svd(c, compute_uv=False)
    optimum = np.sum(yc**2)-np.sum(singular[:rank]**2)
    objective = np.sum((yc-z @ model.weights)**2)+alpha*np.sum(model.weights**2)
    assert np.linalg.matrix_rank(model.weights) <= rank
    assert np.isclose(objective, optimum, rtol=1e-12, atol=1e-10)
    assert np.isclose(model.metadata['train_penalized_objective'], objective)
    if rank == 4:
        assert np.allclose(model.weights, np.linalg.solve(gram, z.T @ yc), atol=1e-12)
    else:
        # Ordinary ridge followed by an unweighted coefficient SVD is inferior.
        ordinary = np.linalg.solve(gram, z.T @ yc)
        u, s, vt = np.linalg.svd(ordinary, full_matrices=False)
        naive = (u[:, :rank]*s[:rank]) @ vt[:rank]
        naive_objective = np.sum((yc-z @ naive)**2)+alpha*np.sum(naive**2)
        assert objective < naive_objective-1e-5


def test_heldout_batches_and_input_mutations_cannot_change_fitted_parameters():
    x, y, ids = data()
    alignment = align(x, x+3., ids)
    model = ridge(x, y, ids)
    holdout = np.random.default_rng(17).normal(size=(5, 6))
    before = model.predict(holdout)
    aligned = alignment.transform(holdout)
    metadata = deepcopy(model.metadata)
    changed = holdout.copy();changed[1:] = 1e8
    assert np.array_equal(model.predict(changed)[:1], before[:1])
    assert np.array_equal(alignment.transform(changed)[:1], aligned[:1])
    x[:] = 1e4;y[:] = -1e8
    assert np.array_equal(probes.predict_reduced_rank_ridge(model, holdout), before)
    assert np.array_equal(alignment.transform(holdout), aligned)
    assert model.metadata == metadata
    model.metadata['training_ids'].clear()
    assert model.metadata['training_ids'] == ids
    for array in (model.x_mean, model.x_scale, model.weights, alignment.rotation):
        with pytest.raises(ValueError):array.flat[0] = 9.
        with pytest.raises(ValueError):array.setflags(write=True)


def test_constant_features_and_targets_have_finite_unambiguous_predictions():
    x, y, ids = data();x[:, 2] = 4.;y[:] = 7.
    model = ridge(x, y, ids)
    assert model.x_scale[2] == 1.
    assert np.array_equal(model.weights, np.zeros((6, 4)))
    assert np.allclose(model.predict(x), 7.)


@pytest.mark.parametrize('split', ['development', 'final', None, 'TRAIN'])
def test_every_fit_requires_explicit_train_split(split):
    x, y, ids = data()
    with pytest.raises(ValueError, match='train'):
        probes.fit_alignment(x, x, source_ids=ids, target_ids=ids, split=split, provenance=PROVENANCE)
    with pytest.raises(ValueError, match='train'):
        probes.fit_reduced_rank_ridge(x, y, train_ids=ids, split=split,
            alpha=1., rank=2, provenance=PROVENANCE)


def test_id_geometry_complete_targets_and_provenance_guards():
    x, y, ids = data()
    invalid_ids = [ids[:-1], [ids[0]]*len(ids), [None]*len(ids), 'one_string']
    for bad in invalid_ids:
        with pytest.raises(ValueError):align(x, x, bad)
        with pytest.raises(ValueError):ridge(x, y, bad)
    with pytest.raises(ValueError, match='row order'):
        probes.fit_alignment(x, x, source_ids=ids, target_ids=ids[::-1],
            split='train', provenance=PROVENANCE)
    with pytest.raises(ValueError, match='row order'):ridge(x, y, ids, target_ids=ids[::-1])
    for bad in (np.full_like(y, np.nan), np.ma.array(y), y[:, 0], y[:-1], y.astype(complex)):
        with pytest.raises(ValueError):ridge(x, bad, ids)
    with pytest.raises(ValueError, match='mask'):ridge(x, y, ids, target_mask=np.ones_like(y, dtype=bool))
    for bad in (x[:, 0], x[:-1], np.full_like(x, np.inf)):
        with pytest.raises(ValueError):align(x, bad, ids)
    for bad in ({}, None, {'source': float('nan')}):
        with pytest.raises(ValueError):
            probes.fit_alignment(x, x, source_ids=ids, target_ids=ids,
                split='train', provenance=bad)
    with pytest.raises(ValueError):ridge(x, y, ids, config={'split': 'development'})
    with pytest.raises(ValueError):ridge(x, y, ids).predict(np.ones((3, 7)))
    with pytest.raises(ValueError):align(x, x, ids).transform(x, ids=ids[::-1]+['extra'])


@pytest.mark.parametrize('change', [
    {'alpha': 0}, {'alpha': -1}, {'alpha': float('nan')}, {'alpha': True},
    {'rank': 0}, {'rank': 8}, {'rank': 2.}, {'rank': True},
])
def test_ridge_penalty_and_rank_are_fixed_valid_hyperparameters(change):
    x, y, ids = data()
    with pytest.raises(ValueError):ridge(x, y, ids, **change)


def test_metadata_preflight_and_selfcheck_write_logged_reviews_without_payloads(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('preparation opened a data payload')
    monkeypatch.setattr(np, 'load', forbidden)
    from codecue.binding import datasets
    monkeypatch.setattr(datasets, 'read_jsonl', forbidden)
    config = {'evaluation_role': probes.ROLE, 'split': 'train',
        'alignment': {'enabled': True, 'center': True},
        'reduced_rank_ridge': {'alpha': 1., 'rank': 2, 'complete_targets': True},
        'provenance': PROVENANCE, 'output_review': str(tmp_path/'preflight.json')}
    review = probes.preflight(config)
    assert json.loads((tmp_path/'preflight.json').read_text()) == review
    assert review['status'] == 'passed_preparation_preflight'
    assert review['activation_payloads_opened'] == 0 and review['study_fits_performed'] == 0
    selfcheck = probes.selfcheck(str(tmp_path/'selfcheck.json'))
    assert selfcheck['status'] == 'passed_synthetic_selfcheck'
    assert selfcheck['ridge_optimal_objective_absolute_error'] < 1e-10
    assert selfcheck['new_model_queries'] == 0
    for change in ({'activation_path': '/never/open'}, {'split': 'development'},
                   {'evaluation_role': 'final'}, {'alignment': {'center': False}},
                   {'reduced_rank_ridge': {'alpha': 1., 'rank': 2, 'complete_targets': False}}):
        with pytest.raises(ValueError):probes.preflight({**config, **change})
