import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from codecue.binding import overnight_relationship_suite as suite
from codecue.binding.datasets import digest


def setup(tmp_path):
    plan=tmp_path/'plan.md';plan.write_text('Frozen discovery suite.\n')
    cfg=tmp_path/'capture.json';cfg.write_text('{"source": "fixture"}')
    nodes=[]
    for key,phase,deps in [('prepare','gpu',[]),('capture','gpu',['prepare']),('behavior','gpu',['capture']),('audit','cpu',['capture']),('readouts','cpu',['audit'])]:
        marker=tmp_path/key/'done.json';marker.parent.mkdir()
        nodes.append(dict(key=key,phase=phase,dependencies=deps,script='scripts/149_binding_overnight_relationship_capture.py',
            command='run',config=str(cfg),config_sha256=hashlib.sha256(cfg.read_bytes()).hexdigest(),partition='normal',
            mem='4G',cpus=1,time='02:00:00',time_min=None,marker=str(marker),marker_status='passed',expected_cases=10))
    config=dict(evaluation_role=suite.ROLE,nodes=nodes,run_dir=str(tmp_path/'suite'),report=str(tmp_path/'status.md'),
        morning_at='2030-10-28T08:00:00-05:00',declared_plan=str(plan),declared_plan_sha256=hashlib.sha256(plan.read_bytes()).hexdigest(),
        software_validation=dict(junit=str(tmp_path/'tests.xml'),review=str(tmp_path/'validation_review.json'),minimum_tests=1))
    state=dict(config_hash=digest(config),source={'snapshot':'fixture'},attempts={n['key']:[] for n in nodes},status={},controllers=[])
    return config,state


def done(node):
    Path(node['marker']).write_text(json.dumps({'status':'passed','config_hash':digest(json.loads(Path(node['config']).read_text()))}))


def test_cpu_work_waits_for_gpu_phase_then_obeys_its_required_parent(tmp_path):
    c,s=setup(tmp_path)
    for index,n in enumerate(c['nodes'][:3]):s['attempts'][n['key']]=[{'job_id':str(index+1),'progress_before':0}]
    for n in c['nodes'][:2]:done(n)
    observed={'1':{'state':'COMPLETED','exit_code':'0:0'},'2':{'state':'COMPLETED','exit_code':'0:0'},'3':{'state':'RUNNING'}}
    assert suite.reconcile(c,s,observed)==[]
    done(c['nodes'][2]);observed['3']={'state':'COMPLETED','exit_code':'0:0'}
    assert suite.reconcile(c,s,observed)==['audit']
    assert s['status']['readouts']['state']=='planned'


def test_failed_gpu_branch_does_not_block_other_successful_cpu_work(tmp_path):
    c,s=setup(tmp_path)
    for i,n in enumerate(c['nodes'][:3]):s['attempts'][n['key']]=[{'job_id':str(i+1),'progress_before':0}]
    done(c['nodes'][0]);done(c['nodes'][1])
    actions=suite.reconcile(c,s,{'1':{'state':'COMPLETED','exit_code':'0:0'},'2':{'state':'COMPLETED','exit_code':'0:0'},'3':{'state':'FAILED','exit_code':'1:0'}})
    assert actions==['audit'] and s['status']['behavior']['state']=='failed'


def test_only_transient_scheduler_failures_retry_and_no_progress_stops_loop(tmp_path):
    c,s=setup(tmp_path);n=c['nodes'][0]
    s['attempts']['prepare']=[{'job_id':'1','progress_before':0}]
    assert suite.reconcile(c,s,{'1':{'state':'TIMEOUT'}})==['prepare']
    s['attempts']['prepare'].append({'job_id':'2','progress_before':0})
    assert suite.reconcile(c,s,{'1':{'state':'TIMEOUT'},'2':{'state':'TIMEOUT'}})==[]
    assert s['status']['prepare']['state']=='failed'
    assert s['status']['capture']['state']=='blocked'


