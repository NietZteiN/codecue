"""Extend a frozen conditional ridge path with explicit fit reuse and priors."""
from pathlib import Path
import numpy as np

from . import arithmetic_conditional_state as old
from . import arithmetic_state_common as common
from . import arithmetic_semantic_controls as semantic
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from . import weighted_ridge
from .datasets import digest

PRIORS = 'discovery_arithmetic_penalty_priors_v1'
FIT = 'discovery_arithmetic_penalty_fit_v1'
AUDIT = 'discovery_arithmetic_penalty_audit_v1'
REPORT = 'discovery_arithmetic_penalty_report_v1'
OLD_ALPHAS = (1., 100., 10000.)
NEW_ALPHAS = (100000., 1000000., 10000000.)
ALPHAS = OLD_ALPHAS + NEW_ALPHAS
PRIOR_NAMES = ('zero', 'mean', 'median', 'computed_median')


def weighted_median(values, weights):
    values, weights = np.asarray(values), np.asarray(weights)
    if (values.ndim != 1 or values.shape != weights.shape or not len(values)
            or not np.isfinite(values).all() or not np.isfinite(weights).all() or np.any(weights <= 0)):
        raise ValueError('finite nonempty values and positive median weights required')
    order = np.argsort(values, kind='stable'); v, w = values[order], weights[order]
    return float(v[np.searchsorted(np.cumsum(w), .5 * w.sum(), side='left')])


def fit_priors(values, computed, groups, weights, split):
    values, computed, groups, weights = map(np.asarray, (values, computed, groups, weights))
    if (split != 'train' or values.shape != (len(groups), 4) or computed.shape != values.shape
            or computed.dtype != bool or weights.shape != (len(groups),) or not len(groups)
            or not np.isfinite(values).all() or not np.isfinite(weights).all() or np.any(weights <= 0)):
        raise ValueError('TRAIN-only aligned four-slot prior observations required')
    denominators = {g: max(1, int(computed[groups == g].sum())) for g in set(groups)}
    cw = weights / np.asarray([denominators[g] for g in groups])
    med = np.asarray([weighted_median(values[:, j], weights) for j in range(4)])
    support = computed.sum(axis=0)
    conditional = [weighted_median(values[computed[:, j], j], cw[computed[:, j]]) if support[j] else med[j] for j in range(4)]
    constants = dict(zero=np.zeros(4).tolist(), mean=np.average(values, axis=0, weights=weights).tolist(),
        median=med.tolist(), computed_median=list(conditional))
    return dict(constants=constants, computed_support=support.tolist(),
        unsupported_computed_heads=np.flatnonzero(support == 0).tolist(),
        fallback='all-slot TRAIN median for a head with no computed fitting observations')


def reference(config):
    request = config['reference_worker']; cfg = base._json(request['path'], request['sha256'])
    proof = common.completed(cfg); data = base._json(Path(cfg['run_dir']) / 'results.json')
    if cfg['evaluation_role'] != old.FIT or data['cv_banks'] != 27 or data['new_readout_fits'] != 30:
        raise ValueError('complete original conditional recipe required')
    audit = base._json(config['reference_audit']['path'], config['reference_audit']['sha256'])
    key = cfg['alias'] + '/' + cfg['condition']
    if (audit['status'] != 'complete_audited_exploratory' or audit['inputs'][key] != proof['artifacts']['results']
            or cfg['seeds'] != [11, 29, 47]):
        raise ValueError('original worker must be covered by its numerical audit')
    return cfg, proof, data


def prior_context(values, masks, ids, groups, indices, weights):
    return dict(fit_ids_sha256=digest(ids[indices].tolist()), fit_groups=sorted(set(groups[indices])),
        targets_sha256=weighted_ridge._array_hash(values[indices]), weights_sha256=weighted_ridge._array_hash(weights),
        computed_sha256=digest(masks['computed'][indices].tolist()))


