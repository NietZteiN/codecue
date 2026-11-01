"""Semantic-label correctness, fixed features, paired replay and TRAIN discipline."""
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import arithmetic_semantic_controls as study
from codecue.binding import arithmetic_local_programs as programs
from codecue.binding import arithmetic_numeric_exploration as numeric


def row(source, **extra):
    body, query = source.rsplit('\n', 1)
    result = dict(id='example', bare_canonical_source=source, source=body + '\nprint(' + query + ')',
        oracle=programs.truth(source), split='train', component_id='family', family_stratum='depth2_mixed',
        depth=len(body.splitlines()) - 4)
    result.update(extra)
    result['expected_answer'] = result['oracle']['expected_answer']
    return result


def example():
    return row('v0 = 2\nv1 = 5\nv2 = -1\nv3 = 0\nv0 = v0 + v1\nv1 = v0 - v2\nv1')


def test_swaps_binary_meanings_without_changing_unary_negative_roots_or_versions():
    original, altered = study.traces(example())
    assert [w['value'] for w in original['execution_trace']] == [2, 5, -1, 0, 7, 8]
    assert [w['value'] for w in altered['execution_trace']] == [2, 5, -1, 0, -3, -4]
    assert altered['execution_trace'][-1]['uses'][0]['definition'] == 'v0@2'
    assert altered['execution_trace'][-1]['uses'][1]['definition'] == 'v2@1'
    assert original['dependency_edges'] == altered['dependency_edges']


def test_the_analytic_bound_covers_every_update_without_old_domain_clipping():
    source = '\n'.join([f'v{i} = 6' for i in range(4)] + ['v0 = v0 - v0'] * 6 + ['v0'])
    original, alternate = study.traces(row(source))
    assert original['expected_answer'] == 0
    assert alternate['expected_answer'] == study.BOUND == 384
    assert study.targets(np.asarray([-384, 384])).shape == (2, 11)


@pytest.mark.parametrize('source', [
    'v0 = 7\nv1 = 1\nv2 = 0\nv3 = 0\nv0 = v0 + v1\nv0',
    'v0 = 1\nv1 = 1\nv2 = 0\nv3 = 0\nv0 = v0 * 2\nv0',
    'v0 = 1\nv1 = 1\nv2 = 0\nv3 = 0\nv0 = abs(v1)\nv0',
    'v0 = 1\nv1 = 1\nv2 = 0\nv3 = 0\nv0 = v4 + v1\nv0',
    'v1 = 1\nv0 = 1\nv2 = 0\nv3 = 0\nv0 = v0 + v1\nv0',
])
def test_unsupported_or_out_of_contract_programs_rejected(source):
    with pytest.raises(ValueError): study.rewrite(source, 'operator_swap')


def test_unknown_semantics_rejected():
    with pytest.raises(ValueError): study.rewrite(example()['bare_canonical_source'], 'invented')


def test_both_interpreters_and_auxiliary_state_relation_labels_agree():
    item = example(); cases = [dict(descriptors=programs.points(item))]
    table, arrays = study.label_arrays([item], cases)
    assert len(table) == 6
    assert arrays['definition_values'].tolist()[-2:] == [[7, -3], [8, -4]]
    assert arrays['current_values'][-1].tolist() == [[7, 8, -1, 0], [-3, -4, -1, 0]]
    assert arrays['assignment_versions'][-1].tolist() == [2, 2, 1, 1]
    assert arrays['defined_slots'][0].tolist() == [True, False, False, False]
    final = arrays['final_values']
    for k, (a, b) in enumerate(study.PAIRS):
        assert np.array_equal(arrays['final_pair_lt'][:, :, k], final[:, :, a] < final[:, :, b])
    for k, (a, b, c) in enumerate(study.TRIPLES):
        assert np.array_equal(arrays['final_triple_add'][:, :, k], final[:, :, c] == final[:, :, a] + final[:, :, b])


def test_modified_archived_ordinary_oracle_rejected():
    item = example(); item['oracle']['writes'][-1]['value'] += 1
    with pytest.raises(ValueError): study.traces(item)


def test_perfect_unbounded_scalar_and_components_roundtrip():
    values = np.arange(-384, 385)
    result = study.score_heads(study.targets(values), values, np.asarray(['a'] * len(values)))
    assert result['scalar'] == dict(exact=1., mae=0.)
    assert all(r['exact'] == 1 for r in result.values())
    assert all(r.get('balanced_accuracy', 1) == 1 for r in result.values())


