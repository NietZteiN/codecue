"""Posthoc joins of existing overnight probe scores and generated answers.

Only saved score/identity arrays are opened. No hidden states, model calls,
fitting or parameter prediction is performed. All reported rows are DEV; TRAIN
responses are checked only for integrity of the original response artifact.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import io
import json
import os
from pathlib import Path

import numpy as np

from . import relationship_capture as bounded, relationship_readouts as common
from . import overnight_relationship_capture as capture
from . import overnight_relationship_behavior as behavior
from . import overnight_relationship_readouts as study
from . import relationship_targets as target
from .datasets import digest

ROLE = 'posthoc_discovery_overnight_relationship_behavior_link_v1'
MODELS = {'llama8b': ('meta-llama/Llama-3.1-8B-Instruct',24),
          'codellama34b': ('codellama/CodeLlama-34b-Instruct-hf',36)}
SITES = (3,7,8)
SEEDS = (11,29,47)
MAX_BANK = 256*1024**2
MAX_RESULT = 32*1024**2
LIMITATION = (
    'Posthoc adaptive discovery on the same nine familiar structural components. '
    'Decoded correctness is an external readout measurement, not evidence that '
    'the model naturally uses that information or that it causes an answer. '
    'Conditional associations do not validate an unfamiliar-program predictor. '
    'Computed/literal formats also change operations, tokens and positions. '
    'Weighting seeds, lexical twins, numeric draws and query siblings are not '
    'independent replications. Other slots can be answer ancestors. Query is '
    'future text at sites3/7, so slot/recency differences are not query effects. '
    'Intervals condition on saved fits, omit refitting and multiplicity correction.'
)


def protocol():
    return dict(primary_layers={key:value[1] for key,value in MODELS.items()},sites=list(SITES),
        seeds=list(SEEDS),backends=['hidden','surface'],development_cases_per_model=2430,
        literal_development_cases=1944,computed_development_cases=486,
        generated_responses_validated_per_model=7290,selected_score_banks=72,
        joint_aggregation='Average binary joint masses over fits before deriving conditional ratios.',
        component_aggregation='Equal component masses; sub-strata retain zero masses in unrepresented components.',
        strata=['overall','query_slot','numeric_seed','response_validity'],
        bootstrap=dict(draws=2000,seed=117,minimum_valid_draws=1900),
        query_diagnostic='Same literal body and fixed target slot; queried minus other queries, sites7/8 and difference; retain4x4tables.',
        graph_site3='undefined; omitted',posthoc=True)


def _config(config):
    required={'evaluation_role','declared_plan','declared_plan_sha256','run_dir','report','models'}
    if not isinstance(config,dict) or set(config)!=required or config.get('evaluation_role')!=ROLE:
        raise ValueError('exact posthoc score/behavior discovery configuration required')
    if not isinstance(config.get('models'),dict) or set(config['models'])!=set(MODELS):raise ValueError('both fixed cached model contracts required')
    def checksum(value):
        return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)
    if not checksum(config['declared_plan_sha256']):raise ValueError('explicit plan SHA256 required')
    sources=[config['declared_plan']]
    for key in MODELS:
        spec=config['models'][key]
        paths={panel+'_'+kind for panel in ('literal','computed','behavior') for kind in ('config','completion')}
        expected=paths|{name+'_sha256' for name in paths}
        if not isinstance(spec,dict) or set(spec)!=expected:raise ValueError('six pinned model configuration/receipt paths required')
        for name in paths:
            if not checksum(spec[name+'_sha256']):raise ValueError('explicit input SHA256 required')
            sources.append(spec[name])
    for path in [*sources,config['run_dir'],config['report']]:bounded._safe(path)
    if len(common._json_bytes(config))>16*1024:raise ValueError('bounded analysis configuration required')
    out,report=Path(config['run_dir']).resolve(),Path(config['report']).resolve()
    reserved={out/name for name in ('registration.json','results_v1.json','summary.json','audit.json','completion_manifest_v1.json')}
    if (report.suffix!='.md' or report==out or report in reserved or any(path in report.parents for path in reserved)
            or any(out==Path(path).resolve() or out in Path(path).resolve().parents or report==Path(path).resolve() for path in sources)):
        raise ValueError('analysis outputs cannot replace sources or reserved artifacts')


def _pin(path):
    path=bounded._safe(path)
    return dict(path=str(path),sha256=bounded._sha(path),bytes=path.stat().st_size)


def _entry(entry,path,maximum=MAX_BANK,read=False):
    path=bounded._safe(path)
    if (not isinstance(entry,dict) or set(entry)!={'path','sha256','bytes'}
            or Path(entry['path']).resolve()!=path.resolve() or type(entry['bytes']) is not int
            or not 0<entry['bytes']<=maximum or path.stat().st_size!=entry['bytes']
            or not isinstance(entry['sha256'],str) or len(entry['sha256'])!=64
            or any(c not in '0123456789abcdef' for c in entry['sha256'])):
        raise ValueError('bounded exact original artifact inventory required')
    if read:
        payload=bounded._bytes(path,maximum)
        if hashlib.sha256(payload).hexdigest()!=entry['sha256']:raise ValueError('original artifact checksum differs before parsing')
        return payload


def _pinned_json(entry,path):
    result=json.loads(_entry(entry,path,16*1024**2,read=True))
    if not isinstance(result,dict):raise ValueError('original metadata object required')
    return result


def _readout(config,receipt,records,cap,model,layer,panel):
    study._config(config)
    if config['panel']!=panel or config['primary_layer']!=layer:raise ValueError('fixed original panel/primary layer differs')
    if (receipt.get('status')!='complete_exploratory' or receipt.get('evaluation_role')!=study.ROLE
            or receipt.get('config_hash')!=digest(config) or receipt.get('factorizations')!=45
            or receipt.get('parameter_replay_rows')!=45*5832 or receipt.get('new_model_queries')!=0
            or receipt.get('generated_holdouts_opened') is not False):raise ValueError('complete original readout receipt required')
    bounded._verify_source(config,receipt['analysis_source'])
    folder=Path(config['run_dir']);artifacts=receipt['artifacts']
    expected={common._name(backend,block,site,seed):folder/(common._name(backend,block,site,seed)+'.npz')
        for site in SITES for backend,block in [('hidden',i) for i in cap['layers']]+[('surface',-1)] for seed in SEEDS}
    if 'transfer_from' in config:expected.update({name+'_literal_transfer':folder/(name+'_literal_transfer.npz') for name in list(expected)})
    expected.update(registration=folder/'registration.json',results=folder/'results_v1.json',audit=folder/'audit.json',report=Path(config['report']))
    if set(artifacts)!=set(expected):raise ValueError('original readout inventory differs')
    for name,path in expected.items():_entry(artifacts[name],path,MAX_BANK if path.suffix=='.npz' else 128*1024**2)
    registration=_pinned_json(artifacts['registration'],expected['registration'])
    audit=_pinned_json(artifacts['audit'],expected['audit'])
    chosen=[row for row in records if panel in row['cohorts'] and row['source_form']==('computed' if panel=='computed_roots' else 'literal')]
    if (len(chosen)!=5832 or registration.get('config')!=config or registration.get('config_hash')!=digest(config)
            or registration.get('evaluation_role')!=study.ROLE or registration.get('analysis_source')!=receipt['analysis_source']
            or registration.get('model')!=model or registration.get('protocol')!=study.protocol()
            or registration.get('selected_case_ids')!=[row['id'] for row in chosen]
            or audit.get('status')!='passed' or audit.get('exact_parameter_replays') is not True
            or audit.get('config_hash')!=digest(config)):
        raise ValueError('original source, score-case or replay certification differs')
    capture_receipt=_pinned_json(registration['capture_completion'],Path(cap['run_dir'])/'completion_manifest_v1.json')
    if (capture_receipt.get('status')!='complete_exploratory' or capture_receipt.get('evaluation_role')!=capture.ROLE
            or capture_receipt.get('config_hash')!=digest(cap) or capture_receipt.get('model')!=model
            or capture_receipt.get('dataset_sha256')!=cap['dataset_sha256'] or capture_receipt.get('cases')!=16038):
        raise ValueError('original union capture metadata differs')
    selected={name:artifacts[name] for site in SITES for backend,block in [('hidden',layer),('surface',-1)]
        for seed in SEEDS for name in [common._name(backend,block,site,seed)]}
    return dict(config=config,receipt=receipt,records=chosen,selected=selected)


def _inputs(config):
    _config(config)
    if hashlib.sha256(bounded._bytes(config['declared_plan'],1024**2)).hexdigest()!=config['declared_plan_sha256']:
        raise ValueError('declared score/behavior plan changed')
    result={};datasets={}
    for key,(model,layer) in MODELS.items():
        spec=config['models'][key]
        configs={kind:bounded._json(spec[kind+'_config'],spec[kind+'_config_sha256']) for kind in ('literal','computed','behavior')}
        receipts={kind:bounded._json(spec[kind+'_completion'],spec[kind+'_completion_sha256']) for kind in configs}
        caps=[]
        for kind,cfg in configs.items():
            if Path(spec[kind+'_completion']).resolve()!=(Path(cfg['run_dir'])/'completion_manifest_v1.json').resolve():
                raise ValueError('fixed original completion path differs')
            caps.append(bounded._json(cfg['capture_config'],cfg['capture_config_sha256']))
        cap=caps[0];capture._config(cap)
        if any(value!=cap for value in caps[1:]) or cap['model']!=model:raise ValueError('one matching model/union capture required')
        dataset=bounded._safe(cap['dataset']);dataset_key=(str(dataset.resolve()),cap['dataset_sha256'])
        if dataset_key not in datasets:
            payload=bounded._bytes(dataset,256*1024**2)
            if hashlib.sha256(payload).hexdigest()!=cap['dataset_sha256']:raise ValueError('source union checksum changed')
            rows=[]
            for line in payload.splitlines():
                row=json.loads(line);capture._validate_row(row);rows.append(capture._record(row))
            if len(rows)!=16038 or len({row['id'] for row in rows})!=16038:raise ValueError('complete unique original union required')
            datasets[dataset_key]=rows
        rows=datasets[dataset_key]
        panels={kind:_readout(configs[kind],receipts[kind],rows,cap,model,layer,
            'query_twins' if kind=='literal' else 'computed_roots') for kind in ('literal','computed')}
        bcfg=configs['behavior'];behavior._config(bcfg);receipt=receipts['behavior'];folder=Path(bcfg['run_dir'])
        if (receipt.get('status')!='complete_exploratory' or receipt.get('evaluation_role')!=behavior.ROLE
                or receipt.get('config_hash')!=digest(bcfg) or receipt.get('cases')!=7290
                or receipt.get('generated_holdouts_opened') is not False):raise ValueError('complete original behavior receipt required')
        bounded._verify_source(bcfg,receipt['source'])
        expected={'registration':folder/'registration.json','manifest':folder/'manifest.json','summary':folder/'summary.json',
            'responses':folder/'responses.jsonl','report':Path(bcfg['report'])}
        if set(receipt['artifacts'])!=set(expected):raise ValueError('exact behavior artifact inventory required')
        for name,path in expected.items():_entry(receipt['artifacts'][name],path,128*1024**2,read=True)
        registration=_pinned_json(receipt['artifacts']['registration'],expected['registration'])
        manifest=_pinned_json(receipt['artifacts']['manifest'],expected['manifest'])
        if registration.get('config')!=bcfg or registration.get('source')!=receipt['source'] or manifest.get('identity')!=registration or manifest.get('status')!='complete':
            raise ValueError('original behavior registration/manifest differs')
        cases=[{'record':row} for row in rows if row['numeric_draw']==0]
        observed=behavior.read_responses(expected['responses'],cases,repair=False)
        if bounded._sha(expected['responses'])!=receipt['artifacts']['responses']['sha256']:
            raise ValueError('behavior response bytes changed during identity validation')
        if len(observed)!=7290:raise ValueError('all original response identities and scoring must validate')
        dev={row['id']:row for row in observed if row['split']=='development'}
        if len(dev)!=2430:raise ValueError('exact DEV-only behavior join required')
        for info in panels.values():
            chosen=[row for row in info['records'] if row['split']=='development' and row['numeric_draw']==0]
            if any(row['id'] not in dev for row in chosen):raise ValueError('missing exact behavior/probe ID match')
        source_folders=[Path(cfg['run_dir']).resolve() for cfg in [*configs.values(),cap]]
        source_files=[Path(cfg[name]).resolve() for cfg in configs.values() for name in ('report','declared_plan')]
        source_files.append(dataset.resolve())
        out,report=Path(config['run_dir']).resolve(),Path(config['report']).resolve()
        if (any(out==folder or out in folder.parents or folder in out.parents or report==folder or folder in report.parents for folder in source_folders)
                or report in source_files or any(out==path or out in path.parents for path in source_files)):
            raise ValueError('analysis outputs cannot overlap original workers')
        result[key]=dict(model=model,layer=layer,panels=panels,behavior=dev,
            original_response_cases_validated=len(observed),source_dataset=dict(path=str(dataset),sha256=cap['dataset_sha256']))
    return result


def load_scores(entry,full_ids,indices,bundle,config_hash):
    """Hash exact bounded bank bytes, then open scores and identity arrays only."""
    payload=_entry(entry,entry['path'],MAX_BANK,read=True)
    with np.load(io.BytesIO(payload),allow_pickle=False) as saved:
        if str(saved['config_hash'].item())!=config_hash or tuple(saved['case_ids'].tolist())!=tuple(full_ids):
            raise ValueError('original score configuration or ordered case IDs differ')
        if (not np.array_equal(saved['targets'][indices],bundle.y,equal_nan=True)
                or not np.array_equal(saved['target_mask'][indices],bundle.mask)):
            raise ValueError('saved DEV target identities differ from source')
        scores=saved['real_scores'][indices].copy()
    if (scores.dtype!=np.float64 or scores.shape!=bundle.y.shape or not np.isfinite(scores[bundle.mask]).all()
            or not np.isnan(scores[~bundle.mask]).all()):raise ValueError('complete finite saved scores required')
    return scores


def _binary_fits(value,n):
    value=np.asarray(value,dtype=float)
    if value.shape!=(3,n) or not np.isin(value,[0,1]).all():raise ValueError('three complete binary correctness fits required')
    return value


def _interval(numerator,denominator,draws):
    point_denominator=float(denominator.mean());valid=denominator[draws].mean(axis=1)>0
    estimates=numerator[draws].mean(axis=1)[valid]/denominator[draws].mean(axis=1)[valid]
    return dict(point=float(numerator.mean()/point_denominator) if point_denominator>0 else None,
        conditional_group_bootstrap_95=np.quantile(estimates,[.025,.975]).tolist() if valid.sum()>=1900 else None,
        point_denominator=point_denominator,valid_draws=int(valid.sum()),invalid_draws=int((~valid).sum()),
        status='qualified_conditional_interval' if valid.sum()>=1900 else 'unqualified_denominator')


def joint_summary(answer,valid_response,value_fits,groups,*,graph_fits=None,parent_fits=None,selected=None):
    """Fit-average JOINT masses, normalize within components, then take ratios."""
    answer=np.asarray(answer);valid_response=np.asarray(valid_response);groups=np.asarray(groups)
    n=len(answer)
    if (answer.shape!=(n,) or valid_response.shape!=(n,) or groups.shape!=(n,)
            or not np.isin(answer,[0,1]).all() or not np.isin(valid_response,[0,1]).all()
            or np.any(answer>valid_response)):raise ValueError('valid binary answer/response identities required')
    names=sorted(set(groups.tolist()))
    if len(names)!=9:raise ValueError('all nine DEV components required')
    mask=np.ones(n,dtype=bool) if selected is None else np.asarray(selected)
    if mask.shape!=(n,) or mask.dtype!=np.bool_:raise ValueError('exact stratum mask required')
    value=_binary_fits(value_fits,n)
    events={'queried_value':value}
    if graph_fits is not None:
        graph=_binary_fits(graph_fits,n);events.update(graph=graph,graph_and_queried_value=graph*value)
    if parent_fits is not None:events['queried_parent']=_binary_fits(parent_fits,n)
    draws=np.random.default_rng(117).integers(0,9,size=(2000,9))
    def masses(row_values):
        return np.array([np.mean(np.asarray(row_values)[groups==name]*mask[groups==name]) for name in names])
    support=masses(np.ones(n));a=masses(answer);invalid=masses(1-valid_response)
    result=dict(cases=int(mask.sum()),components=names,
        component_case_counts={name:int(np.sum(mask&(groups==name))) for name in names},
        answer_accuracy=_interval(a,support,draws),invalid_response_fraction=_interval(invalid,support,draws),events={})
    for key,fits in events.items():
        c=fits.mean(axis=0);ac=(fits*answer[None,:]).mean(axis=0)
        c_mass,ac_mass=masses(c),masses(ac);wrong=masses(1-answer)
        result['events'][key]=dict(
            decoding_correct=_interval(c_mass,support,draws),
            decoding_correct_and_answer_wrong=_interval(c_mass-ac_mass,support,draws),
            answer_correct_given_decoding_correct=_interval(ac_mass,c_mass,draws),
            answer_correct_given_decoding_incorrect=_interval(a-ac_mass,support-c_mass,draws),
            decoding_correct_given_answer_wrong=_interval(c_mass-ac_mass,wrong,draws),
            fit_averaged_condition_sum=float(c[mask].sum()))
    result.update(graph_defined=graph_fits is not None,bootstrap=protocol()['bootstrap'],
        aggregation=protocol()['component_aggregation'],joint_fits_averaged_first=True)
    return result


def query_diagnostic(records,correctness):
    """Hold body and target head fixed while changing only the actual query."""
    if set(correctness)!=set(SITES):raise ValueError('all three fixed query checkpoints required')
    n=len(records);by_body={}
    for i,row in enumerate(records):
        if row['split']!='development' or row['source_form']!='literal':raise ValueError('literal DEV query twins required')
        body=by_body.setdefault(row['surface_body_id'],{})
        if row['query_slot'] in body:raise ValueError('duplicate query twin')
        body[row['query_slot']]=i
    bodies=[];groups=[]
    for body in by_body.values():
        if set(body)!={0,1,2,3}:raise ValueError('complete four-query bodies required')
        chosen=[body[i] for i in range(4)]
        if (len({records[i]['component_id'] for i in chosen})!=1
                or len({records[i]['source'].rsplit('\n',1)[0] for i in chosen})!=1):
            raise ValueError('query twins must have identical source bodies and components')
        bodies.append(chosen);groups.append(records[chosen[0]]['component_id'])
    groups=np.asarray(groups);names=sorted(set(groups.tolist()))
    if len(names)!=9:raise ValueError('nine DEV query components required')
    indices=np.asarray(bodies);draws=np.random.default_rng(117).integers(0,9,size=(2000,9))
    def estimate(values):
        component=np.array([np.mean(values[groups==name],axis=0) for name in names])
        return dict(point=np.mean(component,axis=0).tolist(),
            conditional_group_bootstrap_95=np.quantile(component[draws].mean(axis=1),[.025,.975],axis=0).tolist(),
            valid_draws=2000,invalid_draws=0)
    sites={};effects={}
    for site in SITES:
        fits=np.asarray(correctness[site],dtype=float)
        if fits.shape!=(3,n,4) or not np.isin(fits,[0,1]).all():raise ValueError('three fits of all four value-head correctness required')
        matrix=fits.mean(axis=0)[indices]  # body, actual query, fixed target slot
        diagonal=np.diagonal(matrix,axis1=1,axis2=2)
        effect=diagonal-(matrix.sum(axis=1)-diagonal)/3
        effects[site]=effect
        sites[str(site)]=dict(query_by_target_matrix=estimate(matrix),fixed_slot_effect=estimate(effect),
            mean_slot_effect=estimate(effect.mean(axis=1)),
            within_body_target_correctness_disagreement_fraction=float(np.mean(np.ptp(matrix,axis=1)>0)))
    difference=effects[8]-effects[7]
    return dict(status='posthoc_descriptive',literal_cases=n,bodies=len(bodies),components=names,
        sites=sites,site8_minus_site7=dict(fixed_slot_effect=estimate(difference),mean_slot_effect=estimate(difference.mean(axis=1))),
        query_axis='actual query0..3',target_axis='fixed target slot0..3',
        causal_use_established=False,other_slots_are_not_necessarily_irrelevant=True,
        bootstrap=protocol()['bootstrap'])


def _analyze(info):
    panels={};selected={};saved_rows=0
    for panel,p in info['panels'].items():
        indices=np.array([i for i,row in enumerate(p['records']) if row['split']=='development' and row['numeric_draw']==0])
        records=[p['records'][i] for i in indices]
        expected=1944 if panel=='literal' else 486
        if len(records)!=expected:raise ValueError('exact DEV score/behavior panel coverage required')
        answers=np.array([info['behavior'][row['id']]['correct'] for row in records],dtype=bool)
        valid=np.array([info['behavior'][row['id']]['parsed'] is not None for row in records])
        groups=np.array([row['component_id'] for row in records]);queries=np.array([row['query_slot'] for row in records])
        numeric=np.array([row['numeric_seed'] for row in records]);cells={};query_values={'hidden':{},'surface':{}}
        for site in SITES:
            bundle=study.targets(records,site)
            for backend,layer in [('hidden',info['layer']),('surface',-1)]:
                values=[];graphs=[];parents=[];all_values=[]
                for seed in SEEDS:
                    name=common._name(backend,layer,site,seed);entry=p['selected'][name]
                    scores=load_scores(entry,[row['id'] for row in p['records']],indices,bundle,digest(p['config']))
                    selected[panel+'/'+name]=entry;saved_rows+=len(p['records'])
                    equality=target.categorical_value_predictions(bundle,scores)==bundle.numeric_truth
                    all_values.append(equality);values.append(equality[np.arange(len(records)),queries])
                    if site!=3:
                        correct=target.reconstruct_parent_graph(bundle,scores)['parent_predictions']==bundle.parent_truth
                        graphs.append(correct.all(axis=1));parents.append(correct[np.arange(len(records)),queries])
                arrays=dict(graph_fits=np.asarray(graphs) if graphs else None,parent_fits=np.asarray(parents) if parents else None)
                strata={'overall':np.ones(len(records),dtype=bool)}
                strata.update({'query/'+str(q):queries==q for q in (0,1,2,3)})
                strata.update({'numeric_seed/'+str(seed):numeric==seed for seed in (101,211,307)})
                strata.update({'response/valid':valid,'response/invalid':~valid})
                cells[backend+'/site'+str(site)]={name:joint_summary(answers,valid,np.asarray(values),groups,
                    selected=mask,**arrays) for name,mask in strata.items()}
                for cell in cells[backend+'/site'+str(site)].values():
                    cell['value_reference']='initialization_binding' if site==3 else 'final_binding_for_actual_query'
                if panel=='literal':query_values[backend][site]=np.asarray(all_values)
                print(f'behavior link {info["model"]} {panel} {backend} site{site}',flush=True)
        panels[panel]=dict(cases=len(records),components=sorted(set(groups.tolist())),cells=cells,
            queried_value_semantics='Current value of the queried variable at the checkpoint; site3 is its initialization value, not necessarily the final answer.')
        if panel=='literal':panels[panel]['query_diagnostics']={name:query_diagnostic(records,values) for name,values in query_values.items()}
    return dict(model=info['model'],primary_layer=info['layer'],cases=2430,
        original_responses_validated=info['original_response_cases_validated'],panels=panels,
        selected_score_banks=selected,saved_score_rows_read=saved_rows)


def _source(config,scheduled):
    _config(config)
    if scheduled:
        bounded._slurm();return bounded._current_source(config)
    registration=bounded._json(Path(config['run_dir'])/'registration.json')
    if registration.get('config')!=config or registration.get('config_hash')!=digest(config):raise ValueError('analysis registration differs')
    bounded._verify_source(config,registration['source']);return registration['source']


def _report(result):
    lines=['# Posthoc relationship decoding and answer behavior','',LIMITATION,'',
        'All rows below are DEV, joined by exact ID. Conditional probabilities use fit-averaged joint masses. Undefined graph checkpoints are omitted.','',
        '| Model | Form | Backend / site | Answer correct | Graph correct | Value correct | Graph correct and answer wrong |',
        '|---|---|---|---:|---:|---:|---:|']
    def percent(entry):return 'undefined' if entry is None or entry['point'] is None else f'{100*entry["point"]:.3f}%'
    for key,model in result['models'].items():
        for form,panel in model['panels'].items():
            for name,cells in panel['cells'].items():
                c=cells['overall'];g=c['events'].get('graph');v=c['events']['queried_value']
                lines.append(f'| {key} | {form} | {name} | {percent(c["answer_accuracy"])} | {percent(g["decoding_correct"] if g else None)} | {percent(v["decoding_correct"])} | {percent(g["decoding_correct_and_answer_wrong"] if g else None)} |')
    lines+=['','Queried value means its current checkpoint value. At site3 this is the initialization value, not necessarily the final answer.',
        '', '| Model | Backend | Site7 placebo | Site8 query effect | Site8 minus7 |','|---|---|---:|---:|---:|']
    for key,model in result['models'].items():
        for backend,diagnostic in model['panels'].get('literal',{}).get('query_diagnostics',{}).items():
            lines.append(f'| {key} | {backend} | {100*diagnostic["sites"]["7"]["mean_slot_effect"]["point"]:.3f} pp | {100*diagnostic["sites"]["8"]["mean_slot_effect"]["point"]:.3f} pp | {100*diagnostic["site8_minus_site7"]["mean_slot_effect"]["point"]:.3f} pp |')
    lines+=['','The machine result retains every query/numeric-seed/validity cell, support, conditional denominator and valid/invalid bootstrap count, plus the full4×4 within-body query tables and fixed-slot contrasts. Invalid responses remain wrong. Other slots can be answer ancestors.','',
        'No new model queries, fits, parameter predictions or hidden-state array reads were performed. Original score banks and generated responses remain unchanged.','']
    return '\n'.join(lines)


def run(config):
    from .confidence import _run_lock
    source=_source(config,True);inputs=_inputs(config);folder=Path(config['run_dir']);folder.mkdir(parents=True,exist_ok=True)
    with _run_lock(folder):
        if (folder/'completion_manifest_v1.json').exists():
            result=_audited_result(config);_logging_summary(config,result);return result
        registration=dict(evaluation_role=ROLE,config=config,config_hash=digest(config),source=source,
            protocol=protocol(),posthoc=True,new_model_queries=0,new_fits=0,parameter_replays=0,
            raw_activations_loaded=False,generated_holdouts_opened=False)
        bounded._put(folder/'registration.json',registration)
        models={key:_analyze(info) for key,info in inputs.items()}
        result=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
            protocol=protocol(),models=models,development_cases=4860,original_responses_validated=14580,
            new_model_queries=0,new_fits=0,parameter_replays=0,raw_activations_loaded=False,
            generated_holdouts_opened=False,limitation=LIMITATION)
        payload=common._json_bytes(result)
        if len(payload)>MAX_RESULT:raise ValueError('bounded joint/conditional result required')
        common.immutable(folder/'results_v1.json',payload);common.immutable(config['report'],_report(result).encode())
        review=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),development_cases=4860,
            original_responses_validated=14580,selected_score_banks=sum(len(m['selected_score_banks']) for m in models.values()),
            new_model_queries=0,new_fits=0,parameter_replays=0,raw_activations_loaded=False,generated_holdouts_opened=False)
        bounded._put(folder/'audit.json',review)
        artifacts={name:_pin(path) for name,path in {'registration':folder/'registration.json','results':folder/'results_v1.json',
            'audit':folder/'audit.json','report':Path(config['report'])}.items()}
        bounded._put(folder/'completion_manifest_v1.json',dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),
            source=source,artifacts=artifacts,protocol=protocol(),new_model_queries=0,new_fits=0,
            parameter_replays=0,raw_activations_loaded=False,generated_holdouts_opened=False))
        _logging_summary(config,result)
        return result


def _logging_summary(config,result):
    bounded._put(Path(config['run_dir'])/'summary.json',dict(status='complete_exploratory',evaluation_role=ROLE,
        config_hash=digest(config),development_cases=result['development_cases'],original_responses_validated=result['original_responses_validated'],
        models=sorted(result['models']),report=config['report'],derived_logging_summary=True,new_model_queries=0,new_fits=0,
        parameter_replays=0,raw_activations_loaded=False,generated_holdouts_opened=False))


def _audited_result(config):
    source=_source(config,False);inputs=_inputs(config)
    folder=Path(config['run_dir']);receipt=bounded._json(folder/'completion_manifest_v1.json')
    if (receipt.get('status')!='complete_exploratory' or receipt.get('evaluation_role')!=ROLE or receipt.get('config_hash')!=digest(config)
            or receipt.get('source')!=source or receipt.get('protocol')!=protocol()
            or any(receipt.get(key)!=0 for key in ('new_model_queries','new_fits','parameter_replays'))
            or receipt.get('raw_activations_loaded') is not False or receipt.get('generated_holdouts_opened') is not False):
        raise ValueError('matching analysis receipt required')
    expected={'registration':folder/'registration.json','results':folder/'results_v1.json','audit':folder/'audit.json','report':Path(config['report'])}
    if set(receipt['artifacts'])!=set(expected):raise ValueError('exact analysis artifact inventory required')
    published={key:_entry(receipt['artifacts'][key],path,MAX_RESULT,read=True) for key,path in expected.items()}
    registration=json.loads(published['registration']);review=json.loads(published['audit'])
    if (registration.get('evaluation_role')!=ROLE or registration.get('config')!=config
            or registration.get('config_hash')!=digest(config) or registration.get('source')!=source
            or registration.get('protocol')!=protocol()
            or any(registration.get(key)!=0 for key in ('new_model_queries','new_fits','parameter_replays'))
            or registration.get('raw_activations_loaded') is not False or registration.get('generated_holdouts_opened') is not False):
        raise ValueError('complete original analysis registration required')
    if (review.get('status')!='passed' or review.get('evaluation_role')!=ROLE or review.get('config_hash')!=digest(config)
            or review.get('development_cases')!=4860 or review.get('original_responses_validated')!=14580
            or review.get('selected_score_banks')!=72):raise ValueError('complete original analysis audit required')
    result=json.loads(published['results'])
    if (result.get('status')!='complete_exploratory' or result.get('evaluation_role')!=ROLE
            or result.get('protocol')!=protocol() or result.get('generated_holdouts_opened') is not False
            or result.get('config_hash')!=digest(config) or result.get('source')!=source
            or result.get('development_cases')!=4860 or result.get('new_model_queries')!=0
            or result.get('original_responses_validated')!=14580 or set(result.get('models',{}))!=set(MODELS)
            or result.get('new_fits')!=0 or result.get('parameter_replays')!=0 or result.get('raw_activations_loaded') is not False):
        raise ValueError('complete unchanged behavior-link result required')
    for key,model in result['models'].items():
        selected={panel+'/'+name:entry for panel,info in inputs[key]['panels'].items() for name,entry in info['selected'].items()}
        if model.get('cases')!=2430 or len(selected)!=36 or model.get('selected_score_banks')!=selected:
            raise ValueError('exact original selected score inventory required')
        for entry in model['selected_score_banks'].values():
            _entry(entry,entry['path'],MAX_BANK)
            if bounded._sha(entry['path'])!=entry['sha256']:raise ValueError('original selected score bank changed')
    return result


def audit(config):
    result=_audited_result(config)
    return dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),development_cases=result['development_cases'],
        original_responses_validated=result['original_responses_validated'],new_model_queries=0,new_fits=0,parameter_replays=0,
        additional_array_loads=0,raw_activations_loaded=False,generated_holdouts_opened=False)
