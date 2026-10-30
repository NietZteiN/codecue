"""Posthoc DEV diagnostics from pinned saved scores, never model parameters.

The original numerical replay proofs remain authoritative. This audit opens only
identity/scores/random_scores NPZ members, verifies original metrics exactly,
then retains prediction-only DEV banks for independently repeatable diagnostics.
"""
from __future__ import annotations

from collections import defaultdict
import io
import json
from itertools import combinations
import os
from pathlib import Path
import zipfile

import numpy as np

from . import relationship_capture as bounded
from . import overnight_relationship_capture as durable
from . import relationship_readouts as publication
from . import schedule_readouts as original
from . import schedule_targets as target
from .datasets import digest
from .discovery_readouts import group_weights
from .weighted_ridge import _array_hash

ROLE = 'discovery_schedule_score_review_v1'
METHODS = ('direct', 'training_prior', 'random_prefix_control')
FAMILIES = ('current_definition', 'current_version', 'copy_parent')
QUERY_FAMILIES = ('current_definition', 'current_version')
SITES = (3, 7, 8)
SEEDS = (17, 29, 43)
MAX_JSON = 64 * 1024**2
COMPLETION = 'completion_manifest_v1.json'
PROFILES = {
    'meta-llama/Llama-3.1-8B-Instruct': ('llama8b', '0e9e39f249a16976918f6564b8830bc894c89659', [8,16,24,31], 4096),
    'codellama/CodeLlama-34b-Instruct-hf': ('codellama34b', 'd4c1c474abcacd32d2a6eda45f9811d38c83e93d', [12,24,36,47], 8192),
}
LIMITATIONS = [
    'Posthoc discovery analysis after examining the original aggregate results; this is neither an untouched test nor a reliability-gate rescue.',
    'Five unequal DEV graph families are the structural units. Numeric, lexical, body-query and weighting-seed relatives are dependent; no new confidence interval is claimed.',
    'Every fixed target slot is compared with itself across the four queries on an identical assignment body. Query effects do not compare different queried targets.',
    'Site7 is a pre-query placebo; site8 observes the explicit query. Any site7 disagreement or margin difference is retained, including numerical or padding effects.',
    'Joint scalar-version/definition/parent correctness describes different decoder tasks; correct version integers do not establish correct bindings or a causal state-tracking algorithm.',
    'Random-prefix controls are separate sham tasks with different class marginals and potentially unlawful joint graphs. Their diagnostic results do not establish matched task difficulty.',
    'Scores are uncalibrated ridge outputs; margins and top scores are descriptive. No threshold, layer, seed, class or subgroup is selected using this analysis.',
    'No model/tokenizer/activation/coefficient arrays are loaded, no parameters are reapplied, and no model or probe is fitted.',
]


def _json_bytes(value):
    return publication._json_bytes(value)


def _same(left, right):
    return _json_bytes(left) == _json_bytes(right)


def _sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _config(config):
    required = {'evaluation_role', 'readout_configs', 'declared_plan',
                'declared_plan_sha256', 'run_dir', 'report'}
    if (not isinstance(config, dict) or set(config) != required or config.get('evaluation_role') != ROLE
            or len(_json_bytes(config)) > 16*1024 or not _sha(config.get('declared_plan_sha256'))):
        raise ValueError('exact bounded posthoc schedule-score configuration required')
    sources = config['readout_configs']
    if (not isinstance(sources, list) or len(sources) != 2
            or any(not isinstance(item, dict) or set(item) != {'path', 'sha256'}
                   or not isinstance(item['path'], str) or not _sha(item['sha256']) for item in sources)):
        raise ValueError('two explicitly pinned original readout configurations required')
    paths = [bounded._safe(item['path']).resolve() for item in sources]
    for key in ('declared_plan', 'run_dir', 'report'):
        if not isinstance(config[key], str) or not config[key]: raise ValueError('explicit safe paths required')
        bounded._safe(config[key])
    if len(set(paths)) != 2: raise ValueError('duplicate source readout configurations excluded')
    out, report, plan = (Path(config[key]).resolve() for key in ('run_dir', 'report', 'declared_plan'))
    sources_ = paths+[plan]
    reserved = [out/name for name in ('registration.json', 'results_v1.json', 'audit.json',
                                     'summary.json', 'progress.json', COMPLETION,
                                     'prediction_replay_review_v1.json')]
    if (report.suffix != '.md' or report == out or report in out.parents
            or (out.exists() and not out.is_dir()) or (report.exists() and not report.is_file())
            or any(p == report or p in report.parents for p in reserved)
            or any(p in report.parents and p.suffix == '.npz' for p in report.parents if out in p.parents)
            or any(out == p or out in p.parents or p in out.parents
                   or report == p or report in p.parents or p in report.parents for p in sources_)):
        raise ValueError('posthoc outputs cannot overlap inputs or reserved artifacts')
    return config


def _pin(path):
    path = bounded._safe(path)
    if path.is_symlink() or not path.is_file(): raise ValueError('regular nonsymlink input artifact required')
    return dict(path=str(path), sha256=bounded._sha(path), bytes=path.stat().st_size)


def _read(path, expected=None, limit=MAX_JSON):
    payload = bounded._bytes(path, limit)
    import hashlib
    if expected is not None:
        checksum = expected if isinstance(expected, str) else expected['sha256']
        if hashlib.sha256(payload).hexdigest() != checksum: raise ValueError('metadata checksum differs')
        if isinstance(expected, dict) and ('bytes' in expected and len(payload) != expected['bytes']):
            raise ValueError('metadata byte count differs')
    value = json.loads(payload)
    if not isinstance(value, dict): raise ValueError('metadata object required')
    return value


