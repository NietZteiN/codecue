"""Resumable generated-answer calibration; formal cohorts are never inferred."""
from collections import defaultdict
import json
import os
from pathlib import Path
import time

from . import arithmetic_paired_stage as stages
from . import arithmetic_paired_programs as programs
from . import arithmetic_state_common as common
from . import arithmetic_semantic_controls as semantic
from . import arithmetic_graph_capture as capture
from . import relationship_capture as base
from . import arithmetic_graph_readouts as storage
from . import overnight_relationship_capture as journal
from . import budget
from .datasets import digest

ROLE = 'discovery_arithmetic_paired_calibration_v1'
LIMITS = dict(output_only=64, intermediate_query=128, stepwise=512)


def score_response(case, text, tokens, truncated):
    if (not isinstance(text, str) or not isinstance(tokens, list) or len(tokens) > LIMITS[case['protocol']]
            or any(type(t) is not int or t < 0 for t in tokens) or type(truncated) is not bool):
        raise ValueError('bounded generated response required')
    parsed = programs.parse_answer(case['forced_prefix'] + text, case['scope'])
    accepted = parsed['valid'] and not truncated
    values = parsed.get('values', [])
    slots = [accepted and a == b for a, b in zip(values, case['expected'])] if accepted else [False] * len(case['expected'])
    return dict(id=case['id'], record_id=case['record_id'], component_id=case['component_id'], scope=case['scope'],
        protocol=case['protocol'], instruction=case['instruction'], calibration_kind=case['calibration_kind'] or 'arithmetic',
        depth=case['depth'], mutation=case['mutation'], raw_response=text, output_token_ids=tokens,
        truncated=truncated, parsed=parsed, accepted=bool(accepted), expected=case['expected'],
        per_slot_correct=slots, correct=bool(accepted and values == case['expected']))


def summarize(rows):
    cells = defaultdict(list)
    for row in rows:
        for key in ('overall', 'protocol/' + row['protocol'], 'scope/' + row['scope'],
                f"{row['protocol']}/{row['scope']}/{row['calibration_kind']}/depth{row['depth']}/instruction{row['instruction']}"):
            cells[key].append(row)
    result = {k: dict(rows=len(v), joint_accuracy=sum(r['correct'] for r in v) / len(v),
        slot_accuracy=sum(sum(r['per_slot_correct']) for r in v) / sum(len(r['expected']) for r in v),
        invalid_or_truncated=sum(not r['accepted'] for r in v), truncated=sum(r['truncated'] for r in v)) for k, v in cells.items()}
    gates = []
    for scope in programs.SCOPES:
        for kind, threshold in [('literal', .95), ('copy', .90), ('arithmetic', .70)]:
            for instruction in range(3):
                key = f'output_only/{scope}/{kind}/depth0/instruction{instruction}'
                cell = result.get(key)
                gates.append(dict(scope=scope, kind=kind, instruction=instruction, threshold=threshold,
                    rows=cell['rows'] if cell else 0, accuracy=cell['joint_accuracy'] if cell else None,
                    passed=bool(cell and cell['joint_accuracy'] >= threshold)))
    return dict(cells=result, gates=gates, output_only_competence_passed=all(g['passed'] for g in gates),
        gate_scope='finite calibration feasibility checks, not statistical confirmation; every wording and both scopes must qualify',
        formal_capture_submitted=False)


def batches(cases, size):
    offset = 0
    for protocol in programs.PROTOCOLS:
        rows = sorted([c for c in cases if c['protocol'] == protocol], key=lambda c: (c['scope'], c['instruction'], c['id']))
        for first in range(0, len(rows), size):
            part = rows[first:first + size]
            yield offset, part
            offset += len(part)


