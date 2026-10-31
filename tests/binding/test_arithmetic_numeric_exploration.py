"""Compression, target semantics, grouped selection and replay invariants."""
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import arithmetic_numeric_exploration as study
from codecue.binding import arithmetic_local_probes as local
from codecue.binding import relationship_capture as base
from codecue.binding.weighted_ridge import fit


def test_all_signed_integer_targets_round_trip_through_perfect_heads():
    values = np.arange(-96, 97)
    scores = study.targets(values)
    assert scores.shape == (193, study.HEAD_WIDTH)
    decoded = study.predictions(scores)
    assert np.array_equal(decoded['digits_joint'], values)
    assert decoded['digits_valid'].all()
    result = study.score_heads(scores, values, np.asarray(['a'] * len(values)))
    assert all(v['exact'] == 1 for v in result.values())
    assert all(v.get('mae', 0) == 0 for v in result.values())


def test_signed_residues_differ_from_absolute_decimal_components():
    labels = study.class_labels(np.asarray([-12, 12]))
    assert labels['units'].tolist() == [2, 2]
    assert labels['tens'].tolist() == [1, 1]
    assert labels['mod10'].tolist() == [8, 2]
    assert labels['mod5'].tolist() == [3, 2]


def test_inconsistent_zero_sign_cannot_count_as_correct_digit_reconstruction():
    scores = study.targets(np.asarray([0]))
    band = study.slices()['units']
    scores[:, band] = 0; scores[0, band.start + 5] = 1
    result = study.score_heads(scores, np.asarray([0]), np.asarray(['a']))
    assert result['digits_joint']['exact'] == 0
    assert result['digits_joint']['invalid'] == 1


def test_out_of_domain_digit_reconstruction_is_invalid():
    scores = study.targets(np.asarray([96]))
    band = study.slices()['units']; scores[:, band] = 0; scores[0, band.start + 9] = 1
    assert not study.predictions(scores)['digits_valid'][0]


@pytest.mark.parametrize('values', [np.asarray([97]), np.asarray([-97]), np.asarray([1.5]), np.asarray([[1]])])
def test_invalid_target_domain_rejected(values):
    with pytest.raises(ValueError): study.targets(values)


@pytest.mark.parametrize('scores', [np.zeros((2, study.HEAD_WIDTH - 1)), np.full((1, study.HEAD_WIDTH), np.nan)])
def test_invalid_head_geometry_rejected(scores):
    with pytest.raises(ValueError): study.predictions(scores)


def test_projection_prefix_preserves_original_64_coordinate_map():
    for seed in study.SEEDS:
        transform = study.nested_projection(1024, seed)
        assert transform.shape == (1024, 1024)
        assert np.array_equal(transform[:, :64] * 4, local.projection(1024, seed))
        assert np.array_equal(transform, study.nested_projection(1024, seed))
    assert not np.array_equal(study.nested_projection(1024, 11), study.nested_projection(1024, 29))


def test_source_folding_matches_direct_hashing_at_each_smaller_width():
    from sklearn.feature_extraction.text import HashingVectorizer
    texts = ['x = -3\ny = x + x', 'renamed_name = 7\ny = renamed_name - x']
    def hashed(width):
        return HashingVectorizer(analyzer='char', ngram_range=(3, 5), n_features=width,
            norm=None, alternate_sign=True).transform(texts).toarray().astype(np.float32)
    full = hashed(8192)
    for width in (64, 256, 1024, 4096, 8192):
        assert np.array_equal(study.fold_source(full, width), hashed(width))


def records():
    from copy import deepcopy
    panel = study.score_heads(study.targets(np.asarray([-1, 0, 1])), np.asarray([-1, 0, 1]), np.asarray(['a', 'b', 'c']))
    return [dict(seed=s, fold=f, alpha=a, validation=deepcopy(panel)) for s in study.SEEDS for f in range(3) for a in study.ALPHAS]


def test_train_grid_ties_choose_stronger_regularization():
    assert set(study.select(records()).values()) == {10000.}


def test_each_format_has_independent_predeclared_selection_criterion():
    data = records()
    for r in data:
        r['validation']['scalar']['mae'] = 0 if r['alpha'] == 1 else 1
        r['validation']['digits_joint']['exact'] = 1 if r['alpha'] == 100 else 0
        r['validation']['parity']['balanced_accuracy'] = 1 if r['alpha'] == 10000 else .5
    selected = study.select(data)
    assert selected['scalar'] == 1 and selected['digits_joint'] == 100 and selected['parity'] == 10000


@pytest.mark.parametrize('kind', ['missing', 'duplicate'])
def test_incomplete_or_duplicate_train_grid_rejected(kind):
    data = records()
    data = data[:-1] if kind == 'missing' else data[:-1] + [data[0]]
    with pytest.raises(ValueError): study.select(data)


def test_only_supported_component_classes_enter_macro_recall():
    values = np.asarray([-2, -1])
    result = study.score_heads(study.targets(values), values, np.asarray(['a', 'a']))
    assert result['sign']['support'] == {'0': 2}
    assert result['sign']['balanced_accuracy'] == 1


