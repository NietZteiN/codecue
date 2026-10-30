"""Joint-first conditionals, matched query placebo and bounded score-only I/O."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import hashlib
import io
import json

import numpy as np
import pytest

from codecue.binding import overnight_relationship_behavior_link as link


def config(tmp_path):
    models={}
    for key in link.MODELS:
        spec={}
        for panel in ('literal','computed','behavior'):
            for kind in ('config','completion'):
                name=panel+'_'+kind;spec[name]=str(tmp_path/(key+'_'+name+'.json'));spec[name+'_sha256']='a'*64
        models[key]=spec
    plan=tmp_path/'plan.md';plan.write_text('Declared saved-score diagnostic.\n')
    return dict(evaluation_role=link.ROLE,declared_plan=str(plan),declared_plan_sha256=hashlib.sha256(plan.read_bytes()).hexdigest(),
        models=models,run_dir=str(tmp_path/'analysis'),report=str(tmp_path/'analysis.md'))


def fixture():
    groups=np.repeat([f'g{i}' for i in range(9)],2)
    answer=np.tile([True,False],9);valid=np.ones(18,dtype=bool)
    graph=np.zeros((3,18));graph[0]=1
    values=np.zeros((3,18));values[1]=1
    return answer,valid,graph,values,groups


def test_joint_events_are_averaged_before_conditioning_not_multiplied_marginals():
    answer,valid,graph,values,groups=fixture()
    r=link.joint_summary(answer,valid,values,groups,graph_fits=graph)
    assert r['answer_accuracy']['point']==pytest.approx(.5)
    assert r['events']['graph']['decoding_correct']['point']==pytest.approx(1/3)
    assert r['events']['graph']['decoding_correct_and_answer_wrong']['point']==pytest.approx(1/6)
    assert r['events']['graph']['answer_correct_given_decoding_correct']['point']==pytest.approx(.5)
    both=r['events']['graph_and_queried_value']
    assert both['decoding_correct']['point']==0  # Product of averaged marginals would be1/9.
    assert both['answer_correct_given_decoding_correct']['point'] is None
    assert both['answer_correct_given_decoding_correct']['valid_draws']==0
    assert both['answer_correct_given_decoding_correct']['conditional_group_bootstrap_95'] is None
    assert r['joint_fits_averaged_first']


def test_graph_undefined_is_omitted_and_invalid_outputs_remain_wrong():
    answer,valid,_,values,groups=fixture();valid[1]=False
    r=link.joint_summary(answer,valid,values,groups)
    assert not r['graph_defined'] and set(r['events'])=={'queried_value'}
    assert r['invalid_response_fraction']['point']==pytest.approx(1/18)
    with pytest.raises(ValueError,match='binary answer'):link.joint_summary(answer,np.zeros(18,dtype=bool),values,groups)


def test_empty_and_sparse_condition_denominators_do_not_fabricate_intervals():
    answer,valid,graph,values,groups=fixture()
    empty=link.joint_summary(answer,valid,values,groups,selected=np.zeros(18,dtype=bool))
    assert empty['cases']==0 and empty['answer_accuracy']['point'] is None
    assert empty['answer_accuracy']['invalid_draws']==2000
    sparse=link.joint_summary(answer,valid,values,groups,selected=groups=='g0')
    assert sparse['answer_accuracy']['point']==pytest.approx(.5)
    assert 0<sparse['answer_accuracy']['valid_draws']<1900
    assert sparse['answer_accuracy']['conditional_group_bootstrap_95'] is None
    assert len(sparse['component_case_counts'])==9


@pytest.mark.parametrize('problem',['eight_groups','soft_correctness','two_fits','mask_shape'])
def test_joint_input_guards(problem):
    answer,valid,graph,values,groups=fixture();kwargs={}
    if problem=='eight_groups':groups[-2:]='g0'
    elif problem=='soft_correctness':values[0,0]=.5
    elif problem=='two_fits':values=values[:2]
    else:kwargs['selected']=np.ones(17,dtype=bool)
    with pytest.raises(ValueError):link.joint_summary(answer,valid,values,groups,**kwargs)


def query_fixture():
    records=[]
    for group in range(9):
        for query in range(4):
            records.append(dict(id=f'g{group}:q{query}',split='development',source_form='literal',component_id=f'g{group}',
                surface_body_id=f'b{group}',query_slot=query,source=f'x = {group}\ny = 1\nv{query}'))
    n=len(records);pre=np.zeros((3,n,4));pre[:,:,3]=1
    post=np.zeros_like(pre)
    for i,row in enumerate(records):post[:,i,row['query_slot']]=1
    return records,{3:pre,7:pre.copy(),8:post}


def test_query_comparison_holds_target_head_fixed_and_removes_recency_placebo():
    records,correct=query_fixture();r=link.query_diagnostic(records,correct)
    assert r['bodies']==9 and r['literal_cases']==36
    assert r['sites']['3']['query_by_target_matrix']['point']==[[0.,0.,0.,1.]]*4
    assert r['sites']['7']['fixed_slot_effect']['point']==[0.]*4
    assert r['sites']['8']['fixed_slot_effect']['point']==[1.]*4
    assert r['site8_minus_site7']['mean_slot_effect']['point']==1.
    assert r['site8_minus_site7']['mean_slot_effect']['conditional_group_bootstrap_95']==[1.,1.]
    assert r['other_slots_are_not_necessarily_irrelevant'] and not r['causal_use_established']


@pytest.mark.parametrize('problem',['missing_query','different_body','computed','not_three_fits'])
def test_query_pair_identity_guards(problem):
    rows,scores=query_fixture()
    if problem=='missing_query':rows[0]['query_slot']=1
    elif problem=='different_body':rows[0]['source']='changed\nv0'
    elif problem=='computed':rows[0]['source_form']='computed'
    else:scores[7]=scores[7][:2]
    with pytest.raises(ValueError):link.query_diagnostic(rows,scores)


def bank_fixture(tmp_path):
    path=tmp_path/'saved.npz';ids=['one','two','three','four'];indices=np.array([1,3])
    y=np.arange(12,dtype=float).reshape(4,3);mask=np.ones((4,3),dtype=bool);mask[:,-1]=False;y[:,-1]=0
    scores=y.copy();scores[~mask]=np.nan
    np.savez(path,case_ids=np.asarray(ids),config_hash=np.array('a'*64),targets=y,target_mask=mask,real_scores=scores,
        coef=np.array({'never':'decode parameters'},dtype=object),features=np.array({'never':'decode hidden states'},dtype=object))
    entry=dict(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    bundle=SimpleNamespace(y=y[indices],mask=mask[indices])
    return entry,ids,indices,bundle,scores[indices]


def test_score_reader_opens_only_scores_and_identity_arrays_not_parameters_or_features(tmp_path):
    entry,ids,indices,bundle,expected=bank_fixture(tmp_path)
    actual=link.load_scores(entry,ids,indices,bundle,'a'*64)
    np.testing.assert_array_equal(actual,expected)


@pytest.mark.parametrize('problem',['sha','bytes','cap'])
def test_byte_pins_fail_before_any_array_open(tmp_path,monkeypatch,problem):
    entry,ids,indices,bundle,_=bank_fixture(tmp_path)
    if problem=='sha':entry['sha256']='b'*64
    elif problem=='bytes':entry['bytes']+=1
    else:monkeypatch.setattr(link,'MAX_BANK',1)
    monkeypatch.setattr(link.np,'load',lambda *a,**k:pytest.fail('opened arrays before input byte verification'))
    with pytest.raises(ValueError):link.load_scores(entry,ids,indices,bundle,'a'*64)


def test_score_reader_checks_order_targets_and_masks(tmp_path):
    entry,ids,indices,bundle,_=bank_fixture(tmp_path)
    with pytest.raises(ValueError,match='ordered case'):link.load_scores(entry,list(reversed(ids)),indices,bundle,'a'*64)
    bundle.y=bundle.y.copy();bundle.y[0,0]+=1
    with pytest.raises(ValueError,match='target identities'):link.load_scores(entry,ids,indices,bundle,'a'*64)


@pytest.mark.parametrize('problem',['role','extra','missing_pin','wrong_model','collision'])
def test_configuration_role_pin_and_collision_guards(tmp_path,problem):
    cfg=config(tmp_path)
    if problem=='role':cfg['evaluation_role']='sealed_final_link'
    elif problem=='extra':cfg['layer']=8
    elif problem=='missing_pin':cfg['models']['llama8b'].pop('literal_config_sha256')
    elif problem=='wrong_model':cfg['models']['new_model']=cfg['models'].pop('llama8b')
    else:cfg['report']=cfg['declared_plan']
    with pytest.raises(ValueError):link._config(cfg)


def test_real_publication_requires_sbatch_and_current_frozen_source_before_inputs(tmp_path,monkeypatch):
    cfg=config(tmp_path);monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    monkeypatch.setattr(link,'_inputs',lambda cfg:pytest.fail('read original inputs before execution guard'))
    with pytest.raises(ValueError,match='SLURM'):link.run(cfg)
    monkeypatch.setenv('SLURM_JOB_ID','unit')
    monkeypatch.setattr(link.bounded,'_current_source',lambda cfg:(_ for _ in ()).throw(ValueError('unfrozen')))
    with pytest.raises(ValueError,match='unfrozen'):link.run(cfg)


def publication_fixture(tmp_path,monkeypatch):
    from codecue.binding import experiment_log
    cfg=config(tmp_path);source={'snapshot':'synthetic','source_sha256':'b'*64};calls=[];inputs={}
    for model in link.MODELS:
        panels={}
        for panel in ('literal','computed'):
            selected={}
            for i in range(18):
                path=tmp_path/(model+'_'+panel+'_'+str(i)+'.npz');path.write_bytes(b'saved-score-byte-fixture')
                selected[str(i)]=link._pin(path)
            panels[panel]={'selected':selected}
        inputs[model]=dict(key=model,panels=panels)
    monkeypatch.setattr(link,'_source',lambda *args:source)
    monkeypatch.setattr(link,'_inputs',lambda cfg:inputs)
    monkeypatch.setattr(experiment_log,'note_artifact',lambda *a,**k:None)
    def analyze(info):
        calls.append(info['key'])
        selected={panel+'/'+name:entry for panel,p in info['panels'].items() for name,entry in p['selected'].items()}
        return dict(model=info['key'],cases=2430,panels={},selected_score_banks=selected)
    monkeypatch.setattr(link,'_analyze',analyze)
    return cfg,calls


def test_atomic_publication_reuse_audit_and_no_additional_score_reads(tmp_path,monkeypatch):
    cfg,calls=publication_fixture(tmp_path,monkeypatch)
    first=link.run(cfg)
    assert len(calls)==2
    monkeypatch.setattr(link,'_analyze',lambda info:pytest.fail('reanalyzed completed result'))
    assert link.run(cfg)==first
    assert link.audit(cfg)['additional_array_loads']==0
    assert (Path(cfg['run_dir'])/'summary.json').exists()
    p=Path(cfg['run_dir'])/'results_v1.json';p.write_text(p.read_text()+' ')
    with pytest.raises(ValueError):link.audit(cfg)


@pytest.mark.parametrize('problem',['result_status','result_protocol','result_sealed','receipt_queries','receipt_raw','registration_protocol','selected_inventory'])
def test_semantically_invalid_resealed_publication_is_rejected(tmp_path,monkeypatch,problem):
    cfg,_=publication_fixture(tmp_path,monkeypatch);link.run(cfg)
    folder=Path(cfg['run_dir']);receipt_path=folder/'completion_manifest_v1.json';receipt=json.loads(receipt_path.read_text())
    if problem in ('receipt_queries','receipt_raw'):
        receipt['new_model_queries' if problem=='receipt_queries' else 'raw_activations_loaded']=1 if problem=='receipt_queries' else True
    else:
        key='registration' if problem=='registration_protocol' else 'results';path=Path(receipt['artifacts'][key]['path']);data=json.loads(path.read_text())
        if problem=='result_status':data['status']='failed'
        elif problem in ('result_protocol','registration_protocol'):data['protocol']={}
        elif problem=='result_sealed':data['generated_holdouts_opened']=True
        else:data['models']['llama8b']['selected_score_banks'].pop(next(iter(data['models']['llama8b']['selected_score_banks'])))
        path.write_text(json.dumps(data));receipt['artifacts'][key]=link._pin(path)
    receipt_path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError):link.audit(cfg)


def test_completed_reuse_repairs_missing_compact_logging_summary_without_score_reload(tmp_path,monkeypatch):
    cfg,_=publication_fixture(tmp_path,monkeypatch);result=link.run(cfg)
    (Path(cfg['run_dir'])/'summary.json').unlink()
    monkeypatch.setattr(link,'_analyze',lambda info:pytest.fail('loaded score arrays again'))
    assert link.run(cfg)==result
    assert (Path(cfg['run_dir'])/'summary.json').exists()
