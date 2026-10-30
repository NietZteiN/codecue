"""Matched CRUXEval serialization comparisons with immutable baseline reuse."""
from __future__ import annotations

import ast
import json
from pathlib import Path

from .datasets import digest, read_jsonl
from .published_benchmarks import assets, immutable, plan, sha
from .published_review import descriptive

TASKS = ('cruxeval_o_direct', 'cruxeval_o_cot')


def preflight_all(config):
    from .registry import ROOT, code_identity
    from .published_benchmarks import preflight
    verify_generation_source(config, code_identity())
    results = {}
    for name, path, expected in (
        ('native_replay', config['replay_config'], config['replay_config_hash']),
        ('completion_smoke', config['smoke_config'], config['smoke_config_hash']),
        ('completion_full', config['completion_config'], config['completion_config_hash']),
    ):
        cfg = json.loads((ROOT / path).read_text())
        if digest(cfg) != expected:
            raise ValueError('preflight frozen configuration checksum mismatch')
        results[name] = preflight(cfg)
    return results


def smoke(config):
    from .registry import ROOT
    from .published_benchmarks import run
    replay_cfg = json.loads((ROOT / config['replay_config']).read_text())
    raw_cfg = json.loads((ROOT / config['smoke_config']).read_text())
    if digest(replay_cfg) != config['replay_config_hash'] or digest(raw_cfg) != config['smoke_config_hash']:
        raise ValueError('frozen smoke configuration checksum mismatch')
    if replay_cfg.get('first_n_per_task') != 8 or raw_cfg.get('first_n_per_task') != 8:
        raise ValueError('smoke/replay must use the fixed first eight questions per task')
    matched_config(replay_cfg, raw_cfg)
    run(replay_cfg)
    checked_replay = replay(config)
    raw_summary = run(raw_cfg)
    if not raw_summary['complete']:
        raise ValueError('completion smoke did not finish within its operating cap')
    return {'replay': checked_replay, 'completion_smoke': raw_summary}


def finalize(config):
    from .published_review import review
    manifest, _ = verified_run(config['completion_stage'], config_hash=config['completion_config_hash'])
    review({**config['completion_review'], 'run_identity_hash': manifest['identity_hash']})
    return compare(config)


def profile_budget(stage_seconds, available_seconds, configured_seconds, margin_seconds):
    """Runtime estimate only; historical compute-budget fields do not gate work."""
    projected = 100 * stage_seconds  # first eight / 800 questions in each protocol
    if stage_seconds <= 0:
        raise ValueError('positive measured smoke runtime required')
    return {'projected_seconds': projected, 'stage_ceiling_seconds': None,
            'rule': '100 times complete 16-query smoke stage time; includes model loading'}


def dispatch_full(config):
    """Queue-safe controller; the actual model always runs its original QA'd source."""
    import subprocess
    import sys
    from .datasets import write_json
    from .snapshots import verify
    pointer = json.loads(Path(config['inference_source']).read_text())
    source = Path(pointer['snapshot'])
    frozen = verify(source)
    if frozen['code']['source_sha256'] != config['inference_source_sha256']:
        raise ValueError('dispatch inference source pin changed')
    comparison = json.loads((source / config['comparison_config']).read_text())
    replay(comparison)
    smoke_manifest, smoke_rows = verified_run(config['smoke_stage'], config_hash=comparison['smoke_config_hash'])
    if len(smoke_rows) != 16:
        raise ValueError('runtime profile must cover the complete fixed smoke')
    full = json.loads((source / comparison['completion_config']).read_text())
    if digest(full) != comparison['completion_config_hash']:
        raise ValueError('dispatch full configuration checksum mismatch')
    decision = profile_budget(smoke_manifest['wall_seconds_total'], None, None, 0)
    decision.update(status='starting_full_run', inference_source_sha256=frozen['code']['source_sha256'],
                    smoke_identity_hash=smoke_manifest['identity_hash'],
                    full_config_hash=digest(full))
    write_json(config['dispatch_report'], decision)
    argv = [sys.executable, str(source / 'scripts/91_binding_frozen_run.py'), str(source),
            'scripts/97_binding_published_benchmarks.py', 'run',
            str(source / comparison['completion_config'])]
    try:
        subprocess.run(argv, check=True)
    except Exception as exc:
        decision.update(status='failed', error=str(exc))
        write_json(config['dispatch_report'], decision)
        raise
    manifest = json.loads((Path(full['run_dir']) / 'published_behavior/manifest.json').read_text())
    decision.update(status=manifest['status'], full_identity_hash=manifest['identity_hash'])
    write_json(config['dispatch_report'], decision)
    if manifest['status'] != 'complete':
        raise ValueError('full serialization run incomplete; preserve resumable partial outputs')
    return decision