def _source(config, scheduled):
    _config(config)
    if scheduled:
        bounded._slurm()
        return bounded._current_source(config)
    registration = _read(Path(config['run_dir'])/'registration.json')
    if registration.get('config') != config or registration.get('config_hash') != digest(config):
        raise ValueError('original posthoc source/configuration differs')
    source = registration['source']
    bounded._verify_source(config, source)
    return source


def matched_bodies(records, expected_bodies=None):
    """Group exact actual assignment bodies, preserving lexical/numeric identity."""
    if not isinstance(records, (list, tuple)) or not records:
        raise ValueError('nonempty DEV source records required')
    bodies, ids = {}, set()
    for index, row in enumerate(records):
        case = row.get('id'); query = row.get('query_slot')
        if not isinstance(case, str) or not case or case in ids:
            raise ValueError('unique ordered case IDs required')
        ids.add(case)
        lines = row.get('source', '').splitlines()
        if len(lines) != 9 or type(query) is not int or query not in range(4):
            raise ValueError('eight actual assignments and an explicit four-slot query required')
        if row.get('split') != 'development': raise ValueError('posthoc comparisons use DEV records only')
        expected_query = row.get('rename_map', {}).get(f'v{query}')
        if expected_query is not None and lines[-1].strip() != expected_query:
            raise ValueError('actual query and declared queried slot differ')
        key = digest('\n'.join(lines[:8]))
        group = row.get('component_id', row.get('cluster_id', row.get('template_id')))
        if not isinstance(group, str) or not group: raise ValueError('explicit graph family required')
        entry = bodies.setdefault(key, dict(body_id=key, body='\n'.join(lines[:8]), group=group, rows={}))
        if entry['group'] != group or entry['body'] != '\n'.join(lines[:8]) or query in entry['rows']:
            raise ValueError('duplicate queried slot or mixed graph identity in a matched body')
        entry['rows'][query] = index
    if any(set(body['rows']) != set(range(4)) for body in bodies.values()):
        raise ValueError('all four query variants are required for every exact matched body')
    if expected_bodies is not None and len(bodies) != expected_bodies:
        raise ValueError('expected complete matched-body inventory differs')
    return tuple(dict(body_id=body['body_id'], group=body['group'],
                      indices=tuple(body['rows'][q] for q in range(4)))
                 for _, body in sorted(bodies.items()))


