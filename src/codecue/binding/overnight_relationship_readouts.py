"""Frozen, train-only readouts for the overnight relationship cohorts.

Each run selects one panel from a separately verified union capture.  Source
normalization is used only to construct oracle labels; features always retain
the actual literal/computed source and the actual visible query prefix.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import time

import numpy as np

from . import relationship_capture as bounded
from . import relationship_readouts as original
from . import relationship_targets as target
from .datasets import digest, write_json
from .programs import rename
from .registry import code_identity
from .weighted_ridge import from_parameters

ROLE = 'discovery_overnight_relationship_readouts_v1'
PANELS = ('numeric_replication', 'query_twins', 'computed_roots')
SITES = (3, 7, 8)
SEEDS = (11, 29, 47)
COMPLETION = 'completion_manifest_v1.json'
MAX_RESULT = 128 * 1024**2
LIMITATION = (
    'Exploratory overnight follow-up on the same fixed four-root/four-copy '
    'structural scaffold. New numeric seeds, queries and constant-root formats '
    'are not independent structural or causal replications. Only TRAIN neutral '
    'rows fit normalizers and ridge heads. The fixed categorical value pipeline '
    'and direct relation pipeline have different total parameter counts. '
    'Source-valued and hidden-valued baselines are both retained. Relations '
    'are oracle targets, never features. Constant-expression canonicalization '
    'is target-only; feature prefixes are the actual captured source. '
    'Conditional intervals resample nine development components without '
    'refitting or multiplicity correction. Weighting seeds and lexical/query '
    'relatives are not independent experiments. Whole-row donor controls preserve '
    'unweighted split marginals; weighted marginals and task difficulty may differ. Parent reconstruction assumes '
    'known node/version identities and does not establish natural causal use.'
)


def protocol():
    return dict(sites=list(SITES), seeds=list(SEEDS), alpha=100.,
        source_features='signed character ngrams 3..8, matched hidden width',
        primary_algebraic_cells=18, primary_train_minimum_class_groups=12,
        categorical_value_domain=list(target.VALUE_CLASSES), binary_threshold=.5,
        shuffle='split/component derangement; base-block permutation; first-parent permutation; lexical/query ties',
        bootstrap=original.BOOTSTRAP, layer_selection='explicit nominated layer before capture',
        output_ancestry='actual query slot at pre_answer; never canonicalized to v0')


def _capture():
    from . import overnight_relationship_capture
    return overnight_relationship_capture


def _config(config):
    required = {'evaluation_role', 'capture_config', 'capture_config_sha256',
        'declared_plan', 'declared_plan_sha256', 'primary_layer', 'panel', 'run_dir', 'report'}
    optional = {'transfer_from', 'transfer_from_sha256'}
    if (not isinstance(config, dict) or config.get('evaluation_role') != ROLE
            or required - set(config) or set(config) - required - optional
            or config.get('panel') not in PANELS):
        raise ValueError('exact overnight discovery readout configuration required')
    if ('transfer_from' in config) != ('transfer_from_sha256' in config):
        raise ValueError('literal transfer configuration and checksum are paired')
    if 'transfer_from' in config and config['panel'] != 'computed_roots':
        raise ValueError('literal-to-computed transfer belongs to computed_roots only')
    for key in ('capture_config_sha256', 'declared_plan_sha256',
                *(['transfer_from_sha256'] if 'transfer_from' in config else [])):
        value = config[key]
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('explicit SHA256 identity required')
    if type(config['primary_layer']) is not int or config['primary_layer'] < 0:
        raise ValueError('explicit nominated primary layer required')
    for key in ('capture_config', 'declared_plan', 'run_dir', 'report',
                *(['transfer_from'] if 'transfer_from' in config else [])):
        if not isinstance(config[key], str) or not config[key]: raise ValueError('explicit safe path required')
        bounded._safe(config[key])
    out, report = Path(config['run_dir']).resolve(), Path(config['report']).resolve()
    if report.suffix != '.md' or report in {out, *(Path(config[k]).resolve() for k in ('capture_config', 'declared_plan'))}:
        raise ValueError('report cannot replace an input or output directory')
    reserved={out/name for name in ('registration.json','results_v1.json','audit.json','summary.json',COMPLETION,'progress.json')}
    if report in reserved or any(parent in reserved or (out in parent.parents and parent.suffix=='.npz') for parent in report.parents):
        raise ValueError('report cannot be nested under a reserved output file')
    inputs=[Path(config[k]).resolve() for k in ('capture_config','declared_plan',*(['transfer_from'] if 'transfer_from' in config else []))]
    if any(out==p or out in p.parents for p in inputs):raise ValueError('output cannot contain declared inputs')
    if len(original._json_bytes(config)) > 16*1024: raise ValueError('bounded overnight configuration required')
    return config


def _source(config, scheduled):
    _config(config)
    if scheduled:
        bounded._slurm()
        return bounded._current_source(config)
    registration = bounded._json(Path(config['run_dir'])/'registration.json')
    if (registration.get('evaluation_role') != ROLE or registration.get('config') != config
            or registration.get('config_hash') != digest(config)):
        raise ValueError('original overnight registration identity differs')
    source = registration.get('analysis_source')
    bounded._verify_source(config, source)
    return source


def select_panel(cases, panel):
    if panel not in PANELS: raise ValueError('known overnight panel required')
    indices = []
    for index, case in enumerate(cases):
        row = case['record']
        selected = panel in row.get('cohorts', [])
        selected &= row.get('source_form') == ('computed' if panel == 'computed_roots' else 'literal')
        selected &= panel == 'query_twins' or row.get('query_slot') == 0
        if selected: indices.append(index)
    if not indices: raise ValueError('capture has no rows for requested panel')
    return np.asarray(indices, dtype=np.int64)


def _integer(expression):
    if isinstance(expression, ast.Constant) and type(expression.value) is int: return expression.value
    if isinstance(expression, ast.UnaryOp) and isinstance(expression.op, (ast.UAdd, ast.USub)):
        value = _integer(expression.operand)
        return value if isinstance(expression.op, ast.UAdd) else -value
    if isinstance(expression, ast.BinOp) and isinstance(expression.op, (ast.Add, ast.Sub)):
        left, right = _integer(expression.left), _integer(expression.right)
        return left + right if isinstance(expression.op, ast.Add) else left - right
    raise ValueError('root must be an independent integer constant expression')


def source_facts(row):
    """Derive oracle-only facts from the actual surface-verified source."""
    tree = ast.parse(row['canonical_source']); mapping = row['rename_map']
    if len(tree.body) != 9: raise ValueError('four roots/four copies/one query required')
    assignments = tree.body[:8]
    if any(not isinstance(s, ast.Assign) or len(s.targets) != 1 or not isinstance(s.targets[0], ast.Name)
           or s.targets[0].id != f'v{i%4}' for i, s in enumerate(assignments)):
        raise ValueError('fixed canonical assignment schedule required')
    query = tree.body[-1]
    if not isinstance(query, ast.Expr) or not isinstance(query.value, ast.Name) or query.value.id not in {f'v{i}' for i in range(4)}:
        raise ValueError('one explicit query slot required')
    slot = int(query.value.id[1:])
    if row.get('source_form') not in ('literal','computed'): raise ValueError('declared source form required')
    for statement in assignments[:4]:
        expression=statement.value
        if row['source_form']=='literal' and isinstance(expression,ast.BinOp):
            raise ValueError('literal roots cannot be computed expressions')
        if row['source_form']=='computed':
            if not isinstance(expression,ast.BinOp) or not isinstance(expression.op,(ast.Add,ast.Sub)):
                raise ValueError('computed roots require one binary plus/minus')
            if any(isinstance(node,ast.BinOp) for child in (expression.left,expression.right) for node in ast.walk(child)):
                raise ValueError('computed root operands must be integer literals')
    values = [_integer(s.value) for s in assignments[:4]]
    if any(value not in target.VALUE_CLASSES for value in values): raise ValueError('root outside categorical domain')
    parents = []
    for i, statement in enumerate(assignments[4:]):
        if not isinstance(statement.value, ast.Name) or statement.value.id not in {f'v{j}' for j in range(4) if j != i}:
            raise ValueError('three-way distinct-slot copy required')
        parents.append(int(statement.value.id[1:]))
    if (type(row.get('query_slot')) is not int or row['query_slot'] != slot
            or ('root_values' in row and row['root_values'] != values)
            or ('parent_slots' in row and row['parent_slots'] != parents)):
        raise ValueError('source-derived query/root/parent metadata differs')
    if ast.dump(ast.parse(rename(row['canonical_source'], mapping))) != ast.dump(ast.parse(row['source'])):
        raise ValueError('actual canonical and surface sources differ')
    return dict(row,root_values=values,parent_slots=parents)


def canonical_target_row(row):
    """Normalize only oracle input; never feed the normalization as features."""
    row=source_facts(row);values=row['root_values'];parents=row['parent_slots'];mapping=row['rename_map']
    source = '\n'.join([*(f'v{i} = {value}' for i, value in enumerate(values)),
        *(f'v{i} = v{parent}' for i, parent in enumerate(parents)), 'v0'])
    return dict(row, canonical_source=source, source=rename(source, mapping),
        variable_slots={f'v{i}': i for i in range(4)})


def targets(records, site):
    normalized = [canonical_target_row(row) for row in records]
    parts = [target.targets(normalized[first:first+target.MAX_ROWS], site)
             for first in range(0, len(records), target.MAX_ROWS)]
    first = parts[0]
    arrays = {name: target._readonly(np.concatenate([getattr(part, name) for part in parts]))
              for name in ('y', 'mask', 'numeric_truth', 'numeric_mask', 'parent_truth', 'parent_mask')}
    identities = {name: sum((getattr(part, name) for part in parts), ())
                  for name in ('case_ids', 'group_ids', 'splits', 'label_case_ids')}
    if len(set(identities['case_ids'])) != len(records): raise ValueError('unique ordered overnight case IDs required')
    splits = defaultdict(set)
    for group, split in zip(identities['group_ids'], identities['splits']): splits[group].add(split)
    if any(len(value) != 1 for value in splits.values()): raise ValueError('component crosses TRAIN/DEV')
    if site == 8:
        y = np.array(arrays['y'], copy=True)
        for index, row in enumerate(records):
            direct = np.zeros((8, 8), dtype=bool)
            for spec in target.COLUMNS:
                if spec['family'] == 'direct' and arrays['mask'][index, spec['index']]:
                    direct[target.NODE_INDEX[spec['source_node']], target.NODE_INDEX[spec['consumer_node']]] = bool(y[index, spec['index']])
            ancestor = target._closure(direct); query_node = 4 + row['query_slot']
            for spec in target.COLUMNS:
                if spec['family'] == 'output_ancestor':
                    node = target.NODE_INDEX[spec['source_node']]
                    y[index, spec['index']] = node == query_node or ancestor[node, query_node]
        arrays['y'] = target._readonly(y)
    return replace(first, **arrays, **identities, descriptive=dict(first.descriptive,
        target_only_root_canonicalization=True, actual_query_output_ancestry=True,
        source_forms=sorted({r['source_form'] for r in records})))


def coherent_donors(records, seed):
    """Whole-row donor permutation with component/base/parent/lex/query ties."""
    groups = defaultdict(lambda: defaultdict(dict)); initial = {}
    for index, row in enumerate(records):
        group, base = row['template_id'], row['base_id']
        state = tuple(row['root_values'])
        if state in initial and initial[state] != base:
            raise ValueError('different numeric bases have identical initial states')
        initial[state] = base
        key = (row['parent_slots'][0], row['lexical_realization'], row['query_slot'])
        if key in groups[row['split']][group].setdefault(base, {}): raise ValueError('duplicate control relative')
        groups[row['split']][group][base][key] = index
    rng = np.random.default_rng(int(seed)+100000); donors = np.full(len(records), -1, dtype=np.int64)
    for split, components in groups.items():
        names = sorted(components)
        if len(names) < 2: raise ValueError('at least two whole components per split required')
        perm = np.arange(len(names))
        for _ in range(1000):
            perm = rng.permutation(len(names))
            if np.all(perm != np.arange(len(names))): break
        else: raise ValueError('component derangement failed')
        for group_index, name in enumerate(names):
            left = sorted(components[name]); right_group = components[names[perm[group_index]]]
            right = sorted(right_group)
            if len(left) != len(right): raise ValueError('control component base coverage differs')
            for left_base, right_index in zip(left, rng.permutation(len(right))):
                recipient, supplier = components[name][left_base], right_group[right[right_index]]
                roles = sorted({key[0] for key in recipient}); donor_roles = sorted({key[0] for key in supplier})
                if len(roles) != 3 or len(donor_roles) != 3: raise ValueError('three first-parent variants required')
                mapping = dict(zip(roles, rng.permutation(donor_roles)))
                if {(lex, query) for _, lex, query in recipient} != {(lex, query) for _, lex, query in supplier}:
                    raise ValueError('lexical/query control coverage differs')
                for (parent, lex, query), index in recipient.items():
                    if (mapping[parent], lex, query) not in supplier: raise ValueError('incomplete parent/lex/query factorial')
                    donors[index] = supplier[mapping[parent], lex, query]
    if set(donors.tolist()) != set(range(len(records))): raise ValueError('whole-row donor bijection required')
    return donors


def _verify_prefix_controls(cases, bundles, donors):
    for site_index, site in enumerate(SITES):
        bundle = bundles[site]; seen = {}
        for index, case in enumerate(cases):
            key = case['visible_prefixes'][site_index]
            donor = donors[index]
            fingerprint = (bundle.y[donor].tobytes(), bundle.mask[donor].tobytes())
            if key in seen and seen[key] != fingerprint:
                raise ValueError('identical visible prefixes have contradictory shuffled targets')
            seen[key] = fingerprint


def _metadata(config, scheduled=False):
    source = _source(config, scheduled)
    if bounded._sha(config['declared_plan']) != config['declared_plan_sha256']:
        raise ValueError('overnight plan checksum differs')
    cap_config = bounded._json(config['capture_config'], config['capture_config_sha256'])
    checked = _capture().completed_metadata(cap_config)
    if checked['config'] != cap_config: raise ValueError('resolved capture config differs')
    indices = select_panel(checked['cases'], config['panel'])
    cases = [checked['cases'][i] for i in indices]; records = [source_facts(case['record']) for case in cases]
    layers = checked['layers']; shape = checked['feature_shape']
    if (not isinstance(shape,list) or len(shape)!=4 or len(layers) != 4 or config['primary_layer'] not in layers or shape != [len(checked['cases']), 3, 4, shape[-1]]
            or not 1 <= shape[-1] <= 16384 or not 1 <= len(cases) <= 25000
            or checked['sites'] != ['statement:3', 'statement:7', 'pre_answer']):
        raise ValueError('fixed three-site/four-layer overnight feature geometry required')
    group_splits = defaultdict(set)
    for row, case in zip(records, cases):
        if row.get('condition') != 'neutral' or row.get('split') not in ('train', 'development') or len(case['visible_prefixes']) != 3:
            raise ValueError('neutral TRAIN/DEV visible-prefix cases required')
        group_splits[row['template_id']].add(row['split'])
    if any(len(v) != 1 for v in group_splits.values()) or Counter(next(iter(v)) for v in group_splits.values()) != {'train':18, 'development':9}:
        raise ValueError('18 TRAIN/nine DEV structural components required')
    folder = Path(cap_config['run_dir']).resolve(); out = Path(config['run_dir']).resolve(); report = Path(config['report']).resolve()
    if out == folder or folder in out.parents or out in folder.parents or folder in report.parents:
        raise ValueError('readout/capture outputs cannot overlap')
    if report == Path(cap_config['dataset']).resolve(): raise ValueError('report cannot replace source dataset')
    return source, checked, indices, cases, records


def _bundles(records, cases):
    bundles = {site: targets(records, site) for site in SITES}
    train = np.asarray([r['split'] == 'train' for r in records]); indices = np.flatnonzero(train)
    support = {site: target.training_support(target.subset(bundle, indices), min_class_groups=12)
               for site, bundle in bundles.items()}
    eligible = target.fixed_primary_boolean_indices(bundles[3])
    qualified = set(eligible) <= set(support[3]['eligible_boolean_indices'])
    donors = {seed: coherent_donors(records, seed) for seed in SEEDS}
    for donor in donors.values(): _verify_prefix_controls(cases, bundles, donor)
    return bundles, support, eligible, train, donors, qualified


def preflight(config):
    _, checked, _, cases, records = _metadata(config, scheduled=True)
    _, support, eligible, train, _, qualified = _bundles(records, cases)
    return dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), cases=len(records),
        training_rows=int(train.sum()), development_rows=int((~train).sum()),
        primary_cells=list(eligible), primary_training_support_qualified=qualified,
        training_support=support[3], model=checked['model'], primary_layer=config['primary_layer'],
        raw_activation_arrays_loaded=False, new_model_queries=0, generated_holdouts_opened=False)


def _load(checked, selected):
    shape = [len(selected), *checked['feature_shape'][1:]]
    features = np.empty(shape, dtype=np.float32); first = 0; written = 0
    for entry in checked['chunks']:
        if entry['first'] != first: raise ValueError('contiguous union capture chunks required')
        positions = np.flatnonzero((selected >= first) & (selected < first + entry['rows']))
        if len(positions):
            cases = checked['cases'][first:first+entry['rows']]
            values, _ = _capture().load_chunk(entry, cases, checked['config'])
            features[positions] = values[selected[positions]-first]; written += len(positions)
        first += entry['rows']
    if first != len(checked['cases']) or written != len(selected) or not np.isfinite(features).all():
        raise ValueError('complete finite selected-panel features required')
    return features


def _selection(bundle, scores, rows):
    q = np.asarray([row['query_slot'] for row in rows]); n = len(rows)
    values = target.categorical_value_predictions(bundle, scores) == bundle.numeric_truth
    queried_values = values[np.arange(n), q].astype(float)
    result = dict(queried_value_correct=queried_values,
        unqueried_value_correct=(values.sum(axis=1)-queried_values)/3)
    parent_columns = [s['index'] for s in target.COLUMNS if s['kind'] == 'parent']
    if np.all(bundle.parent_mask) and np.isfinite(scores[:, parent_columns]).all():
        parents = target.reconstruct_parent_graph(bundle, scores)['parent_predictions'] == bundle.parent_truth
        queried = parents[np.arange(n), q].astype(float)
        result.update(queried_parent_correct=queried, unqueried_parent_correct=(parents.sum(axis=1)-queried)/3)
    return result


def _summary(bundle, correctness, selections, records, qualified):
    groups = np.asarray(bundle.group_ids); queries = np.asarray([r['query_slot'] for r in records])
    names = sorted(set(groups.tolist())); families = next(iter(correctness.values()))['families']
    truth = next(iter(correctness.values()))['truth']
    algebraic = {name: value['algebraic'] for name, value in correctness.items()}
    result = dict(site=bundle.site, query_slots=sorted(set(queries.tolist())), per_query={}, per_component={})
    result['algebraic'] = original.algebraic_bootstrap(truth, algebraic, groups, families) if bundle.site == 3 and qualified else dict(
        status='descriptive_only' if bundle.site != 3 else 'unqualified_training_support',
        methods={name: original.family_macro_balanced_accuracy(value, truth, families) for name, value in algebraic.items()}, comparisons={})
    structural = {name: value['graph'] for name, value in correctness.items() if np.isfinite(value['graph']).all()}
    result['structural'] = original.structural_bootstrap(structural, groups) if bundle.site in (7,8) and 'direct' in structural else None
    def describe(chosen):
        methods = {}
        for name, value in correctness.items():
            methods[name] = dict(algebraic=original.family_macro_balanced_accuracy(value['algebraic'][chosen], truth[chosen], families),
                whole_graph_accuracy=float(value['graph'][chosen].mean()) if np.isfinite(value['graph'][chosen]).all() else None)
            if name in selections:
                methods[name]['query_selection'] = {key: float(array[chosen].mean()) for key, array in selections[name].items()}
        return methods
    for query in sorted(set(queries.tolist())): result['per_query'][str(query)] = describe(np.flatnonzero(queries == query))
    for group in names: result['per_component'][group] = describe(np.flatnonzero(groups == group))
    result.update(grouped_uncertainty_unit='structural component', query_effect_intervals_computed=False,
        seed_aggregation='Mean row correctness over three fixed group-weight fits before summaries.',
        query_selection_interpretation='Probe correctness for queried versus other slots; no behavioral responses or causal-use inference.')
    return result


def _transfer(config, checked, records):
    if 'transfer_from' not in config: return None
    other = bounded._json(config['transfer_from'], config['transfer_from_sha256'])
    if other.get('panel') != 'numeric_replication': raise ValueError('literal numeric replication transfer source required')
    if other['capture_config_sha256']!=config['capture_config_sha256']:
        raise ValueError('literal transfer must use the same pinned union capture')
    output,old_output=Path(config['run_dir']).resolve(),Path(other['run_dir']).resolve()
    report,old_report=Path(config['report']).resolve(),Path(other['report']).resolve()
    if (output==old_output or output in old_output.parents or old_output in output.parents
            or report==old_report or old_report in report.parents or old_output==report or old_output in report.parents
            or output==old_report or output in old_report.parents):
        raise ValueError('literal transfer source and output cannot overlap')
    result = completed_result(other)
    old_records=[source_facts(checked['cases'][i]['record']) for i in select_panel(checked['cases'],'numeric_replication')]
    old_pairs = {row['format_pair_id']: row for row in old_records}
    if len(old_pairs) != len(old_records) or set(old_pairs) != {row['format_pair_id'] for row in records}:
        raise ValueError('one-to-one literal/computed format pairs required')
    for row in records:
        peer = old_pairs[row['format_pair_id']]
        if any(row[key] != peer[key] for key in ('split','template_id','root_values','parent_slots','query_slot')):
            raise ValueError('literal/computed matched scientific targets differ')
    receipt = bounded._json(Path(other['run_dir'])/COMPLETION)
    return dict(config=other, result=result, receipt=receipt,
        matched_literal_ids=[old_pairs[row['format_pair_id']]['id'] for row in records])


def _transfer_predict(entry, x, bundle, source_hash):
    if Path(entry['path']).stat().st_size != entry['bytes'] or bounded._sha(entry['path']) != entry['sha256']:
        raise ValueError('literal transfer parameter artifact differs')
    if entry['bytes'] > 256*1024**2: raise ValueError('bounded literal parameter bank required')
    payload = bounded._bytes(entry['path'], 256*1024**2)
    if hashlib.sha256(payload).hexdigest() != entry['sha256']: raise ValueError('transfer bytes changed')
    with np.load(io.BytesIO(payload), allow_pickle=False) as saved:
        if str(saved['config_hash'].item()) != source_hash: raise ValueError('literal parameter config differs')
        active = saved['active_columns']
        if not np.array_equal(active, np.flatnonzero(bundle.mask.all(axis=0))): raise ValueError('transfer target columns differ')
        metadata = json.loads(saved['model_metadata'].tobytes())
        model = from_parameters(metadata, {key:saved[key] for key in ('mean','scale','coef','intercept','weighted_feature_mean','weighted_target_mean')})
    predicted = model.predict(x); result = np.full(bundle.y.shape, np.nan)
    result[:, active] = predicted[:, :len(active)]
    return result


def _save_transfer(path,scores,case_ids,source_ids,source_sha):
    arrays={'case_ids':np.asarray(case_ids),'scores':scores,'source_case_ids':np.asarray(source_ids),
            'source_sha256':np.asarray(source_sha)}
    if path.exists():
        payload=bounded._bytes(path,256*1024**2)
        with np.load(io.BytesIO(payload),allow_pickle=False) as saved:
            if set(saved.files)!=set(arrays) or any(not np.array_equal(saved[k],v,equal_nan=True) if v.dtype.kind in 'fc' else not np.array_equal(saved[k],v) for k,v in arrays.items()):
                raise ValueError('saved literal transfer identities or predictions differ')
    else:
        stream=io.BytesIO();np.savez(stream,**arrays);original.immutable(path,stream.getvalue())


def run(config):
    from .confidence import _run_lock
    from sklearn.feature_extraction.text import HashingVectorizer
    from threadpoolctl import threadpool_limits
    source, checked, selected, cases, records = _metadata(config, scheduled=True)
    bundles, support, eligible, train, donors, qualified = _bundles(records, cases)
    out = Path(config['run_dir']); out.mkdir(parents=True, exist_ok=True)
    with _run_lock(out):
        if (out/COMPLETION).exists():
            completed=completed_result(config);_logging_summary(config,completed)
            return completed
        transfer = _transfer(config, checked, records)
        capture_folder = Path(checked['config']['run_dir'])
        registration = dict(evaluation_role=ROLE, config=config, config_hash=digest(config), analysis_source=source,
            protocol=protocol(), capture_completion=original._artifact(capture_folder/'completion_manifest_v1.json'),
            selected_case_ids=[r['id'] for r in records], model=checked['model'], model_revision=checked['model_revision'],
            panel=config['panel'], source_form=records[0]['source_form'], primary_layer=config['primary_layer'],
            transfer_completion=original._artifact(Path(transfer['config']['run_dir'])/COMPLETION) if transfer else None,
            new_model_queries=0, generated_holdouts_opened=False, limitation=LIMITATION)
        original.immutable(out/'registration.json', original._json_bytes(registration))
        vectors = _load(checked, selected); fits=[]; artifacts={}; summaries={}; replays=0; transfer_rows=0
        dev=np.flatnonzero(~train); train_rows=[r for r,keep in zip(records,train) if keep]
        threads=int(os.environ.get('SLURM_CPUS_PER_TASK','4'))
        if threads<1: raise ValueError('positive CPU allocation required')
        started=time.monotonic()
        with threadpool_limits(limits=threads):
            for site_index,site in enumerate(SITES):
                bundle=bundles[site]; dev_bundle=target.subset(bundle,dev)
                grouped=defaultdict(list); selection=defaultdict(lambda:defaultdict(list))
                surface=HashingVectorizer(analyzer='char',ngram_range=(3,8),n_features=checked['feature_shape'][-1],
                    alternate_sign=True,norm=None,dtype=np.float64).transform([c['visible_prefixes'][site_index] for c in cases]).toarray()
                banks=[('hidden',layer,vectors[:,site_index,i]) for i,layer in enumerate(checked['layers'])]+[('surface',-1,surface)]
                for backend,layer,x in banks:
                    for seed in SEEDS:
                        weights=original.group_weights(train_rows,seed).astype(np.float64); donor=donors[seed]
                        name=original._name(backend,layer,site,seed); path=out/(name+'.npz')
                        model,active,scores,shuffled=original._fit_bank(path,x,bundle,train,weights,donor,digest(config))
                        replays+=len(records); artifacts[name]=original._artifact(path)
                        prior=original._prior(bundle,train,weights)
                        methods=dict(direct=scores,categorical_value_derived=target.derived_categorical_relations(bundle,scores),
                            structural_position_prior=prior)
                        if transfer:
                            transferred=_transfer_predict(transfer['receipt']['artifacts'][name],x,bundle,digest(transfer['config']))
                            transfer_path=out/(name+'_literal_transfer.npz')
                            _save_transfer(transfer_path,transferred,bundle.case_ids,transfer['matched_literal_ids'],transfer['receipt']['artifacts'][name]['sha256'])
                            artifacts[name+'_literal_transfer']=original._artifact(transfer_path);transfer_rows+=len(records)
                            methods['literal_transfer_direct']=transferred
                            methods['literal_transfer_categorical']=target.derived_categorical_relations(bundle,transferred)
                        measured={}
                        control=target.permute_bundle(bundle,donor)
                        for split,indices in [('train',np.flatnonzero(train)),('development',dev)]:
                            sub=target.subset(bundle,indices)
                            measured[split]={method:target.metrics(sub,value[indices],eligible_boolean_indices=eligible,
                                training_support_info=support[site],include_per_group=False) for method,value in methods.items()}
                            measured[split]['coherent_shuffle_task']=target.metrics(target.subset(control,indices),shuffled[indices],
                                eligible_boolean_indices=eligible,include_per_group=False)
                        metadata=model.metadata;metadata.pop('training_ids',None)
                        fits.append(dict(name=name,backend=backend,layer=layer,site=site,seed=seed,model=metadata,
                            metrics=measured,factorizations=1,artifact=str(path),
                            weighted_training_target_mean_max_abs_difference=float(np.max(abs(
                                np.average(bundle.y[train][:,active],axis=0,weights=weights)
                                -np.average(control.y[train][:,active],axis=0,weights=weights)))),
                            control_train_marginals_preserved=bool(np.array_equal(np.sort(bundle.y[train],axis=0),np.sort(control.y[train],axis=0))),
                            control_development_marginals_preserved=bool(np.array_equal(np.sort(bundle.y[dev],axis=0),np.sort(control.y[dev],axis=0)))))
                        if layer==config['primary_layer'] or backend=='surface':
                            for method,value in methods.items():
                                if backend=='surface' and method=='structural_position_prior':continue
                                key=method if backend=='hidden' else 'source_'+method
                                correct=target.task_correctness(dev_bundle,value[dev],eligible)
                                grouped[key].append(correct)
                                for metric,array in _selection(dev_bundle,value[dev],[records[i] for i in dev]).items():selection[key][metric].append(array)
                        write_json(out/'progress.json',dict(status='started',fits=len(fits),planned_fits=45,new_model_queries=0))
                        print(f'overnight relationship {config["panel"]} {name}',flush=True)
                correctness={name:dict(algebraic=np.mean([v['algebraic_correct'] for v in values],axis=0),
                    graph=np.mean([v['whole_graph_correct'] for v in values],axis=0),truth=values[0]['algebraic_truth'],
                    families=values[0]['algebraic_families']) for name,values in grouped.items()}
                selections={name:{metric:np.mean(values,axis=0) for metric,values in fields.items()} for name,fields in selection.items()}
                summaries[str(site)]=_summary(dev_bundle,correctness,selections,[records[i] for i in dev],qualified)
        if len(fits)!=45 or replays!=45*len(records):raise ValueError('complete45-bank replay grid required')
        result=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),analysis_source=source,
            protocol=protocol(),panel=config['panel'],source_form=records[0]['source_form'],model=checked['model'],
            model_revision=checked['model_revision'],layers=checked['layers'],primary_layer=config['primary_layer'],
            cases=len(records),training_rows=int(train.sum()),development_rows=len(dev),
            factorizations=45,parameter_replay_rows=replays,literal_transfer_rows=transfer_rows,new_fits=45,
            feature_dimensions=checked['feature_shape'][-1],primary_training_support_qualified=qualified,
            training_support=support[3],summaries=summaries,fits=fits,
            runtime=dict(threads=threads,slurm_job_id=os.environ.get('SLURM_JOB_ID'),wall_seconds=time.monotonic()-started),
            source_model_prefill_cases=checked['summary']['model_prefill_cases'],new_model_queries=0,
            capture_completion=registration['capture_completion'],source_prefill_accounting='Shared union capture; do not sum across panel readouts.',
            runtime_scope='Readout fitting loop only; excludes input validation, target construction and feature-file loading.',
            generated_holdouts_opened=False,limitation=LIMITATION)
        return _finish(config,result,artifacts)


def _finish(config,result,artifacts):
    out=Path(config['run_dir']);path=out/'results_v1.json';current_runtime=original._runtime(result['runtime'])
    payload=original._json_bytes(result)
    if len(payload)>MAX_RESULT:raise ValueError('bounded overnight scientific result required')
    if path.exists():
        previous=json.loads(bounded._bytes(path,MAX_RESULT))
        original._runtime(previous['runtime'])
        if original._json_bytes({k:v for k,v in previous.items() if k!='runtime'})!=original._json_bytes({k:v for k,v in result.items() if k!='runtime'}):
            raise ValueError('partial overnight scientific result differs after exact replay')
        result=previous
    else:original.immutable(path,payload)
    original.immutable(config['report'],_report(result).encode())
    review=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),factorizations=45,
        parameter_replay_rows=result['parameter_replay_rows'],exact_parameter_replays=True,new_model_queries=0,generated_holdouts_opened=False)
    original.immutable(out/'audit.json',original._json_bytes(review))
    artifacts.update({key:original._artifact(path) for key,path in [('registration',out/'registration.json'),('results',out/'results_v1.json'),('report',Path(config['report'])),('audit',out/'audit.json')]})
    receipt=dict(status='complete_exploratory',evaluation_role=ROLE,schema_version=1,config_hash=digest(config),
        analysis_source=result['analysis_source'],factorizations=45,parameter_replay_rows=result['parameter_replay_rows'],
        literal_transfer_rows=result['literal_transfer_rows'],artifacts=artifacts,completion_runtime=current_runtime,
        new_model_queries=0,generated_holdouts_opened=False)
    original.immutable(out/COMPLETION,original._json_bytes(receipt))
    _logging_summary(config,result)
    return result


def _logging_summary(config,result):
    """A compact derived log mirror, published only after the scientific receipt."""
    folder=Path(config['run_dir'])
    value=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),
        model=result['model'],revision=result.get('model_revision'),panel=result['panel'],
        source_form=result['source_form'],cases=result['cases'],factorizations=45,
        parameter_replay_rows=result['parameter_replay_rows'],literal_transfer_rows=result['literal_transfer_rows'],
        scientific_completion=original._artifact(folder/COMPLETION),derived_logging_summary=True,
        report=config['report'],new_model_queries=0,generated_holdouts_opened=False,
        algebraic_methods={name:entry['score'] if entry else None for name,entry in result['summaries']['3']['algebraic']['methods'].items()},
        structural_methods={site:result['summaries'][site]['structural']['methods'] for site in ('7','8')})
    original.immutable(folder/'summary.json',original._json_bytes(value))


def completed_result(config):
    source,checked,_,_,records=_metadata(config)
    folder=Path(config['run_dir']);receipt=bounded._json(folder/COMPLETION)
    if (receipt.get('status')!='complete_exploratory' or receipt.get('evaluation_role')!=ROLE
            or receipt.get('schema_version')!=1
            or receipt.get('config_hash')!=digest(config) or receipt.get('analysis_source')!=source
            or receipt.get('factorizations')!=45 or receipt.get('parameter_replay_rows')!=45*len(records)
            or receipt.get('new_model_queries')!=0 or receipt.get('generated_holdouts_opened') is not False):
        raise ValueError('complete matching overnight readout receipt required')
    expected={original._name(backend,layer,site,seed):folder/(original._name(backend,layer,site,seed)+'.npz')
        for site in SITES for backend,layer in [('hidden',l) for l in checked['layers']]+[('surface',-1)] for seed in SEEDS}
    if 'transfer_from' in config:
        expected.update({name+'_literal_transfer':folder/(name+'_literal_transfer.npz') for name in list(expected)})
    expected.update(registration=folder/'registration.json',results=folder/'results_v1.json',report=Path(config['report']),audit=folder/'audit.json')
    if set(receipt.get('artifacts',{}))!=set(expected):raise ValueError('complete overnight artifact inventory required')
    for name,path in expected.items():
        if receipt['artifacts'][name]!=original._artifact(path):raise ValueError('overnight artifact checksum/size/path differs')
    registration=bounded._json(folder/'registration.json')
    if (registration.get('protocol')!=protocol() or registration.get('model')!=checked['model']
            or registration.get('model_revision')!=checked['model_revision']
            or registration.get('primary_layer')!=config['primary_layer']
            or registration.get('selected_case_ids')!=[row['id'] for row in records]
            or registration.get('capture_completion')!=original._artifact(Path(checked['config']['run_dir'])/'completion_manifest_v1.json')):
        raise ValueError('original source protocol/capture receipt differs')
    for entry in checked['chunks']:
        if bounded._sha(entry['path'])!=entry['sha256']:raise ValueError('original union capture chunk changed')
    transfer_rows=45*len(records) if 'transfer_from' in config else 0
    if receipt.get('literal_transfer_rows')!=transfer_rows:raise ValueError('literal transfer coverage differs')
    if 'transfer_from' in config:
        peer=bounded._json(config['transfer_from'],config['transfer_from_sha256'])
        if registration.get('transfer_completion')!=original._artifact(Path(peer['run_dir'])/COMPLETION):
            raise ValueError('original literal transfer receipt changed')
    payload=bounded._bytes(folder/'results_v1.json',MAX_RESULT)
    if hashlib.sha256(payload).hexdigest()!=receipt['artifacts']['results']['sha256']:raise ValueError('scientific bytes changed before parsing')
    result=json.loads(payload)
    expected_fits={name:str(path) for name,path in expected.items() if path.suffix=='.npz' and not name.endswith('_literal_transfer')}
    if (result.get('status')!='complete_exploratory' or result.get('evaluation_role')!=ROLE
            or result.get('config_hash')!=digest(config) or result.get('analysis_source')!=source
            or result.get('protocol')!=protocol() or result.get('panel')!=config['panel']
            or result.get('model')!=checked['model'] or result.get('model_revision')!=checked['model_revision']
            or result.get('primary_layer')!=config['primary_layer'] or result.get('cases')!=len(records)
            or result.get('factorizations')!=45 or result.get('parameter_replay_rows')!=45*len(records)
            or result.get('new_fits')!=45
            or result.get('source_model_prefill_cases')!=checked['summary']['model_prefill_cases']
            or result.get('capture_completion')!=registration['capture_completion']
            or result.get('literal_transfer_rows')!=transfer_rows or len(result.get('fits',[]))!=45
            or {fit['name']:fit['artifact'] for fit in result['fits']}!=expected_fits
            or result.get('new_model_queries')!=0 or result.get('generated_holdouts_opened') is not False):
        raise ValueError('original overnight scientific payload differs')
    return result


def audit(config):
    result=completed_result(config)
    saved=bounded._json(Path(config['run_dir'])/'audit.json')
    if (saved.get('status')!='passed' or saved.get('evaluation_role')!=ROLE or saved.get('config_hash')!=digest(config)
            or saved.get('factorizations')!=45 or saved.get('new_model_queries')!=0
            or saved.get('generated_holdouts_opened') is not False
            or saved.get('parameter_replay_rows')!=result['parameter_replay_rows'] or saved.get('exact_parameter_replays') is not True):
        raise ValueError('overnight exact parameter-replay audit differs')
    return dict(status='passed',evaluation_role=ROLE,factorizations=45,parameter_replay_rows=result['parameter_replay_rows'],
        literal_transfer_rows=result['literal_transfer_rows'],additional_fits=0,new_model_queries=0,generated_holdouts_opened=False)


def _report(result):
    lines=['# Overnight relationship readouts','',LIMITATION,'',
        f"Panel `{result['panel']}`, source form `{result['source_form']}`, model `{result['model']}`; {result['cases']:,} rows. Nominated primary layer {result['primary_layer']}. 45 factorizations, {result['parameter_replay_rows']:,} exact parameter-score row replays, zero additional model queries.",'',
        '## Fixed algebraic comparison after initialization','',
        '| Method | Four-family macro balanced accuracy |','|---|---:|']
    alg=result['summaries']['3']['algebraic']
    for name,scored in alg['methods'].items():lines.append(f"| {name} | {100*scored['score']:.3f}% |" if scored else f'| {name} | undefined |')
    lines+=['',f"Interval status: {alg['status']}. Fixed TRAIN support qualified: {result['primary_training_support_qualified']}.",'',
        '| Direct minus comparator | Percentage points | Conditional component 95% |','|---|---:|---|']
    for name,item in alg.get('comparisons',{}).items():
        ci=item['conditional_group_bootstrap_95'];lines.append(f"| {name} | {100*item['mean']:+.3f} | {None if ci is None else [100*v for v in ci]} |")
    for site in (7,8):
        lines+=['',f'## Complete parent graph at site {site}','', '| Method | Whole-graph accuracy |','|---|---:|']
        for name,value in result['summaries'][str(site)]['structural']['methods'].items():lines.append(f'| {name} | {100*value:.3f}% |')
    lines+=['','## Query-conditioned probes','','| Site | Query | Method | Whole graph | Queried value | Other values | Queried parent | Other parents |','|---|---:|---|---:|---:|---:|---:|---:|']
    for site,summary in result['summaries'].items():
        for query,methods in summary['per_query'].items():
            for name,item in methods.items():
                if name not in ('direct','source_direct','literal_transfer_direct'):continue
                selection=item.get('query_selection',{});graph=item['whole_graph_accuracy']
                percentage=lambda value:'undefined' if value is None else f'{100*value:.3f}%'
                lines.append(f"| {site} | {query} | {name} | {percentage(graph)} | {percentage(selection['queried_value_correct'])} | {percentage(selection['unqueried_value_correct'])} | {percentage(selection.get('queried_parent_correct'))} | {percentage(selection.get('unqueried_parent_correct'))} |")
    lines+=['','Query-conditioned values are descriptive probe correctness, not generated-answer correctness. Component summaries, all captured layer/site fits, coherent controls and matched literal-transfer evidence are retained in the pinned result JSON.','']
    return '\n'.join(lines)
