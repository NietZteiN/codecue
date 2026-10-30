"""GPU throughput tuning on fixed published prompts, isolated from scientific runs."""
from __future__ import annotations

import gc
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import threading
import time

from .datasets import digest, read_jsonl, write_json
from .published_benchmarks import assets, content_for, literal, plan, render, score, sha
from .registry import guarded


def reference(config):
    path = Path(config['reference_stage'])
    manifest = json.loads((path / 'manifest.json').read_text())
    if (manifest['status'] != 'complete' or digest(manifest['identity']) != manifest['identity_hash']
            or manifest['identity_hash'] != config['reference_identity_hash']
            or sha(path / 'responses.jsonl') != config['reference_responses_sha256']):
        raise ValueError('throughput reference identity/checksum differs')
    original = manifest['identity']['config']
    for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype', 'protocol', 'prompt_wrapper', 'tokenization_mode'):
        if original[key] != config[key]:
            raise ValueError('performance reference contract differs: ' + key)
    if any(original['max_new_tokens'][task] != config['max_new_tokens'][task] for task in config['tasks']):
        raise ValueError('performance reference token ceiling differs')
    return {(r['task'], r['id']): r for r in read_jsonl(path / 'responses.jsonl')}


def groups(items, size, bucket=False):
    if size < 1:
        raise ValueError('batch size must be positive')
    for task in dict.fromkeys(item['task'] for item in items):
        selected = [item for item in items if item['task'] == task]
        if bucket:
            selected.sort(key=lambda item: (len(item['input_token_ids']), item['id']))
        for start in range(0, len(selected), size):
            yield selected[start:start + size]


def quality(rows, references):
    pairs = [(row, references[row['task'], row['id']]) for row in rows]
    both_valid = [(a, b) for a, b in pairs if a['score']['valid'] and b['score']['valid']]
    return {'n': len(rows), 'correct': sum(r['score']['correct'] for r in rows),
            'reference_correct': sum(b['score']['correct'] for _, b in pairs),
            'valid': sum(r['score']['valid'] for r in rows),
            'correctness_matches': sum(a['score']['correct'] == b['score']['correct'] for a, b in pairs),
            'validity_matches': sum(a['score']['valid'] == b['score']['valid'] for a, b in pairs),
            'raw_matches': sum(a['raw_response'] == b['raw_response'] for a, b in pairs),
            'both_valid': len(both_valid),
            'parsed_values_match': sum(literal(a['score']['prediction']) == literal(b['score']['prediction'])
                                       for a, b in both_valid)}


