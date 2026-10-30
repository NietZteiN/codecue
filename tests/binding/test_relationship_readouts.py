"""Finite CPU checks for train-only fitting, coherent controls and rich receipts."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import relationship_readouts as study
from codecue.binding.datasets import digest


def fixture():
    rng = np.random.default_rng(71)
    x = rng.normal(size=(18, 9)); y = rng.normal(size=(18, 7))
    mask = np.ones(y.shape, dtype=bool); mask[:, -2:] = False; y[:, -2:] = 0
    train = np.arange(18) < 12
    donor = np.r_[np.roll(np.arange(12), 3), np.roll(np.arange(12, 18), 2)]
    weights = np.linspace(.4, 2., 12)
    ids = tuple(f'case-{index}' for index in range(18))
    return x, y, mask, train, weights, ids, donor


def config(tmp_path):
    cap = tmp_path/'capture'
    return dict(evaluation_role=study.ROLE, capture_config=str(tmp_path/'capture_config.json'),
        capture_config_sha256='a'*64, capture_audit=str(cap/'audit.json'), capture_audit_sha256='b'*64,
        capture_registration=str(cap/'registration.json'), capture_registration_sha256='c'*64,
        run_dir=str(tmp_path/'readouts'), report=str(tmp_path/'relationship_readouts.md'))


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(study._json_bytes(value)); return study._sha(path)


@pytest.mark.parametrize('phase', ['write', 'fsync', 'link'])
def test_atomic_publication_interrupted_staging_leaves_no_partial_destination(tmp_path, monkeypatch, phase):
    import tempfile
    from codecue.binding import experiment_log
    path = tmp_path/'results_v1.json'; payload = b'{"complete": "scientific result"}\n'
    factory, fsync, link = tempfile.NamedTemporaryFile, study.os.fsync, study.os.link
    logged = []; monkeypatch.setattr(experiment_log, 'note_artifact', lambda path: logged.append(path))
    class PartialWrite:
        def __init__(self, **kwargs): self.stream = factory(**kwargs)
        def __enter__(self): self.stream.__enter__(); return self
        def __exit__(self, *args): return self.stream.__exit__(*args)
        @property
        def name(self): return self.stream.name
        def write(self, data):
            self.stream.write(data[:5]); self.stream.flush()
            raise OSError('interrupted staging write')
    if phase == 'write': monkeypatch.setattr(tempfile, 'NamedTemporaryFile', PartialWrite)
    if phase == 'fsync': monkeypatch.setattr(study.os, 'fsync', lambda *args: (_ for _ in ()).throw(OSError('interrupted staging fsync')))
    if phase == 'link': monkeypatch.setattr(study.os, 'link', lambda *args: (_ for _ in ()).throw(OSError('interrupted staging link')))
    with pytest.raises(OSError, match='interrupted staging'): study.immutable(path, payload)
    assert not path.exists() and not list(tmp_path.glob('*.pending')) and logged == []
    monkeypatch.setattr(tempfile, 'NamedTemporaryFile', factory)
    monkeypatch.setattr(study.os, 'fsync', fsync); monkeypatch.setattr(study.os, 'link', link)
    study.immutable(path, payload)
    assert path.read_bytes() == payload and logged == [path.resolve()]
    study.immutable(path, payload)
    assert logged == [path.resolve()]
    with pytest.raises(ValueError, match='differs'): study.immutable(path, b'changed')
    assert path.read_bytes() == payload


@pytest.mark.parametrize('dangling', [False, True])
def test_atomic_publication_rejects_output_symlinks_without_touching_target(tmp_path, dangling):
    path = tmp_path/'review.md'; target = tmp_path/'external.txt'
    if not dangling: target.write_bytes(b'preserve')
    path.symlink_to(target)
    with pytest.raises(ValueError, match='symbolic links'): study.immutable(path, b'new result')
    assert path.is_symlink()
    if dangling: assert not target.exists()
    else: assert target.read_bytes() == b'preserve'


def test_complete_columns_share_factorization_without_coupling_or_dev_fit():
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    x, y, mask, train, weights, ids, donor = fixture()
    model, active, real, shuffled = study.fit_complete_columns(x, y, mask, train, weights, ids, donor)
    scaler = StandardScaler().fit(x[train]); z = scaler.transform(x)
    joined = np.c_[y[train][:, active], y[donor[train]][:, active]]
    expected = Ridge(alpha=100., solver='cholesky').fit(z[train], joined, sample_weight=weights).predict(z)
    np.testing.assert_allclose(real[:, active], expected[:, :len(active)], atol=2e-15, rtol=2e-14)
    np.testing.assert_allclose(shuffled[:, active], expected[:, len(active):], atol=2e-15, rtol=2e-14)
    assert np.isnan(real[:, -2:]).all() and np.isnan(shuffled[:, -2:]).all()
    assert model.metadata['factorizations'] == 1 and model.metadata['output_columns_independent']
    assert model.train_ids == ids[:12]
    changed = x.copy(); changed[~train] += 10_000
    second = study.fit_complete_columns(changed, y, mask, train, weights, ids, donor)[0]
    for name, value in model.parameters.items(): np.testing.assert_array_equal(value, second.parameters[name])


@pytest.mark.parametrize('problem', ['cross_split', 'duplicate_donor', 'duplicate_ids', 'partial_mask', 'nonfinite_x', 'nonfinite_y', 'zero_weight', 'dev_weights', 'no_train'])
def test_fitting_guards(problem):
    x, y, mask, train, weights, ids, donor = fixture()
    if problem == 'cross_split': donor[[0, -1]] = donor[[-1, 0]]
    if problem == 'duplicate_donor': donor[0] = donor[1]
    if problem == 'duplicate_ids': ids = (ids[1],)+ids[1:]
    if problem == 'partial_mask': mask[0, 0] = False
    if problem == 'nonfinite_x': x[-1, 0] = np.nan
    if problem == 'nonfinite_y': y[0, 0] = np.inf
    if problem == 'zero_weight': weights[0] = 0
    if problem == 'dev_weights': weights = np.ones(18)
    if problem == 'no_train': train[:] = False
    with pytest.raises(ValueError): study.fit_complete_columns(x, y, mask, train, weights, ids, donor)


def test_saved_parameters_resume_exactly_and_reject_changed_targets(tmp_path, monkeypatch):
    x, y, mask, train, weights, ids, donor = fixture()
    bundle = SimpleNamespace(y=y, mask=mask, case_ids=ids)
    path = tmp_path/'bank.npz'
    first = study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)
    monkeypatch.setattr(study, 'ridge_fit', lambda *args, **kwargs: pytest.fail('completed bank must not refit'))
    second = study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)
    for a, b in zip(first[1:], second[1:]): np.testing.assert_array_equal(a, b)
    y[0, 0] += 1
    with pytest.raises(ValueError, match='identity'): study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)


def test_resume_replays_every_row_and_detects_changed_features(tmp_path):
    x, y, mask, train, weights, ids, donor = fixture()
    bundle = SimpleNamespace(y=y, mask=mask, case_ids=ids); path = tmp_path/'bank.npz'
    study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)
    x[-1, 0] += 2
    with pytest.raises(ValueError, match='replay'): study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)


def test_resume_rejects_changed_ordered_training_membership(tmp_path):
    x, y, mask, train, weights, ids, donor = fixture()
    bundle = SimpleNamespace(y=y, mask=mask, case_ids=ids); path = tmp_path/'bank.npz'
    study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)
    with pytest.raises(ValueError, match='training input identity'):
        study._fit_bank(path, x, bundle, np.roll(train, 1), weights, donor, 'a'*64)


@pytest.mark.parametrize('field', ['features', 'targets', 'sample_weight'])
def test_resume_validates_saved_training_input_hash_pins(tmp_path, field):
    x, y, mask, train, weights, ids, donor = fixture()
    bundle = SimpleNamespace(y=y, mask=mask, case_ids=ids); path = tmp_path/'bank.npz'
    study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)
    with np.load(path, allow_pickle=False) as saved: arrays = {key: saved[key].copy() for key in saved.files}
    metadata = json.loads(arrays['model_metadata'].tobytes())
    metadata['training_input_sha256'][field] = 'e'*64
    arrays['model_metadata'] = np.frombuffer(study._json_bytes(metadata), dtype=np.uint8)
    np.savez(path, **arrays)
    with pytest.raises(ValueError, match='training input identity'):
        study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)


def test_resume_checks_current_training_features_before_saved_prediction_replay(tmp_path):
    x, y, mask, train, weights, ids, donor = fixture()
    bundle = SimpleNamespace(y=y, mask=mask, case_ids=ids); path = tmp_path/'bank.npz'
    study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)
    x[0, 0] += 1
    with pytest.raises(ValueError, match='training input identity'):
        study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)


def test_resume_validates_saved_donor_case_ids(tmp_path):
    x, y, mask, train, weights, ids, donor = fixture()
    bundle = SimpleNamespace(y=y, mask=mask, case_ids=ids); path = tmp_path/'bank.npz'
    study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)
    with np.load(path, allow_pickle=False) as saved: arrays = {key: saved[key].copy() for key in saved.files}
    arrays['donor_case_ids'][0] = 'other'
    np.savez(path, **arrays)
    with pytest.raises(ValueError, match='input identity'):
        study._fit_bank(path, x, bundle, train, weights, donor, 'a'*64)


@pytest.mark.parametrize('site', [3, 7, 8])
def test_real_target_api_coherent_control_truth_and_value_comparators(site):
    from codecue.binding import relationship_targets as target
    from codecue.binding.programs import rename
    rows = []
    for split in ('train', 'development'):
        for group in range(2):
            for program, values in enumerate([(2, 3, 5, 7), (2, 3, 3, 7)]):
                values = tuple(value+group+(2 if split == 'development' else 0) for value in values)
                for variant in range(3):
                    parents = (variant+1, 0, 1, 2) if group == 0 else (variant+1, 2, 3, 0)
                    source = '\n'.join([*(f'v{i} = {value}' for i, value in enumerate(values)),
                        *(f'v{i} = v{parent}' for i, parent in enumerate(parents)), 'v0'])
                    for lexical in range(2):
                        identity = f'{split}-{group}-{program}-{variant}-{lexical}'
                        mapping = {f'v{i}': f'item_{lexical}_{i}' for i in range(4)}
                        rows.append(dict(id=identity, split=split, template_id=f'{split}-{group}',
                            cluster_id=f'{split}-{group}', base_id=f'{split}-{group}-{program}',
                            lexical_realization=lexical, source=rename(source, mapping), canonical_source=source,
                            rename_map=mapping, variable_slots={f'v{i}': i for i in range(4)}))
    bundle = target.targets(rows, site); donor = target.coherent_shuffle(rows, 11)
    control = target.permute_bundle(bundle, donor)
    train = np.array([row['split'] == 'train' for row in rows]); weights = np.ones(train.sum())
    x = np.random.default_rng(19).normal(size=(len(rows), 5))
    _, active, real, shuffled = study.fit_complete_columns(x, bundle.y, bundle.mask, train,
        weights, bundle.case_ids, donor)
    np.testing.assert_array_equal(control.y, bundle.y[donor])
    if site == 3:
        same_prefix_targets = {}
        for index, row in enumerate(rows):
            prefix = tuple(row['canonical_source'].splitlines()[:4])
            signature = control.numeric_truth[index].tobytes()
            assert same_prefix_targets.setdefault(prefix, signature) == signature
    for subset in (train, ~train):
        np.testing.assert_array_equal(np.sort(control.y[subset][:, active], axis=0),
            np.sort(bundle.y[subset][:, active], axis=0))
    indices = target.fixed_primary_boolean_indices(bundle)
    measured = target.metrics(control, shuffled, eligible_boolean_indices=indices, include_per_group=False)
    assert measured['rows'] == len(rows) and measured['per_group_cells_included'] is False
    categorical = target.derived_categorical_relations(bundle, real)
    scalar = target.derived_relations(bundle, real)
    assert np.isfinite(categorical[:, indices]).all() and np.isfinite(scalar[:, indices]).all()
    correctness = target.task_correctness(bundle, categorical, indices)
    assert correctness['algebraic_correct'].shape == (len(rows), 18)
    assert np.isnan(correctness['whole_graph_correct']).all()  # Derived values do not supply parent heads.
    if site == 3: assert target.metrics(bundle, real, include_per_group=False)['parent_graph'] is None
    else: assert target.metrics(bundle, real, include_per_group=False)['parent_graph']['whole_graph_rows'] == len(rows)


def test_family_macro_and_fractional_seed_means():
    truth = np.array([[0]*5, [1]*5], dtype=bool)
    families = ('equal', 'less_than', 'less_than', 'sum_equals_third', 'difference_equals_third')
    correct = np.array([[1, 0, 0, 1, 1]]*2)
    assert study.family_macro_balanced_accuracy(correct, truth, families)['score'] == .75
    assert study.family_macro_balanced_accuracy(correct/3, truth, families)['score'] == .25
    assert study.family_macro_balanced_accuracy(correct[:1], truth[:1], families) is None


def test_shuffle_recipe_explicitly_preserves_initialization_prefix_base_blocks():
    assert study.protocol()['shuffle_recipe'] == ('component derangement; initialization-prefix base blocks; '
        'within-base copy-parent permutation; lexical ties')


def bootstrap_fixture():
    groups = np.repeat([f'g{i}' for i in range(9)], 2)
    truth = np.tile([[0]*4, [1]*4], (9, 1)).astype(bool)
    methods = dict(direct=np.ones(truth.shape), categorical_value_derived=np.full(truth.shape, .5))
    return groups, truth, methods


def test_algebraic_bootstrap_uses_fixed_groups_classes_and_seed_mean_correctness():
    groups, truth, methods = bootstrap_fixture()
    result = study.algebraic_bootstrap(truth, methods, groups, study.FAMILIES)
    contrast = result['comparisons']['direct_minus_categorical_value_derived']
    assert result['valid_draws'] == 2000 and result['invalid_draws'] == 0
    assert contrast['mean'] == .5 and contrast['conditional_group_bootstrap_95'] == [.5, .5]
    assert result['same_invalid_draws_for_all_methods'] and result['refits_per_draw'] == 0
    assert result == study.algebraic_bootstrap(truth, methods, groups, study.FAMILIES)


def test_missing_development_class_never_changes_eligible_cells():
    groups, truth, methods = bootstrap_fixture(); truth[:, 0] = False
    result = study.algebraic_bootstrap(truth, methods, groups, study.FAMILIES)
    assert result['status'] == 'unqualified_primary_missing_development_class'
    assert result['valid_draws'] == 0 and result['comparisons'] == {}


def test_invalid_bootstrap_draws_shared_and_no_retry_for_favorable_interval():
    groups, truth, methods = bootstrap_fixture(); truth[:, 0] = False; truth[0, 0] = True
    result = study.algebraic_bootstrap(truth, methods, groups, study.FAMILIES)
    assert result['status'] == 'unqualified_insufficient_valid_draws'
    assert 1000 < result['valid_draws'] < 1900
    assert result['valid_draws']+result['invalid_draws'] == 2000
    assert result['comparisons']['direct_minus_categorical_value_derived']['conditional_group_bootstrap_95'] is None


def test_structural_bootstrap_macro_weights_components_and_requires_nine():
    groups, _, _ = bootstrap_fixture()
    result = study.structural_bootstrap(dict(direct=np.ones(18), surface=np.zeros(18)), groups)
    assert result['comparisons']['direct_minus_surface']['conditional_group_bootstrap_95'] == [1, 1]
    with pytest.raises(ValueError): study.structural_bootstrap(dict(direct=np.ones(16)), groups[:16])


@pytest.mark.parametrize('change', [dict(fit_sites=[3, 7]), dict(alpha=1), dict(seeds=[1, 2, 3]),
    dict(evaluation_role='final_test'), dict(unknown=True), dict(capture_config_sha256='no'),
    dict(capture_summary='summary.json'), dict(run_dir='/tmp/final_test/out'),
    dict(shuffle_recipe='independent canonical-program permutation')])
def test_role_protocol_path_and_pin_guards_precede_metadata(tmp_path, monkeypatch, change):
    cfg = config(tmp_path); cfg.update(change)
    monkeypatch.setattr(study, '_json', lambda *args, **kwargs: pytest.fail('no metadata before role/path/protocol guards'))
    with pytest.raises(ValueError): study._capture_metadata(cfg)


def test_bad_capture_pin_fails_before_capture_reader_targets_or_arrays(tmp_path, monkeypatch):
    from codecue.binding import relationship_capture as capture
    cfg = config(tmp_path); save(cfg['capture_config'], {'not': 'matching_pin'})
    monkeypatch.setattr(capture, 'completed_metadata', lambda *args: pytest.fail('bad pin before reader'))
    monkeypatch.setattr(study, '_targets', lambda *args: pytest.fail('bad pin before labels'))
    monkeypatch.setattr(np, 'load', lambda *args, **kwargs: pytest.fail('no arrays'))
    with pytest.raises(ValueError, match='checksum'): study.preflight(cfg)


@pytest.mark.parametrize('filename', ['results_v1.json', 'registration.json', 'audit.json', 'progress.json',
    study.COMPLETION_NAME, 'hidden_layer8_site3_seed11.npz'])
def test_report_cannot_alias_reserved_generated_artifacts_before_payload(tmp_path, monkeypatch, filename):
    cfg = config(tmp_path); cfg['report'] = str(Path(cfg['run_dir'])/filename)
    monkeypatch.setattr(study, '_json', lambda *args, **kwargs: pytest.fail('path collision before payload'))
    with pytest.raises(ValueError, match='report cannot alias'): study.preflight(cfg)


@pytest.mark.parametrize('source', ['capture_config', 'capture_audit', 'capture_registration', 'capture_chunk'])
def test_report_cannot_replace_capture_source_paths(tmp_path, source):
    cfg = config(tmp_path)
    cfg['report'] = (str(tmp_path/'capture'/'chunks'/'chunk.npz') if source == 'capture_chunk' else cfg[source])
    with pytest.raises(ValueError, match='report cannot alias'): study._config(cfg)


def test_legitimate_markdown_report_inside_run_directory_allowed(tmp_path):
    cfg = config(tmp_path); cfg['report'] = str(Path(cfg['run_dir'])/'review.md')
    assert study._config(cfg) == study.protocol()


def test_output_directory_cannot_contain_declared_source_metadata(tmp_path):
    cfg = config(tmp_path); cfg['capture_config'] = str(Path(cfg['run_dir'])/'capture_config.json')
    with pytest.raises(ValueError, match='cannot contain source metadata'): study._config(cfg)


def test_dataset_report_alias_blocked_before_capture_payload_reader(tmp_path, monkeypatch):
    from codecue.binding import relationship_capture as capture
    cfg = config(tmp_path); dataset = tmp_path/'source.jsonl'
    cfg['report'] = str(dataset)
    cfg['capture_config_sha256'] = save(cfg['capture_config'], dict(run_dir=str(tmp_path/'capture'), dataset=str(dataset)))
    monkeypatch.setattr(capture, '_config', lambda config: None)
    monkeypatch.setattr(capture, 'completed_metadata', lambda *args: pytest.fail('source alias before reader'))
    with pytest.raises(ValueError, match='cannot replace source'): study.preflight(cfg)


def test_wrong_capture_role_fails_before_payload_reader(tmp_path, monkeypatch):
    from codecue.binding import relationship_capture as capture
    cfg = config(tmp_path); cfg['capture_config_sha256'] = save(cfg['capture_config'], {'evaluation_role': 'final_test'})
    monkeypatch.setattr(capture, 'completed_metadata', lambda *args: pytest.fail('role before reader'))
    with pytest.raises(ValueError): study.preflight(cfg)


def test_real_fitting_requires_scheduler_and_frozen_source(monkeypatch, tmp_path):
    from codecue.binding import registry
    monkeypatch.delenv('SLURM_JOB_ID', raising=False); monkeypatch.setattr(registry, 'ROOT', tmp_path)
    with pytest.raises(RuntimeError): study._scheduled_frozen()
    monkeypatch.setenv('SLURM_JOB_ID', 'synthetic')
    with pytest.raises(RuntimeError): study._scheduled_frozen()
    (tmp_path/'frozen_manifest.json').write_text('{}')
    assert study._scheduled_frozen() == tmp_path


def completed_fixture(tmp_path, monkeypatch, rich_padding=0):
    from codecue.binding import snapshots
    cfg = config(tmp_path); out = Path(cfg['run_dir']); out.mkdir()
    source = {'source_sha256': 'd'*64, 'git_revision': 'synthetic'}
    snapshot = tmp_path/'snapshot'; snapshot.mkdir()
    manifest_sha = save(snapshot/'frozen_manifest.json', {'synthetic': True})
    fit_source = dict(snapshot=str(snapshot), source_sha256=source['source_sha256'], frozen_manifest_sha256=manifest_sha)
    checked = dict(source={'source_sha256': 'e'*64}, chunks=[])
    monkeypatch.setattr(study, '_capture_metadata', lambda config: (checked, []))
    monkeypatch.setattr(snapshots, 'verify', lambda path: {'code': source})
    expected = study._expected_artifacts(cfg)
    result = dict(status='complete_exploratory', evaluation_role=study.ROLE, config_hash=digest(cfg),
        analysis_source=source, fit_source=fit_source, factorizations=45, parameter_replay_rows=45*1944,
        primary={'synthetic': True}, new_model_queries=0, generated_holdouts_opened=False,
        fits=[{'name': name, 'artifact': str(path)} for name, path in expected.items() if path.suffix == '.npz'],
        harmless_padding='x'*rich_padding)
    registration = dict(evaluation_role=study.ROLE, config=cfg, config_hash=digest(cfg), analysis_source=source,
        fit_source=fit_source, fixed_recipe=study.protocol())
    audit = dict(status='passed', evaluation_role=study.ROLE, config_hash=digest(cfg), factorizations=45,
        parameter_replay_rows=45*1944, exact_parameter_score_replays=True)
    for name, path in expected.items():
        if name == 'registration': save(path, registration)
        elif name == 'results': save(path, result)
        elif name == 'audit': save(path, audit)
        else: path.write_bytes(b'no array loading required')
    receipt = dict(schema_version=1, status='complete_exploratory', evaluation_role=study.ROLE,
        config_hash=digest(cfg), capture_source=checked['source'], fit_source=fit_source, factorizations=45,
        parameter_replay_rows=45*1944, new_model_queries=0, generated_holdouts_opened=False,
        mechanism_C_fitted=False, primary=result['primary'], artifacts={key: study._artifact(path) for key, path in expected.items()})
    save(out/study.COMPLETION_NAME, receipt)
    return cfg, result, receipt, expected


def test_compact_receipt_and_separately_bounded_rich_result_no_array_load(tmp_path, monkeypatch):
    cfg, result, _, _ = completed_fixture(tmp_path, monkeypatch, rich_padding=8*1024**2)
    monkeypatch.setattr(np, 'load', lambda *args, **kwargs: pytest.fail('verified reader must not load arrays'))
    assert study.completed_result(cfg) == result
    assert study.audit(cfg)['exact_parameter_replays_verified_during_fit']


@pytest.mark.parametrize('problem', ['role', 'config', 'inventory', 'artifact_path', 'artifact_hash', 'rich_hash', 'rich_cap'])
def test_completion_identity_inventory_and_hash_guards(tmp_path, monkeypatch, problem):
    cfg, _, receipt, expected = completed_fixture(tmp_path, monkeypatch)
    if problem == 'role': receipt['evaluation_role'] = 'final_test'
    if problem == 'config': receipt['config_hash'] = 'f'*64
    if problem == 'inventory': receipt['artifacts'].pop(next(iter(receipt['artifacts'])))
    if problem == 'artifact_path': receipt['artifacts']['results']['path'] = str(tmp_path/'unrelated.json')
    if problem == 'artifact_hash': receipt['artifacts']['audit']['sha256'] = 'f'*64
    if problem == 'rich_hash': expected['results'].write_bytes(expected['results'].read_bytes()+b' ')
    if problem == 'rich_cap': monkeypatch.setattr(study, 'MAX_RESULT_BYTES', 10)
    save(Path(cfg['run_dir'])/study.COMPLETION_NAME, receipt)
    monkeypatch.setattr(np, 'load', lambda *args, **kwargs: pytest.fail('no arrays'))
    with pytest.raises(ValueError): study.completed_result(cfg)


def test_completion_role_guard_precedes_source_or_rich_access(tmp_path, monkeypatch):
    cfg, _, receipt, _ = completed_fixture(tmp_path, monkeypatch)
    receipt['evaluation_role'] = 'final_test'; save(Path(cfg['run_dir'])/study.COMPLETION_NAME, receipt)
    monkeypatch.setattr(study, '_sha', lambda *args: pytest.fail('role before artifact hashing'))
    with pytest.raises(ValueError, match='receipt'): study.completed_result(cfg)


def finalization_fixture(tmp_path):
    cfg = config(tmp_path); out = Path(cfg['run_dir']); out.mkdir()
    save(out/'registration.json', {'synthetic': True})
    result = dict(status='complete_exploratory', evaluation_role=study.ROLE, config_hash=digest(cfg),
        cases=1944, training_rows=1296, development_rows=648, factorizations=45,
        parameter_replay_rows=45*1944, capture_source={'source_sha256': 'a'*64}, fit_source={'snapshot': 'synthetic'},
        source_model_prefill_cases=1944, runtime=dict(threads=2, slurm_job_id='first', wall_seconds=12.),
        primary=dict(algebraic=dict(status='qualified_conditional_interval', methods={}, comparisons={}),
            structural=dict(methods={}, comparisons={})), scientific_payload={'unchanged': [1, 2, 3]})
    return cfg, result


@pytest.mark.parametrize('crash_after', ['results_v1.json', 'report', 'audit.json'])
def test_finalization_recovers_partial_commits_preserving_original_runtime(tmp_path, monkeypatch, crash_after):
    cfg, result = finalization_fixture(tmp_path); original_immutable = study.immutable
    crash_path = Path(cfg['report']) if crash_after == 'report' else Path(cfg['run_dir'])/crash_after
    def crash(path, data):
        value = original_immutable(path, data)
        if Path(path) == crash_path: raise RuntimeError('injected after immutable commit')
        return value
    monkeypatch.setattr(study, 'immutable', crash)
    monkeypatch.setattr(study, 'ridge_fit', lambda *args, **kwargs: pytest.fail('finalization never refits'))
    with pytest.raises(RuntimeError, match='injected'): study._finish(cfg, result, {})
    rich_path = Path(cfg['run_dir'])/'results_v1.json'; original_bytes = rich_path.read_bytes()
    assert not (Path(cfg['run_dir'])/study.COMPLETION_NAME).exists()
    resumed = deepcopy(result); resumed['runtime'] = dict(threads=4, slurm_job_id='second', wall_seconds=3.)
    monkeypatch.setattr(study, 'immutable', original_immutable)
    completed = study._finish(cfg, resumed, {})
    assert completed == result and rich_path.read_bytes() == original_bytes
    receipt = json.loads((Path(cfg['run_dir'])/study.COMPLETION_NAME).read_text())
    assert receipt['completion_runtime'] == resumed['runtime']
    assert completed['runtime']['slurm_job_id'] == 'first'
    assert 'later cached-bank replays' in json.loads((Path(cfg['run_dir'])/'audit.json').read_text())['result_runtime_scope']
    assert Path(cfg['report']).read_text() == study._report(result)


def test_recovery_rejects_any_changed_scientific_payload(tmp_path):
    cfg, result = finalization_fixture(tmp_path)
    save(Path(cfg['run_dir'])/'results_v1.json', result)
    changed = deepcopy(result); changed['scientific_payload']['unchanged'][0] += 1
    changed['runtime'] = dict(threads=2, slurm_job_id='second', wall_seconds=3.)
    with pytest.raises(ValueError, match='scientific result differs'): study._finish(cfg, changed, {})
    assert not Path(cfg['report']).exists()


def test_recovery_rejects_invalid_original_runtime_and_bounded_old_result(tmp_path, monkeypatch):
    cfg, result = finalization_fixture(tmp_path); bad = deepcopy(result)
    bad['runtime']['slurm_job_id'] = None
    path = Path(cfg['run_dir'])/'results_v1.json'; save(path, bad)
    with pytest.raises(ValueError, match='runtime provenance'): study._finish(cfg, result, {})
    bad = deepcopy(result); bad['padding'] = 'x'*20_000; save(path, bad)
    monkeypatch.setattr(study, 'MAX_RESULT_BYTES', 10_000)
    with pytest.raises(ValueError, match='bounded existing'): study._finish(cfg, result, {})
