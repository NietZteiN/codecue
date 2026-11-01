#!/usr/bin/env python
"""Audit saved exact-value failures and TRAIN-only mode baselines; never refit probes."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from codecue.binding import arithmetic_penalty_path as study


def mode(values, weights):
    values, weights = np.asarray(values), np.asarray(weights)
    if values.ndim != 1 or not len(values) or weights.shape != values.shape:
        raise ValueError('nonempty aligned mode observations required')
    if not np.isfinite(values).all() or not np.isfinite(weights).all() or np.any(weights <= 0):
        raise ValueError('finite observations and positive weights required')
    labels, index = np.unique(values, return_inverse=True)
    # Sorted labels and argmax choose the smallest integer on an exact tie.
    return int(labels[np.argmax(np.bincount(index, weights=weights))])


def family_average(values, groups):
    return float(np.mean([np.mean(values[groups == g]) for g in np.unique(groups)]))


def panel(prediction, truth, groups, masks):
    metrics = study.old.score_partition(prediction, truth, groups, masks, np.arange(len(truth)))
    metrics['all_four_exact'] = family_average(np.all(np.rint(prediction) == truth, axis=1), groups)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--edition', type=int, required=True)
    args = parser.parse_args()
    root = Path('artifacts/binding/arithmetic_penalty_path/20261101_v1')
    output = root / f'exact_value_diagnostic_v{args.edition}.json'
    report = Path(f'reports/binding/arithmetic_exact_value_diagnostic_20261101_v{args.edition}.md')
    if args.edition < 1 or output.exists() or report.exists(): raise ValueError('new positive edition required')
    own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    cfg = study.base._json('configs/binding/arithmetic_penalty_path_20261101_v1/report.json')
    study.common.completed(cfg)
    ref = study.base._json('configs/binding/arithmetic_conditional_20261101_v1/llama8b_joint.json')
    rows, truth, _ = study.old.state.load_inputs(ref)  # Metadata and targets; no feature arrays or models loaded.
    ids = np.asarray([r['id'] for r in rows]); groups = np.asarray([r['component_id'] for r in rows])
    splits = np.asarray([r['split'] for r in rows]); train, dev = splits == 'train', splits == 'development'
    masks = study.old.state.annotation(rows); table = study.common.mask_table(study.old.state.table_for(rows), train)
    dev_masks = {k: v[dev] for k, v in masks.items()}
    priors, prior_inputs = {}, {}
    for seed in study.old.numeric.SEEDS:
        w = study.common.weights(table, seed); computed = masks['computed'][train]
        computed_weights = w.copy()
        for g in np.unique(groups[train]):
            part = groups[train] == g; mass = float((w[part, None] * computed[part]).sum())
            if mass: computed_weights[part] /= mass
        all_mode = [mode(truth[train, j], w) for j in range(4)]
        computed_mode = [mode(truth[train, j][computed[:, j]], computed_weights[computed[:, j]])
            if computed[:, j].any() else all_mode[j] for j in range(4)]
        prior_inputs[str(seed)] = dict(all_slot_mode=all_mode, computed_family_mode=computed_mode,
            training_ids_sha256=study.digest(ids[train].tolist()), training_weights_sha256=study.digest(w.tolist()),
            unsupported_computed_heads=[j for j in range(4) if not computed[:, j].any()])
        priors[seed] = {name: panel(np.broadcast_to(values, truth[dev].shape), truth[dev], groups[dev], dev_masks)
            for name, values in [('zero', [0]*4), ('all_slot_mode', all_mode), ('computed_family_mode', computed_mode)]}
    support = []
    for j in range(4):
        fitting = truth[train, j]; fitting_computed = fitting[masks['computed'][train, j]]
        heldout = truth[dev, j]; selected = masks['computed'][dev, j]
        unseen = ~np.isin(heldout, fitting); unseen_computed = ~np.isin(heldout, fitting_computed)
        support.append(dict(slot=j, train_values=sorted(set(map(int, fitting))),
            train_computed_values=sorted(set(map(int, fitting_computed))), dev_computed_observations=int(selected.sum()),
            dev_computed_unseen_all_slot=int((selected & unseen).sum()),
            dev_computed_unseen_computed_slot=int((selected & unseen_computed).sum())))
    values, counts = np.unique(truth[dev][masks['computed'][dev]], return_counts=True)
    cells, inputs = {}, {}
    lines = ['# Exact-value diagnostic of the audited penalty path', '',
        'Postrun exploratory diagnostic on the inspected DEV cohort. No new probe fits, model calls, '
        'feature loads or sealed-final access. Modes are estimated on full TRAIN only and are diagnostic '
        'comparators; they do not participate in the frozen TRAIN-fold selection. '
        'Each displayed metric averages fitting seeds after taking structural-family means. '
        'All-four exact requires every variable to be correct in the same case.', '',
        '| Cell/predictor | Computed MAE | Computed exact | Untouched exact | All-four exact |',
        '|---|---:|---:|---:|---:|']
    def line(name, records):
        return f"| {name} | {np.mean([r['computed']['mae'] for r in records]):.4f} | " + ' | '.join(
            f'{100*np.mean(v):.2f}%' for v in ([r['computed']['exact'] for r in records],
                [r['untouched']['exact'] for r in records], [r['all_four_exact'] for r in records])) + ' |'
    for name in ('zero', 'all_slot_mode', 'computed_family_mode'):
        lines.append(line(name, [priors[s][name] for s in study.old.numeric.SEEDS]))
    for request in cfg['workers']:
        worker = study.base._json(request['path'], request['sha256']); study.common.completed(worker)
        p = Path(worker['run_dir']) / 'results.json'; data = study.base._json(p)
        key = data['alias'] + '/' + data['condition']; records = []
        for fit in data['fits']:
            pin = fit['artifacts']['analysis_scores']
            if study.base._sha(pin['path']) != pin['sha256']: raise ValueError('saved score hash differs')
            with np.load(pin['path'], allow_pickle=False) as z:
                if not np.array_equal(z['ids'], ids) or not np.array_equal(z['truth'], truth) or not np.array_equal(z['splits'], splits):
                    raise ValueError('saved score ordering/targets/splits differ')
                metrics = panel(z['ridge'][dev], truth[dev], groups[dev], dev_masks)
                if metrics['computed'] != fit['ridge_panels']['development']['real']['computed']:
                    raise ValueError('computed metric replay differs')
                records.append(metrics)
        cells[key] = records; inputs[key] = study.storage._pin(p); lines.append(line(key, records))
    lines += ['', '## Target support', '',
        '| Slot | Distinct TRAIN values | Distinct TRAIN computed values | DEV computed slots | Unseen in TRAIN slot | Unseen in TRAIN computed slot |',
        '|---|---:|---:|---:|---:|---:|']
    for r in support:
        lines.append(f"| {r['slot']} | {len(r['train_values'])} | {len(r['train_computed_values'])} | "
            f"{r['dev_computed_observations']} | {r['dev_computed_unseen_all_slot']} | {r['dev_computed_unseen_computed_slot']} |")
    lines += ['', 'Support is an exact numeric-value check, not a generalization guarantee. '
        'The JSON contains per-slot TRAIN supports, TRAIN mode vectors and the DEV computed-target histogram '
        '(observation counts include repeated lexical/query relatives). No predictor is selected using this histogram. '
        'Mode tie-breaking uses the smallest integer. Computed modes use family-normalized computed-slot weights; '
        'unsupported heads fall back to the all-slot TRAIN mode.', '']
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('diagnostic utility changed')
    study.base._publish(report, '\n'.join(lines).encode())
    study.base._put(output, dict(status='complete_exploratory', utility=dict(path=str(own), sha256=own_sha),
        inputs=inputs, priors=priors, prior_inputs=prior_inputs, cells=cells, support=support,
        dev_computed_target_histogram={str(v): int(c) for v, c in zip(values, counts)},
        report=study.storage._pin(report), new_probe_fits=0, new_model_queries=0,
        new_prior_vectors=6, generated_holdouts_opened=False))
    print(json.dumps(dict(status='complete_exploratory', report=str(report))))


if __name__ == '__main__': main()
