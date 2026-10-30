"""Cached-checkpoint feasibility suites using one continuously batched engine.

Public benchmarks and generated discovery/calibration data only. This module never
opens generated final-test or extrapolation outcomes or changes historical gates.
"""
from __future__ import annotations

from collections import defaultdict
import json
import time
from pathlib import Path

from .datasets import digest, read_jsonl, write_json
from .published_benchmarks import assets, content_for, immutable, plan, render, score, sha
from .registry import code_identity, guarded


def configure_runtime(config):
    import os
    import sys
    manifest = Path(config['runtime_manifest'])
    if sha(manifest) != config['runtime_manifest_sha256']:
        raise ValueError('runtime manifest changed')
    package = json.loads(manifest.read_text())['package_root']
    if not (Path(package) / 'vllm/__init__.py').exists():
        raise ValueError('isolated CUDA12.9 runtime missing')
    sys.path.insert(0, package)
    os.environ['PYTHONPATH'] = package + ':' + os.environ.get('PYTHONPATH', '')
    os.environ['CUDA_HOME'] = config['cuda_home']
    os.environ['PATH'] = config['cuda_home'] + '/bin:' + os.environ.get('PATH', '')
    os.environ.update(VLLM_USE_FLASHINFER_SAMPLER='0', VLLM_WORKER_MULTIPROC_METHOD='spawn',
                      VLLM_NO_USAGE_STATS='1', DO_NOT_TRACK='1', TOKENIZERS_PARALLELISM='false')


def generated_rows(section):
    from .interpreter import execute
    from .program_diagnostics import validate_rows
    path = Path(section['dataset'])
    manifest = json.loads(path.with_suffix('.manifest.json').read_text())
    if sha(path) != section['sha256'] or manifest['sha256'] != section['sha256']:
        raise ValueError('generated discovery dataset checksum changed')
    rows = read_jsonl(path)
    if section['kind'] == 'computation_routing':
        from .computation_routing_programs import validate_rows, ROLE
        if manifest['evaluation_role'] != ROLE:
            raise ValueError('computation/routing calibration role differs')
        validate_rows(rows)
        return rows
    if section['kind'] == 'arithmetic_readout':
        from .arithmetic_readout import validate_rows, ROLE
        if manifest['evaluation_role'] != ROLE:
            raise ValueError('arithmetic readout feasibility role differs')
        return validate_rows(rows)
    if section['kind'] == 'live_load':
        from .live_load import validate_rows, ROLE
        if manifest['evaluation_role'] != ROLE:
            raise ValueError('computed retention study role differs')
        return validate_rows(rows)
    if section['kind'] == 'competition':
        from .competition import validate_rows, ROLE
        if manifest['evaluation_role'] != ROLE:
            raise ValueError('competition discovery role differs')
        eligibility = json.loads(Path(section['eligibility_artifact']).read_text())
        if sha(section['eligibility_artifact']) != section['eligibility_sha256']:
            raise ValueError('competition prerequisite evidence changed')
        selected = eligibility['exploratory_calibration_gates'][section['eligible_model']]['arithmetic_free']['validated_protocol']
        if not selected or section['variants'] != [selected]:
            raise ValueError('competition requires the validated arithmetic-free protocol')
        return validate_rows(rows)
    if section['kind'] == 'diagnostic':
        return validate_rows(rows, section['diagnostic_kind'])
    if section['kind'] != 'counterbalanced' or manifest['evaluation_role'] != 'counterbalanced_followup_only':
        raise ValueError('only registered discovery/calibration sources are eligible')
    if len(rows) != 768 or len({r['id'] for r in rows}) != 768:
        raise ValueError('counterbalanced cohort incomplete')
    groups = defaultdict(list)
    for row in rows:
        if row['split'] not in ('train', 'development') or row['evaluation_role'] != 'counterbalanced_followup_only':
            raise ValueError('generated final outcomes are sealed')
        truth = execute(row['source'])
        if truth['expected_answer'] != row['expected_answer'] or truth['execution_trace'] != row['execution_trace']:
            raise ValueError('counterbalanced semantics changed')
        groups[row['paired_group_id']].append(row)
    for pair in groups.values():
        if (len(pair) != 2 or {r['query_followed_by_distractor'] for r in pair} != {False, True}
                or pair[0]['expected_answer'] != pair[1]['expected_answer']):
            raise ValueError('counterbalanced pair differs')
    return rows


