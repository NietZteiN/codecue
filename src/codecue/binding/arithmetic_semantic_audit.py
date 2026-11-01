"""Independent no-fit postrun replay of alternate-semantics readouts."""
from pathlib import Path
import numpy as np
from . import arithmetic_semantic_controls as study

ROLE = 'discovery_semantic_postrun_audit_v1'


def equal(first, second):
    if isinstance(first, dict):
        return isinstance(second, dict) and set(first) == set(second) and all(equal(v, second[k]) for k, v in first.items())
    if isinstance(first, list):
        return isinstance(second, list) and len(first) == len(second) and all(equal(a, b) for a, b in zip(first, second))
    if isinstance(first, float): return isinstance(second, (float, int)) and np.isfinite(first) and np.isfinite(second) and abs(first - second) <= 1e-12
    return type(first) is type(second) and first == second


def independent_metrics(scores, truth, families):
    if scores.shape != (len(truth), 11) or not np.isfinite(scores).all(): raise ValueError('finite semantic scores required')
    def family_average(v):
        values = {str(f): np.asarray(v)[families == f].tolist() for f in sorted(set(families))}
        return float(sum(sum(v) / len(v) for v in values.values()) / len(values))
    output = dict(scalar=dict(exact=family_average(np.round(scores[:, 0]) == truth),
        mae=family_average(abs(scores[:, 0] - truth))))
    for name, begin, end, labels in [('sign', 1, 4, np.where(truth < 0, 0, np.where(truth == 0, 1, 2))),
            ('parity', 4, 6, np.remainder(truth, 2)), ('mod5', 6, 11, np.remainder(truth, 5))]:
        correct = scores[:, begin:end].argmax(axis=1) == labels
        classes, counts = np.unique(labels, return_counts=True)
        output[name] = dict(exact=family_average(correct),
            balanced_accuracy=float(sum(float(correct[labels == c].sum()) / int(n) for c, n in zip(classes, counts)) / len(classes)),
            support={str(int(c)): int(n) for c, n in zip(classes, counts)})
    return output


def worker(request):
    numeric, common, base = study.numeric, study.common, study.base
    config = base._json(request['path'], request['sha256']); common.completed(config)
    data = base._json(Path(config['run_dir']) / 'results.json')
    _, _, _, rows, cases = study.audit.load_cache(config)
    table = study.swap_examples(rows, cases); mask = np.asarray([e['role'] == 'computed_definition' for e in table])
    subset = common.mask_table(table, mask); values = np.asarray([e['value'] for e in table])
    control = values[numeric.controls(rows, table)][mask]; values = values[mask]
    split = np.asarray([e['split'] for e in subset]); train = split == 'train'; ti = np.flatnonzero(train)
    ids = np.asarray([e['case_id'] + ':definition:' + str(e['statement']) for e in subset]); groups = np.asarray([e['group'] for e in subset])
    folds = common.folds(common.mask_table(subset, train)); width = config['widths'][0]
    folder = Path(config['run_dir']); records = []
    for seed in numeric.SEEDS:
        for fold in range(3):
            fit, val = ti[folds != fold], ti[folds == fold]
            for alpha in numeric.ALPHAS:
                path = folder / f'width{width}_cv_seed{seed}_fold{fold}_alpha{int(alpha)}.json'
                bank = numeric.resume(path, config, data['source'])
                if bank is None: raise ValueError('missing semantic CV bank')
                metadata = base._json(bank['artifacts']['metadata']['path'])
                if (metadata['training_ids'] != ids[fit].tolist() or bank['fit_groups'] != sorted(set(groups[fit]))
                        or bank['validation_groups'] != sorted(set(groups[val]))): raise ValueError('semantic CV fold or TRAIN identities differ')
                with np.load(bank['artifacts']['parameters']['path'], allow_pickle=False) as z:
                    numeric.from_parameters(metadata, {k: z[k] for k in z.files})
                records.append(bank)
    selection = study._CORE.select(records)
    if selection != base._json(folder / f'width{width}_selection_review_v1.json')['encodings']:
        raise ValueError('semantic TRAIN selection changed')
    old = base._json(config['cache_config']['path'], config['cache_config']['sha256']); common.completed(old)
    cache = base._json(Path(old['run_dir']) / 'results.json')
    matrix = numeric.load_features(cache['features']['source' if config['backend'] == 'source' else 'raw'])
    feature = numeric.fold_source(matrix[mask], width) if config['backend'] == 'source' else matrix[mask]
    x = np.concatenate((feature, numeric.metadata_features(subset)), axis=1)
    count, max_error, scores = 0, 0., 0
    expected = {(s, a) for s in numeric.SEEDS for a in set(selection.values())}
    observed = set()
    for bank in data['fits']:
        key = (bank['seed'], bank['alpha'])
        if key in observed or key not in expected: raise ValueError('semantic selected grid differs')
        observed.add(key)
        if bank['selected_formats'] != [k for k in study.FORMATS if selection[k] == bank['alpha']]: raise ValueError('semantic selected heads differ')
        metadata = base._json(bank['artifacts']['metadata']['path'])
        if metadata['training_ids'] != ids[train].tolist(): raise ValueError('selected semantic TRAIN identities differ')
        with np.load(bank['artifacts']['parameters']['path'], allow_pickle=False) as z:
            model = numeric.from_parameters(metadata, {k: z[k] for k in z.files})
        with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
            if (not np.array_equal(z['ids'], ids) or not np.array_equal(z['split'], split)
                    or not np.array_equal(z['truth'], values) or not np.array_equal(z['control_truth'], control)):
                raise ValueError('semantic selected score labels/order differ')
            real, shuffled = z['real'], z['shuffled']
        predicted = model.predict(x); saved = np.concatenate((real, shuffled), axis=1)
        if not np.allclose(predicted, saved, rtol=1e-10, atol=1e-12): raise ValueError('semantic saved-model replay differs')
        max_error = max(max_error, float(np.max(abs(predicted - saved))))
        for actual, reference in [(predicted[:, :11], real), (predicted[:, 11:], shuffled)]:
            if not np.array_equal(np.rint(actual[:, 0]), np.rint(reference[:, 0])): raise ValueError('scalar decisions changed')
            for lo, hi in [(1, 4), (4, 6), (6, 11)]:
                if not np.array_equal(actual[:, lo:hi].argmax(axis=1), reference[:, lo:hi].argmax(axis=1)): raise ValueError('categorical decisions changed')
        for label in ('train', 'development', 'calibration'):
            m = split == label
            panels = dict(real=independent_metrics(real[m], values[m], groups[m]),
                control=independent_metrics(shuffled[m], control[m], groups[m]),
                prior=independent_metrics(np.broadcast_to(model.weighted_target_mean[:11], (int(m.sum()), 11)), values[m], groups[m]))
            if not equal(panels, bank[label]): raise ValueError('independent semantic metrics differ')
        count += 1; scores += int(predicted.size)
    if observed != expected or data['cv_banks'] != 27 or data['new_readout_fits'] != 27 + count:
        raise ValueError('semantic fit accounting differs')
    return dict(config=request, results=study.storage._pin(folder / 'results.json'), cv_banks=27,
        selected_banks=count, replayed_scores=scores, max_abs_difference=max_error)