def verified_run(stage, identity_hash=None, config_hash=None):
    stage = Path(stage)
    manifest = json.loads((stage / 'manifest.json').read_text())
    identity = manifest['identity']
    if (manifest['status'] != 'complete' or digest(identity) != manifest['identity_hash']
            or digest(identity['config']) != identity['config_hash']
            or identity_hash is not None and manifest['identity_hash'] != identity_hash
            or config_hash is not None and identity['config_hash'] != config_hash):
        raise ValueError('serialization run identity mismatch or incomplete run')
    path = stage / 'responses.jsonl'
    if sha(path) != manifest['responses_sha256']:
        raise ValueError('serialization response checksum mismatch')
    cfg = identity['config']
    assets(cfg)
    if json.loads(Path(cfg['dataset']).with_suffix('.manifest.json').read_text()) != identity['dataset_manifest']:
        raise ValueError('serialization dataset manifest changed')
    planned = plan(cfg)
    rows = read_jsonl(path)
    descriptive(rows, planned)
    if [(r['task'], r['id']) for r in rows] != [(t, r['id']) for t, r in planned]:
        raise ValueError('serialization release order differs')
    qa = json.loads((stage / 'runtime.json').read_text())['preflight']
    tokens_hash = digest([[r['task'], r['id'], digest(r['input_token_ids'])] for r in rows])
    if (tokens_hash != qa['prompt_token_ids_sha256'] or qa['config_hash'] != identity['config_hash']
            or qa['source_sha256'] != identity['code']['source_sha256']
            or qa['dataset_sha256'] != identity['dataset_manifest']['sha256']):
        raise ValueError('serialization token preflight provenance mismatch')
    return manifest, rows


def matched_config(chat, raw):
    for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype', 'device',
                'protocol', 'tokenization_mode', 'batch_size', 'context_limit', 'scorer'):
        if chat[key] != raw[key]:
            raise ValueError('serialization inference contract differs: ' + key)
    for task in TASKS:
        if chat['max_new_tokens'][task] != raw['max_new_tokens'][task]:
            raise ValueError('serialization generation ceilings differ')
    if chat['prompt_wrapper'] != 'native_single_user_official_boundary_v1':
        raise ValueError('baseline must use native chat serialization')
    if raw['prompt_wrapper'] != 'cruxeval_released_completion_v1':
        raise ValueError('comparison must use released completion serialization')


def paired_counts(chat, raw, field):
    if set(chat) != set(raw) or not chat:
        raise ValueError('serialization question pairing differs')
    result = {'n': len(chat), 'both_correct': 0, 'chat_only_correct': 0,
              'completion_only_correct': 0, 'both_incorrect': 0}
    for key in chat:
        a, b = bool(chat[key]['score'][field]), bool(raw[key]['score'][field])
        name = ('both_correct' if a and b else 'chat_only_correct' if a else
                'completion_only_correct' if b else 'both_incorrect')
        result[name] += 1
    result['chat_correct'] = result['both_correct'] + result['chat_only_correct']
    result['completion_correct'] = result['both_correct'] + result['completion_only_correct']
    result['delta_percentage_points'] = 100 * (result['completion_correct'] - result['chat_correct']) / result['n']
    return result


def verify_generation_source(config, current_identity):
    from .snapshots import verify
    pointer = json.loads(Path(config['baseline_source']).read_text())
    frozen = Path(pointer['snapshot'])
    baseline_code = verify(frozen)['code']
    if baseline_code['source_sha256'] != config['baseline_source_sha256']:
        raise ValueError('baseline source pin differs')
    relative = 'src/codecue/binding/model_adapter.py'
    if baseline_code['source_files'][relative] != current_identity['source_files'][relative]:
        raise ValueError('model loading/tokenizer adapter changed across serialization arms')
    from .registry import ROOT
    relative = 'src/codecue/binding/published_benchmarks.py'
    function_hashes = {}
    for name in ('generate', 'content_for', 'crux_answer', 'upstream_literal_score', 'literal'):
        funcs = []
        for path in (frozen / relative, ROOT / relative):
            tree = ast.parse(path.read_text())
            node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            funcs.append(digest(ast.dump(node, include_attributes=False)))
        if funcs[0] != funcs[1]:
            raise ValueError('generation/prompt/scoring function changed: ' + name)
        function_hashes[name] = funcs[0]
    return function_hashes