def _metadata(config, scheduled):
    source = _source(config, scheduled)
    if bounded._sha(config['declared_plan']) != config['declared_plan_sha256']:
        raise ValueError('prospective posthoc plan changed')
    models = {}; pins = [_pin(config['declared_plan'])]
    for item in config['readout_configs']:
        cfg = _read(item['path'], item['sha256'], 16*1024)
        old_source, checked, records = original._metadata(cfg, scheduled=False)
        if cfg.get('evaluation_role') != original.ROLE or cfg.get('primary_layer') != 24:
            raise ValueError('original fixed readout configuration required')
        if checked['model'] not in PROFILES: raise ValueError('only the two completed cached model profiles are permitted')
        model, revision, layers, width = PROFILES[checked['model']]
        if (model in models or checked['model_revision'] != revision or checked['layers'] != layers
                or checked['feature_shape'] != [2016,3,4,width]
                or checked['dataset_sha256'] != '4021f720282fbd7b1344a4a92d5da02abf5269cd9b62d13eebbd5e40e2f4e287'):
            raise ValueError('original model/source/feature geometry differs')
        folder = Path(cfg['run_dir']); receipt = _read(folder/COMPLETION)
        if (receipt.get('evaluation_role') != original.ROLE or receipt.get('status') != 'complete_exploratory'
                or receipt.get('schema_version') != 1 or receipt.get('config_hash') != digest(cfg)
                or receipt.get('fit_source') != old_source or receipt.get('capture_source') != checked['source']
                or (receipt.get('fit_banks'), receipt.get('factorizations'), receipt.get('parameter_replay_rows')) != (45,45,90720)
                or receipt.get('new_model_queries') != 0 or receipt.get('generated_holdouts_opened') is not False):
            raise ValueError('completed original 45-bank readout receipt required')
        expected = {original._name(backend, layer, site, seed): folder/(original._name(backend, layer, site, seed)+'.npz')
                    for site in SITES for backend, layer in [('hidden', l) for l in layers]+[('surface',-1)] for seed in SEEDS}
        expected.update(registration=folder/'registration.json', results=folder/'results_v1.json',
                        summary=folder/'summary.json', audit=folder/'audit.json', report=Path(cfg['report']))
        inventory = receipt.get('artifacts', {})
        if set(inventory) != set(expected): raise ValueError('exact original 50-artifact inventory required')
        for name, path in expected.items():
            entry = inventory[name]
            if (not isinstance(entry, dict) or set(entry) != {'path','sha256','bytes'}
                    or Path(entry['path']).resolve() != path.resolve() or not _sha(entry['sha256'])
                    or type(entry['bytes']) is not int or not 0 < entry['bytes'] <= 512*1024**2):
                raise ValueError('original artifact inventory path/hash/size differs')
        proof = _read(folder/'parameter_replay_review_v1.json')
        if (proof.get('status') != 'passed' or proof.get('evaluation_role') != original.ROLE
                or proof.get('config_hash') != digest(cfg) or proof.get('source_artifacts') != inventory
                or proof.get('fit_source') != old_source or proof.get('capture_source') != checked['source']
                or (proof.get('fit_banks'), proof.get('factorizations'), proof.get('parameter_replay_rows')) != (45,45,90720)
                or proof.get('new_fits') != 0 or proof.get('new_model_queries') != 0
                or proof.get('generated_holdouts_opened') is not False
                or not all(proof.get(k) is True for k in ('exact_saved_parameter_score_replays',
                    'all_real_and_control_scores_replayed','all_scientific_metrics_recomputed',
                    'train_support_and_control_marginals_recomputed'))):
            raise ValueError('completed original parameter/metric replay proof required before reading scores')
        metadata = {name: _read(expected[name], inventory[name]) for name in ('registration','results','summary','audit')}
        result = metadata['results']
        if any(value.get('evaluation_role')!=original.ROLE or value.get('config_hash')!=digest(cfg)
               or value.get('new_model_queries')!=0 or value.get('generated_holdouts_opened') is not False
               for value in metadata.values()):
            raise ValueError('original metadata discovery role and configuration differs')
        registration=metadata['registration']
        if (registration.get('config')!=cfg or registration.get('fit_source')!=old_source
                or registration.get('capture_source')!=checked['source']
                or registration.get('fixed_recipe')!=original.protocol()
                or metadata['audit'].get('status')!='passed'):
            raise ValueError('completed original registration and artifact audit required')
        if (result.get('evaluation_role') != original.ROLE or result.get('status') != 'complete_exploratory'
                or result.get('config_hash') != digest(cfg) or result.get('fit_source') != old_source
                or result.get('capture_source') != checked['source'] or result.get('model') != checked['model']
                or result.get('cases') != 2016 or result.get('training_rows') != 1320
                or result.get('development_rows') != 696 or result.get('protocol') != original.protocol()
                or not _same(result.get('target_columns'), list(target.COLUMNS))
                or result.get('new_model_queries') != 0 or result.get('generated_holdouts_opened') is not False):
            raise ValueError('original 232-column score schema and fixed fitting recipe required')
        if not _same(metadata['summary'],original._summary(result)):
            raise ValueError('original primary summary differs from its complete fixed metric grid')
        fit_map = {fit['name']: fit for fit in result['fits']}
        bank_names = {name for name, path in expected.items() if path.suffix == '.npz'}
        if len(result['fits']) != 45 or set(fit_map) != bank_names:
            raise ValueError('all original feature/site/seed score banks required')
        for name, fit in fit_map.items():
            if (fit['name'] != original._name(fit['backend'], fit['layer'], fit['site'], fit['seed'])
                    or Path(fit['artifact']).resolve() != expected[name].resolve()
                    or fit['factorizations'] != 1 or fit['exact_parameter_score_replay'] is not True):
                raise ValueError('original fit geometry/replay inventory differs')
        ids = tuple(row['id'] for row in records)
        if len(ids) != 2016 or len(set(ids)) != 2016:
            raise ValueError('exact unique ordered captured source IDs required')
        dev = np.flatnonzero([row['split'] == 'development' for row in records])
        dev_records = [records[i] for i in dev]
        bodies = matched_bodies(dev_records, expected_bodies=174)
        if len(dev) != 696 or len({r['component_id'] for r in dev_records}) != 5:
            raise ValueError('696 DEV cases in five canonical graph groups required')
        for body in bodies:
            cases = [checked['cases'][dev[index]] for index in body['indices']]
            for site_index in (0,1):
                if len({case['visible_prefixes'][site_index] for case in cases}) != 1:
                    raise ValueError('a matched pre-query prefix exposes queried identity or changed assignments')
        out, report = Path(config['run_dir']).resolve(), Path(config['report']).resolve()
        reserved_sources = [folder.resolve(), Path(checked['config']['run_dir']).resolve()]
        if any(out == p or out in p.parents or p in out.parents
               or report == p or report in p.parents or p in report.parents for p in reserved_sources):
            raise ValueError('posthoc outputs cannot overlap original capture/readout data')
        for name in ('registration','results','summary','audit'):
            pins.append(_pin(expected[name]))
        pins += [_pin(item['path']), _pin(folder/COMPLETION), _pin(folder/'parameter_replay_review_v1.json'),
                 _pin(cfg['capture_config']), _pin(Path(checked['config']['run_dir'])/COMPLETION),
                 _pin(Path(checked['config']['run_dir'])/'prepared_cases.jsonl'),
                 _pin(checked['config']['dataset']), _pin(Path(checked['config']['dataset']).with_suffix('.manifest.json'))]
        models[model] = dict(config=cfg, checked=checked, records=records, ids=ids, dev=dev,
            dev_records=dev_records, bodies=bodies, fit_map=fit_map, inventory=inventory,
            result=result, summary=metadata['summary'])
    if set(models) != {'llama8b','codellama34b'}: raise ValueError('both distinct cached model score studies required')
    if models['llama8b']['ids'] != models['codellama34b']['ids']:
        raise ValueError('both model score studies must align to the same ordered source cases')
    return source, models, pins


def preflight(config):
    source, models, pins = _metadata(config, scheduled=True)
    return dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), source=source,
        models=2, saved_score_banks=90, development_rows_per_bank=696,
        matched_development_bodies=174, graph_families=5, input_pins=pins,
        saved_score_arrays_opened=False, activation_arrays_opened=False,
        coefficient_arrays_opened=False, new_fits=0, new_model_queries=0, generated_holdouts_opened=False)


