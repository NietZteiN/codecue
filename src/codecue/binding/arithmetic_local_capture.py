"""Frozen, resumable local arithmetic capture with explicit causal token spans."""
import hashlib
import io
import json
import os
from pathlib import Path
import time

import numpy as np

from . import arithmetic_local_programs as programs
from . import arithmetic_graph_capture as legacy
from . import relationship_capture as base
from .datasets import digest

ROLE = 'discovery_arithmetic_local_capture_v1'
MAX_PREPARED = 256 * 1024**2
MAX_CHUNK = 128 * 1024**2


def inputs_config(config):
    if (config.get('evaluation_role') != ROLE or config.get('chunk_size') != 32
            or config.get('batch_size') != 16 or config.get('instruction') != 0):
        raise ValueError('fixed local capture recipe required')
    if base._sha(config['declared_plan']) != config['declared_plan_sha256']:
        raise ValueError('declared local plan changed')
    profile = base._json(config['profile_config'], config['profile_config_sha256'])
    legacy._CORE._config(profile)
    # The audited model loader supplies cached revisions and memory checks. This
    # new experiment has a separately declared fixed batch and point geometry.
    profile = dict(profile, batch_size=config['batch_size'])
    source = base._bytes(config['dataset'], 64 * 1024**2)
    if hashlib.sha256(source).hexdigest() != config['dataset_sha256']:
        raise ValueError('local source bank changed')
    manifest = base._json(Path(config['dataset']).with_suffix('.manifest.json'), config['dataset_manifest_sha256'])
    rows = [json.loads(line) for line in source.splitlines()]
    if manifest['sha256'] != config['dataset_sha256'] or programs.validate(rows, independent=False)['rows'] != manifest['rows']:
        raise ValueError('source manifest differs')
    return profile, rows


def layout(tokenizer, row):
    from .model_adapter import normalize_prompt
    prompt = normalize_prompt(tokenizer, tokenizer.apply_chat_template(
        [{'role': 'user', 'content': programs.INSTRUCTIONS[0] + '\n\n' + row['source']}],
        tokenize=False, add_generation_prompt=True) + 'Output:')
    if prompt.count(row['source']) != 1:
        raise ValueError('one exact source occurrence required')
    encoded = tokenizer(prompt, add_special_tokens=False, return_offsets_mapping=True)
    tokens, offsets = encoded['input_ids'], encoded['offset_mapping']
    if not tokens or len(tokens) > 4096 or len(tokens) != len(offsets):
        raise ValueError('bounded native token layout required')
    start = prompt.index(row['source'])
    descriptors = programs.points(row)
    positions = []
    for point in descriptors:
        if point['kind'] == 'answer':
            positions.append(len(tokens) - 1)
            continue
        end = start + point['stop']
        matches = [i for i, (a, b) in enumerate(offsets) if a <= end - 1 < b]
        if len(matches) != 1:
            raise ValueError('one native token must cover the last span character')
        index = matches[0]
        if prompt[end:offsets[index][1]].strip():
            raise ValueError('capture token extends into future non-whitespace source')
        prefix = tokenizer.decode(tokens[:index + 1], skip_special_tokens=False, clean_up_tokenization_spaces=False)
        if prefix != prompt[:offsets[index][1]]:
            raise ValueError('native causal token prefix differs from source text')
        positions.append(index)
    if positions != sorted(positions):
        raise ValueError('capture points must be causally ordered')
    count = len(positions)
    positions += [positions[-1]] * (programs.MAX_POINTS - count)
    return dict(id=row['id'], prompt=prompt, input_token_ids=tokens,
        positions=positions, point_count=count, descriptors=descriptors,
        token_offsets=[list(o) for o in offsets],
        prefix_sha256=[digest(tokens[:p + 1]) for p in positions])


def validate_case(case, row):
    tokens, offsets, positions = case['input_token_ids'], case['token_offsets'], case['positions']
    if (case['id'] != row['id'] or case['descriptors'] != programs.points(row)
            or case['point_count'] != len(case['descriptors']) or len(positions) != programs.MAX_POINTS
            or positions != sorted(positions) or positions[-1] != len(tokens) - 1
            or len(tokens) != len(offsets) or not tokens or len(tokens) > 4096
            or any(type(p) is not int or not 0 <= p < len(tokens) for p in positions)
            or case['prefix_sha256'] != [digest(tokens[:p + 1]) for p in positions]):
        raise ValueError('prepared local point identity differs')
    start = case['prompt'].index(row['source'])
    for point, position in zip(case['descriptors'], positions):
        if point['kind'] == 'answer':
            continue
        end = start + point['stop']
        a, b = offsets[position]
        if not a <= end - 1 < b or case['prompt'][end:b].strip():
            raise ValueError('prepared point exposes future source')


