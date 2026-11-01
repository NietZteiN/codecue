"""Automatic experiment-log guarantees, with fixture data only."""
import builtins
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from codecue.binding import experiment_log as log
from codecue.binding.datasets import digest, write_json


def run_fixture(root, name, *, status='complete', correct=2, role='development'):
    folder=root/'artifacts/binding'/name/'behavior'
    config=dict(model='fixture-model',model_revision='a'*40,tokenizer_revision='b'*40,
                dataset=str(root/'artifacts/binding/discovery.jsonl'),run_dir=str(folder.parent),
                evaluation_role=role,device='cpu')
    identity=dict(config=config,config_hash=digest(config),code=dict(git_revision='fixture-revision',source_sha256='source-proof'),
                  dataset_manifest=dict(sha256='dataset-proof',rows=10,evaluation_role=role),stage='behavior')
    manifest=dict(identity=identity,identity_hash=digest(identity),status=status,artifact_dir=str(folder),
                  started_utc='2026-01-01T00:00:00+00:00',host='fixture-host',slurm_job_id='101',
                  attempts=[dict(status=status,wall_seconds=2.)],wall_seconds_total=2.)
    if status=='failed':manifest['error']='RuntimeError: controlled fixture failure'
    else:manifest['finished_utc']='2026-01-01T00:00:02+00:00'
    write_json(folder/'manifest.json',manifest)
    if correct is not None:
        write_json(folder/'summary.json',dict(complete=status=='complete',evaluated=10,planned=10,correct=correct,
                   reliability_gate=dict(status='failed'),generated_holdouts_opened=False))
    return folder,manifest


def events(root):
    return [json.loads(p.read_text()) for p in sorted((root/'artifacts/binding/experiment_log/events').glob('*.json'))]


def values_for_key(value,key):
    result=[]
    if isinstance(value,dict):
        for name,item in value.items():
            if name==key:result.append(item)
            result.extend(values_for_key(item,key))
    elif isinstance(value,list):
        for item in value:result.extend(values_for_key(item,key))
    return result


def test_event_spool_is_durable_unique_and_keeps_exact_payload(tmp_path):
    payload=dict(message='A measured negative result',nested=dict(correct=2,n=10),tags=['audit','failure'])
    def emit(index):
        return log.emit_event('unit_observation',root=tmp_path,run_dir=str(tmp_path/'run'),stage='behavior',
                              job_id=str(index),payload=dict(payload,index=index))
    with ThreadPoolExecutor(max_workers=8) as pool:emitted=list(pool.map(emit,range(32)))
    assert len({e['event_id'] for e in emitted})==32
    for e in emitted:
        assert e['event_type']=='unit_observation' and e['schema_version']==1 and e['occurred_utc']
        assert {k:v for k,v in e['payload'].items() if k!='index'}==payload
    saved=events(tmp_path)
    assert {e['event_id'] for e in saved}=={e['event_id'] for e in emitted}
    assert {e['payload']['index'] for e in saved}==set(range(32))
    result=log.refresh(tmp_path)
    assert result['events']==32


