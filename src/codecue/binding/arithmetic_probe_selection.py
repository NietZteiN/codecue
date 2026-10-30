"""Grouped TRAIN-only selection of archived arithmetic representation probes.

The previously examined DEV cohort is used once after a durable selection file
has been written. It remains adaptive discovery, never fresh confirmation.
Rank means principal-component regression in the weighted, standardized TRAIN
feature space. Full rank is the ordinary independent ridge objective.
"""
from collections import defaultdict
from pathlib import Path
import io

import numpy as np

from . import arithmetic_graph_capture as capture
from . import arithmetic_graph_readouts as original
from . import relationship_capture as base
from .datasets import digest
from .weighted_ridge import _array_hash

ROLE = 'discovery_arithmetic_probe_selection_v1'
ALPHAS = (1., 100., 10000.)
RANKS = (32, 128, 'full')
SEEDS = (11, 29, 47)
TASKS = ('parent_accuracy', 'relation_balanced_accuracy', 'value_negative_mae')


def folds(rows):
    """Assign whole structures, stratified by operation family, to three folds."""
    families = {}
    for row in rows:
        if row['split'] != 'train':
            raise ValueError('selection accepts TRAIN rows only')
        group = row['component_id']
        if group in families and families[group] != row['operation_family']:
            raise ValueError('structural family has inconsistent operation strata')
        families[group] = row['operation_family']
    assigned = {}
    for kind in sorted(set(families.values())):
        groups = sorted(g for g in families if families[g] == kind)
        if len(groups) < 3:
            raise ValueError('at least three structures per operator stratum required')
        assigned.update({g: i % 3 for i, g in enumerate(groups)})
    return np.asarray([assigned[r['component_id']] for r in rows])


def targets(rows):
    _, binary, values, heads, _ = original.targets(rows, 2)
    truth = np.asarray([original.programs.oracle(r['canonical_source'])['parents'] for r in rows])
    if truth.shape != (len(rows), 8):
        raise ValueError('four ordered two-operand writes required')
    labels = np.concatenate([binary.astype(float), *[np.eye(8)[truth[:, i]] for i in range(8)], values], axis=1)
    return labels, binary, truth, values


def support(rows, binary):
    # Lexical and queried-slot relatives must not inflate relation support.
    unique = np.asarray([r['lexical_realization'] == 0 and r['query_slot'] == 0 for r in rows])
    return (binary[unique].sum(axis=0) >= 12) & ((~binary[unique]).sum(axis=0) >= 12)


def metrics(scores, labels, eligible, groups):
    binary = labels[:, :48].astype(bool)
    predicted = scores[:, :48] >= .5
    parents = scores[:, 48:112].reshape(-1, 8, 8).argmax(axis=2)
    truth = labels[:, 48:112].reshape(-1, 8, 8).argmax(axis=2)
    by_family = []
    for group in sorted(set(groups)):
        mask = groups == group
        relation_families = defaultdict(list)
        for i, relation in enumerate(original.RELATIONS):
            t, p = binary[mask, i], predicted[mask, i]
            if eligible[i] and t.any() and (~t).any():
                relation_families[relation[0]].append(float((p[t].mean() + (~p[~t]).mean()) / 2))
        relation = float(np.mean([np.mean(v) for v in relation_families.values()])) if relation_families else None
        by_family.append(dict(group=str(group), parent_accuracy=float((parents[mask] == truth[mask]).mean()),
            relation_balanced_accuracy=relation, value_negative_mae=-float(np.abs(scores[mask, -4:] - labels[mask, -4:]).mean())))
    result = {task: float(np.mean([f[task] for f in by_family if f[task] is not None]))
              if any(f[task] is not None for f in by_family) else None for task in TASKS}
    result.update(whole_parent_accuracy=float((parents == truth).all(axis=1).mean()),
        rounded_value_accuracy=float((np.rint(scores[:, -4:]) == labels[:, -4:]).mean()),
        whole_rounded_state_accuracy=float((np.rint(scores[:, -4:]) == labels[:, -4:]).all(axis=1).mean()),
        relation_supported_cells=int(eligible.sum()), family_metrics=by_family)
    derived = original.relations(np.rint(scores[:, -4:]))
    derived_families = defaultdict(list)
    for i, relation in enumerate(original.RELATIONS):
        t = binary[:, i]
        if eligible[i] and t.any() and (~t).any():
            derived_families[relation[0]].append(float((derived[t, i].mean() + (~derived[~t, i]).mean()) / 2))
    result['rounded_value_derived_relation_balanced_accuracy'] = float(np.mean([np.mean(v) for v in derived_families.values()])) if derived_families else None
    return result


