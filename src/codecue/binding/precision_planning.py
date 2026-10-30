"""Conditional structural-group precision scenarios from consumed discovery OOF.

The empirical group distribution is a planning assumption, not new independent
structures. The toolkit never refits a model, queries a checkpoint, selects a
winning cohort size, or opens original final/extrapolation outcomes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

from .datasets import digest, read_jsonl
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable, sha

ROLE='conditional_structural_precision_planning_v1'
LIMITATION=(
    'Conditional planning scenarios from previously observed discovery-template '
    'losses. Resampling empirical templates does not create new structures or '
    'independent scientific replications. Projected detection probabilities use '
    'a centered empirical null and are not guaranteed confirmatory power. '
    'They omit model refitting, feature/penalty selection and pilot-distribution '
    'uncertainty. No cohort size or positive result is selected automatically.'
)


def _options(config):
    counts=config.get('component_counts',[24,48,72,96,144,240])
    effects=config.get('effect_scenarios',[0.,.001,.0025,.005,.01])
    draws=config.get('draws',2000);seed=config.get('seed',117);alpha=config.get('alpha',.05)
    stratify=config.get('stratify',True)
    if (not isinstance(counts,list) or not counts or len(set(counts))!=len(counts)
            or any(type(value) is not int or value<2 for value in counts)):
        raise ValueError('declare distinct structural component counts of at least two')
    if (not isinstance(effects,list) or not effects or len(set(effects))!=len(effects)
            or any(isinstance(value,bool) or not isinstance(value,(int,float)) or not np.isfinite(value) for value in effects)):
        raise ValueError('declare distinct finite effect scenarios')
    if type(draws) is not int or draws<100 or type(seed) is not int or seed<0:
        raise ValueError('at least 100 simulation draws and a nonnegative integer seed required')
    if isinstance(alpha,bool) or not isinstance(alpha,(int,float)) or not 0<alpha<.5 or type(stratify) is not bool:
        raise ValueError('declare alpha in (0,.5) and a boolean stratification rule')
    return counts,list(map(float,effects)),draws,seed,float(alpha),stratify


def simulate(groups,config):
    """Resample complete independent group means, never individual example rows.

    Each input row is {group_id, stratum, value}. The future design is balanced
    across declared strata. A common effect shift is applied to the centered
    empirical group distribution; all effects share the same Monte Carlo draws.
    """
    counts,effects,draws,seed,alpha,stratify=_options(config)
    groups=list(groups)
    if not groups or len({str(row['group_id']) for row in groups})!=len(groups):
        raise ValueError('supply exactly one value per distinct structural group')
    strata=defaultdict(list)
    for row in sorted(groups,key=lambda item:str(item['group_id'])):
        value=row['value']
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not np.isfinite(value):
            raise ValueError('finite paired group-mean loss differences required')
        stratum=str(row.get('stratum','all')) if stratify else 'all'
        strata[stratum].append(float(value))
    if any(count%len(strata) for count in counts):
        raise ValueError('candidate component counts must permit balanced whole-group strata')
    arrays={key:np.asarray(values,dtype=float) for key,values in sorted(strata.items())}
    pilot=float(np.mean([values.mean() for values in arrays.values()]))
    centered={key:values-values.mean() for key,values in arrays.items()}
    reason=None
    if len(groups)<2 or any(len(values)<2 for values in arrays.values()):
        reason='fewer than two independent pilot components in a required stratum'
    elif not any(np.ptp(values)>0 for values in arrays.values()):
        reason='no within-stratum pilot dispersion; finite-sample certainty cannot be inferred'
    rows=[]
    for count in counts:
        per_stratum=count//len(strata)
        if reason is None:
            rng=np.random.default_rng(np.random.SeedSequence([seed,count]))
            errors=np.mean([values[rng.integers(0,len(values),size=(draws,per_stratum))].mean(axis=1)
                            for values in centered.values()],axis=0)
            critical=float(np.quantile(errors,1-alpha))
        for effect in effects:
            row={'component_count':count,'components_per_stratum':per_stratum,
                 'effect_scenario':effect,'eligible':reason is None,
                 'projection_interval_level':1-alpha,'simulation_draws':draws,
                 'estimator_mean':None,'estimator_quantiles':None,'projection_half_width':None,
                 'empirical_null_critical_difference':None,'probability_estimate_positive':None,
                 'conditional_one_sided_detection_probability':None,'detection_monte_carlo_se':None}
            if reason is None:
                estimates=effect+errors
                quantiles=np.quantile(estimates,[alpha/2,.5,1-alpha/2]).tolist()
                probability=float(np.mean(estimates>critical))
                row.update(estimator_mean=float(estimates.mean()),estimator_quantiles=quantiles,
                    projection_half_width=float((quantiles[2]-quantiles[0])/2),
                    empirical_null_critical_difference=critical,
                    probability_estimate_positive=float(np.mean(estimates>0)),
                    conditional_one_sided_detection_probability=probability,
                    detection_monte_carlo_se=float(np.sqrt(probability*(1-probability)/draws)))
            rows.append(row)
    return {'status':'conditional_scenarios' if reason is None else 'ineligible_pilot',
        'eligible':reason is None,'ineligibility_reason':reason,'pilot_groups':len(groups),
        'strata_counts':{key:len(values) for key,values in arrays.items()},
        'pilot_balanced_group_mean_difference':pilot,'stratified':stratify,
        'estimand':'equally weighted mean of structural-group means within balanced strata',
        'null_centering':'within each fixed stratum' if stratify else 'pooled pilot group mean',
        'rows':rows,'seed':seed,'alpha':alpha,
        'detection_rule':'shifted future estimator exceeds the fixed centered empirical-null (1-alpha) quantile',
        'common_random_numbers_across_effect_scenarios':True,
        'source_partition_seeds_are_replications':False,'model_refits':0,
        'limitation':LIMITATION}


def _object(path):
    value=json.loads(Path(path).read_text())
    if not isinstance(value,dict):raise ValueError('metadata must be an object')
    _discovery_declaration(value)
    return value


def _pinned(path,expected,name):
    if not expected or sha(path)!=expected:raise ValueError(name+' checksum changed or is unpinned')


def _metadata(config):
    """Validate both source chains completely before opening any OOF payload."""
    _options(config);_discovery_declaration(config)
    for name in ('comparison','source_config'):_discovery_response_path(config[name])
    _pinned(config['source_config'],config.get('source_config_sha256'),'comparison configuration')
    source=_object(config['source_config'])
    _pinned(config['comparison'],config.get('comparison_sha256'),'completed comparison')
    comparison=_object(config['comparison'])
    if (comparison.get('status')!='complete_exploratory' or comparison.get('complete') is not True
            or comparison.get('generated_holdouts_opened') is not False
            or comparison.get('mechanism_C_fitted') is not False
            or comparison.get('config_hash')!=digest(source)
            or Path(source.get('comparison_artifact','')).resolve()!=Path(config['comparison']).resolve()
            or len(source.get('runs',{}))!=2 or set(source['runs'])!=set(comparison.get('models',{}))):
        raise ValueError('matching completed two-checkpoint discovery controls required')
    contrasts=config.get('contrasts')
    if (not isinstance(contrasts,list) or not contrasts
            or any(not isinstance(pair,dict) or set(pair)!={'left','right'} or pair['left']==pair['right'] for pair in contrasts)
            or len({(pair['left'],pair['right']) for pair in contrasts})!=len(contrasts)):
        raise ValueError('predeclare distinct directed predictor contrasts')
    metrics=config.get('metrics',['brier_score','log_loss'])
    if (not isinstance(metrics,list) or not metrics or len(set(metrics))!=len(metrics)
            or not set(metrics)<={'brier_score','log_loss'}):
        raise ValueError('predeclare Brier and/or log-loss planning metrics')
    chains={};common=None
    for name,spec in source['runs'].items():
        _discovery_response_path(spec['config']);_pinned(spec['config'],spec.get('sha256'),'predictive run configuration')
        run=_object(spec['config'])
        for key in ('feature_manifest','feature_table','review_artifact'):_discovery_response_path(run[key])
        _pinned(run['feature_manifest'],run.get('feature_manifest_sha256'),'feature manifest')
        manifest=_object(run['feature_manifest'])
        if (run.get('feature_profile')!='capacity_oracle_v1'
                or manifest.get('status')!='passed'
                or manifest.get('evaluation_role')!='discovery_failure_prediction_controls_v1'
                or manifest.get('generated_holdouts_opened') is not False
                or manifest.get('target_outcomes_used_as_features') is not False
                or not manifest.get('source_dataset_sha256')
                or (run.get('feature_table_sha256') is not None
                    and run['feature_table_sha256']!=manifest.get('sha256'))
                or manifest.get('source_model')!=run.get('model')
                or manifest.get('source_model_revision')!=run.get('model_revision')):
            raise ValueError('only pinned discovery capacity-control features are eligible')
        review_hash=comparison.get('review_checksums',{}).get(run['review_artifact'])
        _pinned(run['review_artifact'],review_hash,'predictive review')
        review=_object(run['review_artifact'])
        if (review!=comparison['models'][name] or review.get('status')!='complete_exploratory'
                or review.get('config_hash')!=digest(run)
                or review.get('feature_manifest_sha256')!=run['feature_manifest_sha256']
                or review.get('feature_table_sha256')!=manifest.get('sha256')
                or review.get('generated_holdouts_opened') is not False
                or review.get('mechanism_C_fitted') is not False):
            raise ValueError('predictive review identity differs from completed discovery comparison')
        plan=review.get('analysis_plan',{});seeds=plan.get('seeds')
        if (plan.get('feature_profile')!='capacity_oracle_v1' or not isinstance(seeds,list) or not seeds
                or len(set(seeds))!=len(seeds) or any(type(seed) is not int for seed in seeds)):
            raise ValueError('recorded fixed discovery partition seeds required')
        pairs={tuple(pair) for pair in plan.get('comparisons',[])}
        if any((pair['left'],pair['right']) not in pairs for pair in contrasts):
            raise ValueError('planning contrast was not registered in the source analysis')
        if any(pair[key] not in plan.get('predictors',{}) for pair in contrasts for key in ('left','right')):
            raise ValueError('planning predictor absent from source analysis')
        artifacts=review.get('artifacts',{});oof=artifacts.get('oof_predictions',{})
        if not oof.get('sha256') or not oof.get('path'):raise ValueError('pinned OOF artifact required')
        _discovery_response_path(oof['path'])
        if Path(oof['path']).resolve().parent!=Path(run['output_dir']).resolve():
            raise ValueError('OOF artifact must belong to its registered discovery run')
        registration=_object(Path(run['output_dir'])/'registration.json')
        if registration.get('config')!=run or registration.get('config_hash')!=digest(run):
            raise ValueError('predictive analysis registration differs')
        identity=(manifest.get('source_dataset_sha256'),plan)
        if common is not None and identity!=common:raise ValueError('checkpoint source banks or analysis plans differ')
        common=identity
        chains[name]={'run':run,'manifest':manifest,'review':review,'oof':oof,
            'review_sha256':review_hash,'config_sha256':spec['sha256']}
    return comparison,chains,contrasts,metrics


def _loss(probability,label,metric):
    if metric=='brier_score':return (probability-label)**2
    safe=min(1-1e-12,max(1e-12,probability))
    return -(label*np.log(safe)+(1-label)*np.log1p(-safe))


def collect(config):
    """Build independent template-level paired loss summaries from pinned OOF."""
    comparison,chains,contrasts,metrics=_metadata(config)
    series=[];provenance={}
    for name,chain in chains.items():
        run=chain['run'];manifest=chain['manifest'];review=chain['review']
        _pinned(run['feature_table'],manifest.get('sha256'),'discovery feature payload')
        features=read_jsonl(run['feature_table']);by_id={row['id']:row for row in features}
        if len(by_id)!=len(features) or len(features)!=manifest.get('n') or len(features)!=review.get('n'):
            raise ValueError('feature target identities or count differ')
        levels={};labels={}
        for row in features:
            group=str(row['template_id']);level=row['available_bindings']
            if (row.get('original_split') not in ('train','development') or row['label'] not in (0,1)
                    or level not in (2,4) or group in levels and levels[group]!=level):
                raise ValueError('invalid discovery feature label, split or group stratum')
            levels[group]=level;labels[row['id']]=row['label']
        if len(levels)!=manifest.get('groups') or len(levels)!=review.get('templates'):
            raise ValueError('source structural group count differs')
        oof=chain['oof'];_pinned(oof['path'],oof['sha256'],'OOF payload')
        records=read_jsonl(oof['path']);seeds=review['analysis_plan']['seeds'];lookup={}
        for row in records:
            key=row['seed'],row['id'];source=by_id.get(row['id'])
            if (key in lookup or source is None or row['seed'] not in seeds
                    or row['label']!=labels[row['id']] or str(row['template_id'])!=str(source['template_id'])
                    or set(row['predictions'])!=set(review['analysis_plan']['predictors'])
                    or any(isinstance(p,bool) or not isinstance(p,(int,float)) or not np.isfinite(p) or not 0<=p<=1 for p in row['predictions'].values())):
                raise ValueError('OOF identity, labels, probabilities or seed coverage differ')
            lookup[key]=row
        if set(lookup)!={(seed,identity) for seed in seeds for identity in by_id}:
            raise ValueError('every discovery target must have one OOF record per fixed seed')
        for pair in contrasts:
            for metric in metrics:
                grouped=defaultdict(list)
                for identity,row in sorted(by_id.items()):
                    left=float(np.mean([lookup[seed,identity]['predictions'][pair['left']] for seed in seeds]))
                    right=float(np.mean([lookup[seed,identity]['predictions'][pair['right']] for seed in seeds]))
                    grouped[str(row['template_id'])].append(_loss(left,row['label'],metric)-_loss(right,row['label'],metric))
                groups=[{'group_id':group,'stratum':levels[group],'value':float(np.mean(values)),
                         'target_examples':len(values)} for group,values in sorted(grouped.items())]
                series.append({'checkpoint':name,'left':pair['left'],'right':pair['right'],'metric':metric,
                    'targets':len(by_id),'partition_seeds':seeds,'ensemble':'fixed mean probability before scoring',
                    'groups':groups})
        provenance[name]={'config_sha256':chain['config_sha256'],'review_sha256':chain['review_sha256'],
            'feature_manifest_sha256':run['feature_manifest_sha256'],'feature_table_sha256':manifest['sha256'],
            'oof_sha256':oof['sha256'],'targets':len(by_id),'structural_components':len(levels),
            'partition_seeds':seeds,'partition_seeds_treated_as_replications':False}
    return {'status':'collected_discovery_groups','series':series,'provenance':provenance,
        'comparison_sha256':config['comparison_sha256'],
        'source_config_sha256':config['source_config_sha256'],'generated_holdouts_opened':False}


def run(config):
    """Export all registered scenarios without selecting a confirmatory cohort size."""
    source=collect(config)
    from .registry import code_identity
    result={'status':'complete_conditional_planning','complete':True,'evaluation_role':ROLE,
        'config_hash':digest(config),'analysis_source':code_identity(),
        'source_comparison_sha256':source['comparison_sha256'],
        'source_config_sha256':source['source_config_sha256'],'provenance':source['provenance'],
        'scenarios':[],'generated_holdouts_opened':False,'new_model_queries':0,
        'confirmatory_sample_size_selected':False,'limitation':LIMITATION}
    flattened=[]
    for series in source['series']:
        projection=simulate(series['groups'],config)
        label={key:series[key] for key in ('checkpoint','left','right','metric','targets')}
        result['scenarios'].append({**series,'projection':projection})
        for row in projection['rows']:flattened.append({**label,**row})
    stream=io.StringIO();fields=list(flattened[0]);writer=csv.DictWriter(stream,fieldnames=fields)
    writer.writeheader();writer.writerows(flattened)
    lines=['# Conditional structural-cohort precision planning','',LIMITATION,'',
        'All scenarios use whole structural-component means. Original partition seeds are averaged into one OOF probability per target before loss is scored; they are not additional groups. Strata, when enabled, remain balanced in each simulated future cohort.','',
        '| Checkpoint | Left | Right | Metric | Pilot groups | Pilot mean difference | Eligible |',
        '|---|---|---|---|---:|---:|---|']
    for scenario in result['scenarios']:
        projection=scenario['projection']
        lines.append(f"| {scenario['checkpoint']} | {scenario['left']} | {scenario['right']} | {scenario['metric']} | {projection['pilot_groups']} | {projection['pilot_balanced_group_mean_difference']:+.6f} | {projection['eligible']} |")
    lines+=['','## Complete effect and component-count matrix','',
        'Effects are hypothetical future mean improvements, not newly measured effects. Detection means exceeding the centered empirical-null (1−alpha) quantile. It is a conditional simulation result, not guaranteed statistical power or a recommendation to begin confirmation. Degenerate pilots retain every row with ineligible/null projections.','',
        '| Checkpoint | Metric | Left → right | Components | Scenario effect | Projection half-width | Conditional detection probability |',
        '|---|---|---|---:|---:|---:|---:|']
    for row in flattened:
        width='ineligible' if row['projection_half_width'] is None else f"{row['projection_half_width']:.6f}"
        detection='ineligible' if row['conditional_one_sided_detection_probability'] is None else f"{row['conditional_one_sided_detection_probability']:.4f}"
        lines.append(f"| {row['checkpoint']} | {row['metric']} | {row['left']} → {row['right']} | {row['component_count']} | {row['effect_scenario']:+.6f} | {width} | {detection} |")
    lines+=['','No final/extrapolation outcomes, model loading, new model responses, language-model training or final cohort selection were performed. Fresh independently generated structures and a supported scientific claim remain prerequisites for genuine confirmation.','']
    csv_path=Path(config['csv']);report=Path(config['report']);review=Path(config['review_artifact'])
    data={csv_path:stream.getvalue().encode(),report:'\n'.join(lines).encode()}
    result['outputs']={key:{'path':str(path),'sha256':hashlib.sha256(data[path]).hexdigest()} for key,path in [('csv',csv_path),('report',report)]}
    data[review]=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
    for path,content in data.items():
        if path.exists() and path.read_bytes()!=content:raise ValueError('immutable precision artifact differs: '+str(path))
    for path,content in data.items():immutable(path,content)
    return {'status':result['status'],'series':len(result['scenarios']),'scenario_rows':len(flattened),
        'report':str(report),'review_artifact':str(review),'confirmatory_sample_size_selected':False}
