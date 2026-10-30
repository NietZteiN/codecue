"""Reciprocal-label fairness, causal-prefix numerics and fixed readout guards."""
from copy import deepcopy
import json

import numpy as np
import pytest

from codecue.binding import query_selectivity as query
from codecue.binding import weighted_ridge


def bank(width=8):
    rng = np.random.default_rng(137)
    rows = []; x = []
    for split, groups in [('train', 2), ('development', 6)]:
        for group in range(groups):
            for base in range(8):
                latent = rng.normal(size=width)
                target = [int(query.CLASSES[(group*8+base)%32]), int(query.CLASSES[(group*7+base*3+5)%32])]
                for condition in query.CONDITIONS:
                    prefix = f'{split}:{group}:{base}:{condition}'
                    for role in ('current', 'saved'):
                        rows.append({'id': prefix+':'+role, 'base_id': f'{split}:{group}:{base}',
                            'template_id': f'{split}:template{group}', 'split': split, 'condition': condition,
                            'query_role': role, 'lexical_realization': 0, 'available_bindings': 2,
                            'updates': 1, 'tail_placement': 'before', 'targets': target.copy(),
                            'state_prefix_sha256': prefix, 'positions': [10, 20, 30],
                            'visible_prefixes': [prefix, prefix+'print('+role+')', prefix+'Output:']})
                        x.append(latent)
    return rows, np.array(x, dtype=np.float64)


def config(tmp_path):
    return {'evaluation_role': query.ROLE, 'capture_config': str(tmp_path/'capture.json'),
        'capture_config_sha256': 'a'*64, 'capture_audit_sha256': 'b'*64,
        'capture_manifest_sha256': 'c'*64, 'run_dir': str(tmp_path/'out'), 'report': str(tmp_path/'report.md')}


def test_fixed_recipe_and_declared_head_capacity(tmp_path):
    fixed = query._config(config(tmp_path))
    assert fixed['alpha'] == 100 and fixed['seeds'] == [11, 29, 47]
    assert fixed['layers'] == [8, 16, 24, 31] and fixed['sites'] == list(query.SITES)
    assert fixed['primary'] == {'backend': 'hidden', 'layer': 24, 'site': 'pre_answer', 'condition': 'neutral', 'split': 'development'}
    assert len(fixed['class_values']) == 32 and 0 not in fixed['class_values']
    assert fixed['score_tolerance'] == 1e-8
    assert len([p for p in query._expected(config(tmp_path)).values() if p.suffix == '.npz']) == 45


@pytest.mark.parametrize('field,value', [('evaluation_role', 'final'), ('alpha', 1.), ('seeds', [11]),
    ('feature_dimensions', 64), ('layers', [24]), ('sites', ['pre_answer']),
    ('primary', {'layer': 31}), ('bootstrap', {'draws': 100}), ('score_tolerance', .1), ('query_role_feature', True)])
def test_changed_recipe_rejected_before_metadata_or_payload_reads(tmp_path, monkeypatch, field, value):
    value_config = config(tmp_path); value_config[field] = value
    monkeypatch.setattr(query, '_json', lambda *a, **k: pytest.fail('recipe guard must precede metadata reads'))
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('recipe guard must precede arrays'))
    with pytest.raises(ValueError): query.preflight(value_config)


def test_source_metadata_pin_checked_before_arrays(tmp_path, monkeypatch):
    value = config(tmp_path); (tmp_path/'capture.json').write_text('{}')
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('changed source metadata must precede array access'))
    with pytest.raises(ValueError, match='checksum'): query.preflight(value)


def test_reciprocal_labels_keep_both_twins_and_complete_four_heads():
    rows, _ = bank(); pairs = query.twin_groups(rows)
    labels, truth, canonical, shuffled, _ = query.targets(rows, 11)
    assert len(pairs)*2 == len(rows)
    assert labels.shape == (len(rows), 4) and truth.shape == (len(rows), 128)
    assert np.array_equal(truth.reshape(len(rows), 4, 32).sum(axis=2), np.ones((len(rows), 4)))
    for i, j in pairs:
        assert np.array_equal(labels[i, :2], labels[j, :2][::-1])
        assert np.array_equal(labels[i, 2:], labels[j, 2:][::-1])
        assert np.array_equal(canonical[i], canonical[j]) and np.array_equal(shuffled[i], shuffled[j])
    assert np.array_equal(query.query_labels(rows, canonical), labels[:, :2])


