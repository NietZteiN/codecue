#!/usr/bin/env python
"""Review a quota failure, recover a saved bank receipt, and resume owned jobs.

Scientific functions come from the original immutable source. This operational
repair does not fit, regenerate activations, or change the experiment protocol.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

SNAPSHOT = Path('/work/jvl210002/migration/codecue/artifacts/binding/sources/8c1bda5687b078517a933459')
sys.path.insert(0, str(SNAPSHOT / 'src'))

import numpy as np
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_numeric_exploration as study
from codecue.binding import arithmetic_numeric_exploration_suite as suite
from codecue.binding import relationship_capture as base

ROOT = Path('artifacts/binding/arithmetic_numeric_exploration/20261031_v1')
CFG = Path('configs/binding/arithmetic_numeric_exploration_20261031_v1')
FAILED = dict(llama8b_root_definition='486530', llama8b_computed_definition='486531',
    codellama34b_root_definition='486532', codellama34b_computed_definition='486533',
    source_root_definition='486534', source_computed_definition='486535')


def reconstruct(config, prefix):
    source = base._current_source(config)
    _, _, _, rows, cases = study.audit.load_cache(config)
    table = study.examples(rows, cases)
    mask = np.asarray([e['role'] == config['role'] for e in table])
    subset = study.common.mask_table(table, mask)
    groups = np.asarray([e['group'] for e in subset])
    splits = np.asarray([e['split'] for e in subset])
    ids = np.asarray([e['case_id'] + ':definition:' + str(e['statement']) for e in subset])
    values = np.asarray([e['value'] for e in table])
    controls = values[study.controls(rows, table)][mask]
    values = values[mask]
    folder = Path(config['run_dir'])
    metadata = base._json(folder / (prefix + '_metadata.json'))
    with np.load(folder / (prefix + '_parameters.npz'), allow_pickle=False) as arrays:
        model = study.from_parameters(metadata, {k: arrays[k] for k in arrays.files})
    if model.train_ids != tuple(ids[splits == 'train']):
        raise ValueError('saved model training identity differs')
    with np.load(folder / (prefix + '_scores.npz'), allow_pickle=False) as stored:
        arrays = {k: stored[k] for k in stored.files}
    if (set(arrays) != {'real', 'shuffled', 'truth', 'control_truth', 'ids', 'split'}
            or not np.array_equal(arrays['ids'], ids) or not np.array_equal(arrays['split'], splits)
            or not np.array_equal(arrays['truth'], values) or not np.array_equal(arrays['control_truth'], controls)):
        raise ValueError('saved bank row/label identities differ')
    parts = prefix.split('_')
    width = int(parts[0][5:]); seed = int(parts[2][4:]); alpha = float(parts[3][5:])
    cache_config = base._json(config['cache_config']['path'], config['cache_config']['sha256'])
    cache = base._json(Path(cache_config['run_dir']) / 'results.json')
    if cache['table_sha256'] != study.digest(table):
        raise ValueError('cached input identities differ')
    matrix = study.load_features(cache['features'][f'projected_seed{seed}'])
    x = np.concatenate((np.asarray(matrix[mask, :width]) * np.sqrt(1024 / width), study.metadata_features(subset)), axis=1)
    real, shuffled = arrays['real'], arrays['shuffled']
    replay = model.predict(x)
    saved = np.concatenate((real, shuffled), axis=1)
    if not np.allclose(replay, saved, rtol=1e-10, atol=1e-12):
        raise ValueError('saved score replay differs beyond numerical tolerance')
    for actual, expected in [(replay[:, :study.HEAD_WIDTH], real), (replay[:, study.HEAD_WIDTH:], shuffled)]:
        a, b = study.predictions(actual), study.predictions(expected)
        for name in study.FORMATS:
            if name != 'scalar' and not np.array_equal(a[name], b[name]):
                raise ValueError('numeric decisions differ after parameter replay')
    panels = {}
    for label in ('train', 'development', 'calibration'):
        m = splits == label
        panels[label] = dict(real=study.score_heads(real[m], values[m], groups[m]),
            control=study.score_heads(shuffled[m], controls[m], groups[m]),
            prior=study.score_heads(np.broadcast_to(model.weighted_target_mean[:study.HEAD_WIDTH],
                (int(m.sum()), study.HEAD_WIDTH)), values[m], groups[m]))
    seen = np.asarray([e['value'] in {w['value'] for w in rows[e['row']]['oracle']['writes'][:4]} for e in subset])
    depth = np.asarray([e['depth'] for e in subset])
    unseen = ~np.isin(values, np.unique(values[splits == 'train']))
    strata = {}
    for label, m in {'matches_initial_literal': seen, 'absent_from_initial_literals': ~seen,
            'unseen_train_value': unseen, **{f'depth{d}': depth == d for d in (2, 4, 6)}}.items():
        m = m & (splits == 'development')
        strata[label] = dict(observations=int(m.sum()), real=study.score_heads(real[m], values[m], groups[m])) if m.any() else dict(observations=0)
    selected = base._json(folder / f'width{width}_selection_review_v1.json')['encodings']
    artifacts = {key: study.storage._pin(folder / (prefix + suffix)) for key, suffix in
        [('parameters', '_parameters.npz'), ('metadata', '_metadata.json'), ('scores', '_scores.npz')]}
    bank = dict(status='complete_exploratory', source=source, config_hash=study.digest(config),
        width=width, seed=seed, alpha=alpha, selected_formats=[k for k in study.FORMATS if selected[k] == alpha],
        train=panels['train'], development=panels['development'], calibration=panels['calibration'],
        parameters=int(model.coef.size + model.intercept.size), features=x.shape[1], artifacts=artifacts,
        development_strata=strata, parameters_per_encoding={k: (x.shape[1] + 1) *
            (23 if k == 'digits_joint' else dict(study.HEADS)[k]) for k in study.FORMATS})
    return bank, float(np.max(np.abs(replay - saved)))


def recover():
    if not os.environ.get('SLURM_JOB_ID'):
        raise ValueError('replay recovery requires a CPU allocation')
    relocation = base._json(ROOT / 'storage_relocation_review_v1.json')
    if relocation['status'] != 'relocated_verified':
        raise ValueError('verified relocation must finish first')
    config = base._json(CFG / 'llama8b_root_definition.json')
    folder = Path(config['run_dir']); source = base._current_source(config)
    verified = 0
    for path in sorted(folder.glob('width*.json')):
        if path.name.endswith('_metadata.json') or 'selection_review' in path.name:
            continue
        if study.resume(path, config, source): verified += 1
    # Reconstruct one already-published bank first as a serialization/metric
    # control, then recover the orphan from its own saved parameters and scores.
    existing = 'width256_selected_seed11_alpha100'
    positive, positive_difference = reconstruct(config, existing)
    if positive != base._json(folder / (existing + '.json')):
        raise ValueError('receipt reconstruction differs on the existing control bank')
    orphan = 'width256_selected_seed11_alpha10000'
    bank, difference = reconstruct(config, orphan)
    path = folder / (orphan + '.json')
    if path.exists():
        if base._json(path) != bank: raise ValueError('existing recovered receipt differs')
    else:
        base._put(path, bank)
    review = dict(status='recovered_verified', recorded_utc=datetime.now(timezone.utc).isoformat(),
        source=source, config=study.storage._pin(CFG / 'llama8b_root_definition.json'),
        original_committed_banks_verified=verified, recovered_bank=study.storage._pin(path),
        existing_bank_control='exact metadata equality', positive_replay_max_difference=positive_difference,
        orphan_replay_max_difference=difference, recovery_script=study.storage._pin(Path(__file__)),
        new_fits=0, new_model_queries=0, reason='Quota exhaustion prevented completion JSON publication after the model and scores were saved.')
    base._put(ROOT / 'storage_recovery_review_v1.json', review)
    print(json.dumps(review), flush=True)


def rearm():
    proof = base._json(ROOT / 'storage_recovery_review_v1.json')
    if proof['status'] != 'recovered_verified' or proof['new_fits'] != 0:
        raise ValueError('successful no-fit recovery review required')
    file = CFG / 'suite.json'; config = base._json(file)
    with suite._CORE._lock(Path(config['run_dir'])):
        suite._CORE._config(config)
        state = base._json(Path(config['run_dir']) / 'jobs_live_v1.json')
        if state.get('storage_recovery_rearmed'):
            raise ValueError('owned recovery has already been rearmed')
        source = suite._CORE._source(SNAPSHOT, config)
        if state['source'] != source:
            raise ValueError('suite source identity differs')
        ids = [attempts[-1]['job_id'] for attempts in state['attempts'].values() if attempts]
        observed, errors = suite._CORE.scheduler(ids)
        if errors: raise ValueError('scheduler inspection failed: ' + str(errors))
        suite._CORE._plan(config, state, observed)
        for key, job in FAILED.items():
            if state['attempts'][key][-1]['job_id'] != job or observed[job]['state'] != 'FAILED':
                raise ValueError('only the reviewed failed jobs can be resumed')
        for name in ['llama8b_cache', 'codellama34b_cache', 'source_cache']:
            study.common.completed(base._json(CFG / (name + '.json')))
        state['storage_recovery_rearmed'] = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
            reviewed_jobs=FAILED, review=study.storage._pin(ROOT / 'storage_recovery_review_v1.json'),
            rationale='Reviewed environmental EDQUOT; caches verified, outputs relocated, saved banks preserved. Frozen protocol unchanged.')
        suite._CORE._save(config, state)
        suite.controller(config, state)
        for node in config['nodes']:
            if node['key'] in FAILED:
                suite._CORE._submit_node(config, state, node)
        suite._CORE._save(config, state)
    print(json.dumps(suite.status(config)['stages']), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['recover', 'rearm'])
    with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))):
        {'recover': recover, 'rearm': rearm}[parser.parse_args().command]()