class Monitor:
    """Sample only the allocated GPU; polling is independent of the decode loop."""
    def __init__(self):
        visible = os.environ.get('CUDA_VISIBLE_DEVICES', os.environ.get('SLURM_JOB_GPUS', ''))
        self.device = visible.split(',')[0] if visible else None
        self.samples = []
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.poll, daemon=True)

    def poll(self):
        while not self.stop.is_set():
            try:
                if self.device is None:
                    return
                out = subprocess.run(['nvidia-smi', '-i', self.device,
                                      '--query-gpu=utilization.gpu,memory.used,power.draw',
                                      '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=2)
                fields = out.stdout.strip().split(',')
                if out.returncode == 0 and len(fields) == 3:
                    self.samples.append([time.monotonic(), *[float(v.strip()) for v in fields]])
            except (ValueError, OSError, subprocess.TimeoutExpired):
                pass
            self.stop.wait(.5)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        self.thread.join(timeout=3)

    def summary(self):
        return {'samples': len(self.samples),
                'mean_gpu_utilization_percent': sum(s[1] for s in self.samples) / len(self.samples) if self.samples else None,
                'peak_device_memory_mib': max((s[2] for s in self.samples), default=None),
                'mean_power_watts': sum(s[3] for s in self.samples) / len(self.samples) if self.samples else None}


def inputs(config, count):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tokenizer, config)
    sources, refs = assets(config), reference(config)
    effective = {**config, 'first_n_per_task': count} if count else config
    items = []
    for task, row in plan(effective):
        prompt = render(tokenizer, content_for(task, row, sources), config['prompt_wrapper'])
        ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
        if ids != refs[task, row['id']]['input_token_ids']:
            raise ValueError('performance input tokens differ from completed reference')
        items.append({'task': task, 'id': row['id'], 'record': row, 'prompt': prompt, 'input_token_ids': ids})
    return tokenizer, items, refs


def tensor_generate(tokenizer, model, batch, ceiling, criterion):
    import torch
    from transformers import StoppingCriteriaList
    encoded = tokenizer([r['prompt'] for r in batch], add_special_tokens=False, padding=True,
                        return_tensors='pt').to(model.device)
    width = encoded.input_ids.shape[1]
    for index, item in enumerate(batch):
        if encoded.input_ids[index][encoded.attention_mask[index].bool()].tolist() != item['input_token_ids']:
            raise ValueError('batched tokenizer changed the audited input')
    with torch.inference_mode():
        output = model.generate(**encoded, do_sample=False, num_beams=1, max_new_tokens=ceiling,
                                use_cache=True, eos_token_id=tokenizer.eos_token_id,
                                pad_token_id=tokenizer.pad_token_id,
                                stopping_criteria=StoppingCriteriaList([criterion]))
    tails = output[:, width:].tolist()
    results = []
    for tail in tails:
        if tokenizer.eos_token_id in tail:
            tail = tail[:tail.index(tokenizer.eos_token_id)]
        results.append({'raw_response': tokenizer.decode(tail, skip_special_tokens=True),
                        'output_token_ids': tail})
    return results


def save_trial(config, spec, setting, items, refs, call, output, torch_memory=False):
    import torch
    if torch_memory:
        torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    with Monitor() as monitor:
        started = time.monotonic()
        generated = call()
        torch.cuda.synchronize()
        seconds = time.monotonic() - started
    if len(generated) != len(items):
        raise ValueError('engine returned incorrect number of completions')
    rows = []
    for item, result in zip(items, generated):
        if len(result['output_token_ids']) > config['max_new_tokens'][item['task']]:
            raise ValueError('engine exceeded the fixed token ceiling')
        rows.append({'task': item['task'], 'id': item['id'], 'input_token_ids': item['input_token_ids'],
                     **result, 'score': score(item['task'], item['record'], result['raw_response'])})
    tokens = sum(len(r['output_token_ids']) for r in rows)
    result = {'status': 'complete', 'backend': spec['backend'], 'setting': setting,
              'cases': len(rows), 'generation_seconds': seconds,
              'requests_per_second': len(rows) / seconds, 'output_tokens': tokens,
              'output_tokens_per_second': tokens / seconds,
              'gpu': monitor.summary(),
              'torch_peak_allocated_bytes': torch.cuda.max_memory_allocated() if torch_memory else None,
              'prompt_token_ids_sha256': digest([[r['task'], r['id'], digest(r['input_token_ids'])] for r in rows]),
              'quality': quality(rows, refs), 'responses': rows}
    write_json(output, result)
    return {k: v for k, v in result.items() if k != 'responses'}


def worker(config, spec, output):
    import torch
    ledger = json.loads(Path(config['budget_ledger']).read_text())
    lease = ledger['active'].get(os.environ.get('CODECUE_THROUGHPUT_LEASE'))
    if not lease or lease['stage'] != 'throughput_profile' or lease['run_dir'] != config['run_dir']:
        raise ValueError('GPU worker requires the active parent throughput budget lease')
    started = time.monotonic()
    tokenizer, items, refs = inputs(config, spec.get('first_n_per_task'))
    results = []
    if spec['backend'] == 'hf':
        from .model_adapter import load
        from .published_benchmarks import generate as legacy_generate
        from transformers import StopStringCriteria
        tokenizer, model = load(config)
        model.set_attn_implementation(spec['attention'])
        criterion = StopStringCriteria(tokenizer, stop_strings=['[/ANSWER]'])
        # Warm up kernels without using answers to select any configuration.
        tensor_generate(tokenizer, model, items[:8], 16, criterion)
        load_seconds = time.monotonic() - started
        for size in spec['batch_sizes']:
            setting = {k: spec[k] for k in ('attention', 'stopping', 'bucket')}
            setting['batch_size'] = size
            name = f"hf_{spec['attention']}_{spec['stopping']}_{size}"
            ordered = [item for batch in groups(items, size, spec['bucket']) for item in batch]
            def generate_all():
                generated = []
                for batch in groups(items, size, spec['bucket']):
                    ceiling = config['max_new_tokens'][batch[0]['task']]
                    if spec['stopping'] == 'legacy':
                        block = legacy_generate(tokenizer, model, [r['prompt'] for r in batch], ceiling, batch[0]['task'])
                        for item, row in zip(batch, block):
                            if row['input_token_ids'] != item['input_token_ids']:
                                raise ValueError('legacy generator changed the audited input')
                            if tokenizer.eos_token_id in row['output_token_ids']:
                                row['output_token_ids'] = row['output_token_ids'][:row['output_token_ids'].index(tokenizer.eos_token_id)]
                            row.pop('input_token_ids', None)
                        generated += block
                    else:
                        generated += tensor_generate(tokenizer, model, batch, ceiling, criterion)
                return generated
            try:
                tensor_generate(tokenizer, model, items[:size], 16, criterion)
                results.append(save_trial(config, spec, setting, ordered, refs, generate_all,
                                          output.parent / (name + '.json'), True))
            except torch.cuda.OutOfMemoryError as exc:
                results.append({'status': 'out_of_memory', 'backend': 'hf', 'setting': setting, 'error': str(exc)})
                break  # Larger static batches cannot fit; leave the GPU usable.
            finally:
                gc.collect()
                torch.cuda.empty_cache()
            write_json(output, {'load_seconds': load_seconds, 'trials': results})
    elif spec['backend'] == 'vllm':
        from vllm import LLM, SamplingParams
        engine = LLM(model=config['model'], revision=config['model_revision'],
                     tokenizer_revision=config['tokenizer_revision'], dtype='bfloat16',
                     tensor_parallel_size=spec.get('tensor_parallel_size', 1), max_model_len=config['context_limit'],
                     gpu_memory_utilization=spec['gpu_memory_utilization'],
                     max_num_seqs=spec['max_num_seqs'], max_num_batched_tokens=spec['max_num_batched_tokens'],
                     enable_chunked_prefill=True, enable_prefix_caching=True,
                     generation_config='vllm', seed=0)
        warm = [{'prompt_token_ids': r['input_token_ids']} for r in items[:8]]
        engine.generate(warm, SamplingParams(temperature=0, max_tokens=16), use_tqdm=False)
        load_seconds = time.monotonic() - started
        def generation_call(dataset, chunk):
            def generate_all():
                generated = []
                for start in range(0, len(dataset), chunk):
                    block = dataset[start:start + chunk]
                    params = [SamplingParams(temperature=0, top_p=1, max_tokens=config['max_new_tokens'][r['task']],
                                             stop=['[/ANSWER]'], include_stop_str_in_output=True) for r in block]
                    outputs = engine.generate([{'prompt_token_ids': r['input_token_ids']} for r in block], params, use_tqdm=False)
                    for item, response in zip(block, outputs):
                        if list(response.prompt_token_ids) != item['input_token_ids'] or len(response.outputs) != 1:
                            raise ValueError('vLLM changed the audited prompt or sample count')
                        completion = response.outputs[0]
                        tokens = list(completion.token_ids)
                        if tokenizer.eos_token_id in tokens:
                            tokens = tokens[:tokens.index(tokenizer.eos_token_id)]
                        generated.append({'raw_response': completion.text, 'output_token_ids': tokens,
                                          'finish_reason': completion.finish_reason})
                return generated
            return generate_all
        for chunk in spec['chunk_sizes']:
            engine.reset_prefix_cache()  # Prevent reuse of whole prompts from earlier trials.
            setting = {k: spec[k] for k in ('gpu_memory_utilization', 'max_num_seqs', 'max_num_batched_tokens')}
            setting['chunk_size'] = chunk
            results.append(save_trial(config, spec, setting, items, refs, generation_call(items, chunk),
                                      output.parent / f'vllm_{chunk}.json'))
            write_json(output, {'load_seconds': load_seconds, 'trials': results})
        if spec.get('inline_validation_chunks'):
            _, complete_items, _ = inputs(config, None)
            directory = output.parent.parent / 'validation_candidates'
            directory.mkdir(parents=True, exist_ok=True)
            checked = []
            for chunk in spec['inline_validation_chunks']:
                if not engine.reset_prefix_cache():
                    raise ValueError('cannot clear whole-prompt cache before validation')
                setting = {k: spec[k] for k in ('gpu_memory_utilization', 'max_num_seqs', 'max_num_batched_tokens')}
                setting['chunk_size'] = chunk
                checked.append(save_trial(config, spec, setting, complete_items, refs,
                                          generation_call(complete_items, chunk), directory / f'vllm_{chunk}.json'))
                write_json(output, {'load_seconds': load_seconds, 'trials': results,
                                    'inline_candidates': checked})
            fastest = choose([{'trials': checked}])
            validation_dir = output.parent.parent / 'validation'
            validation_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(directory / f"vllm_{fastest['setting']['chunk_size']}.json",
                            validation_dir / 'vllm_selected.json')
            inline = {'status': 'complete', 'trials': [fastest], 'device_name': torch.cuda.get_device_name(),
                      'versions': {name: importlib.metadata.version(name) for name in ('torch', 'transformers', 'vllm')}}
            production = {**spec, 'first_n_per_task': None,
                          'chunk_sizes': [fastest['setting']['chunk_size']]}
            production.pop('inline_validation_chunks', None)
    else:
        raise ValueError('unknown throughput backend')
    result = {'load_seconds': load_seconds, 'trials': results, 'device_name': torch.cuda.get_device_name(),
              'versions': {name: importlib.metadata.version(name) for name in ('torch', 'transformers', 'vllm')}}
    if spec.get('inline_validation_chunks'):
        result.update(inline_validation=inline, inline_candidates=checked, production_spec=production)
    write_json(output, result)
    return result


def launch(config_path, spec, folder, timeout):
    from .registry import ROOT
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    spec_path, output = folder / 'spec.json', folder / 'worker.json'
    write_json(spec_path, spec)
    argv = [sys.executable, str(ROOT / 'scripts/102_binding_throughput.py'), 'worker', str(config_path), str(spec_path), str(output)]
    env = {**os.environ, 'VLLM_WORKER_MULTIPROC_METHOD': 'spawn', 'VLLM_NO_USAGE_STATS': '1',
           'DO_NOT_TRACK': '1', 'TOKENIZERS_PARALLELISM': 'false'}
    started = time.monotonic()
    with (folder / 'worker.log').open('w') as log:
        process = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            partial = json.loads(output.read_text()) if output.exists() else {'trials': []}
            return {**partial, 'status': 'timeout', 'log': str(folder / 'worker.log'),
                    'worker_wall_seconds': time.monotonic() - started}
    if code:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        partial = json.loads(output.read_text()) if output.exists() else {'trials': []}
        return {**partial, 'status': 'worker_failed', 'exit_code': code, 'log': str(folder / 'worker.log'),
                'worker_wall_seconds': time.monotonic() - started}
    return {**json.loads(output.read_text()), 'status': 'complete', 'worker_wall_seconds': time.monotonic() - started}


def choose(results):
    trials = [trial for result in results for trial in result.get('trials', []) if trial['status'] == 'complete']
    if not trials:
        raise ValueError('no throughput candidate completed')
    # Optimize work completed, not accuracy; all numerical/answer changes stay visible.
    return max(trials, key=lambda t: t['requests_per_second'])


def validation_complete(result, expected_cases):
    trials = result.get('trials', [])
    return (result.get('status') == 'complete' and len(trials) == 1
            and trials[0].get('status') == 'complete' and trials[0].get('cases') == expected_cases)


@guarded
def run(config):
    from .registry import ROOT, begin, finish, code_identity
    qa = json.loads(Path(config['preflight_result']).read_text())
    if qa['config_hash'] != digest(config) or qa['source_sha256'] != code_identity()['source_sha256'] or qa['status'] != 'passed':
        raise ValueError('throughput requires matching actual-tokenizer preflight')
    out, manifest = begin(config, 'throughput_profile')
    os.environ['CODECUE_THROUGHPUT_LEASE'] = manifest['budget_lease']['id']
    started = time.monotonic()
    config_path = out / 'effective_config.json'
    write_json(config_path, config)
    results = []
    for index, base_spec in enumerate(config['workers']):
        spec = {**base_spec, 'first_n_per_task': config['profile_first_n_per_task']}
        result = launch(config_path, spec, out / f'worker_{index}', None)
        result['spec'] = spec
        results.append(result)
        write_json(out / 'profile.json', results)
        print(f"throughput worker {index}: {result['status']}", flush=True)
    best = choose(results)
    write_json(out / 'selected.json', best)
    selected_spec = next(result['spec'] for result in results if best in result.get('trials', []))
    selected_result = next(result for result in results if best in result.get('trials', []))
    validation = {**selected_spec, 'first_n_per_task': None}
    if best['backend'] == 'hf':
        validation['batch_sizes'] = [best['setting']['batch_size']]
    else:
        # Feed the full request backlog for continuous batching across completions.
        validation['max_num_seqs'] = min(validation['max_num_seqs'], best['setting']['chunk_size'])
        validation['chunk_sizes'] = [config['validation_chunk_size']]
    if selected_result.get('inline_validation'):
        validation = selected_result['production_spec']
        checked = {**selected_result['inline_validation'],
                   'worker_wall_seconds': selected_result['worker_wall_seconds'],
                   'timing_scope': 'shared engine lifetime including profiling; no second model load'}
    else:
        checked = launch(config_path, validation, out / 'validation', None)
    write_json(out / 'selected_worker.json', validation)
    baseline = next((t for r in results for t in r.get('trials', [])
                     if t.get('status') == 'complete' and t.get('setting', {}).get('stopping') == 'legacy'), None)
    summary = {'complete': validation_complete(checked, len(plan(config))), 'selected': best,
               'validation': checked, 'production_spec': validation, 'baseline': baseline,
               'profile_speedup': best['requests_per_second'] / baseline['requests_per_second'] if baseline else None,
               'old_scientific_runs_modified': False, 'generated_holdouts_opened': False,
               'selection_rule': 'highest requests/second among completed prompt- and generation-contract checks; no accuracy optimization'}
    write_json(out / 'summary.json', summary)
    finish(out, manifest, time.monotonic() - started, 'complete' if summary['complete'] else 'budget_limited')
    report(config, summary, results)
    return summary


def report(config, summary, results):
    lines = ['# GPU throughput optimization', '',
             'Same pinned CodeLlama checkpoint, BF16, greedy decoding, published prompt-token IDs and per-task ceilings. '
             'Performance replay is separate from the recorded scientific experiments. Selection uses requests/second, '
             'not answer accuracy. Numerical and answer changes are recorded rather than silently pooled.', '',
             '| Backend / setting | Cases | Generation seconds | Requests/s | Output tokens/s | GPU utilization | Valid | Correct |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for result in results:
        for trial in result.get('trials', []):
            if trial['status'] != 'complete':
                lines.append(f"| {trial['backend']} {trial['setting']} | {trial['status']} | | | | | | |")
                continue
            util = trial['gpu']['mean_gpu_utilization_percent']
            lines.append(f"| {trial['backend']} {trial['setting']} | {trial['cases']} | {trial['generation_seconds']:.2f} | "
                         f"{trial['requests_per_second']:.2f} | {trial['output_tokens_per_second']:.1f} | "
                         f"{f'{util:.1f}%' if util is not None else 'unavailable'} | {trial['quality']['valid']} | {trial['quality']['correct']} |")
        if result['status'] != 'complete':
            lines += ['', f"Worker {result['spec']['backend']} status: {result['status']}; inspect `{result.get('log')}`.", '']
    lines += ['', f"Selected: `{summary['selected']['backend']}` / `{summary['selected']['setting']}`.",
              f"Profile speedup over original eager/batch-eight generation: {summary['profile_speedup']:.2f}×." if summary['profile_speedup'] else 'Original baseline did not complete.',
              'Full-backlog validation: `' + summary['validation']['status'] + '`.', '',
              'Useful output token counts exclude EOS-valued padding. Generation timing includes decode/stopping overhead '
              'and GPU synchronization; model loading, warmup and compilation are reported separately per worker. '
              'GPU utilization/memory/power samples come only from the allocated device. Larger batching and attention '
              'kernels can change numerical outputs; quality agreement and raw responses accompany every trial.', '',
              'The old scientific reports are unchanged. See `artifacts/binding/throughput/` for profiles, '
              'worker logs, GPU telemetry and the selected execution settings.', '']
    Path(config['report']).parent.mkdir(parents=True, exist_ok=True)
    Path(config['report']).write_text('\n'.join(lines))