def load_score_bank(path, entry, bundle, control, train, weights, config_hash):
    """Read only three whitelisted NPZ members after whole-file SHA verification."""
    n, width = bundle.y.shape
    if len(bundle.case_ids)!=n or len(set(bundle.case_ids))!=n:
        raise ValueError('unique ordered source case IDs required')
    if _pin(path) != entry: raise ValueError('pinned original score bank changed')
    with zipfile.ZipFile(path) as archive:
        for name, maximum in (('identity.npy', 2*1024**2), ('scores.npy', n*width*8+1024),
                              ('random_scores.npy', n*width*8+1024)):
            try: info = archive.getinfo(name)
            except KeyError as exc: raise ValueError('required saved-score member missing') from exc
            if not 0 < info.file_size <= maximum: raise ValueError('bounded saved-score members required')
    with np.load(path, allow_pickle=False) as archive:
        identity_bytes = archive['identity']
        if identity_bytes.dtype != np.uint8 or identity_bytes.ndim != 1:
            raise ValueError('bounded UTF-8 identity byte vector required')
        identity = json.loads(identity_bytes.tobytes())
        scores = archive['scores'].copy(); random_scores = archive['random_scores'].copy()
    expected = dict(config_hash=config_hash, case_ids=list(bundle.case_ids),
        targets_sha256=_array_hash(bundle.y), mask_sha256=_array_hash(bundle.mask),
        control_sha256=_array_hash(control.y), train_mask_sha256=_array_hash(train),
        weights_sha256=_array_hash(weights))
    if (not isinstance(identity, dict) or set(identity) != set(expected)|{'features_sha256'}
            or not _sha(identity.get('features_sha256'))
            or any(identity.get(k) != v for k,v in expected.items())):
        raise ValueError('saved-score ordered case/target/training identity differs')
    active = bundle.mask.any(axis=0)
    for array in (scores, random_scores):
        if (array.dtype != np.float64 or array.shape != (n,width)
                or not np.isfinite(array[:,active]).all() or not np.isnan(array[:,~active]).all()):
            raise ValueError('exact finite/undefined saved-score geometry required')
    return scores, random_scores, identity


def predictions(bundle, scores):
    """Categorical decisions use finite fitted scores, never target masks as features."""
    scores = np.asarray(scores)
    if scores.shape != bundle.y.shape: raise ValueError('score/target geometry differs')
    n, heads = len(scores), len(target.HEADS)
    truth = np.full((n,heads), -1, dtype=np.int16)
    predicted = np.full_like(truth,-1); valid = np.zeros_like(truth,dtype=bool)
    margins = np.full((n,heads),np.nan); top = np.full_like(margins,np.nan)
    for h, spec in enumerate(target.HEADS):
        indices = list(spec['indices']); candidates = np.array(spec['candidates'],dtype=np.int16)
        y = bundle.y[:,indices]
        defined = (y.sum(axis=1)==1) & bundle.mask[:,indices].any(axis=1)
        valid[:,h] = defined
        truth[defined,h] = candidates[np.argmax(y[defined],axis=1)]
        values = scores[:,indices]; finite = np.isfinite(values)
        usable = finite.any(axis=1)
        ordered = np.sort(np.where(finite,values,-np.inf),axis=1)
        predicted[usable,h] = candidates[np.argmax(np.where(finite,values,-np.inf),axis=1)[usable]]
        top[usable,h] = ordered[usable,-1]
        two = finite.sum(axis=1)>=2
        margins[two,h] = ordered[two,-1]-ordered[two,-2]
    return dict(truth=truth, predicted=predicted, valid=valid,
                correct=valid & (truth==predicted), margin=margins, top_score=top)


def _group_point(indicator, valid, groups):
    per_group = {g: dict(n=int((valid & (groups==g)).sum()),
                         count=int(indicator[valid & (groups==g)].sum()))
                 for g in sorted(set(groups[valid]))}
    for value in per_group.values(): value['rate'] = value['count']/value['n']
    return dict(n=int(valid.sum()), count=int(indicator[valid].sum()),
        rate=float(indicator[valid].mean()) if valid.any() else None,
        group_macro_rate=float(np.mean([v['rate'] for v in per_group.values()])) if per_group else None,
        per_group=per_group)


def categorical_diagnostics(data, groups):
    groups = np.asarray(groups); heads = {}; whole = {}; flags = {}
    for h, spec in enumerate(target.HEADS):
        valid = data['valid'][:,h]; truth = data['truth'][:,h]; pred = data['predicted'][:,h]
        domain = list(spec['candidates']); decisions = [-1]+domain
        confusion = [[int((valid & (truth==a) & (pred==b)).sum()) for b in decisions] for a in domain]
        head = _group_point(data['correct'][:,h],valid,groups)
        head.update(family=spec['family'], truth_candidates=domain, prediction_candidates=decisions,
                    confusion_counts=confusion, missing_predictions=int((valid & (pred<0)).sum()))
        heads[spec['name']] = head
    for family in FAMILIES:
        indices = [h for h,spec in enumerate(target.HEADS) if spec['family']==family]
        valid = data['valid'][:,indices].all(axis=1); correct = data['correct'][:,indices].all(axis=1)
        flags[family] = (valid,correct)
        whole[family] = _group_point(correct,valid,groups)
    joints = {}
    for left,right in combinations(FAMILIES,2):
        defined = flags[left][0] & flags[right][0]
        states = {}
        for a,b in ((False,False),(False,True),(True,False),(True,True)):
            name = f'{left}_'+('correct' if a else 'wrong')+'__'+right+'_'+('correct' if b else 'wrong')
            states[name] = _group_point((flags[left][1]==a)&(flags[right][1]==b),defined,groups)
        joints[left+'__'+right] = states
    return dict(heads=heads,whole_families=whole,pair_joint_mass=joints)