@pytest.mark.parametrize('mutation', ['missing_twin', 'future_prefix', 'target', 'position', 'role', 'group_overlap'])
def test_causal_prefix_and_target_guards(mutation):
    rows, _ = bank()
    if mutation == 'missing_twin': rows.pop()
    elif mutation == 'future_prefix': rows[1]['visible_prefixes'][0] += ' future saved'
    elif mutation == 'target': rows[1]['targets'][0] = int(query.CLASSES[-1])
    elif mutation == 'position': rows[1]['positions'][0] += 1
    elif mutation == 'role': rows[1]['query_role'] = 'current'
    else: rows[-1]['template_id'] = rows[0]['template_id']
    with pytest.raises(ValueError): query.twin_groups(rows)


def test_all_split_condition_queryrole_and_weighted_head_marginals_match():
    rows, _ = bank(); pairs = query.twin_groups(rows)
    train = np.array([r['split'] == 'train' and r['condition'] == 'neutral' for r in rows])
    train_rows = [r for r, keep in zip(rows, train) if keep]
    for seed in query.SEEDS:
        labels, _, _, _, _ = query.targets(rows, seed)
        weights = query.group_weights(train_rows, seed).astype(float)
        result = query.marginal_audit(rows, labels, train, weights, pairs)
        assert len(result['cells']) == 18
        assert result['maximum_weighted_head_count_difference'] < 1e-8
        assert result['query_twin_training_weights_exact']
        for cell in result['cells']:
            counts = np.array(cell['class_counts'])
            assert np.array_equal(counts[0], counts[2]) and np.array_equal(counts[1], counts[3])
            if cell['query_role'] == 'all': assert np.array_equal(counts[0], counts[1])


def test_different_training_weight_for_query_twins_is_rejected():
    rows, _ = bank(); pairs = query.twin_groups(rows)
    train = np.array([r['split'] == 'train' and r['condition'] == 'neutral' for r in rows])
    labels = query.targets(rows, 11)[0]; weights = np.ones(train.sum()); weights[0] = 2
    with pytest.raises(ValueError, match='equal training weights'):
        query.marginal_audit(rows, labels, train, weights, pairs)


def test_prediction_reconstruction_respects_which_canonical_slot_was_queried():
    rows, _ = bank(); labels, _, canonical, shuffled, _ = query.targets(rows, 11)
    train = np.array([r['split'] == 'train' and r['condition'] == 'neutral' for r in rows])
    predictions = labels.copy()
    result = query.metric_cells(rows, labels, canonical, shuffled, predictions, train)
    assert len(result) == 12
    assert all(all(h['accuracy'] == 1 for h in cell['heads']) for cell in result)
    assert all(cell['canonical_reconstruction']['value']['whole_pair_accuracy'] == 1 for cell in result)
    # Queried head correct, unqueried wrong: when current is queried, only the
    # reconstructed current value is correct; saved-query rows reverse this.
    predictions[:, 1] = (labels[:, 1]+1)%32
    result = query.metric_cells(rows, labels, canonical, shuffled, predictions, train)
    for cell in result:
        reconstructed = cell['canonical_reconstruction']['value']
        if cell['query_role'] == 'current':
            assert reconstructed['current_accuracy'] == 1 and reconstructed['saved_accuracy'] == 0
        elif cell['query_role'] == 'saved':
            assert reconstructed['current_accuracy'] == 0 and reconstructed['saved_accuracy'] == 1
        else: assert reconstructed['current_accuracy'] == reconstructed['saved_accuracy'] == .5
        assert reconstructed['whole_pair_accuracy'] == 0
        assert all(h['parameter_count_per_head'] == 131104 for h in cell['heads'])


