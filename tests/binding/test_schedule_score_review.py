from copy import deepcopy
import json
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import schedule_score_review as study
from codecue.binding import schedule_targets as target


def records(groups=('large',),lexical='item'):
    rows=[]
    mapping={f'v{i}':f'{lexical}_{i}' for i in range(4)}
    for body,group in enumerate(groups):
        lines=[f'{mapping[f"v{i}"]} = {body*5+i+1}' for i in range(4)]
        lines += [f'{mapping[f"v{i}"]} = {mapping[f"v{(i+1)%4}"]}' for i in range(4)]
        for query in range(4):
            rows.append(dict(id=f'body{body}-{lexical}-query{query}',source='\n'.join(lines+[mapping[f'v{query}']]),
                split='development',query_slot=query,rename_map=mapping,
                component_id=group,template_id=group))
    return rows


def decision_data(correct,valid=None):
    correct=np.asarray(correct,dtype=bool)
    n=len(correct)
    if correct.shape!=(n,12): raise ValueError('test fixture shape')
    truth=np.array([[head['candidates'][0] for head in target.HEADS]]*n,dtype=np.int16)
    wrong=np.array([[head['candidates'][1] for head in target.HEADS]]*n,dtype=np.int16)
    valid=np.ones_like(correct) if valid is None else np.asarray(valid,dtype=bool)
    predicted=np.where(correct,truth,wrong).astype(np.int16)
    truth[~valid]=-1;predicted[~valid]=-1
    return dict(truth=truth,predicted=predicted,valid=valid,
                correct=valid&(truth==predicted),margin=np.full((n,12),.5),top_score=np.ones((n,12)))


