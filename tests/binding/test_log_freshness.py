"""Scheduling guards alone cannot establish fresh experiment data."""
import json

from codecue.binding import experiment_log_scheduler as scheduler
from test_log_scheduler import FakeSlurm


def state(root, fake, now=1000):
    scheduler.enable(root,account='test_account',runner=fake,now=now)
    path=scheduler.control_paths(root)['state']
    data=json.loads(path.read_text())
    return path,data


def root_path(tmp_path):
    root=tmp_path/'workspace';(root/'scripts').mkdir(parents=True)
    (root/'scripts/118_binding_log_scheduler.py').write_text('# fixture\n')
    return root


def test_queued_guards_do_not_hide_old_success(tmp_path,monkeypatch):
    root=root_path(tmp_path);fake=FakeSlurm();path,data=state(root,fake)
    data['last_success_utc']=scheduler._utc(1000);path.write_text(json.dumps(data))
    monkeypatch.setattr(scheduler.time,'time',lambda:4000)
    result=scheduler.status(root,runner=fake)
    assert result['pending_guards']==2
    assert result['healthy'] is False
    assert result['freshness_status']=='overdue'
    assert result['last_success_utc']==scheduler._utc(1000)
    assert result['last_success_age_seconds']==3000


def test_never_successful_worker_eventually_becomes_overdue(tmp_path,monkeypatch):
    root=root_path(tmp_path);fake=FakeSlurm();state(root,fake)
    monkeypatch.setattr(scheduler.time,'time',lambda:2801)
    result=scheduler.status(root,runner=fake)
    assert result['healthy'] is False
    assert result['freshness_status']=='overdue'
    assert result['last_success_utc'] is None


def test_initial_startup_has_grace(tmp_path,monkeypatch):
    root=root_path(tmp_path);fake=FakeSlurm();state(root,fake)
    monkeypatch.setattr(scheduler.time,'time',lambda:1001)
    result=scheduler.status(root,runner=fake)
    assert result['healthy'] is True
    assert result['freshness_status']=='starting'
    assert result['freshness_grace_seconds']==1800


def test_new_success_recovers_freshness_without_canceling_jobs(tmp_path,monkeypatch):
    root=root_path(tmp_path);fake=FakeSlurm();path,data=state(root,fake)
    data['last_success_utc']=scheduler._utc(1000);path.write_text(json.dumps(data))
    monkeypatch.setattr(scheduler.time,'time',lambda:4000)
    result=scheduler.tick(root,runner=fake,now=4000,force=True,refresh_fn=lambda *a,**k:dict(status='ok'))
    assert result['status']=='complete'
    assert result['scheduler']['freshness_status']=='fresh'
    healthy=scheduler.status(root,runner=fake)
    assert healthy['healthy'] and healthy['freshness_status']=='fresh'
    assert healthy['last_success_age_seconds']==0
    assert not any(call[0]=='scancel' for call in fake.calls)


def test_recent_attempt_does_not_replace_actual_success(tmp_path,monkeypatch):
    root=root_path(tmp_path);fake=FakeSlurm();path,data=state(root,fake)
    data.update(last_success_utc=scheduler._utc(1000),last_tick_utc=scheduler._utc(3999))
    path.write_text(json.dumps(data));monkeypatch.setattr(scheduler.time,'time',lambda:4000)
    assert scheduler.status(root,runner=fake)['freshness_status']=='overdue'


def test_bad_success_timestamp_is_not_reported_healthy(tmp_path,monkeypatch):
    root=root_path(tmp_path);fake=FakeSlurm();path,data=state(root,fake)
    data['last_success_utc']='not-a-time';path.write_text(json.dumps(data))
    monkeypatch.setattr(scheduler.time,'time',lambda:1001)
    result=scheduler.status(root,runner=fake)
    assert not result['healthy'] and result['freshness_status']=='unknown'