def prepare(config):
    base._slurm()
    source = base._current_source(config)
    profile, rows = inputs_config(config)
    tokenizer = legacy._CORE._tokenizer(profile)
    cases = [layout(tokenizer, row) for row in rows]
    for case, row in zip(cases, rows):
        validate_case(case, row)
    payload = ''.join(json.dumps(c, sort_keys=True) + '\n' for c in cases).encode()
    if len(payload) > MAX_PREPARED:
        raise ValueError('prepared layouts exceed declared bound')
    folder = Path(config['run_dir'])
    base._publish(folder / 'prepared_cases.jsonl', payload)
    result = dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), source=source,
        cases=len(cases), prepared_sha256=hashlib.sha256(payload).hexdigest(),
        chat_template_sha256=hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        ordered_ids_sha256=digest([r['id'] for r in rows]), max_prompt_tokens=max(len(c['input_token_ids']) for c in cases),
        layers=profile['layers'], hidden_size=profile['hidden_size'], max_points=programs.MAX_POINTS,
        model=profile['model'], model_revision=profile['model_revision'], generated_holdouts_opened=False)
    base._put(folder / 'preflight.json', result)
    return result


def inputs(config):
    profile, rows = inputs_config(config)
    folder = Path(config['run_dir'])
    proof = base._json(folder / 'preflight.json')
    if proof.get('status') != 'passed' or proof['config_hash'] != digest(config):
        raise ValueError('passing native local preflight required')
    base._verify_source(config, proof['source'])
    payload = base._bytes(folder / 'prepared_cases.jsonl', MAX_PREPARED)
    if hashlib.sha256(payload).hexdigest() != proof['prepared_sha256']:
        raise ValueError('prepared layouts changed')
    cases = [json.loads(line) for line in payload.splitlines()]
    if len(cases) != len(rows) or digest([r['id'] for r in rows]) != proof['ordered_ids_sha256']:
        raise ValueError('complete ordered native layout coverage required')
    for case, row in zip(cases, rows):
        validate_case(case, row)
    return profile, rows, proof, cases


def forward(tokenizer, model, cases, profile):
    import torch
    from codecue.patching import decoder_layers
    encoded = tokenizer([c['prompt'] for c in cases], add_special_tokens=False, padding=True, return_tensors='pt')
    width = encoded.input_ids.shape[1]
    physical = []
    for i, case in enumerate(cases):
        pad = width - len(case['input_token_ids'])
        if (encoded.input_ids[i, pad:].tolist() != case['input_token_ids']
                or encoded.attention_mask[i].tolist() != [0] * pad + [1] * len(case['input_token_ids'])):
            raise ValueError('runtime left-padded token identity differs')
        physical.append([pad + p for p in case['positions']])
    encoded = encoded.to(model.device)
    position_ids = (encoded.attention_mask.long().cumsum(-1) - 1).clamp_min(0)
    positions = torch.tensor(physical, device=model.device)
    indices = torch.arange(len(cases), device=model.device)[:, None]
    captured, handles = {}, []
    blocks = decoder_layers(model)
    for layer in profile['layers']:
        def hook(module, args, output, layer=layer):
            hidden = output[0] if isinstance(output, tuple) else output
            if hidden.shape != (len(cases), width, profile['hidden_size']) or layer in captured:
                raise ValueError('unexpected local decoder tensor geometry')
            captured[layer] = hidden[indices, positions].detach()
        handles.append(blocks[layer].register_forward_hook(hook))
    try:
        with torch.inference_mode():
            model.model(**encoded, position_ids=position_ids, use_cache=False, output_hidden_states=False, return_dict=True)
    finally:
        for handle in handles:
            handle.remove()
    if set(captured) != set(profile['layers']):
        raise ValueError('all nominated local layers required')
    features = torch.stack([captured[layer] for layer in profile['layers']], dim=2).float().cpu().numpy()
    for i, case in enumerate(cases):
        features[i, case['point_count']:] = 0
    validate_features(features, cases, profile)
    # Identical prefixes are compared only within the actual batch/geometry.
    seen = {}
    for i, case in enumerate(cases):
        for j in range(case['point_count']):
            key = (len(case['input_token_ids']), physical[i][j], case['prefix_sha256'][j])
            if key in seen:
                a, b = seen[key]
                if not np.allclose(features[i, j], features[a, b], rtol=0, atol=1e-5):
                    raise ValueError('identical causal prefixes differ within batch geometry')
            else:
                seen[key] = (i, j)
    return features


def validate_features(features, cases, profile):
    expected = (len(cases), programs.MAX_POINTS, len(profile['layers']), profile['hidden_size'])
    if features.dtype != np.float32 or features.shape != expected or not np.isfinite(features).all():
        raise ValueError('finite float32 local feature geometry required')
    if any(np.any(features[i, case['point_count']:]) for i, case in enumerate(cases)):
        raise ValueError('unused local point padding must be zero')


def load_chunk(entry, cases, profile):
    payload = base._bytes(entry['path'], MAX_CHUNK)
    if hashlib.sha256(payload).hexdigest() != entry['sha256']:
        raise ValueError('local feature chunk changed')
    with np.load(io.BytesIO(payload), allow_pickle=False) as saved:
        if set(saved.files) != {'features', 'metadata'} or json.loads(saved['metadata'].tobytes()) != cases:
            raise ValueError('local feature row identities differ')
        features = saved['features']
    validate_features(features, cases, profile)
    return features


