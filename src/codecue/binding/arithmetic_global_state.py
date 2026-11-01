"""TRAIN-selected all-variable and direct-relation readouts of one query state.

Oracle values, query slots and definition identities are labels/annotations only.
The design matrix contains exactly the declared hidden or source features.
"""
from itertools import combinations, permutations
from pathlib import Path

import numpy as np

from . import arithmetic_numeric_exploration as numeric
from . import arithmetic_numeric_geometry as geometry
from . import arithmetic_semantic_controls as semantic
from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

PREPARE = 'discovery_global_state_prepare_v1'
FIT = 'discovery_global_state_fit_v1'
REPORT = 'discovery_global_state_report_v1'
GROUPS = ('scalar', 'categorical', 'relations')
PAIRS = tuple(combinations(range(4), 2))
SUMS = tuple((a, b, c) for a, b in PAIRS for c in range(4) if c not in (a, b))
DIFFERENCES = tuple(permutations(range(4), 3))
COORDINATES = tuple([('eq', *p) for p in PAIRS] + [('lt', *p) for p in PAIRS]
    + [('sum', *p) for p in SUMS] + [('difference', *p) for p in DIFFERENCES])
TYPES = ('eq', 'lt', 'sum', 'difference')
SLICES = dict(scalar=slice(0, 4), categorical=slice(4, 776), relations=slice(776, 824))
WIDTH = 824


def relations(values):
    values = np.asarray(values)
    if values.ndim != 2 or values.shape[1] != 4 or not np.isfinite(values).all():
        raise ValueError('four finite numeric slots required')
    return np.stack([values[:, a] == values[:, b] for a, b in PAIRS]
        + [values[:, a] < values[:, b] for a, b in PAIRS]
        + [values[:, a] + values[:, b] == values[:, c] for a, b, c in SUMS]
        + [values[:, a] - values[:, b] == values[:, c] for a, b, c in DIFFERENCES], axis=1)


def targets(values):
    values = np.asarray(values)
    if (values.ndim != 2 or values.shape[1] != 4 or not np.issubdtype(values.dtype, np.integer)
            or np.any(np.abs(values) > 96)):
        raise ValueError('four integer targets in the frozen -96..96 domain required')
    return np.concatenate((values.astype(float), np.eye(193)[values + 96].reshape(len(values), 772),
        relations(values).astype(float)), axis=1)


def predictions(scores):
    scores = np.asarray(scores)
    if scores.ndim != 2 or scores.shape[1] != WIDTH or not np.isfinite(scores).all():
        raise ValueError('finite 824-column predictions required')
    return dict(scalar=scores[:, :4], categorical=scores[:, 4:776].reshape(-1, 4, 193).argmax(axis=2) - 96,
        relations=scores[:, 776:])


def eligibility(truth, body_ids, minimum=12):
    """Count independent numeric bodies, never repeated lexical realizations."""
    truth, body_ids = np.asarray(truth), np.asarray(body_ids)
    if truth.ndim != 2 or truth.shape != (len(body_ids), 48) or truth.dtype != bool or minimum < 1:
        raise ValueError('aligned Boolean relation truth and positive support threshold required')
    _, first, inverse = np.unique(body_ids, return_index=True, return_inverse=True)
    unique = truth[first]
    if not np.array_equal(truth, unique[inverse]):
        raise ValueError('one numeric body has inconsistent relation truth')
    positive = unique.sum(axis=0)
    negative = len(unique) - positive
    return dict(eligible=((positive >= minimum) & (negative >= minimum)).tolist(),
        positive_bodies=positive.tolist(), negative_bodies=negative.tolist(), minimum_bodies=minimum)


def family_mean(values, groups):
    values, groups = np.asarray(values), np.asarray(groups)
    if values.ndim != 1 or values.shape != groups.shape or not len(values):
        raise ValueError('nonempty aligned family observations required')
    return float(np.mean([values[groups == g].mean() for g in np.unique(groups)]))


