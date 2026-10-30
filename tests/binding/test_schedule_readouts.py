from dataclasses import replace
from types import SimpleNamespace
import json

import numpy as np
import pytest
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from codecue.binding import schedule_readouts as study


def fixture():
    rng = np.random.default_rng(6)
    x = rng.normal(size=(18, 7))
    y = rng.integers(0, 2, size=(18, 5)).astype(float)
    control = rng.integers(0, 2, size=y.shape).astype(float)
    mask = np.ones(y.shape, dtype=bool)
    mask[:3, 2:4] = False
    mask[:, 4] = False
    y[~mask] = 0; control[~mask] = 0
    train = np.arange(18) < 12
    weights = np.linspace(.4, 2, 12)
    ids = tuple(f'case{i}' for i in range(18))
    bundle = SimpleNamespace(y=y, mask=mask, case_ids=ids)
    sham = SimpleNamespace(y=control, mask=mask, case_ids=ids)
    return x, bundle, sham, train, weights


def test_masked_heads_match_independent_training_only_sklearn_fits():
    x, bundle, control, train, weights = fixture()
    fitted, real, random = study.fit_masked_columns(x, bundle.y, bundle.mask, control.y,
                                                   train, weights, bundle.case_ids)
    assert len(fitted) == 2
    for column in range(4):
        valid = bundle.mask[train, column]
        rows = np.flatnonzero(train)[valid]
        scaler = StandardScaler().fit(x[rows])
        expected = Ridge(alpha=100, solver='cholesky').fit(scaler.transform(x[rows]),
            np.column_stack((bundle.y[rows, column], control.y[rows, column])),
            sample_weight=weights[valid]).predict(scaler.transform(x))
        np.testing.assert_allclose(real[:, column], expected[:, 0], atol=2e-14)
        np.testing.assert_allclose(random[:, column], expected[:, 1], atol=2e-14)
    assert np.isnan(real[:, 4]).all()
    changed_x = x.copy(); changed_x[~train] += 1000
    changed_y = bundle.y.copy(); changed_y[~train] = 17; changed_y[~bundle.mask] = 0
    changed_models = study.fit_masked_columns(changed_x, changed_y, bundle.mask,
                                             control.y, train, weights, bundle.case_ids)[0]
    for (_, _, before), (_, _, after) in zip(fitted, changed_models):
        for key in before.parameters:
            assert np.array_equal(before.parameters[key], after.parameters[key])


def test_partial_mask_with_one_train_row_does_not_fit_development():
    x, bundle, control, train, weights = fixture()
    bundle.mask[:12, 3] = False; bundle.mask[0, 3] = True
    bundle.y[~bundle.mask] = 0; control.y[~bundle.mask] = 0
    _, scores, random = study.fit_masked_columns(x, bundle.y, bundle.mask,
                                                control.y, train, weights, bundle.case_ids)
    assert np.isnan(scores[:, 3]).all() and np.isnan(random[:, 3]).all()


@pytest.mark.parametrize('problem', ['dev_weights', 'zero_weight', 'nonfinite', 'duplicate_id',
                                   'masked_positive', 'bad_train_dtype'])
def test_masked_input_guards(problem):
    x, bundle, control, train, weights = fixture()
    if problem == 'dev_weights': weights = np.ones(18)
    if problem == 'zero_weight': weights[0] = 0
    if problem == 'nonfinite': x[0, 0] = np.nan
    if problem == 'duplicate_id': bundle.case_ids = ('repeat',)*18
    if problem == 'masked_positive': bundle.y[0, 4] = 1
    if problem == 'bad_train_dtype': train = train.astype(int)
    with pytest.raises(ValueError):
        study.fit_masked_columns(x, bundle.y, bundle.mask, control.y, train, weights, bundle.case_ids)


def test_parameter_banks_replay_and_resume_without_fitting(tmp_path, monkeypatch):
    x, bundle, control, train, weights = fixture()
    path = tmp_path/'bank.npz'
    first = study._fit_bank(path, x, bundle, control, train, weights, 'a'*64)
    assert first[-1]
    monkeypatch.setattr(study, 'ridge_fit', lambda *a, **k: pytest.fail('resume must not refit'))
    second = study._fit_bank(path, x, bundle, control, train, weights, 'a'*64, allow_fit=False)
    assert not second[-1]
    assert np.array_equal(first[0], second[0], equal_nan=True)
    with pytest.raises(ValueError, match='identity'):
        study._fit_bank(path, x+1, bundle, control, train, weights, 'a'*64)
    with pytest.raises(ValueError, match='missing fit'):
        study._fit_bank(tmp_path/'missing.npz', x, bundle, control, train, weights, 'a'*64, allow_fit=False)


