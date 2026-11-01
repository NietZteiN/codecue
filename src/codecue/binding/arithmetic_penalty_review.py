"""Numerical audit and reporting of extended ridge paths; never refits models."""
from pathlib import Path
import numpy as np

from . import arithmetic_penalty_path as path


def independent_metrics(pred, truth, groups, masks):
    result = {}
    for name, mask in dict(all=np.ones(truth.shape, bool), **masks).items():
        errors, exact = {}, {}
        for family in sorted(set(groups)):
            rows = groups == family; selected = mask[rows]
            if not selected.any(): continue
            a, b = pred[rows][selected], truth[rows][selected]
            errors[str(family)] = float(np.abs(a - b).mean()); exact[str(family)] = float((np.rint(a) == b).mean())
        result[name] = dict(observations=int(mask.sum()), families=len(errors),
            mae=float(np.mean(list(errors.values()))) if errors else None, exact=float(np.mean(list(exact.values()))) if exact else None,
            family_mae=errors, family_exact=exact)
    return result


def compare(a, b):
    if isinstance(a, dict):
        if set(a) != set(b): raise ValueError('independent metric keys differ')
        for key in a: compare(a[key], b[key])
    elif a is None:
        if b is not None: raise ValueError('unsupported metric differs')
    elif not np.isclose(a, b, rtol=1e-12, atol=1e-12): raise ValueError('independent numerical metric differs')


def check_prior_values(expected, saved):
    for key in ('computed_support', 'unsupported_computed_heads', 'fallback'):
        if expected[key] != saved[key]: raise ValueError('prior support/fallback policy differs')
    if set(expected['constants']) != set(saved['constants']): raise ValueError('prior classes differ')
    for key, values in expected['constants'].items():
        actual = np.asarray(saved['constants'][key])
        if actual.shape != (4,) or not np.allclose(values, actual, rtol=1e-12, atol=1e-12):
            raise ValueError('TRAIN prior values differ')


def audit_model(bank, context, x, y, weights, counters):
    path.check_context(bank, context, bank['seed'], bank['alpha'], bank.get('fold'))
    metadata = path.base._json(bank['artifacts']['metadata']['path'], bank['artifacts']['metadata']['sha256'])
    with np.load(bank['artifacts']['parameters']['path'], allow_pickle=False) as z:
        model = path.weighted_ridge.from_parameters(metadata, {k: z[k] for k in z.files})
    x = np.asarray(x, np.float64); mean, scale = x.mean(axis=0), x.std(axis=0); scale[scale == 0] = 1
    if not np.allclose(model.mean, mean, rtol=1e-10, atol=1e-10) or not np.allclose(model.scale, scale, rtol=1e-10, atol=1e-10):
        raise ValueError('independent TRAIN normalization differs')
    standardized = (x - model.mean) / model.scale
    if not np.allclose(model.weighted_target_mean, np.average(y, axis=0, weights=weights), rtol=1e-10, atol=1e-10):
        raise ValueError('weighted target mean differs')
    if not np.allclose(model.weighted_feature_mean, np.average(standardized, axis=0, weights=weights), rtol=1e-10, atol=1e-10):
        raise ValueError('weighted feature mean differs')
    residual = y - (standardized @ model.coef + model.intercept)
    left = standardized.T @ (weights[:, None] * residual); right = bank['alpha'] * model.coef
    relative = float(np.max(np.abs(left - right)) / (1 + np.max(np.abs(left)) + np.max(np.abs(right))))
    intercept = float(np.max(np.abs(np.sum(weights[:, None] * residual, axis=0))) / (1 + weights.sum()))
    if relative > 1e-7 or intercept > 1e-7: raise ValueError('ridge stationarity audit failed')
    counters['max_relative_normal_equation_residual'] = max(counters['max_relative_normal_equation_residual'], relative)
    counters['max_intercept_residual'] = max(counters['max_intercept_residual'], intercept)
    return model


def replay(model, x, saved, counters):
    actual = ((np.asarray(x, np.float64) - model.mean) / model.scale) @ model.coef + model.intercept
    if actual.shape != saved.shape or not np.allclose(actual, saved, rtol=1e-10, atol=1e-10): raise ValueError('prediction replay differs')
    counters['prediction_coordinates'] += int(actual.size)
    counters['max_prediction_abs_difference'] = max(counters['max_prediction_abs_difference'], float(np.max(np.abs(actual - saved))))


