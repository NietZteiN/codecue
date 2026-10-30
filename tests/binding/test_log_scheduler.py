from pathlib import Path
import json
import os
import subprocess

import pytest

from codecue.binding import experiment_log_scheduler as scheduler


class FakeSlurm:
    def __init__(self):
        self.calls=[];self.jobs={};self.next_id=100;self.submit_count=0;self.fail_submit=None;self.hide=set()

    def __call__(self,argv,**kwargs):
        self.calls.append(list(argv))
        if argv[0]=='squeue':
            text='\n'.join('|'.join([jid,j['name'],j['account'],j['state'],'2026-10-26T12:00:00',j['user']])
                           for jid,j in self.jobs.items() if jid not in self.hide)
            return subprocess.CompletedProcess(argv,0,text,'')
        if argv[0]=='sacctmgr':return subprocess.CompletedProcess(argv,0,'test_account|\n','')
        if argv[0]=='sbatch':
            self.submit_count+=1
            if self.submit_count==self.fail_submit:return subprocess.CompletedProcess(argv,1,'','submission rejected')
            jid=str(self.next_id);self.next_id+=1
            name=next(x.split('=',1)[1] for x in argv if x.startswith('--job-name='))
            account=next(x.split('=',1)[1] for x in argv if x.startswith('--account='))
            self.jobs[jid]=dict(name=name,account=account,state='PENDING',user=scheduler._owner())
            return subprocess.CompletedProcess(argv,0,jid+'\n','')
        if argv[0]=='scancel':
            for jid in argv[1:]:self.jobs.pop(jid,None)
            return subprocess.CompletedProcess(argv,0,'','')
        raise AssertionError(argv)


@pytest.fixture
def root(tmp_path):
    path=tmp_path/'workspace';(path/'scripts').mkdir(parents=True)
    (path/'scripts/118_binding_log_scheduler.py').write_text('# scheduler entrypoint\n')
    return path


def install(root,fake,now=1000):
    return scheduler.enable(root,account='test_account',runner=fake,now=now)


def test_two_durable_cpu_guards_are_idempotent_and_preserve_virtualenv_entrypoint(root):
    env=root.parent/'envs/probe-cu129/bin';env.mkdir(parents=True)
    (env/'python').symlink_to('/usr/bin/python3')
    fake=FakeSlurm();result=install(root,fake)
    assert result['healthy'] and result['pending_guards']==2 and len(fake.jobs)==2
    submissions=[c for c in fake.calls if c[0]=='sbatch']
    assert ['--begin=now+10minutes','--begin=now+20minutes']==[next(x for x in c if x.startswith('--begin=')) for c in submissions]
    for c in submissions:
        assert '--partition=dev' in c and '--cpus-per-task=1' in c and '--mem=1G' in c
        assert '--time=00:10:00' in c and '--requeue' in c and '--dependency=singleton' in c
        assert not any(x.startswith(('--gpus','--gres')) for x in c)
        command=c[c.index('--wrap')+1]
        assert str(env/'python') in command and str(root/'scripts/118_binding_log_scheduler.py') in command
    install(root,fake,now=1001)
    scheduler.ensure_enabled(root,runner=fake,now=1100,force=True)
    assert fake.submit_count==2


def test_activity_hook_never_installs_or_reenables_a_disabled_loop(root):
    fake=FakeSlurm()
    assert scheduler.ensure_enabled(root,runner=fake,now=1000)['status']=='not_installed'
    assert fake.calls==[]
    install(root,fake);scheduler.disable(root,runner=fake,now=1010)
    fake.calls.clear()
    assert scheduler.ensure_enabled(root,runner=fake,now=1200)['status']=='disabled'
    assert not fake.calls


def test_guards_are_submitted_before_failed_refresh_and_next_worker_recovers(root):
    fake=FakeSlurm();install(root,fake)
    first='100';fake.jobs[first]['state']='RUNNING'
    def broken(project,*,reconcile_scheduler):
        assert project==root.resolve() and reconcile_scheduler
        assert sum(j['state']=='PENDING' for j in fake.jobs.values())==2
        raise RuntimeError('temporary index failure')
    failed=scheduler.tick(root,runner=fake,refresh_fn=broken,now=1600)
    assert failed['status']=='failed' and fake.submit_count==3
    state=json.loads(scheduler.control_paths(root)['state'].read_text())
    assert state['last_tick_error']=='RuntimeError: temporary index failure'
    fake.jobs.pop(first);fake.jobs['101']['state']='RUNNING'
    healthy=scheduler.tick(root,runner=fake,refresh_fn=lambda *a,**k:dict(status='updated',counts={'runs':2}),now=2200)
    assert healthy['status']=='complete' and fake.submit_count==4
    assert sum(j['state']=='PENDING' for j in fake.jobs.values())==2
    assert json.loads(scheduler.control_paths(root)['state'].read_text())['last_tick_error'] is None