def _query_count(queried, unqueried, groups, units_per_body=1):
    if queried.ndim != 1 or unqueried.shape != (len(queried),3):
        raise ValueError('each body must contribute one queried and three other-query decisions for the same target')
    def point(indices):
        n = len(indices); q=int(queried[indices].sum()); u=int(unqueried[indices].sum())
        if n%units_per_body: raise ValueError('complete fixed-target comparisons per matched body required')
        return dict(matched_bodies=n//units_per_body,comparison_units=n,
            queried_correct=q,queried_total=n,
            unqueried_correct=u,unqueried_total=3*n,
            queried_accuracy=q/n if n else None,unqueried_accuracy=u/(3*n) if n else None,
            effect=q/n-u/(3*n) if n else None)
    groups=np.asarray(groups); result=point(np.arange(len(queried)))
    per_group={g:point(np.flatnonzero(groups==g)) for g in sorted(set(groups))}
    result.update(per_group=per_group,group_macro_effect=float(np.mean([v['effect'] for v in per_group.values()])) if per_group else None)
    return result


def query_effects(data, bodies):
    """Compare each fixed target head across its body's four queried variables."""
    results={}
    for family in QUERY_FAMILIES:
        slots={}; pooled_q=[];pooled_u=[];pooled_g=[]
        for slot in range(4):
            head=next(h for h,spec in enumerate(target.HEADS) if spec['name']==f'{family}/{slot}')
            q=[];u=[];groups=[]
            for body in bodies:
                rows=list(body['indices'])
                if not data['valid'][rows,head].all() or len(set(data['truth'][rows,head].tolist()))!=1:
                    raise ValueError('matched queries must share a defined fixed-target truth')
                correct=data['correct'][rows,head]
                q.append(bool(correct[slot]));u.append([bool(correct[j]) for j in range(4) if j!=slot]);groups.append(body['group'])
            slots[str(slot)]=_query_count(np.asarray(q),np.asarray(u,dtype=bool),groups)
            pooled_q.extend(q);pooled_u.extend(u);pooled_g.extend(groups)
        results[family]=dict(fixed_target_slots=slots,
            pooled_fixed_target_comparisons=_query_count(np.asarray(pooled_q),np.asarray(pooled_u,dtype=bool),pooled_g,units_per_body=4),
            interpretation='Within each actual assignment body, hold target slot fixed while varying only queried variable.')
    return results


def prefix_disagreements(data,bodies):
    result={}
    for h,spec in enumerate(target.HEADS):
        prediction_changes=0; margin_changes=0; top_changes=0; undefined_margins=0
        margin_spans=[];top_spans=[]
        for body in bodies:
            rows=list(body['indices'])
            prediction_changes+=int(len(set(data['predicted'][rows,h].tolist()))>1)
            margins=data['margin'][rows,h];tops=data['top_score'][rows,h]
            if np.isfinite(margins).all():
                span=float(np.max(margins)-np.min(margins));margin_spans.append(span);margin_changes+=int(span!=0)
            else: undefined_margins+=1
            if np.isfinite(tops).all():
                span=float(np.max(tops)-np.min(tops));top_spans.append(span);top_changes+=int(span!=0)
        result[spec['name']]=dict(matched_bodies=len(bodies),
            prediction_disagreement_bodies=prediction_changes,margin_disagreement_bodies=margin_changes,
            top_score_disagreement_bodies=top_changes,undefined_top_two_margin_bodies=undefined_margins,
            maximum_margin_span=max(margin_spans) if margin_spans else None,
            maximum_top_score_span=max(top_spans) if top_spans else None,
            scope='All sites retained; sites3/7 are pre-query placebos, site8 observes the query.')
    return result


def _diagnose(data,groups,bodies):
    return dict(categorical=categorical_diagnostics(data,groups),
                fixed_target_query_effects=query_effects(data,bodies),
                query_variant_prediction_disagreements=prefix_disagreements(data,bodies))


def _save_predictions(path,identity,records,bodies,methods):
    body_ids=['']*len(records)
    for body in bodies:
        for i in body['indices']: body_ids[i]=body['body_id']
    arrays=dict(identity=np.frombuffer(_json_bytes(identity),dtype=np.uint8),
        case_ids=np.array([r['id'] for r in records]),group_ids=np.array([r['component_id'] for r in records]),
        query_slots=np.array([r['query_slot'] for r in records],dtype=np.int8),body_ids=np.array(body_ids),
        methods=np.array(METHODS),heads=np.array([head['name'] for head in target.HEADS]))
    for field in ('truth','predicted','valid','correct','margin','top_score'):
        arrays[field]=np.stack([methods[method][field] for method in METHODS],axis=1)
    stream=io.BytesIO();np.savez_compressed(stream,**arrays)
    publication.immutable(path,stream.getvalue())


