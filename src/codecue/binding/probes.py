"""Capacity-controlled shared linear state decoders with train-only preprocessing.

Primary estimator: ridge regression of canonical values, rounded to [-64,64].
Value recovery, obsolete-version recovery and sorted-multiset recovery use separate
slot-count-matched fits with identical capacity. Slot indexing is a measurement convention.
"""
from __future__ import annotations
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
from .datasets import read_jsonl, write_json
from .registry import guarded


def fit_ridge(x, y, alpha=1.0):
    # Fit normalization and every slot's mask using training rows only.
    mu, sd = x.mean(0), x.std(0).clip(1e-5)
    z = (x - mu) / sd
    width = y.shape[1]
    weights = np.zeros((x.shape[1], width), dtype=np.float64)
    intercept = np.zeros(width)
    for slot in range(width):
        mask = np.isfinite(y[:, slot])
        if not mask.any():
            continue
        a, b = z[mask], y[mask, slot]
        # Masking can move the feature mean away from the shared training mean.
        # Center the valid rows so the unpenalized intercept remains correct.
        feature_mean = a.mean(0)
        label_mean = b.mean()
        a = a - feature_mean
        b = b - label_mean
        if len(a) < a.shape[1]:
            weights[:, slot] = a.T @ np.linalg.solve(a @ a.T + alpha * np.eye(len(a)), b)
        else:
            weights[:, slot] = np.linalg.solve(a.T @ a + alpha * np.eye(a.shape[1]), a.T @ b)
        intercept[slot] = label_mean - feature_mean @ weights[:, slot]
    return (mu, sd, weights, intercept)


def predict(model, x):
    mu, sd, weights, intercept = model
    return np.rint(((x - mu) / sd) @ weights + intercept).clip(-64, 64)


def metrics(pred, gold):
    if pred.shape != gold.shape:
        raise ValueError('probe output slots do not match evaluation labels')
    mask = np.isfinite(gold)
    whole = mask.all(1)
    return {'slot_exact_accuracy': float((pred[mask] == gold[mask]).mean()) if mask.any() else None,
            'whole_state_accuracy': float((pred[whole] == gold[whole]).all(1).mean()) if whole.any() else None,
            'mae': float(np.abs(pred[mask] - gold[mask]).mean()) if mask.any() else None,
            'defined_slot_labels': int(mask.sum()), 'complete_states': int(whole.sum())}


def surface_features(record, width=128):
    # Cheap token bag and visible syntax features. No semantic oracle values.
    import ast
    import re
    x = np.zeros(width + 4, dtype=np.float64)
    for token in re.findall(r'\w+|[^\s\w]', record['source']):
        index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], 'little') % width
        x[index] += 1
    tree = ast.parse(record['source'])
    x[-4:] = [len(record['source']), sum(isinstance(n,ast.BinOp) for n in ast.walk(tree)),
              sum(isinstance(n,ast.Assign) for n in tree.body), record['updates']]
    return x


def check_cache_identity(cache_manifest, manifest, config):
    """Permit an explicitly pinned cache for a separately versioned analysis."""
    analysis = config.get('probe_analysis', {})
    expected = analysis.get('cache_source_sha256')
    cache_code = cache_manifest['identity']['code']
    if expected:
        if cache_code['source_sha256'] != expected:
            raise ValueError('pinned activation source checksum mismatch')
    elif cache_code != manifest['identity']['code']:
        raise ValueError('activation cache identity mismatch')
    extraction_config = {k:v for k,v in config.items() if k != 'probe_analysis'}
    cached_config={k:v for k,v in cache_manifest['identity']['config'].items() if k != 'probe_analysis'}
    if cached_config != extraction_config:
        raise ValueError('activation cache configuration mismatch')


