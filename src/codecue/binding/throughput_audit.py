"""Validate throughput replay artifacts and export the measured execution preset."""
from __future__ import annotations

import json
import math
from pathlib import Path

from .datasets import digest, read_jsonl
from .published_benchmarks import immutable, plan, score, sha
from .published_review import equivalent_score
from .throughput import quality, reference


def audit_trial(trial, expected, refs, ceilings):
    rows = trial['responses']
    keys = [(r['task'], r['id']) for r in rows]
    if len(set(keys)) != len(keys) or set(keys) != set(expected) or len(rows) != trial['cases']:
        raise ValueError('performance trial coverage differs')
    for row in rows:
        key = row['task'], row['id']
        if row['input_token_ids'] != refs[key]['input_token_ids']:
            raise ValueError('performance trial prompt differs')
        if len(row['output_token_ids']) > ceilings[row['task']]:
            raise ValueError('performance trial token ceiling exceeded')
        if not equivalent_score(row['score'], score(row['task'], expected[key], row['raw_response'])):
            raise ValueError('performance trial scoring differs')
    tokens = sum(len(row['output_token_ids']) for row in rows)
    if tokens != trial['output_tokens'] or trial['generation_seconds'] <= 0:
        raise ValueError('performance token count or timing invalid')
    if (not math.isclose(trial['requests_per_second'], len(rows) / trial['generation_seconds'], rel_tol=1e-9)
            or not math.isclose(trial['output_tokens_per_second'], tokens / trial['generation_seconds'], rel_tol=1e-9)
            or trial['quality'] != quality(rows, refs)):
        raise ValueError('performance metrics differ from saved responses')
    actual_hash = digest([[r['task'], r['id'], digest(r['input_token_ids'])] for r in rows])
    if actual_hash != trial['prompt_token_ids_sha256']:
        raise ValueError('performance prompt-token aggregate differs')
    return {k: v for k, v in trial.items() if k != 'responses'}


