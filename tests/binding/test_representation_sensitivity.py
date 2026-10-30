"""Synthetic projection, pairing, complete-target and provenance checks."""
from copy import deepcopy
import json

import numpy as np
import pytest

from codecue.binding import representation_sensitivity as study


def rows_and_features(width=8, train_bases=80, dev_bases=24):
    rng = np.random.default_rng(716)
    neutral = rng.normal(size=(train_bases+dev_bases, width))
    rotations = {'neutral': np.eye(width)}
    for condition in study.CONDITIONS[1:]:
        rotations[condition] = np.linalg.qr(rng.normal(size=(width, width)))[0]
    rows = []; vectors = []
    for i in range(train_bases+dev_bases):
        split = 'train' if i < train_bases else 'development'
        index = i if split == 'train' else i-train_bases
        for condition in study.CONDITIONS:
            rows.append({'id': f'{split}:{index}:{condition}', 'base_id': f'{split}:{index}',
                'template_id': f'{split}:template{index//8}', 'split': split,
                'condition': condition, 'query_role': 'current', 'lexical_realization': 0,
                'available_bindings': 2, 'updates': 1, 'tail_placement': 'before',
                'targets': [int(study.CLASSES[index%32]), int(study.CLASSES[(index*7+3)%32])],
                'state_prefix_sha256': f'{split}:{index}:{condition}:prefix'})
            shift = {'neutral': 0., 'informative': 2., 'misleading': -3.}[condition]
            vectors.append(neutral[i] @ rotations[condition]+shift)
    return rows, np.array(vectors)


def config(tmp_path):
    return {'evaluation_role': study.ROLE,
        'capture_config': str(tmp_path/'capture.json'), 'capture_config_sha256': 'a'*64,
        'capture_audit_sha256': 'b'*64, 'capture_manifest_sha256': 'c'*64,
        'run_dir': str(tmp_path/'output'), 'report': str(tmp_path/'report.md')}


def test_recipe_is_fixed_and_targets_are_two_complete_class_heads(tmp_path):
    fixed = study._validate(config(tmp_path))
    assert fixed['ranks'] == [1, 2, 4, 8, 16, 32, 64]
    assert fixed['pca']['components'] == 64
    rows, _ = rows_and_features()
    labels, targets = study.complete_targets(rows)
    assert labels.shape == (len(rows), 2)
    assert targets.shape == (len(rows), 64)
    assert np.array_equal(targets.reshape(len(rows), 2, 32).sum(axis=2), np.ones((len(rows), 2)))
    assert len(study.CLASSES) == 32 and 0 not in study.CLASSES


@pytest.mark.parametrize('field,value', [('evaluation_role', 'final_confirmation'), ('alpha', 1.),
    ('ranks', [1, 2]), ('layer', 31), ('sites', ['pre_query_state']),
    ('pca', {'components': 32}), ('split', 'final'), ('control_seeds', [11])])
def test_changed_scientific_recipe_rejected_before_payload_access(tmp_path, monkeypatch, field, value):
    value_config = config(tmp_path); value_config[field] = value
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('no payload access allowed'))
    with pytest.raises(ValueError):
        study.preflight(value_config)


def test_role_guard_precedes_even_metadata_reads(tmp_path, monkeypatch):
    value = config(tmp_path); value['evaluation_role'] = 'final'
    monkeypatch.setattr(study, '_json', lambda *a, **k: pytest.fail('role must be checked first'))
    with pytest.raises(ValueError, match='discovery'):
        study.preflight(value)


def test_pinned_metadata_is_checked_before_numpy_load(tmp_path, monkeypatch):
    value = config(tmp_path); (tmp_path/'capture.json').write_text('{}')
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('no payload access allowed'))
    with pytest.raises(ValueError, match='checksum'):
        study.preflight(value)


def test_bounded_metadata_and_sealed_paths_are_never_opened(tmp_path, monkeypatch):
    path = tmp_path/'too_big.json'; path.write_bytes(b'x'*(study.MAX_JSON_BYTES+1))
    monkeypatch.setattr(study, '_sha', lambda *a, **k: pytest.fail('oversized metadata must not be hashed'))
    with pytest.raises(ValueError, match='bounded'):
        study._json(path)
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log, '_protected_outcome', lambda p: True)
    with pytest.raises(ValueError, match='reserved'):
        study._json(tmp_path/'missing.json')


