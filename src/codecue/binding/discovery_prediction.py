"""Nested grouped failure baselines on already-consumed discovery data.

These are exploratory out-of-fold predictions, not frozen unfamiliar-program
confirmation or a mechanism C model. Every relative of a template stays in one
outer/inner fold. Neutral correctness is an explicitly oracle-graded extra query.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

import numpy as np

from .datasets import digest, read_jsonl
from .forecasting import (_discovery_declaration, _discovery_response_path,
                          fit_logistic, predict)
from .heldout import probability_scores
from .published_benchmarks import immutable, sha

ROLE='discovery_failure_prediction_features_v1'
PREDICTORS=('prior','A_input','A_neutral_raw','A_neutral_scored')
LIMITATION=(
    'Exploratory nested grouped cross-validation on previously consumed discovery '
    'data, not M5 confirmation or a frozen unfamiliar-program forecast. No '
    'mechanism C, confidence or internal measurement feature is fitted. Repeated '
    'fold seeds reuse the same data and are not independent replications. '
    'Bootstrap intervals condition on the saved OOF predictions and do not '
    'rerun feature collection, model fitting or hyperparameter selection. '
    'Raw neutral behavior uses one distinct extra query without its oracle '
    'correctness; the scored tier additionally requires the neutral reference '
    'oracle. Target response properties and correctness never enter features.'
)
CAPACITY_ORACLE_LIMITATION=(
    LIMITATION+' Capacity controls add fixed source-feature interactions. '
    'Source-oracle tiers additionally receive the program oracle value and '
    'its magnitude/sign without any target language-model response. On a '
    'source-oracle plus raw-neutral tier, neutral failure is a deterministic '
    'comparison of existing information, not a new observation; an increment '
    'can reflect the encoding capacity of the fitted function class.'
)


def _feature_profile(config=None):
    profile=(config or {}).get('feature_profile')
    if profile not in (None,'capacity_oracle_v1','confidence_access_v1','candidate_event_confidence_v1','joint_confidence_v1','stress_query_confidence_v1'):
        raise ValueError('unknown discovery feature profile')
    return profile


def _limitation(config=None):
    if _feature_profile(config)=='stress_query_confidence_v1':
        from .stress_prediction import LIMITATION as stress_limitation
        return stress_limitation
    if _feature_profile(config)=='joint_confidence_v1':
        from .joint_confidence import LIMITATION as joint_limitation
        return joint_limitation
    if _feature_profile(config)=='candidate_event_confidence_v1':
        from .candidate_prediction import LIMITATION as candidate_limitation
        return candidate_limitation
    if _feature_profile(config)=='confidence_access_v1':
        from .confidence_prediction import LIMITATION as confidence_limitation
        return confidence_limitation
    return CAPACITY_ORACLE_LIMITATION if _feature_profile(config) else LIMITATION


def predictor_columns(config=None):
    if _feature_profile(config)=='stress_query_confidence_v1':
        from .stress_prediction import predictor_columns as stress_columns
        return stress_columns(config)
    if _feature_profile(config)=='joint_confidence_v1':
        from .joint_confidence import predictor_columns as joint_columns
        return joint_columns(config)
    if _feature_profile(config)=='candidate_event_confidence_v1':
        from .candidate_prediction import predictor_columns as candidate_columns
        return candidate_columns(config)
    if _feature_profile(config)=='confidence_access_v1':
        from .confidence_prediction import predictor_columns as confidence_columns
        return confidence_columns(config)
    if _feature_profile(config)=='capacity_oracle_v1':
        from .discovery_controls import predictor_columns as control_columns
        return control_columns()
    from .discovery_features import INPUT_COLUMNS, NEUTRAL_RAW_COLUMNS, NEUTRAL_SCORED_COLUMNS
    return {'prior':[], 'A_input':list(INPUT_COLUMNS),
            'A_neutral_raw':list(INPUT_COLUMNS)+list(NEUTRAL_RAW_COLUMNS),
            'A_neutral_scored':list(INPUT_COLUMNS)+list(NEUTRAL_RAW_COLUMNS)+list(NEUTRAL_SCORED_COLUMNS)}


def predictor_comparisons(config=None):
    """Fixed reported contrasts; profile choice never depends on fit scores."""
    if _feature_profile(config)=='stress_query_confidence_v1':
        from .stress_prediction import predictor_comparisons as stress_comparisons
        return stress_comparisons(config)
    if _feature_profile(config)=='joint_confidence_v1':
        from .joint_confidence import predictor_comparisons as joint_comparisons
        return joint_comparisons(config)
    if _feature_profile(config)=='candidate_event_confidence_v1':
        from .candidate_prediction import predictor_comparisons as candidate_comparisons
        return candidate_comparisons(config)
    if _feature_profile(config)=='confidence_access_v1':
        from .confidence_prediction import predictor_comparisons as confidence_comparisons
        return confidence_comparisons(config)
    if _feature_profile(config)=='capacity_oracle_v1':
        names=tuple(predictor_columns(config))
        scientific=(
            ('A_input','A_interactions'),
            ('A_interactions','A_interactions_neutral_raw'),
            ('A_interactions','A_interactions_neutral_scored'),
            ('A_interactions','A_interactions_oracle'),
            ('A_interactions_oracle','A_interactions_oracle_neutral_raw'),
            ('A_interactions_oracle_neutral_raw','A_interactions_oracle_neutral_scored'),
            ('A_interactions_neutral_raw','A_interactions_neutral_scored'),
            ('A_interactions_neutral_raw','A_interactions_oracle_neutral_raw'),
            ('A_interactions_neutral_scored','A_interactions_oracle_neutral_scored'),
        )
        return tuple(('prior',name) for name in names if name!='prior')+scientific
    return (('prior','A_input'),('prior','A_neutral_raw'),('prior','A_neutral_scored'),
            ('A_input','A_neutral_raw'),('A_input','A_neutral_scored'),('A_neutral_raw','A_neutral_scored'))


def _feature_contract(config):
    from .discovery_features import INPUT_COLUMNS, NEUTRAL_RAW_COLUMNS, NEUTRAL_SCORED_COLUMNS
    if _feature_profile(config)=='stress_query_confidence_v1':
        from .stress_prediction import feature_contract as stress_contract
        return stress_contract(config)
    if _feature_profile(config)=='joint_confidence_v1':
        from .joint_confidence import feature_contract as joint_contract
        return joint_contract(config)
    if _feature_profile(config)=='candidate_event_confidence_v1':
        from .candidate_prediction import feature_contract as candidate_contract
        return candidate_contract(config)
    if _feature_profile(config)=='confidence_access_v1':
        from .confidence_prediction import feature_contract as confidence_contract
        return confidence_contract(config)
    if _feature_profile(config)=='capacity_oracle_v1':
        from .discovery_controls import ROLE as control_role, INTERACTION_COLUMNS, ORACLE_COLUMNS
        return control_role,dict(input=list(INPUT_COLUMNS),interaction=list(INTERACTION_COLUMNS),
            oracle=list(ORACLE_COLUMNS),neutral_raw=list(NEUTRAL_RAW_COLUMNS),
            neutral_scored=list(NEUTRAL_SCORED_COLUMNS))
    return ROLE,dict(input=list(INPUT_COLUMNS),neutral_raw=list(NEUTRAL_RAW_COLUMNS),
                     neutral_scored=list(NEUTRAL_SCORED_COLUMNS))


def _rows(rows):
    rows=sorted(list(rows),key=lambda row:row['id'])
    if not rows or len({row['id'] for row in rows})!=len(rows):
        raise ValueError('feature rows require nonempty unique target identities')
    groups={}
    for row in rows:
        if row['label'] not in (0,1):raise ValueError('binary failure labels required')
        if row['original_split'] not in ('train','development'):
            raise ValueError('discovery prediction cannot include final outcomes')
        if row['condition'] not in ('informative','misleading'):
            raise ValueError('only distinct transformed targets are eligible')
        if row['available_bindings'] not in (2,4):raise ValueError('unexpected binding stratum')
        group=str(row['template_id']);level=row['available_bindings']
        if group in groups and groups[group]!=level:raise ValueError('template crosses binding strata')
        groups[group]=level
        if row.get('reference_id')==row['id']:raise ValueError('neutral reference must be a distinct query')
    return rows,groups


def assign_folds(rows,n_folds=6,seed=17,groups=None):
    """Hash and round-robin template IDs within source-defined binding strata."""
    if type(n_folds) is not int or n_folds<2 or type(seed) is not int:
        raise ValueError('at least two folds and an integer seed required')
    # Assignments inspect only source-defined grouping metadata, never outcomes.
    levels={}
    for row in rows:
        group=str(row['template_id']);level=row['available_bindings']
        if level not in (2,4) or group in levels and levels[group]!=level:
            raise ValueError('template crosses or lacks a registered binding stratum')
        levels[group]=level
    selected=set(levels) if groups is None else set(map(str,groups))
    if not selected or not selected<=set(levels):raise ValueError('unknown or empty fold groups')
    strata=defaultdict(list)
    for group in selected:strata[levels[group]].append(group)
    if set(strata)!={2,4}:raise ValueError('both binding strata are required')
    result={}
    for level,members in sorted(strata.items()):
        if len(members)<n_folds or len(members)%n_folds:
            raise ValueError('binding-stratum template count must divide evenly across folds')
        ordered=sorted(members,key=lambda group:(digest([seed,'template_fold',level,group]),group))
        for index,group in enumerate(ordered):result[group]=index%n_folds
    return result


def fit_predict_columns(xtrain,ytrain,xtest,l2,*,max_iterations=100):
    """Train-only normalization, with an explicit deterministic single-class fallback."""
    if type(max_iterations) is not int or max_iterations < 1:
        raise ValueError('max_iterations must be a positive integer')
    xtrain=np.asarray(xtrain,dtype=float);xtest=np.asarray(xtest,dtype=float)
    ytrain=np.asarray(ytrain,dtype=float)
    if (xtrain.ndim!=2 or xtest.ndim!=2 or xtrain.shape[1]!=xtest.shape[1]
            or ytrain.shape!=(len(xtrain),) or not len(ytrain)
            or not np.isfinite(xtrain).all() or not np.isfinite(xtest).all()
            or not np.isin(ytrain,[0,1]).all()):
        raise ValueError('invalid fitting features or failure labels')
    fallback=len(np.unique(ytrain))<2 and xtrain.shape[1]>0
    if not xtrain.shape[1] or fallback:
        probability=float((ytrain.sum()+.5)/(len(ytrain)+1))
        model={'kind':'jeffreys_prior','probability':probability,'train_n':len(ytrain),
               'train_failures':int(ytrain.sum()),
               'fallback_reason':'single_class_training' if fallback else None}
        return model,np.full(len(xtest),probability),fallback
    model=fit_logistic(xtrain,ytrain,l2) if max_iterations==100 else fit_logistic(
        xtrain,ytrain,l2,max_iterations=max_iterations)
    model.update(kind='logistic',train_n=len(ytrain),train_failures=int(ytrain.sum()))
    return model,predict(model,xtest),False


def _matrix(rows,columns):
    if not columns:return np.zeros((len(rows),0),dtype=float)
    try:result=np.asarray([[row['features'][key] for key in columns] for row in rows],dtype=float)
    except (KeyError,TypeError,ValueError) as exc:raise ValueError('missing or nonnumeric declared feature') from exc
    if not np.isfinite(result).all():raise ValueError('nonfinite declared feature')
    return result


def _metrics(labels,probabilities):
    labels=np.asarray(labels,dtype=float)
    return {'n':len(labels),'failures':int(labels.sum()),
            'failure_rate':float(labels.mean()),**probability_scores(probabilities,labels)}


def _plan(config):
    profile=_feature_profile(config)
    seeds=config.get('seeds',[17,29,43]);outer=config.get('outer_folds',6);inner=config.get('inner_folds',5)
    grid=config.get('l2_grid',[.1,1.,10.,100.])
    if (not seeds or len(set(seeds))!=len(seeds) or any(type(seed) is not int for seed in seeds)
            or type(outer) is not int or outer<2 or type(inner) is not int or inner<2
            or not grid or len(set(grid))!=len(grid)
            or any(isinstance(value,bool) or not np.isfinite(value) or value<=0 for value in grid)):
        raise ValueError('declare unique integer seeds, folds and a positive ordered penalty grid')
    result={'seeds':list(seeds),'outer_folds':outer,'inner_folds':inner,'l2_grid':list(grid),
            'bootstrap_replicates':config.get('bootstrap_replicates',2000),
            'bootstrap_seed':config.get('bootstrap_seed',117),
            'predictors':predictor_columns(config),
            'selection':'minimum pooled inner-OOF Brier; ties use first declared l2; refit outer training only',
            'fold_assignment':'source-defined template binding strata, outcome-independent hash ordering',
            'inner_seed_rule':'outer_seed + 100000 * (outer_fold + 1)'}
    if profile:
        result['feature_profile']=profile
        result['comparisons']=[list(pair) for pair in predictor_comparisons(config)]
    if profile=='stress_query_confidence_v1':
        from .stress_prediction import NEW_PREDICTOR_MAX_ITERATIONS
        if config.get('new_predictor_max_iterations')!=NEW_PREDICTOR_MAX_ITERATIONS:
            raise ValueError('declare the fixed stress-tier numerical iteration allowance')
        result['new_predictor_max_iterations']=NEW_PREDICTOR_MAX_ITERATIONS
    return result


def predictor_max_iterations(config,name):
    """Keep every parent fit unchanged; extend only the five stress tiers."""
    if _feature_profile(config)=='stress_query_confidence_v1':
        from .stress_prediction import PAIRED_TIERS,NEW_PREDICTOR_MAX_ITERATIONS
        if name in {row[3] for row in PAIRED_TIERS}:
            if config.get('new_predictor_max_iterations')!=NEW_PREDICTOR_MAX_ITERATIONS:
                raise ValueError('declare the fixed stress-tier numerical iteration allowance')
            return NEW_PREDICTOR_MAX_ITERATIONS
    return 100


def run_grouped_cv(rows,config):
    rows,levels=_rows(rows);plan=_plan(config);columns=plan['predictors']
    names=tuple(columns)
    matrices={name:_matrix(rows,keys) for name,keys in columns.items()}
    labels=np.asarray([row['label'] for row in rows],dtype=float)
    row_groups=np.asarray([str(row['template_id']) for row in rows]);predictions=[];fits=[]
    for seed in plan['seeds']:
        assignment=assign_folds(rows,plan['outer_folds'],seed)
        oof={name:np.full(len(rows),np.nan) for name in names}
        for fold in range(plan['outer_folds']):
            test_groups=sorted(group for group,value in assignment.items() if value==fold)
            train_groups=sorted(set(levels)-set(test_groups))
            train=np.isin(row_groups,train_groups);test=~train
            inner_assignment=assign_folds(rows,plan['inner_folds'],seed+100000*(fold+1),train_groups)
            saved={'seed':seed,'outer_fold':fold,'train_groups':train_groups,'test_groups':test_groups,
                   'inner_assignments':inner_assignment,'predictors':{},'fallbacks':[]}
            for name in names:
                x=matrices[name];curves=[]
                max_iterations=predictor_max_iterations(config,name)
                penalties=[plan['l2_grid'][0]] if name=='prior' else plan['l2_grid']
                for penalty in penalties:
                    inner_oof=np.full(len(rows),np.nan);inner_models=[]
                    for inner_fold in range(plan['inner_folds']):
                        validation_groups=sorted(g for g,v in inner_assignment.items() if v==inner_fold)
                        fit_groups=sorted(set(train_groups)-set(validation_groups))
                        inner_train=np.isin(row_groups,fit_groups);validation=np.isin(row_groups,validation_groups)
                        model,probabilities,fallback=fit_predict_columns(x[inner_train],labels[inner_train],x[validation],penalty,max_iterations=max_iterations)
                        inner_oof[validation]=probabilities
                        inner_models.append({'inner_fold':inner_fold,'train_groups':fit_groups,
                            'validation_groups':validation_groups,'model':model,'fallback':fallback})
                        if fallback:saved['fallbacks'].append({'predictor':name,'l2':penalty,'inner_fold':inner_fold,'reason':'single_class_training'})
                    if not np.isfinite(inner_oof[train]).all():raise ValueError('inner OOF coverage incomplete')
                    score=probability_scores(inner_oof[train],labels[train])
                    curves.append({'l2':float(penalty),'brier_score':score['brier_score'],
                                   'log_loss':score['log_loss'],'inner_fits':inner_models})
                best=min(range(len(curves)),key=lambda index:(curves[index]['brier_score'],index))
                penalty=curves[best]['l2']
                model,probabilities,fallback=fit_predict_columns(x[train],labels[train],x[test],penalty,max_iterations=max_iterations)
                oof[name][test]=probabilities
                saved['predictors'][name]={'columns':columns[name],'selected_l2':penalty,
                    'inner_curves':curves,'model':model,'outer_single_class_fallback':fallback}
                if fallback:saved['fallbacks'].append({'predictor':name,'l2':penalty,'outer_fold':fold,'reason':'single_class_training'})
            fits.append(saved)
        if any(not np.isfinite(values).all() for values in oof.values()):raise ValueError('outer OOF coverage incomplete')
        for index,row in enumerate(rows):
            predictions.append({'id':row['id'],'template_id':str(row['template_id']),'seed':seed,
                'outer_fold':assignment[str(row['template_id'])],'label':int(row['label']),
                'predictions':{name:float(oof[name][index]) for name in names}})
    return {'oof_predictions':predictions,'fold_fits':fits,'summary':summarize(predictions,rows,config),
            'analysis_plan':plan}


def group_bootstrap_improvement(labels,left,right,groups,draws=2000,seed=117):
    """Positive loss(left)-loss(right) favors the right-hand predictor."""
    y=np.asarray(labels,dtype=float);left=np.asarray(left,dtype=float);right=np.asarray(right,dtype=float)
    probability_scores(left,y);probability_scores(right,y)
    if len(groups)!=len(y) or type(draws) is not int or draws<1 or type(seed) is not int:
        raise ValueError('valid groups, positive bootstrap count and integer seed required')
    membership=defaultdict(list)
    for index,group in enumerate(groups):membership[str(group)].append(index)
    clusters=[membership[group] for group in sorted(membership)]
    rng=np.random.default_rng(seed);indices=rng.integers(0,len(clusters),size=(draws,len(clusters)))
    sizes=np.asarray([len(cluster) for cluster in clusters],dtype=float)
    def logloss(p):
        safe=p.clip(1e-12,1-1e-12)
        return -(y*np.log(safe)+(1-y)*np.log1p(-safe))
    result={'n':len(y),'templates':len(clusters),'bootstrap_replicates':draws,'bootstrap_seed':seed,
            'resampling_unit':'template_id','conditional_on_saved_oof_probabilities':True,
            'refits_per_bootstrap_draw':0,'multiplicity_adjusted':False}
    differences={'brier_score':(left-y)**2-(right-y)**2,'log_loss':logloss(left)-logloss(right)}
    for name,values in differences.items():
        sums=np.asarray([values[cluster].sum() for cluster in clusters])
        means=sums[indices].sum(axis=1)/sizes[indices].sum(axis=1)
        result[name]={'mean':float(values.mean()),'exploratory_template_bootstrap_95':np.quantile(means,[.025,.975]).tolist()}
    return result


def _cells(rows,labels,probabilities):
    groups=defaultdict(list)
    for index,row in enumerate(rows):
        for axis in ('condition','query_role','available_bindings','original_split'):
            groups[axis,str(row[axis])].append(index)
        groups['joint',json.dumps([row[k] for k in ('condition','query_role','available_bindings','original_split')])].append(index)
    return [dict(axis=axis,value=value,templates=len({rows[i]['template_id'] for i in indices}),
                 **_metrics(labels[indices],probabilities[indices]))
            for (axis,value),indices in sorted(groups.items())]


def summarize(oof_predictions,rows,config):
    rows,levels=_rows(rows);plan=_plan(config);by_id={row['id']:row for row in rows};lookup={}
    names=tuple(plan['predictors'])
    for row in oof_predictions:
        key=row['seed'],row['id']
        if (key in lookup or row['id'] not in by_id or row['label']!=by_id[row['id']]['label']
                or str(row['template_id'])!=str(by_id[row['id']]['template_id'])
                or set(row['predictions'])!=set(names)):
            raise ValueError('OOF labels, identities or coverage differ')
        lookup[key]=row
    expected={(seed,row['id']) for seed in plan['seeds'] for row in rows}
    if set(lookup)!=expected:raise ValueError('OOF table must cover every target once per seed')
    labels=np.asarray([row['label'] for row in rows],dtype=float)
    by_seed={seed:{name:np.asarray([lookup[seed,row['id']]['predictions'][name] for row in rows]) for name in names} for seed in plan['seeds']}
    ensemble={name:np.mean([by_seed[seed][name] for seed in plan['seeds']],axis=0) for name in names}
    contexts=[('seed',seed,by_seed[seed]) for seed in plan['seeds']]+[('ensemble','mean_probability',ensemble)]
    results=[];contrasts=[]
    comparisons=predictor_comparisons(config)
    for scope,seed,probabilities in contexts:
        metrics={name:_metrics(labels,values) for name,values in probabilities.items()}
        cells={name:_cells(rows,labels,values) for name,values in probabilities.items()}
        results.append({'scope':scope,'seed':seed,'metrics':metrics,'cells':cells})
        for left,right in comparisons:
            contrasts.append({'scope':scope,'seed':seed,'left':left,'right':right,
                'positive_means':'right predictor improves on left',
                **group_bootstrap_improvement(labels,probabilities[left],probabilities[right],
                    [row['template_id'] for row in rows],plan['bootstrap_replicates'],plan['bootstrap_seed'])})
    return {'status':'complete_exploratory','n':len(rows),'templates':len(levels),'failures':int(labels.sum()),
            'per_seed_and_ensemble':results,'contrasts':contrasts,'analysis_plan':plan,
            'ensemble_method':'mean of the fixed seeded OOF probabilities per target, never label-weighted',
            'limitation':_limitation(config),'generated_holdouts_opened':False,'mechanism_C_fitted':False}


def load_features(config):
    """Reject reserved roles/paths/contracts before opening a feature payload."""
    role,contract=_feature_contract(config)
    _discovery_declaration(config)
    for key in ('feature_table','feature_manifest'):_discovery_response_path(config[key])
    manifest_path=Path(config['feature_manifest'])
    if not config.get('feature_manifest_sha256'):
        raise ValueError('pin the feature manifest checksum before fitting')
    if sha(manifest_path)!=config['feature_manifest_sha256']:
        raise ValueError('feature manifest checksum changed')
    manifest=json.loads(manifest_path.read_text())
    _discovery_declaration(manifest)
    if manifest.get('status')!='passed' or manifest.get('evaluation_role')!=role:
        raise ValueError('passed discovery feature manifest role required before payload access')
    if manifest.get('columns')!=contract:raise ValueError('registered feature column contract differs')
    for key,field in (('model','source_model'),('model_revision','source_model_revision')):
        if config.get(key) and config[key]!=manifest.get(field):raise ValueError('feature checkpoint identity differs')
    declared=config.get('feature_table_sha256') or manifest.get('sha256')
    if not declared or declared!=manifest.get('sha256'):raise ValueError('feature payload hash declaration differs')
    if sha(config['feature_table'])!=declared:raise ValueError('feature table checksum changed')
    rows=read_jsonl(config['feature_table']);rows,groups=_rows(rows)
    if manifest.get('n')!=len(rows) or manifest.get('groups')!=len(groups):raise ValueError('feature manifest coverage differs')
    expected=set(sum(contract.values(),[]))
    if any(set(row['features'])!=expected for row in rows):raise ValueError('feature payload columns differ')
    for columns in predictor_columns(config).values():_matrix(rows,columns)
    return manifest,rows


def _report(summary,model):
    lines=['# Discovery-only failure prediction: '+model,'',summary['limitation'],'',
        f"{summary['n']:,} transformed targets, {summary['templates']} template components, {summary['failures']} failures. All target IDs remain in every fixed seed's OOF evaluation.",'',
        '| Evaluation | Predictor | Brier | Log loss | n | Failures |','|---|---|---:|---:|---:|---:|']
    for context in summary['per_seed_and_ensemble']:
        for name,metric in context['metrics'].items():
            lines.append(f"| {context['scope']}:{context['seed']} | {name} | {metric['brier_score']:.6f} | {metric['log_loss']:.6f} | {metric['n']} | {metric['failures']} |")
    lines+=['','## All paired template-bootstrap improvements','',
        'Positive loss(left) − loss(right) favors the right predictor. These are conditional exploratory intervals with no refitting or multiplicity adjustment.','',
        '| Evaluation | Left baseline | Right predictor | Brier improvement [95%] | Log-loss improvement [95%] |','|---|---|---|---|---|']
    for comparison in summary['contrasts']:
        values=[]
        for key in ('brier_score','log_loss'):
            metric=comparison[key];low,high=metric['exploratory_template_bootstrap_95']
            values.append(f"{metric['mean']:+.6f} [{low:+.6f}, {high:+.6f}]")
        lines.append('| '+f"{comparison['scope']}:{comparison['seed']} | {comparison['left']} | {comparison['right']} | "+' | '.join(values)+' |')
    lines+=['','## All condition, query, load and original-split cells','',
        'Calibration-bin counts, means and observed failure rates are retained in the machine-readable review for every cell. Original train/development labels are descriptive strata; the new template folds define the statistical training boundaries.','',
        '| Evaluation | Predictor | Axis | Cell | n | Failures | Brier | Log loss |','|---|---|---|---|---:|---:|---:|---:|']
    for context in summary['per_seed_and_ensemble']:
        for name,cells in context['cells'].items():
            for cell in cells:
                lines.append(f"| {context['scope']}:{context['seed']} | {name} | {cell['axis']} | {cell['value']} | {cell['n']} | {cell['failures']} | {cell['brier_score']:.6f} | {cell['log_loss']:.6f} |")
    lines+=['','Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.','']
    return '\n'.join(lines)


def _json_bytes(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def _reuse(config,manifest):
    path=Path(config['review_artifact'])
    _discovery_response_path(path)
    if not path.exists():return None
    previous=json.loads(path.read_text())
    if (previous.get('status')!='complete_exploratory' or previous.get('config_hash')!=digest(config)
            or previous.get('feature_table_sha256')!=manifest['sha256']
            or previous.get('feature_manifest_sha256')!=sha(config['feature_manifest'])):
        raise ValueError('completed discovery prediction identity changed')
    for name,artifact in previous['artifacts'].items():
        _discovery_response_path(artifact['path'])
        if sha(artifact['path'])!=artifact['sha256']:raise ValueError('completed '+name+' artifact changed')
    summary=previous['artifacts'].get('summary')
    if not summary:raise ValueError('completed prediction review requires a pinned summary')
    saved=json.loads(Path(summary['path']).read_text())
    if not isinstance(saved,dict) or any(key not in previous or previous[key]!=value for key,value in saved.items()):
        raise ValueError('completed prediction review metrics differ from pinned summary')
    return previous


def run(config):
    manifest,rows=load_features(config);reused=_reuse(config,manifest)
    if reused:return {'status':'complete_reused','report':config['report'],'n':reused['n']}
    from .registry import code_identity
    out=Path(config['output_dir']);out.mkdir(parents=True,exist_ok=True)
    registration=out/'registration.json';source=code_identity()
    if registration.exists():
        prior=json.loads(registration.read_text())
        if prior.get('config_hash')!=digest(config) or prior.get('analysis_source')!=source:
            raise ValueError('analysis registration identity changed; choose a new output directory')
    else:
        immutable(registration,_json_bytes({'status':'started','stage':'discovery_failure_prediction',
            'scope':'CPU statistical fitting only; no language-model training or query',
            'config':config,'config_hash':digest(config),'analysis_source':source,
            'started_utc':datetime.now(timezone.utc).isoformat(),
            'feature_table_sha256':manifest['sha256'],'feature_manifest_sha256':sha(config['feature_manifest'])}))
    started=time.monotonic();summary_path=out/'summary.json'
    try:
        result=run_grouped_cv(rows,config)
        oof=out/'oof_predictions.jsonl';fits=out/'fold_fits.json'
        immutable(oof,''.join(json.dumps(row,sort_keys=True)+'\n' for row in result['oof_predictions']).encode())
        immutable(fits,_json_bytes(result['fold_fits']))
        result['summary'].update(wall_seconds=time.monotonic()-started,
            finished_utc=datetime.now(timezone.utc).isoformat(),
            model=manifest.get('source_model'),model_revision=manifest.get('source_model_revision'))
        immutable(summary_path,_json_bytes(result['summary']))
        immutable(config['report'],_report(result['summary'],manifest.get('source_model','discovery checkpoint')).encode())
        review={**result['summary'],'config_hash':digest(config),'analysis_source':source,
                'feature_table_sha256':manifest['sha256'],'feature_manifest_sha256':sha(config['feature_manifest']),
                'feature_manifest':manifest,
                'fallback_count':sum(len(fold['fallbacks']) for fold in result['fold_fits']),
                'artifacts':{name:{'path':str(path),'sha256':sha(path)} for name,path in
                             [('oof_predictions',oof),('fold_fits',fits),('summary',summary_path),('report',Path(config['report']))]},
                'report':config['report']}
        immutable(config['review_artifact'],_json_bytes(review))
        return {'status':'complete_exploratory','report':config['report'],'n':review['n'],
                'templates':review['templates'],'fallback_count':review['fallback_count']}
    except Exception as exc:
        failed={'status':'failed','stage':'discovery_failure_prediction',
            'error':f'{type(exc).__name__}: {exc}','wall_seconds':time.monotonic()-started,
            'finished_utc':datetime.now(timezone.utc).isoformat(),'generated_holdouts_opened':False,
            'scope':'CPU statistical fitting; no language-model training or query'}
        try:immutable(summary_path if not summary_path.exists() else out/'failure_review.json',_json_bytes(failed))
        except Exception as logging_error:print(f'Failed prediction analysis summary: {logging_error}',file=sys.stderr)
        raise


def compare(config):
    from .registry import code_identity
    reviews={};checksums={};common=None
    for name,spec in config['runs'].items():
        if sha(spec['config'])!=spec['sha256']:raise ValueError('prediction run configuration changed')
        effective=json.loads(Path(spec['config']).read_text());manifest,_=load_features(effective)
        review=_reuse(effective,manifest)
        if review is None:raise ValueError('complete prediction reviews required')
        bank=(review['analysis_plan'],manifest.get('source_dataset_sha256'),
              tuple(sorted((row['id'],row['template_id']) for row in read_jsonl(Path(effective['output_dir'])/'oof_predictions.jsonl') if row['seed']==review['analysis_plan']['seeds'][0])))
        if common is not None and bank!=common:raise ValueError('prediction comparison analysis plans or group banks differ')
        common=bank;reviews[name]=review;checksums[effective['review_artifact']]=sha(effective['review_artifact'])
    if len(reviews)!=2:raise ValueError('two registered checkpoint reviews required')
    target=config.get('comparison_artifact') or config.get('output')
    if not target:raise ValueError('comparison artifact path required')
    if Path(target).exists():
        previous=json.loads(Path(target).read_text())
        if previous.get('config_hash')!=digest(config) or previous.get('review_checksums')!=checksums or previous.get('report_sha256')!=sha(config['report']):
            raise ValueError('completed prediction comparison changed')
        return {'status':'complete_reused','report':config['report']}
    lines=['# Discovery-only failure-prediction comparison','',_limitation(common[0]),'',
           '| Checkpoint | Mean-OOF predictor | Brier | Log loss | n | Failures |',
           '|---|---|---:|---:|---:|---:|']
    for name,review in reviews.items():
        ensemble=next(row for row in review['per_seed_and_ensemble'] if row['scope']=='ensemble')
        for predictor,metric in ensemble['metrics'].items():
            lines.append(f"| {name} | {predictor} | {metric['brier_score']:.6f} | {metric['log_loss']:.6f} | {metric['n']} | {metric['failures']} |")
    lines+=['','All three fixed seeds, every descriptive condition/query/load/original-split cell, fixed calibration bins and paired template-bootstrap comparisons remain in the per-checkpoint reports and machine-readable comparison. No best seed or checkpoint is selected.','']
    for name,spec in config['runs'].items():
        effective=json.loads(Path(spec['config']).read_text());lines.append(f"- [{name}]({Path(effective['report']).name})")
    lines+=['','Neutral raw and scored tiers use at most one cached distinct reference query per target. Oracle-graded neutral failure additionally requires its ground truth; it is not an oracle-free comparator. No original final/extrapolation outcomes or mechanism C features are used.','']
    if _feature_profile(common[0]):
        lines+=['Source-oracle tiers require the program oracle value even without a neutral query. On source-oracle plus raw-neutral inputs, the scored failure flag is a deterministic comparison, so gains from adding it describe encoding capacity rather than a new observation. All fixed capacity/access contrasts remain reported.','']
    immutable(config['report'],'\n'.join(lines).encode())
    result={'status':'complete_exploratory','complete':True,'models':reviews,'analysis_source':code_identity(),
            'config_hash':digest(config),'review_checksums':checksums,'report':config['report'],
            'report_sha256':sha(config['report']),'generated_holdouts_opened':False,'mechanism_C_fitted':False}
    immutable(target,_json_bytes(result))
    return {'status':'complete_exploratory','report':config['report'],'checkpoints':list(reviews)}