def relation_metrics(guess, truth, groups, eligible, mask=None):
    """Each class recall gives equal weight to families containing that class.

    Missing classes and TRAIN-ineligible cells are explicit nulls. Each relation
    type averages its supported heads; the aggregate weights the four types equally.
    """
    guess, truth = np.asarray(guess, bool), np.asarray(truth, bool)
    eligible = np.asarray(eligible, bool)
    if guess.shape != truth.shape or truth.shape != (len(groups), 48) or eligible.shape != (48,):
        raise ValueError('aligned direct relation decisions required')
    mask = np.ones(truth.shape, bool) if mask is None else np.asarray(mask, bool)
    if mask.shape != truth.shape: raise ValueError('relation annotation shape differs')
    cells = []
    for j, coordinate in enumerate(COORDINATES):
        use = mask[:, j]; positive = use & truth[:, j]; negative = use & ~truth[:, j]
        supported = eligible[j] and positive.any() and negative.any()
        ba = .5 * (family_mean(guess[positive, j], np.asarray(groups)[positive])
            + family_mean(~guess[negative, j], np.asarray(groups)[negative])) if supported else None
        cells.append(dict(coordinate=list(coordinate), eligible=bool(eligible[j]),
            positive=int(positive.sum()), negative=int(negative.sum()), balanced_accuracy=ba))
    by_type = {}
    for kind in TYPES:
        valid = [c['balanced_accuracy'] for c in cells if c['coordinate'][0] == kind and c['balanced_accuracy'] is not None]
        by_type[kind] = dict(balanced_accuracy=float(np.mean(valid)) if valid else None, supported_heads=len(valid))
    valid = [v['balanced_accuracy'] for v in by_type.values() if v['balanced_accuracy'] is not None]
    return dict(type_macro_balanced_accuracy=float(np.mean(valid)) if len(valid) == 4 else None,
        supported_types=len(valid), by_type=by_type, cells=cells)


def score(scores, values, groups, support, prevalence, annotations=None):
    guessed = predictions(scores)
    prevalence = np.asarray(prevalence)
    if prevalence.shape != (48,) or not np.isfinite(prevalence).all() or np.any((prevalence < 0) | (prevalence > 1)):
        raise ValueError('fitting-only weighted binary prevalences required')
    output = {}
    for kind in ('scalar', 'categorical'):
        value = guessed[kind]; correct = np.rint(value) == values
        slots = [dict(exact=family_mean(correct[:, j], groups), mae=family_mean(np.abs(value[:, j] - values[:, j]), groups)) for j in range(4)]
        output[kind] = dict(per_slot=slots, slot_macro_exact=float(np.mean([p['exact'] for p in slots])),
            slot_macro_mae=float(np.mean([p['mae'] for p in slots])), all_four_exact=family_mean(correct.all(axis=1), groups))
        if annotations is not None:
            strata = {}
            for name, mask in annotations.items():
                if np.asarray(mask).shape != values.shape: raise ValueError('slot annotation shape differs')
                i, j = np.nonzero(mask)
                strata[name] = dict(observations=len(i), exact=family_mean(correct[i, j], np.asarray(groups)[i]),
                    mae=family_mean(np.abs(value[i, j] - values[i, j]), np.asarray(groups)[i])) if len(i) else dict(observations=0)
            output[kind]['strata'] = strata
    truth = relations(values); eligible = support['eligible']
    decisions = guessed['relations'] >= prevalence
    output['direct_relations'] = relation_metrics(decisions, truth, groups, eligible)
    output['derived_scalar_relations'] = relation_metrics(relations(np.rint(guessed['scalar'])), truth, groups, eligible)
    output['derived_categorical_relations'] = relation_metrics(relations(guessed['categorical']), truth, groups, eligible)
    if annotations is not None:
        computed = annotations['computed']
        involving = np.stack([computed[:, list(c[1:])].any(axis=1) for c in COORDINATES], axis=1)
        output['direct_relations_involving_computed'] = relation_metrics(decisions, truth, groups, eligible, involving)
    return output


def select(records):
    expected = {(s, f, a) for s in numeric.SEEDS for f in range(3) for a in numeric.ALPHAS}
    if len(records) != len(expected) or {(r['seed'], r['fold'], r['alpha']) for r in records} != expected:
        raise ValueError('complete TRAIN three-seed three-fold alpha grid required')
    def loss(row, name):
        panel = row['validation']
        return panel[name]['slot_macro_mae'] if name == 'scalar' else -panel[name]['slot_macro_exact'] if name == 'categorical' else (
            -panel['direct_relations']['type_macro_balanced_accuracy'] if panel['direct_relations']['type_macro_balanced_accuracy'] is not None else None)
    result = {}
    for name in GROUPS:
        # Unsupported folds are identical across alphas. If none support all
        # types, the group remains unselected rather than tuning on DEV.
        available = {(r['seed'], r['fold']) for r in records if loss(r, name) is not None}
        result[name] = min(numeric.ALPHAS, key=lambda a: (np.mean([loss(r, name) for r in records
            if r['alpha'] == a and (r['seed'], r['fold']) in available]), -a)) if available else None
    return result


