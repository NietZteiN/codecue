"""Train-only structural/algebraic readouts and independent value comparators.

This CPU controller consumes separately audited causal-prefix captures. Oracle
values, edges, source metadata and strata are targets/validation metadata only;
features are raw hidden coordinates or exact visible-prefix character ngrams.
"""
from __future__ import annotations

from collections import Counter
import io
import json
import os
from pathlib import Path
import time

import numpy as np

from .datasets import digest, write_json
from .discovery_readouts import group_weights
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable as _published_immutable
from .registry import code_identity
from .representation_sensitivity import _json, _safe, _sha
from .weighted_ridge import fit as ridge_fit, from_parameters, _array_hash as _ridge_array_hash

ROLE = 'discovery_relationship_readouts_v1'
FIT_SITES = (3, 7, 8)
LAYERS = (8, 16, 24, 31)
SEEDS = (11, 29, 47)
FAMILIES = ('equal', 'less_than', 'sum_equals_third', 'difference_equals_third')
BOOTSTRAP = {'draws': 2000, 'seed': 117, 'minimum_valid_draws': 1900}
PRIMARY = {
    'algebraic': {'backend': 'hidden', 'site': 3, 'layer': 24, 'split': 'development',
        'metric': 'four_family_macro_balanced_accuracy', 'contrast': 'direct_minus_categorical_value_derived'},
    'structural': {'backend': 'hidden', 'site': 7, 'layer': 24, 'split': 'development',
        'metric': 'whole_parent_graph_accuracy', 'contrast': 'direct_minus_surface'},
}
MAX_RESULT_BYTES = 128*1024**2
COMPLETION_NAME = 'completion_manifest_v1.json'
LIMITATION = (
    'Prospective fixed readout recipe on an adaptive discovery bank, not final '
    'confirmation, natural causal use or mechanism C. Sites 3, 7 and 8 alone are '
    'fitted; other captured sites are reserved for later work. Raw 4096-dimensional '
    'hidden coordinates and matched 4096 character-ngram features have train-only '
    'float64 normalization and fixed alpha 100. Independent relation columns and '
    'value columns share a Gram factorization without output coupling. Primary '
    'algebraic comparisons use relations derived from four independent 32-class '
    'categorical value heads; rounded/clipped scalar-value derivation is secondary. '
    'Whole-pipeline parameter counts differ, so this is not an equal-total-capacity '
    'comparison. Numeric values, graph/stratum IDs and oracle relations never '
    'enter readout features. Binary ridge outputs are uncalibrated scores, with '
    'threshold 0.5. Undefined and constant tasks are retained and reported, not '
    'claimed as relationship learning. Primary eligibility uses only training '
    'group class support; all fixed eligible development cells must contain both '
    'classes. Components, not numeric/lexical relatives, are uncertainty units. '
    'Three seeds change component weights and coherent shuffle tasks, not '
    'independent experiments. Component derangements move initialization-prefix '
    'base blocks, with copy-parent permutations inside each base and lexical '
    'ties retained. This preserves unweighted target marginals, not necessarily '
    'weighted marginals. Conditional '
    'intervals resample nine development components without refitting or '
    'multiplicity adjustment. Successful relation decoding alone does not '
    'establish a dedicated relational representation or an identified algorithm.'
)


def protocol():
    return dict(fit_sites=list(FIT_SITES), layers=list(LAYERS), seeds=list(SEEDS), alpha=100.,
        feature_dimensions=4096, primary=PRIMARY, bootstrap=BOOTSTRAP,
        primary_train_class_group_minimum=12, binary_threshold=.5,
        scalar_value_derivation='clip[-64,64] then numpy.rint, secondary',
        categorical_value_derivation='four independent 32-class score argmax heads, primary',
        shuffle_recipe='component derangement; initialization-prefix base blocks; within-base copy-parent permutation; lexical ties',
        group_weight_recipe='discovery_readouts.group_weights: exponential+1e-6; float32 mean normalization then float64 cast')