def test_corrupted_saved_scores_cannot_pass_parameter_replay(tmp_path):
    x, bundle, control, train, weights = fixture()
    path = tmp_path/'bank.npz'
    study._fit_bank(path, x, bundle, control, train, weights, 'b'*64)
    with np.load(path, allow_pickle=False) as saved:
        arrays = {key: saved[key].copy() for key in saved.files}
    arrays['scores'][15, 0] += .01
    np.savez(path, **arrays)
    with pytest.raises(ValueError, match='replay'):
        study._fit_bank(path, x, bundle, control, train, weights, 'b'*64, allow_fit=False)


def metrics_fixture():
    columns = (
        dict(index=0, kind='boolean', family='direct', name='direct/0/4'),
        dict(index=1, kind='categorical', family='copy_parent', head='copy_parent/0', candidate=0, name='parent0'),
        dict(index=2, kind='categorical', family='copy_parent', head='copy_parent/0', candidate=1, name='parent1'))
    y = np.array([[0., 1, 0], [1, 0, 1], [0, 1, 0], [1, 0, 1]])
    bundle = SimpleNamespace(y=y, mask=np.ones_like(y, dtype=bool), columns=columns,
        group_ids=('g0', 'g1', 'g2', 'g3'))
    support = dict(columns=[dict(binary_eligible=True)]*3,
                   categorical_heads={'copy_parent/0': dict(all_observed_train_classes_supported=False,
                       dev_only_classes=[1], constant_training_task=True)})
    return bundle, support


def test_metrics_keep_unsupported_classes_and_missing_predictions_as_errors():
    bundle, support = metrics_fixture()
    scores = bundle.y.copy(); scores[:, 2] = np.nan
    report = study.metrics(bundle, scores, support)
    head = report['categorical_heads']['copy_parent/0']
    assert head['n'] == 4 and head['accuracy'] == .5
    assert head['classes']['1'] == dict(n=2, accuracy=0.)
    assert head['train_support']['dev_only_classes'] == [1]
    assert report['whole_categorical_families']['copy_parent']['accuracy'] == .5
    assert len(head['per_group']) == 4


def test_boolean_macro_stays_undefined_when_any_fixed_eligible_class_is_missing():
    bundle, support = metrics_fixture()
    bundle.y[:, 0] = 0
    report = study.metrics(bundle, bundle.y, support)
    family = report['boolean_families']['direct']
    assert family['train_eligible_columns'] == 1
    assert family['eligible_macro_balanced_accuracy'] is None
    assert report['boolean_cells'][0]['constant_evaluation_task']


def test_categorical_decision_does_not_use_oracle_mask_to_remove_wrong_predictions():
    bundle, support = metrics_fixture()
    bundle.mask[:, 1] = False
    bundle.y[:, 1] = 0; bundle.y[:, 2] = 1
    scores = bundle.y.copy(); scores[:, 1] = 100
    assert study.metrics(bundle, scores, support)['categorical_heads']['copy_parent/0']['accuracy'] == 0


def test_support_eligibility_uses_only_training_labels():
    bundle, _ = metrics_fixture()
    train = np.array([True, True, False, False])
    first = study._train_support(bundle, train)
    bundle.y[~train] = 1-bundle.y[~train]
    second = study._train_support(bundle, train)
    assert first['columns'] == second['columns']


def test_config_rejects_report_reserved_paths_and_bad_pins(tmp_path):
    config = dict(evaluation_role=study.ROLE, capture_config=str(tmp_path/'capture.json'),
        capture_config_sha256='a'*64, declared_plan=str(tmp_path/'plan.md'),
        declared_plan_sha256='b'*64, primary_layer=24, run_dir=str(tmp_path/'run'),
        report=str(tmp_path/'report.md'))
    assert study._config(config) == config
    with pytest.raises(ValueError): study._config({**config, 'capture_config_sha256': 'bad'})
    with pytest.raises(ValueError): study._config({**config, 'report': str(tmp_path/'run')})
    with pytest.raises(ValueError): study._config({**config, 'report': str(tmp_path/'run'/'hidden_layer24_site7_seed17.npz'/'report.md')})
    with pytest.raises(ValueError): study._config({**config, 'run_dir': str(tmp_path/'ancestor.md'/'run'),
                                                'report': str(tmp_path/'ancestor.md')})


