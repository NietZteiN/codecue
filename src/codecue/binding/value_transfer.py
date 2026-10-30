"""Discovery-only literal-value routing assay with paired semantic controls."""
from collections import defaultdict
import ast
import json
from pathlib import Path
import time

from .datasets import digest, read_jsonl, write_json
from .interpreter import execute, python_oracle
from .published_benchmarks import immutable, sha
from .registry import code_identity, guarded


CONDITIONS = ('literal_transfer', 'unrelated_position', 'answer_vector',
              'identity_sham', 'random_11', 'random_29', 'random_47')


def conditions(config):
    return (config.get('primary_condition', CONDITIONS[0]), *CONDITIONS[1:])


def qualification(config, cases, baselines):
    """Qualify complete families, never select individual successful examples."""
    families = sorted({c['record']['family'] for c in cases.values()})
    if config.get('baseline_only'):
        return dict(status='behavior_only', eligible_families=[], cells=[])
    gate = config.get('baseline_gate')
    if not gate:
        return dict(status='not_requested', eligible_families=families, cells=[])
    cells, eligible = [], []
    for family in families:
        passed = True
        family_records = [(key, c['record']) for key, c in cases.items() if c['record']['family'] == family]
        for mapping, query in sorted({(r['mapping'], r['query']) for _, r in family_records}):
            selected = [baselines[key] for key, r in family_records if (r['mapping'], r['query']) == (mapping, query)]
            n = len(selected)
            correct = sum(b['correct'] for b in selected)
            invalid = sum(b['prediction'] is None for b in selected)
            ok = (n >= gate['minimum_cell_n'] and correct / n >= gate['minimum_accuracy']
                  and invalid / n <= gate['maximum_invalid_rate'])
            cells.append(dict(family=family, mapping=mapping, query=query, n=n, correct=correct,
                              invalid=invalid, passed=ok))
            passed = passed and ok
        if passed:
            eligible.append(family)
    return dict(status='passed' if len(eligible) == len(families) else 'partial' if eligible else 'failed',
                eligible_families=eligible, cells=cells, thresholds=gate)


def make_rows(config):
    rows = []
    for stride in config['generation']['strides']:
        for offset in range(9):
            a, b, c = [1 + (offset + j * stride) % 9 for j in range(3)]
            if len({a, b, c}) != 3:
                raise ValueError('literal replacements must be distinct positive digits')
            for family in ('ownership', 'versions'):
                for mapping in (0, 1):
                    for lexical in (0, 1):
                        names = [('v0', 'v1', 'buffer', 's0'), ('n0', 'n1', 'temp', 's1')][lexical]
                        x, y, scratch, saved = names
                        for query in (0, 1):
                            group = f'{family}:{mapping}:lex{lexical}:s{stride}:n{offset}:q{query}'
                            for variant, values in [('base', [a, b]), ('slot0', [c, b]), ('slot1', [a, c])]:
                                lines = [f'{scratch} = 0', f'{x} = {values[0]}', f'{y} = {values[1]}']
                                if family == 'ownership':
                                    lines += [f'{scratch} = {x}', f'{x} = {y if mapping else x}',
                                              f'{y} = {scratch if mapping else y}', f'{scratch} = 0']
                                    output = [x, y][query]
                                    role = ['v0', 'v1'][query]
                                else:
                                    old, other = (x, y) if mapping == 0 else (y, x)
                                    lines += [f'{saved} = {old}', f'{old} = {other}', f'{scratch} = 0']
                                    output = [old, saved][query]
                                    role = ['current', 'saved'][query]
                                source = '\n'.join(lines + [output])
                                rows.append(dict(id='value-transfer:' + digest([family, source])[:24],
                                    group_id=group, numeric_group=f's{stride}:n{offset}', family=family,
                                    mapping=mapping, lexical_realization=lexical, query=query, query_role=role,
                                    variant=variant, source=source, literal_values=values,
                                    expected_answer=execute(source)['expected_answer'],
                                    split='development', evaluation_role='literal_routing_discovery_only'))
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate generated programs; inspect numeric design')
    return rows


def directed_pairs(rows):
    groups = defaultdict(dict)
    for row in rows:
        if row['variant'] in groups[row['group_id']]:
            raise ValueError('duplicate counterfactual variant')
        groups[row['group_id']][row['variant']] = row
    result = []
    for group, variants in sorted(groups.items()):
        if set(variants) != {'base', 'slot0', 'slot1'}:
            raise ValueError('incomplete counterfactual group')
        for slot in (0, 1):
            for reverse in (False, True):
                base, changed = variants['base'], variants[f'slot{slot}']
                recipient, donor = (changed, base) if reverse else (base, changed)
                result.append(dict(id=digest([recipient['id'], donor['id']]), group_id=group,
                    recipient=recipient['id'], donor=donor['id'], slot=slot, reverse=reverse,
                    replacement=donor['literal_values'][slot],
                    baseline_answer=recipient['expected_answer'], counterfactual_answer=donor['expected_answer'],
                    affected=recipient['expected_answer'] != donor['expected_answer'],
                    family=recipient['family'], query_role=recipient['query_role'],
                    numeric_group=recipient['numeric_group'], mapping=recipient['mapping'],
                    lexical_realization=recipient['lexical_realization']))
    return result


