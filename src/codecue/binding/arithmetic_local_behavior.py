"""Three-instruction printed arithmetic calibration on one/two updates."""
from collections import defaultdict
import hashlib
import os
from pathlib import Path
import time

import numpy as np

from . import arithmetic_local_capture as capture
from . import arithmetic_local_programs as programs
from . import arithmetic_graph_readouts as original
from . import relationship_capture as base
from .datasets import digest
from .overnight_relationship_behavior import parse_integer

ROLE = 'discovery_arithmetic_local_behavior_v1'


def summarize(records):
    cells = defaultdict(list)
    for row in records:
        key = (row['instruction'], row['split'], row['depth'], row['query_kind'])
        cells[key].append(row)
    results = []
    for (instruction, split, depth, kind), rows in sorted(cells.items()):
        groups = defaultdict(list)
        for row in rows:
            groups[row['component_id']].append(row['correct'])
        results.append(dict(instruction=instruction, split=split, depth=depth, query_kind=kind,
            cases=len(rows), correct=sum(r['correct'] for r in rows), invalid=sum(r['parsed'] is None for r in rows),
            accuracy=float(np.mean([r['correct'] for r in rows])), families=len(groups),
            family_macro_accuracy=float(np.mean([np.mean(v) for v in groups.values()]))))
    return results


