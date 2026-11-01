"""Calibration-only error diagnostics and prefix-preserving length exploration.

Original scores and competence gates are never changed. Diagnostic extraction is
target-blind and cannot make a truncated response an official success.
"""
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import re
import time

from . import arithmetic_paired_calibration as pilot
from . import arithmetic_paired_stage as stages
from . import arithmetic_paired_programs as programs
from . import arithmetic_state_common as common
from . import arithmetic_graph_capture as capture
from . import arithmetic_graph_readouts as storage
from . import arithmetic_semantic_controls as semantic
from . import relationship_capture as base
from . import overnight_relationship_capture as journal
from . import budget
from .datasets import digest

AUDIT = 'discovery_arithmetic_paired_error_audit_v1'
CONTINUE = 'discovery_arithmetic_paired_continuation_v1'
REPORT = 'discovery_arithmetic_paired_exploration_report_v1'
CAP = 1024
LEASE_STAGE = 'protocol_calibration'


def answer_values(text, scope, *, diagnostic=False):
    """Last explicit answer label only: no searching for expected values/numbers.

    Diagnostic grammar additionally admits Markdown headings and a value on the
    next line. It does not extract unlabeled prose, traces, tuples or print output.
    A later malformed answer label overrides an earlier valid one.
    """
    if scope not in ('single', 'all'): raise ValueError('known answer scope required')
    if diagnostic:
        labels = list(re.finditer(r'(?im)^[ \t]*(?:#{1,6}[ \t]+)?(?:\*\*)?(?:Final[ \t]+)?Answer(?:\*\*)?:(?:\*\*)?[ \t]*', text))
        if not labels: return None
        suffix = text[labels[-1].end():].lstrip(' \t\r\n')
        value = suffix.splitlines()[0].strip() if suffix else ''
    else:
        labels = re.findall(r'(?m)^\s*Answer:[ \t]*([^\r\n]*)', text)
        if not labels: return None
        value = labels[-1].strip()
    pattern = r'[+-]?\d+' if scope == 'single' else r'\[[ \t]*[+-]?\d+(?:[ \t]*,[ \t]*[+-]?\d+){3}[ \t]*\]'
    if not re.fullmatch(pattern, value): return None
    try: return [int(v) for v in re.findall(r'[+-]?\d+', value)]
    except ValueError: return None


def independent_score(case, text, tokens, truncated):
    values = answer_values(case['forced_prefix'] + text, case['scope'])
    accepted = values is not None and not truncated
    return dict(accepted=accepted, correct=bool(accepted and values == case['expected']),
        per_slot_correct=[a == b for a, b in zip(values, case['expected'])] if accepted else [False] * len(case['expected']))


def describe(case, response, source):
    text = case['forced_prefix'] + response['raw_response']
    strict = answer_values(text, case['scope'])
    diagnostic = answer_values(text, case['scope'], diagnostic=True)
    expected = case['expected']
    target_index = 0 if case['scope'] == 'single' else source['slot_names'].index(source['target_name'])
    candidates = dict(source['error_candidates'])
    matches = []
    # Multi-label coincidences remain explicit; no candidate is called a mechanism.
    if strict is not None:
        prediction = strict[target_index]
        matches = [k for k, value in candidates.items() if value == prediction]
        source_target = source['slot_names'].index(source['target_name'])
        if any(prediction == v for i, v in enumerate(source['final_values']) if i != source_target):
            matches.append('other_current_binding')
    return dict(id=case['id'], record_id=case['record_id'], component_id=case['component_id'],
        protocol=case['protocol'], scope=case['scope'], instruction=case['instruction'],
        kind=case['calibration_kind'] or 'arithmetic', depth=case['depth'], mutation=case['mutation'],
        numeric_seed=source['numeric_seed'], source_literal_visible=case['target_literal_visible'],
        tokens=len(response['output_token_ids']), truncated=response['truncated'],
        strict_values=strict, diagnostic_values=diagnostic, expected=expected,
        strict_correct=response['correct'], strict_accepted=response['accepted'],
        diagnostic_complete_correct=bool(not response['truncated'] and diagnostic == expected),
        explicit_answer_correct_before_cutoff=bool(strict == expected),
        target_correct=bool(response['accepted'] and strict[target_index] == expected[target_index]),
        candidate_matches=matches,
        wrong_target_candidate_matches=matches if strict is not None and strict[target_index] != expected[target_index] else [])


