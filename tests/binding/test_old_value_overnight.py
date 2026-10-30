import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from codecue.binding import old_value_overnight as study

NOW=datetime(2026,10,29,11,0,tzinfo=timezone.utc)


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


def pin(path):return dict(path=str(path),bytes=path.stat().st_size,sha256=study._sha(path))


def fixture(root,*,gate='failed'):
    out=root/'suite';out.mkdir();source_folder=root/'frozen';source_file=source_folder/'src/checker.py'
    source_file.parent.mkdir(parents=True);source_file.write_text('pass\n')
    files={'src/checker.py':study._sha(source_file)};source=dict(snapshot=str(source_folder),snapshot_id='a'*24,code=study._digest(files))
    write(source_folder/'frozen_manifest.json',dict(snapshot_id=source['snapshot_id'],code=dict(source_sha256=source['code'],source_files=files),config_files={}))
    write(out/'execution_source_v1.json',source)
    artifacts=[]
    for index in range(161):
        path=root/'baseline'/(str(index)+('.npz' if index==160 else '.json'))
        path.parent.mkdir(exist_ok=True);path.write_bytes(b'not an array' if index==160 else b'{}\n');artifacts.append(pin(path))
    baseline=root/'baseline/handoff.json';write(baseline,dict(status='complete_audited',pins=artifacts))
    configs=[]
    source_for_receipt=dict(snapshot=str(source_folder),snapshot_id=source['snapshot_id'],source_sha256=source['code'])
    for model,name in study.MODELS.items():
        folder=out/name
        cfg=dict(evaluation_role=study.MODEL_ROLE,model=model,run_dir=str(folder),preflight_result=str(folder/'native.json'),review_artifact=str(folder/'review.json'),report=str(folder/'report.md'),dataset=str(root/'DO_NOT_READ_sources.jsonl'),prepared_cases=str(root/'DO_NOT_READ_prepared.jsonl'),declared_plan=str(root/'plan.md'))
        path=root/'configs'/(name+'.json');write(path,cfg);configs.append(dict(path=str(path),sha256=study._sha(path)))
        write(Path(cfg['preflight_result']),dict(status='passed',config_hash=study._digest(cfg),source_sha256=source['code'],cases=2,model_inference=False,generated_holdouts_opened=False))
        write(folder/'routing_preflight_v1.json',dict(status='passed',config_hash=study._digest(cfg),source=source_for_receipt))
        responses=folder/'checkpoint_suite/responses.jsonl';responses.parent.mkdir();responses.write_text(''.join(json.dumps(dict(section='old_value',task='variant',id=str(i),raw_response='uninspected'))+'\n' for i in range(2)))
        review=dict(status='complete_audited',complete=True,evaluation_role=study.MODEL_ROLE,config_hash=study._digest(cfg),new_fits=0,generated_holdouts_opened=False,model=model,source=source_for_receipt,n=2,reliability_gate=dict(status=gate,automatic_causal_launch=False,causal_design_review_required=True),artifacts=dict(responses=pin(responses)),gate_cells={'previous':{'n':1,'correct':0}},paired_contrasts={'pair':{'n':1}},equality_control_cells={'equal':{'n':0}},accounting={'scored_responses':2})
        write(Path(cfg['review_artifact']),review);Path(cfg['report']).write_text('Behavioral calibration only.\n')
        write(folder/'routing_completion_v1.json',dict(status='complete_audited',evaluation_role=study.MODEL_ROLE,config_hash=study._digest(cfg),source=source_for_receipt,new_fits=0,generated_holdouts_opened=False,scored_cases=2,artifacts=dict(review=pin(Path(cfg['review_artifact'])),report=pin(Path(cfg['report'])))))
    config=dict(evaluation_role=study.ROLE,suite_root=str(out),model_configs=configs,source_pointer=str(out/'execution_source_v1.json'),baseline_handoff=dict(path=str(baseline),sha256=study._sha(baseline)),morning_at='2026-10-29T08:00:00-05:00',report=str(root/'status.md'),morning_report=str(root/'morning.md'))
    jobs={name:str(100+i) for i,name in enumerate(study.WORK+study.AUX)};write(out/'jobs_v1.json',jobs)
    xml=out/'regression_v1.xml';xml.write_text('<testsuites><testsuite tests="2192" failures="0" errors="0" skipped="0"/></testsuites>')
    write(out/'software_validation_review_v1.json',dict(status='passed',source=source,counts=dict(tests=2192,failures=0,errors=0,skipped=0),junit_sha256=study._sha(xml)))
    log=dict(enabled=True,interval_minutes=10,last_success_utc=NOW.isoformat(),jobs=[dict(job_id='201'),dict(job_id='202')])
    write(root/'artifacts/binding/experiment_log/scheduler_state.json',log)
    observed={jid:dict(state='COMPLETED',exit_code='0:0',reason='None') for key,jid in jobs.items() if key not in study.AUX}
    observed.update({jobs['publication']:dict(state='RUNNING',reason='None'),jobs['morning']:dict(state='PENDING',reason='BeginTime'),'201':dict(state='PENDING',reason='BeginTime'),'202':dict(state='PENDING',reason='Dependency')})
    return config,jobs,observed