def validate_dataset(config, rows, independent=False):
    if rows != make_rows(config):
        raise ValueError('dataset differs from registered generated sources or labels')
    pairs = directed_pairs(rows)
    by_id = {r['id']: r for r in rows}
    for pair in pairs:
        recipient, donor = [by_id[pair[k]] for k in ('recipient', 'donor')]
        a, b = recipient['source'], donor['source']
        differences = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(a) != len(b) or len(differences) != 1 or not a[differences[0]].isdigit() or not b[differences[0]].isdigit():
            raise ValueError('donor must differ in precisely one literal digit')
        if pair['replacement'] in recipient['literal_values']:
            raise ValueError('replacement value already occurs in recipient')
        if any(isinstance(node, ast.BinOp) for node in ast.walk(ast.parse(a))):
            raise ValueError('literal-routing assay cannot contain arithmetic')
    if sum(p['affected'] for p in pairs) * 2 != len(pairs):
        raise ValueError('affected and unchanged-answer query controls must balance')
    if independent:
        for start in range(0, len(rows), 128):
            part = rows[start:start + 128]
            if any(r['expected_answer'] != q['answer'] for r, q in zip(part, python_oracle([r['source'] for r in part]))):
                raise ValueError('independent Python oracle disagrees')
    return pairs


def build(config):
    rows = make_rows(config)
    pairs = validate_dataset(config, rows, independent=True)
    path = Path(config['dataset'])
    immutable(path, ''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows).encode())
    manifest = dict(sha256=sha(path), generation_config_hash=digest(config['generation']),
                    role='literal_routing_discovery_only', rows=len(rows), directed_pairs=len(pairs),
                    independent_oracle_passed=True, generated_holdouts_opened=False)
    immutable(path.with_suffix('.manifest.json'), (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode())
    return manifest


def token_layout(tokenizer, row, suffix=''):
    from .calibration import prompt
    text, source = prompt(tokenizer, row, 'print_direct_v3')
    text += suffix
    encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    start = text.index(source)
    lines = source.splitlines(keepends=True)
    positions = []
    for line_index in (1, 2, 0):  # two changed-literal sites and the unrelated zero literal
        end = start + sum(map(len, lines[:line_index])) + len(lines[line_index].rstrip('\n'))
        matches = [i for i, span in enumerate(encoded['offset_mapping']) if span == (end - 1, end)]
        if len(matches) != 1:
            raise ValueError('literal site must be exactly one token without adjacent text')
        positions.append(matches[0])
    positions.append(len(encoded['input_ids']) - 1)
    return dict(record=row, prompt=text, input_token_ids=encoded['input_ids'], positions=positions)


def validate_layouts(cases, pairs):
    for pair in pairs:
        recipient, donor = [cases[pair[k]] for k in ('recipient', 'donor')]
        a, b = recipient['input_token_ids'], donor['input_token_ids']
        position = recipient['positions'][pair['slot']]
        if (len(a) != len(b) or recipient['positions'] != donor['positions']
                or [i for i, (x, y) in enumerate(zip(a, b)) if x != y] != [position]):
            raise ValueError('donor/recipient token layouts differ beyond the changed literal')
        if recipient['positions'][2] >= position or position >= recipient['positions'][3]:
            raise ValueError('unrelated position must precede changed literal and answer')


def prepare(config):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    rows = read_jsonl(config['dataset'])
    pairs = validate_dataset(config, rows)
    if sha(config['hook_proof']) != config['hook_proof_sha256']:
        raise ValueError('hook software proof checksum differs')
    proof = json.loads(Path(config['hook_proof']).read_text())
    if proof['status'] != 'passed' or proof['model'] != config['model']:
        raise ValueError('passing checkpoint hook proof required')
    tok = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tok, config)
    cases = {row['id']: token_layout(tok, row, config.get('answer_prefix_suffix', '')) for row in rows}
    validate_layouts(cases, pairs)
    if config.get('previous_prepared_cases'):
        if sha(config['previous_prepared_cases']) != config['previous_prepared_sha256']:
            raise ValueError('previous boundary diagnostic checksum differs')
        previous = json.loads(Path(config['previous_prepared_cases']).read_text())
        suffix = config['fixed_prefix_token_ids']
        if set(previous['cases']) != set(cases) or any(
                case['input_token_ids'] != previous['cases'][key]['input_token_ids'] + suffix
                for key, case in cases.items()):
            raise ValueError('answer boundary correction changed more than the fixed formatting prefix')
    if len(cases) % config['batch_size'] or len(pairs) % config['batch_size']:
        raise ValueError('assay uses full equal-size batches for numerical prefix checks')
    answer_ids = {}
    for value in range(1, 10):
        ids = tok(str(value), add_special_tokens=False)['input_ids']
        if len(ids) != 1:
            raise ValueError('first-token assay requires one-token positive-digit answers')
        answer_ids[str(value)] = ids[0]
    payload = dict(cases=cases, pairs=pairs, answer_token_ids=answer_ids,
                   padded_width=max(len(c['input_token_ids']) for c in cases.values()))
    path = Path(config['prepared_cases'])
    immutable(path, (json.dumps(payload, sort_keys=True) + '\n').encode())
    result = dict(status='passed', cases=len(cases), directed_pairs=len(pairs),
        config_hash=digest(config), source_sha256=code_identity()['source_sha256'],
        prepared_sha256=sha(path), dataset_sha256=sha(config['dataset']), generated_holdouts_opened=False)
    write_json(config['preflight_result'], result)
    return result


