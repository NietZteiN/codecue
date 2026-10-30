import hashlib
import json
import subprocess
from types import SimpleNamespace

import pytest

from codecue.binding.datasets import write_json
from codecue.binding.experiment_status import classify, collect, inspect_stage, inspect_throughput, query_scheduler, response_progress


def test_scheduler_ignores_steps_and_keeps_failed_dependencies_visible():
    def runner(argv, **kwargs):
        if argv[0] == 'sacct':
            return SimpleNamespace(returncode=0, stderr='', stdout='1|FAILED|1:0|10\n1.batch|FAILED|1:0|10\n2|PENDING|0:0|0\n')
        return SimpleNamespace(returncode=0, stderr='', stdout='2|PENDING|DependencyNeverSatisfied\n')
    jobs, errors = query_scheduler(['1', '2'], runner)
    assert not errors and set(jobs) == {'1', '2'}
    assert jobs['2']['reason'] == 'DependencyNeverSatisfied'
    status, issues = classify(jobs, [], False)
    assert status == 'needs_attention' and len(issues) == 2


@pytest.mark.parametrize('timed_out', [('sacct',), ('squeue',), ('sacct', 'squeue')])
def test_scheduler_timeouts_preserve_other_observations_and_report_unknown(timed_out):
    from codecue.binding.experiment_status import SCHEDULER_TIMEOUT_SECONDS
    calls = []
    def runner(argv, **kwargs):
        calls.append(argv[0])
        assert kwargs['timeout'] == SCHEDULER_TIMEOUT_SECONDS
        if argv[0] in timed_out:
            raise subprocess.TimeoutExpired(argv, kwargs['timeout'])
        output = '1|RUNNING|0:0|10\n' if argv[0] == 'sacct' else '1|RUNNING|None\n'
        return SimpleNamespace(returncode=0, stderr='', stdout=output)
    jobs, errors = query_scheduler(['1'], runner)
    assert calls == ['sacct', 'squeue']
    assert len(errors) == len(timed_out)
    assert all('timed out' in error for error in errors)
    if len(timed_out) == 2:
        assert jobs == {}
    else:
        assert jobs['1']['state'] == 'RUNNING'


def test_partial_response_append_is_reported_without_repairing_file(tmp_path):
    path = tmp_path / 'responses.jsonl'
    path.write_bytes(b'{"id":"saved"}\n{"id":')
    before = path.read_bytes()
    assert response_progress(path) == {'records': 1, 'incomplete_tail': True, 'malformed_lines': []}
    assert path.read_bytes() == before
    path.write_bytes(b'{"id":"saved"}\ninvalid\n')
    assert response_progress(path)['malformed_lines'] == [2]


def stage_fixture(tmp_path, completed=True):
    path = tmp_path / 'stage'
    path.mkdir()
    data = b'{"id":"saved"}\n'
    (path / 'responses.jsonl').write_bytes(data)
    checksum = hashlib.sha256(data).hexdigest()
    write_json(path / 'manifest.json', {'status': 'complete' if completed else 'started', 'responses_sha256': checksum})
    write_json(path / 'summary.json', {'complete': completed, 'evaluated': 1, 'planned': 1 if completed else 2,
                                     'responses_sha256': checksum})
    return path


def test_active_stage_can_have_more_rows_than_last_atomic_summary(tmp_path):
    path = stage_fixture(tmp_path, completed=False)
    with (path / 'responses.jsonl').open('a') as stream:
        stream.write('{"id":"new"}\n')
    state = inspect_stage(path)
    assert state['evaluated'] == 1 and state['responses']['records'] == 2
    assert not state['issues']


def test_completed_stage_checks_coverage_and_content_hash(tmp_path):
    path = stage_fixture(tmp_path)
    assert not inspect_stage(path)['issues']
    (path / 'responses.jsonl').write_text('{"id":"tampered"}\n')
    assert inspect_stage(path)['issues'] == ['completed response checksum mismatch']
    (path / 'responses.jsonl').write_text('{"id":"one"}\n{"id":"two"}\n')
    assert 'coverage' in inspect_stage(path)['issues'][0]