def test_abrupt_worker_loss_keeps_successors_and_next_tick_records_actual_success(root,monkeypatch):
    class WorkerTerminated(BaseException):
        pass
    fake=FakeSlurm();install(root,fake);paths=scheduler.control_paths(root)
    fake.jobs['100']['state']='RUNNING'
    def terminated(*args,**kwargs):
        # Scheduler termination can bypass the normal Exception/error journal.
        saved=json.loads(paths['state'].read_text())
        assert {j['job_id'] for j in saved['jobs']}==set(fake.jobs)
        assert sum(j['state']=='PENDING' for j in fake.jobs.values())==2
        raise WorkerTerminated()
    with pytest.raises(WorkerTerminated):
        scheduler.tick(root,runner=fake,refresh_fn=terminated,now=1600)
    assert json.loads(paths['state'].read_text()).get('last_success_utc') is None
    fake.jobs.pop('100');fake.jobs['101']['state']='RUNNING'
    # A metadata refresh lasting beyond the old allocation can finish and report
    # its real completion time; ten-minute scheduling remains unchanged.
    completed=2200+150
    monkeypatch.setattr(scheduler.time,'time',lambda:completed)
    restored=scheduler.tick(root,runner=fake,refresh_fn=lambda *a,**k:dict(status='ok'),now=2200)
    assert restored['status']=='complete'
    saved=json.loads(paths['state'].read_text())
    assert saved['last_success_utc']==scheduler._utc(completed)
    assert saved['next_reconcile_epoch']==2800
    assert sum(j['state']=='PENDING' for j in fake.jobs.values())==2
    assert fake.submit_count==4
    assert all('--time=00:10:00' in c for c in fake.calls if c[0]=='sbatch')
    assert not any(c[0]=='scancel' for c in fake.calls)


def test_cancelled_pending_guard_is_repaired_without_spawning_duplicates(root):
    fake=FakeSlurm();install(root,fake);fake.jobs.pop('100')
    repaired=scheduler.ensure_enabled(root,runner=fake,now=1121,force=True)
    assert repaired['pending_guards']==2 and fake.submit_count==3
    scheduler.ensure_enabled(root,runner=fake,now=1122,force=True)
    assert fake.submit_count==3


def test_recent_rpc_visibility_lag_does_not_duplicate_accepted_submissions(root):
    fake=FakeSlurm();install(root,fake);fake.hide={'100','101'}
    result=scheduler.ensure_enabled(root,runner=fake,now=1001,force=True)
    assert result['pending_guards']==2 and fake.submit_count==2
    assert all(not j['verified'] for j in result['workers'])


def test_disable_cancels_only_recorded_jobs_with_verified_name_account_and_owner(root):
    fake=FakeSlurm();install(root,fake);paths=scheduler.control_paths(root);state=json.loads(paths['state'].read_text())
    common=dict(name=state['job_name'],account='test_account',state='PENDING',user=scheduler._owner())
    fake.jobs.update({'999':dict(common,name='hold-node'),'888':dict(common,account='other-account'),
                      '777':dict(common,user='someone-else'),'666':dict(common)})
    state['jobs'] += [dict(job_id=jid,submitted_epoch=0,requested_start_epoch=0) for jid in ('999','888','777')]
    paths['state'].write_text(json.dumps(state))
    result=scheduler.disable(root,runner=fake,now=1200)
    assert result['status']=='disabled' and result['cancelled_jobs']==['100','101']
    assert result['unrecorded_matching_jobs']==['666']
    assert set(fake.jobs)=={'999','888','777','666'}
    assert [c for c in fake.calls if c[0]=='scancel']==[['scancel','100','101']]


def test_non_due_or_concurrent_ticks_do_not_duplicate_refresh(root):
    fake=FakeSlurm();install(root,fake);calls=[]
    refresh=lambda *a,**k:(calls.append(1) or dict(status='updated'))
    assert scheduler.tick(root,runner=fake,refresh_fn=refresh,now=1000)['status']=='complete'
    assert scheduler.tick(root,runner=fake,refresh_fn=refresh,now=1001)['status']=='not_due'
    with scheduler._lock(scheduler.control_paths(root)['run_lock']):
        assert scheduler.tick(root,runner=fake,refresh_fn=refresh,now=1600)['status']=='busy'
    assert calls==[1]