def _config(config):
    required = {'evaluation_role', 'capture_config', 'capture_config_sha256', 'capture_audit',
        'capture_audit_sha256', 'capture_registration', 'capture_registration_sha256', 'run_dir', 'report'}
    fixed = protocol(); optional = {'capture_summary', 'capture_summary_sha256'}
    if (not isinstance(config, dict) or config.get('evaluation_role') != ROLE
            or required-set(config) or set(config)-required-set(fixed)-optional):
        raise ValueError('explicit discovery relationship-readout configuration required')
    _discovery_declaration(config)
    if any(name in config and config[name] != value for name, value in fixed.items()):
        raise ValueError('fixed prospective relationship readout recipe differs')
    if ('capture_summary' in config) != ('capture_summary_sha256' in config):
        raise ValueError('optional capture summary path and pin must be supplied together')
    for key in ('capture_config', 'capture_audit', 'capture_registration', 'run_dir', 'report', *(['capture_summary'] if 'capture_summary' in config else [])):
        if not isinstance(config[key], str) or not config[key]: raise ValueError('explicit source/output path required')
        _discovery_response_path(config[key]); _safe(config[key])
    for key in ('capture_config_sha256', 'capture_audit_sha256', 'capture_registration_sha256', *(['capture_summary_sha256'] if 'capture_summary' in config else [])):
        value = config[key]
        if not isinstance(value, str) or len(value) != 64 or any(character not in '0123456789abcdef' for character in value):
            raise ValueError('explicit source metadata SHA256 pins required')
    out = Path(config['run_dir']).resolve(); report = Path(config['report']).resolve()
    reserved = {path.resolve() for name, path in _expected_artifacts(config).items() if name != 'report'}
    reserved.update({out/COMPLETION_NAME, out/'progress.json', out})
    sources = {Path(config[key]).resolve() for key in ('capture_config', 'capture_audit', 'capture_registration',
        *(['capture_summary'] if 'capture_summary' in config else []))}
    capture_folder = Path(config['capture_audit']).resolve().parent
    if report in reserved or report in sources or report == capture_folder or capture_folder in report.parents:
        raise ValueError('readout report cannot alias reserved output or capture source paths')
    if out in sources or any(out in path.parents for path in sources):
        raise ValueError('readout output directory cannot contain source metadata')
    return fixed


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def immutable(path, payload):
    """Publish complete bytes exclusively; interrupted staging never creates a result."""
    import tempfile
    path = _safe(path)
    if path.is_symlink(): raise ValueError('readout output files must not be symbolic links')
    if path.exists():
        _published_immutable(path, payload)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary, created = None, False
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.'+path.name+'.', suffix='.pending', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
            created = True
        except FileExistsError:
            if path.is_symlink(): raise ValueError('readout output files must not be symbolic links')
            _published_immutable(path, payload)
    finally:
        if temporary is not None and temporary.exists(): temporary.unlink()
    if created:
        try:
            from .experiment_log import note_artifact
            note_artifact(path.resolve())
        except Exception as exc:
            import sys
            print(f'Experiment metadata logging deferred: {type(exc).__name__}: {exc}', file=sys.stderr)


def _npz(path, arrays):
    from .confidence import _atomic
    stream = io.BytesIO(); np.savez(stream, **arrays); _atomic(path, stream.getvalue())


def fit_complete_columns(x, y, mask, train, weights, case_ids, donor_indices):
    """One factorization for independent real/shuffled columns sharing row masks."""
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    mask = np.asarray(mask); train = np.asarray(train); donor = np.asarray(donor_indices)
    n = len(x)
    if (x.ndim != 2 or y.ndim != 2 or len(y) != n or mask.shape != y.shape or mask.dtype != np.bool_
            or train.shape != (n,) or train.dtype != np.bool_ or donor.shape != (n,)
            or donor.dtype.kind not in 'iu' or set(donor.tolist()) != set(range(n))
            or not np.array_equal(train[donor], train) or not np.isfinite(x).all()
            or not np.isfinite(y[mask]).all() or len(case_ids) != n or len(set(case_ids)) != n):
        raise ValueError('complete finite discovery features/targets, IDs and split-preserving donor permutation required')
    active = np.flatnonzero(mask.all(axis=0))
    if not len(active) or np.any(mask.any(axis=0) != mask.all(axis=0)):
        raise ValueError('fixed fitted sites require complete or entirely undefined target columns')
    if train.sum() < 2: raise ValueError('training-only complete rows required')
    training_targets = np.concatenate((y[train][:, active], y[donor[train]][:, active]), axis=1)
    model = ridge_fit(x[train], training_targets, weights,
        train_ids=[case_ids[index] for index in np.flatnonzero(train)], split='train', alpha=100.)
    output = model.predict(x); width = len(active)
    real = np.full(y.shape, np.nan); shuffled = np.full(y.shape, np.nan)
    real[:, active], shuffled[:, active] = output[:, :width], output[:, width:]
    return model, active, real, shuffled


def family_macro_balanced_accuracy(correctness, truth, families):
    """Fixed-cell/family macro with class denominators recomputed on given rows."""
    correct = np.asarray(correctness, dtype=float); truth = np.asarray(truth)
    if (correct.ndim != 2 or truth.shape != correct.shape or len(families) != correct.shape[1]
            or not np.isfinite(correct).all() or np.any(correct < 0) or np.any(correct > 1)
            or not np.isin(truth, [0, 1]).all() or set(families) != set(FAMILIES)):
        raise ValueError('complete correctness/boolean truth for all four fixed relation families required')
    cells = []
    for column in range(correct.shape[1]):
        yes = truth[:, column] == 1; no = ~yes
        if not yes.any() or not no.any(): return None
        cells.append(.5*(float(correct[yes, column].mean())+float(correct[no, column].mean())))
    means = {family: float(np.mean([value for value, name in zip(cells, families) if name == family])) for family in FAMILIES}
    return dict(score=float(np.mean(list(means.values()))), families=means, cells=cells)


