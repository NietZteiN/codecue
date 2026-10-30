"""Durable, CPU-only SLURM reconciliation for the local experiment log.

Two delayed workers are kept in SLURM, rather than a terminal-owned daemon.
Every worker schedules replacement guards before importing/running the indexer.
A failed worker or disconnected VSCode session does not own its successor.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import pwd
import shlex
import subprocess
import sys
import time

SCHEMA_VERSION = 1
GUARDS = 2
CHECK_INTERVAL_SECONDS = 60
RECENT_SUBMISSION_SECONDS = 120
RUNNING = {'RUNNING', 'COMPLETING', 'CONFIGURING', 'SUSPENDED'}


class SchedulerError(RuntimeError):
    pass


def workspace(root=None):
    path=Path(root).resolve() if root is not None else Path(__file__).resolve().parents[3]
    frozen=path/'frozen_manifest.json'
    if frozen.exists():path=Path(json.loads(frozen.read_text())['workspace_root']).resolve()
    return path


def control_paths(root=None):
    root=workspace(root);folder=root/'artifacts/binding/experiment_log'
    return dict(root=root,folder=folder,state=folder/'scheduler_state.json',lock=folder/'scheduler.lock',
                run_lock=folder/'scheduler_run.lock',journal=folder/'scheduler_journal.jsonl',logs=folder/'scheduler_jobs')


def _utc(epoch):
    return datetime.fromtimestamp(epoch,timezone.utc).isoformat()


def _save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    with temp.open('w') as stream:
        stream.write(json.dumps(data,sort_keys=True,indent=2,default=str)+'\n')
        stream.flush();os.fsync(stream.fileno())
    temp.replace(path)


def _read(path):
    return json.loads(path.read_text()) if path.exists() else None


@contextmanager
def _lock(path,blocking=True):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        try:yield
        finally:fcntl.flock(stream,fcntl.LOCK_UN)


def _journal(paths,kind,now,**payload):
    with paths['journal'].open('a') as stream:
        stream.write(json.dumps(dict(kind=kind,recorded_utc=_utc(now),**payload),sort_keys=True,default=str)+'\n')
        stream.flush();os.fsync(stream.fileno())


def _run(argv,runner):
    try:result=runner(argv,capture_output=True,text=True,timeout=20,check=False)
    except (OSError,subprocess.TimeoutExpired) as exc:raise SchedulerError(f'{argv[0]}: {exc}') from exc
    if result.returncode:raise SchedulerError(f'{argv[0]}: {result.stderr.strip() or result.stdout.strip()}')
    return result.stdout.strip()


def _owner():
    return pwd.getpwuid(os.getuid()).pw_name


def _account(user,runner):
    if os.environ.get('SLURM_JOB_ACCOUNT'):return os.environ['SLURM_JOB_ACCOUNT']
    text=_run(['sacctmgr','-n','-P','show','user',user,'format=DefaultAccount'],runner)
    values=[line.split('|')[0].strip() for line in text.splitlines() if line.strip()]
    if len(values)!=1 or not values[0]:raise SchedulerError('Cannot determine the SLURM account; use --account explicitly.')
    return values[0]


def _job_name(root):
    return 'binding-log-'+hashlib.sha256(str(root).encode()).hexdigest()[:12]


def _python(root):
    candidate=(root.parent/'envs/probe-cu129/bin/python').absolute()
    # Preserve the virtualenv entrypoint: resolving its symlink selects base Python.
    return str(candidate if candidate.exists() else Path(sys.executable).absolute())


def _query(state,runner):
    if state.get('job_name')!=_job_name(Path(state['root'])) or state.get('owner_user')!=_owner():
        raise SchedulerError('Scheduler control identity differs from this workspace/user; refusing job actions.')
    text=_run(['squeue','-h','-u',state['owner_user'],'--name',state['job_name'],
               '-o','%i|%j|%a|%T|%S|%u'],runner)
    jobs={}
    for line in text.splitlines():
        fields=[part.strip() for part in line.split('|')]
        if len(fields)!=6:continue
        jid,name,account,status,start,user=fields
        # A damaged state file or an unrelated job must never widen cancellation.
        if (not jid.isdigit() or name!=state['job_name'] or account!=state['account'] or user!=state['owner_user']):continue
        jobs[jid]=dict(job_id=jid,name=name,account=account,state=status,start_time=start,user=user,verified=True)
    return jobs


def _freshness(state,now):
    interval=state.get('interval_minutes')
    if type(interval) is not int or interval<1:
        return dict(freshness_status='unknown',freshness_error='Invalid reconciliation interval',
                    last_success_age_seconds=None,freshness_grace_seconds=None)
    grace=3*interval*60
    success=state.get('last_success_utc')
    reference=success or state.get('enabled_utc')
    try:
        stamp=datetime.fromisoformat(reference)
        if stamp.tzinfo is None:raise ValueError('timezone required')
        age=max(0.,now-stamp.timestamp())
    except (TypeError,ValueError,OverflowError):
        return dict(freshness_status='unknown',freshness_error='Missing or invalid reconciliation timestamp',
                    last_success_age_seconds=None,freshness_grace_seconds=grace)
    overdue=age>grace
    return dict(freshness_status='overdue' if overdue else 'fresh' if success else 'starting',
                freshness_error='No successful reconciliation within three intervals' if overdue else None,
                last_success_age_seconds=age if success else None,freshness_grace_seconds=grace)


def _view(state,jobs=None,*,cached=False,error=None,now=None):
    if state is None:return dict(status='not_installed',installed=False,enabled=False,healthy=False)
    jobs=list((jobs or {}).values())
    pending=sum(job['state'] not in RUNNING for job in jobs)
    running=sum(job['state'] in RUNNING for job in jobs)
    now=time.time() if now is None else now
    freshness=_freshness(state,now)
    enabled=bool(state.get('enabled'));problem=error or state.get('last_scheduler_error') or state.get('last_tick_error') or freshness['freshness_error']
    return dict(status='disabled' if not enabled else 'degraded' if problem or pending<GUARDS else 'enabled',
                installed=True,enabled=enabled,healthy=enabled and not problem and pending>=GUARDS,
                root=state['root'],job_name=state['job_name'],account=state['account'],partition=state['partition'],
                interval_minutes=state['interval_minutes'],pending_guards=pending,running_workers=running,
                workers=jobs,cached=cached,last_tick_utc=state.get('last_tick_utc'),
                last_success_utc=state.get('last_success_utc'),**freshness,
                next_reconcile_utc=_utc(state['next_reconcile_epoch']) if state.get('next_reconcile_epoch') else None,
                last_result=state.get('last_result'),error=problem,scheduler_error=error or state.get('last_scheduler_error'))


def _submit(state,paths,start_epoch,now,runner):
    paths['logs'].mkdir(parents=True,exist_ok=True)
    minutes=max(1,math.ceil((start_epoch-now)/60))
    command=shlex.join([state['python'],state['script'],'tick','--root',state['root']])
    # Reconciliation now exceeds two minutes on the accumulated metadata index.
    # Leave room for the index lock and export; this is separate from tick cadence.
    argv=['sbatch','--parsable','--job-name='+state['job_name'],'--account='+state['account'],
          '--partition='+state['partition'],'--cpus-per-task=1','--mem=1G','--time=00:10:00',
          '--requeue','--dependency=singleton','--nice=1000','--begin=now+'+str(minutes)+'minutes',
          '--chdir='+state['root'],'--output='+str(paths['logs']/'%j.out'),
          '--comment=CodeCue experiment-log reconciliation; no model or GPU', '--wrap',command]
    jid=_run(argv,runner).split(';')[0]
    if not jid.isdigit():raise SchedulerError('sbatch did not return a decimal job ID')
    job=dict(job_id=jid,submitted_epoch=now,requested_start_epoch=now+minutes*60)
    state.setdefault('jobs',[]).append(job)
    # Persist each accepted job before attempting another submission.
    _save(paths['state'],state);_journal(paths,'worker_submitted',now,job=job,argv=argv)
    return job


def _ensure_locked(state,paths,runner,now):
    active=_query(state,runner)
    known={j['job_id']:j for j in state.get('jobs',[])}
    # sbatch and the following squeue RPC need not become visible atomically.
    for jid,job in known.items():
        if jid not in active and now-job.get('submitted_epoch',0)<RECENT_SUBMISSION_SECONDS:
            active[jid]=dict(job_id=jid,name=state['job_name'],account=state['account'],state='PENDING',
                             start_time='awaiting scheduler visibility',user=state['owner_user'],verified=False)
    state['jobs']=[dict(known.get(jid,dict(job_id=jid,submitted_epoch=0,requested_start_epoch=now+60*state['interval_minutes'])))
                   for jid in active]
    pending=[j for j in active.values() if j['state'] not in RUNNING]
    starts=[j.get('requested_start_epoch',now) for j in state['jobs'] if j['job_id'] in {x['job_id'] for x in pending}]
    next_start=max([now]+starts)
    while len(pending)<GUARDS:
        next_start+=60*state['interval_minutes'];job=_submit(state,paths,next_start,now,runner)
        entry=dict(job_id=job['job_id'],name=state['job_name'],account=state['account'],state='PENDING',
                   start_time=_utc(job['requested_start_epoch']),user=state['owner_user'],verified=True)
        active[job['job_id']]=entry;pending.append(entry)
    state['last_health_check_epoch']=now;state['last_scheduler_error']=None
    _save(paths['state'],state)
    return _view(state,active,now=now)


def enable(root=None,*,interval_minutes=10,partition='dev',account=None,runner=None,now=None):
    runner=runner or subprocess.run;now=time.time() if now is None else now;paths=control_paths(root)
    if type(interval_minutes) is not int or interval_minutes<1:raise ValueError('interval_minutes must be a positive integer')
    if partition not in ('dev','normal'):raise ValueError('Use a CPU-only dev or normal partition')
    paths['folder'].mkdir(parents=True,exist_ok=True)
    with _lock(paths['lock']):
        state=_read(paths['state']);user=_owner();chosen=account or (state or {}).get('account') or _account(user,runner)
        if state and state.get('enabled') and (state['account']!=chosen or state['partition']!=partition):
            raise SchedulerError('Disable the existing reconciler before changing its account or partition.')
        if state is None:
            state=dict(schema_version=SCHEMA_VERSION,root=str(paths['root']),owner_user=user,job_name=_job_name(paths['root']),
                       python=_python(paths['root']),script=str((paths['root']/'scripts/118_binding_log_scheduler.py').absolute()),jobs=[])
        state.update(enabled=True,account=chosen,partition=partition,interval_minutes=interval_minutes,
                     next_reconcile_epoch=state.get('next_reconcile_epoch',now),enabled_utc=_utc(now))
        _save(paths['state'],state);_journal(paths,'enabled',now,interval_minutes=interval_minutes,partition=partition)
        try:return _ensure_locked(state,paths,runner,now)
        except SchedulerError as exc:
            state.update(last_scheduler_error=str(exc),last_health_check_epoch=now);_save(paths['state'],state)
            return _view(state,error=str(exc),now=now)


def ensure_enabled(root=None,*,runner=None,now=None,force=False):
    """Repair an installed enabled loop; ordinary activity must not auto-enable it."""
    runner=runner or subprocess.run;now=time.time() if now is None else now;paths=control_paths(root)
    try:state=_read(paths['state'])
    except (OSError,ValueError) as exc:return dict(status='degraded',installed=True,enabled=None,healthy=False,error=f'Invalid scheduler control state: {exc}')
    if not state or not state.get('enabled'):return _view(state,now=now)
    if not force and now-state.get('last_health_check_epoch',0)<CHECK_INTERVAL_SECONDS:
        jobs={j['job_id']:dict(job_id=j['job_id'],state='PENDING',verified=False) for j in state.get('jobs',[])}
        return _view(state,jobs,cached=True,now=now)
    try:
        with _lock(paths['lock'],blocking=force):
            state=_read(paths['state'])
            if not state or not state.get('enabled'):return _view(state,now=now)
            try:return _ensure_locked(state,paths,runner,now)
            except SchedulerError as exc:
                state.update(last_scheduler_error=str(exc),last_health_check_epoch=now);_save(paths['state'],state)
                return _view(state,error=str(exc),now=now)
    except BlockingIOError:return dict(status='busy',installed=True,enabled=True,healthy=None)


def status(root=None,*,runner=None,now=None):
    runner=runner or subprocess.run;now=time.time() if now is None else now;paths=control_paths(root)
    try:state=_read(paths['state'])
    except (OSError,ValueError) as exc:return dict(status='degraded',installed=True,enabled=None,healthy=False,error=f'Invalid scheduler control state: {exc}')
    if not state:return _view(state,now=now)
    try:return _view(state,_query(state,runner),now=now)
    except SchedulerError as exc:return _view(state,error=str(exc),now=now)


def disable(root=None,*,runner=None,now=None):
    runner=runner or subprocess.run;now=time.time() if now is None else now;paths=control_paths(root)
    if not paths['state'].exists():return _view(None,now=now)
    with _lock(paths['lock']):
        state=_read(paths['state']);state.update(enabled=False,disabled_utc=_utc(now));_save(paths['state'],state)
        known={j['job_id'] for j in state.get('jobs',[])}
        try:
            active=_query(state,runner);verified=sorted(known & set(active))
            if verified:_run(['scancel',*verified],runner)
            _journal(paths,'disabled',now,cancelled_verified_jobs=verified)
            result=_view(state,now=now);result['cancelled_jobs']=verified
            result['unrecorded_matching_jobs']=sorted(set(active)-known)
            return result
        except SchedulerError as exc:
            state['last_scheduler_error']=str(exc);_save(paths['state'],state)
            result=_view(state,error=str(exc),now=now);result['cancellation_failed']=True
            return result


def tick(root=None,*,runner=None,refresh_fn=None,now=None,force=False):
    runner=runner or subprocess.run;now=time.time() if now is None else now;paths=control_paths(root)
    ensured=ensure_enabled(paths['root'],runner=runner,now=now,force=True)
    if not ensured.get('enabled'):return ensured
    if ensured.get('pending_guards',0)<GUARDS or ensured.get('scheduler_error'):
        return dict(status='failed',error=ensured.get('error') or 'Unable to preserve two successor guards',scheduler=ensured)
    try:
        with _lock(paths['run_lock'],blocking=False):
            with _lock(paths['lock']):
                state=_read(paths['state'])
                if not state.get('enabled'):return _view(state,now=now)
                interval_seconds=state['interval_minutes']*60
                # Guard slots are scheduled ahead of time. Small differences in
                # startup delay must not turn every other worker into a skip.
                due_grace=min(30,interval_seconds/10)
                if not force and now+due_grace<state.get('next_reconcile_epoch',0):return dict(status='not_due',scheduler=ensured)
                state.update(last_tick_utc=_utc(now),next_reconcile_epoch=now+interval_seconds)
                _save(paths['state'],state)
            try:
                if refresh_fn is None:
                    from .experiment_log import refresh
                    refresh_fn=refresh
                result=refresh_fn(paths['root'],reconcile_scheduler=True)
            except Exception as exc:
                with _lock(paths['lock']):
                    state=_read(paths['state']);state['last_tick_error']=f'{type(exc).__name__}: {exc}';_save(paths['state'],state)
                    _journal(paths,'tick_failed',now,error=state['last_tick_error'])
                return dict(status='failed',error=state['last_tick_error'],scheduler=ensured)
            with _lock(paths['lock']):
                state=_read(paths['state']);state.update(last_success_utc=_utc(time.time()),last_tick_error=None,
                    last_result={k:v for k,v in result.items() if k in ('status','counts','events','runs','analyses','jobs','artifacts','report','database','root','indexed_events','new_events')})
                _save(paths['state'],state);_journal(paths,'tick_complete',now,result=state['last_result'])
            # Report the successful refresh rather than its pre-refresh stale view.
            observed={job['job_id']:job for job in ensured.get('workers',[])}
            ensured=_view(state,observed,now=time.time())
            return dict(status='complete',result=result,scheduler=ensured)
    except BlockingIOError:return dict(status='busy',scheduler=ensured)
