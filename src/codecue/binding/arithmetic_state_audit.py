"""Independent replay of local dependencies and reusable projected caches.

No fits or language-model calls. Cache all archived layers while reading each
immutable capture once, then reapply all saved local dependency readouts.
"""
import ast
from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from . import arithmetic_local_capture as capture
from . import arithmetic_local_probes as old
from . import arithmetic_local_behavior as behavior
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

ROLE = 'discovery_arithmetic_state_audit_v1'


def independent_trace(row):
    """Read parents before writes using the actual renamed source's AST."""
    definitions, values, versions = {}, {}, defaultdict(int)
    for statement, node in enumerate(ast.parse(row['source']).body[:-1]):
        names = [n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)]
        parents = [definitions[name] for name in names]
        result = eval(compile(ast.Expression(node.value), '<generated-state-audit>', 'eval'), {'__builtins__': {}}, values)
        name = node.targets[0].id
        versions[name] += 1
        expected = row['oracle']['writes'][statement]
        if parents != expected['parents'] or result != expected['value'] or versions[name] != expected['version']:
            raise ValueError('independent source read-time trace differs')
        definitions[name], values[name] = statement, result
    query = ast.parse(row['source']).body[-1].value.args[0].id
    if values[query] != row['expected_answer']:
        raise ValueError('independent printed value differs')
    for canonical, surface in row['rename_map'].items():
        slot = int(canonical[1:])
        if definitions[surface] != row['oracle']['definitions'][slot] or values[surface] != row['oracle']['values'][slot]:
            raise ValueError('independent current bindings differ')


def independent_metrics(logits, labels, table):
    correct = np.argmax(logits, axis=1) == labels
    groups, cases, sides, case_groups, case_depth = {}, {}, {}, {}, {}
    for e, yes in zip(table, correct.tolist()):
        groups.setdefault(e['group'], []).append(yes)
        cases.setdefault(e['case_id'], []).append(yes)
        sides.setdefault(f"depth{e['depth']}_{e['side']}", []).append(yes)
        case_groups[e['case_id']], case_depth[e['case_id']] = e['group'], e['depth']
    whole_by_family, whole_by_depth = defaultdict(list), defaultdict(list)
    for case_id, decisions in cases.items():
        whole_by_family[case_groups[case_id]].append(all(decisions))
        whole_by_depth[str(case_depth[case_id])].append(all(decisions))
    family = {g: float(sum(v) / len(v)) for g, v in groups.items()}
    return dict(individual_accuracy=float(sum(correct) / len(correct)),
        family_macro_accuracy=float(sum(family.values()) / len(family)),
        whole_program_graph_accuracy=float(sum(all(v) for v in cases.values()) / len(cases)),
        family_metrics=family, depth_side_accuracy={k: float(sum(v) / len(v)) for k, v in sides.items()},
        family_whole_program={g: float(sum(v) / len(v)) for g, v in whole_by_family.items()},
        depth_whole_program={g: float(sum(v) / len(v)) for g, v in whole_by_depth.items()})


def replay_check(actual, saved, mask):
    if actual.shape != saved.shape or mask.shape != actual.shape or not np.isfinite(actual).all() or not np.isfinite(saved).all():
        raise ValueError('finite aligned local score replay required')
    if not np.array_equal(actual.argmax(axis=1), saved.argmax(axis=1)):
        raise ValueError('replayed dependency decisions differ')
    if not np.all(actual[~mask] == -1e9) or not np.all(saved[~mask] == -1e9):
        raise ValueError('future or padded candidate mask changed')
    if not np.allclose(actual, saved, rtol=1e-5, atol=1e-5):
        raise ValueError('score replay exceeds declared numerical tolerance')
    return float(np.max(np.abs(actual - saved)))


def source_nodes(cases):
    from sklearn.feature_extraction.text import HashingVectorizer
    output = np.zeros((len(cases), capture.programs.MAX_POINTS, old.PROJECTION_RANK), np.float32)
    texts, coordinates = [], []
    for i, case in enumerate(cases):
        for j in range(case['point_count']):
            end = case['token_offsets'][case['positions'][j]][1]
            texts.append(case['prompt'] if j == case['point_count'] - 1 else case['prompt'][:end])
            coordinates.append((i, j))
    hashed = HashingVectorizer(analyzer='char', ngram_range=(3, 5), n_features=old.PROJECTION_RANK,
        alternate_sign=True, norm=None).transform(texts).toarray().astype(np.float32)
    for coordinate, vector in zip(coordinates, hashed):
        output[coordinate] = vector
    return output