def algebraic_bootstrap(truth, method_correctness, groups, families):
    """Same nine-component draws/invalid-class rule for every original-label method."""
    truth = np.asarray(truth); groups = np.asarray(groups)
    if truth.ndim != 2 or groups.shape != (len(truth),) or len(set(groups.tolist())) != 9:
        raise ValueError('nine complete development components required')
    names = sorted(set(groups.tolist())); indices = [np.flatnonzero(groups == name) for name in names]
    methods = {name: np.asarray(value, dtype=float) for name, value in method_correctness.items()}
    points = {name: family_macro_balanced_accuracy(value, truth, families) for name, value in methods.items()}
    if any(value is None for value in points.values()):
        return dict(status='unqualified_primary_missing_development_class', methods=points,
            valid_draws=0, invalid_draws=BOOTSTRAP['draws'], comparisons={})
    rng = np.random.default_rng(BOOTSTRAP['seed']); differences = {name: [] for name in methods if name != 'direct'}
    invalid = 0
    for draw in rng.integers(0, 9, size=(BOOTSTRAP['draws'], 9)):
        chosen = np.concatenate([indices[index] for index in draw])
        scored = {name: family_macro_balanced_accuracy(value[chosen], truth[chosen], families) for name, value in methods.items()}
        if any(value is None for value in scored.values()): invalid += 1; continue
        for name in differences: differences[name].append(scored['direct']['score']-scored[name]['score'])
    valid = BOOTSTRAP['draws']-invalid; qualified = valid >= BOOTSTRAP['minimum_valid_draws']
    comparisons = {}
    for name, values in differences.items():
        comparisons['direct_minus_'+name] = dict(mean=points['direct']['score']-points[name]['score'],
            conditional_group_bootstrap_95=np.quantile(values, [.025, .975]).tolist() if qualified else None)
    return dict(status='qualified_conditional_interval' if qualified else 'unqualified_insufficient_valid_draws',
        methods=points, comparisons=comparisons, valid_draws=valid, invalid_draws=invalid,
        bootstrap=BOOTSTRAP, eligible_cells_fixed=True, same_invalid_draws_for_all_methods=True,
        seed_aggregation='Mean row correctness over three fixed fits before whole-group resampling; class denominators recomputed in every draw.',
        refits_per_draw=0, multiplicity_adjusted=False, groups=names)


def structural_bootstrap(method_correctness, groups):
    groups = np.asarray(groups); names = sorted(set(groups.tolist()))
    if len(names) != 9: raise ValueError('nine development components required for structural contrast')
    methods = {name: np.asarray(value, dtype=float) for name, value in method_correctness.items()}
    if any(value.shape != groups.shape or not np.isfinite(value).all() or np.any(value < 0) or np.any(value > 1) for value in methods.values()):
        raise ValueError('one finite whole-parent-graph correctness value per development row required')
    group_means = {name: np.array([value[groups == group].mean() for group in names]) for name, value in methods.items()}
    draws = np.random.default_rng(BOOTSTRAP['seed']).integers(0, 9, size=(BOOTSTRAP['draws'], 9))
    return dict(metric='whole_parent_graph_accuracy', methods={name: float(value.mean()) for name, value in group_means.items()},
        comparisons={'direct_minus_'+name: dict(mean=float((group_means['direct']-value).mean()),
            conditional_group_bootstrap_95=np.quantile((group_means['direct']-value)[draws].mean(axis=1), [.025, .975]).tolist())
            for name, value in group_means.items() if name != 'direct'},
        bootstrap=BOOTSTRAP, groups=names, refits_per_draw=0, multiplicity_adjusted=False,
        seed_aggregation='Mean row correctness over three fixed fits before nine whole-group draws.')


def _capture_metadata(config):
    from . import relationship_capture as capture
    _config(config)
    cap = _json(config['capture_config'], config['capture_config_sha256'])
    capture._config(cap)
    folder = Path(cap['run_dir'])
    out = Path(config['run_dir']).resolve(); report = Path(config['report']).resolve()
    sources = [config['capture_config'], config['capture_audit'], config['capture_registration'], cap['dataset']]
    if out == folder.resolve() or folder.resolve() in out.parents or out in folder.resolve().parents:
        raise ValueError('readout output directory must not overlap the capture source')
    if (report in {Path(path).resolve() for path in sources} or report == folder.resolve()
            or folder.resolve() in report.parents):
        raise ValueError('readout report cannot replace source artifacts')
    if any(out == Path(path).resolve() or out in Path(path).resolve().parents for path in sources):
        raise ValueError('readout output directory cannot contain source artifacts')
    for key, filename in [('capture_audit', 'audit.json'), ('capture_registration', 'registration.json')]:
        if Path(config[key]).resolve() != (folder/filename).resolve():
            raise ValueError('fixed capture metadata path differs')
    registration = _json(config['capture_registration'], config['capture_registration_sha256'])
    checked_audit = _json(config['capture_audit'], config['capture_audit_sha256'])
    if (registration.get('evaluation_role') != capture.ROLE or registration.get('config') != cap
            or registration.get('config_hash') != digest(cap)
            or checked_audit.get('status') != 'passed' or checked_audit.get('config_hash') != digest(cap)):
        raise ValueError('complete matching discovery capture registration/audit required')
    checked = capture.completed_metadata(cap)  # No np.load; source/IDs/pins first.
    if checked['audit'] != checked_audit or checked['source'] != registration['source']:
        raise ValueError('capture metadata changed after checksum verification')
    if 'capture_summary' in config:
        if Path(config['capture_summary']).resolve() != (folder/'summary.json').resolve():
            raise ValueError('fixed capture summary path differs')
        if _json(config['capture_summary'], config['capture_summary_sha256']) != checked['summary']:
            raise ValueError('pinned capture summary differs')
    cases = checked['cases']; records = [case['record'] for case in cases]
    if (checked['layers'] != list(LAYERS) or checked['sites'] != list(capture.SITES)
            or checked['feature_shape'] != [1944, 9, 4, 4096] or len(cases) != 1944
            or len({row['id'] for row in records}) != 1944
            or Counter(row['split'] for row in records) != {'train': 1296, 'development': 648}
            or any(row['condition'] != 'neutral' for row in records)
            or any(len(case['visible_prefixes']) != 9 for case in cases)):
        raise ValueError('fixed neutral discovery capture geometry/coverage differs')
    group_splits = {}
    for row in records:
        group = row['template_id']
        if group in group_splits and group_splits[group] != row['split']:
            raise ValueError('capture structural groups cross fitting/evaluation splits')
        group_splits[group] = row['split']
    if Counter(group_splits.values()) != {'train': 18, 'development': 9}:
        raise ValueError('18 training and nine development components required')
    return checked, records


