import json

from codecue.binding.budget import reserve, release
from codecue.binding.datasets import write_json


def test_explicitly_uncapped_ledger_tracks_parallel_cached_models_without_exhaustion(tmp_path):
    path = tmp_path / 'usage.json'
    write_json(path, dict(cap_seconds=10, checkpoint_policy='single', checkpoint=['legacy', 'a' * 40],
                         used_seconds=1000000, active={}, completed=[]))
    cfg = dict(device='cuda', model='cached-a', model_revision='a' * 40,
               run_dir='suite-a', max_gpu_seconds=0, budget_ledger=str(path))
    first = reserve(cfg, 'checkpoint_suite')
    second = reserve({**cfg, 'model': 'cached-b', 'run_dir': 'suite-b'}, 'checkpoint_suite')
    assert first['reserved_seconds'] == second['reserved_seconds'] == 0
    release(first, 100, 'complete')
    state = json.loads(path.read_text())
    assert state['cap_seconds'] is None and state['used_seconds'] == 1000100
    assert len(state['active']) == 1 and len(state['checkpoints']) == 2
    release(second, 200, 'complete')
    assert json.loads(path.read_text())['used_seconds'] == 1000300


def test_old_default_ledger_is_read_only_and_all_new_work_uses_uncapped_accounting(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    historical = tmp_path / 'artifacts/binding/gpu_budget.json'
    write_json(historical, dict(cap_seconds=14400, used_seconds=14400, active={}, completed=[]))
    before = historical.read_bytes()
    lease = reserve(dict(device='cuda', model='new', model_revision='b' * 40, run_dir='new',
                         budget_ledger='artifacts/binding/gpu_budget.json'), 'published_behavior')
    assert lease['ledger'] == 'artifacts/binding/gpu_usage_uncapped.json'
    assert historical.read_bytes() == before
    release(lease, 40, 'complete')


def test_parallel_allocation_accounts_for_every_gpu_without_limiting_runtime(tmp_path, monkeypatch):
    monkeypatch.setenv('SLURM_GPUS_ON_NODE', '2')
    path = tmp_path / 'usage.json'
    lease = reserve(dict(device='cuda', model='parallel', model_revision='c' * 40, run_dir='parallel',
                         budget_ledger=str(path), max_gpu_seconds=None), 'checkpoint_suite')
    release(lease, 30, 'complete')
    state = json.loads(path.read_text())
    assert state['used_seconds'] == 60 and state['completed'][0]['wall_seconds'] == 30
