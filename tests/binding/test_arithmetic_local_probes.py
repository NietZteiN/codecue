import numpy as np
import pytest

from codecue.binding import arithmetic_local_probes as probe


def test_family_controls_are_coherent_valid_and_do_not_read_parent_labels():
    table = [dict(group='a', statement=5, side='left', parent=0),
             dict(group='a', statement=5, side='left', parent=3),
             dict(group='b', statement=4, side='right', parent=1)]
    labels = probe.random_targets(table)
    assert labels[0] == labels[1] and np.all(labels < [5, 5, 4])
    changed = [dict(e, parent=99) for e in table]
    np.testing.assert_array_equal(labels, probe.random_targets(changed))


def test_family_weight_sums_are_invariant_to_number_of_uses():
    table = [dict(group='a') for _ in range(9)] + [dict(group='b') for _ in range(3)]
    w = probe.family_weights(table, 11)
    small = probe.family_weights([dict(group='a'), dict(group='b')], 11)
    np.testing.assert_allclose([w[:9].sum(), w[9:].sum()], small, rtol=1e-6)


def test_learning_curves_add_whole_families_in_nested_stratified_subsets():
    table = [dict(group=f'{s}:{g}', stratum=str(s), split='train') for s in range(9) for g in range(24)]
    small = probe.family_subset(table, 54)
    middle = probe.family_subset(table, 108)
    full = probe.family_subset(table, 216)
    assert len(small) == 54 and len(middle) == 108 and len(full) == 216
    assert small < middle < full
    for stratum in range(9):
        assert sum(g.startswith(str(stratum) + ':') for g in small) == 6
    table[0]['split'] = 'development'
    with pytest.raises(ValueError):
        probe.family_subset(table, 54)


def test_projection_is_reproducible_and_seed_specific():
    a = probe.projection(96, 11)
    np.testing.assert_array_equal(a, probe.projection(96, 11))
    assert a.shape == (96, 64)
    assert not np.array_equal(a, probe.projection(96, 29))


def synthetic():
    labels = np.tile(np.arange(4), 12)
    q = np.zeros((len(labels), probe.DIMENSION), np.float32)
    q[np.arange(len(labels)), labels] = 1
    c = np.zeros((len(labels), probe.MAX_CANDIDATES, probe.DIMENSION), np.float32)
    for i in range(4):
        c[:, i, i] = 1
    mask = np.zeros(c.shape[:2], bool)
    mask[:, :4] = True
    return q, c, mask, labels.astype(np.int64)


def test_query_candidate_interaction_is_an_explicit_architecture_difference():
    import torch
    q, c, mask, labels = synthetic()
    linear = probe.make_model('linear')
    first = linear(torch.from_numpy(q), torch.from_numpy(c), torch.from_numpy(mask)).detach().numpy()
    second = linear(torch.from_numpy(q + 10), torch.from_numpy(c), torch.from_numpy(mask)).detach().numpy()
    np.testing.assert_allclose(first[:, :4] - first[:, :1], second[:, :4] - second[:, :1], atol=1e-5)
    interaction = probe.make_model('bilinear')
    first = interaction(torch.from_numpy(q), torch.from_numpy(c), torch.from_numpy(mask)).detach().numpy()
    second = interaction(torch.from_numpy(q + 10), torch.from_numpy(c), torch.from_numpy(mask)).detach().numpy()
    assert not np.allclose(first[:, :4] - first[:, :1], second[:, :4] - second[:, :1])


@pytest.mark.parametrize('method', ['bilinear', 'mlp'])
def test_small_probe_learns_compatibility_and_replays_parameters(method):
    import torch
    torch.set_num_threads(1)
    q, c, mask, labels = synthetic()
    model, norm = probe.train(q, c, mask, labels, np.ones(len(labels), np.float32), method, 11, epochs=100)
    logits = probe.scores(model, norm, q, c, mask)
    assert (logits.argmax(axis=1) == labels).mean() == 1
    copied = probe.make_model(method)
    copied.load_state_dict(model.state_dict())
    copied.eval()
    np.testing.assert_array_equal(logits, probe.scores(copied, norm, q, c, mask))
    assert np.all(logits[:, 4:] == -1e9)


def test_future_or_nonfinite_training_inputs_are_rejected():
    q, c, mask, labels = synthetic()
    labels[0] = 4
    with pytest.raises(ValueError):
        probe.train(q, c, mask, labels, np.ones(len(labels), np.float32), 'linear', 11)
    labels[0] = 0
    q[0, 0] = np.nan
    with pytest.raises(ValueError):
        probe.train(q, c, mask, labels, np.ones(len(labels), np.float32), 'linear', 11)


def test_normalizer_uses_only_supplied_fit_partition():
    q, c, mask, _ = synthetic()
    norm = probe.normalize(q, c, mask)
    expected = q.mean(axis=0).copy()
    probe.normalized(q * 100000, c * 100000, norm)
    np.testing.assert_array_equal(norm['mean_q'], expected)


def records():
    return [dict(backend=b, method=m, fold=f, seed=s, validation=dict(family_macro_accuracy=.5))
        for b in probe.BACKENDS for m in probe.METHODS for f in range(3) for s in probe.SEEDS]


def test_complete_grouped_selection_and_explicit_tie_break():
    assert set(probe.choose(records()).values()) == {'linear'}
    changed = records()
    for row in changed:
        if row['method'] == 'bilinear':
            row['validation']['family_macro_accuracy'] = .6
    assert set(probe.choose(changed).values()) == {'bilinear'}


@pytest.mark.parametrize('change', ['missing', 'duplicate'])
def test_incomplete_local_selection_rejected(change):
    rows = records()
    rows = rows[:-1] if change == 'missing' else rows + rows[:1]
    with pytest.raises(ValueError):
        probe.choose(rows)


def test_per_edge_and_whole_program_scores_are_distinct():
    logits = np.asarray([[2., 1.], [2., 1.], [1., 2.], [1., 2.]])
    labels = np.asarray([0, 1, 1, 0])
    table = [dict(group=g, case_id=g, depth=2, side='left', statement=4) for g in ['a', 'a', 'b', 'b']]
    result = probe.metrics(logits, labels, table)
    assert result['individual_accuracy'] == result['family_macro_accuracy'] == .5
    assert result['whole_program_graph_accuracy'] == 0