def _targets(records):
    from . import relationship_targets as target
    bundles = {site: target.targets(records, site) for site in FIT_SITES}
    train = np.array([row['split'] == 'train' and row['condition'] == 'neutral' for row in records])
    support = {}
    for site, bundle in bundles.items():
        if tuple(bundle.case_ids) != tuple(row['id'] for row in records):
            raise ValueError('target/capture ordered case IDs differ')
        support[site] = target.training_support(target.subset(bundle, np.flatnonzero(train)), min_class_groups=12)
    eligible = tuple(target.fixed_primary_boolean_indices(bundles[3]))
    if set(support[3]['eligible_boolean_indices']) != set(eligible) or len(eligible) != 18:
        raise ValueError('TRAIN-only source support differs from the fixed 18 primary boolean tasks')
    return bundles, support, eligible, train


def preflight(config):
    checked, records = _capture_metadata(config)
    bundles, support, eligible, train = _targets(records)
    return dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), fixed_recipe=protocol(),
        capture_source=checked['source'], capture_dataset_sha256=checked['dataset_sha256'],
        capture_model=checked['model'], capture_model_revision=checked['model_revision'],
        cases=len(records), training_rows=int(train.sum()), development_rows=int((~train).sum()),
        primary_algebraic_columns=[bundles[3].columns[index] for index in eligible],
        primary_training_support=support[3], activation_arrays_loaded=False,
        learned_readouts_fitted=False, new_model_queries=0, generated_holdouts_opened=False, limitation=LIMITATION)


def _load(checked):
    from . import relationship_capture as capture
    cases = checked['cases']; chunks = []
    first = 0
    for entry in checked['chunks']:
        if entry['first'] != first: raise ValueError('contiguous captured feature chunks required')
        part = cases[first:first+entry['rows']]
        features, _ = capture.load_chunk(entry, part)
        chunks.append(features); first += len(part)
    result = np.concatenate(chunks, axis=0)
    if result.shape != (1944, 9, 4, 4096) or not np.isfinite(result).all():
        raise ValueError('fixed finite feature bank required')
    return result


def _scheduled_frozen():
    from . import registry
    if not os.environ.get('SLURM_JOB_ID') or not (registry.ROOT/'frozen_manifest.json').is_file():
        raise RuntimeError('real relationship fits require an sbatch worker and immutable frozen source')
    return registry.ROOT


def _prior(bundle, train, weights):
    active = np.flatnonzero(bundle.mask.all(axis=0)); scores = np.full(bundle.y.shape, np.nan)
    scores[:, active] = np.average(bundle.y[train][:, active], axis=0, weights=weights)
    return scores


def _name(backend, layer, site, seed):
    return f'{backend}_layer{layer}_site{site}_seed{seed}'


def _artifact(path):
    return dict(path=str(path), sha256=_sha(path), bytes=Path(path).stat().st_size)


def _fit_bank(path, x, bundle, train, weights, donor, config_hash):
    active = np.flatnonzero(bundle.mask.all(axis=0))
    if path.exists():
        with np.load(_safe(path), allow_pickle=False) as data:
            if (str(data['config_hash'].item()) != config_hash or tuple(data['case_ids'].tolist()) != bundle.case_ids
                    or not np.array_equal(data['targets'], bundle.y, equal_nan=True)
                    or not np.array_equal(data['target_mask'], bundle.mask)
                    or not np.array_equal(data['donor_indices'], donor)
                    or not np.array_equal(data['donor_case_ids'], np.array(bundle.case_ids)[donor])
                    or not np.array_equal(data['training_weights'], weights)
                    or not np.array_equal(data['active_columns'], active)):
                raise ValueError('existing immutable relationship fit input identity differs')
            metadata = json.loads(data['model_metadata'].tobytes())
            parameters = {key: data[key] for key in ('mean', 'scale', 'coef', 'intercept', 'weighted_feature_mean', 'weighted_target_mean')}
            model = from_parameters(metadata, parameters)
            training_targets = np.concatenate((bundle.y[train][:, active], bundle.y[donor[train]][:, active]), axis=1)
            expected_inputs = {name: _ridge_array_hash(value) for name, value in
                [('features', x[train]), ('targets', training_targets), ('sample_weight', weights)]}
            if (model.train_ids != tuple(bundle.case_ids[index] for index in np.flatnonzero(train))
                    or metadata['training_input_sha256'] != expected_inputs):
                raise ValueError('existing immutable relationship fit training input identity differs')
            real, shuffled = data['real_scores'].copy(), data['shuffled_scores'].copy()
    else:
        model, active, real, shuffled = fit_complete_columns(x, bundle.y, bundle.mask, train, weights, bundle.case_ids, donor)
        arrays = {**model.parameters, 'model_metadata': np.frombuffer(_json_bytes(model.metadata), dtype=np.uint8),
            'config_hash': np.array(config_hash), 'case_ids': np.array(bundle.case_ids),
            'targets': bundle.y, 'target_mask': bundle.mask, 'active_columns': active,
            'donor_indices': donor, 'donor_case_ids': np.array(bundle.case_ids)[donor],
            'training_weights': weights, 'real_scores': real, 'shuffled_scores': shuffled}
        _npz(path, arrays)
        with np.load(_safe(path), allow_pickle=False) as data:
            model = from_parameters(json.loads(data['model_metadata'].tobytes()), {key: data[key] for key in model.parameters})
            if not np.array_equal(data['real_scores'], real, equal_nan=True) or not np.array_equal(data['shuffled_scores'], shuffled, equal_nan=True):
                raise ValueError('saved relationship score arrays differ')
    replay = model.predict(x); width = len(active)
    if (not np.array_equal(replay[:, :width], real[:, active]) or not np.array_equal(replay[:, width:], shuffled[:, active])):
        raise ValueError('saved relationship parameters fail exact full-row prediction replay')
    return model, active, real, shuffled