def bundle_fixture(n=8):
    y=np.zeros((n,target.N_COLUMNS));mask=np.zeros_like(y,dtype=bool)
    for head in target.HEADS:
        indices=list(head['indices']);mask[:,indices]=True
        for row in range(n): y[row,indices[row%len(indices)]]=1
    descriptive={key:['fixture']*n for key in ('version_map_by_case','canonical_visible_prefixes','canonical_output_visible_prefixes')}
    return target.TargetBundle(y,mask,target.COLUMNS,tuple(f'c{i}' for i in range(n)),
        tuple(f'g{i//2}' for i in range(n)),tuple('train' if i<n//2 else 'development' for i in range(n)),7,descriptive)


def bank_fixture(tmp_path):
    bundle=bundle_fixture()
    train=np.arange(8)<4;weights=np.ones(4)
    scores=np.full(bundle.y.shape,np.nan);active=bundle.mask.any(axis=0);scores[:,active]=bundle.y[:,active]
    identity=dict(config_hash='a'*64,case_ids=list(bundle.case_ids),features_sha256='f'*64,
        targets_sha256=study._array_hash(bundle.y),mask_sha256=study._array_hash(bundle.mask),
        control_sha256=study._array_hash(bundle.y),train_mask_sha256=study._array_hash(train),
        weights_sha256=study._array_hash(weights))
    path=tmp_path/'original.npz'
    np.savez(path,identity=np.frombuffer(study._json_bytes(identity),dtype=np.uint8),
             scores=scores,random_scores=scores,m0_coef=np.arange(3.))
    return path,study._pin(path),bundle,train,weights,identity


def test_fixed_target_effect_preserves_same_head_across_different_queries():
    rows=records();bodies=study.matched_bodies(rows,1)
    correct=np.zeros((4,12),dtype=bool)
    for row in range(4):
        for family_offset in (0,4): correct[row,family_offset+row]=True
    effects=study.query_effects(decision_data(correct),bodies)
    for family in study.QUERY_FAMILIES:
        pooled=effects[family]['pooled_fixed_target_comparisons']
        assert pooled['effect']==1
        assert pooled['matched_bodies']==1 and pooled['comparison_units']==4
        assert pooled['queried_correct']==4 and pooled['unqueried_correct']==0
        assert all(slot['effect']==1 for slot in effects[family]['fixed_target_slots'].values())
    # Comparing the separately queried heads instead would compare four successes.
    assert correct[np.arange(4),np.arange(4)].mean()==1


def test_prequery_constant_predictions_have_zero_fixed_target_effect_despite_target_difficulty():
    correct=np.zeros((4,12),dtype=bool);correct[:,0]=True;correct[:,4]=True
    data=decision_data(correct);bodies=study.matched_bodies(records())
    effects=study.query_effects(data,bodies)
    assert all(slot['effect']==0 for family in effects.values() for slot in family['fixed_target_slots'].values())
    changes=study.prefix_disagreements(data,bodies)
    assert all(value['prediction_disagreement_bodies']==0 for value in changes.values())
    # A different-target comparison would incorrectly call target0 easier.
    assert correct[0,0]-correct[1:,1:4].mean()==1


def test_unequal_graph_sizes_preserve_row_and_equal_graph_effects_separately():
    rows=records(('large','large','large','small'));bodies=study.matched_bodies(rows,4)
    correct=np.zeros((16,12),dtype=bool)
    for body in range(4):
        for query in range(4):
            for offset in (0,4):
                for slot in range(4): correct[4*body+query,offset+slot]=(query==slot) if body<3 else (query!=slot)
    effect=study.query_effects(decision_data(correct),bodies)['current_definition']['pooled_fixed_target_comparisons']
    assert effect['matched_bodies']==4 and effect['comparison_units']==16
    assert effect['effect']==.5 and effect['group_macro_effect']==0
    assert effect['per_group']['large']['matched_bodies']==3
    assert effect['per_group']['small']['matched_bodies']==1


@pytest.mark.parametrize('problem',['missing','duplicate_slot','duplicate_id','wrong_query','changed_body','mixed_group','train'])
def test_exact_body_matching_guards(problem):
    rows=records()
    if problem=='missing':rows.pop()
    if problem=='duplicate_slot':rows[-1]['query_slot']=2;rows[-1]['source']=rows[-1]['source'].rsplit('\n',1)[0]+'\nitem_2'
    if problem=='duplicate_id':rows[-1]['id']=rows[0]['id']
    if problem=='wrong_query':rows[-1]['query_slot']=0
    if problem=='changed_body':rows[-1]['source']=rows[-1]['source'].replace('item_0 = 1','item_0 = 8')
    if problem=='mixed_group':rows[-1]['component_id']='different'
    if problem=='train':rows[-1]['split']='train'
    with pytest.raises(ValueError):study.matched_bodies(rows)


def test_matching_keeps_actual_lexical_names_and_numeric_body_identity():
    rows=records(('g0','g1'))+records(('g0','g1'),lexical='cell')
    assert len(study.matched_bodies(rows,4))==4


def test_query_effect_rejects_changing_truth_for_a_fixed_target():
    data=decision_data(np.ones((4,12),dtype=bool));data['truth'][1,0]=1
    with pytest.raises(ValueError,match='fixed-target truth'):
        study.query_effects(data,study.matched_bodies(records()))


def test_npz_reader_never_accesses_parameter_members(tmp_path,monkeypatch):
    path,pin,bundle,train,weights,_=bank_fixture(tmp_path)
    original=np.load;accesses=[]
    class Guard:
        def __init__(self,archive):self.archive=archive
        def __enter__(self):return self
        def __exit__(self,*args):self.archive.close()
        def __getitem__(self,key):
            accesses.append(key)
            assert key in ('identity','scores','random_scores'),'parameter member was opened'
            return self.archive[key]
    monkeypatch.setattr(study.np,'load',lambda *args,**kwargs:Guard(original(*args,**kwargs)))
    real,random,identity=study.load_score_bank(path,pin,bundle,bundle,train,weights,'a'*64)
    assert accesses==['identity','scores','random_scores']
    assert np.array_equal(real,random,equal_nan=True)
    assert identity['case_ids']==list(bundle.case_ids)


def test_score_bank_rejects_reordered_case_ids_even_with_recomputed_file_pin(tmp_path):
    path,_,bundle,train,weights,_=bank_fixture(tmp_path)
    with np.load(path,allow_pickle=False) as archive:arrays={k:archive[k].copy() for k in archive.files}
    identity=json.loads(arrays['identity'].tobytes());identity['case_ids'].reverse()
    arrays['identity']=np.frombuffer(study._json_bytes(identity),dtype=np.uint8);np.savez(path,**arrays)
    with pytest.raises(ValueError,match='ordered case'):
        study.load_score_bank(path,study._pin(path),bundle,bundle,train,weights,'a'*64)


@pytest.mark.parametrize('problem',['dtype','nonfinite','undefined_finite','checksum','duplicate_ids'])
def test_saved_score_guards(tmp_path,problem):
    path,pin,bundle,train,weights,_=bank_fixture(tmp_path)
    if problem=='duplicate_ids':
        from dataclasses import replace
        bundle=replace(bundle,case_ids=('repeat',)*8)
    else:
        with np.load(path,allow_pickle=False) as archive:arrays={k:archive[k].copy() for k in archive.files}
        if problem=='dtype':arrays['scores']=arrays['scores'].astype(np.float32)
        if problem=='nonfinite':arrays['scores'][0,target.HEADS[0]['indices'][0]]=np.inf
        if problem=='undefined_finite':arrays['scores'][0,0]=0
        if problem=='checksum':arrays['scores'][0,target.HEADS[0]['indices'][0]]+=.25
        np.savez(path,**arrays)
        if problem!='checksum':pin=study._pin(path)
    with pytest.raises(ValueError):study.load_score_bank(path,pin,bundle,bundle,train,weights,'a'*64)


def test_confusions_preserve_absent_classes_and_joint_correctness_mass():
    correct=np.zeros((4,12),dtype=bool);correct[:,4:8]=True
    data=decision_data(correct)
    report=study.categorical_diagnostics(data,np.array(['large','large','large','small']))
    version=report['heads']['current_version/0']
    assert version['truth_candidates']==[1,2,3,4]
    assert len(version['confusion_counts'])==4 and sum(map(sum,version['confusion_counts']))==4
    assert all(sum(row)==0 for row in version['confusion_counts'][1:])
    states=report['pair_joint_mass']['current_definition__current_version']
    cell=states['current_definition_wrong__current_version_correct']
    assert cell['count']==4 and cell['rate']==1 and cell['group_macro_rate']==1


def test_undefined_future_parent_tasks_do_not_enter_joint_denominators():
    valid=np.ones((4,12),dtype=bool);valid[:,8:]=False
    report=study.categorical_diagnostics(decision_data(np.ones((4,12),dtype=bool),valid),np.array(['g']*4))
    assert report['whole_families']['copy_parent']['n']==0
    assert all(cell['n']==0 for cell in report['pair_joint_mass']['current_definition__copy_parent'].values())


def test_prediction_ties_and_unsigned_margin_do_not_depend_on_oracle_mask():
    bundle=bundle_fixture(4);scores=np.zeros_like(bundle.y)
    first=target.HEADS[0];scores[:,first['indices'][1]]=2
    bundle.mask[:,first['indices'][1]]=False
    data=study.predictions(bundle,scores)
    assert (data['predicted'][:,0]==first['candidates'][1]).all()
    assert (data['margin'][:,0]==2).all()


def test_prediction_only_banks_roundtrip_and_detect_misalignment(tmp_path):
    rows=records();bodies=study.matched_bodies(rows)
    methods={m:decision_data(np.ones((4,12),dtype=bool)) for m in study.METHODS}
    identity=dict(evaluation_role=study.ROLE,config_hash='a'*64)
    path=tmp_path/'predictions.npz'
    study._save_predictions(path,identity,rows,bodies,methods)
    loaded=study._read_predictions(path,study._pin(path),identity,rows,bodies)
    assert all(np.array_equal(loaded[m]['predicted'],methods[m]['predicted']) for m in methods)
    changed=deepcopy(rows);changed[0]['id']='changed'
    with pytest.raises(ValueError,match='case/schema'):
        study._read_predictions(path,study._pin(path),identity,changed,bodies)


def test_prediction_only_banks_reject_inconsistent_correctness(tmp_path):
    rows=records();bodies=study.matched_bodies(rows)
    methods={m:decision_data(np.ones((4,12),dtype=bool)) for m in study.METHODS}
    path=tmp_path/'predictions.npz';identity={'role':'fixture'}
    study._save_predictions(path,identity,rows,bodies,methods)
    with np.load(path,allow_pickle=False) as archive:arrays={k:archive[k].copy() for k in archive.files}
    arrays['correct'][0,0,0]=False;np.savez(path,**arrays)
    with pytest.raises(ValueError,match='correctness'):
        study._read_predictions(path,study._pin(path),identity,rows,bodies)


def test_original_saved_metrics_must_reproduce_exactly():
    bundle=bundle_fixture();train=np.arange(8)<4;dev=np.flatnonzero(~train);weights=np.ones(4)
    scores=np.full(bundle.y.shape,np.nan);scores[:,bundle.mask.any(axis=0)]=bundle.y[:,bundle.mask.any(axis=0)]
    sub=target.subset(bundle,dev)
    support=study.original._train_support(bundle,train)
    prior=study.original._prior(bundle,train,weights)
    fit=dict(metrics=dict(direct=study.original.metrics(sub,scores[dev],support),
        training_prior=study.original.metrics(sub,prior[dev],support),
        random_prefix_control=study.original.metrics(sub,scores[dev],support)))
    assert np.array_equal(study.verify_original_metrics(bundle,bundle,train,weights,dev,scores,scores,fit),prior,equal_nan=True)
    changed=deepcopy(fit);changed['metrics']['direct']['whole_categorical_families']['current_definition']['accuracy']=.25
    with pytest.raises(ValueError,match='exactly reproduce'):
        study.verify_original_metrics(bundle,bundle,train,weights,dev,scores,scores,changed)


def test_config_requires_two_distinct_pinned_studies_and_separate_outputs(tmp_path):
    config=dict(evaluation_role=study.ROLE,readout_configs=[{'path':str(tmp_path/'a.json'),'sha256':'a'*64},
        {'path':str(tmp_path/'b.json'),'sha256':'b'*64}],declared_plan=str(tmp_path/'plan.md'),
        declared_plan_sha256='c'*64,run_dir=str(tmp_path/'run'),report=str(tmp_path/'report.md'))
    assert study._config(config)==config
    with pytest.raises(ValueError):study._config({**config,'readout_configs':[config['readout_configs'][0]]*2})
    with pytest.raises(ValueError):study._config({**config,'report':str(tmp_path/'run'/'registration.json'/'bad.md')})
    with pytest.raises(ValueError):study._config({**config,'run_dir':str(tmp_path/'plan.md'/'run')})
