"""Development-only full-residual value-transfer assay and negative controls.

This is an assay, not automatic binding localization. Sites must be supplied in
config before execution; no automatic sweep or choice based on final-test labels.
"""
from __future__ import annotations
from contextlib import contextmanager
import copy
import ast
import json
import time
from collections import defaultdict
import numpy as np
from .datasets import read_jsonl, write_json
from .interpreter import execute, substituted_source
from .behavior import parse_answer
from .registry import guarded


@contextmanager
def residual_patch(block, position, vector):
    """Patch prefill only during cached generation; always remove the hook."""
    def hook(module, args, output):
        h = output[0] if isinstance(output, tuple) else output
        if h.shape[1] > position:
            h = h.clone()
            h[:, position, :] = vector.to(device=h.device, dtype=h.dtype)
            return (h, *output[1:]) if isinstance(output, tuple) else h
        return output
    handle = block.register_forward_hook(hook)
    try:
        yield
    finally:
        handle.remove()


def changed_record(recipient, changes, *, computed=False):
    """Changes refer to canonical assignments; spans rebuilt after AST rendering."""
    from .programs import rename
    source = recipient['canonical_source']
    initial = execute(source)
    order = {p['definition']:p['statement'] for p in initial['execution_trace']}
    if not set(changes) <= set(order):
        raise ValueError('donor changes must name existing assignment versions')
    # Apply upstream changes before downstream targets, so each requested value
    # is achieved even when changed definitions depend on each other.
    for definition in sorted(changes,key=order.__getitem__):
        replacement = changes[definition]
        if computed:
            trace = execute(source)
            delta = replacement - trace['versioned_bindings'][definition]
            if abs(delta)>64:
                raise ValueError('computed donor delta outside restricted literal range')
            tree = ast.parse(source)
            counts = defaultdict(int)
            for stmt in tree.body[:-1]:
                name = stmt.targets[0].id
                counts[name] += 1
                if f'{name}@{counts[name]}' == definition and delta:
                    stmt.value = ast.BinOp(left=stmt.value, op=ast.Add(), right=ast.Constant(value=delta))
            source = ast.unparse(ast.fix_missing_locations(tree))
        else:
            source = substituted_source(source, definition, replacement)
    truth = execute(source)
    row = copy.deepcopy(recipient)
    row.update(truth)
    row['canonical_source'] = source
    row['source'] = rename(source, row['rename_map'])
    from .programs import features
    from .datasets import diagnostics, digest
    row['features'] = features(source, truth)
    row['diagnostic_counterfactuals'] = diagnostics(source, truth)
    row['canonical_ast_hash'] = digest(ast.dump(ast.parse(source)))
    offset = 0
    row['statement_spans'] = []
    for i, line in enumerate(row['source'].splitlines()):
        row['statement_spans'].append({'statement': i, 'start': offset, 'end': offset + len(line)})
        offset += len(line) + 1
    return row


def quantity_record(recipient, slot):
    """Change only the late output expression; keep the assignment prefix fixed."""
    if slot not in recipient['variable_slots']:
        raise ValueError('quantity query must be a canonical variable slot')
    row = copy.deepcopy(recipient)
    lines = ast.unparse(ast.parse(row['canonical_source'])).splitlines()
    row['canonical_source'] = '\n'.join(lines[:-1] + [slot])
    return changed_record(row, {})


