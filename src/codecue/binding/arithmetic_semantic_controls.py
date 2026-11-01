"""Alternate-operator semantics on fixed, previously captured program states."""
import ast
import importlib.util
from itertools import permutations, combinations
from pathlib import Path

import numpy as np

from . import arithmetic_numeric_exploration as numeric
from . import arithmetic_numeric_geometry as geometry
from . import arithmetic_state_common as common
from . import arithmetic_state_audit as audit
from . import arithmetic_graph_readouts as storage
from . import relationship_capture as base
from . import interpreter
from .datasets import digest

PREPARE = 'discovery_semantic_control_prepare_v1'
CACHE = 'discovery_semantic_control_cache_view_v1'
FIT = 'discovery_semantic_control_fit_v1'
REPORT = 'discovery_semantic_control_report_v1'
SEMANTICS = ('ordinary', 'operator_swap')
HEADS = (('scalar', 1), ('sign', 3), ('parity', 2), ('mod5', 5))
FORMATS = tuple(k for k, _ in HEADS)
WIDTH = sum(d for _, d in HEADS)
BOUND = 384  # abs(root) <= 6; at most six +/- writes, each at most doubles max.
SLOTS = tuple(f'v{i}' for i in range(4))
PAIRS = tuple(permutations(range(4), 2))
EQUAL_PAIRS = tuple(combinations(range(4), 2))
TRIPLES = tuple(permutations(range(4), 3))


def literature(config):
    entries = config['literature']
    for entry in entries.values():
        if base._sha(entry['path']) != entry['sha256']: raise ValueError('literature evidence changed')
    register = base._json(entries['register']['path'], entries['register']['sha256'])
    if register['source_count'] != 23 or register['report_sha256'] != entries['report']['sha256']:
        raise ValueError('literature report/register identity differs')
    return entries


def rewrite(source, semantic):
    if semantic not in SEMANTICS: raise ValueError('declared operation semantics required')
    tree = interpreter.parse(source)
    if not 6 <= len(tree.body) <= 11 or not isinstance(tree.body[-1].value, ast.Name):
        raise ValueError('four-root, one-to-six-update canonical program required')
    for i, statement in enumerate(tree.body[:-1]):
        if statement.targets[0].id not in SLOTS: raise ValueError('canonical variable slots required')
        value = statement.value
        if i < 4:
            if statement.targets[0].id != SLOTS[i] or not (
                    isinstance(value, ast.Constant) or isinstance(value, ast.UnaryOp) and isinstance(value.operand, ast.Constant)):
                raise ValueError('four ordered integer roots required')
            root = interpreter.value(value, {})
            if abs(root) > 6: raise ValueError('root magnitude exceeds analytic alternate bound')
        else:
            if not isinstance(value, ast.BinOp) or not isinstance(value.op, (ast.Add, ast.Sub)) or not all(
                    isinstance(operand, ast.Name) for operand in (value.left, value.right)):
                raise ValueError('binary variable addition/subtraction updates required')
            if semantic == 'operator_swap': value.op = ast.Sub() if isinstance(value.op, ast.Add) else ast.Add()
    return ast.unparse(ast.fix_missing_locations(tree))


def traces(row):
    result = [interpreter.execute(rewrite(row['bare_canonical_source'], s), bound=BOUND) for s in SEMANTICS]
    ordinary, swapped = result
    if [w['value'] for w in ordinary['execution_trace']] != [w['value'] for w in row['oracle']['writes']]:
        raise ValueError('ordinary trace disagrees with archived oracle')
    if ordinary['expected_answer'] != row['oracle']['expected_answer']:
        raise ValueError('ordinary answer differs from archived oracle')
    for first, second in zip(ordinary['execution_trace'], swapped['execution_trace']):
        if any(first[k] != second[k] for k in ('statement', 'definition', 'versions', 'uses')):
            raise ValueError('operator relabeling changed assignment identity or def-use structure')
    if ordinary['dependency_edges'] != swapped['dependency_edges']: raise ValueError('dependencies changed')
    return result


