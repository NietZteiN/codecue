"""Capacity-matched queried/unqueried readouts on one consumed capture bank.

Keep both query twins at every site. Query identity defines the target heads and
never becomes an extra feature. Shared factorization fits four independent ridge
heads, with no low-rank constraint, PCA, gating or representation alignment.
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
from .discovery_readouts import CLASSES, group_weights
from .published_benchmarks import immutable
from .registry import code_identity
from .representation_sensitivity import _safe, _json, _sha, _row_checks

ROLE = 'discovery_query_selectivity_v1'
LAYERS = (8, 16, 24, 31)
SITES = ('pre_query_state', 'after_query', 'pre_answer')
CONDITIONS = ('neutral', 'informative', 'misleading')
SEEDS = (11, 29, 47)
HEADS = ('queried', 'unqueried', 'shuffled_queried', 'shuffled_unqueried')
CANONICAL_RECONSTRUCTION = ('Evaluation-only remapping of the two new queried/unqueried head predictions '
    'using the known input query_role; no separately fitted canonical-slot heads, old canonical-probe '
    'replay or additional owner information.')
PRIMARY = {'backend': 'hidden', 'layer': 24, 'site': 'pre_answer', 'condition': 'neutral', 'split': 'development'}
BOOTSTRAP = {'draws': 2000, 'seed': 117}
TOLERANCE = 1e-8
SOURCE_CASES = 9216
MAX_RESULT_BYTES = 64*1024**2
COMPLETION_NAME = 'completion_manifest_v2.json'
LIMITATION = (
    'Adaptive descriptive discovery readouts on one checkpoint and previously consumed structures. '
    'The primary site was selected because earlier queried-value recovery was known, not from new results. '
    'Queried/unqueried labels have matched aggregate class marginals and identical per-head capacity, '
    'but their conditional task difficulty can differ. A gap describes query-dependent accessibility '
    'under this decoder; it does not identify tracking, reconstruction, owner coding, a binding register '
    'or natural causal use. Canonical current/saved reconstruction only relabels the queried/unqueried '
    'predictions using the known input query role; it is postprocessing, not separately trained '
    'canonical-slot heads or a replay of the older canonical probes. Those and query-role cells are descriptive. '
    'Both identical pre-query twins are retained: their analytic head objectives coincide and contain '
    'no information about the future query. Raw heads are not averaged or canonicalized to enforce agreement; '
    'floating-point argmax disagreements within the fixed 1e-8 score tolerance are reported as ties. '
    'Three seeds vary template weights and grouped shuffle controls, not independent experiments. '
    'Primary intervals resample six whole development components after averaging the fixed-seed paired '
    'correctness differences; they condition on saved fits without refitting or multiplicity correction. '
    'Float64 standardization/fitting differs from possible float32 rounding in older probe fits; '
    'new results are not claimed to replay those older fit scores exactly. The captured pre_answer '
    'site precedes the later formatting-space correction and is not the later digit boundary. '
    'Capture validation reads stored response/score metadata, but no response, correctness, row ID or '
    'query-role field becomes a readout feature. No model/tokenizer is loaded or new response generated.'
)


def _config(config):
    if not isinstance(config, dict) or config.get('evaluation_role') != ROLE:
        raise ValueError('explicit discovery query-selectivity role required')
    required = {'evaluation_role', 'capture_config', 'capture_config_sha256',
        'capture_audit_sha256', 'capture_manifest_sha256', 'run_dir', 'report'}
    fixed = {'alpha': 100., 'seeds': list(SEEDS), 'feature_dimensions': 4096,
        'layers': list(LAYERS), 'sites': list(SITES), 'class_values': CLASSES.tolist(),
        'primary': PRIMARY, 'bootstrap': BOOTSTRAP, 'score_tolerance': TOLERANCE}
    if required-set(config) or set(config)-required-set(fixed):
        raise ValueError('missing or unknown query-selectivity configuration fields')
    for name, value in fixed.items():
        if name in config and config[name] != value:
            raise ValueError('fixed query-selectivity recipe differs: '+name)
    for name in ('capture_config_sha256', 'capture_audit_sha256', 'capture_manifest_sha256'):
        value = config[name]
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('explicit SHA256 source metadata pins required')
    for name in ('capture_config', 'run_dir', 'report'):
        if not isinstance(config[name], str) or not config[name]: raise ValueError('explicit source/output paths required')
        _safe(config[name])
    return fixed


def _source_metadata(config):
    fixed = _config(config)
    capture = _json(config['capture_config'], config['capture_config_sha256'])
    if (capture.get('model') != 'meta-llama/Llama-3.1-8B-Instruct' or capture.get('layers') != list(LAYERS)
            or capture.get('sites') != list(SITES) or capture.get('hidden_size') != 4096):
        raise ValueError('fixed audited discovery checkpoint/capture geometry required')
    for name in ('dataset', 'capture_cases', 'preflight_result', 'run_dir'): _safe(capture[name])
    folder = Path(capture['run_dir'])/'activations'
    manifest = _json(folder/'manifest.json', config['capture_manifest_sha256'])
    audit = _json(folder/'audit.json', config['capture_audit_sha256'])
    identity = manifest.get('identity', {})
    from .experiment_log import _sealed
    if (_sealed(capture) or _sealed(identity.get('dataset_manifest') or {})
            or manifest.get('status') != 'complete' or audit.get('status') != 'passed'
            or identity.get('config') != capture or manifest.get('identity_hash') != digest(identity)
            or audit.get('identity_hash') != manifest['identity_hash'] or audit.get('cases') != SOURCE_CASES
            or audit.get('generated_holdouts_opened') is not False or not audit.get('chunk_checksums')):
        raise ValueError('complete matching discovery capture metadata required')
    qa = _json(capture['preflight_result'])
    if (qa != audit.get('preflight') or qa.get('status') != 'passed' or qa.get('config_hash') != digest(capture)
            or qa.get('source_sha256') != identity.get('code', {}).get('source_sha256')):
        raise ValueError('capture preparation/source identity differs')
    for name, checksum in audit['chunk_checksums'].items():
        path = _safe(name)
        if (path.resolve().parent != (folder/'chunks').resolve() or path.suffix != '.npz' or not path.is_file()
                or not isinstance(checksum, str) or len(checksum) != 64):
            raise ValueError('pinned capture chunk paths/checksums required')
    return capture, manifest, audit, fixed


def preflight(config):
    capture, manifest, audit, fixed = _source_metadata(config)
    return {'status': 'passed', 'evaluation_role': ROLE, 'config_hash': digest(config),
        'fixed_recipe': fixed, 'capture_identity': manifest['identity_hash'],
        'model': capture['model'], 'model_revision': capture['model_revision'],
        'cases': audit['cases'], 'chunks': len(audit['chunk_checksums']),
        'activation_arrays_read': False, 'new_model_queries': 0, 'behavioral_response_features': False,
        'generated_holdouts_opened': False, 'canonical_reconstruction_definition': CANONICAL_RECONSTRUCTION,
        'limitation': LIMITATION}


def twin_groups(rows):
    """Require reciprocal queries with the exact same causal prefix/targets."""
    _row_checks(rows)
    groups = defaultdict(list)
    for i, row in enumerate(rows): groups[row['state_prefix_sha256']].append(i)
    fields = ('base_id', 'template_id', 'split', 'condition', 'lexical_realization',
        'available_bindings', 'updates', 'tail_placement', 'targets')
    pairs = []
    for _, indices in sorted(groups.items()):
        if len(indices) != 2 or {rows[i]['query_role'] for i in indices} != {'current', 'saved'}:
            raise ValueError('complete reciprocal current/saved query twins required')
        i, j = sorted(indices, key=lambda k: rows[k]['query_role'])
        if (any(rows[i][key] != rows[j][key] for key in fields)
                or rows[i]['visible_prefixes'][0] != rows[j]['visible_prefixes'][0]
                or rows[i]['positions'][0] != rows[j]['positions'][0]):
            raise ValueError('query twins differ in state, targets or visible pre-query prefix')
        pairs.append((i, j))
    return np.array(pairs, dtype=int)


def canonical_labels(rows):
    lookup = {int(value): i for i, value in enumerate(CLASSES)}
    try:
        labels = np.array([[lookup[v] for v in row['targets']] for row in rows], dtype=int)
    except (KeyError, TypeError) as exc: raise ValueError('complete fixed-domain canonical targets required') from exc
    if labels.shape != (len(rows), 2): raise ValueError('two complete canonical target columns required')
    return labels


def query_labels(rows, canonical):
    canonical = np.asarray(canonical)
    if (canonical.shape != (len(rows), 2) or canonical.dtype.kind not in 'iu'
            or (canonical < 0).any() or (canonical >= len(CLASSES)).any()
            or any(r['query_role'] not in ('current', 'saved') for r in rows)):
        raise ValueError('complete reciprocal query targets required')
    slot = np.array([0 if r['query_role'] == 'current' else 1 for r in rows])
    indices = np.arange(len(rows))
    return np.column_stack((canonical[indices, slot], canonical[indices, 1-slot]))


def targets(rows, seed):
    from .matched_probe_controls import grouped_shuffle
    canonical = canonical_labels(rows); shuffled, mapping = grouped_shuffle(rows, seed)
    labels = np.column_stack((query_labels(rows, canonical), query_labels(rows, shuffled)))
    truth = np.concatenate([np.eye(len(CLASSES), dtype=np.float64)[labels[:, head]] for head in range(4)], axis=1)
    if not np.array_equal(truth.reshape(len(rows), 4, len(CLASSES)).sum(axis=2), np.ones((len(rows), 4))):
        raise ValueError('four complete one-hot target heads required')
    return labels, truth, canonical, shuffled, mapping


def marginal_audit(rows, labels, train, weights, pairs):
    """Check equal task difficulty marginals without claiming equal complexity."""
    train = np.asarray(train, dtype=bool); weights = np.asarray(weights, dtype=float)
    if train.shape != (len(rows),) or weights.shape != (int(train.sum()),) or not np.isfinite(weights).all() or (weights <= 0).any():
        raise ValueError('positive row-aligned neutral-training weights required')
    index = {i: j for j, i in enumerate(np.flatnonzero(train))}
    if any((i in index) != (j in index) or i in index and weights[index[i]] != weights[index[j]] for i, j in pairs):
        raise ValueError('query twins require exactly equal training weights')
    cells = []
    for split in ('train', 'development'):
        for condition in CONDITIONS:
            for query in ('all', 'current', 'saved'):
                mask = np.array([r['split'] == split and r['condition'] == condition
                    and (query == 'all' or r['query_role'] == query) for r in rows])
                if not mask.any(): raise ValueError('complete split/naming/query-role cells required')
                hist = np.array([np.bincount(labels[mask, h], minlength=len(CLASSES)) for h in range(4)])
                if (not np.array_equal(hist[0], hist[2]) or not np.array_equal(hist[1], hist[3])
                        or query == 'all' and not np.array_equal(hist[0], hist[1])):
                    raise ValueError('queried/unqueried or matched-control class marginals differ')
                cells.append({'split': split, 'condition': condition, 'query_role': query,
                    'n': int(mask.sum()), 'class_counts': hist.tolist()})
    weighted = np.array([np.bincount(labels[train, h], weights=weights, minlength=len(CLASSES)) for h in range(4)])
    if not np.allclose(weighted, weighted[0], rtol=0, atol=TOLERANCE):
        raise ValueError('seed-weighted queried/unqueried/control class marginals differ')
    return {'cells': cells, 'weighted_training_class_counts': weighted.tolist(),
        'maximum_weighted_head_count_difference': float(np.max(np.abs(weighted-weighted[0]))),
        'query_twin_training_weights_exact': True}


def _load(config):
    capture, manifest, audit, _ = _source_metadata(config)
    from .state_capture import inputs, validate_chunk
    _, cases = inputs(capture, manifest['identity']['code']['source_sha256'])
    declared = []
    for item in cases:
        row = item['case']['record']
        declared.append({**{k: row[k] for k in ('id', 'base_id', 'template_id', 'split', 'condition', 'query_role')},
            'targets': item['targets']})
    coverage = _row_checks(declared)
    if len(cases) != SOURCE_CASES or coverage['structural_groups'] != {'train': 18, 'development': 6}:
        raise ValueError('fixed discovery case/structural-group coverage differs')
    # All split/label declarations and metadata paths are checked before NPZ.
    vectors = np.empty((len(cases), len(LAYERS), len(SITES), 4096), dtype=np.float32)
    rows = []
    for name, checksum in sorted(audit['chunk_checksums'].items()):
        if _sha(name) != checksum: raise ValueError('audited capture chunk changed before array loading')
        with np.load(_safe(name), allow_pickle=False) as saved:
            part = json.loads(saved['metadata'].tobytes()); features = saved['features']
            validate_chunk(capture, cases[len(rows):len(rows)+len(part)], features, part)
            vectors[len(rows):len(rows)+len(part)] = features; rows.extend(part)
    if len(rows) != len(cases) or [r['id'] for r in rows] != [r['id'] for r in declared]:
        raise ValueError('complete ordered capture IDs required')
    pairs = twin_groups(rows)
    if not np.array_equal(vectors[pairs[:, 0], :, 0], vectors[pairs[:, 1], :, 0]):
        raise ValueError('pre-query hidden twins differ at a captured block')
    return vectors, rows, pairs, capture, coverage


def _predictions(scores):
    scores = np.asarray(scores)
    if scores.ndim != 2 or scores.shape[1] != 4*len(CLASSES) or not np.isfinite(scores).all():
        raise ValueError('finite four-head class scores required')
    return scores.reshape(len(scores), 4, len(CLASSES)).argmax(axis=2)


def _comparison(left, right):
    left = np.asarray(left); right = np.asarray(right)
    if (left.ndim != 2 or left.shape[1] != 32 or right.shape != left.shape or not len(left)
            or not np.isfinite(left).all() or not np.isfinite(right).all()):
        raise ValueError('paired finite 32-class score matrices required')
    difference = np.max(np.abs(left-right), axis=1)
    if np.max(difference) > TOLERANCE: raise ValueError('analytic pre-query score symmetry exceeds fixed numeric tolerance')
    prediction_left = left.argmax(axis=1); prediction_right = right.argmax(axis=1)
    disagreement = prediction_left != prediction_right
    margin_left = np.sort(left, axis=1)[:, -1]-np.sort(left, axis=1)[:, -2]
    margin_right = np.sort(right, axis=1)[:, -1]-np.sort(right, axis=1)[:, -2]
    margin = np.maximum(margin_left, margin_right)
    if (disagreement & (margin > 2*TOLERANCE)).any():
        raise ValueError('pre-query argmax disagreement is outside the fixed tie tolerance')
    return {'maximum_absolute_score_difference': float(np.max(difference)),
        'prediction_agreement_fraction': float((~disagreement).mean()),
        'argmax_disagreements': int(disagreement.sum()),
        'disagreement_maximum_top_two_margin': float(margin[disagreement].max()) if disagreement.any() else None,
        'disagreement_minimum_top_two_margin': float(margin[disagreement].min()) if disagreement.any() else None,
        'all_disagreements_within_fixed_tie_bound': True, 'score_tolerance_absolute': TOLERANCE,
        'raw_scores_and_predictions_retained': True, 'analytic_future_query_information': False}


def prequery_symmetry(x, truth, train, weights, model, scores, pairs):
    params = model.parameters
    z = (np.asarray(x[train], dtype=np.float64)-params['mean'])/params['scale']-params['weighted_feature_mean']
    result = {}
    for task, first in (('value', 0), ('shuffled', 2)):
        a = slice(first*32, (first+1)*32); b = slice((first+1)*32, (first+2)*32)
        cross_a = z.T@(weights[:, None]*truth[train, a]); cross_b = z.T@(weights[:, None]*truth[train, b])
        diagnostics = {'maximum_weighted_crossproduct_difference': float(np.max(np.abs(cross_a-cross_b))),
            'maximum_weighted_target_mean_difference': float(np.max(np.abs(params['weighted_target_mean'][a]-params['weighted_target_mean'][b]))),
            'maximum_coefficient_difference': float(np.max(np.abs(params['coef'][:, a]-params['coef'][:, b]))),
            'maximum_intercept_difference': float(np.max(np.abs(params['intercept'][a]-params['intercept'][b])))}
        if any(value > TOLERANCE for value in diagnostics.values()):
            raise ValueError('analytic pre-query equal-objective parameters exceed fixed numeric tolerance')
        diagnostics.update(_comparison(scores[:, a], scores[:, b]))
        diagnostics['twin_queried_scores'] = _comparison(scores[pairs[:, 0], a], scores[pairs[:, 1], a])
        diagnostics['twin_unqueried_scores'] = _comparison(scores[pairs[:, 0], b], scores[pairs[:, 1], b])
        result[task] = diagnostics
    return result


def metric_cells(rows, labels, canonical, shuffled, predictions, train):
    cells = []; slot = np.array([0 if r['query_role'] == 'current' else 1 for r in rows])
    value_reconstructed = np.take_along_axis(predictions[:, :2], np.column_stack((slot, 1-slot)), axis=1)
    control_reconstructed = np.take_along_axis(predictions[:, 2:], np.column_stack((slot, 1-slot)), axis=1)
    for split, condition in [('train', 'neutral')]+[('development', c) for c in CONDITIONS]:
        for query in ('all', 'current', 'saved'):
            mask = np.array([r['split'] == split and r['condition'] == condition
                and (query == 'all' or r['query_role'] == query) for r in rows])
            if not mask.any(): raise ValueError('registered readout cell is empty')
            groups = sorted({r['template_id'] for r, keep in zip(rows, mask) if keep})
            heads = []
            for h, name in enumerate(HEADS):
                counts = np.bincount(labels[train, h], minlength=len(CLASSES)); support = np.flatnonzero(counts)
                correct = predictions[:, h] == labels[:, h]
                template_cells = []
                for group in groups:
                    tm = mask & np.array([r['template_id'] == group for r in rows])
                    template_cells.append({'template_id': group, 'n': int(tm.sum()), 'correct': int(correct[tm].sum())})
                heads.append({'head': name, 'n': int(mask.sum()), 'training_rows': int(train.sum()),
                    'accuracy': float(correct[mask].mean()), 'training_classes': len(support),
                    'evaluation_classes': int(len(np.unique(labels[mask, h]))),
                    'out_of_training_support': int((~np.isin(labels[mask, h], support)).sum()),
                    'training_majority_accuracy': float((labels[mask, h] == counts.argmax()).mean()),
                    'training_class_counts': counts.tolist(), 'evaluation_class_counts': np.bincount(labels[mask, h], minlength=32).tolist(),
                    'parameter_count_per_head': 32*(4096+1), 'template_cells': template_cells})
            reconstructed = {}
            for task, predicted, expected in [('value', value_reconstructed, canonical), ('shuffled', control_reconstructed, shuffled)]:
                correct = predicted == expected
                reconstructed[task] = {'current_accuracy': float(correct[mask, 0].mean()),
                    'saved_accuracy': float(correct[mask, 1].mean()), 'whole_pair_accuracy': float(correct[mask].all(axis=1).mean())}
            cells.append({'split': split, 'condition': condition, 'query_role': query, 'n': int(mask.sum()),
                'structural_groups': len(groups), 'heads': heads, 'canonical_reconstruction': reconstructed})
    return cells


def primary_bootstrap(rows, differences):
    if set(differences) != set(SEEDS): raise ValueError('all three fixed weighting fits required before group resampling')
    if any(np.asarray(differences[seed]).shape != (len(rows),)
            or not np.isin(differences[seed], [-1., 0., 1.]).all() for seed in SEEDS):
        raise ValueError('each fit requires one paired binary-correctness difference per row')
    averaged = np.stack([differences[seed] for seed in SEEDS]).mean(axis=0)
    names = sorted({r['template_id'] for r in rows if r['split'] == 'development' and r['condition'] == 'neutral'})
    if len(names) != 6: raise ValueError('six fixed development components required for the primary contrast')
    values = []; sizes = []
    for name in names:
        mask = np.array([r['split'] == 'development' and r['condition'] == 'neutral' and r['template_id'] == name for r in rows])
        values.append(float(averaged[mask].mean())); sizes.append(int(mask.sum()))
    values = np.array(values)
    rng = np.random.default_rng(BOOTSTRAP['seed'])
    draws = rng.integers(0, len(values), size=(BOOTSTRAP['draws'], len(values)))
    return {'contrast': 'queried_minus_unqueried_accuracy', 'primary': PRIMARY,
        'mean_group_increment': float(values.mean()),
        'conditional_group_bootstrap_95': np.quantile(values[draws].mean(axis=1), [.025, .975]).tolist(),
        'template_ids': names, 'template_increments': values.tolist(), 'rows_per_template': sizes,
        'n': sum(sizes), 'structural_groups': len(names), 'bootstrap': BOOTSTRAP,
        'seed_aggregation': 'Average paired row correctness differences across the three fixed weighting fits before group resampling.',
        'refits_per_draw': 0, 'multiplicity_adjusted': False, 'seeds_are_replications': False,
        'scope': 'Conditional descriptive discovery interval on six known development components; no confirmatory or causal claim.'}


def _json_bytes(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def _npz(path, arrays):
    stream = io.BytesIO(); np.savez(stream, **arrays); immutable(path, stream.getvalue())


def fit_name(backend, layer, site_index, seed):
    return f'{backend}_layer{layer}_site{site_index}_seed{seed}'


def _expected(config):
    out = Path(config['run_dir']); expected = {}
    for site in range(len(SITES)):
        for backend, layer in [('hidden', value) for value in LAYERS]+[('surface', -1)]:
            for seed in SEEDS:
                name = fit_name(backend, layer, site, seed); expected[name] = out/(name+'.npz')
    expected.update(summary=out/'summary.json', report=Path(config['report']), cells=out/'cells.csv',
        cases=out/'readout_cases.jsonl', audit=out/'audit.json')
    return expected


def _pin(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('explicit SHA256 result/source pin required')
    return value


def _result_payload(path, checksum):
    """Read scientific RESULT data, never general metadata, after SHA pinning.

    Callers first validate the bounded config/registration/source and all expected
    canonical paths. The independent result cap does not relax the 8 MiB metadata
    reader imported above. No unpinned JSON fallback is allowed.
    """
    path = _safe(path); _pin(checksum)
    if path.suffix != '.json' or not path.is_file() or path.stat().st_size > MAX_RESULT_BYTES:
        raise ValueError('scientific result exceeds its separate declared payload bound')
    with path.open('rb') as stream:
        payload = stream.read(MAX_RESULT_BYTES+1)
    if len(payload) > MAX_RESULT_BYTES:
        raise ValueError('scientific result exceeds its separate declared payload bound')
    if hashlib.sha256(payload).hexdigest() != checksum:
        raise ValueError('pinned scientific result payload checksum changed')
    value = json.loads(payload)
    if not isinstance(value, dict): raise ValueError('scientific result object required')
    return value


def _fit_registration(config, snapshot):
    """Bounded role/config/source guards required before any rich result read."""
    capture, manifest, _, _ = _source_metadata(config)
    expected = _expected(config)
    for path in expected.values(): _safe(path)
    registration_path = _safe(Path(config['run_dir'])/'registration.json')
    registration = _json(registration_path)
    if (registration.get('evaluation_role') != ROLE or registration.get('config') != config
            or registration.get('config_hash') != digest(config)
            or registration.get('capture_identity') != manifest['identity_hash']
            or registration.get('generated_holdouts_opened') is not False
            or registration.get('new_model_queries') != 0
            or registration.get('behavioral_response_features') is not False):
        raise ValueError('bounded original fit registration role/config/source differs')
    snapshot = _safe(snapshot).resolve()
    frozen_path = snapshot/'frozen_manifest.json'
    frozen = _json(frozen_path)
    if not isinstance(frozen.get('config_files'), dict):
        raise ValueError('bounded frozen configuration inventory required')
    for name in frozen['config_files']:
        relative = Path(name)
        path = snapshot/relative
        if (relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] != 'configs'
                or relative.suffix not in ('.json', '.yaml') or path.is_symlink() or not path.is_file()
                or path.stat().st_size > 8*1024**2 or not path.resolve().is_relative_to(snapshot/'configs')):
            raise ValueError('frozen configuration inventory is not bounded source metadata')
    from .snapshots import verify
    verified = verify(snapshot)
    if verified != frozen or verified.get('code') != registration.get('analysis_source'):
        raise ValueError('frozen original fit source differs from its registration')
    workspace = Path(verified['workspace_root']).resolve()
    capture_path = Path(config['capture_config'])
    try:
        relative_capture = str(capture_path.resolve().relative_to(workspace)) if capture_path.is_absolute() else str(capture_path)
    except ValueError as exc:
        raise ValueError('capture configuration is outside the original fit workspace') from exc
    if verified.get('config_files', {}).get(relative_capture) != config['capture_config_sha256']:
        raise ValueError('original frozen capture configuration SHA differs')
    if _json(snapshot/relative_capture, config['capture_config_sha256']) != capture:
        raise ValueError('original frozen capture configuration content differs')
    matching = []
    for name, checksum in verified.get('config_files', {}).items():
        if not name.endswith('.json'): continue
        try:
            path = _safe(snapshot/name)
        except ValueError:
            continue  # An unrelated reserved config is not this readout config.
        if _json(path, checksum) == config: matching.append({'path': name, 'sha256': checksum})
    if not matching: raise ValueError('the original frozen source lacks the exact scientific fit configuration')
    source = {'snapshot': str(snapshot), 'snapshot_id': verified['snapshot_id'],
        'source_sha256': verified['code']['source_sha256'], 'frozen_manifest_sha256': _sha(frozen_path),
        'scientific_config_files': matching}
    return registration, source


def _artifact_inventory(config, artifacts):
    expected = _expected(config)
    if not isinstance(artifacts, dict) or set(artifacts) != set(expected):
        raise ValueError('complete fixed query-selectivity artifact inventory required')
    for name, path in expected.items():
        item = artifacts[name]
        if (not isinstance(item, dict) or set(item) != {'path', 'sha256'}
                or not isinstance(item['path'], str) or _safe(item['path']).resolve() != _safe(path).resolve()):
            raise ValueError('query-selectivity artifact path differs')
        _pin(item['sha256'])
    return expected


def _fixed_result(config, review, registration):
    """Validate the registered finite fit matrix and denominators, no refits."""
    fixed = {'status': 'complete_exploratory', 'evaluation_role': ROLE, 'config_hash': digest(config),
        'analysis_source': registration['analysis_source'], 'capture_identity': registration['capture_identity'],
        'cases': SOURCE_CASES, 'retained_query_twins': SOURCE_CASES//2, 'factorizations': 45,
        'independent_heads': 180, 'parameter_count_per_head': 131104, 'parameter_replay_rows': SOURCE_CASES*45,
        'class_values': CLASSES.tolist(), 'heads': list(HEADS), 'float64_standardization_and_fitting': True,
        'query_role_is_feature': False, 'behavioral_response_features': False, 'new_model_queries': 0,
        'generated_holdouts_opened': False, 'mechanism_C_fitted': False}
    if any(review.get(k) != value for k, value in fixed.items()):
        raise ValueError('completed scientific result fixed source/count/access contract differs')
    if review.get('coverage', {}).get('structural_groups') != {'train': 18, 'development': 6}:
        raise ValueError('completed scientific structural-group inventory differs')
    primary = review.get('primary_comparison', {})
    if (primary.get('primary') != PRIMARY or primary.get('structural_groups') != 6 or primary.get('n') != 768
            or primary.get('bootstrap') != BOOTSTRAP or primary.get('refits_per_draw') != 0
            or primary.get('seeds_are_replications') is not False):
        raise ValueError('completed scientific primary contrast registration differs')
    expected = _expected(config); paths = {}; fits = review.get('fits')
    if not isinstance(fits, list) or len(fits) != 45: raise ValueError('complete fixed readout fit paths required')
    required_cells = {(s, c, q) for s, c in [('train', 'neutral')]+[('development', c) for c in CONDITIONS]
        for q in ('all', 'current', 'saved')}
    for item in fits:
        if not isinstance(item, dict): raise ValueError('scientific fit metadata object required')
        backend, layer, site, seed = (item.get(k) for k in ('backend', 'layer', 'site', 'seed'))
        if (backend, layer) not in [('hidden', value) for value in LAYERS]+[('surface', -1)] or site not in SITES or seed not in SEEDS:
            raise ValueError('completed scientific fit grid differs')
        name = fit_name(backend, layer, SITES.index(site), seed)
        if item.get('name') != name or name in paths or _safe(item.get('artifact', '')).resolve() != expected[name].resolve():
            raise ValueError('complete fixed readout fit paths required')
        paths[name] = expected[name]
        model = item.get('model', {})
        if any(model.get(k) != value for k, value in {'n_train': 2304, 'features': 4096, 'targets': 128,
                'alpha': 100., 'dtype': 'float64', 'factorizations': 1, 'heldout_rows_used_for_fit': 0,
                'fit_split': 'train', 'output_columns_independent': True}.items()):
            raise ValueError('completed independent ridge model counts/protocol differ')
        cells = item.get('cells', [])
        if len(cells) != 12 or {(c.get('split'), c.get('condition'), c.get('query_role')) for c in cells} != required_cells:
            raise ValueError('completed split/naming/query-role cell inventory differs')
        for cell in cells:
            n = (2304 if cell['split'] == 'train' else 768)//(1 if cell['query_role'] == 'all' else 2)
            if cell.get('n') != n or cell.get('structural_groups') != (18 if cell['split'] == 'train' else 6):
                raise ValueError('completed readout cell denominators differ')
            if [h.get('head') for h in cell.get('heads', [])] != list(HEADS):
                raise ValueError('four independent completed readout heads required')
            for head in cell['heads']:
                if head.get('n') != n or head.get('training_rows') != 2304 or head.get('parameter_count_per_head') != 131104:
                    raise ValueError('completed per-head capacity/denominators differ')
    if set(paths) != {k for k, p in expected.items() if p.suffix == '.npz'}:
        raise ValueError('complete fixed readout fit paths required')


def _verify_result(config, review, registration):
    _fixed_result(config, review, registration)
    expected = _artifact_inventory(config, review.get('artifacts'))
    for name, path in expected.items():
        if _sha(path) != review['artifacts'][name]['sha256']:
            raise ValueError('query-selectivity artifact checksum changed')
    summary = _result_payload(expected['summary'], review['artifacts']['summary']['sha256'])
    if (set(review) != set(summary)|{'artifacts', 'wall_seconds'}
            or any(review.get(k) != value for k, value in summary.items())):
        raise ValueError('query-selectivity review summary differs')
    audit = _json(expected['audit'], review['artifacts']['audit']['sha256'])
    if any(audit.get(k) != value for k, value in {'status': 'passed', 'config_hash': digest(config),
            'capture_identity': registration['capture_identity'], 'factorizations': 45, 'independent_heads': 180,
            'parameter_replay_rows': SOURCE_CASES*45, 'serialized_raw_scores_and_predictions_exact': True,
            'complete_query_twins_all_sites': True, 'per_head_classes': 32, 'parameter_count_per_head': 131104,
            'prequery_score_tolerance_absolute': TOLERANCE, 'behavioral_response_features': False,
            'new_model_queries': 0, 'generated_holdouts_opened': False}.items()):
        raise ValueError('completed immutable numerical audit differs')
    return audit


def seal(config, review_sha256, fit_source_snapshot):
    """Create only a compact receipt for explicitly pinned completed results.

    Existing scientific artifacts are neither rewritten nor refitted. The caller
    supplies the original frozen fit source, not this newer reader's source.
    """
    _pin(review_sha256)
    registration, fit_source = _fit_registration(config, fit_source_snapshot)
    out = _safe(config['run_dir']); review_path = out/'review_v1.json'
    receipt_path = out/COMPLETION_NAME
    if receipt_path.exists():
        receipt = _json(receipt_path)
        if receipt.get('review', {}).get('sha256') != review_sha256 or receipt.get('fit_source') != fit_source:
            raise ValueError('existing compact completion receipt belongs to another result/source')
        completed_result(config)
        return receipt  # Preserve its original reader provenance; no new timestamp.
    review = _result_payload(review_path, review_sha256)
    _verify_result(config, review, registration)
    reader = code_identity()
    receipt = {'schema_version': 2, 'status': 'complete_exploratory', 'evaluation_role': ROLE,
        'config_hash': digest(config), 'capture_identity': registration['capture_identity'],
        'fit_source': fit_source, 'seal_reader_source': {k: reader[k] for k in ('source_sha256', 'git_revision') if k in reader},
        'registration': {'path': str(out/'registration.json'), 'sha256': _sha(out/'registration.json')},
        'review': {'path': str(review_path), 'sha256': review_sha256, 'bytes': review_path.stat().st_size},
        'artifacts': review['artifacts'], 'primary_comparison': review['primary_comparison'],
        'audit_status': 'passed', 'cases': SOURCE_CASES, 'retained_query_twins': SOURCE_CASES//2,
        'factorizations': 45, 'independent_heads': 180, 'parameter_count_per_head': 131104,
        'parameter_replay_rows': SOURCE_CASES*45, 'general_metadata_limit_bytes': 8*1024**2,
        'scientific_result_payload_limit_bytes': MAX_RESULT_BYTES, 'scientific_artifacts_changed': False,
        'new_fits': 0, 'new_model_queries': 0, 'behavioral_response_features': False,
        'generated_holdouts_opened': False, 'scope': 'Compact completion migration/read receipt; original scientific fit source and all 50 artifacts retained.'}
    immutable(receipt_path, _json_bytes(receipt)); return receipt


def completed_result(config):
    """Verify a compact receipt/source chain, then read pinned rich results."""
    _source_metadata(config)
    out = _safe(config['run_dir']); receipt = _json(out/COMPLETION_NAME)
    if any(receipt.get(k) != value for k, value in {'schema_version': 2, 'status': 'complete_exploratory',
            'evaluation_role': ROLE, 'config_hash': digest(config), 'audit_status': 'passed', 'cases': SOURCE_CASES,
            'factorizations': 45, 'independent_heads': 180, 'retained_query_twins': SOURCE_CASES//2,
            'parameter_count_per_head': 131104, 'parameter_replay_rows': SOURCE_CASES*45,
            'general_metadata_limit_bytes': 8*1024**2, 'scientific_result_payload_limit_bytes': MAX_RESULT_BYTES,
            'scientific_artifacts_changed': False, 'new_fits': 0, 'new_model_queries': 0,
            'behavioral_response_features': False, 'generated_holdouts_opened': False}.items()):
        raise ValueError('bounded compact completion role/config/count contract differs')
    source_pin = receipt.get('fit_source', {})
    if not isinstance(source_pin, dict) or not isinstance(source_pin.get('snapshot'), str):
        raise ValueError('compact completion requires an original frozen fit source')
    registration, fit_source = _fit_registration(config, source_pin['snapshot'])
    if source_pin != fit_source or receipt.get('capture_identity') != registration['capture_identity']:
        raise ValueError('compact completion original source/capture differs')
    reg_pin = receipt.get('registration', {})
    review_pin = receipt.get('review', {})
    if (not isinstance(reg_pin, dict) or set(reg_pin) != {'path', 'sha256'}
            or _safe(reg_pin['path']).resolve() != (out/'registration.json').resolve()
            or _sha(out/'registration.json') != _pin(reg_pin['sha256'])
            or not isinstance(review_pin, dict) or set(review_pin) != {'path', 'sha256', 'bytes'}
            or _safe(review_pin['path']).resolve() != (out/'review_v1.json').resolve()
            or review_pin['bytes'] != (out/'review_v1.json').stat().st_size):
        raise ValueError('compact completion canonical registration/review pins differ')
    _artifact_inventory(config, receipt.get('artifacts'))  # Before rich payload access.
    review = _result_payload(out/'review_v1.json', review_pin['sha256'])
    if review.get('artifacts') != receipt['artifacts'] or review.get('primary_comparison') != receipt.get('primary_comparison'):
        raise ValueError('compact completion differs from pinned scientific result')
    _verify_result(config, review, registration)
    return review


def _current_fit_snapshot():
    from .registry import ROOT
    if not (ROOT/'frozen_manifest.json').is_file():
        raise ValueError('new scientific readout fits require a frozen source snapshot')
    return str(ROOT)


def _reuse(config, source):
    registration = _json(Path(config['run_dir'])/'registration.json')
    if registration.get('analysis_source') != source:
        raise ValueError('run reuse cannot change the original scientific fit source')
    receipt = Path(config['run_dir'])/COMPLETION_NAME
    if not receipt.exists():
        seal(config, _sha(Path(config['run_dir'])/'review_v1.json'), _current_fit_snapshot())
    result = completed_result(config)
    if result['analysis_source'] != source: raise ValueError('scientific fit source differs from current run')
    return result


def _report(result):
    lines = ['# Queried versus unqueried discovery readouts', '', LIMITATION, '',
        'All 9,216 rows, including both query twins, are retained at every site. '
        'Neutral training uses 2,304 rows and 18 structural groups; each development naming condition '
        'has 768 rows and six groups. Each of four independent heads has 32 classes and '
        '131,104 coefficient/intercept parameters. A shared Cholesky factorization changes computation cost, '
        'not per-head capacity or the independent summed ridge objective.', '',
        f"Primary paired accuracy increment: {result['primary_comparison']['mean_group_increment']:.6f}; "
        f"conditional group interval {result['primary_comparison']['conditional_group_bootstrap_95']}.", '',
        '| Backend | Layer | Site | Development naming | Queried | Unqueried | Shuffled queried | Shuffled unqueried | Whole pair |',
        '|---|---:|---|---|---:|---:|---:|---:|---:|']
    aggregate = defaultdict(list)
    for fit in result['fits']:
        for cell in fit['cells']:
            if cell['split'] == 'development' and cell['query_role'] == 'all':
                aggregate[fit['backend'], fit['layer'], fit['site'], cell['condition']].append(cell)
    for key, cells in sorted(aggregate.items()):
        backend, layer, site, condition = key
        means = [float(np.mean([cell['heads'][h]['accuracy'] for cell in cells])) for h in range(4)]
        pair = float(np.mean([cell['canonical_reconstruction']['value']['whole_pair_accuracy'] for cell in cells]))
        lines.append(f'| {backend} | {layer} | {site} | {condition} | '+
            ' | '.join(f'{v:.4f}' for v in [*means, pair])+' |')
    lines += ['', 'The table averages three fixed weighting fits. Full training/development, '
        'query-role, class-support, canonical-slot and numerical symmetry cells remain in JSON and CSV.', '',
        f"{result['factorizations']} shared factorizations fit {result['independent_heads']} independent heads. "
        f"All {result['parameter_replay_rows']} saved-model row replays passed exactly.", '',
        'No original final/extrapolation outcome was evaluated, and no language model was loaded or trained.', '']
    return '\n'.join(lines)


def run(config):
    checked = preflight(config)
    if not os.environ.get('SLURM_JOB_ID'):
        raise RuntimeError('real capture readout fits require an sbatch CPU worker')
    fit_snapshot = _current_fit_snapshot()
    source = code_identity(); out = _safe(config['run_dir']); out.mkdir(parents=True, exist_ok=True)
    immutable(out/'registration.json', _json_bytes({'evaluation_role': ROLE, 'config': config,
        'config_hash': digest(config), 'analysis_source': source, 'capture_identity': checked['capture_identity'],
        'fixed_recipe': checked['fixed_recipe'], 'behavioral_response_features': False, 'new_model_queries': 0,
        'generated_holdouts_opened': False, 'limitation': LIMITATION}))
    if (out/'review_v1.json').exists(): return _reuse(config, source)
    from .weighted_ridge import fit, from_parameters
    from sklearn.feature_extraction.text import HashingVectorizer
    from threadpoolctl import threadpool_limits
    import sklearn
    started = time.monotonic(); vectors, rows, pairs, capture, coverage = _load(config)
    train = np.array([r['split'] == 'train' and r['condition'] == 'neutral' for r in rows])
    train_rows = [r for r, keep in zip(rows, train) if keep]; train_ids = [r['id'] for r in train_rows]
    case_ids_sha = digest([r['id'] for r in rows]); expected = _expected(config)
    fields = ('id', 'base_id', 'template_id', 'split', 'condition', 'query_role', 'lexical_realization',
        'available_bindings', 'updates', 'tail_placement', 'targets', 'state_prefix_sha256')
    immutable(expected['cases'], ''.join(json.dumps({key: row[key] for key in fields}, sort_keys=True)+'\n' for row in rows).encode())
    fits = []; artifacts = {}; primary_differences = {}; total_replays = 0
    threads = int(os.environ.get('SLURM_CPUS_PER_TASK', '8'))
    if threads < 1: raise ValueError('positive scheduler CPU allocation required')
    with threadpool_limits(limits=threads):
        for site_index, site in enumerate(SITES):
            texts = [r['visible_prefixes'][site_index] for r in rows]
            vectorizer = HashingVectorizer(analyzer='char', ngram_range=(3, 8), n_features=4096,
                alternate_sign=True, norm=None, dtype=np.float64)
            surface = vectorizer.transform(texts).toarray()
            if site_index == 0 and not np.array_equal(surface[pairs[:, 0]], surface[pairs[:, 1]]):
                raise ValueError('pre-query surface twins differ')
            candidates = [('hidden', layer, vectors[:, index, site_index]) for index, layer in enumerate(LAYERS)]
            candidates.append(('surface', -1, surface))
            for backend, layer, x in candidates:
                for seed in SEEDS:
                    labels, truth, canonical, shuffled, mapping = targets(rows, seed)
                    weights = group_weights(train_rows, seed).astype(np.float64)
                    hist = marginal_audit(rows, labels, train, weights, pairs)
                    model = fit(np.asarray(x[train], dtype=np.float64), truth[train], weights,
                        train_ids=train_ids, split='train', alpha=100.)
                    scores = model.predict(x); predictions = _predictions(scores)
                    symmetry = prequery_symmetry(x, truth, train, weights, model, scores, pairs) if site_index == 0 else None
                    name = fit_name(backend, layer, site_index, seed); path = expected[name]
                    arrays = {**model.parameters, 'model_metadata': np.frombuffer(_json_bytes(model.metadata), dtype=np.uint8),
                        'case_ids_sha256': np.array(case_ids_sha), 'labels': labels.astype(np.int16),
                        'canonical_labels': canonical.astype(np.int16), 'shuffled_canonical_labels': shuffled.astype(np.int16),
                        'raw_scores': scores, 'predictions': predictions.astype(np.int16), 'training_weights': weights}
                    _npz(path, arrays)
                    with np.load(path, allow_pickle=False) as saved:
                        restored = from_parameters(json.loads(saved['model_metadata'].tobytes()), {key: saved[key] for key in model.parameters})
                        replay = restored.predict(x)
                        if (str(saved['case_ids_sha256'].item()) != case_ids_sha or not np.array_equal(saved['labels'], labels)
                                or not np.array_equal(replay, saved['raw_scores']) or not np.array_equal(saved['raw_scores'], scores)
                                or not np.array_equal(_predictions(replay), saved['predictions'])):
                            raise ValueError('saved query-selectivity parameters, scores or predictions fail exact replay')
                    total_replays += len(rows)
                    artifacts[name] = {'path': str(path), 'sha256': _sha(path)}
                    metadata = model.metadata; metadata.pop('training_ids')
                    fits.append({'name': name, 'artifact': str(path), 'backend': backend, 'layer': layer,
                        'site': site, 'seed': seed, 'model': metadata, 'marginal_audit': hist,
                        'shuffle_donor_base_mapping': mapping, 'prequery_symmetry': symmetry,
                        'cells': metric_cells(rows, labels, canonical, shuffled, predictions, train)})
                    if backend == 'hidden' and layer == PRIMARY['layer'] and site == PRIMARY['site']:
                        primary_differences[seed] = (predictions[:, 0] == labels[:, 0]).astype(float)-(predictions[:, 1] == labels[:, 1])
                    print(f'query selectivity {name}', flush=True)
    primary = primary_bootstrap(rows, primary_differences)
    result = {'status': 'complete_exploratory', 'evaluation_role': ROLE, 'config_hash': digest(config),
        'analysis_source': source, 'capture_identity': checked['capture_identity'], 'model': capture['model'],
        'model_revision': capture['model_revision'], 'coverage': coverage, 'cases': len(rows),
        'case_ids_sha256': case_ids_sha, 'retained_query_twins': len(pairs), 'fits': fits,
        'factorizations': len(fits), 'independent_heads': 4*len(fits), 'parameter_count_per_head': 32*(4096+1),
        'parameter_replay_rows': total_replays, 'class_values': CLASSES.tolist(), 'heads': list(HEADS),
        'primary_comparison': primary, 'float64_standardization_and_fitting': True,
        'readout_features': '4096 raw block coordinates or matched 4096 character-ngram features from the visible prefix only',
        'query_role_is_feature': False, 'behavioral_response_features': False, 'source_response_metadata_validated': True,
        'canonical_reconstruction_definition': CANONICAL_RECONSTRUCTION,
        'new_model_queries': 0, 'generated_holdouts_opened': False, 'mechanism_C_fitted': False,
        'runtime': {'threads': threads, 'slurm_cpus_per_task': os.environ.get('SLURM_CPUS_PER_TASK'),
            'slurm_job_id': os.environ.get('SLURM_JOB_ID'), 'numpy_version': np.__version__, 'sklearn_version': sklearn.__version__},
        'limitation': LIMITATION}
    if result['factorizations'] != 45 or result['independent_heads'] != 180:
        raise ValueError('full registered readout fit matrix incomplete')
    immutable(expected['summary'], _json_bytes(result)); immutable(expected['report'], _report(result).encode())
    flat = []
    for item in fits:
        for cell in item['cells']:
            for head in cell['heads']:
                flat.append({'backend': item['backend'], 'layer': item['layer'], 'site': item['site'], 'seed': item['seed'],
                    **{key: cell[key] for key in ('split', 'condition', 'query_role', 'n', 'structural_groups')},
                    **{key: value for key, value in head.items() if key not in ('template_cells', 'training_class_counts', 'evaluation_class_counts')},
                    **{'canonical_'+key: value for key, value in cell['canonical_reconstruction']['value'].items()}})
    stream = io.StringIO(); writer = csv.DictWriter(stream, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    immutable(expected['cells'], stream.getvalue().encode())
    audit = {'status': 'passed', 'config_hash': digest(config), 'capture_identity': checked['capture_identity'],
        'factorizations': len(fits), 'independent_heads': 4*len(fits), 'parameter_replay_rows': total_replays,
        'serialized_raw_scores_and_predictions_exact': True, 'complete_query_twins_all_sites': True,
        'per_head_classes': 32, 'parameter_count_per_head': 32*(4096+1),
        'prequery_score_tolerance_absolute': TOLERANCE, 'behavioral_response_features': False,
        'new_model_queries': 0, 'generated_holdouts_opened': False,
        'scope': 'Pinned full discovery captures, exact ordered IDs/targets/visible prefixes, equal label/weight marginals, train-only fixed weighted fits, raw pre-query symmetry/tie diagnostics and exact saved-model score/prediction replays.'}
    immutable(expected['audit'], _json_bytes(audit))
    for name, path in expected.items():
        if name not in artifacts: artifacts[name] = {'path': str(path), 'sha256': _sha(path)}
    result.update(artifacts=artifacts, wall_seconds=time.monotonic()-started)
    review_path = out/'review_v1.json'
    immutable(review_path, _json_bytes(result))
    seal(config, _sha(review_path), fit_snapshot)
    return result


def audit(config):
    """Verify a completed fixed inventory and its immutable numerical audit."""
    review = completed_result(config)
    return _json(review['artifacts']['audit']['path'], review['artifacts']['audit']['sha256'])