@pytest.fixture(autouse=True)
def prevent_real_log(monkeypatch):
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log,'safe_emit_event',lambda *a,**k:None)


def run_check(tmp_path,monkeypatch,config,observed,**kwargs):
    monkeypatch.setattr(study,'scheduler',lambda ids,runner=None:(observed,[]))
    return study.check(config,root=tmp_path,now=kwargs.pop('now',NOW),**kwargs)


def test_scheduler_normalizes_states_reasons_and_preserves_partial_success():
    def runner(argv,**kwargs):
        assert kwargs['timeout']==20
        return SimpleNamespace(returncode=0,stderr='',stdout='12|COMPLETED|0:0|None\n13|CANCELLED by 7|1:0|DependencyNeverSatisfied\n' if argv[0]=='sacct' else '14|PENDING|QOSMaxJobsPerUserLimit\n')
    result,errors=study.scheduler(['12','13','14'],runner)
    assert not errors and result['12']['exit_code']=='0:0' and result['13']['state']=='CANCELLED'
    assert result['14']['reason']=='QOSMaxJobsPerUserLimit'


def test_scheduler_timeout_is_a_warning_not_invented_job_failure():
    import subprocess
    def runner(argv,**kwargs):
        if argv[0]=='sacct':raise subprocess.TimeoutExpired(argv,20)
        return SimpleNamespace(returncode=0,stderr='',stdout='12|RUNNING|None\n')
    jobs,errors=study.scheduler(['12'],runner)
    assert jobs['12']['state']=='RUNNING' and len(errors)==1


def test_execution_complete_even_when_behavioral_gate_failed(tmp_path,monkeypatch):
    cfg,jobs,seen=fixture(tmp_path);result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['status']=='complete' and result['scientific_status']=='gate_failed'
    assert result['all_scientific_work_complete'] and result['stages']['publication']['status']=='running'
    assert result['stages']['morning']['status']=='waiting' and result['causal_qualification'] is False
    assert result['needs_attention'] is False
    assert result['models']['llama8b']['paired_contrasts'] and result['completion_check_v1']
    assert not result['morning_due'] and not (tmp_path/'suite/morning_review_v1.json').exists()


def test_passed_gate_still_does_not_qualify_causality(tmp_path,monkeypatch):
    cfg,_,seen=fixture(tmp_path,gate='passed');result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['scientific_status']=='calibration_passed' and result['causal_qualification'] is False


def test_completed_job_without_committed_output_fails(tmp_path,monkeypatch):
    cfg,jobs,seen=fixture(tmp_path);(tmp_path/'suite/llama8b/routing_completion_v1.json').unlink()
    result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['status']=='failed' and result['stages']['llama8b_behavior']['status']=='failed'
    assert 'matching output' in result['stages']['llama8b_behavior']['reason']


def test_failed_and_waiting_jobs_remain_distinct(tmp_path,monkeypatch):
    cfg,jobs,seen=fixture(tmp_path);seen[jobs['llama8b_behavior']]=dict(state='OUT_OF_MEMORY',exit_code='1:0',reason='OutOfMemory')
    seen[jobs['codellama34b_behavior']]=dict(state='PENDING',reason='QOSMaxJobsPerUserLimit')
    result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['status']=='failed' and result['stages']['codellama34b_behavior']['status']=='waiting'
    assert result['stages']['codellama34b_behavior']['reason']=='QOSMaxJobsPerUserLimit'


def test_unknown_scheduler_state_is_not_success_from_existing_outputs(tmp_path,monkeypatch):
    cfg,jobs,seen=fixture(tmp_path);seen.pop(jobs['llama8b_behavior'])
    result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['status']=='waiting' and result['stages']['llama8b_behavior']['status']=='unknown'


def test_committed_response_prefix_excludes_partial_tail_and_detects_duplicates(tmp_path):
    p=tmp_path/'responses.jsonl';line=json.dumps(dict(section='s',task='t',id='i'))+'\n'
    p.write_text(line+'{"section":')
    assert study.committed_responses(p)==dict(committed=1,trailing_partial=True,invalid_committed_line=None)
    p.write_text(line+line)
    assert study.committed_responses(p)['invalid_committed_line']==2


def test_partial_response_cannot_certify_completed_job(tmp_path,monkeypatch):
    cfg,_,seen=fixture(tmp_path);p=tmp_path/'suite/llama8b/checkpoint_suite/responses.jsonl'
    with p.open('a') as stream:stream.write('{')
    result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['status']=='failed' and 'coverage' in result['models']['llama8b']['error']


@pytest.mark.parametrize('age,fresh',[(1199,True),(1200,True),(1201,False)])
def test_freshness_boundary_is_independent_of_pending_guards(age,fresh):
    state=dict(enabled=True,interval_minutes=10,last_success_utc=(NOW-timedelta(seconds=age)).isoformat(),jobs=[dict(job_id='1'),dict(job_id='2')])
    result=study._logging(state,{'1':dict(state='PENDING'),'2':dict(state='PENDING')},NOW)
    assert result['guard_health'] is True and result['fresh_within_two_intervals'] is fresh