def _read_predictions(path,entry,identity,records,bodies):
    if _pin(path)!=entry: raise ValueError('posthoc prediction bank changed')
    n=len(records)
    with np.load(path,allow_pickle=False) as bank:
        if (json.loads(bank['identity'].tobytes())!=identity
                or bank['case_ids'].tolist()!=[r['id'] for r in records]
                or bank['group_ids'].tolist()!=[r['component_id'] for r in records]
                or bank['query_slots'].tolist()!=[r['query_slot'] for r in records]
                or bank['methods'].tolist()!=list(METHODS)
                or bank['heads'].tolist()!=[head['name'] for head in target.HEADS]):
            raise ValueError('posthoc prediction bank case/schema identity differs')
        expected_body=['']*n
        for body in bodies:
            for i in body['indices']: expected_body[i]=body['body_id']
        if bank['body_ids'].tolist()!=expected_body: raise ValueError('posthoc body membership differs')
        arrays={field:bank[field].copy() for field in ('truth','predicted','valid','correct','margin','top_score')}
    if any(a.shape!=(n,3,12) for a in arrays.values()): raise ValueError('posthoc prediction geometry differs')
    if (arrays['valid'].dtype!=np.bool_ or arrays['correct'].dtype!=np.bool_
            or arrays['truth'].dtype.kind not in 'iu' or arrays['predicted'].dtype.kind not in 'iu'
            or not np.array_equal(arrays['correct'],arrays['valid']&(arrays['truth']==arrays['predicted']))):
        raise ValueError('posthoc correctness does not follow preserved predictions')
    if (arrays['margin'].dtype!=np.float64 or arrays['top_score'].dtype!=np.float64
            or np.isinf(arrays['margin']).any() or np.isinf(arrays['top_score']).any()
            or np.any(arrays['margin'][np.isfinite(arrays['margin'])]<0)):
        raise ValueError('finite-or-undefined nonnegative score margins required')
    for h,spec in enumerate(target.HEADS):
        valid=arrays['valid'][:,:,h]
        if (not np.isin(arrays['predicted'][:,:,h],[-1,*spec['candidates']]).all()
                or not np.isin(arrays['truth'][:,:,h][valid],spec['candidates']).all()
                or np.any(arrays['truth'][:,:,h][~valid]!=-1)):
            raise ValueError('predictions and truths must retain declared categorical domains')
    return {method:{field:array[:,m] for field,array in arrays.items()} for m,method in enumerate(METHODS)}


def _summary(result):
    points={}
    for model in ('llama8b','codellama34b'):
        points[model]={}
        for backend,layer in (('hidden',24),('surface',-1)):
            points[model][backend]={}
            for site in (7,8):
                points[model][backend][str(site)]={}
                for method in METHODS:
                    points[model][backend][str(site)][method]={}
                    fits=[c for c in result['cells'] if c['model']==model and c['backend']==backend
                          and c['layer']==layer and c['site']==site]
                    if len(fits)!=3 or {fit['seed'] for fit in fits}!=set(SEEDS):
                        raise ValueError('all three fixed seeds required for primary posthoc summary')
                    for family in QUERY_FAMILIES:
                        cells=[fit['methods'][method]['fixed_target_query_effects'][family]['pooled_fixed_target_comparisons'] for fit in fits]
                        points[model][backend][str(site)][method][family]=dict(
                            effect=float(np.mean([c['effect'] for c in cells])),
                            group_macro_effect=float(np.mean([c['group_macro_effect'] for c in cells])),
                            seeds=list(SEEDS),matched_bodies_per_seed=174,fixed_target_comparisons_per_seed=696)
    return dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=result['config_hash'],
        score_banks=90,saved_score_rows_checked=181440,development_rows_per_bank=696,
        development_prediction_rows=62640,matched_bodies=174,graph_groups=5,
        primary=points,new_fits=0,new_model_queries=0,parameters_reapplied=0,
        activation_arrays_opened=False,coefficient_arrays_opened=False,
        generated_holdouts_opened=False,limitations=LIMITATIONS)


def verify_original_metrics(bundle,control,train,weights,dev,real,random,fit):
    """Check every original metric using saved scores and source-only target labels."""
    dev_bundle=target.subset(bundle,dev);dev_control=target.subset(control,dev)
    prior=original._prior(bundle,train,weights)
    verified=dict(direct=original.metrics(dev_bundle,real[dev],original._train_support(bundle,train)),
        training_prior=original.metrics(dev_bundle,prior[dev],original._train_support(bundle,train)),
        random_prefix_control=original.metrics(dev_control,random[dev],original._train_support(control,train)))
    if not _same(verified,fit['metrics']):
        raise ValueError('saved scores do not exactly reproduce original scientific metrics')
    return prior


def _report(result):
    summary=_summary(result)
    lines=['# Posthoc saved-score and fixed-target query diagnostics','',
        'All 90 completed parameter banks were read only through their saved identity and score arrays. Original metrics reproduce exactly; no parameters were applied or fitted.',
        '', 'The table retains layer24 for both models and the matched surface baseline. Site7 precedes the query; site8 observes it. Effects hold each target slot fixed across the four queries on an identical assignment body.', '',
        '| Model | Backend | Site | Method | Current-definition effect (pp) | Equal-graph effect (pp) | Current-version effect (pp) | Equal-graph effect (pp) |',
        '|---|---|---:|---|---:|---:|---:|---:|']
    for model in ('llama8b','codellama34b'):
        for backend in ('hidden','surface'):
            for site in ('7','8'):
                for method in METHODS:
                    points=summary['primary'][model][backend][site][method]
                    a,b=points['current_definition'],points['current_version']
                    lines.append(f"| {model} | {backend} | {site} | {method} | {100*a['effect']:.3f} | {100*a['group_macro_effect']:.3f} | {100*b['effect']:.3f} | {100*b['group_macro_effect']:.3f} |")
    lines+=['','Every layer, seed, site, fixed target slot, confusion matrix, joint-correctness mass, pre-query prediction disagreement and graph denominator remains in results_v1.json. Prediction-only DEV banks retain aligned case IDs, truths, decisions and uncalibrated margins.','']
    lines+=['- '+text for text in LIMITATIONS]
    return '\n'.join(lines)+'\n'


