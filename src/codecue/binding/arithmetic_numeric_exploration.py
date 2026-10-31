"""Role-specific compression/encoding discovery on archived arithmetic states."""
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_local_capture as capture
from . import arithmetic_local_probes as local
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest
from .weighted_ridge import fit, from_parameters

PREPARE = 'discovery_numeric_exploration_cache_v1'
FIT = 'discovery_numeric_exploration_fit_v1'
REPORT = 'discovery_numeric_exploration_report_v1'
SEEDS = (11, 29, 47)
ALPHAS = (1., 100., 10000.)
ROLES = ('root_definition', 'computed_definition')
HEADS = (('scalar', 1), ('categorical', 193), ('sign', 3), ('magnitude', 3),
         ('units', 10), ('tens', 10), ('parity', 2), ('mod5', 5), ('mod10', 10))
FORMATS = tuple(name for name, _ in HEADS) + ('digits_joint',)
HEAD_WIDTH = sum(width for _, width in HEADS)


def slices():
    result, cursor = {}, 0
    for name, width in HEADS:
        result[name] = slice(cursor, cursor + width)
        cursor += width
    return result


def class_labels(values):
    values = np.asarray(values)
    if values.ndim != 1 or not np.issubdtype(values.dtype, np.integer) or np.any(np.abs(values) > 96):
        raise ValueError('bounded integer numeric targets required')
    magnitude = np.abs(values)
    return dict(categorical=values + 96, sign=np.sign(values) + 1,
        magnitude=np.where(magnitude == 0, 0, np.where(magnitude < 10, 1, 2)),
        units=magnitude % 10, tens=magnitude // 10, parity=values % 2,
        mod5=values % 5, mod10=values % 10)


def targets(values):
    labels = class_labels(values)
    return np.concatenate([np.asarray(values)[:, None].astype(float)] +
        [np.eye(width)[labels[name]] for name, width in HEADS if name != 'scalar'], axis=1)


def predictions(scores):
    scores = np.asarray(scores)
    if scores.ndim != 2 or scores.shape[1] != HEAD_WIDTH or not np.isfinite(scores).all():
        raise ValueError('finite declared numeric head layout required')
    bands = slices()
    output = {name: scores[:, band].argmax(axis=1) for name, band in bands.items() if name != 'scalar'}
    output['scalar'] = scores[:, 0]
    magnitude = output['tens'] * 10 + output['units']
    sign = output['sign'] - 1
    output['digits_joint'] = magnitude * sign
    output['digits_valid'] = ((magnitude == 0) & (sign == 0) | (magnitude > 0) & (sign != 0)) & (magnitude <= 96)
    return output


def score_heads(scores, values, groups):
    predicted, actual = predictions(scores), class_labels(values)
    _, family_inverse, family_counts = np.unique(groups, return_inverse=True, return_counts=True)
    if not len(family_counts):
        raise ValueError('nonempty evaluation families required')
    def family_mean(value):
        return float(np.mean(np.bincount(family_inverse, weights=np.asarray(value, float)) / family_counts))
    result = {}
    for name in FORMATS:
        if name in ('scalar', 'digits_joint', 'categorical'):
            value = predicted[name] - 96 if name == 'categorical' else predicted[name]
            correct = np.rint(value) == values
            if name == 'digits_joint':
                correct &= predicted['digits_valid']
            result[name] = dict(exact=family_mean(correct), mae=family_mean(np.abs(value - values)))
            if name == 'categorical':
                classes, counts = np.unique(values, return_counts=True)
                result[name]['support'] = {str(int(c)): int(n) for c, n in zip(classes, counts)}
            if name == 'digits_joint':
                result[name]['invalid'] = float((~predicted['digits_valid']).mean())
        else:
            truth, guess = actual[name], predicted[name]
            classes, counts = np.unique(truth, return_counts=True)
            recalls = [float((guess[truth == label] == label).mean()) for label in classes]
            result[name] = dict(exact=family_mean(guess == truth),
                balanced_accuracy=float(np.mean(recalls)), support={str(int(c)): int(n) for c, n in zip(classes, counts)})
    return result


def selection_loss(panel, name):
    # Whole numeric values use MAE for scalar and valid exact reconstruction
    # for categorical/digits. Component heads use macro recall on supported
    # classes; every alpha sees the same validation class support.
    return panel[name]['mae'] if name == 'scalar' else -panel[name]['exact'] if name in ('categorical', 'digits_joint') else -panel[name]['balanced_accuracy']


