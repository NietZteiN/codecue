"""Role-conditioned numeric decoding and fixed global-state baselines.

Written values and read-time operands can share a physical token. Separate
feature blocks allow independent linear maps for these different questions.
"""
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_graph_readouts as graph
from . import arithmetic_local_capture as capture
from . import relationship_capture as base
from .datasets import digest
from .weighted_ridge import fit, from_parameters

ROLE = 'discovery_arithmetic_local_numeric_v1'
ALPHAS = (1., 100., 10000.)
FORMATS = ('regression', 'categorical')
ROLES = ('root_definition', 'computed_definition', 'left_use', 'right_use')


def examples(rows, cases):
    table = []
    for index, (row, case) in enumerate(zip(rows, cases)):
        for point, descriptor in enumerate(case['descriptors']):
            if descriptor['kind'] == 'answer':
                continue
            if descriptor['kind'] == 'definition':
                role = 'root_definition' if descriptor['statement'] < 4 else 'computed_definition'
                value, kind = descriptor['value'], role
            else:
                role = descriptor['side'] + '_use'
                parent = descriptor['parent']
                value = row['oracle']['writes'][parent]['value']
                kind = 'operand_from_root' if parent < 4 else 'operand_from_computed'
            if type(value) is not int or not -96 <= value <= 96:
                raise ValueError('declared integer target domain required')
            table.append(dict(row=index, point=point, statement=descriptor['statement'], role=role,
                value=value, target_kind=kind, group=row['component_id'], split=row['split'],
                stratum=row['family_stratum'], case_id=row['id'], depth=row['depth']))
    return table


def features(nodes, table):
    output = np.zeros((len(table), 4 * 64 + 16), np.float32)
    for i, e in enumerate(table):
        role = ROLES.index(e['role'])
        output[i, role * 64:(role + 1) * 64] = nodes[e['row'], e['point']]
        output[i, 256 + e['statement']] = 1
        output[i, 266 + role] = 1
        output[i, -1] = e['depth'] / 6
    return output


def labels(values):
    values = np.asarray(values)
    if not np.issubdtype(values.dtype, np.integer) or np.any(np.abs(values) > 96):
        raise ValueError('bounded exact integer numeric labels required')
    return np.concatenate((values[:, None].astype(float), np.eye(193)[values + 96]), axis=1)


def decode(scores, kind):
    if kind == 'regression':
        return scores[:, 0]
    if kind == 'categorical':
        return scores[:, 1:194].argmax(axis=1) - 96
    raise ValueError('declared numeric decoding format required')


def metrics(prediction, table):
    truth = np.asarray([e['value'] for e in table])
    if prediction.shape != truth.shape or not np.isfinite(prediction).all():
        raise ValueError('finite aligned numeric predictions required')
    groups = np.asarray([e['group'] for e in table])
    error = np.abs(prediction - truth)
    correct = np.rint(prediction) == truth
    result = dict(family_macro_mae=common.group_mean(error, groups)[0],
        family_macro_exact_accuracy=common.group_mean(correct, groups)[0],
        mae=float(error.mean()), exact_accuracy=float(correct.mean()), per_kind={})
    for kind in sorted({e['target_kind'] for e in table}):
        mask = np.asarray([e['target_kind'] == kind for e in table])
        result['per_kind'][kind] = dict(family_macro_mae=common.group_mean(error[mask], groups[mask])[0],
            family_macro_exact_accuracy=common.group_mean(correct[mask], groups[mask])[0],
            cases=int(mask.sum()), family_metrics=common.group_mean(error[mask], groups[mask])[1])
    return result


def prior(values, table, train, weights, kind):
    output = np.empty(len(table), float)
    train_roles = np.asarray([e['role'] for e, yes in zip(table, train) if yes])
    for role in ROLES:
        mask = train_roles == role
        if not mask.any():
            raise ValueError('every numeric role needs TRAIN support')
        observed = values[train][mask]
        predicted = np.average(observed, weights=weights[mask]) if kind == 'regression' else np.bincount(
            observed + 96, weights=weights[mask], minlength=193).argmax() - 96
        output[np.asarray([e['role'] == role for e in table])] = predicted
    return output


def choose(records, representations):
    grouped = defaultdict(dict)
    for bank in records:
        for cell in bank['candidates']:
            key = (bank['representation'], cell['alpha'], cell['format'])
            point = (bank['fold'], bank['seed'])
            if point in grouped[key]:
                raise ValueError('duplicate numeric CV observation')
            grouped[key][point] = -cell['metrics']['per_kind']['computed_definition']['family_macro_mae']
    expected = {(r, a, f) for r in representations for a in ALPHAS for f in FORMATS}
    observations = {(f, s) for f in range(3) for s in common.SEEDS}
    if set(grouped) != expected or any(set(v) != observations for v in grouped.values()):
        raise ValueError('complete numeric layer/alpha/format grouped CV grid required')
    result = {}
    for backend in ('hidden', 'source'):
        result[backend] = {}
        for kind in FORMATS:
            candidates = [(float(np.mean(list(v.values()))), alpha, representation)
                for (representation, alpha, f), v in grouped.items() if f == kind and representation.startswith(backend)]
            score, alpha, representation = max(candidates)
            result[backend][kind] = dict(representation=representation, alpha=alpha, format=kind, selection_score=score)
    return result


