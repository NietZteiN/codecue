#!/usr/bin/env python
"""Pinned, no-fit exploratory diagnostics for the completed cached-state suite."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import numpy as np


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''):
            h.update(block)
    return h.hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path))


def read(entry):
    if sha(entry['path']) != entry['sha256']:
        raise ValueError('pinned diagnostic input changed: ' + entry['path'])
    return json.loads(Path(entry['path']).read_text())


def arrays(entry):
    if sha(entry['path']) != entry['sha256']:
        raise ValueError('saved prediction checksum differs')
    with np.load(entry['path'], allow_pickle=False) as stored:
        return {key: stored[key] for key in stored.files}


def publish(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError('preserve existing diagnostic output: ' + str(path))
    temporary = path.with_suffix(path.suffix + '.pending')
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def family_summary(values, groups, draws=2000):
    """Average seeds first; resample whole structural families, never rows/seeds."""
    values = np.asarray(values, float)
    groups = np.asarray(groups)
    if values.ndim == 1:
        values = values[None, :]
    if values.ndim != 2 or values.shape[1] != len(groups) or not len(groups) or not np.isfinite(values).all():
        raise ValueError('finite seed-by-observation scores and nonempty family IDs required')
    names, inverse = np.unique(groups, return_inverse=True)
    mean = values.mean(axis=0)
    families = np.bincount(inverse, weights=mean) / np.bincount(inverse)
    rng = np.random.default_rng(731)
    samples = families[rng.integers(0, len(families), size=(draws, len(families)))].mean(axis=1)
    return dict(mean=float(families.mean()), interval95=np.quantile(samples, [.025, .975]).tolist(),
        families=len(names), observations=len(groups), fitting_seeds=len(values))


def oracle_numeric_route(pointers, rows):
    """Evaluator ceiling: substitute ground-truth node values, not activations."""
    pointers = np.asarray(pointers)
    if pointers.shape != (len(rows), 4) or not np.issubdtype(pointers.dtype, np.integer):
        raise ValueError('integer four-slot pointers required')
    values = []
    for row, predicted in zip(rows, pointers):
        writes = row['oracle']['writes']
        if np.any(predicted < 0) or np.any(predicted >= len(writes)):
            raise ValueError('pointer outside supplied definition nodes')
        values.append([writes[int(p)]['value'] for p in predicted])
    return np.asarray(values)


def exact_scores(predicted, truth):
    predicted, truth = np.asarray(predicted), np.asarray(truth)
    if predicted.shape != truth.shape or not np.isfinite(predicted).all() or not np.isfinite(truth).all():
        raise ValueError('finite aligned numeric predictions and own-task labels required')
    return np.rint(predicted) == truth


def matched_difference(first, second, metric, draws):
    if {b['seed'] for b in first} != {11, 29, 47} or {b['seed'] for b in second} != {11, 29, 47} or len(first) != 3 or len(second) != 3:
        raise ValueError('exact three-seed comparison required')
    first, second = sorted(first, key=lambda b: b['seed']), sorted(second, key=lambda b: b['seed'])
    groups = sorted(first[0]['development'][metric])
    if any(sorted(b['development'][metric]) != groups for b in first + second):
        raise ValueError('paired dependency families differ')
    a = np.asarray([[b['development'][metric][g] for g in groups] for b in first])
    b = np.asarray([[b['development'][metric][g] for g in groups] for b in second])
    return family_summary(a - b, groups, draws)


def numeric_diagnostics(model, rows, cases, draws):
    table = []
    for i, (row, case) in enumerate(zip(rows, cases)):
        roots = {w['value'] for w in row['oracle']['writes'][:4]}
        for j, d in enumerate(case['descriptors']):
            if d['kind'] != 'definition' or d['statement'] < 4:
                continue
            table.append((i, j, d['value'], row['component_id'], row['split'], row['depth'], d['value'] in roots))
    values = np.asarray([e[2] for e in table])
    groups = np.asarray([e[3] for e in table])
    dev = np.asarray([e[4] == 'development' for e in table])
    depth = np.asarray([e[5] for e in table])
    seen_literal = np.asarray([e[6] for e in table])
    predictions, controls = {}, {}
    for bank in model['fits']:
        data = arrays(bank['artifacts']['scores'])
        if len(set(zip(data['row_indices'].tolist(), data['point_indices'].tolist()))) != len(data['truth']):
            raise ValueError('duplicate numeric point identity')
        lookup = {(int(r), int(p)): k for k, (r, p) in enumerate(zip(data['row_indices'], data['point_indices']))}
        indices = np.asarray([lookup[e[:2]] for e in table])
        if not np.array_equal(data['truth'][indices], values):
            raise ValueError('numeric targets and descriptor values differ')
        key = (bank['backend'], bank['format'], bank['seed'])
        if key in predictions:
            raise ValueError('duplicate numeric seed bank')
        predictions[key] = data['predicted'][indices]
        controls[key] = exact_scores(data['shuffled'][indices], data['shuffle_truth'][indices])
    output = {}
    strata = {'all': dev, 'matches_initial_literal': dev & seen_literal,
        'absent_from_initial_literals': dev & ~seen_literal}
    strata.update({f'depth{d}': dev & (depth == d) for d in (2, 4, 6)})
    for backend in ('hidden', 'source'):
        for kind in ('regression', 'categorical'):
            predicted = np.asarray([predictions[(backend, kind, seed)] for seed in (11, 29, 47)])
            control_correct = np.asarray([controls[(backend, kind, seed)] for seed in (11, 29, 47)])
            correct = np.rint(predicted) == values
            key = backend + '/' + kind
            output[key] = {}
            for label, mask in strata.items():
                if not mask.any():
                    output[key][label] = dict(status='empty')
                    continue
                output[key][label] = dict(exact=family_summary(correct[:, mask], groups[mask], draws),
                    mae=family_summary(np.abs(predicted[:, mask] - values[mask]), groups[mask], draws),
                    real_minus_shuffled_exact=family_summary((correct.astype(float) - control_correct)[:, mask], groups[mask], draws))
    return output


def composition_diagnostics(model, rows, draws):
    groups = np.asarray([r['component_id'] for r in rows])
    dev = np.asarray([r['split'] == 'development' for r in rows])
    truth = np.asarray([r['oracle']['values'] for r in rows])
    expected = np.asarray([r['oracle']['definitions'] for r in rows])
    outputs = defaultdict(list)
    for bank in model['pipelines']:
        if bank['route'] not in ('anchor_query', 'oracle_route') or bank['numeric_backend'] != 'hidden' or bank['numeric_format'] != 'regression':
            continue
        data = arrays(bank['scores'])
        if (not np.array_equal(data['ids'], [r['id'] for r in rows]) or not np.array_equal(data['truth'], truth)
                or not np.array_equal(data['true_pointers'], expected) or not np.array_equal(data['development'], dev)):
            raise ValueError('composition identities or targets differ')
        predicted = np.rint(data['values'])
        outputs[bank['route'] + '_decoded_values'].append((bank['seed'], (predicted == truth).all(axis=1)))
        if bank['route'] == 'anchor_query':
            oracle_values = oracle_numeric_route(data['pointers'], rows)
            outputs['predicted_route_oracle_values'].append((bank['seed'], (oracle_values == truth).all(axis=1)))
            correct_binding = (data['pointers'] == expected).all(axis=1)
            outputs['all_bindings_correct'].append((bank['seed'], correct_binding))
            outputs['correct_state_with_wrong_binding'].append((bank['seed'], (predicted == truth).all(axis=1) & ~correct_binding))
    output = {}
    for label, entries in outputs.items():
        entries.sort(key=lambda item: item[0])
        if [seed for seed, _ in entries] != [11, 29, 47]:
            raise ValueError('complete composition seeds required')
        output[label] = family_summary(np.asarray([v[dev] for _, v in entries]), groups[dev], draws)
    if not np.array_equal(oracle_numeric_route(expected, rows), truth):
        raise ValueError('oracle routing/value sanity check failed')
    output['oracle_route_oracle_values_sanity'] = 1.0
    return output


def run(config_path):
    if not os.environ.get('SLURM_JOB_ID'):
        raise ValueError('run scientific diagnostics inside a CPU allocation')
    config = json.loads(Path(config_path).read_text())
    if config['script_sha256'] != sha(__file__) or config['bootstrap_draws'] != 2000:
        raise ValueError('frozen diagnostic recipe differs')
    read(config['plan_receipt'])
    if sha(config['plan']) != config['plan_sha256']:
        raise ValueError('exploration plan changed')
    root = Path(config['run_dir'])
    if (root / 'completion_review_v1.json').exists():
        receipt = json.loads((root / 'completion_review_v1.json').read_text())
        if receipt['config_sha256'] != sha(config_path):
            raise ValueError('completed diagnostic configuration differs')
        for entry in receipt['artifacts'].values():
            if sha(entry['path']) != entry['sha256']:
                raise ValueError('completed diagnostic output changed')
        return receipt
    if sha(config['rows']['path']) != config['rows']['sha256']:
        raise ValueError('source bank changed')
    rows = [json.loads(line) for line in Path(config['rows']['path']).read_text().splitlines()]
    result = dict(status='complete_exploratory', models={}, new_fits=0, new_model_queries=0,
        sealed_final_opened=False, bootstrap='2000 paired structural-family resamples; seed averages inside family; exploratory percentile intervals')
    for name, inputs in config['models'].items():
        if sha(inputs['prepared']['path']) != inputs['prepared']['sha256']:
            raise ValueError('prepared token layouts changed')
        cases = [json.loads(line) for line in Path(inputs['prepared']['path']).read_text().splitlines()]
        if [c['id'] for c in cases] != [r['id'] for r in rows]:
            raise ValueError('prepared/source identities differ')
        collision, unequal, total = 0, 0, 0
        for case in cases:
            for p, d in enumerate(case['descriptors']):
                if d['kind'] == 'definition' and d['statement'] >= 4:
                    previous = case['descriptors'][p - 1]
                    if previous['kind'] != 'use' or previous['side'] != 'right':
                        raise ValueError('right-use/definition adjacency differs')
                    total += 1
                    collision += case['positions'][p] == case['positions'][p - 1]
        # Values differ even though the two numeric questions can share a token.
        for row, case in zip(rows, cases):
            for p, d in enumerate(case['descriptors']):
                if d['kind'] == 'definition' and d['statement'] >= 4:
                    right = case['descriptors'][p - 1]
                    unequal += d['value'] != row['oracle']['writes'][right['parent']]['value']
        local, capacity = read(inputs['local']), read(inputs['capacity'])
        local_banks = [b for b in local['fits'] if b['backend'] == 'hidden_local' and b['target'] == 'real' and b['training_families'] == 216]
        source_banks = [b for b in capacity['fits'] if b['backend'] == 'source_local' and b['target'] == 'real']
        if any(b['method'] != capacity['reference_method'] for b in local_banks + source_banks):
            raise ValueError('decoder architectures differ in matched comparison')
        result['models'][name] = dict(token_timing=dict(computed_definitions=total,
            same_token_as_right_operand=int(collision), different_numeric_target=int(unequal)),
            dependency_hidden_minus_matched_source=matched_difference(local_banks, source_banks, 'family_metrics', config['bootstrap_draws']),
            numeric=numeric_diagnostics(read(inputs['numeric']), rows, cases, config['bootstrap_draws']),
            composition=composition_diagnostics(read(inputs['compose']), rows, config['bootstrap_draws']))
    publish(root / 'results.json', result)
    lines = ['# Exploratory measurement diagnostics', '',
        'Saved-result analysis only; no fits or model calls. Intervals resample structural families with fitting seeds averaged inside families. Existing DEV is an adaptive discovery cohort; intervals do not correct for earlier selection.', '',
        '| Model | Contrast / measurement | Mean | Exploratory 95% interval |', '|---|---|---:|---:|']
    for name, model in result['models'].items():
        panels = {'Local hidden minus matched-source parent accuracy': model['dependency_hidden_minus_matched_source']}
        panels.update({'Whole state: ' + key: value for key, value in model['composition'].items() if isinstance(value, dict)})
        panels.update({'Computed categorical exact: ' + key: value['exact'] for key, value in model['numeric']['hidden/categorical'].items() if 'exact' in value})
        for label, score in panels.items():
            lo, hi = score['interval95']
            lines.append(f"| {name} | {label} | {100 * score['mean']:.3f}% | [{100 * lo:.3f}, {100 * hi:.3f}]% |")
        timing = model['token_timing']
        lines += ['', f"{name}: {timing['same_token_as_right_operand']}/{timing['computed_definitions']} computed-definition sites coincide with the right-operand token; {timing['different_numeric_target']} ask for a different value. This motivates a temporal-site experiment, not a conclusion that a result cannot be encoded at that token.", '']
    report = Path(config['report'])
    if report.exists():
        raise ValueError('preserve existing diagnostic report')
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text('\n'.join(lines).rstrip() + '\n')
    receipt = dict(status='complete_exploratory', recorded_utc=datetime.now(timezone.utc).isoformat(),
        config_sha256=sha(config_path), script_sha256=sha(__file__), slurm_job_id=os.environ['SLURM_JOB_ID'],
        artifacts=dict(results=pin(root / 'results.json'), report=pin(report)), new_fits=0, new_model_queries=0)
    publish(root / 'completion_review_v1.json', receipt)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    print(json.dumps(run(parser.parse_args().config)))