def test_head_support_and_training_majority_are_reported_separately():
    rows, _ = bank(); labels, _, canonical, shuffled, _ = query.targets(rows, 11)
    train = np.array([r['split'] == 'train' and r['condition'] == 'neutral' for r in rows])
    result = query.metric_cells(rows, labels, canonical, shuffled, labels.copy(), train)
    neutral_dev = next(c for c in result if c['split'] == 'development' and c['condition'] == 'neutral' and c['query_role'] == 'all')
    assert neutral_dev['n'] == 96 and neutral_dev['structural_groups'] == 6
    for head in neutral_dev['heads']:
        assert head['training_classes'] <= 32 and head['evaluation_classes'] <= 32
        assert 0 <= head['out_of_training_support'] <= neutral_dev['n']
        assert 0 <= head['training_majority_accuracy'] <= 1
        assert sum(c['n'] for c in head['template_cells']) == neutral_dev['n']


def test_prequery_independent_objectives_have_close_parameters_and_raw_scores():
    rows, x = bank(); pairs = query.twin_groups(rows)
    labels, truth, _, _, _ = query.targets(rows, 11)
    train = np.array([r['split'] == 'train' and r['condition'] == 'neutral' for r in rows])
    train_rows = [r for r, keep in zip(rows, train) if keep]; weights = query.group_weights(train_rows, 11).astype(float)
    model = weighted_ridge.fit(x[train], truth[train], weights,
        train_ids=[r['id'] for r in train_rows], split='train', alpha=100)
    scores = model.predict(x); result = query.prequery_symmetry(x, truth, train, weights, model, scores, pairs)
    assert result['value']['maximum_coefficient_difference'] <= query.TOLERANCE
    assert result['shuffled']['maximum_absolute_score_difference'] <= query.TOLERANCE
    assert result['value']['analytic_future_query_information'] is False
    assert _has_no_synthetic_feature_leak(x, rows)


def _has_no_synthetic_feature_leak(x, rows):
    # The same feature rows occur under reciprocal query labels.
    pairs = query.twin_groups(rows)
    return np.array_equal(x[pairs[:, 0]], x[pairs[:, 1]])


def test_ulp_argmax_ties_are_reported_without_modifying_or_averaging_scores():
    left = np.zeros((3, 32)); right = left.copy()
    left[:, 0] = 1.; left[:, 1] = 1.-1e-12
    right[:, 0] = 1.-1e-12; right[:, 1] = 1.
    original = left.copy(); result = query._comparison(left, right)
    assert result['argmax_disagreements'] == 3 and result['prediction_agreement_fraction'] == 0
    assert result['all_disagreements_within_fixed_tie_bound']
    assert result['disagreement_maximum_top_two_margin'] < 2e-8
    assert np.array_equal(left, original)
    changed = right.copy(); changed[:, 1] = 1.1
    with pytest.raises(ValueError, match='symmetry'): query._comparison(left, changed)


def test_primary_resamples_components_after_fixed_seed_averaging():
    rows, _ = bank()
    differences = {11: np.ones(len(rows)), 29: -np.ones(len(rows)), 47: np.ones(len(rows))}
    result = query.primary_bootstrap(rows, differences)
    assert np.isclose(result['mean_group_increment'], 1/3)
    assert np.allclose(result['conditional_group_bootstrap_95'], [1/3, 1/3])
    assert result['structural_groups'] == 6 and result['n'] == 96
    assert result['refits_per_draw'] == 0 and result['seeds_are_replications'] is False
    with pytest.raises(ValueError, match='three'): query.primary_bootstrap(rows, {11: differences[11]})


def test_raw_score_schema_rejects_missing_head_and_nonfinite_values():
    with pytest.raises(ValueError): query._predictions(np.zeros((4, 64)))
    bad = np.zeros((4, 128)); bad[1, 1] = np.nan
    with pytest.raises(ValueError): query._predictions(bad)


