import json

import pytest

from codecue.binding.throughput import choose, groups, quality, validation_complete


def test_prompt_buckets_preserve_questions_and_do_not_mix_token_ceilings():
    items = [dict(task=t, id=str(i), input_token_ids=list(range(n)))
             for t, i, n in [('direct', 0, 8), ('cot', 1, 2), ('direct', 2, 3), ('cot', 3, 4)]]
    batches = list(groups(items, 2, bucket=True))
    assert [[r['id'] for r in b] for b in batches] == [['2', '0'], ['1', '3']]
    assert all(len({r['task'] for r in batch}) == 1 for batch in batches)
    with pytest.raises(ValueError, match='positive'):
        list(groups(items, 0))


def test_quality_records_numerical_changes_without_selecting_by_accuracy():
    baseline = {('task', 'a'): dict(raw_response='old', score=dict(correct=True, valid=True, prediction="{'x': 1, 'y': 2}")),
                ('task', 'b'): dict(raw_response='invalid', score=dict(correct=False, valid=False, prediction=None))}
    rows = [dict(task='task', id='a', raw_response='new', score=dict(correct=True, valid=True, prediction="{'y': 2, 'x': 1}")),
            dict(task='task', id='b', raw_response='3', score=dict(correct=False, valid=True, prediction='3'))]
    result = quality(rows, baseline)
    assert result['correctness_matches'] == 2 and result['validity_matches'] == 1
    assert result['parsed_values_match'] == result['both_valid'] == 1
    assert result['raw_matches'] == 0


def test_tuning_selects_completed_work_rate_not_favorable_answers():
    slow = dict(status='complete', requests_per_second=1, quality={'correct': 100})
    fast = dict(status='complete', requests_per_second=10, quality={'correct': 99})
    oom = dict(status='out_of_memory', requests_per_second=100)
    assert choose([{'trials': [slow, oom]}, {'trials': [fast]}]) == fast
    with pytest.raises(ValueError, match='no throughput candidate'):
        choose([{'trials': [oom]}])


def test_throughput_workers_share_and_charge_the_existing_gpu_budget(tmp_path):
    from codecue.binding.budget import reserve, release
    path = tmp_path / 'budget.json'
    config = dict(device='cuda', model='fixture', model_revision='a' * 40, run_dir='profile',
                  budget_ledger=str(path), max_gpu_seconds=3600)
    lease = reserve(config, 'throughput_profile')
    assert lease['reserved_seconds'] == 0 and lease['mode'] == 'accounting_only'
    release(lease, 20, 'complete')
    assert json.loads(path.read_text())['used_seconds'] == 20


def test_timeout_keeps_successfully_completed_trials(tmp_path, monkeypatch):
    import subprocess
    import codecue.binding.throughput as module
    folder = tmp_path / 'worker'
    folder.mkdir()
    saved = {'trials': [{'status': 'complete', 'requests_per_second': 2}], 'load_seconds': 3}
    (folder / 'worker.json').write_text(json.dumps(saved))
    class Process:
        pid = 12345
        calls = 0
        def wait(self, timeout=None):
            self.calls += 1
            if self.calls == 1:raise subprocess.TimeoutExpired('fixture', timeout)
            return -15
    monkeypatch.setattr(module.subprocess, 'Popen', lambda *a, **k: Process())
    killed = []
    monkeypatch.setattr(module.os, 'killpg', lambda pid, sig: killed.append((pid, sig)))
    result = module.launch(tmp_path / 'config.json', {'backend': 'fixture'}, folder, 1)
    assert result['status'] == 'timeout' and result['trials'] == saved['trials']
    assert killed[0][0] == 12345
    assert module.choose([result]) == saved['trials'][0]


def test_worker_exit_without_full_validation_is_not_success():
    assert not validation_complete({'status': 'complete', 'trials': [{'status': 'out_of_memory'}]}, 1600)
    assert not validation_complete({'status': 'complete', 'trials': [{'status': 'complete', 'cases': 16}]}, 1600)
    assert validation_complete({'status': 'complete', 'trials': [{'status': 'complete', 'cases': 1600}]}, 1600)