def score_case(case, raw):
    if case['kind'] == 'published':
        return score(case['task'], case['record'], raw)
    if case['kind'] == 'computation_routing':
        from .computation_routing_programs import score_case as routing_score
        return routing_score(case, raw)
    from .calibration import parse_completion, VARIANTS
    prediction = parse_completion(raw, VARIANTS[case['variant']]['answer_mode'])
    result = dict(prediction=prediction, valid=prediction is not None,
                  correct=prediction == case['record']['expected_answer'])
    if case['kind'] in ('competition', 'live_load'):
        result['compatible_error_labels'] = sorted({a['label'] for a in case['record']['error_alternatives']
                                                   if prediction == a['value'] and not result['correct']})
    return result


def preflight(config):
    from transformers import AutoTokenizer
    from .calibration import prompt, VARIANTS
    from .interpreter import python_oracle
    from .model_adapter import configure_tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tokenizer, config)
    cases = []
    for section in config['sections']:
        if section['kind'] == 'published':
            effective = {**config, **section}
            sources = assets(effective)
            if sha(effective['dataset']) != section['sha256']:
                raise ValueError('published dataset changed')
            for task, row in plan(effective):
                text = render(tokenizer, content_for(task, row, sources), section['prompt_wrapper'])
                cases.append(dict(section=section['name'], kind='published', task=task, id=row['id'], record=row,
                                  prompt_wrapper=section['prompt_wrapper'], prompt=text,
                                  max_new_tokens=config['max_new_tokens'][task],
                                  stop=['[/ANSWER]'] if task.startswith('cruxeval') else ['\n\nQ:']))
        else:
            if section['kind'] == 'competition':
                evidence = json.loads(Path(section['eligibility_artifact']).read_text())['results'][section['eligible_model']]
                if evidence['model'] != config['model'] or evidence['revision'] != config['model_revision']:
                    raise ValueError('competition checkpoint differs from eligible evidence')
            rows = generated_rows(section)
            for start in range(0, len(rows), 128):
                batch = rows[start:start + 128]
                oracle = python_oracle([r.get('oracle_source', r['source']) for r in batch])
                if any(r['expected_answer'] != o['answer'] for r, o in zip(batch, oracle)):
                    raise ValueError('independent generated-program oracle differs')
            for variant in section['variants']:
                if section['kind'] == 'computation_routing':
                    from .computation_routing_programs import instruction_spec
                    spec = instruction_spec(variant)
                else:
                    spec = VARIANTS[variant]
                for row in rows:
                    if section['kind'] == 'computation_routing':
                        from .computation_routing_programs import prompt as routing_prompt
                        text, _ = routing_prompt(tokenizer, row, variant)
                    else:
                        text, _ = prompt(tokenizer, row, variant)
                    cases.append(dict(section=section['name'], kind=section['kind'], task=variant, variant=variant,
                                      id=row['id'], record=row, prompt=text, max_new_tokens=spec['max_new_tokens'],
                                      stop=['\n\n'] if spec['stop_at_blank_line'] else []))
    keys = [(c['section'], c['task'], c['id']) for c in cases]
    if len(set(keys)) != len(cases):
        raise ValueError('suite has duplicate cases')
    for case in cases:
        case['input_token_ids'] = tokenizer(case['prompt'], add_special_tokens=False)['input_ids']
        if len(case['input_token_ids']) + case['max_new_tokens'] > config['context_limit']:
            raise ValueError('suite prompt exceeds registered context limit')
        case['prompt_sha256'] = digest(case['prompt'])
        if case['kind'] == 'published':
            row = case['record']
            gold = (f"[ANSWER]\nassert f({row['input']}) == {row['output']}\n[/ANSWER]" if case['task'].startswith('cruxeval')
                    else 'So the answer is ' + row['target'] + '.')
            if not score_case(case, gold)['correct']:
                raise ValueError('gold scorer roundtrip failed')
    naming = {}
    for case in cases:
        if case['kind'] == 'competition' and case['record']['family'] == 'versions':
            row = case['record']
            key = (row['base_id'], row['updates'], row['tail_placement'], row['query_role'], row['lexical_realization'])
            naming.setdefault(key, {})[row['condition']] = len(case['input_token_ids'])
    if any(c['informative'] != c['misleading'] for c in naming.values()):
        raise ValueError('competition naming contrast has unmatched prompt token lengths')
    length_pairs = {}
    for case in cases:
        if case['kind'] != 'competition':continue
        row = case['record']
        for axis, others in [('updates', ('condition', 'lexical_realization', 'query_role', 'tail_placement')),
                             ('tail_placement', ('condition', 'lexical_realization', 'query_role', 'updates'))]:
            key = (row['base_id'], axis, *(row[k] for k in others))
            length_pairs.setdefault(key, set()).add(len(case['input_token_ids']))
    if any(len(values) != 1 for values in length_pairs.values()):
        raise ValueError('competition version/tail contrast has unmatched prompt token lengths')
    layout_proof = None
    if any(c['kind'] == 'live_load' for c in cases):
        from .live_load import validate_token_layouts
        layout_proof = validate_token_layouts(cases, tokenizer)
    path = Path(config['prepared_cases'])
    immutable(path, ''.join(json.dumps(c, sort_keys=True) + '\n' for c in cases).encode())
    result = dict(status='passed', config_hash=digest(config), source_sha256=code_identity()['source_sha256'],
                  cases=len(cases), prepared_cases_sha256=sha(path), generated_holdouts_opened=False, model_inference=False)
    if layout_proof is not None:result['live_load_layout'] = layout_proof
    write_json(config['preflight_result'], result)
    return result


