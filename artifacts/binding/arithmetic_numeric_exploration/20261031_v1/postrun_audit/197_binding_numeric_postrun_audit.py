#!/usr/bin/env python
"""No-fit integrity, selection and independent metric audit of numeric discovery."""
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import sys

SNAPSHOT = Path('/work/jvl210002/migration/codecue/artifacts/binding/sources/8c1bda5687b078517a933459')
sys.path.insert(0, str(SNAPSHOT / 'src'))

import numpy as np
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_numeric_exploration as study
from codecue.binding import relationship_capture as base

RUN = Path('artifacts/binding/arithmetic_numeric_exploration/20261031_v1')
CFG = Path('configs/binding/arithmetic_numeric_exploration_20261031_v1')
HEADS = [('scalar', 1), ('categorical', 193), ('sign', 3), ('magnitude', 3),
    ('units', 10), ('tens', 10), ('parity', 2), ('mod5', 5), ('mod10', 10)]


def equal(a, b):
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    if isinstance(a, float):
        return isinstance(b, (float, int)) and np.isfinite(a) and np.isfinite(b) and abs(a - b) <= 1e-12
    return type(a) is type(b) and a == b


def independent_metrics(scores, truth, groups):
    """Recompute head semantics and family/class aggregation outside the scorer."""
    if scores.shape != (len(truth), 237) or not np.isfinite(scores).all():
        raise ValueError('finite 237-head predictions required')
    guess, position = {}, 0
    for name, width in HEADS:
        guess[name] = scores[:, position] if name == 'scalar' else np.argmax(scores[:, position:position + width], axis=1)
        position += width
    actual = dict(sign=np.where(truth < 0, 0, np.where(truth == 0, 1, 2)),
        magnitude=np.where(truth == 0, 0, np.where(np.abs(truth) <= 9, 1, 2)),
        units=np.abs(truth) - 10 * (np.abs(truth) // 10), tens=np.abs(truth) // 10,
        parity=np.mod(truth, 2), mod5=np.mod(truth, 5), mod10=np.mod(truth, 10))
    magnitude = 10 * guess['tens'] + guess['units']
    numeric = dict(scalar=guess['scalar'], categorical=guess['categorical'] - 96,
        digits_joint=(guess['sign'] - 1) * magnitude)
    valid = ((guess['sign'] == 1) & (magnitude == 0)) | ((guess['sign'] != 1) & (magnitude >= 1) & (magnitude <= 96))
    order = np.argsort(groups, kind='stable')
    sorted_groups = groups[order]
    starts = np.flatnonzero(np.r_[True, sorted_groups[1:] != sorted_groups[:-1]])
    counts_by_family = np.diff(np.r_[starts, len(groups)])
    def mean(values):
        sums = np.add.reduceat(np.asarray(values, dtype=float)[order], starts)
        return float((sums / counts_by_family).sum() / len(starts))
    out = {}
    for name, values in numeric.items():
        correct = np.round(values) == truth
        if name == 'digits_joint': correct &= valid
        out[name] = dict(exact=mean(correct), mae=mean(np.abs(values - truth)))
        if name == 'categorical':
            labels, counts = np.unique(truth, return_counts=True)
            out[name]['support'] = {str(int(label)): int(count) for label, count in zip(labels, counts)}
        if name == 'digits_joint': out[name]['invalid'] = float((~valid).mean())
    for name, labels in actual.items():
        classes, counts = np.unique(labels, return_counts=True)
        correct = guess[name] == labels
        out[name] = dict(exact=mean(correct), balanced_accuracy=float(sum(float(correct[labels == c].mean()) for c in classes) / len(classes)),
            support={str(int(c)): int(n) for c, n in zip(classes, counts)})
    return out


def selftest():
    for values in [np.arange(-96, 97), np.asarray([-2, -2, -1]), np.asarray([0, 1, 1, 2, 9])]:
        groups = np.asarray(['family' + str(i % 3) for i in range(len(values))])
        for scores in [study.targets(values), np.zeros((len(values), 237)), np.random.default_rng(731).normal(size=(len(values), 237))]:
            if not equal(independent_metrics(scores, values, groups), study.score_heads(scores, values, groups)):
                raise ValueError('independent metric self-test differs')
    print('Independent numeric metric self-test passed.', flush=True)


def audit_worker(item):
    config = base._json(item['path'], item['sha256'])
    study.common.completed(config)
    folder = Path(config['run_dir']); data = base._json(folder / 'results.json')
    _, _, _, rows, cases = study.audit.load_cache(config)
    table = study.examples(rows, cases)
    mask = np.asarray([e['role'] == config['role'] for e in table])
    subset = study.common.mask_table(table, mask)
    train = np.asarray([e['split'] == 'train' for e in subset])
    split = np.asarray([e['split'] for e in subset])
    groups = np.asarray([e['group'] for e in subset])
    ids = np.asarray([e['case_id'] + ':definition:' + str(e['statement']) for e in subset])
    values = np.asarray([e['value'] for e in table])
    control = values[study.controls(rows, table)][mask]; truth = values[mask]
    folds = study.common.folds(study.common.mask_table(subset, train))
    train_indices = np.flatnonzero(train)
    cache_cfg = base._json(config['cache_config']['path'], config['cache_config']['sha256'])
    cache = base._json(Path(cache_cfg['run_dir']) / 'results.json')
    if cache['table_sha256'] != study.digest(table): raise ValueError('cached point identities differ')
    cv, selected, replayed, max_difference = 0, 0, 0, 0.
    loaded = {}
    for width in config['widths']:
        records = []
        for seed in study.SEEDS:
            for fold in range(3):
                fit_ids = train_indices[folds != fold]; val_ids = train_indices[folds == fold]
                for alpha in study.ALPHAS:
                    name = f'width{width}_cv_seed{seed}_fold{fold}_alpha{int(alpha)}'
                    bank = study.resume(folder / (name + '.json'), config, data['source'])
                    if bank is None: raise ValueError('missing predeclared CV bank')
                    metadata = base._json(bank['artifacts']['metadata']['path'])
                    if (metadata['training_ids'] != ids[fit_ids].tolist() or metadata['fit_split'] != 'train'
                            or metadata['heldout_rows_used_for_fit'] != 0
                            or bank['fit_groups'] != sorted(set(groups[fit_ids]))
                            or bank['validation_groups'] != sorted(set(groups[val_ids]))):
                        raise ValueError('CV identities, fold groups or TRAIN boundary differ')
                    with np.load(bank['artifacts']['parameters']['path'], allow_pickle=False) as arrays:
                        study.from_parameters(metadata, {k: arrays[k] for k in arrays.files})
                    records.append(bank); cv += 1
        selection = study.select(records)
        if selection != base._json(folder / f'width{width}_selection_review_v1.json')['encodings']:
            raise ValueError('recomputed TRAIN selection differs')
        for seed in study.SEEDS:
            key = 'source' if config['backend'] == 'source' else 'raw' if width == cache['width'] else f'projected_seed{seed}'
            if key not in loaded: loaded[key] = study.load_features(cache['features'][key])
            matrix = loaded[key]
            features = study.fold_source(matrix[mask], width) if config['backend'] == 'source' else np.asarray(matrix[mask]) if width == cache['width'] else np.asarray(matrix[mask, :width]) * np.sqrt(1024 / width)
            x = np.concatenate((features, study.metadata_features(subset)), axis=1)
            for alpha in sorted(set(selection.values())):
                banks = [b for b in data['fits'] if b['width'] == width and b['seed'] == seed and b['alpha'] == alpha]
                if len(banks) != 1: raise ValueError('missing or duplicate selected bank')
                bank = banks[0]
                if bank['selected_formats'] != [k for k in study.FORMATS if selection[k] == alpha]:
                    raise ValueError('selected format assignments differ')
                metadata = base._json(bank['artifacts']['metadata']['path'])
                if metadata['training_ids'] != ids[train].tolist() or metadata['heldout_rows_used_for_fit'] != 0:
                    raise ValueError('selected model TRAIN boundary differs')
                with np.load(bank['artifacts']['parameters']['path'], allow_pickle=False) as arrays:
                    model = study.from_parameters(metadata, {k: arrays[k] for k in arrays.files})
                with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as z:
                    if (not np.array_equal(z['ids'], ids) or not np.array_equal(z['split'], split)
                            or not np.array_equal(z['truth'], truth) or not np.array_equal(z['control_truth'], control)):
                        raise ValueError('saved score identities or real/control labels differ')
                    real, shuffled = z['real'], z['shuffled']
                predicted = model.predict(x)
                saved = np.concatenate((real, shuffled), axis=1)
                if not np.allclose(predicted, saved, rtol=1e-10, atol=1e-12):
                    raise ValueError('replayed selected scores differ')
                max_difference = max(max_difference, float(np.max(np.abs(predicted - saved))))
                for label in ('train', 'development', 'calibration'):
                    m = split == label
                    panels = dict(real=independent_metrics(real[m], truth[m], groups[m]),
                        control=independent_metrics(shuffled[m], control[m], groups[m]),
                        prior=independent_metrics(np.broadcast_to(model.weighted_target_mean[:237], (int(m.sum()), 237)), truth[m], groups[m]))
                    if not equal(panels, bank[label]): raise ValueError('independent numeric metrics differ')
                for actual, expected in [(predicted[:, :237], real), (predicted[:, 237:], shuffled)]:
                    a, b = study.predictions(actual), study.predictions(expected)
                    for name in study.FORMATS:
                        if name != 'scalar' and not np.array_equal(a[name], b[name]):
                            raise ValueError('discrete selected decisions changed during replay')
                    if not np.array_equal(np.rint(a['scalar']), np.rint(b['scalar'])):
                        raise ValueError('rounded scalar decisions changed during replay')
                selected += 1; replayed += int(predicted.size)
            print(folder.name, 'verified width', width, 'seed', seed, flush=True)
    if cv != data['cv_banks'] or selected != len(data['fits']) or cv + selected != data['new_readout_fits']:
        raise ValueError('fit bank accounting differs')
    return dict(config=item, results=study.storage._pin(folder / 'results.json'), cv_banks=cv,
        selected_banks=selected, replayed_scores=replayed, max_abs_replay_difference=max_difference)


def run(recipe):
    if not os.environ.get('SLURM_JOB_ID'): raise ValueError('postrun replay requires a CPU allocation')
    source = base._json(recipe)
    if source['script_sha256'] != base._sha(__file__): raise ValueError('audit source changed')
    out = Path(source['run_dir'])
    if (out / 'completion_review_v1.json').exists(): raise ValueError('preserve completed audit')
    report = base._json(source['report_config']['path'], source['report_config']['sha256'])
    study.common.completed(report)
    cache_pins = {}
    for worker in report['workers']:
        config = base._json(worker['path'], worker['sha256'])
        cache_pins[config['cache_config']['path']] = config['cache_config']
    for entry in cache_pins.values(): study.common.completed(base._json(entry['path'], entry['sha256']))
    panels = [audit_worker(item) for item in report['workers']]
    if sum(p['cv_banks'] for p in panels) != 702 or sum(p['selected_banks'] for p in panels) != 216:
        raise ValueError('expected 702 CV and 216 selected banks')
    result = dict(status='passed', recorded_utc=datetime.now(timezone.utc).isoformat(),
        source_snapshot=str(SNAPSHOT), recipe=study.storage._pin(recipe), script=study.storage._pin(__file__),
        workers=panels, verified_banks=918, replayed_selected_banks=216,
        replayed_scores=sum(p['replayed_scores'] for p in panels),
        max_abs_replay_difference=max(p['max_abs_replay_difference'] for p in panels),
        metrics='independent target semantics, family means and class recall verified for real/control/TRAIN-prior panels',
        cv='all CV payloads and metadata verified; selections recomputed from stored TRAIN validation records; CV scores were not reapplied',
        new_fits=0, new_model_queries=0, sealed_final_opened=False)
    base._put(out / 'completion_review_v1.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'workers'}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe', nargs='?')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))):
        if args.self_test: selftest()
        else: run(args.recipe)