def replay(config):
    from .registry import code_identity
    baseline, before = verified_run(config['baseline_stage'], config['baseline_identity_hash'])
    if baseline['responses_sha256'] != config['baseline_responses_sha256']:
        raise ValueError('baseline response pin differs')
    repeat, after = verified_run(config['replay_stage'], config_hash=config['replay_config_hash'])
    if baseline['identity']['dataset_manifest'] != repeat['identity']['dataset_manifest']:
        raise ValueError('replay dataset differs')
    a, b = baseline['identity']['config'], repeat['identity']['config']
    for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype', 'device', 'protocol',
                'prompt_wrapper', 'tokenization_mode', 'batch_size', 'context_limit', 'scorer'):
        if a[key] != b[key]:
            raise ValueError('replay configuration differs: ' + key)
    if any(a['max_new_tokens'][t] != b['max_new_tokens'][t] for t in TASKS):
        raise ValueError('replay token ceilings differ')
    expected = {(r['task'], r['id']): r for r in before}
    if len(after) != 16:
        raise ValueError('replay must cover fixed first eight questions per protocol')
    comparisons = []
    for row in after:
        old = expected[row['task'], row['id']]
        if old['input_token_ids'] != row['input_token_ids'] or old['prompt_sha256'] != row['prompt_sha256']:
            raise ValueError('native replay prompt differs from baseline')
        comparisons.append({'task': row['task'], 'id': row['id'],
                            'output_tokens_match': old['output_token_ids'] == row['output_token_ids'],
                            'raw_response_matches': old['raw_response'] == row['raw_response'],
                            'correctness_matches': old['score']['correct'] == row['score']['correct']})
    result = {'model_inference': False, 'generated_holdouts_opened': False,
              'baseline_identity': baseline['identity_hash'], 'replay_identity': repeat['identity_hash'],
              'generation_source': verify_generation_source(config, code_identity()),
              'n': len(comparisons), 'input_tokens_all_match': True,
              'output_tokens_match': sum(r['output_tokens_match'] for r in comparisons),
              'raw_responses_match': sum(r['raw_response_matches'] for r in comparisons),
              'correctness_matches': sum(r['correctness_matches'] for r in comparisons),
              'comparisons': comparisons}
    immutable(config['replay_output'], (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return {k: v for k, v in result.items() if k != 'comparisons'}


def compare(config):
    from .registry import code_identity
    baseline, chat_rows = verified_run(config['baseline_stage'], config['baseline_identity_hash'])
    if baseline['responses_sha256'] != config['baseline_responses_sha256']:
        raise ValueError('baseline response pin differs')
    raw, raw_rows = verified_run(config['completion_stage'], config_hash=config['completion_config_hash'])
    matched_config(baseline['identity']['config'], raw['identity']['config'])
    for key in ('python', 'torch', 'transformers', 'backend', 'sampling'):
        if baseline['identity']['environment'][key] != raw['identity']['environment'][key]:
            raise ValueError('serialization runtime environment differs: ' + key)
    if baseline['identity']['dataset_manifest'] != raw['identity']['dataset_manifest']:
        raise ValueError('comparison datasets differ')
    audit = json.loads(Path(config['completion_audit']).read_text())
    if audit['run_identity_hash'] != raw['identity_hash'] or audit['responses_sha256'] != raw['responses_sha256']:
        raise ValueError('completion audit does not cover this run')
    replay(config)  # Revalidate the native replay artifact without model inference.
    replay_result = json.loads(Path(config['replay_output']).read_text())
    if replay_result['baseline_identity'] != baseline['identity_hash'] or not replay_result['input_tokens_all_match']:
        raise ValueError('native replay did not verify the baseline')
    tasks = []
    for task in TASKS:
        chat = {r['id']: r for r in chat_rows if r['task'] == task}
        completion = {r['id']: r for r in raw_rows if r['task'] == task}
        if len(chat) != 800 or len(completion) != 800:
            raise ValueError('comparison requires all 800 questions per protocol')
        tasks.append({'task': task,
                      'released_postprocessing_literal': paired_counts(chat, completion, 'upstream_postprocessing_literal_correct'),
                      'answer_block_literal': paired_counts(chat, completion, 'correct'),
                      'chat_invalid': sum(not r['score']['valid'] for r in chat.values()),
                      'completion_invalid': sum(not r['score']['valid'] for r in completion.values()),
                      'chat_token_limited': sum(r['stop_reason'] == 'token_limit' for r in chat.values()),
                      'completion_token_limited': sum(r['stop_reason'] == 'token_limit' for r in completion.values()),
                      'chat_python_echoes': sum('[PYTHON]' in r['raw_response'] for r in chat.values()),
                      'completion_python_echoes': sum('[PYTHON]' in r['raw_response'] for r in completion.values())})
    result = {'complete': True, 'model_inference': False, 'generated_holdouts_opened': False,
              'baseline_identity_hash': baseline['identity_hash'], 'completion_identity_hash': raw['identity_hash'],
              'baseline_responses_sha256': baseline['responses_sha256'],
              'completion_responses_sha256': raw['responses_sha256'],
              'generation_source': verify_generation_source(config, code_identity()),
              'review_source_sha256': code_identity()['source_sha256'], 'tasks': tasks,
              'hardware': {
                  'chat': json.loads((Path(config['baseline_stage']) / 'runtime.json').read_text())['device_name'],
                  'native_replay': json.loads((Path(config['replay_stage']) / 'runtime.json').read_text())['device_name'],
                  'completion': json.loads((Path(config['completion_stage']) / 'runtime.json').read_text())['device_name'],
              },
              'replay': {k: v for k, v in replay_result.items() if k != 'comparisons'}}
    immutable(config['output'], (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    lines = ['# CRUXEval serialization comparison', '',
             'All 800 released questions were evaluated under direct and CoT completion prompts. '
             'The native-chat arm reuses the previously completed run on those same questions. '
             'Checkpoint, dtype, greedy decoding, batch size, task content, scoring functions and '
             'new-token ceilings are matched. The follow-up was planned after observing the earlier '
             'formatting gap; it is not an independent confirmatory dataset.', '',
             '| Protocol | Chat: released processing + literal | Completion: released processing + literal | Chat: answer-block literal | Completion: answer-block literal |',
             '|---|---:|---:|---:|---:|']
    for task in tasks:
        a, b = task['released_postprocessing_literal'], task['answer_block_literal']
        lines.append(f"| {task['task']} | {a['chat_correct']}/800 ({a['chat_correct']/8:.2f}%) | "
                     f"{a['completion_correct']}/800 ({a['completion_correct']/8:.2f}%) | "
                     f"{b['chat_correct']}/800 ({b['chat_correct']/8:.2f}%) | "
                     f"{b['completion_correct']}/800 ({b['completion_correct']/8:.2f}%) |")
    lines += ['', 'The first metric uses released string postprocessing followed by Python literal equality. '
              'The second extracts an explicit answer block and validates the assertion input. Neither '
              'executes model output or credits nonliteral expressions, and neither is the paper\'s '
              'sampled execution pass@k. Malformed and missing responses remain in the denominator.', '',
              f"Devices: native baseline on {result['hardware']['chat']}; completion on "
              f"{result['hardware']['completion']}; native replay on {result['hardware']['native_replay']}. "
              'Jobs were eligible for H100 or H200 after resource unavailability. '
              'The native replay tests a small fixed batch; even exact replay does not rule out '
              'all numerical device effects on the remaining questions. This is a limitation of '
              'interpreting the paired differences as serialization effects.', '',
              'Completion inputs contain exactly one BOS followed by reference SentencePiece encoding '
              'of the unchanged released prompt text. Every recorded input-token sequence matches '
              'actual-tokenizer preflight. The generation and prompt/scoring function ASTs were '
              'checked against the frozen native baseline; model loading/tokenizer adapter source is identical.', '',
              f"Native replay: all {replay_result['n']} prompt sequences match; "
              f"{replay_result['output_tokens_match']}/{replay_result['n']} output-token sequences match; "
              f"{replay_result['correctness_matches']}/{replay_result['n']} correctness decisions match. "
              'Smoke/replay questions overlap the full release and are not independent validation.', '',
              '| Protocol | Chat / completion invalid | Chat / completion token-limited | Chat / completion Python-section echoes |',
              '|---|---:|---:|---:|']
    for task in tasks:
        lines.append(f"| {task['task']} | {task['chat_invalid']} / {task['completion_invalid']} | "
                     f"{task['chat_token_limited']} / {task['completion_token_limited']} | "
                     f"{task['chat_python_echoes']} / {task['completion_python_echoes']} |")
    lines += ['', 'Paired correctness transitions for both metrics, complete provenance and checksums '
              'are in `' + config['output'] + '`. Existing generated final-test and extrapolation outcomes '
              'remain sealed. This comparison does not identify a binding mechanism or change the '
              'earlier synthetic mechanism gates.', '',
              'See [the fixed plan](serialization_plan.md) and '
              '[earlier benchmark results](published_baseline_review.md).', '']
    immutable(config['report'], '\n'.join(lines).encode())
    return result