def test_parameter_scores_and_predictions_are_lossless_pickle_free(tmp_path):
    rows, x = bank(); labels, truth, _, _, _ = query.targets(rows, 11)
    train = np.array([r['split'] == 'train' and r['condition'] == 'neutral' for r in rows])
    model = weighted_ridge.fit(x[train], truth[train], np.ones(train.sum()),
        train_ids=[r['id'] for r, keep in zip(rows, train) if keep], split='train')
    scores = model.predict(x); path = tmp_path/'fit.npz'
    query._npz(path, {**model.parameters, 'metadata': np.frombuffer(query._json_bytes(model.metadata), dtype=np.uint8),
        'scores': scores, 'labels': labels})
    with np.load(path, allow_pickle=False) as saved:
        restored = weighted_ridge.from_parameters(json.loads(saved['metadata'].tobytes()), {key: saved[key] for key in model.parameters})
        assert np.array_equal(restored.predict(x), scores)
        assert np.array_equal(query._predictions(restored.predict(x)), query._predictions(saved['scores']))
    with pytest.raises(ValueError, match='already differs'): query._npz(path, {'scores': scores+1})


def completed_fixture(tmp_path, monkeypatch, *, oversized=False, sealed=True):
    workspace = tmp_path/'workspace'; workspace.mkdir()
    value = config(workspace)
    capture_path = workspace/'configs/capture.json'; capture_path.parent.mkdir()
    capture = {'synthetic': 'capture metadata'}; capture_path.write_text(json.dumps(capture))
    value['capture_config'] = str(capture_path); value['capture_config_sha256'] = query._sha(capture_path)
    def metadata(c):
        query._config(c)
        return capture, {'identity_hash': 'capture'}, {'chunk_checksums': {}}, {}
    monkeypatch.setattr(query, '_source_metadata', metadata)
    snapshot = tmp_path/'fit_snapshot'
    files = {'src/codecue/synthetic.py': b'pass\n', 'scripts/env.sh': b'# synthetic\n'}
    source_files = {}
    for name, content in files.items():
        path = snapshot/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content)
        source_files[name] = query._sha(path)
    source = {'git_revision': 'original-fit', 'source_files': source_files, 'source_sha256': query.digest(source_files)}
    frozen_capture = snapshot/'configs/capture.json'; frozen_capture.parent.mkdir(); frozen_capture.write_text(capture_path.read_text())
    frozen_config = snapshot/'configs/query.json'; frozen_config.write_text(json.dumps(value))
    frozen = {'snapshot_id': 'synthetic', 'code': source, 'workspace_root': str(workspace),
        'config_files': {'configs/capture.json': query._sha(frozen_capture), 'configs/query.json': query._sha(frozen_config)}}
    (snapshot/'frozen_manifest.json').write_text(json.dumps(frozen))
    monkeypatch.setattr(query, 'code_identity', lambda: {'source_sha256': 'e'*64, 'git_revision': 'new-reader'})
    expected = query._expected(value)
    for name, path in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if name != 'summary': path.write_text('{}' if path.suffix == '.json' else 'synthetic')
    fit_records = []
    for site_index, site in enumerate(query.SITES):
        for backend, layer in [('hidden', layer) for layer in query.LAYERS]+[('surface', -1)]:
            for seed in query.SEEDS:
                name = query.fit_name(backend, layer, site_index, seed); cells = []
                for split, condition in [('train', 'neutral')]+[('development', c) for c in query.CONDITIONS]:
                    for role in ('all', 'current', 'saved'):
                        n = (2304 if split == 'train' else 768)//(1 if role == 'all' else 2)
                        cells.append({'split': split, 'condition': condition, 'query_role': role, 'n': n,
                            'structural_groups': 18 if split == 'train' else 6,
                            'heads': [{'head': h, 'n': n, 'training_rows': 2304, 'parameter_count_per_head': 131104} for h in query.HEADS]})
                fit_records.append({'name': name, 'artifact': str(expected[name]), 'backend': backend,
                    'layer': layer, 'site': site, 'seed': seed, 'cells': cells,
                    'model': {'n_train': 2304, 'features': 4096, 'targets': 128, 'alpha': 100., 'dtype': 'float64',
                        'factorizations': 1, 'heldout_rows_used_for_fit': 0, 'fit_split': 'train', 'output_columns_independent': True}})
    summary = {'status': 'complete_exploratory', 'evaluation_role': query.ROLE, 'config_hash': query.digest(value),
        'analysis_source': source, 'capture_identity': 'capture', 'fits': fit_records, 'cases': 9216,
        'retained_query_twins': 4608, 'factorizations': 45, 'independent_heads': 180, 'parameter_count_per_head': 131104,
        'parameter_replay_rows': 414720, 'class_values': query.CLASSES.tolist(), 'heads': list(query.HEADS),
        'float64_standardization_and_fitting': True, 'query_role_is_feature': False, 'behavioral_response_features': False,
        'new_model_queries': 0, 'generated_holdouts_opened': False, 'mechanism_C_fitted': False,
        'coverage': {'structural_groups': {'train': 18, 'development': 6}},
        'primary_comparison': {'primary': query.PRIMARY, 'structural_groups': 6, 'n': 768, 'bootstrap': query.BOOTSTRAP,
            'refits_per_draw': 0, 'seeds_are_replications': False}}
    if oversized: summary['synthetic_padding'] = 'x'*(8*1024**2)
    expected['summary'].write_text(json.dumps(summary))
    numerical_audit = {'status': 'passed', 'config_hash': query.digest(value), 'capture_identity': 'capture',
        'factorizations': 45, 'independent_heads': 180, 'parameter_replay_rows': 414720,
        'serialized_raw_scores_and_predictions_exact': True, 'complete_query_twins_all_sites': True,
        'per_head_classes': 32, 'parameter_count_per_head': 131104, 'prequery_score_tolerance_absolute': query.TOLERANCE,
        'behavioral_response_features': False, 'new_model_queries': 0, 'generated_holdouts_opened': False}
    expected['audit'].write_text(json.dumps(numerical_audit))
    registration = {'evaluation_role': query.ROLE, 'config': value, 'config_hash': query.digest(value),
        'capture_identity': 'capture', 'analysis_source': source, 'generated_holdouts_opened': False,
        'new_model_queries': 0, 'behavioral_response_features': False}
    (expected['summary'].parent/'registration.json').write_text(json.dumps(registration))
    review = {**summary, 'wall_seconds': 1., 'artifacts': {name: {'path': str(path), 'sha256': query._sha(path)} for name, path in expected.items()}}
    review_path = expected['summary'].parent/'review_v1.json'; review_path.write_text(json.dumps(review))
    if sealed: query.seal(value, query._sha(review_path), str(snapshot))
    return value, source, review, review_path