def prepared(config, source_sha256=None):
    qa = json.loads(Path(config['preflight_result']).read_text())
    if (qa['status'] != 'passed' or qa['config_hash'] != digest(config)
            or qa['source_sha256'] != (source_sha256 or code_identity()['source_sha256']) or sha(config['prepared_cases']) != qa['prepared_cases_sha256']):
        raise ValueError('matching tokenizer/semantic preflight required')
    return qa, read_jsonl(config['prepared_cases'])


def validate_response(case, row):
    if (any(row[key] != case[key] for key in ('section', 'task', 'id', 'input_token_ids', 'prompt_sha256'))
            or row['record_sha256'] != digest(case['record']) or len(row['output_token_ids']) > case['max_new_tokens']
            or row['score'] != score_case(case, row['raw_response'])):
        raise ValueError('suite response identity, token ceiling or score differs')


def summarize(rows, total):
    groups = defaultdict(list)
    for row in rows:
        groups[row['section'], row['task']].append(row)
    return dict(complete=len(rows) == total, evaluated=len(rows), planned=total,
                cells=[dict(section=s, task=t, n=len(group), correct=sum(r['score']['correct'] for r in group),
                            valid=sum(r['score']['valid'] for r in group)) for (s, t), group in groups.items()],
                interpretation='Exploratory checkpoint feasibility/capacity comparison. No causal or confirmatory claim; historical gates unchanged.',
                generated_holdouts_opened=False)


def engine_settings(config, memory_bytes):
    settings = {'tensor_parallel_size': config.get('tensor_parallel_size', 1), **config['engine']}
    for override in config.get('engine_memory_overrides', []):
        if memory_bytes <= override['max_memory_gib'] * 2**30:
            settings.update(override['settings'])
            break
    small = memory_bytes < 48 * 2**30
    if settings.get('max_num_seqs') == 'auto':
        settings['max_num_seqs'] = 256 if small else 512
    if settings.get('max_num_batched_tokens') == 'auto':
        settings['max_num_batched_tokens'] = 8192 if small else 16384
    return settings


