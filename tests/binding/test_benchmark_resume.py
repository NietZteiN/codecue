import hashlib
import json
import sys
from types import SimpleNamespace

import pytest

from codecue.binding.datasets import digest, write_json
from codecue.binding.published_benchmarks import aggregate, completed_summary, score, sha, WRAPPERS


def test_completed_registration_is_read_only_even_after_gpu_cap_is_spent(tmp_path, monkeypatch):
    import codecue.binding.registry as registry
    monkeypatch.setitem(sys.modules, 'torch', SimpleNamespace(__version__='fixture'))
    monkeypatch.setitem(sys.modules, 'transformers', SimpleNamespace(__version__='fixture'))
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': 'fixture'})
    monkeypatch.setattr(registry, 'ROOT', tmp_path)
    dataset = tmp_path / 'data.jsonl'
    dataset.write_text('{}\n')
    write_json(dataset.with_suffix('.manifest.json'), {'sha256': hashlib.sha256(dataset.read_bytes()).hexdigest()})
    ledger = tmp_path / 'budget.json'
    cfg = dict(dataset=str(dataset), run_dir=str(tmp_path / 'run'), model='fixture',
               model_revision='a' * 40, tokenizer_revision='a' * 40, device='cuda',
               max_gpu_seconds=100, budget_ledger=str(ledger))
    out, manifest = registry.begin(cfg, 'published_behavior')
    registry.finish(out, manifest, 2.)
    budget = json.loads(ledger.read_text())
    budget['cap_seconds'] = budget['used_seconds'] = 2
    write_json(ledger, budget)
    original = (out / 'manifest.json').read_bytes(), ledger.read_bytes()
    same_out, same_manifest = registry.begin(cfg, 'published_behavior', reuse_complete=True)
    assert same_out == out and same_manifest['status'] == 'complete'
    assert len(same_manifest['attempts']) == 1
    assert ((out / 'manifest.json').read_bytes(), ledger.read_bytes()) == original
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': 'different'})
    with pytest.raises(ValueError, match='resume identity differs'):
        registry.begin(cfg, 'published_behavior', reuse_complete=True)
    assert (out / 'manifest.json').read_bytes() == original[0]


def completed_fixture(tmp_path):
    task = 'bbh_tracking_3'
    row = {'id': 'fixture', 'target': '(A)'}
    results = [{'id': row['id'], 'task': task, 'raw_response': '(A)',
                'score': score(task, row, '(A)'), 'stop_reason': 'eos'}]
    path = tmp_path / 'responses.jsonl'
    path.write_text(json.dumps(results[0]) + '\n')
    summary = {**aggregate(results, [(task, row)]), 'responses_sha256': sha(path),
               'gpu_peak_bytes': 1234, 'extra_metadata': {'preserved': True}}
    write_json(tmp_path / 'summary.json', summary)
    manifest = {'status': 'complete', 'responses_sha256': sha(path)}
    return manifest, results, [(task, row)], summary


def test_completed_summary_reuse_preserves_all_resource_and_custom_metadata(tmp_path):
    manifest, rows, planned, original = completed_fixture(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert completed_summary(tmp_path, manifest, rows, planned, WRAPPERS[0]) == original
    assert completed_summary(tmp_path, manifest, rows, planned, WRAPPERS[0]) == original
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
    with pytest.raises(ValueError, match='coverage mismatch'):
        completed_summary(tmp_path, manifest, [], planned, WRAPPERS[0])


def test_completed_summary_refuses_corrupt_or_missing_metadata(tmp_path):
    manifest, rows, planned, original = completed_fixture(tmp_path)
    corrupted = {k: v for k, v in original.items() if k != 'gpu_peak_bytes'}
    write_json(tmp_path / 'summary.json', corrupted)
    with pytest.raises(ValueError, match='metadata mismatch'):
        completed_summary(tmp_path, manifest, rows, planned, WRAPPERS[0])
    assert json.loads((tmp_path / 'summary.json').read_text()) == corrupted
    write_json(tmp_path / 'summary.json', original)
    (tmp_path / 'responses.jsonl').write_text('changed\n')
    with pytest.raises(ValueError, match='checksum or metadata mismatch'):
        completed_summary(tmp_path, manifest, rows, planned, WRAPPERS[0])


def test_last_batch_recovery_finishes_without_loading_a_model(tmp_path, monkeypatch):
    import codecue.binding.published_benchmarks as published
    import codecue.binding.registry as registry
    import codecue.binding.model_adapter as adapter
    monkeypatch.setitem(sys.modules, 'torch', SimpleNamespace())
    out = tmp_path / 'run' / 'published_behavior'
    out.mkdir(parents=True)
    task = 'bbh_tracking_3'
    row = {'id': 'fixture', 'target': '(A)'}
    result = dict(id=row['id'], task=task, record_sha256=digest(row), raw_response='(A)',
                  score=score(task, row, '(A)'), stop_reason='eos')
    (out / 'responses.jsonl').write_text(json.dumps(result) + '\n')
    cfg = dict(run_dir=str(out.parent), prompt_wrapper=WRAPPERS[0], model='fixture',
               model_revision='a' * 40, report=str(tmp_path / 'report.md'),
               preflight_result=str(tmp_path / 'qa.json'))
    write_json(cfg['preflight_result'], dict(status='passed', config_hash=digest(cfg), source_sha256='source'))
    monkeypatch.setattr(published, 'assets', lambda c: None)
    monkeypatch.setattr(published, 'plan', lambda c: [(task, row)])
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': 'source'})
    monkeypatch.setattr(registry, 'begin', lambda *a, **k: (out, {'status': 'started'}))
    finished = []
    monkeypatch.setattr(registry, 'finish', lambda *a, **k: finished.append(k))
    def must_not_load(config):
        raise AssertionError('recovery must not query a model')
    monkeypatch.setattr(adapter, 'load', must_not_load)
    summary = published.run(cfg)
    assert summary['complete'] and summary['recovered_without_inference']
    assert summary['gpu_peak_bytes'] is None
    assert finished[0]['responses_sha256'] == sha(out / 'responses.jsonl')


def test_recovered_audit_reports_missing_peak_memory_without_inventing_it():
    from codecue.binding.published_review import report
    result = dict(summary={'evaluated': 1, 'tasks': []}, checkpoint={'model': 'fixture', 'model_revision': 'a'},
                  prompt_wrapper=WRAPPERS[0], diagnostics={'tasks': [], 'cruxeval_paired_correctness': None},
                  resources={'stage_seconds': 1, 'gpu_peak_bytes': None}, run_identity_hash='fixture',
                  prompt_token_ids_sha256='fixture', responses_path='fixture', audit_path='fixture')
    assert 'not recorded (recovered run)' in report(result)