def test_symlink_to_reserved_payload_is_rejected_before_content_read(tmp_path):
    folder = tmp_path/'binding'/'final'; folder.mkdir(parents=True)
    target = folder/'outcomes.json'; target.write_text('{}')
    link = tmp_path/'allowed.json'; link.symlink_to(target)
    with pytest.raises(ValueError, match='reserved'):
        study._json(link)


def test_row_groups_conditions_and_targets_are_guarded():
    rows, _ = rows_and_features()
    checked = study._row_checks(rows)
    assert checked['structural_groups'] == {'train': 10, 'development': 3}
    for mutation in ('split', 'condition', 'target', 'group', 'duplicate', 'base'):
        changed = deepcopy(rows)
        if mutation == 'split': changed[0]['split'] = 'final'
        elif mutation == 'condition': changed[0]['condition'] = 'new'
        elif mutation == 'target': changed[0]['targets'] = [0, 1]
        elif mutation == 'group': changed[-1]['template_id'] = changed[0]['template_id']
        elif mutation == 'duplicate': changed[1]['id'] = changed[0]['id']
        elif mutation == 'base': changed[1]['targets'][0] = int(study.CLASSES[-1])
        with pytest.raises(ValueError):
            study._row_checks(changed)


def test_prequery_twins_are_deduplicated_but_both_complete_targets_remain():
    rows, _ = rows_and_features()
    paired = []
    for row in rows:
        for query in ('current', 'saved'):
            other = deepcopy(row); other['query_role'] = query; other['id'] += ':'+query
            paired.append(other)
    before = study.site_indices(paired, 'pre_query_state')
    after = study.site_indices(paired, 'pre_answer')
    assert len(before) == len(rows) and len(after) == len(paired)
    assert all(paired[i]['query_role'] == 'current' for i in before)
    assert study.complete_targets([paired[i] for i in before])[1].shape[1] == 64
    paired[1]['targets'][0] = int(study.CLASSES[-1])
    with pytest.raises(ValueError, match='two-query'):
        study.site_indices(paired, 'pre_query_state')


def test_semantic_pairs_use_exact_training_relatives_without_outcome_pairing():
    rows, _ = rows_and_features()
    source, target, ids = study.semantic_pairs(rows, 'misleading')
    assert len(source) == 80 and len(set(ids)) == 80
    assert all(rows[i]['split'] == 'train' for i in np.r_[source, target])
    assert all(rows[i]['base_id'] == rows[j]['base_id'] for i, j in zip(source, target))
    changed = deepcopy(rows); changed[1]['lexical_realization'] = 99
    with pytest.raises(ValueError, match='complete exact'):
        study.semantic_pairs(changed, 'informative')
    changed = deepcopy(rows); changed[1]['targets'][0] = int(study.CLASSES[-1])
    with pytest.raises(ValueError, match='targets/groups'):
        study.semantic_pairs(changed, 'informative')


def test_pooled_pca_is_fitted_only_on_training_rows_and_records_loss():
    rows, x = rows_and_features()
    projected, params, metadata = study.fit_projection(x, rows, components=4)
    assert projected.shape == (len(rows), 4)
    assert metadata['heldout_rows_used_for_fit'] == 0
    assert len(metadata['training_ids']) == 240
    assert metadata['condition_counts'] == dict.fromkeys(study.CONDITIONS, 80)
    assert 0 < metadata['retained_variance_fraction'] <= 1+1e-12
    changed = x.copy(); changed[[r['split'] == 'development' for r in rows]] = 1e9
    _, again, more = study.fit_projection(changed, rows, components=4)
    for name in params:
        assert np.array_equal(params[name], again[name])
    assert metadata == more


def test_pca_rejects_missing_condition_and_underidentified_subspaces():
    rows, x = rows_and_features()
    missing = deepcopy(rows); missing[0]['condition'] = 'informative'
    with pytest.raises(ValueError, match='equally'):
        study.fit_projection(x, missing, components=4)
    with pytest.raises(ValueError, match='underidentified'):
        study.fit_projection(x, rows, components=1000)
    with pytest.raises(ValueError, match='rank deficient'):
        study.fit_projection(np.ones_like(x), rows, components=4)


