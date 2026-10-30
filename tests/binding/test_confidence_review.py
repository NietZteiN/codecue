from copy import deepcopy
import math
from pathlib import Path
import pytest

from codecue.binding import confidence_review as review


def fixture():
    names=('prior','A_input')
    rows=[dict(id='row'+str(i),seed=17,template_id='g'+str(i),outer_fold=i,label=i,
        predictions={'prior':.4,'A_input':.1+.3*i}) for i in (0,1)]
    folds=[dict(seed=17,outer_fold=i,train_groups=['g'+str(1-i)],test_groups=['g'+str(i)],
        inner_assignments={'g'+str(1-i):0},fallbacks=[],predictors={name:dict(columns=[] if name=='prior' else ['x'],
        selected_l2=1.,model={'mean':[0.],'scale':[1.],'weights':[.3]},inner_curves=[]) for name in names}) for i in (0,1)]
    newrows=deepcopy(rows);newfolds=deepcopy(folds)
    for row in newrows:row['predictions']['B_input_confidence']=.2
    for fold in newfolds:fold['predictors']['B_input_confidence']={'model':'new'}
    return rows,newrows,folds,newfolds,names


def test_identical_all_baseline_parameters_and_predictions_pass():
    result=review.compare_anchor_data(*fixture())
    assert result['status']=='passed' and result['maximum_absolute_probability_difference']==0
    assert result['probability_values_compared']==4


@pytest.mark.parametrize('mutation',[
    'probability','label','group','fold','missing_row','duplicate','missing_tier',
    'weights','normalizer','penalty','inner_assignment','missing_fit','duplicate_fit','nonfinite','nan_parameter','fallback',
])
def test_anchor_drift_is_rejected(mutation):
    old,new,folds,newfolds,names=fixture()
    if mutation=='probability':new[0]['predictions']['A_input']+=1e-12
    if mutation=='label':new[0]['label']=1
    if mutation=='group':new[0]['template_id']='other'
    if mutation=='fold':new[0]['outer_fold']=7
    if mutation=='missing_row':new.pop()
    if mutation=='duplicate':new.append(deepcopy(new[0]))
    if mutation=='missing_tier':new[0]['predictions'].pop('A_input')
    if mutation=='weights':newfolds[0]['predictors']['A_input']['model']['weights'][0]+=.1
    if mutation=='normalizer':newfolds[0]['predictors']['A_input']['model']['mean'][0]+=.1
    if mutation=='penalty':newfolds[0]['predictors']['A_input']['selected_l2']=2.
    if mutation=='inner_assignment':newfolds[0]['inner_assignments']={'g1':2}
    if mutation=='missing_fit':newfolds.pop()
    if mutation=='duplicate_fit':newfolds.append(deepcopy(newfolds[0]))
    if mutation=='nonfinite':new[0]['predictions']['prior']=math.nan
    if mutation=='nan_parameter':newfolds[0]['predictors']['A_input']['model']['weights'][0]=math.nan
    if mutation=='fallback':newfolds[0]['fallbacks']=[{'predictor':'A_input','reason':'changed'}]
    with pytest.raises(ValueError):review.compare_anchor_data(old,new,folds,newfolds,names)


def test_new_tier_fallback_does_not_change_baseline_anchor():
    old,new,folds,newfolds,names=fixture()
    newfolds[0]['fallbacks']=[{'predictor':'B_input_confidence','reason':'single_class_training'}]
    assert review.compare_anchor_data(old,new,folds,newfolds,names)['status']=='passed'


def test_reserved_comparison_rejected_before_hash_or_read(monkeypatch):
    def reject(*args,**kwargs):raise AssertionError('reserved comparison opened')
    monkeypatch.setattr(review,'sha',reject)
    with pytest.raises(ValueError):review._comparison('/x/artifacts/binding/final/comparison.json','0'*64,'unused')


def test_joint_profile_checks_all_eighteen_parent_tiers_and_fixed_primary_pairs():
    from codecue.binding import candidate_prediction,joint_confidence
    old_role,new_role,columns,pairs=review._profile({'comparison_profile':'joint_confidence_v1'})
    assert old_role==candidate_prediction.ROLE and new_role==joint_confidence.ROLE
    assert columns==candidate_prediction.predictor_columns() and len(columns)==18
    assert pairs==joint_confidence.PRIMARY_PAIRS and len(pairs)==5
    for left,right in pairs:
        assert left in columns
        assert set(columns[left])<set(joint_confidence.predictor_columns()[right])


def test_profile_choice_rejects_unknown_review_before_payload_access():
    with pytest.raises(ValueError,match='unknown confidence comparison profile'):
        review._profile({'comparison_profile':'unregistered'})


def test_stress_profile_checks_all_twenty_three_parent_tiers_and_nested_pairs():
    from codecue.binding import joint_confidence,stress_prediction
    old_role,new_role,columns,pairs=review._profile({'comparison_profile':'stress_query_confidence_v1'})
    assert old_role==joint_confidence.ROLE and new_role==stress_prediction.ROLE
    assert columns==joint_confidence.predictor_columns() and len(columns)==23
    assert pairs==stress_prediction.PRIMARY_PAIRS and len(pairs)==5
    for left,right in pairs:
        assert set(columns[left])<set(stress_prediction.predictor_columns()[right])
