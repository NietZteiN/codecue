from copy import deepcopy
import numpy as np
import pytest
from codecue.binding import arithmetic_conditional_state as study


def test_metrics_weight_families_equally():
    truth = np.zeros((4, 4)); pred = truth.copy(); pred[1:] = 2
    out = study.metrics(pred, truth, ['a', 'b', 'b', 'b'], dict(computed=np.ones((4, 4), bool)))
    assert out['computed']['mae'] == 1 and out['computed']['exact'] == .5
    assert out['computed']['observations'] == 16 and out['computed']['families'] == 2


def test_computed_selection_excludes_literal_slots():
    truth = np.zeros((2, 4)); pred = np.ones((2, 4)) * 100; pred[:, 2] = 0
    mask = np.zeros((2, 4), bool); mask[:, 2] = True
    out = study.metrics(pred, truth, ['a', 'b'], dict(computed=mask, untouched=~mask))
    assert out['computed']['mae'] == 0 and out['computed']['exact'] == 1
    assert out['untouched']['mae'] == 100 and out['all']['mae'] == 75


def test_unsupported_stratum_is_explicit():
    out = study.metrics(np.zeros((2, 4)), np.zeros((2, 4)), ['a', 'b'], dict(computed=np.zeros((2, 4), bool)))
    assert out['computed']['mae'] is None and out['computed']['exact'] is None
    assert out['computed']['families'] == 0


@pytest.mark.parametrize('fault', ['width', 'rows', 'infinite', 'mask_shape', 'mask_dtype'])
def test_metrics_reject_invalid_panels(fault):
    p = np.zeros((2, 4)); y = p.copy(); mask = np.ones((2, 4), bool)
    if fault == 'width': p = p[:, :3]
    if fault == 'rows': y = y[:1]
    if fault == 'infinite': p[0, 0] = np.inf
    if fault == 'mask_shape': mask = mask[:, :3]
    if fault == 'mask_dtype': mask = mask.astype(int)
    with pytest.raises(ValueError): study.metrics(p, y, ['a', 'b'], dict(computed=mask))


def fixture():
    rows = [dict(split=split, component_id=split + str(family), family_stratum='depth2',
        numeric_seed=1, numeric_draw=draw, lexical_realization=lexical)
        for split in ('train', 'development') for family in range(6) for draw in range(2) for lexical in range(2)]
    s = np.zeros((len(rows), 1024), np.float32); h = s.copy()
    s[:, 0] = np.arange(len(rows)) + 10; h[:, 0] = np.arange(len(rows)) + 100
    return rows, s, h


@pytest.mark.parametrize('condition', ['source1024', 'source2048', 'hidden', 'joint'])
def test_feature_design_uses_only_declared_blocks(condition):
    rows, s, h = fixture(); indices = np.arange(12)
    if condition == 'source2048': s = np.concatenate((s, s), axis=1)
    x, donor = study.design(condition, s, h, rows, indices)
    assert np.array_equal(donor, indices)
    if condition.startswith('source'): assert np.array_equal(x, s[indices])
    elif condition == 'hidden': assert np.array_equal(x, h[indices])
    else: assert np.array_equal(x, np.concatenate((s[indices], h[indices]), axis=1))


def test_shuffled_hidden_preserves_source_and_partition_boundaries():
    rows, s, h = fixture()
    for indices in (np.arange(12), np.arange(12, 24), np.arange(24, 48)):
        x, donor = study.design('shuffled_joint', s, h, rows, indices)
        assert set(donor) == set(indices) and np.array_equal(x[:, :1024], s[indices])
        assert np.array_equal(x[:, 1024:], h[donor])
        for a, b in zip(indices, donor):
            assert rows[a]['component_id'] != rows[b]['component_id']
            for field in ('split', 'family_stratum', 'numeric_seed', 'numeric_draw', 'lexical_realization'):
                assert rows[a][field] == rows[b][field]


@pytest.mark.parametrize('indices', [[0, 0], [-1], [100], [1.5], [0, 24], []])
def test_partition_errors_fail_before_fitting(indices):
    rows, s, h = fixture()
    with pytest.raises(ValueError): study.design('joint', s, h, rows, np.asarray(indices))


@pytest.mark.parametrize('condition', ['source1024', 'hidden', 'joint', 'unknown'])
def test_feature_width_changes_are_rejected(condition):
    rows, s, h = fixture()
    with pytest.raises(ValueError): study.design(condition, s[:, :3], h[:, :3], rows, np.arange(12))


@pytest.mark.parametrize('block', ['source', 'hidden'])
def test_train_mean_ablation_is_exact_after_standardization(block):
    rng = np.random.default_rng(3); x = rng.normal(size=(4, 2048)).astype(np.float32)
    mean = rng.normal(size=2048); before = x.copy()
    result = study.zero_block(x, mean, block); chosen = slice(0, 1024) if block == 'source' else slice(1024, 2048)
    assert np.all(result[:, chosen] - mean[chosen] == 0)
    assert np.array_equal(x, before) and result.dtype == np.float64
    other = slice(1024, 2048) if block == 'source' else slice(0, 1024)
    assert np.array_equal(result[:, other], x[:, other])