@pytest.mark.parametrize('values', [np.asarray([385]), np.asarray([-385]),
    np.asarray([np.iinfo(np.int64).min]), np.asarray([1.5]), np.asarray([[1]])])
def test_bad_targets_rejected(values):
    with pytest.raises(ValueError): study.targets(values)


def test_ordinary_and_new_metrics_match_on_identical_scores():
    rng = np.random.default_rng(17)
    values = rng.integers(-96, 97, 47)
    groups = np.asarray([f'family{i%7}' for i in range(len(values))])
    old_scores = rng.normal(size=(len(values), numeric.HEAD_WIDTH))
    selected = np.concatenate([old_scores[:, numeric.slices()[name]] for name in study.FORMATS], axis=1)
    old = numeric.score_heads(old_scores, values, groups)
    new = study.score_heads(selected, values, groups)
    assert new == {name: old[name] for name in study.FORMATS}
    assert numeric.HEAD_WIDTH != study._CORE.HEAD_WIDTH == 11
    assert numeric.examples is not study._CORE.examples


def test_literature_access_and_hash_mismatch_guard(tmp_path):
    report = tmp_path / 'review.md'; report.write_text('literature')
    register = tmp_path / 'register.json'
    study.base._put(register, dict(source_count=23, report_sha256=study.base._sha(report)))
    config = dict(literature=dict(report=study.storage._pin(report), register=study.storage._pin(register)))
    assert study.literature(config) == config['literature']
    report.write_text('changed')
    with pytest.raises(ValueError): study.literature(config)


def test_ridge_target_subsetting_preserves_the_ordinary_per_target_objective():
    from codecue.binding.weighted_ridge import fit
    rng = np.random.default_rng(73)
    x = rng.normal(size=(35, 9)); y = rng.normal(size=(35, 17)); w = rng.uniform(.2, 2., 35)
    ids = [f'train-{i}' for i in range(len(x))]
    full = fit(x, y, w, ids, 'train', 100.)
    subset = fit(x, y[:, [0, 3, 11]], w, ids, 'train', 100.)
    assert np.allclose(full.predict(x)[:, [0, 3, 11]], subset.predict(x), rtol=1e-12, atol=1e-12)


def test_label_preparation_borrows_identical_features_and_resumes_without_execution(tmp_path, monkeypatch):
    rows, cases = [], []
    for split in ('train', 'development', 'calibration'):
        item = example(); item.update(split=split, id=split)
        rows.append(item); cases.append(dict(descriptors=programs.points(item)))
    table = numeric.examples(rows, cases)
    payload = tmp_path / 'features.npy'; np.save(payload, np.ones((len(table), 2), np.float32))
    old_folder = tmp_path / 'old'; old_folder.mkdir()
    original = tmp_path / 'original.json'; study.base._put(original, dict(run_dir=str(old_folder)))
    feature = dict(study.storage._pin(payload), shape=[len(table), 2])
    study.base._put(old_folder / 'results.json', dict(table_sha256=study.digest(table), features=dict(raw=feature), width=2))
    view_path = tmp_path / 'view.json'
    view = dict(evaluation_role=study.CACHE, run_dir=str(tmp_path / 'view'), original_cache=study.storage._pin(original))
    study.base._put(view_path, view)
    monkeypatch.setattr(study, 'literature', lambda config: {})
    monkeypatch.setattr(study.common, 'validate_role', lambda config, role: dict(snapshot_id='unit'))
    monkeypatch.setattr(study.audit, 'load_cache', lambda config: ({}, {}, {}, rows, cases))
    monkeypatch.setattr(study.common, 'completed', lambda config: study.base._json(Path(config['run_dir']) / 'results.json'))
    config = dict(evaluation_role=study.PREPARE, run_dir=str(tmp_path / 'labels'), literature={}, cache_views=[study.storage._pin(view_path)])
    result = study.prepare(config)
    assert result['excluded_rows'] == 0 and result['independent_python_verified']
    actual = study.base._json(tmp_path / 'view/results.json')
    assert actual['features']['raw'] == feature
    assert actual['table_sha256'] == study.digest(study.swap_examples(rows, cases))
    assert np.array_equal(numeric.metadata_features(table), numeric.metadata_features(study.swap_examples(rows, cases)))
    assert not (tmp_path / 'view/features.npy').exists()
    monkeypatch.setattr(study, 'label_arrays', lambda *a, **k: pytest.fail('completed labels must not be rebuilt'))
    assert study.prepare(config)['excluded_rows'] == 0


