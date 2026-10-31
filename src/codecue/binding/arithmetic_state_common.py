"""Shared TRAIN-only metadata and cache helpers for state discovery readouts."""
from collections import defaultdict
from pathlib import Path

import numpy as np

from . import arithmetic_state_audit as audit
from . import arithmetic_local_probes as pair
from . import arithmetic_probe_selection as selector
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

SEEDS = (11, 29, 47)


def inputs(config):
    return audit.load_cache(config)


def donors(rows):
    """Derange whole structural families inside each split/depth/operator stratum."""
    strata = defaultdict(set)
    index = {}
    for i, r in enumerate(rows):
        strata[(r['split'], r['family_stratum'])].add(r['component_id'])
        key = (r['component_id'], r['numeric_seed'], r['numeric_draw'], r['lexical_realization'])
        if key in index:
            raise ValueError('one query per numeric/lexical relative required')
        index[key] = i
    mapping = {}
    for key, values in sorted(strata.items()):
        values = np.asarray(sorted(values))
        if len(values) < 2:
            raise ValueError('within-stratum family derangement requires two families')
        values = values[np.random.default_rng(117).permutation(len(values))]
        mapping.update(dict(zip(values.tolist(), np.roll(values, -1).tolist())))
    result = np.asarray([index[(mapping[r['component_id']], r['numeric_seed'], r['numeric_draw'], r['lexical_realization'])] for r in rows])
    if np.any(result == np.arange(len(rows))) or len(set(result.tolist())) != len(rows):
        raise ValueError('complete family derangement required')
    for i, j in enumerate(result):
        if rows[i]['split'] != rows[j]['split'] or rows[i]['family_stratum'] != rows[j]['family_stratum']:
            raise ValueError('family control leaked across split or stratum')
    return result


def folds(table):
    return selector.folds([dict(split=e['split'], component_id=e['group'], operation_family=e['stratum']) for e in table])


def weights(table, seed):
    values = pair.family_weights(table, seed).astype(float)
    return values / values.mean()


def group_mean(values, groups):
    result = {str(g): float(np.mean(values[np.asarray(groups) == g])) for g in sorted(set(groups))}
    return float(np.mean(list(result.values()))), result


def mask_table(table, mask):
    return [e for e, yes in zip(table, mask) if yes]


def save_scorer(path, model, norm):
    values = {'state_' + k: v.detach().numpy() for k, v in model.state_dict().items()}
    storage._npz(path, **values, **norm)


def validate_role(config, role):
    base._slurm()
    if config.get('evaluation_role') != role or config.get('seeds') != list(SEEDS):
        raise ValueError('declared three-seed state discovery recipe required')
    if base._sha(config['declared_plan']) != config['declared_plan_sha256']:
        raise ValueError('state follow-up plan changed')
    return base._current_source(config)


def receipt(config, source, result, artifacts):
    folder = Path(config['run_dir'])
    base._put(folder / 'results.json', result)
    artifacts = dict(artifacts, results=storage._pin(folder / 'results.json'))
    base._put(folder / 'completion_manifest_v1.json', dict(status='complete_exploratory',
        evaluation_role=config['evaluation_role'], source=source, config_hash=digest(config), artifacts=artifacts,
        new_model_queries=0))
    return result


def completed(config):
    folder = Path(config['run_dir'])
    proof = base._json(folder / 'completion_manifest_v1.json')
    if proof['config_hash'] != digest(config) or proof['status'] != 'complete_exploratory':
        raise ValueError('state completion identity differs')
    base._verify_source(config, proof['source'])
    for entry in proof['artifacts'].values():
        if base._sha(entry['path']) != entry['sha256']:
            raise ValueError('state artifact changed')
    entry = proof['artifacts'].get('results')
    if entry:
        result = base._json(entry['path'], entry['sha256'])
        for field in ('fits', 'global_fits'):
            for bank in result.get(field, []):
                for payload in bank.get('artifacts', {}).values():
                    if base._sha(payload['path']) != payload['sha256']:
                        raise ValueError('state model/score payload changed')
    return proof
