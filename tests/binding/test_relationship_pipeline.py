import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from codecue.binding import relationship_capture as capture
from codecue.binding import relationship_pipeline as pipeline
from codecue.binding.datasets import digest

REAL_VERIFY_SOURCE = capture._verify_source


@pytest.fixture
def setup(tmp_path, monkeypatch):
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log, 'note_artifact', lambda *args, **kwargs: None)
    monkeypatch.setenv('SLURM_JOB_ID', 'unit')
    config_path = tmp_path/'capture.json'; plan = tmp_path/'plan.md'; plan.write_text('Prospective fixed recipe.\n')
    cap = dict(evaluation_role=capture.ROLE, dataset=str(tmp_path/'bank.jsonl'),
        dataset_sha256=capture.DATASET_SHA256, run_dir=str(tmp_path/'capture'))
    config_path.write_text(json.dumps(cap)); folder = Path(cap['run_dir']); folder.mkdir()
    for name in ('audit.json', 'registration.json', 'summary.json'):
        (folder/name).write_text(json.dumps(dict(status='passed', model_prefill_cases=1944)))
    (folder/'completion_manifest_v1.json').write_text('{}')
    receipt = {'metadata': {name: {'path': str(folder/name), 'sha256': capture._sha(folder/name)}
        for name in ('audit.json', 'registration.json', 'summary.json')}}
    source = dict(snapshot='/unit/frozen', snapshot_id='unit', source_sha256='a'*64,
                  frozen_manifest_sha256='b'*64)
    checked = dict(receipt=receipt, source=source, summary=dict(model_prefill_cases=1944))
    calls = []
    monkeypatch.setattr(capture, '_current_source', lambda config: source)
    monkeypatch.setattr(capture, '_verify_source', lambda config, source: None)
    monkeypatch.setattr(capture, 'completed_metadata', lambda config: (calls.append('capture') or checked))
    result = dict(status='complete_exploratory', factorizations=45, parameter_replay_rows=87480,
                  primary={'fixed': True})
    def fit(config):
        calls.append('run'); out=Path(config['run_dir']);out.mkdir()
        (out/'completion_manifest_v1.json').write_text('{}');(out/'audit.json').write_text('{}')
        return result
    readouts=SimpleNamespace(ROLE='discovery_relationship_readouts_v1',protocol=lambda: {'fixed_recipe': True},
        preflight=lambda config:(calls.append('preflight') or {'status':'passed'}),run=fit,
        audit=lambda config:(calls.append('audit') or {'status':'passed'}),
        completed_result=lambda config:(calls.append('completed') or result))
    monkeypatch.setattr(pipeline,'_readouts',lambda:readouts)
    config=dict(evaluation_role=pipeline.ROLE,capture_config=str(config_path),capture_config_sha256=capture._sha(config_path),
        readout_run_dir=str(tmp_path/'readouts'),readout_report=str(tmp_path/'readouts.md'),
        pipeline_run_dir=str(tmp_path/'pipeline'),expected_readout_protocol_sha256=digest(readouts.protocol()),
        declared_plan=str(plan),declared_plan_sha256=capture._sha(plan))
    return config,calls,readouts,checked


def test_pipeline_resolves_named_pins_then_prefights_fits_and_audits_same_process(setup):
    config,calls,_,_=setup
    result=pipeline.run(config)
    assert calls==['capture','preflight','run','audit']
    assert result['factorizations']==45 and result['parameter_replay_rows']==87480
    assert result['new_model_queries']==0 and result['nested_jobs_submitted']==0
    resolved=json.loads((Path(config['pipeline_run_dir'])/'resolved_config.json').read_text())
    assert resolved['evaluation_role']=='discovery_relationship_readouts_v1'
    assert resolved['fixed_recipe'] is True
    assert resolved['capture_audit_sha256']==capture._sha(resolved['capture_audit'])
    assert resolved['capture_registration_sha256']==capture._sha(resolved['capture_registration'])
    assert resolved['capture_summary_sha256']==capture._sha(resolved['capture_summary'])


def test_completed_audit_and_run_reuse_never_fit_again(setup):
    config,calls,readouts,_=setup
    result=pipeline.run(config);calls.clear()
    readouts.run=lambda config:pytest.fail('refitted completed pipeline')
    assert pipeline.audit(config)==result
    assert calls==['capture','completed','audit']
    calls.clear();assert pipeline.run(config)==result
    assert calls==['capture','completed','audit']


@pytest.mark.parametrize('change',['protocol','plan','capture_pin','role','extra'])
def test_recipe_or_identity_mismatch_fails_before_capture_and_fits(setup,change):
    config,calls,readouts,_=setup
    if change=='protocol':readouts.protocol=lambda:{'different':True}
    elif change=='plan':Path(config['declared_plan']).write_text('changed')
    elif change=='capture_pin':config['capture_config_sha256']='f'*64
    elif change=='role':config['evaluation_role']='final'
    else:config['alpha']=1
    with pytest.raises(ValueError):pipeline.run(config)
    assert calls==[] and not Path(config['pipeline_run_dir']).exists()


def test_scheduled_and_frozen_source_guards_precede_capture_access(setup,monkeypatch):
    config,calls,_,_=setup
    monkeypatch.delenv('SLURM_JOB_ID')
    with pytest.raises(ValueError,match='SLURM'):pipeline.run(config)
    assert calls==[]
    monkeypatch.setenv('SLURM_JOB_ID','unit')
    monkeypatch.setattr(capture,'_current_source',lambda config:(_ for _ in ()).throw(ValueError('unfrozen')))
    with pytest.raises(ValueError,match='unfrozen'):pipeline.run(config)
    assert calls==[]


