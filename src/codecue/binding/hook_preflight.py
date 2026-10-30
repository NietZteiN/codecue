"""Finite cross-backend replay and causal-prefix hook software checks."""
import json
from pathlib import Path
import time

from .datasets import digest, read_jsonl, write_json
from .published_benchmarks import immutable, sha
from .registry import guarded


def select_cases(cases, per_available=8):
    selected = set()
    for available in (2, 4):
        bases = sorted({c['record']['base_id'] for c in cases if c['kind'] == 'competition'
                        and c['record']['family'] == 'ownership' and c['record']['available_bindings'] == available})
        if len(bases) < per_available:raise ValueError('insufficient complete ownership groups')
        selected.update(bases[:per_available])
    result = [c for c in cases if c['kind'] == 'competition' and c['record']['base_id'] in selected]
    if len(result) != per_available * 2 * 8:
        raise ValueError('replay must preserve every query/swap/lexical relative')
    return result


def state_position(tokenizer, case):
    from .calibration import printed_source
    source = printed_source(case['record']['source'])
    start = case['prompt'].index(source)
    end = start + len(source.rsplit('\n', 1)[0])
    encoded = tokenizer(case['prompt'], add_special_tokens=False, return_offsets_mapping=True)
    if encoded['input_ids'] != case['input_token_ids']:
        raise ValueError('HF hook tokenizer changed registered prompt IDs')
    positions = [i for i, (a, b) in enumerate(encoded['offset_mapping']) if a < end <= b]
    if len(positions) != 1 or encoded['offset_mapping'][positions[0]][1] > end:
        raise ValueError('state token crosses the future query boundary')
    return positions[0]


def layout_check(config):
    from transformers import AutoTokenizer
    from .checkpoint_suite import prepared
    from .model_adapter import configure_tokenizer
    if sha(config['upstream_config']) != config['upstream_config_sha256']:
        raise ValueError('hook upstream configuration changed')
    upstream = json.loads(Path(config['upstream_config']).read_text())
    qa = json.loads(Path(upstream['preflight_result']).read_text())
    _, all_cases = prepared(upstream, qa['source_sha256'])
    cases = select_cases(all_cases, config['bases_per_available'])
    tokenizer = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tokenizer, config)
    positions = [state_position(tokenizer, case) for case in cases]
    result = dict(status='passed', cases=len(cases), config_hash=digest(config),
                  prefix_checks=[dict(id=c['id'], state_position=p, prefix_sha256=digest(c['input_token_ids'][:p+1]))
                                 for c, p in zip(cases, positions)], model_inference=False)
    write_json(Path(config['run_dir']) / 'layout_preflight.json', result)
    return result