def run(config):
    from . import relationship_targets as target
    from .confidence import _run_lock
    from sklearn.feature_extraction.text import HashingVectorizer
    from threadpoolctl import threadpool_limits
    fit_root = _scheduled_frozen(); checked, records = _capture_metadata(config)
    bundles, support, eligible, train = _targets(records)
    out = _safe(config['run_dir']); out.mkdir(parents=True, exist_ok=True)
    source = code_identity(); ids = tuple(row['id'] for row in records)
    train_rows = [row for row, keep in zip(records, train) if keep]
    groups = np.array([row['template_id'] for row in records]); development = np.flatnonzero(~train)
    donor_maps = {seed: target.coherent_shuffle(records, seed) for seed in SEEDS}
    with _run_lock(out):
        if (out/COMPLETION_NAME).exists():
            previous = completed_result(config)
            if previous['analysis_source'] != source: raise ValueError('completed fits use another frozen source; choose a new run directory')
            return previous
        registration = dict(evaluation_role=ROLE, config=config, config_hash=digest(config), analysis_source=source,
            fit_source=dict(snapshot=str(fit_root), source_sha256=source['source_sha256'], frozen_manifest_sha256=_sha(fit_root/'frozen_manifest.json')),
            capture_source=checked['source'], capture_dataset_sha256=checked['dataset_sha256'], fixed_recipe=protocol(),
            primary_algebraic_columns=[bundles[3].columns[index] for index in eligible], primary_training_support=support[3],
            new_model_queries=0, generated_holdouts_opened=False, limitation=LIMITATION)
        immutable(out/'registration.json', _json_bytes(registration))
        vectors = _load(checked); fits = []; artifacts = {}; comparisons = {}; replay_rows = 0
        threads = int(os.environ.get('SLURM_CPUS_PER_TASK', '8'))
        if threads < 1: raise ValueError('positive scheduler CPU allocation required')
        started = time.monotonic()
        with threadpool_limits(limits=threads):
            for site in FIT_SITES:
                bundle = bundles[site]; fixed_indices = target.fixed_primary_boolean_indices(bundle)
                dev_bundle = target.subset(bundle, development)
                control_bundles = {seed: target.permute_bundle(bundle, donor_maps[seed]) for seed in SEEDS}
                control_support = {seed: target.training_support(target.subset(control_bundles[seed], np.flatnonzero(train)),
                    min_class_groups=12) for seed in SEEDS}
                prior_metrics = {}
                surface = HashingVectorizer(analyzer='char', ngram_range=(3, 8), n_features=4096,
                    alternate_sign=True, norm=None, dtype=np.float64).transform([case['visible_prefixes'][site] for case in checked['cases']]).toarray()
                candidates = [('hidden', layer, vectors[:, site, index]) for index, layer in enumerate(LAYERS)]+[('surface', -1, surface)]
                for backend, layer, x in candidates:
                    for seed in SEEDS:
                        weights = group_weights(train_rows, seed).astype(np.float64); donor = donor_maps[seed]
                        shuffled_bundle = control_bundles[seed]
                        name = _name(backend, layer, site, seed); path = out/(name+'.npz')
                        model, active, scores, shuffled_scores = _fit_bank(path, x, bundle, train, weights, donor, digest(config))
                        replay_rows += len(records); artifacts[name] = _artifact(path)
                        categorical = target.derived_categorical_relations(bundle, scores)
                        scalar = target.derived_relations(bundle, scores); prior = _prior(bundle, train, weights)
                        method_scores = dict(direct=scores, categorical_value_derived=categorical,
                            scalar_value_derived=scalar, structural_position_prior=prior)
                        method_metrics = {}
                        for split, indices in [('train', np.flatnonzero(train)), ('development', development)]:
                            subset = target.subset(bundle, indices)
                            method_metrics[split] = {}
                            for method, values in method_scores.items():
                                cache_key = seed, split
                                if method == 'structural_position_prior' and cache_key in prior_metrics:
                                    measured = prior_metrics[cache_key]
                                else:
                                    measured = target.metrics(subset, values[indices], eligible_boolean_indices=fixed_indices,
                                        training_support_info=support[site], include_per_group=False)
                                    if method == 'structural_position_prior': prior_metrics[cache_key] = measured
                                method_metrics[split][method] = measured
                            control = target.subset(shuffled_bundle, indices)
                            method_metrics[split]['coherent_shuffle_task'] = target.metrics(control, shuffled_scores[indices],
                                eligible_boolean_indices=fixed_indices, training_support_info=control_support[seed], include_per_group=False)
                        metadata = model.metadata; metadata.pop('training_ids')
                        weighted_real = np.average(bundle.y[train][:, active], axis=0, weights=weights)
                        weighted_control = np.average(shuffled_bundle.y[train][:, active], axis=0, weights=weights)
                        fits.append(dict(name=name, artifact=str(path), backend=backend, layer=layer, site=site, seed=seed,
                            model=metadata, active_columns=active.tolist(), masked_columns=len(bundle.columns)-len(active),
                            real_and_shuffle_outputs_independent=True, factorization_count=1,
                            donor_case_ids_sha256=digest(list(shuffled_bundle.label_case_ids)),
                            unweighted_training_target_histograms_preserved=bool(np.array_equal(
                                np.sort(bundle.y[train][:, active], axis=0), np.sort(shuffled_bundle.y[train][:, active], axis=0))),
                            unweighted_development_target_histograms_preserved=bool(np.array_equal(
                                np.sort(bundle.y[development][:, active], axis=0), np.sort(shuffled_bundle.y[development][:, active], axis=0))),
                            weighted_training_target_mean_max_abs_difference=float(np.max(abs(weighted_real-weighted_control))),
                            metrics=method_metrics))
                        if layer == 24 or backend == 'surface':
                            for method, values in method_scores.items():
                                correctness = target.task_correctness(dev_bundle, values[development], fixed_indices)
                                key = (site, 'surface' if backend == 'surface' else method)
                                # Each surface method is redundant; retain ONLY
                                # its directly fitted score for the comparisons.
                                if backend == 'surface' and method != 'direct': continue
                                comparisons.setdefault(key, []).append(correctness)
                        write_json(out/'progress.json', {'status': 'started', 'fits': len(fits), 'planned_fits': 45,
                            'generated_holdouts_opened': False})
                        print(f'relationship readout {name}', flush=True)
        def means(site, task):
            methods = {}
            for name in ('direct', 'categorical_value_derived', 'scalar_value_derived', 'structural_position_prior', 'surface'):
                values = comparisons[site, name]
                if len(values) != 3: raise ValueError('all three fixed fits required before primary comparison')
                methods[name] = np.mean([value[task] for value in values], axis=0)
            return methods
        reference = comparisons[3, 'direct'][0]
        algebraic = algebraic_bootstrap(reference['algebraic_truth'], means(3, 'algebraic_correct'),
            groups[development], reference['algebraic_families'])
        structural_methods = means(7, 'whole_graph_correct')
        structural_methods = {name: structural_methods[name] for name in ('direct', 'structural_position_prior', 'surface')}
        structural = structural_bootstrap(structural_methods, groups[development])
        result = dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=digest(config), analysis_source=source,
            fit_source=registration['fit_source'], capture_source=checked['source'], dataset_sha256=checked['dataset_sha256'],
            cases=len(records), training_rows=int(train.sum()), development_rows=len(development),
            training_groups=18, development_groups=9, fitted_sites=list(FIT_SITES), captured_sites=list(range(9)),
            factorizations=len(fits), fitted_real_and_shuffle_columns=sum(2*len(fit['active_columns']) for fit in fits),
            parameter_replay_rows=replay_rows, target_columns=list(bundles[3].columns),
            training_support={str(site): value for site, value in support.items()},
            target_descriptive_metadata={str(site): bundle.descriptive for site, bundle in bundles.items()},
            scalar_parameters_per_output=4097, primary_algebraic_direct_outputs=18,
            categorical_value_outputs=128, scalar_value_outputs=4, whole_pipeline_parameter_counts_matched=False,
            metrics_include_per_group_cells=False, group_uncertainty='Exact saved per-row correctness; nine-component conditional bootstrap.',
            primary=dict(definition=PRIMARY, algebraic=algebraic, structural=structural), fits=fits,
            runtime={'threads': threads, 'slurm_job_id': os.environ.get('SLURM_JOB_ID'), 'wall_seconds': time.monotonic()-started},
            source_model_prefill_cases=checked['summary']['model_prefill_cases'], source_generated_responses=0,
            new_model_queries=0, behavioral_response_features=False, oracle_target_features=False,
            generated_holdouts_opened=False, mechanism_C_fitted=False, limitation=LIMITATION)
        if len(fits) != 45 or replay_rows != 45*1944: raise ValueError('complete fixed 45-fit grid and exact replays required')
        return _finish(config, result, artifacts)