def test_group_macro_reports_unequal_family_sizes_separately():
    bundle, support = metrics_fixture()
    bundle.group_ids = ('large', 'large', 'large', 'small')
    scores = bundle.y.copy(); scores[-1, 1:] = [1, 0]
    report = study.metrics(bundle, scores, support)
    head = report['categorical_heads']['copy_parent/0']
    assert head['accuracy'] == .75 and head['group_macro_accuracy'] == .5
    assert report['whole_categorical_families']['copy_parent']['group_macro_accuracy'] == .5


def test_publication_interruption_resumes_banks_and_audits_without_refitting(tmp_path, monkeypatch):
    rng = np.random.default_rng(27)
    n = 18
    columns = (
        dict(index=0, kind='boolean', family='current', name='current/0'),
        dict(index=1, kind='categorical', family='current_definition',
             head='current_definition/0', candidate=0, name='definition0'),
        dict(index=2, kind='categorical', family='current_definition',
             head='current_definition/0', candidate=1, name='definition1'))
    y = rng.integers(0, 2, size=(n, 3)).astype(float); y[:, 2] = 1-y[:, 1]
    bundle = SimpleNamespace(y=y, mask=np.ones_like(y, dtype=bool), columns=columns,
        case_ids=tuple(f'c{i}' for i in range(n)), group_ids=tuple(f'g{i//3}' for i in range(n)),
        splits=tuple('train' if i < 12 else 'development' for i in range(n)), descriptive={})
    records = [dict(id=f'c{i}', split=bundle.splits[i], template_id=bundle.group_ids[i]) for i in range(n)]
    config = dict(evaluation_role=study.ROLE, run_dir=str(tmp_path/'run'),
                  report=str(tmp_path/'report.md'), primary_layer=3)
    source = dict(snapshot='synthetic-fixture-only', source_sha256='c'*64)
    checked = dict(layers=[1, 2, 3, 4], feature_shape=[n, 3, 4, 7],
        cases=[dict(visible_prefixes=[f'code-{i}-{s}' for s in range(3)]) for i in range(n)],
        source={'synthetic_fixture_only': True}, dataset_sha256='d'*64, model='synthetic-fixture')
    vectors = rng.normal(size=checked['feature_shape']).astype('float32')
    def subset(value, indices):
        return SimpleNamespace(y=value.y[indices], mask=value.mask[indices], columns=value.columns,
            case_ids=tuple(value.case_ids[i] for i in indices),
            group_ids=tuple(value.group_ids[i] for i in indices),
            splits=tuple(value.splits[i] for i in indices), descriptive={})
    monkeypatch.setattr(study, '_metadata', lambda *a, **k: (source, checked, records))
    monkeypatch.setattr(study, '_bundles', lambda rows: (
        {site: bundle for site in study.SITES},
        {(site, seed): bundle for site in study.SITES for seed in study.SEEDS},
        {site: {} for site in study.SITES}))
    monkeypatch.setattr(study, '_targets', lambda: SimpleNamespace(subset=subset))
    monkeypatch.setattr(study, '_load', lambda _: vectors)
    immutable = study.publication.immutable
    def interrupted(path, payload):
        if str(path).endswith(study.COMPLETION): raise OSError('fixture publication interruption')
        return immutable(path, payload)
    monkeypatch.setattr(study.publication, 'immutable', interrupted)
    with pytest.raises(OSError, match='publication interruption'): study.run(config)
    assert len(list((tmp_path/'run').glob('*.npz'))) == 45
    assert not (tmp_path/'run'/study.COMPLETION).exists()
    monkeypatch.setattr(study.publication, 'immutable', immutable)
    monkeypatch.setattr(study, 'ridge_fit', lambda *a, **k: pytest.fail('must resume existing parameters'))
    result = study.run(config)
    assert result['fit_banks'] == result['factorizations'] == 45
    assert result['parameter_replay_rows'] == 45*n
    assert study.completed_result(config) == result
    audited = study.audit(config)
    assert audited['new_fits'] == 0 and audited['parameter_replay_rows'] == 45*n
    assert (tmp_path/'run'/'parameter_replay_review_v1.json').is_file()
    attempts = json.loads((tmp_path/'run'/'attempts.json').read_text())['attempts']
    assert [a['status'] for a in attempts] == ['failed', 'complete']
    attempts[-1]['status'] = 'running'
    study.durable._journal(tmp_path/'run'/'attempts.json', dict(evaluation_role=study.ROLE, attempts=attempts))
    assert study.run(config) == result
    recovered = json.loads((tmp_path/'run'/'attempts.json').read_text())['attempts'][-1]
    assert recovered['status'] == 'complete_from_verified_receipt'
    assert (tmp_path/'run'/'attempts_before_completion_recovery_v1.json').is_file()
