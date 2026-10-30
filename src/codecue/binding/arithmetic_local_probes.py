"""Shared dependency scorers on causal local or global arithmetic states.

Backbones stay frozen. Only small CPU readouts are trained. Architecture is
selected by grouped TRAIN validation before the fresh discovery DEV is scored.
"""
from collections import defaultdict
import hashlib
import io
from pathlib import Path

import numpy as np

from . import arithmetic_local_capture as capture
from . import arithmetic_probe_selection as selection
from . import arithmetic_graph_readouts as original
from . import relationship_capture as base
from .datasets import digest

ROLE = 'discovery_arithmetic_local_probes_v1'
METHODS = ('linear', 'bilinear', 'mlp')
BACKENDS = ('hidden_local', 'hidden_global', 'source_local')
SEEDS = (11, 29, 47)
DIMENSION = 80
PROJECTION_RANK = 64
MAX_CANDIDATES = 10
EPOCHS = 25
FAMILY_BUDGETS = (54, 108, 216)


def examples(rows, cases):
    result = []
    for index, (row, case) in enumerate(zip(rows, cases)):
        if row['split'] == 'calibration':
            continue
        for point_index, point in enumerate(case['descriptors']):
            if point['kind'] != 'use':
                continue
            definitions = [case['descriptors'][i] for i in point['candidate_points']]
            matching = [p['statement'] for p in definitions if p['name'] == point['name']]
            if not matching or max(matching) != point['parent']:
                raise ValueError('exact source recency oracle and read-time label differ')
            result.append(dict(row=index, point=point_index, candidates=point['candidate_points'],
                parent=point['parent'], statement=point['statement'], side=point['side'],
                group=row['component_id'], split=row['split'], depth=row['depth'],
                stratum=row['family_stratum'], case_id=row['id']))
    return result


def random_targets(table):
    # Random family labels are stable across numeric/lexical relatives, valid
    # past candidates, and independent of every observed semantic target.
    return np.asarray([int(hashlib.sha256(digest(['random-family-edge', e['group'], e['statement'], e['side'], 117]).encode()).hexdigest(), 16)
        % e['statement'] for e in table], dtype=np.int64)


def family_weights(table, seed):
    counts = defaultdict(int)
    for e in table:
        counts[e['group']] += 1
    groups = sorted(counts)
    values = np.random.default_rng(seed).exponential(1., len(groups)) + .1
    mapping = dict(zip(groups, values))
    return np.asarray([mapping[e['group']] / counts[e['group']] for e in table], np.float32)