class SpectralRidge:
    """One TRAIN eigendecomposition supports the fixed alpha/rank grid."""
    def __init__(self, x, y, weights):
        from scipy.linalg import eigh
        x, y, weights = np.asarray(x, float), np.asarray(y, float), np.asarray(weights, float)
        if (x.ndim != 2 or y.ndim != 2 or len(x) != len(y) or weights.shape != (len(x),)
                or not all(np.isfinite(a).all() for a in (x, y, weights)) or np.any(weights <= 0)):
            raise ValueError('finite matrices and positive aligned sample weights required')
        self.mean = x.mean(axis=0)
        self.scale = x.std(axis=0)
        self.scale[self.scale == 0] = 1
        z = (x - self.mean) / self.scale
        self.center = np.average(z, axis=0, weights=weights)
        self.intercept = np.average(y, axis=0, weights=weights)
        self.design = (z - self.center) * np.sqrt(weights)[:, None]
        gram = self.design @ self.design.T
        values, vectors = eigh(gram, check_finite=False, driver='evd')
        order = np.argsort(values)[::-1]
        values, vectors = values[order], vectors[:, order]
        keep = values > max(float(values[0]) * 1e-12, 1e-12)
        self.values, self.vectors = values[keep], vectors[:, keep]
        if not len(self.values):
            # Constant features are a valid prior-only diagnostic.
            self.values, self.vectors = np.empty(0), np.empty((len(x), 0))
        self.rhs = self.vectors.T @ ((y - self.intercept) * np.sqrt(weights)[:, None])
        self.training_hashes = dict(features=_array_hash(x), targets=_array_hash(y), sample_weight=_array_hash(weights))

    def coefficients(self, alpha, rank):
        if alpha not in ALPHAS or rank not in RANKS:
            raise ValueError('fixed positive alpha/rank grid required')
        n = len(self.values) if rank == 'full' else min(rank, len(self.values))
        return self.design.T @ (self.vectors[:, :n] @ (self.rhs[:n] / (self.values[:n, None] + alpha)))

    def parameters(self, alpha, rank):
        return dict(mean=self.mean, scale=self.scale, center=self.center,
            intercept=self.intercept, coef=self.coefficients(alpha, rank))

    def predictions(self, x, candidates):
        cross = (((np.asarray(x, float) - self.mean) / self.scale) - self.center) @ self.design.T
        outputs = {}
        for alpha, rank in candidates:
            if alpha not in ALPHAS or rank not in RANKS:
                raise ValueError('fixed grid required')
            n = len(self.values) if rank == 'full' else min(rank, len(self.values))
            dual = self.vectors[:, :n] @ (self.rhs[:n] / (self.values[:n, None] + alpha))
            outputs[(alpha, rank)] = cross @ dual + self.intercept
        return outputs


def predict(parameters, x):
    return (((np.asarray(x, float) - parameters['mean']) / parameters['scale']) - parameters['center']) @ parameters['coef'] + parameters['intercept']


def weights(rows, seed):
    groups = sorted({r['component_id'] for r in rows})
    values = np.random.default_rng(seed).exponential(1., len(groups)) + .1
    mapping = dict(zip(groups, values))
    return np.asarray([mapping[r['component_id']] for r in rows])


def choose(records):
    """All nine fold/seed observations required; deterministic declared tie break."""
    collected = defaultdict(dict)
    for record in records:
        key = (record['representation'], record['alpha'], record['rank'])
        point = (record['fold'], record['seed'])
        if point in collected[key]:
            raise ValueError('duplicate selection observation')
        collected[key][point] = record['metrics']
    expected = {(fold, seed) for fold in range(3) for seed in SEEDS}
    if not collected or any(set(v) != expected for v in collected.values()):
        raise ValueError('complete three-fold, three-seed selection grid required')
    choices = {}
    for backend in ('hidden', 'source'):
        choices[backend] = {}
        for task in TASKS:
            candidates = []
            for (representation, alpha, rank), observations in collected.items():
                if representation.startswith(backend) and all(m[task] is not None for m in observations.values()):
                    score = float(np.mean([m[task] for m in observations.values()]))
                    candidates.append((score, -(10**9 if rank == 'full' else rank), alpha,
                        representation, dict(representation=representation, alpha=alpha, rank=rank, selection_score=score)))
            if not candidates:
                raise ValueError('no completely supported candidate for ' + backend + '/' + task)
            choices[backend][task] = max(candidates, key=lambda c: c[:4])[-1]
    return choices


def _npz(path, **values):
    stream = io.BytesIO()
    np.savez_compressed(stream, **values)
    base._publish(path, stream.getvalue())


