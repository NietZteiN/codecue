"""One declared task-preserving stress query on consumed discovery targets.

Preparation exports only source inputs; generation exports separate raw responses
and five unscored scalars. Original responses and correctness never enter here.
All real tokenizer/model loads are restricted to scheduled workers and cache.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import importlib.metadata
import json
import math
import os
from pathlib import Path
import time
import uuid

from . import confidence
from .datasets import digest, read_jsonl, write_json
from .published_benchmarks import immutable, sha
from .registry import code_identity, guarded

ROLE = 'discovery_task_preserving_stress_measurement_v1'
MEASUREMENT = 'task_preserving_names_arbitrary_query_v1'
TRANSFORM = 'names_are_arbitrary_instruction_v1'
BACKEND_DESCRIPTION = 'vLLM BF16 greedy exact prepared stress prompt IDs; one distinct query per target'
CUE = 'Treat every variable name as an arbitrary label. Determine values only from the assignments, in their written order.'
INSTRUCTION = 'What does this Python 3 program print? Give only the signed integer output, without explanation.'
SOURCE_CASES = 6144
SCALARS = ('valid', 'response_chars', 'output_tokens', 'prediction_value', 'prediction_abs')
CASE_FIELDS = confidence.CASE_FIELDS
HASH_FIELDS = ('prompt_sha256', 'input_token_ids_sha256', 'original_prompt_sha256', 'original_input_token_ids_sha256')
ROW_FIELDS = set(CASE_FIELDS)|{'measurement_role', *HASH_FIELDS, *SCALARS}
RESPONSE_FIELDS = ROW_FIELDS|{'raw_response', 'output_token_ids', 'finish_reason', 'stop_reason'}
PREPARED_FIELDS = set(CASE_FIELDS)|{'evaluation_role', 'transform', 'source_printed', 'assistant_boundary_suffix',
    'original_prompt', 'original_input_token_ids', 'prompt', 'input_token_ids', *HASH_FIELDS}
LIMITATION = ('One distinct instructed query per previously consumed target, not an independent structural replication. '
    'The source program, query and checkpoint-specific assistant suffix are unchanged, but the instruction, '
    'input length and declared generation limit change; its responses are observations, not a causal intervention '
    'or target correctness features. Raw stress output is never compared with a gold answer here. '
    'The vLLM BF16 generation backend is declared separately from earlier outcomes and HF confidence. '
    'Smoke jobs and retried uncommitted chunks are actual additional requests and are counted separately '
    'from the nominal one-distinct-query feature contract. No original response payload or final outcome is opened.')


def _path(value):
    from .forecasting import _discovery_response_path
    from .experiment_log import _protected_outcome
    path = Path(value); _discovery_response_path(path)
    if _protected_outcome(path) or _protected_outcome(path.resolve()):
        raise ValueError('reserved/final outcome paths are excluded')
    return path


def _json(path, expected=None):
    path = _path(path)
    if path.suffix != '.json' or path.stat().st_size > 8*1024**2:
        raise ValueError('bounded JSON metadata required before payload access')
    if expected is not None and sha(path) != expected:
        raise ValueError('pinned stress metadata checksum changed')
    value = json.loads(path.read_text())
    if not isinstance(value, dict): raise ValueError('metadata object required')
    return value


def _scheduled():
    if not os.environ.get('SLURM_JOB_ID'):
        raise RuntimeError('real tokenizer/model loading requires an sbatch worker')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')


def _metadata(config):
    from .forecasting import _discovery_declaration
    if not isinstance(config, dict) or config.get('evaluation_role') != ROLE:
        raise ValueError('explicit discovery stress measurement role required')
    _discovery_declaration(config)
    if config.get('transform', TRANSFORM) != TRANSFORM or config.get('cue', CUE) != CUE:
        raise ValueError('fixed task-preserving stress instruction required')
    if config.get('max_new_tokens', 32) != 32 or type(config.get('max_new_tokens', 32)) is not int:
        raise ValueError('stress generation limit is fixed at 32 new tokens')
    if config.get('device') != 'cuda' or config.get('dtype') != 'bfloat16':
        raise ValueError('declared cached CUDA BF16 vLLM measurement required')
    if config.get('execution_backend') != BACKEND_DESCRIPTION:
        raise ValueError('declare the actual stress vLLM execution_backend explicitly')
    for key in ('source_config', 'prepared_cases', 'preflight_result', 'run_dir', 'dataset', 'runtime_manifest'):
        _path(config[key])
    for key in ('source_config', 'runtime_manifest'):
        if not isinstance(config.get(key+'_sha256'), str) or len(config[key+'_sha256']) != 64:
            raise ValueError('explicit source/runtime SHA256 pins required')
    chunk = config.get('request_chunk_size', 1024)
    if type(chunk) is not int or chunk < 1: raise ValueError('positive request_chunk_size required')
    limit = config.get('case_limit')
    if limit is not None and (type(limit) is not int or not 4 <= limit <= SOURCE_CASES or limit % 4):
        raise ValueError('balanced hash smoke case_limit must be a positive multiple of four')
    if type(config.get('selection_seed', 117)) is not int: raise ValueError('integer selection_seed required')
    if type(config.get('context_limit')) is not int or config['context_limit'] < 33:
        raise ValueError('explicit positive model context_limit required')
    if not isinstance(config.get('engine'), dict) or not isinstance(config.get('cuda_home'), str):
        raise ValueError('declare cached vLLM engine and CUDA runtime settings')
    if set(config['engine']) & {'model', 'revision', 'tokenizer', 'tokenizer_revision', 'dtype', 'seed', 'generation_config', 'max_model_len'}:
        raise ValueError('engine settings cannot replace frozen checkpoint or generation identity')
    source = _json(config['source_config'], config['source_config_sha256'])
    confidence._source(config)
    _json(config['runtime_manifest'], config['runtime_manifest_sha256'])
    source = _json(config['source_config'], config['source_config_sha256'])
    stage = _path(Path(source['run_dir'])/'checkpoint_suite')
    manifest = _json(stage/'manifest.json'); identity = manifest.get('identity', {})
    audit = _json(stage/'audit.json'); qa = _json(source['preflight_result'])
    dataset_manifest = _json(Path(source['dataset']).with_suffix('.manifest.json'))
    for value in (source, manifest, identity, audit, qa, dataset_manifest): _discovery_declaration(value)
    if (manifest.get('status') != 'complete' or manifest.get('identity_hash') != digest(identity)
            or identity.get('config') != source or audit.get('status') != 'passed' or not audit.get('complete')
            or audit.get('identity_hash') != manifest['identity_hash'] or audit.get('preflight') != qa
            or qa.get('status') != 'passed' or qa.get('config_hash') != digest(source)
            or qa.get('source_sha256') != identity.get('code', {}).get('source_sha256')
            or dataset_manifest.get('status') != 'validated'
            or identity.get('dataset_manifest') != dataset_manifest
            or not manifest.get('responses_sha256')):
        raise ValueError('complete matching original discovery source metadata required')
    provenance = {'source_config_sha256': config['source_config_sha256'],
        'source_dataset_sha256': dataset_manifest['sha256'], 'source_identity_hash': manifest['identity_hash'],
        'source_model': source['model'], 'source_model_revision': source['model_revision'],
        'source_prepared_sha256': qa['prepared_cases_sha256'], 'source_audit_sha256': sha(stage/'audit.json'),
        'original_source_sha256': identity['code']['source_sha256'], 'source_responses_sha256': manifest['responses_sha256']}
    return source, provenance


def metadata_preflight(config):
    source, provenance = _metadata(config)
    return {'status': 'passed', 'evaluation_role': ROLE, 'measurement': MEASUREMENT,
        'config_hash': digest(config), 'model': source['model'], 'model_revision': source['model_revision'],
        'source_config_sha256': config['source_config_sha256'], 'source_provenance': provenance,
        'transform': TRANSFORM, 'cue': CUE, 'nominal_distinct_queries_per_target': 1,
        'max_new_tokens': 32, 'source_payloads_read': False, 'target_outcomes_read': False,
        'generated_holdouts_opened': False, 'model_loading': False, 'limitation': LIMITATION}


def select_cases(cases, config):
    """Select task inputs by IDs only, balanced smoke bins, no correctness."""
    from .competition import ROLE as SOURCE_ROLE
    selected = []; seen = set()
    for case in cases:
        row = case['record']
        if case.get('kind') != 'competition' or row.get('evaluation_role') != SOURCE_ROLE or row.get('split') not in ('train', 'development'):
            raise ValueError('only original competition discovery inputs are eligible')
        if row.get('family') != 'versions' or row.get('condition') not in ('informative', 'misleading'): continue
        if case['id'] != row['id'] or case['id'] in seen: raise ValueError('duplicate or mismatched original IDs')
        seen.add(case['id']); selected.append(case)
    if len(selected) != SOURCE_CASES: raise ValueError('complete nonneutral discovery target bank required')
    limit = config.get('case_limit')
    if limit is not None:
        groups = defaultdict(list)
        for case in selected: groups[case['record']['split'], case['record']['condition']].append(case)
        if set(groups) != {(s, c) for s in ('train', 'development') for c in ('informative', 'misleading')}:
            raise ValueError('complete balanced smoke strata required')
        selected = []
        for group in groups.values():
            if len(group) < limit//4: raise ValueError('smoke stratum has insufficient cases')
            selected.extend(sorted(group, key=lambda c: (digest([config.get('selection_seed', 117), c['id']]), c['id']))[:limit//4])
    return sorted(selected, key=lambda case: case['id'])


def transform_case(tokenizer, case):
    from .calibration import prompt as original_prompt, printed_source
    from .model_adapter import normalize_prompt
    row = case['record']; original, source = original_prompt(tokenizer, row, 'print_direct_v3')
    old_ids = tokenizer(original, add_special_tokens=False)['input_ids']
    if (case.get('prompt') != original or case.get('input_token_ids') != old_ids
            or case.get('prompt_sha256') != digest(original) or source != printed_source(row['source'])):
        raise ValueError('official-template parent prompt bytes or exact saved IDs differ')
    block = '```python\n'+source+'\n```'
    if original.count(INSTRUCTION) != 1 or original.count(block) != 1 or INSTRUCTION+'\n\n'+block not in original:
        raise ValueError('unique original user instruction and exact printed source required')
    content = INSTRUCTION+'\n'+CUE+'\n\n'+block
    rendered = tokenizer.apply_chat_template([{'role': 'user', 'content': content},
        {'role': 'assistant', 'content': 'Output:\n'}], tokenize=False, continue_final_message=True)
    rendered = normalize_prompt(tokenizer, rendered)
    expected = original.replace(INSTRUCTION, INSTRUCTION+'\n'+CUE, 1)
    if rendered != expected or rendered.split(block, 1)[1] != original.split(block, 1)[1]:
        raise ValueError('stress transformation changed code, query or checkpoint-specific assistant suffix')
    ids = tokenizer(rendered, add_special_tokens=False)['input_ids']
    item = {key: row[key] for key in CASE_FIELDS}
    item.update(evaluation_role=ROLE, transform=TRANSFORM, source_printed=source,
        assistant_boundary_suffix=original.split(block, 1)[1], original_prompt=original,
        original_input_token_ids=list(old_ids), original_prompt_sha256=digest(original),
        original_input_token_ids_sha256=digest(old_ids), prompt=rendered, input_token_ids=list(ids),
        prompt_sha256=digest(rendered), input_token_ids_sha256=digest(ids))
    validate_prepared(item); return item


def validate_prepared(item):
    if (set(item) != PREPARED_FIELDS or item['evaluation_role'] != ROLE or item['transform'] != TRANSFORM
            or item['split'] not in ('train', 'development') or item['condition'] not in ('informative', 'misleading')):
        raise ValueError('strict label-free stress input schema required')
    for prefix in ('', 'original_'):
        prompt = item[prefix+'prompt']; tokens = item[prefix+'input_token_ids']
        if (not isinstance(prompt, str) or not prompt or digest(prompt) != item[prefix+'prompt_sha256']
                or not isinstance(tokens, list) or not tokens or any(type(t) is not int or t < 0 for t in tokens)
                or digest(tokens) != item[prefix+'input_token_ids_sha256']):
            raise ValueError('prepared prompt/token identity differs')
    block = '```python\n'+item['source_printed']+'\n```'
    if (item['original_prompt'].count(INSTRUCTION) != 1 or item['original_prompt'].count(block) != 1
            or item['prompt'] != item['original_prompt'].replace(INSTRUCTION, INSTRUCTION+'\n'+CUE, 1)
            or item['prompt'].count(block) != 1 or item['input_token_ids'] == item['original_input_token_ids']
            or item['prompt'].split(block, 1)[1] != item['assistant_boundary_suffix']
            or item['original_prompt'].split(block, 1)[1] != item['assistant_boundary_suffix']):
        raise ValueError('exact task-preserving cue/code/assistant-boundary contract differs')


def prepare(config):
    _, provenance = _metadata(config); _scheduled()
    from .discovery_features import _source_inputs
    from .model_adapter import configure_tokenizer
    from transformers import AutoTokenizer
    source, _, cases, observed = _source_inputs({'source_config': config['source_config'],
        'source_config_sha256': config['source_config_sha256'], 'model': config['model'], 'model_revision': config['model_revision']})
    if observed != provenance: raise ValueError('original source provenance changed before input preparation')
    tokenizer = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tokenizer, config)
    prepared = [transform_case(tokenizer, case) for case in select_cases(cases, config)]
    if any(len(case['input_token_ids'])+32 > config['context_limit'] for case in prepared):
        raise ValueError('transformed prompt exceeds the declared model context')
    path = _path(config['prepared_cases'])
    immutable(path, ''.join(json.dumps(case, sort_keys=True)+'\n' for case in prepared).encode())
    result = {'status': 'passed', 'evaluation_role': ROLE, 'measurement': MEASUREMENT,
        'config_hash': digest(config), 'source_sha256': code_identity()['source_sha256'],
        'source_config_sha256': config['source_config_sha256'], 'source_provenance': provenance,
        'prepared_cases_sha256': sha(path), 'case_ids_sha256': digest([case['id'] for case in prepared]),
        'cases': len(prepared), 'model': source['model'], 'model_revision': source['model_revision'],
        'tokenizer_revision': config['tokenizer_revision'], 'eos_token_ids': config['eos_token_ids'],
        'conditions': dict(Counter(case['condition'] for case in prepared)),
        'original_splits': dict(Counter(case['split'] for case in prepared)),
        'boundary_suffixes': dict(Counter(case['assistant_boundary_suffix'] for case in prepared)),
        'smoke_subset': config.get('case_limit') is not None, 'transform': TRANSFORM, 'cue': CUE,
        'nominal_distinct_queries_per_target': 1, 'max_new_tokens': 32, 'generated_tokens': 0,
        'original_prompt_replay_verified': True, 'code_and_query_unchanged': True, 'assistant_boundary_unchanged': True,
        'target_outcomes_read': False, 'oracle_fields_exported': False, 'generated_holdouts_opened': False, 'limitation': LIMITATION}
    immutable(config['preflight_result'], confidence._json(result)); return result


def _preparation_metadata(config, expected_source=None):
    _, provenance = _metadata(config); qa = _json(config['preflight_result'])
    if (qa.get('status') != 'passed' or qa.get('evaluation_role') != ROLE or qa.get('measurement') != MEASUREMENT
            or qa.get('config_hash') != digest(config) or qa.get('source_provenance') != provenance
            or qa.get('source_sha256') != (expected_source or code_identity()['source_sha256'])
            or any(qa.get(k) != config[k] for k in ('model', 'model_revision', 'tokenizer_revision', 'eos_token_ids'))
            or qa.get('cases') != (config.get('case_limit') or SOURCE_CASES)
            or qa.get('smoke_subset') is not (config.get('case_limit') is not None)
            or qa.get('transform') != TRANSFORM or qa.get('cue') != CUE
            or qa.get('source_config_sha256') != config['source_config_sha256']
            or qa.get('nominal_distinct_queries_per_target') != 1 or qa.get('max_new_tokens') != 32
            or qa.get('generated_tokens') != 0
            or any(qa.get(k) is not True for k in ('original_prompt_replay_verified', 'code_and_query_unchanged', 'assistant_boundary_unchanged'))
            or any(qa.get(k) is not False for k in ('target_outcomes_read', 'oracle_fields_exported', 'generated_holdouts_opened'))):
        raise ValueError('matching frozen label-free stress preparation required')
    return qa


def inputs(config, expected_source=None):
    qa = _preparation_metadata(config, expected_source)
    if sha(_path(config['prepared_cases'])) != qa['prepared_cases_sha256']:
        raise ValueError('prepared stress payload checksum changed')
    cases = read_jsonl(config['prepared_cases'])
    if (len(cases) != qa['cases'] or len({c['id'] for c in cases}) != len(cases)
            or digest([c['id'] for c in cases]) != qa['case_ids_sha256'] or [c['id'] for c in cases] != sorted(c['id'] for c in cases)):
        raise ValueError('stress prepared ID coverage differs')
    for case in cases:
        validate_prepared(case)
        if len(case['input_token_ids'])+32 > config['context_limit']: raise ValueError('stress context coverage differs')
    if (qa.get('conditions') != dict(Counter(c['condition'] for c in cases))
            or qa.get('original_splits') != dict(Counter(c['split'] for c in cases))
            or qa.get('boundary_suffixes') != dict(Counter(c['assistant_boundary_suffix'] for c in cases))):
        raise ValueError('prepared stress condition/split/boundary coverage differs')
    return qa, cases


def scalars(raw, token_ids):
    from .behavior import parse_answer
    if not isinstance(raw, str): raise ValueError('raw stress response text required')
    if not isinstance(token_ids, list) or len(token_ids) > 32 or any(type(t) is not int or t < 0 for t in token_ids):
        raise ValueError('finite declared output token IDs required')
    value = parse_answer(raw)
    if value is not None:
        try: finite = math.isfinite(float(value))
        except OverflowError: finite = False
        if not finite: raise ValueError('parsed stress integer exceeds finite numeric feature range')
    return {'valid': int(value is not None), 'response_chars': len(raw), 'output_tokens': len(token_ids),
        'prediction_value': value if value is not None else 0, 'prediction_abs': abs(value) if value is not None else 0}


def scalar_rows(rows):
    return [{key: row[key] for key in ROW_FIELDS} for row in rows]


def _validate_stop(row, eos):
    reason = row['stop_reason']; tokens = row['output_token_ids']
    if row['finish_reason'] == 'length':
        if len(tokens) != 32 or reason is not None: raise ValueError('length stop must exhaust the declared 32-token limit')
    elif reason is None:
        if not tokens or tokens[-1] not in eos: raise ValueError('native EOS stop requires a declared final EOS token')
    elif type(reason) is int:
        if reason not in eos or not tokens or tokens[-1] != reason: raise ValueError('configured stop token differs from declared EOS')
    elif reason != '\n\n' or not row['raw_response'].endswith(reason):
        raise ValueError('stress stop string must be the included declared blank line')


def validate_rows(cases, rows, *, responses=False, config=None):
    if len(cases) != len(rows): raise ValueError('stress response coverage differs')
    for case, row in zip(cases, rows):
        if (set(row) != (RESPONSE_FIELDS if responses else ROW_FIELDS) or row['measurement_role'] != ROLE
                or any(row[k] != case[k] for k in (*CASE_FIELDS, *HASH_FIELDS))):
            raise ValueError('stress row schema or exact original/transformed identity differs')
        if (any(type(row[k]) is not int for k in SCALARS) or row['valid'] not in (0, 1)
                or row['response_chars'] < 0 or not 0 <= row['output_tokens'] <= 32
                or row['prediction_abs'] != abs(row['prediction_value'])
                or not row['valid'] and (row['prediction_value'] or row['prediction_abs'])):
            raise ValueError('stress unscored scalar domains differ')
        if responses:
            if ({key: row[key] for key in SCALARS} != scalars(row['raw_response'], row['output_token_ids'])
                    or row['finish_reason'] not in ('stop', 'length')
                    or row['stop_reason'] is not None and type(row['stop_reason']) not in (int, str)):
                raise ValueError('raw stress response parsing/token/generation provenance differs')
            if config is not None: _validate_stop(row, config['eos_token_ids'])


def _validate_execution(value, config=None):
    if (not isinstance(value, dict) or value.get('backend') != 'vllm'
            or value.get('actual_model_dtype') != 'bfloat16' or value.get('actual_model_dtype_verified') is not True
            or not isinstance(value.get('device_name'), str) or not value['device_name']
            or not isinstance(value.get('engine'), dict) or not isinstance(value.get('versions'), dict)
            or any(not isinstance(value['versions'].get(k), str) for k in ('torch', 'transformers', 'vllm'))
            or not isinstance(value.get('slurm_job_id'), str) or not value['slurm_job_id']
            or value.get('max_new_tokens') != 32 or value.get('greedy_seed') != 0 or value.get('temperature') != 0
            or value.get('top_p') != 1 or value.get('stop') != ['\n\n']
            or value.get('prefix_caching') is not True or value.get('chunked_prefill') is not True
            or not isinstance(value.get('eos_token_ids'), list) or not value['eos_token_ids']
            or type(value.get('device_total_memory_bytes')) is not int or value['device_total_memory_bytes'] < 1
            or value.get('generation_config') != 'vllm'):
        raise ValueError('verified actual vLLM backend/dtype/device/runtime execution required')
    if config is not None:
        from .checkpoint_suite import engine_settings
        if (value['eos_token_ids'] != config['eos_token_ids']
                or value['engine'] != engine_settings(config, value['device_total_memory_bytes'])):
            raise ValueError('stress execution EOS or hardware-resolved engine settings differ')


def _chunks(config, qa, cases, out):
    size = config.get('request_chunk_size', 1024); folder = out/'chunks'; folder.mkdir(exist_ok=True)
    expected = {f'{start:08d}.json' for start in range(0, len(cases), size)}
    if any(path.name not in expected for path in folder.glob('*.json')): raise ValueError('unexpected stress chunk identity')
    rows = []; pending = []; gap = False
    for start in range(0, len(cases), size):
        part = cases[start:start+size]; path = folder/f'{start:08d}.json'
        if not path.exists(): gap = True; pending.append((start, part, path)); continue
        if gap: raise ValueError('stress chunks must form a contiguous committed prefix')
        data = json.loads(_path(path).read_text())
        if (data.get('config_hash') != digest(config) or data.get('prepared_cases_sha256') != qa['prepared_cases_sha256']
                or data.get('start') != start or data.get('measurement') != MEASUREMENT
                or not isinstance(data.get('request_id'), str)):
            raise ValueError('stress chunk source/config/request identity differs')
        _validate_execution(data.get('execution'), config)
        validate_rows(part, data['rows'], responses=True, config=config); rows.extend(data['rows'])
    return rows, pending


def _request_counts(out, config):
    started = {}; completed = {}
    for path in sorted((out/'requests').glob('*.json')):
        data = _json(path)
        if data.get('config_hash') != digest(config) or data.get('state') not in ('started', 'completed'):
            raise ValueError('stress request accounting identity differs')
        if (not isinstance(data.get('request_id'), str) or len(data['request_id']) != 32
                or any(c not in '0123456789abcdef' for c in data['request_id'])
                or type(data.get('start')) is not int or data['start'] < 0 or data['start'] % config.get('request_chunk_size', 1024)
                or type(data.get('cases')) is not int or not 1 <= data['cases'] <= config.get('request_chunk_size', 1024)
                or not isinstance(data.get('case_ids_sha256'), str) or len(data['case_ids_sha256']) != 64
                or any(c not in '0123456789abcdef' for c in data['case_ids_sha256'])
                or data['start'] >= (config.get('case_limit') or SOURCE_CASES)
                or data['cases'] != min(config.get('request_chunk_size', 1024), (config.get('case_limit') or SOURCE_CASES)-data['start'])):
            raise ValueError('stress request count/range/ID digest differs')
        _validate_execution(data.get('execution'), config)
        target = started if data['state'] == 'started' else completed
        if data['request_id'] in target: raise ValueError('duplicate stress request lifecycle event')
        target[data['request_id']] = data
    if set(completed)-set(started): raise ValueError('stress request completion lacks its started record')
    for key, end in completed.items():
        if any(end.get(field) != started[key].get(field) for field in ('start', 'cases', 'case_ids_sha256', 'execution')):
            raise ValueError('stress request completion case identities differ')
    committed = {}
    for path in sorted((out/'chunks').glob('*.json')):
        chunk = json.loads(_path(path).read_text()); rid = chunk.get('request_id')
        if rid in committed or rid not in started: raise ValueError('committed stress chunk lacks a unique started request')
        if (chunk.get('config_hash') != digest(config) or chunk.get('start') != started[rid]['start']
                or len(chunk.get('rows', [])) != started[rid]['cases']
                or digest([r['id'] for r in chunk['rows']]) != started[rid]['case_ids_sha256']
                or chunk.get('execution') != started[rid]['execution']):
            raise ValueError('committed chunk and request case identities differ')
        tokens = sum(row['output_tokens'] for row in chunk['rows'])
        if rid in completed and completed[rid].get('generated_tokens') != tokens:
            raise ValueError('completed request generated-token accounting differs')
        committed[rid] = chunk
    if set(completed)-set(committed): raise ValueError('completed stress request lacks its immutable committed chunk')
    # A crash after committing a chunk but before its completion journal is
    # observable as completed from the immutable chunk; never requery it.
    observed = set(completed)|set(committed)
    return {'request_attempts': len(started), 'case_request_attempts': sum(d['cases'] for d in started.values()),
        'completed_request_attempts': len(observed), 'completed_case_request_attempts': sum(started[k]['cases'] for k in observed),
        'completion_observed_from_chunk_only': len(set(committed)-set(completed)),
        'incomplete_request_attempts': len(set(started)-observed),
        'uncommitted_case_request_attempts': sum(d['cases'] for key, d in started.items() if key not in observed)}


def response_rows(cases, outputs, config=None):
    if len(cases) != len(outputs): raise ValueError('vLLM stress response count differs')
    rows = []
    for case, output in zip(cases, outputs):
        if list(output.prompt_token_ids) != case['input_token_ids'] or len(output.outputs) != 1:
            raise ValueError('vLLM changed exact stress prompt IDs or completion count')
        completion = output.outputs[0]
        row = {key: case[key] for key in (*CASE_FIELDS, *HASH_FIELDS)}
        row.update(measurement_role=ROLE, raw_response=completion.text, output_token_ids=list(completion.token_ids),
            finish_reason=completion.finish_reason, stop_reason=getattr(completion, 'stop_reason', None),
            **scalars(completion.text, list(completion.token_ids)))
        rows.append(row)
    validate_rows(cases, rows, responses=True, config=config); return rows


@guarded
def collect(config):
    qa, cases = inputs(config); _scheduled()
    out = _path(Path(config['run_dir'])/'stress_measurement')
    with confidence._run_lock(out):
        from .checkpoint_suite import configure_runtime, engine_settings
        configure_runtime(config)
        from .registry import begin, finish
        out, manifest = begin(config, 'stress_measurement', reuse_complete=True)
        rows, pending = _chunks(config, qa, cases, out)
        if manifest['status'] == 'complete':
            audit(config); return _json(out/'summary.json')
        started = time.monotonic(); resumed = len(rows); gpu = None; load_seconds = 0.; settings = None; device = None
        if pending:
            import torch
            from vllm import LLM, SamplingParams
            from .gpu_telemetry import UUIDMonitor
            settings = engine_settings(config, torch.cuda.get_device_properties(0).total_memory)
            before = time.monotonic()
            engine = LLM(model=config['model'], revision=config['model_revision'], tokenizer_revision=config['tokenizer_revision'],
                dtype='bfloat16', max_model_len=config['context_limit'], enable_prefix_caching=True,
                enable_chunked_prefill=True, seed=0, generation_config='vllm', **settings)
            load_seconds = time.monotonic()-before; device = torch.cuda.get_device_name()
            actual_dtype = str(getattr(getattr(engine, 'model_config', None), 'dtype', None)).removeprefix('torch.')
            execution = {'backend': 'vllm', 'actual_model_dtype': actual_dtype,
                'actual_model_dtype_verified': actual_dtype == 'bfloat16', 'device_name': device, 'engine': settings,
                'versions': {name: importlib.metadata.version(name) for name in ('torch', 'transformers', 'vllm')},
                'cuda_matmul_allow_tf32': bool(torch.backends.cuda.matmul.allow_tf32),
                'cudnn_allow_tf32': bool(torch.backends.cudnn.allow_tf32),
                'slurm_job_id': os.environ['SLURM_JOB_ID'],
                'gpu_uuid': str(getattr(torch.cuda.get_device_properties(0), 'uuid', 'unavailable')),
                'device_total_memory_bytes': int(torch.cuda.get_device_properties(0).total_memory),
                'generation_config': 'vllm',
                'max_new_tokens': 32, 'greedy_seed': 0, 'temperature': 0, 'top_p': 1,
                'stop': ['\n\n'], 'eos_token_ids': config['eos_token_ids'],
                'prefix_caching': True, 'chunked_prefill': True}
            _validate_execution(execution, config)
            params = SamplingParams(temperature=0, top_p=1, max_tokens=32, stop=['\n\n'],
                include_stop_str_in_output=True, stop_token_ids=config['eos_token_ids'])
            with UUIDMonitor() as monitor:
                for start, part, path in pending:
                    request_id = uuid.uuid4().hex
                    request = {'request_id': request_id, 'state': 'started', 'config_hash': digest(config),
                        'start': start, 'cases': len(part), 'case_ids_sha256': digest([c['id'] for c in part]),
                        'slurm_job_id': os.environ.get('SLURM_JOB_ID'), 'execution': execution}
                    confidence._atomic(out/'requests'/f'{request_id}_started.json', confidence._json(request))
                    outputs = engine.generate([{'prompt_token_ids': c['input_token_ids']} for c in part], params, use_tqdm=False)
                    block = response_rows(part, outputs, config)
                    confidence._atomic(path, confidence._json({'config_hash': digest(config),
                        'prepared_cases_sha256': qa['prepared_cases_sha256'], 'measurement': MEASUREMENT,
                        'start': start, 'request_id': request_id, 'execution': execution, 'rows': block}))
                    confidence._atomic(out/'requests'/f'{request_id}_completed.json', confidence._json({**request, 'state': 'completed',
                        'generated_tokens': sum(r['output_tokens'] for r in block)}))
                    rows.extend(block)
                    write_json(out/'progress.json', {'status': 'running', 'evaluated': len(rows), 'planned': len(cases),
                        'target_outcomes_read': False, 'generated_holdouts_opened': False})
                    print(f'stress measurement {len(rows)}/{len(cases)}', flush=True)
            gpu = monitor.summary()
        validate_rows(cases, rows, responses=True, config=config); scalar = scalar_rows(rows); validate_rows(cases, scalar)
        response_path = out/'responses.jsonl'; scalar_path = out/'scalars.jsonl'
        confidence._atomic(response_path, ''.join(json.dumps(row, sort_keys=True)+'\n' for row in rows).encode())
        confidence._atomic(scalar_path, ''.join(json.dumps(row, sort_keys=True)+'\n' for row in scalar).encode())
        import torch
        executions = {digest(value): value for path in sorted((out/'chunks').glob('*.json'))
            for value in [json.loads(path.read_text())['execution']]}
        runtime = {'status': 'recorded', 'backend': 'vllm', 'dtype': 'bfloat16', 'device_name': device,
            'load_seconds': load_seconds, 'engine': settings, 'eos_token_ids': config['eos_token_ids'],
            'greedy_seed': 0, 'temperature': 0, 'top_p': 1, 'max_new_tokens': 32,
            'padding_policy': 'engine-managed batching of exact unpadded saved token-ID requests',
            'prefix_caching': True, 'chunked_prefill': True, 'stop': ['\n\n'],
            'gpu': gpu, 'resumed_cases': resumed, 'measured_this_attempt': len(rows)-resumed,
            'executions': list(executions.values()),
            'cuda_matmul_allow_tf32': bool(torch.backends.cuda.matmul.allow_tf32),
            'cudnn_allow_tf32': bool(torch.backends.cudnn.allow_tf32),
            'versions': {name: importlib.metadata.version(name) for name in ('torch', 'transformers', 'vllm')},
            'gpu_scope': 'current attempt only; prior committed requests are preserved', **_request_counts(out, config)}
        write_json(out/'runtime.json', runtime)
        summary = {'status': 'complete', 'complete': True, 'evaluation_role': ROLE, 'measurement': MEASUREMENT,
            'evaluated': len(rows), 'planned': len(cases), 'model': config['model'], 'model_revision': config['model_revision'],
            'source_provenance': qa['source_provenance'], 'scalars_sha256': sha(scalar_path), 'responses_sha256': sha(response_path),
            'prepared_cases_sha256': qa['prepared_cases_sha256'], 'case_ids_sha256': qa['case_ids_sha256'],
            'nominal_distinct_queries_per_target': 1, 'max_new_tokens': 32, 'transform': TRANSFORM, 'cue': CUE,
            'smoke_subset': qa['smoke_subset'], 'generated_tokens': sum(r['output_tokens'] for r in rows),
            'valid': sum(r['valid'] for r in rows), 'target_outcomes_read': False, 'oracle_fields_exported': False,
            'generated_holdouts_opened': False, 'wall_seconds': time.monotonic()-started, 'load_seconds': load_seconds,
            'gpu': gpu, 'runtime_sha256': sha(out/'runtime.json'), **_request_counts(out, config), 'limitation': LIMITATION}
        write_json(out/'summary.json', summary)
        finish(out, manifest, time.monotonic()-started, scalars_sha256=summary['scalars_sha256'],
            responses_sha256=summary['responses_sha256'], evaluated=len(rows), planned=len(cases))
        audit(config); return summary


def _completion_metadata(config, *, require_audit, allow_smoke):
    _metadata(config); out = _path(Path(config['run_dir'])/'stress_measurement')
    manifest = _json(out/'manifest.json'); identity = manifest.get('identity', {})
    if (manifest.get('status') != 'complete' or manifest.get('identity_hash') != digest(identity)
            or identity.get('config') != config): raise ValueError('complete matching stress manifest required')
    qa = _preparation_metadata(config, identity.get('code', {}).get('source_sha256'))
    summary = _json(out/'summary.json'); runtime = _json(out/'runtime.json', summary.get('runtime_sha256'))
    if (not allow_smoke and qa['smoke_subset']) or (summary.get('status') != 'complete' or summary.get('complete') is not True
            or summary.get('measurement') != MEASUREMENT or summary.get('evaluation_role') != ROLE
            or summary.get('evaluated') != qa['cases'] or summary.get('planned') != qa['cases']
            or summary.get('source_provenance') != qa['source_provenance']
            or summary.get('prepared_cases_sha256') != qa['prepared_cases_sha256'] or summary.get('case_ids_sha256') != qa['case_ids_sha256']
            or summary.get('nominal_distinct_queries_per_target') != 1 or summary.get('max_new_tokens') != 32
            or summary.get('transform') != TRANSFORM or summary.get('cue') != CUE or summary.get('smoke_subset') is not qa['smoke_subset']
            or any(summary.get(k) != config[k] for k in ('model', 'model_revision'))
            or any(summary.get(k) is not False for k in ('target_outcomes_read', 'oracle_fields_exported', 'generated_holdouts_opened'))
            or any(not isinstance(summary.get(k), str) or len(summary[k]) != 64 or summary[k] != manifest.get(k) for k in ('scalars_sha256', 'responses_sha256'))):
        raise ValueError('stress completion/source/access metadata differs')
    if (runtime.get('status') != 'recorded' or runtime.get('backend') != 'vllm' or runtime.get('dtype') != config['dtype']
            or runtime.get('eos_token_ids') != config['eos_token_ids'] or runtime.get('max_new_tokens') != 32
            or runtime.get('greedy_seed') != 0 or runtime.get('temperature') != 0 or runtime.get('top_p') != 1
            or runtime.get('prefix_caching') is not True or runtime.get('chunked_prefill') is not True
            or runtime.get('stop') != ['\n\n']): raise ValueError('stress runtime/generation contract differs')
    if not runtime.get('executions'): raise ValueError('actual stress runtime execution records required')
    for value in runtime['executions']: _validate_execution(value, config)
    result = {'preparation': qa, 'manifest': manifest, 'summary': summary, 'runtime': runtime}
    if require_audit:
        audit = _json(out/'audit.json')
        if (audit.get('status') != 'passed' or audit.get('complete') is not True or audit.get('evaluated') != qa['cases']
                or audit.get('identity_hash') != manifest['identity_hash'] or audit.get('measurement') != MEASUREMENT
                or audit.get('evaluation_role') != ROLE or audit.get('preparation') != qa
                or any(audit.get(k) != summary[k] for k in ('scalars_sha256', 'responses_sha256', 'model', 'model_revision'))):
            raise ValueError('complete stress audit metadata differs')
        result['audit'] = audit
    return result


def completed_metadata(config, *, allow_smoke=False):
    """Metadata-only completed-bank guard before a collector reads any payload."""
    return _completion_metadata(config, require_audit=True, allow_smoke=allow_smoke)


def audit(config):
    checked = _completion_metadata(config, require_audit=False, allow_smoke=True)
    qa = checked['preparation']; out = Path(config['run_dir'])/'stress_measurement'
    _, cases = inputs(config, checked['manifest']['identity']['code']['source_sha256'])
    for name in ('responses', 'scalars'):
        if sha(_path(out/(name+'.jsonl'))) != checked['summary'][name+'_sha256']:
            raise ValueError('stress final response/scalar payload checksum differs')
    rows = read_jsonl(out/'responses.jsonl'); values = read_jsonl(out/'scalars.jsonl')
    validate_rows(cases, rows, responses=True, config=config); validate_rows(cases, values)
    chunk_rows, pending = _chunks(config, qa, cases, out)
    if pending or chunk_rows != rows or scalar_rows(rows) != values: raise ValueError('stress chunk/final/scalar coverage differs')
    executions = {digest(value): value for path in sorted((out/'chunks').glob('*.json'))
        for value in [json.loads(path.read_text())['execution']]}
    if list(executions.values()) != checked['runtime']['executions']:
        raise ValueError('stress chunk/runtime execution provenance differs')
    counts = _request_counts(out, config)
    if any(checked['summary'].get(k) != v or checked['runtime'].get(k) != v for k, v in counts.items()):
        raise ValueError('stress actual request attempt accounting differs')
    if (checked['summary']['generated_tokens'] != sum(row['output_tokens'] for row in rows)
            or checked['summary']['valid'] != sum(row['valid'] for row in rows)):
        raise ValueError('stress generated token or parser counts differ')
    result = {'status': 'passed', 'complete': True, 'evaluated': len(rows), 'evaluation_role': ROLE,
        'measurement': MEASUREMENT, 'identity_hash': checked['manifest']['identity_hash'],
        'scalars_sha256': checked['summary']['scalars_sha256'], 'responses_sha256': checked['summary']['responses_sha256'],
        'model': config['model'], 'model_revision': config['model_revision'], 'preparation': qa,
        'target_outcomes_read': False, 'generated_holdouts_opened': False, 'oracle_fields_exported': False,
        'nominal_distinct_queries_per_target': 1, **counts,
        'scope': 'Exact source/transform identities, label-free schemas, full ID coverage, deterministic parser, chunks, request accounting and payload checksums; no correctness scoring.'}
    immutable(out/'audit.json', confidence._json(result)); return result
