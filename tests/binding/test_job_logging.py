"""Job lifecycle logging must not alter task execution or scheduler outcomes."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types

import pytest


PROJECT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location('test_slurm_' + name, PROJECT / 'scripts/slurm' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def logger(monkeypatch, *, failing=False):
    events, synced = [], []
    def emit(kind, **kwargs):
        if failing:raise OSError('logging unavailable')
        events.append((kind, kwargs))
    def sync(**kwargs):
        if failing:raise OSError('index unavailable')
        synced.append(kwargs)
    monkeypatch.setitem(sys.modules, 'codecue.binding.experiment_log', types.SimpleNamespace(safe_emit_event=emit, safe_sync_job=sync))
    return events, synced


def submitter(tmp_path, monkeypatch, *, returncode=0, stdout='12345;cluster\n'):
    mod = module('submit')
    monkeypatch.setattr(mod, 'ROOT', tmp_path)
    monkeypatch.setattr(mod, 'load_config', lambda name: dict(slurm=dict(log_dir_rel='log/slurm', partitions=dict(dev=dict(cpus=4, mem='32G', time='00:10:00')))))
    calls = []
    def command(argv, **kwargs):
        calls.append(argv)
        if argv[0] == 'git':return subprocess.CompletedProcess(argv, 0, 'abc123\n', '')
        assert argv[:2] == ['sbatch', '--parsable']
        return subprocess.CompletedProcess(argv, returncode, stdout, 'scheduler refused' if returncode else '')
    monkeypatch.setattr(mod.subprocess, 'run', command)
    return mod, calls


def test_submission_event_has_real_scheduler_identity_and_exact_resources(tmp_path,monkeypatch):
    events,_ = logger(monkeypatch)
    mod,calls = submitter(tmp_path,monkeypatch)
    argv = [sys.executable,'frozen/scripts/91_binding_frozen_run.py','snapshot','module','run','cfg.json']
    assert mod.submit('experiment','dev',argv,dependency='afterok:12',mem='48G',time='00:20:00') == '12345'
    assert len(events) == 1 and events[0][0] == 'job_submitted'
    item = events[0][1]
    assert item['job_id'] == '12345' and item['root'] == tmp_path.resolve()
    payload = item['payload']
    assert payload['argv'] == argv and payload['dependency'] == 'afterok:12'
    assert payload['mem'] == '48G' and payload['cpus'] == 4 and payload['time'] == '00:20:00'
    saved = json.loads(Path(payload['submission_manifest']).read_text())
    assert saved['job_id'] == '12345' and saved['status'] == 'submitted'


def test_submission_failure_and_dry_run_are_not_recorded_as_submitted(tmp_path,monkeypatch):
    events,_ = logger(monkeypatch)
    mod,calls = submitter(tmp_path,monkeypatch,returncode=1)
    with pytest.raises(SystemExit) as exc:mod.submit('failed','dev',['python','run.py'])
    assert exc.value.code == 1
    assert [kind for kind,_ in events] == ['job_submission_failed']
    before = len(calls)
    assert mod.submit('dry','dev',['python','run.py'],dry_run=True) is None
    assert len(calls) == before + 1  # Read-only git identity; no sbatch or real event.
    assert [kind for kind,_ in events] == ['job_submission_failed']
    assert not list((tmp_path/'log/slurm').glob('*_dry.json'))


def test_logging_outage_does_not_change_successful_submission(tmp_path,monkeypatch,capsys):
    logger(monkeypatch,failing=True)
    mod,_ = submitter(tmp_path,monkeypatch)
    assert mod.submit('experiment','dev',['python','run.py']) == '12345'
    assert 'Experiment logging warning' in capsys.readouterr().err


def test_frozen_submit_uses_workspace_logs_and_current_stamp_wrapper(tmp_path,monkeypatch):
    events,_ = logger(monkeypatch)
    workspace=tmp_path/'workspace';workspace.mkdir()
    frozen=tmp_path/'snapshot';frozen.mkdir()
    (frozen/'frozen_manifest.json').write_text(json.dumps(dict(workspace_root=str(workspace))))
    mod,_ = submitter(frozen,monkeypatch)
    mod.submit('frozen','dev',['python','snapshot/scripts/91_binding_frozen_run.py'])
    assert not (frozen/'log').exists()
    script=next((workspace/'log/slurm').glob('*.sbatch')).read_text()
    assert str(workspace/'scripts/slurm/stamp.py') in script
    assert events[0][1]['root'] == workspace.resolve()


def test_stamp_lifecycle_and_duplicate_finish_keep_original_result(tmp_path,monkeypatch):
    events,synced = logger(monkeypatch)
    mod=module('stamp');monkeypatch.setattr(mod,'ROOT',tmp_path)
    monkeypatch.setenv('SLURM_JOB_ID','42');monkeypatch.setenv('SLURMD_NODENAME','node1')
    monkeypatch.setenv('SLURM_JOB_PARTITION','h200');monkeypatch.setenv('SLURM_RESTART_COUNT','1')
    source=tmp_path/'submit.json';target=tmp_path/'42.json';argv=['python','frozen/91_binding_frozen_run.py','config.json']
    source.write_text(json.dumps(dict(name='study',argv=argv,partition='h100,h200')))
    monkeypatch.setattr(sys,'argv',['stamp.py','start',str(source),str(target)])
    assert mod.main() == 0
    started=json.loads(target.read_text())
    assert started['status']=='running' and started['actual_partition']=='h200' and started['restart_count']==1
    monkeypatch.setattr(sys,'argv',['stamp.py','finish',str(target),'7'])
    assert mod.main() == 0
    finished=json.loads(target.read_text())
    assert finished['exit_code']==7 and finished['status']=='failed'
    assert mod.main() == 0 and json.loads(target.read_text()) == finished
    assert [kind for kind,_ in events] == ['job_started','job_finished']
    assert len(synced)==2 and synced[0]['payload']['argv']==argv
    assert synced[0]['payload']['job_manifest']==str(target.resolve())
    assert synced[0]['job_id']=='42'


def test_stamp_recovers_completion_and_tolerates_logging_outage(tmp_path,monkeypatch,capsys):
    logger(monkeypatch,failing=True)
    mod=module('stamp');monkeypatch.setattr(mod,'ROOT',tmp_path)
    monkeypatch.setenv('SLURM_JOB_ID','43');monkeypatch.setenv('SLURM_JOB_NAME','recovered')
    target=tmp_path/'43.json'
    monkeypatch.setattr(sys,'argv',['stamp.py','finish',str(target),'0'])
    assert mod.main()==0
    data=json.loads(target.read_text())
    assert data['exit_code']==0 and data['status']=='completed' and data['job_id']=='43'
    assert 'metadata_warning' in data
    assert 'logging warning' in capsys.readouterr().err


def test_multiline_argv_is_not_evaluated_by_display_and_stamp_failure_preserves_exit(tmp_path,monkeypatch):
    # Render with mocked sbatch, then execute the actual Bash wrapper locally.
    # Both stamp invocations fail deliberately; only the task's exit 7 may win.
    logger(monkeypatch)
    real_run = subprocess.run
    mod,_ = submitter(tmp_path,monkeypatch)
    marker=tmp_path/'injected';other=tmp_path/'substitution';output=tmp_path/'payload.txt'
    payload=f'`touch {marker}` $(touch {other})\n"quoted"\n'
    code=f'from pathlib import Path\nPath({str(output)!r}).write_text({payload!r})\nraise SystemExit(7)'
    mod.submit('quoting','dev',[sys.executable,'-c',code])
    shell=next((tmp_path/'log/slurm').glob('*.sbatch'))
    (tmp_path/'scripts/slurm').mkdir(parents=True)
    (tmp_path/'scripts/env.sh').write_text('export PATH='+str(Path(sys.executable).absolute().parent)+':$PATH\n')
    (tmp_path/'scripts/slurm/stamp.py').write_text('raise SystemExit(9)\n')
    env=dict(os.environ,SLURM_JOB_ID='12345',SLURMD_NODENAME='node',SLURM_JOB_PARTITION='dev')
    # submitter monkeypatches the shared subprocess module; restore for Bash.
    monkeypatch.undo()
    result=real_run(['bash',str(shell)],env=env,capture_output=True,text=True)
    assert result.returncode==7
    assert output.read_text()==payload and not marker.exists() and not other.exists()


def test_accepted_job_id_survives_post_submission_manifest_write_failure(tmp_path,monkeypatch,capsys):
    events,_=logger(monkeypatch)
    mod,_=submitter(tmp_path,monkeypatch)
    original=Path.replace
    def replace(path,target):
        if path.name.endswith('.json.tmp'):raise OSError('temporary manifest update failed')
        return original(path,target)
    monkeypatch.setattr(Path,'replace',replace)
    assert mod.submit('accepted','dev',['python','run.py'])=='12345'
    assert events[0][0]=='job_submitted' and events[0][1]['job_id']=='12345'
    assert 'submission_manifest_update_error' in events[0][1]['payload']
    assert 'Submission metadata warning' in capsys.readouterr().err
