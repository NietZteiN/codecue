"""Durable ten-minute metadata monitor; no models, scientific retries or cancellation."""
from contextlib import contextmanager
from datetime import datetime,timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

PYTHON='/work/jvl210002/migration/envs/probe-cu129/bin/python'
CONFIG='configs/binding/old_value_overnight_20261028_v1/check.json'
WORK=('regression','llama8b_preflight','codellama34b_preflight','llama8b_behavior','codellama34b_behavior','publication')
INTERVAL=600
STALL=1800


def _json(path):return json.loads(Path(path).read_text())
def _sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def _bytes(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def _save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as stream:
        temporary=Path(stream.name);stream.write(_bytes(value));stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)


@contextmanager
def _lock(folder):
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'.monitor.lock').open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        try:yield
        finally:fcntl.flock(stream,fcntl.LOCK_UN)


def _records(folder,repair=False):
    path=folder/'monitor_checks_v1.jsonl'
    if not path.exists():return []
    if path.stat().st_size>16*1024**2:raise ValueError('bounded monitor journal required')
    data=path.read_bytes();end=data.rfind(b'\n')+1
    if end<len(data) and repair:
        tail=data[end:];backup=folder/('monitor_uncommitted_'+hashlib.sha256(tail).hexdigest()[:16]+'.bin')
        if not backup.exists():backup.write_bytes(tail)
        with path.open('r+b') as stream:stream.truncate(end);stream.flush();os.fsync(stream.fileno())
    return [json.loads(line) for line in data[:end].splitlines() if line]


def _append(folder,record):
    _records(folder,repair=True)
    with (folder/'monitor_checks_v1.jsonl').open('ab') as stream:
        stream.write(json.dumps(record,sort_keys=True,separators=(',',':'),allow_nan=False).encode()+b'\n');stream.flush();os.fsync(stream.fileno())


def _pins(pointer,manifest,config_sha,helper_sha):
    if (pointer.get('snapshot_id')!=manifest.get('snapshot_id') or pointer.get('code')!=manifest.get('code',{}).get('source_sha256')
            or manifest.get('config_files',{}).get(CONFIG)!=config_sha):raise ValueError('monitor frozen source/config pins differ')
    if len(helper_sha)!=64:raise ValueError('monitor helper SHA required')
    return dict(snapshot_id=pointer['snapshot_id'],source_sha256=pointer['code'],check_config_sha256=config_sha,helper_sha256=helper_sha)


def _recover(intent,runner=subprocess.run,now=None):
    """Find exactly this uniquely named accepted submission; never guess ownership."""
    for path in Path(intent['log_dir']).glob('submit_*_'+intent['name']+'.json'):
        try:value=_json(path)
        except (OSError,ValueError):continue
        if value.get('name')==intent['name'] and value.get('argv')==intent['argv'] and str(value.get('job_id','')).isdigit():return str(value['job_id']),True
    found=set();ok=True
    start=datetime.fromtimestamp(intent['epoch'],timezone.utc).strftime('%Y-%m-%dT00:00:00')
    for command in [['squeue','-h','--name',intent['name'],'-o','%i|%j'],['sacct','-n','-X','-P','--name',intent['name'],'--starttime',start,'--format=JobIDRaw,JobName%128']]:
        try:value=runner(command,capture_output=True,text=True,timeout=20,check=False)
        except (OSError,subprocess.TimeoutExpired):ok=False;continue
        if value.returncode:ok=False;continue
        for line in value.stdout.splitlines():
            fields=line.strip().split('|')
            if len(fields)>=2 and fields[0].isdigit() and fields[1].strip()==intent['name']:found.add(fields[0])
    if len(found)>1:raise ValueError('multiple jobs match one monitor intent')
    return (next(iter(found)),True) if found else (None,ok and (time.time() if now is None else now)-intent['epoch']>=60)


