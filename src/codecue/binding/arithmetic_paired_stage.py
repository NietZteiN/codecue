"""Frozen paired-source and native-tokenizer gates before new inference."""
from collections import Counter
from itertools import islice
import json
import os
from pathlib import Path

from . import arithmetic_paired_programs as programs
from . import arithmetic_state_common as common
from . import arithmetic_semantic_controls as semantic
from . import arithmetic_graph_capture as capture
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from . import overnight_relationship_capture as journal
from .datasets import digest

PREPARE = 'discovery_arithmetic_paired_prepare_v1'
NATIVE = 'discovery_arithmetic_paired_native_v1'


def paired_checks(rows):
    """Independent source/value checks on complete within-family relatives."""
    retention, binding, invariance, delays = {}, {}, {}, {}
    counts = Counter()
    for r in rows:
        stem = (r['component_id'], r['numeric_seed'], r['lexical_realization'], r['root_order'], r['delay'])
        if r['contrast'] == 'retention':
            retention.setdefault(stem + (r['target_operator'],), {})[r['mutation']] = r
        else: binding.setdefault(stem, {})[r['binding_swap']] = r
        nuisance = (r['component_id'], r['numeric_seed'], r['contrast'], r['target_operator'], r['mutation'], r['binding_swap'], r['delay'])
        actual = (r['expected_answer'], tuple(r['final_values']))
        if nuisance in invariance and invariance[nuisance] != actual: raise ValueError('renaming/root order changes values')
        invariance[nuisance] = actual
        temporal = nuisance[:-1] + (r['lexical_realization'], r['root_order'])
        stripped = '\n'.join(line for line, role in zip(r['body'].splitlines(), r['roles']) if role != 'delay')
        delay_truth = (stripped, actual)
        if temporal in delays and delays[temporal] != delay_truth: raise ValueError('delay changes source semantics')
        delays[temporal] = delay_truth
    for pair in retention.values():
        if set(pair) != {'operand', 'irrelevant'}: raise ValueError('retention pair incomplete')
        first, second = pair['operand'], pair['irrelevant']
        if first['expected_answer'] != second['expected_answer']: raise ValueError('mutation changed retained target')
        a, b = first['body'].splitlines(), second['body'].splitlines(); mutation = first['roles'].index('mutation')
        if a[:mutation] != b[:mutation] or a[mutation + 1:] != b[mutation + 1:] or a[mutation].split(' = ')[1] != b[mutation].split(' = ')[1]:
            raise ValueError('matched mutation sources differ beyond destination')
        counts['retention_pairs'] += 1
    for pair in binding.values():
        if set(pair) != {False, True}: raise ValueError('binding twin incomplete')
        first, second = pair[False], pair[True]
        if (sorted(first['final_values']) != sorted(second['final_values'])
                or programs.token_bag(first['body']) != programs.token_bag(second['body'])
                or first['expected_answer'] == second['expected_answer']):
            raise ValueError('functional same-bag binding contrast failed')
        counts['same_bag_pairs'] += 1
    return dict(counts)