def table_for(rows):
    return [dict(case_id=r['id'], group=r['component_id'], split=r['split'], stratum=r['family_stratum']) for r in rows]


def annotation(rows, donor=None):
    donor = np.arange(len(rows)) if donor is None else donor
    query = np.arange(4)[None, :] == np.asarray([rows[i]['query_slot'] for i in donor])[:, None]
    computed = np.asarray([rows[i]['oracle']['definitions'] for i in donor]) >= 4
    return dict(queried=query, unqueried=~query, computed=computed, untouched=~computed)


def prepare(config):
    from sklearn.feature_extraction.text import HashingVectorizer
    from .confidence import _run_lock
    source = common.validate_role(config, PREPARE); semantic.literature(config)
    _, _, _, rows, _ = audit.load_cache(config)
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        prepared = base._json(config['labels']['path'], config['labels']['sha256']); common.completed(prepared)
        # The completion receipt, rather than a mutable path lookup, pins labels.
        proof = base._json(Path(prepared['run_dir']) / 'completion_manifest_v1.json')
        entry = proof['artifacts']['labels']
        with np.load(entry['path'], allow_pickle=False) as arrays:
            values, ids = arrays['final_values'][:, 0], arrays['case_ids']
        if not np.array_equal(ids, [r['id'] for r in rows]) or not np.array_equal(values, [r['oracle']['values'] for r in rows]):
            raise ValueError('global targets differ from independent semantic oracle')
        targets(values)  # Validate the declared categorical domain before fits.
        artifacts, features = {}, {}
        def save(name, x):
            path = folder / (name + '.npy'); pending = folder / (name + '.pending.npy')
            with pending.open('wb') as stream: np.save(stream, np.asarray(x, np.float32), allow_pickle=False)
            pending.replace(path)
            entry = dict(storage._pin(path), shape=list(x.shape)); features[name] = entry; artifacts[name] = entry
        text = HashingVectorizer(analyzer='char', ngram_range=(3, 5), n_features=8192, norm=None,
            alternate_sign=True).transform([r['source'] for r in rows]).toarray().astype(np.float32)
        save('source', text); del text
        for name, request in config['query_caches'].items():
            old = base._json(request['path'], request['sha256']); common.completed(old)
            data = base._json(Path(old['run_dir']) / 'results.json')
            if data['ordered_case_ids_sha256'] != digest(ids.tolist()): raise ValueError('query cache order differs')
            raw = numeric.load_features(data['query_vectors'])[:, data['layers'].index(config['layers'][name])]
            save(name + '_raw', raw)
            for seed in numeric.SEEDS: save(name + f'_seed{seed}', raw @ numeric.nested_projection(raw.shape[1], seed))
        result = dict(status='complete_exploratory', evaluation_role=PREPARE, source=source, config_hash=digest(config),
            cases=len(rows), ordered_case_ids_sha256=digest(ids.tolist()), values_sha256=digest(values.tolist()),
            features=features, coordinates=[list(c) for c in COORDINATES], real_target_columns=WIDTH,
            new_model_queries=0, new_fits=0, generated_holdouts_opened=False)
        return common.receipt(config, source, result, artifacts)


def load_inputs(config):
    _, _, _, rows, _ = audit.load_cache(config)
    request = config['cache_config']; cache_config = base._json(request['path'], request['sha256']); common.completed(cache_config)
    cache = base._json(Path(cache_config['run_dir']) / 'results.json')
    values = np.asarray([r['oracle']['values'] for r in rows], np.int64)
    if cache['ordered_case_ids_sha256'] != digest([r['id'] for r in rows]) or cache['values_sha256'] != digest(values.tolist()):
        raise ValueError('prepared global rows or targets changed')
    return rows, values, cache


def features(config, cache, seed):
    name = 'source' if config['backend'] == 'source' else config['alias'] + ('_raw' if config['width'] == config['full_width'] else f'_seed{seed}')
    x = numeric.load_features(cache['features'][name])
    x = numeric.fold_source(x, config['width']) if config['backend'] == 'source' else x
    if x.shape[1] != config['width']: raise ValueError('declared pure feature width differs')
    return x