def run(config):
    from .confidence import _run_lock
    source,models,pins=_metadata(config,scheduled=True)
    out=Path(config['run_dir']);out.mkdir(parents=True,exist_ok=True)
    with _run_lock(out):
        if (out/COMPLETION).exists():
            previous=completed_result(config)
            if previous['source']!=source: raise ValueError('completed score audit belongs to another frozen source')
            durable._journal(out/'progress.json',dict(status='complete',score_banks=90,planned_banks=90,
                new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
            return previous
        if not (out/'registration.json').exists() and any(out.glob('predictions_*.npz')):
            raise ValueError('orphan prediction banks require original registration')
        registration=dict(evaluation_role=ROLE,config=config,config_hash=digest(config),source=source,
            input_pins=pins,new_fits=0,new_model_queries=0,parameters_reapplied=0,
            activation_arrays_opened=False,coefficient_arrays_opened=False,generated_holdouts_opened=False)
        publication.immutable(out/'registration.json',_json_bytes(registration))
        cells=[];artifacts={};score_pins=[]
        for model,data in sorted(models.items()):
            records=data['records'];train=np.array([row['split']=='train' for row in records]);dev=data['dev']
            train_rows=[row for row,use in zip(records,train) if use];groups=np.array([row['component_id'] for row in data['dev_records']])
            bundles={site:target.targets(records,site) for site in SITES}
            controls={(site,seed):target.control_targets(records,site,seed) for site in SITES for seed in SEEDS}
            for name,fit in sorted(data['fit_map'].items()):
                site,seed=fit['site'],fit['seed'];bundle=bundles[site]
                control=controls[site,seed]
                weights=group_weights(train_rows,seed).astype(np.float64)
                entry=data['inventory'][name]
                real,random,identity=load_score_bank(fit['artifact'],entry,bundle,control,train,weights,digest(data['config']))
                dev_bundle=target.subset(bundle,dev);dev_control=target.subset(control,dev)
                prior=verify_original_metrics(bundle,control,train,weights,dev,real,random,fit)
                methods=dict(direct=predictions(dev_bundle,real[dev]),training_prior=predictions(dev_bundle,prior[dev]),
                             random_prefix_control=predictions(dev_control,random[dev]))
                prediction_identity=dict(evaluation_role=ROLE,config_hash=digest(config),model=model,
                    bank_name=name,input_bank=entry,original_score_identity_sha256=digest(identity),
                    original_case_ids_sha256=digest(identity['case_ids']),
                    opaque_original_feature_sha256=identity['features_sha256'])
                path=out/f'predictions_{model}_{name}.npz'
                _save_predictions(path,prediction_identity,data['dev_records'],data['bodies'],methods)
                artifact=_pin(path);artifacts[model+'_'+name]=artifact;score_pins.append(entry)
                saved=_read_predictions(path,artifact,prediction_identity,data['dev_records'],data['bodies'])
                cell=dict(model=model,name=name,backend=fit['backend'],layer=fit['layer'],site=site,seed=seed,
                    original_metrics_exact=True,original_score_bank=entry,prediction_bank=artifact,
                    prediction_identity=prediction_identity,
                    margin_definition='Unsigned gap between the two highest finite class scores; no target conditioning.',
                    methods={method:_diagnose(saved[method],groups,data['bodies']) for method in METHODS})
                cells.append(cell)
                durable._journal(out/'progress.json',dict(status='running',score_banks=len(cells),planned_banks=90,
                    new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
                print(f'posthoc score audit {model} {name}',flush=True)
        if len(cells)!=90: raise ValueError('all 90 fixed original score banks required')
        result=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
            models=2,score_banks=90,development_rows_per_bank=696,matched_bodies=174,graph_groups=5,
            saved_score_rows_checked=181440,development_prediction_rows=62640,
            original_metrics_exact=True,cells=cells,input_pins=pins+score_pins,
            categorical_schema=[dict(spec) for spec in target.HEADS],
            new_fits=0,new_model_queries=0,parameters_reapplied=0,
            activation_arrays_opened=False,coefficient_arrays_opened=False,
            generated_holdouts_opened=False,limitations=LIMITATIONS)
        publication.immutable(out/'results_v1.json',_json_bytes(result))
        publication.immutable(out/'summary.json',_json_bytes(_summary(result)))
        publication.immutable(config['report'],_report(result).encode())
        audit_value=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),score_banks=90,
            original_metrics_exact=True,prediction_banks_reopened_and_checked=True,
            activation_arrays_opened=False,coefficient_arrays_opened=False,parameters_reapplied=0,
            new_fits=0,new_model_queries=0,generated_holdouts_opened=False)
        publication.immutable(out/'audit.json',_json_bytes(audit_value))
        artifacts.update({name:_pin(path) for name,path in [('registration',out/'registration.json'),
            ('results',out/'results_v1.json'),('summary',out/'summary.json'),('audit',out/'audit.json'),('report',Path(config['report']))]})
        receipt=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
            score_banks=90,artifacts=artifacts,new_fits=0,new_model_queries=0,parameters_reapplied=0,
            generated_holdouts_opened=False)
        publication.immutable(out/COMPLETION,_json_bytes(receipt))
        durable._journal(out/'progress.json',dict(status='complete',score_banks=90,planned_banks=90,
            new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        return result


def completed_result(config):
    source=_source(config,scheduled=False);out=Path(config['run_dir'])
    receipt=_read(out/COMPLETION)
    if (receipt.get('evaluation_role')!=ROLE or receipt.get('status')!='complete_exploratory'
            or receipt.get('config_hash')!=digest(config) or receipt.get('source')!=source
            or receipt.get('score_banks')!=90 or receipt.get('new_fits')!=0
            or receipt.get('new_model_queries')!=0 or receipt.get('parameters_reapplied')!=0
            or receipt.get('generated_holdouts_opened') is not False):
        raise ValueError('complete matching posthoc score-review receipt required')
    inventory=receipt.get('artifacts',{})
    expected={model+'_'+original._name(backend,layer,site,seed):
        out/f'predictions_{model}_{original._name(backend,layer,site,seed)}.npz'
        for model,_,layers,_ in PROFILES.values() for site in SITES
        for backend,layer in [('hidden',l) for l in layers]+[('surface',-1)] for seed in SEEDS}
    expected.update(registration=out/'registration.json',results=out/'results_v1.json',
                    summary=out/'summary.json',audit=out/'audit.json',report=Path(config['report']))
    if set(inventory)!=set(expected): raise ValueError('ninety prediction banks and five exact metadata artifacts required')
    for name,path in expected.items():
        if inventory[name]!=_pin(path): raise ValueError('immutable posthoc output artifact changed')
    result=_read(out/'results_v1.json',inventory['results'])
    if (result.get('evaluation_role')!=ROLE or result.get('config_hash')!=digest(config)
            or result.get('source')!=source or len(result.get('cells',[]))!=90
            or result.get('score_banks')!=90 or result.get('new_fits')!=0
            or result.get('new_model_queries')!=0 or result.get('parameters_reapplied')!=0
            or result.get('generated_holdouts_opened') is not False):
        raise ValueError('completed posthoc scientific result differs')
    return result


def audit(config):
    """Recompute diagnostics from prediction-only outputs; never reopen input NPZs."""
    result=completed_result(config)
    # Original source records are metadata; score/parameter and activation banks are not reopened.
    _,models,_=_metadata(config,scheduled=False)
    expected={(model,original._name(backend,layer,site,seed))
        for model,data in models.items() for site in SITES
        for backend,layer in [('hidden',l) for l in data['checked']['layers']]+[('surface',-1)] for seed in SEEDS}
    observed=set()
    source_targets={}
    for model,data in models.items():
        bundles={site:target.targets(data['records'],site) for site in SITES}
        controls={(site,seed):target.control_targets(data['records'],site,seed) for site in SITES for seed in SEEDS}
        source_targets[model]=(bundles,controls)
    for cell in result['cells']:
        key=(cell['model'],cell['name'])
        if key not in expected or key in observed: raise ValueError('undeclared or duplicate posthoc cell')
        observed.add(key);data=models[cell['model']]
        if (cell['original_score_bank']!=data['inventory'][cell['name']]
                or cell['prediction_identity'].get('model')!=cell['model']
                or cell['prediction_identity'].get('bank_name')!=cell['name']
                or cell['prediction_identity'].get('input_bank')!=cell['original_score_bank']
                or cell['prediction_identity'].get('config_hash')!=digest(config)
                or cell['prediction_identity'].get('evaluation_role')!=ROLE):
            raise ValueError('posthoc prediction provenance differs from completed original bank')
        methods=_read_predictions(cell['prediction_bank']['path'],cell['prediction_bank'],cell['prediction_identity'],
                                  data['dev_records'],data['bodies'])
        bundles,controls=source_targets[cell['model']]
        for method in METHODS:
            source_bundle=controls[cell['site'],cell['seed']] if method=='random_prefix_control' else bundles[cell['site']]
            dev_bundle=target.subset(source_bundle,data['dev'])
            # Zero scores are sufficient to derive truth and visibility; no stored params are applied.
            truth_only=predictions(dev_bundle,np.zeros_like(dev_bundle.y))
            if (not np.array_equal(methods[method]['truth'],truth_only['truth'])
                    or not np.array_equal(methods[method]['valid'],truth_only['valid'])):
                raise ValueError('preserved categorical truth/visibility differs from actual source targets')
        groups=np.array([row['component_id'] for row in data['dev_records']])
        recomputed={method:_diagnose(methods[method],groups,data['bodies']) for method in METHODS}
        if not _same(recomputed,cell['methods']): raise ValueError('posthoc diagnostic metrics differ from preserved predictions')
    if observed!=expected: raise ValueError('all 90 posthoc cells required')
    if (not _same(_read(Path(config['run_dir'])/'summary.json'),_summary(result))
            or Path(config['report']).read_bytes()!=_report(result).encode()):
        raise ValueError('posthoc summary/report differs from all preserved diagnostics')
    proof=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),source=result['source'],
        score_banks=90,prediction_rows=62640,all_diagnostics_recomputed=True,
        original_score_banks_reopened=False,activation_arrays_opened=False,coefficient_arrays_opened=False,
        parameters_reapplied=0,new_fits=0,new_model_queries=0,generated_holdouts_opened=False)
    publication.immutable(Path(config['run_dir'])/'prediction_replay_review_v1.json',_json_bytes(proof))
    return proof
