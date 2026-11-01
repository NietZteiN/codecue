"""Conditional numeric prediction from source features and archived query states.

The source already determines the answer. 'Conditional gain' here means better
held-out prediction within these finite learned feature/readout classes, never
information absent from the program or proof of causal use.
"""
from pathlib import Path
import numpy as np

from . import arithmetic_global_state as state
from . import arithmetic_numeric_exploration as numeric
from . import arithmetic_numeric_geometry as geometry
from . import arithmetic_state_common as common
from . import arithmetic_semantic_controls as semantic
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

FIT = 'discovery_arithmetic_conditional_fit_v1'
REPORT = 'discovery_arithmetic_conditional_report_v1'
CONDITIONS = ('source1024', 'source2048', 'hidden', 'joint', 'shuffled_joint')


def metrics(prediction, truth, groups, masks):
    prediction, truth, groups = np.asarray(prediction), np.asarray(truth), np.asarray(groups)
    if (prediction.shape != truth.shape or truth.shape != (len(groups), 4)
            or not np.isfinite(prediction).all() or not np.isfinite(truth).all()):
        raise ValueError('four finite aligned value heads required')
    result = {}
    for key, mask in dict(all=np.ones(truth.shape, bool), **masks).items():
        mask = np.asarray(mask)
        if mask.shape != truth.shape or mask.dtype != bool: raise ValueError('Boolean oracle annotations required')
        i, j = np.nonzero(mask); family_mae, family_exact = {}, {}
        for family in np.unique(groups[i]):
            use = groups[i] == family
            family_mae[str(family)] = float(np.abs(prediction[i[use], j[use]] - truth[i[use], j[use]]).mean())
            family_exact[str(family)] = float((np.rint(prediction[i[use], j[use]]) == truth[i[use], j[use]]).mean())
        result[key] = dict(observations=len(i), families=len(family_mae),
            mae=float(np.mean(list(family_mae.values()))) if family_mae else None,
            exact=float(np.mean(list(family_exact.values()))) if family_exact else None,
            family_mae=family_mae, family_exact=family_exact)
    return result


def design(condition, source, hidden, rows, indices):
    """Controls are constructed independently inside EACH fit/evaluation partition.

    Source and oracle labels stay aligned. Only the hidden block moves to a
    different complete family inside the same split/structural stratum. Numeric
    draws and lexical relatives remain coherent. No held-out donor enters fitting.
    """
    if condition not in CONDITIONS: raise ValueError('declared conditional feature condition required')
    indices = np.asarray(indices)
    if indices.ndim != 1 or indices.dtype.kind not in 'iu' or len(set(indices.tolist())) != len(indices):
        raise ValueError('unique integer partition indices required')
    if not len(indices) or np.any(indices < 0) or np.any(indices >= len(rows)): raise ValueError('nonempty in-range partition required')
    subset = [rows[i] for i in indices]
    if len({r['split'] for r in subset}) != 1: raise ValueError('fit/evaluation source splits must be separate')
    donor = indices.copy()
    if condition == 'shuffled_joint': donor = indices[common.donors(subset)]
    if condition.startswith('source'):
        if source is None or source.shape[1] != int(condition[6:]): raise ValueError('declared source width differs')
        x = source[indices]
    elif condition == 'hidden':
        if hidden is None or hidden.shape[1] != 1024: raise ValueError('1024 hidden features required')
        x = hidden[indices]
    else:
        if source is None or hidden is None or source.shape[1] != 1024 or hidden.shape[1] != 1024:
            raise ValueError('two 1024-wide feature blocks required')
        x = np.concatenate((source[indices], hidden[donor]), axis=1)
    if len(x) != len(indices) or not np.isfinite(x).all(): raise ValueError('finite aligned design required')
    return x, donor


def zero_block(x, training_mean, block):
    x, mean = np.asarray(x), np.asarray(training_mean)
    if x.ndim != 2 or x.shape[1] != 2048 or mean.shape != (2048,) or block not in ('source', 'hidden'):
        raise ValueError('two-block fitted normalizer and named block required')
    result = x.astype(np.float64, copy=True); chosen = slice(0, 1024) if block == 'source' else slice(1024, 2048)
    result[:, chosen] = mean[chosen]
    return result


