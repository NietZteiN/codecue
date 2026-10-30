import json
from types import SimpleNamespace

import pytest

from codecue.binding.published_benchmarks import (
    SCORER, aggregate, checked_manifest, content_for, crux_answer, immutable,
    score, sha, upstream_literal_score,
)


@pytest.mark.parametrize('value', ['True', '1', '1.5', 'None', "b'hi'", "'hello'",
                                  '[1, (2, 3)]', '{1: None, 2: False}', '(1,)',
                                  "'a==b'", "'[ANSWER]'", "'[/ANSWER]'"])
def test_crux_python_literals_and_assertions(value):
    row = {'input': '(1, ), (2, )', 'output': value}
    for text in (value, f'assert f({row["input"]}) == {value}',
                 f'[ANSWER]\nassert f({row["input"]}) == {value}\n[/ANSWER]'):
        result = score('cruxeval_o_direct', row, text)
        assert result['valid'] and result['correct']


def test_crux_cot_uses_answer_and_known_input():
    row = {'input': '2', 'output': '5'}
    assert score('cruxeval_o_cot', row,
                 'First consider 3.\n[ANSWER]\nassert f(2) == 5\n[/ANSWER]')['correct']
    for text in ('5', 'assert f(2) == 5', '[ANSWER]assert f(3) == 5[/ANSWER]'):
        assert not score('cruxeval_o_cot', row, text)['valid']


def test_crux_direct_extracts_explicit_answer_after_echoed_program():
    row = {'input': '2', 'output': '5'}
    text = '[PYTHON]\ndef f(x): return x+3\nassert f(2) == 5\n[/PYTHON]\n[ANSWER]\nassert f(2) == 5\n[/ANSWER]'
    assert score('cruxeval_o_direct', row, text)['correct']
    assert not upstream_literal_score(text, row)


@pytest.mark.parametrize('bad', ['f(2)', '2+3', '__import__("os").system("echo unsafe")',
                               'assert f(3) == 5', 'assert f(2) == 5; x=1',
                               'assert f(2) == 5 == 5', 'assert f(2) == 5, "message"',
                               'Here is 5', ''])
def test_crux_rejects_expressions_calls_and_malformed_assertions(bad):
    result = score('cruxeval_o_direct', {'input': '2', 'output': '5'}, bad)
    assert not result['valid'] and not result['correct']


def test_crux_python_equality_and_disclosed_upstream_edge_case():
    # The upstream evaluator uses Python == rather than type-strict equality.
    assert score('cruxeval_o_direct', {'input': '2', 'output': 'True'}, '1')['correct']
    row = {'input': '2', 'output': "'a==b'"}
    text = "assert f(2) == 'a==b'"
    assert crux_answer(text, row) == 'a==b'
    assert not upstream_literal_score(text, row)


def test_invalid_literal_error_text_is_deterministic_for_resume():
    row = {'input': '2', 'output': '5'}
    scores = [score('cruxeval_o_direct', row, 'abs(5)') for _ in range(3)]
    assert scores[0] == scores[1] == scores[2]
    assert 'object at 0x' not in scores[0]['parse_error']
    assert '<address>' in scores[0]['parse_error']


@pytest.mark.parametrize('text', ['(B)', 'So the answer is (B).', 'Answer: (B)',
                                 'Explain (A).\nTherefore, the answer is (B).'])
def test_bbh_final_answer(text):
    result = score('bbh_tracking_3', {'target': '(B)'}, text)
    assert result['valid'] and result['correct']


@pytest.mark.parametrize('text', ['I saw (B) in the options.', 'The answer is (G).',
                                 'B', '(B) and (C)', 'The answer is (B). More explanation.'])
def test_bbh_rejects_ambiguous_nonfinal_and_out_of_range(text):
    assert not score('bbh_tracking_3', {'target': '(B)'}, text)['valid']


def test_bbh_stops_before_next_question():
    assert score('bbh_tracking_3', {'target': '(B)'},
                 'The answer is (B).\n\nQ: extra')['correct']


