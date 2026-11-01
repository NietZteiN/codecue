from copy import deepcopy
import numpy as np
import pytest

from codecue.binding import arithmetic_penalty_path as study, arithmetic_penalty_review as review


@pytest.mark.parametrize('values,weights,expected', [
    ([0, 10], [3, 1], 0), ([0, 10], [1, 3], 10), ([0, 10], [1, 1], 0),
    ([-4, -4, 9], [1, 2, 1], -4), ([5], [1], 5),
])
def test_weighted_median(values, weights, expected):
    assert study.weighted_median(values, weights) == expected


def test_weighted_median_minimizes_brute_force_absolute_loss():
    rng = np.random.default_rng(1)
    for _ in range(30):
        v = rng.normal(size=20); w = rng.uniform(.1, 3, 20)
        result = study.weighted_median(v, w)
        assert np.dot(w, np.abs(v - result)) <= min(np.dot(w, np.abs(v - c)) for c in v) + 1e-10


@pytest.mark.parametrize('v,w', [([], []), ([1], [0]), ([1], [-1]), ([1], [np.nan]), ([np.inf], [1]), ([1], [1, 2])])
def test_median_rejects_bad_data(v, w):
    with pytest.raises(ValueError): study.weighted_median(v, w)


def test_computed_prior_respects_family_observation_weights():
    values = np.array([[0]*4] + [[10]*4]*3)
    p = study.fit_priors(values, np.ones((4, 4), bool), ['a', 'b', 'b', 'b'], np.ones(4), 'train')
    assert p['constants']['median'] == [10]*4
    assert p['constants']['computed_median'] == [0]*4
    assert p['constants']['mean'] == [7.5]*4


def test_computed_prior_records_unsupported_heads_and_train_fallback():
    values = np.arange(16).reshape(4, 4); mask = np.zeros((4, 4), bool); mask[:, 0] = True
    p = study.fit_priors(values, mask, ['a']*4, np.ones(4), 'train')
    assert p['unsupported_computed_heads'] == [1, 2, 3]
    assert p['constants']['computed_median'][1:] == p['constants']['median'][1:]


@pytest.mark.parametrize('difference,accepted', [(1e-13, True), (.01, False)])
def test_prior_audit_tolerates_roundoff_but_rejects_changed_constants(difference, accepted):
    p = study.fit_priors(np.zeros((4, 4)), np.ones((4, 4), bool), ['a']*4, np.ones(4), 'train')
    saved = deepcopy(p); saved['constants']['mean'][0] += difference
    if accepted: review.check_prior_values(p, saved)
    else:
        with pytest.raises(ValueError): review.check_prior_values(p, saved)


@pytest.mark.parametrize('fault', ['split', 'width', 'mask', 'weight', 'nan'])
def test_prior_fit_is_train_only_and_shape_checked(fault):
    values = np.zeros((4, 4)); mask = np.ones((4, 4), bool); w = np.ones(4); split = 'train'
    if fault == 'split': split = 'development'
    if fault == 'width': values = values[:, :3]
    if fault == 'mask': mask = mask.astype(int)
    if fault == 'weight': w[0] = 0
    if fault == 'nan': values[0, 0] = np.nan
    with pytest.raises(ValueError): study.fit_priors(values, mask, ['a']*4, w, split)


def records():
    cv = [dict(seed=s, fold=f, alpha=a, validation=dict(computed=dict(mae=.5 if a == 100000 else 1.)))
        for s in study.old.numeric.SEEDS for f in range(3) for a in study.ALPHAS]
    priors = [dict(seed=s, fold=f, validation={p: dict(computed=dict(mae=2.)) for p in study.PRIOR_NAMES})
        for s in study.old.numeric.SEEDS for f in range(3)]
    return cv, priors


def test_selection_has_interior_ridge_and_no_dev_dependency():
    cv, p = records(); expected = study.select(cv, p)
    assert expected['ridge_alpha'] == 100000 and expected['ridge_grid_position'] == 'interior'
    assert expected['overall']['kind'] == 'ridge'
    for row in cv: row['development'] = dict(computed=dict(mae=-1000000))
    assert study.select(cv, p) == expected


def test_prior_can_win_without_refitting_and_zero_wins_constant_ties():
    cv, p = records()
    for row in p:
        for panel in row['validation'].values(): panel['computed']['mae'] = .1
    result = study.select(cv, p)
    assert result['ridge_alpha'] == 100000 and result['overall']['kind'] == 'prior' and result['overall']['prior'] == 'zero'


def test_ridge_ties_choose_larger_penalty_and_report_boundary():
    cv, p = records()
    for row in cv: row['validation']['computed']['mae'] = .5
    result = study.select(cv, p)
    assert result['ridge_alpha'] == max(study.ALPHAS) and result['ridge_grid_position'] == 'upper_boundary'


def test_constant_wins_an_exact_tie_with_ridge():
    cv, p = records()
    for row in p: row['validation']['median']['computed']['mae'] = .5
    assert study.select(cv, p)['overall']['prior'] == 'median'