def _runtime(value):
    if (not isinstance(value, dict) or set(value) != {'threads', 'slurm_job_id', 'wall_seconds'}
            or type(value['threads']) is not int or value['threads'] < 1
            or not isinstance(value['slurm_job_id'], str) or not value['slurm_job_id']
            or isinstance(value['wall_seconds'], bool) or not isinstance(value['wall_seconds'], (int, float))
            or not np.isfinite(value['wall_seconds']) or value['wall_seconds'] < 0):
        raise ValueError('complete finite original relationship runtime provenance required')
    return value


def _finish(config, result, artifacts):
    """Commit after every bank replay; recover only identical scientific results."""
    out = Path(config['run_dir']); path = out/'results_v1.json'
    completion_runtime = _runtime(result.get('runtime'))
    payload = _json_bytes(result)
    if len(payload) > MAX_RESULT_BYTES: raise ValueError('rich relationship result exceeds separate result byte bound')
    if path.exists():
        _safe(path)
        if path.stat().st_size > MAX_RESULT_BYTES: raise ValueError('bounded existing scientific result required')
        with path.open('rb') as stream: previous_payload = stream.read(MAX_RESULT_BYTES+1)
        if len(previous_payload) > MAX_RESULT_BYTES: raise ValueError('bounded existing scientific result required')
        previous = json.loads(previous_payload)
        if not isinstance(previous, dict): raise ValueError('existing scientific result object required')
        _runtime(previous.get('runtime'))
        scientific = {key: value for key, value in result.items() if key != 'runtime'}
        saved_scientific = {key: value for key, value in previous.items() if key != 'runtime'}
        if _json_bytes(scientific) != _json_bytes(saved_scientific):
            raise ValueError('existing immutable relationship scientific result differs after exact bank replay')
        result = previous
    else:
        immutable(path, payload)
    immutable(config['report'], _report(result).encode())
    audit_result = dict(status='passed', evaluation_role=ROLE, config_hash=digest(config),
        factorizations=45, parameter_replay_rows=result['parameter_replay_rows'], exact_parameter_score_replays=True,
        capture_source=result['capture_source'], new_model_queries=0, generated_holdouts_opened=False,
        result_runtime_scope='Original scientific result construction only; later cached-bank replays and completion workers are not included.')
    immutable(out/'audit.json', _json_bytes(audit_result))
    artifacts = {**artifacts, 'registration': _artifact(out/'registration.json'), 'results': _artifact(path),
        'report': _artifact(config['report']), 'audit': _artifact(out/'audit.json')}
    receipt = dict(status='complete_exploratory', evaluation_role=ROLE, schema_version=1, config_hash=digest(config),
        fit_source=result['fit_source'], capture_source=result['capture_source'], factorizations=45,
        parameter_replay_rows=result['parameter_replay_rows'], artifacts=artifacts, primary=result['primary'],
        generated_holdouts_opened=False, new_model_queries=0, mechanism_C_fitted=False,
        completion_runtime=completion_runtime,
        completion_runtime_scope='Current worker through exact bank replay and scientific result construction; excludes later immutable publication.')
    immutable(out/COMPLETION_NAME, _json_bytes(receipt))
    return result


