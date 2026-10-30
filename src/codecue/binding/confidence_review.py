"""Exact baseline replay checks and fixed discovery-confidence contrast figures."""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path

from .datasets import digest,read_jsonl
from .published_benchmarks import immutable,sha

PAIRS=(
    ('A_input','B_input_confidence'),
    ('A_interactions','B_interactions_confidence'),
    ('A_interactions_neutral_raw','B_interactions_neutral_raw_confidence'),
    ('A_interactions_oracle_neutral_raw','B_interactions_oracle_neutral_raw_confidence'),
    ('A_interactions_oracle_neutral_scored','B_interactions_oracle_neutral_scored_confidence'),
)
LABELS=('Source','Source + interactions','Interactions + raw neutral',
        'Interactions + oracle + raw neutral','Interactions + oracle + scored neutral')


def _profile(config):
    selected=config.get('comparison_profile','next_token_v1')
    from . import confidence_prediction
    if selected=='next_token_v1':
        from .discovery_controls import ROLE,predictor_columns
        return ROLE,confidence_prediction.ROLE,predictor_columns(),PAIRS
    if selected=='candidate_event_v1':
        from . import candidate_prediction
        return (confidence_prediction.ROLE,candidate_prediction.ROLE,
            confidence_prediction.predictor_columns(),
            tuple((old,new) for _,old,new in candidate_prediction.PAIRED_TIERS))
    if selected=='joint_confidence_v1':
        from . import candidate_prediction,joint_confidence
        return (candidate_prediction.ROLE,joint_confidence.ROLE,
            candidate_prediction.predictor_columns(),joint_confidence.PRIMARY_PAIRS)
    if selected=='stress_query_confidence_v1':
        from . import joint_confidence,stress_prediction
        return (joint_confidence.ROLE,stress_prediction.ROLE,
            joint_confidence.predictor_columns(),stress_prediction.PRIMARY_PAIRS)
    raise ValueError('unknown confidence comparison profile')


def _index(rows,keys):
    result={}
    for row in rows:
        key=tuple(row[name] for name in keys)
        if key in result:raise ValueError('duplicate anchor identity')
        result[key]=row
    if not result:raise ValueError('nonempty anchor bank required')
    return result


def _finite(value):
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('nonfinite anchor parameter')
    if isinstance(value,dict):
        for child in value.values():_finite(child)
    if isinstance(value,list):
        for child in value:_finite(child)


def compare_anchor_data(old_oof,new_oof,old_fits,new_fits,predictors):
    """Compare every old OOF value and fitted baseline, with exact identities."""
    names=tuple(predictors)
    if not names or len(set(names))!=len(names):raise ValueError('unique baseline predictor names required')
    left=_index(old_oof,('seed','id'));right=_index(new_oof,('seed','id'))
    if set(left)!=set(right):raise ValueError('OOF anchor coverage differs')
    maximum=0.;values=0
    for identity,old in left.items():
        new=right[identity]
        if any(old[key]!=new[key] for key in ('seed','id','template_id','outer_fold','label')):
            raise ValueError('OOF anchor grouping, labels or folds differ')
        if type(old['label']) is not int or old['label'] not in (0,1):raise ValueError('binary anchor labels required')
        if set(old['predictions'])!=set(names) or not set(names)<=set(new['predictions']):
            raise ValueError('baseline anchor predictor coverage differs')
        for name in names:
            a,b=old['predictions'][name],new['predictions'][name]
            if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in (a,b)):
                raise ValueError('finite anchor probabilities required')
            maximum=max(maximum,abs(a-b));values+=1
    if maximum!=0:raise ValueError('baseline OOF probability anchors differ')
    oldfolds=_index(old_fits,('seed','outer_fold'));newfolds=_index(new_fits,('seed','outer_fold'))
    if set(oldfolds)!=set(newfolds):raise ValueError('fitting anchor coverage differs')
    for identity,old in oldfolds.items():
        new=newfolds[identity];_finite(old);_finite(new)
        for key in ('train_groups','test_groups','inner_assignments'):
            if old[key]!=new[key]:raise ValueError('fitting anchor group assignment differs')
        if set(old['predictors'])!=set(names) or not set(names)<=set(new['predictors']):
            raise ValueError('fitted baseline predictor coverage differs')
        for name in names:
            if old['predictors'][name]!=new['predictors'][name]:
                raise ValueError('baseline weights, normalizers, penalties or inner curves differ')
        filtered=[row for row in new['fallbacks'] if row['predictor'] in names]
        if old['fallbacks']!=filtered:raise ValueError('baseline fallback records differ')
    return dict(status='passed',oof_rows=len(left),fitting_folds=len(oldfolds),predictors=list(names),
        probability_values_compared=values,maximum_absolute_probability_difference=maximum,
        fitted_parameters_and_inner_curves_identical=True,group_assignments_identical=True)


