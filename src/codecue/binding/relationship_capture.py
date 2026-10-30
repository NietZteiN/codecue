"""Frozen, discovery-only prefill captures for structural and numeric readouts.

No response is generated or scored. Features are raw decoder-block outputs;
minimal source metadata provides targets separately. Every saved surface prefix
is exactly the decoded token prefix seen at its capture position.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import io
import json
import math
import os
from pathlib import Path
import time

import numpy as np

from . import algebraic_programs
from .datasets import digest, write_json
from .published_benchmarks import immutable

ROLE = 'discovery_relationship_capture_v1'
DATASET_SHA256 = '8a96759d14968605d7d2a21e9a91c552b62072e926f3a49d5cf11f5f870ac2c5'
SOURCE_ROWS = 1944
MODEL = 'meta-llama/Llama-3.1-8B-Instruct'
REVISION = '0e9e39f249a16976918f6564b8830bc894c89659'
LAYERS = (8, 16, 24, 31)
SITES = tuple(f'statement:{i}' for i in range(8)) + ('pre_answer',)
HIDDEN_SIZE = 4096
ATOL = 1e-5
INSTRUCTION = 'Execute this Python program and return only its final integer output.'
BACKEND = 'Transformers BF16 SDPA decoder prefill, explicit left-padding position IDs, use_cache=False; no generation'
PREFIX_SCOPE = ('Identical token prefixes within the same prefill batch, unpadded prompt length and physical position; '
                'different-padding geometry is diagnostic only; no cross-batch numerical-identity claim.')
MAX_JSON = 8 * 1024**2
MAX_PREPARED = 64 * 1024**2
RECORD_FIELDS = ('id', 'base_id', 'component_id', 'cluster_id', 'template_id', 'split', 'condition',
    'lexical_realization', 'source', 'canonical_source', 'rename_map', 'variable_slots',
    'evaluation_role', 'family', 'control_kind', 'query_role', 'query_count')


def _safe(path):
    from .experiment_log import _protected_outcome
    if not isinstance(path, (str, Path)) or not str(path) or len(str(path)) > 1024:
        raise ValueError('bounded explicit discovery paths required')
    path = Path(path)
    if _protected_outcome(path) or _protected_outcome(path.resolve()):
        raise ValueError('reserved/final outcome paths are excluded')
    return path


def _bytes(path, maximum):
    path = _safe(path)
    if not path.is_file() or path.stat().st_size > maximum:
        raise ValueError('bounded regular artifact required: ' + str(path))
    with path.open('rb') as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum: raise ValueError('artifact exceeds byte bound')
    return data


def _sha(path):
    path = _safe(path)
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''): hasher.update(block)
    return hasher.hexdigest()


def _json(path, checksum=None):
    data = _bytes(path, MAX_JSON)
    if checksum is not None and hashlib.sha256(data).hexdigest() != checksum:
        raise ValueError('metadata checksum differs')
    result = json.loads(data)
    if not isinstance(result, dict): raise ValueError('metadata object required')
    return result


def _put(path, value):
    payload = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    if len(payload) > MAX_JSON: raise ValueError('capture metadata exceeds byte bound')
    _publish(path, payload)


def _publish(path, payload):
    """Atomically publish caller-bounded immutable bytes without following links."""
    import tempfile
    path = _safe(path)
    if path.is_symlink(): raise ValueError('capture output files must not be symbolic links')
    if not isinstance(payload, bytes): raise ValueError('immutable publication requires bytes')
    if path.exists():
        immutable(path, payload)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary, created = None, False
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '.', suffix='.pending', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
            created = True
        except FileExistsError:
            if path.is_symlink(): raise ValueError('capture output files must not be symbolic links')
            immutable(path, payload)
    finally:
        if temporary is not None and temporary.exists(): temporary.unlink()
    if created:
        try:
            from .experiment_log import note_artifact
            note_artifact(path.resolve())
        except Exception as exc:
            import sys
            print(f'Experiment metadata logging deferred: {type(exc).__name__}: {exc}', file=sys.stderr)


def _config(config):
    required = {'evaluation_role', 'dataset', 'dataset_sha256', 'run_dir'}
    fixed = {'model': MODEL, 'model_revision': REVISION, 'tokenizer_revision': REVISION,
        'dtype': 'bfloat16', 'device': 'cuda', 'tokenization_mode': 'native',
        'layers': list(LAYERS), 'hidden_size': HIDDEN_SIZE, 'context_limit': 4096,
        'prefix_atol': ATOL, 'chunk_size': 128, 'execution_backend': BACKEND}
    if (not isinstance(config, dict) or config.get('evaluation_role') != ROLE
            or required - set(config) or set(config) - required - set(fixed) - {'batch_size'}
            or config.get('dataset_sha256') != DATASET_SHA256):
        raise ValueError('fixed discovery capture configuration and source SHA required')
    if len(json.dumps(config, allow_nan=False).encode()) > 16 * 1024:
        raise ValueError('bounded capture configuration required')
    for key, value in fixed.items():
        if key in config and config[key] != value: raise ValueError('fixed capture recipe differs: ' + key)
    batch = config.get('batch_size', 32)
    if type(batch) is not int or not 1 <= batch <= 256:
        raise ValueError('batch_size must be a strict integer in [1,256]')
    if _safe(config['dataset']).suffix != '.jsonl': raise ValueError('JSONL source bank required')
    folder = _safe(config['run_dir'])
    if folder.exists() and not folder.is_dir(): raise ValueError('capture run_dir must be a directory')
    if folder.resolve() == _safe(config['dataset']).resolve() or folder.resolve() in _safe(config['dataset']).resolve().parents:
        raise ValueError('capture output must not contain its source dataset')
    return dict(fixed, batch_size=batch), folder


def _dataset(config):
    fixed, _ = _config(config)
    manifest = _json(Path(config['dataset']).with_suffix('.manifest.json'))
    if (manifest.get('status') != 'complete' or manifest.get('evaluation_role') != algebraic_programs.ROLE
            or manifest.get('role') != algebraic_programs.ROLE or manifest.get('sha256') != DATASET_SHA256
            or manifest.get('rows') != SOURCE_ROWS or manifest.get('generated_holdouts_opened') is not False):
        raise ValueError('complete pinned discovery source manifest required')
    data = _bytes(config['dataset'], 32 * 1024**2)
    if hashlib.sha256(data).hexdigest() != DATASET_SHA256: raise ValueError('source dataset checksum differs')
    rows = [json.loads(line) for line in data.splitlines() if line.strip()]
    if (len(rows) != SOURCE_ROWS or any(not isinstance(row, dict)
            or row.get('evaluation_role') != algebraic_programs.ROLE
            or row.get('split') not in ('train', 'development') for row in rows)):
        raise ValueError('all source rows must have discovery roles and training/development splits')
    generation = manifest.get('generation_config', {})
    if (generation.get('evaluation_role') != algebraic_programs.ROLE or generation.get('seed') != 20261027
            or generation.get('numeric_instances') != 4):
        raise ValueError('fixed algebraic source generation identity required')
    review = algebraic_programs.validate_rows(generation, rows)
    return rows, {'dataset_sha256': DATASET_SHA256, 'source_rows': len(rows),
        'split_rows': review['split_rows'], 'components': review['split_components'],
        'numeric_stratum_rows': review['numeric_stratum_rows'], 'layers': list(LAYERS), 'sites': list(SITES),
        'feature_shape': [len(rows), len(SITES), len(LAYERS), HIDDEN_SIZE], 'recipe': fixed}


def metadata(config):
    _, result = _dataset(config)
    return dict(result, status='passed', evaluation_role=ROLE, config_hash=digest(config),
                model=MODEL, model_revision=REVISION, new_model_queries=0, generated_holdouts_opened=False)


def _slurm():
    if not os.environ.get('SLURM_JOB_ID'): raise ValueError('tokenizer/model capture commands require SLURM')


def _verify_source(config, source):
    from .snapshots import verify
    snapshot = _safe(source['snapshot'])
    verified = verify(snapshot)
    if (verified['snapshot_id'] != source['snapshot_id'] or verified['code']['source_sha256'] != source['source_sha256']
            or _sha(snapshot/'frozen_manifest.json') != source['frozen_manifest_sha256']):
        raise ValueError('frozen capture source identity differs')
    found = False
    for name in verified['config_files']:
        path = snapshot/name
        if path.suffix == '.json' and path.stat().st_size <= 16 * 1024 and json.loads(path.read_text()) == config:
            found = True
            break
    if not found: raise ValueError('exact capture config must be frozen with its source')
    return verified


def _current_source(config):
    from .registry import ROOT
    from .snapshots import verify
    if not (ROOT/'frozen_manifest.json').is_file(): raise ValueError('capture requires an immutable source snapshot')
    frozen = verify(ROOT)
    result = {'snapshot': str(ROOT.resolve()), 'snapshot_id': frozen['snapshot_id'],
        'source_sha256': frozen['code']['source_sha256'], 'frozen_manifest_sha256': _sha(ROOT/'frozen_manifest.json')}
    _verify_source(config, result)
    return result


def _record(row):
    result = {key: row[key] for key in RECORD_FIELDS}
    result['numeric_stratum'] = row['targets']['numeric_stratum']
    return result


def _tokenizer(config):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True, use_fast=True)
    configure_tokenizer(tokenizer, {'model': MODEL, 'tokenization_mode': 'native'})
    if not tokenizer.is_fast or not tokenizer.chat_template: raise ValueError('cached native fast chat tokenizer required')
    return tokenizer


def layout_case(tokenizer, row, config, index):
    """Save exact token visibility; a checkpoint token may extend only into whitespace."""
    recipe, _ = _config(config)
    content = INSTRUCTION + '\n\n' + row['source']
    prompt = tokenizer.apply_chat_template([{'role': 'user', 'content': content}],
                tokenize=False, add_generation_prompt=True) + 'Output:'
    if prompt.count(row['source']) != 1: raise ValueError('source must occur exactly once in native prompt')
    encoded = tokenizer(prompt, add_special_tokens=False, return_offsets_mapping=True)
    tokens, offsets = encoded['input_ids'], encoded['offset_mapping']
    if (not tokens or len(tokens) != len(offsets) or len(tokens) > recipe['context_limit']
            or any(type(token) is not int or token < 0 for token in tokens)):
        raise ValueError('invalid or oversized native token layout')
    start = prompt.index(row['source'])
    lines = row['source'].splitlines()
    if len(lines) != 9: raise ValueError('eight assignments and one query required')
    positions, character_ends = [], []
    for statement in range(8):
        end = start + sum(len(line) + 1 for line in lines[:statement]) + len(lines[statement].rstrip())
        candidates = [i for i, (a, b) in enumerate(offsets) if a <= end - 1 < b]
        if len(candidates) != 1: raise ValueError('checkpoint final character must have one token')
        position = candidates[0]
        character_end = offsets[position][1]
        if character_end < end or prompt[end:character_end].strip():
            raise ValueError('checkpoint token exposes later code')
        positions.append(position); character_ends.append(character_end)
    positions.append(len(tokens) - 1); character_ends.append(len(prompt))
    if positions != sorted(set(positions)): raise ValueError('capture positions must increase strictly')
    prefixes = [tokens[:position + 1] for position in positions]
    texts = [tokenizer.decode(prefix, skip_special_tokens=False, clean_up_tokenization_spaces=False) for prefix in prefixes]
    if any(text != prompt[:end] for text, end in zip(texts, character_ends)):
        raise ValueError('decoded token prefix differs from its exact prompt visibility')
    chunk_first = index // recipe['chunk_size'] * recipe['chunk_size']
    return {'record': _record(row), 'prompt': prompt, 'input_token_ids': tokens,
        'token_offsets': [list(pair) for pair in offsets], 'source_start': start,
        'sites': list(SITES), 'positions': positions, 'visible_prefixes': texts,
        'prefix_character_ends': character_ends, 'prefix_token_ids': prefixes,
        'prefix_sha256': [digest(prefix) for prefix in prefixes],
        'capture_batch_start': chunk_first + (index - chunk_first) // recipe['batch_size'] * recipe['batch_size'],
        'batch_padded_width': len(tokens), 'physical_positions': list(positions)}


def _batch_geometry(cases, *, assign=False):
    widths = {}
    for case in cases:
        batch = case['capture_batch_start']
        widths[batch] = max(widths.get(batch, 0), len(case['input_token_ids']))
    for case in cases:
        width = widths[case['capture_batch_start']]
        physical = [width - len(case['input_token_ids']) + p for p in case['positions']]
        if assign:
            case.update(batch_padded_width=width, physical_positions=physical)
        elif case.get('batch_padded_width') != width or case.get('physical_positions') != physical:
            raise ValueError('prepared batch padding geometry differs')


def prepare(config):
    recipe, folder = _config(config)
    _slurm(); source = _current_source(config)
    rows, source_review = _dataset(config)  # All roles, groups and splits checked before tokenizer load.
    registration = {'schema_version': 1, 'evaluation_role': ROLE, 'config': config, 'config_hash': digest(config),
        'source': source, 'source_review': source_review, 'model': MODEL, 'model_revision': REVISION,
        'tokenizer_revision': REVISION, 'execution_backend': BACKEND,
        'prompt_contract': {'user_instruction': INSTRUCTION, 'source_separator': '\n\n',
            'native_single_user_chat': True, 'add_generation_prompt': True, 'assistant_suffix': 'Output:'},
        'new_model_queries': 0, 'generated_holdouts_opened': False}
    # A different source/config cannot touch a pre-existing registration or layout.
    _put(folder/'registration.json', registration)
    tokenizer = _tokenizer(config)
    cases = [layout_case(tokenizer, row, config, i) for i, row in enumerate(rows)]
    _batch_geometry(cases, assign=True)
    payload = ''.join(json.dumps(case, sort_keys=True) + '\n' for case in cases).encode()
    if len(payload) > MAX_PREPARED: raise ValueError('prepared token layouts exceed byte bound')
    _publish(folder/'prepared_cases.jsonl', payload)
    result = {'status': 'passed', 'evaluation_role': ROLE, 'config_hash': digest(config), 'source': source,
        'registration_sha256': _sha(folder/'registration.json'), 'dataset_sha256': DATASET_SHA256,
        'cases': len(cases), 'prepared_sha256': hashlib.sha256(payload).hexdigest(),
        'model': MODEL, 'model_revision': REVISION, 'tokenizer_revision': REVISION,
        'chat_template_sha256': hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        'recipe': recipe, 'source_review': source_review, 'new_model_queries': 0,
        'generated_holdouts_opened': False}
    _put(folder/'preflight.json', result)
    return result


def _case_check(case, row, config, index):
    recipe, _ = _config(config)
    if case.get('record') != _record(row) or case.get('sites') != list(SITES):
        raise ValueError('prepared source row identity differs')
    tokens, offsets, prompt = case['input_token_ids'], case['token_offsets'], case['prompt']
    if (not isinstance(prompt, str) or len(prompt) > 32 * 1024 or not prompt.endswith('Output:')
            or not tokens or len(tokens) > recipe['context_limit'] or len(offsets) != len(tokens)
            or any(type(token) is not int or token < 0 for token in tokens)
            or prompt.count(row['source']) != 1 or case['source_start'] != prompt.index(row['source'])
            or INSTRUCTION + '\n\n' + row['source'] not in prompt):
        raise ValueError('prepared prompt or token layout differs')
    positions = case['positions']
    if (len(positions) != 9 or any(type(p) is not int or not 0 <= p < len(tokens) for p in positions)
            or positions != sorted(set(positions)) or positions[-1] != len(tokens) - 1
            or any(len(case[key]) != 9 for key in ('visible_prefixes', 'prefix_character_ends', 'prefix_token_ids', 'prefix_sha256'))):
        raise ValueError('prepared checkpoint coverage differs')
    lines = row['source'].splitlines()
    for site, (position, end, text, prefix, checksum) in enumerate(zip(positions,
            case['prefix_character_ends'], case['visible_prefixes'], case['prefix_token_ids'], case['prefix_sha256'])):
        if (type(end) is not int or not 0 < end <= len(prompt) or text != prompt[:end]
                or prefix != tokens[:position + 1] or checksum != digest(prefix)):
            raise ValueError('prepared visible prefix differs')
        if site < 8:
            statement_end = case['source_start'] + sum(len(line) + 1 for line in lines[:site]) + len(lines[site].rstrip())
            a, b = offsets[position]
            if not a <= statement_end - 1 < b or b != end or prompt[statement_end:b].strip():
                raise ValueError('prepared checkpoint leaks later code')
        elif end != len(prompt): raise ValueError('pre_answer must see the whole prompt')
    chunk_first = index // recipe['chunk_size'] * recipe['chunk_size']
    if case['capture_batch_start'] != chunk_first + (index - chunk_first) // recipe['batch_size'] * recipe['batch_size']:
        raise ValueError('recorded prefill batch differs')
    width = case['batch_padded_width']
    if (type(width) is not int or not len(tokens) <= width <= recipe['context_limit']
            or case['physical_positions'] != [width - len(tokens) + p for p in positions]):
        raise ValueError('recorded physical prefill positions differ')


def inputs(config):
    """Validate all bounded identity metadata and source rows before bulk arrays."""
    _, folder = _config(config)
    registration = _json(folder/'registration.json')
    if (registration.get('evaluation_role') != ROLE or registration.get('config') != config
            or registration.get('config_hash') != digest(config)
            or registration.get('generated_holdouts_opened') is not False):
        raise ValueError('capture registration identity differs')
    _verify_source(config, registration['source'])
    rows, review = _dataset(config)
    if registration.get('source_review') != review: raise ValueError('registered source review differs')
    preflight = _json(folder/'preflight.json')
    if (preflight.get('status') != 'passed' or preflight.get('evaluation_role') != ROLE
            or preflight.get('config_hash') != digest(config) or preflight.get('source') != registration['source']
            or preflight.get('registration_sha256') != _sha(folder/'registration.json')
            or preflight.get('dataset_sha256') != DATASET_SHA256 or preflight.get('cases') != SOURCE_ROWS
            or preflight.get('recipe') != review['recipe'] or preflight.get('source_review') != review
            or preflight.get('model') != MODEL or preflight.get('model_revision') != REVISION
            or preflight.get('tokenizer_revision') != REVISION or preflight.get('generated_holdouts_opened') is not False):
        raise ValueError('passing matching token-layout preflight required')
    data = _bytes(folder/'prepared_cases.jsonl', MAX_PREPARED)
    if hashlib.sha256(data).hexdigest() != preflight['prepared_sha256']:
        raise ValueError('prepared token layouts checksum differs')
    cases = [json.loads(line) for line in data.splitlines() if line.strip()]
    if len(cases) != len(rows): raise ValueError('prepared source coverage differs')
    for index, (case, row) in enumerate(zip(cases, rows)): _case_check(case, row, config, index)
    _batch_geometry(cases)
    return preflight, cases


def _prefix_check(features, cases):
    references, comparisons, maximum = {}, 0, 0.
    for i, case in enumerate(cases):
        for site, prefix in enumerate(case['prefix_token_ids']):
            key = (case['capture_batch_start'], len(case['input_token_ids']),
                   case['physical_positions'][site], tuple(prefix))
            if key in references:
                previous_i, previous_site = references[key]
                difference = float(np.max(np.abs(features[i, site] - features[previous_i, previous_site])))
                comparisons += 1; maximum = max(maximum, difference)
                if difference > ATOL: raise ValueError('identical causal prefixes differ at matching prefill geometry')
            else: references[key] = i, site
    return comparisons, maximum


def _padding_diagnostics(features, cases):
    references, comparisons, maximum = {}, 0, 0.
    for i, case in enumerate(cases):
        for site, prefix in enumerate(case['prefix_token_ids']):
            key = case['capture_batch_start'], tuple(prefix)
            if key in references:
                other, other_site = references[key]
                geometry = len(case['input_token_ids']), case['physical_positions'][site]
                other_geometry = len(cases[other]['input_token_ids']), cases[other]['physical_positions'][other_site]
                if geometry != other_geometry:
                    comparisons += 1
                    maximum = max(maximum, float(np.max(np.abs(features[i, site] - features[other, other_site]))))
            else: references[key] = i, site
    return comparisons, maximum


def validate_chunk(features, cases):
    if (features.dtype != np.float32 or features.shape != (len(cases), 9, 4, HIDDEN_SIZE)
            or not np.isfinite(features).all()):
        raise ValueError('capture dtype, shape or finiteness differs')
    return _prefix_check(features, cases)


def load_chunk(entry, cases):
    """Read the same checksum-verified bounded bytes that are decoded as arrays."""
    maximum = len(cases) * 9 * 4 * HIDDEN_SIZE * 4 + MAX_JSON + 65536
    payload = _bytes(entry['path'], maximum)
    if hashlib.sha256(payload).hexdigest() != entry['sha256']: raise ValueError('capture chunk checksum differs')
    with np.load(io.BytesIO(payload), allow_pickle=False) as saved:
        if set(saved.files) != {'features', 'metadata'}: raise ValueError('exact capture array inventory required')
        metadata_array = saved['metadata']
        if metadata_array.dtype != np.uint8 or metadata_array.ndim != 1 or metadata_array.size > MAX_JSON:
            raise ValueError('bounded capture metadata array required')
        if json.loads(metadata_array.tobytes()) != cases: raise ValueError('capture chunk row identity differs')
        features = saved['features']
    checks = validate_chunk(features, cases)
    return features, checks


def _models(config):
    import torch
    from transformers import AutoModelForCausalLM
    tokenizer = _tokenizer(config)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION, local_files_only=True,
        dtype=torch.bfloat16, device_map='cuda', attn_implementation='sdpa')
    model.eval()
    if (model.config.hidden_size != HIDDEN_SIZE or model.config.num_hidden_layers != 32
            or model.config._attn_implementation != 'sdpa' or next(model.parameters()).dtype != torch.bfloat16):
        raise ValueError('actual checkpoint geometry, dtype or attention backend differs')
    return tokenizer, model


def _forward(tokenizer, model, cases):
    import torch
    from codecue.patching import decoder_layers
    encoded = tokenizer([case['prompt'] for case in cases], add_special_tokens=False, padding=True, return_tensors='pt')
    width = encoded.input_ids.shape[1]
    physical = []
    for i, case in enumerate(cases):
        mask = encoded.attention_mask[i].bool()
        padding = width - len(case['input_token_ids'])
        if (encoded.input_ids[i][mask].tolist() != case['input_token_ids']
                or encoded.attention_mask[i].tolist() != [0] * padding + [1] * len(case['input_token_ids'])
                or case['batch_padded_width'] != width
                or case['physical_positions'] != [padding + p for p in case['positions']]):
            raise ValueError('left-padded prefill input differs from prepared tokens')
        physical.append([padding + position for position in case['positions']])
    encoded = encoded.to(model.device)
    position_ids = encoded.attention_mask.long().cumsum(-1) - 1
    position_ids.masked_fill_(encoded.attention_mask == 0, 0)
    positions = torch.tensor(physical, device=model.device)
    indices = torch.arange(len(cases), device=model.device)[:, None]
    captured, handles = {}, []
    blocks = decoder_layers(model)
    for layer in LAYERS:
        def hook(module, args, output, layer=layer):
            hidden = output[0] if isinstance(output, tuple) else output
            if hidden.shape[:2] != (len(cases), width) or layer in captured:
                raise ValueError('unexpected decoder hook shape or repeated invocation')
            captured[layer] = hidden[indices, positions].detach().float().cpu().numpy()
        handles.append(blocks[layer].register_forward_hook(hook))
    try:
        with torch.inference_mode():
            # Avoid materializing a vocabulary-logit tensor for a feature-only capture.
            model.model(**encoded, position_ids=position_ids, use_cache=False,
                        output_hidden_states=False, return_dict=True)
    finally:
        for handle in handles: handle.remove()
    if set(captured) != set(LAYERS): raise ValueError('missing decoder capture layer')
    features = np.stack([captured[layer] for layer in LAYERS], axis=2)
    validate_chunk(features, cases)
    return features


def _monitor():
    from .gpu_telemetry import UUIDMonitor
    return UUIDMonitor()


def _runtime(model):
    import importlib.metadata
    import torch
    return {'device_name': torch.cuda.get_device_name(),
        'gpu_uuid': str(getattr(torch.cuda.get_device_properties(0), 'uuid', 'unavailable')),
        'torch_peak_allocated_bytes': torch.cuda.max_memory_allocated(),
        'dtype': str(next(model.parameters()).dtype), 'attention_backend': model.config._attn_implementation,
        'versions': {name: importlib.metadata.version(name) for name in ('torch', 'transformers')},
        'position_ids': '(attention_mask.cumsum(-1)-1).clamp_min(0)', 'use_cache': False,
        'forward': 'causal-LM model.model backbone; no vocabulary logits or generation',
        'gpu_scope': 'Current attempt prefill capture and chunk commits after model load; excludes model loading.'}


def _entry(folder, first, rows):
    return {'path': str(folder/'chunks'/f'{first:06d}.npz'), 'first': first, 'rows': rows}


def _commit_chunk(path, payload):
    """An interrupted write leaves a temporary file, never a partial committed NPZ."""
    path = _safe(path)
    if path.is_symlink(): raise ValueError('capture output files must not be symbolic links')
    pending = path.with_name('.' + path.name + '.pending')
    if path.exists():
        immutable(path, payload)
        return
    created = False
    try:
        # Exclusive creation must never follow an existing temporary symlink.
        with pending.open('xb') as stream:
            created = True
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        try: os.link(pending, path)
        except FileExistsError:
            if path.is_symlink(): raise ValueError('capture output files must not be symbolic links')
            immutable(path, payload)
    finally:
        if created and pending.exists(): pending.unlink()


def _attempt_loaded(attempt):
    # Older completed captures recorded successful loading only in runtime.
    return attempt.get('model_loaded') is True or bool(attempt.get('runtime'))


def _recover_summary(config, previous, identity):
    """Finish metadata commit after all immutable capture results were saved."""
    folder = Path(config['run_dir'])
    summary = _json(folder/'summary.json')
    candidate = dict(previous, status='complete', identity=identity, chunks=summary.get('chunks'),
        attempts=summary.get('collection_attempts'), summary_sha256=_sha(folder/'summary.json'))
    for key in ('model_prefill_cases', 'prefill_batch_calls', 'model_loaded', 'generated_responses', 'generation_calls'):
        candidate[key] = summary.get(key)
    # Verify a candidate without publishing a complete manifest first.
    _, _, cases, _, _ = _completed_base(config, manifest=candidate)
    for entry in candidate['chunks']:
        load_chunk(entry, cases[entry['first']:entry['first'] + entry['rows']])
    if previous.get('error'):
        failures = list(previous.get('finalization_errors', []))
        if previous['error'] not in failures: failures.append(previous['error'])
        candidate['finalization_errors'] = failures
    candidate.pop('error', None)
    write_json(folder/'manifest.json', candidate)
    return summary


def _manifest_base(config, preflight):
    return {'evaluation_role': ROLE, 'config': config, 'config_hash': digest(config),
        'source': preflight['source'], 'dataset_sha256': DATASET_SHA256,
        'preflight_sha256': _sha(Path(config['run_dir'])/'preflight.json'),
        'model': MODEL, 'model_revision': REVISION, 'tokenizer_revision': REVISION,
        'layers': list(LAYERS), 'sites': list(SITES), 'hidden_size': HIDDEN_SIZE,
        'stored_dtype': 'float32', 'execution_backend': BACKEND,
        'prefix_atol': ATOL, 'prefix_check_scope': PREFIX_SCOPE,
        'generated_responses': 0, 'generation_calls': 0, 'generated_holdouts_opened': False}


def run(config):
    recipe, folder = _config(config)
    _slurm(); source = _current_source(config)
    preflight, cases = inputs(config)
    if source != preflight['source']: raise ValueError('running source differs from registered capture source')
    identity = _manifest_base(config, preflight)
    manifest_path = folder/'manifest.json'
    import fcntl
    folder.mkdir(parents=True, exist_ok=True)
    with (folder/'capture.lock').open('a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc: raise ValueError('another capture process owns this run') from exc
        # Read state after acquiring the lock: a previous writer may just have
        # finished between our source checks and lock acquisition.
        previous = _json(manifest_path) if manifest_path.exists() else {'identity': identity, 'attempts': []}
        if previous.get('identity') != identity: raise ValueError('capture resume identity differs')
        if previous.get('status') == 'complete':
            _completed_base(config)
            return _json(folder/'summary.json')
        if (folder/'summary.json').exists(): return _recover_summary(config, previous, identity)
        if previous.get('error') and previous['attempts']:
            previous['attempts'][-1].setdefault('error', previous['error'])
        for attempt in previous['attempts']:
            if attempt.get('status') is None:
                attempt.update(status='interrupted', completion_observation='Process ended before its final attempt record; durable counters retained.')
        manifest = dict(previous, status='started', attempts=[*previous['attempts'], {
            'slurm_job_id': os.environ['SLURM_JOB_ID'], 'prefill_batch_calls': 0,
            'prefill_cases_attempted': 0, 'prefill_cases_returned': 0, 'model_loaded': False}])
        manifest.pop('error', None)
        write_json(manifest_path, manifest)
        started = time.monotonic()
        try:
            (folder/'chunks').mkdir(exist_ok=True)
            expected_names = {f'{first:06d}.npz' for first in range(0, len(cases), recipe['chunk_size'])}
            pending_names = {'.' + name + '.pending' for name in expected_names}
            if any(path.name not in expected_names | pending_names for path in (folder/'chunks').iterdir()):
                raise ValueError('unexpected existing capture chunk artifact')
            for path in (folder/'chunks').iterdir():
                if path.name in pending_names: path.unlink()  # Only this writer's uncommitted temporary bytes.
            entries, comparisons, maximum, pending = [], 0, 0., []
            geometry_comparisons, geometry_maximum = 0, 0.
            pins = {}
            for entry in previous.get('chunks', []):
                target = _entry(folder, entry['first'], min(recipe['chunk_size'], len(cases) - entry['first']))
                if (entry['first'] in pins or entry['first'] not in range(0, len(cases), recipe['chunk_size'])
                        or set(entry) != set(target) | {'sha256'} or any(entry.get(k) != v for k, v in target.items())
                        or not isinstance(entry['sha256'], str) or len(entry['sha256']) != 64):
                    raise ValueError('partial capture checksum inventory differs')
                pins[entry['first']] = entry
            for first in range(0, len(cases), recipe['chunk_size']):
                selected = cases[first:first + recipe['chunk_size']]
                entry = _entry(folder, first, len(selected))
                if Path(entry['path']).exists():
                    if first not in pins: raise ValueError('committed capture chunk lacks a durable checksum pin')
                    entry = pins[first]
                    features, (checks, difference) = load_chunk(entry, selected)
                    comparisons += checks; maximum = max(maximum, difference)
                    checks, difference = _padding_diagnostics(features, selected)
                    geometry_comparisons += checks; geometry_maximum = max(geometry_maximum, difference)
                    entries.append(entry)
                else: pending.append((first, selected))
            if pending:
                manifest['attempts'][-1]['model_load_attempted'] = True
                write_json(manifest_path, manifest)
                tokenizer, model = _models(config)
                manifest['attempts'][-1]['model_loaded'] = True
                write_json(manifest_path, manifest)
                if hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() != preflight['chat_template_sha256']:
                    raise ValueError('runtime native chat template differs')
                with _monitor() as monitor:
                    try:
                        for first, selected in pending:
                            batches = []
                            for offset in range(0, len(selected), recipe['batch_size']):
                                batch = selected[offset:offset + recipe['batch_size']]
                                attempt = manifest['attempts'][-1]
                                attempt['prefill_batch_calls'] += 1
                                attempt['prefill_cases_attempted'] += len(batch)
                                write_json(manifest_path, manifest)  # Durable attempt before each new model call.
                                batches.append(_forward(tokenizer, model, batch))
                                attempt['prefill_cases_returned'] += len(batch)
                            features = np.concatenate(batches)
                            checks, difference = validate_chunk(features, selected)
                            comparisons += checks; maximum = max(maximum, difference)
                            checks, difference = _padding_diagnostics(features, selected)
                            geometry_comparisons += checks; geometry_maximum = max(geometry_maximum, difference)
                            path = folder/'chunks'/f'{first:06d}.npz'
                            buffer = io.BytesIO()
                            np.savez(buffer, features=features, metadata=np.frombuffer(json.dumps(selected, sort_keys=True).encode(), dtype=np.uint8))
                            payload = buffer.getvalue()
                            entry = dict(_entry(folder, first, len(selected)), sha256=hashlib.sha256(payload).hexdigest())
                            pins[first] = entry
                            manifest['chunks'] = [pins[key] for key in sorted(pins)]
                            write_json(manifest_path, manifest)  # Pin expected bytes BEFORE atomic chunk publication.
                            _commit_chunk(path, payload)
                            entries.append(entry)
                            write_json(folder/'progress.json', {'complete': False, 'captured_rows': sum(e['rows'] for e in entries), 'planned': len(cases)})
                            print(f'capture {sum(e["rows"] for e in entries)}/{len(cases)}', flush=True)
                    finally:
                        manifest['attempts'][-1]['runtime'] = dict(_runtime(model), gpu=monitor.summary())
            entries.sort(key=lambda entry: entry['first'])
            manifest['attempts'][-1].update(status='complete', wall_seconds=time.monotonic() - started)
            summary = dict(identity, complete=True, cases=len(cases), feature_shape=[len(cases), 9, 4, HIDDEN_SIZE],
                chunks=entries, storage_bytes=sum(Path(entry['path']).stat().st_size for entry in entries),
                prefix_comparisons=comparisons, prefix_max_abs_diff=maximum,
                different_padding_prefix_comparisons=geometry_comparisons, different_padding_prefix_max_abs_diff=geometry_maximum,
                model_loaded=any(_attempt_loaded(attempt) for attempt in manifest['attempts']),
                model_prefill_cases=len(cases), prefill_batch_calls=sum(a['prefill_batch_calls'] for a in manifest['attempts']),
                model_prefill_cases_attempted=sum(a['prefill_cases_attempted'] for a in manifest['attempts']),
                new_model_queries=sum(a['prefill_cases_attempted'] for a in manifest['attempts']),
                new_model_queries_semantics='Source-case prefill attempts, including any uncommitted retry work; no generation.',
                collection_attempts=manifest['attempts'],
                distinct_committed_prefill_rows=len(cases), committed_batch_groups=sum(math.ceil(entry['rows']/recipe['batch_size']) for entry in entries),
                interpretation='Raw prefill activations only; no decoded relation, model response, accuracy or causal-mechanism claim.')
            _put(folder/'summary.json', summary)
            manifest.update(status='complete', chunks=entries, summary_sha256=_sha(folder/'summary.json'))
            manifest.update(model_prefill_cases=len(cases), prefill_batch_calls=summary['prefill_batch_calls'],
                model_loaded=summary['model_loaded'], generated_responses=0, generation_calls=0)
            write_json(manifest_path, manifest)
            return summary
        except Exception as exc:
            finalizing = (folder/'summary.json').exists()
            manifest.update(status='finalizing' if finalizing else 'failed', error=f'{type(exc).__name__}: {exc}')
            if not finalizing: manifest['attempts'][-1].update(status='failed', error=manifest['error'], wall_seconds=time.monotonic() - started)
            write_json(manifest_path, manifest)
            raise


def _completed_base(config, *, manifest=None):
    recipe, folder = _config(config)
    preflight, cases = inputs(config)
    if manifest is None: manifest = _json(folder/'manifest.json')
    if manifest.get('status') != 'complete' or manifest.get('identity') != _manifest_base(config, preflight):
        raise ValueError('complete matching capture manifest required')
    summary = _json(folder/'summary.json', manifest.get('summary_sha256'))
    expected = [_entry(folder, first, min(recipe['chunk_size'], len(cases) - first))
                for first in range(0, len(cases), recipe['chunk_size'])]
    entries = manifest.get('chunks', [])
    if (len(entries) != len(expected) or summary.get('chunks') != entries or summary.get('complete') is not True
            or summary.get('cases') != len(cases) or summary.get('feature_shape') != [len(cases), 9, 4, HIDDEN_SIZE]
            or any(summary.get(key) != value for key, value in manifest['identity'].items())):
        raise ValueError('complete capture inventory/counts differ')
    for entry, target in zip(entries, expected):
        if (set(entry) != set(target) | {'sha256'} or any(entry.get(k) != v for k, v in target.items())
                or not isinstance(entry['sha256'], str) or len(entry['sha256']) != 64):
            raise ValueError('exact canonical capture chunk paths required')
    attempts = manifest.get('attempts', [])
    if (not attempts or attempts[-1].get('status') != 'complete'
            or any(not isinstance(attempt, dict) or attempt.get('status') not in ('failed', 'complete', 'interrupted')
            or any(type(attempt.get(key)) is not int or attempt[key] < 0 for key in
                   ('prefill_batch_calls', 'prefill_cases_attempted', 'prefill_cases_returned'))
            or attempt['prefill_cases_returned'] > attempt['prefill_cases_attempted']
            or not attempt['prefill_batch_calls'] <= attempt['prefill_cases_attempted'] <= attempt['prefill_batch_calls'] * recipe['batch_size']
            for attempt in attempts)):
        raise ValueError('capture attempt accounting differs')
    counts = {'model_prefill_cases': len(cases), 'model_prefill_cases_attempted': sum(a['prefill_cases_attempted'] for a in attempts),
        'prefill_batch_calls': sum(a['prefill_batch_calls'] for a in attempts),
        'new_model_queries': sum(a['prefill_cases_attempted'] for a in attempts),
        'distinct_committed_prefill_rows': len(cases),
        'committed_batch_groups': sum(math.ceil(e['rows']/recipe['batch_size']) for e in entries),
        'model_loaded': any(_attempt_loaded(a) for a in attempts), 'generated_responses': 0, 'generation_calls': 0}
    if (summary.get('collection_attempts') != attempts or counts['model_loaded'] is not True
            or counts['model_prefill_cases_attempted'] < len(cases)
            or counts['prefill_batch_calls'] < counts['committed_batch_groups']
            or any(summary.get(key) != value for key, value in counts.items())
            or any(manifest.get(key) != counts[key] for key in
                   ('model_prefill_cases', 'prefill_batch_calls', 'model_loaded', 'generated_responses', 'generation_calls'))):
        raise ValueError('completed capture prefill/generation accounting differs')
    if {path.resolve() for path in (folder/'chunks').iterdir()} != {Path(e['path']).resolve() for e in entries}:
        raise ValueError('capture chunk directory inventory differs')
    return folder, preflight, cases, manifest, summary


def _receipt(folder, preflight, manifest, summary, audit):
    return {'schema_version': 1, 'status': 'complete_exploratory', 'evaluation_role': ROLE,
        'config_hash': preflight['config_hash'], 'source': preflight['source'],
        'dataset_sha256': DATASET_SHA256, 'model': MODEL, 'model_revision': REVISION,
        'cases': summary['cases'], 'feature_shape': summary['feature_shape'],
        'metadata': {name: {'path': str(folder/name), 'sha256': _sha(folder/name)} for name in
                     ('registration.json', 'preflight.json', 'prepared_cases.jsonl', 'manifest.json', 'summary.json', 'audit.json')},
        'chunks': manifest['chunks'], 'prefix_comparisons': audit['prefix_comparisons'],
        'prefix_max_abs_diff': audit['prefix_max_abs_diff'], 'prefix_atol': ATOL, 'prefix_check_scope': PREFIX_SCOPE,
        'different_padding_prefix_comparisons': audit['different_padding_prefix_comparisons'],
        'different_padding_prefix_max_abs_diff': audit['different_padding_prefix_max_abs_diff'],
        'model_prefill_cases': summary['model_prefill_cases'], 'prefill_batch_calls': summary['prefill_batch_calls'],
        'model_prefill_cases_attempted': summary['model_prefill_cases_attempted'], 'model_loaded': summary['model_loaded'],
        'new_model_queries': summary['new_model_queries'], 'generated_responses': 0, 'generation_calls': 0,
        'generated_holdouts_opened': False}


def audit(config):
    folder, preflight, cases, manifest, summary = _completed_base(config)
    comparisons, maximum, geometry_comparisons, geometry_maximum = 0, 0., 0, 0.
    for entry in manifest['chunks']:
        selected = cases[entry['first']:entry['first'] + entry['rows']]
        features, (checks, difference) = load_chunk(entry, selected)
        comparisons += checks; maximum = max(maximum, difference)
        checks, difference = _padding_diagnostics(features, selected)
        geometry_comparisons += checks; geometry_maximum = max(geometry_maximum, difference)
    if (comparisons != summary['prefix_comparisons'] or maximum != summary['prefix_max_abs_diff']
            or geometry_comparisons != summary['different_padding_prefix_comparisons']
            or geometry_maximum != summary['different_padding_prefix_max_abs_diff']):
        raise ValueError('capture prefix checks differ from saved summary')
    result = {'status': 'passed', 'evaluation_role': ROLE, 'config_hash': digest(config),
        'source': preflight['source'], 'cases': len(cases), 'feature_shape': summary['feature_shape'],
        'chunks': manifest['chunks'], 'prefix_comparisons': comparisons, 'prefix_max_abs_diff': maximum,
        'prefix_atol': ATOL, 'prefix_check_scope': PREFIX_SCOPE, 'new_model_queries': 0,
        'source_model_prefill_cases': summary['model_prefill_cases'], 'source_prefill_batch_calls': summary['prefill_batch_calls'],
        'different_padding_prefix_comparisons': geometry_comparisons,
        'different_padding_prefix_max_abs_diff': geometry_maximum,
        'generated_responses': 0, 'generation_calls': 0,
        'finite_float32_features': True, 'generated_holdouts_opened': False}
    _put(folder/'audit.json', result)
    _put(folder/'completion_manifest_v1.json', _receipt(folder, preflight, manifest, summary, result))
    return result


def completed_metadata(config):
    """Guard the complete source/metadata/inventory chain before array access.

    Returned cases contain source programs and token visibility, never oracle
    values or responses. Use load_chunk(entry, cases_slice) for pinned arrays.
    """
    _, folder = _config(config)
    receipt = _json(folder/'completion_manifest_v1.json')
    if (receipt.get('status') != 'complete_exploratory' or receipt.get('evaluation_role') != ROLE
            or receipt.get('config_hash') != digest(config) or receipt.get('dataset_sha256') != DATASET_SHA256):
        raise ValueError('complete discovery capture receipt required')
    names = ('registration.json', 'preflight.json', 'prepared_cases.jsonl', 'manifest.json', 'summary.json', 'audit.json')
    if set(receipt.get('metadata', {})) != set(names): raise ValueError('exact completion metadata inventory required')
    for name in names:
        entry = receipt['metadata'][name]
        if (set(entry) != {'path', 'sha256'} or entry['path'] != str(folder/name)
                or not isinstance(entry['sha256'], str) or len(entry['sha256']) != 64):
            raise ValueError('completion metadata path/checksum differs')
    # Bounded registration, original frozen source and discovery row guards run
    # before even hashing the larger prepared JSONL payload through this reader.
    folder, preflight, cases, manifest, summary = _completed_base(config)
    for name in names:
        if _sha(folder/name) != receipt['metadata'][name]['sha256']:
            raise ValueError('completion metadata path/checksum differs')
    checked = _json(folder/'audit.json')
    if (checked.get('status') != 'passed' or checked.get('config_hash') != digest(config)
            or checked.get('source') != preflight['source'] or checked.get('cases') != len(cases)
            or checked.get('chunks') != manifest['chunks'] or checked.get('finite_float32_features') is not True
            or checked.get('generated_holdouts_opened') is not False
            or receipt != _receipt(folder, preflight, manifest, summary, checked)):
        raise ValueError('capture audit/receipt identity differs')
    return {'config': config, 'model': MODEL, 'model_revision': REVISION, 'source': preflight['source'],
        'dataset_sha256': DATASET_SHA256, 'layers': list(LAYERS), 'sites': list(SITES),
        'feature_shape': summary['feature_shape'], 'chunks': manifest['chunks'], 'cases': cases,
        'preflight': preflight, 'summary': summary, 'audit': checked, 'receipt': receipt}
