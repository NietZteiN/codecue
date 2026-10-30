"""Declared discovery-only projection, rank and naming-alignment sensitivity.

This is a new descriptive fitting contract on an already consumed capture bank.
Pooled-condition training PCA and within-condition fits are explicitly separate
from the earlier neutral-training-only readouts. No checkpoint is loaded here.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import time

import numpy as np

from .datasets import digest
from .discovery_readouts import CLASSES
from .probe_sensitivities import fit_alignment, fit_reduced_rank_ridge
from .published_benchmarks import immutable
from .registry import code_identity

ROLE = 'discovery_representation_sensitivity_v1'
CONDITIONS = ('neutral', 'informative', 'misleading')
SITES = ('pre_query_state', 'pre_answer')
RANKS = (1, 2, 4, 8, 16, 32, 64)
CONTROL_SEEDS = (11, 29, 47)
PCA = {'components': 64, 'algorithm': 'randomized_svd', 'n_iter': 5, 'seed': 17}
MAX_JSON_BYTES = 8 * 1024**2
LIMITATION = (
    'Adaptive discovery sensitivity on already consumed structures, not final '
    'confirmation or a causal mechanism. A common 64-dimensional training PCA '
    'projection is fitted separately at each fixed site and feature backend, '
    'using all three naming conditions equally. This changes the earlier '
    'neutral-only fitting contract explicitly. Within-condition ceilings and '
    'retained variance describe projection loss; failure in this projection '
    'cannot reject harmless change elsewhere in the 4096-dimensional space. '
    'Train-only orthogonal alignment has full anchor rank in the projected '
    'space but is a fitted descriptive map, not a causal correspondence. '
    'Both canonical current and saved targets are always predicted together. '
    'Linear class scores are not calibrated probabilities. Frequency-matched '
    'shuffles preserve labels but do not equate all task complexity. Three '
    'shuffle seeds are controls, not independent replications. The pre_answer '
    'site precedes the later formatting-space correction and is not the actual '
    'digit boundary used by subsequent interventions. No ownership-control '
    'capture exists in this bank, so these results cannot isolate owner coding '
    'from value recovery or show natural use.'
)


def _safe(path):
    from .experiment_log import _protected_outcome
    path = Path(path)
    if _protected_outcome(path) or _protected_outcome(path.resolve()):
        raise ValueError('reserved/final outcome paths are excluded')
    return path


def _sha(path):
    path = _safe(path)
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024**2), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def _json(path, expected=None):
    path = _safe(path)
    if path.suffix != '.json' or path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError('bounded JSON metadata required before payload access')
    if expected is not None and _sha(path) != expected:
        raise ValueError('pinned metadata checksum changed: '+str(path))
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError('metadata object required')
    return value


def _validate(config):
    if not isinstance(config, dict) or config.get('evaluation_role') != ROLE:
        raise ValueError('explicit discovery representation-sensitivity role required')
    required = {'evaluation_role', 'capture_config', 'capture_config_sha256',
        'capture_audit_sha256', 'capture_manifest_sha256', 'run_dir', 'report'}
    fixed = {'layer': 24, 'sites': list(SITES), 'pca': PCA, 'ranks': list(RANKS),
        'alpha': 100., 'control_seeds': list(CONTROL_SEEDS),
        'class_values': CLASSES.tolist(), 'conditions': list(CONDITIONS)}
    if required-set(config) or set(config)-required-set(fixed):
        raise ValueError('missing or unknown scientific configuration fields')
    for name, value in fixed.items():
        if name in config and config[name] != value:
            raise ValueError('fixed discovery recipe differs: '+name)
    for name in ('capture_config_sha256', 'capture_audit_sha256', 'capture_manifest_sha256'):
        if not isinstance(config[name], str) or len(config[name]) != 64 or any(c not in '0123456789abcdef' for c in config[name]):
            raise ValueError('explicit SHA256 metadata pins required')
    for name in ('capture_config', 'run_dir', 'report'):
        if not isinstance(config[name], str) or not config[name]:
            raise ValueError('explicit path required: '+name)
        _safe(config[name])
    return fixed


def preflight(config):
    """Validate the declared recipe and complete discovery metadata, no arrays."""
    fixed = _validate(config)
    capture = _json(config['capture_config'], config['capture_config_sha256'])
    if (capture.get('model') != 'meta-llama/Llama-3.1-8B-Instruct'
            or capture.get('layers') != [8, 16, 24, 31]
            or capture.get('sites') != ['pre_query_state', 'after_query', 'pre_answer']
            or capture.get('hidden_size') != 4096):
        raise ValueError('fixed audited Llama discovery capture geometry required')
    for name in ('dataset', 'capture_cases', 'preflight_result', 'run_dir'):
        _safe(capture[name])
    folder = _safe(Path(capture['run_dir'])/'activations')
    manifest = _json(folder/'manifest.json', config['capture_manifest_sha256'])
    audit = _json(folder/'audit.json', config['capture_audit_sha256'])
    identity = manifest.get('identity', {})
    if (manifest.get('status') != 'complete' or audit.get('status') != 'passed'
            or identity.get('config') != capture or manifest.get('identity_hash') != digest(identity)
            or audit.get('identity_hash') != manifest.get('identity_hash')
            or audit.get('generated_holdouts_opened') is not False
            or audit.get('cases') != 9216 or not audit.get('chunk_checksums')):
        raise ValueError('complete pinned discovery capture and audit required')
    if any(str(capture.get('evaluation_role', '')).lower().find(word) >= 0 for word in ('final', 'confirmatory')):
        raise ValueError('capture role is not eligible for discovery fitting')
    from .experiment_log import _sealed
    if _sealed(identity.get('dataset_manifest') or {}) or _sealed(capture):
        raise ValueError('sealed capture metadata is excluded')
    for name, checksum in audit['chunk_checksums'].items():
        path = _safe(name)
        if path.resolve().parent != (folder/'chunks').resolve() or path.suffix != '.npz' or not path.is_file():
            raise ValueError('audited capture chunks must stay in the pinned folder')
        if not isinstance(checksum, str) or len(checksum) != 64:
            raise ValueError('every capture chunk requires a checksum')
    qa = _json(capture['preflight_result'])
    if (qa != audit.get('preflight') or qa.get('status') != 'passed'
            or qa.get('config_hash') != digest(capture)
            or qa.get('source_sha256') != identity.get('code', {}).get('source_sha256')):
        raise ValueError('capture preflight source/identity differs')
    return {'status': 'passed', 'evaluation_role': ROLE, 'fixed_recipe': fixed,
        'capture_identity': manifest['identity_hash'], 'cases': audit['cases'],
        'chunks': len(audit['chunk_checksums']), 'arrays_read': False,
        'generated_holdouts_opened': False, 'model_loading': False,
        'new_fitting_contract': 'Pooled-condition TRAIN-only PCA and separate within-condition TRAIN fits; neutral-trained unaligned/aligned transfer.',
        'limitation': LIMITATION}


def _row_checks(rows):
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('unique complete capture row IDs required')
    groups = {}; bases = {}; conditions = Counter()
    for row in rows:
        if row['split'] not in ('train', 'development') or row['condition'] not in CONDITIONS:
            raise ValueError('only declared discovery split/condition rows are eligible')
        if (len(row['targets']) != 2 or any(type(v) is not int or v not in CLASSES for v in row['targets'])
                or row['query_role'] not in ('current', 'saved')):
            raise ValueError('complete fixed-domain current/saved targets required')
        template, base = row['template_id'], row['base_id']
        if template in groups and groups[template] != row['split']:
            raise ValueError('train/development structural groups overlap')
        groups[template] = row['split']
        identity = (row['split'], template, tuple(row['targets']))
        if base in bases and bases[base] != identity:
            raise ValueError('numeric-base relatives disagree on split/group/targets')
        bases[base] = identity
        conditions[row['split'], row['condition']] += 1
    if any(len({conditions[s, c] for c in CONDITIONS}) != 1 or not conditions[s, 'neutral'] for s in ('train', 'development')):
        raise ValueError('balanced complete naming conditions required in each split')
    return {'split_condition_counts': {s: {c: conditions[s, c] for c in CONDITIONS} for s in ('train', 'development')},
        'structural_groups': {s: sum(v == s for v in groups.values()) for s in ('train', 'development')},
        'numeric_bases': {s: sum(v[0] == s for v in bases.values()) for s in ('train', 'development')}}


def _load(config):
    preflight(config)  # All metadata/role guards precede any NPZ read.
    capture = _json(config['capture_config'], config['capture_config_sha256'])
    folder = Path(capture['run_dir'])/'activations'
    manifest = _json(folder/'manifest.json', config['capture_manifest_sha256'])
    audit = _json(folder/'audit.json', config['capture_audit_sha256'])
    from .state_capture import inputs, validate_chunk
    _, cases = inputs(capture, manifest['identity']['code']['source_sha256'])
    if len(cases) != audit['cases']:
        raise ValueError('prepared capture case coverage differs')
    # Validate split/target declarations before activation payloads are read.
    declared = []
    for item in cases:
        row = item['case']['record']
        declared.append({k: row[k] for k in ('id', 'base_id', 'template_id', 'split', 'condition', 'query_role')})
        declared[-1]['targets'] = item['targets']
    coverage = _row_checks(declared)
    if coverage['structural_groups'] != {'train': 18, 'development': 6}:
        raise ValueError('fixed discovery structural-group inventory differs')
    chunks = []; rows = []
    layer = capture['layers'].index(24)
    sites = [capture['sites'].index(site) for site in SITES]
    for name, checksum in sorted(audit['chunk_checksums'].items()):
        if _sha(name) != checksum:
            raise ValueError('audited capture chunk changed before array loading')
        with np.load(_safe(name), allow_pickle=False) as saved:
            vectors = saved['features']
            part = json.loads(saved['metadata'].tobytes())
            validate_chunk(capture, cases[len(rows):len(rows)+len(part)], vectors, part)
            chunks.append(vectors[:, layer, sites, :].copy())
            rows.extend(part)
    if len(rows) != audit['cases'] or [r['id'] for r in rows] != [r['id'] for r in declared]:
        raise ValueError('capture chunk IDs/order/coverage differ')
    _row_checks(rows)
    return np.concatenate(chunks), rows, capture, coverage


def site_indices(rows, site):
    """Deduplicate causal pre-query twins; preserve both query choices later."""
    if site not in SITES:
        raise ValueError('fixed site required')
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[row['state_prefix_sha256']].append(i)
    if any(len(v) != 2 or {rows[i]['query_role'] for i in v} != {'current', 'saved'}
           or rows[v[0]]['targets'] != rows[v[1]]['targets'] for v in groups.values()):
        raise ValueError('exact two-query causal-prefix relatives required')
    if site == 'pre_answer':
        return np.arange(len(rows), dtype=int)
    return np.array([min(v, key=lambda i: rows[i]['query_role']) for _, v in sorted(groups.items())], dtype=int)


def semantic_pairs(rows, condition, split='train'):
    """Exact same-program same-query anchors; no pairing from outcome labels."""
    if condition not in CONDITIONS or split not in ('train', 'development'):
        raise ValueError('declared pairing condition/split required')
    fields = ('base_id', 'lexical_realization', 'available_bindings', 'updates', 'tail_placement', 'query_role')
    grouped = defaultdict(dict)
    for i, row in enumerate(rows):
        if row['split'] != split:
            continue
        key = tuple(row[field] for field in fields)
        if row['condition'] in grouped[key]:
            raise ValueError('duplicate semantic relative in one naming condition')
        grouped[key][row['condition']] = i
    if not grouped or any(set(v) != set(CONDITIONS) for v in grouped.values()):
        raise ValueError('complete exact naming relatives required')
    source = []; neutral = []; identities = []
    for key, members in sorted(grouped.items()):
        selected = [rows[i] for i in members.values()]
        if len({(r['template_id'], tuple(r['targets'])) for r in selected}) != 1:
            raise ValueError('semantic anchor targets/groups differ')
        source.append(members[condition]); neutral.append(members['neutral'])
        identities.append(digest(list(key)))
    return np.array(source), np.array(neutral), identities


def complete_targets(rows, labels=None):
    lookup = {int(value): i for i, value in enumerate(CLASSES)}
    if labels is None:
        try:
            labels = np.array([[lookup[value] for value in row['targets']] for row in rows], dtype=int)
        except (KeyError, TypeError) as exc:
            raise ValueError('fixed-domain complete slot targets required') from exc
    labels = np.asarray(labels)
    if labels.shape != (len(rows), 2) or labels.dtype.kind not in 'iu' or (labels < 0).any() or (labels >= len(CLASSES)).any():
        raise ValueError('two complete class-index target columns required')
    onehot = np.concatenate([np.eye(len(CLASSES))[labels[:, slot]] for slot in range(2)], axis=1)
    return labels, onehot


def fit_projection(x, rows, *, components=64):
    from sklearn.utils.extmath import randomized_svd
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 2 or len(x) != len(rows) or not np.isfinite(x).all():
        raise ValueError('finite full row-aligned feature matrix required')
    train = np.array([r['split'] == 'train' for r in rows])
    selected = x[train]
    counts = Counter(r['condition'] for r, keep in zip(rows, train) if keep)
    if set(counts) != set(CONDITIONS) or len(set(counts.values())) != 1:
        raise ValueError('pooled training PCA must weight all naming conditions equally')
    if type(components) is not int or components < 1 or min(selected.shape[0]-1, selected.shape[1]) < components:
        raise ValueError('training PCA dimension is underidentified')
    mean = selected.mean(axis=0); centered = selected-mean
    _, singular, vt = randomized_svd(centered, n_components=components,
        n_iter=PCA['n_iter'], random_state=PCA['seed'], flip_sign=True)
    tol = singular[0]*max(centered.shape)*np.finfo(np.float64).eps
    if singular[-1] <= tol:
        raise ValueError('training PCA retained subspace is rank deficient')
    projected = (x-mean) @ vt.T
    total = float(np.sum(centered**2))
    metadata = {'algorithm': PCA['algorithm'], 'n_iter': PCA['n_iter'], 'seed': PCA['seed'],
        'components': components, 'fit_split': 'train', 'n_train': int(train.sum()),
        'training_ids': [r['id'] for r, keep in zip(rows, train) if keep],
        'training_ids_sha256': digest([r['id'] for r, keep in zip(rows, train) if keep]),
        'condition_counts': dict(counts), 'retained_variance_fraction': float(np.sum(singular**2)/total),
        'training_total_centered_sum_squares': total, 'singular_values': singular.tolist(),
        'heldout_rows_used_for_fit': 0, 'feature_standardization_before_PCA': False}
    return projected, {'mean': mean, 'components': vt, 'singular_values': singular}, metadata


def align_conditions(projected, rows, provenance):
    """Fit only training anchors and transform every held-out row unchanged."""
    projected = np.asarray(projected)
    aligned = projected.copy(); models = {}; metadata = {}
    for condition in CONDITIONS[1:]:
        source, target, identities = semantic_pairs(rows, condition, 'train')
        model = fit_alignment(projected[source], projected[target], source_ids=identities,
            target_ids=identities, split='train', provenance=provenance,
            config={'condition': condition, 'target_condition': 'neutral', 'space': 'common_training_PCA'})
        if model.metadata['anchor_cross_rank'] != projected.shape[1]:
            raise ValueError('projected alignment is underidentified by training anchors')
        mask = np.array([r['condition'] == condition for r in rows])
        aligned[mask] = model.transform(projected[mask], ids=[r['id'] for r, keep in zip(rows, mask) if keep])
        details = model.metadata
        details.update(source_training_case_ids=[rows[i]['id'] for i in source],
            neutral_training_case_ids=[rows[i]['id'] for i in target])
        # Pairwise development geometry is descriptive only; no map is fitted.
        dev_source, dev_target, _ = semantic_pairs(rows, condition, 'development')
        details['development_unaligned_mean_squared_distance'] = float(np.mean((projected[dev_source]-projected[dev_target])**2))
        details['development_aligned_mean_squared_distance'] = float(np.mean((aligned[dev_source]-projected[dev_target])**2))
        models[condition] = model; metadata[condition] = details
    return aligned, models, metadata


def _score(scores):
    return np.asarray(scores).reshape(len(scores), 2, len(CLASSES)).argmax(axis=2)


def cell_metrics(scores, labels, rows, mask, *, majority):
    mask = np.asarray(mask, dtype=bool)
    if not mask.any():
        raise ValueError('complete nonempty evaluation cell required')
    predicted = _score(scores); correct = predicted == labels
    targets = complete_targets(rows, labels)[1]
    raw_error = ((scores-targets)**2).reshape(len(rows), 2, len(CLASSES))
    templates = []
    for name in sorted({r['template_id'] for r, keep in zip(rows, mask) if keep}):
        tm = mask & np.array([r['template_id'] == name for r in rows])
        templates.append({'template_id': name, 'n': int(tm.sum()),
            'current_correct': int(correct[tm, 0].sum()), 'saved_correct': int(correct[tm, 1].sum()),
            'joint_correct': int(correct[tm].all(axis=1).sum())})
    return {'n': int(mask.sum()), 'structural_groups': len(templates),
        'current_accuracy': float(correct[mask, 0].mean()),
        'saved_accuracy': float(correct[mask, 1].mean()), 'joint_accuracy': float(correct[mask].all(axis=1).mean()),
        'current_score_mse': float(raw_error[mask, 0].mean()), 'saved_score_mse': float(raw_error[mask, 1].mean()),
        'current_training_majority_accuracy': float((labels[mask, 0] == majority[0]).mean()),
        'saved_training_majority_accuracy': float((labels[mask, 1] == majority[1]).mean()),
        'template_cells': templates}


def paired_group_comparisons(raw, aligned, labels, rows, *, draws=2000, seed=117):
    """Conditional descriptive resampling of whole development components."""
    raw = np.asarray(raw); aligned = np.asarray(aligned); labels = np.asarray(labels)
    if raw.shape != labels.shape or aligned.shape != labels.shape or labels.shape != (len(rows), 2):
        raise ValueError('paired complete current/saved predictions required')
    before = raw == labels; after = aligned == labels
    output = []
    for condition in CONDITIONS[1:]:
        names = sorted({r['template_id'] for r in rows if r['split'] == 'development' and r['condition'] == condition})
        if len(names) < 2:
            raise ValueError('multiple development components required for group resampling')
        for endpoint, left, right in [('current_accuracy', before[:, 0], after[:, 0]),
                ('saved_accuracy', before[:, 1], after[:, 1]),
                ('joint_accuracy', before.all(axis=1), after.all(axis=1))]:
            values = []; sizes = []
            for name in names:
                mask = np.array([r['split'] == 'development' and r['condition'] == condition and r['template_id'] == name for r in rows])
                values.append(float((right[mask].astype(float)-left[mask]).mean())); sizes.append(int(mask.sum()))
            values = np.array(values)
            sampled = np.random.default_rng(seed).integers(0, len(values), size=(draws, len(values)))
            distribution = values[sampled].mean(axis=1)
            output.append({'condition': condition, 'endpoint': endpoint, 'rank': 64,
                'contrast': 'neutral_decoder_aligned_minus_unaligned', 'mean_group_increment': float(values.mean()),
                'conditional_group_bootstrap_95': np.quantile(distribution, [.025, .975]).tolist(),
                'resampling_unit': 'template_id', 'structural_groups': len(names), 'n': sum(sizes),
                'template_ids': names, 'template_increments': values.tolist(), 'rows_per_template': sizes,
                'bootstrap_draws': draws, 'bootstrap_seed': seed, 'refits_per_draw': 0,
                'multiplicity_adjusted': False, 'partition_seeds_are_replications': False,
                'limitation': 'Descriptive intervals condition on the saved projection/alignment/decoder; sparse development groups, adaptive discovery and no refits prevent a generalization or mechanism claim.'})
    return output


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def _npz(path, **arrays):
    stream = io.BytesIO(); np.savez(stream, **arrays)
    immutable(path, stream.getvalue())


def _fit_bank(x, rows, *, backend, site, provenance, ranks=RANKS, alpha=100.):
    """Return all fixed fits, saved parameters/predictions, and full cells."""
    from .matched_probe_controls import grouped_shuffle
    projected, pca_arrays, pca_meta = fit_projection(x, rows)
    aligned, alignments, alignment_meta = align_conditions(projected, rows, provenance)
    arrays = {'case_ids': np.array([r['id'] for r in rows]), 'pca_mean': pca_arrays['mean'],
        'pca_components': pca_arrays['components'], 'pca_singular_values': pca_arrays['singular_values'],
        'pca_training_ids': np.array(pca_meta['training_ids'])}
    for condition, model in alignments.items():
        arrays.update({f'align_{condition}_{key}': value for key, value in {
            'source_mean': model.source_mean, 'target_mean': model.target_mean, 'rotation': model.rotation,
            'training_pair_ids': np.array(model.training_ids),
            'source_training_ids': np.array(alignment_meta[condition]['source_training_case_ids']),
            'neutral_training_ids': np.array(alignment_meta[condition]['neutral_training_case_ids'])}.items()})
    truth, _ = complete_targets(rows)
    tasks = {'value': truth}; shuffle_meta = {}
    for seed in CONTROL_SEEDS:
        shuffled, donors = grouped_shuffle(rows, seed)
        histograms = []
        for split in ('train', 'development'):
            for condition in CONDITIONS:
                mask = np.array([r['split'] == split and r['condition'] == condition for r in rows])
                for slot in range(2):
                    counts = np.bincount(truth[mask, slot], minlength=len(CLASSES))
                    control_counts = np.bincount(shuffled[mask, slot], minlength=len(CLASSES))
                    if not np.array_equal(counts, control_counts):
                        raise ValueError('complete within-condition shuffle class frequencies differ')
                    histograms.append({'split': split, 'condition': condition, 'slot': slot,
                        'n': int(mask.sum()), 'counts': counts.tolist(), 'control_counts': control_counts.tolist()})
        shuffle_meta[str(seed)] = {'donor_base_mapping': donors,
            'frequency_audit': histograms}
        tasks['shuffle'+str(seed)] = shuffled
    metrics = []; fits = []; comparisons = []; replay_count = 0
    for task, labels in tasks.items():
        _, targets = complete_targets(rows, labels)
        arrays['labels_'+task] = labels
        for training_condition in CONDITIONS:
            train = np.array([r['split'] == 'train' and r['condition'] == training_condition for r in rows])
            train_ids = [r['id'] for r, keep in zip(rows, train) if keep]
            train_key = 'training_ids_'+training_condition
            arrays[train_key] = np.array(train_ids)
            majority = [int(np.bincount(labels[train, slot], minlength=len(CLASSES)).argmax()) for slot in range(2)]
            for rank in ranks:
                if rank > min(projected.shape[1], targets.shape[1]):
                    raise ValueError('declared rank exceeds projected complete-target dimensions')
                key = f'{task}_{training_condition}_rank{rank}'
                model = fit_reduced_rank_ridge(projected[train], targets[train], train_ids=train_ids,
                    target_ids=train_ids, split='train', alpha=alpha, rank=rank, provenance=provenance,
                    config={'backend': backend, 'site': site, 'training_condition': training_condition,
                        'task': task, 'complete_targets': 'current32_plus_saved32_onehot'})
                for name, value in {'x_mean': model.x_mean, 'x_scale': model.x_scale,
                        'y_mean': model.y_mean, 'weights': model.weights}.items():
                    arrays[key+'_'+name] = value
                scores = model.predict(projected); arrays[key+'_predictions'] = _score(scores).astype(np.int16)
                replays = ((projected-arrays[key+'_x_mean'])/arrays[key+'_x_scale']) @ arrays[key+'_weights']+arrays[key+'_y_mean']
                if not np.array_equal(scores, replays):
                    raise ValueError('saved readout parameter replay differs')
                replay_count += len(rows)
                metadata = model.metadata; metadata.pop('training_ids')
                fits.append({'key': key, 'training_ids_array': train_key,
                    'training_structural_groups': len({r['template_id'] for r, keep in zip(rows, train) if keep}), 'model': metadata})
                modes = [('within_condition', training_condition, scores)]
                if training_condition == 'neutral':
                    aligned_scores = model.predict(aligned)
                    arrays[key+'_aligned_predictions'] = _score(aligned_scores).astype(np.int16)
                    if rank == 64 and task == 'value':
                        comparisons = paired_group_comparisons(arrays[key+'_predictions'], arrays[key+'_aligned_predictions'], labels, rows)
                    for condition in CONDITIONS[1:]:
                        modes.extend([('neutral_transfer_unaligned', condition, scores),
                            ('neutral_transfer_aligned', condition, aligned_scores)])
                for mode, condition, predicted_scores in modes:
                    for split in ('train', 'development'):
                        mask = np.array([r['split'] == split and r['condition'] == condition for r in rows])
                        metrics.append({'backend': backend, 'site': site, 'layer': 24 if backend == 'hidden' else None,
                            'task': task, 'rank': rank, 'training_condition': training_condition,
                            'evaluation_condition': condition, 'mode': mode, 'split': split,
                            **cell_metrics(predicted_scores, labels, rows, mask, majority=majority)})
    # Compact summaries point to arrays containing the full, immutable train IDs.
    pca_meta.pop('training_ids')
    for detail in alignment_meta.values():
        detail.pop('training_ids'); detail.pop('source_training_case_ids'); detail.pop('neutral_training_case_ids')
    return {'pca': pca_meta, 'alignments': alignment_meta, 'shuffle_controls': shuffle_meta,
        'fits': fits, 'metrics': metrics, 'comparisons': comparisons,
        'models': len(fits), 'parameter_replay_rows': replay_count}, arrays


def _render(result):
    lines = ['# Discovery representation rank and alignment sensitivity', '', LIMITATION, '',
        'The recipe was fixed before new scores were read, after earlier discovery readouts were known. '
        'Complete 64-column one-hot current/saved targets, alpha 100 and ranks 1/2/4/8/16/32/64 are fixed. '
        'PCA uses pooled TRAIN rows only; alignments use exact paired TRAIN relatives only. '
        'Within-condition fits provide ceilings in the same common projected space. '
        'Surface features use 4,096 character-ngram features and their own common TRAIN PCA64.', '',
        '| Backend | Site | PCA retained training variance | Training anchors per alignment |',
        '|---|---|---:|---:|']
    for bank in result['banks']:
        details = bank['summary']
        n = details['alignments']['informative']['n_train']
        lines.append(f"| {bank['backend']} | {bank['site']} | {details['pca']['retained_variance_fraction']:.4f} | {n} |")
    lines += ['', 'Full rank 64 is the fixed reference in this projection; all ranks and control cells are retained in JSON/CSV.', '',
        '| Backend | Site | Training condition | Development condition | Mode | Rows | Structural groups | Current accuracy | Saved accuracy | Joint accuracy |',
        '|---|---|---|---|---|---:|---:|---:|---:|---:|']
    for bank in result['banks']:
        for cell in bank['summary']['metrics']:
            if cell['task'] == 'value' and cell['rank'] == 64 and cell['split'] == 'development':
                lines.append(f"| {cell['backend']} | {cell['site']} | {cell['training_condition']} | {cell['evaluation_condition']} | {cell['mode']} | {cell['n']} | {cell['structural_groups']} | {cell['current_accuracy']:.4f} | {cell['saved_accuracy']:.4f} | {cell['joint_accuracy']:.4f} |")
    lines += ['', 'Rank-64 alignment increments use the same neutral decoder before and after alignment. '
        'Conditional 95% intervals resample whole development components without refitting; '
        'all sites/backends/endpoints are descriptive and have no multiplicity adjustment.', '',
        '| Backend | Site | Development condition | Endpoint | Aligned minus unaligned | Conditional group interval |',
        '|---|---|---|---|---:|---|']
    for bank in result['banks']:
        for cell in bank['summary']['comparisons']:
            lo, hi = cell['conditional_group_bootstrap_95']
            lines.append(f"| {bank['backend']} | {bank['site']} | {cell['condition']} | {cell['endpoint']} | {cell['mean_group_increment']:.4f} | [{lo:.4f}, {hi:.4f}] |")
    lines += ['', f"Saved fits: {result['fits']}; exact saved-parameter row replays: {result['parameter_replay_rows']}.", '',
        'The original final/extrapolation outcomes remain sealed. No language model was loaded, trained or queried.', '']
    return '\n'.join(lines)


def _expected_artifacts(config):
    out = Path(config['run_dir'])
    expected = {backend+'_'+site: out/f'{backend}_{site}_parameters.npz'
        for backend in ('hidden', 'surface') for site in SITES}
    expected.update(summary=out/'summary.json', report=Path(config['report']),
        cells=out/'cells.csv', audit=out/'audit.json')
    return expected


def _verify_completed(config, source):
    """Require the entire fixed artifact inventory before any reuse checksum."""
    review = _json(Path(config['run_dir'])/'review_v1.json')
    if (review.get('config_hash') != digest(config) or review.get('analysis_source') != source
            or review.get('status') != 'complete_exploratory'):
        raise ValueError('existing representation review identity differs')
    expected = _expected_artifacts(config)
    artifacts = review.get('artifacts')
    if not isinstance(artifacts, dict) or set(artifacts) != set(expected):
        raise ValueError('existing representation artifact inventory is incomplete or changed')
    for name, path in expected.items():
        artifact = artifacts[name]
        if (not isinstance(artifact, dict) or set(artifact) != {'path', 'sha256'}
                or not isinstance(artifact['path'], str)
                or _safe(artifact['path']).resolve() != _safe(path).resolve()):
            raise ValueError('existing representation artifact path differs: '+name)
    for name, path in expected.items():
        if _sha(path) != artifacts[name]['sha256']:
            raise ValueError('existing representation artifact changed: '+name)
    summary = _json(expected['summary'])
    if any(review.get(k) != value for k, value in summary.items()):
        raise ValueError('existing representation review summary differs')
    banks = summary.get('banks')
    if not isinstance(banks, list) or len(banks) != 2*len(SITES):
        raise ValueError('existing representation bank inventory differs')
    bank_paths = {}
    for bank in banks:
        if not isinstance(bank, dict):
            raise ValueError('existing representation bank metadata differs')
        name = str(bank.get('backend'))+'_'+str(bank.get('site'))
        if name in bank_paths or name not in expected or not isinstance(bank.get('artifact'), str):
            raise ValueError('existing representation bank inventory differs')
        bank_paths[name] = _safe(bank['artifact']).resolve()
    expected_banks = {backend+'_'+site: expected[backend+'_'+site].resolve()
        for backend in ('hidden', 'surface') for site in SITES}
    if bank_paths != expected_banks:
        raise ValueError('existing representation bank paths differ')
    return review


def _thread_count():
    allocated = os.environ.get('SLURM_CPUS_PER_TASK')
    try:
        threads = 8 if allocated is None else int(allocated)
    except ValueError as exc:
        raise ValueError('SLURM_CPUS_PER_TASK must declare a positive integer') from exc
    if threads < 1:
        raise ValueError('SLURM_CPUS_PER_TASK must declare a positive integer')
    return threads


def run(config):
    """Fit and audit a finite CPU workload; all checkpoint loading stays absent."""
    checked = preflight(config)
    out = _safe(config['run_dir']); out.mkdir(parents=True, exist_ok=True)
    source = code_identity()
    registration = {'evaluation_role': ROLE, 'config': config, 'config_hash': digest(config),
        'analysis_source': source, 'preflight': checked, 'generated_holdouts_opened': False,
        'mechanism_C_fitted': False, 'limitation': LIMITATION}
    immutable(out/'registration.json', _json_bytes(registration))
    review_path = out/'review_v1.json'
    if review_path.exists():
        return _verify_completed(config, source)
    from sklearn.feature_extraction.text import HashingVectorizer
    import sklearn
    from threadpoolctl import threadpool_limits
    started = time.monotonic(); features, rows, capture, coverage = _load(config)
    banks = []; artifacts = {}
    provenance = {'capture_identity': checked['capture_identity'], 'capture_audit_sha256': config['capture_audit_sha256'],
        'config_hash': digest(config), 'analysis_source_sha256': source['source_sha256']}
    threads = _thread_count()
    with threadpool_limits(limits=threads):
        for site_index, site in enumerate(SITES):
            indices = site_indices(rows, site); meta = [rows[i] for i in indices]
            _row_checks(meta)
            for condition in CONDITIONS:
                semantic_pairs(meta, condition, 'train'); semantic_pairs(meta, condition, 'development')
            texts = [r['visible_prefixes'][capture['sites'].index(site)] for r in meta]
            vectorizer = HashingVectorizer(analyzer='char', ngram_range=(3, 8),
                n_features=4096, alternate_sign=True, norm=None, dtype=np.float64)
            surface = vectorizer.transform(texts).toarray()
            for backend in ('hidden', 'surface'):
                x = features[indices, site_index] if backend == 'hidden' else surface
                summary, arrays = _fit_bank(x, meta, backend=backend, site=site, provenance=provenance)
                params = out/f'{backend}_{site}_parameters.npz'
                _npz(params, **arrays)
                with np.load(params, allow_pickle=False) as saved:
                    if set(saved.files) != set(arrays) or any(not np.array_equal(saved[key], value) for key, value in arrays.items()):
                        raise ValueError('serialized fit parameters/predictions differ')
                name = backend+'_'+site
                artifacts[name] = {'path': str(params), 'sha256': _sha(params)}
                banks.append({'backend': backend, 'site': site, 'rows': len(meta),
                    'coverage': _row_checks(meta), 'artifact': str(params), 'summary': summary})
    result = {'status': 'complete_exploratory', 'evaluation_role': ROLE, 'config_hash': digest(config),
        'analysis_source': source, 'capture_identity': checked['capture_identity'], 'capture_config_sha256': config['capture_config_sha256'],
        'capture_audit_sha256': config['capture_audit_sha256'], 'capture_manifest_sha256': config['capture_manifest_sha256'],
        'coverage': coverage, 'banks': banks, 'fits': sum(b['summary']['models'] for b in banks),
        'parameter_replay_rows': sum(b['summary']['parameter_replay_rows'] for b in banks),
        'class_values': CLASSES.tolist(), 'slots': ['current', 'saved'], 'target_columns': 64,
        'fixed_layer': 24, 'fixed_sites': list(SITES), 'fixed_ranks': list(RANKS), 'fixed_alpha': 100.,
        'shuffle_seeds': list(CONTROL_SEEDS), 'pca': PCA, 'sklearn_version': sklearn.__version__,
        'runtime': {'threadpool_limit': threads, 'slurm_cpus_per_task': os.environ.get('SLURM_CPUS_PER_TASK'),
            'slurm_job_id': os.environ.get('SLURM_JOB_ID'), 'numpy_version': np.__version__},
        'generated_holdouts_opened': False, 'mechanism_C_fitted': False, 'model_loading': False,
        'new_checkpoint_queries': 0, 'limitation': LIMITATION}
    # No elapsed time in immutable results: interrupted recomputation is identical.
    summary_path = out/'summary.json'; immutable(summary_path, _json_bytes(result))
    report = _safe(config['report']); immutable(report, _render(result).encode())
    stream = io.StringIO(); flat = []
    for bank in banks:
        flat.extend({k: v for k, v in cell.items() if k != 'template_cells'} for cell in bank['summary']['metrics'])
    writer = csv.DictWriter(stream, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    csv_path = out/'cells.csv'; immutable(csv_path, stream.getvalue().encode())
    audit = {'status': 'passed', 'config_hash': digest(config), 'fits': result['fits'],
        'parameter_replay_rows': result['parameter_replay_rows'], 'serialized_parameters_and_predictions_exact': True,
        'pca_and_alignment_heldout_fit_rows': 0, 'full_target_columns': 64,
        'capture_identity': checked['capture_identity'], 'generated_holdouts_opened': False,
        'scope': 'Exact audited capture identities, source chunk hashes, complete grouped targets, train-only transforms, full fixed fit coverage and immutable parameter/prediction serialization.'}
    audit_path = out/'audit.json'; immutable(audit_path, _json_bytes(audit))
    artifacts.update({name: {'path': str(path), 'sha256': _sha(path)} for name, path in
        [('summary', summary_path), ('report', report), ('cells', csv_path), ('audit', audit_path)]})
    result.update(artifacts=artifacts, wall_seconds=time.monotonic()-started)
    immutable(review_path, _json_bytes(result))
    return result
