"""Posthoc source-oracle-assisted identity diagnostics from saved DEV scores.

Only the original identity/scores/random_scores NPZ members are opened. Existing
parameters are never read or applied. Real-task diagnostics use source maps only
after predictions are fixed; the prefix-sham task retains its separate labels.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import diversity_readouts as original
from . import diversity_targets as target
from . import schedule_score_review as saved
from . import relationship_capture as bounded
from . import relationship_readouts as publication
from . import overnight_relationship_capture as durable
from .datasets import digest
from .discovery_readouts import group_weights

ROLE='discovery_diversity_identity_review_v1'
SOURCE_SNAPSHOT='345f75b01f5c3b33bd0ca6d8'
SOURCE_SHA='9cfa6c42fd79ddb9a4f049650ba311bb996dcb9f48afb9f9c31a2cc22254a918'
DATA_SHA='d43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1'
SITES=(3,7,8)
SEEDS=(17,29,43)
REAL_METHODS=('direct','training_prior')
METHODS=saved.METHODS
FAMILIES=saved.FAMILIES
COMPLETION='completion_manifest_v1.json'
MAX_RICH=192*1024**2
MAX_COMPACT=8*1024**2
LIMITATIONS=[
    'Adaptive posthoc discovery after the Llama8B aggregate outcomes were inspected; no untouched replication, reliability qualification or historical gate rescue.',
    'Predicted statement indices are converted to owner/version identities with source-oracle maps. These postmetrics are oracle-assisted diagnostics, not independently learned full bindings.',
    'Current-definition status is evaluated at the capture checkpoint; parent referents are evaluated immediately before the consuming assignment.',
    'Scalar-version heads are separate from mapped statement heads. Agreement can be jointly wrong and does not establish correct ownership or natural causal use.',
    'Every site, layer, weighting seed, target slot and class is retained. Category and metric denominators exclude undefined targets and retain missing/invalid defined predictions as errors.',
    'Fifteen DEV graph families have96dependent numeric/rotation/lexical/query relatives each. Class frequencies differ; seeds are dependent estimator variants and no new interval is computed.',
    'Prefix-sham scores are verified and reported on their original separate task; no source-oracle real-task error partition is assigned to sham predictions.',
    'Per-family rates pool four head decisions; they are distinct from whole-state AND accuracy in the original study.',
    'No activation, feature, coefficient or normalization arrays are loaded; no parameters are applied or fitted and no model/tokenizer is queried.',
]


def _core():
    from . import binding_identity_diagnostics
    return binding_identity_diagnostics


def _bytes(value):return publication._json_bytes(value)
def _same(left,right):return _bytes(left)==_bytes(right)
def _pin(path):return saved._pin(path)
def _read(path,expected=None,limit=MAX_COMPACT):return saved._read(path,expected,limit=limit)


def _config(config):
    fields={'evaluation_role','readout_configs','declared_plan','declared_plan_sha256','run_dir','report'}
    if (not isinstance(config,dict) or set(config)!=fields or config.get('evaluation_role')!=ROLE
            or len(_bytes(config))>16*1024 or not saved._sha(config.get('declared_plan_sha256'))):
        raise ValueError('exact bounded posthoc identity-review configuration required')
    sources=config['readout_configs']
    if (not isinstance(sources,list) or len(sources)!=2 or any(not isinstance(item,dict)
            or set(item)!={'path','sha256'} or not isinstance(item['path'],str)
            or not saved._sha(item['sha256']) for item in sources)):
        raise ValueError('two SHA-pinned original diversity readout configurations required')
    inputs=[bounded._safe(item['path']).resolve() for item in sources]
    if len(set(inputs))!=2:raise ValueError('source configurations must be distinct')
    for key in ('declared_plan','run_dir','report'):
        if not isinstance(config[key],str) or not config[key]:raise ValueError('explicit discovery paths required')
        bounded._safe(config[key])
    out,report,plan=(Path(config[key]).resolve() for key in ('run_dir','report','declared_plan'))
    inputs.append(plan)
    reserved=[out/name for name in ('registration.json','results_v1.json','summary.json','audit.json',
                                   'progress.json',COMPLETION,'prediction_replay_review_v1.json')]
    if (report.suffix!='.md' or report==out or report in out.parents
            or (out.exists() and not out.is_dir()) or (report.exists() and not report.is_file())
            or any(p==report or p in report.parents for p in reserved)
            or any(out in p.parents and p.suffix in ('.npz','.json') for p in report.parents)
            or any(out==p or out in p.parents or p in out.parents
                   or report==p or report in p.parents or p in report.parents for p in inputs)):
        raise ValueError('identity-review inputs and output artifacts cannot overlap')
    return config


def _source(config,scheduled):
    _config(config)
    if scheduled:
        bounded._slurm();return bounded._current_source(config)
    registration=_read(Path(config['run_dir'])/'registration.json')
    if registration.get('evaluation_role')!=ROLE or registration.get('config')!=config:
        raise ValueError('original identity-review registration differs')
    source=registration['source'];bounded._verify_source(config,source)
    return source


def _expected(folder,layers):
    paths={original._CORE._name(backend,layer,site,seed):
        folder/(original._CORE._name(backend,layer,site,seed)+'.npz')
        for site in SITES for backend,layer in [('hidden',layer) for layer in layers]+[('surface',-1)] for seed in SEEDS}
    return paths


def _metadata(config,scheduled):
    source=_source(config,scheduled)
    if not _same(target.COLUMNS,saved.target.COLUMNS) or not _same(target.HEADS,saved.target.HEADS):
        raise ValueError('saved-score prediction helper must use the identical original232-column/head schema')
    if bounded._sha(config['declared_plan'])!=config['declared_plan_sha256']:
        raise ValueError('declared posthoc identity plan differs')
    models={};pins=[_pin(config['declared_plan'])]
    for item in config['readout_configs']:
        cfg=_read(item['path'],item['sha256'],16*1024)
        old_source,checked,records=original._metadata(cfg,scheduled=False)
        if (cfg.get('evaluation_role')!=original.ROLE or cfg.get('primary_layer')!=24
                or old_source['snapshot_id']!=SOURCE_SNAPSHOT or old_source['source_sha256']!=SOURCE_SHA
                or checked['source']!=old_source or checked['dataset_sha256']!=DATA_SHA):
            raise ValueError('the fixed originalS3 diversity source/configuration is required')
        if checked['model'] not in saved.PROFILES:raise ValueError('supported cached model profile required')
        model,revision,layers,width=saved.PROFILES[checked['model']]
        if (model in models or checked['model_revision']!=revision or checked['layers']!=layers
                or checked['feature_shape']!=[5760,3,4,width]):
            raise ValueError('original two-model capture geometry differs')
        folder=Path(cfg['run_dir']);receipt=_read(folder/COMPLETION)
        if (receipt.get('evaluation_role')!=original.ROLE or receipt.get('status')!='complete_exploratory'
                or receipt.get('schema_version')!=1 or receipt.get('config_hash')!=digest(cfg)
                or receipt.get('fit_source')!=old_source or receipt.get('capture_source')!=checked['source']
                or (receipt.get('fit_banks'),receipt.get('factorizations'),receipt.get('parameter_replay_rows'))!=(45,45,259200)
                or receipt.get('new_model_queries')!=0 or receipt.get('generated_holdouts_opened') is not False):
            raise ValueError('complete original45-bank diversity receipt required before score access')
        expected=_expected(folder,layers)
        expected.update(registration=folder/'registration.json',results=folder/'results_v1.json',
                        summary=folder/'summary.json',audit=folder/'audit.json',report=Path(cfg['report']))
        inventory=receipt.get('artifacts',{})
        if set(inventory)!=set(expected):raise ValueError('exact original50-artifact inventory required')
        for name,path in expected.items():
            entry=inventory[name]
            if (not isinstance(entry,dict) or set(entry)!={'path','sha256','bytes'}
                    or Path(entry['path']).resolve()!=path.resolve() or not saved._sha(entry['sha256'])
                    or type(entry['bytes']) is not int or not 0<entry['bytes']<=512*1024**2):
                raise ValueError('original pinned artifact path/hash/size differs')
            out,report=Path(config['run_dir']).resolve(),Path(config['report']).resolve()
            source_path=path.resolve()
            if (out==source_path or out in source_path.parents or source_path in out.parents
                    or report==source_path or report in source_path.parents or source_path in report.parents):
                raise ValueError('new identity outputs cannot overlap any original scientific artifact')
        original_report_pin=_pin(expected['report'])
        if original_report_pin!=inventory['report']:
            raise ValueError('original completed report SHA/bytes differ')
        proof=_read(folder/'parameter_replay_review_v1.json')
        if (proof.get('evaluation_role')!=original.ROLE or proof.get('status')!='passed'
                or proof.get('config_hash')!=digest(cfg) or proof.get('source_artifacts')!=inventory
                or proof.get('fit_source')!=old_source or proof.get('capture_source')!=old_source
                or (proof.get('fit_banks'),proof.get('factorizations'),proof.get('parameter_replay_rows'))!=(45,45,259200)
                or proof.get('new_fits')!=0 or proof.get('new_model_queries')!=0
                or proof.get('generated_holdouts_opened') is not False
                or not all(proof.get(k) is True for k in ('exact_saved_parameter_score_replays',
                    'all_real_and_control_scores_replayed','all_scientific_metrics_recomputed',
                    'train_support_and_control_marginals_recomputed'))):
            raise ValueError('actual original parameter/metric replay proof required before score access')
        metadata={name:_read(path,inventory[name],MAX_RICH if name=='results' else MAX_COMPACT)
                  for name,path in expected.items() if name in ('registration','results','summary','audit')}
        if any(v.get('evaluation_role')!=original.ROLE or v.get('config_hash')!=digest(cfg)
               or v.get('new_model_queries')!=0 or v.get('generated_holdouts_opened') is not False for v in metadata.values()):
            raise ValueError('original metadata discovery/configuration identity differs')
        result=metadata['results']
        if (result.get('status')!='complete_exploratory' or result.get('fit_source')!=old_source
                or result.get('capture_source')!=old_source or result.get('model')!=checked['model']
                or result.get('dataset_sha256')!=DATA_SHA
                or (result.get('cases'),result.get('training_rows'),result.get('development_rows'),
                    result.get('training_groups'),result.get('development_groups'))!=(5760,4320,1440,45,15)
                or not _same(result.get('target_columns'),list(target.COLUMNS))
                or result.get('protocol')!=original.protocol()
                or not _same(metadata['summary'],original._summary(result))
                or metadata['registration'].get('config')!=cfg
                or metadata['registration'].get('fixed_recipe')!=original.protocol()
                or metadata['audit'].get('status')!='passed'):
            raise ValueError('completed original source/target/metric schema differs')
        fits={fit['name']:fit for fit in result['fits']}
        names={name for name,path in expected.items() if path.suffix=='.npz'}
        if len(result['fits'])!=45 or set(fits)!=names:raise ValueError('all45 original fixed score banks required')
        for name,fit in fits.items():
            if (fit['name']!=original._CORE._name(fit['backend'],fit['layer'],fit['site'],fit['seed'])
                    or Path(fit['artifact']).resolve()!=expected[name].resolve()
                    or fit['factorizations']!=1 or fit['exact_parameter_score_replay'] is not True):
                raise ValueError('original fit cell identity differs')
        ids=tuple(row['id'] for row in records)
        if len(ids)!=5760 or len(set(ids))!=5760:raise ValueError('unique original ordered case identities required')
        dev=np.flatnonzero([row['split']=='development' for row in records]);dev_records=[records[i] for i in dev]
        profiles=[row['profile_id'] for row in dev_records]
        if (len(dev)!=1440 or len({row['component_id'] for row in dev_records})!=15
                or set(profiles)!={'2_1_1_0','3_1_0_0','2_2_0_0'}):
            raise ValueError('all1440 DEV rows/15graphs/three profiles required')
        bodies=saved.matched_bodies(dev_records,360)
        for p in (folder.resolve(),Path(checked['config']['run_dir']).resolve()):
            out,report=Path(config['run_dir']).resolve(),Path(config['report']).resolve()
            if out==p or out in p.parents or p in out.parents or report==p or report in p.parents or p in report.parents:
                raise ValueError('new identity outputs cannot overlap original scientific source artifacts')
        models[model]=dict(config=cfg,checked=checked,records=records,ids=ids,dev=dev,
            dev_records=dev_records,profiles=profiles,bodies=bodies,fit_map=fits,inventory=inventory)
        pins += [_pin(item['path']),_pin(folder/COMPLETION),_pin(folder/'parameter_replay_review_v1.json')]
        pins += [_pin(expected[name]) for name in ('registration','results','summary','audit')]+[original_report_pin]
        pins += [_pin(cfg['capture_config']),_pin(Path(checked['config']['run_dir'])/COMPLETION),
                 _pin(Path(checked['config']['run_dir'])/'prepared_cases.jsonl'),
                 _pin(checked['config']['dataset']),_pin(Path(checked['config']['dataset']).with_suffix('.manifest.json'))]
    if set(models)!={'llama8b','codellama34b'} or models['llama8b']['ids']!=models['codellama34b']['ids']:
        raise ValueError('both distinct original models must share exact ordered source cases')
    return source,models,pins


def preflight(config):
    source,models,pins=_metadata(config,scheduled=True)
    return dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),source=source,
        models=2,score_banks=90,development_rows_per_bank=1440,graph_groups=15,
        original_source_snapshot=SOURCE_SNAPSHOT,input_pins=pins,
        saved_score_arrays_opened=False,activation_arrays_opened=False,coefficient_arrays_opened=False,
        new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False)


def _compact_stats(stats):
    fields=('n_total','n_defined','n_undefined','counts','rates','equal_graph_rates',
            'metric_counts','metric_denominators','metric_rates','equal_graph_metric_rates')
    return {key:stats[key] for key in fields if key in stats}


def _diagnostics(bundle,methods,groups,profiles,original_sham):
    diagnostics={method:_core().diagnostics(bundle,methods[method],groups=groups,profiles=profiles)
                 for method in REAL_METHODS}
    sham=saved.categorical_diagnostics(methods['random_prefix_control'],np.asarray(groups))
    for name,head in original_sham['categorical_heads'].items():
        actual=sham['heads'][name]
        if (head['n']!=actual['n'] or head['accuracy']!=actual['rate']
                or head['group_macro_accuracy']!=actual['group_macro_rate']):
            raise ValueError('preserved sham predictions differ from original separate-task accuracy')
    for family,whole in original_sham['whole_categorical_families'].items():
        actual=sham['whole_families'][family]
        if (whole['n']!=actual['n'] or whole['accuracy']!=actual['rate']
                or whole['group_macro_accuracy']!=actual['group_macro_rate']):
            raise ValueError('preserved sham whole-task outcomes differ from original scores')
    return dict(oracle_assisted_real_methods=diagnostics,
        sham_original_task=dict(scope='Original source-keyed random task; no real-truth oracle-assisted error partition.',
            categorical_heads=original_sham['categorical_heads'],
            whole_categorical_families=original_sham['whole_categorical_families'],
            preserved_prediction_metrics=sham))


def _cell_summary(diagnostics):
    return {method:{family:_compact_stats(stats) for family,stats in diagnostic['per_family'].items()}
            for method,diagnostic in diagnostics['oracle_assisted_real_methods'].items()}


def _prediction_identity(config,model,name,entry,identity,profiles):
    return dict(evaluation_role=ROLE,config_hash=digest(config),model=model,bank_name=name,
        input_bank=entry,original_score_identity_sha256=digest(identity),
        original_case_ids_sha256=digest(identity['case_ids']),
        opaque_original_feature_sha256=identity['features_sha256'],profile_ids_sha256=digest(profiles))


def _summary(result):
    primary={}
    for model in ('llama8b','codellama34b'):
        primary[model]={}
        for backend,layer in (('hidden',24),('surface',-1)):
            primary[model][backend]={}
            for site in (7,8):
                selected=[c for c in result['cells'] if (c['model'],c['backend'],c['layer'],c['site'])==(model,backend,layer,site)]
                if len(selected)!=3 or {c['seed'] for c in selected}!=set(SEEDS):raise ValueError('all fixed primary seeds required')
                points={}
                for method in REAL_METHODS:
                    points[method]={}
                    for family in FAMILIES:
                        stats=[cell['summary_methods'][method][family] for cell in selected]
                        rates={};equal={}
                        for metric in ('exact','owner_correct','version_number_equal'):
                            values=[s.get('metric_rates',{}).get(metric) for s in stats]
                            graph_values=[s.get('equal_graph_metric_rates',{}).get(metric) for s in stats]
                            rates[metric]=float(np.mean(values)) if all(v is not None for v in values) else None
                            equal[metric]=float(np.mean(graph_values)) if all(v is not None for v in graph_values) else None
                        points[method][family]=dict(metric_rates=rates,equal_graph_metric_rates=equal,
                            weighting_seeds=list(SEEDS),n_defined_per_seed=stats[0]['n_defined'],
                            scope='Four pooled head decisions per case; source-oracle-assisted for statement heads.')
                primary[model][backend][str(site)]=points
    return dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=result['config_hash'],
        score_banks=90,development_rows_per_bank=1440,development_prediction_rows=129600,
        saved_score_rows_checked=518400,graph_groups=15,source_oracle_assisted=True,primary=primary,
        new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False,
        activation_arrays_opened=False,coefficient_arrays_opened=False,limitations=LIMITATIONS)


def _report(result):
    summary=_summary(result)
    lines=['# Posthoc source-oracle-assisted binding identity diagnostics','',
        'All90 original saved-score banks reproduce their original metrics. Statements are mapped to owner/version identities using source-derived maps after predictions are fixed. This mapping is oracle-assisted.',
        '', 'The table uses the original layer24/site7 endpoint, averaging the three fixed weighting seeds. Rates pool four target heads per case. All sites/layers/seeds, profile/slot/group counts and scalar-version joint tables remain in the per-bank diagnostic artifacts.', '',
        '| Model | Backend | Method | Target | Exact identity/class (%) | Owner correct (%) | Version number equal (%) |',
        '|---|---|---|---|---:|---:|---:|']
    def point(value):return 'undefined' if value is None else f'{100*value:.3f}'
    for model in ('llama8b','codellama34b'):
        for backend in ('hidden','surface'):
            for method in REAL_METHODS:
                for family in FAMILIES:
                    p=summary['primary'][model][backend]['7'][method][family]['metric_rates']
                    lines.append('| '+' | '.join([model,backend,method,family,
                        point(p['exact']),point(p['owner_correct']),point(p['version_number_equal'])])+' |')
    lines+=['','Equal-graph rates, all category partitions and complete target-specific denominators are retained. Parent referents use the pre-consumer checkpoint, including a parent that becomes obsolete later. Prefix-sham accuracy is retained solely on its original separate task.','']
    lines+=['- '+item for item in LIMITATIONS]
    return '\n'.join(lines)+'\n'


def _publish_json(path,value):
    data=_bytes(value)
    if len(data)>MAX_COMPACT:raise ValueError('compact identity-review JSON exceeds8MiB; keep rich per-bank diagnostics separate')
    publication.immutable(path,data)


def run(config):
    from .confidence import _run_lock
    source,models,pins=_metadata(config,scheduled=True);out=Path(config['run_dir']);out.mkdir(parents=True,exist_ok=True)
    with _run_lock(out):
        if (out/COMPLETION).exists():
            previous=completed_result(config)
            if previous['source']!=source:raise ValueError('completed identity review belongs to another source')
            durable._journal(out/'progress.json',dict(status='complete',score_banks=90,new_fits=0,new_model_queries=0))
            return previous
        if not (out/'registration.json').exists() and (any(out.glob('predictions_*.npz')) or any(out.glob('diagnostics_*.json'))):
            raise ValueError('orphan identity outputs require their original registration')
        _publish_json(out/'registration.json',dict(evaluation_role=ROLE,config=config,config_hash=digest(config),
            source=source,input_pins=pins,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        cells=[];artifacts={};score_pins=[]
        for model,data in sorted(models.items()):
            records=data['records'];dev=data['dev'];train=np.array([r['split']=='train' for r in records])
            train_rows=[r for r,use in zip(records,train) if use]
            groups=np.array([r['component_id'] for r in data['dev_records']])
            bundles={site:target.targets(records,site) for site in SITES}
            controls={(site,seed):target.control_targets(records,site,seed) for site in SITES for seed in SEEDS}
            for name,fit in sorted(data['fit_map'].items()):
                bundle=bundles[fit['site']];control=controls[fit['site'],fit['seed']]
                weights=group_weights(train_rows,fit['seed']).astype(np.float64);entry=data['inventory'][name]
                real,sham,identity=saved.load_score_bank(fit['artifact'],entry,bundle,control,train,weights,digest(data['config']))
                prior=saved.verify_original_metrics(bundle,control,train,weights,dev,real,sham,fit)
                dev_bundle=target.subset(bundle,dev);dev_control=target.subset(control,dev)
                methods=dict(direct=saved.predictions(dev_bundle,real[dev]),
                    training_prior=saved.predictions(dev_bundle,prior[dev]),
                    random_prefix_control=saved.predictions(dev_control,sham[dev]))
                identity=_prediction_identity(config,model,name,entry,identity,data['profiles'])
                prediction_path=out/f'predictions_{model}_{name}.npz'
                saved._save_predictions(prediction_path,identity,data['dev_records'],data['bodies'],methods)
                prediction_pin=_pin(prediction_path)
                restored=saved._read_predictions(prediction_path,prediction_pin,identity,data['dev_records'],data['bodies'])
                diagnostics=_diagnostics(dev_bundle,restored,groups,data['profiles'],fit['metrics']['random_prefix_control'])
                diagnostic=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),
                    source_oracle_assisted=True,model=model,name=name,site=fit['site'],layer=fit['layer'],
                    backend=fit['backend'],seed=fit['seed'],original_metrics_exact=True,
                    prediction_bank=prediction_pin,**diagnostics)
                diagnostic_path=out/f'diagnostics_{model}_{name}.json';_publish_json(diagnostic_path,diagnostic)
                diagnostic_pin=_pin(diagnostic_path)
                artifacts['predictions_'+model+'_'+name]=prediction_pin
                artifacts['diagnostics_'+model+'_'+name]=diagnostic_pin;score_pins.append(entry)
                cells.append(dict(model=model,name=name,backend=fit['backend'],layer=fit['layer'],site=fit['site'],seed=fit['seed'],
                    prediction_bank=prediction_pin,diagnostic=diagnostic_pin,prediction_identity=identity,
                    original_score_bank=entry,original_metrics_exact=True,summary_methods=_cell_summary(diagnostics)))
                durable._journal(out/'progress.json',dict(status='running',score_banks=len(cells),planned_banks=90,
                    new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
                print(f'identity review {model} {name}',flush=True)
        if len(cells)!=90:raise ValueError('all90 original cells required')
        result=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
            original_source_snapshot=SOURCE_SNAPSHOT,source_oracle_assisted=True,score_banks=90,
            development_rows_per_bank=1440,development_prediction_rows=129600,saved_score_rows_checked=518400,
            cells=cells,input_pins=pins+score_pins,original_metrics_exact=True,
            new_fits=0,new_model_queries=0,parameters_reapplied=0,activation_arrays_opened=False,
            coefficient_arrays_opened=False,generated_holdouts_opened=False,limitations=LIMITATIONS)
        _publish_json(out/'results_v1.json',result);_publish_json(out/'summary.json',_summary(result))
        publication.immutable(config['report'],_report(result).encode())
        _publish_json(out/'audit.json',dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),
            score_banks=90,original_metrics_exact=True,prediction_banks_reopened_and_checked=True,
            source_oracle_assisted=True,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        artifacts.update({name:_pin(path) for name,path in [('registration',out/'registration.json'),('results',out/'results_v1.json'),
            ('summary',out/'summary.json'),('report',Path(config['report'])),('audit',out/'audit.json')]})
        _publish_json(out/COMPLETION,dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),
            source=source,score_banks=90,artifacts=artifacts,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False))
        durable._journal(out/'progress.json',dict(status='complete',score_banks=90,new_fits=0,new_model_queries=0))
        return result


def _output_paths(config):
    out=Path(config['run_dir']);expected={}
    for model,_,layers,_ in saved.PROFILES.values():
        for name in _expected(out,layers):
            expected['predictions_'+model+'_'+name]=out/f'predictions_{model}_{name}.npz'
            expected['diagnostics_'+model+'_'+name]=out/f'diagnostics_{model}_{name}.json'
    expected.update(registration=out/'registration.json',results=out/'results_v1.json',summary=out/'summary.json',
                    audit=out/'audit.json',report=Path(config['report']))
    return expected


def completed_result(config):
    source=_source(config,scheduled=False);out=Path(config['run_dir']);receipt=_read(out/COMPLETION)
    if (receipt.get('evaluation_role')!=ROLE or receipt.get('status')!='complete_exploratory'
            or receipt.get('config_hash')!=digest(config) or receipt.get('source')!=source
            or receipt.get('score_banks')!=90 or receipt.get('new_fits')!=0 or receipt.get('new_model_queries')!=0
            or receipt.get('parameters_reapplied')!=0 or receipt.get('generated_holdouts_opened') is not False):
        raise ValueError('complete matching identity-review receipt required')
    expected=_output_paths(config);inventory=receipt.get('artifacts',{})
    if set(inventory)!=set(expected):raise ValueError('exact90prediction/90diagnostic/fivemetadata inventory required')
    for name,path in expected.items():
        if _pin(path)!=inventory[name]:raise ValueError('immutable identity output changed')
    result=_read(out/'results_v1.json',inventory['results'])
    if (result.get('evaluation_role')!=ROLE or result.get('config_hash')!=digest(config)
            or result.get('source')!=source or result.get('score_banks')!=90 or len(result.get('cells',[]))!=90
            or result.get('new_fits')!=0 or result.get('new_model_queries')!=0 or result.get('parameters_reapplied')!=0):
        raise ValueError('completed identity result differs')
    return result


def audit(config):
    """Recompute all source-oracle partitions from prediction-only DEV outputs."""
    result=completed_result(config);_,models,_=_metadata(config,scheduled=False)
    expected={(model,name) for model,data in models.items() for name in data['fit_map']};observed=set()
    bundles={model:{site:target.targets(data['records'],site) for site in SITES} for model,data in models.items()}
    controls={model:{(site,seed):target.control_targets(data['records'],site,seed) for site in SITES for seed in SEEDS}
              for model,data in models.items()}
    for cell in result['cells']:
        key=cell['model'],cell['name']
        if key not in expected or key in observed:raise ValueError('duplicate or undeclared identity cell')
        observed.add(key);data=models[cell['model']];fit=data['fit_map'][cell['name']]
        if (cell['original_score_bank']!=data['inventory'][cell['name']]
                or cell['prediction_identity'].get('input_bank')!=cell['original_score_bank']
                or cell['prediction_identity'].get('config_hash')!=digest(config)
                or cell['prediction_identity'].get('profile_ids_sha256')!=digest(data['profiles'])):
            raise ValueError('identity prediction provenance differs')
        methods=saved._read_predictions(cell['prediction_bank']['path'],cell['prediction_bank'],cell['prediction_identity'],
                                       data['dev_records'],data['bodies'])
        bundle=target.subset(bundles[cell['model']][cell['site']],data['dev'])
        for method in METHODS:
            truth_bundle=target.subset(controls[cell['model']][cell['site'],cell['seed']],data['dev']) if method=='random_prefix_control' else bundle
            truth=saved.predictions(truth_bundle,np.zeros_like(truth_bundle.y))
            if not np.array_equal(methods[method]['truth'],truth['truth']) or not np.array_equal(methods[method]['valid'],truth['valid']):
                raise ValueError('preserved prediction truth/visibility differs from actual source')
        groups=np.array([r['component_id'] for r in data['dev_records']])
        diagnostic=_diagnostics(bundle,methods,groups,data['profiles'],fit['metrics']['random_prefix_control'])
        saved_diagnostic=_read(cell['diagnostic']['path'],cell['diagnostic'])
        if (any(not _same(saved_diagnostic[k],v) for k,v in diagnostic.items())
                or not _same(cell['summary_methods'],_cell_summary(diagnostic))
                or (cell['backend'],cell['layer'],cell['site'],cell['seed'])!=(fit['backend'],fit['layer'],fit['site'],fit['seed'])):
            raise ValueError('oracle-assisted diagnostics differ from saved predictions/source maps')
    if observed!=expected:raise ValueError('all90 identity cells required')
    if not _same(_read(Path(config['run_dir'])/'summary.json'),_summary(result)) or Path(config['report']).read_bytes()!=_report(result).encode():
        raise ValueError('identity summary/report differs from complete diagnostics')
    proof=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),source=result['source'],score_banks=90,
        prediction_rows=129600,all_oracle_assisted_diagnostics_recomputed=True,source_oracle_assisted=True,
        sham_original_task_kept_separate=True,original_score_banks_reopened=False,activation_arrays_opened=False,
        coefficient_arrays_opened=False,new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False)
    _publish_json(Path(config['run_dir'])/'prediction_replay_review_v1.json',proof)
    return proof
