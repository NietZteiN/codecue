import hashlib
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import diversity_readouts as study
from codecue.binding import schedule_readouts as original


def result_fixture(diversity=False):
    engine=study if diversity else original
    fits=[]
    for site in original.SITES:
        for backend,layer in [('hidden',8),('hidden',16),('hidden',24),('hidden',31),('surface',-1)]:
            for seed in original.SEEDS:
                metrics={m:{'whole_categorical_families':{family:dict(accuracy=.5,group_macro_accuracy=.4)
                    for family in ('current_definition','current_version','copy_parent')}}
                    for m in ('direct','training_prior','random_prefix_control')}
                fits.append(dict(name=original._name(backend,layer,site,seed),backend=backend,
                                 layer=layer,site=site,seed=seed,metrics=metrics))
    return dict(model='synthetic',config_hash='a'*64,cases=engine.SOURCE_ROWS,
        training_rows=engine.TRAIN_ROWS,development_rows=engine.DEV_ROWS,
        factorizations=45,parameter_replay_rows=45*engine.SOURCE_ROWS,primary={'layer':24},fits=fits)


def config(tmp_path,role=study.ROLE):
    return dict(evaluation_role=role,capture_config=str(tmp_path/'capture.json'),
        capture_config_sha256='b'*64,declared_plan=str(tmp_path/'plan.md'),
        declared_plan_sha256='c'*64,primary_layer=24,run_dir=str(tmp_path/'readouts'),
        report=str(tmp_path/'report.md'))


def test_old_default_protocol_summary_and_report_bytes_are_preserved():
    result=result_fixture()
    hashes={
        'protocol':hashlib.sha256(original.publication._json_bytes(original.protocol())).hexdigest(),
        'summary':hashlib.sha256(original.publication._json_bytes(original._summary(result))).hexdigest(),
        'report':hashlib.sha256(original._report(result).encode()).hexdigest()}
    assert hashes=={
        'protocol':'25a7b231d54622e663fe7ed06e743c05ffa30afacaa368b6012f3ba610d20aa8',
        'summary':'67343d1a1d88ebd1ddc638ec69aa42a23ce247289e176b1e2888d36607f4483c',
        'report':'eb58ade5be4c505a1ff508ef8403426eb3ed0fdab0fbfa5852b58d91adf28f80'}


def test_engine_isolation_preserves_original_role_counts_and_policies():
    assert original.ROLE=='discovery_schedule_readouts_v1'
    assert (original.SOURCE_ROWS,original.TRAIN_ROWS,original.DEV_ROWS,original.TRAIN_GROUPS,original.DEV_GROUPS)==(2016,1320,696,10,5)
    assert (study.SOURCE_ROWS,study.TRAIN_ROWS,study.DEV_ROWS,study.TRAIN_GROUPS,study.DEV_GROUPS)==(5760,4320,1440,45,15)
    assert study.preflight.__globals__ is study._CORE.__dict__
    assert study.run.__globals__ is study._CORE.__dict__
    assert study.audit.__globals__ is study._CORE.__dict__
    assert study._CORE is not original
    assert study.LIMITATIONS is not original.LIMITATIONS
    assert original.MAX_RESULT==64*1024**2 and study.MAX_RESULT==192*1024**2
    new=study.protocol();old=original.protocol()
    assert {k:v for k,v in new.items() if k!='interval'}=={k:v for k,v in old.items() if k!='interval'}
    assert new['interval']=='none; all 15 development graph outcomes retained'
    assert new['seeds']==[17,29,43] and new['alpha']==100 and new['binary_threshold']==.5


def test_new_role_is_required_without_source_role_coercion(tmp_path):
    assert study._config(config(tmp_path))['evaluation_role']==study.ROLE
    with pytest.raises(ValueError):study._config(config(tmp_path,original.ROLE))
    with pytest.raises(ValueError):original._config(config(tmp_path))


def test_new_summary_and_report_use_new_counts_without_changing_grid():
    result=result_fixture(True)
    summary=study._summary(result)
    assert summary['evaluation_role']==study.ROLE
    assert (summary['cases'],summary['training_rows'],summary['development_rows'],summary['training_groups'],summary['development_groups'])==(5760,4320,1440,45,15)
    assert summary['fit_banks']==summary['factorizations']==45
    assert summary['parameter_replay_rows']==259200
    assert summary['primary']['hidden']['direct']['current_definition']==.5
    report=study._report(result)
    assert '5,760 source cases; 45 TRAIN and 15 DEV canonical graph families.' in report
    assert 'All 45 fixed feature/site/seed banks' in report
    assert '2,016 source cases' not in report


