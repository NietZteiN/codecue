from copy import deepcopy

import pytest

from codecue.binding.checkpoint_suite import score_case, summarize, validate_response, generated_rows, engine_settings
from codecue.binding.datasets import digest, write_json
from codecue.binding.published_benchmarks import sha


def fixture():
    case = dict(kind='published', section='released', task='cruxeval_o_direct', id='a',
                record=dict(id='a', input='2', output='3'), input_token_ids=[1, 2],
                prompt_sha256='prompt', max_new_tokens=10)
    row = {k: case[k] for k in ('section', 'task', 'id', 'input_token_ids', 'prompt_sha256')}
    row.update(record_sha256=digest(case['record']), raw_response='assert f(2) == 3',
               output_token_ids=[4, 5], score=score_case(case, 'assert f(2) == 3'))
    return case, row


@pytest.mark.parametrize('change', ['prompt', 'record', 'score', 'ceiling'])
def test_response_validation_rejects_wrong_question_prompt_score_and_ceiling(change):
    case, row = fixture()
    validate_response(case, row)
    if change == 'prompt':row['input_token_ids'] = [9]
    elif change == 'record':row['record_sha256'] = 'wrong'
    elif change == 'score':row['score']['correct'] = False
    else:case['max_new_tokens'] = 1
    with pytest.raises(ValueError, match='identity, token ceiling or score'):
        validate_response(case, row)


def test_native_calibration_scores_final_answer_without_reopening_old_gates():
    case = dict(kind='diagnostic', variant='print_trace_long_v1', record=dict(expected_answer=7))
    assert score_case(case, 'x is 7\nAnswer: 7')['correct']
    assert not score_case(case, 'Answer: 7\nmore explanation')['valid']
    _, row = fixture()
    summary = summarize([row], 2)
    assert not summary['complete'] and summary['cells'][0]['correct'] == 1
    assert summary['generated_holdouts_opened'] is False


def test_generated_sources_require_registered_calibration_role_and_content_hash(tmp_path):
    path = tmp_path / 'rows.jsonl'
    path.write_text('{}\n')
    write_json(path.with_suffix('.manifest.json'), dict(sha256=sha(path), evaluation_role='final_test'))
    spec = dict(kind='counterbalanced', dataset=str(path), sha256=sha(path))
    with pytest.raises(ValueError, match='only registered discovery'):
        generated_rows(spec)
    spec['sha256'] = 'wrong'
    with pytest.raises(ValueError, match='checksum'):
        generated_rows(spec)


def test_engine_scales_batching_to_available_hardware_and_accepts_model_parallelism():
    cfg = dict(tensor_parallel_size=2, engine=dict(max_num_seqs='auto', max_num_batched_tokens='auto'))
    small = engine_settings(cfg, 24 * 2**30)
    large = engine_settings(cfg, 140 * 2**30)
    assert small['max_num_seqs'] == 256 and large['max_num_seqs'] == 512
    assert large['max_num_batched_tokens'] == 16384 and large['tensor_parallel_size'] == 2
    assert cfg['engine']['max_num_seqs'] == 'auto'


def test_large_checkpoint_hardware_override_keeps_h100_eligible_without_changing_h200():
    cfg = dict(engine=dict(max_num_seqs=512, max_num_batched_tokens=16384), engine_memory_overrides=[
        dict(max_memory_gib=100, settings=dict(max_num_seqs=128, max_num_batched_tokens=4096))])
    small = engine_settings(cfg, 80*2**30)
    large = engine_settings(cfg, 140*2**30)
    assert small['max_num_seqs'] == 128 and small['max_num_batched_tokens'] == 4096
    assert large['max_num_seqs'] == 512 and large['max_num_batched_tokens'] == 16384