def test_alignment_recovers_train_rotation_and_never_fits_development_rows():
    rows, x = rows_and_features(width=4)
    aligned, models, metadata = study.align_conditions(x, rows, {'test': 'synthetic'})
    for condition in study.CONDITIONS[1:]:
        source, target, _ = study.semantic_pairs(rows, condition, 'development')
        assert np.allclose(aligned[source], x[target], atol=1e-12)
        assert metadata[condition]['anchor_cross_rank'] == 4
        assert metadata[condition]['heldout_rows_used_for_fit'] == 0
        assert all(identity.startswith('train:') for identity in metadata[condition]['source_training_case_ids'])
    changed = x.copy(); changed[[r['split'] == 'development' for r in rows]] *= 1e4
    _, again, _ = study.align_conditions(changed, rows, {'test': 'synthetic'})
    for condition in models:
        assert np.array_equal(models[condition].rotation, again[condition].rotation)


def test_alignment_rejects_rank_deficient_anchor_mapping():
    rows, x = rows_and_features(width=4); x[:, -1] = 1
    with pytest.raises(ValueError, match='underidentified'):
        study.align_conditions(x, rows, {'test': 'synthetic'})


def test_complete_target_validation_rejects_missing_or_float_indices():
    rows, _ = rows_and_features()
    for bad in [np.zeros((len(rows), 1), int), np.zeros((len(rows), 2), float), np.full((len(rows), 2), 32)]:
        with pytest.raises(ValueError, match='two complete'):
            study.complete_targets(rows, bad)


def test_cell_metrics_keep_slot_and_whole_pair_denominators_separate():
    rows, _ = rows_and_features(); labels, targets = study.complete_targets(rows)
    mask = np.array([r['split'] == 'development' and r['condition'] == 'neutral' for r in rows])
    scores = targets.copy(); first = np.flatnonzero(mask)[0]; scores[first, :32] = 0.; scores[first, 31] = 2
    result = study.cell_metrics(scores, labels, rows, mask, majority=[0, 0])
    assert result['n'] == 24 and result['structural_groups'] == 3
    assert result['saved_accuracy'] == 1 and result['current_accuracy'] == result['joint_accuracy'] == 23/24
    assert sum(c['n'] for c in result['template_cells']) == 24
    assert result['saved_score_mse'] == 0


def test_paired_bootstrap_uses_groups_and_saved_predictions_without_refits():
    rows, _ = rows_and_features(); labels, _ = study.complete_targets(rows)
    bad = (labels+1)%32
    result = study.paired_group_comparisons(bad, labels, labels, rows, draws=100)
    assert len(result) == 6
    assert all(c['mean_group_increment'] == 1. for c in result)
    assert all(c['conditional_group_bootstrap_95'] == [1., 1.] for c in result)
    assert all(c['structural_groups'] == 3 and c['n'] == 24 and c['refits_per_draw'] == 0 for c in result)
    assert all(c['multiplicity_adjusted'] is False for c in result)


def test_finite_bank_keeps_all_tasks_conditions_ranks_and_replays_parameters(monkeypatch):
    rows, x = rows_and_features(width=70)
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        result, arrays = study._fit_bank(x, rows, backend='hidden', site='pre_query_state',
            provenance={'test': 'synthetic'}, ranks=(1, 64))
    assert result['models'] == 4*3*2
    assert len(result['fits']) == result['models']
    assert result['parameter_replay_rows'] == result['models']*len(rows)
    assert len(result['metrics']) == 4*2*7*2
    assert len(result['comparisons']) == 6
    assert all(c['structural_groups'] in (3, 10) for c in result['metrics'])
    assert all(f['model']['heldout_rows_used_for_fit'] == 0 for f in result['fits'])
    assert all(f['model']['targets'] == 64 for f in result['fits'])
    for condition in study.CONDITIONS[1:]:
        assert arrays[f'align_{condition}_rotation'].shape == (64, 64)
    assert arrays['value_neutral_rank64_weights'].shape == (64, 64)
    assert set(arrays['pca_training_ids']) == {r['id'] for r in rows if r['split'] == 'train'}
    assert all(len(control['frequency_audit']) == 12 for control in result['shuffle_controls'].values())