def cells(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r['protocol'] + '/' + r['scope']].append(r)
        groups[f"{r['protocol']}/{r['scope']}/{r['kind']}/depth{r['depth']}/instruction{r['instruction']}/mutation-{r['mutation']}"] .append(r)
    result = {}
    for key, group in sorted(groups.items()):
        result[key] = dict(rows=len(group), components=len({r['component_id'] for r in group}),
            strict_correct=sum(r['strict_correct'] for r in group),
            strict_accepted=sum(r['strict_accepted'] for r in group),
            target_correct=sum(r['target_correct'] for r in group),
            diagnostic_complete_correct=sum(r['diagnostic_complete_correct'] for r in group),
            truncated=sum(r['truncated'] for r in group),
            correct_explicit_answer_but_truncated=sum(r['truncated'] and r['explicit_answer_correct_before_cutoff'] for r in group),
            wrong_target_candidate_matches=dict(Counter(k for r in group for k in r['wrong_target_candidate_matches'])),
            ambiguous_wrong_candidate_rows=sum(len(r['wrong_target_candidate_matches']) > 1 for r in group))
    return result


def paired_scopes(rows):
    pairs = defaultdict(dict)
    for r in rows:
        key = (r['record_id'], r['protocol'], r['instruction'])
        if r['scope'] in pairs[key]: raise ValueError('duplicate scope relative')
        pairs[key][r['scope']] = r
    result = {}
    for protocol in programs.PROTOCOLS:
        group = [p for (_, pcode, _), p in pairs.items() if pcode == protocol]
        if any(set(p) != {'single', 'all'} for p in group): raise ValueError('incomplete query-scope pairing')
        result[protocol] = dict(pairs=len(group), single_target_correct=sum(p['single']['target_correct'] for p in group),
            all_target_correct=sum(p['all']['target_correct'] for p in group),
            all_only_correct=sum(p['all']['target_correct'] and not p['single']['target_correct'] for p in group),
            single_only_correct=sum(p['single']['target_correct'] and not p['all']['target_correct'] for p in group),
            both_accepted=sum(p['single']['strict_accepted'] and p['all']['strict_accepted'] for p in group),
            accepted_target_disagreements=sum(p['single']['strict_accepted'] and p['all']['strict_accepted'] and
                p['single']['strict_values'][0] != p['all']['strict_values'][2] for p in group))
    return result


def load_pilot(request):
    cfg = base._json(request['path'], request['sha256']); proof = common.completed(cfg)
    native = base._json(cfg['native_config']['path'], cfg['native_config']['sha256']); common.completed(native)
    prepared = base._json(Path(native['run_dir']) / 'results.json')
    wanted = set(prepared['calibration_case_ids']); cases = {}
    with Path(prepared['prepared_cases']['path']).open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['id'] in wanted:
                if row['split'] != 'calibration' or row['delay'] != 0: raise ValueError('calibration-only cohort required')
                cases[row['id']] = row
    records, pins = {}, dict(config=request, completion=storage._pin(Path(cfg['run_dir']) / 'completion_manifest_v1.json'))
    for name, entry in proof['artifacts'].items():
        if not name.startswith('batch_'): continue
        pins[name] = entry
        for row in base._json(entry['path'], entry['sha256'])['records']:
            if row['id'] in records: raise ValueError('duplicate pilot response')
            case = cases[row['id']]
            score = independent_score(case, row['raw_response'], row['output_token_ids'], row['truncated'])
            if any(row[k] != v for k, v in score.items()): raise ValueError('independent pilot scoring differs')
            if row != pilot.score_response(case, row['raw_response'], row['output_token_ids'], row['truncated']):
                raise ValueError('pilot identities/labels differ')
            records[row['id']] = row
    if set(records) != wanted or set(cases) != wanted or len(wanted) != 1296: raise ValueError('full calibration factorial required')
    if pilot.summarize(list(records.values())) != base._json(Path(cfg['run_dir']) / 'results.json')['summary']:
        raise ValueError('pilot summary differs')
    pins['prepared'] = prepared['prepared_cases']
    manifest, path = stages.dataset(native); sources = {}
    with path.open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['split'] == 'calibration': sources[row['id']] = row
    pins['source_dataset'] = manifest['dataset']
    if not all(c['record_id'] in sources for c in cases.values()): raise ValueError('source join missing')
    for case in cases.values():
        row = sources[case['record_id']]
        expected = [row['expected_answer']] if case['scope'] == 'single' else row['final_values']
        if case['expected'] != expected or case['component_id'] != row['component_id']:
            raise ValueError('source oracle join differs')
    return cfg, cases, records, sources, pins


