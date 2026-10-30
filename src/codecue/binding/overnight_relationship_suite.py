"""Durable SLURM DAG and morning status for the overnight discovery suite."""
from __future__ import annotations

from datetime import datetime,timezone
from contextlib import contextmanager
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from . import relationship_capture as base,overnight_relationship_capture as capture
from .datasets import digest

ROLE='discovery_overnight_relationship_suite_v1'
TRANSIENT={'TIMEOUT','PREEMPTED','NODE_FAIL','BOOT_FAIL'}
TERMINAL={'COMPLETED','FAILED','CANCELLED','TIMEOUT','PREEMPTED','NODE_FAIL','BOOT_FAIL','OUT_OF_MEMORY'}
SCRIPTS={'scripts/149_binding_overnight_relationship_capture.py','scripts/150_binding_overnight_relationship_readouts.py','scripts/151_binding_overnight_relationship_behavior.py'}


@contextmanager
def _lock(folder):
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'.suite.lock').open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        try:yield
        finally:fcntl.flock(stream,fcntl.LOCK_UN)


def _config(config):
    required={'evaluation_role','nodes','run_dir','report','morning_at','declared_plan','declared_plan_sha256','software_validation'}
    if not isinstance(config,dict) or set(config)!=required or config.get('evaluation_role')!=ROLE:
        raise ValueError('exact overnight suite configuration required')
    for key in ('run_dir','report','declared_plan'):base._safe(config[key])
    if base._sha(config['declared_plan'])!=config['declared_plan_sha256']:raise ValueError('overnight suite plan changed')
    if datetime.fromisoformat(config['morning_at']).tzinfo is None:raise ValueError('explicit local morning offset required')
    names=[];phases={}
    for node in config['nodes']:
        required_node={'key','script','command','config','config_sha256','dependencies','partition','mem','cpus','time','time_min','phase','marker','marker_status','expected_cases'}
        if not isinstance(node,dict) or set(node)!=required_node or node['script'] not in SCRIPTS or node['phase'] not in ('gpu','cpu'):
            raise ValueError('exact typed overnight job node required')
        if node['key'] in names or set(node['dependencies'])-set(names):raise ValueError('unique topologically ordered suite nodes required')
        if node['phase']=='gpu' and any(phases[name]=='cpu' for name in node['dependencies']):
            raise ValueError('GPU phase cannot depend on the deferred CPU phase')
        if base._sha(node['config'])!=node['config_sha256']:raise ValueError('overnight node configuration changed')
        base._safe(node['marker']);names.append(node['key']);phases[node['key']]=node['phase']
    if not names:raise ValueError('nonempty overnight job suite required')
    if Path(config['report']).resolve()==Path(config['declared_plan']).resolve():raise ValueError('suite report cannot replace its plan')


def _validation_passed(config,state):
    proof=config['software_validation']
    try:
        review=base._json(proof['review'])
        tree=ET.parse(proof['junit']).getroot()
        suites=tree.findall('testsuite')
        return (review.get('status')=='passed' and review.get('source_sha256')==state['source']['source_sha256']
            and review.get('junit_sha256')==base._sha(proof['junit'])
            and sum(int(s.attrib.get('tests',0)) for s in suites)>=proof['minimum_tests']
            and all(int(s.attrib.get(k,0))==0 for s in suites for k in ('failures','errors','skipped')))
    except (OSError,ValueError,ET.ParseError):return False


def _source(snapshot,config):
    from .snapshots import verify
    folder=Path(snapshot).resolve();m=verify(folder)
    result=dict(snapshot=str(folder),snapshot_id=m['snapshot_id'],source_sha256=m['code']['source_sha256'],frozen_manifest_sha256=base._sha(folder/'frozen_manifest.json'))
    base._verify_source(config,result);return result