def audit(config):
    source = path.common.validate_role(config, path.AUDIT); path.semantic.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return path.common.completed(config)
    totals = dict(new_cv=0, reused_cv=0, new_selected=0, reused_selected=0, prediction_coordinates=0,
        max_prediction_abs_difference=0., max_relative_normal_equation_residual=0., max_intercept_residual=0.)
    inputs = {}
    for request in config['workers']:
        cfg = path.base._json(request['path'], request['sha256']); proof = path.common.completed(cfg)
        data = path.base._json(Path(cfg['run_dir']) / 'results.json'); ref, old_proof, _ = path.reference(cfg)
        rows, values, cache = path.old.state.load_inputs(ref)
        ids = np.asarray([r['id'] for r in rows]); groups = np.asarray([r['component_id'] for r in rows]); splits = np.asarray([r['split'] for r in rows])
        train = splits == 'train'; ti = np.flatnonzero(train); table = path.old.state.table_for(rows)
        folds = path.common.folds(path.common.mask_table(table, train)); masks = path.old.state.annotation(rows)
        priors, full = path.load_priors(cfg, ids, values); cv = []
        for seed in path.old.numeric.SEEDS:
            s, h = path.old.input_features(ref, cache, seed); weights = path.common.weights(path.common.mask_table(table, train), seed)
            for fold in range(3):
                fi, vi = ti[folds != fold], ti[folds == fold]; w = weights[folds != fold]; w = w / w.mean()
                xf, df = path.old.design(ref['condition'], s, h, rows, fi); xv, dv = path.old.design(ref['condition'], s, h, rows, vi)
                if set(df) & set(vi) or set(dv) & set(fi): raise ValueError('donor partition leakage')
                context = path.training_context(xf, values, w, ids, fi, df)
                prior = next(p for p in priors if p['seed'] == seed and p['fold'] == fold)
                expected = path.prior_context(values, masks, ids, groups, fi, w)
                if expected != {k: prior[k] for k in expected} or prior['validation_ids_sha256'] != path.digest(ids[vi].tolist()):
                    raise ValueError('prior fitting/validation identities differ')
                estimate = path.fit_priors(values[fi], masks['computed'][fi], groups[fi], w, 'train')
                check_prior_values(estimate, prior)
                for name, c in prior['constants'].items():
                    compare(independent_metrics(np.broadcast_to(c, values[vi].shape), values[vi], groups[vi],
                        {k: v[vi] for k, v in masks.items()}), prior['validation'][name])
                for alpha in path.ALPHAS:
                    key = f'cv_seed{seed}_fold{fold}_alpha{int(alpha)}'; pin = proof['artifacts'][key]
                    bank = path.base._json(pin['path'], pin['sha256'])
                    path.check_context(bank, context, seed, alpha, fold, source, cfg)
                    if alpha in path.OLD_ALPHAS:
                        if bank['bank_type'] != 'reused_fit_reference' or bank['origin']['source'] != old_proof['source'] or bank['origin']['config'] != cfg['reference_worker']:
                            raise ValueError('original fit provenance not preserved')
                        if path.base._sha(bank['origin']['bank']['path']) != bank['origin']['bank']['sha256']: raise ValueError('original bank changed')
                        totals['reused_cv'] += 1
                    else:
                        if bank['bank_type'] != 'new_fit': raise ValueError('new fit incorrectly counted as reuse')
                        totals['new_cv'] += 1
                    model = audit_model(bank, context, xf, values[fi], w, totals)
                    with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
                        if not np.array_equal(z['ids'], ids[vi]) or not np.array_equal(z['truth'], values[vi]) or not np.array_equal(z['donor_ids'], ids[dv]):
                            raise ValueError('CV score/label/donor order differs')
                        replay(model, xv, z['predicted'], totals)
                        compare(independent_metrics(z['predicted'], values[vi], groups[vi], {k: v[vi] for k, v in masks.items()}), bank['validation'])
                    cv.append(bank)
            del s, h
        if path.select(cv, priors) != data['selection']: raise ValueError('TRAIN-only selection replay differs')
        if len(data['fits']) != 3 or sorted(b['seed'] for b in data['fits']) != list(path.old.numeric.SEEDS): raise ValueError('selected seed support differs')
        for analysis in data['fits']:
            seed = analysis['seed']; bank = path.base._json(analysis['ridge_bank']['path'], analysis['ridge_bank']['sha256'])
            s, h = path.old.input_features(ref, cache, seed); weights = path.common.weights(path.common.mask_table(table, train), seed)
            xt, donor = path.old.design(ref['condition'], s, h, rows, ti); context = path.training_context(xt, values, weights, ids, ti, donor)
            path.check_context(bank, context, seed, data['selection']['ridge_alpha'], source=source, config=cfg)
            if bank['bank_type'] not in ('new_fit', 'reused_fit_reference'): raise ValueError('unknown selected bank provenance')
            if bank['bank_type'] == 'reused_fit_reference':
                if bank['origin']['source'] != old_proof['source'] or bank['origin']['config'] != cfg['reference_worker']:
                    raise ValueError('selected original fit provenance not preserved')
                if path.base._sha(bank['origin']['bank']['path']) != bank['origin']['bank']['sha256']:
                    raise ValueError('selected original bank changed')
            model = audit_model(bank, context, xt, values[ti], weights, totals)
            totals['reused_selected' if bank['bank_type'] == 'reused_fit_reference' else 'new_selected'] += 1
            prior = full[seed]; expected = path.prior_context(values, masks, ids, groups, ti, weights)
            if expected != {k: prior[k] for k in expected}: raise ValueError('full-TRAIN prior context differs')
            check_prior_values(path.fit_priors(values[ti], masks['computed'][ti], groups[ti], weights, 'train'), prior)
            with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z, np.load(analysis['artifacts']['analysis_scores']['path'], allow_pickle=False) as a:
                if not np.array_equal(a['ids'], ids) or not np.array_equal(a['truth'], values) or not np.array_equal(a['splits'], splits): raise ValueError('analysis case order differs')
                if not np.array_equal(a['ridge'], z['predicted']): raise ValueError('ridge analysis scores changed')
                for label in ('train', 'development', 'calibration'):
                    idx = np.flatnonzero(splits == label)
                    if not len(idx): continue
                    x, donor = path.old.design(ref['condition'], s, h, rows, idx)
                    if not np.array_equal(z['donor_ids'][idx], ids[donor]): raise ValueError('selected donor IDs differ')
                    replay(model, x, z['predicted'][idx], totals)
                    selected_masks = {k: v[idx] for k, v in masks.items()}
                    compare(independent_metrics(z['predicted'][idx], values[idx], groups[idx], selected_masks), analysis['ridge_panels'][label]['real'])
                    for name, c in prior['constants'].items():
                        compare(independent_metrics(np.broadcast_to(c, values[idx].shape), values[idx], groups[idx], selected_masks), analysis['prior_panels'][label][name])
                    chosen = data['selection']['overall']
                    expected_overall = z['predicted'][idx] if chosen['kind'] == 'ridge' else np.broadcast_to(prior['constants'][chosen['prior']], values[idx].shape)
                    if not np.array_equal(a['overall'][idx], expected_overall): raise ValueError('overall TRAIN-selected predictor differs')
                    compare(independent_metrics(a['overall'][idx], values[idx], groups[idx], selected_masks), analysis['overall_panels'][label])
                    totals['prediction_coordinates'] += int(a['overall'][idx].size)
                    if ref['condition'] in ('joint', 'shuffled_joint'):
                        for name, chosen in [('hidden_at_training_mean', slice(1024, 2048)), ('source_at_training_mean', slice(0, 1024))]:
                            ablated = np.asarray(x, np.float64).copy(); ablated[:, chosen] = model.mean[chosen]
                            replay(model, ablated, z[name][idx], totals)
                            compare(independent_metrics(z[name][idx], values[idx], groups[idx], selected_masks), analysis['ridge_panels'][label][name])
            del s, h
        key = ref['alias'] + '/' + ref['condition']; inputs[key] = path.storage._pin(Path(cfg['run_dir']) / 'results.json')
        print('audited penalty cell ' + key, flush=True)
    if totals['new_cv'] != 216 or totals['reused_cv'] != 216 or totals['new_selected'] + totals['reused_selected'] != 24:
        raise ValueError('complete extended-path bank counts required')
    result = dict(status='complete_exploratory', evaluation_role=path.AUDIT, source=source, config_hash=path.digest(config), inputs=inputs,
        totals=totals, audit_status='passed', new_readout_fits=0, new_model_queries=0, generated_holdouts_opened=False)
    return path.common.receipt(config, source, result, {})