def select(records):
    expected = {(s, f, a) for s in numeric.SEEDS for f in range(3) for a in numeric.ALPHAS}
    if len(records) != len(expected) or {(r['seed'], r['fold'], r['alpha']) for r in records} != expected:
        raise ValueError('complete TRAIN seed/fold/alpha grid required')
    if any(r['validation']['computed']['mae'] is None or not np.isfinite(r['validation']['computed']['mae']) for r in records):
        raise ValueError('computed-value selection requires support in every TRAIN fold')
    return min(numeric.ALPHAS, key=lambda a: (np.mean([r['validation']['computed']['mae'] for r in records if r['alpha'] == a]), -a))


def input_features(config, cache, seed):
    condition = config['condition']
    source = hidden = None
    if condition != 'hidden':
        width = 2048 if condition == 'source2048' else 1024
        source = numeric.fold_source(numeric.load_features(cache['features']['source']), width)
    if not condition.startswith('source'):
        if config['alias'] not in ('llama8b', 'codellama34b'): raise ValueError('cached checkpoint alias required')
        hidden = numeric.load_features(cache['features'][config['alias'] + f'_seed{seed}'])
    return source, hidden


def score_partition(prediction, values, groups, annotations, indices):
    return metrics(prediction, values[indices], groups[indices], {k: v[indices] for k, v in annotations.items()})


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, FIT); semantic.literature(config)
    if config['condition'] not in CONDITIONS: raise ValueError('declared feature condition required')
    rows, values, cache = state.load_inputs(config)
    ids = np.asarray([r['id'] for r in rows]); groups = np.asarray([r['component_id'] for r in rows])
    splits = np.asarray([r['split'] for r in rows]); table = state.table_for(rows)
    train = splits == 'train'; ti = np.flatnonzero(train)
    folds = common.folds(common.mask_table(table, train)); annotations = state.annotation(rows)
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        cv, fits, artifacts = [], [], {}
        for seed in numeric.SEEDS:
            s, h = input_features(config, cache, seed); weights = common.weights(common.mask_table(table, train), seed)
            for fold in range(3):
                fi, vi = ti[folds != fold], ti[folds == fold]
                if set(groups[fi]) & set(groups[vi]): raise ValueError('structural family spans TRAIN folds')
                xf, df = design(config['condition'], s, h, rows, fi)
                xv, dv = design(config['condition'], s, h, rows, vi)
                if set(df) & set(vi) or set(dv) & set(fi): raise ValueError('hidden donors cross fit/validation boundary')
                w = weights[folds != fold]; w = w / w.mean()
                for alpha in numeric.ALPHAS:
                    key = f'cv_seed{seed}_fold{fold}_alpha{int(alpha)}'; path = folder / (key + '.json')
                    bank = numeric.resume(path, config, source)
                    if bank is None:
                        model = numeric.fit(xf, values[fi], w, ids[fi].tolist(), 'train', alpha)
                        replay, payloads = numeric.save_model(folder, key, model); prediction = model.predict(xv)
                        if not np.array_equal(prediction, replay.predict(xv)): raise ValueError('CV parameter replay differs')
                        p = folder / (key + '_scores.npz')
                        storage._npz(p, predicted=prediction, truth=values[vi], ids=ids[vi], donor_ids=ids[dv])
                        payloads['scores'] = storage._pin(p)
                        bank = dict(source=source, config_hash=digest(config), seed=seed, fold=fold, alpha=alpha,
                            fit_groups=sorted(set(groups[fi])), validation_groups=sorted(set(groups[vi])),
                            fit_donor_ids_sha256=digest(ids[df].tolist()), validation_donor_ids_sha256=digest(ids[dv].tolist()),
                            validation=score_partition(prediction, values, groups, annotations, vi), artifacts=payloads)
                        base._put(path, bank)
                    cv.append(bank); artifacts[key] = storage._pin(path)
                    numeric.capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(cv) + len(fits)))
            del s, h
        alpha = select(cv); path = folder / 'selection_review_v1.json'
        base._put(path, dict(source=source, config_hash=digest(config), alpha=alpha,
            objective='computed-slot family-macro MAE; TRAIN structural folds and three seeds only; larger-alpha tie break'))
        artifacts['selection'] = storage._pin(path)
        for seed in numeric.SEEDS:
            key = f'selected_seed{seed}_alpha{int(alpha)}'; path = folder / (key + '.json')
            bank = numeric.resume(path, config, source)
            if bank is None:
                s, h = input_features(config, cache, seed); weights = common.weights(common.mask_table(table, train), seed)
                xt, dt = design(config['condition'], s, h, rows, ti)
                model = numeric.fit(xt, values[ti], weights, ids[ti].tolist(), 'train', alpha)
                replay, payloads = numeric.save_model(folder, key, model)
                arrays = dict(ids=ids, truth=values, splits=splits, predicted=np.zeros(values.shape, np.float64))
                joint = config['condition'] in ('joint', 'shuffled_joint')
                if joint:
                    arrays['hidden_at_training_mean'] = np.zeros(values.shape, np.float64)
                    arrays['source_at_training_mean'] = np.zeros(values.shape, np.float64)
                donor_ids = ids.copy(); panels = {}
                for split in ('train', 'development', 'calibration'):
                    indices = np.flatnonzero(splits == split)
                    if not len(indices): continue
                    x, donor = design(config['condition'], s, h, rows, indices); donor_ids[indices] = ids[donor]
                    pred = model.predict(x)
                    if not np.array_equal(pred, replay.predict(x)): raise ValueError('selected parameter replay differs')
                    arrays['predicted'][indices] = pred
                    panels[split] = dict(real=score_partition(pred, values, groups, annotations, indices),
                        prior=score_partition(np.broadcast_to(model.weighted_target_mean, pred.shape), values, groups, annotations, indices))
                    if joint:
                        for name, block in [('hidden_at_training_mean', 'hidden'), ('source_at_training_mean', 'source')]:
                            guesses = model.predict(zero_block(x, model.mean, block)); arrays[name][indices] = guesses
                            panels[split][name] = score_partition(guesses, values, groups, annotations, indices)
                arrays['donor_ids'] = donor_ids
                p = folder / (key + '_scores.npz'); storage._npz(p, **arrays); payloads['scores'] = storage._pin(p)
                bank = dict(source=source, config_hash=digest(config), seed=seed, alpha=alpha, panels=panels,
                    feature_width=len(model.mean), parameters=int(model.coef.size + model.intercept.size),
                    fit_donor_ids_sha256=digest(ids[dt].tolist()), artifacts=payloads)
                base._put(path, bank); del s, h
            fits.append(bank); artifacts[key] = storage._pin(path)
            numeric.capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(cv) + len(fits)))
        result = dict(status='complete_exploratory', evaluation_role=FIT, source=source, config_hash=digest(config),
            alias=config['alias'], condition=config['condition'], fits=fits, cv_banks=len(cv), selected_alpha=alpha,
            new_readout_fits=len(cv) + len(fits), new_model_queries=0, generated_holdouts_opened=False,
            inputs='source hash and/or archived hidden block plus intercept; annotations, values and IDs are labels/controls only',
            controls='shuffled hidden donors stay inside each fit/evaluation partition; their alphas are independently TRAIN-selected')
        return common.receipt(config, source, result, artifacts)


