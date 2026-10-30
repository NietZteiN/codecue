"""Train-only readouts of actual varied-schedule definition identities.

Oracle graphs, versions and schedules are labels only. Features are captured
hidden coordinates or signed character ngrams of the exact visible prefix.
The random-prefix control is a separate task, not a marginal-matched shuffle.
All held-out classes remain scored, including rare or unsupported TRAIN classes.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import time

import numpy as np

from . import relationship_capture as bounded
from . import overnight_relationship_capture as durable
from . import relationship_readouts as publication
from .datasets import digest
from .discovery_readouts import group_weights
from .weighted_ridge import fit as ridge_fit, from_parameters, _array_hash

ROLE = 'discovery_schedule_readouts_v1'
SITES = (3, 7, 8)
CAPTURE_SITE_IDS = (3, 7, 8)
FIXED_GRID_BANKS = 45
SEEDS = (17, 29, 43)
COMPLETION = 'completion_manifest_v1.json'
MAX_RESULT = 64 * 1024**2
SOURCE_ROWS = 2016
TRAIN_ROWS = 1320
DEV_ROWS = 696
TRAIN_GROUPS = 10
DEV_GROUPS = 5
COHORT_DESCRIPTION = '2,016 source cases; ten TRAIN and five DEV canonical graph families.'
COHORT_ERROR = 'ten TRAIN and five DEV disjoint graph families required'
PROTOCOL_INTERVAL = 'none; all five development graph outcomes retained'
SUMMARY_AGGREGATION = 'Mean of three weighting-seed point estimates; five dependent DEV graph families; no interval or reliability qualification.'
LIMITATIONS = [
    'Adaptive discovery on 15 canonical SSA graph families: ten TRAIN and five DEV; numeric, lexical and query relatives are dependent.',
    'All actual definition, parent and current-version identities are targets only. Hidden features contain no oracle source or target fields.',
    'The exact-prefix character baseline and training prior are retained; neither positive decoding nor a hidden-minus-surface difference proves natural causal use.',
    'Eligibility is descriptive TRAIN class support of at least three graph groups per observed class, distinct from historical behavioral qualification gates.',
    'Every categorical head and held-out class is scored, including rare, unsupported and constant classes; absent classes do not count as successful discrimination.',
    'Binary ridge scores use threshold 0.5 and categorical heads use argmax; scores are uncalibrated. No DEV threshold or hyperparameter selection occurs.',
    'Weight seeds change graph weights and random-prefix control labels, not independent experimental replications.',
    'Random-prefix controls preserve prefix consistency and visibility, not structural coherence, class marginals or task difficulty.',
    'Point estimates and per-graph outcomes are descriptive; no confirmatory or multiplicity-adjusted interval is claimed from five DEV families.',
    'Changing assignment schedules also changes variable age, positions and dependency depth. Decoding does not establish a causal version-tracking algorithm.',
]


def protocol():
    return dict(sites=list(SITES), seeds=list(SEEDS), alpha=100.,
                primary_train_class_group_minimum=3, binary_threshold=.5,
                source_features='signed character ngrams 3..8, matched hidden width',
                fitted_layers='all four captured layers; primary nominated before capture',
                categorical_decision='argmax across finite fitted class scores; lowest candidate breaks ties',
                control='deterministic prefix-keyed random labels, separately scored',
                interval=PROTOCOL_INTERVAL)


def _targets():
    from . import schedule_targets
    return schedule_targets


def _capture():
    from . import schedule_capture
    return schedule_capture


def _config(config):
    required = {'evaluation_role', 'capture_config', 'capture_config_sha256',
                'declared_plan', 'declared_plan_sha256', 'primary_layer', 'run_dir', 'report'}
    if (not isinstance(config, dict) or set(config) != required
            or config.get('evaluation_role') != ROLE):
        raise ValueError('exact discovery schedule readout configuration required')
    if len(publication._json_bytes(config)) > 16 * 1024:
        raise ValueError('bounded readout configuration required')
    for key in ('capture_config_sha256', 'declared_plan_sha256'):
        value = config[key]
        if (not isinstance(value, str) or len(value) != 64
                or any(c not in '0123456789abcdef' for c in value)):
            raise ValueError('explicit SHA256 input pins required')
    if type(config['primary_layer']) is not int or config['primary_layer'] < 0:
        raise ValueError('nominated primary layer required')
    for key in ('capture_config', 'declared_plan', 'run_dir', 'report'):
        if not isinstance(config[key], str) or not config[key]:
            raise ValueError('explicit safe discovery paths required')
        path = bounded._safe(config[key])
        if path.is_symlink(): raise ValueError('readout paths must not be symlinks')
    out, report = (Path(config[key]).resolve() for key in ('run_dir', 'report'))
    inputs = [Path(config[key]).resolve() for key in ('capture_config', 'declared_plan')]
    reserved = {out / name for name in ('registration.json', 'results_v1.json', 'audit.json',
                                       'summary.json', 'progress.json', 'attempts.json', COMPLETION,
                                       'parameter_replay_review_v1.json',
                                       'attempts_before_completion_recovery_v1.json')}
    if (report.suffix != '.md' or report == out or report in reserved or report in inputs
            or report in out.parents or (out.exists() and not out.is_dir())
            or (report.exists() and not report.is_file())
            or any(p in report.parents for p in reserved)
            or any(out in p.parents and p.suffix == '.npz' for p in report.parents)
            or any(report in p.parents or p in report.parents for p in inputs)
            or any(out == p or out in p.parents or p in out.parents for p in inputs)):
        raise ValueError('input, output and report paths must not overlap')
    return config


def _source(config, scheduled):
    _config(config)
    if scheduled:
        bounded._slurm()
        return bounded._current_source(config)
    registration = bounded._json(Path(config['run_dir']) / 'registration.json')
    if (registration.get('evaluation_role') != ROLE or registration.get('config') != config
            or registration.get('config_hash') != digest(config)):
        raise ValueError('original schedule readout registration differs')
    source = registration['fit_source']
    bounded._verify_source(config, source)
    return source


def _metadata(config, scheduled):
    source = _source(config, scheduled)
    if bounded._sha(config['declared_plan']) != config['declared_plan_sha256']:
        raise ValueError('declared schedule plan changed')
    cap_config = bounded._json(config['capture_config'], config['capture_config_sha256'])
    checked = _capture().completed_metadata(cap_config)
    records = [case['record'] for case in checked['cases']]
    shape = checked['feature_shape']
    if (len(records) != SOURCE_ROWS or shape != [SOURCE_ROWS, 3, 4, cap_config['hidden_size']]
            or checked['sites'] != ['statement:3', 'statement:7', 'pre_answer']
            or len(checked['layers']) != 4 or config['primary_layer'] not in checked['layers']
            or any(len(case['visible_prefixes']) != 3 for case in checked['cases'])):
        raise ValueError('complete schedule feature geometry required')
    groups = defaultdict(set)
    for row in records:
        if row.get('condition') != 'neutral' or row.get('split') not in ('train', 'development'):
            raise ValueError('neutral TRAIN/DEV schedule rows required')
        groups[row['template_id']].add(row['split'])
    if (any(len(v) != 1 for v in groups.values())
            or sum(v == {'train'} for v in groups.values()) != TRAIN_GROUPS
            or sum(v == {'development'} for v in groups.values()) != DEV_GROUPS):
        raise ValueError(COHORT_ERROR)
    capture_folder = Path(cap_config['run_dir']).resolve()
    out, report = (Path(config[key]).resolve() for key in ('run_dir', 'report'))
    data = Path(cap_config['dataset']).resolve()
    if (out == capture_folder or out in capture_folder.parents or capture_folder in out.parents
            or report == capture_folder or capture_folder in report.parents or report in capture_folder.parents
            or out == data or out in data.parents or data in out.parents
            or report == data or report in data.parents or data in report.parents):
        raise ValueError('readout outputs must not overlap capture or source data')
    return source, checked, records


def _bundles(records):
    target = _targets()
    bundles = {site: target.targets(records, site) for site in SITES}
    controls = {(site, seed): target.control_targets(records, site, seed)
                for site in SITES for seed in SEEDS}
    support = {site: target.training_support(bundle, min_class_groups=3)
               for site, bundle in bundles.items()}
    for (site, _), control in controls.items():
        if (control.case_ids != bundles[site].case_ids or control.columns != bundles[site].columns
                or not np.array_equal(control.mask, bundles[site].mask)):
            raise ValueError('random-prefix control schema/visibility differs')
    return bundles, controls, support


def preflight(config):
    source, checked, records = _metadata(config, scheduled=True)
    bundles, _, support = _bundles(records)
    return dict(status='passed', evaluation_role=ROLE, config_hash=digest(config),
                source=source, cases=SOURCE_ROWS, training_rows=TRAIN_ROWS, development_rows=DEV_ROWS,
                training_graph_groups=TRAIN_GROUPS, development_graph_groups=DEV_GROUPS,
                target_columns=len(bundles[7].columns), training_support=support,
                model=checked['model'], primary_layer=config['primary_layer'],
                raw_activation_arrays_loaded=False, new_model_queries=0,
                generated_holdouts_opened=False, protocol=protocol())


def _load(checked):
    features = np.empty(checked['feature_shape'], dtype=np.float32)
    first = 0
    for entry in checked['chunks']:
        if entry['first'] != first: raise ValueError('contiguous capture chunks required')
        count = entry['rows']
        values, _ = _capture().load_chunk(entry, checked['cases'][first:first+count], checked['config'])
        features[first:first+count] = values
        first += count
    if first != len(features) or not np.isfinite(features).all():
        raise ValueError('complete finite capture features required')
    return features


def _fit_inputs(x, y, mask, control, train, weights, case_ids):
    x, y, control = [np.asarray(v, dtype=np.float64) for v in (x, y, control)]
    mask, train, weights = np.asarray(mask), np.asarray(train), np.asarray(weights, dtype=np.float64)
    n = len(x)
    if (x.ndim != 2 or y.ndim != 2 or y.shape != control.shape or len(y) != n
            or mask.shape != y.shape or mask.dtype != np.bool_ or train.dtype != np.bool_
            or train.shape != (n,) or train.sum() < 2 or (~train).sum() < 1
            or weights.shape != (int(train.sum()),) or not np.isfinite(weights).all()
            or np.any(weights <= 0) or not np.isfinite(x).all()
            or not np.isfinite(y).all() or not np.isfinite(control).all()
            or len(case_ids) != n or len(set(case_ids)) != n
            or np.any(y[~mask] != 0) or np.any(control[~mask] != 0)):
        raise ValueError('finite masked targets, training-only positive weights and unique IDs required')
    return x, y, mask, control, train, weights


def _mask_groups(mask, train):
    groups = defaultdict(list)
    for column in range(mask.shape[1]):
        if mask[:, column].any():
            groups[mask[train, column].tobytes()].append(column)
    return [np.array(columns, dtype=np.int64) for _, columns in sorted(groups.items())]


def fit_masked_columns(x, y, mask, control, train, weights, case_ids):
    """Share a factorization only across columns with identical TRAIN visibility."""
    x, y, mask, control, train, weights = _fit_inputs(x, y, mask, control, train, weights, case_ids)
    scores, random_scores = [np.full(y.shape, np.nan) for _ in range(2)]
    fitted = []
    for columns in _mask_groups(mask, train):
        local = mask[train, columns[0]]
        indices = np.flatnonzero(train)[local]
        if len(indices) < 2:
            # No unsupported target gets invented labels or fitted DEV rows.
            continue
        joined = np.concatenate((y[indices][:, columns], control[indices][:, columns]), axis=1)
        model = ridge_fit(x[indices], joined, weights[local],
                          train_ids=[case_ids[i] for i in indices], split='train', alpha=100.)
        output = model.predict(x)
        scores[:, columns] = output[:, :len(columns)]
        random_scores[:, columns] = output[:, len(columns):]
        fitted.append((columns, indices, model))
    return fitted, scores, random_scores


def _identity(x, y, mask, control, train, weights, case_ids, config_hash):
    return dict(config_hash=config_hash, case_ids=list(case_ids),
                features_sha256=_array_hash(x), targets_sha256=_array_hash(y),
                mask_sha256=_array_hash(mask), control_sha256=_array_hash(control),
                train_mask_sha256=_array_hash(train), weights_sha256=_array_hash(weights))


def _fit_bank(path, x, bundle, control, train, weights, config_hash, allow_fit=True):
    x, y, mask, random_y, train, weights = _fit_inputs(
        x, bundle.y, bundle.mask, control.y, train, weights, bundle.case_ids)
    identity = _identity(x, y, mask, random_y, train, weights, bundle.case_ids, config_hash)
    path = bounded._safe(path)
    created = not path.exists()
    if created:
        if not allow_fit: raise ValueError('audit cannot create a missing fit bank')
        fitted, scores, random_scores = fit_masked_columns(
            x, y, mask, random_y, train, weights, bundle.case_ids)
        arrays = dict(identity=np.frombuffer(publication._json_bytes(identity), dtype=np.uint8),
                      scores=scores, random_scores=random_scores, model_count=np.array(len(fitted)))
        for index, (columns, rows, model) in enumerate(fitted):
            prefix = f'm{index}_'
            arrays[prefix+'columns'] = columns
            arrays[prefix+'rows'] = rows
            arrays[prefix+'metadata'] = np.frombuffer(publication._json_bytes(model.metadata), dtype=np.uint8)
            arrays.update({prefix+key: value for key, value in model.parameters.items()})
        stream = io.BytesIO()
        np.savez(stream, **arrays)
        publication.immutable(path, stream.getvalue())
    expected_groups = []
    for columns in _mask_groups(mask, train):
        rows = np.flatnonzero(train)[mask[train, columns[0]]]
        if len(rows) >= 2: expected_groups.append((columns, rows))
    with np.load(path, allow_pickle=False) as bank:
        if json.loads(bank['identity'].tobytes()) != identity:
            raise ValueError('saved schedule fit input identity differs')
        if int(bank['model_count']) != len(expected_groups):
            raise ValueError('saved masked factorization inventory differs')
        scores, random_scores = bank['scores'].copy(), bank['random_scores'].copy()
        if scores.shape != y.shape or random_scores.shape != y.shape:
            raise ValueError('saved score geometry differs')
        replay = np.full(y.shape, np.nan)
        random_replay = np.full(y.shape, np.nan)
        models = []
        for index, (columns, rows) in enumerate(expected_groups):
            prefix = f'm{index}_'
            if (not np.array_equal(bank[prefix+'columns'], columns)
                    or not np.array_equal(bank[prefix+'rows'], rows)):
                raise ValueError('saved target columns or TRAIN membership differs')
            metadata = json.loads(bank[prefix+'metadata'].tobytes())
            parameters = {name: bank[prefix+name] for name in
                          ('mean', 'scale', 'coef', 'intercept', 'weighted_feature_mean', 'weighted_target_mean')}
            model = from_parameters(metadata, parameters)
            joined = np.concatenate((y[rows][:, columns], random_y[rows][:, columns]), axis=1)
            wanted = dict(features=_array_hash(x[rows]), targets=_array_hash(joined),
                          sample_weight=_array_hash(weights[mask[train, columns[0]]]))
            if (metadata['training_input_sha256'] != wanted
                    or model.train_ids != tuple(bundle.case_ids[i] for i in rows)):
                raise ValueError('saved TRAIN-only input pins differ')
            predicted = model.predict(x)
            replay[:, columns] = predicted[:, :len(columns)]
            random_replay[:, columns] = predicted[:, len(columns):]
            models.append(dict(columns=columns.tolist(), training_rows=len(rows), metadata=metadata))
    if (not np.array_equal(scores, replay, equal_nan=True)
            or not np.array_equal(random_scores, random_replay, equal_nan=True)):
        raise ValueError('saved parameters fail exact full-row score replay')
    return scores, random_scores, models, created


def _train_support(bundle, train):
    groups = np.array(bundle.group_ids)
    columns, heads = [], defaultdict(list)
    for spec in bundle.columns:
        index = spec['index']; valid = train & bundle.mask[:, index]
        yes, no = valid & (bundle.y[:, index] == 1), valid & (bundle.y[:, index] == 0)
        positive, negative = len(set(groups[yes])), len(set(groups[no]))
        columns.append(dict(index=index, name=spec['name'], family=spec['family'],
                            training_rows=int(valid.sum()), positive_groups=positive,
                            negative_groups=negative,
                            binary_eligible=positive >= 3 and negative >= 3))
        if spec['kind'] == 'categorical': heads[spec['head']].append(index)
    categorical = {}
    for name, indices in heads.items():
        observed = [j for j in indices if np.any(train & bundle.mask[:, j] & (bundle.y[:, j] == 1))]
        dev = [j for j in indices if np.any(~train & bundle.mask[:, j] & (bundle.y[:, j] == 1))]
        categorical[name] = dict(
            family=bundle.columns[indices[0]]['family'],
            class_group_support={str(bundle.columns[j]['candidate']): columns[j]['positive_groups'] for j in indices},
            observed_train_classes=[bundle.columns[j]['candidate'] for j in observed],
            dev_only_classes=[bundle.columns[j]['candidate'] for j in dev if j not in observed],
            all_observed_train_classes_supported=bool(observed) and all(columns[j]['positive_groups'] >= 3 for j in observed),
            constant_training_task=len(observed) <= 1,
            constant_development_task=len(dev) <= 1)
    return dict(columns=columns, categorical_heads=categorical,
                minimum_class_graph_groups=3, support_selection_split='train')


def metrics(bundle, scores, train_support):
    """Score every defined DEV task; missing/unsupported predictions are wrong."""
    scores = np.asarray(scores, dtype=np.float64)
    if scores.shape != bundle.y.shape: raise ValueError('score/target shape differs')
    boolean, categorical, heads, row_correct = [], {}, defaultdict(list), {}
    groups = np.array(bundle.group_ids)
    for spec in bundle.columns:
        j = spec['index']
        if spec['kind'] == 'categorical':
            heads[spec['head']].append(j)
            continue
        valid = bundle.mask[:, j]
        truth = bundle.y[:, j] == 1
        predicted = scores[:, j] >= .5
        correct = np.isfinite(scores[:, j]) & (predicted == truth)
        yes, no = valid & truth, valid & ~truth
        bacc = .5 * (float(correct[yes].mean())+float(correct[no].mean())) if yes.any() and no.any() else None
        boolean.append(dict(index=j, name=spec['name'], family=spec['family'],
                            n=int(valid.sum()), positives=int(yes.sum()), negatives=int(no.sum()),
                            missing_predictions=int((valid & ~np.isfinite(scores[:, j])).sum()),
                            accuracy=float(correct[valid].mean()) if valid.any() else None,
                            balanced_accuracy=bacc, constant_evaluation_task=bool(valid.any() and not (yes.any() and no.any())),
                            training_eligible=train_support['columns'][j]['binary_eligible']))
        boolean[-1]['aggregation'] = 'Rows within each cell; no class-balanced score is assigned to a constant DEV task.'
    for name, indices in heads.items():
        chosen = sorted(indices, key=lambda j: bundle.columns[j]['candidate'])
        truth = bundle.y[:, chosen]
        valid = (truth.sum(axis=1) == 1) & bundle.mask[:, chosen].any(axis=1)
        # Only fitted scores determine prediction: masks never reveal a true slot/version.
        values = scores[:, chosen]
        finite = np.isfinite(values).any(axis=1)
        predicted = np.argmax(np.where(np.isfinite(values), values, -np.inf), axis=1)
        expected = np.argmax(truth, axis=1)
        correct = finite & (predicted == expected)
        family = bundle.columns[chosen[0]]['family']
        per_group = {name_: dict(n=int((valid & (groups == name_)).sum()),
                                 accuracy=float(correct[valid & (groups == name_)].mean()))
                     for name_ in sorted(set(groups[valid]))}
        by_class = {}
        for local, column in enumerate(chosen):
            selected = valid & (expected == local)
            by_class[str(bundle.columns[column]['candidate'])] = dict(
                n=int(selected.sum()), accuracy=float(correct[selected].mean()) if selected.any() else None)
        categorical[name] = dict(family=family, n=int(valid.sum()),
            accuracy=float(correct[valid].mean()) if valid.any() else None,
            group_macro_accuracy=float(np.mean([item['accuracy'] for item in per_group.values()])) if per_group else None,
            missing_predictions=int((valid & ~finite).sum()), classes=by_class,
            train_support=train_support['categorical_heads'][name], per_group=per_group)
        row_correct[name] = (family, valid, correct)
    families = {}
    for family in sorted({item['family'] for item in boolean}):
        cells = [item for item in boolean if item['family'] == family]
        eligible = [item for item in cells if item['training_eligible']]
        comparable = [item for item in eligible if item['balanced_accuracy'] is not None]
        families[family] = dict(total_columns=len(cells), evaluated_columns=sum(item['n'] > 0 for item in cells),
            train_eligible_columns=len(eligible), evaluable_two_class_columns=len(comparable),
            eligible_macro_balanced_accuracy=float(np.mean([v['balanced_accuracy'] for v in comparable])) if comparable and len(comparable) == len(eligible) else None,
            all_fixed_eligible_cells_evaluable=bool(eligible) and len(comparable) == len(eligible),
            aggregation='Macro over fixed TRAIN-eligible columns; each column uses row-weighted sensitivity/specificity.')
    whole = {}
    for family in sorted({value[0] for value in row_correct.values()}):
        selected = [v for v in row_correct.values() if v[0] == family]
        valid = np.logical_and.reduce([v[1] for v in selected])
        correct = np.logical_and.reduce([v[2] for v in selected])
        per_group = {g: dict(n=int((valid & (groups == g)).sum()),
                             accuracy=float(correct[valid & (groups == g)].mean()))
                     for g in sorted(set(groups[valid]))}
        whole[family] = dict(heads=len(selected), n=int(valid.sum()),
            accuracy=float(correct[valid].mean()) if valid.any() else None,
            group_macro_accuracy=float(np.mean([item['accuracy'] for item in per_group.values()])) if per_group else None,
            per_group=per_group)
    return dict(boolean_cells=boolean, categorical_heads=categorical,
                boolean_families=families, whole_categorical_families=whole)


def _prior(bundle, train, weights):
    scores = np.full(bundle.y.shape, np.nan)
    for column in range(bundle.y.shape[1]):
        valid = bundle.mask[train, column]
        if valid.any(): scores[:, column] = np.average(bundle.y[train, column][valid], weights=weights[valid])
    return scores


def _additional_predictions(bundle, train, weights):
    """Optional train-only comparator scores; the historical recipe adds none."""
    return {}


def _score_methods(bundle, control, train, weights, development, scores, random_scores,
                   *, eligibility=None, control_support=None):
    """One scoring path for fitted, prior, sham and optional train-only methods."""
    dev_bundle = _targets().subset(bundle, development)
    if eligibility is None: eligibility = _train_support(bundle, train)
    if control_support is None: control_support = _train_support(control, train)
    methods = dict(direct=metrics(dev_bundle, scores[development], eligibility),
        training_prior=metrics(dev_bundle, _prior(bundle, train, weights)[development], eligibility),
        random_prefix_control=metrics(_targets().subset(control, development),
            random_scores[development], control_support))
    extras = _additional_predictions(bundle, train, weights)
    if not isinstance(extras, dict): raise ValueError('named additional comparator score banks required')
    for name, values in extras.items():
        values = np.asarray(values, dtype=np.float64)
        if (not isinstance(name, str) or not name or name in methods
                or values.shape != bundle.y.shape or np.isinf(values).any()
                or not np.isfinite(values[bundle.mask]).all()):
            raise ValueError('additional comparator identity, geometry or finite defined scores differ')
        methods[name] = metrics(dev_bundle, values[development], eligibility)
    return methods


def _artifact(path):
    return dict(path=str(path), sha256=bounded._sha(path), bytes=Path(path).stat().st_size)


def _name(backend, layer, site, seed):
    return f'{backend}_layer{layer}_site{site}_seed{seed}'


def _control_metadata(control):
    """Keep changed-task semantics/marginals without copying all real prefix maps."""
    heavy = {'version_map_by_case', 'canonical_visible_prefixes', 'canonical_output_visible_prefixes'}
    return {key: value for key, value in control.descriptive.items() if key not in heavy}


def _features(checked, vectors, site_index, backend, layer):
    if backend == 'hidden': return vectors[:, site_index, checked['layers'].index(layer)]
    from sklearn.feature_extraction.text import HashingVectorizer
    return HashingVectorizer(analyzer='char', ngram_range=(3, 8),
        n_features=checked['feature_shape'][-1], alternate_sign=True, norm=None,
        dtype=np.float64).transform([case['visible_prefixes'][site_index] for case in checked['cases']]).toarray()


def run(config):
    from .confidence import _run_lock
    from threadpoolctl import threadpool_limits
    source, checked, records = _metadata(config, scheduled=True)
    bundles, controls, support = _bundles(records)
    train = np.array([r['split'] == 'train' for r in records])
    development = np.flatnonzero(~train)
    train_rows = [row for row, use in zip(records, train) if use]
    out = Path(config['run_dir']); out.mkdir(parents=True, exist_ok=True)
    with _run_lock(out):
        if (out / COMPLETION).exists():
            previous = completed_result(config)
            if previous['fit_source'] != source:
                raise ValueError('completed readouts belong to another frozen fit source')
            attempts_path = out / 'attempts.json'
            if attempts_path.exists():
                journal = durable._json(attempts_path)
                attempts = journal.get('attempts', [])
                if attempts and attempts[-1]['status'] == 'running':
                    publication.immutable(out / 'attempts_before_completion_recovery_v1.json',
                                          publication._json_bytes(journal))
                    attempts[-1].update(status='complete_from_verified_receipt',
                        worker_exit_status='unknown; artifact completion alone is verified',
                        recovery_utc=datetime.now(timezone.utc).isoformat(), completed_banks=FIXED_GRID_BANKS)
                    durable._journal(attempts_path, dict(evaluation_role=ROLE, attempts=attempts))
            durable._journal(out / 'progress.json', dict(status='complete', evaluation_role=ROLE,
                completed_banks=FIXED_GRID_BANKS, planned_banks=FIXED_GRID_BANKS, new_model_queries=0, generated_holdouts_opened=False))
            return previous
        if not (out / 'registration.json').exists() and any(out.glob('*.npz')):
            raise ValueError('orphan fit banks require original registration; choose another output')
        registration = dict(evaluation_role=ROLE, config=config, config_hash=digest(config),
            fit_source=source, capture_source=checked['source'], dataset_sha256=checked['dataset_sha256'],
            fixed_recipe=protocol(), limitations=LIMITATIONS, new_model_queries=0,
            generated_holdouts_opened=False)
        publication.immutable(out / 'registration.json', publication._json_bytes(registration))
        attempts_path = out / 'attempts.json'
        attempts = durable._json(attempts_path).get('attempts', []) if attempts_path.exists() else []
        if attempts and attempts[-1]['status'] == 'running':
            attempts[-1]['status'] = 'interrupted_before_completion'
        attempt = dict(status='running', slurm_job_id=os.environ.get('SLURM_JOB_ID'),
                       started_utc=datetime.now(timezone.utc).isoformat(),
                       existing_fit_banks=len(list(out.glob('*.npz'))))
        attempts.append(attempt)
        durable._journal(attempts_path, dict(evaluation_role=ROLE, attempts=attempts))
        started = time.monotonic(); fits = []; artifacts = {}; replay_rows = 0
        threads = int(os.environ.get('SLURM_CPUS_PER_TASK', '8'))
        if threads < 1: raise ValueError('positive allocated CPU count required')
        try:
            vectors = _load(checked)
            with threadpool_limits(limits=threads):
                for site in SITES:
                    site_index = CAPTURE_SITE_IDS.index(site)
                    bundle = bundles[site]
                    eligibility = _train_support(bundle, train)
                    control_supports = {seed: _train_support(controls[site, seed], train) for seed in SEEDS}
                    for backend, layer in [('hidden', layer) for layer in checked['layers']] + [('surface', -1)]:
                        x = _features(checked, vectors, site_index, backend, layer)
                        for seed in SEEDS:
                            control = controls[site, seed]
                            weights = group_weights(train_rows, seed).astype(np.float64)
                            name = _name(backend, layer, site, seed); path = out / (name+'.npz')
                            scores, random_scores, models, created = _fit_bank(
                                path, x, bundle, control, train, weights, digest(config))
                            control_support = control_supports[seed]
                            fit = dict(name=name, backend=backend, layer=layer, site=site, seed=seed,
                                artifact=str(path), factorizations=len(models),
                                fitted_columns=sum(len(model['columns']) for model in models),
                                metrics=_score_methods(bundle, control, train, weights, development, scores, random_scores,
                                    eligibility=eligibility, control_support=control_support),
                                exact_parameter_score_replay=True,
                                random_control_support=control_support)
                            fits.append(fit); artifacts[name] = _artifact(path)
                            replay_rows += len(records) * len(models)
                            durable._journal(out / 'progress.json', dict(status='running', evaluation_role=ROLE,
                                completed_banks=len(fits), planned_banks=FIXED_GRID_BANKS,
                                factorization_banks=sum(f['factorizations'] for f in fits),
                                new_model_queries=0, generated_holdouts_opened=False))
                            print(f'schedule readout {name} factorization_groups={len(models)} cached={not created}', flush=True)
                        del x
            result = dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=digest(config),
                fit_source=source, capture_source=checked['source'], model=checked['model'],
                dataset_sha256=checked['dataset_sha256'], cases=SOURCE_ROWS, training_rows=int(train.sum()),
                development_rows=len(development), training_groups=TRAIN_GROUPS, development_groups=DEV_GROUPS,
                target_columns=list(bundles[7].columns), protocol=protocol(),
                primary=dict(layer=config['primary_layer'], site=7,
                             tasks=['current_definition', 'current_version', 'copy_parent'],
                             scope='all fixed heads and classes retained; descriptive only'),
                training_support={str(site): support[site] for site in SITES},
                descriptive_target_metadata={str(site): bundles[site].descriptive for site in SITES},
                control_descriptive_metadata={str(site): {str(seed): _control_metadata(controls[site, seed])
                    for seed in SEEDS} for site in SITES},
                fit_banks=len(fits), factorizations=sum(f['factorizations'] for f in fits),
                parameter_replay_rows=replay_rows, fits=fits, limitations=LIMITATIONS,
                new_model_queries=0, generated_holdouts_opened=False,
                oracle_target_features=False, behavioral_response_features=False,
                runtime=dict(wall_seconds=time.monotonic()-started, threads=threads,
                             slurm_job_id=os.environ.get('SLURM_JOB_ID')))
            if len(fits) != FIXED_GRID_BANKS: raise ValueError('complete fixed bank grid required')
            result = _finish(config, result, artifacts)
        except BaseException as exc:
            attempt.update(status='failed', error=f'{type(exc).__name__}: {exc}',
                           completed_banks=len(fits), ended_utc=datetime.now(timezone.utc).isoformat())
            durable._journal(attempts_path, dict(evaluation_role=ROLE, attempts=attempts))
            raise
        attempt.update(status='complete', completed_banks=FIXED_GRID_BANKS,
                       ended_utc=datetime.now(timezone.utc).isoformat())
        durable._journal(attempts_path, dict(evaluation_role=ROLE, attempts=attempts))
        durable._journal(out / 'progress.json', dict(status='complete', evaluation_role=ROLE,
            completed_banks=FIXED_GRID_BANKS, planned_banks=FIXED_GRID_BANKS, new_model_queries=0, generated_holdouts_opened=False))
        return result


def _report(result):
    lines = ['# Varied-schedule definition and relationship decoding', '',
        f"{result['model']}: {COHORT_DESCRIPTION}", '',
        'All 45 fixed feature/site/seed banks completed exact saved-parameter score replay. All classes, rare TRAIN classes and constant DEV tasks remain reported.', '',
        '| Backend | Layer | Site | Seed | Whole current definitions | Whole current versions | Whole copy parents |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for fit in result['fits']:
        whole = fit['metrics']['direct']['whole_categorical_families']
        def value(family):
            point = whole.get(family, {}).get('accuracy')
            return 'undefined' if point is None else f'{100*point:.3f}%'
        lines.append(f"| {fit['backend']} | {fit['layer']} | {fit['site']} | {fit['seed']} | {value('current_definition')} | {value('current_version')} | {value('copy_parent')} |")
    lines += ['', 'The machine-readable result retains every boolean cell, categorical class, per-graph outcome, training prior, random-prefix control, and TRAIN-only support decision. Constant/unsupported classes are descriptive and never removed from whole-head evaluation.', '']
    lines += ['- '+message for message in LIMITATIONS]
    return '\n'.join(lines)+'\n'


def _summary(result):
    primary, primary_group_macro = {}, {}
    for backend in ('hidden', 'surface'):
        fits = [fit for fit in result['fits'] if fit['site'] == 7 and fit['backend'] == backend
                and (backend == 'surface' or fit['layer'] == result['primary']['layer'])]
        primary[backend] = {}
        primary_group_macro[backend] = {}
        for method in ('direct', 'training_prior', 'random_prefix_control'):
            primary[backend][method] = {}
            primary_group_macro[backend][method] = {}
            for family in ('current_definition', 'current_version', 'copy_parent'):
                points = [fit['metrics'][method]['whole_categorical_families'].get(family, {}).get('accuracy') for fit in fits]
                primary[backend][method][family] = float(np.mean(points)) if points and all(p is not None for p in points) else None
                group_points = [fit['metrics'][method]['whole_categorical_families'].get(family, {}).get('group_macro_accuracy') for fit in fits]
                primary_group_macro[backend][method][family] = float(np.mean(group_points)) if group_points and all(p is not None for p in group_points) else None
    return dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=result['config_hash'],
        cases=result['cases'], training_rows=result['training_rows'], development_rows=result['development_rows'],
        training_groups=TRAIN_GROUPS, development_groups=DEV_GROUPS, fit_banks=FIXED_GRID_BANKS, factorizations=result['factorizations'],
        parameter_replay_rows=result['parameter_replay_rows'], primary=primary,
        primary_group_macro=primary_group_macro,
        aggregation=SUMMARY_AGGREGATION,
        new_model_queries=0, generated_holdouts_opened=False, limitations=LIMITATIONS)


def _finish(config, result, artifacts):
    out = Path(config['run_dir']); path = out / 'results_v1.json'
    if path.exists():
        previous = _rich_json(path)
        if (publication._json_bytes({k: v for k, v in previous.items() if k != 'runtime'})
                != publication._json_bytes({k: v for k, v in result.items() if k != 'runtime'})):
            raise ValueError('existing immutable scientific result differs after bank replay')
        result = previous
    payload = publication._json_bytes(result)
    if len(payload) > MAX_RESULT: raise ValueError('bounded schedule scientific result required')
    publication.immutable(path, payload)
    publication.immutable(config['report'], _report(result).encode())
    audit_value = dict(status='passed', evaluation_role=ROLE, config_hash=digest(config),
        fit_banks=FIXED_GRID_BANKS, factorizations=result['factorizations'],
        parameter_replay_rows=result['parameter_replay_rows'], exact_parameter_score_replays=True,
        new_model_queries=0, generated_holdouts_opened=False)
    publication.immutable(out / 'audit.json', publication._json_bytes(audit_value))
    publication.immutable(out / 'summary.json', publication._json_bytes(_summary(result)))
    artifacts.update({name: _artifact(path_) for name, path_ in
                      [('registration', out/'registration.json'), ('results', path),
                       ('report', Path(config['report'])), ('audit', out/'audit.json'),
                       ('summary', out/'summary.json')]})
    receipt = dict(schema_version=1, status='complete_exploratory', evaluation_role=ROLE,
        config_hash=digest(config), fit_source=result['fit_source'], capture_source=result['capture_source'],
        fit_banks=FIXED_GRID_BANKS, factorizations=result['factorizations'],
        parameter_replay_rows=result['parameter_replay_rows'], artifacts=artifacts,
        new_model_queries=0, generated_holdouts_opened=False)
    publication.immutable(out / COMPLETION, publication._json_bytes(receipt))
    return result


def _rich_json(path):
    payload = bounded._bytes(path, MAX_RESULT)
    result = json.loads(payload)
    if not isinstance(result, dict): raise ValueError('result metadata object required')
    return result


def completed_result(config):
    source, checked, _ = _metadata(config, scheduled=False)
    out = Path(config['run_dir']); receipt = durable._json(out / COMPLETION)
    if (receipt.get('evaluation_role') != ROLE or receipt.get('status') != 'complete_exploratory'
            or receipt.get('schema_version') != 1 or receipt.get('config_hash') != digest(config)
            or receipt.get('fit_source') != source or receipt.get('capture_source') != checked['source']
            or receipt.get('fit_banks') != FIXED_GRID_BANKS or receipt.get('new_model_queries') != 0
            or receipt.get('generated_holdouts_opened') is not False):
        raise ValueError('complete matching schedule readout receipt required')
    expected = {_name(backend, layer, site, seed): out / (_name(backend, layer, site, seed)+'.npz')
                for site in SITES for backend, layer in [('hidden', l) for l in checked['layers']]+[('surface', -1)] for seed in SEEDS}
    expected.update(registration=out/'registration.json', results=out/'results_v1.json',
                    report=Path(config['report']), audit=out/'audit.json', summary=out/'summary.json')
    if set(receipt.get('artifacts', {})) != set(expected):
        raise ValueError('exact fit and metadata inventory required')
    for name, path in expected.items():
        if receipt['artifacts'][name] != _artifact(path):
            raise ValueError('immutable schedule artifact changed: '+name)
    registration = bounded._json(out/'registration.json')
    if (registration.get('fit_source') != source or registration.get('config') != config
            or registration.get('fixed_recipe') != protocol()):
        raise ValueError('frozen original schedule fit recipe differs')
    result = _rich_json(out/'results_v1.json')
    if (result.get('config_hash') != digest(config) or result.get('fit_source') != source
            or result.get('evaluation_role') != ROLE or result.get('status') != 'complete_exploratory'
            or result.get('capture_source') != checked['source'] or result.get('protocol') != protocol()
            or result.get('fit_banks') != FIXED_GRID_BANKS or len(result.get('fits', [])) != FIXED_GRID_BANKS
            or result.get('new_model_queries') != 0 or result.get('generated_holdouts_opened') is not False):
        raise ValueError('complete scientific result differs from receipt')
    fit_map = {fit['name']: fit['artifact'] for fit in result['fits']}
    if fit_map != {name: str(path) for name, path in expected.items() if path.suffix == '.npz'}:
        raise ValueError('scientific result fit inventory differs')
    return result


def audit(config):
    """Restore and replay every fitted parameter bank, with no fitting allowed."""
    from threadpoolctl import threadpool_limits
    result = completed_result(config)
    _, checked, records = _metadata(config, scheduled=False)
    bundles, controls, support = _bundles(records)
    train = np.array([r['split'] == 'train' for r in records])
    development = np.flatnonzero(~train)
    train_rows = [row for row, use in zip(records, train) if use]
    if (publication._json_bytes(result['training_support']) != publication._json_bytes({str(site): support[site] for site in SITES})
            or publication._json_bytes(result['control_descriptive_metadata']) != publication._json_bytes({
                str(site): {str(seed): _control_metadata(controls[site, seed]) for seed in SEEDS}
                for site in SITES})):
        raise ValueError('saved TRAIN support or control marginal metadata differs')
    saved_fits = {fit['name']: fit for fit in result['fits']}
    vectors = _load(checked); replay_rows = 0; factorizations = 0
    with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK', '8'))):
        for site in SITES:
            site_index = CAPTURE_SITE_IDS.index(site)
            bundle = bundles[site]
            eligibility = _train_support(bundle, train)
            control_supports = {seed: _train_support(controls[site, seed], train) for seed in SEEDS}
            for backend, layer in [('hidden', l) for l in checked['layers']]+[('surface', -1)]:
                x = _features(checked, vectors, site_index, backend, layer)
                for seed in SEEDS:
                    name = _name(backend, layer, site, seed)
                    weights = group_weights(train_rows, seed).astype(np.float64)
                    control = controls[site, seed]
                    scores, random_scores, models, created = _fit_bank(Path(config['run_dir'])/(name+'.npz'), x,
                        bundle, control, train, weights, digest(config), allow_fit=False)
                    if created: raise ValueError('audit unexpectedly fitted a bank')
                    control_support = control_supports[seed]
                    recalculated = _score_methods(bundle, control, train, weights, development, scores, random_scores,
                        eligibility=eligibility, control_support=control_support)
                    saved = saved_fits[name]
                    if (saved['metrics'] != recalculated or saved['random_control_support'] != control_support
                            or saved['factorizations'] != len(models)
                            or saved['fitted_columns'] != sum(len(model['columns']) for model in models)
                            or (saved['backend'], saved['layer'], saved['site'], saved['seed']) != (backend, layer, site, seed)):
                        raise ValueError('saved scientific metrics differ from independently replayed scores')
                    replay_rows += len(records)*len(models)
                    factorizations += len(models)
                del x
    if replay_rows != result['parameter_replay_rows'] or factorizations != result['factorizations']:
        raise ValueError('exact replay row accounting differs')
    if (bounded._json(Path(config['run_dir']) / 'summary.json') != _summary(result)
            or Path(config['report']).read_bytes() != _report(result).encode()):
        raise ValueError('published summary or report differs from recomputed scientific metrics')
    proof = dict(status='passed', evaluation_role=ROLE, config_hash=digest(config),
                fit_source=result['fit_source'], capture_source=result['capture_source'], fit_banks=FIXED_GRID_BANKS,
                factorizations=result['factorizations'], parameter_replay_rows=replay_rows,
                exact_saved_parameter_score_replays=True, all_real_and_control_scores_replayed=True,
                all_scientific_metrics_recomputed=True, train_support_and_control_marginals_recomputed=True,
                source_artifacts=durable._json(Path(config['run_dir']) / COMPLETION)['artifacts'],
                new_fits=0, new_model_queries=0, generated_holdouts_opened=False)
    path = Path(config['run_dir']) / 'parameter_replay_review_v1.json'
    publication.immutable(path, publication._json_bytes(proof))
    return {**proof, 'review': _artifact(path)}