@guarded
def run(config):
    import torch
    from codecue.models import generate_free
    from codecue.patching import decoder_layers
    from .model_adapter import load, prompt_for, layout, score_answers
    from .registry import begin, finish
    from .analysis import interval
    assay = config.get('intervention')
    if not assay or assay.get('split') != 'development' or len(assay.get('layers', [])) != 1:
        raise ValueError('supply one predeclared development intervention layer in config')
    out, manifest = begin(config, 'interventions')
    started = time.monotonic()
    tokenizer, model = load(config)
    blocks = decoder_layers(model)
    layer = assay['layers'][0]
    if not 0 <= layer < len(blocks):
        raise ValueError('invalid intervention layer')
    all_rows = read_jsonl(config['dataset'])
    ownership_donors = {r['base_id']:r for r in all_rows if r['split'] == 'development'
                       and r['condition'] == 'neutral' and r['lexical_realization'] == 0 and r['control_kind'] == 'binding_swap'}
    rows = [r for r in all_rows if r['split'] == 'development'
            and r['family'] in assay.get('families', ('parallel','snapshot','accumulator'))
            and r['condition'] == 'neutral' and r['lexical_realization'] == 0 and r['control_kind'] == 'primary']
    by_cell, recipients = {}, []
    for r in rows:
        by_cell.setdefault((r['family'], r['load'], r['updates']), []).append(r)
    for cell, group in sorted(by_cell.items()):
        recipients.extend(sorted(group, key=lambda r: r['id'])[:assay.get('per_cell_limit', 1)])
    rng = np.random.default_rng(config['seed'])
    output = out / 'assays.jsonl'
    if output.exists():
        raise ValueError('intervention assay is immutable; use a new run directory to repeat')

    def hidden(row, site):
        prompt = prompt_for(tokenizer, row, config['protocol'])
        aligned = layout(tokenizer, row, prompt)
        pos = aligned['positions'][site]
        captured = []
        def hook(module, args, result):
            h = result[0] if isinstance(result, tuple) else result
            captured.append(h[0, pos].detach().clone())
        handle = blocks[layer].register_forward_hook(hook)
        try:
            with torch.inference_mode():
                model(input_ids=torch.tensor([aligned['input_ids']], device=model.device), use_cache=False)
        finally:
            handle.remove()
        return captured[0], aligned, prompt

    completed_recipients, excluded_recipients = 0, []
    for recipient in recipients:
        last = recipient['execution_trace'][-1]
        target_slot = assay.get('target_slot', 'v1')
        wrong_slot = 'v0' if target_slot != 'v0' else 'v1'
        target, wrong = last['versions'][target_slot], last['versions'][wrong_slot]
        source_value = last['values'][target_slot] + 2
        if abs(source_value) > 64:
            excluded_recipients.append({'id':recipient['id'],'reason':'donor value outside allowed range'})
            continue
        construction = assay.get('donor_construction', 'computed_delta')
        if construction not in ('computed_delta','literalized_assignment'):
            raise ValueError('unknown donor construction')
        def make_donor(changes):
            return changed_record(recipient, changes, computed=construction == 'computed_delta')
        kind = assay.get('kind', 'value_transfer')
        if kind == 'value_transfer':
            donor = make_donor({target: source_value})
        elif kind == 'binding_ownership':
            donor = ownership_donors[recipient['base_id']]
            if sorted(last['values'].values()) != sorted(donor['execution_trace'][-1]['values'].values()):
                raise ValueError('ownership donors must match the complete value multiset')
            if donor['expected_answer'] == recipient['expected_answer']:
                excluded_recipients.append({'id':recipient['id'],'reason':'ownership contrast has identical output'})
                with (out/'exclusions.jsonl').open('a') as f:
                    f.write(json.dumps({'id':recipient['id'],'reason':'ownership contrast has identical output'})+'\n')
                continue
        else:
            raise ValueError('unknown intervention kind')
        expected = donor['expected_answer']
        site = f"statement:{len(recipient['execution_trace']) - 1}"
        rh, aligned, prompt = hidden(recipient, site)
        dh, _, _ = hidden(donor, site)
        wrong_donor = make_donor({wrong: last['values'][wrong_slot] + 2})
        wh, _, _ = hidden(wrong_donor, site)
        history = [p for p in recipient['execution_trace'] if p['definition'].startswith(target_slot+'@')]
        older = history[-2]['value'] if len(history) > 1 else last['values'][target_slot]
        old_donor = make_donor({target: older})
        oh, _, _ = hidden(old_donor, site)
        target_effect = execute(recipient['canonical_source'], {target:last['values'][target_slot]+1})['expected_answer'] - recipient['expected_answer']
        wrong_effect = execute(recipient['canonical_source'], {wrong:last['values'][wrong_slot]+1})['expected_answer'] - recipient['expected_answer']
        if not wrong_effect or (-2*target_effect) % wrong_effect:
            raise ValueError('same-answer control needs an integer compensating intervention')
        compensation = (-2*target_effect)//wrong_effect
        same_answer = make_donor({target: source_value, wrong: last['values'][wrong_slot] + compensation})
        if same_answer['expected_answer'] != recipient['expected_answer']:
            raise ValueError('same-answer control failed semantic check')
        sh, _, _ = hidden(same_answer, site)
        group = by_cell[(recipient['family'], recipient['load'], recipient['updates'])]
        shuffle = next((r for r in group if r['base_id'] != recipient['base_id']), None)
        if shuffle is None:
            raise ValueError('need at least two development bases per cell for donor control')
        random_h, _, _ = hidden(shuffle, site)
        delta = dh - rh
        permutation = torch.tensor(rng.permutation(len(delta)), device=delta.device)
        controls = [('no_op', None, None), ('self_patch', rh, recipient), ('value_donor', dh, donor), ('wrong_variable', wh, wrong_donor),
                    ('wrong_version', oh, old_donor), ('same_answer_different_state', sh, same_answer), ('shuffled_donor', random_h, shuffle),
                    ('matched_norm_random_direction', rh + delta[permutation], None)]
        candidates = [recipient['expected_answer'], expected, wrong_donor['expected_answer'], old_donor['expected_answer']]
        ids = torch.tensor([aligned['input_ids']], device=model.device)
        baseline_prediction = None
        for label, vector, control_donor in controls:
            quantity_results = {}
            ctx = residual_patch(blocks[layer], aligned['positions'][site], vector) if vector is not None else null_context()
            with ctx, torch.inference_mode():
                raw = generate_free(tokenizer, model, [prompt], config['max_new_tokens'], 1,
                                    stop_at_blank_line=config['protocol'] == 'short_answer_prefill_v2')[0]
                scores = score_answers(tokenizer, model, prompt, candidates)
                for slot in assay.get('quantity_queries', []):
                    query = quantity_record(recipient, slot)
                    query_prompt = prompt_for(tokenizer, query, config['protocol'])
                    query_layout = layout(tokenizer, query, query_prompt)
                    position = aligned['positions'][site]
                    if query_layout['positions'][site] != position or query_layout['input_ids'][:position+1] != aligned['input_ids'][:position+1]:
                        raise ValueError('late quantity query changed the patched causal prefix')
                    quantity_raw = generate_free(tokenizer, model, [query_prompt], config['max_new_tokens'], 1,
                                                 stop_at_blank_line=config['protocol'] == 'short_answer_prefill_v2')[0]
                    original_value = last['values'][slot]
                    changed_value = donor['execution_trace'][-1]['values'][slot]
                    quantity_results[slot] = {'prediction':parse_answer(quantity_raw), 'raw_response':quantity_raw,
                                             'recipient_value':original_value, 'counterfactual_value':changed_value,
                                             'dependent':original_value != changed_value}
            pred = parse_answer(raw)
            if label == 'no_op':
                baseline_prediction = pred
            item = {'id': recipient['id'], 'template_id': recipient['template_id'], 'cluster_id': recipient['cluster_id'], 'base_id': recipient['base_id'],
                    'layer': layer, 'site': site, 'control': label, 'raw_response': raw, 'prediction': pred,
                    'recipient_answer': recipient['expected_answer'], 'counterfactual_answer': expected,
                    'exact_counterfactual': pred == expected, 'baseline_correct': baseline_prediction == recipient['expected_answer'],
                    'baseline_prediction': baseline_prediction,
                    'expected_downstream_state': donor['execution_trace'][-1]['values'],
                    'observed_downstream_state': {s:q['prediction'] for s,q in quantity_results.items()} or None,
                    'quantity_queries':quantity_results,
                    'state_specificity_status': ('late-query diagnostic; reconstruction remains possible' if quantity_results else
                                                  'not measured; final output alone cannot establish binding specificity'),
                    'scores': scores, 'patch_delta_norm': float(torch.linalg.vector_norm(vector - rh)) if vector is not None else 0.0,
                    'target_definition': target, 'target_slot':target_slot, 'wrong_slot':wrong_slot,
                    'donor_source': control_donor['source'] if control_donor else None,
                    'main_donor_source': donor['source'], 'donor_construction': construction if kind == 'value_transfer' else 'computed ownership swap',
                    'control_donor_answer': control_donor['expected_answer'] if control_donor else None,
                    'assay_type': kind + '; transfer assay, not established natural binding repair',
                    'donor_matches_value_multiset': sorted(last['values'].values()) == sorted(donor['execution_trace'][-1]['values'].values())}
            with output.open('a') as f:
                f.write(json.dumps(item) + '\n')
        # Reciprocal natural donor direction uses precisely the same site correspondence.
        dh2, donor_layout, donor_prompt = hidden(donor, site)
        donor_ids = torch.tensor([donor_layout['input_ids']], device=model.device)
        with residual_patch(blocks[layer], donor_layout['positions'][site], rh), torch.inference_mode():
            raw = generate_free(tokenizer, model, [donor_prompt], config['max_new_tokens'], 1,
                                stop_at_blank_line=config['protocol'] == 'short_answer_prefill_v2')[0]
        with output.open('a') as f:
            f.write(json.dumps({'id': recipient['id'], 'base_id': recipient['base_id'], 'template_id': recipient['template_id'], 'cluster_id': recipient['cluster_id'],
                'control': 'reciprocal_value_donor', 'raw_response': raw, 'prediction': parse_answer(raw),
                'exact_counterfactual': parse_answer(raw) == recipient['expected_answer'],
                'recipient_answer': donor['expected_answer'], 'counterfactual_answer': recipient['expected_answer'],
                'layer': layer, 'site': site}) + '\n')
        print(f"assay {recipient['base_id']}", flush=True)
        completed_recipients += 1
    actual = read_jsonl(output) if output.exists() else []
    def likelihood_margin(row):
        scores = {s['answer']: s['log_likelihood_sum'] for s in row['scores']['scores']}
        return scores[row['counterfactual_answer']] - scores[row['recipient_answer']]
    baselines = {r['id']: r for r in actual if r['control'] == 'no_op'}
    summary = []
    for control in sorted({r['control'] for r in actual}):
        subset = [r for r in actual if r['control'] == control]
        entry = {'control': control, 'n': len(subset),
                 'counterfactual_accuracy': interval([r['exact_counterfactual'] for r in subset], [r['cluster_id'] for r in subset])}
        scored = [r for r in subset if 'scores' in r]
        if scored:
            entry['counterfactual_accuracy_change_from_no_op'] = interval(
                [float(r['exact_counterfactual']) - float(baselines[r['id']]['exact_counterfactual']) for r in scored],
                [r['cluster_id'] for r in scored])
            entry['counterfactual_log_likelihood_margin_change'] = interval(
                [likelihood_margin(r) - likelihood_margin(baselines[r['id']]) for r in scored],
                [r['cluster_id'] for r in scored])
            entry['baseline_correct_n'] = sum(r['baseline_correct'] for r in scored)
            entry['induced_counterfactual_on_baseline_correct_n'] = sum(r['baseline_correct'] and r['exact_counterfactual'] for r in scored)
            for dependent in (True, False):
                quantities = [(r,q) for r in scored for q in r.get('quantity_queries',{}).values() if q['dependent'] == dependent]
                if quantities:
                    name = 'dependent' if dependent else 'independent'
                    entry[name + '_quantity_accuracy'] = interval(
                        [q['prediction'] == q['counterfactual_value'] for r,q in quantities],
                        [r['cluster_id'] for r,q in quantities])
                    entry[name + '_quantity_n'] = len(quantities)
        summary.append(entry)
    complete = completed_recipients + len(excluded_recipients) == len(recipients)
    write_json(out / 'summary.json', {'controls': summary, 'complete':complete,
               'recipients_planned':len(recipients),'recipients_completed':completed_recipients,
               'exclusions':excluded_recipients,
               'interpretation': 'development transfer assay; late-query specificity is measured when requested, natural-use path specificity remains unestablished'})
    finish(out, manifest, time.monotonic() - started, 'complete' if complete else 'budget_limited',
           samples_completed=len(actual),recipients_completed=completed_recipients,
           recipients_planned=len(recipients),excluded_recipients=excluded_recipients)
    return {'assays': str(output), 'summary': str(out / 'summary.json')}


@contextmanager
def null_context():
    yield
