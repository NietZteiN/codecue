"""Evaluate predicted binding -> numeric value -> algebraic relation pipelines."""
from collections import defaultdict
import ast
from pathlib import Path

import numpy as np

from . import arithmetic_state_common as common
from . import arithmetic_binding_readouts as binding
from . import arithmetic_numeric_readouts as numeric
from . import arithmetic_graph_readouts as graph
from . import relationship_capture as base
from .datasets import digest

ROLE = 'discovery_arithmetic_state_composition_v1'


def route_values(pointers, point_values, cases):
    """Use predicted node IDs only. No oracle value or latest-definition pointer."""
    if pointers.shape != (len(cases), 4) or not np.issubdtype(pointers.dtype, np.integer):
        raise ValueError('four integer predicted pointers per program required')
    result = np.empty(pointers.shape, float)
    for i, case in enumerate(cases):
        nodes = [j for j, d in enumerate(case['descriptors']) if d['kind'] == 'definition']
        for slot, pointer in enumerate(pointers[i]):
            if not 0 <= pointer < len(nodes):
                raise ValueError('predicted definition is outside supplied node scaffold')
            value = point_values[i, nodes[int(pointer)]]
            if not np.isfinite(value):
                raise ValueError('routed definition has no finite numeric prediction')
            result[i, slot] = value
    return result


def operand_composition(point_values, rows, cases):
    """External arithmetic on decoded operands; not a decoded neural result."""
    output = point_values.copy()
    for i, (row, case) in enumerate(zip(rows, cases)):
        statements = ast.parse(row['source']).body[:-1]
        for point, descriptor in enumerate(case['descriptors']):
            if descriptor['kind'] != 'definition' or descriptor['statement'] < 4:
                continue
            statement = descriptor['statement']
            operands = {p['side']: j for j, p in enumerate(case['descriptors']) if p['kind'] == 'use' and p['statement'] == statement}
            left, right = point_values[i, operands['left']], point_values[i, operands['right']]
            op = statements[statement].value.op
            if isinstance(op, ast.Add):
                output[i, point] = left + right
            elif isinstance(op, ast.Sub):
                output[i, point] = left - right
            else:
                raise ValueError('declared addition/subtraction syntax required')
    return output


def relation_metrics(predicted, truth, eligible):
    families, cells = defaultdict(list), []
    for i, relation in enumerate(graph.RELATIONS):
        target, guess = truth[:, i], predicted[:, i]
        positive, negative = int(target.sum()), int((~target).sum())
        score = float((guess[target].mean() + (~guess[~target]).mean()) / 2) if positive and negative else None
        cells.append(dict(relation=list(relation), positive=positive, negative=negative,
            eligible_from_train=bool(eligible[i]), balanced_accuracy=score))
        if eligible[i] and score is not None:
            families[relation[0]].append(score)
    return dict(macro_balanced_accuracy=float(np.mean([np.mean(v) for v in families.values()])) if families else None,
        family_balanced_accuracy={k: float(np.mean(v)) for k, v in families.items()}, cells=cells)


def metrics(values, truth, groups, eligible):
    if values.shape != truth.shape or values.shape[1] != 4 or not np.isfinite(values).all():
        raise ValueError('finite aligned four-variable state predictions required')
    correct = np.rint(values) == truth
    per_row_accuracy = correct.mean(axis=1)
    per_row_mae = np.abs(values - truth).mean(axis=1)
    whole = correct.all(axis=1)
    family_accuracy, families = common.group_mean(per_row_accuracy, groups)
    relation_truth = graph.relations(truth)
    relation_predictions = graph.relations(np.rint(values))
    return dict(value_accuracy=float(correct.mean()), whole_state_accuracy=float(whole.mean()),
        family_macro_value_accuracy=family_accuracy, family_macro_mae=common.group_mean(per_row_mae, groups)[0],
        family_value_accuracy=families, family_whole_state=common.group_mean(whole, groups)[1],
        relations=relation_metrics(relation_predictions, relation_truth, eligible))