def load_cache(config):
    """Immutable cache receipt; loads only small source metadata, not weights."""
    request = config['audit_config']
    audit_config = base._json(request['path'], request['sha256'])
    folder = Path(audit_config['run_dir'])
    receipt = base._json(folder / 'completion_manifest_v1.json')
    if receipt['status'] != 'complete_exploratory' or receipt['config_hash'] != digest(audit_config):
        raise ValueError('passing projected-cache audit required')
    base._verify_source(audit_config, receipt['source'])
    summary = base._json(folder / 'summary_review_v1.json', receipt['artifacts']['summary']['sha256'])
    cap = base._json(audit_config['capture_config'], audit_config['capture_config_sha256'])
    profile, rows, preflight, cases = capture.inputs(cap)
    if summary['ordered_ids_sha256'] != digest([r['id'] for r in rows]):
        raise ValueError('projected cache row identity differs')
    return audit_config, summary, profile, rows, cases


def cache_array(summary, key):
    entry = summary['caches'][key]
    if base._sha(entry['path']) != entry['sha256']:
        raise ValueError('projected cache changed')
    with np.load(entry['path'], allow_pickle=False) as stored:
        if stored.files != ['features']:
            raise ValueError('exact projected-cache array inventory required')
        values = stored['features']
    if values.dtype != np.float32 or not np.isfinite(values).all():
        raise ValueError('finite float32 projected cache required')
    expected = (summary['cases'], 23, 64) if key == 'source' else (summary['cases'], 23, len(summary['layers']), 64)
    if values.shape != expected:
        raise ValueError('projected cache geometry differs')
    return values


def restore_scorer(path, method):
    import torch
    model = old.make_model(method)
    with np.load(path, allow_pickle=False) as data:
        state = {k[6:]: torch.from_numpy(data[k].copy()) for k in data.files if k.startswith('state_')}
        norm = {k: data[k] for k in ('mean_q', 'scale_q', 'mean_c', 'scale_c')}
    model.load_state_dict(state)
    model.eval()
    return model, norm