def _successor(folder,state,parent,argv,submit,recover,now):
    if parent in state['successors']:return state['successors'][parent]['job_id']
    intent=state.get('submission_intent')
    if intent:
        if intent.get('argv')!=argv or not intent.get('name','').startswith('oldvalue-watch-'):raise ValueError('monitor intent command differs')
        jid,definitive=recover(intent)
        if jid:
            state['successors'][intent['parent']]=dict(job_id=jid,name=intent['name'],recovered=True)
            state.pop('submission_intent');_save(folder/'monitor_state_v1.json',state)
            if jid!=parent:return jid
            intent=None
        if jid is None and not definitive:raise RuntimeError('accepted monitor submission remains uncertain; recovery deferred')
        if state.pop('submission_intent',None) is not None:_save(folder/'monitor_state_v1.json',state)
    intent=dict(name='oldvalue-watch-'+uuid.uuid4().hex[:12],argv=argv,parent=parent,epoch=now,
        log_dir=state['log_dir'],dependency='afterany:'+parent,begin='now+10minutes')
    state['submission_intent']=intent;_save(folder/'monitor_state_v1.json',state)
    try:jid=submit(intent)
    except (OSError,ValueError,SystemExit) as exc:raise RuntimeError('monitor submission pending recovery: '+str(exc)) from exc
    if not isinstance(jid,str) or not jid.isdigit():raise RuntimeError('scheduler returned no accepted monitor ID; recovery required')
    state['successors'][parent]=dict(job_id=jid,name=intent['name'],recovered=False)
    state.pop('submission_intent');_save(folder/'monitor_state_v1.json',state)
    return jid


def _terminal(result):return all(result.get('stages',{}).get(key,{}).get('status') in ('completed','failed') for key in WORK)


def _progress(result,previous,now):
    models={};issues=[];after={}
    for name in ('llama8b','codellama34b'):
        item=result.get('models',{}).get(name,{});progress=item.get('progress',{});count=progress.get('committed',0)
        old=previous.get(name);stage=result.get('stages',{}).get(name+'_behavior',{});running=stage.get('raw_state')=='RUNNING'
        if type(count) is not int or count<0:raise ValueError('nonnegative committed model count required')
        delta=None if old is None else count-old['committed']
        since=now if old is None or not running or not old.get('running') or delta!=0 else old['last_progress_epoch']
        stalled=max(0,now-since) if running else 0
        if stalled>=STALL:issues.append(name+': RUNNING without committed progress for '+str(int(stalled))+' seconds')
        if delta is not None and delta<0:issues.append(name+': committed response prefix decreased')
        if progress.get('invalid_committed_line') is not None:issues.append(name+': malformed committed response line '+str(progress['invalid_committed_line']))
        models[name]=dict(committed=count,planned=item.get('planned'),committed_delta=delta,running=running,
            stalled_running_seconds=stalled,trailing_partial=progress.get('trailing_partial',False),
            invalid_committed_line=progress.get('invalid_committed_line'),scientific_status=item.get('scientific_status','pending'))
        after[name]=dict(committed=count,running=running,last_progress_epoch=since,last_seen_epoch=now)
    return models,issues,after