def report(config):
    source = common.validate_role(config, REPORT); semantic.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
    lines = ['# Conditional numeric prediction beyond source features', '',
        'Adaptive discovery on archived single-variable query states; no new model calls. '
        'All four scalar heads use TRAIN-only normalization and structural-fold selection on computed-value MAE. '
        'A conditional gain is relative to these finite source features/readout classes: the complete source determines the answer. '
        'It does not establish additional information beyond the program, native model execution or causal use.', '',
        '| Features | Width | Computed MAE | Computed exact | Untouched MAE | All-slot MAE |',
        '|---|---:|---:|---:|---:|---:|']
    cells, inputs, total = {}, {}, 0
    for request in config['workers']:
        worker = base._json(request['path'], request['sha256']); common.completed(worker)
        path = Path(worker['run_dir']) / 'results.json'; data = base._json(path); inputs[request['path']] = storage._pin(path)
        rows, truth, _ = state.load_inputs(worker); ids = np.asarray([r['id'] for r in rows])
        groups = np.asarray([r['component_id'] for r in rows]); split = np.asarray([r['split'] for r in rows]); annotations = state.annotation(rows)
        panels, families = [], None
        if len(data['fits']) != 3 or sorted(b['seed'] for b in data['fits']) != list(numeric.SEEDS):
            raise ValueError('all selected fitting seeds required')
        for bank in sorted(data['fits'], key=lambda b: b['seed']):
            with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
                if not np.array_equal(z['ids'], ids) or not np.array_equal(z['truth'], truth) or not np.array_equal(z['splits'], split):
                    raise ValueError('saved conditional labels/order differ')
                for label in ('train', 'development', 'calibration'):
                    indices = np.flatnonzero(split == label)
                    if not len(indices): continue
                    for variant in ('predicted', 'hidden_at_training_mean', 'source_at_training_mean'):
                        if variant not in z.files: continue
                        expected = bank['panels'][label]['real' if variant == 'predicted' else variant]
                        if score_partition(z[variant][indices], truth, groups, annotations, indices) != expected:
                            raise ValueError('saved conditional metrics differ')
            panel = bank['panels']['development']['real']; panels.append(panel)
            current = sorted(panel['computed']['family_mae'])
            if families is not None and families != current: raise ValueError('seed family support differs')
            families = current
        key = worker['alias'] + '/' + worker['condition']; total += data['new_readout_fits']
        if key in cells: raise ValueError('duplicate conditional cell')
        cells[key] = dict(families=families,
            mae=np.asarray([[p['computed']['family_mae'][g] for g in families] for p in panels]))
        average = lambda kind, metric: float(np.mean([p[kind][metric] for p in panels]))
        lines.append(f"| {key} | {data['fits'][0]['feature_width']} | {average('computed','mae'):.4f} | "
            f"{100*average('computed','exact'):.2f}% | {average('untouched','mae'):.4f} | {average('all','mae'):.4f} |")
    lines += ['', '## Paired family contrasts', '',
        'Joint minus comparator computed-value MAE; negative favors the joint predictor. '
        'Seeds are averaged inside families before 2,000 bootstrap replicates. Intervals are descriptive, '
        'non-simultaneous and based on inspected DEV. Three fitting seeds are not three independent datasets.', '',
        '| Model | Comparator | MAE difference | Descriptive 95% interval |', '|---|---|---:|---|']
    contrasts = []
    for alias in ('llama8b', 'codellama34b'):
        left = cells[alias + '/joint']
        for key in ('source/source1024', 'source/source2048', alias + '/hidden', alias + '/shuffled_joint'):
            right = cells[key]
            if left['families'] != right['families']: raise ValueError('paired comparison families differ')
            contrast = dict(alias=alias, comparator=key, **geometry.paired_family_interval(left['mae'], right['mae']))
            contrasts.append(contrast)
            lines.append(f"| {alias} | {key} | {contrast['delta']:.4f} | [{contrast['lower']:.4f}, {contrast['upper']:.4f}] |")
    lines += ['', 'Source1024 plus hidden1024 has2,048 nominal features. Source2048 controls nominal feature count, '
        'not identical inductive bias or effective rank. Hidden-only1024 is also independently selected. '
        'Shuffled-joint controls move the entire hidden block between structural families within each fold/split, '
        'preserving source/target alignment and numeric/lexical relatives. Their coefficients and alphas are fitted separately. '
        'Fixed-coefficient TRAIN-mean block ablations are saved as probe diagnostics, not interventions in the language model. '
        'The old pure global-state results remain unchanged; this edition changes the inputs and TRAIN selection objective. '
        'No layer, wording or feature-width search is performed here. No novel-family confirmation or sealed-final access.', '']
    path = Path(config['report']); base._publish(path, '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', evaluation_role=REPORT, source=source, config_hash=digest(config),
        inputs=inputs, paired_family_contrasts=contrasts, new_readout_fits=total, new_model_queries=0, generated_holdouts_opened=False)
    return common.receipt(config, source, result, dict(report=storage._pin(path)))