def run(config):
    from .confidence import _run_lock
    base._slurm()
    if config.get('evaluation_role') != ROLE:
        raise ValueError('explicit postrun state audit role required')
    if base._sha(config['declared_plan']) != config['declared_plan_sha256']:
        raise ValueError('state audit plan changed')
    source = base._current_source(config)
    cap = base._json(config['capture_config'], config['capture_config_sha256'])
    probe_config = base._json(config['probe_config'], config['probe_config_sha256'])
    behavior_config = base._json(config['behavior_config'], config['behavior_config_sha256'])
    profile, rows, preflight, cases = capture.inputs(cap)
    old_manifest = base._verify_source(probe_config, preflight['source'])
    current_manifest = base._verify_source(config, source)
    for name in ('arithmetic_local_capture.py', 'arithmetic_local_programs.py', 'arithmetic_local_probes.py', 'weighted_ridge.py'):
        path = 'src/codecue/binding/' + name
        if old_manifest['code']['source_files'][path] != current_manifest['code']['source_files'][path]:
            raise ValueError('original capture/decoder mathematics changed')
    folder = Path(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return audit(config)
        for row in rows:
            independent_trace(row)
        cap_folder = Path(cap['run_dir'])
        receipt = base._json(cap_folder / 'completion_manifest_v1.json')
        manifest = base._json(cap_folder / 'summary.json', receipt['artifacts']['summary']['sha256'])
        expected = list(range(0, len(rows), cap['chunk_size']))
        if [e['first'] for e in manifest['chunks']] != expected:
            raise ValueError('complete ordered capture chunk coverage required')
        hidden = {seed: np.zeros((len(rows), capture.programs.MAX_POINTS, len(profile['layers']), old.PROJECTION_RANK), np.float32)
                  for seed in old.SEEDS}
        transforms = {seed: old.projection(profile['hidden_size'], seed) for seed in old.SEEDS}
        for entry in manifest['chunks']:
            first, count = entry['first'], entry['rows']
            if count != len(cases[first:first + cap['chunk_size']]):
                raise ValueError('capture chunk row coverage differs')
            features = capture.load_chunk(entry, cases[first:first + count], profile)
            for seed in old.SEEDS:
                transform = transforms[seed]
                for layer in range(len(profile['layers'])):
                    # Preserve the exact original GEMM shape/strides, rather
                    # than regrouping token/layer axes in a batched multiply.
                    hidden[seed][first:first + count, :, layer] = features[:, :, layer] @ transform
        caches = {}
        for seed, values in hidden.items():
            path = folder / f'projected_seed{seed}.npz'
            storage._npz(path, features=values)
            caches[f'hidden_seed{seed}'] = storage._pin(path)
        surface = source_nodes(cases)
        path = folder / 'source_nodes.npz'
        storage._npz(path, features=surface)
        caches['source'] = storage._pin(path)
        old.audit(probe_config)
        behavior.audit(behavior_config)
        probe_folder = Path(probe_config['run_dir'])
        result = base._json(probe_folder / 'results.json')
        records = [base._json(p) for p in sorted(probe_folder.glob('cv_*.json'))]
        if len(records) != 81 or old.choose(records) != result['selected_methods']:
            raise ValueError('locked TRAIN architecture selection differs')
        train_groups = {r['component_id'] for r in rows if r['split'] == 'train'}
        for record in records:
            fit, validation = set(record['fit_groups']), set(record['validation_groups'])
            if fit & validation or fit | validation != train_groups or len(fit) != 144 or len(validation) != 72:
                raise ValueError('CV structural group separation differs')
        table = old.examples(rows, cases)
        truth = np.asarray([e['parent'] for e in table])
        controls = old.random_targets(table)
        train_mask = np.asarray([e['split'] == 'train' for e in table])
        source_features = old.pair_features(surface, table, cases)
        del surface
        layer = profile['layers'].index(probe_config['layer'])
        banks, applications = [], 0
        for seed in old.SEEDS:
            for backend in old.BACKENDS:
                q, c, mask = source_features if backend == 'source_local' else old.pair_features(
                    hidden[seed][:, :, layer], table, cases, global_query=backend == 'hidden_global')
                for bank in [b for b in result['fits'] if b['seed'] == seed and b['backend'] == backend]:
                    target = truth if bank['target'] == 'real' else controls
                    model, norm = restore_scorer(bank['artifacts']['parameters']['path'], bank['method'])
                    actual = old.scores(model, norm, q, c, mask)
                    with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as saved:
                        if (not np.array_equal(saved['labels'], target) or not np.array_equal(saved['real_labels'], truth)
                                or not np.array_equal(saved['development'], ~train_mask)
                                or not np.array_equal(saved['point_indices'], [e['point'] for e in table])
                                or not np.array_equal(saved['case_ids'], [e['case_id'] for e in table])):
                            raise ValueError('saved dependency target/row order differs')
                        difference = replay_check(actual, saved['logits'], mask)
                    computed = independent_metrics(actual[~train_mask], target[~train_mask], [e for e in table if e['split'] == 'development'])
                    for key in ('individual_accuracy', 'family_macro_accuracy', 'whole_program_graph_accuracy'):
                        if not np.isclose(computed[key], bank['development'][key], rtol=0, atol=1e-12):
                            raise ValueError('independent dependency metric differs')
                    banks.append(dict(backend=backend, method=bank['method'], seed=seed, target=bank['target'],
                        training_families=bank['training_families'], replay_max_abs_difference=difference, development=computed))
                    applications += len(table)
                    print(f"replay {backend} groups{bank['training_families']} {bank['target']} seed{seed}", flush=True)
        if len(banks) != 54:
            raise ValueError('all completed dependency readouts must replay')
        summary = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=digest(config),
            model=profile['model'], cases=len(rows), layers=profile['layers'], nominated_layer=probe_config['layer'],
            ordered_ids_sha256=digest([r['id'] for r in rows]), caches=caches, replayed_banks=banks,
            selected_methods=result['selected_methods'], behavior=base._json(Path(behavior_config['run_dir']) / 'summary.json')['metrics'],
            inputs=dict(probe_results=storage._pin(probe_folder / 'results.json'),
                capture_summary=storage._pin(cap_folder / 'summary.json'),
                behavior_summary=storage._pin(Path(behavior_config['run_dir']) / 'summary.json')),
            parameter_application_uses=applications, new_fits=0, new_model_queries=0,
            generated_holdouts_opened=False, limitations='Postrun discovery audit. Supplied spans and source recency oracle remain explicit; '
                'projection caches preserve all four layers but do not establish causal use or arbitrary graph discovery.')
        base._put(folder / 'summary_review_v1.json', summary)
        artifacts = dict(caches, summary=storage._pin(folder / 'summary_review_v1.json'))
        base._put(folder / 'completion_manifest_v1.json', dict(status='complete_exploratory', source=source,
            config_hash=digest(config), evaluation_role=ROLE, artifacts=artifacts))
        return summary


def audit(config):
    receipt = base._json(Path(config['run_dir']) / 'completion_manifest_v1.json')
    if receipt['config_hash'] != digest(config) or receipt['status'] != 'complete_exploratory':
        raise ValueError('state audit receipt differs')
    base._verify_source(config, receipt['source'])
    for entry in receipt['artifacts'].values():
        if base._sha(entry['path']) != entry['sha256']:
            raise ValueError('state audit/cache payload changed')
    return receipt