def test_end_to_end_alternate_worker_reuses_ordinary_fit_and_replays_paired_metrics(tmp_path, monkeypatch):
    rows, cases = [], []
    for split, families in [('train', 6), ('development', 3), ('calibration', 3)]:
        for family in range(families):
            for draw in range(2):
                source = f'v0 = {family%3}\nv1 = {draw+1}\nv2 = -1\nv3 = 0\nv0 = v0 + v1\nv1 = v0 - v2\nv1'
                item = row(source, split=split, component_id=f'{split}-{family}', family_stratum='depth2_addition',
                    depth=2, numeric_seed=11, numeric_draw=draw, lexical_realization=0)
                item['id'] = f'{split}-{family}-{draw}'
                rows.append(item); cases.append(dict(descriptors=programs.points(item)))
    ordinary = numeric.examples(rows, cases); alternate = study.swap_examples(rows, cases)
    matrix = np.zeros((len(ordinary), 64), np.float32)
    for i, e in enumerate(ordinary): matrix[i, e['value'] + 20] = 1
    monkeypatch.setattr(numeric, 'load_features', lambda entry: matrix)
    monkeypatch.setattr(study._CORE, 'load_features', lambda entry: matrix)
    monkeypatch.setattr(study, 'literature', lambda config: {})
    monkeypatch.setattr(study.common, 'validate_role', lambda config, role: dict(snapshot_id='unit'))
    monkeypatch.setattr(study.audit, 'load_cache', lambda config: ({}, {}, dict(model='unit'), rows, cases))
    monkeypatch.setattr(study.common, 'completed', lambda config: study.base._json(Path(config['run_dir']) / 'results.json'))
    def folds(table):
        groups = sorted({e['group'] for e in table}); mapping = {g: i%3 for i, g in enumerate(groups)}
        return np.asarray([mapping[e['group']] for e in table])
    monkeypatch.setattr(study.common, 'folds', folds)
    requests = {}
    for name, engine, table in [('ordinary', numeric, ordinary), ('alternate', study._CORE, alternate)]:
        folder = tmp_path / (name + '_cache'); folder.mkdir()
        cache = tmp_path / (name + '_cache.json'); study.base._put(cache, dict(run_dir=str(folder)))
        study.base._put(folder / 'results.json', dict(table_sha256=study.digest(table), width=64, features=dict(source={})))
        config = dict(evaluation_role=engine.FIT, run_dir=str(tmp_path / name), backend='source',
            role='computed_definition', widths=[64], cache_config=study.storage._pin(cache), semantic='operator_swap')
        path = tmp_path / (name + '.json'); study.base._put(path, config); requests[name] = study.storage._pin(path)
        data = engine.run(config)
        assert data['cv_banks'] == 27
        for meta in (tmp_path / name).glob('*_metadata.json'):
            assert all(identity.startswith('train-') for identity in study.base._json(meta)['training_ids'])
    prepared = tmp_path / 'prepared'; prepared.mkdir()
    prepared_cfg = tmp_path / 'prepared.json'; study.base._put(prepared_cfg, dict(run_dir=str(prepared)))
    values = np.asarray([[a['value'], b['value']] for a,b in zip(ordinary, alternate)])
    study.base._put(prepared / 'results.json', dict(target_diagnostics=study.diagnostics(ordinary, values)))
    config = dict(evaluation_role=study.REPORT, run_dir=str(tmp_path / 'report'), literature={}, report=str(tmp_path / 'report.md'),
        prepared=study.storage._pin(prepared_cfg), comparisons=[dict(name='unit_source', backend='source', width=64, **requests)])
    result = study.report(config)
    assert len(result['paired_family_contrasts']) == 1
    assert result['paired_family_contrasts'][0]['families'] == 3
    monkeypatch.setattr(study._CORE, 'fit', lambda *a, **k: pytest.fail('completed alternate worker must not refit'))
    assert study.run(study.base._json(requests['alternate']['path']))['new_readout_fits'] >= 30
