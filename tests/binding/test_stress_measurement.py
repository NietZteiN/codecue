"""Task preservation, label-free schemas, bounded guards and request resume."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import json

import pytest

from codecue.binding import stress_measurement as study


class Tokenizer:
    binding_official_boundary = False
    def __init__(self, style='llama'): self.style = style
    def apply_chat_template(self, messages, **kwargs):
        assert kwargs == {'tokenize': False, 'continue_final_message': True}
        assert messages[-1] == {'role': 'assistant', 'content': 'Output:\n'}
        suffix = '<END><ASSISTANT>Output:' if self.style == 'llama' else ' [/INST] Output:\n'
        return '<BOS><USER>'+messages[0]['content']+suffix
    def __call__(self, prompt, **kwargs):
        assert kwargs == {'add_special_tokens': False}
        return {'input_ids': [ord(c)+5 for c in prompt]}


def source_case(index=0, style='llama'):
    from codecue.binding.calibration import prompt
    from codecue.binding.competition import ROLE
    tokenizer = Tokenizer(style)
    row = dict(id=f'case{index}', base_id=f'base{index}', template_id=f'template{index//2}',
        split='train' if index < 2 else 'development', condition='informative' if index%2 == 0 else 'misleading',
        lexical_realization=0, available_bindings=2, updates=1, tail_placement='before', query_role='saved',
        source='a = 1\nsaved = a\na = 2\nsaved', family='versions', evaluation_role=ROLE,
        expected_answer=1, correctness=True, raw_response='OLD OUTCOME MUST NOT BE EXPORTED')
    rendered, _ = prompt(tokenizer, row, 'print_direct_v3')
    case = {'id': row['id'], 'kind': 'competition', 'record': row, 'prompt': rendered,
        'input_token_ids': tokenizer(rendered, add_special_tokens=False)['input_ids'],
        'prompt_sha256': study.digest(rendered), 'score': {'correct': True}}
    return tokenizer, case


def minimal_config(tmp_path):
    return {'evaluation_role': study.ROLE, 'transform': study.TRANSFORM, 'max_new_tokens': 32,
        'execution_backend': study.BACKEND_DESCRIPTION, 'device': 'cuda', 'dtype': 'bfloat16',
        'model': 'synthetic/model', 'model_revision': 'a'*40, 'tokenizer_revision': 'a'*40,
        'eos_token_ids': [2], 'protocol': 'short_answer_chat_v1', 'tokenization_mode': 'native',
        'dataset': str(tmp_path/'dataset.jsonl'), 'source_config': str(tmp_path/'source.json'),
        'source_config_sha256': 'b'*64, 'runtime_manifest': str(tmp_path/'runtime_source.json'),
        'runtime_manifest_sha256': 'c'*64, 'cuda_home': '/usr/local/cuda', 'engine': {},
        'context_limit': 4096, 'request_chunk_size': 2,
        'prepared_cases': str(tmp_path/'prepared.jsonl'), 'preflight_result': str(tmp_path/'preparation.json'),
        'run_dir': str(tmp_path/'run')}


def execution():
    return {'backend': 'vllm', 'actual_model_dtype': 'bfloat16', 'actual_model_dtype_verified': True,
        'device_name': 'Synthetic GPU', 'engine': {'tensor_parallel_size': 1}, 'versions': dict.fromkeys(('torch', 'transformers', 'vllm'), 'test'),
        'slurm_job_id': 'synthetic', 'max_new_tokens': 32, 'greedy_seed': 0, 'temperature': 0, 'top_p': 1,
        'stop': ['\n\n'], 'eos_token_ids': [2], 'prefix_caching': True, 'chunked_prefill': True,
        'device_total_memory_bytes': 64*2**30, 'generation_config': 'vllm'}


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value)); return path


def bundle(tmp_path, monkeypatch):
    config = minimal_config(tmp_path); provenance = {'source_identity_hash': 'source'}
    monkeypatch.setattr(study, 'SOURCE_CASES', 4)
    monkeypatch.setattr(study, '_metadata', lambda c: ({}, provenance))
    monkeypatch.setattr(study, 'code_identity', lambda: {'source_sha256': 's'*64})
    cases = [study.transform_case(*source_case(i)) for i in range(4)]
    prepared = Path(config['prepared_cases']); prepared.write_text(''.join(json.dumps(c)+'\n' for c in cases))
    qa = {'status': 'passed', 'evaluation_role': study.ROLE, 'measurement': study.MEASUREMENT,
        'config_hash': study.digest(config), 'source_sha256': 's'*64, 'source_config_sha256': config['source_config_sha256'],
        'source_provenance': provenance, 'prepared_cases_sha256': study.sha(prepared),
        'case_ids_sha256': study.digest([c['id'] for c in cases]), 'cases': 4,
        **{k: config[k] for k in ('model', 'model_revision', 'tokenizer_revision', 'eos_token_ids')},
        'smoke_subset': False, 'transform': study.TRANSFORM, 'cue': study.CUE,
        'original_prompt_replay_verified': True, 'code_and_query_unchanged': True, 'assistant_boundary_unchanged': True,
        'target_outcomes_read': False, 'oracle_fields_exported': False, 'generated_holdouts_opened': False,
        'nominal_distinct_queries_per_target': 1, 'max_new_tokens': 32, 'generated_tokens': 0,
        'conditions': {'informative': 2, 'misleading': 2}, 'original_splits': {'train': 2, 'development': 2},
        'boundary_suffixes': {cases[0]['assistant_boundary_suffix']: 4}}
    write(config['preflight_result'], qa)
    outputs = [SimpleNamespace(prompt_token_ids=c['input_token_ids'], outputs=[SimpleNamespace(
        text='-2', token_ids=[101, 2], finish_reason='stop', stop_reason=None)]) for c in cases]
    rows = study.response_rows(cases, outputs, config)
    out = Path(config['run_dir'])/'stress_measurement'; out.mkdir(parents=True, exist_ok=True)
    for start in range(0, 4, 2):
        rid = f'{start+1:032x}'; part = rows[start:start+2]
        request = {'request_id': rid, 'state': 'started', 'config_hash': study.digest(config),
            'start': start, 'cases': 2, 'case_ids_sha256': study.digest([r['id'] for r in part]), 'execution': execution()}
        write(out/'requests'/f'{rid}_started.json', request)
        write(out/'requests'/f'{rid}_completed.json', {**request, 'state': 'completed', 'generated_tokens': 4})
        write(out/'chunks'/f'{start:08d}.json', {'config_hash': study.digest(config), 'prepared_cases_sha256': qa['prepared_cases_sha256'],
            'measurement': study.MEASUREMENT, 'start': start, 'request_id': rid, 'execution': execution(), 'rows': part})
    for name, values in [('responses', rows), ('scalars', study.scalar_rows(rows))]:
        (out/(name+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in values))
    counts = study._request_counts(out, config)
    runtime = {'status': 'recorded', 'backend': 'vllm', 'dtype': 'bfloat16', 'eos_token_ids': [2],
        'max_new_tokens': 32, 'greedy_seed': 0, 'temperature': 0, 'top_p': 1, 'prefix_caching': True,
        'chunked_prefill': True, 'stop': ['\n\n'], 'executions': [execution()], **counts}
    write(out/'runtime.json', runtime)
    summary = {'status': 'complete', 'complete': True, 'measurement': study.MEASUREMENT, 'evaluation_role': study.ROLE,
        'evaluated': 4, 'planned': 4, 'source_provenance': provenance, 'prepared_cases_sha256': qa['prepared_cases_sha256'],
        'case_ids_sha256': qa['case_ids_sha256'], 'nominal_distinct_queries_per_target': 1, 'max_new_tokens': 32,
        'transform': study.TRANSFORM, 'cue': study.CUE, 'smoke_subset': False,
        'model': config['model'], 'model_revision': config['model_revision'], 'target_outcomes_read': False,
        'oracle_fields_exported': False, 'generated_holdouts_opened': False, 'generated_tokens': 8, 'valid': 4,
        'scalars_sha256': study.sha(out/'scalars.jsonl'), 'responses_sha256': study.sha(out/'responses.jsonl'),
        'runtime_sha256': study.sha(out/'runtime.json'), **counts}
    write(out/'summary.json', summary)
    identity = {'config': config, 'code': {'source_sha256': 's'*64}}
    write(out/'manifest.json', {'status': 'complete', 'identity': identity, 'identity_hash': study.digest(identity),
        'scalars_sha256': summary['scalars_sha256'], 'responses_sha256': summary['responses_sha256']})
    return config, qa, cases, rows, out


@pytest.mark.parametrize('style,suffix', [('llama', '<END><ASSISTANT>Output:'), ('code', ' [/INST] Output:\n')])
def test_transform_preserves_exact_program_query_original_ids_and_checkpoint_suffix(style, suffix):
    tokenizer, case = source_case(style=style)
    result = study.transform_case(tokenizer, case)
    assert result['assistant_boundary_suffix'] == suffix
    assert result['original_input_token_ids'] == case['input_token_ids']
    assert result['original_prompt'] == case['prompt']
    assert result['prompt'].count(study.CUE) == 1
    assert 'print(saved)' in result['source_printed']
    assert result['prompt'].replace(study.INSTRUCTION+'\n'+study.CUE, study.INSTRUCTION) == case['prompt']
    assert result['input_token_ids'] != case['input_token_ids']
    assert set(result) == study.PREPARED_FIELDS
    assert not ({'expected_answer', 'correct', 'correctness', 'score', 'raw_response'} & set(result))


@pytest.mark.parametrize('mutation', ['prompt', 'tokens', 'hash'])
def test_changed_original_prompt_or_ids_rejected_before_transformation(mutation):
    tokenizer, case = source_case()
    if mutation == 'prompt': case['prompt'] += ' '
    elif mutation == 'tokens': case['input_token_ids'][0] += 1
    else: case['prompt_sha256'] = 'bad'
    with pytest.raises(ValueError, match='parent prompt'):
        study.transform_case(tokenizer, case)


def test_prepared_schema_rejects_gold_and_boundary_or_code_changes():
    tokenizer, case = source_case(); item = study.transform_case(tokenizer, case)
    for key, value in [('expected_answer', 1), ('assistant_boundary_suffix', 'Answer:'), ('source_printed', 'print(0)')]:
        changed = {**item, key: value}
        with pytest.raises(ValueError): study.validate_prepared(changed)


def test_balanced_hash_selection_is_order_invariant_and_has_no_correctness_selection(monkeypatch):
    monkeypatch.setattr(study, 'SOURCE_CASES', 8)
    cases = []
    for i in range(8):
        _, c = source_case(i%4); c['id'] = c['record']['id'] = f'case{i}'
        c['record']['split'] = 'train' if i%4 < 2 else 'development'; cases.append(c)
    selected = study.select_cases(cases, {'case_limit': 4, 'selection_seed': 117})
    again = study.select_cases(list(reversed(cases)), {'case_limit': 4, 'selection_seed': 117})
    assert [c['id'] for c in selected] == [c['id'] for c in again]
    assert len({(c['record']['split'], c['record']['condition']) for c in selected}) == 4
    cases[0]['record']['split'] = 'final'
    with pytest.raises(ValueError, match='discovery'): study.select_cases(cases, {})


@pytest.mark.parametrize('field,value', [('evaluation_role', 'final'), ('max_new_tokens', 16), ('transform', 'other'),
    ('cue', 'Ignore names'), ('device', 'cpu'), ('dtype', 'float32'), ('case_limit', 7), ('request_chunk_size', 0),
    ('execution_backend', 'transformers eager'), ('engine', {'model': 'other'})])
def test_metadata_guards_precede_any_source_or_payload_read(tmp_path, monkeypatch, field, value):
    config = minimal_config(tmp_path); config[field] = value
    monkeypatch.setattr(study, '_json', lambda *a, **k: pytest.fail('guard must precede metadata content reads'))
    with pytest.raises(ValueError): study.metadata_preflight(config)


def test_real_loading_requires_scheduled_worker_and_forces_cache_only(monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID', raising=False)
    with pytest.raises(RuntimeError, match='sbatch'): study._scheduled()
    monkeypatch.setenv('SLURM_JOB_ID', 'synthetic'); study._scheduled()
    assert study.os.environ['HF_HUB_OFFLINE'] == '1' and study.os.environ['TRANSFORMERS_OFFLINE'] == '1'


@pytest.mark.parametrize('raw,tokens,expected', [('-16', [2], (1, -16)), (' +2\n', [3, 2], (1, 2)),
    ('Answer: 2', [3], (0, 0)), ('1 and 2', [], (0, 0)), ('', [2], (0, 0))])
def test_scalar_parser_has_no_oracle_access(raw, tokens, expected):
    values = study.scalars(raw, tokens)
    assert values['valid'] == expected[0] and values['prediction_value'] == expected[1]
    assert values['prediction_abs'] == abs(expected[1]) and values['response_chars'] == len(raw)
    assert values['output_tokens'] == len(tokens) and set(values) == set(study.SCALARS)


def test_invalid_output_token_domains_and_scalar_schema_are_rejected():
    for tokens in ([1]*33, [-1], [True], '1'):
        with pytest.raises(ValueError): study.scalars('1', tokens)
    tokenizer, source = source_case(); case = study.transform_case(tokenizer, source)
    row = {k: case[k] for k in (*study.CASE_FIELDS, *study.HASH_FIELDS)}
    row.update(measurement_role=study.ROLE, **study.scalars('1', [2]))
    study.validate_rows([case], [row])
    for key, value in [('correct', True), ('valid', True), ('prediction_abs', -1), ('original_prompt_sha256', 'bad')]:
        with pytest.raises(ValueError): study.validate_rows([case], [{**row, key: value}])


@pytest.mark.parametrize('finish,reason,tokens,raw,passes', [
    ('length', None, [1]*32, '1', True), ('length', None, [1], '1', False),
    ('stop', None, [1, 2], '1', True), ('stop', None, [1], '1', False),
    ('stop', 2, [1, 2], '1', True), ('stop', 99, [1, 99], '1', False),
    ('stop', '\n\n', [1], '1\n\n', True), ('stop', 'other', [1], '1other', False)])
def test_generation_stop_contract_is_audited(finish, reason, tokens, raw, passes):
    row = {'finish_reason': finish, 'stop_reason': reason, 'output_token_ids': tokens, 'raw_response': raw}
    if passes: study._validate_stop(row, [2])
    else:
        with pytest.raises(ValueError): study._validate_stop(row, [2])


def test_complete_bundle_audit_and_metadata_guard_do_not_score_correctness(tmp_path, monkeypatch):
    config, qa, cases, rows, out = bundle(tmp_path, monkeypatch)
    result = study.audit(config)
    assert result['status'] == 'passed' and result['evaluated'] == 4
    assert result['case_request_attempts'] == 4
    assert study.completed_metadata(config)['preparation'] == qa
    assert study.inputs(config)[1] == cases
    assert all('correct' not in r for r in study.scalar_rows(rows))


def test_completed_metadata_never_reads_prepared_or_response_payloads(tmp_path, monkeypatch):
    config, _, _, _, _ = bundle(tmp_path, monkeypatch); study.audit(config)
    monkeypatch.setattr(study, 'read_jsonl', lambda *a: pytest.fail('metadata-only stage opened bulk payload'))
    old = study.sha
    def no_bulk(path):
        if Path(path).suffix == '.jsonl': pytest.fail('metadata-only stage hashed bulk payload')
        return old(path)
    monkeypatch.setattr(study, 'sha', no_bulk)
    assert study.completed_metadata(config)['summary']['complete']


def test_changed_final_scalar_and_missing_request_start_fail_audit(tmp_path, monkeypatch):
    config, _, _, _, out = bundle(tmp_path, monkeypatch)
    (out/'scalars.jsonl').write_text('{}\n')
    with pytest.raises(ValueError, match='checksum'): study.audit(config)
    config, _, _, _, out = bundle(tmp_path, monkeypatch)
    next((out/'requests').glob('*_started.json')).unlink()
    with pytest.raises(ValueError, match='started record'): study.audit(config)


def test_committed_chunk_without_completion_record_is_reused_without_requery(tmp_path, monkeypatch):
    config, qa, cases, rows, out = bundle(tmp_path, monkeypatch)
    next((out/'requests').glob('*_completed.json')).unlink()
    got, pending = study._chunks(config, qa, cases, out)
    counts = study._request_counts(out, config)
    assert got == rows and pending == []
    assert counts['case_request_attempts'] == counts['completed_case_request_attempts'] == 4
    assert counts['completion_observed_from_chunk_only'] == 1
    assert counts['incomplete_request_attempts'] == 0


def test_uncommitted_failed_attempts_are_counted_separately(tmp_path, monkeypatch):
    config, _, _, _, out = bundle(tmp_path, monkeypatch)
    start = json.loads(next((out/'requests').glob('*_started.json')).read_text())
    start['request_id'] = 'f'*32
    write(out/'requests'/('f'*32+'_started.json'), start)
    counts = study._request_counts(out, config)
    assert counts['case_request_attempts'] == 6 and counts['completed_case_request_attempts'] == 4
    assert counts['uncommitted_case_request_attempts'] == 2 and counts['incomplete_request_attempts'] == 1


@pytest.mark.parametrize('mutation', ['zero', 'negative', 'wrong_ids', 'missing_chunk_start'])
def test_request_counts_and_chunk_bindings_are_strict(tmp_path, monkeypatch, mutation):
    config, _, _, _, out = bundle(tmp_path, monkeypatch)
    path = next((out/'requests').glob('*_started.json')); data = json.loads(path.read_text())
    if mutation == 'zero': data['cases'] = 0
    elif mutation == 'negative': data['start'] = -2
    elif mutation == 'wrong_ids': data['case_ids_sha256'] = 'x'*64
    else:
        for p in (out/'requests').glob('*.json'): p.unlink()
    if mutation != 'missing_chunk_start': write(path, data)
    with pytest.raises(ValueError): study._request_counts(out, config)


def test_chunk_gap_and_changed_actual_dtype_are_rejected(tmp_path, monkeypatch):
    config, qa, cases, _, out = bundle(tmp_path, monkeypatch)
    first = out/'chunks/00000000.json'; first.unlink()
    with pytest.raises(ValueError, match='contiguous'): study._chunks(config, qa, cases, out)
    config, qa, cases, _, out = bundle(tmp_path, monkeypatch)
    data = json.loads(first.read_text()); data['execution']['actual_model_dtype'] = 'float32'; write(first, data)
    with pytest.raises(ValueError, match='actual vLLM'): study._chunks(config, qa, cases, out)


def test_vllm_response_must_replay_exact_prepared_prompt_ids():
    tokenizer, source = source_case(); case = study.transform_case(tokenizer, source)
    output = SimpleNamespace(prompt_token_ids=[1], outputs=[SimpleNamespace(text='1', token_ids=[2], finish_reason='stop', stop_reason=None)])
    with pytest.raises(ValueError, match='exact stress prompt'): study.response_rows([case], [output])