def test_completed_reuse_requires_all_45_fits_and_all_five_supporting_artifacts(tmp_path, monkeypatch):
    value, source, review, _ = completed_fixture(tmp_path, monkeypatch)
    assert len(review['artifacts']) == 50
    assert query._reuse(value, source) == review


@pytest.mark.parametrize('missing', ['hidden_layer24_site2_seed11', 'report', 'cases', 'audit'])
def test_missing_artifact_entry_cannot_bypass_any_checksum(tmp_path, monkeypatch, missing):
    value, source, review, path = completed_fixture(tmp_path, monkeypatch)
    receipt_path = path.parent/query.COMPLETION_NAME
    receipt = json.loads(receipt_path.read_text()); receipt['artifacts'].pop(missing); receipt_path.write_text(json.dumps(receipt))
    original_sha = query._sha
    def checked_sha(p):
        if p in [v for v in query._expected(value).values() if v.suffix == '.npz']:
            pytest.fail('inventory check must precede artifact hash loop')
        return original_sha(p)
    monkeypatch.setattr(query, '_sha', checked_sha)
    with pytest.raises(ValueError, match='inventory'): query._reuse(value, source)


def test_completed_fit_paths_must_match_actual_fixed_hashed_parameter_files(tmp_path, monkeypatch):
    value, source, review, path = completed_fixture(tmp_path, monkeypatch)
    review['fits'][0]['artifact'] = str(tmp_path/'other.npz')
    summary_path = query._expected(value)['summary']; summary = {k: v for k, v in review.items() if k not in ('artifacts', 'wall_seconds')}
    summary_path.write_text(json.dumps(summary)); review['artifacts']['summary']['sha256'] = query._sha(summary_path)
    path.write_text(json.dumps(review))
    receipt_path = path.parent/query.COMPLETION_NAME; receipt = json.loads(receipt_path.read_text())
    receipt['review'].update(sha256=query._sha(path), bytes=path.stat().st_size)
    receipt['artifacts'] = review['artifacts']; receipt_path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='fit paths'): query._reuse(value, source)