def inputs(config, source_hash=None):
    if config.get('assay') in ('value_owner', 'cue_control'):
        from .mechanism_followup import inputs as followup_inputs
        return followup_inputs(config, source_hash)
    if config.get('assay') in ('query_timing', 'copy_path'):
        from .timing_and_copy import inputs as study_inputs
        return study_inputs(config, source_hash)
    if config.get('assay') in ('computed_routing', 'swap_reset'):
        from .routing_extension import inputs as extension_inputs
        return extension_inputs(config, source_hash)
    qa = json.loads(Path(config['preflight_result']).read_text())
    if (qa['status'] != 'passed' or qa['config_hash'] != digest(config)
            or qa['source_sha256'] != (source_hash or code_identity()['source_sha256'])
            or qa['prepared_sha256'] != sha(config['prepared_cases'])
            or qa['dataset_sha256'] != sha(config['dataset'])):
        raise ValueError('matching frozen tokenizer preflight required')
    data = json.loads(Path(config['prepared_cases']).read_text())
    # Canonical row order is independent of JSON dictionary key order.
    rows = read_jsonl(config['dataset'])
    if (data['pairs'] != validate_dataset(config, rows)
            or {r['id']: r for r in rows} != {k: c['record'] for k, c in data['cases'].items()}):
        raise ValueError('prepared semantic identities differ')
    validate_layouts(data['cases'], data['pairs'])
    if data['padded_width'] != max(len(c['input_token_ids']) for c in data['cases'].values()):
        raise ValueError('registered fixed padding width differs')
    return qa, data


def matched_perturbation(base, direction, target_norm, tolerance=0.03):
    """Match norms AFTER dtype rounding; batch search avoids CPU/GPU sync per step."""
    import torch
    original = base.float()
    unit = direction.float() / direction.float().norm(dim=-1, keepdim=True).clamp_min(1e-30)
    goal = target_norm.float()
    low = torch.zeros_like(goal)
    high = goal * 4 + 1
    best = base.clone()
    best_error = goal.clone()
    for _ in range(28):
        scale = (low + high) / 2
        candidate = (original + unit * scale[:, None]).to(base.dtype)
        actual = (candidate.float() - original).norm(dim=-1)
        error = (actual - goal).abs()
        update = error < best_error
        best = torch.where(update[:, None], candidate, best)
        best_error = torch.minimum(best_error, error)
        low = torch.where(actual < goal, scale, low)
        high = torch.where(actual >= goal, scale, high)
    actual = (best.float() - original).norm(dim=-1)
    if not torch.isfinite(best).all() or not torch.all((actual - goal).abs() <= tolerance * goal + 1e-6):
        raise ValueError('effective perturbation norm failed after dtype rounding')
    return best, actual


def patch_prefill(hidden, width, positions, vectors):
    """Only patch the registered prefill, never a cached one-token decode step."""
    import torch
    if hidden.shape[1] == width:
        result = hidden.clone()
        result[torch.arange(len(positions), device=hidden.device), positions] = vectors.to(hidden)
        return result
    return hidden


def _encode(tok, cases, device, fixed_width):
    encoded = tok([c['prompt'] for c in cases], add_special_tokens=False,
                  padding='max_length', max_length=fixed_width, return_tensors='pt').to(device)
    for index, case in enumerate(cases):
        if encoded.input_ids[index][encoded.attention_mask[index].bool()].tolist() != case['input_token_ids']:
            raise ValueError('GPU tokenization differs from registered prompt')
    # Match generate's left-padding-aware rotary positions for direct forward calls.
    positions = encoded.attention_mask.long().cumsum(-1) - 1
    encoded['position_ids'] = positions.masked_fill(encoded.attention_mask == 0, 1)
    return encoded


