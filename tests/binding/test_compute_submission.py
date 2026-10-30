import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


def test_gpu_submission_accepts_multiple_gpus_and_uses_scheduler_maximum(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[2] / 'scripts/slurm/submit.py'
    spec = importlib.util.spec_from_file_location('test_gpu_submit', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    monkeypatch.setattr(module, 'load_config', lambda _: {'slurm': {'log_dir_rel': 'logs', 'partitions': {
        'h200': dict(gres='gpu:1', cpus=8, mem='64G', time='2-00:00:00')}}})
    calls = []
    def runner(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout='123\n' if argv[0] == 'sbatch' else 'revision\n')
    monkeypatch.setattr(module.subprocess, 'run', runner)
    assert module.submit('parallel', 'h200', ['python', 'job.py'], gpus=2, time_min='00:15:00') == '123'
    script = next((tmp_path / 'logs').glob('*.sbatch')).read_text()
    assert '#SBATCH --gres=gpu:2' in script and '#SBATCH --time=2-00:00:00' in script
    assert '#SBATCH --kill-on-invalid-dep=yes' in script
    assert '#SBATCH --time-min=00:15:00' in script


def test_cpu_override_is_real_allocation_and_recorded_in_manifest(tmp_path,monkeypatch):
    source=Path(__file__).resolve().parents[2]/'scripts/slurm/submit.py'
    spec=importlib.util.spec_from_file_location('test_cpu_submit',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'ROOT',tmp_path)
    monkeypatch.setattr(module,'load_config',lambda _:{'slurm':{'log_dir_rel':'logs','partitions':{'normal':dict(gres=None,cpus=4,mem='32G',time='2-00:00:00')}}})
    monkeypatch.setattr(module,'log_job',lambda *a,**k:None)
    monkeypatch.setattr(module.subprocess,'run',lambda argv,**kwargs:SimpleNamespace(returncode=0,stdout='123\n' if argv[0]=='sbatch' else 'revision\n'))
    assert module.submit('cpu','normal',['python','readouts.py'],cpus=16,begin='now+5minutes')=='123'
    assert '#SBATCH --cpus-per-task=16' in next((tmp_path/'logs').glob('*.sbatch')).read_text()
    assert json.loads(next((tmp_path/'logs').glob('*.json')).read_text())['cpus']==16
    assert '#SBATCH --begin=now+5minutes' in next((tmp_path/'logs').glob('*.sbatch')).read_text()