def select(records):
    grid = {(r['seed'], r['fold'], r['alpha']) for r in records}
    expected = {(s, f, a) for s in SEEDS for f in range(3) for a in ALPHAS}
    if len(records) != len(expected) or grid != expected:
        raise ValueError('complete three-fold three-seed alpha grid required')
    return {name: min(ALPHAS, key=lambda a: (np.mean([selection_loss(r['validation'], name) for r in records if r['alpha'] == a]), -a)) for name in FORMATS}


def nested_projection(width, seed):
    if width < 1024:
        raise ValueError('archived model width must exceed projection widths')
    signs = np.empty((width, 1024), np.float32)
    signs[:, :64] = local.projection(width, seed) * 8
    signs[:, 64:] = np.random.default_rng(seed + 2000).integers(0, 2, (width, 960)) * 2 - 1
    return signs / 32


def fold_source(values, width):
    if values.ndim != 2 or values.shape[1] % width:
        raise ValueError('power-of-two source widths must divide shared hash width')
    return np.asarray(values).reshape(len(values), -1, width).sum(axis=1, dtype=np.float32)


def examples(rows, cases):
    table = []
    for i, (row, case) in enumerate(zip(rows, cases)):
        for point, d in enumerate(case['descriptors']):
            if d['kind'] != 'definition':
                continue
            table.append(dict(row=i, point=point, statement=d['statement'], value=d['value'],
                role=ROLES[int(d['statement'] >= 4)], group=row['component_id'], split=row['split'],
                stratum=row['family_stratum'], depth=row['depth'], case_id=row['id']))
    return table


def metadata_features(table):
    x = np.zeros((len(table), 12), np.float32)
    for i, e in enumerate(table):
        x[i, e['statement']] = 1
        x[i, 10] = e['depth'] / 6
        x[i, 11] = e['statement'] / 10
    return x


def controls(rows, table):
    donor = common.donors(rows)
    lookup = {(e['row'], e['statement']): i for i, e in enumerate(table)}
    return np.asarray([lookup[(int(donor[e['row']]), e['statement'])] for e in table])


def load_features(entry):
    if base._sha(entry['path']) != entry['sha256']:
        raise ValueError('cached numeric features changed')
    x = np.load(entry['path'], mmap_mode='r', allow_pickle=False)
    if list(x.shape) != entry['shape'] or x.dtype != np.float32:
        raise ValueError('cached feature shape/dtype differs')
    return x