def swap_examples(rows, cases):
    table = numeric.examples(rows, cases)
    values = [[w['value'] for w in traces(row)[1]['execution_trace']] for row in rows]
    return [dict(e, value=values[e['row']][e['statement']]) for e in table]


def targets(values):
    values = np.asarray(values)
    if values.ndim != 1 or not np.issubdtype(values.dtype, np.integer) or np.any((values < -BOUND) | (values > BOUND)):
        raise ValueError('integer semantic labels inside analytic bound required')
    return np.concatenate((values[:, None].astype(float), np.eye(3)[np.sign(values) + 1],
        np.eye(2)[values % 2], np.eye(5)[values % 5]), axis=1)


def predictions(scores):
    scores = np.asarray(scores)
    if scores.ndim != 2 or scores.shape[1] != WIDTH or not np.isfinite(scores).all():
        raise ValueError('finite declared semantic head layout required')
    return dict(scalar=scores[:, 0], sign=scores[:, 1:4].argmax(axis=1),
        parity=scores[:, 4:6].argmax(axis=1), mod5=scores[:, 6:11].argmax(axis=1))


def score_heads(scores, values, groups):
    guessed = predictions(scores)
    _, inverse, family_counts = np.unique(groups, return_inverse=True, return_counts=True)
    if not len(family_counts): raise ValueError('nonempty evaluation families required')
    def mean(value):
        return float(np.mean(np.bincount(inverse, weights=np.asarray(value, float)) / family_counts))
    result = dict(scalar=dict(exact=mean(np.rint(guessed['scalar']) == values),
        mae=mean(np.abs(guessed['scalar'] - values))))
    labels = dict(sign=np.sign(values) + 1, parity=values % 2, mod5=values % 5)
    for name, truth in labels.items():
        classes, counts = np.unique(truth, return_counts=True)
        if not len(classes): raise ValueError('nonempty semantic evaluation required')
        correct = guessed[name] == truth
        result[name] = dict(exact=mean(correct),
            balanced_accuracy=float(np.mean([correct[truth == c].mean() for c in classes])),
            support={str(int(c)): int(n) for c, n in zip(classes, counts)})
    return result