def tick(folder,identity,parent,argv,check,submit,recover,*,now=None,log_dir=None):
    """One locked tick, with injectable operations for a source-only self-test."""
    now=time.time() if now is None else now
    with _lock(folder):
        path=folder/'monitor_state_v1.json'
        state=_json(path) if path.exists() else dict(schema_version=1,identity=identity,successors={},progress={},terminal=False,log_dir=str(log_dir or folder/'logs'))
        if state.get('identity')!=identity:raise ValueError('monitor source/config/helper identity changed')
        records=_records(folder,repair=True)
        completed=[r for r in records if r.get('kind')=='tick' and r.get('monitor_job_id')==parent]
        if completed:
            record=completed[-1];state['progress']=record['progress_state_after'];state['terminal']=record['all_work_and_publication_terminal']
            _save(path,state);return dict(status='already_checked',record=record)
        if state.get('terminal'):return dict(status='terminal_no_successor',last_check=state.get('last_check'))
        try:next_job=_successor(folder,state,parent,argv,submit,recover,now)
        except BaseException as exc:
            record=dict(kind='monitor_error',monitor_job_id=parent,checked_epoch=now,needs_attention=True,error=type(exc).__name__+': '+str(exc),submission_intent_preserved=bool(state.get('submission_intent')))
            _append(folder,record);_save(folder/'monitor_live_v1.json',record);raise
        try:
            result=check();models,issues,after=_progress(result,state.get('progress',{}),now)
            terminal=_terminal(result);error=None
        except Exception as exc:
            result={};models={};issues=['metadata checker failed'];after=state.get('progress',{});terminal=False;error=type(exc).__name__+': '+str(exc)
        record=dict(kind='tick',monitor_job_id=parent,checked_at=datetime.fromtimestamp(now,timezone.utc).isoformat(),checked_epoch=now,
            identity=identity,next_monitor_job_id=next_job,status=result.get('status','check_failed'),scientific_status=result.get('scientific_status','pending'),
            models=models,stages=result.get('stages',{}),logging=result.get('logging',{}),logging_refresh=result.get('logging_refresh'),checker_issues=result.get('issues',[]),
            scheduler_errors=result.get('scheduler_errors',[]),monitor_issues=issues,checker_error=error,
            needs_attention=bool(error or issues or result.get('needs_attention')),all_work_and_publication_terminal=terminal,
            progress_state_after=after,new_model_queries=0,new_fits=0)
        _append(folder,record);state.update(progress=after,terminal=terminal,last_check=record['checked_at']);_save(path,state)
        _save(folder/'monitor_live_v1.json',record)
        return dict(status='checked',record=record)


def _refresh_log_index(root,scheduler):
    # Guard scheduling alone does not refresh the index or last_success_utc.
    return scheduler.tick(root,force=True)


def _checked_with_logging(checker,refresh):
    first=checker()
    if first['logging']['fresh_within_two_intervals']:return first
    before_age=first['logging'].get('last_success_age_seconds')
    try:refreshed=refresh()
    except Exception as exc:refreshed=dict(status='failed',error=type(exc).__name__+': '+str(exc))
    # Observe persisted last_success again, including when a concurrent tick was busy.
    result=checker();actual_status=refreshed.get('status')
    result['logging_refresh']=dict(status=actual_status if actual_status in ('complete','busy','failed') else 'failed',
        raw_status=actual_status,error=refreshed.get('error'),force=True,previous_success_age_seconds=before_age,
        freshness_rechecked=True,observed_fresh=result['logging']['fresh_within_two_intervals'],
        observed_success_age_seconds=result['logging'].get('last_success_age_seconds'))
    if not result['logging']['fresh_within_two_intervals']:result['needs_attention']=True
    return result