def receipt(config, source, result, artifacts):
    folder = Path(config['run_dir'])
    base._put(folder / 'results.json', result)
    base._put(folder / 'completion_manifest_v1.json', dict(status='complete_exploratory',
        source=source, config_hash=digest(config), evaluation_role=config['evaluation_role'],
        artifacts=dict(artifacts, results=storage._pin(folder / 'results.json')),
        new_model_queries=result['new_model_queries']))
    return result


def audit(config):
    source = common.validate_role(config, AUDIT); semantic.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
    models, details, inputs = {}, {}, {}
    for alias, request in config['pilots'].items():
        cfg, cases, records, sources, pins = load_pilot(request)
        rows = [describe(cases[k], records[k], sources[cases[k]['record_id']]) for k in sorted(cases)]
        models[alias] = dict(cases=len(rows), cells=cells(rows), scope_pairs=paired_scopes(rows),
            model=base._json(cfg['profile']['path'], cfg['profile']['sha256'])['model'])
        details[alias] = rows; inputs[alias] = pins
    path = folder / 'diagnostic_rows.json'; base._put(path, details)
    result = dict(status='complete_exploratory', evaluation_role=AUDIT, source=source, config_hash=digest(config),
        inputs=inputs, models=models, new_model_queries=0, formal_capture_submitted=False,
        generated_holdouts_opened=False, original_scores_unchanged=True,
        policy='diagnostic extraction is target-blind; candidate matches are ambiguous descriptions, not mechanisms; no inferential claims')
    return receipt(config, source, result, dict(diagnostic_rows=storage._pin(path)))


def continuation_plan(cases, records, size):
    if size not in (32, 64): raise ValueError('fixed continuation batches required')
    pending = [k for k in sorted(cases) if records[k]['truncated']]
    for protocol in programs.PROTOCOLS:
        group = [k for k in pending if cases[k]['protocol'] == protocol]
        for first in range(0, len(group), size):
            yield group[first:first + size]


def continuation_output(tokenizer, model, ids, cases, records):
    """Append to exact generated token prefixes; never decode/re-tokenize them."""
    import torch
    sequences, lengths = [], []
    for key in ids:
        case, row = cases[key], records[key]
        if not row['truncated']: raise ValueError('only truncated outputs may continue')
        if tokenizer(case['prompt'], add_special_tokens=False)['input_ids'] != case['input_token_ids']:
            raise ValueError('runtime native prompt differs')
        if tokenizer.decode(row['output_token_ids'], skip_special_tokens=True) != row['raw_response']:
            raise ValueError('saved output token/text identity differs')
        lengths.append(len(row['output_token_ids']))
        sequences.append(case['input_token_ids'] + row['output_token_ids'])
    if len(set(lengths)) != 1 or lengths[0] >= CAP: raise ValueError('homogeneous bounded remaining lengths required')
    eos = model.generation_config.eos_token_id
    eos = tokenizer.eos_token_id if eos is None else eos
    eos = set(eos if isinstance(eos, list) else [eos])
    if any(t in eos for key in ids for t in records[key]['output_token_ids']): raise ValueError('cannot continue past EOS')
    width = max(map(len, sequences)); pad = tokenizer.pad_token_id
    token_ids = torch.tensor([[pad] * (width - len(s)) + s for s in sequences], device=model.device)
    mask = torch.tensor([[0] * (width - len(s)) + [1] * len(s) for s in sequences], device=model.device)
    with torch.inference_mode():
        output = model.generate(input_ids=token_ids, attention_mask=mask, do_sample=False, use_cache=True,
            max_new_tokens=CAP - lengths[0], logits_to_keep=1, pad_token_id=pad)
    responses = []
    for key, new in zip(ids, output[:, width:].cpu().tolist()):
        stop = next((i + 1 for i, t in enumerate(new) if t in eos), None)
        added = new[:stop] if stop is not None else new
        tokens = records[key]['output_token_ids'] + added
        truncated = stop is None and len(tokens) >= CAP
        case = cases[key]; text = tokenizer.decode(tokens, skip_special_tokens=True)
        score = independent_score(case, text, tokens, truncated)
        responses.append(dict(records[key], raw_response=text, output_token_ids=tokens, truncated=truncated,
            **score, parsed=programs.parse_answer(case['forced_prefix'] + text, case['scope']),
            prefix_tokens=len(records[key]['output_token_ids']), added_tokens=len(added), continued=True))
    return responses