def generate(tokenizer, model, cases):
    import torch
    encoded = tokenizer([c['prompt'] for c in cases], add_special_tokens=False, padding=True, return_tensors='pt')
    for i, case in enumerate(cases):
        if encoded.input_ids[i][encoded.attention_mask[i].bool()].tolist() != case['input_token_ids']:
            raise ValueError('runtime generation tokens differ from native preflight')
    encoded = encoded.to(model.device); width = encoded.input_ids.shape[1]
    limit = LIMITS[cases[0]['protocol']]
    if any(c['protocol'] != cases[0]['protocol'] for c in cases): raise ValueError('homogeneous generation limits required')
    with torch.inference_mode():
        output = model.generate(**encoded, do_sample=False, use_cache=True, max_new_tokens=limit,
            logits_to_keep=1, pad_token_id=tokenizer.pad_token_id)
    eos = model.generation_config.eos_token_id
    eos = tokenizer.eos_token_id if eos is None else eos
    eos = set(eos if isinstance(eos, list) else [eos])
    responses = []
    for ids in output[:, width:].cpu().tolist():
        stop = next((i + 1 for i, t in enumerate(ids) if t in eos), None)
        truncated = stop is None and len(ids) >= limit
        ids = ids[:stop] if stop is not None else ids
        responses.append((tokenizer.decode(ids, skip_special_tokens=True), ids, truncated))
    return responses


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, ROLE); semantic.literature(config)
    if config['generation_batch_size'] not in (64, 128) or config['max_new_tokens'] != LIMITS:
        raise ValueError('fixed prospectively declared generation recipe required')
    request = config['native_config']; native_cfg = base._json(request['path'], request['sha256']); common.completed(native_cfg)
    prepared = base._json(Path(native_cfg['run_dir']) / 'results.json')
    wanted = set(prepared['calibration_case_ids'])
    cases = []
    with Path(prepared['prepared_cases']['path']).open() as stream:
        for line in stream:
            case = json.loads(line)
            if case['id'] in wanted:
                if case['split'] != 'calibration' or case['delay'] != 0: raise ValueError('calibration-only source selection required')
                cases.append(case)
    if len(cases) != len(wanted) or len(wanted) != 1296: raise ValueError('complete calibration factorial required')
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        profile = base._json(config['profile']['path'], config['profile']['sha256'])
        size = 128 if profile['hidden_size'] == 4096 else 64
        if config['generation_batch_size'] != size: raise ValueError('declared hardware/profile batch differs')
        profile = dict(profile, batch_size=size)
        base._put(folder / 'registration.json', dict(source=source, config_hash=digest(config), cases=len(cases),
            ordered_cases_sha256=digest([c['id'] for _, part in batches(cases, size) for c in part]),
            prepared_cases=prepared['prepared_cases'], no_formal_rows_inferred=True, policy='greedy; no wording choice; all invalid/truncated retained'))
        plan = list(batches(cases, size)); responses, artifacts, pending = [], {}, []
        for first, part in plan:
            path = folder / f'batch_{first:06d}.json'
            if not path.exists(): pending.append((first, part)); continue
            batch = base._json(path)
            if batch['source'] != source or batch['config_hash'] != digest(config) or batch['ids'] != [c['id'] for c in part]:
                raise ValueError('resumed calibration batch identity differs')
            if len(batch['records']) != len(part): raise ValueError('resumed batch incomplete')
            for case, saved in zip(part, batch['records']):
                if saved != score_response(case, saved['raw_response'], saved['output_token_ids'], saved['truncated']):
                    raise ValueError('resumed response scoring differs')
            responses.extend(batch['records']); artifacts[f'batch_{first:06d}'] = storage._pin(path)
        started = time.monotonic(); lease = None; status = 'failed'; attempt = dict(attempted=0, returned=0, committed=len(responses))
        attempt_path = folder / ('attempt_live_' + os.environ['SLURM_JOB_ID'] + '.json')
        try:
            if pending:
                lease = budget.reserve(dict(device='cuda', model=profile['model'], model_revision=profile['model_revision'],
                    run_dir=config['run_dir'], budget_ledger='artifacts/binding/gpu_usage_uncapped.json'), 'protocol_calibration')
                maximum = max(len(c['input_token_ids']) for c in cases)
                tokenizer, model = capture._CORE.load_models(profile, max_prompt_tokens=maximum)
                import torch
                m = model.config; free, _ = torch.cuda.mem_get_info()
                kv = 2 * m.num_hidden_layers * m.num_key_value_heads * (m.hidden_size // m.num_attention_heads) * 2 * size * (maximum + 512)
                margin = (2 if m.hidden_size == 4096 else 4) * 1024**3
                if free < kv + margin: raise ValueError('declared calibration batch/generation KV cache does not fit')
                base._put(folder / ('memory_review_' + os.environ['SLURM_JOB_ID'] + '.json'), dict(source=source, prefill=model.overnight_memory_review,
                    kv_estimate_bytes=kv, working_margin_bytes=margin, free_after_load_bytes=free,
                    batch_size=size, max_prompt_tokens=maximum, max_generated_tokens=512))
                from .gpu_telemetry import UUIDMonitor
                with UUIDMonitor() as monitor:
                    for first, part in pending:
                        attempt['attempted'] += len(part); journal._journal(attempt_path, attempt)
                        output = generate(tokenizer, model, part)
                        if len(output) != len(part): raise ValueError('complete generated batch required')
                        attempt['returned'] += len(output)
                        records = [score_response(c, *r) for c, r in zip(part, output)]
                        path = folder / f'batch_{first:06d}.json'
                        base._put(path, dict(source=source, config_hash=digest(config), ids=[c['id'] for c in part], records=records))
                        responses.extend(records); artifacts[f'batch_{first:06d}'] = storage._pin(path)
                        attempt['committed'] = len(responses); journal._journal(attempt_path, attempt)
                        journal._journal(folder / 'progress.json', dict(captured_rows=len(responses)))
                        print(f'paired calibration {len(responses)}/{len(cases)}', flush=True)
                    attempt['gpu'] = monitor.summary()
            if len(responses) != len(cases) or len({r['id'] for r in responses}) != len(cases): raise ValueError('complete unique calibration responses required')
            summary = summarize(responses)
            result = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=digest(config),
                model=profile['model'], model_revision=profile['model_revision'], cases=len(cases), summary=summary,
                new_model_queries=len(responses), query_count_scope='unique completed prompts; per-attempt attempted/returned counts retained separately',
                generated_holdouts_opened=False, formal_capture_submitted=False)
            base._put(folder / 'results.json', result); artifacts['results'] = storage._pin(folder / 'results.json')
            base._put(folder / 'completion_manifest_v1.json', dict(status='complete_exploratory', source=source,
                evaluation_role=ROLE, config_hash=digest(config), artifacts=artifacts, new_model_queries=len(responses)))
            status = 'complete'; return result
        finally:
            attempt.update(status=status, wall_seconds=time.monotonic() - started)
            journal._journal(attempt_path, attempt)
            base._put(folder / ('attempt_' + os.environ['SLURM_JOB_ID'] + '_review_v1.json'), attempt)
            if lease is not None: budget.release(lease, attempt['wall_seconds'], status)