def _runtime():
    folder=Path(__file__).resolve().parent;root=folder.parents[3];pointer=_json(folder/'execution_source_v1.json');snapshot=Path(pointer['snapshot'])
    sys.path.insert(0,str(snapshot/'src'))
    from codecue.binding import snapshots,old_value_overnight
    manifest=snapshots.verify(snapshot);config_path=snapshot/CONFIG;helper_sha=_sha(__file__)
    build=_json(folder/'monitor_build_review_v1.json')
    if build.get('status')!='passed' or build.get('helper_sha256')!=helper_sha:raise ValueError('monitor build review differs')
    identity=_pins(pointer,manifest,_sha(config_path),helper_sha);config=_json(config_path)
    spec=importlib.util.spec_from_file_location('old_value_monitor_submit',snapshot/'scripts/slurm/submit.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    def submit(intent):return module.submit(intent['name'],'dev,normal',intent['argv'],dependency=intent['dependency'],begin=intent['begin'],cpus=1,mem='4G',time='00:10:00')
    def check():
        from codecue.binding import experiment_log_scheduler
        return _checked_with_logging(lambda:old_value_overnight.check(config),
            lambda:_refresh_log_index(root,experiment_log_scheduler))
    return folder,root,identity,check,submit


def self_test():
    from types import SimpleNamespace
    checks=0;identity=dict(snapshot_id='a'*24,source_sha256='b'*64,check_config_sha256='c'*64,helper_sha256='d'*64)
    def result(count=0,raw='RUNNING',terminal=False):
        stages={key:dict(status='completed' if terminal else 'running',raw_state='COMPLETED' if terminal else raw,reason='None') for key in WORK}
        return dict(status='complete' if terminal else 'running',scientific_status='gate_failed',stages=stages,
            models={n:dict(planned=10,progress=dict(committed=count,trailing_partial=False,invalid_committed_line=None),scientific_status='gate_failed') for n in ('llama8b','codellama34b')},logging={},needs_attention=False)
    with tempfile.TemporaryDirectory(prefix='oldvalue-monitor-fixture-') as temporary:
        folder=Path(temporary);calls=[]
        def submit(intent):calls.append(intent);return str(100+len(calls))
        def check():assert len(calls)==1;return result(1)
        first=tick(folder,identity,'10',['python','helper'],check,submit,lambda i:(None,True),now=0)
        assert len(calls)==1 and first['record']['next_monitor_job_id']=='101';checks+=1
        second=tick(folder,identity,'10',['python','helper'],lambda:(_ for _ in ()).throw(AssertionError('repeat check')),submit,lambda i:(None,True),now=1)
        assert second['status']=='already_checked' and len(_records(folder))==1 and len(calls)==1;checks+=1
        bad=dict(identity,source_sha256='e'*64)
        try:tick(folder,bad,'11',[],check,submit,lambda i:(None,True),now=2)
        except ValueError:checks+=1
        else:raise AssertionError('changed source accepted')
        previous=first['record']['progress_state_after'];models,issues,_=_progress(result(1),previous,1800)
        assert len(issues)==2 and models['llama8b']['stalled_running_seconds']==1800;checks+=1
        models,issues,_=_progress(result(1,raw='PENDING'),previous,9999)
        assert not issues and models['llama8b']['stalled_running_seconds']==0;checks+=1
        models,issues,_=_progress(result(2),previous,1801);assert not issues and models['llama8b']['committed_delta']==1;checks+=1
        partial=result();partial['models']['llama8b']['progress']['trailing_partial']=True
        assert not _progress(partial,{},1)[1];partial['models']['llama8b']['progress']['invalid_committed_line']=1
        assert len(_progress(partial,{},1)[1])==1;checks+=1
        error=tick(folder,identity,'11',[],lambda:(_ for _ in ()).throw(ValueError('synthetic check error')),submit,lambda i:(None,True),now=1802)
        assert error['record']['needs_attention'] and 'synthetic check error' in error['record']['checker_error'];checks+=1
        terminal=tick(folder,identity,'12',[],lambda:result(10,terminal=True),submit,lambda i:(None,True),now=1803)
        before=len(calls);assert terminal['record']['all_work_and_publication_terminal'];checks+=1
        assert tick(folder,identity,'13',[],check,submit,lambda i:(None,True),now=1804)['status']=='terminal_no_successor' and len(calls)==before;checks+=1
        state=_json(folder/'monitor_state_v1.json');state['terminal']=False;state['submission_intent']=dict(name='oldvalue-watch-exact',argv=[],parent='14',epoch=1,log_dir=str(folder/'logs'));_save(folder/'monitor_state_v1.json',state)
        recovered=tick(folder,identity,'14',[],lambda:result(),lambda i:(_ for _ in ()).throw(AssertionError('duplicate sbatch')),lambda i:('777',True),now=1805)
        assert recovered['record']['next_monitor_job_id']=='777';checks+=1
        state=_json(folder/'monitor_state_v1.json');state['submission_intent']=dict(name='oldvalue-watch-self',argv=[],parent='15',epoch=1,log_dir=str(folder/'logs'));_save(folder/'monitor_state_v1.json',state)
        before=len(calls);current=tick(folder,identity,'16',[],lambda:result(),submit,lambda i:('16',True),now=1806)
        assert len(calls)==before+1 and current['record']['next_monitor_job_id']!='16';checks+=1
        journal=folder/'monitor_checks_v1.jsonl'
        with journal.open('ab') as stream:stream.write(b'{"partial":')
        _append(folder,dict(kind='synthetic_tail_recovery'));assert _records(folder)[-1]['kind']=='synthetic_tail_recovery' and list(folder.glob('monitor_uncommitted_*.bin'));checks+=1
        log=folder/'logs';log.mkdir(exist_ok=True);intent=dict(name='oldvalue-watch-recover',argv=['exact'],parent='15',epoch=0,log_dir=str(log))
        _save(log/'submit_now_oldvalue-watch-recover.json',dict(name=intent['name'],argv=['exact'],job_id='888'))
        assert _recover(intent,runner=lambda *a,**k:(_ for _ in ()).throw(AssertionError('unneeded scheduler query')),now=90)==('888',True);checks+=1
        intent=dict(intent,name='oldvalue-watch-ambiguous')
        blank=lambda *a,**k:SimpleNamespace(returncode=0,stdout='',stderr='')
        assert _recover(intent,runner=blank,now=10)==(None,False) and _recover(intent,runner=blank,now=90)==(None,True);checks+=1
        pointer=dict(snapshot_id='a'*24,code='b'*64);manifest=dict(snapshot_id='a'*24,code=dict(source_sha256='b'*64),config_files={CONFIG:'c'*64})
        assert _pins(pointer,manifest,'c'*64,'d'*64)==identity;checks+=1
        try:_pins(pointer,manifest,'e'*64,'d'*64)
        except ValueError:checks+=1
        else:raise AssertionError('changed frozen config accepted')
    # A successful index tick is distinct from merely preserving two queued guards.
    for api_status,becomes_fresh in [('complete',True),('busy',False),('failed',False),('complete',False),('enabled',False)]:
        state={'fresh':False,'checks':0,'ticks':0}
        def checker():
            state['checks']+=1
            return dict(logging=dict(guard_health=True,pending_guards=2,fresh_within_two_intervals=state['fresh'],
                last_success_age_seconds=0 if state['fresh'] else 2095),needs_attention=not state['fresh'])
        def index_tick(root,force=False):
            assert root=='synthetic-root' and force is True
            state['ticks']+=1;state['fresh']=becomes_fresh
            return dict(status=api_status,error='synthetic refresh failure' if api_status=='failed' else None,
                healthy=True,pending_guards=2)
        fake=SimpleNamespace(tick=index_tick,ensure_enabled=lambda *a,**k:(_ for _ in ()).throw(AssertionError('guard scheduling is not an index refresh')))
        observed=_checked_with_logging(checker,lambda:_refresh_log_index('synthetic-root',fake))
        assert state['ticks']==1 and state['checks']==2 and observed['logging_refresh']['freshness_rechecked']
        assert observed['logging_refresh']['observed_fresh'] is becomes_fresh
        assert observed['logging']['fresh_within_two_intervals'] is becomes_fresh
        assert observed['needs_attention'] is (not becomes_fresh)
        assert observed['logging_refresh']['status']==(api_status if api_status in ('complete','busy','failed') else 'failed')
        checks+=1
    fresh=dict(logging=dict(fresh_within_two_intervals=True),needs_attention=False)
    assert _checked_with_logging(lambda:fresh,lambda:(_ for _ in ()).throw(AssertionError('unneeded refresh'))) is fresh
    checks+=1
    return dict(status='passed',synthetic_checks=checks,actual_jobs_submitted=0,actual_models_loaded=False,actual_study_scans=False)


def main():
    if sys.argv[1:]==['--self-test']:print(json.dumps(self_test(),sort_keys=True));return
    if sys.argv[1:]:raise ValueError('only --self-test is supported')
    parent=os.environ.get('SLURM_JOB_ID')
    if not parent or not parent.isdigit():raise ValueError('monitor requires its own CPU SLURM allocation')
    folder,root,identity,check,submit=_runtime();argv=[PYTHON,str(Path(__file__).resolve())]
    deadline=time.monotonic()+180
    while True:
        try:value=tick(folder,identity,parent,argv,check,submit,_recover,log_dir=root/'log/slurm');break
        except (RuntimeError,OSError,SystemExit) as exc:
            if time.monotonic()>=deadline:raise
            time.sleep(15)
    print(json.dumps(dict(status=value['status'],record=value.get('record',{})),sort_keys=True))


if __name__=='__main__':main()
