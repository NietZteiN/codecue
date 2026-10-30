"""Provenance-checked descriptive review of completed external benchmark runs."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

from .datasets import digest, read_jsonl
from .published_benchmarks import aggregate, assets, immutable, plan, score, sha, serialization_description


def equivalent_score(recorded, recomputed):
    """AST literal errors contain object addresses; decision fields remain exact."""
    def stable(result):
        result = dict(result)
        if 'parse_error' in result:
            result['parse_error'] = re.sub(r'(?<= object at )0x[0-9a-fA-F]+',
                                           '<address>', result['parse_error'])
        return result
    return stable(recorded) == stable(recomputed)


def descriptive(rows, planned):
    """Exact benchmark counts; no causal attribution or prompt selection."""
    expected = {(task, row['id']): row for task, row in planned}
    if len(expected) != len(planned) or len(rows) != len(planned):
        raise ValueError('review requires complete unique benchmark coverage')
    observed = [(r['task'], r['id']) for r in rows]
    if len(set(observed)) != len(observed) or set(observed) != set(expected):
        raise ValueError('review coverage differs from planned questions')
    for result in rows:
        row = expected[result['task'], result['id']]
        if result['record_sha256'] != digest(row) or not equivalent_score(
                result['score'], score(result['task'], row, result['raw_response'])):
            raise ValueError('review record or recomputed score mismatch')
    tasks = []
    for task in dict.fromkeys(t for t, _ in planned):
        subset = [r for r in rows if r['task'] == task]
        item = {'task': task, 'n': len(subset),
                'parse_errors': dict(Counter(r['score'].get('parse_error', 'valid').split(':', 1)[0] for r in subset)),
                'stop_reasons': dict(Counter(r['stop_reason'] for r in subset)),
                'generated_tokens': sum(r['generated_tokens'] for r in subset),
                'mean_generated_tokens': sum(r['generated_tokens'] for r in subset) / len(subset),
                'starts_new_question': sum(r['raw_response'].lstrip().startswith('Q:') for r in subset),
                'contains_python_section': sum('[PYTHON]' in r['raw_response'] for r in subset)}
        if task.startswith('bbh_'):
            item['gold_letters'] = dict(Counter(expected[task, r['id']]['target'] for r in subset))
            item['predicted_letters'] = dict(Counter(r['score']['prediction'] or 'invalid' for r in subset))
            item['uniform_guess_accuracy'] = 1 / int(task.rsplit('_', 1)[1])
        else:
            item['primary_upstream_score_disagreements'] = sum(
                r['score']['correct'] != r['score']['upstream_postprocessing_literal_correct'] for r in subset)
        tasks.append(item)
    direct = {r['id']: r['score']['correct'] for r in rows if r['task'] == 'cruxeval_o_direct'}
    cot = {r['id']: r['score']['correct'] for r in rows if r['task'] == 'cruxeval_o_cot'}
    paired = None
    if direct and cot:
        if set(direct) != set(cot):
            raise ValueError('direct/CoT pairing differs')
        paired = {'n': len(direct), 'both_correct': sum(direct[k] and cot[k] for k in direct),
                  'direct_only_correct': sum(direct[k] and not cot[k] for k in direct),
                  'cot_only_correct': sum(not direct[k] and cot[k] for k in direct),
                  'both_incorrect': sum(not direct[k] and not cot[k] for k in direct)}
    return {'tasks': tasks, 'cruxeval_paired_correctness': paired,
            'interpretation': 'Descriptive checks of a fixed public benchmark. Answer format validity does not establish reasoning faithfulness. Direct/CoT change both prompt and token budget. BBH sizes use different released examples; they are not matched load contrasts.'}


def report(result):
    peak = result['resources']['gpu_peak_bytes']
    memory = f'{peak / 2**30:.2f} GiB' if peak is not None else 'not recorded (recovered run)'
    lines = ['# Published benchmark results and audit', '',
             f"All {result['summary']['evaluated']:,} planned predictions completed on "
             f"`{result['checkpoint']['model']}` at `{result['checkpoint']['model_revision']}`. "
             'One greedy completion per question/protocol; no training or prompt selection.', '',
             '| Evaluation | Correct / questions | Literal / letter accuracy | Invalid | Token limit | Upstream postprocessing + literal correct |',
             '|---|---:|---:|---:|---:|---:|']
    for row in result['summary']['tasks']:
        secondary = str(row['upstream_postprocessing_literal_correct']) if 'upstream_postprocessing_literal_correct' in row else '—'
        lines.append(f"| {row['task']} | {row['correct']} / {row['planned']} | {row['accuracy']:.2%} | "
                     f"{row['evaluated'] - row['valid']} | {row['token_limited']} | {secondary} |")
    lines += ['', 'CRUXEval numbers use a literal-only scorer without executing model output. '
              'The secondary count applies the exact upstream string postprocessing, then literal equality. '
              'Neither count reproduces the official execution evaluator or sampled pass@k. '
              'Serialization: ' + serialization_description(result['prompt_wrapper']) + '. '
              'Greedy decoding and new-token ceilings differ from sampled paper settings.', '',
              'Malformed and missing answers remain in the full denominator. A token-limited response '
              'can still be correct if it contains an accepted complete answer. Smoke questions '
              'overlap the full release and are not independent validation. The previously smoke-discovered direct '
              'answer-block parser bug was fixed and tested before full inference; its original artifacts '
              'and separate corrected scores remain available.', '', '## Output diagnostics', '',
              '| Task | Mean generated tokens | Begins a new question | Contains a Python section |',
              '|---|---:|---:|---:|']
    for row in result['diagnostics']['tasks']:
        lines.append(f"| {row['task']} | {row['mean_generated_tokens']:.1f} | {row['starts_new_question']} | {row['contains_python_section']} |")
    lines += ['', 'A response beginning a new question or copying a demonstration may still end in '
              'a format-valid letter. Format validity is not evidence that the requested task was solved faithfully. '
              'These flags are descriptive observations, not post hoc exclusions or changes to the score.', '']
    pair = result['diagnostics']['cruxeval_paired_correctness']
    if pair:
        lines += [f"On the same {pair['n']} CRUXEval questions, both protocols are correct on {pair['both_correct']}; "
                  f"only direct on {pair['direct_only_correct']}; only CoT on {pair['cot_only_correct']}; "
                  f"both are incorrect on {pair['both_incorrect']}. This jointly compares prompting and "
                  'generation budget, not an isolated causal effect of reasoning.', '']
    lines += ['## Verification and resources', '',
              'The audit checked the completed run identity, immutable response hash, source/data hashes, '
              'exact planned IDs and record hashes, all recomputed scores, and the aggregate hash of '
              'every recorded input-token sequence against the full actual-tokenizer preflight. '
              'Only process-specific AST object addresses inside parse-error text are normalized during '
              'comparison; every decision field must match exactly. '
              'No model inference or downloaded-program execution occurs during review.', '',
              f"Measured model-stage time: {result['resources']['stage_seconds']:.2f} seconds; peak allocated "
              f"GPU memory: {memory}. "
              'Stage time excludes framework startup before the registry opens; SLURM allocation time '
              'is recorded separately in the job logs. Current project usage accounting has no compute cap.', '',
              f"Run identity: `{result['run_identity_hash']}`. Input-token aggregate: "
              f"`{result['prompt_token_ids_sha256']}`. Raw responses: `{result['responses_path']}`. "
              f"Audit: `{result['audit_path']}`.", '',
              'Existing generated final-test and structural-extrapolation outcomes remain sealed. '
              'These published benchmarks establish external behavioral baselines; their scores alone '
              'do not identify a binding mechanism or establish a new scientific contribution.', '',
              'See [the evaluation plan and parser correction](published_evaluation_plan.md), '
              '[dataset/source details](published_datasets.md), '
              '[CRUXEval, ICML 2024](https://proceedings.mlr.press/v235/gu24c.html), and '
              '[BBH, Findings of ACL 2023](https://aclanthology.org/2023.findings-acl.824/).', '']
    return '\n'.join(lines)


def review(config):
    from .registry import ROOT, code_identity
    stage = Path(config['stage'])
    manifest = json.loads((stage / 'manifest.json').read_text())
    identity = manifest['identity']
    if (manifest['status'] != 'complete' or digest(identity) != manifest['identity_hash']
            or manifest['identity_hash'] != config['run_identity_hash']):
        raise ValueError('review requires the pinned completed run identity')
    response_path = stage / 'responses.jsonl'
    if sha(response_path) != manifest['responses_sha256']:
        raise ValueError('review response checksum mismatch')
    # Additional analysis code may exist, but inference/scoring source must match.
    for name in ('published_benchmarks.py', 'datasets.py', 'model_adapter.py'):
        relative = 'src/codecue/binding/' + name
        if sha(ROOT / relative) != identity['code']['source_files'][relative]:
            raise ValueError('review inference/scoring source differs from the completed run')
    original = identity['config']
    assets(original)
    planned = plan(original)
    rows = read_jsonl(response_path)
    diagnostics = descriptive(rows, planned)
    if [(r['task'], r['id']) for r in rows] != [(task, row['id']) for task, row in planned]:
        raise ValueError('review release order mismatch')
    runtime = json.loads((stage / 'runtime.json').read_text())
    qa = runtime['preflight']
    if (qa['source_sha256'] != identity['code']['source_sha256']
            or qa['config_hash'] != identity['config_hash']
            or qa['dataset_sha256'] != identity['dataset_manifest']['sha256']):
        raise ValueError('review tokenizer QA identity mismatch')
    prompt_hash = digest([[r['task'], r['id'], digest(r['input_token_ids'])] for r in rows])
    if prompt_hash != qa['prompt_token_ids_sha256']:
        raise ValueError('recorded prompts differ from tokenizer preflight')
    summary = aggregate(rows, planned, original['prompt_wrapper'])
    recorded_summary = json.loads((stage / 'summary.json').read_text())
    if any(recorded_summary[k] != v for k, v in summary.items()):
        raise ValueError('recorded summary differs from recomputed counts')
    result = {'run_identity_hash': manifest['identity_hash'],
              'inference_source_sha256': identity['code']['source_sha256'],
              'review_source_sha256': code_identity()['source_sha256'],
              'responses_sha256': sha(response_path), 'responses_path': str(response_path),
              'audit_path': config['output'], 'prompt_token_ids_sha256': prompt_hash,
              'checkpoint': {k: original[k] for k in ('model', 'model_revision', 'tokenizer_revision')},
              'prompt_wrapper': original['prompt_wrapper'],
              'resources': {'stage_seconds': manifest['wall_seconds_total'],
                            'gpu_peak_bytes': recorded_summary['gpu_peak_bytes']},
              'summary': summary, 'diagnostics': diagnostics,
              'model_inference': False, 'generated_holdouts_opened': False}
    immutable(config['output'], (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    immutable(config['report'], report(result).encode())
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()
    print(json.dumps(review(json.loads(Path(args.config).read_text())), indent=2))
