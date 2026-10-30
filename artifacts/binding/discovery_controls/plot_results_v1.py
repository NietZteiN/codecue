#!/usr/bin/env python
"""Plot completed source-capacity/oracle controls without opening response rows.

All eight fixed tiers remain visible. Oracle-assisted tiers are hatched, and the
last tier explicitly re-encodes information already present in the preceding
oracle-plus-raw tier. These discovery OOF scores make no final-test/C claim.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys


ROOT=Path(__file__).resolve().parents[3]
PROFILE='capacity_oracle_v1'
MODELS={'llama31_8b':'Llama 3.1 8B Instruct','codellama34b':'CodeLlama 34B Instruct'}
PREDICTORS=(
    'prior','A_input','A_interactions','A_interactions_neutral_raw',
    'A_interactions_neutral_scored','A_interactions_oracle',
    'A_interactions_oracle_neutral_raw','A_interactions_oracle_neutral_scored',
)
LABELS=(
    'Training prior\n0 queries',
    'Inputs (19 features)\n0 queries',
    'Inputs + interactions (44)\n0 queries',
    'Interactions + neutral\n1 query',
    'Interactions + scored neutral\n1 query + reference oracle',
    'Interactions + source oracle\n0 queries + oracle',
    'Source oracle + neutral\n1 query + oracle',
    'Source oracle + scored neutral \u2021\n1 query + oracle',
)
RAW_COLUMNS={'neutral_valid','neutral_output_tokens','neutral_response_chars',
             'neutral_prediction_value','neutral_prediction_abs'}
ORACLE_COLUMNS={'oracle_answer_value','oracle_answer_abs','oracle_answer_negative'}
ORACLE_TIERS=tuple(PREDICTORS[4:])
SEEDS=(17,29,43)


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _integer(value,name):
    if type(value) is not int or value<0:raise ValueError(name+' must be a nonnegative integer')
    return value


def _number(value,name,minimum=0,maximum=None):
    if (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)
            or value<minimum or maximum is not None and value>maximum):
        raise ValueError(name+' must be a finite valid score')
    return value


def _metric(metric,n,failures):
    if metric.get('n')!=n or metric.get('failures')!=failures:
        raise ValueError('metric target or failure coverage differs')
    if abs(_number(metric.get('failure_rate'),'failure rate',maximum=1)-failures/n)>1e-12:
        raise ValueError('failure rate differs from its counts')
    _number(metric.get('brier_score'),'Brier score',maximum=1)
    _number(metric.get('log_loss'),'log loss')
    bins=metric.get('calibration') or []
    if len(bins)!=10:raise ValueError('all ten fixed calibration bins are required')
    observations=0;errors=0.
    for index,cell in enumerate(bins):
        if abs(cell.get('bin_start',-1)-index/10)>1e-12:
            raise ValueError('calibration bin boundary differs')
        count=_integer(cell.get('n'),'calibration count');observations+=count
        if count:
            forecast=_number(cell.get('mean_forecast'),'bin mean forecast',maximum=1)
            observed=_number(cell.get('observed_error'),'bin observed failure',maximum=1)
            if forecast<index/10-1e-12 or forecast>(index+1)/10+1e-12:
                raise ValueError('mean forecast lies outside the declared bin')
            errors+=count*observed
        elif cell.get('mean_forecast') is not None or cell.get('observed_error') is not None:
            raise ValueError('empty calibration bins require null means')
    if observations!=n or abs(errors-failures)>1e-8:
        raise ValueError('calibration observations differ from complete score coverage')


def _columns(columns):
    if set(columns)!=set(PREDICTORS) or columns['prior']!=[]:
        raise ValueError('all eight fixed predictor tiers are required')
    if any(not isinstance(value,list) or len(set(value))!=len(value) for value in columns.values()):
        raise ValueError('predictor columns must be unique ordered lists')
    original=set(columns['A_input']);strong=set(columns['A_interactions'])
    if len(original)!=19 or len(strong)!=44 or not original<strong:
        raise ValueError('registered source feature counts differ')
    added=strong-original
    if len(added)!=25 or any(not value.startswith(('interaction_','distance_x_')) for value in added):
        raise ValueError('fixed source interaction terms differ')
    expected={
        'A_interactions_neutral_raw':strong|RAW_COLUMNS,
        'A_interactions_neutral_scored':strong|RAW_COLUMNS|{'neutral_failure'},
        'A_interactions_oracle':strong|ORACLE_COLUMNS,
        'A_interactions_oracle_neutral_raw':strong|ORACLE_COLUMNS|RAW_COLUMNS,
        'A_interactions_oracle_neutral_scored':strong|ORACLE_COLUMNS|RAW_COLUMNS|{'neutral_failure'},
    }
    if any(set(columns[name])!=values for name,values in expected.items()):
        raise ValueError('source, query and oracle access tiers differ')
    if original & (RAW_COLUMNS|ORACLE_COLUMNS|{'neutral_failure'}):
        raise ValueError('source-only baseline contains query/oracle features')


def _comparisons():
    return tuple(('prior',name) for name in PREDICTORS if name!='prior')+(
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


def validate_comparison(data):
    if data.get('status')!='complete_exploratory' or data.get('complete') is not True:
        raise ValueError('completed exploratory capacity/oracle comparison required')
    if data.get('generated_holdouts_opened') is not False or data.get('mechanism_C_fitted') is not False:
        raise ValueError('only discovery controls without mechanism C may be plotted')
    if set(data.get('models') or {})!=set(MODELS):
        raise ValueError('both registered checkpoint reviews are required')
    checksums=data.get('review_checksums') or {}
    if len(checksums)!=2 or any(not isinstance(value,str) or len(value)!=64
            or any(character not in '0123456789abcdef' for character in value)
            for value in checksums.values()):
        raise ValueError('both pinned review hashes are required')
    selected={};common=None
    expected_contexts={('seed',seed) for seed in SEEDS}|{('ensemble','mean_probability')}
    expected_comparisons=set(_comparisons())
    for name in MODELS:
        review=data['models'][name]
        if (review.get('status')!='complete_exploratory'
                or review.get('generated_holdouts_opened') is not False
                or review.get('mechanism_C_fitted') is not False):
            raise ValueError(name+': complete discovery review required')
        n=_integer(review.get('n'),'target count');failures=_integer(review.get('failures'),'failure count')
        if n!=6144 or failures>n or review.get('templates')!=24:
            raise ValueError(name+': complete 6144-target/24-component bank required')
        plan=review.get('analysis_plan') or {}
        if (plan.get('feature_profile')!=PROFILE or tuple(plan.get('seeds') or [])!=SEEDS
                or plan.get('outer_folds')!=6 or plan.get('inner_folds')!=5):
            raise ValueError(name+': fixed profile or grouped-fold plan differs')
        _columns(plan.get('predictors') or {})
        if len(plan.get('comparisons') or [])!=16 or {tuple(pair) for pair in plan['comparisons']}!=expected_comparisons:
            raise ValueError(name+': retain all sixteen fixed contrasts')
        if common is not None and plan!=common:raise ValueError('checkpoint plans differ')
        common=plan;contexts={}
        for context in review.get('per_seed_and_ensemble',[]):
            key=(context.get('scope'),context.get('seed'))
            if key in contexts:raise ValueError(name+': duplicate evaluation context')
            metrics=context.get('metrics') or {}
            if set(metrics)!=set(PREDICTORS):raise ValueError(name+': every tier must remain visible')
            for metric in metrics.values():_metric(metric,n,failures)
            contexts[key]=metrics
        if set(contexts)!=expected_contexts:
            raise ValueError(name+': all three fixed partitions and mean ensemble are required')
        contrasts={}
        for contrast in review.get('contrasts',[]):
            context=(contrast.get('scope'),contrast.get('seed'))
            pair=(contrast.get('left'),contrast.get('right'))
            key=context+pair
            if key in contrasts or context not in expected_contexts or pair not in expected_comparisons:
                raise ValueError(name+': contrast identities or coverage differ')
            contrasts[key]=contrast
        if len(contrasts)!=len(expected_contexts)*len(expected_comparisons):
            raise ValueError(name+': incomplete fixed contrast matrix')
        cost=(review.get('feature_manifest') or {}).get('additional_query_cost') or {}
        if cost.get('maximum_reference_queries_per_target')!=1:
            raise ValueError(name+': one-reference-query access contract required')
        selected[name]=contexts['ensemble','mean_probability']
    return selected


def render(selected,comparison_hash,source_hash):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
        'axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','svg.hashsalt':'discovery-controls-v1'})
    figure,axes=plt.subplots(1,2,figsize=(15.5,9.1),sharey=True)
    colors=('#277DA8','#DB8734');positions=list(range(len(PREDICTORS)))
    for axis,metric,title in zip(axes,('brier_score','log_loss'),('Brier score','Log loss')):
        maximum=max(selected[name][predictor][metric] for name in MODELS for predictor in PREDICTORS)
        for index,(name,color) in enumerate(zip(MODELS,colors)):
            offset=-.19 if index==0 else .19
            values=[selected[name][predictor][metric] for predictor in PREDICTORS]
            bars=axis.barh([position+offset for position in positions],values,height=.32,
                           color=color,edgecolor='#333333',linewidth=.4,zorder=3)
            for predictor,bar,value in zip(PREDICTORS,bars,values):
                if predictor in ORACLE_TIERS:bar.set_hatch('////')
                axis.annotate(f'{value:.4g}',(value,bar.get_y()+bar.get_height()/2),
                    xytext=(5,0),textcoords='offset points',ha='left',va='center',fontsize=9)
        axis.set_yticks(positions,LABELS)
        axis.tick_params(axis='y',labelsize=9,pad=9,length=0)
        axis.set_xlim(0,maximum*1.28 if maximum else .05)
        axis.set_xlabel(title+' (lower is better)')
        axis.set_title(title,fontweight='bold',pad=12)
        axis.grid(axis='x',alpha=.18,zorder=0)
        for index,predictor in enumerate(PREDICTORS):
            if predictor in ORACLE_TIERS:axis.axhspan(index-.45,index+.45,color='#F3ECE3',alpha=.7,zorder=0)
        axis.axhspan(5.55,7.45,facecolor='none',edgecolor='#817360',linestyle=':',linewidth=1,zorder=2)
    axes[0].invert_yaxis()
    handles=[Patch(facecolor=color,label=MODELS[name]) for name,color in zip(MODELS,colors)]
    handles.append(Patch(facecolor='white',edgecolor='#555555',hatch='////',label='Requires program/reference oracle'))
    figure.legend(handles=handles,loc='upper center',bbox_to_anchor=(.6,.925),ncol=3,frameon=False,fontsize=10)
    figure.suptitle('Discovery failure prediction: fixed capacity and oracle-access controls',
                   fontsize=15,fontweight='bold',y=.98)
    figure.subplots_adjust(left=.245,right=.985,top=.83,bottom=.27,wspace=.19)
    footer=(
        'Inputs: 19 additive source features; 25 fixed interactions give 44 total. Source-oracle tiers add value, magnitude and sign.',
        'Hatched tiers require an oracle. Neutral tiers use at most one extra query; reference gold is additional access, not a target LM response.',
        '\u2021 Last tier adds no observation beyond source oracle + raw neutral above it; only the deterministic failure encoding changes.',
        'Mean-OOF ensemble: fixed seeds 17, 29 and 43; 24 consumed discovery components. Partition seeds are not independent replications.',
        'Scores compare predictors within each checkpoint. No mechanism C or untouched final-test claim; conditional intervals are in the full report.',
    )
    for position,line in zip((.205,.17,.135,.10,.065),footer):
        figure.text(.08,position,line,fontsize=9,color='#444444')
    figure.text(.08,.03,f'Comparison SHA256 {comparison_hash[:16]}  |  Plot source SHA256 {source_hash[:16]}',fontsize=8,color='#666666')
    svg=io.BytesIO();png=io.BytesIO()
    figure.savefig(svg,format='svg',metadata={'Date':None,'Creator':'CodeCue discovery controls v1'})
    figure.savefig(png,format='png',dpi=180,metadata={'Software':'CodeCue discovery controls v1'})
    plt.close(figure)
    return {'svg':svg.getvalue(),'png':png.getvalue()},matplotlib.__version__


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comparison',type=Path,default=ROOT/'artifacts/binding/discovery_controls/comparison_v1.json')
    args=parser.parse_args();comparison=args.comparison.resolve()
    if not comparison.is_file():raise ValueError('comparison is missing; no figure created')
    content=comparison.read_bytes();data=json.loads(content);selected=validate_comparison(data)
    source_hash=_sha(Path(__file__).read_bytes());comparison_hash=_sha(content)
    figures,version=render(selected,comparison_hash,source_hash)
    paths={suffix:ROOT/f'reports/binding/discovery_controls_results_v1.{suffix}' for suffix in figures}
    review_path=ROOT/'artifacts/binding/discovery_controls/figure_review_v1.json'
    review={'status':'passed','complete':True,'analysis_role':'descriptive_discovery_capacity_oracle_control_figure',
        'feature_profile':PROFILE,'comparison':str(comparison),'comparison_sha256':comparison_hash,
        'review_checksums':data['review_checksums'],
        'plot_source':str(Path(__file__).resolve()),'plot_source_sha256':source_hash,
        'matplotlib_version':version,'evaluation':'fixed mean-probability OOF ensemble',
        'models':list(MODELS),'predictors':list(PREDICTORS),'seeds':list(SEEDS),
        'templates':24,'targets_per_checkpoint':6144,'outer_folds':6,'inner_folds':5,
        'metrics':['brier_score','log_loss'],'uncertainty_whiskers':False,
        'source_feature_counts':{'additive':19,'interaction_terms_added':25,'interactions_total':44,'source_oracle_descriptors':3},
        'oracle_assisted_tiers':list(ORACLE_TIERS),'reference_query_budget_per_target':1,
        'deterministic_encoding_comparison':{'left':'A_interactions_oracle_neutral_raw',
            'right':'A_interactions_oracle_neutral_scored','new_observations':0},
        'generated_holdouts_opened':False,'mechanism_C_fitted':False,
        'limitation':'Previously consumed discovery data; partition seeds are not independent replications. '
                     'The final scored flag re-encodes information already available in source-oracle plus raw-neutral features.',
        'outputs':{suffix:{'path':str(paths[suffix]),'bytes':len(value),'sha256':_sha(value)} for suffix,value in figures.items()}}
    metadata=(json.dumps(review,sort_keys=True,indent=2)+'\n').encode()
    # Check every immutable target before writing any output.
    for path,value in [(paths[suffix],value) for suffix,value in figures.items()]+[(review_path,metadata)]:
        if path.exists() and path.read_bytes()!=value:raise ValueError('existing figure/provenance differs: '+str(path))
    sys.path.insert(0,str(ROOT/'src'))
    from codecue.binding.published_benchmarks import immutable
    for suffix,value in figures.items():immutable(paths[suffix],value)
    immutable(review_path,metadata)
    print(json.dumps({'status':'passed','figure':review['outputs'],'provenance':str(review_path)},indent=2))


if __name__=='__main__':main()