def test_feature_metadata_does_not_read_gold_values_or_parents():
    first = dict(statement=4, depth=2, value=-7, group='a', parent=1)
    second = dict(first, value=96, parent=10000, group='different')
    assert np.array_equal(study.metadata_features([first]), study.metadata_features([second]))


def test_small_positive_control_and_save_reload(tmp_path):
    values = np.arange(-9, 10)
    x = np.eye(len(values)); labels = study.targets(values)
    model = fit(x, np.concatenate((labels, labels), axis=1), np.ones(len(values)),
        [f'point{i}' for i in range(len(values))], 'train', 1.)
    replay, artifacts = study.save_model(tmp_path, 'positive', model)
    assert np.array_equal(model.predict(x), replay.predict(x))
    real, control = np.split(replay.predict(x), 2, axis=1)
    assert study.score_heads(real, values, np.asarray(['a'] * len(values)))['categorical']['exact'] == 1
    assert np.allclose(real, control, rtol=1e-12, atol=1e-12)
    for entry in artifacts.values(): assert Path(entry['path']).is_file()


def test_resume_detects_changed_parameters(tmp_path):
    payload = tmp_path / 'payload.txt'; payload.write_text('original')
    config, source = {}, {'snapshot_id': 'test'}
    path = tmp_path / 'bank.json'
    base._put(path, dict(source=source, config_hash=study.digest(config), artifacts=dict(payload=study.storage._pin(payload))))
    assert study.resume(path, config, source)
    payload.write_text('changed')
    with pytest.raises(ValueError): study.resume(path, config, source)


def test_complete_small_worker_keeps_dev_out_of_fits_and_reuses_saved_completion(tmp_path, monkeypatch):
    rows, cases = [], []
    for split, families in [('train', 6), ('development', 3), ('calibration', 3)]:
        for family in range(families):
            for draw in range(2):
                values = [0, 1, 2, 3, family % 3 + draw, family % 3 + draw + 1]
                row = dict(id=f'{split}-{family}-{draw}', split=split, component_id=f'{split}-{family}',
                    family_stratum='depth2:add', depth=2, numeric_seed=11, numeric_draw=draw,
                    lexical_realization=0, oracle=dict(writes=[dict(value=v) for v in values]))
                rows.append(row)
                cases.append(dict(descriptors=[dict(kind='definition', statement=i, value=v) for i, v in enumerate(values)]))
    table = study.examples(rows, cases)
    cache_folder = tmp_path / 'cache'; cache_folder.mkdir()
    cache_config = dict(run_dir=str(cache_folder))
    cache_path = tmp_path / 'cache.json'; base._put(cache_path, cache_config)
    base._put(cache_folder / 'results.json', dict(table_sha256=study.digest(table), width=64, features=dict(source={})))
    matrix = np.zeros((len(table), 64), np.float32)
    # Explicitly make copying possible without using targets from held-out rows
    # during fitting; labels are encoded in the synthetic measurement itself.
    for i, e in enumerate(table): matrix[i, e['value'] + 10] = 1
    monkeypatch.setattr(study, 'load_features', lambda entry: matrix)
    source = dict(snapshot_id='synthetic-unit-test')
    monkeypatch.setattr(study.common, 'validate_role', lambda config, role: source)
    monkeypatch.setattr(study.audit, 'load_cache', lambda config: ({}, {}, dict(model='synthetic'), rows, cases))
    def completed(config):
        path = Path(config['run_dir']) / 'results.json'
        return base._json(path) if path.exists() else {}
    monkeypatch.setattr(study.common, 'completed', completed)
    def folds(table):
        groups = sorted({e['group'] for e in table})
        mapping = {g: i % 3 for i, g in enumerate(groups)}
        return np.asarray([mapping[e['group']] for e in table])
    monkeypatch.setattr(study.common, 'folds', folds)
    config = dict(evaluation_role=study.FIT, run_dir=str(tmp_path / 'worker'), backend='source', role='computed_definition',
        widths=[64], cache_config=study.storage._pin(cache_path))
    result = study.run(config)
    assert result['cv_banks'] == 27
    for path in (tmp_path / 'worker').glob('*_metadata.json'):
        metadata = base._json(path)
        assert metadata['training_ids'] and all(identity.startswith('train-') for identity in metadata['training_ids'])
    for path in (tmp_path / 'worker').glob('*_cv_*.json'):
        if path.name.endswith('_metadata.json'): continue
        bank = base._json(path)
        assert not set(bank['fit_groups']) & set(bank['validation_groups'])
        assert all(g.startswith('train-') for g in bank['fit_groups'] + bank['validation_groups'])
    for bank in result['fits']:
        with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as saved:
            assert set(saved['split']) == {'train', 'development', 'calibration'}
    monkeypatch.setattr(study, 'fit', lambda *a, **k: pytest.fail('completed worker must not refit'))
    assert study.run(config)['new_readout_fits'] == result['new_readout_fits']
