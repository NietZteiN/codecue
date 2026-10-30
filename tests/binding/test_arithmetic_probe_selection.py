import numpy as np
import pytest

from codecue.binding import arithmetic_probe_selection as probe
from codecue.binding.weighted_ridge import fit


def data():
    rng = np.random.default_rng(3)
    x = rng.normal(size=(22, 7))
    x[:, -1] = 2
    y = rng.normal(size=(22, 3))
    w = rng.uniform(.1, 2, 22)
    return x, y, w, rng.normal(size=(9, 7))


@pytest.mark.parametrize('alpha', probe.ALPHAS)
def test_full_spectral_ridge_matches_audited_weighted_objective(alpha):
    x, y, w, held = data()
    expected = fit(x, y, w, train_ids=[str(i) for i in range(len(x))], split='train', alpha=alpha)
    model = probe.SpectralRidge(x, y, w)
    actual = model.predictions(held, [(alpha, 'full')])[(alpha, 'full')]
    np.testing.assert_allclose(actual, expected.predict(held), rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize('rank', probe.RANKS)
def test_saved_coefficient_replay_and_training_only_normalization(rank):
    x, y, w, held = data()
    model = probe.SpectralRidge(x, y, w)
    expected = model.predictions(held, [(100., rank)])[(100., rank)]
    np.testing.assert_allclose(probe.predict(model.parameters(100., rank), held), expected, atol=1e-9)
    np.testing.assert_array_equal(model.mean, x.mean(axis=0))
    before = model.parameters(100., rank)
    model.predictions(held * 100000, [(100., rank)])
    for key, array in before.items():
        np.testing.assert_array_equal(array, model.parameters(100., rank)[key])


def test_rank_constraint_reduces_learned_map():
    rng = np.random.default_rng(44)
    x = rng.normal(size=(45, 37))
    y = rng.normal(size=(45, 36))
    model = probe.SpectralRidge(x, y, np.ones(45))
    coef = model.parameters(1., 32)['coef']
    assert np.linalg.matrix_rank(coef, tol=1e-8) <= 32
    assert np.linalg.matrix_rank(model.parameters(1., 'full')['coef'], tol=1e-8) > 32


def test_constant_features_return_training_prior():
    x = np.ones((5, 3))
    y = np.arange(10).reshape(5, 2)
    w = np.arange(1, 6)
    model = probe.SpectralRidge(x, y, w)
    expected = np.broadcast_to(np.average(y, weights=w, axis=0), (2, 2))
    np.testing.assert_array_equal(model.predictions(np.ones((2, 3)), [(100., 'full')])[(100., 'full')], expected)


@pytest.mark.parametrize('bad', [0, -1, np.nan])
def test_invalid_weights_rejected(bad):
    x, y, w, _ = data()
    w[0] = bad
    with pytest.raises(ValueError):
        probe.SpectralRidge(x, y, w)


def train_rows():
    return [dict(split='train', component_id=f'{kind}:{g}', operation_family=kind)
        for kind in ['addition', 'subtraction', 'mixed'] for g in range(12) for _ in range(4)]


def test_folds_keep_all_relatives_together_and_balance_operator_strata():
    rows = train_rows()
    assigned = probe.folds(rows)
    for group in {r['component_id'] for r in rows}:
        assert len(set(f for r, f in zip(rows, assigned) if r['component_id'] == group)) == 1
    for fold in range(3):
        for kind in ['addition', 'subtraction', 'mixed']:
            assert len({r['component_id'] for r, f in zip(rows, assigned) if f == fold and r['operation_family'] == kind}) == 4


def test_dev_rows_rejected_from_selector():
    rows = train_rows()
    rows[0]['split'] = 'development'
    with pytest.raises(ValueError, match='TRAIN'):
        probe.folds(rows)


def records():
    return [dict(representation=backend, alpha=alpha, rank=rank, fold=fold, seed=seed,
                 metrics={task: .8 for task in probe.TASKS})
        for backend in ['hidden_layer_8', 'hidden_layer_24', 'source_char']
        for alpha in probe.ALPHAS for rank in probe.RANKS for fold in range(3) for seed in probe.SEEDS]


def test_selection_has_deterministic_declared_tie_break():
    chosen = probe.choose(records())
    for backend in chosen.values():
        for choice in backend.values():
            assert choice['rank'] == 32 and choice['alpha'] == 10000.
    assert chosen['hidden']['parent_accuracy']['representation'] == 'hidden_layer_8'


def test_selection_follows_mean_not_single_lucky_fold():
    entries = records()
    for entry in entries:
        if entry['representation'] == 'hidden_layer_24':
            entry['metrics']['parent_accuracy'] = 1. if entry['fold'] == 0 else 0.
    assert probe.choose(entries)['hidden']['parent_accuracy']['representation'] == 'hidden_layer_8'


@pytest.mark.parametrize('mutation', ['missing', 'duplicate'])
def test_incomplete_or_duplicated_fold_seed_grid_rejected(mutation):
    entries = records()
    if mutation == 'missing':
        entries.pop()
    else:
        entries.append(entries[0])
    with pytest.raises(ValueError):
        probe.choose(entries)


def test_numeric_query_relatives_have_identical_family_weight():
    rows = train_rows()
    w = probe.weights(rows, 11)
    assert all(len(set(w[i:i+4])) == 1 for i in range(0, len(w), 4))
    np.testing.assert_array_equal(w, probe.weights(rows, 11))


def test_support_counts_unique_bodies_not_lexical_query_duplicates():
    rows = [dict(lexical_realization=0, query_slot=0) for _ in range(24)]
    binary = np.zeros((24, 48), dtype=bool)
    binary[:12] = True
    assert probe.support(rows, binary).all()
    duplicate = [dict(lexical_realization=1, query_slot=1) for _ in range(100)]
    assert not probe.support(rows[:12] + duplicate, np.ones((112, 48), bool)).any()