# Preserve the completed ordinary fits exactly. Ridge columns are independent;
# the alternate targets use the same feature scaler, weights, folds and grid.
spec = importlib.util.spec_from_file_location(__package__ + '._semantic_control_fit_engine', numeric.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.FIT, _CORE.HEADS, _CORE.FORMATS, _CORE.HEAD_WIDTH = FIT, HEADS, FORMATS, WIDTH
_CORE.examples, _CORE.targets, _CORE.predictions, _CORE.score_heads = swap_examples, targets, predictions, score_heads


def run(config):
    literature(config)
    if config['semantic'] != 'operator_swap' or config['role'] != 'computed_definition':
        raise ValueError('alternate computed-definition discovery recipe required')
    return _CORE.run(config)


def label_arrays(rows, cases, independent=True):
    table = numeric.examples(rows, cases)
    all_traces = [traces(row) for row in rows]
    if independent:
        for start in range(0, len(rows), 128):
            subset = rows[start:start + 128]
            sources = [rewrite(row['bare_canonical_source'], s) for row in subset for s in SEMANTICS]
            checked = interpreter.python_oracle(sources)
            for i, truth in enumerate(checked):
                trace = all_traces[start + i // 2][i % 2]
                if truth['answer'] != trace['expected_answer'] or truth['trace'] != [w['values'] for w in trace['execution_trace']]:
                    raise ValueError('independent Python semantic execution differs')
    values = np.asarray([[all_traces[e['row']][s]['execution_trace'][e['statement']]['value'] for s in range(2)]
        for e in table], dtype=np.int16)
    states = np.asarray([[[ts[s]['execution_trace'][e['statement']]['values'].get(slot, 0) for slot in SLOTS]
        for s in range(2)] for e in table for ts in [all_traces[e['row']]]], dtype=np.int16)
    versions = np.asarray([[int(all_traces[e['row']][0]['execution_trace'][e['statement']]['versions'].get(slot, '@0').split('@')[-1])
        for slot in SLOTS] for e in table], dtype=np.int16)
    final = np.asarray([[[trace['execution_trace'][-1]['values'][slot] for slot in SLOTS] for trace in ts]
        for ts in all_traces], dtype=np.int16)
    # These are exact oracle labels for later structured readouts, not inputs
    # or claims that the model decodes the relationships in this experiment.
    pairs = np.stack([final[:, :, a] < final[:, :, b] for a, b in PAIRS], axis=2)
    equal = np.stack([final[:, :, a] == final[:, :, b] for a, b in EQUAL_PAIRS], axis=2)
    ternary = np.stack([final[:, :, c] == final[:, :, a] + final[:, :, b] for a, b, c in TRIPLES], axis=2)
    return table, dict(definition_values=values, current_values=states, assignment_versions=versions,
        defined_slots=versions > 0, final_values=final, final_pair_lt=pairs, final_pair_eq=equal,
        final_triple_add=ternary, case_ids=np.asarray([r['id'] for r in rows]))


def diagnostics(table, values):
    result = {}
    for split in ('train', 'development', 'calibration'):
        mask = np.asarray([e['split'] == split and e['role'] == 'computed_definition' for e in table])
        result[split] = {}
        for index, semantic in enumerate(SEMANTICS):
            selected = values[mask, index]
            labels, counts = np.unique(selected, return_counts=True)
            p = counts / counts.sum()
            result[split][semantic] = dict(observations=len(selected), minimum=int(selected.min()), maximum=int(selected.max()),
                mean=float(selected.mean()), std=float(selected.std()), mean_abs=float(np.abs(selected).mean()),
                entropy_bits=float(-(p * np.log2(p)).sum()), outside_old_domain=int((np.abs(selected) > 96).sum()),
                histogram={str(int(k)): int(n) for k, n in zip(labels, counts)})
        result[split]['changed_values'] = int((values[mask, 0] != values[mask, 1]).sum())
    return result


def prepare(config):
    from .confidence import _run_lock
    source = common.validate_role(config, PREPARE); literature(config)
    _, _, _, rows, cases = audit.load_cache(config)
    folder = Path(config['run_dir']); folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
        table, arrays = label_arrays(rows, cases)
        altered = [dict(e, value=int(arrays['definition_values'][i, 1])) for i, e in enumerate(table)]
        path = folder / 'semantic_labels.npz'; storage._npz(path, **arrays)
        artifacts = dict(labels=storage._pin(path))
        for entry in config['cache_views']:
            view = base._json(entry['path'], entry['sha256']); common.validate_role(view, CACHE); literature(view)
            old = base._json(view['original_cache']['path'], view['original_cache']['sha256']); common.completed(old)
            old_result = base._json(Path(old['run_dir']) / 'results.json')
            if old_result['table_sha256'] != digest(table): raise ValueError('original feature example identities differ')
            output = dict(old_result, evaluation_role=CACHE, source=source, config_hash=digest(view),
                table_sha256=digest(altered), target_semantic='operator_swap', source_program_semantic='ordinary',
                original_cache=view['original_cache'], labels=artifacts['labels'], borrowed_features=True,
                new_model_queries=0, new_fits=0)
            if (Path(view['run_dir']) / 'completion_manifest_v1.json').exists(): common.completed(view)
            else: common.receipt(view, source, output, dict(old_result['features'], labels=artifacts['labels']))
            artifacts[Path(entry['path']).stem] = storage._pin(Path(view['run_dir']) / 'completion_manifest_v1.json')
        result = dict(status='complete_exploratory', evaluation_role=PREPARE, source=source, config_hash=digest(config),
            literature=config['literature'], cases=len(rows), examples=len(table), table_sha256=digest(table),
            alternate_table_sha256=digest(altered), analytic_bound=BOUND, semantics=list(SEMANTICS),
            ordinary_oracle_verified=True, independent_python_verified=True, excluded_rows=0,
            target_diagnostics=diagnostics(table, arrays['definition_values']),
            pair_coordinates=[list(p) for p in PAIRS], equal_coordinates=[list(p) for p in EQUAL_PAIRS],
            triple_coordinates=[list(p) for p in TRIPLES], new_model_queries=0, new_fits=0,
            scope='Fixed ordinary captures; alternate targets and future structured oracle labels only. No direct relation fits.')
        return common.receipt(config, source, result, artifacts)


def selected_panels(config, data, rows, cases, alternate, width=None):
    table = common.mask_table(numeric.examples(rows, cases), [e['role'] == 'computed_definition' for e in numeric.examples(rows, cases)])
    actual = swap_examples(rows, cases) if alternate else numeric.examples(rows, cases)
    values = np.asarray([e['value'] for e in actual if e['role'] == 'computed_definition'])
    ids = np.asarray([e['case_id'] + ':definition:' + str(e['statement']) for e in table])
    groups = np.asarray([e['group'] for e in table]); train = np.asarray([e['split'] == 'train' for e in table])
    dev = np.asarray([e['split'] == 'development' for e in table]); families = np.unique(groups[dev])
    width = config['widths'][-1] if width is None else width
    metrics, family = {name: {} for name in FORMATS}, {}
    for bank in data['fits']:
        if bank['width'] != width: continue
        names = set(bank['selected_formats']) & set(FORMATS)
        if not names: continue
        with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as saved:
            if not np.array_equal(saved['ids'], ids) or not np.array_equal(saved['truth'], values):
                raise ValueError('ordinary/alternate selected score identities differ')
            all_scores = saved['real'][dev]
        if alternate: scores = all_scores
        else: scores = np.concatenate([all_scores[:, numeric.slices()[name]] for name in FORMATS], axis=1)
        recomputed = score_heads(scores, values[dev], groups[dev])
        for name in names:
            if bank['seed'] in metrics[name]: raise ValueError('duplicate selected seed')
            reported = bank['development']['real'][name]
            if reported != recomputed[name]: raise ValueError('selected metric replay differs')
            metrics[name][bank['seed']] = recomputed[name]
        if 'scalar' in names:
            weights = common.weights(common.mask_table(table, train), bank['seed'])
            mean = np.average(values[train], weights=weights)
            scale = float(np.sqrt(np.average((values[train] - mean) ** 2, weights=weights)))
            if not np.isfinite(scale) or scale <= 0: raise ValueError('positive TRAIN-only target scale required')
            error = np.abs(predictions(scores)['scalar'] - values[dev]) / scale
            family[bank['seed']] = np.asarray([error[groups[dev] == g].mean() for g in families])
    if any(sorted(v) != [11, 29, 47] for v in metrics.values()) or sorted(family) != [11, 29, 47]:
        raise ValueError('complete ordinary/alternate seed panels required')
    return families.tolist(), metrics, np.stack([family[s] for s in (11, 29, 47)])


def report(config):
    source = common.validate_role(config, REPORT); literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return common.completed(config)
    _, _, _, rows, cases = audit.load_cache(config)
    prepared_cfg = base._json(config['prepared']['path'], config['prepared']['sha256']); common.completed(prepared_cfg)
    prepared_path = storage._pin(Path(prepared_cfg['run_dir']) / 'results.json')
    prepared = base._json(prepared_path['path'], prepared_path['sha256'])
    lines = ['# Ordinary versus alternate program semantics: discovery results', '',
        'All features were captured from ordinary programs. Ordinary fits are reused from the completed numeric study; '
        'alternate fits swap addition/subtraction meanings without changing inputs, captures, rows or splits. '
        'Scalar normalized MAE divides by the selected seed\'s weighted TRAIN target standard deviation. '
        'Differences in target difficulty remain explicit; this is not causal-use evidence.', '',
        '| Features | Width | Target semantics | Scalar exact | Scalar MAE | Normalized MAE | Sign BA | Parity BA | Mod5 BA |',
        '|---|---:|---|---:|---:|---:|---:|---:|---:|']
    inputs, cells, contrasts = {'prepared': prepared_path}, [], []
    for item in config['comparisons']:
        panels = {}
        for semantic, key in [('ordinary', 'ordinary'), ('operator_swap', 'alternate')]:
            request = item[key]; worker = base._json(request['path'], request['sha256']); common.completed(worker)
            entry = storage._pin(Path(worker['run_dir']) / 'results.json'); inputs[request['path']] = entry
            data = base._json(entry['path'], entry['sha256'])
            families, metrics, family = selected_panels(worker, data, rows, cases, key == 'alternate', item['width'])
            panels[semantic] = dict(metrics=metrics, family=family, families=families)
            average = lambda name, metric: float(np.mean([m[metric] for m in metrics[name].values()]))
            lines.append(f"| {item['name']} | {item['width']} | {semantic} | {100*average('scalar','exact'):.2f}% | "
                f"{average('scalar','mae'):.3f} | {family.mean():.3f} | {100*average('sign','balanced_accuracy'):.2f}% | "
                f"{100*average('parity','balanced_accuracy'):.2f}% | {100*average('mod5','balanced_accuracy'):.2f}% |")
        first, second = panels['ordinary'], panels['operator_swap']
        if first['families'] != second['families']: raise ValueError('semantic contrast families differ')
        contrast = geometry.paired_family_interval(second['family'], first['family'])
        contrasts.append(dict(name=item['name'], comparison='alternate minus ordinary normalized MAE', **contrast))
        cells.append(dict(name=item['name'], backend=item['backend'], width=item['width'], families=first['families'],
            difference=second['family'] - first['family']))
    for cell in cells:
        if cell['backend'] != 'hidden': continue
        matched = [s for s in cells if s['backend'] == 'source' and s['width'] == cell['width']]
        if len(matched) != 1 or matched[0]['families'] != cell['families']: raise ValueError('matched source cell required')
        contrasts.append(dict(name=cell['name'], comparison='hidden semantic preference minus matched source preference',
            **geometry.paired_family_interval(cell['difference'], matched[0]['difference'])))
    lines += ['', '## Paired family contrasts', '',
        'Positive differences favor ordinary semantics. Average the three fitting seeds within each family, then bootstrap '
        'structural families (2,000 replicates, seed 20261031). Intervals are descriptive, non-simultaneous and use adaptive DEV. '
        'A positive difference can reflect target difficulty or surface inductive biases; source contrasts help assess this limitation.', '',
        '| Features | Contrast | Difference | 95% interval | Families |', '|---|---|---:|---:|---:|']
    for c in contrasts:
        lines.append(f"| {c['name']} | {c['comparison']} | {c['delta']:.3f} | [{c['lower']:.3f}, {c['upper']:.3f}] | {c['families']} |")
    lines += ['', '## Target difficulty', '',
        '| Split | Semantics | Rows | Range | Standard deviation | Value entropy (bits) | Values beyond old ±96 domain |',
        '|---|---|---:|---|---:|---:|---:|']
    for split, panel in prepared['target_diagnostics'].items():
        for semantic in SEMANTICS:
            d = panel[semantic]
            lines.append(f"| {split} | {semantic} | {d['observations']} | [{d['minimum']}, {d['maximum']}] | "
                f"{d['std']:.3f} | {d['entropy_bits']:.3f} | {d['outside_old_domain']} |")
    lines += ['', 'No rows were clipped, wrapped or removed. Label entropies describe the row distribution, not independent samples. '
        'Fixed paired inputs and source controls do not prove equal learnability of the two target semantics. '
        'Only one nonidentity permutation exists for this two-operator language. '
        'The oracle archive also prepares all-variable/version and pair/triple relation labels; these are not additional decoded results. '
        'No misleading-name, trace-format, unfamiliar-family confirmation or neural-intervention claim is established here. '
        'Family-shuffled controls and encoded TRAIN priors remain in the saved fit banks; their alphas are selected on real TRAIN targets. '
        'Ordinary baseline fits retain their original source and larger independent-column target layout.', '']
    path = Path(config['report']); base._publish(path, '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', evaluation_role=REPORT, source=source, config_hash=digest(config),
        inputs=inputs, literature=config['literature'], paired_family_contrasts=contrasts,
        new_model_queries=0, new_fits=0, generated_holdouts_opened=False)
    return common.receipt(config, source, result, dict(report=storage._pin(path)))