def test_scientific_capture_fits_cannot_accidentally_run_on_login_host(tmp_path, monkeypatch):
    monkeypatch.setattr(query, 'preflight', lambda c: {'status': 'passed'})
    monkeypatch.setattr(query, '_load', lambda *a: pytest.fail('unscheduled run must not read activations'))
    monkeypatch.delenv('SLURM_JOB_ID', raising=False)
    with pytest.raises(RuntimeError, match='sbatch'): query.run(config(tmp_path))
    assert not (tmp_path/'out').exists()


def test_primary_accepts_only_unaggregated_per_fit_binary_correctness_differences():
    rows, _ = bank(); base = {seed: np.zeros(len(rows)) for seed in query.SEEDS}
    for invalid in (np.full(len(rows), .25), np.zeros((len(rows), 2)), np.full(len(rows), np.nan)):
        with pytest.raises(ValueError, match='binary-correctness'):
            query.primary_bootstrap(rows, {**base, 11: invalid})


def test_oversized_scientific_result_seals_without_relaxing_general_metadata_cap_or_changing_results(tmp_path, monkeypatch):
    value, source, review, path = completed_fixture(tmp_path, monkeypatch, oversized=True, sealed=False)
    expected = query._expected(value)
    pinned_before = {str(p): query._sha(p) for p in [path, path.parent/'registration.json', *expected.values()]}
    assert path.stat().st_size > 8*1024**2
    with pytest.raises(ValueError, match='bounded'): query._json(path)
    receipt = query.seal(value, query._sha(path), str(tmp_path/'fit_snapshot'))
    assert (path.parent/query.COMPLETION_NAME).stat().st_size < 8*1024**2
    assert receipt['fit_source']['source_sha256'] == source['source_sha256']
    assert receipt['seal_reader_source']['source_sha256'] != source['source_sha256']
    assert receipt['scientific_artifacts_changed'] is False and receipt['new_fits'] == 0
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('completion migration must not load parameter/activation arrays'))
    assert query.completed_result(value) == review
    assert {p: query._sha(p) for p in pinned_before} == pinned_before


def test_seal_is_idempotent_and_historical_audit_does_not_require_current_reader_to_be_fit_source(tmp_path, monkeypatch):
    value, source, review, path = completed_fixture(tmp_path, monkeypatch)
    receipt_path = path.parent/query.COMPLETION_NAME; original_bytes = receipt_path.read_bytes()
    monkeypatch.setattr(query, 'code_identity', lambda: {'source_sha256': 'f'*64, 'git_revision': 'later-reader'})
    again = query.seal(value, query._sha(path), str(tmp_path/'fit_snapshot'))
    assert receipt_path.read_bytes() == original_bytes
    assert again['seal_reader_source']['git_revision'] == 'new-reader'
    assert query.completed_result(value)['analysis_source'] == source
    assert query.audit(value)['status'] == 'passed'
    monkeypatch.setattr(query, '_result_payload', lambda *a: pytest.fail('run reuse must reject changed source before reading results'))
    with pytest.raises(ValueError, match='cannot change'): query._reuse(value, {'source_sha256': 'f'*64})


def test_mismatched_original_registration_source_fails_before_result_payload_is_read(tmp_path, monkeypatch):
    value, _, _, path = completed_fixture(tmp_path, monkeypatch, sealed=False)
    registration_path = path.parent/'registration.json'
    registration = json.loads(registration_path.read_text()); registration['analysis_source']['source_sha256'] = 'a'*64
    registration_path.write_text(json.dumps(registration))
    monkeypatch.setattr(query, '_result_payload', lambda *a: pytest.fail('original source must be verified before rich results'))
    with pytest.raises(ValueError, match='frozen original fit source'):
        query.seal(value, query._sha(path), str(tmp_path/'fit_snapshot'))
    assert not (path.parent/query.COMPLETION_NAME).exists()


def test_changed_frozen_source_configuration_fails_before_rich_payload(tmp_path, monkeypatch):
    value, _, _, path = completed_fixture(tmp_path, monkeypatch, sealed=False)
    (tmp_path/'fit_snapshot/configs/capture.json').write_text('{"changed": true}')
    monkeypatch.setattr(query, '_result_payload', lambda *a: pytest.fail('frozen config verification must precede rich payload'))
    with pytest.raises(ValueError, match='frozen configuration changed'):
        query.seal(value, query._sha(path), str(tmp_path/'fit_snapshot'))


