"""Current definition lookup from distributed states, with supplied node scaffold."""
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_local_probes as pair
from . import arithmetic_local_capture as capture
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

ROLE = 'discovery_arithmetic_current_binding_v1'
BACKENDS = ('anchor_query', 'answer_query', 'source_query', 'position_only')


def examples(rows, cases):
    table = []
    for r, (row, case) in enumerate(zip(rows, cases)):
        definitions = [i for i, p in enumerate(case['descriptors']) if p['kind'] == 'definition']
        if len(definitions) != 4 + row['depth'] or any(case['descriptors'][slot]['statement'] != slot for slot in range(4)):
            raise ValueError('supplied initial variable anchors and all definition nodes required')
        for slot in range(4):
            name = case['descriptors'][slot]['name']
            matches = [j for j, point in enumerate(definitions) if case['descriptors'][point]['name'] == name]
            label = row['oracle']['definitions'][slot]
            if label != max(matches):
                raise ValueError('current definition and exact source recency oracle differ')
            table.append(dict(row=r, slot=slot, candidates=definitions, parent=label, statement=len(definitions),
                group=row['component_id'], split=row['split'], stratum=row['family_stratum'], depth=row['depth'],
                side='slot' + str(slot), case_id=row['id']))
    return table


def features(nodes, table, cases, backend):
    if backend not in BACKENDS:
        raise ValueError('declared current-binding backend required')
    q = np.zeros((len(table), 80), np.float32)
    c = np.zeros((len(table), 10, 80), np.float32)
    mask = np.zeros((len(table), 10), bool)
    for i, e in enumerate(table):
        r, slot = e['row'], e['slot']
        point = cases[r]['point_count'] - 1 if backend == 'answer_query' else slot
        if backend != 'position_only':
            q[i, :64] = nodes[r, point]
        q[i, 64 + slot] = 1
        q[i, -1] = e['depth'] / 6
        for candidate, p in enumerate(e['candidates']):
            if backend != 'position_only':
                c[i, candidate, :64] = nodes[r, p]
            c[i, candidate, 64 + candidate] = 1
            c[i, candidate, -1] = (len(e['candidates']) - candidate) / 10
            mask[i, candidate] = True
    return q, c, mask


def metrics(logits, labels, table, rows):
    result = pair.metrics(logits, labels, table)
    result['whole_current_binding_accuracy'] = result.pop('whole_program_graph_accuracy')
    result['source_binding_oracle_accuracy'] = result.pop('source_name_recency_oracle_accuracy')
    predicted = logits.argmax(axis=1)
    versions = np.asarray([rows[e['row']]['oracle']['writes'][int(p)]['version'] for e, p in zip(table, predicted)])
    expected = np.asarray([rows[e['row']]['oracle']['writes'][int(p)]['version'] for e, p in zip(table, labels)])
    result['version_from_predicted_node_accuracy'] = float((versions == expected).mean())
    return result