def _comparison(path,expected,role):
    from .forecasting import _discovery_response_path,_discovery_declaration
    _discovery_response_path(path)
    if sha(path)!=expected:raise ValueError('pinned comparison checksum changed')
    data=json.loads(Path(path).read_text());_discovery_declaration(data)
    if (data.get('status')!='complete_exploratory' or not data.get('complete')
            or data.get('generated_holdouts_opened') is not False or data.get('mechanism_C_fitted') is not False):
        raise ValueError('complete discovery-only comparison required')
    for review in data['models'].values():
        _discovery_declaration(review)
        if review.get('status')!='complete_exploratory':raise ValueError('completed discovery review required')
        manifest=review.get('feature_manifest',{});_discovery_declaration(manifest)
        if manifest.get('evaluation_role')!=role:raise ValueError('expected discovery feature role required')
        for artifact in review['artifacts'].values():
            _discovery_response_path(artifact['path'])
    return data


def review(config):
    from .registry import code_identity
    OLD_ROLE,NEW_ROLE,predictors,pairs=_profile(config)
    old=_comparison(config['baseline_comparison'],config['baseline_comparison_sha256'],OLD_ROLE)
    new=_comparison(config['comparison'],config['comparison_sha256'],NEW_ROLE)
    if set(old['models'])!=set(new['models']) or len(old['models'])!=2:
        raise ValueError('matching two-checkpoint comparisons required')
    result=dict(status='passed',config_hash=digest(config),analysis_source=code_identity(),models={},
        comparison_profile=config.get('comparison_profile','next_token_v1'),
        baseline_comparison_sha256=config['baseline_comparison_sha256'],comparison_sha256=config['comparison_sha256'],
        generated_holdouts_opened=False,mechanism_C_fitted=False,
        limitation='Exploratory discovery comparisons. Bootstrap intervals condition on saved grouped OOF predictions; '
                   'no refit uncertainty, multiplicity correction or unfamiliar-program confirmation. Each confidence '
                   'tier receives one label-free target prefill using the new Transformers backend.')
    if result['comparison_profile']=='candidate_event_v1':
        from .candidate_prediction import LIMITATION
        result['limitation']=LIMITATION
    if result['comparison_profile']=='joint_confidence_v1':
        from .joint_confidence import LIMITATION
        result['limitation']=LIMITATION
    if result['comparison_profile']=='stress_query_confidence_v1':
        from .stress_prediction import LIMITATION
        result['limitation']=LIMITATION
    # Complete both metadata chains before any OOF/fitted-parameter payload read.
    for name,prior in old['models'].items():
        current=new['models'][name];pm=prior['feature_manifest'];cm=current['feature_manifest']
        if pm['evaluation_role']!=OLD_ROLE or cm['evaluation_role']!=NEW_ROLE:
            raise ValueError('expected discovery feature roles required before anchor payload access')
        for key in ('source_model','source_model_revision','source_dataset_sha256','source_identity_hash'):
            if pm[key]!=cm[key]:raise ValueError('baseline/confidence source identity differs')
        for key in ('seeds','outer_folds','inner_folds','l2_grid'):
            if prior['analysis_plan'][key]!=current['analysis_plan'][key]:raise ValueError('fitting protocol changed')
    for data in (old,new):
        for model in data['models'].values():
            for artifact in model['artifacts'].values():
                if sha(artifact['path'])!=artifact['sha256']:raise ValueError('comparison artifact checksum changed')
    for name,prior in old['models'].items():
        current=new['models'][name]
        anchor=compare_anchor_data(read_jsonl(prior['artifacts']['oof_predictions']['path']),
            read_jsonl(current['artifacts']['oof_predictions']['path']),
            json.loads(Path(prior['artifacts']['fold_fits']['path']).read_text()),
            json.loads(Path(current['artifacts']['fold_fits']['path']).read_text()),predictors)
        comparisons=[]
        for left,right in pairs:
            matches=[row for row in current['contrasts'] if row['scope']=='ensemble' and row['left']==left and row['right']==right]
            if len(matches)!=1:raise ValueError('all five fixed confidence contrasts required')
            comparisons.append(deepcopy(matches[0]))
        ensemble=[row for row in current['per_seed_and_ensemble'] if row['scope']=='ensemble']
        if len(ensemble)!=1:raise ValueError('single fixed mean-OOF ensemble required')
        result['models'][name]=dict(anchors=anchor,contrasts=comparisons,metrics=ensemble[0]['metrics'],n=current['n'])
    return result


