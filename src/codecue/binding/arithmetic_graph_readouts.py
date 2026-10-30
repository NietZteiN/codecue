"""TRAIN-only arithmetic dependency/relation readouts with saved parameters.

Every target comes from the visible prefix. Hidden and source pipelines receive
the same readout objective. All fitted parameter banks and DEV scores persist.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations, permutations
import io
import json
from pathlib import Path

import numpy as np

from . import arithmetic_graph_programs as programs, arithmetic_graph_capture as capture
from . import relationship_capture as base
from .datasets import digest
from .weighted_ridge import fit, from_parameters

ROLE = 'discovery_arithmetic_graph_readouts_v1'
SEEDS = (11, 29, 47)
VALUE_CLASSES = np.arange(-96, 97)
PAIRS = tuple(combinations(range(4), 2))
RELATIONS = tuple([('equal', a, b) for a, b in PAIRS] + [('less_than', a, b) for a, b in PAIRS] +
    [('sum', a, b, c) for a, b in PAIRS for c in range(4) if c not in (a, b)] +
    [('difference', a, b, c) for a, b, c in permutations(range(4), 3)])


def relations(values):
    values = np.asarray(values)
    columns = []
    for family, a, b, *tail in RELATIONS:
        if family == 'equal': result = values[:, a] == values[:, b]
        elif family == 'less_than': result = values[:, a] < values[:, b]
        elif family == 'sum': result = values[:, a]+values[:, b] == values[:, tail[0]]
        else: result = values[:, a]-values[:, b] == values[:, tail[0]]
        columns.append(result)
    return np.asarray(columns).T


def targets(rows, site):
    truth = [programs.oracle(row['canonical_source'], 3 if site == 0 else 7) for row in rows]
    values = np.asarray([t['values'] for t in truth])
    binary = relations(values)
    parts = [binary.astype(float)]
    heads = []
    offset = len(RELATIONS)
    for kind, labels, count in [
        ('value', values+96, 193),
        ('definition', np.asarray([t['definitions'] for t in truth]), 8),
        ('version', np.asarray([t['versions'] for t in truth])-1, 5),
        *([('parent', np.asarray([t['parents'] for t in truth]), 8)] if site else [])]:
        for slot in range(labels.shape[1]):
            if np.any(labels[:, slot] < 0) or np.any(labels[:, slot] >= count):
                raise ValueError('categorical target domain exceeded')
            parts.append(np.eye(count)[labels[:, slot]])
            heads.append(dict(kind=kind, slot=slot, start=offset, stop=offset+count))
            offset += count
    differences = np.asarray([values[:, a]-values[:, b] for a, b in PAIRS]).T
    parts.append(differences.astype(float))
    return np.concatenate(parts, axis=1), binary, values, heads, differences


def donor_indices(rows):
    """Whole-family derangements, identical relative coordinates within a split."""
    families = sorted({r['component_id'] for r in rows})
    indices = {(r['component_id'], r['numeric_seed'], r['numeric_draw'], r['lexical_realization'], r['query_slot']): i
               for i, r in enumerate(rows)}
    donor = np.zeros(len(rows), dtype=int)
    for split in ('train', 'development'):
        names = [g for g in families if next(r['split'] for r in rows if r['component_id'] == g) == split]
        rng = np.random.default_rng(117)
        names = [names[i] for i in rng.permutation(len(names))]
        mapping = dict(zip(names, names[1:]+names[:1]))
        for i, row in enumerate(rows):
            if row['split'] == split:
                donor[i] = indices[(mapping[row['component_id']], row['numeric_seed'], row['numeric_draw'],
                                    row['lexical_realization'], row['query_slot'])]
    if sorted(donor.tolist()) != list(range(len(rows))) or np.any(donor == np.arange(len(rows))):
        raise ValueError('complete split-preserving derangement required')
    return donor


def _decode(scores, heads, kind):
    selected = [h for h in heads if h['kind'] == kind]
    return np.asarray([np.argmax(scores[:, h['start']:h['stop']], axis=1) for h in selected]).T


def summarize(scores, y, binary, values, heads, differences, eligible, mask):
    result = {}
    family_scores = defaultdict(list)
    cells = []
    for index, relation in enumerate(RELATIONS):
        truth, predicted = binary[mask, index], scores[mask, index] >= .5
        positive, negative = int(truth.sum()), int((~truth).sum())
        score = float(((predicted[truth] == truth[truth]).mean() +
                       (predicted[~truth] == truth[~truth]).mean())/2) if positive and negative else None
        cells.append(dict(relation=list(relation), positive=positive, negative=negative,
                          eligible_from_train=bool(eligible[index]), balanced_accuracy=score))
        if eligible[index] and score is not None:
            family_scores[relation[0]].append(score)
    result['relations'] = dict(family_balanced_accuracy={k: float(np.mean(v)) for k, v in family_scores.items()},
        macro_balanced_accuracy=float(np.mean([np.mean(v) for v in family_scores.values()])) if family_scores else None,
        supported_cells=sum(map(len, family_scores.values())), cells=cells)
    decoded_values = _decode(scores, heads, 'value')-96
    derived = relations(decoded_values)
    derived_families = defaultdict(list)
    for i, relation in enumerate(RELATIONS):
        t = binary[mask, i]
        if eligible[i] and t.any() and (~t).any():
            derived_families[relation[0]].append(float(((derived[mask, i][t] == t[t]).mean()+
                                                       (derived[mask, i][~t] == t[~t]).mean())/2))
    result['value_derived_relation_macro_balanced_accuracy'] = float(np.mean([np.mean(v) for v in derived_families.values()])) if derived_families else None
    result['value_accuracy'] = float((decoded_values[mask] == values[mask]).mean())
    result['whole_state_accuracy'] = float((decoded_values[mask] == values[mask]).all(axis=1).mean())
    for kind in ('definition', 'version', 'parent'):
        selected = [h for h in heads if h['kind'] == kind]
        if not selected:
            continue
        predicted = _decode(scores, heads, kind)
        truth = _decode(y, heads, kind)
        result[kind+'_accuracy'] = float((predicted[mask] == truth[mask]).mean())
        result['whole_'+kind+'_accuracy'] = float((predicted[mask] == truth[mask]).all(axis=1).mean())
        if kind == 'parent':
            p, t = predicted[mask].reshape(-1, 4, 2), truth[mask].reshape(-1, 4, 2)
            result['whole_unordered_parent_graph_accuracy'] = float((np.sort(p, axis=2) == np.sort(t, axis=2)).all(axis=(1, 2)).mean())
            result['valid_past_parent_graph_fraction'] = float((p < np.arange(4, 8)[None, :, None]).all(axis=(1, 2)).mean())
    result['signed_difference_mae'] = float(np.abs(scores[mask, -6:]-differences[mask]).mean())
    return result


def _pin(path):
    path = Path(path)
    return dict(path=str(path), sha256=base._sha(path), bytes=path.stat().st_size)


def _npz(path, **arrays):
    stream = io.BytesIO()
    np.savez_compressed(stream, **arrays)
    base._publish(path, stream.getvalue())


def audit(config):
    folder = Path(config['run_dir'])
    receipt = base._json(folder/'completion_manifest_v1.json')
    if receipt['config_hash'] != digest(config) or receipt['status'] != 'complete_exploratory':
        raise ValueError('readout receipt identity differs')
    base._verify_source(config, receipt['source'])
    for entry in receipt['artifacts'].values():
        if Path(entry['path']).stat().st_size != entry['bytes'] or base._sha(entry['path']) != entry['sha256']:
            raise ValueError('readout artifact changed')
    result = base._json(folder/'results.json')
    if result.get('config_hash') != digest(config) or len(result.get('fits', [])) != 18:
        raise ValueError('complete fixed readout grid required')
    for bank in result['fits']:
        for entry in bank['artifacts'].values():
            if Path(entry['path']).stat().st_size != entry['bytes'] or base._sha(entry['path']) != entry['sha256']:
                raise ValueError('readout bank payload changed')
    return receipt


def run(config):
    from .confidence import _run_lock
    from sklearn.feature_extraction.text import HashingVectorizer
    base._slurm()
    source = base._current_source(config)
    if config.get('evaluation_role') != ROLE or config.get('alpha') != 100. or config.get('seeds') != list(SEEDS):
        raise ValueError('fixed arithmetic ridge recipe required')
    cap = base._json(config['capture_config'], config['capture_config_sha256'])
    folder = Path(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder/'completion_manifest_v1.json').exists():
            return audit(config)
        capture.audit(cap)
        preflight, cases = capture.inputs(cap)
        rows, _ = capture._CORE._dataset(cap)
        if source != preflight['source']:
            raise ValueError('readout/capture frozen source differs')
        manifest = base._json(Path(cap['run_dir'])/'summary.json')
        layer_index = cap['layers'].index(config['primary_layer'])
        # Keep just the nominated layer in RAM; other captured layers are archived.
        vectors = np.empty((len(rows), 3, cap['hidden_size']), dtype=np.float32)
        for entry in manifest['chunks']:
            first = entry['first']
            chunk, _ = capture.load_chunk(entry, cases[first:first+entry['rows']], cap)
            vectors[first:first+entry['rows']] = chunk[:, :, layer_index]
        train = np.asarray([r['split'] == 'train' for r in rows])
        dev = ~train
        ids = [r['id'] for r in rows]
        groups = np.asarray([r['component_id'] for r in rows])
        donor = donor_indices(rows)
        all_fits, artifacts = [], {}
        for site in range(3):
            y, binary, values, heads, differences = targets(rows, site)
            # Count unique numeric bodies, not lexical/query repeats, for support.
            unique = np.asarray([r['split'] == 'train' and r['lexical_realization'] == 0 and r['query_slot'] == 0 for r in rows])
            eligible = (binary[unique].sum(axis=0) >= 12) & ((~binary[unique]).sum(axis=0) >= 12)
            surface = HashingVectorizer(analyzer='char', ngram_range=(3, 8), n_features=cap['hidden_size'],
                alternate_sign=True, norm=None).transform(c['visible_prefixes'][site] for c in cases).toarray().astype(np.float32)
            for backend, x in [('hidden', vectors[:, site]), ('source', surface)]:
                for seed in SEEDS:
                    key = f'site{site}_{backend}_seed{seed}'
                    marker = folder/(key+'.json')
                    if marker.exists():
                        saved = base._json(marker)
                        if saved['config_hash'] != digest(config) or saved['source'] != source:
                            raise ValueError('readout resume bank identity differs')
                        for entry in saved['artifacts'].values():
                            if base._sha(entry['path']) != entry['sha256']:
                                raise ValueError('saved readout bank changed')
                        all_fits.append(saved)
                        artifacts[key] = _pin(marker)
                        continue
                    rng = np.random.default_rng(seed)
                    weights_by_group = dict(zip(sorted(set(groups[train])), rng.exponential(1., len(set(groups[train])))+.1))
                    weights = np.asarray([weights_by_group[g] for g in groups[train]])
                    joined = np.concatenate((y[train], y[donor[train]]), axis=1)
                    model = fit(x[train], joined, weights, train_ids=np.asarray(ids)[train].tolist(), split='train', alpha=100.)
                    parameter_path = folder/(key+'_parameters.npz')
                    _npz(parameter_path, **model.parameters)
                    with np.load(parameter_path, allow_pickle=False) as stored:
                        replay = from_parameters(model.metadata, {k: stored[k] for k in model.parameters})
                    scores = model.predict(x)
                    if not np.array_equal(scores, replay.predict(x)):
                        raise ValueError('saved parameter replay differs')
                    real, shuffled = np.split(scores, 2, axis=1)
                    prior = np.broadcast_to(np.average(y[train], axis=0, weights=weights), y.shape)
                    metrics = {name: summarize(pred, truth, labels, vals, heads, diffs, eligible, dev)
                        for name, pred, truth, labels, vals, diffs in [
                            ('direct', real, y, binary, values, differences),
                            ('train_prior', prior, y, binary, values, differences),
                            ('coherent_shuffle', shuffled, y[donor], binary[donor], values[donor], differences[donor]) ]}
                    group_metrics = {g: summarize(real, y, binary, values, heads, differences, eligible, dev & (groups == g))
                                     for g in sorted(set(groups[dev]))}
                    scores_path = folder/(key+'_scores.npz')
                    _npz(scores_path, dev_indices=np.flatnonzero(dev), real=real[dev], shuffled=shuffled[dev],
                         truth=y[dev], shuffle_truth=y[donor[dev]], eligible=eligible, donor=donor,
                         ordered_case_ids=np.asarray(ids))
                    saved = dict(status='complete_exploratory', config_hash=digest(config), source=source,
                        site=site, backend=backend, seed=seed, metrics=metrics, development_family_metrics=group_metrics,
                        target_heads=heads, relation_columns=[list(r) for r in RELATIONS],
                        ridge_metadata=model.metadata,
                        fitted_scalar_outputs=joined.shape[1], parameter_replay_rows=len(rows),
                        artifacts=dict(parameters=_pin(parameter_path), scores=_pin(scores_path)))
                    base._put(marker, saved)
                    all_fits.append(saved)
                    artifacts[key] = _pin(marker)
                    capture._CORE._journal(folder/'progress.json', dict(fits=len(all_fits), planned=18))
                    print(f'arithmetic readouts {key}: {len(all_fits)}/18', flush=True)
        # Average weighting seeds within each family, then resample families.
        contrasts = []
        groups_dev = sorted(set(groups[dev]))
        samples = np.random.default_rng(117).integers(0, len(groups_dev), (2000, len(groups_dev)))
        for site in range(3):
            for metric in ('whole_parent_accuracy', 'whole_state_accuracy', 'value_accuracy'):
                if site == 0 and metric == 'whole_parent_accuracy':
                    continue
                grouped = {}
                for backend in ('hidden', 'source'):
                    selected = [f for f in all_fits if f['site'] == site and f['backend'] == backend]
                    grouped[backend] = np.asarray([np.mean([f['development_family_metrics'][g][metric] for f in selected]) for g in groups_dev])
                delta = grouped['hidden']-grouped['source']
                contrasts.append(dict(site=site, metric=metric, hidden=float(grouped['hidden'].mean()),
                    source=float(grouped['source'].mean()), hidden_minus_source=float(delta.mean()),
                    conditional_family_bootstrap_95=np.quantile(delta[samples].mean(axis=1), [.025, .975]).tolist()))
        result = dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=digest(config), source=source,
            model=cap['model'], cases=len(rows), fits=all_fits, factorizations=len(all_fits), contrasts=contrasts,
            primary_layer=config['primary_layer'], new_model_queries=0, generated_holdouts_opened=False,
            relation_summary='All 48 cells retained; balanced metrics use TRAIN-supported cells with both DEV classes. Compare direct and value-derived pipelines.',
            limitations='Adaptive discovery. Statement skeleton supplied. Source character baseline is not every possible source algorithm; interpreter ceiling is 100%. No natural causal-use claim. Intervals conditional on fixed fits; no multiplicity correction.')
        base._put(folder/'results.json', result)
        artifacts['results'] = _pin(folder/'results.json')
        text = ['# Two-input arithmetic relationship readouts', '', result['limitations'], '',
                '| Site | Backend | Seed | Relation balanced accuracy | Value-derived relations | Whole parent graph | Whole state |',
                '|---|---|---:|---:|---:|---:|---:|']
        for bank in all_fits:
            m = bank['metrics']['direct']
            def number(value): return '' if value is None else f'{100*value:.3f}%'
            text.append(f"| {bank['site']} | {bank['backend']} | {bank['seed']} | {number(m['relations']['macro_balanced_accuracy'])} | {number(m['value_derived_relation_macro_balanced_accuracy'])} | {number(m.get('whole_parent_accuracy'))} | {number(m['whole_state_accuracy'])} |")
        base._publish(config['report'], ('\n'.join(text)+'\n').encode())
        artifacts['report'] = _pin(config['report'])
        base._put(folder/'completion_manifest_v1.json', dict(status='complete_exploratory', evaluation_role=ROLE,
            config_hash=digest(config), source=source, cases=len(rows), artifacts=artifacts, new_model_queries=0))
        return result