@pytest.mark.parametrize('state',['FAILED','OUT_OF_MEMORY','CANCELLED'])
def test_no_resurrection_of_scientific_failures_or_user_cancellation(tmp_path,state):
    c,s=setup(tmp_path);s['attempts']['prepare']=[{'job_id':'1','progress_before':0}]
    assert suite.reconcile(c,s,{'1':{'state':state,'reason':'None'}})==[]
    assert s['status']['prepare']['state']=='failed'


def test_dependency_cancellation_waits_for_replacement_parent(tmp_path):
    c,s=setup(tmp_path)
    s['attempts']['prepare']=[{'job_id':'1','progress_before':0}];s['attempts']['capture']=[{'job_id':'2','progress_before':0}]
    actions=suite.reconcile(c,s,{'1':{'state':'TIMEOUT'},'2':{'state':'CANCELLED','reason':'DependencyNeverSatisfied'}})
    assert actions==['prepare']
    done(c['nodes'][0]);s['attempts']['prepare'].append({'job_id':'3','progress_before':0})
    assert suite.reconcile(c,s,{'3':{'state':'COMPLETED','exit_code':'0:0'},'2':{'state':'CANCELLED','reason':'DependencyNeverSatisfied'}})==['capture']


def test_scheduler_preserves_other_observations_on_timeout():
    import subprocess
    def runner(argv,**kwargs):
        assert kwargs['timeout']==20
        if argv[0]=='sacct':raise subprocess.TimeoutExpired(argv,20)
        return SimpleNamespace(returncode=0,stdout='4|RUNNING|None\n',stderr='')
    jobs,errors=suite.scheduler(['4'],runner)
    assert jobs['4']['state']=='RUNNING' and len(errors)==1


def test_status_does_not_overwrite_controller_job_state(tmp_path,monkeypatch):
    c,s=setup(tmp_path);folder=Path(c['run_dir']);folder.mkdir()
    p=folder/'jobs_live_v1.json';p.write_text(json.dumps(s));before=p.read_bytes()
    monkeypatch.setattr(suite,'scheduler',lambda ids:({},[]))
    assert suite.status(c)['status']=='running'
    assert p.read_bytes()==before


def test_already_terminal_successor_does_not_create_infinite_controller_chain(tmp_path,monkeypatch):
    c,s=setup(tmp_path);folder=Path(c['run_dir']);folder.mkdir()
    s['source']={'frozen':True};(folder/'jobs_live_v1.json').write_text(json.dumps(s))
    monkeypatch.setattr(suite.base,'_slurm',lambda:None)
    monkeypatch.setattr(suite.base,'_current_source',lambda cfg:{'frozen':True})
    monkeypatch.setattr(suite,'status',lambda cfg:{'all_terminal':True,'status':'complete_exploratory','stages':{},'attempts':s['attempts']})
    monkeypatch.setattr(suite,'_submit_controller',lambda *a,**k:pytest.fail('unneeded successor submitted'))
    assert suite.watch(c)['status']=='complete_exploratory'


def test_terminal_supervisor_persists_completed_attempt_histories(tmp_path,monkeypatch):
    c,s=setup(tmp_path);folder=Path(c['run_dir']);folder.mkdir()
    s['source']={'frozen':True}
    for i,node in enumerate(c['nodes']):
        done(node)
        s['attempts'][node['key']]=[{'job_id':str(i+1),'state':'RUNNING','progress_before':0}]
    (folder/'jobs_live_v1.json').write_text(json.dumps(s))
    monkeypatch.setattr(suite.base,'_slurm',lambda:None)
    monkeypatch.setattr(suite.base,'_current_source',lambda cfg:{'frozen':True})
    monkeypatch.setattr(suite,'scheduler',lambda ids:({job:{'state':'COMPLETED','exit_code':'0:0'} for job in ids},[]))
    monkeypatch.setattr(suite,'_collect_outputs',lambda *args:{})
    monkeypatch.setattr(suite,'_submit_controller',lambda *a,**k:pytest.fail('terminal supervisor created a successor'))
    assert suite.watch(c)['status']=='complete_exploratory'
    saved=json.loads((folder/'jobs_live_v1.json').read_text())
    assert all(attempts[-1]['state']=='COMPLETED' and attempts[-1]['exit_code']=='0:0'
        for attempts in saved['attempts'].values())


