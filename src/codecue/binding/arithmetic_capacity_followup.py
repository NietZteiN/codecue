"""Fill only missing, capacity-matched counterparts to the local edge probe."""
from pathlib import Path

import numpy as np

from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_local_probes as old
from . import arithmetic_local_capture as capture
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

ROLE = 'discovery_arithmetic_capacity_followup_v1'


def missing_cells(choices):
    reference = choices['hidden_local']
    return [(backend, reference) for backend in ('hidden_global', 'source_local') if choices[backend] != reference]


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, ROLE)
    audit_config, cache, profile, rows, cases = common.inputs(config)
    old_config = base._json(audit_config['probe_config'], audit_config['probe_config_sha256'])
    entry = cache['inputs']['probe_results']
    original = base._json(entry['path'], entry['sha256'])
    method = original['selected_methods']['hidden_local']
    folder = Path(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return common.completed(config)
        table = old.examples(rows, cases)
        truth = np.asarray([e['parent'] for e in table])
        random = old.random_targets(table)
        train = np.asarray([e['split'] == 'train' for e in table])
        training_table = common.mask_table(table, train)
        surface = audit.cache_array(cache, 'source')
        layer = profile['layers'].index(cache['nominated_layer'])
        results, artifacts, new_fits = [], {}, 0
        for seed in common.SEEDS:
            hidden = None
            for backend in ('hidden_global', 'source_local'):
                if original['selected_methods'][backend] == method:
                    for bank in original['fits']:
                        if bank['seed'] == seed and bank['backend'] == backend and bank['training_families'] == 216:
                            for entry in bank['artifacts'].values():
                                if base._sha(entry['path']) != entry['sha256']:
                                    raise ValueError('reused matched counterpart changed')
                            results.append(dict(bank, reused_original=True))
                    continue
                if backend == 'hidden_global':
                    if hidden is None:
                        hidden = audit.cache_array(cache, 'hidden_seed' + str(seed))[:, :, layer]
                    q, c, mask = old.pair_features(hidden, table, cases, global_query=True)
                else:
                    q, c, mask = old.pair_features(surface, table, cases)
                for target_name, target in [('real', truth), ('random_family', random)]:
                    key = f'matched_{backend}_{method}_{target_name}_seed{seed}'
                    path = folder / (key + '.json')
                    if path.exists():
                        result = base._json(path)
                        if result['source'] != source or result['config_hash'] != digest(config):
                            raise ValueError('capacity follow-up resume identity differs')
                        for entry in result['artifacts'].values():
                            if base._sha(entry['path']) != entry['sha256']:
                                raise ValueError('capacity follow-up payload changed')
                    else:
                        model, norm = old.train(q[train], c[train], mask[train], target[train],
                            old.family_weights(training_table, seed), method, seed)
                        scores = old.scores(model, norm, q, c, mask)
                        parameters = folder / (key + '_parameters.npz')
                        common.save_scorer(parameters, model, norm)
                        replay, repeated_norm = audit.restore_scorer(parameters, method)
                        if not np.array_equal(scores, old.scores(replay, repeated_norm, q, c, mask)):
                            raise ValueError('capacity follow-up model replay differs')
                        score_path = folder / (key + '_scores.npz')
                        storage._npz(score_path, logits=scores, labels=target, real_labels=truth,
                            development=~train, case_ids=np.asarray([e['case_id'] for e in table]),
                            point_indices=np.asarray([e['point'] for e in table]))
                        result = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                            backend=backend, method=method, seed=seed, target=target_name, training_families=216,
                            train=old.metrics(scores[train], target[train], training_table),
                            development=old.metrics(scores[~train], target[~train], common.mask_table(table, ~train)),
                            artifacts=dict(parameters=storage._pin(parameters), scores=storage._pin(score_path)), reused_original=False)
                        base._put(path, result)
                        print(key, flush=True)
                    new_fits += 1
                    results.append(result)
                    artifacts[key] = storage._pin(path)
                    capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=new_fits))
        if len(results) != 12:
            raise ValueError('complete matched source/global counterpart grid required')
        result = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=digest(config),
            model=profile['model'], reference_method=method, fits=results, new_readout_fits=new_fits,
            new_model_queries=0, generated_holdouts_opened=False,
            limitations='Adaptive postrun capacity sensitivity. Architecture is the original TRAIN-selected local method; '
                'no new selection or best-DEV choice. Supplied scaffold and exact source oracle remain explicit. '
                'Original selected comparisons are preserved; no causal-use or source-superiority claim.')
        return common.receipt(config, source, result, artifacts)