def test_content_uses_no_target_and_preserves_author_prompt():
    prompts = SimpleNamespace(make_direct_output_prompt=lambda x: repr(x),
                              make_cot_output_prompt=lambda x: 'cot' + repr(x))
    sources = prompts, {3: 'released three demonstrations'}
    row = {'code': 'def f(x): return x', 'input': '1', 'output': 'SECRET_REFERENCE'}
    assert 'SECRET_REFERENCE' not in content_for('cruxeval_o_direct', row, sources)
    assert 'SECRET_REFERENCE' not in content_for('cruxeval_o_cot', row, sources)
    assert content_for('bbh_tracking_3', {'input': 'question', 'target': 'SECRET'}, sources) == (
        "released three demonstrations\n\nQ: question\nA: Let's think step by step.")


def test_public_artifacts_are_immutable_and_sources_are_checked(tmp_path):
    path = tmp_path / 'source.txt'
    immutable(path, b'original')
    immutable(path, b'original')
    with pytest.raises(ValueError, match='already differs'):
        immutable(path, b'changed')
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'files': [{'path': str(path), 'sha256': sha(path)}]}))
    checked_manifest(manifest, sha(manifest))
    path.write_text('tampered')
    with pytest.raises(ValueError, match='source checksum mismatch'):
        checked_manifest(manifest)


def test_incomplete_coverage_never_reports_full_benchmark_accuracy():
    task = 'bbh_tracking_3'
    row = {'task': task, 'score': {'valid': True, 'correct': True}, 'stop_reason': 'eos'}
    result = aggregate([row], [(task, {}), (task, {})])
    assert not result['complete']
    assert result['tasks'][0]['accuracy'] is None
    assert result['tasks'][0]['evaluated_accuracy'] == 1
    result = aggregate([row, {**row, 'score': {'valid': False, 'correct': False}}],
                       [(task, {}), (task, {})])
    assert result['complete'] and result['tasks'][0]['accuracy'] == .5


def test_published_gpu_stage_charges_shared_ledger(tmp_path):
    from codecue.binding.budget import reserve, release
    config = dict(device='cuda', model='cached', model_revision='a' * 40,
                  run_dir='published', max_gpu_seconds=100, budget_ledger=str(tmp_path / 'budget.json'))
    lease = reserve(config, 'published_behavior')
    assert lease['reserved_seconds'] == 0
    release(lease, 12, 'complete')
    assert json.loads((tmp_path / 'budget.json').read_text())['used_seconds'] == 12


def test_smoke_correction_checks_provenance_and_preserves_original_scores(tmp_path, monkeypatch):
    import codecue.binding.published_benchmarks as published
    from codecue.binding.datasets import digest
    stage = tmp_path / 'old_smoke'
    stage.mkdir()
    row = {'id': 'cruxeval/sample_1', 'input': '2', 'output': '5'}
    response = {'id': row['id'], 'task': 'cruxeval_o_direct', 'record_sha256': digest(row),
                'raw_response': '[PYTHON]echo[/PYTHON]\n[ANSWER]\nassert f(2) == 5\n[/ANSWER]',
                'stop_reason': 'answer_end_marker',
                'score': {'scorer': 'old', 'valid': False, 'correct': False}}
    responses = stage / 'responses.jsonl'
    responses.write_text(json.dumps(response) + '\n')
    manifest = {'status': 'complete', 'identity_hash': 'original', 'responses_sha256': sha(responses),
                'identity': {'config': {}, 'code': {'source_sha256': 'old_code'}}}
    (stage / 'manifest.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(published, 'assets', lambda c: None)
    monkeypatch.setattr(published, 'plan', lambda c: [('cruxeval_o_direct', row)])
    import codecue.binding.registry as registry
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': 'new_code'})
    config = dict(smoke_stage=str(stage), smoke_identity_hash='original',
                  responses_sha256=sha(responses), output=str(tmp_path / 'corrected.json'))
    result = published.rescore_smoke(config)
    corrected = json.loads((tmp_path / 'corrected.json').read_text())
    assert result['model_inference'] is False
    assert corrected['responses'][0]['original_score']['valid'] is False
    assert corrected['responses'][0]['score']['correct'] is True
    assert json.loads(responses.read_text()) == response
    responses.write_text(responses.read_text() + '\n')
    with pytest.raises(ValueError, match='provenance mismatch'):
        published.rescore_smoke(config)
