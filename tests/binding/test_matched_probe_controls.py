from copy import deepcopy
from itertools import product

import numpy as np
import pytest

from codecue.binding.matched_probe_controls import (
    grouped_shuffle,class_labels,select_queried,histogram_audit,validate_model,predictions_from_saved,
)
from codecue.binding.discovery_readouts import CLASSES


def rows():
    result=[]
    for split,base,condition,lexical,updates,tail,query in product(
            ('train','development'),range(8),('neutral','informative','misleading'),range(2),(1,3),('before','after'),('current','saved')):
        result.append(dict(base_id=f'{split}:{base}',template_id='template:'+split,split=split,condition=condition,
            lexical_realization=lexical,updates=updates,tail_placement=tail,query_role=query,targets=[base+1,-base-1]))
    return result


def test_joint_shuffle_keeps_all_relatives_together_and_exact_class_frequencies():
    records=rows();truth=class_labels(records)
    for seed in (11,29,47):
        control,donors=grouped_shuffle(records,seed)
        assert set(donors)==set(donors.values())
        assert all(k.split(':')[0]==v.split(':')[0] for k,v in donors.items())
        seen={}
        for row,labels in zip(records,control):
            key=row['base_id']
            assert key not in seen or np.array_equal(seen[key],labels)
            seen[key]=labels
            # Complete current/saved pair is preserved, not independently relabeled.
            assert CLASSES[labels[0]]==-CLASSES[labels[1]]
        cells=histogram_audit(records,truth,control)
        assert all(c['counts']==c['control_counts'] and c['classes']==8 for c in cells)
        qtruth=class_labels(records,True);qcontrol=select_queried(control,records)
        assert all(c['counts']==c['control_counts'] for c in histogram_audit(records,qtruth,qcontrol))


def test_development_labels_cannot_change_training_control_labels():
    records=rows();before,_=grouped_shuffle(records,29)
    changed=deepcopy(records)
    for row in changed:
        if row['split']=='development':row['targets']=row['targets'][::-1]
    after,_=grouped_shuffle(changed,29)
    training=np.array([r['split']=='train' for r in records])
    assert np.array_equal(before[training],after[training])
    assert not np.array_equal(before[~training],after[~training])


def test_shuffle_is_row_order_independent_and_seeded():
    records=rows();a,donors=grouped_shuffle(records,11);b,reversed_donors=grouped_shuffle(records[::-1],11)
    assert np.array_equal(a,b[::-1]) and donors==reversed_donors
    assert grouped_shuffle(records,47)[1]!=donors


def test_rejects_leaking_splits_inconsistent_relatives_and_final_outcomes():
    records=rows();bad=deepcopy(records);bad[-1]['template_id']='template:train'
    # Check a complete dev template overlap rather than an inconsistent one-row edit.
    for r in bad:
        if r['split']=='development':r['template_id']='template:train'
    with pytest.raises(ValueError,match='templates overlap'):grouped_shuffle(bad,11)
    bad=deepcopy(records);bad[0]['targets']=[16,-16]
    with pytest.raises(ValueError,match='base relatives disagree'):grouped_shuffle(bad,11)
    bad=deepcopy(records);bad[0]['split']='final'
    with pytest.raises(ValueError,match='cannot open final'):grouped_shuffle(bad,11)


def test_frequency_audit_rejects_unmatched_control_difficulty():
    records=rows();truth=class_labels(records);bad=np.zeros_like(truth)
    with pytest.raises(ValueError,match='frequencies differ'):histogram_audit(records,truth,bad)


def test_saved_model_replay_preserves_training_only_normalization():
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    rng=np.random.default_rng(4);x=rng.normal(size=(40,6)).astype(np.float32);x[30:]+=7
    scaler=StandardScaler().fit(x[:30]);z=scaler.transform(x)
    target=np.zeros((30,64),dtype=np.float32);target[np.arange(30),np.arange(30)%32]=1
    target[np.arange(30),32+np.arange(30)[::-1]%32]=1
    model=Ridge(alpha=10.,solver='cholesky').fit(z[:30],target)
    expected=model.predict(z).reshape(40,2,32).argmax(2)
    saved=dict(registration_hash=np.array('registered'),case_ids=np.array([str(i) for i in range(40)]),
        training_ids=np.array([str(i) for i in range(30)]),classes=CLASSES,mean=scaler.mean_,scale=scaler.scale_,
        coef=model.coef_,intercept=model.intercept_,target_labels=np.zeros((40,1),int),control_labels=np.ones((40,1),int),predictions=expected)
    validate_model(saved,'registered',saved['case_ids'].tolist(),saved['training_ids'].tolist(),saved['target_labels'],saved['control_labels'],6)
    assert np.array_equal(predictions_from_saved(saved,x),expected)
    assert np.allclose(saved['mean'],x[:30].mean(0)) and not np.allclose(saved['mean'],x.mean(0))
    corrupt=dict(saved,control_labels=np.zeros((40,1),int))
    with pytest.raises(ValueError,match='identity or geometry'):
        validate_model(corrupt,'registered',saved['case_ids'].tolist(),saved['training_ids'].tolist(),saved['target_labels'],saved['control_labels'],6)