@pytest.mark.parametrize('fault', ['cv_missing', 'cv_duplicate', 'prior_missing', 'prior_duplicate', 'cv_nan', 'cv_unsupported', 'prior_nan'])
def test_selection_rejects_incomplete_or_unsupported_training_grid(fault):
    cv, p = records()
    if fault == 'cv_missing': cv.pop()
    if fault == 'cv_duplicate': cv[0] = deepcopy(cv[1])
    if fault == 'prior_missing': p.pop()
    if fault == 'prior_duplicate': p[0] = deepcopy(p[1])
    if fault == 'cv_nan': cv[0]['validation']['computed']['mae'] = np.nan
    if fault == 'cv_unsupported': cv[0]['validation']['computed']['mae'] = None
    if fault == 'prior_nan': p[0]['validation']['zero']['computed']['mae'] = np.nan
    with pytest.raises(ValueError): study.select(cv, p)


def fixture_bank(tmp_path):
    rng = np.random.default_rng(5); x = rng.normal(size=(20, 3)); y = rng.normal(size=(20, 4)); w = rng.uniform(.5, 2, 20)
    ids = np.array([str(i) for i in range(20)]); indices = np.arange(20)
    model = study.old.numeric.fit(x, y, w, ids.tolist(), 'train', 10000)
    _, artifacts = study.old.numeric.save_model(tmp_path, 'original', model)
    context = study.training_context(x, y, w, ids, indices, indices)
    cfg = dict(condition='joint', immutable='fixture'); source = dict(snapshot_id='original')
    bank = dict(source=source, config_hash=study.digest(cfg), seed=11, fold=0, alpha=10000,
        fit_donor_ids_sha256=context['fit_donor_ids_sha256'], artifacts=artifacts)
    p = tmp_path / 'bank.json'; study.base._put(p, bank)
    return x, y, w, ids, model, context, cfg, source, bank, p


def test_old_fit_reuse_preserves_provenance_and_never_calls_fit(tmp_path, monkeypatch):
    x, y, w, ids, model, context, cfg, source, bank, p = fixture_bank(tmp_path)
    before = p.read_bytes(); target = tmp_path / 'reference.json'; new_cfg = dict(reference_worker=dict(path='old.json', sha256='a'*64))
    def forbidden(*args, **kwargs): raise AssertionError('old fit was repeated')
    monkeypatch.setattr(study.old.numeric, 'fit', forbidden)
    wrapper = study.reused_bank(new_cfg, dict(snapshot_id='new'), cfg, dict(source=source), p, target, context, 11, 10000, 0)
    assert wrapper['bank_type'] == 'reused_fit_reference' and wrapper['origin']['source'] == source
    assert wrapper['source'] == dict(snapshot_id='new') and wrapper['artifacts']['parameters'] == bank['artifacts']['parameters']
    assert wrapper['origin']['bank']['sha256'] == study.base._sha(p) and p.read_bytes() == before
    assert study.reused_bank(new_cfg, dict(snapshot_id='new'), cfg, dict(source=source), p, target, context, 11, 10000, 0) == wrapper


@pytest.mark.parametrize('fault', ['features', 'targets', 'weights', 'ids', 'donor', 'source', 'config', 'alpha'])
def test_reuse_rejects_changed_fit_context(tmp_path, fault):
    x, y, w, ids, model, context, cfg, source, bank, p = fixture_bank(tmp_path)
    context = deepcopy(context); expected_source, expected_cfg, alpha = source, cfg, 10000
    if fault in ('features', 'targets'):
        context['training_input_sha256'][fault] = '0'*64
    if fault == 'weights': context['training_input_sha256']['sample_weight'] = '0'*64
    if fault == 'ids': context['training_ids'].reverse()
    if fault == 'donor': context['fit_donor_ids_sha256'] = '0'*64
    if fault == 'source': expected_source = dict(snapshot_id='wrong')
    if fault == 'config': expected_cfg = dict(wrong=True)
    if fault == 'alpha': alpha = 100000
    with pytest.raises(ValueError): study.check_context(bank, context, 11, alpha, 0, expected_source, expected_cfg)


def test_numerical_audit_accepts_actual_ridge_solution(tmp_path):
    x, y, w, ids, model, context, cfg, source, bank, p = fixture_bank(tmp_path)
    counters = dict(max_relative_normal_equation_residual=0., max_intercept_residual=0., prediction_coordinates=0, max_prediction_abs_difference=0.)
    audited = review.audit_model(bank, context, x, y, w, counters)
    review.replay(audited, x, model.predict(x), counters)
    assert counters['max_relative_normal_equation_residual'] < 1e-7 and counters['prediction_coordinates'] == 80


def test_numerical_audit_rejects_well_hashed_but_nonoptimal_coefficients(tmp_path):
    x, y, w, ids, model, context, cfg, source, bank, p = fixture_bank(tmp_path)
    parameters = dict(model.parameters); parameters['coef'] = parameters['coef'] + .1
    metadata = deepcopy(model.metadata); metadata['parameters_sha256']['coef'] = study.weighted_ridge._array_hash(parameters['coef'])
    pp, mp = tmp_path / 'wrong_parameters.npz', tmp_path / 'wrong_metadata.json'
    study.storage._npz(pp, **parameters); study.base._put(mp, metadata)
    bank = dict(bank, artifacts=dict(parameters=study.storage._pin(pp), metadata=study.storage._pin(mp)))
    with pytest.raises(ValueError, match='stationarity'):
        review.audit_model(bank, context, x, y, w, dict(max_relative_normal_equation_residual=0., max_intercept_residual=0.))