def fit_policy(values, bodies, weights):
    truth = relations(values)
    return eligibility(truth, bodies), np.average(truth, axis=0, weights=weights)


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, FIT); semantic.literature(config)
    rows, values, cache = load_inputs(config)
    table = table_for(rows); ids = np.asarray([r['id'] for r in rows]); groups = np.asarray([r['component_id'] for r in rows])
    split = np.asarray([r['split'] for r in rows]); bodies = np.asarray([r['body_id'] for r in rows])
    donor = common.donors(rows); control = values[donor]; control_bodies = bodies[donor]
    y = targets(values); shuffled_y = targets(control)
    train = split == 'train'; ti = np.flatnonzero(train); folds = common.folds(common.mask_table(table, train))
    annotations = annotation(rows); control_annotations = annotation(rows, donor)
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        cv, selected, artifacts = [], [], {}
        for seed in numeric.SEEDS:
            x = features(config, cache, seed); weights = common.weights(common.mask_table(table, train), seed)
            for fold in range(3):
                fit_indices, val = ti[folds != fold], ti[folds == fold]
                w = weights[folds != fold]; w = w / w.mean()
                support, threshold = fit_policy(values[fit_indices], bodies[fit_indices], w)
                for alpha in numeric.ALPHAS:
                    key = f'cv_seed{seed}_fold{fold}_alpha{int(alpha)}'; path = folder / (key + '.json')
                    record = numeric.resume(path, config, source)
                    if record is None:
                        model = numeric.fit(x[fit_indices], y[fit_indices], w, ids[fit_indices].tolist(), 'train', alpha)
                        replay, payloads = numeric.save_model(folder, key, model)
                        pred = model.predict(x[val])
                        if not np.array_equal(pred, replay.predict(x[val])): raise ValueError('CV parameter replay differs')
                        record = dict(source=source, config_hash=digest(config), seed=seed, fold=fold, alpha=alpha,
                            fit_groups=sorted(set(groups[fit_indices])), validation_groups=sorted(set(groups[val])),
                            relation_support=support, threshold=threshold.tolist(),
                            validation=score(pred, values[val], groups[val], support, threshold), artifacts=payloads)
                        base._put(path, record)
                    cv.append(record); artifacts[key] = storage._pin(path)
                    numeric.capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(cv) + len(selected)))
        selection = select(cv); selection_path = folder / 'selection_review_v1.json'
        locked = dict(source=source, config_hash=digest(config), groups=selection,
            scope='TRAIN structural folds only; larger-alpha tie break; unsupported relation group unselected')
        base._put(selection_path, locked); artifacts['selection'] = storage._pin(selection_path)
        for seed in numeric.SEEDS:
            x = features(config, cache, seed); weights = common.weights(common.mask_table(table, train), seed)
            support, threshold = fit_policy(values[train], bodies[train], weights)
            csupport, cthreshold = fit_policy(control[train], control_bodies[train], weights)
            for alpha in sorted({a for a in selection.values() if a is not None}):
                key = f'selected_seed{seed}_alpha{int(alpha)}'; path = folder / (key + '.json')
                bank = numeric.resume(path, config, source)
                if bank is None:
                    model = numeric.fit(x[train], np.concatenate((y[train], shuffled_y[train]), axis=1), weights, ids[train].tolist(), 'train', alpha)
                    replay, payloads = numeric.save_model(folder, key, model); pred = model.predict(x)
                    if not np.array_equal(pred, replay.predict(x)): raise ValueError('selected parameter replay differs')
                    real, shuffled = np.split(pred, 2, axis=1)
                    scores_path = folder / (key + '_scores.npz')
                    storage._npz(scores_path, real=real, shuffled=shuffled, truth=values, control_truth=control, ids=ids, split=split)
                    payloads['scores'] = storage._pin(scores_path)
                    panels = {}
                    for label in ('train', 'development', 'calibration'):
                        mask = split == label
                        panels[label] = dict(real=score(real[mask], values[mask], groups[mask], support, threshold,
                                {k: v[mask] for k, v in annotations.items()}),
                            control=score(shuffled[mask], control[mask], groups[mask], csupport, cthreshold,
                                {k: v[mask] for k, v in control_annotations.items()}),
                            prior=score(np.broadcast_to(model.weighted_target_mean[:WIDTH], (int(mask.sum()), WIDTH)),
                                values[mask], groups[mask], support, threshold))
                    seen = [set(values[train, j]) for j in range(4)]
                    bank = dict(source=source, config_hash=digest(config), seed=seed, alpha=alpha,
                        selected_groups=[k for k, a in selection.items() if a == alpha],
                        relation_support=support, control_relation_support=csupport,
                        threshold=threshold.tolist(), control_threshold=cthreshold.tolist(), panels=panels,
                        features=x.shape[1], real_columns=WIDTH, parameters=int(model.coef.size + model.intercept.size),
                        development_unseen_train_values_per_slot=[int(sum(v not in seen[j] for v in values[split == 'development', j])) for j in range(4)],
                        artifacts=payloads)
                    base._put(path, bank)
                selected.append(bank); artifacts[key] = storage._pin(path)
                numeric.capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(cv) + len(selected)))
        result = dict(status='complete_exploratory', evaluation_role=FIT, source=source, config_hash=digest(config),
            backend=config['backend'], alias=config['alias'], width=config['width'], selected_groups=selection,
            cv_banks=len(cv), fits=selected, new_readout_fits=len(cv) + len(selected), new_model_queries=0,
            feature_inputs='pure declared features plus intercept; oracle annotations never enter design',
            controls='coherent family derangement; own labels/support/prevalence; real-target-selected alphas',
            generated_holdouts_opened=False)
        return common.receipt(config, source, result, artifacts)