def run(config):
    from sklearn.feature_extraction.text import HashingVectorizer
    from .confidence import _run_lock
    base._slurm()
    if config.get('evaluation_role') != ROLE or config.get('site') != 2:
        raise ValueError('explicit answer-preparation adaptive selection role required')
    if (config.get('alphas') != list(ALPHAS) or config.get('ranks') != list(RANKS)
            or config.get('seeds') != list(SEEDS)):
        raise ValueError('prospectively fixed grid required')
    source = base._current_source(config)
    cache = {}
    if config.get('cv_reuse'):
        from .arithmetic_probe_reuse import verified_cache
        cache = verified_cache(config, source)
    cap = base._json(config['capture_config'], config['capture_config_sha256'])
    folder = base._safe(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return audit(config)
        capture.audit(cap)
        preflight, cases = capture.inputs(cap)
        rows, _ = capture._CORE._dataset(cap)
        train = np.asarray([r['split'] == 'train' for r in rows])
        train_rows = [r for r in rows if r['split'] == 'train']
        groups = np.asarray([r['component_id'] for r in rows])
        fold_ids = folds(train_rows)
        labels, binary, _, _ = targets(train_rows)
        inner = {}
        for fold in range(3):
            fit_mask = fold_ids != fold
            fit_rows = [r for r, yes in zip(train_rows, fit_mask) if yes]
            inner[fold] = dict(fit=fit_mask, valid=~fit_mask, weights={s: weights(fit_rows, s) for s in SEEDS},
                eligible=support(fit_rows, binary[fit_mask]))
        train_groups = groups[train]
        manifest = base._json(Path(cap['run_dir']) / 'summary.json')
        for entry in manifest['chunks']:
            if base._sha(entry['path']) != entry['sha256']:
                raise ValueError('archived activation changed')
        records, representations = [], ['hidden_layer_' + str(layer) for layer in cap['layers']] + ['source_char']

        def features(representation):
            if representation == 'source_char':
                return HashingVectorizer(analyzer='char', ngram_range=(3, 8), n_features=cap['hidden_size'],
                    alternate_sign=True, norm=None).transform(c['visible_prefixes'][2] for c in cases).toarray().astype(np.float32)
            layer = cap['layers'].index(int(representation.rsplit('_', 1)[1]))
            vectors = np.empty((len(rows), cap['hidden_size']), np.float32)
            for entry in manifest['chunks']:
                start, count = entry['first'], entry['rows']
                chunk, _ = capture.load_chunk(entry, cases[start:start + count], cap)
                vectors[start:start + count] = chunk[:, 2, layer]
            return vectors

        grid = [(alpha, rank) for alpha in ALPHAS for rank in RANKS]
        for representation in representations:
            x = None
            for fold, masks in inner.items():
                for seed in SEEDS:
                    path = folder / f'cv_{representation}_fold{fold}_seed{seed}.json'
                    if not path.exists() and path.name in cache:
                        reused, entry = cache[path.name]
                        base._put(path, dict(reused, source=source, config_hash=digest(config),
                            reused_from=dict(entry, source=reused['source'], config_hash=reused['config_hash'])))
                    if path.exists():
                        saved = base._json(path)
                        if saved['source'] != source or saved['config_hash'] != digest(config):
                            raise ValueError('selection resume identity changed')
                        records.extend(saved['records'])
                        continue
                    if x is None:
                        x = features(representation)[train]
                    fit_mask, valid = masks['fit'], masks['valid']
                    model = SpectralRidge(x[fit_mask], labels[fit_mask], masks['weights'][seed])
                    candidates = model.predictions(x[valid], grid)
                    block = [dict(representation=representation, fold=fold, seed=seed, alpha=alpha, rank=rank,
                        metrics=metrics(scores, labels[valid], masks['eligible'], train_groups[valid]))
                        for (alpha, rank), scores in candidates.items()]
                    base._put(path, dict(status='complete_exploratory', source=source, config_hash=digest(config),
                        training_hashes=model.training_hashes,
                        fit_groups=sorted(set(train_groups[fit_mask])), validation_groups=sorted(set(train_groups[valid])), records=block))
                    records.extend(block)
                    print(f'CV {representation} fold{fold} seed{seed}', flush=True)
                    del model, candidates
            del x
        selected = choose(records)
        if cache:
            request = config['cv_reuse']
            proof = base._json(request['manifest'], request['sha256'])
            entry = proof['original_selection']
            prior_selection = base._json(entry['path'], entry['sha256'])
            if selected != prior_selection['choices']:
                raise ValueError('reused CV changed previously locked choices')
        selection = dict(status='selection_locked', evaluation_role=ROLE, source=source, config_hash=digest(config),
            choices=selected, selection_split='TRAIN only; three grouped folds and three weighting seeds',
            tie_break='highest mean score; then smaller rank; larger alpha; lexicographically larger representation',
            family_count=len(set(train_groups)), training_ids=[r['id'] for r in train_rows],
            fold_by_group={r['component_id']: int(f) for r, f in zip(train_rows, fold_ids)}, candidate_records=len(records))
        # No DEV target generation or scoring takes place before this immutable commit.
        base._put(folder / 'selection_review_v1.json', selection)
        all_labels, all_binary, _, _ = targets(rows)
        donor = original.donor_indices(rows)
        joined = np.concatenate((all_labels[train], all_labels[donor[train]]), axis=1)
        eligible = support(train_rows, binary)
        final = []
        artifacts = {'selection': original._pin(folder / 'selection_review_v1.json')}
        for representation in sorted({v['representation'] for b in selected.values() for v in b.values()}):
            x = features(representation)
            relevant = [(backend, task, choice) for backend, tasks in selected.items() for task, choice in tasks.items()
                        if choice['representation'] == representation]
            for seed in SEEDS:
                key = f'selected_{representation}_seed{seed}'
                marker = folder / (key + '.json')
                if marker.exists():
                    saved = base._json(marker)
                    if saved['source'] != source or saved['config_hash'] != digest(config):
                        raise ValueError('final bank resume identity changed')
                    for entry in saved['artifacts'].values():
                        if base._sha(entry['path']) != entry['sha256']:
                            raise ValueError('resumed final bank payload changed')
                    final.extend(saved['results'])
                    artifacts[key] = original._pin(marker)
                    continue
                model = SpectralRidge(x[train], joined, weights(train_rows, seed))
                bank, stored = [], {}
                for backend, task, choice in relevant:
                    parameters = model.parameters(choice['alpha'], choice['rank'])
                    stem = key + '_' + task
                    parameter_path = folder / (stem + '_parameters.npz')
                    _npz(parameter_path, **parameters)
                    with np.load(parameter_path, allow_pickle=False) as data:
                        replay = {k: data[k] for k in data.files}
                    scores = predict(parameters, x)
                    if not np.array_equal(scores, predict(replay, x)):
                        raise ValueError('persisted parameter replay differs')
                    real, shuffled = np.split(scores, 2, axis=1)
                    prior = np.broadcast_to(model.intercept[:116], all_labels.shape)
                    score_path = folder / (stem + '_scores.npz')
                    _npz(score_path, ids=np.asarray([r['id'] for r in rows]), real=real, shuffled=shuffled,
                        truth=all_labels, shuffle_truth=all_labels[donor], donor=donor, development=~train)
                    result = dict(backend=backend, selected_for=task, choice=choice, seed=seed,
                        training_hashes=model.training_hashes, train=metrics(real[train], all_labels[train], eligible, groups[train]),
                        development=metrics(real[~train], all_labels[~train], eligible, groups[~train]),
                        development_prior=metrics(prior[~train], all_labels[~train], eligible, groups[~train]),
                        development_shuffle=metrics(shuffled[~train], all_labels[donor[~train]], eligible, groups[~train]),
                        artifacts=dict(parameters=original._pin(parameter_path), scores=original._pin(score_path)))
                    bank.append(result)
                    stored[task + '_parameters'] = result['artifacts']['parameters']
                    stored[task + '_scores'] = result['artifacts']['scores']
                base._put(marker, dict(status='complete_exploratory', source=source, config_hash=digest(config), results=bank, artifacts=stored))
                artifacts[key] = original._pin(marker)
                final.extend(bank)
                print(f'Final {representation} seed{seed}', flush=True)
        result = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=digest(config),
            model=cap['model'], choices=selected, fits=final, new_model_queries=0,
            generated_holdouts_opened=False, development_role='Previously inspected DEV; adaptive discovery only',
            limitations='Answer-preparation site only. Rank constrains weighted principal components, not supervised target rank. '
                'Numeric outputs are continuous regression with rounded-value diagnostics. Selection is grouped TRAIN-only; '
                'no claim of fresh confirmation, causal use, or representational absence.')
        base._put(folder / 'results.json', result)
        artifacts['results'] = original._pin(folder / 'results.json')
        base._put(folder / 'completion_manifest_v1.json', dict(status='complete_exploratory', evaluation_role=ROLE,
            source=source, config_hash=digest(config), artifacts=artifacts, new_model_queries=0))
        return result


def audit(config):
    folder = Path(config['run_dir'])
    receipt = base._json(folder / 'completion_manifest_v1.json')
    if receipt['config_hash'] != digest(config) or receipt['status'] != 'complete_exploratory':
        raise ValueError('selection completion identity differs')
    base._verify_source(config, receipt['source'])
    for entry in receipt['artifacts'].values():
        if base._sha(entry['path']) != entry['sha256']:
            raise ValueError('selection artifact changed')
    result = base._json(folder / 'results.json')
    if len(result['fits']) != 18:
        raise ValueError('three weighting seeds for both backends and all three selected tasks required')
    for bank in result['fits']:
        for entry in bank['artifacts'].values():
            if base._sha(entry['path']) != entry['sha256']:
                raise ValueError('selected model payload changed')
    return receipt