def run(config):
    from .confidence import _run_lock
    base._slurm()
    source = base._current_source(config)
    profile, rows, preflight, cases = inputs(config)
    if source != preflight['source']:
        raise ValueError('local preparation and collection source differ')
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return audit(config)
        identity = dict(evaluation_role=ROLE, source=source, config_hash=digest(config))
        journal = folder / 'manifest.json'
        previous = base._json(journal) if journal.exists() else dict(identity, attempts=[], chunks=[])
        if any(previous[k] != v for k, v in identity.items()):
            raise ValueError('local capture resume source/config differs')
        pins = {e['first']: e for e in previous['chunks']}
        if len(pins) != len(previous['chunks']):
            raise ValueError('duplicate local chunk pin')
        attempt = dict(slurm_job_id=os.environ['SLURM_JOB_ID'], model_loaded=False, prefill_cases_attempted=0, prefill_cases_returned=0)
        previous['attempts'].append(attempt)
        legacy._CORE._journal(journal, previous)
        pending = []
        for first in range(0, len(cases), config['chunk_size']):
            subset = cases[first:first + config['chunk_size']]
            path = folder / 'chunks' / f'{first:06d}.npz'
            if path.exists():
                if first not in pins or pins[first]['path'] != str(path) or pins[first]['rows'] != len(subset):
                    raise ValueError('committed local chunk lacks matching durable pin')
                load_chunk(pins[first], subset, profile)
            else:
                pending.append((first, subset, path))
        started = time.monotonic()
        try:
            if pending:
                tokenizer, model = legacy._CORE.load_models(profile, max_prompt_tokens=preflight['max_prompt_tokens'])
                attempt['model_loaded'] = True
                if hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() != preflight['chat_template_sha256']:
                    raise ValueError('runtime native chat template differs')
                with base._monitor() as monitor:
                    try:
                        for first, subset, path in pending:
                            batches = []
                            for offset in range(0, len(subset), config['batch_size']):
                                batch = subset[offset:offset + config['batch_size']]
                                attempt['prefill_cases_attempted'] += len(batch)
                                legacy._CORE._journal(journal, previous)
                                batches.append(forward(tokenizer, model, batch, profile))
                                attempt['prefill_cases_returned'] += len(batch)
                            features = np.concatenate(batches)
                            stream = io.BytesIO()
                            np.savez_compressed(stream, features=features,
                                metadata=np.frombuffer(json.dumps(subset, sort_keys=True).encode(), dtype=np.uint8))
                            payload = stream.getvalue()
                            if len(payload) > MAX_CHUNK:
                                raise ValueError('local chunk exceeds declared byte bound')
                            pins[first] = dict(path=str(path), first=first, rows=len(subset), sha256=hashlib.sha256(payload).hexdigest())
                            previous['chunks'] = [pins[i] for i in sorted(pins)]
                            legacy._CORE._journal(journal, previous)
                            base._publish(path, payload)
                            legacy._CORE._journal(folder / 'progress.json', dict(captured_rows=sum(e['rows'] for e in pins.values()), planned=len(cases)))
                            print(f'local capture {first + len(subset)}/{len(cases)}', flush=True)
                    finally:
                        attempt['runtime'] = dict(base._runtime(model), gpu=monitor.summary())
            attempt.update(status='complete', wall_seconds=time.monotonic() - started)
            previous['chunks'] = [pins[i] for i in sorted(pins)]
            summary = dict(identity, status='complete_exploratory', cases=len(cases), chunks=previous['chunks'],
                attempts=previous['attempts'], layers=profile['layers'], hidden_size=profile['hidden_size'],
                model=profile['model'], new_generated_answers=0, generated_holdouts_opened=False)
            base._put(folder / 'summary.json', summary)
            base._put(folder / 'completion_manifest_v1.json', dict(identity, status='complete_exploratory',
                artifacts=dict(summary=dict(path=str(folder / 'summary.json'), sha256=base._sha(folder / 'summary.json')))))
            legacy._CORE._journal(journal, dict(previous, status='complete'))
            return summary
        except Exception as exc:
            attempt.update(status='failed', error=f'{type(exc).__name__}: {exc}', wall_seconds=time.monotonic() - started)
            legacy._CORE._journal(journal, previous)
            raise


def audit(config):
    profile, rows, proof, cases = inputs(config)
    folder = Path(config['run_dir'])
    receipt = base._json(folder / 'completion_manifest_v1.json')
    if receipt['status'] != 'complete_exploratory' or receipt['config_hash'] != digest(config) or receipt['source'] != proof['source']:
        raise ValueError('local completion identity differs')
    entry = receipt['artifacts']['summary']
    summary = base._json(entry['path'], entry['sha256'])
    expected = list(range(0, len(cases), config['chunk_size']))
    if [e['first'] for e in summary['chunks']] != expected or summary['cases'] != len(rows):
        raise ValueError('complete ordered local chunk coverage required')
    for entry in summary['chunks']:
        first = entry['first']
        load_chunk(entry, cases[first:first + config['chunk_size']], profile)
    return receipt