def _submitter(source):
    spec=importlib.util.spec_from_file_location('overnight_frozen_submit',Path(source['snapshot'])/'scripts/slurm/submit.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def _save(config,state):
    capture._journal(Path(config['run_dir'])/'jobs_live_v1.json',state)


def _submit_node(config,state,node):
    if node['command']=='run' and node['script'].endswith(('capture.py','behavior.py')) and not _validation_passed(config,state):
        state['status'][node['key']]={'state':'awaiting_software_validation'};_save(config,state);return
    module=_submitter(state['source'])
    deps=[state['attempts'][name][-1]['job_id'] for name in node['dependencies']
        if state['status'].get(name,{}).get('state')!='complete']
    argv=['/work/jvl210002/migration/envs/probe-cu129/bin/python',str(module.workspace_root(module.ROOT)/'scripts/91_binding_frozen_run.py'),
        state['source']['snapshot'],node['script'],node['command'],node['config']]
    attempts=state['attempts'][node['key']]
    intents=state.setdefault('submission_intents',{})
    intent=intents.get(node['key'])
    if intent is not None:
        if intent.get('argv')!=argv or not intent.get('name','').startswith('rel-night-'+node['key']+'-'):
            raise ValueError('owned submission intent does not match its frozen node')
        recovered,definitive=_recover_intent(intent)
        if recovered:
            attempts.append(dict(job_id=recovered,state='SUBMITTED',progress_before=intent['progress_before'],
                time_min=intent['time_min'],submitted_utc=intent['created_utc'],dependencies=intent['dependencies']))
            intents.pop(node['key']);state['status'][node['key']]={'state':'submitted','job_id':recovered};_save(config,state);return
        if not definitive:
            state['status'][node['key']]={'state':'awaiting_submission_recovery'};_save(config,state);return
        intents.pop(node['key'])
    minimum=node['time_min']
    if minimum and attempts and attempts[-1].get('state')=='TIMEOUT':
        minimum=attempts[-1].get('time_min') or minimum
        hours,minutes,seconds=map(int,minimum.split(':'))
        limit=node['time'];days=0
        if '-' in limit:day,limit=limit.split('-',1);days=int(day)
        lh,lm,ls=map(int,limit.split(':'));maximum=days*86400+lh*3600+lm*60+ls
        total=min((hours*3600+minutes*60+seconds)*2,maximum)
        minimum=f'{total//3600:02d}:{total%3600//60:02d}:{total%60:02d}'
    intent=dict(name='rel-night-'+node['key']+'-'+uuid.uuid4().hex[:8],argv=argv,
        created_utc=datetime.now(timezone.utc).isoformat(),epoch=time.time(),dependencies=deps,
        time_min=minimum,progress_before=_progress(node),log_dir=str(module.workspace_root(module.ROOT)/'log/slurm'))
    intents[node['key']]=intent;_save(config,state)
    try:
        job=module.submit(intent['name'],node['partition'],argv,
            dependency='afterok:'+':'.join(deps) if deps else None,mem=node['mem'],cpus=node['cpus'],time=node['time'],time_min=minimum)
    except (OSError,ValueError,SystemExit) as exc:
        state.setdefault('submission_failures',{})[node['key']]={
            'error':f'{type(exc).__name__}: {exc}','terminal':isinstance(exc,(SystemExit,OSError))}
        state['status'][node['key']]={'state':'failed' if isinstance(exc,(SystemExit,OSError)) else 'awaiting_submission_recovery','reason':str(exc)}
        _save(config,state);return
    attempts.append(dict(job_id=job,state='SUBMITTED',progress_before=intent['progress_before'],time_min=minimum,
        submitted_utc=datetime.now(timezone.utc).isoformat(),dependencies=deps))
    intents.pop(node['key']);state['status'][node['key']]={'state':'submitted','job_id':job};_save(config,state)


def _recover_intent(intent):
    """Recover accepted own jobs from submit's durable metadata or exact unique name."""
    for path in Path(intent['log_dir']).glob('submit_*_'+intent['name']+'.json'):
        try:data=base._json(path)
        except (OSError,ValueError):continue
        if data.get('name')==intent['name'] and data.get('argv')==intent['argv'] and str(data.get('job_id','')).isdigit():
            return str(data['job_id']),True
    found=set();ok=True
    local=datetime.fromisoformat(intent['created_utc']).astimezone(ZoneInfo('America/Chicago')).strftime('%Y-%m-%dT00:00:00')
    for command in [['squeue','-h','--name',intent['name'],'-o','%i|%j'],
                    ['sacct','-X','-n','-P','--name',intent['name'],'--starttime',local,'--format=JobIDRaw,JobName%128']]:
        try:result=subprocess.run(command,capture_output=True,text=True,timeout=20,check=False)
        except (OSError,subprocess.TimeoutExpired):ok=False;continue
        if result.returncode:ok=False;continue
        for line in result.stdout.splitlines():
            fields=line.strip().split('|')
            if len(fields)>=2 and fields[0].isdigit() and fields[1].strip()==intent['name']:found.add(fields[0])
    if len(found)>1:raise ValueError('multiple scheduler jobs match one suite submission intent')
    if found:return next(iter(found)),True
    return None,ok and time.time()-intent['epoch']>=60


def submit(config,snapshot,config_path):
    with _lock(Path(config['run_dir'])):return _submit_locked(config,snapshot,config_path)


def _submit_locked(config,snapshot,config_path):
    _config(config);source=_source(snapshot,config);folder=Path(config['run_dir']);folder.mkdir(parents=True,exist_ok=True)
    path=folder/'jobs_live_v1.json'
    if path.exists():raise ValueError('overnight suite already submitted; use watch/status, do not duplicate')
    if base._json(config_path)!=config:raise ValueError('suite configuration path differs')
    state=dict(evaluation_role=ROLE,config_hash=digest(config),source=source,config_path=str(config_path),
        attempts={n['key']:[] for n in config['nodes']},status={},controllers=[],created_utc=datetime.now(timezone.utc).isoformat())
    _save(config,state)
    # A delayed supervisor is durable before any scientific worker submission.
    _submit_controller(config,state)
    for node in config['nodes']:
        if node['phase']=='gpu' and node['command']=='prepare':_submit_node(config,state,node)
    return status(config)


def _submit_controller(config,state,parent=None):
    module=_submitter(state['source'])
    argv=['/work/jvl210002/migration/envs/probe-cu129/bin/python',str(module.workspace_root(module.ROOT)/'scripts/91_binding_frozen_run.py'),
        state['source']['snapshot'],'scripts/152_binding_overnight_relationship_suite.py','watch',state['config_path']]
    job=module.submit('rel-night-controller','dev',argv,dependency='afterany:'+parent if parent else None,
        mem='4G',cpus=1,time='02:00:00',begin='now+5minutes')
    state['controllers'].append(job);_save(config,state)
    return job


def scheduler(ids,runner=None):
    runner=runner or subprocess.run
    if not ids:return {},[]
    if any(not str(value).isdigit() for value in ids):raise ValueError('numeric owned job IDs required')
    jobs={};errors=[]
    for command in [['sacct','-X','-n','-P','-j',','.join(ids),'--format=JobIDRaw,State%32,ExitCode,Reason%80,ElapsedRaw'],
                    ['squeue','-h','-j',','.join(ids),'-o','%i|%T|%r']]:
        try:r=runner(command,capture_output=True,text=True,timeout=20,check=False)
        except (OSError,subprocess.TimeoutExpired) as exc:errors.append(f'{command[0]}: {exc}');continue
        if r.returncode:errors.append(f'{command[0]}: {r.stderr.strip()}');continue
        for line in r.stdout.splitlines():
            fields=line.strip().split('|')
            if len(fields)<3 or fields[0] not in ids:continue
            entry=jobs.setdefault(fields[0],{});entry['state']=fields[1].split()[0].rstrip('+')
            if command[0]=='sacct':entry.update(exit_code=fields[2],reason=fields[3] if len(fields)>3 else '')
            else:entry['reason']=fields[2]
    return jobs,errors


def _marker(node):
    p=Path(node['marker'])
    if not p.exists():return False
    try:data=capture._json(p)
    except (ValueError,OSError):return False
    expected=node['marker_status']
    return (data.get('config_hash')==digest(base._json(node['config']))
        and (data.get('status')==expected if isinstance(expected,str) else data.get('complete') is expected))


def _progress(node):
    folder=Path(node['marker']).parent
    for name in ('progress.json','manifest.json'):
        try:data=capture._json(folder/name)
        except (OSError,ValueError):continue
        if 'fits' in data:return int(data['fits'])
        if 'captured_rows' in data:return int(data['captured_rows'])
        if 'chunks' in data:return sum(entry['rows'] for entry in data['chunks'] if Path(entry['path']).is_file())
    p=folder/'responses.jsonl'
    if p.exists():
        with p.open('rb') as stream:return sum(block.count(b'\n') for block in iter(lambda:stream.read(1024**2),b''))
    return 0


def reconcile(config,state,observed):
    """Pure transition decisions; only owned nodes can be retried/submitted."""
    actions=[];statuses={}
    for node in config['nodes']:
        key=node['key'];attempts=state['attempts'][key]
        parents=[statuses[name]['state'] for name in node['dependencies']]
        if not attempts:
            failure=state.get('submission_failures',{}).get(key,{})
            statuses[key]={'state':'failed' if failure.get('terminal') else 'blocked' if any(v in ('failed','blocked') for v in parents) else 'planned'}
            continue
        latest=attempts[-1];job=observed.get(latest['job_id'],{});raw=job.get('state','UNKNOWN')
        latest.update(job)
        if raw=='COMPLETED':
            statuses[key]={'state':'complete' if job.get('exit_code') in ('0:0','0') and _marker(node) else 'failed','job_id':latest['job_id']}
        elif raw in TRANSIENT:
            progress=_progress(node);latest['progress_after']=progress
            executed=[a for a in attempts if a.get('state') in TRANSIENT]
            stalled=sum(a.get('progress_after',a.get('progress_before',0))<=a.get('progress_before',0) for a in executed[-2:])
            retry=not(len(executed)>=2 and stalled==2)
            statuses[key]={'state':'retry' if retry else 'failed','job_id':latest['job_id'],'reason':raw}
        elif raw=='CANCELLED' and job.get('reason')=='DependencyNeverSatisfied':
            statuses[key]={'state':'retry' if not any(v in ('failed','blocked') for v in parents) else 'blocked','job_id':latest['job_id']}
        elif raw in TERMINAL:statuses[key]={'state':'failed','job_id':latest['job_id'],'reason':job.get('reason',raw)}
        elif any(value in ('failed','blocked') for value in parents) and raw=='PENDING':
            statuses[key]={'state':'blocked','job_id':latest['job_id'],'reason':'required upstream stage failed'}
        else:statuses[key]={'state':raw.lower(),'job_id':latest['job_id'],'reason':job.get('reason')}
    gpu_terminal=all(statuses[n['key']]['state'] in ('complete','failed','blocked') for n in config['nodes'] if n['phase']=='gpu')
    for node in config['nodes']:
        item=statuses[node['key']]
        if item['state'] in ('planned','retry') and all(statuses[name]['state']=='complete' for name in node['dependencies']):
            if node['phase']=='gpu' or gpu_terminal:actions.append(node['key'])
    state['status']=statuses
    return actions


def _report(config,state,errors):
    values=[entry['state'] for entry in state['status'].values()]
    complete=bool(values) and all(value=='complete' for value in values)
    terminal=bool(values) and all(value in ('complete','failed','blocked') for value in values)
    science=[n for n in config['nodes'] if (n['script'].endswith('capture.py') and n['command']=='run') or n['script'].endswith('behavior.py')]
    observed_queries=0
    for node in science:
        try:journal=capture._json(Path(node['marker']).parent/'manifest.json')
        except (OSError,ValueError):continue
        observed_queries+=sum(a.get('prefill_cases_attempted',0) for a in journal.get('attempts',[]))
    result=dict(status='complete_exploratory' if complete else 'needs_attention' if terminal else 'running',
        evaluation_role=ROLE,config_hash=digest(config),recorded_utc=datetime.now(timezone.utc).isoformat(),
        stages=state['status'],attempts=state['attempts'],scheduler_errors=errors,all_terminal=terminal,
        source=state['source'],new_model_queries=0,generated_holdouts_opened=False,
        planned_scientific_case_prefills=sum(n['expected_cases'] for n in science),observed_scientific_prefill_attempts=observed_queries,
        scope='Controller metadata only. Scientific worker query counts remain in their own manifests.')
    folder=Path(config['run_dir']);capture._journal(folder/'status_review_v1.json',result)
    text=['# Overnight relationship suite','',f"Status: {result['status']}. Morning status time: {config['morning_at']}.",'',
        '| Stage | State | Latest job | Reason |','|---|---|---:|---|']
    for key,item in state['status'].items():text.append(f"| {key} | {item['state']} | {item.get('job_id','')} | {item.get('reason','')} |")
    text+=['','Stages use the frozen discovery plan. Failed scientific guards are reported rather than retried. Only resumable scheduler interruptions receive automatic retries; repeated failures with no committed progress stop retrying. Existing jobs outside this suite are never canceled.','']
    from .overnight_relationship_behavior import _replace_owned
    p=Path(config['report']);p.parent.mkdir(parents=True,exist_ok=True);_replace_owned(p,'\n'.join(text).encode())
    morning=datetime.fromisoformat(config['morning_at'])
    if (terminal or datetime.now(timezone.utc)>=morning) and not (folder/'morning_review_v1.json').exists():
        base._put(folder/'morning_review_v1.json',dict(result,scientific_results=_collect_outputs(config,state)))
    if terminal and not (folder/'results_review_v1.json').exists():
        base._put(folder/'results_review_v1.json',dict(result,scientific_results=_collect_outputs(config,state)))
    return result


def _collect_outputs(config,state):
    """Read only completed, checksum-pinned scientific JSON; no arrays or model calls."""
    summaries={}
    for node in config['nodes']:
        if state['status'].get(node['key'],{}).get('state')!='complete':continue
        cfg=base._json(node['config']);folder=Path(cfg['run_dir'])
        if node['script'].endswith('readouts.py'):
            receipt=capture._json(folder/'completion_manifest_v1.json');entry=receipt['artifacts']['results']
            payload=base._bytes(entry['path'],256*1024**2)
            if base._sha(entry['path'])!=entry['sha256']:raise ValueError('completed overnight scientific result changed')
            data=json.loads(payload)
            summaries[node['key']]=dict(kind='readouts',model=data.get('model'),panel=data.get('panel'),
                cases=data.get('cases'),factorizations=data.get('factorizations'),parameter_replay_rows=data.get('parameter_replay_rows'),
                literal_transfer_rows=data.get('literal_transfer_rows'),primary_layer=cfg['primary_layer'],
                summaries=data.get('summaries'),source_result=dict(path=entry['path'],sha256=entry['sha256']))
        elif node['script'].endswith('behavior.py'):
            receipt=capture._json(folder/'completion_manifest_v1.json');entry=receipt['artifacts']['summary']
            data=base._json(entry['path'],entry['sha256'])
            summaries[node['key']]=dict(kind='behavior',model=data['model'],cases=data['cases'],
                new_model_queries=data['new_model_queries'],metrics=data['metrics'],source_result=entry)
    return summaries


def status(config):
    _config(config);state=capture._json(Path(config['run_dir'])/'jobs_live_v1.json')
    ids=[a['job_id'] for attempts in state['attempts'].values() for a in attempts]
    observed,errors=scheduler(ids);reconcile(config,state,observed)
    return _report(config,state,errors)


def watch(config):
    _config(config)
    with _lock(Path(config['run_dir'])):return _watch(config)


def _watch(config):
    _config(config);base._slurm();source=base._current_source(config)
    folder=Path(config['run_dir']);state=capture._json(folder/'jobs_live_v1.json')
    if state['source']!=source or state['config_hash']!=digest(config):raise ValueError('controller source/config identity differs')
    first=status(config)
    if first['all_terminal']:
        state['status']=first['stages'];state['attempts']=first['attempts']
        _save(config,state);return first
    # Install successor before doing work, so a scheduler kill cannot orphan retry supervision.
    _submit_controller(config,state,parent=os.environ['SLURM_JOB_ID'])
    state=capture._json(folder/'jobs_live_v1.json')
    ids=[a['job_id'] for attempts in state['attempts'].values() for a in attempts]
    observed,errors=scheduler(ids);actions=reconcile(config,state,observed);_save(config,state)
    if not errors:
        for key in actions:_submit_node(config,state,next(n for n in config['nodes'] if n['key']==key))
    result=_report(config,state,errors)
    from .experiment_log_scheduler import tick
    from .registry import ROOT
    from .snapshots import workspace_root
    tick(workspace_root(ROOT),force=False)
    return result