def test_bad_result_sha_rejected_before_json_payload_parsing(tmp_path, monkeypatch):
    value, _, _, path = completed_fixture(tmp_path, monkeypatch, sealed=False)
    old = type(path).read_text
    def guarded_read(self, *args, **kwargs):
        if self == path: pytest.fail('rich JSON was parsed before its explicit SHA matched')
        return old(self, *args, **kwargs)
    monkeypatch.setattr(type(path), 'read_text', guarded_read)
    with pytest.raises(ValueError, match='payload checksum'):
        query.seal(value, '0'*64, str(tmp_path/'fit_snapshot'))


def test_scientific_result_has_an_independent_finite_size_cap_before_hash_read(tmp_path, monkeypatch):
    path = tmp_path/'result.json'; path.write_text(json.dumps({'large': 'x'*2048}))
    monkeypatch.setattr(query, 'MAX_RESULT_BYTES', 1024)
    monkeypatch.setattr(query, '_sha', lambda *a: pytest.fail('over-limit scientific result must not be hashed/read'))
    with pytest.raises(ValueError, match='payload bound'): query._result_payload(path, 'a'*64)


def test_compact_role_guard_precedes_rich_result_access(tmp_path, monkeypatch):
    value, _, _, path = completed_fixture(tmp_path, monkeypatch)
    receipt_path = path.parent/query.COMPLETION_NAME
    receipt = json.loads(receipt_path.read_text()); receipt['evaluation_role'] = 'final_confirmation'
    receipt_path.write_text(json.dumps(receipt))
    monkeypatch.setattr(query, '_result_payload', lambda *a: pytest.fail('wrong compact role must precede result access'))
    with pytest.raises(ValueError, match='role/config'): query.completed_result(value)


def test_reserved_artifact_path_rejected_before_any_rich_payload(tmp_path, monkeypatch):
    value, _, _, path = completed_fixture(tmp_path, monkeypatch)
    receipt_path = path.parent/query.COMPLETION_NAME
    receipt = json.loads(receipt_path.read_text())
    receipt['artifacts']['summary']['path'] = str(tmp_path/'binding/final/summary.json')
    receipt_path.write_text(json.dumps(receipt))
    monkeypatch.setattr(query, '_result_payload', lambda *a: pytest.fail('reserved artifact path must precede result payload'))
    with pytest.raises(ValueError, match='reserved'): query.completed_result(value)


def test_tampered_parameter_bytes_fail_completion_audit_without_refitting(tmp_path, monkeypatch):
    value, _, _, _ = completed_fixture(tmp_path, monkeypatch)
    query._expected(value)['hidden_layer24_site2_seed11'].write_bytes(b'changed parameter bytes')
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('hash verification must not load/refit models'))
    with pytest.raises(ValueError, match='artifact checksum'): query.audit(value)


def test_fixed_scientific_counts_are_validated_even_for_an_explicitly_pinned_result(tmp_path, monkeypatch):
    value, _, review, path = completed_fixture(tmp_path, monkeypatch, sealed=False)
    review['factorizations'] = 46; path.write_text(json.dumps(review))
    with pytest.raises(ValueError, match='fixed source/count'):
        query.seal(value, query._sha(path), str(tmp_path/'fit_snapshot'))
    assert not (path.parent/query.COMPLETION_NAME).exists()


def test_new_fits_require_frozen_source_before_writing_any_registration(tmp_path, monkeypatch):
    monkeypatch.setattr(query, 'preflight', lambda c: {'status': 'passed'})
    monkeypatch.setenv('SLURM_JOB_ID', 'synthetic')
    monkeypatch.setattr(query, '_load', lambda *a: pytest.fail('unfrozen run must not open captures'))
    def unfrozen(): raise ValueError('new scientific readout fits require a frozen source snapshot')
    monkeypatch.setattr(query, '_current_fit_snapshot', unfrozen)
    with pytest.raises(ValueError, match='frozen source snapshot'): query.run(config(tmp_path))
    assert not (tmp_path/'out').exists()