def run(config):
    from .registry import ROOT, code_identity
    stage = Path(config['stage'])
    manifest = json.loads((stage / 'manifest.json').read_text())
    if (manifest['status'] != 'complete' or digest(manifest['identity']) != manifest['identity_hash']
            or not (config.get('identity_hash') or config.get('config_hash'))
            or config.get('identity_hash') and manifest['identity_hash'] != config['identity_hash']
            or config.get('config_hash') and manifest['identity']['config_hash'] != config['config_hash']):
        raise ValueError('throughput audit requires the pinned completed run')
    original = manifest['identity']['config']
    for name in ('throughput.py', 'published_benchmarks.py', 'model_adapter.py'):
        relative = 'src/codecue/binding/' + name
        if sha(ROOT / relative) != manifest['identity']['code']['source_files'][relative]:
            raise ValueError('throughput inference/scoring source changed: ' + name)
    refs = reference(original)
    full = {(task, row['id']): row for task, row in plan(original)}
    profiled = {(task, row['id']): row for task, row in plan(
        {**original, 'first_n_per_task': original['profile_first_n_per_task']})}
    summary = json.loads((stage / 'summary.json').read_text())
    if not summary['complete']:
        raise ValueError('full performance validation did not complete')
    audited, validation, candidates, checksums = [], [], [], {}
    for path in (sorted(stage.glob('worker_*/*.json')) + sorted((stage / 'validation').glob('*.json'))
                 + sorted((stage / 'validation_candidates').glob('*.json'))):
        content = json.loads(path.read_text())
        if 'responses' not in content:
            continue
        trial = audit_trial(content, full if path.parent.name in ('validation', 'validation_candidates') else profiled,
                            refs, original['max_new_tokens'])
        trial['artifact'] = str(path)
        checksums[str(path)] = sha(path)
        (validation if path.parent.name == 'validation' else candidates if path.parent.name == 'validation_candidates' else audited).append(trial)
    if len(validation) != 1 or validation[0]['cases'] != len(full):
        raise ValueError('selected backend lacks a complete full-workload validation')
    if not audited:
        raise ValueError('no completed profiling trials to audit')
    best = max(audited, key=lambda t: t['requests_per_second'])
    if (best['setting'] != summary['selected']['setting']
            or best['requests_per_second'] != summary['selected']['requests_per_second']):
        raise ValueError('selected backend was not the measured throughput maximum')
    if candidates and validation[0]['requests_per_second'] != max(t['requests_per_second'] for t in candidates):
        raise ValueError('selected full-backlog setting was not fastest')
    baseline = next((t for t in audited if t['setting'].get('stopping') == 'legacy'), None)
    if baseline is None and original.get('baseline_trial'):
        baseline_path = Path(original['baseline_trial'])
        if sha(baseline_path) != original['baseline_trial_sha256']:
            raise ValueError('external timing baseline checksum mismatch')
        baseline = audit_trial(json.loads(baseline_path.read_text()), profiled, refs, original['max_new_tokens'])
    production = summary['production_spec']
    baseline_device = None
    if original.get('baseline_trial'):
        metadata = Path(original['baseline_trial']).parent / 'worker.json'
        if metadata.exists():
            baseline_device = json.loads(metadata.read_text()).get('device_name')
            checksums[str(metadata)] = sha(metadata)
    elif baseline:
        baseline_device = summary['validation']['device_name']
    if json.loads((stage / 'selected_worker.json').read_text()) != production:
        raise ValueError('selected execution preset changed')
    preset = {k: original[k] for k in ('model', 'model_revision', 'tokenizer_revision', 'dtype',
                                      'prompt_wrapper', 'tokenization_mode', 'context_limit', 'max_new_tokens')}
    preset.update(worker=production, device_name=summary['validation']['device_name'],
                  versions=summary['validation']['versions'],
                  input_contract='pretokenized single-BOS plus reference-SP prompt IDs; no engine chat wrapping',
                  stop=['[/ANSWER]'], include_stop_str_in_output=True, sampling='greedy',
                  profile_identity_hash=manifest['identity_hash'],
                  validation_quality=validation[0]['quality'])
    if original.get('runtime_manifest'):
        preset.update(runtime_manifest=original['runtime_manifest'], runtime_manifest_sha256=original['runtime_manifest_sha256'])
    for key in ('cuda_home', 'flashinfer_sampler', 'uuid_telemetry'):
        if key in original:preset[key] = original[key]
    result = {'status': 'passed', 'model_inference': False, 'old_scientific_runs_modified': False,
              'generated_holdouts_opened': False, 'profile_identity_hash': manifest['identity_hash'],
              'analysis_source_sha256': code_identity()['source_sha256'],
              'profile_trials_audited': len(audited), 'validation_cases': len(full),
              'full_workload_candidates': candidates,
              'selected': best, 'validation': validation[0], 'baseline': baseline,
              'speedup': best['requests_per_second'] / baseline['requests_per_second'] if baseline else None,
              'baseline_device_name': baseline_device,
              'same_device_model': baseline_device == summary['validation']['device_name'] if baseline_device else None,
              'worker_end_to_end_seconds': summary['validation'].get('worker_wall_seconds'),
              'worker_timing_scope': summary['validation'].get('timing_scope', 'validation worker lifetime'),
              'registered_gpu_stage_seconds': manifest['wall_seconds_total'],
              'artifact_checksums': checksums, 'preset': preset}
    immutable(config['output'], (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    immutable(config['preset'], (json.dumps(preset, sort_keys=True, indent=2) + '\n').encode())
    trial = validation[0]
    lines = ['# Validated GPU throughput', '',
             f"Selected `{best['backend']}` with `{production}` on {preset['device_name']}.", '',
             f"The matched {best['cases']}-request profile improved from "
             f"{baseline['requests_per_second']:.2f} to {best['requests_per_second']:.2f} requests/s "
             f"({result['speedup']:.2f}×)." if baseline else 'The original baseline did not complete.',
             f"Baseline hardware: {baseline_device or 'unverified'}; candidate hardware: {preset['device_name']}. "
             + ('The GPU model is matched.' if result['same_device_model'] else
                'This ratio combines hardware and execution changes; it does not isolate a software speedup.'), '',
             f"Full workload: {trial['cases']} requests in {trial['generation_seconds']:.2f} generation seconds, "
             f"{trial['requests_per_second']:.2f} requests/s and {trial['output_tokens_per_second']:.0f} useful output tokens/s.",
             f"Allocated-device utilization averaged {trial['gpu']['mean_gpu_utilization_percent']}%; "
             f"peak device memory was {trial['gpu']['peak_device_memory_mib']} MiB. "
             'Device memory includes model weights, reserved KV cache and allocator reservations.',
             f"The engine worker lifetime was {result['worker_end_to_end_seconds']:.2f} seconds "
             f"({result['worker_timing_scope']}, including loading/compilation/warmup and cleanup).", '',
             f"Full validation quality: {trial['quality']['correct']} correct, {trial['quality']['valid']} parseable; "
             f"the saved reference has {trial['quality']['reference_correct']} correct. Correctness decisions "
             f"agree on {trial['quality']['correctness_matches']}/{trial['cases']}; raw strings agree on "
             f"{trial['quality']['raw_matches']}/{trial['cases']}. Parsed values agree on "
             f"{trial['quality']['parsed_values_match']}/{trial['quality']['both_valid']} cases where both are valid.", '',
             'The fastest setting was selected by work completed per second, not by favorable answer scores. '
             'Different batching and numerical kernels can change answers; this is an explicit new execution profile. '
             'Old scientific scores and snapshots are unchanged.', '',
             f"The audit rechecked all {len(audited)} completed profile trials and all {len(full)} validation "
             'prompt sequences, response scores, token ceilings and throughput calculations. Raw responses, '
             'GPU telemetry summaries, memory use, failures and timing are retained in the run directory.', '',
             'Reusable preset: `' + config['preset'] + '`. Measured settings and per-candidate utilization '
             'are in [the profiling report](' + Path(original['report']).name + '). '
             'See [the fixed plan](throughput_plan.md).', '']
    immutable(config['report'], '\n'.join(lines).encode())
    return result
