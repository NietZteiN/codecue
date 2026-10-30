"""Chunked extraction of raw block outputs at audited prefix-visible sites."""
from __future__ import annotations
import json
import time
from pathlib import Path
import numpy as np
from .behavior import select
from .datasets import read_jsonl, write_json
from .registry import guarded


def extraction_rows(rows,config):
    rows=select(rows,config,'extraction_splits')
    conditions=config.get('extraction_conditions_by_split')
    if conditions is not None:
        if set(conditions) != set(config['extraction_splits']) or any(
            not values or not set(values) <= {'neutral','informative','misleading'} for values in conditions.values()):
            raise ValueError('declare valid extraction naming conditions for every requested split')
        rows=[r for r in rows if r['condition'] in conditions[r['split']]]
    if not rows:
        raise ValueError('no activation samples selected')
    return rows


def labels_at(record, statement):
    point = record['execution_trace'][statement]
    width = len(record.get('variable_slots', {f'v{i}':i for i in range(4)}))
    values = [point['values'].get(f'v{i}') for i in range(width)]
    previous = []
    for i in range(width):
        versions = [p['value'] for p in record['execution_trace'][:statement+1]
                    if p['definition'].startswith(f'v{i}@')]
        previous.append(versions[-2] if len(versions) >= 2 else None)
    return {'current': values, 'previous': previous,
            'multiset': sorted(v for v in values if v is not None) + [None] * values.count(None)}


@guarded
def extract(config):
    import torch
    from codecue.patching import decoder_layers
    from .model_adapter import load, prompt_for, layout
    from .registry import begin, finish
    out, manifest = begin(config, 'activations')
    started = time.monotonic()
    rows = extraction_rows(read_jsonl(config['dataset']), config)
    tokenizer, model = load(config)
    blocks = decoder_layers(model)
    if any(l < 0 or l >= len(blocks) for l in config['layers']):
        raise ValueError('extraction block outside model')
    index_path = out / 'index.jsonl'
    previous = read_jsonl(index_path) if index_path.exists() else []
    done = {r['id'] for r in previous}
    size = sum(p.stat().st_size for p in out.glob('*.npz'))
    device_seconds = 0.0
    for r in rows:
        if r['id'] in done:
            continue
        prompt = prompt_for(tokenizer, r, config['protocol'])
        aligned = layout(tokenizer, r, prompt)
        sites = list(aligned['positions'])
        positions = list(aligned['positions'].values())
        width = model.config.hidden_size
        expected_bytes = len(sites) * len(config['layers']) * width * 2
        if size + expected_bytes + 4096 > config['activation_limit_bytes']:
            break
        captured, handles = {}, []
        def hook_for(layer):
            def hook(module, args, output):
                hidden = output[0] if isinstance(output, tuple) else output
                captured[layer] = hidden[0, positions, :].detach().to(dtype=torch.float16).cpu().numpy()
            return hook
        try:
            for layer in config['layers']:
                handles.append(blocks[layer].register_forward_hook(hook_for(layer)))
            torch.cuda.synchronize() if config['device'] == 'cuda' else None
            start = time.monotonic()
            with torch.inference_mode():
                model(input_ids=torch.tensor([aligned['input_ids']], device=model.device), use_cache=False)
            torch.cuda.synchronize() if config['device'] == 'cuda' else None
            device_seconds += time.monotonic() - start
        finally:
            for handle in handles:
                handle.remove()
        hidden = np.stack([captured[l] for l in config['layers']], axis=1)
        from .datasets import digest
        filename = digest(r['id']) + '.npz'
        temp = out / (filename + '.tmp')
        with temp.open('wb') as f:
            np.savez(f, hidden=hidden)
        temp.replace(out / filename)
        size += (out / filename).stat().st_size
        checkpoints = []
        for site in sites:
            statement = int(site.split(':')[1]) if site.startswith('statement:') else len(r['execution_trace']) - 1
            checkpoints.append({'site': site, 'execution_prefix_last_statement': statement,
                                **labels_at(r, statement)})
        item = {'id': r['id'], 'base_id': r['base_id'], 'template_id': r['template_id'], 'cluster_id': r['cluster_id'],
                'split': r['split'], 'condition': r['condition'], 'control_kind': r['control_kind'],
                'file': filename, 'shape': list(hidden.shape), 'dtype': 'float16', 'sites': sites,
                'layers': config['layers'], 'checkpoints': checkpoints,
                'token_positions': aligned['positions'], 'token_offsets': aligned['offsets'],
                'token_counts': aligned['token_counts'], 'input_token_ids': aligned['input_ids'],
                'hook_convention': aligned['hook_convention']}
        with index_path.open('a') as f:
            f.write(json.dumps(item) + '\n')
        done.add(r['id'])
        if len(done) % 24 == 0:
            print(f'extract {len(done)}/{len(rows)}; {size} bytes', flush=True)
    complete = len(done) == len(rows)
    finish(out, manifest, time.monotonic() - started, 'complete' if complete else 'budget_limited',
           artifact_bytes=size, samples_completed=len(done), samples_planned=len(rows), device_seconds=device_seconds)
    return {'complete': complete, 'samples': len(done), 'artifact_bytes': size, 'index': str(index_path)}