def test_check_never_reads_source_or_prepared_records(tmp_path,monkeypatch):
    cfg,_,seen=fixture(tmp_path);read=study._read
    def guarded(path,*args,**kwargs):
        assert 'DO_NOT_READ' not in str(path)
        return read(path,*args,**kwargs)
    monkeypatch.setattr(study,'_read',guarded)
    result=run_check(tmp_path,monkeypatch,cfg,seen,deep=True)
    assert result['baseline']['hashes_checked']==161 and not result['source_records_opened'] and not result['score_arrays_opened']


def test_deep_hash_detects_binary_corruption_without_decoding_arrays(tmp_path,monkeypatch):
    cfg,_,seen=fixture(tmp_path);p=tmp_path/'baseline/160.npz';p.write_bytes(b'bad an array')
    result=run_check(tmp_path,monkeypatch,cfg,seen,deep=True)
    assert result['status']=='failed' and any('baseline:' in e for e in result['issues'])


def test_qa_requires_matching_junit_not_just_positive_claim(tmp_path,monkeypatch):
    cfg,jobs,seen=fixture(tmp_path);(tmp_path/'suite/regression_v1.xml').write_text('<testsuites/>')
    result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['stages']['regression']['status']=='failed'


def test_morning_not_early_even_with_flag_and_snapshot_is_idempotent(tmp_path,monkeypatch):
    cfg,jobs,seen=fixture(tmp_path);seen[jobs['llama8b_behavior']]=dict(state='RUNNING')
    run_check(tmp_path,monkeypatch,cfg,seen,morning=True)
    path=tmp_path/'suite/morning_review_v1.json';assert not path.exists()
    target=datetime.fromisoformat(cfg['morning_at']);run_check(tmp_path,monkeypatch,cfg,seen,morning=True,now=target)
    before=path.read_bytes();report=(tmp_path/'morning.md').read_bytes()
    run_check(tmp_path,monkeypatch,cfg,seen,morning=True,now=target+timedelta(minutes=30))
    assert path.read_bytes()==before and (tmp_path/'morning.md').read_bytes()==report
    (tmp_path/'morning.md').unlink()
    run_check(tmp_path,monkeypatch,cfg,seen,morning=True,now=target+timedelta(minutes=40))
    assert (tmp_path/'morning.md').read_bytes()==report


def test_frozen_source_tampering_detected_in_deep_mode(tmp_path,monkeypatch):
    cfg,_,seen=fixture(tmp_path);(tmp_path/'frozen/src/checker.py').write_text('oops\n')
    result=run_check(tmp_path,monkeypatch,cfg,seen,deep=True)
    assert result['status']=='failed' and any('source:' in e for e in result['issues'])


def test_reports_cannot_replace_frozen_model_plan(tmp_path,monkeypatch):
    cfg,_,seen=fixture(tmp_path);cfg['report']=str(tmp_path/'plan.md')
    with pytest.raises(ValueError,match='replace model'):run_check(tmp_path,monkeypatch,cfg,seen)


@pytest.mark.parametrize('stage',study.AUX)
@pytest.mark.parametrize('gate',['failed','passed'])
@pytest.mark.parametrize('raw,exit_code',[('FAILED','1:0'),('TIMEOUT','0:0'),('COMPLETED','1:0')])
def test_auxiliary_stage_failure_needs_attention_without_reversing_scientific_completion(tmp_path,monkeypatch,stage,gate,raw,exit_code):
    cfg,jobs,seen=fixture(tmp_path,gate=gate)
    seen[jobs[stage]]=dict(state=raw,exit_code=exit_code,reason='auxiliary failed')
    result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['status']=='failed' and result['needs_attention'] is True
    assert result['stages'][stage]['status']=='failed'
    assert result['all_scientific_work_complete'] is True and result['completion_check_v1']
    assert result['scientific_status']==('gate_failed' if gate=='failed' else 'calibration_passed')
    assert result['causal_qualification'] is False


@pytest.mark.parametrize('stage',study.AUX)
def test_auxiliary_failure_is_visible_while_scientific_work_waits(tmp_path,monkeypatch,stage):
    cfg,jobs,seen=fixture(tmp_path)
    seen[jobs['llama8b_behavior']]=dict(state='PENDING',reason='QOSMaxJobsPerUserLimit')
    seen[jobs[stage]]=dict(state='OUT_OF_MEMORY',exit_code='1:0',reason='OutOfMemory')
    result=run_check(tmp_path,monkeypatch,cfg,seen)
    assert result['status']=='failed' and result['needs_attention'] is True
    assert result['all_scientific_work_complete'] is False and result['completion_check_v1'] is None
    assert result['stages']['llama8b_behavior']['status']=='waiting'
    assert result['scientific_status']=='gate_failed'