def source_at_site(record, site):
    if site=='definition_pool':
        from .readouts import definition_surface_source
        return dict(record,source=definition_surface_source(record))
    if site != 'last_assignment':
        return record
    # The query has not arrived at this checkpoint. Give the surface baseline
    # the same source prefix as the hidden-state measurement.
    result = dict(record)
    result['source'] = '\n'.join(record['source'].splitlines()[:-1])
    return result


@guarded
def fit(config):
    from .registry import begin, finish
    stage = config.get('probe_analysis', {}).get('output_stage', 'probes')
    import re
    if not re.fullmatch(r'probes(?:_[a-zA-Z0-9_-]+)?', stage):
        raise ValueError('invalid probe analysis stage')
    out, manifest = begin(config, stage)
    started = time.monotonic()
    cache = Path(config['run_dir']) / 'activations'
    cache_manifest = json.loads((cache / 'manifest.json').read_text())
    if cache_manifest['status'] != 'complete':
        raise ValueError('activation extraction must be complete before probe fitting')
    check_cache_identity(cache_manifest, manifest, config)
    index = [r for r in read_jsonl(cache / 'index.jsonl') if r['control_kind'] == 'primary']
    if any(r['split'] == 'test' for r in index):
        raise ValueError('probe selection cannot open the sealed test')
    records = {r['id']: r for r in read_jsonl(config['dataset'])}
    alpha=float(config.get('probe_analysis',{}).get('alpha',1.0))
    if not np.isfinite(alpha) or alpha<=0:
        raise ValueError('probe ridge penalty must be finite and positive')
    train_conditions=config.get('probe_analysis',{}).get('train_conditions',('neutral','informative','misleading'))
    if not train_conditions or not set(train_conditions) <= {'neutral','informative','misleading'}:
        raise ValueError('invalid probe training conditions')
    results = []
    readouts=config.get('probe_analysis',{}).get('readouts',['last_assignment','source_final'])
    if not readouts or len(set(readouts))!=len(readouts) or not set(readouts)<={'last_assignment','source_final','definition_pool'}:
        raise ValueError('declare unique supported probe readouts')
    readout_seed=config.get('probe_analysis',{}).get('readout_seed',17)
    if type(readout_seed) is not int:raise ValueError('readout projection seed must be an integer')
    # Prefix sites share final assignment labels; only source_final reveals the query.
    for site in readouts:
        for li, layer in enumerate(config['layers']):
            x, ys = [], {k: [] for k in ('current', 'previous', 'multiset')}
            for row in index:
                pi = len(row['sites']) - 1 if site == 'source_final' else len(row['sites']) - 2
                with np.load(cache / row['file']) as f:
                    if site=='definition_pool':
                        from .readouts import definition_pool
                        x.append(definition_pool(f['hidden'],row,records[row['id']],li,seed=readout_seed))
                    else:
                        x.append(f['hidden'][pi, li].astype(np.float64))
                point = row['checkpoints'][pi]
                for task in ys:
                    ys[task].append([np.nan if v is None else v for v in point[task]])
            x = np.array(x)
            surface = np.array([surface_features(source_at_site(records[r['id']], site)) for r in index])
            for task, labels in ys.items():
                y = np.array(labels, dtype=np.float64)
                width = y.shape[1]
                for train_condition in train_conditions:
                    train = np.array([i for i, r in enumerate(index) if r['split'] == 'train' and r['condition'] == train_condition])
                    if len(train) < 8:
                        raise ValueError('insufficient training rows for probe study; run extraction on full discovery data')
                    fitted = fit_ridge(x[train], y[train],alpha=alpha)
                    surface_fit = fit_ridge(surface[train], y[train],alpha=alpha)
                    majority = np.array([Counter(y[train, s][np.isfinite(y[train, s])]).most_common(1)[0][0]
                                         if np.isfinite(y[train, s]).any() else 0 for s in range(width)])
                    controls = []
                    for seed in (0, 1, 2):
                        # Base-keyed label tasks keep lexical relatives consistent; mapping is
                        # independent of semantic labels, structural split remains untouched.
                        draws = [int.from_bytes(hashlib.sha256(f'{seed}:{r["base_id"]}:{task}'.encode()).digest()[:4], 'little')
                                 for r in index]
                        random_y = y[train[np.array(draws) % len(train)]].copy()
                        for slot in range(width):
                            prior = y[train, slot][np.isfinite(y[train, slot])]
                            if len(prior):
                                missing = ~np.isfinite(random_y[:, slot]) & np.isfinite(y[:, slot])
                                random_y[missing, slot] = prior[np.array(draws)[missing] % len(prior)]
                        random_y[~np.isfinite(y)] = np.nan
                        controls.append((random_y, fit_ridge(x[train], random_y[train],alpha=alpha)))
                    for condition in ('neutral', 'informative', 'misleading'):
                        dev = np.array([i for i, r in enumerate(index) if r['split'] == 'development' and r['condition'] == condition])
                        if not len(dev):
                            continue
                        pred = predict(fitted, x[dev])
                        surface_pred = predict(surface_fit, surface[dev])
                        majority_pred = np.tile(majority, (len(dev), 1))
                        control_preds = [(ry, predict(m, x[dev])) for ry,m in controls]
                        if task == 'multiset':
                            pred = np.sort(pred, axis=1)
                            surface_pred = np.sort(surface_pred, axis=1)
                            majority_pred = np.sort(majority_pred, axis=1)
                            control_preds = [(ry, np.sort(p, axis=1)) for ry,p in control_preds]
                        result = {'site': site, 'layer': layer, 'task': task, 'train_condition': train_condition,
                                  'evaluation_condition': condition, 'evaluation_split': 'development',
                                  'train_n': len(train), 'development_n': len(dev),
                                  'parameters': width * (x.shape[1] + 1), 'surface_parameters': width * (surface.shape[1] + 1),
                                  'alpha': alpha, 'linear': metrics(pred, y[dev]),
                                  'readout_seed':readout_seed if site=='definition_pool' else None,
                                  'surface': metrics(surface_pred, y[dev]),
                                  'majority': metrics(majority_pred, y[dev]),
                                  'label_prior': [dict(Counter(y[train,s][np.isfinite(y[train,s])])) for s in range(width)],
                                  'randomized_label_controls': [metrics(p, ry[dev]) for ry,p in control_preds],
                                  'ids': [index[i]['id'] for i in dev], 'predictions': pred.tolist()}
                        # JSON object keys must be built-in scalar types.
                        result['label_prior'] = [{str(int(k)): int(v) for k, v in p.items()} for p in result['label_prior']]
                        results.append(result)
                    filename = f'{site}_L{layer}_{task}_{train_condition}.npz'
                    np.savez(out / filename, mu=fitted[0], sd=fitted[1], weights=fitted[2], intercept=fitted[3])
            print(f'probes {site} L{layer}', flush=True)
    write_json(out / 'development_curves.json', {'results': results, 'selection_status': 'none; full development curves only',
               'estimator': f'one linear output per canonical slot; ridge, train-only standardization, alpha={alpha:g}, integer rounding',
               'numeric_precision': 'float64 fitting from float16 activation cache',
               'masked_intercept': 'valid training rows centered separately per output',
               'surface_information': 'assignment-only prefix at last_assignment; full source at source_final',
               'readouts':readouts,'readout_seed':readout_seed,
               'definition_pool':'syntax-selected latest assignment endings with a fixed slot-specific signed projection to one hidden width; surface controls receive slot/position markers; no execution labels select sites',
               'limitations': 'decoding measures accessibility; no evidence of natural use or absence from failed decoding'})
    finish(out, manifest, time.monotonic() - started, result_count=len(results),
           activation_cache_identity_hash=cache_manifest['identity_hash'],
           activation_index_sha256=hashlib.sha256((cache/'index.jsonl').read_bytes()).hexdigest())
    return {'development_curves': str(out / 'development_curves.json'), 'results': len(results)}