def prepare_priors(config):
    from .confidence import _run_lock
    source = common.validate_role(config, PRIORS); semantic.literature(config)
    cfg, _, _ = reference(config); rows, values, _ = old.state.load_inputs(cfg)
    ids = np.asarray([r['id'] for r in rows]); groups = np.asarray([r['component_id'] for r in rows])
    train = np.asarray([r['split'] == 'train' for r in rows]); ti = np.flatnonzero(train)
    table = old.state.table_for(rows); folds = common.folds(common.mask_table(table, train)); masks = old.state.annotation(rows)
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        cv, full, artifacts = [], [], {}
        for seed in old.numeric.SEEDS:
            weights = common.weights(common.mask_table(table, train), seed)
            for fold in range(3):
                fi, vi = ti[folds != fold], ti[folds == fold]; w = weights[folds != fold]; w = w / w.mean()
                estimate = fit_priors(values[fi], masks['computed'][fi], groups[fi], w, 'train')
                validation = {name: old.score_partition(np.broadcast_to(c, values[vi].shape), values, groups, masks, vi)
                    for name, c in estimate['constants'].items()}
                key = f'cv_seed{seed}_fold{fold}'; path = folder / (key + '.json')
                data = dict(source=source, config_hash=digest(config), seed=seed, fold=fold,
                    validation_ids_sha256=digest(ids[vi].tolist()), validation_groups=sorted(set(groups[vi])),
                    **prior_context(values, masks, ids, groups, fi, w), **estimate, validation=validation)
                base._put(path, data); pin = storage._pin(path); cv.append(pin); artifacts[key] = pin
            estimate = fit_priors(values[ti], masks['computed'][ti], groups[ti], weights, 'train')
            key = f'full_seed{seed}'; path = folder / (key + '.json')
            base._put(path, dict(source=source, config_hash=digest(config), seed=seed,
                **prior_context(values, masks, ids, groups, ti, weights), **estimate))
            pin = storage._pin(path); full.append(pin); artifacts[key] = pin
        result = dict(status='complete_exploratory', source=source, evaluation_role=PRIORS, config_hash=digest(config),
            cv=cv, full=full, ordered_case_ids_sha256=digest(ids.tolist()), values_sha256=digest(values.tolist()),
            new_prior_estimates=36, new_readout_fits=0, new_model_queries=0, generated_holdouts_opened=False,
            policy='all priors fit within each TRAIN fitting partition; full-TRAIN constants are not evaluated on DEV here')
        return common.receipt(config, source, result, artifacts)


def load_priors(config, ids, values):
    request = config['prior_config']; cfg = base._json(request['path'], request['sha256']); common.completed(cfg)
    data = base._json(Path(cfg['run_dir']) / 'results.json')
    if data['ordered_case_ids_sha256'] != digest(ids.tolist()) or data['values_sha256'] != digest(values.tolist()):
        raise ValueError('shared prior cohort/targets differ')
    cv = [base._json(p['path'], p['sha256']) for p in data['cv']]
    full = [base._json(p['path'], p['sha256']) for p in data['full']]
    return cv, {p['seed']: p for p in full}


def select(cv, priors):
    expected = {(s, f, a) for s in old.numeric.SEEDS for f in range(3) for a in ALPHAS}
    if len(cv) != len(expected) or {(r['seed'], r['fold'], r['alpha']) for r in cv} != expected:
        raise ValueError('complete six-penalty TRAIN grid required')
    if len(priors) != 9 or {(r['seed'], r['fold']) for r in priors} != {(s, f) for s in old.numeric.SEEDS for f in range(3)}:
        raise ValueError('complete fold-local prior grid required')
    loss = lambda panel: panel['computed']['mae']
    observations = [loss(r['validation']) for r in cv] + [loss(r['validation'][p]) for r in priors for p in PRIOR_NAMES]
    if any(v is None or not np.isfinite(v) for v in observations): raise ValueError('supported finite computed CV losses required')
    candidates = [dict(kind='ridge', alpha=a, cv_mae=float(np.mean([loss(r['validation']) for r in cv if r['alpha'] == a]))) for a in ALPHAS]
    candidates += [dict(kind='prior', prior=p, cv_mae=float(np.mean([loss(r['validation'][p]) for r in priors]))) for p in PRIOR_NAMES]
    key = lambda r: (r['cv_mae'], 0 if r['kind'] == 'prior' else 1,
        PRIOR_NAMES.index(r['prior']) if r['kind'] == 'prior' else -r['alpha'])
    ridge = min(candidates[:len(ALPHAS)], key=key); overall = min(candidates, key=key)
    return dict(ridge_alpha=ridge['alpha'], overall=overall, candidates=candidates,
        ridge_grid_position='upper_boundary' if ridge['alpha'] == max(ALPHAS) else 'lower_boundary' if ridge['alpha'] == min(ALPHAS) else 'interior',
        policy='TRAIN mean of nine structural fold/seed losses; constants win exact ties, zero first; larger ridge alpha wins ridge ties')