def _metrics(logits, target, original):
    import torch
    lp = torch.log_softmax(logits.float(), dim=-1)
    index = torch.arange(len(target), device=logits.device)
    return dict(argmax=logits.argmax(-1).tolist(), target_logprob=lp[index, target].tolist(),
                original_logprob=lp[index, original].tolist())


def verify_answer_boundary(config, baselines, answer_ids):
    if config.get('require_digit_first'):
        invalid = [key for key, row in baselines.items()
                   if str(row['prediction']) not in answer_ids
                   or row['first_token'] != answer_ids[str(row['prediction'])]]
        if invalid:
            raise ValueError(f'answer-digit boundary failed on {len(invalid)}/{len(baselines)} cases; preserve raw baselines, do not interpret formatting tokens as answers')


@guarded
def run(config):
    import numpy as np
    import torch
    from transformers import StopStringCriteria, StoppingCriteriaList
    from codecue.patching import decoder_layers
    from .behavior import parse_answer
    from .model_adapter import load
    from .registry import begin, finish
    qa, data = inputs(config)
    out, manifest = begin(config, 'interventions', reuse_complete=True)
    if manifest['status'] == 'complete':
        return json.loads((out / 'summary.json').read_text())
    started = time.monotonic()
    cache_proof = out / 'cache_checksums.json'
    if cache_proof.exists():
        for name, checksum in json.loads(cache_proof.read_text()).items():
            if sha(out / name) != checksum:
                raise ValueError('saved baseline/replay cache checksum differs')
    tok, model = load(config)
    model.set_attn_implementation('sdpa')
    blocks = decoder_layers(model)
    cases = data['cases']
    ids = sorted(cases)
    bank_path, baseline_path = out / 'baseline_vectors.npz', out / 'baselines.json'
    if bank_path.exists() and baseline_path.exists():
        with np.load(bank_path, allow_pickle=False) as cache:
            bank = cache['vectors']
            if cache['case_ids'].tolist() != ids or bank.shape != (len(ids), len(config['layers']), 4, config['hidden_size']):
                raise ValueError('baseline cache shape or identity differs')
        baselines = json.loads(baseline_path.read_text())
    else:
        vectors, baselines = [], {}
        criterion = StopStringCriteria(tok, ['\n\n'])
        for start in range(0, len(ids), config['batch_size']):
            keys = ids[start:start + config['batch_size']]
            batch = [cases[k] for k in keys]
            encoded = _encode(tok, batch, model.device, data['padded_width'])
            width = encoded.input_ids.shape[1]
            positions = torch.tensor([[width - len(c['input_token_ids']) + p for p in c['positions']] for c in batch], device=model.device)
            captures, handles, first = {}, [], {}
            for layer in config['layers']:
                def hook(module, args, output, layer=layer):
                    hidden = output[0] if isinstance(output, tuple) else output
                    if layer not in captures and hidden.shape[1] == width:
                        captures[layer] = hidden[torch.arange(len(batch), device=model.device)[:, None], positions].detach().float().cpu().numpy()
                handles.append(blocks[layer].register_forward_hook(hook))
            def logits_hook(module, args, output):
                if not first:
                    first.update(argmax=output.logits[:, -1].argmax(-1).tolist(),
                        digit_logits=output.logits[:, -1, [data['answer_token_ids'][str(v)] for v in range(1, 10)]].float().tolist(),
                        logsumexp=output.logits[:, -1].float().logsumexp(-1).tolist())
            handles.append(model.register_forward_hook(logits_hook))
            try:
                with torch.inference_mode():
                    generated = model.generate(**encoded, do_sample=False, num_beams=1, use_cache=True, max_new_tokens=16,
                        eos_token_id=config['eos_token_ids'], pad_token_id=tok.pad_token_id,
                        stopping_criteria=StoppingCriteriaList([criterion]))[:, width:].tolist()
            finally:
                for handle in handles:
                    handle.remove()
            if set(captures) != set(config['layers']):
                raise ValueError('missing baseline hooks')
            vectors.append(np.stack([captures[layer] for layer in config['layers']], axis=1))
            for index, (key, tail) in enumerate(zip(keys, generated)):
                if not tail or first['argmax'][index] != tail[0]:
                    raise ValueError('prefill logits and first generation token differ')
                full_tail = list(tail)
                for j, token in enumerate(tail):
                    if token in config['eos_token_ids']:
                        tail = tail[:j]
                        break
                raw = tok.decode(tail, skip_special_tokens=True)
                pred = parse_answer(raw)
                baselines[key] = dict(raw_response=raw, output_token_ids=full_tail, prediction=pred,
                    correct=pred == cases[key]['record']['expected_answer'], first_token=first['argmax'][index],
                    digit_logprobs=[v - first['logsumexp'][index] for v in first['digit_logits'][index]])
            print(f'baseline {start + len(batch)}/{len(ids)}', flush=True)
        bank = np.concatenate(vectors)
        if not np.isfinite(bank).all():
            raise ValueError('nonfinite baseline vectors')
        temp = bank_path.with_suffix('.tmp')
        with temp.open('wb') as stream:
            np.savez(stream, vectors=bank, case_ids=np.array(ids))
        temp.replace(bank_path)
        write_json(baseline_path, baselines)
    verify_answer_boundary(config, baselines, data['answer_token_ids'])
    index_by_id = {key: i for i, key in enumerate(ids)}
    # Future query tokens cannot affect any of the three earlier captured sites.
    prefix_groups = defaultdict(list)
    for key in ids:
        case = cases[key]
        # Equal full lengths retain equal physical positions under left padding.
        prefix_groups[digest([case['input_token_ids'][:case['positions'][1] + 1], len(case['input_token_ids'])])].append(key)
    for group in prefix_groups.values():
        reference = bank[index_by_id[group[0]], :, :3]
        if any(not np.array_equal(reference, bank[index_by_id[k], :, :3]) for k in group[1:]):
            raise ValueError('pre-query literal activations depend on future query')
    gate = qualification(config, cases, baselines)
    write_json(out / 'baseline_gate.json', gate)
    original_pairs = data['pairs']
    pairs = [p for p in original_pairs if p['family'] in gate['eligible_families']]
    if not pairs:
        summary = dict(complete=True, baseline_cases=len(ids), directed_pairs=0,
            planned_directed_pairs=len(original_pairs), intervention_forwards=0, baseline_gate=gate,
            baseline_correct=sum(r['correct'] for r in baselines.values()), preflight=qa,
            first_token_consistency_cases=len(ids), answer_digit_boundary_checked=bool(config.get('require_digit_first')),
            pre_query_invariance_groups=len(prefix_groups), layers=config['layers'],
            device_name=torch.cuda.get_device_name(), torch_peak_memory_bytes=torch.cuda.max_memory_allocated(),
            baseline_sha256=sha(baseline_path), vector_bank_sha256=sha(bank_path),
            generated_holdouts_opened=False,
            interpretation='All baseline cases preserved. No interventions: behavior-only protocol or no complete family passed its registered reliability gate.')
        write_json(out / 'summary.json', summary)
        finish(out, manifest, time.monotonic() - started)
        return summary
    folder = out / 'chunks'
    folder.mkdir(exist_ok=True)
    # These recipient replays use exactly the intervention batch order, padding,
    # rotary positions and direct-forward API. Norms and changes reference these
    # vectors/logits, rather than treating a different generation batch as exact.
    replay_path, replay_meta = out / 'replay_vectors.npz', out / 'replays.json'
    if replay_path.exists() and replay_meta.exists():
        with np.load(replay_path, allow_pickle=False) as cache:
            replay_bank = cache['vectors']
            if cache['pair_ids'].tolist() != [p['id'] for p in pairs]:
                raise ValueError('recipient replay identities differ')
        replays = json.loads(replay_meta.read_text())
    else:
        replay_vectors, replays = [], {}
        for start in range(0, len(pairs), config['batch_size']):
            part = pairs[start:start + config['batch_size']]
            batch = [cases[p['recipient']] for p in part]
            encoded = _encode(tok, batch, model.device, data['padded_width'])
            width = encoded.input_ids.shape[1]
            positions = torch.tensor([[width - len(c['input_token_ids']) + p for p in c['positions']] for c in batch], device=model.device)
            captures, handles = {}, []
            for layer in config['layers']:
                def capture(module, args, output, layer=layer):
                    hidden = output[0] if isinstance(output, tuple) else output
                    captures[layer] = hidden[torch.arange(len(part), device=model.device)[:, None], positions].detach().float().cpu().numpy()
                handles.append(blocks[layer].register_forward_hook(capture))
            try:
                with torch.inference_mode():
                    output = model(**encoded, use_cache=False, logits_to_keep=1)
            finally:
                for handle in handles:
                    handle.remove()
            replay_vectors.append(np.stack([captures[layer] for layer in config['layers']], axis=1))
            logits = output.logits[:, -1].float()
            digit_lp = torch.log_softmax(logits, -1)[:, [data['answer_token_ids'][str(v)] for v in range(1, 10)]].tolist()
            for i, pair in enumerate(part):
                replays[pair['id']] = dict(first_token=int(logits[i].argmax()), digit_logprobs=digit_lp[i])
        replay_bank = np.concatenate(replay_vectors)
        temp = replay_path.with_suffix('.tmp')
        with temp.open('wb') as stream:
            np.savez(stream, vectors=replay_bank, pair_ids=np.array([p['id'] for p in pairs]))
        temp.replace(replay_path)
        write_json(replay_meta, replays)
    if (replay_bank.shape != (len(pairs), len(config['layers']), 4, config['hidden_size'])
            or not np.isfinite(replay_bank).all() or set(replays) != {p['id'] for p in pairs}):
        raise ValueError('recipient replay shape, coverage or values differ')
    immutable(cache_proof, (json.dumps({name: sha(out / name) for name in
        ('baseline_vectors.npz', 'baselines.json', 'replay_vectors.npz', 'replays.json')},
        sort_keys=True, indent=2) + '\n').encode())
    for layer_index, layer in enumerate(config['layers']):
        for condition in conditions(config):
            for start in range(0, len(pairs), config['batch_size']):
                part = pairs[start:start + config['batch_size']]
                path = folder / f'l{layer:02d}_{condition}_{start:06d}.json'
                if path.exists():
                    validate_chunk(config, data, layer, condition, part, json.loads(path.read_text()), replays)
                    continue
                batch = [cases[p['recipient']] for p in part]
                encoded = _encode(tok, batch, model.device, data['padded_width'])
                width = encoded.input_ids.shape[1]
                recipient = torch.tensor(replay_bank[start:start + len(part), layer_index], device=model.device, dtype=model.dtype)
                donor = torch.tensor(np.stack([bank[index_by_id[p['donor']], layer_index] for p in part]), device=model.device, dtype=model.dtype)
                arange = torch.arange(len(part), device=model.device)
                slots = torch.tensor([p['slot'] for p in part], device=model.device)
                base = recipient[arange, slots]
                incoming = donor[arange, slots]
                delta = incoming.float() - base.float()
                norm = delta.norm(dim=-1)
                site_indices = slots
                patch, actual = incoming, norm
                if condition == 'answer_vector':
                    site_indices = torch.full_like(slots, 3)
                    patch = donor[:, 3]
                    actual = (patch.float() - recipient[:, 3].float()).norm(dim=-1)
                elif condition == 'identity_sham':
                    patch, actual = base, torch.zeros_like(norm)
                elif condition == 'unrelated_position':
                    site_indices = torch.full_like(slots, 2)
                    patch, actual = matched_perturbation(recipient[:, 2], delta, norm, config['norm_tolerance'])
                elif condition.startswith('random_'):
                    seed = int(condition.split('_')[1])
                    directions = []
                    for pair in part:
                        generator = torch.Generator(device='cpu').manual_seed(int(digest([pair['id'], layer, seed])[:15], 16))
                        directions.append(torch.randn(config['hidden_size'], generator=generator))
                    patch, actual = matched_perturbation(base, torch.stack(directions).to(model.device), norm, config['norm_tolerance'])
                logical = [c['positions'][int(site)] for c, site in zip(batch, site_indices.tolist())]
                positions = torch.tensor([width - len(c['input_token_ids']) + p for c, p in zip(batch, logical)], device=model.device)
                calls = []
                def patch_hook(module, args, output):
                    hidden = output[0] if isinstance(output, tuple) else output
                    if hidden.shape[1] == width:
                        if not torch.equal(hidden[arange, positions], recipient[arange, site_indices]):
                            raise ValueError('actual recipient activation differs from same-batch replay')
                        calls.append(True)
                    changed = patch_prefill(hidden, width, positions, patch)
                    return (changed, *output[1:]) if isinstance(output, tuple) else changed
                handle = blocks[layer].register_forward_hook(patch_hook)
                try:
                    with torch.inference_mode():
                        output = model(**encoded, use_cache=False, logits_to_keep=1)
                finally:
                    handle.remove()
                if len(calls) != 1:
                    raise ValueError('intervention must patch exactly one registered prefill')
                target_ids = torch.tensor([data['answer_token_ids'][str(p['replacement'])] for p in part], device=model.device)
                original_ids = torch.tensor([data['answer_token_ids'][str(p['baseline_answer'])] for p in part], device=model.device)
                metrics = _metrics(output.logits[:, -1], target_ids, original_ids)
                rows = []
                for i, pair in enumerate(part):
                    row = dict(pair_id=pair['id'], layer=layer, condition=condition, position=logical[i],
                        recipient=pair['recipient'], donor=pair['donor'], target_effective_norm=float(norm[i]),
                        actual_effective_norm=float(actual[i]), first_token=metrics['argmax'][i],
                        target_logprob=metrics['target_logprob'][i], original_logprob=metrics['original_logprob'][i],
                        target_token=target_ids[i].item(), original_token=original_ids[i].item())
                    rows.append(row)
                validate_chunk(config, data, layer, condition, part, rows, replays)
                write_json(path, rows)
                write_json(out / 'progress.json', dict(layer=layer, condition=condition, pairs_completed=start + len(part), pairs_planned=len(pairs)))
            print(f'layer {layer} {condition}: {len(pairs)} directed pairs', flush=True)
    summary = dict(complete=True, baseline_cases=len(ids), directed_pairs=len(pairs),
        intervention_forwards=len(pairs) * len(config['layers']) * len(conditions(config)),
        planned_directed_pairs=len(original_pairs), baseline_gate=gate,
        baseline_correct=sum(r['correct'] for r in baselines.values()), preflight=qa,
        generation_replay_first_token_matches=sum(replays[p['id']]['first_token'] == baselines[p['recipient']]['first_token'] for p in pairs),
        first_token_consistency_cases=len(ids), pre_query_invariance_groups=len(prefix_groups),
        answer_digit_boundary_checked=bool(config.get('require_digit_first')),
        layers=config['layers'], conditions=list(conditions(config)), device_name=torch.cuda.get_device_name(),
        torch_peak_memory_bytes=torch.cuda.max_memory_allocated(), generated_holdouts_opened=False,
        interpretation=config.get('interpretation', 'Discovery literal-routing/next-token assay. Final-answer vector transfer is an answer-copy software control; no binding mechanism established.'))
    write_json(out / 'summary.json', summary)
    finish(out, manifest, time.monotonic() - started)
    return summary