def test_incomplete_or_misnamed_capture_cannot_resolve_or_fit(setup):
    config,calls,_,checked=setup
    checked['receipt']['metadata']['audit.json']['path']=str(Path(config['pipeline_run_dir'])/'wrong.json')
    with pytest.raises(ValueError,match='named completion'):pipeline.run(config)
    assert calls==['capture'] and not Path(config['pipeline_run_dir']).exists()


@pytest.mark.parametrize('field',['readout_run_dir','pipeline_run_dir'])
def test_output_directories_cannot_overlap_capture_sources(setup,field):
    config,calls,_,_=setup
    config[field]=json.loads(Path(config['capture_config']).read_text())['run_dir']
    with pytest.raises(ValueError,match='overlap'):pipeline.run(config)
    assert calls==[]


def test_audit_detects_changed_resolved_config_and_evidence_without_fits(setup):
    config,calls,_,_=setup
    pipeline.run(config);calls.clear()
    path=Path(config['pipeline_run_dir'])/'resolved_config.json'
    path.write_text(path.read_text()+'\n')
    with pytest.raises(ValueError,match='checksum'):pipeline.audit(config)
    assert calls==['capture']


def _original_snapshot(folder, config):
    """Real minimal frozen-source/config chain, verified by the production reader."""
    folder.mkdir()
    (folder/'src/codecue').mkdir(parents=True)
    (folder/'src/codecue/__init__.py').write_text('# original frozen package\n')
    (folder/'scripts').mkdir(); (folder/'scripts/env.sh').write_text('# fixed environment\n')
    config_path = folder/'configs/pipeline.json'; config_path.parent.mkdir()
    config_path.write_text(json.dumps(config))
    source_files = {str(path.relative_to(folder)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (folder/'src/codecue/__init__.py', folder/'scripts/env.sh')}
    source_hash = digest(source_files)
    manifest = dict(snapshot_id='original', code=dict(source_files=source_files, source_sha256=source_hash),
        config_files={'configs/pipeline.json': hashlib.sha256(config_path.read_bytes()).hexdigest()})
    path = folder/'frozen_manifest.json'; path.write_text(json.dumps(manifest))
    return dict(snapshot=str(folder), snapshot_id='original', source_sha256=source_hash,
                frozen_manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def test_workspace_audit_verifies_original_frozen_source_without_current_source(setup, tmp_path, monkeypatch):
    from codecue.binding import registry
    config, calls, _, checked = setup
    checked['source'].update(_original_snapshot(tmp_path/'original_source', config))
    pipeline.run(config); calls.clear()
    workspace = tmp_path/'plain_workspace'; workspace.mkdir()
    monkeypatch.setattr(registry, 'ROOT', workspace)
    monkeypatch.setattr(capture, '_verify_source', REAL_VERIFY_SOURCE)
    monkeypatch.setattr(capture, '_current_source', lambda config: pytest.fail('audit required current frozen reader'))
    assert pipeline.audit(config)['status'] == 'complete_exploratory'
    assert calls == ['capture', 'completed', 'audit']


@pytest.mark.parametrize('change', ['role', 'hash', 'template', 'source', 'missing_source'])
def test_workspace_audit_rejects_bad_original_identity_before_capture(setup, change, tmp_path, monkeypatch):
    config, calls, _, checked = setup
    checked['source'].update(_original_snapshot(tmp_path/'original_source', config))
    pipeline.run(config); calls.clear()
    path = Path(config['pipeline_run_dir'])/'resolution_review.json'
    saved = json.loads(path.read_text())
    if change == 'role': saved['evaluation_role'] = 'other'
    elif change == 'hash': saved['config_hash'] = 'f'*64
    elif change == 'template': saved['template']['readout_report'] = 'changed.md'
    elif change == 'source': saved['pipeline_source']['source_sha256'] = 'f'*64
    else: saved.pop('pipeline_source')
    path.write_text(json.dumps(saved))
    # A valid original snapshot is present; tampering cannot fall through to
    # capture/scientific payloads or silently use today's workspace instead.
    monkeypatch.setattr(capture, '_verify_source', REAL_VERIFY_SOURCE)
    with pytest.raises((ValueError, FileNotFoundError)): pipeline.audit(config)
    assert calls == []


def test_interrupted_resolved_config_publication_retries_before_any_fitting(setup, monkeypatch):
    config, calls, _, _ = setup
    folder = Path(config['pipeline_run_dir'])
    original_fsync = capture.os.fsync
    failures = []

    def interrupted(fd):
        if not failures:
            failures.append(True)
            raise OSError('interrupted resolved-config temporary write')
        return original_fsync(fd)

    monkeypatch.setattr(capture.os, 'fsync', interrupted)
    with pytest.raises(OSError, match='resolved-config'):
        pipeline.run(config)
    assert calls == ['capture']
    assert not (folder/'resolved_config.json').exists()
    assert not (folder/'resolution_review.json').exists()
    assert not Path(config['readout_run_dir']).exists()
    monkeypatch.setattr(capture.os, 'fsync', original_fsync)
    assert pipeline.run(config)['status'] == 'complete_exploratory'
    assert calls == ['capture', 'capture', 'preflight', 'run', 'audit']
    resolution = json.loads((folder/'resolution_review.json').read_text())
    assert capture._sha(folder/'resolved_config.json') == resolution['resolved_config']['sha256']
    assert pipeline.audit(config)['status'] == 'complete_exploratory'