@guarded
def run(config):
    from .registry import begin, finish
    from .gpu_telemetry import UUIDMonitor
    import importlib.metadata
    import torch
    from vllm import LLM, SamplingParams
    qa, cases = prepared(config)
    out, manifest = begin(config, 'checkpoint_suite', reuse_complete=True)
    response_path = out / 'responses.jsonl'
    rows = read_jsonl(response_path) if response_path.exists() else []
    if len(rows) > len(cases):
        raise ValueError('suite has excess saved responses')
    for case, row in zip(cases, rows):
        validate_response(case, row)
    if manifest['status'] == 'complete':
        if len(rows) != len(cases) or sha(response_path) != manifest['responses_sha256']:
            raise ValueError('completed suite changed')
        return summarize(rows, len(cases))
    started = time.monotonic()
    settings = engine_settings(config, torch.cuda.get_device_properties(0).total_memory)
    engine = LLM(model=config['model'], revision=config['model_revision'], tokenizer_revision=config['tokenizer_revision'],
                 dtype=config['dtype'], max_model_len=config['context_limit'],
                 enable_prefix_caching=True, enable_chunked_prefill=True, seed=0, generation_config='vllm', **settings)
    engine.generate([{'prompt_token_ids': c['input_token_ids']} for c in cases[:8]],
                    SamplingParams(temperature=0, max_tokens=16), use_tqdm=False)
    write_json(out / 'runtime.json', dict(device_name=torch.cuda.get_device_name(), load_warmup_seconds=time.monotonic() - started,
                                        engine=settings, preflight=qa,
                                        versions={name: importlib.metadata.version(name) for name in ('torch', 'transformers', 'vllm')}))
    timings = []
    with UUIDMonitor() as monitor:
        while len(rows) < len(cases):
            block = cases[len(rows):len(rows) + config['request_chunk_size']]
            params = [SamplingParams(temperature=0, top_p=1, max_tokens=c['max_new_tokens'], stop=c['stop'],
                                     include_stop_str_in_output=True, stop_token_ids=config['eos_token_ids']) for c in block]
            before = time.monotonic()
            outputs = engine.generate([{'prompt_token_ids': c['input_token_ids']} for c in block], params, use_tqdm=False)
            seconds = time.monotonic() - before
            if len(outputs) != len(block):
                raise ValueError('engine response count differs')
            generated = []
            for case, output in zip(block, outputs):
                if list(output.prompt_token_ids) != case['input_token_ids'] or len(output.outputs) != 1:
                    raise ValueError('engine changed exact prompt IDs or completion count')
                completion = output.outputs[0]
                row = {k: case[k] for k in ('section', 'task', 'id', 'input_token_ids', 'prompt_sha256')}
                row.update(record_sha256=digest(case['record']), raw_response=completion.text,
                           output_token_ids=list(completion.token_ids), finish_reason=completion.finish_reason,
                           score=score_case(case, completion.text))
                validate_response(case, row)
                generated.append(row)
            with response_path.open('a') as stream:
                for row in generated:stream.write(json.dumps(row, sort_keys=True) + '\n')
                stream.flush()
            rows += generated
            timings.append(dict(cases=len(block), generation_seconds=seconds, requests_per_second=len(block) / seconds,
                                output_tokens=sum(len(r['output_token_ids']) for r in generated)))
            write_json(out / 'progress.json', dict(**summarize(rows, len(cases)), timings=timings))
            print(f"checkpoint suite {len(rows)}/{len(cases)} in {seconds:.2f}s", flush=True)
    summary = summarize(rows, len(cases))
    summary.update(responses_sha256=sha(response_path), timings=timings, gpu=monitor.summary())
    write_json(out / 'summary.json', summary)
    finish(out, manifest, time.monotonic() - started, 'complete' if summary['complete'] else 'budget_limited',
           responses_sha256=summary['responses_sha256'], evaluated=len(rows), planned=len(cases))
    return summary