def run(config):
    source = study.common.validate_role(config, ROLE); study.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return study.common.completed(config)
    report = study.base._json(config['semantic_report']['path'], config['semantic_report']['sha256']); study.common.completed(report)
    labels = study.base._json(report['prepared']['path'], report['prepared']['sha256']); proof = study.common.completed(labels)
    with np.load(proof['artifacts']['labels']['path'], allow_pickle=False) as z:
        definition = z['definition_values']; current = z['current_values']; final = z['final_values']
        if (not np.array_equal(definition[:, 0] % 2, definition[:, 1] % 2)
                or not np.array_equal(current[:, 0] % 2, current[:, 1] % 2)
                or not np.array_equal(final[:, 0] % 2, final[:, 1] % 2)):
            raise ValueError('plus/minus parity invariant violated')
        parity_checks = int(definition.shape[0] + current.shape[0] * 4 + final.shape[0] * 4)
    workers = [worker(c['alternate']) for c in report['comparisons']]
    result = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=study.digest(config),
        workers=workers, verified_cv_banks=sum(w['cv_banks'] for w in workers),
        replayed_selected_banks=sum(w['selected_banks'] for w in workers), parity_invariant_comparisons=parity_checks,
        replayed_scores=sum(w['replayed_scores'] for w in workers), max_abs_difference=max(w['max_abs_difference'] for w in workers),
        cv_scope='all CV parameter hashes, TRAIN ids and fold groups checked; selection recomputed; no CV score reapplication',
        ordinary_fits='reused with original numeric postrun audit; no duplicate refits',
        new_model_queries=0, new_fits=0, generated_holdouts_opened=False)
    lines = ['# Alternate-semantics postrun review', '',
        f"Replayed {result['replayed_selected_banks']} selected banks and {result['replayed_scores']:,} saved scores; "
        f"verified {result['verified_cv_banks']} CV banks and recomputed TRAIN selections. "
        f"Maximum absolute replay difference: {result['max_abs_difference']:.3g}. "
        'Independent value/sign/parity/modulo metrics agree for real, shuffled and prior panels.', '',
        f"The parity invariant holds at {parity_checks:,} archived value coordinates. "
        'Addition and subtraction are identical modulo two, so swapping these operators preserves parity at every write. '
        'Identical parity scores are a mathematical sanity check, not an independent semantic-recovery finding.', '',
        'The alternate targets have slightly lower raw scalar MAE for both hidden readouts. Source features also find them easier. '
        'The positive source-corrected normalized-MAE interaction does not establish a raw ordinary-semantic advantage, '
        'a native execution mechanism, or causal downstream use. Target scaling and learnability differ. '
        'Keep the paper claim exploratory and test global versus query-specific access next.', '']
    path = Path(config['report']); study.base._publish(path, '\n'.join(lines).encode())
    return study.common.receipt(config, source, result, dict(report=study.storage._pin(path)))
