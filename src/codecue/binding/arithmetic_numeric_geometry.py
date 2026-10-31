"""Controlled output-geometry tests, sharing the validated numeric fit engine."""
from functools import lru_cache
import importlib.util
from pathlib import Path

import numpy as np

from . import arithmetic_numeric_exploration as original
from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_local_capture as capture
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from .datasets import digest

FIT = 'discovery_numeric_geometry_fit_v1'
QUERY_CACHE = 'discovery_full_query_cache_v1'
REPORT = 'discovery_numeric_geometry_report_v1'
VALUES = np.arange(-96, 97, dtype=np.int64)
VALUES.setflags(write=False)
HEADS = (('decimal_circle', 7), ('decimal_permuted', 7),
         ('crt_circle', 4), ('crt_permuted', 4), ('ordinal', 192))
FORMATS = tuple(k for k, _ in HEADS)
WIDTH = sum(d for _, d in HEADS)


def _circle(label, period, permuted, salt):
    if permuted:
        label = np.random.default_rng(salt).permutation(period)[label]
    angle = 2 * np.pi * label / period
    return np.stack((np.cos(angle), np.sin(angle)), axis=1)


@lru_cache(maxsize=None)
def template(name):
    if name in ('decimal_circle', 'decimal_permuted'):
        sign = np.eye(3)[np.sign(VALUES) + 1]
        absolute = np.abs(VALUES)
        changed = name.endswith('permuted')
        result = np.concatenate((sign, _circle(absolute % 10, 10, changed, 731),
            _circle(absolute // 10, 10, changed, 947)), axis=1)
    elif name in ('crt_circle', 'crt_permuted'):
        changed = name.endswith('permuted')
        result = np.concatenate((_circle(VALUES % 17, 17, changed, 12017),
            _circle(VALUES % 19, 19, changed, 12019)), axis=1)
    elif name == 'ordinal':
        result = (VALUES[:, None] > np.arange(-96, 96)[None, :]).astype(float)
    else:
        raise ValueError('predeclared numeric geometry required')
    result.setflags(write=False)
    return result


def targets(values):
    values = np.asarray(values)
    if values.ndim != 1 or not np.issubdtype(values.dtype, np.integer) or np.any((values < -96) | (values > 96)):
        raise ValueError('bounded integer labels required')
    return np.concatenate([template(name)[values + 96] for name in FORMATS], axis=1)


def predictions(scores):
    scores = np.asarray(scores)
    if scores.ndim != 2 or scores.shape[1] != WIDTH or not np.isfinite(scores).all():
        raise ValueError('finite declared geometry scores required')
    result, position = {}, 0
    for name, dimension in HEADS:
        code = template(name)
        projected = scores[:, position:position + dimension]
        # Equivalent to nearest squared distance, including nonconstant code
        # norms for the ordinal representation. Domain is fixed before data.
        similarities = 2 * projected @ code.T - np.square(code).sum(axis=1)
        result[name] = VALUES[np.argmax(similarities, axis=1)]
        position += dimension
    return result


def score_heads(scores, values, groups):
    guess = predictions(scores)
    _, inverse, counts = np.unique(groups, return_inverse=True, return_counts=True)
    if not len(counts): raise ValueError('nonempty evaluation families required')
    def mean(x):
        return float(np.mean(np.bincount(inverse, weights=np.asarray(x, float)) / counts))
    return {name: dict(exact=mean(value == values), mae=mean(np.abs(value - values))) for name, value in guess.items()}


# An isolated module namespace preserves all completed baseline mathematics.
# Only target geometry, decoding, selection score and method labels differ.
spec = importlib.util.spec_from_file_location(__package__ + '._numeric_geometry_fit_engine', original.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.FIT = FIT
_CORE.HEADS, _CORE.FORMATS, _CORE.HEAD_WIDTH = HEADS, FORMATS, WIDTH
_CORE.targets, _CORE.predictions, _CORE.score_heads = targets, predictions, score_heads
_CORE.selection_loss = lambda panel, name: -panel[name]['exact']
run = _CORE.run


def query_values(features, cases):
    if features.ndim != 4 or len(features) != len(cases):
        raise ValueError('native four-axis capture geometry required')
    points = np.asarray([case['point_count'] - 1 for case in cases])
    if any(not case['descriptors'] or len(case['descriptors']) != case['point_count'] or case['descriptors'][-1]['kind'] != 'answer' for case in cases) or np.any(points < 0) or np.any(points >= features.shape[1]):
        raise ValueError('actual answer point identities required')
    return features[np.arange(len(cases)), points]


def prepare_query(config):
    from .confidence import _run_lock
    source = common.validate_role(config, QUERY_CACHE)
    old, _, profile, rows, cases = audit.load_cache(config)
    folder = Path(config['run_dir']); folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        cap = base._json(old['capture_config'], old['capture_config_sha256'])
        receipt = base._json(Path(cap['run_dir']) / 'completion_manifest_v1.json')
        manifest = base._json(Path(cap['run_dir']) / 'summary.json', receipt['artifacts']['summary']['sha256'])
        if manifest['cases'] != len(cases) or [e['first'] for e in manifest['chunks']] != list(range(0, len(cases), cap['chunk_size'])):
            raise ValueError('complete ordered capture coverage required')
        path = folder / 'query_vectors.npy'; pending = folder / 'query_vectors.pending.npy'
        output = np.lib.format.open_memmap(pending, mode='w+', dtype=np.float32,
            shape=(len(cases), len(profile['layers']), profile['hidden_size']))
        for entry in manifest['chunks']:
            first, count = entry['first'], entry['rows']
            if count != min(cap['chunk_size'], len(cases) - first): raise ValueError('chunk rows differ')
            subset = cases[first:first + count]
            features = capture.load_chunk(entry, subset, profile)
            output[first:first + count] = query_values(features, subset)
            capture.legacy._CORE._journal(folder / 'progress.json', dict(captured_rows=first + count))
        if not np.isfinite(output).all(): raise ValueError('nonfinite global query features')
        output.flush(); pending.replace(path)
        artifact = dict(storage._pin(path), shape=list(output.shape))
        result = dict(status='complete_exploratory', evaluation_role=QUERY_CACHE, source=source,
            config_hash=digest(config), model=profile['model'], layers=profile['layers'], cases=len(rows),
            ordered_case_ids_sha256=digest([r['id'] for r in rows]), point='actual point_count-1 answer node',
            capture_manifest=storage._pin(Path(cap['run_dir']) / 'summary.json'), query_vectors=artifact,
            new_fits=0, new_model_queries=0, generated_holdouts_opened=False)
        return common.receipt(config, source, result, dict(query_vectors=artifact))


def paired_family_interval(first, second):
    """Average fitting seeds, then bootstrap independent families, not rows."""
    first, second = np.asarray(first), np.asarray(second)
    if first.shape != second.shape or first.ndim != 2 or first.shape[0] != 3 or not first.shape[1] or not np.isfinite(first - second).all():
        raise ValueError('aligned three-seed family panels required')
    delta = (first - second).mean(axis=0)
    indices = np.random.default_rng(20261031).integers(0, len(delta), (2000, len(delta)))
    lower, upper = np.quantile(delta[indices].mean(axis=1), [.025, .975])
    return dict(delta=float(delta.mean()), lower=float(lower), upper=float(upper), families=len(delta),
        bootstrap_replicates=2000, unit='structural family after averaging three fitting seeds')


def family_panels(worker, data, width):
    _, _, _, rows, cases = audit.load_cache(worker)
    table = [e for e in original.examples(rows, cases) if e['role'] == data['role']]
    expected_ids = np.asarray([e['case_id'] + ':definition:' + str(e['statement']) for e in table])
    groups = np.asarray([e['group'] for e in table])
    dev = np.asarray([e['split'] == 'development' for e in table])
    families = np.unique(groups[dev])
    result = {name: {} for name in FORMATS}
    for bank in data['fits']:
        if bank['width'] != width: continue
        with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as saved:
            if not np.array_equal(saved['ids'], expected_ids) or not np.array_equal(saved['truth'], [e['value'] for e in table]):
                raise ValueError('family comparison score identities differ')
            predictions_by_code = predictions(saved['real'][dev])
            truth = saved['truth'][dev]
        for name in bank['selected_formats']:
            if bank['seed'] in result[name]: raise ValueError('duplicate selected family panel')
            correct = predictions_by_code[name] == truth
            result[name][bank['seed']] = np.asarray([correct[groups[dev] == family].mean() for family in families])
    if any(sorted(panels) != [11, 29, 47] for panels in result.values()): raise ValueError('three selected family seeds required')
    return families.tolist(), {name: np.stack([panels[s] for s in (11, 29, 47)]) for name, panels in result.items()}


def report(config):
    source = common.validate_role(config, REPORT)
    if (Path(config['run_dir']) / 'completion_manifest_v1.json').exists(): return common.completed(config)
    inputs, family_data, contrasts = {}, [], []
    lines = ['# Numeric geometry: controlled discovery comparison', '',
        'Geometry-aware linear output maps on the same full-width definition features. '
        'Circular versus permuted-circle pairs match input access and output dimension. '
        'All alpha selection uses grouped TRAIN validation; existing DEV remains adaptive discovery.', '',
        '| Worker | Role | Width | Code geometry | DEV exact | MAE | Family-control exact | Encoded TRAIN prior exact | Parameters |',
        '|---|---|---:|---|---:|---:|---:|---:|---:|']
    for item in config['workers']:
        worker = base._json(item['path'], item['sha256']); common.completed(worker)
        entry = storage._pin(Path(worker['run_dir']) / 'results.json'); data = base._json(entry['path'], entry['sha256'])
        inputs[item['path']] = entry
        for width in data['widths']:
            families, panels = family_panels(worker, data, width)
            family_data.append(dict(worker=Path(item['path']).stem, backend=data['backend'], role=data['role'], width=width,
                families=families, panels=panels))
            for name in FORMATS:
                banks = [b for b in data['fits'] if b['width'] == width and name in b['selected_formats']]
                if sorted(b['seed'] for b in banks) != [11, 29, 47]: raise ValueError('complete selected seeds required')
                avg = lambda panel, metric: float(np.mean([b['development'][panel][name][metric] for b in banks]))
                lines.append(f"| {Path(item['path']).stem} | {data['role']} | {width} | {name} | {100*avg('real','exact'):.2f}% | "
                    f"{avg('real','mae'):.3f} | {100*avg('control','exact'):.2f}% | {100*avg('prior','exact'):.2f}% | {banks[0]['parameters_per_encoding'][name]} |")
    for item in family_data:
        for natural, permuted in [('decimal_circle', 'decimal_permuted'), ('crt_circle', 'crt_permuted')]:
            contrasts.append(dict(comparison=item['worker'] + ': ' + natural + ' minus ' + permuted,
                **paired_family_interval(item['panels'][natural], item['panels'][permuted])))
        if item['backend'] == 'hidden':
            source_panels = [e for e in family_data if e['backend'] == 'source' and e['role'] == item['role'] and e['width'] == item['width']]
            if len(source_panels) != 1 or source_panels[0]['families'] != item['families']: raise ValueError('unique aligned width/role source comparison required')
            for name in FORMATS:
                contrasts.append(dict(comparison=item['worker'] + ': ' + name + ' hidden minus source',
                    **paired_family_interval(item['panels'][name], source_panels[0]['panels'][name])))
    lines += ['', '## Paired structural-family contrasts', '',
        'Exact-accuracy differences in percentage points. Average fitting seeds within each family, then bootstrap families '
        '(2,000 replicates, fixed seed 20261031). These descriptive 95% percentile intervals are not simultaneous, '
        'do not include new-cohort uncertainty and do not correct adaptive DEV selection.', '',
        '| Comparison | Difference | 95% interval | Families |', '|---|---:|---:|---:|']
    for contrast in contrasts:
        lines.append(f"| {contrast['comparison']} | {100*contrast['delta']:.2f} | [{100*contrast['lower']:.2f}, {100*contrast['upper']:.2f}] | {contrast['families']} |")
    lines += ['', 'The geometric permutation controls preserve code dimension, candidate identities and circular radii while changing numerical adjacency. '
        'Coherent-family controls are a separate label-assignment test. Signed decimal and residue/template decoding are adaptations, not a direct replication of the positive-literal paper. '
        'Neither smooth-code performance nor a stronger nonlinear readout establishes native execution. Compare all planned panels, old categorical/one-hot-digit baselines and independent-family transfer before claiming a representational mechanism. '
        'The decoder enumerates the predeclared integer label domain; it receives no program operators or gold routing pointers. '
        'Probabilistic calibration/MDL and causal interventions are not measured by this fit.', '']
    path = Path(config['report']); base._publish(path, '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', evaluation_role=REPORT, source=source, config_hash=digest(config),
        inputs=inputs, paired_family_contrasts=contrasts, new_fits=0, new_model_queries=0)
    return common.receipt(config, source, result, dict(report=storage._pin(path)))