def choose(records):
    scores = defaultdict(dict)
    for r in records:
        key, point = (r['backend'], r['method']), (r['fold'], r['seed'])
        if point in scores[key]:
            raise ValueError('duplicate binding CV observation')
        scores[key][point] = r['validation']['family_macro_accuracy']
    if set(scores) != {(b, m) for b in BACKENDS for m in pair.METHODS} or any(
            set(v) != {(f, s) for f in range(3) for s in common.SEEDS} for v in scores.values()):
        raise ValueError('complete three-fold three-seed binding grid required')
    return {b: max(pair.METHODS, key=lambda m: (np.mean(list(scores[(b, m)].values())), -pair.METHODS.index(m))) for b in BACKENDS}


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
        labels = np.asarray([e['parent'] for e in table])
        donor = common.donors(rows)
        control = np.asarray([rows[donor[e['row']]]['oracle']['definitions'][e['slot']] for e in table])
        train = np.asarray([e['split'] == 'train' for e in table])
        dev = np.asarray([e['split'] == 'development' for e in table])
        calibration = np.asarray([e['split'] == 'calibration' for e in table])
        training_table = common.mask_table(table, train)
        folds = common.folds(training_table)
        surface = audit.cache_array(cache, 'source')
        layer = profile['layers'].index(cache['nominated_layer'])
        records, artifacts, fits = [], {}, []
        for seed in common.SEEDS:
            hidden = audit.cache_array(cache, 'hidden_seed' + str(seed))[:, :, layer]
            for backend in BACKENDS:
                q, c, mask = features(surface if backend == 'source_query' else hidden, table, cases, backend)
                tq, tc, tm = q[train], c[train], mask[train]
                for fold in range(3):
                    fit, valid = folds != fold, folds == fold
                    fit_table = common.mask_table(training_table, fit)
                    valid_table = common.mask_table(training_table, valid)
                    for method in pair.METHODS:
                        key = f'cv_{backend}_{method}_fold{fold}_seed{seed}'
                        path = folder / (key + '.json')
                        if path.exists():
                            record = base._json(path)
                            if record['source'] != source or record['config_hash'] != digest(config):
                                raise ValueError('binding CV resume identity differs')
                        else:
                            model, norm = pair.train(tq[fit], tc[fit], tm[fit], labels[train][fit], pair.family_weights(fit_table, seed), method, seed)
                            val = metrics(pair.scores(model, norm, tq[valid], tc[valid], tm[valid]), labels[train][valid], valid_table, rows)
                            record = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                                backend=backend, method=method, fold=fold, seed=seed, validation=val,
                                fit_groups=sorted({e['group'] for e in fit_table}), validation_groups=sorted({e['group'] for e in valid_table}))
                            base._put(path, record)
                            print(key, flush=True)
                        records.append(record)
                        artifacts[key] = storage._pin(path)
                        capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records), planned=132))
        selected = choose(records)
        base._put(folder / 'selection_review_v1.json', dict(status='selection_locked', source=source,
            config_hash=digest(config), methods=selected, selection_split='TRAIN only', tie_break=list(pair.METHODS)))
        artifacts['selection'] = storage._pin(folder / 'selection_review_v1.json')
        for seed in common.SEEDS:
            hidden = audit.cache_array(cache, 'hidden_seed' + str(seed))[:, :, layer]
            for backend in BACKENDS:
                q, c, mask = features(surface if backend == 'source_query' else hidden, table, cases, backend)
                for target_name, target in [('real', labels), ('coherent_family', control)]:
                    key = f'selected_{backend}_{target_name}_seed{seed}'
                    path = folder / (key + '.json')
                    if path.exists():
                        result = base._json(path)
                        if result['source'] != source or result['config_hash'] != digest(config):
                            raise ValueError('binding selected-bank identity differs')
                        for entry in result['artifacts'].values():
                            if base._sha(entry['path']) != entry['sha256']:
                                raise ValueError('binding selected payload changed')
                    else:
                        method = selected[backend]
                        model, norm = pair.train(q[train], c[train], mask[train], target[train], pair.family_weights(training_table, seed), method, seed)
                        logits = pair.scores(model, norm, q, c, mask)
                        parameters = folder / (key + '_parameters.npz')
                        common.save_scorer(parameters, model, norm)
                        replay, repeated_norm = audit.restore_scorer(parameters, method)
                        repeated = pair.scores(replay, repeated_norm, q, c, mask)
                        if not np.array_equal(logits, repeated):
                            raise ValueError('binding scorer save/reload replay differs')
                        scores = folder / (key + '_scores.npz')
                        storage._npz(scores, logits=logits, predictions=logits.argmax(axis=1).reshape(len(rows), 4),
                            labels=target, real_labels=labels, case_ids=np.asarray([e['case_id'] for e in table]),
                            row_indices=np.asarray([e['row'] for e in table]), slots=np.asarray([e['slot'] for e in table]))
                        result = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                            backend=backend, method=method, target=target_name, seed=seed,
                            train=metrics(logits[train], target[train], training_table, rows),
                            development=metrics(logits[dev], target[dev], common.mask_table(table, dev), rows),
                            calibration=metrics(logits[calibration], target[calibration], common.mask_table(table, calibration), rows),
                            artifacts=dict(parameters=storage._pin(parameters), scores=storage._pin(scores)))
                        base._put(path, result)
                        print(key, flush=True)
                    fits.append(result)
                    artifacts[key] = storage._pin(path)
                    capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records) + len(fits), planned=132))
        result = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=digest(config),
            model=profile['model'], selected_methods=selected, fits=fits, new_model_queries=0, generated_holdouts_opened=False,
            limitations='Adaptive current-binding lookup with supplied variable anchors and definition nodes. Answer queries still '
                'receive earlier candidate states. Node versions are source annotations of predicted pointers, not independently '
                'decoded version labels. Exact name/recency parsing is a 100% source ceiling. No causal-use claim.')
        return common.receipt(config, source, result, artifacts)