def run(config):
    from .confidence import _run_lock
    source = common.validate_role(config, ROLE)
    audit_config, cache, profile, rows, cases = common.inputs(config)
    binding_config = base._json(config['binding_config'], config['binding_config_sha256'])
    numeric_config = base._json(config['numeric_config'], config['numeric_config_sha256'])
    common.completed(binding_config)
    common.completed(numeric_config)
    bindings = base._json(Path(binding_config['run_dir']) / 'results.json')
    numbers = base._json(Path(numeric_config['run_dir']) / 'results.json')
    folder = Path(config['run_dir'])
    folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        if (folder / 'completion_manifest_v1.json').exists():
            return common.completed(config)
        table = numeric.examples(rows, cases)
        truth = np.asarray([r['oracle']['values'] for r in rows])
        true_pointers = np.asarray([r['oracle']['definitions'] for r in rows])
        groups = np.asarray([r['component_id'] for r in rows])
        split = np.asarray([r['split'] for r in rows])
        relations = graph.relations(truth)
        unique_train = np.asarray([r['split'] == 'train' and r['lexical_realization'] == 0 for r in rows])
        eligible = (relations[unique_train].sum(axis=0) >= 12) & ((~relations[unique_train]).sum(axis=0) >= 12)
        old_config = base._json(audit_config['probe_config'], audit_config['probe_config_sha256'])
        entry = cache['inputs']['probe_results']
        parents = base._json(entry['path'], entry['sha256'])
        results, artifacts = [], {}
        routes = [('anchor_query', 'hidden', 'regression'), ('anchor_query', 'hidden', 'categorical'),
                  ('answer_query', 'hidden', 'regression'), ('source_query', 'source', 'regression'),
                  ('oracle_route', 'hidden', 'regression'), ('anchor_query_operands', 'hidden', 'regression')]
        for seed in common.SEEDS:
            pointer_predictions, point_predictions = {}, {}
            for bank in bindings['fits']:
                if bank['seed'] != seed or bank['target'] != 'real':
                    continue
                entry = bank['artifacts']['scores']
                with np.load(entry['path'], allow_pickle=False) as data:
                    if not np.array_equal(data['row_indices'], np.repeat(np.arange(len(rows)), 4)) or not np.array_equal(data['slots'], np.tile(np.arange(4), len(rows))):
                        raise ValueError('binding prediction row/slot identity differs')
                    if not np.array_equal(data['predictions'], data['logits'].argmax(axis=1).reshape(len(rows), 4)):
                        raise ValueError('binding prediction decisions differ from saved scores')
                    pointer_predictions[bank['backend']] = data['predictions']
            for bank in numbers['fits']:
                if bank['seed'] != seed:
                    continue
                entry = bank['artifacts']['scores']
                with np.load(entry['path'], allow_pickle=False) as data:
                    if (not np.array_equal(data['row_indices'], [e['row'] for e in table])
                            or not np.array_equal(data['point_indices'], [e['point'] for e in table])
                            or not np.array_equal(data['truth'], [e['value'] for e in table])):
                        raise ValueError('numeric prediction point/target identity differs')
                    values = np.full((len(rows), 23), np.nan)
                    for e, predicted in zip(table, data['predicted']):
                        values[e['row'], e['point']] = predicted
                    point_predictions[(bank['backend'], bank['format'])] = values
            parent_bank = next(b for b in parents['fits'] if b['seed'] == seed and b['backend'] == 'hidden_local'
                and b['target'] == 'real' and b['training_families'] == 216)
            entry = parent_bank['artifacts']['scores']
            if base._sha(entry['path']) != entry['sha256']:
                raise ValueError('original parent predictions changed')
            parent_correct = defaultdict(list)
            with np.load(entry['path'], allow_pickle=False) as data:
                for case_id, correct in zip(data['case_ids'], data['logits'].argmax(axis=1) == data['real_labels']):
                    parent_correct[str(case_id)].append(bool(correct))
            for route, backend, kind in routes:
                pointers = true_pointers if route == 'oracle_route' else pointer_predictions['anchor_query' if route == 'anchor_query_operands' else route]
                point_values = point_predictions[(backend, kind)]
                if route == 'anchor_query_operands':
                    point_values = operand_composition(point_values, rows, cases)
                values = route_values(pointers, point_values, cases)
                current = pointers == true_pointers
                version_correct = np.asarray([[rows[i]['oracle']['writes'][int(pointers[i, slot])]['version'] ==
                    rows[i]['oracle']['writes'][int(true_pointers[i, slot])]['version'] for slot in range(4)] for i in range(len(rows))])
                key = f'pipeline_{route}_{backend}_{kind}_seed{seed}'
                path = folder / (key + '_scores.npz')
                graph._npz(path, values=values, pointers=pointers, truth=truth, true_pointers=true_pointers,
                    ids=np.asarray([r['id'] for r in rows]), development=split == 'development')
                panels = {}
                for label in ('train', 'development', 'calibration'):
                    mask = split == label
                    panel = metrics(values[mask], truth[mask], groups[mask], eligible)
                    panel.update(binding_accuracy=float(current[mask].mean()), whole_binding_accuracy=float(current[mask].all(axis=1).mean()),
                        annotated_version_accuracy=float(version_correct[mask].mean()))
                    joint = [bool(current[i].all() and (np.rint(values[i]) == truth[i]).all() and all(parent_correct[rows[i]['id']]))
                        for i in np.flatnonzero(mask) if rows[i]['id'] in parent_correct]
                    panel['binding_values_and_parent_edges_accuracy'] = float(np.mean(joint)) if joint else None
                    panels[label] = panel
                results.append(dict(route=route, numeric_backend=backend, numeric_format=kind, seed=seed,
                    oracle_router_supplied=route == 'oracle_route', panels=panels, scores=graph._pin(path)))
                artifacts[key] = graph._pin(path)
            for bank in numbers['global_fits']:
                if bank['seed'] != seed:
                    continue
                with np.load(bank['artifacts']['scores']['path'], allow_pickle=False) as data:
                    if not np.array_equal(data['ids'], [r['id'] for r in rows]) or not np.array_equal(data['truth'][:, :4], truth):
                        raise ValueError('global answer-state prediction identity differs')
                    panels = {}
                    for label in ('train', 'development', 'calibration'):
                        mask = split == label
                        panels[label] = metrics(data['real'][mask, :4], truth[mask], groups[mask], eligible)
                        panels[label]['direct_relations'] = relation_metrics(data['real'][mask, 4:52] >= .5, relations[mask], eligible)
                        panels[label]['prior'] = metrics(data['prior'][mask, :4], truth[mask], groups[mask], eligible)
                    results.append(dict(route='pure_answer_state', numeric_backend=bank['backend'], numeric_format='regression',
                        seed=seed, oracle_router_supplied=False, panels=panels, scores=bank['artifacts']['scores']))
        result = dict(status='complete_exploratory', evaluation_role=ROLE, source=source, config_hash=digest(config),
            model=profile['model'], pipelines=results, primary_pipeline=['anchor_query', 'hidden', 'regression'],
            new_model_queries=0, new_fits=0, generated_holdouts_opened=False,
            limitations='Adaptive composed discovery readouts with supplied variable/definition scaffold. Primary uses predicted '
                'pointers; oracle-route results are an explicitly supplied ceiling. Versions annotate predicted nodes. '
                'Candidate-history answer queries differ from pure single-answer-state numeric heads. '
                'Operand-composition results use supplied source operators and external arithmetic, not decoded neural results. '
                'Parent/value/binding models are independently fitted, not jointly trained. No causal or confirmatory claim.')
        return common.receipt(config, source, result, artifacts)