def run(config):
    result=review(config)
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt']='binding-discovery-confidence-v1'
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    names=sorted(result['models']);fig,axes=plt.subplots(2,2,figsize=(13,8),squeeze=False)
    for column,name in enumerate(names):
        rows=result['models'][name]['contrasts']
        for axis_index,metric in enumerate(('brier_score','log_loss')):
            axis=axes[axis_index,column]
            for position,row in enumerate(rows):
                value=row[metric];low,high=value['exploratory_template_bootstrap_95'];mean=value['mean']
                axis.plot([low,high],[position,position],color='#285b8e',linewidth=2)
                axis.plot(mean,position,'o',color='#285b8e')
            axis.axvline(0,color='#777777',linewidth=1,linestyle='--')
            axis.set_yticks(range(len(LABELS)),LABELS,fontsize=8);axis.invert_yaxis()
            xlabel={
                'candidate_event_v1':'Loss(next-token bundle) − loss(candidate-event bundle)',
                'joint_confidence_v1':'Loss(next-token bundle) − loss(joint bundle)',
                'stress_query_confidence_v1':'Loss(next-token bundle) − loss(next-token + stress query)',
            }.get(result['comparison_profile'],'Loss(baseline) − loss(baseline + confidence)')
            axis.set_title(name+' / '+metric.replace('_',' '));axis.set_xlabel(xlabel)
            axis.xaxis.set_major_locator(MaxNLocator(nbins=5))
            axis.tick_params(axis='x',labelsize=9)
            axis.grid(axis='x',alpha=.2)
    title={
        'candidate_event_v1':'Alternative confidence bundles',
        'joint_confidence_v1':'Candidate-event features added to next-token confidence',
        'stress_query_confidence_v1':'Extra instructed query added to next-token confidence',
    }.get(result['comparison_profile'],'Discovery confidence increments')
    fig.suptitle(title+': fixed mean-OOF predictions and conditional 95% intervals',fontsize=11)
    fig.tight_layout(rect=(0,0,1,.95))
    paths=[]
    for key in ('figure_png','figure_svg'):
        path=Path(config[key]);path.parent.mkdir(parents=True,exist_ok=True)
        import io
        buffer=io.BytesIO();fig.savefig(buffer,format=path.suffix.lstrip('.'),dpi=170,
            metadata={'Date':None} if path.suffix=='.svg' else None)
        immutable(path,buffer.getvalue());paths.append(path)
    plt.close(fig)
    result['figures']=[dict(path=str(path),sha256=sha(path)) for path in paths]
    immutable(config['review_artifact'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status=result['status'],checkpoints=names,review=config['review_artifact'],figures=[str(p) for p in paths])