def _save_model(folder, key, model):
    metadata, parameters = folder / (key + '_metadata.json'), folder / (key + '_parameters.npz')
    base._put(metadata, model.metadata)
    graph._npz(parameters, **model.parameters)
    with np.load(parameters, allow_pickle=False) as data:
        replay = from_parameters(base._json(metadata), {k: data[k] for k in data.files})
    return replay, dict(metadata=graph._pin(metadata), parameters=graph._pin(parameters))


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, ROLE)
    audit_config, cache, profile, rows, cases = common.inputs(config)
    folder = Path(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return common.completed(config)
        table = examples(rows, cases)
        values = np.asarray([e['value'] for e in table])
        target = labels(values)
        donor = common.donors(rows)
        lookup = {(e['row'], e['point']): i for i, e in enumerate(table)}
        control = np.asarray([lookup[(int(donor[e['row']]), e['point'])] for e in table])
        train = np.asarray([e['split'] == 'train' for e in table])
        dev = np.asarray([e['split'] == 'development' for e in table])
        calibration = np.asarray([e['split'] == 'calibration' for e in table])
        train_table = common.mask_table(table, train)
        fold_ids = common.folds(train_table)
        ids = np.asarray([e['case_id'] + ':point' + str(e['point']) for e in table])
        representations = ['hidden_layer_' + str(layer) for layer in profile['layers']] + ['source_char']
        surface = audit.cache_array(cache, 'source')
        records, artifacts, fits = [], {}, []
        for seed in common.SEEDS:
            hidden = audit.cache_array(cache, 'hidden_seed' + str(seed))
            for representation in representations:
                layer = None if representation == 'source_char' else profile['layers'].index(int(representation.rsplit('_', 1)[1]))
                x = features(surface if layer is None else hidden[:, :, layer], table)[train]
                for fold in range(3):
                    key = f'cv_{representation}_fold{fold}_seed{seed}'
                    path = folder / (key + '.json')
                    if path.exists():
                        record = base._json(path)
                        if record['source'] != source or record['config_hash'] != digest(config):
                            raise ValueError('numeric CV resume identity differs')
                    else:
                        fit_mask, valid = fold_ids != fold, fold_ids == fold
                        fit_table = common.mask_table(train_table, fit_mask)
                        validation_table = common.mask_table(train_table, valid)
                        candidates = []
                        for alpha in ALPHAS:
                            model = fit(x[fit_mask], target[train][fit_mask], common.weights(fit_table, seed),
                                train_ids=ids[train][fit_mask].tolist(), split='train', alpha=alpha)
                            predicted = model.predict(x[valid])
                            for kind in FORMATS:
                                candidates.append(dict(alpha=alpha, format=kind, metrics=metrics(decode(predicted, kind), validation_table)))
                        record = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                            representation=representation, fold=fold, seed=seed, candidates=candidates,
                            fit_groups=sorted({e['group'] for e in fit_table}), validation_groups=sorted({e['group'] for e in validation_table}))
                        base._put(path, record)
                        print(key, flush=True)
                    records.append(record)
                    artifacts[key] = graph._pin(path)
                    capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records), planned=63))
        selected = choose(records, representations)
        base._put(folder / 'selection_review_v1.json', dict(status='selection_locked', source=source,
            config_hash=digest(config), choices=selected, selection_split='TRAIN only',
            objective='family-macro computed-definition MAE', tie_break='larger alpha then lexicographically larger representation'))
        artifacts['selection'] = graph._pin(folder / 'selection_review_v1.json')
        joined = np.concatenate((target[train], target[control[train]]), axis=1)
        fitted = {}
        for seed in common.SEEDS:
            hidden = audit.cache_array(cache, 'hidden_seed' + str(seed))
            for backend, choices in selected.items():
                for kind, choice in choices.items():
                    key = f'selected_{backend}_{kind}_seed{seed}'
                    path = folder / (key + '.json')
                    if path.exists():
                        result = base._json(path)
                        if result['source'] != source or result['config_hash'] != digest(config):
                            raise ValueError('numeric selected resume identity differs')
                        for entry in result['artifacts'].values():
                            if base._sha(entry['path']) != entry['sha256']:
                                raise ValueError('numeric selected payload changed')
                    else:
                        representation = choice['representation']
                        layer = None if backend == 'source' else profile['layers'].index(int(representation.rsplit('_', 1)[1]))
                        x = features(surface if layer is None else hidden[:, :, layer], table)
                        fit_key = (seed, representation, choice['alpha'])
                        if fit_key in fitted:
                            stored = dict(fitted[fit_key])
                            with np.load(stored['parameters']['path'], allow_pickle=False) as data:
                                replay = from_parameters(base._json(stored['metadata']['path']), {k: data[k] for k in data.files})
                            scores = replay.predict(x)
                            reused_fit = True
                        else:
                            model = fit(x[train], joined, common.weights(train_table, seed), train_ids=ids[train].tolist(), split='train', alpha=choice['alpha'])
                            replay, stored = _save_model(folder, key, model)
                            scores = model.predict(x)
                            if not np.array_equal(scores, replay.predict(x)):
                                raise ValueError('saved numeric model replay differs')
                            reused_fit = False
                        real, shuffled = np.split(scores, 2, axis=1)
                        predicted, shuffled_values = decode(real, kind), decode(shuffled, kind)
                        score_path = folder / (key + '_scores.npz')
                        graph._npz(score_path, predicted=predicted, shuffled=shuffled_values, truth=values,
                            shuffle_truth=values[control], row_indices=np.asarray([e['row'] for e in table]),
                            point_indices=np.asarray([e['point'] for e in table]), ids=ids)
                        stored['scores'] = graph._pin(score_path)
                        shuffled_table = [dict(e, value=int(values[control[i]])) for i, e in enumerate(table)]
                        baseline = prior(values, table, train, common.weights(train_table, seed), kind)
                        result = dict(status='complete_exploratory', source=source, config_hash=digest(config), backend=backend,
                            format=kind, seed=seed, choice=choice, train=metrics(predicted[train], train_table),
                            training_fit_reused=reused_fit,
                            development=metrics(predicted[dev], common.mask_table(table, dev)),
                            calibration=metrics(predicted[calibration], common.mask_table(table, calibration)),
                            development_prior=metrics(baseline[dev], common.mask_table(table, dev)),
                            development_control=metrics(shuffled_values[dev], common.mask_table(shuffled_table, dev)), artifacts=stored)
                        base._put(path, result)
                        print(key, flush=True)
                    fits.append(result)
                    fitted[(seed, choice['representation'], choice['alpha'])] = {
                        k: v for k, v in result['artifacts'].items() if k in ('metadata', 'parameters')}
                    artifacts[key] = graph._pin(path)
                    capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records) + len(fits), planned=63))
        # A fixed global baseline provides four values and direct relation heads
        # on the same new cohort. All variable heads are independent linear maps.
        global_fits = []
        global_target = np.concatenate((np.asarray([r['oracle']['values'] for r in rows]),
            graph.relations(np.asarray([r['oracle']['values'] for r in rows])).astype(float)), axis=1)
        row_train = np.asarray([r['split'] == 'train' for r in rows])
        row_dev = np.asarray([r['split'] == 'development' for r in rows])
        row_table = [dict(group=r['component_id']) for r in rows if r['split'] == 'train']
        global_joined = np.concatenate((global_target[row_train], global_target[donor[row_train]]), axis=1)
        for seed in common.SEEDS:
            hidden = audit.cache_array(cache, 'hidden_seed' + str(seed))
            layer = profile['layers'].index(cache['nominated_layer'])
            for backend in ('hidden', 'source'):
                key = f'global_{backend}_seed{seed}'
                path = folder / (key + '.json')
                if path.exists():
                    result = base._json(path)
                    if result['source'] != source or result['config_hash'] != digest(config):
                        raise ValueError('global numeric resume identity differs')
                    for entry in result['artifacts'].values():
                        if base._sha(entry['path']) != entry['sha256']:
                            raise ValueError('global numeric payload changed')
                else:
                    nodes = surface if backend == 'source' else hidden[:, :, layer]
                    x = np.asarray([nodes[i, case['point_count'] - 1] for i, case in enumerate(cases)])
                    model = fit(x[row_train], global_joined, common.weights(row_table, seed),
                        train_ids=[r['id'] for r in rows if r['split'] == 'train'], split='train', alpha=100.)
                    replay, stored = _save_model(folder, key, model)
                    scores = model.predict(x)
                    if not np.array_equal(scores, replay.predict(x)):
                        raise ValueError('global numeric replay differs')
                    score_path = folder / (key + '_scores.npz')
                    graph._npz(score_path, real=scores[:, :52], shuffled=scores[:, 52:], truth=global_target,
                        prior=np.broadcast_to(model.weighted_target_mean[:52], global_target.shape),
                        ids=np.asarray([r['id'] for r in rows]), donor=donor, development=row_dev)
                    stored['scores'] = graph._pin(score_path)
                    result = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                        backend=backend, seed=seed, alpha=100., layer=cache['nominated_layer'], artifacts=stored)
                    base._put(path, result)
                global_fits.append(result)
                artifacts[key] = graph._pin(path)
                capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records) + len(fits) + len(global_fits), planned=63))
        result = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=digest(config),
            model=profile['model'], choices=selected, fits=fits, global_fits=global_fits, new_model_queries=0,
            generated_holdouts_opened=False, limitations='Adaptive discovery. Role-conditioned linear numeric maps, fixed64-wide '
                'projections per layer, TRAIN-only computed-definition MAE selection. Source interpreter ceiling remains100%. '
                'Global alpha100 is a fixed baseline rather than a tuned capacity comparison. No causal or confirmation claim.')
        return common.receipt(config, source, result, artifacts)