def validate_chunk(config, data, layer, condition, pairs, rows, replays):
    import math
    if len(rows) != len(pairs):
        raise ValueError('intervention coverage differs')
    for pair, row in zip(pairs, rows):
        position_index = 3 if condition == 'answer_vector' else 2 if condition == 'unrelated_position' else pair['slot']
        if any(row[k] != v for k, v in dict(pair_id=pair['id'], layer=layer, condition=condition,
                recipient=pair['recipient'], donor=pair['donor'],
                position=data['cases'][pair['recipient']]['positions'][position_index],
                target_token=data['answer_token_ids'][str(pair['replacement'])],
                original_token=data['answer_token_ids'][str(pair['baseline_answer'])]).items()):
            raise ValueError('intervention identity, site or target differs')
        if any(not math.isfinite(row[k]) for k in ('target_logprob', 'original_logprob', 'actual_effective_norm', 'target_effective_norm')):
            raise ValueError('nonfinite intervention metric')
        if row['actual_effective_norm'] < 0 or row['target_effective_norm'] < 0:
            raise ValueError('negative perturbation norm')
        if condition in ('unrelated_position', 'random_11', 'random_29', 'random_47'):
            if abs(row['actual_effective_norm'] - row['target_effective_norm']) > config['norm_tolerance'] * row['target_effective_norm'] + 1e-6:
                raise ValueError('effective perturbation norm mismatch')
        if condition == 'identity_sham' and (row['actual_effective_norm'] != 0
                or row['first_token'] != replays[pair['id']]['first_token']):
            raise ValueError('identity sham changed output')


