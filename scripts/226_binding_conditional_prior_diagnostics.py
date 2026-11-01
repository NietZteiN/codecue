#!/usr/bin/env python
"""TRAIN-only median/zero prior and regularization-boundary diagnostics."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True); parser.add_argument('--script-sha256', required=True)
    args = parser.parse_args(); own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    if own_sha != args.script_sha256: raise ValueError('queued prior diagnostic changed')
    snapshot = Path(args.source_root).resolve(); sys.path.insert(0, str(snapshot / 'src'))
    from codecue.binding.snapshots import verify
    frozen = verify(snapshot)
    from codecue.binding import arithmetic_conditional_state as study
    import numpy as np
    study.base._slurm()
    root = Path('artifacts/binding/arithmetic_conditional/20261101_v1'); folder = root / 'prior_diagnostics'
    if (folder / 'results.json').exists(): raise ValueError('preserve diagnostic editions')
    cfg_path = 'configs/binding/arithmetic_conditional_20261101_v1/report.json'; cfg = study.base._json(cfg_path)
    study.common.completed(cfg)
    first = study.base._json(cfg['workers'][0]['path'], cfg['workers'][0]['sha256'])
    rows, truth, _ = study.state.load_inputs(first)
    groups = np.asarray([r['component_id'] for r in rows]); splits = np.asarray([r['split'] for r in rows])
    train, dev = splits == 'train', splits == 'development'; masks = study.state.annotation(rows)
    table = study.state.table_for(rows); dt = {k: v[dev] for k, v in masks.items()}

    def median(values, weights):
        values, weights = np.asarray(values), np.asarray(weights)
        if values.ndim != 1 or weights.shape != values.shape or not len(values) or np.any(weights <= 0):
            raise ValueError('nonempty aligned positive-weight median required')
        order = np.argsort(values, kind='stable'); v, w = values[order], weights[order]
        result = float(v[np.searchsorted(np.cumsum(w), w.sum() / 2, side='left')])
        loss = lambda c: float(np.dot(weights, np.abs(values - c)))
        if loss(result) > min(loss(0), loss(np.average(values, weights=weights))) + 1e-8:
            raise ValueError('weighted-median absolute-loss optimum check failed')
        return result

    # Check the weighted quantile against a brute-force absolute-loss definition.
    rng = np.random.default_rng(227)
    for _ in range(30):
        v = rng.integers(-10, 11, 20); w = rng.uniform(.1, 3, 20); result = median(v, w)
        if np.dot(w, np.abs(v - result)) > min(np.dot(w, np.abs(v - c)) for c in set(v)) + 1e-8:
            raise ValueError('brute-force weighted-median verification failed')
    methods = {k: [] for k in ('all_slot_mean', 'all_slot_median', 'computed_family_median', 'zero')}
    for seed in study.numeric.SEEDS:
        weights = study.common.weights(study.common.mask_table(table, train), seed)
        y = truth[train]; comp = masks['computed'][train]; tg = groups[train]
        denominators = {g: int(comp[tg == g].sum()) for g in set(tg)}
        if any(n <= 0 for n in denominators.values()): raise ValueError('computed support required in every TRAIN family')
        observation_weights = weights / np.asarray([denominators[g] for g in tg])
        constants = dict(all_slot_mean=np.average(y, axis=0, weights=weights),
            all_slot_median=np.asarray([median(y[:, j], weights) for j in range(4)]),
            computed_family_median=np.asarray([median(y[comp[:, j], j], observation_weights[comp[:, j]]) for j in range(4)]),
            zero=np.zeros(4))
        for name, values in constants.items():
            panel = study.metrics(np.broadcast_to(values, truth[dev].shape), truth[dev], groups[dev], dt)
            methods[name].append(dict(seed=seed, constants=values.tolist(), development=panel))
    inputs = dict(report_config=study.storage._pin(cfg_path)); boundaries, contrasts = [], []
    prior_families = sorted(methods['computed_family_median'][0]['development']['computed']['family_mae'])
    prior_arrays = {name: np.asarray([[r['development']['computed']['family_mae'][g] for g in prior_families] for r in records])
        for name, records in methods.items()}
    for request in cfg['workers']:
        worker = study.base._json(request['path'], request['sha256']); study.common.completed(worker)
        p = Path(worker['run_dir']) / 'results.json'; data = study.base._json(p); key = worker['alias'] + '/' + worker['condition']
        curves = []
        for alpha in study.numeric.ALPHAS:
            losses = []
            for seed in study.numeric.SEEDS:
                for fold in range(3):
                    record = study.base._json(Path(worker['run_dir']) / f'cv_seed{seed}_fold{fold}_alpha{int(alpha)}.json')
                    losses.append(record['validation']['computed']['mae'])
            curves.append(dict(alpha=alpha, train_cv_mae=float(np.mean(losses))))
        boundaries.append(dict(cell=key, selected_alpha=data['selected_alpha'],
            upper_boundary=data['selected_alpha'] == max(study.numeric.ALPHAS), curves=curves))
        inputs[key] = study.storage._pin(p)
        if worker['condition'] == 'joint':
            banks = sorted(data['fits'], key=lambda r: r['seed'])
            actual = np.asarray([[b['panels']['development']['real']['computed']['family_mae'][g] for g in prior_families] for b in banks])
            for name in ('all_slot_median', 'computed_family_median', 'zero'):
                contrasts.append(dict(cell=key, comparator=name, **study.geometry.paired_family_interval(actual, prior_arrays[name])))
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('prior diagnostic source changed')
    result = dict(status='complete_exploratory_diagnostic', source_snapshot_id=frozen['snapshot_id'],
        source_sha256=frozen['code']['source_sha256'], utility=dict(path=str(own), sha256=own_sha), inputs=inputs,
        methods=methods, regularization_boundaries=boundaries, paired_family_contrasts=contrasts,
        new_model_queries=0, new_readout_fits=0, new_prior_estimates=9, generated_holdouts_opened=False,
        policy='postrun exploratory diagnostic; all nonzero prior constants use TRAIN only; no DEV method selection or new ridge fits; original results preserved')
    lines = ['# Conditional readouts: median-prior and regularization diagnostics', '',
        'Exploratory follow-up after observing that the declared ridge grid selected its upper endpoint. '
        'All prior constants below use TRAIN only; all methods are reported, with no best-prior selection on DEV. '
        'The original240 fits and their source/hidden contrasts remain unchanged. '
        'No new ridge fits or language-model calls; nine four-slot prior-statistic vectors were estimated.', '',
        '| Prior | Computed MAE | Computed rounded exact |', '|---|---:|---:|']
    for name, records in methods.items():
        mae = np.mean([r['development']['computed']['mae'] for r in records])
        exact = np.mean([r['development']['computed']['exact'] for r in records])
        lines.append(f'| {name} | {mae:.4f} | {100*exact:.2f}% |')
    lines += ['', 'The computed-family median estimates one constant per output slot from TRAIN computed observations, '
        'weighting each family by its original fitting-seed weight divided by its total computed observations. '
        'It minimizes the corresponding constant-predictor absolute-loss objective. Oracle computed masks are '
        'TRAIN/evaluation annotations only, not per-example prediction inputs. All-slot mean/median and fixed zero '
        'give simpler reference points. Medians are verified against brute-force candidate absolute losses.', '',
        '## Joint minus prior computed-value MAE', '',
        '| Joint cell | Prior | Difference | Descriptive 95% family interval |', '|---|---|---:|---|']
    for c in contrasts:
        lines.append(f"| {c['cell']} | {c['comparator']} | {c['delta']:.4f} | [{c['lower']:.4f}, {c['upper']:.4f}] |")
    lines += ['', '## TRAIN regularization boundary', '',
        '| Cell | Selected alpha | Upper boundary | TRAIN CV loss at1 /100 /10000 |', '|---|---:|---|---|']
    for cell in boundaries:
        losses = ' / '.join(f"{p['train_cv_mae']:.4f}" for p in cell['curves'])
        lines.append(f"| {cell['cell']} | {cell['selected_alpha']:.0f} | {cell['upper_boundary']} | {losses} |")
    lines += ['', 'Upper-boundary selection motivates a new, prospectively frozen TRAIN-only penalty continuation '
        'and stronger robust-loss/constant baselines before treating the current learned models as optimized. '
        'These diagnostics were added after the ridge results were inspected: intervals remain descriptive, '
        'non-simultaneous and adaptive, not confirmation. A joint gain against finite learned source features '
        'does not by itself show an improvement over a loss-appropriate constant predictor or a maintained numeric state.', '']
    text = '\n'.join(lines).replace('original240', 'original 240').replace('at1 /100 /10000', 'at 1 / 100 / 10000')
    report = Path('reports/binding/arithmetic_conditional_prior_diagnostics_20261101_v1.md')
    study.base._publish(report, text.encode()); study.base._put(folder / 'results.json', result)
    study.base._put(folder / 'completion_manifest_v1.json', dict(status=result['status'], utility=result['utility'],
        artifacts=dict(results=study.storage._pin(folder / 'results.json'), report=study.storage._pin(report)), new_model_queries=0, new_readout_fits=0))
    print(json.dumps(dict(status=result['status'], upper_boundary_cells=sum(r['upper_boundary'] for r in boundaries),
        prior_mae={k:float(np.mean([r['development']['computed']['mae'] for r in v])) for k,v in methods.items()})))


if __name__ == '__main__': main()
