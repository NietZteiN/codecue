#!/usr/bin/env python
"""No-refit numerical audit of all conditional readout banks and TRAIN inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True); parser.add_argument('--script-sha256', required=True)
    args = parser.parse_args(); own = Path(__file__).resolve(); own_sha = hashlib.sha256(own.read_bytes()).hexdigest()
    if own_sha != args.script_sha256: raise ValueError('queued numerical audit changed')
    snapshot = Path(args.source_root).resolve(); sys.path.insert(0, str(snapshot / 'src'))
    from codecue.binding.snapshots import verify
    frozen = verify(snapshot)
    from codecue.binding import arithmetic_conditional_state as study, weighted_ridge
    import numpy as np
    from threadpoolctl import threadpool_limits
    import os
    study.base._slurm()
    root = Path('artifacts/binding/arithmetic_conditional/20261101_v1'); folder = root / 'postrun_audit'
    if (folder / 'results.json').exists(): raise ValueError('preserve completed audit editions')
    report_config = study.base._json('configs/binding/arithmetic_conditional_20261101_v1/report.json')
    study.common.completed(report_config)
    totals = dict(cv_banks=0, selected_banks=0, prediction_coordinates=0,
        max_prediction_abs_difference=0., max_relative_normal_equation_residual=0., max_intercept_residual=0.)
    inputs, cells = {}, []

    def independent_metrics(pred, truth, groups, masks):
        result = {}
        for name, mask in dict(all=np.ones(truth.shape, bool), **masks).items():
            errors, exact = {}, {}
            for family in sorted(set(groups)):
                rows = groups == family; selected = mask[rows]
                if not selected.any(): continue
                a, b = pred[rows][selected], truth[rows][selected]
                errors[str(family)] = float(np.abs(a - b).mean())
                exact[str(family)] = float((np.rint(a) == b).mean())
            result[name] = dict(observations=int(mask.sum()), families=len(errors),
                mae=float(np.mean(list(errors.values()))) if errors else None,
                exact=float(np.mean(list(exact.values()))) if exact else None,
                family_mae=errors, family_exact=exact)
        return result

    def compare(a, b):
        if isinstance(a, dict):
            if set(a) != set(b): raise ValueError('independent metric keys differ')
            for key in a: compare(a[key], b[key])
        elif a is None:
            if b is not None: raise ValueError('unsupported metric differs')
        elif not np.isclose(a, b, rtol=1e-12, atol=1e-12): raise ValueError('independent metric differs')

    def train_inputs(x, y, w, ids):
        x = np.asarray(x, np.float64); y = np.asarray(y, np.float64)
        pins = {k: weighted_ridge._array_hash(v) for k, v in [('features', x), ('targets', y), ('sample_weight', w)]}
        return x, y, w, ids, pins

    def model_for(bank, training):
        x, y, w, ids, pins = training
        metadata = study.base._json(bank['artifacts']['metadata']['path'], bank['artifacts']['metadata']['sha256'])
        with np.load(bank['artifacts']['parameters']['path'], allow_pickle=False) as z:
            params = {k: z[k] for k in z.files}
        model = weighted_ridge.from_parameters(metadata, params)
        if metadata['training_ids'] != ids or metadata['training_input_sha256'] != pins:
            raise ValueError('model was not fitted to the declared TRAIN features/targets/weights')
        if metadata['alpha'] != bank['alpha']: raise ValueError('ridge alpha differs')
        mean, scale = x.mean(axis=0), x.std(axis=0)
        scale[scale == 0] = 1
        if not np.allclose(model.mean, mean, rtol=1e-10, atol=1e-10) or not np.allclose(model.scale, scale, rtol=1e-10, atol=1e-10):
            raise ValueError('independent TRAIN-only feature normalization differs')
        z = (x - model.mean) / model.scale
        if not np.allclose(model.weighted_target_mean, np.average(y, axis=0, weights=w), rtol=1e-10, atol=1e-10):
            raise ValueError('weighted TRAIN target mean differs')
        if not np.allclose(model.weighted_feature_mean, np.average(z, axis=0, weights=w), rtol=1e-10, atol=1e-10):
            raise ValueError('weighted TRAIN feature mean differs')
        residual = y - (z @ model.coef + model.intercept)
        left = z.T @ (w[:, None] * residual); right = bank['alpha'] * model.coef
        relative = float(np.max(np.abs(left - right)) / (1 + np.max(np.abs(left)) + np.max(np.abs(right))))
        intercept = float(np.max(np.abs(np.sum(w[:, None] * residual, axis=0))) / (1 + w.sum()))
        if relative > 1e-7 or intercept > 1e-7: raise ValueError('ridge normal equations/intercept stationarity failed')
        totals['max_relative_normal_equation_residual'] = max(totals['max_relative_normal_equation_residual'], relative)
        totals['max_intercept_residual'] = max(totals['max_intercept_residual'], intercept)
        return model

    def predictions(model, x, saved):
        actual = ((np.asarray(x, np.float64) - model.mean) / model.scale) @ model.coef + model.intercept
        if actual.shape != saved.shape or not np.allclose(actual, saved, rtol=1e-10, atol=1e-10):
            raise ValueError('explicit saved-parameter prediction replay differs')
        totals['prediction_coordinates'] += int(actual.size)
        totals['max_prediction_abs_difference'] = max(totals['max_prediction_abs_difference'], float(np.max(np.abs(actual - saved))))
        return actual

    with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))):
        for request in report_config['workers']:
            cfg = study.base._json(request['path'], request['sha256']); proof = study.common.completed(cfg)
            data = study.base._json(Path(cfg['run_dir']) / 'results.json')
            rows, truth, cache = study.state.load_inputs(cfg)
            ids = np.asarray([r['id'] for r in rows]); groups = np.asarray([r['component_id'] for r in rows])
            splits = np.asarray([r['split'] for r in rows]); train = splits == 'train'; ti = np.flatnonzero(train)
            table = study.state.table_for(rows); folds = study.common.folds(study.common.mask_table(table, train))
            annotations = study.state.annotation(rows); records = []
            for seed in study.numeric.SEEDS:
                s, h = study.input_features(cfg, cache, seed); w = study.common.weights(study.common.mask_table(table, train), seed)
                for fold in range(3):
                    fi, vi = ti[folds != fold], ti[folds == fold]
                    xf, df = study.design(cfg['condition'], s, h, rows, fi); xv, dv = study.design(cfg['condition'], s, h, rows, vi)
                    if set(df) & set(vi) or set(dv) & set(fi): raise ValueError('donor crosses fitting/validation partition')
                    weights = w[folds != fold]; weights = weights / weights.mean()
                    training = train_inputs(xf, truth[fi], weights, ids[fi].tolist())
                    for alpha in study.numeric.ALPHAS:
                        key = f'cv_seed{seed}_fold{fold}_alpha{int(alpha)}'
                        pin = proof['artifacts'][key]; bank = study.base._json(pin['path'], pin['sha256'])
                        if bank['fit_groups'] != sorted(set(groups[fi])) or bank['validation_groups'] != sorted(set(groups[vi])):
                            raise ValueError('CV structural family inventory differs')
                        if bank['fit_donor_ids_sha256'] != study.digest(ids[df].tolist()) or bank['validation_donor_ids_sha256'] != study.digest(ids[dv].tolist()):
                            raise ValueError('CV donor identities differ')
                        model = model_for(bank, training)
                        with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
                            if not np.array_equal(z['ids'], ids[vi]) or not np.array_equal(z['truth'], truth[vi]) or not np.array_equal(z['donor_ids'], ids[dv]):
                                raise ValueError('CV prediction/target/donor order differs')
                            pred = predictions(model, xv, z['predicted'])
                        panel = independent_metrics(pred, truth[vi], groups[vi], {k: v[vi] for k, v in annotations.items()})
                        compare(panel, bank['validation']); records.append(bank); totals['cv_banks'] += 1
                del s, h
            alpha = min(study.numeric.ALPHAS, key=lambda a: (np.mean([r['validation']['computed']['mae'] for r in records if r['alpha'] == a]), -a))
            if alpha != data['selected_alpha']: raise ValueError('independent TRAIN selection differs')
            for bank in data['fits']:
                if bank['alpha'] != alpha: raise ValueError('selected refit alpha differs')
                seed = bank['seed']; s, h = study.input_features(cfg, cache, seed)
                x, donor = study.design(cfg['condition'], s, h, rows, ti)
                training = train_inputs(x, truth[ti], study.common.weights(study.common.mask_table(table, train), seed), ids[ti].tolist())
                if bank['fit_donor_ids_sha256'] != study.digest(ids[donor].tolist()): raise ValueError('refit donor identities differ')
                model = model_for(bank, training)
                with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
                    if not np.array_equal(z['ids'], ids) or not np.array_equal(z['truth'], truth) or not np.array_equal(z['splits'], splits):
                        raise ValueError('refit evaluation rows differ')
                    for split in ('train', 'development', 'calibration'):
                        indices = np.flatnonzero(splits == split)
                        if not len(indices): continue
                        x, donor = study.design(cfg['condition'], s, h, rows, indices)
                        if not np.array_equal(z['donor_ids'][indices], ids[donor]): raise ValueError('evaluation donor identities differ')
                        pred = predictions(model, x, z['predicted'][indices])
                        masks = {k: v[indices] for k, v in annotations.items()}
                        compare(independent_metrics(pred, truth[indices], groups[indices], masks), bank['panels'][split]['real'])
                        prior = np.broadcast_to(np.average(training[1], axis=0, weights=training[2]), pred.shape)
                        compare(independent_metrics(prior, truth[indices], groups[indices], masks), bank['panels'][split]['prior'])
                        if cfg['condition'] in ('joint', 'shuffled_joint'):
                            for key, chosen in [('hidden_at_training_mean', slice(1024, 2048)), ('source_at_training_mean', slice(0, 1024))]:
                                ablated = np.asarray(x, np.float64).copy(); ablated[:, chosen] = model.mean[chosen]
                                guessed = predictions(model, ablated, z[key][indices])
                                compare(independent_metrics(guessed, truth[indices], groups[indices], masks), bank['panels'][split][key])
                totals['selected_banks'] += 1; del s, h
            name = cfg['alias'] + '/' + cfg['condition']; cells.append(dict(name=name, selected_alpha=alpha))
            inputs[name] = study.storage._pin(Path(cfg['run_dir']) / 'results.json')
            print('audited conditional cell ' + name, flush=True)
    if totals['cv_banks'] != 216 or totals['selected_banks'] != 24: raise ValueError('complete 240-bank audit required')
    if hashlib.sha256(own.read_bytes()).hexdigest() != own_sha: raise ValueError('audit source changed during execution')
    result = dict(status='complete_audited_exploratory', source_snapshot_id=frozen['snapshot_id'],
        source_sha256=frozen['code']['source_sha256'], utility=dict(path=str(own), sha256=own_sha),
        inputs=inputs, cells=cells, totals=totals, new_model_queries=0, new_fits=0, generated_holdouts_opened=False,
        policy='all 240 TRAIN input hashes/IDs/weights, normalization, ridge stationarity, predictions, donor partitions, independent metrics and selection checked; no refits')
    lines = ['# Conditional readouts: postrun numerical audit', '',
        'All eight cells passed a no-refit audit. Training input hashes/IDs/weights and family/donor partitions match. '
        'Independent TRAIN normalization and ridge normal-equation/intercept checks pass. '
        'Explicit saved-parameter multiplication reproduces CV/selected predictions, including fixed-block ablations. '
        'Independent family-first metrics and TRAIN-only alpha selection match.', '',
        f"- CV banks: **{totals['cv_banks']}**; selected banks: **{totals['selected_banks']}**.",
        f"- Prediction coordinates replayed: **{totals['prediction_coordinates']:,}**.",
        f"- Maximum absolute prediction difference: **{totals['max_prediction_abs_difference']:.3g}**.",
        f"- Maximum relative ridge normal-equation residual: **{totals['max_relative_normal_equation_residual']:.3g}** (limit1e-7).",
        f"- Maximum weighted-intercept residual: **{totals['max_intercept_residual']:.3g}** (limit1e-7).", '',
        'Prediction replay allows rtol/atol1e-10 across CPU kernels; metric checks allow1e-12 and normalization checks1e-10. '
        'This numerical audit does not turn adaptive DEV findings into confirmation or establish causal use. '
        'No new model calls, parameter fits, layer/wording selection or sealed-final access.', '']
    report = Path('reports/binding/arithmetic_conditional_postrun_review_20261101_v1.md')
    study.base._publish(report, '\n'.join(lines).encode()); study.base._put(folder / 'results.json', result)
    study.base._put(folder / 'completion_manifest_v1.json', dict(status=result['status'], utility=result['utility'],
        artifacts=dict(results=study.storage._pin(folder / 'results.json'), report=study.storage._pin(report)), new_model_queries=0, new_fits=0))
    print(json.dumps(dict(status=result['status'], **totals)))


if __name__ == '__main__': main()