def audit(config):
    import numpy as np
    out = Path(config['run_dir']) / 'interventions'
    manifest = json.loads((out / 'manifest.json').read_text())
    if (manifest['status'] != 'complete' or manifest['identity_hash'] != digest(manifest['identity'])
            or manifest['identity']['config'] != config):
        raise ValueError('complete pinned intervention manifest required')
    qa, data = inputs(config, manifest['identity']['code']['source_sha256'])
    baselines = json.loads((out / 'baselines.json').read_text())
    gate = qualification(config, data['cases'], baselines)
    data = dict(data, pairs=[p for p in data['pairs'] if p['family'] in gate['eligible_families']])
    replays = json.loads((out / 'replays.json').read_text())
    for name, checksum in json.loads((out / 'cache_checksums.json').read_text()).items():
        if sha(out / name) != checksum:
            raise ValueError('baseline/replay checksum differs')
    with np.load(out / 'baseline_vectors.npz', allow_pickle=False) as cache:
        bank, bank_ids = cache['vectors'], cache['case_ids'].tolist()
    with np.load(out / 'replay_vectors.npz', allow_pickle=False) as cache:
        replay_bank, replay_ids = cache['vectors'], cache['pair_ids'].tolist()
    if (bank_ids != sorted(data['cases']) or replay_ids != [p['id'] for p in data['pairs']]
            or bank.shape != (len(bank_ids), len(config['layers']), 4, config['hidden_size'])
            or replay_bank.shape != (len(replay_ids), len(config['layers']), 4, config['hidden_size'])
            or not np.isfinite(bank).all() or not np.isfinite(replay_bank).all()
            or set(replays) != set(replay_ids)):
        raise ValueError('cache identity, shape or coverage differs')
    bank_index = {key: i for i, key in enumerate(bank_ids)}
    if set(baselines) != set(data['cases']):
        raise ValueError('baseline coverage differs')
    from .behavior import parse_answer
    verify_answer_boundary(config, baselines, data['answer_token_ids'])
    for key, baseline in baselines.items():
        if (parse_answer(baseline['raw_response']) != baseline['prediction']
                or baseline['correct'] != (baseline['prediction'] == data['cases'][key]['record']['expected_answer'])
                or not baseline['output_token_ids'] or baseline['first_token'] != baseline['output_token_ids'][0]):
            raise ValueError('baseline score or first-token check differs')
    files, results, subgroup_results = {}, [], []
    pairs = data['pairs']
    for layer in config['layers']:
        for condition in conditions(config):
            combined = []
            for start in range(0, len(pairs), config['batch_size']):
                path = out / 'chunks' / f'l{layer:02d}_{condition}_{start:06d}.json'
                part = pairs[start:start + config['batch_size']]
                rows = json.loads(path.read_text())
                validate_chunk(config, data, layer, condition, part, rows, replays)
                for i, (pair, row) in enumerate(zip(part, rows)):
                    source = bank[bank_index[pair['donor']], config['layers'].index(layer), pair['slot']]
                    destination = replay_bank[start + i, config['layers'].index(layer), pair['slot']]
                    expected_norm = float(np.linalg.norm(source - destination))
                    if abs(expected_norm - row['target_effective_norm']) > 1e-5 * max(1., expected_norm):
                        raise ValueError('saved target norm differs from donor/recipient vectors')
                    if condition == config.get('primary_condition', 'literal_transfer') and row['actual_effective_norm'] != row['target_effective_norm']:
                        raise ValueError('literal transfer effective norm differs')
                files[str(path)] = sha(path)
                combined.extend(zip(part, rows))
            for family in ('ownership', 'versions'):
                for affected in (False, True):
                    for eligible_only in (False, True):
                        selected = [(p, r) for p, r in combined if p['family'] == family and p['affected'] == affected
                            and (not eligible_only or (baselines[p['recipient']]['correct'] and baselines[p['donor']]['correct']))]
                        n = len(selected)
                        def mean(fn): return sum(fn(p, r) for p, r in selected) / n if n else None
                        results.append(dict(layer=layer, condition=condition, family=family, affected=affected,
                            both_baselines_correct_only=eligible_only, n=n,
                            replacement_token_rate=mean(lambda p, r: r['first_token'] == r['target_token']),
                            retained_original_token_rate=mean(lambda p, r: r['first_token'] == r['original_token']),
                            target_minus_original_logodds=mean(lambda p, r: r['target_logprob'] - r['original_logprob']),
                            logodds_change=mean(lambda p, r: r['target_logprob'] - r['original_logprob']
                                - (replays[p['id']]['digit_logprobs'][p['replacement'] - 1]
                                   - replays[p['id']]['digit_logprobs'][p['baseline_answer'] - 1])),
                            mean_effective_norm=mean(lambda p, r: r['actual_effective_norm'])))
                        for reverse in (False, True):
                            for lexical in (0, 1):
                                for mapping in (0, 1):
                                    part = [(p, r) for p, r in selected if p['reverse'] == reverse
                                            and p['lexical_realization'] == lexical and p['mapping'] == mapping]
                                    size = len(part)
                                    subgroup_results.append(dict(layer=layer, condition=condition, family=family,
                                        affected=affected, both_baselines_correct_only=eligible_only,
                                        reverse=reverse, lexical_realization=lexical, mapping=mapping, n=size,
                                        replacement_token_rate=sum(r['first_token'] == r['target_token'] for p, r in part) / size if size else None,
                                        retained_original_token_rate=sum(r['first_token'] == r['original_token'] for p, r in part) / size if size else None))
    if len(list((out / 'chunks').glob('*.json'))) != len(files):
        raise ValueError('unexpected extra intervention chunks')
    result = dict(status='passed', identity_hash=manifest['identity_hash'], preflight=qa,
        baseline_cases=len(baselines), baseline_correct=sum(r['correct'] for r in baselines.values()),
        intervention_forwards=len(pairs) * len(config['layers']) * len(conditions(config)), baseline_gate=gate,
        chunk_checksums=files, baseline_sha256=sha(out / 'baselines.json'),
        vector_bank_sha256=sha(out / 'baseline_vectors.npz'), results=results, subgroup_results=subgroup_results,
        replay_vector_bank_sha256=sha(out / 'replay_vectors.npz'), replay_metadata_sha256=sha(out / 'replays.json'),
        generated_holdouts_opened=False,
        limitation=config.get('limitation', 'First-token measurements on positive one-token literal values; two templates per family and two lexical realizations. No computed-value, general binding-register, or causal error-explanation claim. All cases and both-correct descriptive subsets retained.'))
    immutable(out / 'audit.json', (json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
    return {k: v for k, v in result.items() if k not in ('results', 'subgroup_results', 'chunk_checksums')}
