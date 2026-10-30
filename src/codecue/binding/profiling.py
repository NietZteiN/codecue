"""Profile the real cached checkpoint on CPU before choosing a balanced smoke."""
from __future__ import annotations
import gc
import json
import platform
import time
from pathlib import Path
from .datasets import read_jsonl, write_json
from .registry import guarded


@guarded
def profile(config):
    import torch
    from codecue.models import generate_free
    from .model_adapter import load, prompt_for, layout
    from .behavior import parse_answer, select
    from .registry import begin, finish
    if config['device'] != 'cpu':
        raise ValueError('this profile is the CPU feasibility route; GPU profiling uses the bounded pipeline')
    torch.set_num_threads(config.get('cpu_threads', 4))
    out, manifest = begin(config, 'model_profile')
    started = time.monotonic()
    chosen = select(read_jsonl(config['dataset']), config)
    # Profile one training base without using any holdout behavior to select difficulty.
    candidates = [r for r in chosen if r['split'] == 'train' and r['control_kind'] == 'primary']
    base = min(r['base_id'] for r in candidates)
    batch = [r for r in candidates if r['base_id'] == base]
    load_started = time.monotonic()
    tokenizer, model = load(config)
    loading_seconds = time.monotonic() - load_started
    if hasattr(tokenizer, 'add_bos_token'):
        tokenizer.add_bos_token = False
    prompts = [prompt_for(tokenizer, row, config['protocol']) for row in batch]
    for row, prompt in zip(batch, prompts):
        aligned = layout(tokenizer, row, prompt)
        if tokenizer(prompt)['input_ids'] != aligned['input_ids']:
            raise ValueError('profile tokenization differs from audited inputs')
    generation_started = time.monotonic()
    outputs = generate_free(tokenizer, model, prompts, config['max_new_tokens'], config['batch_size'],
                            stop_at_blank_line=config['protocol'] == 'short_answer_prefill_v2')
    generation_seconds = time.monotonic() - generation_started
    predictions = [{'id': row['id'], 'split': row['split'], 'expected_answer': row['expected_answer'],
                    'prediction': parse_answer(raw), 'raw_response': raw} for row, raw in zip(batch, outputs)]
    write_json(out / 'profile_responses.json', predictions)
    estimated = loading_seconds + generation_seconds / len(batch) * len(chosen) * 2.0
    result = {'model_experiment': True, 'purpose': 'throughput and interface profiling on one training base; not a balanced experiment',
              'device': 'cpu', 'host': platform.node(), 'cpu_threads': torch.get_num_threads(),
              'profile_samples': len(batch), 'balanced_smoke_samples': len(chosen),
              'model_loading_seconds': loading_seconds, 'generation_seconds': generation_seconds,
              'estimated_balanced_seconds_with_2x_headroom': estimated,
              'balanced_cpu_run_feasible': estimated < config.get('cpu_smoke_cap_seconds', 1800),
              'model_parameter_count': sum(p.numel() for p in model.parameters()),
              'actual_model_dtype': str(next(model.parameters()).dtype),
              'parsed_profile_fraction': sum(p['prediction'] is not None for p in predictions)/len(predictions)}
    write_json(out / 'profile.json', result)
    finish(out, manifest, time.monotonic()-started, samples_completed=len(batch), device_name=platform.processor())
    del model, tokenizer
    gc.collect()
    if config.get('run_smoke_if_feasible') and result['balanced_cpu_run_feasible'] and result['parsed_profile_fraction'] >= 0.5:
        from .behavior import run
        from .analysis import report
        smoke = run(config)
        result['balanced_smoke_complete'] = smoke['complete']
        result['balanced_smoke_accuracy'] = smoke['accuracy']
        report(Path(config['run_dir']))
        write_json(out / 'profile.json', result)
    return result
