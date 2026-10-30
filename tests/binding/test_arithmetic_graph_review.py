from copy import deepcopy

import numpy as np
import pytest

from codecue.binding import arithmetic_graph_review as review


@pytest.fixture
def original():
    return dict(query_slot=0, expected_answer=5, oracle=dict(definitions=[5,1,2,3],
        values=[5,2,7,9], writes=[dict(slot=0,statement=0,value=2),dict(slot=1,statement=1,value=2),
        dict(slot=0,statement=4,value=3),dict(slot=0,statement=5,value=5)]))


@pytest.mark.parametrize('value,expected',[(None,'invalid'),(5,'correct'),(2,'stale_and_other_current'),
    (3,'stale_only'),(7,'other_current_only'),(99,'neither')])
def test_numeric_match_categories_preserve_ambiguity(original,value,expected):
    assert review.match_signature(original,dict(parsed=value))==expected


def test_current_write_is_not_a_historical_version(original):
    original['expected_answer']=99
    assert review.match_signature(original,dict(parsed=5))=='neither'


def test_partial_parent_success_is_separate_from_whole_graph():
    heads=[dict(kind='parent',slot=i,start=48+i*2,stop=50+i*2) for i in range(2)]
    truth=np.zeros((2,52));scores=truth.copy();prior=truth.copy()
    truth[:,48]=1;truth[:,50]=1
    scores[0,48]=scores[0,51]=1;scores[1,49]=scores[1,50]=1
    prior[:,48]=prior[:,50]=1
    result=review.head_diagnostics(scores,truth,prior,heads,[{},{}],truth)['parent']
    assert result['individual_accuracy']==.5
    assert result['whole_accuracy']==0
    assert result['whole_prior_accuracy']==1
    assert result['heads'][0]['confusion_nonzero']==[[0,0,1],[0,1,1]]


def test_seen_class_and_queried_value_diagnostics():
    heads=[dict(kind='value',slot=i,start=48+i*3,stop=51+i*3) for i in range(4)]
    train=np.zeros((2,60));truth=train.copy();scores=train.copy()
    for h in heads:
        train[:,h['start']]=1;truth[0,h['start']]=1;truth[1,h['start']+1]=1;scores[:,h['start']]=1
    result=review.head_diagnostics(scores,truth,train,heads,[dict(query_slot=0),dict(query_slot=1)],train)['value']
    assert result['seen_class_cells']==4 and result['unseen_class_cells']==4
    assert result['seen_class_accuracy']==1 and result['unseen_class_accuracy']==0
    assert result['queried_accuracy']==.5 and result['unqueried_accuracy']==.5


def test_tiny_floating_differences_can_preserve_exact_decisions():
    a=np.zeros((2,50));a[:,48]=1
    b=a+1e-13
    heads=[dict(kind='parent',start=48,stop=50)]
    assert review.replay_check(a,b,heads)<1e-10


def test_tiny_binary_decision_change_is_rejected():
    a=np.zeros((2,48));a[0,0]=.5
    b=a.copy();b[0,0]-=1e-13
    with pytest.raises(ValueError,match='binary decisions'):
        review.replay_check(a,b,[])


def test_tiny_categorical_argmax_change_is_rejected():
    a=np.zeros((2,50));b=a.copy();b[0,49]=1e-13
    with pytest.raises(ValueError,match='categorical decisions'):
        review.replay_check(a,b,[dict(kind='parent',start=48,stop=50)])


@pytest.mark.parametrize('change',[1e-4,np.nan])
def test_material_or_nonfinite_replay_is_rejected(change):
    a=np.zeros((2,48));b=a.copy();b[0,0]=change
    with pytest.raises(ValueError):review.replay_check(b,a,[])