def _report(result):
    primary = result['primary']
    lines = ['# Structural and algebraic relationship discovery readouts', '', LIMITATION, '',
        f"{result['cases']:,} source cases: {result['training_rows']:,} training rows in 18 components; {result['development_rows']} development rows in nine components. Fitted sites are 3, 7 and 8; other captured sites are not fitted.", '',
        f"{result['factorizations']} shared weighted-ridge factorizations; {result['parameter_replay_rows']:,} exact saved-parameter row replays. Real and coherent-shuffle target columns are independent right-hand sides. Four 32-way categorical value heads are the primary value-derived comparator; scalar-value rounding is secondary.", '',
        'The direct primary algebraic task has 18 scalar outputs; the categorical value pipeline has 128 outputs. Both use the same feature bank, training normalization and per-column ridge objective, with different total parameter counts.', '',
        '## Fixed primary algebraic comparison', '',
        f"Interval status: {primary['algebraic']['status']}.", '',
        '| Method | Four-family macro balanced accuracy |', '|---|---:|']
    for name, value in primary['algebraic']['methods'].items():
        lines.append(f"| {name} | {value['score']:.6f} |" if value is not None else f'| {name} | undefined: missing fixed class |')
    lines += ['', '| Contrast | Increment | Conditional group 95% |', '|---|---:|---|']
    for name, value in primary['algebraic']['comparisons'].items():
        lines.append(f"| {name} | {value['mean']:+.6f} | {value['conditional_group_bootstrap_95']} |")
    lines += ['', '## Fixed primary structural comparison', '',
        'Four three-way parent heads reconstruct the whole eight-definition graph under a known fixed roots/version scaffold. This is compositional parent recovery, not learned node/version discovery.', '',
        '| Method | Whole-parent-graph accuracy |', '|---|---:|']
    for name, value in primary['structural']['methods'].items(): lines.append(f'| {name} | {value:.6f} |')
    lines += ['', '| Contrast | Increment | Conditional group 95% |', '|---|---:|---|']
    for name, value in primary['structural']['comparisons'].items():
        lines.append(f"| {name} | {value['mean']:+.6f} | {value['conditional_group_bootstrap_95']} |")
    lines += ['', 'All fitted layers, sites, weighting seeds, pooled per-cell metrics, class-support and constant/undefined-cell descriptions remain in results_v1.json. Component-level primary uncertainty is computed from saved row correctness; full per-cell/per-group AP tables are not duplicated.', '',
        'Coherent shuffle heads are trained and evaluated against separately shuffled TRAIN/DEV targets. Component derangements move initialization-prefix base blocks, then permute copy-parent variants within each base, keeping lexical relatives tied. One donor mapping applies across every target and site. Unweighted marginals are preserved; reported weighted-marginal differences are retained. Shuffle metrics describe the control task and are not averaged into the original-label primary contrast.', '',
        f"Fitting performs zero additional model queries. The source capture separately records {result['source_model_prefill_cases']:,} case prefills and zero generated responses.", '']
    return '\n'.join(lines)