@guarded
def run(config):
    import torch
    from transformers import StopStringCriteria, StoppingCriteriaList
    from codecue.patching import decoder_layers
    from .checkpoint_suite import audit, prepared, score_case
    from .model_adapter import load
    from .registry import begin, finish
    if sha(config['upstream_config']) != config['upstream_config_sha256']:
        raise ValueError('hook upstream configuration changed')
    upstream = json.loads(Path(config['upstream_config']).read_text())
    for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype', 'tokenization_mode'):
        if upstream[key] != config[key]:raise ValueError('hook checkpoint contract differs: ' + key)
    checked = audit(upstream)
    _, all_cases = prepared(upstream, checked['preflight']['source_sha256'])
    cases = select_cases(all_cases, config['bases_per_available'])
    refs = {(r['task'], r['id']): r for r in read_jsonl(Path(upstream['run_dir']) / 'checkpoint_suite/responses.jsonl')}
    out, manifest = begin(config, 'interface_diagnostics', reuse_complete=True)
    if manifest['status'] == 'complete':return json.loads((out / 'summary.json').read_text())
    started = time.monotonic()
    tokenizer, model = load(config)
    model.set_attn_implementation('sdpa')
    records = []
    criterion = StopStringCriteria(tokenizer, ['\n\n'])
    with torch.inference_mode():
        for first in range(0, len(cases), config['batch_size']):
            batch = cases[first:first + config['batch_size']]
            encoded = tokenizer([c['prompt'] for c in batch], add_special_tokens=False, padding=True, return_tensors='pt').to(model.device)
            width = encoded.input_ids.shape[1]
            for i, case in enumerate(batch):
                if encoded.input_ids[i][encoded.attention_mask[i].bool()].tolist() != case['input_token_ids']:
                    raise ValueError('HF replay prompt differs from registered tokens')
            output = model.generate(**encoded, do_sample=False, num_beams=1, use_cache=True,
                max_new_tokens=16, repetition_penalty=1., eos_token_id=config['eos_token_ids'],
                pad_token_id=tokenizer.pad_token_id, stopping_criteria=StoppingCriteriaList([criterion]))
            for case, tail in zip(batch, output[:, width:].tolist()):
                for i, token in enumerate(tail):
                    if token in config['eos_token_ids']:
                        tail = tail[:i]
                        break
                raw = tokenizer.decode(tail, skip_special_tokens=True)
                baseline = refs[case['task'], case['id']]
                observed = score_case(case, raw)
                records.append(dict(id=case['id'], input_token_ids=case['input_token_ids'], output_token_ids=tail,
                                    raw_response=raw, score=observed, reference_score=baseline['score'],
                                    both_valid=observed['valid'] and baseline['score']['valid'],
                                    parsed_prediction_matches=observed['valid'] and baseline['score']['valid']
                                    and observed['prediction'] == baseline['score']['prediction']))
    first = cases[0]
    pair = [c for c in cases if c['record']['base_id'] == first['record']['base_id']
            and c['record']['ownership_swapped'] == first['record']['ownership_swapped']
            and c['record']['lexical_realization'] == first['record']['lexical_realization']]
    if len(pair) != 2:raise ValueError('hook check requires exactly two late queries on one state prefix')
    positions = [state_position(tokenizer, c) for c in pair]
    if positions[0] != positions[1] or pair[0]['input_token_ids'][:positions[0]+1] != pair[1]['input_token_ids'][:positions[1]+1]:
        raise ValueError('pre-query input prefix differs')
    # Right padding retains identical physical/rotary prefix positions for both queries.
    width = max(len(c['input_token_ids']) for c in pair)
    ids = torch.tensor([c['input_token_ids'] + [tokenizer.pad_token_id] * (width-len(c['input_token_ids'])) for c in pair], device=model.device)
    mask = torch.tensor([[1]*len(c['input_token_ids']) + [0]*(width-len(c['input_token_ids'])) for c in pair], device=model.device)
    captured, handles = {}, []
    blocks = decoder_layers(model)
    for layer in config['layers']:
        def hook(module, args, output, layer=layer):
            hidden = output[0] if isinstance(output, tuple) else output
            captured[layer] = hidden[:, positions[0], :].detach().float().cpu()
        handles.append(blocks[layer].register_forward_hook(hook))
    try:
        with torch.inference_mode():model(input_ids=ids, attention_mask=mask, use_cache=False)
    finally:
        for handle in handles:handle.remove()
    hooks = [dict(layer=layer, shape=list(values.shape), max_absolute_prefix_difference=float((values[0]-values[1]).abs().max()),
                  exact_prefix_invariance=bool(torch.equal(values[0], values[1]))) for layer, values in captured.items()]
    passed = len(hooks) == len(config['layers']) and all(h['exact_prefix_invariance'] for h in hooks)
    result = dict(status='passed' if passed else 'needs_attention', complete=passed, model=config['model'],
                  cases=len(records), hf_correct=sum(r['score']['correct'] for r in records),
                  vllm_correct=sum(r['reference_score']['correct'] for r in records),
                  parsed_prediction_matches=sum(r['parsed_prediction_matches'] for r in records),
                  both_valid=sum(r['both_valid'] for r in records),
                  hidden_hooks=hooks, upstream_identity=checked['identity_hash'], device_name=torch.cuda.get_device_name(),
                  purpose='Software replay and raw-block causal-prefix invariance only. No probe or intervention effect is claimed.',
                  generated_holdouts_opened=False, config_hash=digest(config))
    write_json(out / 'replay.json', records)
    write_json(out / 'summary.json', result)
    finish(out, manifest, time.monotonic()-started, 'complete' if passed else 'failed')
    if not passed:raise ValueError('causal-prefix hook check failed; inspect captured differences')
    return result
