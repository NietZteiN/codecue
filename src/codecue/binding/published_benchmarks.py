"""Public benchmark baselines, separate from the generated mechanism-test gates.

All released questions and labels remain intact. CRUXEval is scored by Python
literal equality WITHOUT running either benchmark programs or generated code.
This is a disclosed literal-only metric, not the upstream execution evaluator.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time

from .datasets import digest, read_jsonl, write_json
from .registry import guarded

TASKS = ('cruxeval_o_direct', 'cruxeval_o_cot', 'bbh_tracking_3',
         'bbh_tracking_5', 'bbh_tracking_7')
SCORER = 'python_literal_equality_and_bbh_final_letter_v2'
WRAPPERS = ('native_single_user_official_boundary_v1', 'cruxeval_released_completion_v1',
            'released_completion_native_tokenizer_v1')


def serialization_description(wrapper):
    if wrapper == WRAPPERS[0]:
        return 'released prompt content inside the checkpoint single-user chat template; audited BOS boundary'
    if wrapper == WRAPPERS[1]:
        return 'released CRUXEval prompt content as a completion prefix; one BOS plus reference SentencePiece encoding'
    if wrapper == WRAPPERS[2]:
        return 'released CRUXEval completion prefix; one explicit BOS plus unchanged native tokenizer content IDs, no chat wrapper'
    raise ValueError('unknown published serialization protocol')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_manifest(path, expected=None):
    if expected is not None and sha(path) != expected:
        raise ValueError('source manifest checksum mismatch')
    manifest = json.loads(Path(path).read_text())
    for entry in manifest['files']:
        if sha(entry['path']) != entry['sha256']:
            raise ValueError(f"published source checksum mismatch: {entry['path']}")
    return manifest


def immutable(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f'published artifact already differs: {path}')
    if not path.exists():
        path.write_bytes(data)
        try:
            from .experiment_log import note_artifact
            note_artifact(path.resolve())
        except Exception as exc:
            import sys
            print(f'Experiment metadata logging deferred: {type(exc).__name__}: {exc}',file=sys.stderr)


def build(config):
    """Wrap original records with namespaced IDs; do not edit original releases."""
    sources = checked_manifest(config['data_sources'], config['data_sources_sha256'])
    protocols = checked_manifest(config['protocol_sources'], config['protocol_sources_sha256'])
    rows = []
    for source in sources['files']:
        if source['examples'] is None:
            continue
        path = Path(source['path'])
        if source['repository'] == 'facebookresearch/cruxeval':
            records = read_jsonl(path)
            for record in records:
                ast.literal_eval(record['output'])  # all 800 released references are literals
                rows.append({'id': 'cruxeval/' + record['id'], 'family': 'cruxeval_o',
                             'source_id': record['id'], 'source_path': str(path), **record})
                rows[-1]['id'] = 'cruxeval/' + record['id']
        else:
            size = next(n for word, n in (('three', 3), ('five', 5), ('seven', 7))
                        if f'_{word}_' in path.name)
            records = json.loads(path.read_text())['examples']
            for index, record in enumerate(records):
                if not re.fullmatch(r'\([A-' + chr(64 + size) + r']\)', record['target']):
                    raise ValueError('invalid released BBH target')
                rows.append({'id': f'bbh_tracking_{size}/{index:03d}',
                             'family': f'bbh_tracking_{size}', 'source_id': index,
                             'source_path': str(path), **record})
        if len(records) != source['examples']:
            raise ValueError('published record count mismatch')
    if len(rows) != 1550 or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('expected all 800 CRUXEval and 750 BBH records with unique IDs')
    content = ''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows).encode()
    immutable(config['dataset'], content)
    manifest = {'sha256': hashlib.sha256(content).hexdigest(), 'rows': len(rows),
                'counts': dict(Counter(r['family'] for r in rows)),
                'role': 'public_external_benchmarks', 'generated_holdouts_opened': False,
                'data_sources': sources, 'protocol_sources': protocols,
                'source_manifests': {config['data_sources']: sha(config['data_sources']),
                                     config['protocol_sources']: sha(config['protocol_sources'])}}
    immutable(Path(config['dataset']).with_suffix('.manifest.json'),
              (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode())
    return {k: manifest[k] for k in ('sha256', 'rows', 'counts', 'role')}


def literal(text):
    if len(text) > 20000:
        raise ValueError('literal exceeds length limit')
    tree = ast.parse(text.strip(), mode='eval')
    if sum(1 for _ in ast.walk(tree)) > 5000:
        raise ValueError('literal exceeds node limit')
    return ast.literal_eval(tree)


def crux_answer(text, record, cot=False):
    """Extract a literal or the RHS of the requested assertion, never execute it."""
    answer = text.strip()
    opening = re.search(r'(?m)^[ \t]*\[ANSWER\]', answer)
    if opening:
        answer = answer[opening.end():]
    elif cot:
        raise ValueError('missing CoT answer tag')
    # A stop tag may itself occur inside a quoted output. Prefer the terminal tag.
    if answer.rstrip().endswith('[/ANSWER]'):
        answer = answer.rstrip()[:-len('[/ANSWER]')]
    answer = answer.strip()
    if answer.startswith('```') and answer.endswith('```'):
        answer = re.sub(r'^```(?:python)?\s*\n?', '', answer)[:-3].strip()
    if answer.startswith('assert '):
        tree = ast.parse(answer)
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assert):
            raise ValueError('expected one assertion')
        test = tree.body[0].test
        if (not isinstance(test, ast.Compare) or len(test.ops) != 1
                or not isinstance(test.ops[0], ast.Eq) or tree.body[0].msg is not None):
            raise ValueError('expected one equality')
        expected = ast.parse(f"f({record['input']})", mode='eval').body
        if ast.dump(test.left) != ast.dump(expected):
            raise ValueError('assertion changed the released input')
        answer = ast.get_source_segment(answer, test.comparators[0])
    return literal(answer)


def upstream_literal_score(text, record, cot=False):
    """Upstream string postprocessing + literal subset of its equality evaluator.

    Deliberately reproduces split('==')[1], including its string-literal edge case.
    Stop marker is removed, as by the authors' vLLM stop configuration.
    Nonliteral expressions receive no execution-based credit.
    """
    answer = text.split('[/ANSWER]', 1)[0]
    if cot and '[ANSWER]' in answer:
        answer = answer.split('[ANSWER]')[1].strip()
    if '==' in answer:
        answer = answer.split('==')[1].strip()
    answer = answer.strip()
    if f"f({record['input']})" in answer:
        return False
    try:
        return bool(literal(record['output']) == literal(answer))
    except (ValueError, SyntaxError, TypeError, RecursionError):
        return False


def score(task, record, text):
    """Missing/malformed answers count as incorrect in the full denominator."""
    result = {'scorer': SCORER, 'valid': False, 'correct': False, 'prediction': None}
    if task.startswith('cruxeval_o_'):
        cot = task.endswith('_cot')
        result['upstream_postprocessing_literal_correct'] = upstream_literal_score(text, record, cot)
        try:
            value = crux_answer(text, record, cot)
            result.update(valid=True, prediction=repr(value), prediction_type=type(value).__name__,
                          correct=bool(value == literal(record['output'])))
        except (ValueError, SyntaxError, TypeError, RecursionError) as exc:
            # ast.literal_eval embeds object addresses in malformed-node errors.
            # Canonical text makes future immutable resumes compare deterministically.
            result['parse_error'] = type(exc).__name__ + ': ' + re.sub(
                r'(?<= object at )0x[0-9a-fA-F]+', '<address>', str(exc))
    else:
        answer = text.split('\n\nQ:', 1)[0].strip()
        match = re.search(r'(?:\bthe answer is\s*|\banswer:\s*|^)(\([A-G]\))\.?\s*\Z',
                          answer, re.IGNORECASE)
        if match and ord(match[1][1]) - 64 <= int(task.rsplit('_', 1)[1]):
            result.update(valid=True, prediction=match[1], correct=match[1] == record['target'])
        else:
            result['parse_error'] = 'missing final in-range answer letter'
    return result


def assets(config):
    manifest = json.loads(Path(config['dataset']).with_suffix('.manifest.json').read_text())
    if manifest['role'] != 'public_external_benchmarks' or sha(config['dataset']) != manifest['sha256']:
        raise ValueError('published dataset manifest mismatch')
    for path, expected in manifest['source_manifests'].items():
        checked_manifest(path, expected)
    path = next(f['path'] for f in manifest['protocol_sources']['files'] if f['path'].endswith('/prompts.py'))
    spec = importlib.util.spec_from_file_location('pinned_cruxeval_prompts', path)
    prompts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prompts)
    bbh = {}
    for size, word in ((3, 'three'), (5, 'five'), (7, 'seven')):
        path = next(f['path'] for f in manifest['protocol_sources']['files']
                    if f['path'].endswith(f'tracking_shuffled_objects_{word}_objects.txt'))
        original = Path(path).read_text()
        if '\n-----\n' not in original:
            raise ValueError('missing BBH prompt metadata separator')
        bbh[size] = original.split('\n-----\n', 1)[1].strip()
        if bbh[size].count('\nQ: ') != 3:
            raise ValueError('expected three released BBH demonstrations')
    return prompts, bbh


def content_for(task, row, sources):
    prompts, bbh = sources
    if task == 'cruxeval_o_direct':
        return prompts.make_direct_output_prompt((row['code'], row['input']))
    if task == 'cruxeval_o_cot':
        return prompts.make_cot_output_prompt((row['code'], row['input']))
    size = int(task.rsplit('_', 1)[1])
    return bbh[size] + '\n\nQ: ' + row['input'] + "\nA: Let's think step by step."


def render(tokenizer, content, wrapper=WRAPPERS[0]):
    from .model_adapter import normalize_prompt
    if wrapper == WRAPPERS[2]:
        if not tokenizer.bos_token or tokenizer.bos_token_id is None:
            raise ValueError('native completion requires an explicit BOS token')
        prompt = tokenizer.bos_token + content
        expected = [tokenizer.bos_token_id] + tokenizer(content, add_special_tokens=False)['input_ids']
        actual = tokenizer(prompt, add_special_tokens=False)['input_ids']
        if actual != expected or actual.count(tokenizer.bos_token_id) != 1:
            raise ValueError('native completion changed the single-BOS/content boundary')
        return prompt
    if wrapper == WRAPPERS[1]:
        reference = getattr(tokenizer, 'binding_sp_model', None)
        if reference is None or not getattr(tokenizer, 'binding_official_boundary', False):
            raise ValueError('released completion requires the audited CodeLlama SentencePiece reference')
        # This separator reproduces SP's initial metaspace after a literal BOS in
        # the HF fast tokenizer. It is verified at the token-ID level, not assumed.
        prompt = tokenizer.bos_token + ' ' + content
        expected = [reference.bos_id()] + reference.encode(content)
        if tokenizer(prompt, add_special_tokens=False)['input_ids'] != expected:
            raise ValueError('released completion differs from one BOS plus reference SentencePiece encoding')
        return prompt
    if wrapper != WRAPPERS[0]:
        raise ValueError('unknown published serialization protocol')
    return normalize_prompt(tokenizer, tokenizer.apply_chat_template(
        [{'role': 'user', 'content': content}], tokenize=False, add_generation_prompt=True))


def plan(config):
    if config['scorer'] != SCORER or config['prompt_wrapper'] not in WRAPPERS:
        raise ValueError('unknown published scoring or serialization protocol')
    if not set(config['tasks']) <= set(TASKS) or len(set(config['tasks'])) != len(config['tasks']):
        raise ValueError('unknown/duplicate benchmark task')
    if config['prompt_wrapper'] in WRAPPERS[1:] and any(not task.startswith('cruxeval_o_') for task in config['tasks']):
        raise ValueError('released completion experiment is limited to CRUXEval-O')
    rows = read_jsonl(config['dataset'])
    selected = []
    for task in config['tasks']:
        family = 'cruxeval_o' if task.startswith('cruxeval_o_') else task
        records = [r for r in rows if r['family'] == family]
        limit = config.get('first_n_per_task')
        if limit is not None:
            records = records[:limit]
        selected += [(task, row) for row in records]
    return selected


def preflight(config):
    """CPU batch job: actual tokenizer, all prompts, and gold scorer roundtrips."""
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    from .registry import code_identity
    sources = assets(config)
    tok = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tok, config)
    summary = defaultdict(list)
    prompts_hash = []
    for task, row in plan(config):
        content = content_for(task, row, sources)
        prompt = render(tok, content, config['prompt_wrapper'])
        ids = tok(prompt, add_special_tokens=False)['input_ids']
        if len(ids) + config['max_new_tokens'][task] > config['context_limit']:
            raise ValueError('benchmark prompt exceeds frozen context limit')
        if task.startswith('cruxeval_o_'):
            gold = f"[ANSWER]\nassert f({row['input']}) == {row['output']}\n[/ANSWER]"
        else:
            gold = 'So the answer is ' + row['target'] + '.'
        if not score(task, row, gold)['correct']:
            raise ValueError('released reference failed scorer roundtrip')
        summary[task].append(len(ids))
        prompts_hash.append([task, row['id'], digest(ids)])
    result = {'status': 'passed', 'model_inference': False, 'generated_holdouts_opened': False,
              'config_hash': digest(config), 'source_sha256': code_identity()['source_sha256'],
              'dataset_sha256': sha(config['dataset']),
              'prompt_token_ids_sha256': digest(prompts_hash),
              'tasks': {k: {'n': len(v), 'min_prompt_tokens': min(v), 'max_prompt_tokens': max(v)}
                        for k, v in summary.items()}}
    write_json(config['preflight_result'], result)
    return result


def generate(tokenizer, model, prompts, max_new_tokens, task):
    import torch
    from transformers import StoppingCriteria, StoppingCriteriaList

    encoded = tokenizer(prompts, add_special_tokens=False, padding=True, return_tensors='pt').to(model.device)
    width = encoded.input_ids.shape[1]
    marker = '[/ANSWER]' if task.startswith('cruxeval_o_') else '\n\nQ:'

    class EndMarker(StoppingCriteria):
        def __call__(self, input_ids, scores, **kwargs):
            tails = tokenizer.batch_decode(input_ids[:, max(width, input_ids.shape[1] - 32):], skip_special_tokens=True)
            return torch.tensor([marker in tail for tail in tails], device=input_ids.device)

    with torch.inference_mode():
        output = model.generate(**encoded, do_sample=False, num_beams=1,
                                max_new_tokens=max_new_tokens, use_cache=True,
                                eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.pad_token_id,
                                stopping_criteria=StoppingCriteriaList([EndMarker()]))
    results = []
    for index, tail in enumerate(output[:, width:].tolist()):
        if tokenizer.eos_token_id in tail:
            tail = tail[:tail.index(tokenizer.eos_token_id) + 1]
        raw = tokenizer.decode(tail, skip_special_tokens=True)
        reason = ('answer_end_marker' if marker in raw else
                  'eos' if tail and tail[-1] == tokenizer.eos_token_id else 'token_limit')
        results.append({'raw_response': raw, 'output_token_ids': tail,
                        'input_token_ids': encoded.input_ids[index][encoded.attention_mask[index].bool()].tolist(),
                        'stop_reason': reason, 'generated_tokens': len(tail)})
    return results


def aggregate(rows, planned, wrapper=WRAPPERS[0]):
    groups = []
    counts = Counter(task for task, _ in planned)
    for task, n in counts.items():
        subset = [r for r in rows if r['task'] == task]
        correct = sum(r['score']['correct'] for r in subset)
        item = {'task': task, 'planned': n, 'evaluated': len(subset), 'correct': correct,
                'valid': sum(r['score']['valid'] for r in subset),
                'token_limited': sum(r['stop_reason'] == 'token_limit' for r in subset),
                'accuracy': correct / n if len(subset) == n else None,
                'evaluated_accuracy': correct / len(subset) if subset else None}
        if task.startswith('cruxeval_o_'):
            item['upstream_postprocessing_literal_correct'] = sum(
                r['score']['upstream_postprocessing_literal_correct'] for r in subset)
        groups.append(item)
    return {'complete': len(rows) == len(planned), 'planned': len(planned), 'evaluated': len(rows),
            'tasks': groups, 'generated_holdouts_opened': False,
            'metric': SCORER, 'decoding': 'one greedy completion per item; no sampled pass@k',
            'cruxeval_metric_limit': 'literal equality without execution; expressions and function calls get no credit',
            'serialization': serialization_description(wrapper)}


def rescore_smoke(config):
    """Correct smoke scoring in a separate artifact without repeating inference."""
    from .registry import code_identity
    root = Path(config['smoke_stage'])
    manifest = json.loads((root / 'manifest.json').read_text())
    path = root / 'responses.jsonl'
    if (manifest['status'] != 'complete' or manifest['identity_hash'] != config['smoke_identity_hash']
            or sha(path) != manifest['responses_sha256'] or sha(path) != config['responses_sha256']):
        raise ValueError('smoke inference provenance mismatch')
    original = manifest['identity']['config']
    effective = {**original, 'scorer': SCORER}
    assets(effective)
    planned = plan(effective)
    rows = read_jsonl(path)
    if len(rows) != len(planned):
        raise ValueError('smoke coverage mismatch')
    corrected = []
    for result, (task, row) in zip(rows, planned):
        if result['id'] != row['id'] or result['task'] != task or result['record_sha256'] != digest(row):
            raise ValueError('smoke record mismatch')
        corrected.append({**result, 'original_score': result['score'],
                          'score': score(task, row, result['raw_response'])})
    result = {'model_inference': False, 'source_smoke_identity': manifest['identity_hash'],
              'source_responses_sha256': sha(path), 'source_code': manifest['identity']['code']['source_sha256'],
              'correction_code': code_identity()['source_sha256'],
              'reason': 'extract explicit line-start answer blocks after an echoed program in direct mode',
              'summary': aggregate(corrected, planned), 'responses': corrected}
    immutable(config['output'], (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return {k: v for k, v in result.items() if k != 'responses'}


def write_report(config, summary):
    lines = ['# Published benchmark baseline', '',
             f"Checkpoint: `{config['model']}` at `{config['model_revision']}`. "
             'Greedy decoding, one completion per question. All released questions and targets are preserved.', '',
             serialization_description(config['prompt_wrapper']) + '. '
             'Greedy decoding and fixed new-token ceilings are explicit evaluation settings; '
             'these results do not reproduce the papers\' sampled decoding/execution-score setup.', '',
             f"Completion: {summary['evaluated']}/{summary['planned']} planned queries. "
             'Smoke questions overlap the full benchmark and are not independent validation.', '',
             '| Task | Evaluated / planned | Correct | Accuracy | Invalid | Token limit |',
             '|---|---:|---:|---:|---:|---:|']
    for row in summary['tasks']:
        accuracy = f"{row['accuracy']:.2%}" if row['accuracy'] is not None else 'incomplete'
        lines.append(f"| {row['task']} | {row['evaluated']} / {row['planned']} | {row['correct']} | "
                     f"{accuracy} | {row['evaluated'] - row['valid']} | {row['token_limited']} |")
    lines += ['', 'Invalid answers count as incorrect. CRUXEval uses Python literal equality, '
              'including container equality; neither downloaded programs nor model output is executed. '
              'This differs from the official execution scorer, which can accept nonliteral expressions. '
              'A secondary count with the upstream string postprocessing followed by literal equality is retained in summary.json. '
              'BBH requires a final in-range option letter, either alone or after “the answer is” / “Answer:”.', '',
              'CRUXEval direct/CoT receive the released demonstrations; BBH receives all three released CoT '
              'demonstrations after its metadata separator. Generation stops on EOS, the CRUXEval closing '
              'answer tag or a new BBH question, or the configured token ceiling. Missing and truncated '
              'answers remain in the denominator. No benchmark score selects or changes a prompt.', '',
              'These are public external behavioral baselines. Existing generated final-test and structural '
              'extrapolation outcomes remain sealed; the earlier synthetic mechanism gate is unchanged.', '',
              'Sources: [CRUXEval, ICML 2024](https://proceedings.mlr.press/v235/gu24c.html), '
              '[BBH, Findings of ACL 2023](https://aclanthology.org/2023.findings-acl.824/). '
              'Exact commits, file hashes, configuration and source snapshot are recorded alongside the responses.', '']
    Path(config['report']).parent.mkdir(parents=True, exist_ok=True)
    Path(config['report']).write_text('\n'.join(lines))


def completed_summary(out, manifest, results, planned, wrapper):
    """Validate a completed artifact without replacing metadata or charging a lease."""
    out = Path(out)
    if manifest['status'] != 'complete' or len(results) != len(planned):
        raise ValueError('completed run coverage mismatch')
    expected = aggregate(results, planned, wrapper)
    summary = json.loads((out / 'summary.json').read_text())
    checksum = sha(out / 'responses.jsonl')
    if (manifest.get('responses_sha256') != checksum or summary.get('responses_sha256') != checksum
            or 'gpu_peak_bytes' not in summary or any(summary.get(k) != v for k, v in expected.items())):
        raise ValueError('completed summary, response checksum or metadata mismatch')
    return summary


@guarded
def run(config):
    import torch
    from .model_adapter import load
    from .registry import begin, finish, code_identity
    sources = assets(config)
    planned = plan(config)
    qa = json.loads(Path(config['preflight_result']).read_text())
    if (qa['status'] != 'passed' or qa['config_hash'] != digest(config)
            or qa['source_sha256'] != code_identity()['source_sha256']):
        raise ValueError('actual-tokenizer preflight must pass for this exact configuration')
    previous = Path(config['run_dir']) / 'published_behavior' / 'manifest.json'
    if previous.exists():
        finished = json.loads(previous.read_text())
        if finished.get('responses_sha256') and sha(previous.parent / 'responses.jsonl') != finished['responses_sha256']:
            raise ValueError('finished response checksum mismatch')
    out, manifest = begin(config, 'published_behavior', reuse_complete=True)
    started = time.monotonic()
    path = out / 'responses.jsonl'
    results = read_jsonl(path) if path.exists() else []
    if len(results) > len(planned):
        raise ValueError('more responses than planned')
    for result, (task, row) in zip(results, planned):
        if (result['task'] != task or result['id'] != row['id']
                or result['record_sha256'] != digest(row)
                or result['score'] != score(task, row, result['raw_response'])):
            raise ValueError('resume response identity or scoring changed')
    if manifest['status'] == 'complete':
        return completed_summary(out, manifest, results, planned, config['prompt_wrapper'])
    if len(results) == len(planned):
        summary = aggregate(results, planned, config['prompt_wrapper'])
        old_summary = json.loads((out / 'summary.json').read_text()) if (out / 'summary.json').exists() else {}
        summary.update(responses_sha256=sha(path), gpu_peak_bytes=old_summary.get('gpu_peak_bytes'),
                       recovered_without_inference=True)
        write_json(out / 'summary.json', summary)
        write_report(config, summary)
        finish(out, manifest, time.monotonic() - started, responses_sha256=summary['responses_sha256'],
               evaluated=len(results), planned=len(planned))
        return summary
    tokenizer, model = load(config)
    write_json(out / 'runtime.json', {
        'model_dtype': str(next(model.parameters()).dtype), 'device': str(model.device),
        'device_name': torch.cuda.get_device_name() if config['device'] == 'cuda' else 'cpu',
        'generation_config': model.generation_config.to_dict(), 'preflight': qa})
    index = len(results)
    while index < len(planned):
        task = planned[index][0]
        batch = []
        for pair in planned[index:index + config['batch_size']]:
            if pair[0] != task:
                break
            batch.append(pair)
        contents = [content_for(task, row, sources) for _, row in batch]
        prompts = [render(tokenizer, content, config['prompt_wrapper']) for content in contents]
        batch_started = time.monotonic()
        generated = generate(tokenizer, model, prompts, config['max_new_tokens'][task], task)
        with path.open('a') as stream:
            for (_, row), prompt, response in zip(batch, prompts, generated):
                result = {'task': task, 'id': row['id'], 'record_sha256': digest(row),
                          'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                          **response, 'score': score(task, row, response['raw_response'])}
                stream.write(json.dumps(result, sort_keys=True) + '\n')
                results.append(result)
            stream.flush()
        index = len(results)
        summary = aggregate(results, planned, config['prompt_wrapper'])
        write_json(out / 'summary.json', summary)
        print(f"published {index}/{len(planned)} {task} batch_seconds={time.monotonic() - batch_started:.2f}", flush=True)
    summary = aggregate(results, planned, config['prompt_wrapper'])
    summary['responses_sha256'] = sha(path) if path.exists() else None
    summary['gpu_peak_bytes'] = torch.cuda.max_memory_allocated() if config['device'] == 'cuda' else None
    write_json(out / 'summary.json', summary)
    write_report(config, summary)
    finish(out, manifest, time.monotonic() - started,
           'complete' if summary['complete'] else 'budget_limited',
           evaluated=len(results), planned=len(planned), responses_sha256=summary['responses_sha256'])
    return summary