def family_subset(table, budget):
    if budget not in FAMILY_BUDGETS or any(e['split'] != 'train' for e in table):
        raise ValueError('declared structure count and TRAIN-only examples required')
    strata = defaultdict(set)
    for e in table:
        strata[e['stratum']].add(e['group'])
    if len(strata) != 9 or any(len(v) != 24 for v in strata.values()):
        raise ValueError('complete 216-family TRAIN cohort required')
    selected = set()
    for stratum, groups in sorted(strata.items()):
        groups = sorted(groups)
        rng = np.random.default_rng(int(hashlib.sha256(stratum.encode()).hexdigest()[:8], 16) + 117)
        selected.update(np.asarray(groups)[rng.permutation(len(groups))[:budget // 9]])
    return selected


def projection(width, seed):
    return (np.random.default_rng(seed + 1000).integers(0, 2, (width, PROJECTION_RANK)) * 2 - 1).astype(np.float32) / np.sqrt(PROJECTION_RANK)


def pair_features(nodes, table, cases, *, global_query=False):
    q = np.zeros((len(table), DIMENSION), np.float32)
    c = np.zeros((len(table), MAX_CANDIDATES, DIMENSION), np.float32)
    mask = np.zeros((len(table), MAX_CANDIDATES), bool)
    for i, e in enumerate(table):
        row, statement = e['row'], e['statement']
        query_point = cases[row]['point_count'] - 1 if global_query else e['point']
        q[i, :PROJECTION_RANK] = nodes[row, query_point]
        q[i, PROJECTION_RANK + statement] = 1
        q[i, PROJECTION_RANK + 10 + int(e['side'] == 'right')] = 1
        q[i, -1] = e['depth'] / 6
        for candidate, point in enumerate(e['candidates']):
            c[i, candidate, :PROJECTION_RANK] = nodes[row, point]
            c[i, candidate, PROJECTION_RANK + candidate] = 1
            c[i, candidate, -1] = (statement - candidate) / 10
            mask[i, candidate] = True
    return q, c, mask


def normalize(q, c, mask):
    scale_q, scale_c = q.std(axis=0), c[mask].std(axis=0)
    scale_q[scale_q == 0] = 1
    scale_c[scale_c == 0] = 1
    return dict(mean_q=q.mean(axis=0), scale_q=scale_q, mean_c=c[mask].mean(axis=0), scale_c=scale_c)


def normalized(q, c, norm):
    return ((q - norm['mean_q']) / norm['scale_q']).astype(np.float32), ((c - norm['mean_c']) / norm['scale_c']).astype(np.float32)


def make_model(kind, dimension=DIMENSION):
    import torch
    from torch import nn
    if kind not in METHODS:
        raise ValueError('declared shared scorer required')

    class Scorer(nn.Module):
        def __init__(self):
            super().__init__()
            if kind in ('linear', 'bilinear'):
                self.query = nn.Linear(dimension, 1, bias=False)
                self.candidate = nn.Linear(dimension, 1)
            if kind == 'bilinear':
                self.query_interaction = nn.Linear(dimension, 16, bias=False)
                self.candidate_interaction = nn.Linear(dimension, 16, bias=False)
            if kind == 'mlp':
                self.network = nn.Sequential(nn.Linear(dimension * 2, 32), nn.Tanh(), nn.Linear(32, 1))

        def forward(self, q, c, mask):
            if kind == 'mlp':
                scores = self.network(torch.cat((q[:, None, :].expand_as(c), c), dim=-1)).squeeze(-1)
            else:
                scores = self.query(q) + self.candidate(c).squeeze(-1)
                if kind == 'bilinear':
                    scores = scores + (self.query_interaction(q)[:, None, :] * self.candidate_interaction(c)).sum(dim=-1) / 4
            return scores.masked_fill(~mask, -1e9)
    return Scorer()


def train(q, c, mask, labels, weights, kind, seed, *, epochs=EPOCHS):
    import torch
    from torch.nn import functional as functional
    if (q.shape != (len(labels), DIMENSION) or c.shape != (len(labels), MAX_CANDIDATES, DIMENSION)
            or mask.shape != (len(labels), MAX_CANDIDATES) or weights.shape != (len(labels),)
            or np.any(weights <= 0) or not np.isfinite(weights).all()
            or not np.isfinite(q).all() or not np.isfinite(c).all()
            or np.any(labels < 0) or np.any(labels >= MAX_CANDIDATES)
            or not mask[np.arange(len(labels)), labels].all()):
        raise ValueError('aligned finite valid candidate features/labels/weights required')
    torch.manual_seed(seed)
    model = make_model(kind)
    norm = normalize(q, c, mask)
    q, c = normalized(q, c, norm)
    tq, tc, tm, ty, tw = [torch.from_numpy(a) for a in (q, c, mask, labels.astype(np.int64), weights)]
    optimizer = torch.optim.AdamW(model.parameters(), lr=.01, weight_decay=.001)
    rng = np.random.default_rng(seed)
    model.train()
    for _ in range(epochs):
        order = rng.permutation(len(labels))
        for first in range(0, len(labels), 512):
            batch = order[first:first + 512]
            optimizer.zero_grad(set_to_none=True)
            losses = functional.cross_entropy(model(tq[batch], tc[batch], tm[batch]), ty[batch], reduction='none')
            loss = (losses * tw[batch]).sum() / tw[batch].sum()
            if not torch.isfinite(loss):
                raise ValueError('nonfinite shared probe loss')
            loss.backward()
            optimizer.step()
    model.eval()
    return model, norm


def scores(model, norm, q, c, mask):
    import torch
    q, c = normalized(q, c, norm)
    result = []
    with torch.inference_mode():
        for first in range(0, len(q), 1024):
            last = first + 1024
            result.append(model(torch.from_numpy(q[first:last]), torch.from_numpy(c[first:last]), torch.from_numpy(mask[first:last])).numpy())
    return np.concatenate(result)


def metrics(logits, labels, table):
    predicted = logits.argmax(axis=1)
    correct = predicted == labels
    groups, programs, strata = defaultdict(list), defaultdict(list), defaultdict(list)
    for i, e in enumerate(table):
        groups[e['group']].append(bool(correct[i]))
        programs[e['case_id']].append(bool(correct[i]))
        strata[f"depth{e['depth']}_{e['side']}"].append(bool(correct[i]))
    family = {g: float(np.mean(v)) for g, v in groups.items()}
    return dict(individual_accuracy=float(correct.mean()), family_macro_accuracy=float(np.mean(list(family.values()))),
        whole_program_graph_accuracy=float(np.mean([all(v) for v in programs.values()])),
        family_metrics=family, depth_side_accuracy={s: float(np.mean(v)) for s, v in strata.items()},
        uses=len(table), families=len(family), source_name_recency_oracle_accuracy=1.,
        uniform_candidate_reference=float(np.mean([1 / e['statement'] for e in table])))


def choose(records):
    values = defaultdict(dict)
    for row in records:
        key, point = (row['backend'], row['method']), (row['fold'], row['seed'])
        if point in values[key]:
            raise ValueError('duplicate local selection point')
        values[key][point] = row['validation']['family_macro_accuracy']
    expected = {(b, m) for b in BACKENDS for m in METHODS}
    observations = {(fold, seed) for fold in range(3) for seed in SEEDS}
    if set(values) != expected or any(set(v) != observations for v in values.values()):
        raise ValueError('complete local three-fold three-seed grid required')
    return {b: max(METHODS, key=lambda m: (np.mean(list(values[(b, m)].values())), -METHODS.index(m))) for b in BACKENDS}


def run(config):
    from sklearn.feature_extraction.text import HashingVectorizer
    from .confidence import _run_lock
    base._slurm()
    if (config.get('evaluation_role') != ROLE or config.get('epochs') != EPOCHS
            or config.get('seeds') != list(SEEDS) or config.get('projection_rank') != PROJECTION_RANK):
        raise ValueError('declared shared local probe recipe required')
    source = base._current_source(config)
    cap = base._json(config['capture_config'], config['capture_config_sha256'])
    capture.audit(cap)
    profile, rows, preflight, cases = capture.inputs(cap)
    if config.get('layer') not in profile['layers']:
        raise ValueError('archived nominated layer required')
    table = examples(rows, cases)
    labels = np.asarray([e['parent'] for e in table])
    control = random_targets(table)
    train_mask = np.asarray([e['split'] == 'train' for e in table])
    train_table = [e for e in table if e['split'] == 'train']
    fold_rows = [dict(split='train', component_id=e['group'], operation_family=e['stratum']) for e in train_table]
    folds = selection.folds(fold_rows)
    folder = Path(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return audit(config)
        manifest = base._json(Path(cap['run_dir']) / 'summary.json')
        source_nodes = np.zeros((len(rows), capture.programs.MAX_POINTS, PROJECTION_RANK), np.float32)
        prefixes, coordinates = [], []
        for i, case in enumerate(cases):
            for j in range(case['point_count']):
                position = case['positions'][j]
                end = case['token_offsets'][position][1]
                prefixes.append(case['prompt'] if j == case['point_count'] - 1 else case['prompt'][:end])
                coordinates.append((i, j))
        hashed = HashingVectorizer(analyzer='char', ngram_range=(3, 5), n_features=PROJECTION_RANK,
            alternate_sign=True, norm=None).transform(prefixes).toarray().astype(np.float32)
        for coordinate, vector in zip(coordinates, hashed):
            source_nodes[coordinate] = vector
        source_features = pair_features(source_nodes, table, cases)
        del source_nodes, hashed, prefixes, coordinates
        artifacts, records, finals = {}, [], []

        def features(seed):
            projected = np.zeros((len(rows), capture.programs.MAX_POINTS, PROJECTION_RANK), np.float32)
            transform = projection(profile['hidden_size'], seed)
            layer = profile['layers'].index(config['layer'])
            for entry in manifest['chunks']:
                first, count = entry['first'], entry['rows']
                block = capture.load_chunk(entry, cases[first:first + count], profile)
                projected[first:first + count] = block[:, :, layer] @ transform
            return dict(hidden_local=pair_features(projected, table, cases),
                hidden_global=pair_features(projected, table, cases, global_query=True), source_local=source_features)

        for seed in SEEDS:
            data = None
            for backend in BACKENDS:
                for fold in range(3):
                    fit = folds != fold
                    valid = ~fit
                    fit_table = [e for e, yes in zip(train_table, fit) if yes]
                    valid_table = [e for e, yes in zip(train_table, valid) if yes]
                    for method in METHODS:
                        key = f'cv_{backend}_{method}_fold{fold}_seed{seed}'
                        path = folder / (key + '.json')
                        if path.exists():
                            record = base._json(path)
                            if record['source'] != source or record['config_hash'] != digest(config):
                                raise ValueError('local CV resume identity differs')
                        else:
                            if data is None:
                                data = features(seed)
                            q, c, mask = [a[train_mask] for a in data[backend]]
                            model, norm = train(q[fit], c[fit], mask[fit], labels[train_mask][fit], family_weights(fit_table, seed), method, seed)
                            validation = metrics(scores(model, norm, q[valid], c[valid], mask[valid]), labels[train_mask][valid], valid_table)
                            record = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                                backend=backend, method=method, fold=fold, seed=seed, validation=validation,
                                fit_groups=sorted({e['group'] for e in fit_table}), validation_groups=sorted({e['group'] for e in valid_table}),
                                fitted_parameters=sum(p.numel() for p in model.parameters()))
                            base._put(path, record)
                            print(key, flush=True)
                        records.append(record)
                        artifacts[key] = original._pin(path)
                        capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records), planned=135))
            del data
        chosen = choose(records)
        base._put(folder / 'selection_review_v1.json', dict(status='selection_locked', source=source, config_hash=digest(config),
            methods=chosen, fit_split='TRAIN only', tie_break='linear, then bilinear, then MLP',
            candidate_records=len(records), calibration_excluded=True))
        artifacts['selection'] = original._pin(folder / 'selection_review_v1.json')
        for seed in SEEDS:
            data = None
            for backend, budget in [(b, n) for b in BACKENDS for n in FAMILY_BUDGETS]:
                selected_groups = family_subset(train_table, budget)
                fit_mask = np.asarray([e['split'] == 'train' and e['group'] in selected_groups for e in table])
                fit_table = [e for e, yes in zip(table, fit_mask) if yes]
                for target_name, target in [('real', labels), ('random_family', control)]:
                    key = f'selected_{backend}_groups{budget}_{target_name}_seed{seed}'
                    path = folder / (key + '.json')
                    if path.exists():
                        result = base._json(path)
                        if result['source'] != source or result['config_hash'] != digest(config):
                            raise ValueError('local final resume identity differs')
                        for entry in result['artifacts'].values():
                            if base._sha(entry['path']) != entry['sha256']:
                                raise ValueError('local final payload changed')
                    else:
                        if data is None:
                            data = features(seed)
                        q, c, mask = data[backend]
                        method = chosen[backend]
                        model, norm = train(q[fit_mask], c[fit_mask], mask[fit_mask], target[fit_mask], family_weights(fit_table, seed), method, seed)
                        logits = scores(model, norm, q, c, mask)
                        state = {k: v.detach().numpy() for k, v in model.state_dict().items()}
                        parameters = folder / (key + '_parameters.npz')
                        original._npz(parameters, **{'state_' + k: v for k, v in state.items()}, **norm)
                        import torch
                        with np.load(parameters, allow_pickle=False) as saved:
                            replay = make_model(method)
                            replay.load_state_dict({k[6:]: torch.from_numpy(saved[k].copy()) for k in saved.files if k.startswith('state_')})
                            replay.eval()
                            replay_norm = {k: saved[k] for k in norm}
                        repeated = scores(replay, replay_norm, q, c, mask)
                        if not np.array_equal(logits, repeated):
                            raise ValueError('saved local scorer replay differs')
                        score_path = folder / (key + '_scores.npz')
                        original._npz(score_path, logits=logits, labels=target, real_labels=labels, development=~train_mask,
                            case_ids=np.asarray([e['case_id'] for e in table]), point_indices=np.asarray([e['point'] for e in table]))
                        result = dict(status='complete_exploratory', source=source, config_hash=digest(config),
                            backend=backend, method=method, seed=seed, target=target_name,
                            training_families=budget, fit_groups=sorted(selected_groups),
                            train=metrics(logits[fit_mask], target[fit_mask], fit_table),
                            development=metrics(logits[~train_mask], target[~train_mask], [e for e in table if e['split'] == 'development']),
                            artifacts=dict(parameters=original._pin(parameters), scores=original._pin(score_path)))
                        base._put(path, result)
                        print(key, flush=True)
                    finals.append(result)
                    artifacts[key] = original._pin(path)
                    capture.legacy._CORE._journal(folder / 'progress.json', dict(fits=len(records) + len(finals), planned=135))
            del data
        result = dict(status='complete_exploratory', source=source, config_hash=digest(config), evaluation_role=ROLE,
            model=profile['model'], selected_methods=chosen, fits=finals, new_model_queries=0,
            generated_holdouts_opened=False, source_name_recency_oracle_accuracy=1.,
            limitations='Adaptive discovery with supplied node spans, candidate boundaries and statement/side metadata. '
                'Hidden vectors use fixed seed-specific 64-dimensional random projections before small readouts; '
                'linear concatenation lacks query-candidate interaction. Global queries also receive operand identity metadata. '
                'Bilinear rank16 and MLP width32 are capacity diagnostics. Exact source recency solves this target. '
                'Success is accessibility, not source superiority, arbitrary graph discovery or natural causal use.')
        base._put(folder / 'results.json', result)
        artifacts['results'] = original._pin(folder / 'results.json')
        base._put(folder / 'completion_manifest_v1.json', dict(status='complete_exploratory', source=source,
            config_hash=digest(config), evaluation_role=ROLE, artifacts=artifacts))
        return result


def audit(config):
    folder = Path(config['run_dir'])
    receipt = base._json(folder / 'completion_manifest_v1.json')
    if receipt['config_hash'] != digest(config) or receipt['status'] != 'complete_exploratory':
        raise ValueError('local probe completion identity differs')
    base._verify_source(config, receipt['source'])
    for entry in receipt['artifacts'].values():
        if base._sha(entry['path']) != entry['sha256']:
            raise ValueError('local probe metadata changed')
    result = base._json(folder / 'results.json')
    if len(result['fits']) != 54:
        raise ValueError('all matched real/control local probe fits required')
    for fit in result['fits']:
        for entry in fit['artifacts'].values():
            if base._sha(entry['path']) != entry['sha256']:
                raise ValueError('local probe payload changed')
    return receipt
