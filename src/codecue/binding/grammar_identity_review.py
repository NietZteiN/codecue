"""Discovery grammar decoding from pinned S5 scores, with no parameter access.

The decoder receives joint score tables only. Source syntax is used separately
for an explicitly algorithmic owner/counter reference; source SSA supplies truth
and evaluation strata. Audits reopen only this study's retained DEV score banks.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import zipfile

import numpy as np

from . import direct_identity_readouts as original, direct_identity_targets as target
from . import identity_grammar as grammar, schedule_score_review as saved
from . import relationship_capture as bounded, relationship_readouts as publication
from . import overnight_relationship_capture as durable
from .datasets import digest
from .discovery_readouts import group_weights
from .weighted_ridge import _array_hash

ROLE = 'discovery_identity_grammar_review_v1'
METHODS = original.METHODS
SITES = (7, 8)
SEEDS = (17, 29, 43)
RULES = {'joint_allow_self': ('joint', True), 'joint_no_self': ('joint', False),
         'owner_marginal_allow_self': ('owner_marginal', True),
         'owner_marginal_no_self': ('owner_marginal', False)}
SCOPES = ('assignment', 'parent', 'combined_eight')
FIT_SNAPSHOT = '3e5471ac9dc9b948761fc429'
FIT_SHA = '6a34415f2a9dfdab2acb5ceecc8fb88e19b8982d21881890c137f96082ddf1ee'
CAPTURE_SNAPSHOT = original.SOURCE_SNAPSHOT
CAPTURE_SHA = original.SOURCE_SHA
COMPLETION = 'completion_manifest_v1.json'
PROOF = 'grammar_replay_review_v1.json'
MAX_JSON = 192 * 1024**2
HEADS = {head['name']: head for head in target.HEADS}
LIMITATIONS = [
    'Adaptive discovery on consumed S5 scores and fifteen dependent DEV graph families; no untouched replication or interval.',
    'Grammar supplies external version counting from four initial version1 slots. Improved decoding does not show natural causal use or independent version representations.',
    'The fixed v1..4 codebook excludes otherwise lawful programs that write one owner four times and create version5.',
    'No-self is an additional global cohort prior. No case-specific profile, source, query, SSA map or truth enters score decoding.',
    'Raw ridge scores are uncalibrated. Their equal-weight sum and exact dyadic owner marginals are fixed decision rules, without temperature or scale tuning.',
    'Historical factorized component argmax differs from the exact same-evidence free objective; cross-objective harm is retained.',
    'Prefix-sham truth need not be globally lawful. Its own-task ceiling and scores against real truth are separate tasks, not matched selectivity evidence.',
    'Source owners plus the same counter algorithm determine all versions perfectly; this stronger source algorithm is reported explicitly.',
    'First versions are constants and last-parent version4 has only two TRAIN graph families. All cases and classes remain evaluated.',
    'No model/tokenizer, activations, features or coefficient arrays are loaded; no fits, parameter applications or bootstraps occur.',
]


def _bytes(value): return publication._json_bytes(value)
def _same(a, b): return _bytes(a) == _bytes(b)
def _pin(path): return saved._pin(path)
def _read(path, expected=None, limit=MAX_JSON): return saved._read(path, expected, limit)
def _publish(path, value): publication.immutable(path, _bytes(value))


def protocol():
    return dict(rules={name: dict(evidence=evidence, allow_self=allow) for name,(evidence,allow) in RULES.items()},
        methods=list(METHODS), sites=list(SITES), primary_layer=24, primary_site=7,
        seeds=list(SEEDS), codebook='4*owner+(version-1)', initial_versions=[1]*4,
        events=4, maximum_version=4, objective='Exact sum of eight raw ridge joint scores; owner_marginal sums four versions exactly.',
        tie='Global lexicographic owner-pair sequence; exact dyadic arithmetic.',
        missing='Any nonfinite joint cell makes the whole case missing and wrong.',
        profile_constraints=False, source_features_to_decoder=False, intervals='none')


def _config(config):
    fields={'evaluation_role','readout_configs','declared_plan','declared_plan_sha256','run_dir','report'}
    if (not isinstance(config,dict) or set(config)!=fields or config.get('evaluation_role')!=ROLE
            or len(_bytes(config))>16*1024 or not saved._sha(config.get('declared_plan_sha256'))):
        raise ValueError('exact bounded grammar-review configuration required')
    sources=config['readout_configs']
    if (not isinstance(sources,list) or len(sources)!=2 or any(not isinstance(item,dict)
            or set(item)!={'path','sha256'} or not isinstance(item['path'],str)
            or not saved._sha(item['sha256']) for item in sources)):
        raise ValueError('two SHA-pinned S5 readout configurations required')
    inputs=[bounded._safe(item['path']).resolve() for item in sources]
    if len(set(inputs))!=2: raise ValueError('distinct source configurations required')
    for key in ('declared_plan','run_dir','report'):
        if not isinstance(config[key],str) or not config[key]: raise ValueError('explicit safe paths required')
        if bounded._safe(config[key]).is_symlink(): raise ValueError('nonsymlink paths required')
    out,report,plan=(Path(config[key]).resolve() for key in ('run_dir','report','declared_plan'))
    reserved=[out/name for name in ('registration.json','results_v1.json','summary.json','audit.json',
                                   'progress.json',COMPLETION,PROOF)]
    if (report.suffix!='.md' or report==out or report in out.parents
            or (out.exists() and not out.is_dir()) or (report.exists() and not report.is_file())
            or any(p==report or p in report.parents for p in reserved)
            or any(out in p.parents and p.suffix in ('.npz','.json') for p in report.parents)
            or any(out==p or out in p.parents or p in out.parents
                   or report==p or report in p.parents or p in report.parents for p in inputs+[plan])):
        raise ValueError('grammar outputs cannot overlap inputs or reserved artifacts')
    return config


def _source(config, scheduled):
    _config(config)
    if scheduled:
        bounded._slurm(); return bounded._current_source(config)
    registration=_read(Path(config['run_dir'])/'registration.json')
    if (registration.get('evaluation_role')!=ROLE or registration.get('config')!=config
            or registration.get('config_hash')!=digest(config)):
        raise ValueError('original grammar registration differs')
    source=registration['source']; bounded._verify_source(config,source)
    return source


def _disjoint(config, paths):
    for value in paths:
        path=Path(value).resolve()
        for output in (Path(config['run_dir']).resolve(),Path(config['report']).resolve()):
            if output==path or output in path.parents or path in output.parents:
                raise ValueError('grammar outputs cannot overlap any original source artifact')


def _expected(folder, layers):
    return {original._CORE._name(backend,layer,site,seed):
        folder/(original._CORE._name(backend,layer,site,seed)+'.npz')
        for site in SITES for backend,layer in [('hidden',layer) for layer in layers]+[('surface',-1)]
        for seed in SEEDS}


def _validate_original(cfg, fit_source, checked, result, receipt, proof):
    """Metadata-only precondition: this never opens an old score NPZ."""
    if (cfg.get('evaluation_role')!=original.ROLE or cfg.get('primary_layer')!=24
            or fit_source.get('snapshot_id')!=FIT_SNAPSHOT or fit_source.get('source_sha256')!=FIT_SHA
            or checked['source'].get('snapshot_id')!=CAPTURE_SNAPSHOT
            or checked['source'].get('source_sha256')!=CAPTURE_SHA
            or checked.get('dataset_sha256')!=target.DATASET_SHA256):
        raise ValueError('frozen S5 fit and distinct S3 capture sources required')
    for doc in (receipt,proof,result):
        if (doc.get('evaluation_role')!=original.ROLE or doc.get('config_hash')!=digest(cfg)
                or doc.get('fit_source')!=fit_source or doc.get('capture_source')!=checked['source']
                or (doc.get('fit_banks'),doc.get('factorizations'),doc.get('parameter_replay_rows'))!=(30,30,172800)
                or doc.get('new_model_queries')!=0 or doc.get('generated_holdouts_opened') is not False):
            raise ValueError('matching completed S5 identities and accounting required')
    if (receipt.get('schema_version')!=1 or receipt.get('status')!='complete_exploratory'
            or result.get('status')!='complete_exploratory' or proof.get('status')!='passed'
            or proof.get('source_artifacts')!=receipt.get('artifacts') or proof.get('new_fits')!=0
            or not all(proof.get(k) is True for k in ('exact_saved_parameter_score_replays',
                'all_real_and_control_scores_replayed','all_scientific_metrics_recomputed',
                'train_support_and_control_marginals_recomputed'))):
        raise ValueError('completed parameter/metric proof required before score access')
    if ((result.get('cases'),result.get('training_rows'),result.get('development_rows'),
         result.get('training_groups'),result.get('development_groups'))!=(5760,4320,1440,45,15)
            or result.get('protocol')!=original.protocol()
            or not _same(result.get('target_columns'),list(target.COLUMNS))):
        raise ValueError('original192-column target/cohort recipe differs')


def _metadata(config, scheduled):
    source=_source(config,scheduled)
    if bounded._sha(config['declared_plan'])!=config['declared_plan_sha256']:
        raise ValueError('declared grammar plan differs')
    models={};pins=[_pin(config['declared_plan'])]
    for item in config['readout_configs']:
        cfg=_read(item['path'],item['sha256'],16*1024)
        fit_source,checked,records=original._metadata(cfg,scheduled=False)
        if checked['model'] not in saved.PROFILES: raise ValueError('supported cached profile required')
        model,revision,layers,width=saved.PROFILES[checked['model']]
        if model in models or checked['model_revision']!=revision or checked['layers']!=layers or checked['feature_shape']!=[5760,3,4,width]:
            raise ValueError('complete two-model capture geometry required')
        folder=Path(cfg['run_dir']);receipt=_read(folder/COMPLETION);proof=_read(folder/'parameter_replay_review_v1.json')
        expected=_expected(folder,layers)
        expected.update(registration=folder/'registration.json',results=folder/'results_v1.json',
                        summary=folder/'summary.json',audit=folder/'audit.json',report=Path(cfg['report']))
        inventory=receipt.get('artifacts',{})
        if set(inventory)!=set(expected): raise ValueError('exact original35-artifact inventory required')
        for name,path in expected.items():
            entry=inventory[name]
            if (not isinstance(entry,dict) or set(entry)!={'path','sha256','bytes'}
                    or Path(entry['path']).resolve()!=path.resolve() or not saved._sha(entry['sha256'])
                    or type(entry['bytes']) is not int or not 0<entry['bytes']<=512*1024**2):
                raise ValueError('original artifact path/hash/size differs')
            for output in (Path(config['run_dir']).resolve(),Path(config['report']).resolve()):
                if output==path.resolve() or output in path.resolve().parents or path.resolve() in output.parents:
                    raise ValueError('new outputs cannot overlap original scientific artifacts')
        result=_read(expected['results'],inventory['results'])
        _validate_original(cfg,fit_source,checked,result,receipt,proof)
        metadata={name:_read(expected[name],inventory[name]) for name in ('registration','summary','audit')}
        registration=metadata['registration']
        if (registration.get('config')!=cfg or registration.get('fit_source')!=fit_source
                or registration.get('capture_source')!=checked['source'] or registration.get('fixed_recipe')!=original.protocol()
                or not _same(metadata['summary'],original._CORE._summary(result))
                or metadata['audit'].get('status')!='passed'):
            raise ValueError('original registration/summary/audit differs')
        for doc in metadata.values():
            if doc.get('evaluation_role')!=original.ROLE or doc.get('config_hash')!=digest(cfg) or doc.get('new_model_queries')!=0 or doc.get('generated_holdouts_opened') is not False:
                raise ValueError('original metadata role or zero-work flags differ')
        if _pin(expected['report'])!=inventory['report']: raise ValueError('original report changed')
        fits={fit['name']:fit for fit in result['fits']}
        names={name for name,path in expected.items() if path.suffix=='.npz'}
        if len(result['fits'])!=30 or set(fits)!=names: raise ValueError('all original30 score banks required')
        for name,fit in fits.items():
            if (fit['name']!=original._CORE._name(fit['backend'],fit['layer'],fit['site'],fit['seed'])
                    or Path(fit['artifact']).resolve()!=expected[name].resolve() or fit.get('factorizations')!=1
                    or fit.get('exact_parameter_score_replay') is not True or set(fit['metrics'])!=set(METHODS)):
                raise ValueError('original fit grid/metric identity differs')
        ids=tuple(row['id'] for row in records);dev=np.flatnonzero([r['split']=='development' for r in records])
        dev_records=[records[i] for i in dev]
        if (len(ids)!=5760 or len(set(ids))!=5760 or len(dev)!=1440
                or len({r['component_id'] for r in dev_records})!=15
                or set(r['profile_id'] for r in dev_records)!={'2_1_1_0','3_1_0_0','2_2_0_0'}):
            raise ValueError('exact ordered source and grouped DEV population required')
        _disjoint(config,[cfg['run_dir'],cfg['declared_plan'],cfg['capture_config'],checked['config']['run_dir'],
            checked['config']['dataset'],Path(checked['config']['dataset']).with_suffix('.manifest.json'),
            Path(checked['config']['run_dir'])/'prepared_cases.jsonl'])
        models[model]=dict(config=cfg,checked=checked,records=records,ids=ids,dev=dev,dev_records=dev_records,
                          fit_map=fits,inventory=inventory,result=result)
        pins += [_pin(item['path']),_pin(folder/COMPLETION),_pin(folder/'parameter_replay_review_v1.json')]
        pins += [_pin(expected[name]) for name in ('registration','results','summary','audit','report')]
        pins += [_pin(cfg['capture_config']),_pin(Path(checked['config']['run_dir'])/COMPLETION),
                 _pin(Path(checked['config']['run_dir'])/'prepared_cases.jsonl'),
                 _pin(checked['config']['dataset']),_pin(Path(checked['config']['dataset']).with_suffix('.manifest.json'))]
    if set(models)!={'llama8b','codellama34b'} or models['llama8b']['ids']!=models['codellama34b']['ids']:
        raise ValueError('both distinct models must align to the same ordered source cases')
    return source,models,pins


def head_predictions(bundle, scores):
    """Own192-column decoder; predictions never consult row-specific truth masks."""
    scores=np.asarray(scores)
    if scores.shape!=bundle.y.shape or tuple(bundle.columns)!=target.COLUMNS:
        raise ValueError('exact192-column score/target schema required')
    n=len(scores);truth=np.full((n,24),-1,dtype=np.int16);pred=np.full_like(truth,-1);valid=np.zeros_like(truth,dtype=bool)
    for h,spec in enumerate(target.HEADS):
        indices=list(spec['indices']);candidates=np.asarray(spec['candidates'],dtype=np.int16)
        values=scores[:,indices];usable=np.isfinite(values).any(axis=1)
        pred[usable,h]=candidates[np.argmax(np.where(np.isfinite(values),values,-np.inf),axis=1)[usable]]
        labels=bundle.y[:,indices];defined=(labels.sum(axis=1)==1)&bundle.mask[:,indices].any(axis=1)
        valid[:,h]=defined;truth[defined,h]=candidates[np.argmax(labels[defined],axis=1)]
    return dict(truth=truth,predicted=pred,valid=valid,correct=valid&(pred==truth))


def _ids(bundle, scores, route='joint'):
    data=head_predictions(bundle,scores);lookup={h['name']:i for i,h in enumerate(target.HEADS)}
    result=[]
    for kind in ('assignment','parent'):
        if route=='joint':values=np.column_stack([data['predicted'][:,lookup[f'{kind}_joint/{event}']] for event in range(4,8)])
        else:
            owners=np.column_stack([data['predicted'][:,lookup[f'{kind}_owner/{event}']] for event in range(4,8)])
            versions=np.column_stack([data['predicted'][:,lookup[f'{kind}_version/{event}']] for event in range(4,8)])
            values=np.where((owners>=0)&(versions>=1),4*owners+versions-1,-1)
        result.append(values.astype(np.int16))
    return tuple(result)


def _joint_tables(scores):
    values=np.asarray(scores)
    if values.ndim!=2 or values.shape[1]!=192: raise ValueError('full192-column score matrix required')
    return tuple(np.stack([values[:,HEADS[f'{kind}_joint/{event}']['indices']] for event in range(4,8)],axis=1)
                 for kind in ('assignment','parent'))


def _truth(bundle):
    w,p=_ids(bundle,bundle.y)
    valid=tuple(np.column_stack([bundle.mask[:,HEADS[f'{kind}_joint/{event}']['indices']].any(axis=1)
                               for event in range(4,8)]) for kind in ('assignment','parent'))
    return (w,p),valid


def _point(correct, valid, groups):
    correct=np.asarray(correct,dtype=bool);valid=np.asarray(valid,dtype=bool);groups=np.asarray(groups)
    items={str(group):dict(n=int((valid&(groups==group)).sum()),correct=int(correct[valid&(groups==group)].sum()),
        accuracy=float(correct[valid&(groups==group)].mean())) for group in sorted(set(groups[valid]))}
    return dict(n=int(valid.sum()),correct=int(correct[valid].sum()),accuracy=float(correct[valid].mean()) if valid.any() else None,
        group_macro_accuracy=float(np.mean([v['accuracy'] for v in items.values()])) if items else None,per_group=items)


def _flags(truth, valid, prediction):
    correct=[v&(p==t)&(p>=0) for t,v,p in zip(truth,valid,prediction)]
    defined=[v.all(1) for v in valid]
    return {'assignment':(correct[0].all(1),defined[0]),'parent':(correct[1].all(1),defined[1]),
            'combined_eight':(correct[0].all(1)&correct[1].all(1),defined[0]&defined[1])}


def _metrics(bundle, prediction):
    truth,valid=_truth(bundle);groups=np.asarray(bundle.group_ids);profiles=np.asarray(bundle.descriptive['profile_ids'])
    flags=_flags(truth,valid,prediction)
    whole={scope:_point(correct,defined,groups) for scope,(correct,defined) in flags.items()}
    heads={};statuses=bundle.descriptive['event_capture_status'];pooled_status={}
    for kind,t,v,p in zip(('assignment','parent'),truth,valid,prediction):
        status_matrix=np.asarray([entry[kind] for entry in statuses],dtype=object)
        pooled_status[kind]={status:_point((p==t).reshape(-1), (v&(status_matrix==status)).reshape(-1),np.repeat(groups,4))
            for status in ('current','obsolete')}
        for step in range(4):
            name=f'{kind}/{step+4}';correct=(p[:,step]==t[:,step])&(p[:,step]>=0);defined=v[:,step]
            cell=_point(correct,defined,groups)
            cell.update(missing_predictions=int((defined&(p[:,step]<0)).sum()),
                owner=_point((p[:,step]>=0)&(p[:,step]//4==t[:,step]//4),defined,groups),
                version=_point((p[:,step]>=0)&(p[:,step]%4==t[:,step]%4),defined,groups),
                classes={str(c):_point(correct,defined&(t[:,step]==c),groups) for c in range(16)},
                by_profile={str(profile):_point(correct,defined&(profiles==profile),groups) for profile in sorted(set(profiles))},
                by_capture_status={status:_point(correct,defined&(status_matrix[:,step]==status),groups) for status in ('current','obsolete')})
            heads[name]=cell
    return dict(whole=whole,per_head=heads,by_profile={str(profile):{scope:_point(correct,defined&(profiles==profile),groups)
        for scope,(correct,defined) in flags.items()} for profile in sorted(set(profiles))},by_capture_status=pooled_status)


def _transitions(bundle, reference, prediction, free_lawful):
    truth,valid=_truth(bundle);groups=np.asarray(bundle.group_ids)
    before=_flags(truth,valid,reference);after=_flags(truth,valid,prediction);result={}
    changed={'assignment':np.any(reference[0]!=prediction[0],axis=1),
             'parent':np.any(reference[1]!=prediction[1],axis=1)}
    changed['combined_eight']=changed['assignment']|changed['parent']
    for scope in SCOPES:
        a,defined=before[scope];b,other=after[scope];defined=defined&other
        indicators=dict(corrected=~a&b,harmed=a&~b,both_correct=a&b,both_wrong=~a&~b,changed=changed[scope])
        result[scope]={key:_point(value,defined,groups) for key,value in indicators.items()}
        result[scope]['by_free_joint_lawfulness']={label:{key:_point(value,defined&(free_lawful==flag),groups)
            for key,value in indicators.items()} for label,flag in (('lawful',True),('unlawful',False))}
    result['lawfulness_stratum_scope']='Broad codebook copy grammar, self allowed, for the HISTORICAL free_joint reference.'
    result['per_head']={}
    for kind,t,v,a,b in zip(('assignment','parent'),truth,valid,reference,prediction):
        for step in range(4):
            old=(a[:,step]==t[:,step])&(a[:,step]>=0);new=(b[:,step]==t[:,step])&(b[:,step]>=0)
            indicators=dict(corrected=~old&new,harmed=old&~new,both_correct=old&new,both_wrong=~old&~new,changed=a[:,step]!=b[:,step])
            result['per_head'][f'{kind}/{step+4}']={key:_point(value,v[:,step],groups) for key,value in indicators.items()}
    return result


def _lawfulness(prediction, groups, allow_self):
    checked=grammar.validate_paths(*prediction,allow_self=allow_self);groups=np.asarray(groups)
    return dict(allow_self=allow_self,lawful=_point(checked['lawful'],np.ones(len(groups),dtype=bool),groups),
        complete_cases=int(checked['complete'].sum()),first_violation_counts={str(step):int((checked['first_violation']==step).sum()) for step in range(-1,4)},
        flags={name:dict(rows=int(flags.any(1).sum()),event_counts=flags.sum(0).tolist(),
                        per_group={str(group):int(flags[groups==group].any(1).sum()) for group in sorted(set(groups))})
               for name,flags in checked['flags'].items()})


def _exact_checks(inputs, output, evidence):
    selected=grammar.score_paths(*inputs,output['write_ids'],output['parent_ids'],evidence=evidence)
    free=grammar.score_paths(*inputs,output['free_write_ids'],output['free_parent_ids'],evidence=evidence)
    if (selected['score_numerators']!=output['score_numerators'] or selected['score_exponents']!=output['score_exponents']
            or free['score_numerators']!=output['free_upper_bound_numerators'] or free['score_exponents']!=output['free_upper_bound_exponents']):
        raise ValueError('selected/free exact path scores differ from decoder objective')
    for i,finite in enumerate(output['finite']):
        keys=[(output[name+'_numerators'][i],output[name+'_exponents'][i]) for name in ('score','free_upper_bound','projection_penalty')]
        if not finite:
            if any(pair!=(None,None) for pair in keys): raise ValueError('missing cases require undefined exact objectives')
            continue
        if any(not isinstance(num,str) or type(exp) is not int for num,exp in keys): raise ValueError('exact dyadic score keys required')
        (a,ae),(b,be),(c,ce)=[(int(num),exp) for num,exp in keys];base=min(ae,be,ce)
        if c<0 or (b<<(be-base))-(a<<(ae-base))!=c<<(ce-base): raise ValueError('exact free bound/penalty identity differs')
    return {key:output[key] for key in ('score_numerators','score_exponents','free_upper_bound_numerators',
        'free_upper_bound_exponents','projection_penalty_numerators','projection_penalty_exponents')}|dict(
        path_code=output['path_code'].tolist(),exact_arithmetic=True,selected_and_free_path_scores_recomputed=True,
        projection_penalty_nonnegative=True,positive_penalty_cases=sum(v not in (None,'0') for v in output['projection_penalty_numerators']))


def _compact_metrics(metrics): return metrics['whole']


def _evaluate_bank(bundle, control, tables):
    """Decode each score/rule once; sham cross-task metrics reuse predictions."""
    tables=np.asarray(tables)
    if tables.shape!=(4,len(bundle.case_ids),192) or tables.dtype!=np.float64:
        raise ValueError('four aligned float64 DEV score tables required')
    diagnostic={'methods':{},'source_owner_counter':None};decoded=[];free_saved=[]
    real_truth,real_valid=_truth(bundle)
    owners=bundle.descriptive['syntax_owners']
    syntax=grammar.owners_to_identities(np.asarray([r['assignment'] for r in owners]),np.asarray([r['parent'] for r in owners]))
    if not syntax['valid'].all(): raise ValueError('source-owner counter reference must be representable')
    syntax_prediction=syntax['write_ids'],syntax['parent_ids']
    diagnostic['source_owner_counter']=_metrics(bundle,syntax_prediction)
    if diagnostic['source_owner_counter']['whole']['combined_eight']['accuracy']!=1.:
        raise ValueError('source-owner counter reference must exactly recover all real identities')
    for m,method in enumerate(METHODS):
        truth_bundle=control if method=='random_prefix_control' else bundle
        truth,valid=_truth(truth_bundle);joint=_ids(truth_bundle,tables[m]);marginal=_ids(truth_bundle,tables[m],'marginal')
        free_saved.append(np.stack([np.column_stack(joint),np.column_stack(marginal)]))
        free_lawful=grammar.validate_paths(*joint,allow_self=True)['lawful']
        item=dict(truth_task='prefix_sham' if method=='random_prefix_control' else 'real',
            free_joint=_metrics(truth_bundle,joint),free_marginal=_metrics(truth_bundle,marginal),rules={})
        item['free_joint_lawfulness']={label:_point(grammar.validate_paths(*joint,allow_self=allow)['lawful'],
            np.ones(len(bundle.case_ids),dtype=bool),bundle.group_ids) for label,allow in (('allow_self',True),('no_self',False))}
        item['historical_reference_lawfulness']={reference:{label:_lawfulness(paths,bundle.group_ids,allow)
            for label,allow in (('allow_self',True),('no_self',False))}
            for reference,paths in (('free_joint',joint),('free_marginal',marginal))}
        inputs=_joint_tables(tables[m]);method_decisions=[];outputs={}
        for rule,(evidence,allow_self) in RULES.items():
            output=grammar.decode(*inputs,evidence=evidence,allow_self=allow_self)
            prediction=output['write_ids'],output['parent_ids'];outputs[rule]=output
            method_decisions.append(np.column_stack(prediction))
            own=_metrics(truth_bundle,prediction);real=own if method!='random_prefix_control' else _metrics(bundle,prediction)
            objective_free=output['free_write_ids'],output['free_parent_ids']
            lawful=grammar.validate_paths(*objective_free,allow_self=allow_self)['lawful']
            unchanged=np.all(np.column_stack(objective_free)==np.column_stack(prediction),axis=1)
            if np.any(lawful&~unchanged): raise ValueError('same-evidence lawful free optimum changed')
            truth_lawful=grammar.validate_paths(*truth,allow_self=allow_self)['lawful']
            truth_defined=np.logical_and.reduce([v.all(1) for v in valid])
            ceiling=_point(truth_lawful,truth_defined,bundle.group_ids)
            if own['whole']['combined_eight']['correct']>ceiling['correct']:
                raise ValueError('lawful prediction exceeds its truth-lawfulness ceiling')
            transitions={name:_transitions(truth_bundle,reference,prediction,free_lawful)
                         for name,reference in (('free_joint',joint),('free_marginal',marginal))}
            old_flags=_flags(truth,valid,joint)['combined_eight'];new_flags=_flags(truth,valid,prediction)['combined_eight']
            if evidence=='joint' and np.any(output['finite']&truth_lawful&old_flags[0]&~new_flags[0]&old_flags[1]):
                raise ValueError('joint grammar harmed a whole-correct lawful free joint path')
            item['rules'][rule]=dict(evidence=evidence,allow_self=allow_self,own_task=own,real_task=real,
                free_objective=_metrics(truth_bundle,objective_free),transitions=transitions,
                finite_cases=int(output['finite'].sum()),lawful_cases=int(output['valid'].sum()),
                missing_cases=int((~output['finite']).sum()),truth_lawfulness_ceiling=ceiling,
                same_evidence_lawful_free_cases=int(lawful.sum()),same_evidence_lawful_free_preserved=True,
                joint_historical_lawful_truth_whole8_monotonic=(True if evidence=='joint' else None),
                monotonicity_scope='Joint evidence, finite128joint-score cases, defined globally lawful truth only; cross-objective and missing-case harms remain.',
                exact_objective_checks=_exact_checks(inputs,output,evidence))
        for evidence in ('joint','owner_marginal'):
            broad=outputs[evidence+'_allow_self'];narrow=outputs[evidence+'_no_self']
            already=grammar.validate_paths(broad['write_ids'],broad['parent_ids'],allow_self=False)['lawful']
            changed=np.any(np.column_stack((broad['write_ids'],broad['parent_ids']))!=np.column_stack((narrow['write_ids'],narrow['parent_ids'])),axis=1)
            if np.any(already&changed): raise ValueError('nested no-self projection changed a feasible broad optimum')
            item['rules'][evidence+'_no_self']['nested_feasible_broad_cases']=int(already.sum())
            item['rules'][evidence+'_no_self']['nested_feasible_broad_preserved']=True
        diagnostic['methods'][method]=item;decoded.append(np.stack(method_decisions))
    return diagnostic,np.asarray(decoded,dtype=np.int16),np.asarray(free_saved,dtype=np.int16)


def _cell_summary(diagnostic):
    return {method:dict(free_joint=item['free_joint']['whole'],free_marginal=item['free_marginal']['whole'],
        rules={rule:{task:entry[task]['whole'] for task in ('own_task','real_task')}
               for rule,entry in item['rules'].items()}) for method,item in diagnostic['methods'].items()}


def _verify_metrics(data, fit, bundle, control, train, weights, tables):
    dev=data['dev'];n=len(bundle.case_ids)
    real=np.zeros((n,192));sham=np.zeros_like(real)
    real[dev]=tables[METHODS.index('direct')];sham[dev]=tables[METHODS.index('random_prefix_control')]
    verified=original._CORE._score_methods(bundle,control,train,weights,dev,real,sham)
    if not _same(verified,fit['metrics']): raise ValueError('saved DEV scores do not exactly reproduce all original metrics')
    prior=original._CORE._prior(bundle,train,weights)[dev]
    syntax=target.syntax_owner_version_prior(bundle,train,weights)[dev]
    if not np.array_equal(prior,tables[METHODS.index('training_prior')],equal_nan=True) or not np.array_equal(syntax,tables[METHODS.index('source_owner_version_prior')],equal_nan=True):
        raise ValueError('retained TRAIN-only baseline scores differ')


def _bank_identity(config, model, name, entry, records, original_identity=None):
    value=dict(evaluation_role=ROLE,config_hash=digest(config),model=model,name=name,input_bank=entry,
        methods=list(METHODS),rules=list(RULES),columns_sha256=digest(list(target.COLUMNS)),
        case_ids_sha256=digest([r['id'] for r in records]),groups_sha256=digest([r['component_id'] for r in records]),
        profiles_sha256=digest([r['profile_id'] for r in records]))
    if original_identity is not None:
        value.update(original_score_identity_sha256=digest(original_identity),
                     opaque_original_feature_sha256=original_identity['features_sha256'])
    return value


def _save_bank(path, identity, records, scores, decoded, free):
    stream=io.BytesIO()
    np.savez_compressed(stream,identity=np.frombuffer(_bytes(identity),dtype=np.uint8),scores=scores,
        decoded_ids=decoded,free_ids=free,case_ids=np.asarray([r['id'] for r in records]),
        group_ids=np.asarray([r['component_id'] for r in records]),profiles=np.asarray([r['profile_id'] for r in records]))
    publication.immutable(path,stream.getvalue())


def _load_bank(path, entry, expected, records):
    if _pin(path)!=entry: raise ValueError('retained DEV score bank changed')
    n=len(records);names={'identity','scores','decoded_ids','free_ids','case_ids','group_ids','profiles'}
    with zipfile.ZipFile(path) as archive:
        if set(archive.namelist())!={name+'.npy' for name in names} or any(info.file_size>16*1024**2 for info in archive.infolist()):
            raise ValueError('bounded exact DEV-score archive members required')
    with np.load(path,allow_pickle=False) as bank:
        raw=bank['identity']
        if raw.dtype!=np.uint8 or raw.ndim!=1 or raw.nbytes>2*1024**2: raise ValueError('bounded score identity required')
        identity=json.loads(raw.tobytes())
        if any(identity.get(key)!=value for key,value in expected.items()) or set(identity)!=set(expected)|{'original_score_identity_sha256','opaque_original_feature_sha256'}:
            raise ValueError('retained score provenance differs')
        if not all(saved._sha(identity.get(key)) for key in ('original_score_identity_sha256','opaque_original_feature_sha256')):
            raise ValueError('opaque original score identity pins required')
        for member,field in (('case_ids','id'),('group_ids','component_id'),('profiles','profile_id')):
            if bank[member].tolist()!=[r[field] for r in records]: raise ValueError('retained ordered DEV metadata differs')
        scores=bank['scores'].copy();decoded=bank['decoded_ids'].copy();free=bank['free_ids'].copy()
    if scores.dtype!=np.float64 or scores.shape!=(4,n,192): raise ValueError('retained full192 DEV scores differ')
    if decoded.dtype!=np.int16 or decoded.shape!=(4,4,n,8) or free.dtype!=np.int16 or free.shape!=(4,2,n,8):
        raise ValueError('retained grammar/reference prediction geometry differs')
    if not np.isin(decoded,range(-1,16)).all() or not np.isin(free,range(-1,16)).all(): raise ValueError('global16-class prediction domain differs')
    return scores,decoded,free,identity


def _summary(result):
    primary={};free={}
    for model in ('llama8b','codellama34b'):
        primary[model]={};free[model]={}
        for backend in ('hidden','surface'):
            primary[model][backend]={};free[model][backend]={}
            for site in SITES:
                cells=[c for c in result['cells'] if c['model']==model and c['backend']==backend and c['site']==site and (backend=='surface' or c['layer']==24)]
                if len(cells)!=3 or {c['seed'] for c in cells}!=set(SEEDS): raise ValueError('all three fixed primary weighting seeds required')
                primary[model][backend][str(site)]={};free[model][backend][str(site)]={}
                def mean(points):
                    return {scope:dict(accuracy=float(np.mean([p[scope]['accuracy'] for p in points])),
                        group_macro_accuracy=float(np.mean([p[scope]['group_macro_accuracy'] for p in points])),
                        n_per_seed=points[0][scope]['n'],seeds=list(SEEDS)) for scope in SCOPES}
                for method in METHODS:
                    primary[model][backend][str(site)][method]={rule:{task:mean([c['summary_methods'][method]['rules'][rule][task] for c in cells])
                        for task in ('own_task','real_task')} for rule in RULES}
                    free[model][backend][str(site)][method]={reference:mean([c['summary_methods'][method][reference] for c in cells])
                        for reference in ('free_joint','free_marginal')}
    return dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=result['config_hash'],source=result['source'],
        score_banks=60,saved_score_rows_checked=345600,development_rows_per_bank=1440,development_prediction_rows=86400,
        decoded_case_rule_method_rows=1382400,graph_groups=15,primary=primary,free=free,
        original_metrics_exact=True,new_fits=0,new_model_queries=0,parameters_reapplied=0,
        activation_arrays_opened=False,coefficient_arrays_opened=False,generated_holdouts_opened=False,limitations=LIMITATIONS)


def _report(result):
    summary=_summary(result);lines=['# Grammar-constrained identity decoding','',
        'This adaptive saved-score review adds external counter grammar to the frozen S5 predictions. No model or probe is fitted or reapplied. Source owners plus the counter rule recover every real identity and remain an explicit algorithmic reference.','',
        'The fixed primary is hidden layer24/site7, averaging seeds17/29/43. Whole endpoints require all four writes, all four parents or all eight identities correct. The same complete grid remains available for character features, priors, both sites and every layer.','',
        '| Model | Method | Rule | Write4 | Parent4 | All8 |','|---|---|---|---:|---:|---:|']
    for model in ('llama8b','codellama34b'):
        for method in METHODS:
            for rule in RULES:
                points=summary['primary'][model]['hidden']['7'][method][rule]['own_task']
                lines.append('| '+' | '.join([model,method,rule,*[f'{100*points[scope]["accuracy"]:.3f}%' for scope in SCOPES]])+' |')
    lines+=['','Prefix-sham rows above score the separate sham task; its truth-lawfulness ceiling and the same predictions against real truth remain separate in every diagnostic. Historical joint/factorized references and exact same-evidence free objectives are distinct. Individual heads and families can be harmed; joint whole-eight monotonicity is checked only against its matching free objective.','']
    lines+=['- '+item for item in LIMITATIONS]
    return '\n'.join(lines)+'\n'


def preflight(config):
    source,models,pins=_metadata(config,scheduled=True);reviews={}
    for model,data in models.items():
        original._initialization(data['records']);bundle=target.targets(data['records'],7)
        syntax=bundle.descriptive['syntax_owners']
        reference=grammar.owners_to_identities(np.asarray([r['assignment'] for r in syntax]),np.asarray([r['parent'] for r in syntax]))
        truth,_=_truth(bundle)
        if not reference['valid'].all() or not np.array_equal(reference['write_ids'],truth[0]) or not np.array_equal(reference['parent_ids'],truth[1]):
            raise ValueError('complete source-owner counter preflight differs')
        reviews[model]=dict(rows=5760,dev_rows=1440,groups=15,site3_defined_columns=0,source_owner_counter_whole8_accuracy=1.,
                           train_class_support=target.training_support(bundle))
    return dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),source=source,score_banks=60,
        saved_score_rows_checked=345600,development_prediction_rows=86400,protocol=protocol(),input_pins=pins,
        source_only_reviews=reviews,saved_score_arrays_opened=False,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False)


def _paths(config):
    out=Path(config['run_dir']);paths={}
    for model,_,layers,_ in saved.PROFILES.values():
        for name in _expected(out,layers):
            paths['scores_'+model+'_'+name]=out/f'scores_{model}_{name}.npz'
            paths['diagnostics_'+model+'_'+name]=out/f'diagnostics_{model}_{name}.json'
    paths.update(registration=out/'registration.json',results=out/'results_v1.json',summary=out/'summary.json',
                 audit=out/'audit.json',report=Path(config['report']))
    return paths


def run(config):
    from .confidence import _run_lock
    source,models,pins=_metadata(config,scheduled=True);out=Path(config['run_dir']);out.mkdir(parents=True,exist_ok=True)
    with _run_lock(out):
        if (out/COMPLETION).exists():
            result=completed_result(config)
            if result['source']!=source: raise ValueError('completed review belongs to another source')
            return result
        if not (out/'registration.json').exists() and (any(out.glob('scores_*.npz')) or any(out.glob('diagnostics_*.json'))):
            raise ValueError('orphan grammar artifacts require original registration')
        _publish(out/'registration.json',dict(evaluation_role=ROLE,config=config,config_hash=digest(config),source=source,
            protocol=protocol(),input_pins=pins,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        cells=[];artifacts={}
        for model,data in sorted(models.items()):
            records=data['records'];dev=data['dev'];train=np.asarray([r['split']=='train' for r in records])
            train_rows=[r for r,use in zip(records,train) if use]
            bundles={site:target.targets(records,site) for site in SITES}
            controls={(site,seed):target.control_targets(records,site,seed) for site in SITES for seed in SEEDS}
            for name,fit in sorted(data['fit_map'].items()):
                bundle=bundles[fit['site']];control=controls[fit['site'],fit['seed']];entry=data['inventory'][name]
                weights=group_weights(train_rows,fit['seed']).astype(np.float64)
                bank_path=out/f'scores_{model}_{name}.npz';expected=_bank_identity(config,model,name,entry,data['dev_records'])
                if bank_path.exists():
                    tables,stored_decoded,stored_free,identity=_load_bank(bank_path,_pin(bank_path),expected,data['dev_records'])
                else:
                    scores,random,old_identity=saved.load_score_bank(fit['artifact'],entry,bundle,control,train,weights,digest(data['config']))
                    tables=np.stack([scores[dev],original._CORE._prior(bundle,train,weights)[dev],random[dev],
                                     target.syntax_owner_version_prior(bundle,train,weights)[dev]])
                    identity=_bank_identity(config,model,name,entry,data['dev_records'],old_identity)
                _verify_metrics(data,fit,bundle,control,train,weights,tables)
                diagnostic,decoded,free=_evaluate_bank(target.subset(bundle,dev),target.subset(control,dev),tables)
                if bank_path.exists():
                    if not np.array_equal(decoded,stored_decoded) or not np.array_equal(free,stored_free): raise ValueError('resumed grammar decisions differ')
                else:_save_bank(bank_path,identity,data['dev_records'],tables,decoded,free)
                score_pin=_pin(bank_path)
                # Reopen new storage once; no second grammar solve is needed here.
                restored=_load_bank(bank_path,score_pin,expected,data['dev_records'])
                if not np.array_equal(restored[0],tables,equal_nan=True) or not np.array_equal(restored[1],decoded): raise ValueError('retained score publication differs')
                header=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
                    model=model,name=name,backend=fit['backend'],layer=fit['layer'],site=fit['site'],seed=fit['seed'],
                    original_metrics_exact=True,score_bank=score_pin,original_score_bank=entry,**diagnostic)
                diagnostic_path=out/f'diagnostics_{model}_{name}.json';_publish(diagnostic_path,header)
                diagnostic_pin=_pin(diagnostic_path)
                artifacts['scores_'+model+'_'+name]=score_pin;artifacts['diagnostics_'+model+'_'+name]=diagnostic_pin
                cells.append({key:header[key] for key in ('model','name','backend','layer','site','seed','score_bank','original_score_bank','original_metrics_exact')}|
                    dict(diagnostic=diagnostic_pin,summary_methods=_cell_summary(diagnostic)))
                durable._journal(out/'progress.json',dict(status='running',score_banks=len(cells),planned_banks=60,
                    new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
                print(f'grammar review {model} {name}',flush=True)
        if len(cells)!=60: raise ValueError('all60 source banks required')
        result=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,protocol=protocol(),
            fit_source_snapshot=FIT_SNAPSHOT,capture_source_snapshot=CAPTURE_SNAPSHOT,score_banks=60,
            saved_score_rows_checked=345600,development_rows_per_bank=1440,development_prediction_rows=86400,
            decoded_case_rule_method_rows=1382400,cells=cells,input_pins=pins,original_metrics_exact=True,
            new_fits=0,new_model_queries=0,parameters_reapplied=0,activation_arrays_opened=False,
            coefficient_arrays_opened=False,generated_holdouts_opened=False,limitations=LIMITATIONS)
        _publish(out/'results_v1.json',result);_publish(out/'summary.json',_summary(result))
        publication.immutable(config['report'],_report(result).encode())
        _publish(out/'audit.json',dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),score_banks=60,
            original_metrics_exact=True,new_dev_score_storage_reopened=True,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        artifacts.update({name:_pin(path) for name,path in _paths(config).items() if name in ('registration','results','summary','audit','report')})
        _publish(out/COMPLETION,dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
            score_banks=60,saved_score_rows_checked=345600,development_prediction_rows=86400,artifacts=artifacts,
            original_metrics_exact=True,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        durable._journal(out/'progress.json',dict(status='complete',score_banks=60,new_fits=0,new_model_queries=0,parameters_reapplied=0))
        return result


def completed_result(config):
    source=_source(config,scheduled=False);out=Path(config['run_dir']);receipt=_read(out/COMPLETION)
    if (receipt.get('evaluation_role')!=ROLE or receipt.get('status')!='complete_exploratory'
            or receipt.get('config_hash')!=digest(config) or receipt.get('source')!=source or receipt.get('score_banks')!=60
            or receipt.get('new_fits')!=0 or receipt.get('new_model_queries')!=0 or receipt.get('parameters_reapplied')!=0
            or receipt.get('generated_holdouts_opened') is not False): raise ValueError('complete matching grammar receipt required')
    paths=_paths(config);inventory=receipt.get('artifacts',{})
    if set(inventory)!=set(paths): raise ValueError('exact60score/60diagnostic/fivemetadata inventory required')
    for name,path in paths.items():
        if _pin(path)!=inventory[name]: raise ValueError('immutable grammar artifact changed')
    registration=_read(paths['registration'],inventory['registration'])
    if registration.get('protocol')!=protocol(): raise ValueError('registered decoder protocol differs')
    result=_read(paths['results'],inventory['results'])
    if (result.get('status')!='complete_exploratory' or result.get('evaluation_role')!=ROLE
            or result.get('config_hash')!=digest(config) or result.get('source')!=source or result.get('protocol')!=protocol()
            or result.get('score_banks')!=60 or len(result.get('cells',[]))!=60
            or result.get('new_fits')!=0 or result.get('new_model_queries')!=0 or result.get('parameters_reapplied')!=0
            or result.get('generated_holdouts_opened') is not False): raise ValueError('complete grammar result differs')
    return result


def audit(config):
    """Replay from NEW DEV tables only; never reopen an original score NPZ."""
    bounded._slurm();result=completed_result(config);_,models,pins=_metadata(config,scheduled=False)
    if not _same(result['input_pins'],pins): raise ValueError('original metadata pins differ from registration')
    expected={(model,name) for model,data in models.items() for name in data['fit_map']};seen=set()
    bundles={model:{site:target.targets(data['records'],site) for site in SITES} for model,data in models.items()}
    controls={model:{(site,seed):target.control_targets(data['records'],site,seed) for site in SITES for seed in SEEDS}
              for model,data in models.items()}
    for cell in result['cells']:
        key=cell['model'],cell['name']
        if key not in expected or key in seen: raise ValueError('duplicate or undeclared grammar bank')
        seen.add(key);data=models[cell['model']];fit=data['fit_map'][cell['name']]
        if cell['original_score_bank']!=data['inventory'][cell['name']] or (cell['backend'],cell['layer'],cell['site'],cell['seed'])!=(fit['backend'],fit['layer'],fit['site'],fit['seed']):
            raise ValueError('original bank/grid provenance differs')
        identity=_bank_identity(config,cell['model'],cell['name'],cell['original_score_bank'],data['dev_records'])
        tables,decoded,free,_=_load_bank(cell['score_bank']['path'],cell['score_bank'],identity,data['dev_records'])
        bundle=bundles[cell['model']][cell['site']];control=controls[cell['model']][cell['site'],cell['seed']]
        train=np.asarray([r['split']=='train' for r in data['records']]);weights=group_weights([r for r,use in zip(data['records'],train) if use],cell['seed']).astype(np.float64)
        _verify_metrics(data,fit,bundle,control,train,weights,tables)
        diagnostic,predicted,reference=_evaluate_bank(target.subset(bundle,data['dev']),target.subset(control,data['dev']),tables)
        recorded=_read(cell['diagnostic']['path'],cell['diagnostic'])
        if (not np.array_equal(decoded,predicted) or not np.array_equal(free,reference)
                or any(not _same(recorded[k],value) for k,value in diagnostic.items())
                or not _same(cell['summary_methods'],_cell_summary(diagnostic))):
            raise ValueError('grammar diagnostics differ from retained DEV scores')
    if seen!=expected: raise ValueError('all60 banks required')
    if not _same(_read(Path(config['run_dir'])/'summary.json'),_summary(result)) or Path(config['report']).read_bytes()!=_report(result).encode():
        raise ValueError('grammar summary/report differs')
    proof=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),source=result['source'],
        score_banks=60,saved_score_rows_checked=345600,development_prediction_rows=86400,
        all_grammar_diagnostics_recomputed=True,all_original_metrics_recomputed=True,
        all_new_dev_score_banks_reopened=True,original_score_banks_reopened=False,
        source_artifacts=_read(Path(config['run_dir'])/COMPLETION)['artifacts'],
        new_fits=0,new_model_queries=0,parameters_reapplied=0,activation_arrays_opened=False,
        coefficient_arrays_opened=False,generated_holdouts_opened=False)
    _publish(Path(config['run_dir'])/PROOF,proof)
    return proof