def audit(config):
    out = Path(config['run_dir']) / 'checkpoint_suite'
    manifest = json.loads((out / 'manifest.json').read_text())
    if (manifest['status'] != 'complete' or digest(manifest['identity']) != manifest['identity_hash']
            or manifest['identity']['config'] != config or sha(out / 'responses.jsonl') != manifest['responses_sha256']):
        raise ValueError('suite audit requires matching complete artifacts')
    qa, cases = prepared(config, manifest['identity']['code']['source_sha256'])
    rows = read_jsonl(out / 'responses.jsonl')
    if len(rows) != len(cases):
        raise ValueError('suite audit coverage differs')
    for case, row in zip(cases, rows):validate_response(case, row)
    summary = summarize(rows, len(cases))
    actual = json.loads((out / 'summary.json').read_text())
    if any(actual.get(k) != v for k, v in summary.items()):
        raise ValueError('saved suite summary differs')
    result = dict(status='passed', model=config['model'], revision=config['model_revision'],
                  identity_hash=manifest['identity_hash'], preflight=qa, **summary,
                  gpu=actual['gpu'], timings=actual['timings'], runtime=json.loads((out / 'runtime.json').read_text()))
    immutable(out / 'audit.json', (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return result


def collect(config):
    """Report complete exploratory suites without selecting on benchmark scores."""
    from .diagnostic_review import paired_counts
    results, pairs, gates = {}, {}, {}
    for name, spec in config['runs'].items():
        if sha(spec['config']) != spec['sha256']:
            raise ValueError('registered checkpoint-suite configuration changed')
        effective = json.loads(Path(spec['config']).read_text())
        result = audit(effective)
        _, cases = prepared(effective, result['preflight']['source_sha256'])
        rows = read_jsonl(Path(effective['run_dir']) / 'checkpoint_suite/responses.jsonl')
        results[name] = result
        paired = defaultdict(lambda: {'without': {}, 'with': {}})
        for case, row in zip(cases, rows):
            if case['kind'] == 'counterbalanced':
                record = case['record']
                side = 'with' if record['query_followed_by_distractor'] else 'without'
                paired[case['variant']][side][record['paired_group_id']] = dict(
                    expected_answer=record['expected_answer'], correct=row['score']['correct'],
                    prediction=row['score']['prediction'])
        pairs[name] = {variant: paired_counts(sides['without'], sides['with']) for variant, sides in paired.items()}
        gates[name] = {}
        for kind, families in [('arithmetic_forms', ('expression', 'assignment')),
                               ('arithmetic_free', ('copy_depth', 'overwrite_count'))]:
            cells = []
            for variant in ('print_direct_v3', 'print_trace_long_v1'):
                for split in ('train', 'development'):
                    for family in families:
                        group = [row for case, row in zip(cases, rows) if case['section'] == kind
                                 and case['variant'] == variant and case['record']['split'] == split
                                 and case['record']['family'] == family
                                 and (kind == 'arithmetic_forms' or case['record']['depth'] == 1)]
                        cells.append(dict(variant=variant, split=split, family=family, n=len(group),
                                          correct=sum(r['score']['correct'] for r in group),
                                          invalid=sum(not r['score']['valid'] for r in group)))
            def passes(variant, split):
                selected = [c for c in cells if c['variant'] == variant and c['split'] == split]
                return len(selected) == 2 and all(c['n'] >= 24 and c['correct'] / c['n'] >= .9
                                                 and c['invalid'] / c['n'] <= .05 for c in selected)
            candidate = next((v for v in ('print_direct_v3', 'print_trace_long_v1') if passes(v, 'train')), None)
            gates[name][kind] = dict(training_candidate=candidate,
                                    validated_protocol=candidate if candidate and passes(candidate, 'development') else None,
                                    cells=cells, scope='exploratory checkpoint feasibility; no replacement of historical decisions')
    combined = dict(status='passed', complete=True, results=results, counterbalanced_pairs=pairs,
                    exploratory_calibration_gates=gates, generated_holdouts_opened=False,
                    resource_policy='artifacts/binding/resource_policy_20261025.json')
    immutable(config['output'], (json.dumps(combined, sort_keys=True, indent=2) + '\n').encode())
    lines = ['# Cached-checkpoint feasibility and capacity comparisons', '',
             'Complete published cohorts and discovery/calibration programs. No generated final outcomes were opened. '
             'The original seven-billion-parameter checkpoint gates and scores are unchanged. '
             'CRUXEval uses literal-only equality without code execution; these are not official execution pass@k scores.', '',
             '| Checkpoint | Section | Protocol/task | Correct / n | Parseable |', '|---|---|---|---:|---:|']
    for name, result in results.items():
        for cell in result['cells']:
            lines.append(f"| {name} | {cell['section']} | {cell['task']} | {cell['correct']}/{cell['n']} | {cell['valid']} |")
    lines += ['', 'CodeLlama CRUXEval runs use the audited released completion boundary. '
              'The Llama instruction checkpoints use their native chat templates around identical released content; '
              'that comparison changes both checkpoint and serialization. BBH and generated calibration use native '
              'chat templates. Precision, exact revisions, prompts, token IDs, responses, GPU device, rates and hashes '
              'are retained separately for every checkpoint.', '',
              '| Checkpoint | Diagnostic | Training choice | Passed numeric validation |', '|---|---|---|---|']
    for name, entries in gates.items():
        for kind, gate in entries.items():
            lines.append(f"| {name} | {kind} | {gate['training_candidate']} | {gate['validated_protocol']} |")
    lines += ['', 'Calibration selects direct before trace using only elementary training cells at ≥90% accuracy '
              'and ≤5% invalid with at least 24 examples per cell, then tests that choice on numeric validation. '
              'There is no fallback after validation failure. These familiar task structures do not establish '
              'structural generalization or a causal binding mechanism.', '',
              '| Checkpoint | Protocol | Pairs | Without-only correct | With-only correct |', '|---|---|---:|---:|---:|']
    for name, variants in pairs.items():
        for variant, result in variants.items():
            lines.append(f"| {name} | {variant} | {result['n']} | {result['counts']['left_only_correct']} | {result['counts']['right_only_correct']} |")
    lines += ['', 'The counterbalanced follow-up removes the previous answer-magnitude/distractor confound. '
              'These are exact descriptive within-cohort comparisons; adding a dead statement also changes length '
              'and context. The results alone do not identify an internal cause.', '',
              'Compute accounting is uncapped under the user’s explicit project-priority instruction. '
              'Per-job walltimes keep jobs resumable; actual scheduler limits still apply.', '']
    immutable(config['report'], '\n'.join(lines).encode())
    return combined