def test_multiple_processes_can_emit_and_refresh_without_dropping_events(tmp_path):
    code='''import sys
from codecue.binding.experiment_log import emit_event,refresh
root,worker=sys.argv[1:]
for index in range(6):
 emit_event('unit_observation',root=root,payload={'worker':int(worker),'index':index})
refresh(root)
'''
    env=dict(os.environ)
    source=str(Path(__file__).resolve().parents[2]/'src')
    env['PYTHONPATH']=source+os.pathsep+env.get('PYTHONPATH','')
    workers=[subprocess.Popen([sys.executable,'-c',code,str(tmp_path),str(i)],env=env,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for i in range(4)]
    for worker in workers:
        stdout,stderr=worker.communicate(timeout=30)
        assert worker.returncode==0,(stdout,stderr)
    result=log.refresh(tmp_path)
    assert result['events']==24
    assert {(e['payload']['worker'],e['payload']['index']) for e in events(tmp_path)}=={
        (worker,index) for worker in range(4) for index in range(6)}


def test_lifecycle_lock_contention_defers_without_blocking_or_losing_event(tmp_path):
    code = '''import sys
from codecue.binding.experiment_log import emit_event,safe_sync_job
root=sys.argv[1]
event=emit_event('job_started',root=root,job_id='42',payload={'name':'fixture','job_id':'42'})
safe_sync_job(root=root,payload={'job_id':'42'},job_id='42')
print(event['event_id'])
'''
    env = dict(os.environ)
    env['PYTHONPATH'] = str(Path(__file__).resolve().parents[2] / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    # Hold the real interprocess lock until the lifecycle writer has returned.
    # A blocking hook deadlocks here and fails the bounded child-process check.
    with log._index(tmp_path):
        child = subprocess.run([sys.executable, '-c', code, str(tmp_path)], env=env,
            capture_output=True, text=True, timeout=5, check=True)
        event_id = child.stdout.strip()
        assert event_id in {e['event_id'] for e in events(tmp_path)}
        assert 'index deferred' in child.stderr and 'sync deferred' in child.stderr
    assert log.refresh(tmp_path)['events'] == 1
    record = log.list_records(tmp_path, kind='job')[0]
    assert record['job_id'] == '42' and record['status'] == 'running'


def test_backfill_preserves_completed_negative_science_and_is_idempotent(tmp_path):
    folder,manifest=run_fixture(tmp_path,'measured_negative')
    write_json(folder/'audit.json',dict(status='passed',identity_hash=manifest['identity_hash'],evaluated=10))
    before={str(p):p.read_bytes() for p in folder.iterdir() if p.is_file()}
    first=log.refresh(tmp_path);records=log.list_records(tmp_path,kind='run')
    assert len(records)==1
    record=records[0]
    assert record['status']=='complete'
    assert record['model']=='fixture-model' and record['config_hash']==manifest['identity']['config_hash']
    assert record['source_hash']=='source-proof'
    assert record['metrics']['summary']['correct']==2
    assert record['metrics']['summary']['reliability_gate']['status']=='failed'
    assert record['metrics']['audit']['status']=='passed'
    assert record['audit_status']=='passed' and record['scientific_status']=='failed'
    assert record['artifacts']
    second=log.refresh(tmp_path)
    assert first['records']==second['records']==1 and first['events']==second['events']
    assert {str(p):p.read_bytes() for p in folder.iterdir() if p.is_file()}==before
    with (tmp_path/'artifacts/binding/experiment_log/experiments.csv').open(newline='') as stream:
        exported=list(csv.DictReader(stream))
    assert len(exported)==1 and exported[0]['status']=='complete' and exported[0]['kind']=='run'
    report=(tmp_path/'reports/binding/experiment_log.md').read_text()
    assert 'fixture-model' in report and 'measured_negative' in report


def test_changed_results_update_current_record_but_preserve_old_snapshot(tmp_path):
    folder,_=run_fixture(tmp_path,'updated',correct=2)
    first=log.refresh(tmp_path);record_id=log.list_records(tmp_path,kind='run')[0]['id']
    write_json(folder/'summary.json',dict(complete=True,evaluated=10,planned=10,correct=3))
    second=log.refresh(tmp_path);current=log.list_records(tmp_path,kind='run')
    assert len(current)==1 and current[0]['id']==record_id
    assert current[0]['metrics']['summary']['correct']==3
    assert second['events']>first['events']
    historical_correct={value for event in events(tmp_path) for value in values_for_key(event['payload'],'correct')}
    assert {2,3}<=historical_correct
    assert log.refresh(tmp_path)['events']==second['events']


def test_result_index_keeps_aggregate_metrics_and_compacts_bulk_payloads(tmp_path):
    folder,_=run_fixture(tmp_path,'compact_metrics',correct=None)
    write_json(folder/'summary.json',dict(complete=True,n=100,correct=62,accuracy=.62,
               by_family=dict(dependency=dict(n=40,correct=30)),
               predictions=[dict(id=i,response='raw-prediction-sentinel'*100) for i in range(100)],
               coefficients=list(range(1000))))
    log.refresh(tmp_path)
    summary=log.list_records(tmp_path,kind='run')[0]['metrics']['summary']
    assert summary['n']==100 and summary['correct']==62 and summary['accuracy']==.62
    assert summary['by_family']['dependency']==dict(n=40,correct=30)
    encoded=json.dumps(summary)
    assert len(encoded)<2000 and 'raw-prediction-sentinel' not in encoded


def test_failed_and_corrupted_runs_remain_visible_without_erasing_good_results(tmp_path):
    good,_=run_fixture(tmp_path,'good',correct=7)
    failure,_=run_fixture(tmp_path,'failed',status='failed',correct=None)
    broken,_=run_fixture(tmp_path,'broken',correct=None)
    (broken/'summary.json').write_text('{"correct":')
    result=log.refresh(tmp_path);records=log.list_records(tmp_path,kind='run')
    assert len(records)==3 and result['status']=='needs_attention' and result['issues']
    failed=next(r for r in records if r['status']=='failed')
    assert 'controlled fixture failure' in json.dumps(failed)
    assert any((r['metrics'].get('summary') or {}).get('correct')==7 for r in records)
    malformed=next(r for r in records if r['path']!=failed['path'] and (r['metrics'].get('summary') or {}).get('correct')!=7)
    assert malformed['issues']
    assert 'correct' not in (malformed['metrics'].get('summary') or {})
    assert (broken/'summary.json').read_text()=='{"correct":'


def test_backfill_includes_probe_analyses_that_bypass_stage_registry(tmp_path):
    folder=tmp_path/'artifacts/binding/readouts/run'
    config=dict(run_dir=str(folder),readout_task='queried_value',alpha=100.,seeds=[11,29,47])
    write_json(folder/'registration.json',dict(config=config,capture_identity='capture-proof',
               analysis_source=dict(git_revision='fixture-revision',source_sha256='analysis-proof')))
    write_json(folder/'summary.json',dict(status='complete',model='probe-model',fit_count=75,correct=8,n=10))
    log.refresh(tmp_path);records=log.list_records(tmp_path,kind='analysis')
    assert len(records)==1
    assert records[0]['status']=='complete' and records[0]['model']=='probe-model'
    assert records[0]['metrics']['summary']['fit_count']==75
    assert records[0]['source_hash']=='analysis-proof'


@pytest.mark.parametrize('sealed_name,role,split_flag,dataset_role',[
    ('reserved_final','structural_extrapolation',True,None),
    ('future_eval','structural_extrapolation',True,None),
    ('unopened_scores','final',False,None),
    ('unseen_metrics','test',False,None),
    ('unreleased_metrics','development',False,'structural_extrapolation'),
])
def test_refresh_never_reads_sealed_outcomes_or_frozen_source_copies(tmp_path,monkeypatch,sealed_name,role,split_flag,dataset_role):
    safe,safe_manifest=run_fixture(tmp_path,'visible',correct=3)
    sealed,manifest=run_fixture(tmp_path,sealed_name,role=role,correct=None)
    if split_flag:manifest['identity']['config']['generation']=dict(split_override='test',evaluation_role='structural_extrapolation')
    if dataset_role:manifest['identity']['dataset_manifest']['evaluation_role']=dataset_role
    manifest['identity']['config_hash']=digest(manifest['identity']['config'])
    manifest['identity_hash']=digest(manifest['identity'])
    write_json(sealed/'manifest.json',manifest)
    safe_manifest['identity']['config']['review_artifact']=str(sealed/'review.json')
    safe_manifest['identity']['config_hash']=digest(safe_manifest['identity']['config'])
    safe_manifest['identity_hash']=digest(safe_manifest['identity'])
    write_json(safe/'manifest.json',safe_manifest)
    protected={sealed/'summary.json',sealed/'audit.json',sealed/'review.json',sealed/'responses.jsonl',sealed/'features.npz'}
    for path in protected:path.write_text('{"correct":987654321,"secret":"sealed_outcome"}\n')
    frozen=tmp_path/'artifacts/binding/sources/frozen_copy/run/manifest.json'
    write_json(frozen,dict(manifest,sentinel='frozen_source_copy'))
    protected.add(frozen);protected={p.resolve() for p in protected};attempted=[]
    path_open=Path.open;builtin_open=builtins.open
    def guard(path,mode):
        if isinstance(path,(str,os.PathLike)) and 'r' in mode and Path(path).resolve() in protected:
            attempted.append(str(path));raise AssertionError('logging attempted to read sealed/frozen content')
    def guarded_path_open(self,mode='r',*args,**kwargs):
        guard(self,mode);return path_open(self,mode,*args,**kwargs)
    def guarded_builtin_open(file,mode='r',*args,**kwargs):
        guard(file,mode);return builtin_open(file,mode,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guarded_path_open);monkeypatch.setattr(builtins,'open',guarded_builtin_open)
    log.refresh(tmp_path)
    assert not attempted
    records=log.list_records(tmp_path)
    assert any((r['metrics'].get('summary') or {}).get('correct')==3 for r in records)
    assert 'sealed_outcome' not in json.dumps(records) and '987654321' not in json.dumps(records)
    assert not any('frozen_copy' in r['path'] for r in records)


def test_safe_emit_reports_logging_failure_without_breaking_experiment(tmp_path,monkeypatch,capsys):
    def unavailable(*args,**kwargs):raise OSError('read-only logging destination')
    monkeypatch.setattr(log,'emit_event',unavailable)
    log.safe_emit_event('unit_failure',root=tmp_path,payload=dict(message='still running'))
    assert 'read-only logging destination' in capsys.readouterr().err


@pytest.mark.parametrize('writer',['json','immutable'])
def test_metadata_writer_hook_uses_absolute_actual_target_from_callers_cwd(tmp_path,monkeypatch,writer):
    target=Path('artifacts/binding/fixture/summary.json');noted=[]
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(log,'note_artifact',lambda path:noted.append(Path(path)))
    if writer=='json':write_json(target,dict(complete=True,correct=2))
    else:
        from codecue.binding.published_benchmarks import immutable
        immutable(target,b'{"complete":true,"correct":2}\n')
    assert target.exists()
    assert noted==[(tmp_path/target).resolve()]


def test_deleted_derived_index_rebuilds_records_and_history_without_duplicate_snapshots(tmp_path):
    run_fixture(tmp_path,'recoverable',correct=4)
    log.emit_event('unit_observation',root=tmp_path,payload=dict(note='durable before index rebuild'))
    first=log.refresh(tmp_path);before=log.list_records(tmp_path)
    (tmp_path/'artifacts/binding/experiment_log/index.sqlite3').unlink()
    recovered=log.refresh(tmp_path);after=log.list_records(tmp_path)
    assert recovered['records']==first['records'] and recovered['events']==first['events']
    assert {r['id'] for r in before}=={r['id'] for r in after}
    assert after[0]['metrics']['summary']['correct']==4


def test_late_submission_or_start_event_cannot_regress_finished_job(tmp_path):
    log.emit_event('job_finished',root=tmp_path,job_id='42',payload=dict(name='fast_failure',exit_code=7,
                   started_utc='2026-01-01T00:00:00+00:00',finished_utc='2026-01-01T00:00:02+00:00'))
    log.emit_event('job_submitted',root=tmp_path,job_id='42',payload=dict(name='fast_failure',argv=['python','experiment.py'],
                   submitted_utc='2025-12-31T23:59:59+00:00',partition='fixture'))
    submitted=log.list_records(tmp_path,kind='job')
    assert len(submitted)==1 and submitted[0]['status']=='failed' and submitted[0]['exit_code']==7
    log.emit_event('job_started',root=tmp_path,job_id='42',payload=dict(node='fixture-node',started_utc='2026-01-01T00:00:00+00:00'))
    started=log.list_records(tmp_path,kind='job')[0]
    assert started['status']=='failed' and started['exit_code']==7
    assert started['finished_utc']=='2026-01-01T00:00:02+00:00'
    assert started['node']=='fixture-node' and started['argv']==['python','experiment.py']
    log.refresh(tmp_path)
    assert log.list_records(tmp_path,kind='job')[0]['status']=='failed'


def test_scheduler_cancellation_wins_over_delayed_events_until_explicit_restart(tmp_path,monkeypatch):
    log.emit_event('job_submitted',root=tmp_path,job_id='77',payload=dict(name='never_started',restart_count=0))
    def scheduler(argv,**kwargs):
        assert argv[0]=='sacct' and '77' in argv
        return subprocess.CompletedProcess(argv,0,stdout='77|CANCELLED|0:15|0\n',stderr='')
    monkeypatch.setattr(log.subprocess,'run',scheduler)
    log.refresh(tmp_path,reconcile_scheduler=True)
    assert log.list_records(tmp_path,kind='job')[0]['status']=='cancelled'
    for event_type in ('job_submitted','job_started'):
        log.emit_event(event_type,root=tmp_path,job_id='77',payload=dict(restart_count=0,node='late-node'))
        assert log.list_records(tmp_path,kind='job')[0]['status']=='cancelled'
    log.refresh(tmp_path)
    assert log.list_records(tmp_path,kind='job')[0]['status']=='cancelled'
    log.emit_event('job_started',root=tmp_path,job_id='77',payload=dict(restart_count=1,node='restart-node'))
    restarted=log.list_records(tmp_path,kind='job')[0]
    assert restarted['status']=='running' and restarted['restart_count']==1


def test_failed_submission_backfill_stays_one_failed_record(tmp_path):
    submission=tmp_path/'log/slurm/submit_fixture_failed.json'
    metadata=dict(name='rejected',argv=['python','fixture.py'],submitted_utc='2026-01-01T00:00:00+00:00',
                  submission_manifest=str(submission),partition='fixture')
    write_json(submission,metadata)
    log.emit_event('job_submission_failed',root=tmp_path,payload=dict(metadata,error='controlled sbatch rejection',exit_code=1))
    first=log.list_records(tmp_path,kind='job')
    assert len(first)==1 and first[0]['status'] in ('failed','submission_failed')
    log.refresh(tmp_path)
    current=log.list_records(tmp_path,kind='job')
    assert len(current)==1 and current[0]['status'] in ('failed','submission_failed')
    assert current[0]['id']==first[0]['id'] and 'controlled sbatch rejection' in json.dumps(current[0])


def test_unassigned_submission_promotes_to_one_scheduler_job_and_keeps_history(tmp_path):
    submission=tmp_path/'log/slurm/submit_fixture_pending.json'
    metadata=dict(name='pending_identity',argv=['python','fixture.py'],submitted_utc='2026-01-01T00:00:00+00:00',
                  submission_manifest=str(submission),partition='fixture')
    write_json(submission,metadata)
    log.refresh(tmp_path)
    unknown=log.list_records(tmp_path,kind='job')
    assert len(unknown)==1 and unknown[0]['status']=='unknown' and not unknown[0].get('job_id')
    log.emit_event('job_submitted',root=tmp_path,payload=metadata)
    unassigned=log.list_records(tmp_path,kind='job')
    assert len(unassigned)==1 and unassigned[0]['status']=='submitted' and not unassigned[0].get('job_id')
    initial_ids={event['event_id'] for event in events(tmp_path)}
    log.emit_event('job_started',root=tmp_path,job_id='81',payload=dict(metadata,job_id='81',node='fixture-node'))
    log.refresh(tmp_path)
    assigned=log.list_records(tmp_path,kind='job')
    assert len(assigned)==1 and assigned[0]['job_id']=='81' and assigned[0]['status']=='running'
    assert initial_ids<={event['event_id'] for event in events(tmp_path)}


def test_repeated_job_backfill_keeps_runtime_manifest_and_unchanged_event_count(tmp_path):
    submission=tmp_path/'log/slurm/submit_fixture_running.json'
    runtime=tmp_path/'log/slurm/82_fixture_running.json'
    metadata=dict(name='running_fixture',argv=['python','fixture.py'],submitted_utc='2026-01-01T00:00:00+00:00',
                  submission_manifest=str(submission),job_id='82',status='submitted')
    write_json(submission,metadata)
    write_json(runtime,dict(metadata,started_utc='2026-01-01T00:00:01+00:00',node='fixture-node',
                           job_manifest=str(runtime),status='running'))
    first=log.refresh(tmp_path)
    initial=log.list_records(tmp_path,kind='job')
    assert len(initial)==1 and initial[0]['status']=='running'
    assert initial[0]['path']==str(runtime)
    assert initial[0]['artifacts']['job_manifest']['path']==str(runtime)
    assert initial[0]['artifacts']['submission_manifest']['path']==str(submission)
    second=log.refresh(tmp_path);third=log.refresh(tmp_path)
    assert first['events']==second['events']==third['events']
    assert log.list_records(tmp_path,kind='job')==initial


def test_scheduler_submit_line_links_legacy_unassigned_submission_to_cancelled_job(tmp_path,monkeypatch):
    submission=tmp_path/'log/slurm/submit_legacy.json'
    metadata=dict(name='legacy_job',argv=['python','legacy_fixture.py'],submitted_utc='2026-01-01T00:00:00+00:00')
    write_json(submission,metadata)
    write_json(tmp_path/'artifacts/binding/unit/jobs.json',dict(legacy_job='83'))
    def scheduler(argv,**kwargs):
        assert argv[0]=='sacct' and '83' in argv
        return subprocess.CompletedProcess(argv,0,stdout=f'83|CANCELLED|0:15|0|sbatch --parsable {submission.with_suffix(".sbatch")}\n',stderr='')
    monkeypatch.setattr(log.subprocess,'run',scheduler)
    log.refresh(tmp_path,reconcile_scheduler=True)
    records=log.list_records(tmp_path,kind='job')
    assert len(records)==1 and records[0]['job_id']=='83' and records[0]['status']=='cancelled'
    assert records[0]['argv']==metadata['argv'] and records[0]['name']=='legacy_job'
    assert records[0]['artifacts']['submission_manifest']['path']==str(submission)
    log.refresh(tmp_path)
    assert len(log.list_records(tmp_path,kind='job'))==1


def test_temporary_index_failure_preserves_result_snapshot_before_file_changes(tmp_path,monkeypatch,capsys):
    folder,_=run_fixture(tmp_path,'index_retry',correct=2)
    def unavailable(*args,**kwargs):raise log.sqlite3.OperationalError('temporarily unavailable')
    with monkeypatch.context() as patch:
        patch.setattr(log.sqlite3,'connect',unavailable)
        emitted=log.emit_event('stage_finished',root=tmp_path,run_dir=str(folder),stage='behavior',payload=dict(status='complete'))
    assert emitted['event_id'] in {e['event_id'] for e in events(tmp_path)}
    assert 'temporarily unavailable' in capsys.readouterr().err
    write_json(folder/'summary.json',dict(complete=True,evaluated=10,planned=10,correct=3))
    log.refresh(tmp_path)
    assert log.list_records(tmp_path,kind='run')[0]['metrics']['summary']['correct']==3
    history={value for event in events(tmp_path) for value in values_for_key(event,'correct')}
    assert {2,3}<=history


def test_registry_lifecycle_and_results_are_logged_without_manual_refresh(tmp_path,monkeypatch):
    from codecue.binding import registry
    original_root=log.workspace_root
    monkeypatch.setattr(log,'workspace_root',lambda root=None:tmp_path.resolve() if root is None else original_root(root))
    monkeypatch.setattr(registry,'ROOT',tmp_path)
    monkeypatch.setattr(registry,'code_identity',lambda:dict(git_revision='fixture',source_sha256='fixture-code',source_files={}))
    dataset=tmp_path/'artifacts/binding/unit/discovery.jsonl';dataset.parent.mkdir(parents=True)
    dataset.write_text('{"id":"fixture"}\n')
    import hashlib
    write_json(dataset.with_suffix('.manifest.json'),dict(sha256=hashlib.sha256(dataset.read_bytes()).hexdigest(),rows=1))
    config=dict(dataset=str(dataset),run_dir=str(tmp_path/'artifacts/binding/unit/run'),device='cpu',
                model='fixture-model',model_revision='a'*40,tokenizer_revision='b'*40)
    folder,manifest=registry.begin(config,'behavior',reuse_complete=True)
    assert log.list_records(tmp_path,kind='run')[0]['status']=='started'
    write_json(folder/'summary.json',dict(complete=True,n=3,correct=2,reliability_gate=dict(status='failed')))
    assert log.list_records(tmp_path,kind='run')[0]['metrics']['summary']['correct']==2
    registry.finish(folder,manifest,2.5)
    current=log.list_records(tmp_path,kind='run')
    assert len(current)==1 and current[0]['status']=='complete'
    assert current[0]['metrics']['summary']['reliability_gate']['status']=='failed'
    event_types=[event['event_type'] for event in events(tmp_path)]
    assert 'stage_started' in event_types and 'stage_finished' in event_types
    original_manifest=(folder/'manifest.json').read_bytes()
    _,reused=registry.begin(config,'behavior',reuse_complete=True)
    assert reused['status']=='complete' and (folder/'manifest.json').read_bytes()==original_manifest
    assert log.list_records(tmp_path,kind='run')[0]['status']=='complete'

    @registry.guarded
    def broken(cfg):
        registry.begin(cfg,'behavior')
        raise RuntimeError('deliberate experiment failure')
    failed_config=dict(config,run_dir=str(tmp_path/'artifacts/binding/unit/failed'))
    with pytest.raises(RuntimeError,match='deliberate experiment failure'):broken(failed_config)
    failed=next(r for r in log.list_records(tmp_path,kind='run') if r['status']=='failed')
    assert 'deliberate experiment failure' in json.dumps(failed)