def training_context(x, values, weights, ids, indices, donor):
    return dict(training_ids=ids[indices].tolist(), training_input_sha256={k: weighted_ridge._array_hash(v)
        for k, v in [('features', x), ('targets', values[indices]), ('sample_weight', weights)]},
        fit_donor_ids_sha256=digest(ids[donor].tolist()))


def check_context(bank, context, seed, alpha, fold=None, source=None, config=None):
    if bank['seed'] != seed or bank['alpha'] != alpha or (fold is not None and bank['fold'] != fold):
        raise ValueError('bank seed/fold/penalty differs')
    if source is not None and (bank['source'] != source or bank['config_hash'] != digest(config)):
        raise ValueError('bank owning source/configuration differs')
    metadata = base._json(bank['artifacts']['metadata']['path'], bank['artifacts']['metadata']['sha256'])
    if (metadata['training_ids'] != context['training_ids'] or metadata['training_input_sha256'] != context['training_input_sha256']
            or bank['fit_donor_ids_sha256'] != context['fit_donor_ids_sha256'] or metadata['alpha'] != alpha):
        raise ValueError('TRAIN feature/target/weight/donor fingerprint differs')


def reused_bank(config, source, old_config, old_proof, old_path, target, context, seed, alpha, fold=None):
    bank = old.numeric.resume(old_path, old_config, old_proof['source'])
    if bank is None: raise ValueError('requested original bank missing')
    check_context(bank, context, seed, alpha, fold, old_proof['source'], old_config)
    pin = storage._pin(old_path)
    wrapper = dict(bank, source=source, config_hash=digest(config), bank_type='reused_fit_reference',
        origin=dict(bank=pin, config=config['reference_worker'], source=bank['source']),
        artifacts=dict(bank['artifacts'], origin_bank=pin))
    base._put(target, wrapper)
    return wrapper


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, FIT); semantic.literature(config)
    if config['alphas'] != list(ALPHAS): raise ValueError('frozen extended penalty path required')
    ref, ref_proof, ref_results = reference(config); rows, values, cache = old.state.load_inputs(ref)
    ids = np.asarray([r['id'] for r in rows]); groups = np.asarray([r['component_id'] for r in rows]); splits = np.asarray([r['split'] for r in rows])
    table = old.state.table_for(rows); train = splits == 'train'; ti = np.flatnonzero(train)
    folds = common.folds(common.mask_table(table, train)); masks = old.state.annotation(rows)
    priors, full_priors = load_priors(config, ids, values); folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        cv, fits, artifacts = [], [], {}; new_cv = reused_cv = new_selected = reused_selected = 0
        for seed in old.numeric.SEEDS:
            s, h = old.input_features(ref, cache, seed); weights = common.weights(common.mask_table(table, train), seed)
            for fold in range(3):
                fi, vi = ti[folds != fold], ti[folds == fold]
                xf, df = old.design(ref['condition'], s, h, rows, fi); xv, dv = old.design(ref['condition'], s, h, rows, vi)
                if set(df) & set(vi) or set(dv) & set(fi): raise ValueError('donors cross TRAIN fold boundary')
                w = weights[folds != fold]; w = w / w.mean(); context = training_context(xf, values, w, ids, fi, df)
                prior = next(p for p in priors if p['seed'] == seed and p['fold'] == fold)
                expected_prior = prior_context(values, masks, ids, groups, fi, w)
                if expected_prior != {k: prior[k] for k in expected_prior}:
                    raise ValueError('prior fitting observations differ')
                for alpha in ALPHAS:
                    key = f'cv_seed{seed}_fold{fold}_alpha{int(alpha)}'; path = folder / (key + '.json')
                    if alpha in OLD_ALPHAS:
                        bank = reused_bank(config, source, ref, ref_proof, Path(ref['run_dir']) / (key + '.json'),
                            path, context, seed, alpha, fold); reused_cv += 1
                    else:
                        bank = old.numeric.resume(path, config, source)
                        if bank is None:
                            model = old.numeric.fit(xf, values[fi], w, ids[fi].tolist(), 'train', alpha)
                            replay, payloads = old.numeric.save_model(folder, key, model); pred = model.predict(xv)
                            if not np.array_equal(pred, replay.predict(xv)): raise ValueError('new CV save/reload replay differs')
                            p = folder / (key + '_scores.npz'); storage._npz(p, predicted=pred, truth=values[vi], ids=ids[vi], donor_ids=ids[dv]); payloads['scores'] = storage._pin(p)
                            bank = dict(source=source, config_hash=digest(config), bank_type='new_fit', seed=seed, fold=fold, alpha=alpha,
                                fit_groups=sorted(set(groups[fi])), validation_groups=sorted(set(groups[vi])),
                                fit_donor_ids_sha256=context['fit_donor_ids_sha256'], validation_donor_ids_sha256=digest(ids[dv].tolist()),
                                validation=old.score_partition(pred, values, groups, masks, vi), artifacts=payloads)
                            base._put(path, bank)
                        check_context(bank, context, seed, alpha, fold, source, config); new_cv += 1
                    if bank['fit_groups'] != sorted(set(groups[fi])) or bank['validation_groups'] != sorted(set(groups[vi])) or bank['validation_donor_ids_sha256'] != digest(ids[dv].tolist()):
                        raise ValueError('reused/new validation partition differs')
                    cv.append(bank); artifacts[key] = storage._pin(path)
                    old.numeric.capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(cv) + len(fits), new_cv_fits=new_cv, reused_cv_banks=reused_cv))
            del s, h
        selection = select(cv, priors); alpha = selection['ridge_alpha']; p = folder / 'selection_review_v1.json'
        base._put(p, dict(source=source, config_hash=digest(config), **selection)); artifacts['selection'] = storage._pin(p)
        for seed in old.numeric.SEEDS:
            s, h = old.input_features(ref, cache, seed); weights = common.weights(common.mask_table(table, train), seed)
            xt, donor = old.design(ref['condition'], s, h, rows, ti); context = training_context(xt, values, weights, ids, ti, donor)
            key = f'selected_seed{seed}_alpha{int(alpha)}'; path = folder / (key + '.json')
            reusable = any(b['seed'] == seed and b['alpha'] == alpha for b in ref_results['fits'])
            if reusable:
                bank = reused_bank(config, source, ref, ref_proof, Path(ref['run_dir']) / (key + '.json'), path, context, seed, alpha)
                reused_selected += 1
            else:
                bank = old.numeric.resume(path, config, source)
                if bank is None:
                    model = old.numeric.fit(xt, values[ti], weights, ids[ti].tolist(), 'train', alpha)
                    replay, payloads = old.numeric.save_model(folder, key, model)
                    arrays = dict(ids=ids, truth=values, splits=splits, donor_ids=ids.copy(), predicted=np.zeros(values.shape))
                    joint = ref['condition'] in ('joint', 'shuffled_joint')
                    if joint:
                        arrays.update(hidden_at_training_mean=np.zeros(values.shape), source_at_training_mean=np.zeros(values.shape))
                    panels = {}
                    for label in ('train', 'development', 'calibration'):
                        idx = np.flatnonzero(splits == label)
                        if not len(idx): continue
                        x, d = old.design(ref['condition'], s, h, rows, idx); pred = model.predict(x)
                        if not np.array_equal(pred, replay.predict(x)): raise ValueError('selected parameter replay differs')
                        arrays['predicted'][idx] = pred; arrays['donor_ids'][idx] = ids[d]
                        panels[label] = dict(real=old.score_partition(pred, values, groups, masks, idx),
                            prior=old.score_partition(np.broadcast_to(model.weighted_target_mean, pred.shape), values, groups, masks, idx))
                        if joint:
                            for name, block in [('hidden_at_training_mean', 'hidden'), ('source_at_training_mean', 'source')]:
                                guesses = model.predict(old.zero_block(x, model.mean, block)); arrays[name][idx] = guesses
                                panels[label][name] = old.score_partition(guesses, values, groups, masks, idx)
                    p = folder / (key + '_scores.npz'); storage._npz(p, **arrays); payloads['scores'] = storage._pin(p)
                    bank = dict(source=source, config_hash=digest(config), bank_type='new_fit', seed=seed, alpha=alpha,
                        panels=panels, feature_width=len(model.mean), parameters=int(model.coef.size + model.intercept.size),
                        fit_donor_ids_sha256=context['fit_donor_ids_sha256'], artifacts=payloads)
                    base._put(path, bank)
                check_context(bank, context, seed, alpha, source=source, config=config); new_selected += 1
            artifacts[key] = storage._pin(path)
            prior = full_priors[seed]
            expected = prior_context(values, masks, ids, groups, ti, weights)
            if expected != {k: prior[k] for k in expected}: raise ValueError('full-TRAIN prior context differs')
            prior_panels = {}; overall_panels = {}
            with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
                if not np.array_equal(z['ids'], ids) or not np.array_equal(z['truth'], values) or not np.array_equal(z['splits'], splits):
                    raise ValueError('selected evaluation cohort differs')
                overall = np.asarray(z['predicted']).copy()
                for label in ('train', 'development', 'calibration'):
                    idx = np.flatnonzero(splits == label)
                    if not len(idx): continue
                    if old.score_partition(z['predicted'][idx], values, groups, masks, idx) != bank['panels'][label]['real']:
                        raise ValueError('selected ridge metric replay differs')
                    prior_panels[label] = {name: old.score_partition(np.broadcast_to(c, values[idx].shape), values, groups, masks, idx)
                        for name, c in prior['constants'].items()}
                    chosen = selection['overall']
                    if chosen['kind'] == 'prior': overall[idx] = prior['constants'][chosen['prior']]
                    overall_panels[label] = old.score_partition(overall[idx], values, groups, masks, idx)
                ap = folder / f'analysis_seed{seed}_scores.npz'
                storage._npz(ap, ridge=z['predicted'], overall=overall, truth=values, ids=ids, splits=splits)
            analysis = dict(seed=seed, alpha=alpha, bank_type=bank['bank_type'], ridge_bank=storage._pin(path),
                ridge_panels=bank['panels'], prior_panels=prior_panels, overall_panels=overall_panels,
                artifacts=dict(bank['artifacts'], ridge_bank=storage._pin(path), analysis_scores=storage._pin(ap)))
            p = folder / f'analysis_seed{seed}.json'; base._put(p, analysis); artifacts[f'analysis_seed{seed}'] = storage._pin(p); fits.append(analysis)
            del s, h
        result = dict(status='complete_exploratory', source=source, evaluation_role=FIT, config_hash=digest(config),
            alias=ref['alias'], condition=ref['condition'], reference_worker=config['reference_worker'], prior_config=config['prior_config'],
            selection=selection, fits=fits, cv_banks=len(cv), new_cv_fits=new_cv, reused_cv_banks=reused_cv,
            new_selected_fits=new_selected, reused_selected_banks=reused_selected,
            new_readout_fits=new_cv + new_selected, reused_readout_banks=reused_cv + reused_selected,
            new_model_queries=0, generated_holdouts_opened=False)
        return common.receipt(config, source, result, artifacts)