def test_npz_write_is_immutable_and_pickle_free(tmp_path):
    path = tmp_path/'fit.npz'
    values = {'weights': np.eye(4), 'ids': np.array(['a', 'b'])}
    study._npz(path, **values)
    with np.load(path, allow_pickle=False) as saved:
        assert np.array_equal(saved['weights'], values['weights'])
        assert np.array_equal(saved['ids'], values['ids'])
    with pytest.raises(ValueError, match='already differs'):
        study._npz(path, weights=np.zeros((4, 4)))


def completed_fixture(tmp_path):
    value = config(tmp_path); source = {'source_sha256': 'd'*64}
    expected = study._expected_artifacts(value)
    for name, path in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if name != 'summary': path.write_text('{}' if path.suffix == '.json' else 'synthetic')
    summary = {'status': 'complete_exploratory', 'config_hash': study.digest(value),
        'analysis_source': source, 'banks': [{'backend': backend, 'site': site,
            'artifact': str(expected[backend+'_'+site])} for backend in ('hidden', 'surface') for site in study.SITES]}
    expected['summary'].write_text(json.dumps(summary))
    review = {**summary, 'artifacts': {name: {'path': str(path), 'sha256': study._sha(path)} for name, path in expected.items()},
        'wall_seconds': 1.}
    review_path = expected['summary'].parent/'review_v1.json'; review_path.write_text(json.dumps(review))
    return value, source, review, review_path


def test_completed_review_reuse_checks_entire_fixed_artifact_inventory(tmp_path):
    value, source, review, _ = completed_fixture(tmp_path)
    assert study._verify_completed(value, source) == review


@pytest.mark.parametrize('missing', ['hidden_pre_query_state', 'report', 'audit'])
def test_removed_artifact_entry_cannot_bypass_checksum_validation(tmp_path, monkeypatch, missing):
    value, source, review, path = completed_fixture(tmp_path)
    review['artifacts'].pop(missing); path.write_text(json.dumps(review))
    monkeypatch.setattr(study, '_sha', lambda *a, **k: pytest.fail('inventory must precede hash reads'))
    with pytest.raises(ValueError, match='inventory'):
        study._verify_completed(value, source)


def test_changed_completed_artifact_path_is_rejected_before_hash_loop(tmp_path, monkeypatch):
    value, source, review, path = completed_fixture(tmp_path)
    review['artifacts']['report']['path'] = str(tmp_path/'other.md'); path.write_text(json.dumps(review))
    monkeypatch.setattr(study, '_sha', lambda *a, **k: pytest.fail('paths must precede hash reads'))
    with pytest.raises(ValueError, match='path differs'):
        study._verify_completed(value, source)


def test_completed_summary_bank_paths_must_match_fixed_hashed_files(tmp_path):
    value, source, review, path = completed_fixture(tmp_path)
    review['banks'][0]['artifact'] = str(tmp_path/'other.npz')
    summary_path = study._expected_artifacts(value)['summary']
    summary = {k: v for k, v in review.items() if k not in ('artifacts', 'wall_seconds')}
    summary_path.write_text(json.dumps(summary))
    review['artifacts']['summary']['sha256'] = study._sha(summary_path); path.write_text(json.dumps(review))
    with pytest.raises(ValueError, match='bank paths'):
        study._verify_completed(value, source)


def test_threadpool_uses_actual_scheduler_allocation_with_local_default(monkeypatch):
    monkeypatch.delenv('SLURM_CPUS_PER_TASK', raising=False)
    assert study._thread_count() == 8
    for n in (1, 4, 16):
        monkeypatch.setenv('SLURM_CPUS_PER_TASK', str(n)); assert study._thread_count() == n
    for invalid in ('0', '-1', 'unknown'):
        monkeypatch.setenv('SLURM_CPUS_PER_TASK', invalid)
        with pytest.raises(ValueError, match='positive integer'):
            study._thread_count()