def prepare(config):
    from .confidence import _run_lock
    source = common.validate_role(config, PREPARE)
    audit_config, cache, profile, rows, cases = audit.load_cache(config)
    table = examples(rows, cases)
    folder = Path(config['run_dir']); folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return common.completed(config)
        matrices, artifacts = {}, {}
        width = 8192 if config['backend'] == 'source' else profile['hidden_size']
        specifications = {'raw': width} if config['backend'] == 'hidden' else {'source': width}
        if config['backend'] == 'hidden':
            specifications.update({f'projected_seed{s}': 1024 for s in SEEDS})
        for key, dimension in specifications.items():
            matrices[key] = np.lib.format.open_memmap(folder / (key + '.pending.npy'), mode='w+', dtype=np.float32, shape=(len(table), dimension))
        if config['backend'] == 'hidden':
            cap = base._json(audit_config['capture_config'], audit_config['capture_config_sha256'])
            proof = base._json(Path(cap['run_dir']) / 'completion_manifest_v1.json')
            manifest = base._json(Path(cap['run_dir']) / 'summary.json', proof['artifacts']['summary']['sha256'])
            if manifest['cases'] != len(cases) or [c['first'] for c in manifest['chunks']] != list(range(0, len(cases), cap['chunk_size'])):
                raise ValueError('complete ordered archived chunk coverage required')
            transforms = {s: nested_projection(width, s) for s in SEEDS}
            layer = profile['layers'].index(cache['nominated_layer'])
            coordinates = defaultdict(list)
            for j, e in enumerate(table):
                coordinates[e['row']].append((j, e['point']))
            for chunk in manifest['chunks']:
                first, count = chunk['first'], chunk['rows']
                if count != min(cap['chunk_size'], len(cases) - first):
                    raise ValueError('archived chunk row coverage differs')
                values = capture.load_chunk(chunk, cases[first:first + count], profile)
                selected = [(j, r - first, p) for r in range(first, first + count) for j, p in coordinates[r]]
                output, indices, points = map(np.asarray, zip(*selected))
                raw = values[indices, points, layer]
                matrices['raw'][output] = raw
                for seed in SEEDS:
                    matrices[f'projected_seed{seed}'][output] = raw @ transforms[seed]
                capture.legacy._CORE._journal(folder / 'progress.json', dict(captured_rows=first + count))
        else:
            from sklearn.feature_extraction.text import HashingVectorizer
            hasher = HashingVectorizer(analyzer='char', ngram_range=(3, 5), n_features=width, norm=None, alternate_sign=True)
            for start in range(0, len(table), 256):
                part = table[start:start + 256]
                texts = [rows[e['row']]['source'][:cases[e['row']]['descriptors'][e['point']]['stop']] for e in part]
                matrices['source'][start:start + len(part)] = hasher.transform(texts).toarray().astype(np.float32)
                capture.legacy._CORE._journal(folder / 'progress.json', dict(captured_rows=start + len(part)))
        for key, values in matrices.items():
            if not np.isfinite(values).all():
                raise ValueError('nonfinite cached features')
            values.flush()
            pending, path = folder / (key + '.pending.npy'), folder / (key + '.npy')
            pending.replace(path)
            artifacts[key] = dict(storage._pin(path), shape=list(values.shape))
        result = dict(status='complete_exploratory', evaluation_role=PREPARE, source=source,
            config_hash=digest(config), table_sha256=digest(table), width=width, features=artifacts,
            backend=config['backend'], nominated_layer=cache['nominated_layer'] if config['backend'] == 'hidden' else None,
            row_count=len(rows), examples=len(table), new_model_queries=0, new_fits=0)
        return common.receipt(config, source, result, artifacts)


def save_model(folder, key, model):
    path = folder / (key + '_parameters.npz')
    storage._npz(path, **model.parameters)
    metadata = folder / (key + '_metadata.json')
    base._put(metadata, model.metadata)
    with np.load(path, allow_pickle=False) as arrays:
        replay = from_parameters(base._json(metadata), {k: arrays[k] for k in arrays.files})
    return replay, dict(parameters=storage._pin(path), metadata=storage._pin(metadata))