def metadata_fixture(tmp_path,monkeypatch,rows=5760,train_groups=45,dev_groups=15):
    cfg=config(tmp_path)
    cap_config=dict(run_dir=str(tmp_path/'capture'),dataset=str(tmp_path/'diversity.jsonl'),hidden_size=4096)
    cases=[]
    for group in range(train_groups+dev_groups):
        split='train' if group<train_groups else 'development'
        for item in range(96):
            cases.append(dict(record=dict(id=f'g{group}i{item}',template_id=f'g{group}',
                split=split,condition='neutral'),visible_prefixes=['a','b','c']))
    cases=cases[:rows]
    checked=dict(cases=cases,feature_shape=[len(cases),3,4,4096],
                 sites=['statement:3','statement:7','pre_answer'],layers=[8,16,24,31])
    monkeypatch.setattr(study._CORE,'_source',lambda *args,**kwargs:{'synthetic_fixture_only':True})
    monkeypatch.setattr(study._CORE.bounded,'_sha',lambda path:'c'*64)
    monkeypatch.setattr(study._CORE.bounded,'_json',lambda *args:cap_config)
    monkeypatch.setattr(study._CORE,'_capture',lambda:SimpleNamespace(completed_metadata=lambda _:checked))
    return cfg,checked


def test_new_metadata_requires_complete_5760_row_45_15_graph_capture(tmp_path,monkeypatch):
    cfg,checked=metadata_fixture(tmp_path,monkeypatch)
    _,actual,records=study._metadata(cfg,scheduled=False)
    assert actual is checked and len(records)==5760


@pytest.mark.parametrize('problem',['old_rows','group_count','feature_shape','missing_site'])
def test_new_metadata_rejects_old_or_incomplete_cohorts(tmp_path,monkeypatch,problem):
    if problem=='old_rows':cfg,checked=metadata_fixture(tmp_path,monkeypatch,rows=2016)
    else:cfg,checked=metadata_fixture(tmp_path,monkeypatch)
    if problem=='group_count':checked['cases'][-1]['record']['template_id']='extra-dev'
    if problem=='feature_shape':checked['feature_shape'][-1]=8192
    if problem=='missing_site':checked['sites']=['statement:3','statement:7']
    with pytest.raises(ValueError):study._metadata(cfg,scheduled=False)


def test_preflight_uses_diversity_counts_and_new_target_hook(tmp_path,monkeypatch):
    cfg,checked=metadata_fixture(tmp_path,monkeypatch)
    checked['model']='synthetic-fixture'
    monkeypatch.setattr(study._CORE,'_bundles',lambda records:({7:SimpleNamespace(columns=[None]*232)},None,{'fixture':True}))
    result=study.preflight(cfg)
    assert (result['cases'],result['training_rows'],result['development_rows'])==(5760,4320,1440)
    assert (result['training_graph_groups'],result['development_graph_groups'])==(45,15)
    assert result['target_columns']==232 and result['evaluation_role']==study.ROLE
    assert result['new_model_queries']==0 and result['raw_activation_arrays_loaded'] is False


@pytest.mark.parametrize('features,mode',[(7,'primal_cholesky'),(24,'dual_cholesky')])
def test_inherited_masked_fit_keeps_train_only_primal_and_dual_solvers(features,mode):
    rng=np.random.default_rng(11);x=rng.normal(size=(20,features));y=rng.normal(size=(20,3))
    mask=np.ones_like(y,dtype=bool);mask[:2,1]=False;y[~mask]=0
    train=np.arange(20)<12;weights=np.ones(12);ids=tuple(f'c{i}' for i in range(20))
    models,scores,control=study.fit_masked_columns(x,y,mask,y,train,weights,ids)
    assert len(models)==2
    assert all(model.metadata['mode']==mode for _,_,model in models)
    assert all(model.metadata['heldout_rows_used_for_fit']==0 for _,_,model in models)
    assert np.isfinite(scores).all() and np.array_equal(scores,control)