@pytest.mark.parametrize('interval_minutes,startup_delay,expected',[
    (10,1,'complete'),
    (10,30,'complete'),
    (10,31,'not_due'),
    (1,6,'complete'),
    (1,7,'not_due'),
])
def test_guard_startup_jitter_has_bounded_grace(root,interval_minutes,startup_delay,expected):
    fake=FakeSlurm();calls=[];interval=interval_minutes*60
    scheduler.enable(root,account='test_account',interval_minutes=interval_minutes,runner=fake,now=1000)
    refresh=lambda *a,**k:(calls.append(1) or dict(status='updated'))
    first_start=1000+interval+startup_delay
    fake.jobs['100']['state']='RUNNING'
    assert scheduler.tick(root,runner=fake,refresh_fn=refresh,now=first_start)['status']=='complete'
    assert scheduler.tick(root,runner=fake,refresh_fn=refresh,now=first_start+1)['status']=='not_due'
    fake.jobs.pop('100');fake.jobs['101']['state']='RUNNING'
    second_start=1000+2*interval
    assert scheduler.tick(root,runner=fake,refresh_fn=refresh,now=second_start)['status']==expected
    assert len(calls)==(2 if expected=='complete' else 1)
    assert sum(j['state']=='PENDING' for j in fake.jobs.values())==2


def test_disabled_tick_never_refreshes_or_submits(root):
    fake=FakeSlurm();install(root,fake);scheduler.disable(root,runner=fake)
    def forbidden(*a,**k):raise AssertionError('must not refresh')
    before=fake.submit_count
    assert scheduler.tick(root,runner=fake,refresh_fn=forbidden,now=2000)['status']=='disabled'
    assert fake.submit_count==before


def test_partial_submission_failure_keeps_first_guard_for_later_repair(root):
    fake=FakeSlurm();fake.fail_submit=2
    result=install(root,fake)
    assert result['status']=='degraded' and set(fake.jobs)=={'100'}
    state=json.loads(scheduler.control_paths(root)['state'].read_text())
    assert state['enabled'] and state['jobs'][0]['job_id']=='100'
    fake.fail_submit=None
    result=scheduler.ensure_enabled(root,runner=fake,now=1121,force=True)
    assert result['healthy'] and len(fake.jobs)==2


def test_activity_checks_are_throttled_and_scheduler_outages_never_submit_blind(root):
    fake=FakeSlurm();install(root,fake);fake.calls.clear()
    assert scheduler.ensure_enabled(root,runner=fake,now=1001)['cached']
    assert fake.calls==[]
    def unavailable(argv,**kwargs):
        assert argv[0]=='squeue'
        return subprocess.CompletedProcess(argv,1,'','controller temporarily unavailable')
    result=scheduler.ensure_enabled(root,runner=unavailable,now=1121,force=True)
    assert result['status']=='degraded' and fake.submit_count==2


def test_status_is_read_only_and_account_resolution_uses_actual_default(root,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ACCOUNT',raising=False)
    fake=FakeSlurm();scheduler.enable(root,runner=fake,now=1000)
    before=scheduler.control_paths(root)['state'].read_bytes();count=fake.submit_count
    result=scheduler.status(root,runner=fake)
    assert result['healthy'] and result['account']=='test_account'
    assert fake.submit_count==count and scheduler.control_paths(root)['state'].read_bytes()==before


def test_reject_gpu_partitions_and_nonpositive_intervals(root):
    with pytest.raises(ValueError,match='CPU-only'):scheduler.enable(root,partition='h200',account='a')
    with pytest.raises(ValueError,match='positive'):scheduler.enable(root,interval_minutes=0,account='a')


def test_corrupt_control_state_is_reported_without_submitting_or_cancelling(root):
    paths=scheduler.control_paths(root);paths['folder'].mkdir(parents=True)
    paths['state'].write_text('{interrupted manual edit')
    fake=FakeSlurm()
    assert scheduler.status(root,runner=fake)['status']=='degraded'
    assert scheduler.ensure_enabled(root,runner=fake)['status']=='degraded'
    assert fake.calls==[]


def test_altered_control_job_name_cannot_masquerade_as_the_host_allocation(root):
    fake=FakeSlurm();install(root,fake);paths=scheduler.control_paths(root)
    state=json.loads(paths['state'].read_text());state['job_name']='hold-node'
    state['jobs']=[dict(job_id='999',submitted_epoch=0,requested_start_epoch=0)]
    paths['state'].write_text(json.dumps(state))
    fake.jobs['999']=dict(name='hold-node',account='test_account',state='RUNNING',user=scheduler._owner())
    result=scheduler.disable(root,runner=fake)
    assert result['cancellation_failed'] and '999' in fake.jobs
    assert not any(call[0]=='scancel' for call in fake.calls)
