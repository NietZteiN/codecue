#!/usr/bin/env python
"""Plot completed discovery-only prediction metadata, never response rows.

The scored neutral tier needs reference ground truth and is hatched explicitly.
Scores describe the fixed mean-probability OOF ensemble; they are not final-test
performance or independent replications across partition seeds.
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
MODELS={'llama31_8b':'Llama 3.1 8B Instruct','codellama34b':'CodeLlama 34B Instruct'}
PREDICTORS=('prior','A_input','A_neutral_raw','A_neutral_scored')
LABELS=('Training prior\n0 extra queries','Input features\n0 extra queries',
        'Input + neutral output\n1 extra query',
        'Input + scored neutral\n1 query + reference gold')
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
        raise ValueError('score coverage or label counts differ')
    if abs(_number(metric.get('failure_rate'),'failure_rate',maximum=1)-failures/n)>1e-12:
        raise ValueError('failure rate differs from counts')
    _number(metric.get('brier_score'),'Brier',maximum=1)
    _number(metric.get('log_loss'),'log loss')
    bins=metric.get('calibration') or []
    if len(bins)!=10:raise ValueError('all ten fixed calibration bins are required')
    observations=0;errors=0.
    for index,cell in enumerate(bins):
        if abs(cell.get('bin_start',-1)-index/10)>1e-12:
            raise ValueError('calibration bin boundaries differ')
        count=_integer(cell.get('n'),'calibration n');observations+=count
        if count:
            forecast=_number(cell.get('mean_forecast'),'bin mean forecast',maximum=1)
            observed=_number(cell.get('observed_error'),'bin observed failure',maximum=1)
            if forecast<index/10-1e-12 or forecast>(index+1)/10+1e-12:
                raise ValueError('mean forecast lies outside its fixed bin')
            errors+=count*observed
        elif cell.get('mean_forecast') is not None or cell.get('observed_error') is not None:
            raise ValueError('empty calibration bins must retain null means')
    if observations!=n or abs(errors-failures)>1e-8:
        raise ValueError('calibration counts differ from score coverage')


def validate_comparison(data):
    if data.get('status')!='complete_exploratory' or data.get('complete') is not True:
        raise ValueError('completed exploratory prediction comparison required')
    if data.get('generated_holdouts_opened') is not False or data.get('mechanism_C_fitted') is not False:
        raise ValueError('figure requires discovery-only baselines without mechanism C')
    if set(data.get('models') or {})!=set(MODELS):
        raise ValueError('both registered checkpoint reviews are required')
    checksums=data.get('review_checksums') or {}
    if len(checksums)!=2 or any(not isinstance(value,str) or len(value)!=64
            or any(character not in '0123456789abcdef' for character in value)
            for value in checksums.values()):
        raise ValueError('both pinned review checksums are required')
    selected={};common=None
    for name in MODELS:
        review=data['models'][name]
        if (review.get('status')!='complete_exploratory'
                or review.get('generated_holdouts_opened') is not False
                or review.get('mechanism_C_fitted') is not False):
            raise ValueError(name+': complete discovery-only review required')
        n=_integer(review.get('n'),'target n');failures=_integer(review.get('failures'),'failures')
        if n<1 or failures>n or review.get('templates')!=24:
            raise ValueError(name+': expected complete 24-template bank')
        plan=review.get('analysis_plan') or {}
        if (tuple(plan.get('seeds') or [])!=SEEDS or plan.get('outer_folds')!=6
                or plan.get('inner_folds')!=5 or set(plan.get('predictors') or {})!=set(PREDICTORS)):
            raise ValueError(name+': fixed seeded nested-fold plan differs')
        columns=plan['predictors']
        if (columns['prior']!=[] or not set(columns['A_input'])<set(columns['A_neutral_raw'])
                or not set(columns['A_neutral_raw'])<set(columns['A_neutral_scored'])
                or set(columns['A_neutral_scored'])-set(columns['A_neutral_raw'])!={'neutral_failure'}
                or 'neutral_failure' in columns['A_neutral_raw']):
            raise ValueError(name+': raw and oracle-scored feature tiers differ')
        if common is not None and plan!=common:raise ValueError('checkpoint analysis plans differ')
        common=plan
        contexts={}
        for context in review.get('per_seed_and_ensemble',[]):
            key=(context.get('scope'),context.get('seed'))
            if key in contexts:raise ValueError(name+': duplicated evaluation context')
            metrics=context.get('metrics') or {}
            if set(metrics)!=set(PREDICTORS):raise ValueError(name+': every predictor must remain visible')
            for metric in metrics.values():_metric(metric,n,failures)
            contexts[key]=metrics
        expected={('seed',seed) for seed in SEEDS}|{('ensemble','mean_probability')}
        if set(contexts)!=expected:raise ValueError(name+': retain all fixed seeds and the mean ensemble')
        cost=(review.get('feature_manifest') or {}).get('additional_query_cost') or {}
        if cost.get('maximum_reference_queries_per_target')!=1:
            raise ValueError(name+': declared one-query neutral reference contract required')
        selected[name]=contexts['ensemble','mean_probability']
    return selected


def render(selected,comparison_hash,source_hash):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
        'axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','svg.hashsalt':'discovery-prediction-v1'})
    figure,axes=plt.subplots(1,2,figsize=(13.5,6.8))
    colors=('#277DA8','#DB8734');positions=list(range(len(PREDICTORS)))
    for axis,metric,title in zip(axes,('brier_score','log_loss'),('Brier score','Log loss')):
        maximum=max(selected[name][predictor][metric] for name in MODELS for predictor in PREDICTORS)
        for index,(name,color) in enumerate(zip(MODELS,colors)):
            offset=-.2 if index==0 else .2
            values=[selected[name][predictor][metric] for predictor in PREDICTORS]
            bars=axis.bar([position+offset for position in positions],values,width=.35,
                          color=color,edgecolor='#333333',linewidth=.4,zorder=3)
            bars[-1].set_hatch('////')
            for bar,value in zip(bars,values):
                axis.annotate(f'{value:.4g}',(bar.get_x()+bar.get_width()/2,value),
                              xytext=(0,5),textcoords='offset points',ha='center',va='bottom',fontsize=9)
        axis.set_xticks(positions,LABELS)
        axis.tick_params(axis='x',labelsize=9,pad=9)
        axis.set_ylim(0,maximum*1.22 if maximum else .05)
        axis.set_ylabel(title+' (lower is better)')
        axis.set_title(title,fontweight='bold',pad=13)
        axis.grid(axis='y',alpha=.18,zorder=0)
        axis.axvspan(2.55,3.45,color='#F3ECE3',alpha=.8,zorder=0)
    handles=[Patch(facecolor=color,label=MODELS[name]) for name,color in zip(MODELS,colors)]
    handles.append(Patch(facecolor='white',edgecolor='#333333',hatch='////',label='Requires neutral reference gold'))
    figure.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.92),ncol=3,frameon=False,fontsize=10)
    figure.suptitle('Discovery-only failure prediction: all baseline tiers',fontsize=15,fontweight='bold',y=.985)
    figure.subplots_adjust(left=.07,right=.985,top=.8,bottom=.29,wspace=.23)
    figure.text(.07,.15,'Bars score the mean-probability OOF ensemble from fixed partition seeds 17, 29 and 43; 24 template components.',fontsize=9,color='#444444')
    figure.text(.07,.115,'Neutral-output tiers use at most one distinct extra query per target. Hatched tier additionally requires the reference oracle.',fontsize=9,color='#444444')
    figure.text(.07,.08,'Already-consumed discovery data; no final-test or mechanism claim. Repeated partition seeds are not independent replications.',fontsize=9,color='#444444')
    figure.text(.07,.04,f'Comparison SHA256 {comparison_hash[:16]}  |  Plot source SHA256 {source_hash[:16]}',fontsize=8,color='#666666')
    svg=io.BytesIO();png=io.BytesIO()
    figure.savefig(svg,format='svg',metadata={'Date':None,'Creator':'CodeCue discovery prediction v1'})
    figure.savefig(png,format='png',dpi=180,metadata={'Software':'CodeCue discovery prediction v1'})
    plt.close(figure)
    return {'svg':svg.getvalue(),'png':png.getvalue()},matplotlib.__version__


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comparison',type=Path,default=ROOT/'artifacts/binding/discovery_prediction/comparison_v1.json')
    args=parser.parse_args();comparison=args.comparison.resolve()
    if not comparison.is_file():raise ValueError('comparison is missing; no figure created')
    content=comparison.read_bytes();data=json.loads(content);selected=validate_comparison(data)
    source_hash=_sha(Path(__file__).read_bytes());comparison_hash=_sha(content)
    figures,version=render(selected,comparison_hash,source_hash)
    paths={suffix:ROOT/f'reports/binding/discovery_prediction_results_v1.{suffix}' for suffix in figures}
    review_path=ROOT/'artifacts/binding/discovery_prediction/figure_review_v1.json'
    review={'status':'passed','complete':True,'analysis_role':'descriptive_discovery_oof_probability_score_figure',
        'comparison':str(comparison),'comparison_sha256':comparison_hash,
        'review_checksums':data['review_checksums'],'plot_source':str(Path(__file__).resolve()),
        'plot_source_sha256':source_hash,'matplotlib_version':version,
        'evaluation':'fixed mean-probability OOF ensemble','seeds':list(SEEDS),'templates':24,
        'models':list(MODELS),'predictors':list(PREDICTORS),'metrics':['brier_score','log_loss'],
        'uncertainty_whiskers':False,'reference_query_budget_per_target':1,
        'oracle_scored_tier':'A_neutral_scored additionally requires reference gold; raw tiers do not',
        'generated_holdouts_opened':False,'mechanism_C_fitted':False,
        'limitation':'Previously consumed discovery data; no final-test claim. Partition seeds are not independent replications.',
        'outputs':{suffix:{'path':str(paths[suffix]),'bytes':len(value),'sha256':_sha(value)} for suffix,value in figures.items()}}
    metadata=(json.dumps(review,sort_keys=True,indent=2)+'\n').encode()
    # Validate every immutable target before creating any output.
    for path,value in [(paths[suffix],value) for suffix,value in figures.items()]+[(review_path,metadata)]:
        if path.exists() and path.read_bytes()!=value:raise ValueError('existing figure/provenance differs: '+str(path))
    sys.path.insert(0,str(ROOT/'src'))
    from codecue.binding.published_benchmarks import immutable
    for suffix,value in figures.items():immutable(paths[suffix],value)
    immutable(review_path,metadata)
    print(json.dumps({'status':'passed','figure':review['outputs'],'provenance':str(review_path)},indent=2))


if __name__=='__main__':main()