def test_gpu_dependency_on_deferred_cpu_phase_is_rejected(tmp_path):
    c,s=setup(tmp_path);c['nodes'][-1]['phase']='gpu'
    with pytest.raises(ValueError,match='deferred CPU'):suite._config(c)


def test_recover_accepted_submission_before_resubmitting(tmp_path,monkeypatch):
    c,s=setup(tmp_path);node=c['nodes'][0];node['command']='prepare';s['source']={'snapshot':'fixture'}
    logs=tmp_path/'logs';logs.mkdir()
    argv=['/work/jvl210002/migration/envs/probe-cu129/bin/python',str(tmp_path/'scripts/91_binding_frozen_run.py'),'fixture',node['script'],'prepare',node['config']]
    intent=dict(name='rel-night-prepare-unique',argv=argv,log_dir=str(logs),
        created_utc='2026-10-28T03:00:00+00:00',epoch=0,dependencies=[],time_min=None,progress_before=0)
    (logs/'submit_time_rel-night-prepare-unique.json').write_text(json.dumps(dict(name=intent['name'],argv=intent['argv'],job_id='123')))
    s['submission_intents']={'prepare':intent}
    fake=SimpleNamespace(ROOT=tmp_path,workspace_root=lambda root:root,submit=lambda *a,**k:pytest.fail('duplicate sbatch'))
    monkeypatch.setattr(suite,'_submitter',lambda source:fake)
    suite._submit_node(c,s,node)
    assert s['attempts']['prepare'][0]['job_id']=='123' and not s['submission_intents']


def test_fast_worker_progress_uses_pre_submission_baseline(tmp_path,monkeypatch):
    c,s=setup(tmp_path);node=c['nodes'][0];node['command']='prepare';s['source']={'snapshot':'fixture'}
    def submit(*args,**kwargs):
        Path(node['marker']).with_name('progress.json').write_text('{"captured_rows":512}')
        return '123'
    fake=SimpleNamespace(ROOT=tmp_path,workspace_root=lambda root:root,submit=submit)
    monkeypatch.setattr(suite,'_submitter',lambda source:fake)
    suite._submit_node(c,s,node)
    assert s['attempts']['prepare'][0]['progress_before']==0


def test_unexecuted_dependency_cancellation_is_not_a_stalled_execution(tmp_path):
    c,s=setup(tmp_path)
    s['attempts']['prepare']=[{'job_id':'1','state':'CANCELLED','progress_before':0},
        {'job_id':'2','state':'SUBMITTED','progress_before':0}]
    assert suite.reconcile(c,s,{'2':{'state':'TIMEOUT'}})==['prepare']


def test_torn_submission_metadata_falls_back_to_exact_scheduler_name(tmp_path,monkeypatch):
    name='rel-night-prepare-unique';(tmp_path/f'submit_time_{name}.json').write_text('{"job_id":')
    intent=dict(name=name,argv=['exact'],log_dir=str(tmp_path),created_utc='2026-10-28T03:00:00+00:00',epoch=0)
    monkeypatch.setattr(suite.subprocess,'run',lambda argv,**k:SimpleNamespace(returncode=0,stderr='',stdout=f'123|{name}\n'))
    assert suite._recover_intent(intent)==('123',True)


def test_scientific_workers_wait_for_matching_full_regression_proof(tmp_path,monkeypatch):
    c,s=setup(tmp_path);s['source']={'source_sha256':'a'*64};node=c['nodes'][0]
    monkeypatch.setattr(suite,'_submitter',lambda *a:pytest.fail('scientific worker submitted before QA'))
    suite._submit_node(c,s,node)
    assert s['status']['prepare']['state']=='awaiting_software_validation'
    proof=c['software_validation'];p=Path(proof['junit'])
    p.write_text('<testsuites><testsuite tests="2" failures="0" errors="0" skipped="0"/></testsuites>')
    review=dict(status='passed',source_sha256='a'*64,junit_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    Path(proof['review']).write_text(json.dumps(review));assert suite._validation_passed(c,s)
    review['source_sha256']='b'*64;Path(proof['review']).write_text(json.dumps(review))
    assert not suite._validation_passed(c,s)