def resume(path, config, source):
    if not path.exists():
        return None
    result = base._json(path)
    if result['source'] != source or result['config_hash'] != digest(config):
        raise ValueError('resumed numeric bank source/config differs')
    for entry in result['artifacts'].values():
        if base._sha(entry['path']) != entry['sha256']:
            raise ValueError('resumed bank payload changed')
    return result


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, FIT)
    _, _, profile, rows, cases = audit.load_cache(config)
    table = examples(rows, cases)
    cache_config = base._json(config['cache_config']['path'], config['cache_config']['sha256'])
    common.completed(cache_config)
    cache = base._json(Path(cache_config['run_dir']) / 'results.json')
    if cache['table_sha256'] != digest(table):
        raise ValueError('cached numeric example identities differ')
    mask = np.asarray([e['role'] == config['role'] for e in table])
    subset = common.mask_table(table, mask)
    train = np.asarray([e['split'] == 'train' for e in subset])
    splits = np.asarray([e['split'] for e in subset])
    groups = np.asarray([e['group'] for e in subset])
    values = np.asarray([e['value'] for e in table])
    control = values[controls(rows, table)][mask]
    values = values[mask]
    y = targets(values)
    randomized = targets(control)
    folds = common.folds(common.mask_table(subset, train))
    ids = np.asarray([e['case_id'] + ':definition:' + str(e['statement']) for e in subset])
    extra = metadata_features(subset)
    folder = Path(config['run_dir']); folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return common.completed(config)
        records, fits, artifacts, loaded = [], [], {}, {}
        def get_matrix(key):
            if key not in loaded:
                loaded[key] = load_features(cache['features'][key])
            return loaded[key]
        for width in config['widths']:
            cv = []
            for seed in SEEDS:
                key = 'source' if config['backend'] == 'source' else 'raw' if width == cache['width'] else f'projected_seed{seed}'
                matrix = get_matrix(key)
                if config['backend'] == 'source':
                    features = fold_source(matrix[mask], width)
                elif width == cache['width']:
                    features = np.asarray(matrix[mask])
                else:
                    features = np.asarray(matrix[mask, :width]) * np.sqrt(1024 / width)
                x = np.concatenate((features, extra), axis=1)
                weight = common.weights(common.mask_table(subset, train), seed)
                train_indices = np.flatnonzero(train)
                for fold in range(3):
                    fit_indices, validation = train_indices[folds != fold], train_indices[folds == fold]
                    for alpha in ALPHAS:
                        name = f'width{width}_cv_seed{seed}_fold{fold}_alpha{int(alpha)}'
                        path = folder / (name + '.json')
                        record = resume(path, config, source)
                        if record is None:
                            w = weight[folds != fold]; w = w / w.mean()
                            model = fit(x[fit_indices], y[fit_indices], w, ids[fit_indices].tolist(), 'train', alpha)
                            predicted = model.predict(x[validation])
                            replay, payloads = save_model(folder, name, model)
                            if not np.array_equal(predicted, replay.predict(x[validation])):
                                raise ValueError('CV save/reload scores differ')
                            record = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                                width=width, seed=seed, fold=fold, alpha=alpha,
                                fit_groups=sorted(set(groups[fit_indices])), validation_groups=sorted(set(groups[validation])),
                                validation=score_heads(predicted, values[validation], groups[validation]), artifacts=payloads)
                            base._put(path, record)
                        cv.append(record); records.append(record); artifacts[name] = storage._pin(path)
                        capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records) + len(fits)))
                # Only CV uses x here. Selected refits follow after all seeds.
            selected = select(cv)
            selection_path = folder / f'width{width}_selection_review_v1.json'
            selection = dict(status='selection_locked', source=source, config_hash=digest(config), width=width,
                encodings=selected, split='TRAIN grouped folds only', tie_break='larger alpha')
            if selection_path.exists() and base._json(selection_path) != selection:
                raise ValueError('locked TRAIN selection changed')
            if not selection_path.exists(): base._put(selection_path, selection)
            artifacts[f'selection_width{width}'] = storage._pin(selection_path)
            for seed in SEEDS:
                key = 'source' if config['backend'] == 'source' else 'raw' if width == cache['width'] else f'projected_seed{seed}'
                matrix = get_matrix(key)
                features = fold_source(matrix[mask], width) if config['backend'] == 'source' else np.asarray(matrix[mask]) if width == cache['width'] else np.asarray(matrix[mask, :width]) * np.sqrt(1024 / width)
                x = np.concatenate((features, extra), axis=1)
                weight = common.weights(common.mask_table(subset, train), seed)
                for alpha in sorted(set(selected.values())):
                    name = f'width{width}_selected_seed{seed}_alpha{int(alpha)}'
                    path = folder / (name + '.json')
                    bank = resume(path, config, source)
                    if bank is None:
                        model = fit(x[train], np.concatenate((y[train], randomized[train]), axis=1), weight, ids[train].tolist(), 'train', alpha)
                        predicted = model.predict(x)
                        replay, payloads = save_model(folder, name, model)
                        if not np.array_equal(predicted, replay.predict(x)):
                            raise ValueError('selected save/reload scores differ')
                        real, shuffled = np.split(predicted, 2, axis=1)
                        score_path = folder / (name + '_scores.npz')
                        storage._npz(score_path, real=real, shuffled=shuffled, truth=values, control_truth=control, ids=ids, split=splits)
                        payloads['scores'] = storage._pin(score_path)
                        panels = {}
                        for label in ('train', 'development', 'calibration'):
                            m = splits == label
                            panels[label] = dict(real=score_heads(real[m], values[m], groups[m]),
                                control=score_heads(shuffled[m], control[m], groups[m]),
                                prior=score_heads(np.broadcast_to(model.weighted_target_mean[:HEAD_WIDTH], (int(m.sum()), HEAD_WIDTH)), values[m], groups[m]))
                        strata = {}
                        seen = np.asarray([e['value'] in {w['value'] for w in rows[e['row']]['oracle']['writes'][:4]} for e in subset])
                        depth = np.asarray([e['depth'] for e in subset])
                        unseen = ~np.isin(values, np.unique(values[train]))
                        for label, m in {'matches_initial_literal': seen, 'absent_from_initial_literals': ~seen,
                                'unseen_train_value': unseen, **{f'depth{d}': depth == d for d in (2, 4, 6)}}.items():
                            m = m & (splits == 'development')
                            strata[label] = dict(observations=int(m.sum()), real=score_heads(real[m], values[m], groups[m])) if m.any() else dict(observations=0)
                        bank = dict(status='complete_exploratory', source=source, config_hash=digest(config), width=width,
                            seed=seed, alpha=alpha, selected_formats=[k for k, v in selected.items() if v == alpha],
                            train=panels['train'], development=panels['development'], calibration=panels['calibration'],
                            parameters=int(model.coef.size + model.intercept.size), features=x.shape[1], artifacts=payloads)
                        bank['development_strata'] = strata
                        bank['parameters_per_encoding'] = {k: (x.shape[1] + 1) * (23 if k == 'digits_joint' else dict(HEADS)[k]) for k in FORMATS}
                        base._put(path, bank)
                    fits.append(bank); artifacts[name] = storage._pin(path)
                    capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records) + len(fits)))
        result = dict(status='complete_exploratory', evaluation_role=FIT, source=source, config_hash=digest(config),
            model=profile['model'] if config['backend'] == 'hidden' else 'shared model-independent source comparator',
            backend=config['backend'], role=config['role'], widths=config['widths'], fits=fits,
            cv_banks=len(records), new_readout_fits=len(records) + len(fits), new_model_queries=0,
            generated_holdouts_opened=False, limitations='Adaptive discovery at a fixed layer/site. Role-specific assay differs from prior shared-role fits. '
                'More features increase capacity; source/prior/coherent-family controls and parameter counts are explicit. '
                'Component scores are not full numeric-state recovery or causal-use evidence.')
        return common.receipt(config, source, result, artifacts)