def prepare(config):
    from .confidence import _run_lock
    source = common.validate_role(config, PREPARE); semantic.literature(config)
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        families, feasibility = programs.families()
        calibration = list(programs.calibration_rows())
        # Merge finite calibration template aliases too, even though they never fit.
        groups = programs.closure([set(r['structural_keys']) for r in calibration])
        for indices in groups:
            group = 'paired-calibration-component:' + digest(sorted({k for i in indices for k in calibration[i]['structural_keys']}))[:24]
            for i in indices: calibration[i]['component_id'] = group
        sources_path = folder / 'sources.jsonl'; pending = folder / 'sources.pending.jsonl'
        if pending.exists(): raise ValueError('preserve and inspect interrupted source preparation before retry')
        seen_ids, key_splits, stats, collisions = set(), {}, Counter(), Counter()
        support, summaries = Counter(), []
        from itertools import chain
        iterator = chain(programs.iter_rows(), calibration)
        with pending.open('xb') as stream:
            while True:
                batch = list(islice(iterator, 128))
                if not batch: break
                independent = programs.interpreter.python_oracle([r['body'] + '\n' + r['target_name'] for r in batch])
                for r, truth in zip(batch, independent):
                    programs.validate_one(r, independent=truth)
                    if r['id'] in seen_ids: raise ValueError('duplicate source identity')
                    seen_ids.add(r['id'])
                    for key in r['structural_keys']:
                        if key in key_splits and key_splits[key] != (r['component_id'], r['split']):
                            raise ValueError('canonical full/live relatives span independent components or splits')
                        key_splits[key] = (r['component_id'], r['split'])
                    stats['rows'] += 1; stats['split/' + r['split']] += 1; stats['contrast/' + r['contrast']] += 1
                    if r['nominated_realization']: stats['nominated/' + r['split']] += 1
                    labels = r['error_candidates']
                    for name, value in labels.items():
                        if name != 'correct' and value == labels['correct']: collisions[name] += 1
                    support[(r['split'], r['expected_answer'])] += 1
                    if r['split'] != 'calibration': summaries.append({k: r[k] for k in (
                        'component_id', 'numeric_seed', 'lexical_realization', 'root_order', 'delay', 'contrast',
                        'target_operator', 'mutation', 'binding_swap', 'expected_answer', 'final_values', 'body', 'roles')})
                    stream.write((json.dumps(r, sort_keys=True) + '\n').encode())
                journal._journal(folder / 'progress.json', dict(captured_rows=stats['rows']))
            stream.flush(); os.fsync(stream.fileno())
        pairs = paired_checks(summaries)
        if stats['split/train'] != 96 * 216 or stats['split/development'] != 32 * 216:
            raise ValueError('complete 96/32 family factorial required')
        pending.replace(sources_path)
        manifest = dict(evaluation_role=programs.ROLE, source=source, config_hash=digest(config),
            dataset=storage._pin(sources_path), rows=stats['rows'], counts=dict(stats),
            feasibility=feasibility, calibration_components=len(groups), matched_pair_checks=pairs,
            error_label_collisions=dict(collisions), calibration_outside_all_probe_fits=True,
            structural_policy='connected closure over full and live-target AST keys; names/numbers/root order/identity-copy delay ignored',
            primary_native_protocols=['output_only'], calibration_native_protocols=list(programs.PROTOCOLS),
            formal_native_realization='lexical 0 / root-order 0; all four nuisance realizations oracle-validated; sensitivity inference deferred',
            range_support={split: {str(value): n for (label, value), n in sorted(support.items()) if label == split}
                for split in ('train', 'development', 'calibration')},
            new_model_queries=0, generated_holdouts_opened=False)
        path = folder / 'sources.manifest.json'; base._put(path, manifest)
        result = dict(manifest, status='complete_exploratory', evaluation_role=PREPARE)
        return common.receipt(config, source, result, dict(dataset=storage._pin(sources_path), manifest=storage._pin(path)))


def dataset(config):
    request = config['dataset_config']; cfg = base._json(request['path'], request['sha256']); proof = common.completed(cfg)
    manifest = base._json(proof['artifacts']['manifest']['path'], proof['artifacts']['manifest']['sha256'])
    return manifest, Path(proof['artifacts']['dataset']['path'])


def layout(tokenizer, record, scope, protocol, instruction):
    from .model_adapter import normalize_prompt
    content = programs.prompt_content(record, scope, protocol, instruction)
    forced_prefix = 'Answer:' if protocol == 'output_only' else ''
    prompt = normalize_prompt(tokenizer, tokenizer.apply_chat_template(
        [{'role': 'user', 'content': content}], tokenize=False, add_generation_prompt=True) + forced_prefix)
    if prompt.count(record['body']) != 1: raise ValueError('one exact body occurrence required')
    encoded = tokenizer(prompt, add_special_tokens=False, return_offsets_mapping=True)
    tokens, offsets = encoded['input_ids'], encoded['offset_mapping']
    if not tokens or len(tokens) != len(offsets) or len(tokens) > 4096:
        raise ValueError('bounded native layout required')
    begin = prompt.index(record['body']); points = []
    for point in programs.sites(record):
        end = begin + point['stop']; matches = [i for i, (a, b) in enumerate(offsets) if a <= end - 1 < b]
        if len(matches) != 1: raise ValueError('unique native source offset required')
        index = matches[0]; stop = offsets[index][1]
        available = not prompt[end:stop].strip()
        if available:
            decoded = tokenizer.decode(tokens[:index + 1], skip_special_tokens=False, clean_up_tokenization_spaces=False)
            if decoded != prompt[:stop]: raise ValueError('native causal prefix roundtrip differs')
        points.append(dict(point, available=available, position=index if available else None,
            unavailable_reason=None if available else 'native_token_contains_future_source',
            prefix_sha256=digest(tokens[:index + 1]) if available else None))
    collapsed = points[0]['available'] and points[1]['available'] and points[0]['position'] == points[1]['position']
    expected = [record['expected_answer']] if scope == 'single' else record['final_values']
    return dict(id='paired-prompt:' + digest([record['id'], scope, protocol, instruction])[:24], record_id=record['id'],
        component_id=record['component_id'], split=record['split'], scope=scope, protocol=protocol, instruction=instruction,
        calibration_kind=record['calibration_kind'], depth=record['depth'], delay=record['delay'],
        contrast=record['contrast'], mutation=record['mutation'], expected=expected,
        same_bag_at_generation=('query' in record['same_bag_guaranteed_sites']),
        forced_prefix=forced_prefix, prompt=prompt, input_token_ids=tokens, sites=points,
        rhs_newline_collapsed=bool(collapsed), generation_position=len(tokens) - 1,
        generation_site='pre_answer' if protocol == 'output_only' else 'pre_trace_generation',
        generated_answer_site_available=(protocol == 'output_only'),
        target_literal_visible=record['expected_answer'] in record['source_literal_values'])