def report(config):
    source = common.validate_role(config, REPORT); semantic.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
    lines = ['# All four values and direct relationships from one query state', '',
        'Adaptive discovery on the existing cohort. Archived prompts request one variable. '
        'This tests access to unrequested slots; it cannot rule out a global representation under an all-variable query. '
        'All alphas use TRAIN structural folds. Hidden features have no metadata or oracle pointers. '
        'Source is a shared character-hash baseline on the complete source including its print query.', '',
        '| Features | Width | Scalar slot exact | Scalar MAE | Scalar all four | Categorical slot exact | Categorical all four | Direct relation BA |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    inputs, cells, total, secondary = {}, [], 0, []
    for request in config['workers']:
        worker = base._json(request['path'], request['sha256']); common.completed(worker)
        pin = storage._pin(Path(worker['run_dir']) / 'results.json'); data = base._json(pin['path'], pin['sha256'])
        inputs[request['path']] = pin; total += data['new_readout_fits']
        rows, values, _ = load_inputs(worker)
        dev = np.asarray([r['split'] == 'development' for r in rows]); groups = np.asarray([r['component_id'] for r in rows])
        families = np.unique(groups[dev]); metrics = {k: {} for k in GROUPS}; panel = {k: {} for k in ('mae', 'scalar_all_four', 'categorical_all_four')}
        for bank in data['fits']:
            for kind in bank['selected_groups']:
                if bank['seed'] in metrics[kind]: raise ValueError('duplicate selected global group/seed')
                metrics[kind][bank['seed']] = bank['panels']['development']['real']['direct_relations' if kind == 'relations' else kind]
            with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
                if not np.array_equal(z['ids'], [r['id'] for r in rows]) or not np.array_equal(z['truth'], values):
                    raise ValueError('selected global score labels/order differ')
                real, shuffled = z['real'], z['shuffled']
                pred = predictions(real[dev])
            recomputed = score(real[dev], values[dev], groups[dev], bank['relation_support'], bank['threshold'],
                {k: v[dev] for k, v in annotation(rows).items()})
            if recomputed != bank['panels']['development']['real']:
                raise ValueError('saved global development metrics differ')
            for kind in bank['selected_groups']:
                if kind == 'relations': continue
                exact = (np.rint(pred[kind]) == values[dev]).all(axis=1)
                panel[kind + '_all_four'][bank['seed']] = np.asarray([exact[groups[dev] == g].mean() for g in families])
                if kind == 'scalar':
                    error = np.abs(pred[kind] - values[dev]).mean(axis=1)
                    panel['mae'][bank['seed']] = np.asarray([error[groups[dev] == g].mean() for g in families])
            secondary.append(dict(alias=worker['alias'], width=worker['width'], seed=bank['seed'],
                selected_groups=bank['selected_groups'], panels=bank['panels']['development']))
        for kind in ('scalar', 'categorical'):
            if sorted(metrics[kind]) != list(numeric.SEEDS): raise ValueError('complete global value fitting seeds required')
        avg = lambda k, m: float(np.mean([p[m] for p in metrics[k].values()]))
        ba = [m['type_macro_balanced_accuracy'] for m in metrics['relations'].values()]
        ba_text = f'{100*np.mean(ba):.2f}%' if len(ba) == 3 and all(v is not None for v in ba) else 'unsupported'
        lines.append(f"| {worker['alias']} | {worker['width']} | {100*avg('scalar','slot_macro_exact'):.2f}% | "
            f"{avg('scalar','slot_macro_mae'):.3f} | {100*avg('scalar','all_four_exact'):.2f}% | "
            f"{100*avg('categorical','slot_macro_exact'):.2f}% | {100*avg('categorical','all_four_exact'):.2f}% | {ba_text} |")
        cells.append(dict(alias=worker['alias'], backend=worker['backend'], width=worker['width'],
            families=families.tolist(), panels={k: np.stack([p[s] for s in numeric.SEEDS]) for k, p in panel.items()}))
    lines += ['', '## Direct versus externally derived relationships', '',
        'Each entry averages the three seeds. Derived rows use the separately TRAIN-selected value readout. '
        'BA is only shown where all four relation types are supported.', '',
        '| Features | Width | Direct real BA | Direct shuffled BA | Direct prior BA | Derived scalar BA | Derived categorical BA |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for cell in cells:
        subset = [p for p in secondary if p['alias'] == cell['alias'] and p['width'] == cell['width']]
        def relation_average(group, label, kind):
            values = [p['panels'][label][kind]['type_macro_balanced_accuracy'] for p in subset if group in p['selected_groups']]
            return f'{100*np.mean(values):.2f}%' if len(values) == 3 and all(v is not None for v in values) else 'unsupported'
        columns = [relation_average('relations', label, 'direct_relations') for label in ('real', 'control', 'prior')]
        columns += [relation_average(kind, 'real', 'derived_' + kind + '_relations') for kind in ('scalar', 'categorical')]
        lines.append(f"| {cell['alias']} | {cell['width']} | " + ' | '.join(columns) + ' |')
    contrasts = []
    lines += ['', '## Paired hidden minus matched-width source contrasts', '',
        'Seeds are averaged within structural families before 2,000 paired bootstrap replicates. '
        'These 95% intervals are descriptive and non-simultaneous on inspected DEV; negative MAE differences favor hidden features.', '',
        '| Features | Width | Metric | Difference | 95% interval |', '|---|---:|---|---:|---:|']
    for cell in cells:
        if cell['backend'] != 'hidden': continue
        matched = [c for c in cells if c['backend'] == 'source' and c['width'] == cell['width']]
        if len(matched) != 1 or matched[0]['families'] != cell['families']: raise ValueError('paired source families differ')
        for metric, values in cell['panels'].items():
            contrast = dict(alias=cell['alias'], width=cell['width'], metric=metric,
                **geometry.paired_family_interval(values, matched[0]['panels'][metric]))
            contrasts.append(contrast)
            lines.append(f"| {cell['alias']} | {cell['width']} | {metric} | {contrast['delta']:.4f} | [{contrast['lower']:.4f}, {contrast['upper']:.4f}] |")
    lines += ['', 'Direct relation scores are independent linear outputs, thresholded at weighted fitting prevalence. '
        'They are not calibrated probabilities. Equality/order/sum/difference types receive equal weight; each class recall '
        'gives equal weight to families containing that class. TRAIN-ineligible heads or evaluation heads lacking either class '
        'are explicitly unsupported. Relations computed externally from rounded scalar or categorical values are derived readouts, '
        'not additional evidence that the model decodes relations. The saved banks include all 48 cell supports, per-slot values, '
        'queried/unqueried and computed/untouched strata, coherent family-shuffled controls, and fitting-prior comparisons. '
        'Their alphas are selected using real TRAIN targets, so controls are not independently optimized null upper bounds. '
        'This is neither a novel-family confirmation nor a causal-use test. No new model calls or sealed-final access.', '']
    path = Path(config['report']); base._publish(path, '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', evaluation_role=REPORT, source=source, config_hash=digest(config),
        inputs=inputs, paired_family_contrasts=contrasts, new_readout_fits=total, new_model_queries=0,
        generated_holdouts_opened=False, literature=config['literature'])
    return common.receipt(config, source, result, dict(report=storage._pin(path)))