def report(config):
    source = common.validate_role(config, REPORT)
    if (Path(config['run_dir']) / 'completion_manifest_v1.json').exists():
        return common.completed(config)
    text = ['# Compression and numeric-encoding discovery', '',
        'Fixed-layer, role-specific probes on archived captures. Hyperparameters selected only inside structural TRAIN folds. Existing DEV remains adaptive discovery. Source comparator fits are shared across checkpoints at matching widths. No new language-model calls.', '',
        '| Model/features | Role | Width | Encoding | DEV exact | DEV MAE | Component balanced accuracy | Shuffled exact | Prior exact |',
        '|---|---|---:|---|---:|---:|---:|---:|---:|']
    inputs = {}
    for item in config['workers']:
        worker = base._json(item['path'], item['sha256']); common.completed(worker)
        entry = storage._pin(Path(worker['run_dir']) / 'results.json'); inputs[item['path']] = entry
        data = base._json(entry['path'], entry['sha256'])
        for width in data['widths']:
            for encoding in FORMATS:
                banks = [b for b in data['fits'] if b['width'] == width and encoding in b['selected_formats']]
                if sorted(b['seed'] for b in banks) != list(SEEDS):
                    raise ValueError('report needs exactly three selected seeds per panel')
                avg = lambda panel, metric: float(np.mean([b['development'][panel][encoding][metric] for b in banks]))
                mae = f"{avg('real', 'mae'):.3f}" if 'mae' in banks[0]['development']['real'][encoding] else 'n.a.'
                balanced = f"{100 * avg('real', 'balanced_accuracy'):.2f}%" if 'balanced_accuracy' in banks[0]['development']['real'][encoding] else 'n.a.'
                text.append(f"| {data['model']} | {data['role']} | {width} | {encoding} | {100 * avg('real', 'exact'):.2f}% | {mae} | {balanced} | {100 * avg('control', 'exact'):.2f}% | {100 * avg('prior', 'exact'):.2f}% |")
    text += ['', 'Scalar exact accuracy rounds to the nearest integer. Categorical and signed-digit reconstruction retain exact/MAE; invalid signed-digit configurations count as incorrect. Component class support, invalid rates, seeds, alpha choices and decoder parameter counts are retained in machine-readable banks. Calibration never enters fitting. A successful readout may recover source-accessible information or learn a calculation; this study alone does not identify natural causal computation.', '']
    path = Path(config['report']); base._publish(path, '\n'.join(text).encode())
    result = dict(status='complete_exploratory', evaluation_role=REPORT, source=source, config_hash=digest(config), inputs=inputs, new_fits=0, new_model_queries=0)
    return common.receipt(config, source, result, dict(report=storage._pin(path)))