def run(config):
    from .confidence import _run_lock
    from .model_adapter import normalize_prompt
    import torch
    base._slurm()
    if config.get('evaluation_role') != ROLE or config.get('generation_batch_size') != 32 or config.get('max_new_tokens') != 12:
        raise ValueError('fixed printed short-arithmetic calibration recipe required')
    source = base._current_source(config)
    cap = base._json(config['capture_config'], config['capture_config_sha256'])
    profile, rows, preflight, cases = capture.inputs(cap)
    if source != preflight['source']:
        raise ValueError('local behavior and preparation source differ')
    folder = Path(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return audit(config)
        tokenizer = capture.legacy._CORE._tokenizer(profile)
        selected = []
        for row, case in zip(rows, cases):
            if row['depth'] not in (1, 2):
                continue
            for instruction, text in enumerate(programs.INSTRUCTIONS):
                prompt = normalize_prompt(tokenizer, tokenizer.apply_chat_template(
                    [{'role': 'user', 'content': text + '\n\n' + row['source']}], tokenize=False,
                    add_generation_prompt=True) + 'Output:')
                tokens = tokenizer(prompt, add_special_tokens=False)['input_ids']
                if not tokens or len(tokens) + 12 > 4096 or (instruction == 0 and (prompt != case['prompt'] or tokens != case['input_token_ids'])):
                    raise ValueError('native calibration prompt or original-instruction identity differs')
                selected.append(dict(id=row['id'] + ':i' + str(instruction), row=row, instruction=instruction,
                    prompt=prompt, input_ids_sha256=digest(tokens), token_count=len(tokens)))
        if len(selected) != 5508:
            raise ValueError('complete one/two-update three-instruction calibration required')
        identity = dict(source=source, config_hash=digest(config), evaluation_role=ROLE)
        journal = folder / 'manifest.json'
        manifest = base._json(journal) if journal.exists() else dict(identity, attempts=[])
        if any(manifest.get(k) != v for k, v in identity.items()):
            raise ValueError('calibration resume identity differs')
        attempt = dict(slurm_job_id=os.environ['SLURM_JOB_ID'], model_loaded=False, generated_answers_attempted=0, generated_answers_returned=0)
        manifest['attempts'].append(attempt)
        capture.legacy._CORE._journal(journal, manifest)
        completed, pending, artifacts = [], [], {}
        for first in range(0, len(selected), 32):
            path = folder / 'batches' / f'{first:06d}.json'
            subset = selected[first:first + 32]
            if path.exists():
                saved = base._json(path)
                if saved['config_hash'] != digest(config) or saved['source'] != source or saved['ids'] != [e['id'] for e in subset]:
                    raise ValueError('calibration batch identity differs')
                for record, example in zip(saved['responses'], subset):
                    if (record['id'] != example['id'] or record['input_ids_sha256'] != example['input_ids_sha256']
                            or parse_integer(record['raw_response']) != record['parsed']
                            or (record['parsed'] == example['row']['expected_answer']) != record['correct']):
                        raise ValueError('calibration persisted parsing/scoring differs')
                if len(saved['responses']) != len(subset):
                    raise ValueError('complete persisted calibration batch required')
                completed.extend(saved['responses'])
                artifacts[f'batch{first}'] = original._pin(path)
            else:
                pending.append((first, subset, path))
        started = time.monotonic()
        try:
            if pending:
                profile = dict(profile, batch_size=32)
                tokenizer, model = capture.legacy._CORE.load_models(profile, max_prompt_tokens=max(e['token_count'] + 12 for e in selected))
                attempt['model_loaded'] = True
                if hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() != preflight['chat_template_sha256']:
                    raise ValueError('runtime calibration tokenizer template differs')
                with base._monitor() as monitor:
                    try:
                        for first, subset, path in pending:
                            encoded = tokenizer([e['prompt'] for e in subset], add_special_tokens=False, padding=True, return_tensors='pt')
                            for i, e in enumerate(subset):
                                ids = encoded.input_ids[i][encoded.attention_mask[i].bool()].tolist()
                                if digest(ids) != e['input_ids_sha256']:
                                    raise ValueError('runtime native calibration IDs differ')
                            encoded = encoded.to(model.device)
                            attempt['generated_answers_attempted'] += len(subset)
                            capture.legacy._CORE._journal(journal, manifest)
                            with torch.inference_mode():
                                outputs = model.generate(**encoded, do_sample=False, max_new_tokens=12,
                                    pad_token_id=tokenizer.pad_token_id, use_cache=True)
                            texts = tokenizer.batch_decode(outputs[:, encoded.input_ids.shape[1]:], skip_special_tokens=True, clean_up_tokenization_spaces=False)
                            responses = []
                            for e, text in zip(subset, texts):
                                row, parsed = e['row'], parse_integer(text)
                                responses.append(dict(id=e['id'], component_id=row['component_id'], instruction=e['instruction'],
                                    split=row['split'], depth=row['depth'], query_kind=row['query_kind'], numeric_seed=row['numeric_seed'],
                                    lexical_realization=row['lexical_realization'], raw_response=text, parsed=parsed,
                                    correct=parsed == row['expected_answer'], expected=row['expected_answer'],
                                    input_ids_sha256=e['input_ids_sha256']))
                            if len(responses) != len(subset):
                                raise ValueError('calibration generation row count differs')
                            attempt['generated_answers_returned'] += len(subset)
                            base._put(path, dict(identity, ids=[e['id'] for e in subset], responses=responses))
                            artifacts[f'batch{first}'] = original._pin(path)
                            completed.extend(responses)
                            capture.legacy._CORE._journal(folder / 'progress.json', dict(captured_rows=len(completed), planned=len(selected)))
                            print(f'local short behavior {len(completed)}/{len(selected)}', flush=True)
                    finally:
                        attempt['runtime'] = dict(base._runtime(model), gpu=monitor.summary(),
                            forward='greedy language-model generation, max12 tokens, KV cache enabled')
            attempt.update(status='complete', wall_seconds=time.monotonic() - started)
            capture.legacy._CORE._journal(journal, manifest)
            result = dict(identity, status='complete_exploratory', model=profile['model'], cases=len(completed),
                metrics=summarize(completed), attempts=manifest['attempts'], generated_holdouts_opened=False,
                limitations='Adaptive discovery with explicit printed queries. All three instructions and invalids retained. '
                    'One-update calibration structures excluded from probe fits. No causal or untouched confirmation claim.')
            base._put(folder / 'summary.json', result)
            artifacts['summary'] = original._pin(folder / 'summary.json')
            base._put(folder / 'completion_manifest_v1.json', dict(identity, status='complete_exploratory', artifacts=artifacts))
            return result
        except Exception as exc:
            attempt.update(status='failed', error=f'{type(exc).__name__}: {exc}', wall_seconds=time.monotonic() - started)
            capture.legacy._CORE._journal(journal, manifest)
            raise


def audit(config):
    folder = Path(config['run_dir'])
    receipt = base._json(folder / 'completion_manifest_v1.json')
    if receipt['config_hash'] != digest(config) or receipt['status'] != 'complete_exploratory':
        raise ValueError('calibration completion identity differs')
    base._verify_source(config, receipt['source'])
    responses = []
    for key, entry in receipt['artifacts'].items():
        data = base._json(entry['path'], entry['sha256'])
        if key.startswith('batch'):
            for row in data['responses']:
                if parse_integer(row['raw_response']) != row['parsed'] or (row['parsed'] == row['expected']) != row['correct']:
                    raise ValueError('calibration response parsing/scoring changed')
            responses.extend(data['responses'])
    if len(responses) != 5508 or len({r['id'] for r in responses}) != 5508:
        raise ValueError('complete unique calibration answers required')
    summary = base._json(folder / 'summary.json')
    if summary['metrics'] != summarize(responses):
        raise ValueError('calibration summary differs from saved responses')
    return receipt