@pytest.mark.parametrize('fault', ['width', 'mean', 'block'])
def test_ablation_requires_fitted_two_block_normalizer(fault):
    x = np.zeros((2, 2048)); mean = np.zeros(2048); block = 'hidden'
    if fault == 'width': x = x[:, :1024]
    if fault == 'mean': mean = mean[:1024]
    if fault == 'block': block = 'oracle'
    with pytest.raises(ValueError): study.zero_block(x, mean, block)


def records():
    return [dict(seed=s, fold=f, alpha=a, validation=dict(computed=dict(mae=2 if a == 1 else 1)))
        for s in study.numeric.SEEDS for f in range(3) for a in study.numeric.ALPHAS]


def test_selection_uses_only_complete_train_grid_and_larger_alpha_ties():
    assert study.select(records()) == 10000


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'unsupported', 'nan'])
def test_selection_rejects_missing_or_unsupported_folds(fault):
    r = records()
    if fault == 'missing': r.pop()
    if fault == 'duplicate': r[0] = deepcopy(r[1])
    if fault == 'unsupported': r[0]['validation']['computed']['mae'] = None
    if fault == 'nan': r[0]['validation']['computed']['mae'] = float('nan')
    with pytest.raises(ValueError): study.select(r)


def test_joint_gain_and_fitted_block_ablation_recover_known_signal():
    rng = np.random.default_rng(17); n = 120
    s = np.zeros((n, 1024)); h = s.copy(); s[:, :2] = rng.normal(size=(n, 2)); h[:, 0] = rng.normal(size=n)
    y = h[:, :1] * np.arange(1, 5)[None, :]; x = np.concatenate((s, h), axis=1)
    ti, vi = np.arange(80), np.arange(80, n); ids = [str(i) for i in ti]
    joint = study.numeric.fit(x[ti], y[ti], np.ones(80), ids, 'train', 1)
    source = study.numeric.fit(s[ti], y[ti], np.ones(80), ids, 'train', 1)
    joint_mae = np.abs(joint.predict(x[vi]) - y[vi]).mean()
    source_mae = np.abs(source.predict(s[vi]) - y[vi]).mean()
    ablated_mae = np.abs(joint.predict(study.zero_block(x[vi], joint.mean, 'hidden')) - y[vi]).mean()
    assert joint_mae < .05 and source_mae > .5 and ablated_mae > 10 * joint_mae


def review_module():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[2] / 'scripts/219_binding_paired_postrun_review.py'
    spec = importlib.util.spec_from_file_location('paired_postrun_test', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def review_rows():
    return [dict(record_id='source', scope=scope, protocol=protocol, instruction=0, truncated=False,
        expected=[3] if scope == 'single' else [1, 2, 3, 4],
        strict_values=None if scope == 'single' else [9, 2, 3, 4],
        diagnostic_values=[3] if scope == 'single' else [9, 2, 3, 4])
        for protocol in ('output_only', 'intermediate_query', 'stepwise') for scope in ('single', 'all')]


def test_postrun_scope_uses_same_target_and_diagnostic_grammar():
    module = review_module(); rows = review_rows()
    for p in module.scope_panel(rows, 'strict').values():
        assert p['single_correct'] == 0 and p['all_target_correct'] == 1
    for p in module.scope_panel(rows, 'diagnostic').values():
        assert p['single_correct'] == p['all_target_correct'] == 1
    assert not module.success(rows[1], 'diagnostic')
    assert module.success(rows[1], 'diagnostic', True)


def test_postrun_truncation_still_fails_diagnostic():
    module = review_module(); row = review_rows()[0]; row['truncated'] = True
    assert not module.success(row, 'diagnostic', True)


@pytest.mark.parametrize('fault', ['duplicate', 'missing', 'target'])
def test_postrun_scope_pairing_guards(fault):
    module = review_module(); rows = review_rows()
    if fault == 'duplicate': rows.append(deepcopy(rows[0]))
    if fault == 'missing': rows.pop()
    if fault == 'target': rows[0]['expected'] = [9]
    with pytest.raises(ValueError): module.scope_panel(rows, 'diagnostic')


@pytest.mark.parametrize('fault', ['duplicate', 'missing', 'target'])
def test_postrun_protocol_pairing_guards(fault):
    module = review_module(); rows = review_rows()
    if fault == 'duplicate': rows.append(deepcopy(rows[0]))
    if fault == 'missing': rows.pop()
    if fault == 'target': rows[0]['expected'] = [9]
    with pytest.raises(ValueError): module.protocol_panel(rows, 'diagnostic')