def native(config):
    from .confidence import _run_lock
    source = common.validate_role(config, NATIVE); semantic.literature(config)
    manifest, path = dataset(config); folder = Path(config['run_dir'])
    profile = base._json(config['profile']['path'], config['profile']['sha256'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        tokenizer = capture._CORE._tokenizer(profile)
        output = folder / 'prepared_cases.jsonl'; pending = folder / 'prepared_cases.pending.jsonl'
        if pending.exists(): raise ValueError('preserve interrupted native layout before retry')
        counts, maximum, prefix_checks, calibration_ids, prompt_hashes = Counter(), 0, 0, [], set()
        with path.open() as inputs, pending.open('xb') as stream:
            for line in inputs:
                record = json.loads(line)
                if not record['nominated_realization']: continue
                protocols = programs.PROTOCOLS if record['split'] == 'calibration' else ('output_only',)
                baseline = None
                for protocol in protocols:
                    for instruction in range(3):
                        cases = [layout(tokenizer, record, scope, protocol, instruction) for scope in programs.SCOPES]
                        for case in cases:
                            prompt_hash = digest(case['input_token_ids'])
                            if prompt_hash in prompt_hashes: raise ValueError('duplicate native prompt would repeat deterministic inference')
                            prompt_hashes.add(prompt_hash)
                            prefixes = [p['prefix_sha256'] for p in case['sites']]
                            if baseline is None: baseline = prefixes
                            elif prefixes != baseline: raise ValueError('scope/protocol/instruction changes supposedly matched earlier token prefixes')
                            prefix_checks += 1; maximum = max(maximum, len(case['input_token_ids']))
                            counts['cases'] += 1; counts['split/' + case['split']] += 1
                            if case['rhs_newline_collapsed']: counts['rhs_newline_collapsed'] += 1
                            for point in case['sites']: counts[point['kind'] + ('/available' if point['available'] else '/unavailable')] += 1
                            if case['split'] == 'calibration' and case['delay'] == 0: calibration_ids.append(case['id'])
                            stream.write((json.dumps(case, sort_keys=True) + '\n').encode())
                if counts['cases'] % 216 == 0: journal._journal(folder / 'progress.json', dict(captured_rows=counts['cases']))
            stream.flush(); os.fsync(stream.fileno())
        if counts['split/train'] != 96 * 3 * 18 * 6 or counts['split/development'] != 32 * 3 * 18 * 6:
            raise ValueError('complete formal native factorial required')
        if any(counts[k + '/available'] < .95 * counts['cases'] for k in ('rhs_end', 'later_use')):
            raise ValueError('native RHS/later-use availability below predeclared 95% gate; no cases dropped')
        pending.replace(output)
        result = dict(status='complete_exploratory', evaluation_role=NATIVE, source=source, config_hash=digest(config),
            model=profile['model'], model_revision=profile['model_revision'], tokenizer_revision=profile['tokenizer_revision'],
            dataset=manifest['dataset'], prepared_cases=storage._pin(output), counts=dict(counts), max_prompt_tokens=maximum,
            matched_native_prefix_checks=prefix_checks, calibration_case_ids=calibration_ids,
            calibration_cases=len(calibration_ids), chat_template_sha256=digest(tokenizer.chat_template),
            formal_protocols=['output_only'], calibration_protocols=list(programs.PROTOCOLS),
            site_policy='native identical prefixes checked; collapsed RHS/newline not independent sites; unavailable future-token spans retained',
            generation_policy='intermediate/stepwise generation boundary is pre-trace, not pre-answer; later answer states require generated-trace capture',
            new_model_queries=0, generated_holdouts_opened=False)
        return common.receipt(config, source, result, dict(prepared=storage._pin(output)))