def report(config):
    source = path.common.validate_role(config, path.REPORT); path.semantic.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return path.common.completed(config)
    audit_cfg = path.base._json(config['audit_config']['path'], config['audit_config']['sha256']); path.common.completed(audit_cfg)
    audit_data = path.base._json(Path(audit_cfg['run_dir']) / 'results.json')
    if audit_data['audit_status'] != 'passed': raise ValueError('numerical audit must pass before reporting')
    lines = ['# Extended conditional penalty path and TRAIN-fold priors', '',
        'Adaptive discovery on the original archived cohort. All choices use TRAIN structural folds only. '
        'Original CV/model files are reused through immutable references with feature/target/weight/ID fingerprints. '
        'Fold-local mean, median, computed-family median and fixed zero compete with the ridge path. '
        'No new language-model calls or sealed-final access.', '',
        '| Cell | Ridge alpha | Grid | Overall TRAIN choice | Ridge computed MAE | Overall computed MAE | Overall exact |',
        '|---|---:|---|---|---:|---:|---:|']
    cells, inputs, total_new, total_reused = {}, {}, 0, 0
    for request in config['workers']:
        cfg = path.base._json(request['path'], request['sha256']); path.common.completed(cfg)
        data = path.base._json(Path(cfg['run_dir']) / 'results.json'); ref, _, original = path.reference(cfg)
        key = ref['alias'] + '/' + ref['condition']; selected = data['selection']; fits = sorted(data['fits'], key=lambda b: b['seed'])
        average = lambda endpoint, metric: float(np.mean([b[endpoint]['development']['computed'][metric] for b in fits]))
        ridge_mae = float(np.mean([b['ridge_panels']['development']['real']['computed']['mae'] for b in fits]))
        overall = selected['overall']; choice = f"ridge({overall['alpha']:.0f})" if overall['kind'] == 'ridge' else overall['prior']
        lines.append(f"| {key} | {selected['ridge_alpha']:.0f} | {selected['ridge_grid_position']} | {choice} | "
            f"{ridge_mae:.4f} | "
            f"{average('overall_panels','mae'):.4f} | {100*average('overall_panels','exact'):.2f}% |")
        families = sorted(fits[0]['overall_panels']['development']['computed']['family_mae'])
        array = lambda endpoint: np.asarray([[b[endpoint]['development']['computed']['family_mae'][g] for g in families] for b in fits])
        ridge_array = np.asarray([[b['ridge_panels']['development']['real']['computed']['family_mae'][g] for g in families] for b in fits])
        old_array = np.asarray([[b['panels']['development']['real']['computed']['family_mae'][g] for g in families] for b in sorted(original['fits'], key=lambda b: b['seed'])])
        cells[key] = dict(families=families, overall=array('overall_panels'), ridge=ridge_array,
            old=old_array, prior={name: np.asarray([[b['prior_panels']['development'][name]['computed']['family_mae'][g] for g in families] for b in fits]) for name in path.PRIOR_NAMES})
        inputs[key] = path.storage._pin(Path(cfg['run_dir']) / 'results.json')
        total_new += data['new_readout_fits']; total_reused += data['reused_readout_banks']
    lines += ['', f'**New ridge fits: {total_new}; reused fit banks: {total_reused}.** Shared priors add36 four-slot TRAIN statistic estimates; zero is fixed.', '',
        '## Paired DEV-family contrasts', '',
        'Differences are selected joint minus comparator computed-value MAE; negative favors joint. '
        'Fitting seeds are averaged within families before2,000 bootstrap replicates. Intervals are descriptive, '
        'non-simultaneous and adaptive on an inspected DEV cohort, not confirmation.', '',
        '| Joint cell | Comparator | Difference | Descriptive 95% interval |', '|---|---|---:|---|']
    contrasts = []
    for alias in ('llama8b', 'codellama34b'):
        left = cells[alias + '/joint']
        comparators = {k: cells[k]['overall'] for k in ('source/source1024', 'source/source2048', alias + '/hidden', alias + '/shuffled_joint')}
        comparators.update({name: left['prior'][name] for name in path.PRIOR_NAMES})
        for name, right in comparators.items():
            if name in cells and cells[name]['families'] != left['families']: raise ValueError('comparison family support differs')
            c = dict(cell=alias + '/joint', comparator=name, **path.old.geometry.paired_family_interval(left['overall'], right)); contrasts.append(c)
            lines.append(f"| {c['cell']} | {name} | {c['delta']:.4f} | [{c['lower']:.4f}, {c['upper']:.4f}] |")
    changes = {key: path.old.geometry.paired_family_interval(cell['ridge'], cell['old']) for key, cell in cells.items()}
    lines += ['', '## Penalty continuation versus original selected ridge', '',
        '| Cell | Computed MAE change | Descriptive 95% interval |', '|---|---:|---|']
    for key, c in changes.items(): lines.append(f"| {key} | {c['delta']:.4f} | [{c['lower']:.4f}, {c['upper']:.4f}] |")
    lines += ['', 'An interior choice is interior only to this finite grid. Any remaining boundary or constant preference '
        'is explicitly reported, not called optimization success. Source2048 matches nominal feature count, '
        'not effective rank/inductive bias. Shuffled-hidden conditions select independently. '
        'Lower MAE does not imply better exact integer recovery; zero/class priors remain essential. '
        'No complete-state, natural causal-use, or cross-protocol representation claim follows.', '']
    text = '\n'.join(lines).replace('add36', 'add 36').replace('before2,000', 'before 2,000')
    out = Path(config['report']); path.base._publish(out, text.encode())
    result = dict(status='complete_exploratory', evaluation_role=path.REPORT, source=source, config_hash=path.digest(config),
        inputs=inputs, audit=path.storage._pin(Path(audit_cfg['run_dir']) / 'results.json'), paired_family_contrasts=contrasts,
        penalty_changes=changes, new_readout_fits=total_new, reused_readout_banks=total_reused,
        new_prior_estimates=36, new_model_queries=0, generated_holdouts_opened=False)
    return path.common.receipt(config, source, result, dict(report=path.storage._pin(out)))
