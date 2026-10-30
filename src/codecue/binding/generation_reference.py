"""Uncached forward-pass argmax reference for the existing short-answer harness."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .behavior import parse_answer
from .datasets import digest, read_jsonl, write_json
from .registry import guarded


def greedy_reference(tokenizer, model, input_ids, max_new_tokens):
    """Single unpadded sequence, full-prefix forwards, no generation machinery."""
    import torch
    generated = []
    steps = []
    stopped = 'token_limit'
    with torch.inference_mode():
        for _ in range(max_new_tokens):
            ids = torch.tensor([input_ids + generated], device=model.device)
            logits = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False).logits[0, -1].float()
            values, indices = logits.topk(2)
            token = int(logits.argmax())
            steps.append({'token_id': token, 'top_two_token_ids': indices.tolist(),
                          'top_two_logits': values.tolist(), 'top_two_margin': float(values[0] - values[1])})
            generated.append(token)
            if token == tokenizer.eos_token_id:
                stopped = 'eos'
                break
            tail = tokenizer.decode(generated[-6:], skip_special_tokens=True)
            if '\n\n' in tail or '\n \n' in tail:
                stopped = 'blank_line'
                break
    raw = tokenizer.decode(generated, skip_special_tokens=True)
    return {'raw_response': raw, 'token_ids': generated, 'steps': steps, 'stop_reason': stopped,
            'prediction': parse_answer(raw)}


@guarded
def run(config):
    import torch
    from .model_adapter import load, prompt_for
    from .registry import begin, finish
    if config['protocol'] != 'short_answer_prefill_v2':
        raise ValueError('reference stopping is defined only for short_answer_prefill_v2')
    out, manifest = begin(config, 'generation_reference')
    if (out/'summary.json').exists():
        raise ValueError('generation reference is immutable; choose a new run directory')
    started = time.monotonic()
    baseline = Path(config['reference_baseline'])
    recorded = json.loads((baseline/'manifest.json').read_text())
    data = json.loads((baseline/'responses.json').read_text())
    identity = recorded['identity']
    if recorded['identity_hash'] != digest(identity) or recorded['status'] != 'complete' or not data['complete']:
        raise ValueError('reference baseline must have a complete verified identity')
    for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype', 'protocol', 'max_new_tokens'):
        if config[key] != identity['config'][key]:
            raise ValueError('reference baseline inference contract mismatch')
    if identity['dataset_manifest']['sha256'] != manifest['identity']['dataset_manifest']['sha256']:
        raise ValueError('reference dataset mismatch')
    rows = data['responses_by_batch_size']['1']
    if data.get('heldout_outcomes_opened') is not False or any(r['split'] != 'train' for r in rows):
        raise ValueError('reference may use only existing training diagnostics')
    from .diagnostics import cases
    selected = cases(read_jsonl(config['dataset']))
    expected = {row['id']: row for row in selected}
    if len(rows) != len(expected) or {row['id'] for row in rows} != set(expected):
        raise ValueError('reference must cover the fixed diagnostic cases exactly once')
    for row in rows:
        if (any(row[key] != expected[row['id']][key] for key in ('source', 'expected_answer', 'kind', 'split'))
                or row['prediction'] != parse_answer(row['raw_response'])):
            raise ValueError('reference baseline case or score mismatch')
    tokenizer, model = load(config)
    results = []
    for row in rows:
        prompt = prompt_for(tokenizer, row, config['protocol'])
        ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
        if ids != row['input_token_ids']:
            raise ValueError('reference prompt tokens differ from baseline')
        reference = greedy_reference(tokenizer, model, ids, config['max_new_tokens'])
        results.append({**{k: row[k] for k in ('id', 'kind', 'split', 'source', 'expected_answer')},
                        'input_token_ids': ids, 'baseline_raw': row['raw_response'],
                        'baseline_prediction': row['prediction'], 'reference': reference,
                        'raw_matches': reference['raw_response'] == row['raw_response'],
                        'prediction_matches': reference['prediction'] == row['prediction'],
                        'reference_correct': reference['prediction'] == row['expected_answer']})
        print(f"reference {len(results)}/{len(rows)} raw_matches={results[-1]['raw_matches']}", flush=True)
    complete = len(results) == len(rows)
    result = {'complete': complete, 'model_experiment': True, 'heldout_outcomes_opened': False,
              'method': 'single unpadded full-prefix forward; use_cache=False; raw logit argmax; EOS/blank-line stop',
              'baseline': {'path': str(baseline), 'identity_hash': recorded['identity_hash'],
                           'responses_sha256': hashlib.sha256((baseline/'responses.json').read_bytes()).hexdigest()},
              'model_generation_config': model.generation_config.to_dict(),
              'actual_model_dtype': str(next(model.parameters()).dtype), 'actual_device': str(model.device),
              'device_name': torch.cuda.get_device_name() if config['device']=='cuda' else 'cpu',
              'gpu_peak_bytes': torch.cuda.max_memory_allocated() if config['device']=='cuda' else None,
              'results': results, 'raw_matches': sum(r['raw_matches'] for r in results),
              'prediction_matches': sum(r['prediction_matches'] for r in results),
              'interpretation': 'Implementation sensitivity, not independent replication or proof of an internal cause.'}
    write_json(out/'summary.json', result)
    finish(out, manifest, time.monotonic() - started, 'complete' if complete else 'budget_limited',
           samples_completed=len(results), samples_planned=len(rows))
    return {'complete': complete, 'raw_matches': result['raw_matches'], 'n': len(results)}