def test_completed_artifacts_need_audit_before_complete_status():
    stages = [{'name': 'full', 'manifest_status': 'complete', 'issues': []}]
    assert classify({}, stages, False)[0] == 'awaiting_audit'
    assert classify({}, stages, True)[0] == 'complete'
    stages[0]['issues'] = ['corrupted']
    assert classify({}, stages, True)[0] == 'needs_attention'


def test_collector_is_read_only_and_ignores_historical_cancelled_attempts(tmp_path):
    path = stage_fixture(tmp_path)
    write_json(tmp_path / 'jobs.json', {'full': '1', 'cancelled_old': '999'})
    write_json(tmp_path / 'comparison.json', {'complete': True})
    (tmp_path / 'report.md').write_text('already audited')
    write_json(tmp_path / 'budget.json', {'cap_seconds': 100, 'used_seconds': 10, 'active': {}})
    config = dict(jobs=str(tmp_path / 'jobs.json'), job_keys=['full'],
                  stages=[dict(name='full', path=str(path))], comparison_artifact=str(tmp_path / 'comparison.json'),
                  completed_report=str(tmp_path / 'report.md'), budget_ledger=str(tmp_path / 'budget.json'))
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    def runner(argv, **kwargs):
        assert '999' not in ','.join(argv)
        return SimpleNamespace(returncode=0, stderr='', stdout='1|COMPLETED|0:0|10\n' if argv[0] == 'sacct' else '')
    result = collect(config, runner)
    assert result['status'] == 'complete'
    assert result['budget']['unreserved_seconds'] == 90
    assert result['model_inference'] is False
    assert {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()} == before


def test_scheduler_unavailable_does_not_pretend_live_run_is_confirmed(tmp_path):
    path = stage_fixture(tmp_path, completed=False)
    write_json(tmp_path / 'jobs.json', {'full': '1'})
    config = dict(jobs=str(tmp_path / 'jobs.json'), job_keys=['full'], stages=[dict(name='full', path=str(path))],
                  comparison_artifact=str(tmp_path / 'absent.json'), completed_report=str(tmp_path / 'absent.md'),
                  budget_ledger=str(tmp_path / 'absent_budget.json'))
    def runner(argv, **kwargs):
        raise FileNotFoundError(argv[0])
    result = collect(config, runner)
    assert result['status'] == 'unconfirmed_running_state'
    assert len(result['scheduler_errors']) == 2


def test_throughput_status_keeps_partial_trials_without_pretending_validation_completed(tmp_path, monkeypatch):
    import codecue.binding.published_benchmarks as benchmarks
    monkeypatch.setattr(benchmarks, 'plan', lambda _: [('task', {})] * 1600)
    write_json(tmp_path / 'manifest.json', {'status': 'started', 'identity': {'config': {}}})
    write_json(tmp_path / 'worker_0/worker.json', {'trials': [
        {'status': 'complete', 'requests_per_second': 10}, {'status': 'out_of_memory'}],
        'inline_candidates': [{'status': 'complete', 'requests_per_second': 20}]})
    status = inspect_throughput(tmp_path)
    assert status['completed_profile_trials'] == status['completed_validation_candidates'] == 1
    assert status['best_profile_requests_per_second'] == 10 and status['evaluated'] == 0
    assert status['planned'] == 1600 and not status['issues']
    write_json(tmp_path / 'manifest.json', {'status': 'complete', 'identity': {'config': {}}})
    assert 'lacks complete' in inspect_throughput(tmp_path)['issues'][0]
    write_json(tmp_path / 'summary.json', {'complete': True, 'validation': {'status': 'complete',
        'trials': [{'status': 'complete', 'cases': 1600, 'requests_per_second': 30}]}})
    status = inspect_throughput(tmp_path)
    assert not status['issues'] and status['evaluated'] == 1600 and status['validation_requests_per_second'] == 30