def continue_run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, CONTINUE); semantic.literature(config)
    if config['total_generated_token_ceiling'] != CAP: raise ValueError('frozen length contrast required')
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        cfg, cases, records, sources, pins = load_pilot(config['pilot'])
        profile = base._json(cfg['profile']['path'], cfg['profile']['sha256'])
        size = 64 if profile['hidden_size'] == 4096 else 32
        if config['generation_batch_size'] != size: raise ValueError('fixed checkpoint batch required')
        batches = list(continuation_plan(cases, records, size)); saved, artifacts, pending = {}, {}, []
        for index, ids in enumerate(batches):
            path = folder / f'continuation_{index:04d}.json'
            if not path.exists(): pending.append((index, ids)); continue
            item = base._json(path)
            if item['source'] != source or item['config_hash'] != digest(config) or item['ids'] != ids:
                raise ValueError('resumed continuation identity differs')
            if [r['id'] for r in item['records']] != ids: raise ValueError('resumed continuation cohort differs')
            for row in item['records']:
                key = row['id']; old = records[key]; prefix = old['output_token_ids']
                if row['output_token_ids'][:len(prefix)] != prefix or len(row['output_token_ids']) > CAP:
                    raise ValueError('saved continuation changed prefix or ceiling')
                check = independent_score(cases[key], row['raw_response'], row['output_token_ids'], row['truncated'])
                if any(row[k] != v for k, v in check.items()): raise ValueError('saved continuation score differs')
                for field in ('id', 'record_id', 'component_id', 'scope', 'protocol', 'instruction', 'expected', 'mutation', 'depth', 'calibration_kind'):
                    if row[field] != old[field]: raise ValueError('saved continuation labels differ')
                saved[key] = row
            artifacts[f'continuation_{index:04d}'] = storage._pin(path)
        started = time.monotonic(); lease = None; status = 'failed'
        attempt = dict(attempted=0, returned=0, committed=len(saved))
        attempt_path = folder / ('attempt_live_' + os.environ['SLURM_JOB_ID'] + '.json')
        try:
            if pending:
                lease = budget.reserve(dict(device='cuda', model=profile['model'], model_revision=profile['model_revision'],
                    run_dir=config['run_dir'], budget_ledger='artifacts/binding/gpu_usage_uncapped.json'), LEASE_STAGE)
                maximum = max(len(cases[k]['input_token_ids']) + len(records[k]['output_token_ids']) for _, ids in pending for k in ids)
                tokenizer, model = capture._CORE.load_models(dict(profile, batch_size=size), max_prompt_tokens=maximum)
                import torch
                m = model.config; free, _ = torch.cuda.mem_get_info()
                total_length = max(len(c['input_token_ids']) for c in cases.values()) + CAP
                if total_length > 4096: raise ValueError('continuation exceeds audited context limit')
                kv = 2 * m.num_hidden_layers * m.num_key_value_heads * (m.hidden_size // m.num_attention_heads) * 2 * size * total_length
                margin = (2 if m.hidden_size == 4096 else 4) * 1024**3
                if free < kv + margin: raise ValueError('fixed continuation batch does not fit')
                base._put(folder / ('memory_review_' + os.environ['SLURM_JOB_ID'] + '.json'),
                    dict(source=source, prefill=model.overnight_memory_review, batch_size=size, free_after_load=free,
                        kv_estimate_bytes=kv, working_margin_bytes=margin, total_generated_token_ceiling=CAP))
                from .gpu_telemetry import UUIDMonitor
                with UUIDMonitor() as monitor:
                    for index, ids in pending:
                        attempt['attempted'] += len(ids); journal._journal(attempt_path, attempt)
                        output = continuation_output(tokenizer, model, ids, cases, records)
                        if len(output) != len(ids): raise ValueError('complete continuation batch required')
                        attempt['returned'] += len(output)
                        path = folder / f'continuation_{index:04d}.json'
                        base._put(path, dict(source=source, config_hash=digest(config), ids=ids, records=output))
                        saved.update({r['id']: r for r in output}); artifacts[f'continuation_{index:04d}'] = storage._pin(path)
                        attempt['committed'] = len(saved); journal._journal(attempt_path, attempt)
                        journal._journal(folder / 'progress.json', dict(captured_rows=len(saved)))
                        print(f'prefix continuation {len(saved)}/{sum(map(len, batches))}', flush=True)
                    attempt['gpu'] = monitor.summary()
            if set(saved) != {k for ids in batches for k in ids}: raise ValueError('complete continuation cohort required')
            merged = {k: saved.get(k, r) for k, r in records.items()}
            details = [describe(cases[k], merged[k], sources[cases[k]['record_id']]) for k in sorted(cases)]
            path = folder / 'diagnostic_rows.json'; base._put(path, details); artifacts['diagnostic_rows'] = storage._pin(path)
            result = dict(status='complete_exploratory', evaluation_role=CONTINUE, source=source, config_hash=digest(config),
                inputs=pins, model=profile['model'], model_revision=profile['model_revision'], cases=len(cases),
                new_model_queries=len(saved), reused_completed_responses=len(records) - len(saved),
                cells=cells(details), scope_pairs=paired_scopes(details), formal_capture_submitted=False,
                generated_holdouts_opened=False, original_scores_unchanged=True, total_generated_token_ceiling=CAP,
                policy='prefix-preserving continuation of every truncated calibration response; completed EOS outputs reused; not monolithic reruns or isolated reasoning effects')
            result = receipt(config, source, result, artifacts)
            status = 'complete'; return result
        finally:
            attempt.update(status=status, wall_seconds=time.monotonic() - started)
            journal._journal(attempt_path, attempt)
            try: base._put(folder / ('attempt_' + os.environ['SLURM_JOB_ID'] + '_review_v1.json'), attempt)
            finally:
                if lease is not None: budget.release(lease, attempt['wall_seconds'], status)


def report(config):
    source = common.validate_role(config, REPORT); semantic.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
    request = config['audit']; cfg = base._json(request['path'], request['sha256']); common.completed(cfg)
    original = base._json(Path(cfg['run_dir']) / 'results.json')
    models, inputs = {}, dict(audit=storage._pin(Path(cfg['run_dir']) / 'results.json'))
    for alias, req in config.get('continuations', {}).items():
        cfg = base._json(req['path'], req['sha256']); common.completed(cfg)
        models[alias] = base._json(Path(cfg['run_dir']) / 'results.json')
        inputs[alias] = storage._pin(Path(cfg['run_dir']) / 'results.json')
    lines = ['# Exploratory calibration error and length audit', '',
        'Calibration-only discovery. Original pilot scores and competence gates remain unchanged. '
        'Diagnostic extraction accepts explicit Markdown answer headings without consulting gold values. '
        'Truncated outputs remain failures in strict and complete-response diagnostic scores. '
        'Answer-before-cutoff is reported separately, never used to pass a gate. '
        'No formal captures, probe fits, causal interventions or sealed-final access.', '',
        '| Model | Protocol | Scope | Cases | Original strict | Diagnostic complete | Truncated | Correct answer but truncated | Continued strict |',
        '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for alias, model in original['models'].items():
        for protocol in programs.PROTOCOLS:
            for scope in programs.SCOPES:
                key = protocol + '/' + scope; c = model['cells'][key]; n = c['rows']
                after = models.get(alias, {}).get('cells', {}).get(key)
                value = f"{100 * after['strict_correct'] / n:.2f}%" if after else 'pending'
                lines.append(f"| {alias} | {protocol} | {scope} | {n} | {100*c['strict_correct']/n:.2f}% | "
                    f"{100*c['diagnostic_complete_correct']/n:.2f}% | {c['truncated']} | {c['correct_explicit_answer_but_truncated']} | {value} |")
    lines += ['', '## Matched query-scope diagnostics', '',
        'Compare the same retained target, rather than single-value accuracy against the harder all-four joint metric. '
        'Every pair has identical source, instruction and protocol. Prefix continuations preserve earlier generated tokens, '
        'but are not guaranteed equivalent to one monolithic greedy run because batching/numerical kernels can differ.', '',
        '| Model | Protocol | Pairs | Single target correct | All-scope target correct | Both accepted | Accepted predictions disagree |',
        '|---|---|---:|---:|---:|---:|---:|']
    for alias, model in original['models'].items():
        for protocol, p in model['scope_pairs'].items():
            lines.append(f"| {alias} | {protocol} | {p['pairs']} | {p['single_target_correct']} | {p['all_target_correct']} | {p['both_accepted']} | {p['accepted_target_disagreements']} |")
    lines += ['', 'Candidate-error matches are retained in the JSON with all coincidences; matching a stale value, '
        'current operand recomputation or another binding does not identify an internal mechanism. '
        'Cells break down task/depth/instruction/mutation, with structural component counts. '
        'No wording is selected, no significance tests are performed, and these finite calibration components '
        'cannot support novel-family generalization claims.', '']
    path = Path(config['report']); base._publish(path, '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', evaluation_role=REPORT, source=source, config_hash=digest(config),
        inputs=inputs, new_model_queries=0, total_continuation_prefills=sum(m['new_model_queries'] for m in models.values()),
        formal_capture_submitted=False, generated_holdouts_opened=False)
    return receipt(config, source, result, dict(report=storage._pin(path)))