def _expected_artifacts(config):
    out = Path(config['run_dir'])
    expected = {_name(backend, layer, site, seed): out/(_name(backend, layer, site, seed)+'.npz')
        for site in FIT_SITES for backend, layer in [('hidden', value) for value in LAYERS]+[('surface', -1)] for seed in SEEDS}
    expected.update(registration=out/'registration.json', results=out/'results_v1.json', report=Path(config['report']), audit=out/'audit.json')
    return expected


def completed_result(config):
    """Verify bounded completion/source identity before any rich result payload."""
    from .snapshots import verify
    checked, _ = _capture_metadata(config)
    out = Path(config['run_dir']); receipt = _json(out/COMPLETION_NAME)
    if (receipt.get('schema_version') != 1 or receipt.get('status') != 'complete_exploratory'
            or receipt.get('evaluation_role') != ROLE or receipt.get('config_hash') != digest(config)
            or receipt.get('capture_source') != checked['source'] or receipt.get('factorizations') != 45
            or receipt.get('parameter_replay_rows') != 45*1944
            or receipt.get('new_model_queries') != 0 or receipt.get('generated_holdouts_opened') is not False
            or receipt.get('mechanism_C_fitted') is not False):
        raise ValueError('complete matching discovery readout receipt required')
    source = receipt.get('fit_source', {}); snapshot = _safe(source.get('snapshot', ''))
    _discovery_response_path(snapshot)
    if _sha(snapshot/'frozen_manifest.json') != source.get('frozen_manifest_sha256'):
        raise ValueError('original immutable readout source manifest changed')
    verified = verify(snapshot)
    if verified['code']['source_sha256'] != source.get('source_sha256'):
        raise ValueError('original readout source identity differs')
    expected = _expected_artifacts(config); artifacts = receipt.get('artifacts')
    if not isinstance(artifacts, dict) or set(artifacts) != set(expected):
        raise ValueError('exact fixed readout artifact inventory required')
    for name, path in expected.items():
        binding = artifacts[name]; _discovery_response_path(path); _safe(path)
        if (not isinstance(binding, dict) or set(binding) != {'path', 'sha256', 'bytes'}
                or _safe(binding['path']).resolve() != path.resolve()
                or not isinstance(binding['sha256'], str) or len(binding['sha256']) != 64
                or type(binding['bytes']) is not int or binding['bytes'] < 1):
            raise ValueError('readout artifact path/hash/size inventory differs')
    registration = _json(expected['registration'], artifacts['registration']['sha256'])
    if (registration.get('evaluation_role') != ROLE or registration.get('config') != config
            or registration.get('config_hash') != digest(config) or registration.get('analysis_source') != verified['code']
            or registration.get('fit_source') != source or registration.get('fixed_recipe') != protocol()):
        raise ValueError('original fit registration/source/protocol differs before result access')
    for entry in checked['chunks']:
        if _sha(entry['path']) != entry['sha256']: raise ValueError('original capture feature chunk changed')
    for name, path in expected.items():
        if path.stat().st_size != artifacts[name]['bytes'] or _sha(path) != artifacts[name]['sha256']:
            raise ValueError('immutable relationship readout artifact changed: '+name)
    path = expected['results']
    if path.stat().st_size > MAX_RESULT_BYTES: raise ValueError('bounded separate scientific result required')
    with path.open('rb') as stream: payload = stream.read(MAX_RESULT_BYTES+1)
    import hashlib
    if len(payload) > MAX_RESULT_BYTES or hashlib.sha256(payload).hexdigest() != artifacts['results']['sha256']:
        raise ValueError('scientific result bytes changed before parsing')
    result = json.loads(payload); _discovery_declaration(result)
    expected_fits = {name: str(path) for name, path in expected.items() if path.suffix == '.npz'}
    if (not isinstance(result, dict) or result.get('status') != 'complete_exploratory'
            or result.get('evaluation_role') != ROLE or result.get('config_hash') != digest(config)
            or result.get('analysis_source') != verified['code'] or result.get('fit_source') != source
            or result.get('factorizations') != 45 or result.get('parameter_replay_rows') != 45*1944
            or result.get('primary') != receipt.get('primary') or len(result.get('fits', [])) != 45
            or {fit['name']: fit['artifact'] for fit in result['fits']} != expected_fits
            or result.get('new_model_queries') != 0 or result.get('generated_holdouts_opened') is not False):
        raise ValueError('complete fixed scientific result differs from its compact receipt')
    return result


def audit(config):
    """Read-only source/artifact audit; exact model-score replays ran at fitting."""
    result = completed_result(config)
    saved = _json(Path(config['run_dir'])/'audit.json')
    if (saved.get('status') != 'passed' or saved.get('evaluation_role') != ROLE
            or saved.get('config_hash') != digest(config) or saved.get('factorizations') != result['factorizations']
            or saved.get('parameter_replay_rows') != result['parameter_replay_rows']
            or saved.get('exact_parameter_score_replays') is not True):
        raise ValueError('completed parameter-replay audit differs')
    return dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), factorizations=45,
        parameter_replay_rows=result['parameter_replay_rows'], source_artifact_hashes_verified=True,
        exact_parameter_replays_verified_during_fit=True, additional_fits=0, new_model_queries=0,
        generated_holdouts_opened=False)
