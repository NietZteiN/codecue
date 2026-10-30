from copy import deepcopy
from dataclasses import replace
import json

import numpy as np
import pytest

from codecue.binding import grammar_identity_review as study


def fixture(n=6):
    rows=[];owners=[];statuses=[];y=np.zeros((n,192))
    for i in range(n):
        rotation=i%4
        w=np.asarray([[(v+rotation)%4 for v in (0,0,1,0)]])
        p=np.asarray([[(v+rotation)%4 for v in (1,2,0,3)]])
        ids=study.grammar.owners_to_identities(w,p);wi,pi=ids['write_ids'][0],ids['parent_ids'][0]
        final=[1]*4
        for slot in w[0]:final[slot]+=1
        status={kind:['current' if code%4+1==final[code//4] else 'obsolete' for code in values]
                for kind,values in (('assignment',wi),('parent',pi))}
        owners.append(dict(assignment=w[0].tolist(),parent=p[0].tolist()));statuses.append(status)
        rows.append(dict(id=f'c{i}',component_id='g'+str(i%2),template_id='g'+str(i%2),
            profile_id='3_1_0_0',split='train' if i<2 else 'development'))
        for head in study.target.HEADS:
            kind,component=head['family'].split('_');code=(wi if kind=='assignment' else pi)[head['event_index']]
            candidate=int(code) if component=='joint' else int(code)//4 if component=='owner' else int(code)%4+1
            y[i,head['indices'][head['candidates'].index(candidate)]]=1
    desc=dict(control=False,profile_ids=[r['profile_id'] for r in rows],syntax_owners=owners,
        event_capture_status=statuses,event_truth_statements=[dict(assignment=[4,5,6,7],parent=[1,2,5,3]) for _ in rows],
        canonical_visible_prefixes=['body'+str(i) for i in range(n)],canonical_output_visible_prefixes=['body'+str(i) for i in range(n)])
    bundle=study.target.TargetBundle(y,np.ones_like(y,dtype=bool),study.target.COLUMNS,
        tuple(r['id'] for r in rows),tuple(r['component_id'] for r in rows),tuple(r['split'] for r in rows),7,desc)
    sham=np.zeros_like(y)
    for head in study.target.HEADS:
        candidate=1 if head['family'].endswith('_version') else 0
        sham[:,head['indices'][head['candidates'].index(candidate)]]=1
    control=replace(bundle,y=sham,descriptive=dict(desc,control=True))
    return rows,bundle,control


def tables_fixture():
    rows,bundle,control=fixture();train=np.asarray([r['split']=='train' for r in rows]);dev=np.flatnonzero(~train)
    weights=study.group_weights([r for r,use in zip(rows,train) if use],17).astype(np.float64)
    tables=np.stack([bundle.y[dev],study.original._CORE._prior(bundle,train,weights)[dev],control.y[dev],
                    study.target.syntax_owner_version_prior(bundle,train,weights)[dev]])
    return rows,bundle,control,train,dev,weights,tables


def config(tmp_path):
    return dict(evaluation_role=study.ROLE,readout_configs=[dict(path=str(tmp_path/'a.json'),sha256='a'*64),
        dict(path=str(tmp_path/'b.json'),sha256='b'*64)],declared_plan=str(tmp_path/'plan.md'),declared_plan_sha256='c'*64,
        run_dir=str(tmp_path/'out'),report=str(tmp_path/'report.md'))


def test_exact192_head_layout_and_historical_factorized_reference():
    _,bundle,_=fixture();result=study.head_predictions(bundle,bundle.y)
    assert result['predicted'].shape==(6,24) and result['correct'].all()
    joint=study._ids(bundle,bundle.y);marginal=study._ids(bundle,bundle.y,'marginal')
    np.testing.assert_array_equal(joint,marginal)
    w,p=study._joint_tables(bundle.y)
    assert w.shape==p.shape==(6,4,16)
    assert np.argmax(w[0,0])==1 and np.argmax(p[0,0])==4
    scores=bundle.y.copy();h=study.HEADS['assignment_owner/4'];scores[:,h['indices']]=0;scores[:,h['indices'][3]]=2
    assert np.all(study._ids(bundle,scores,'marginal')[0][:,0]//4==3)
    np.testing.assert_array_equal(study._ids(bundle,scores)[0],joint[0])


def test_scoped_changes_and_individual_head_transition_counts():
    _,bundle,_=fixture();before=study._ids(bundle,bundle.y);after=(before[0].copy(),before[1].copy())
    after[1][0,0]=(after[1][0,0]+4)%16
    result=study._transitions(bundle,before,after,np.ones(6,dtype=bool))
    assert result['assignment']['changed']['correct']==0 and result['parent']['changed']['correct']==1
    assert result['combined_eight']['changed']['correct']==1
    assert result['per_head']['parent/4']['harmed']['correct']==1
    assert result['per_head']['assignment/4']['harmed']['correct']==0


@pytest.fixture(scope='module')
def evaluated():
    rows,bundle,control,train,dev,weights,tables=tables_fixture()
    real=study.target.subset(bundle,dev);sham=study.target.subset(control,dev)
    diagnostic,decoded,free=study._evaluate_bank(real,sham,tables)
    return rows,bundle,control,dev,tables,diagnostic,decoded,free


def test_real_monotonicity_and_unlawful_sham_ceiling(evaluated):
    _,_,_,_,_,diagnostic,decoded,free=evaluated
    assert decoded.shape==(4,4,4,8) and free.shape==(4,2,4,8)
    assert diagnostic['source_owner_counter']['whole']['combined_eight']['accuracy']==1.
    direct=diagnostic['methods']['direct'];sham=diagnostic['methods']['random_prefix_control']
    for rule in study.RULES:
        assert direct['rules'][rule]['own_task']['whole']['combined_eight']['accuracy']==1.
        assert sham['free_joint']['whole']['combined_eight']['accuracy']==1.
        assert sham['rules'][rule]['truth_lawfulness_ceiling']['accuracy']==0.
        assert sham['rules'][rule]['own_task']['whole']['combined_eight']['accuracy']==0.
        assert sham['rules'][rule]['transitions']['free_joint']['combined_eight']['harmed']['correct']==4
        assert sham['rules'][rule]['same_evidence_lawful_free_preserved'] is True
    assert set(direct['historical_reference_lawfulness'])=={'free_joint','free_marginal'}
    assert 'parent_version_mismatch' in direct['historical_reference_lawfulness']['free_marginal']['no_self']['flags']


def test_all_exact_objectives_retained_and_same_evidence_reference_is_distinct(evaluated):
    diagnostic=evaluated[5]
    for method in study.METHODS:
        for rule,item in diagnostic['methods'][method]['rules'].items():
            exact=item['exact_objective_checks']
            assert len(exact['score_numerators'])==len(exact['projection_penalty_exponents'])==4
            assert len(exact['path_code'])==4 and exact['selected_and_free_path_scores_recomputed']
    direct=diagnostic['methods']['direct']
    assert direct['free_marginal']['whole']['combined_eight']['accuracy']==1.
    assert direct['rules']['owner_marginal_allow_self']['free_objective']['whole']['combined_eight']['accuracy']==0.


def test_missing_unused_joint_candidate_is_wrong_without_false_monotonicity_assertion():
    _,bundle,control,_,dev,_,tables=tables_fixture();tables[0,0,15]=np.nan
    diagnostic,decoded,_=study._evaluate_bank(study.target.subset(bundle,dev),study.target.subset(control,dev),tables)
    direct=diagnostic['methods']['direct']
    assert direct['free_joint']['whole']['combined_eight']['accuracy']==1.
    for item in direct['rules'].values():
        assert item['missing_cases']==1 and item['own_task']['whole']['combined_eight']['n']==4
        assert item['transitions']['free_joint']['combined_eight']['harmed']['correct']==1
        assert item['exact_objective_checks']['score_numerators'][0] is None
    assert np.all(decoded[0,:,0]==-1)


def test_original_four_methods_reproduce_before_grammar(evaluated):
    rows,bundle,control,train,dev,weights,tables=tables_fixture()
    fit=dict(metrics=study.original._CORE._score_methods(bundle,control,train,weights,dev,bundle.y,control.y))
    study._verify_metrics(dict(dev=dev),fit,bundle,control,train,weights,tables)
    altered=tables.copy();altered[0,0,0]+=100
    with pytest.raises(ValueError,match='original metrics'):study._verify_metrics(dict(dev=dev),fit,bundle,control,train,weights,altered)


def test_new_score_archive_preserves_full_tables_ids_and_inf_missing_policy(tmp_path,evaluated):
    rows,_,_,dev,tables,_,decoded,free=evaluated;records=[rows[i] for i in dev]
    cfg=config(tmp_path);entry=dict(path='old.npz',bytes=123,sha256='d'*64)
    expected=study._bank_identity(cfg,'llama8b','bank',entry,records)
    identity=study._bank_identity(cfg,'llama8b','bank',entry,records,dict(features_sha256='f'*64))
    path=tmp_path/'scores.npz';study._save_bank(path,identity,records,tables,decoded,free)
    restored=study._load_bank(path,study._pin(path),expected,records)
    np.testing.assert_array_equal(restored[0],tables);np.testing.assert_array_equal(restored[1],decoded)
    with pytest.raises(ValueError,match='provenance'):study._load_bank(path,study._pin(path),dict(expected,model='other'),records)
    with pytest.raises(ValueError,match='ordered'):study._load_bank(path,study._pin(path),expected,list(reversed(records)))
    other=tmp_path/'missing.npz';missing=tables.copy();missing[0,0,15]=np.inf
    study._save_bank(other,identity,records,missing,decoded,free)
    assert np.isinf(study._load_bank(other,study._pin(other),expected,records)[0][0,0,15])


def test_source_counter_does_not_decode_model_predictions_with_a_source_map(evaluated):
    _,bundle,control,dev,tables,*_=evaluated
    bundle=study.target.subset(bundle,dev);control=study.target.subset(control,dev)
    poison=deepcopy(bundle.descriptive);poison['event_truth_statements']='not a decoder input'
    actual=study._evaluate_bank(replace(bundle,descriptive=poison),control,tables)
    np.testing.assert_array_equal(actual[1],evaluated[6])


def valid_original_fixture():
    cfg=dict(evaluation_role=study.original.ROLE,primary_layer=24)
    fit=dict(snapshot_id=study.FIT_SNAPSHOT,source_sha256=study.FIT_SHA)
    capture=dict(snapshot_id=study.CAPTURE_SNAPSHOT,source_sha256=study.CAPTURE_SHA)
    checked=dict(source=capture,dataset_sha256=study.target.DATASET_SHA256)
    common=dict(evaluation_role=study.original.ROLE,config_hash=study.digest(cfg),fit_source=fit,capture_source=capture,
        fit_banks=30,factorizations=30,parameter_replay_rows=172800,new_model_queries=0,generated_holdouts_opened=False)
    receipt=dict(common,status='complete_exploratory',schema_version=1,artifacts={})
    proof=dict(common,status='passed',source_artifacts={},new_fits=0,exact_saved_parameter_score_replays=True,
        all_real_and_control_scores_replayed=True,all_scientific_metrics_recomputed=True,train_support_and_control_marginals_recomputed=True)
    result=dict(common,status='complete_exploratory',cases=5760,training_rows=4320,development_rows=1440,training_groups=45,development_groups=15,
        protocol=study.original.protocol(),target_columns=list(study.target.COLUMNS))
    return cfg,fit,checked,result,receipt,proof


@pytest.mark.parametrize('problem',['fit_source','capture_source','proof_failed','new_fit','bad_role','schema','banks','replay_missing'])
def test_original_receipt_and_proof_rejected_before_score_access(problem):
    cfg,fit,checked,result,receipt,proof=valid_original_fixture()
    study._validate_original(cfg,fit,checked,result,receipt,proof)
    if problem=='fit_source':fit['snapshot_id']='other'
    elif problem=='capture_source':checked['source']['snapshot_id']='other'
    elif problem=='proof_failed':proof['status']='failed'
    elif problem=='new_fit':proof['new_fits']=1
    elif problem=='bad_role':receipt['evaluation_role']='other'
    elif problem=='schema':result['target_columns']=result['target_columns'][:-1]
    elif problem=='banks':receipt['fit_banks']=45
    elif problem=='replay_missing':proof['all_scientific_metrics_recomputed']=False
    with pytest.raises(ValueError):study._validate_original(cfg,fit,checked,result,receipt,proof)


@pytest.mark.parametrize('problem',['role','duplicate','pin','reserved_report','input_ancestor'])
def test_config_and_input_overlap_guards(tmp_path,problem):
    cfg=config(tmp_path)
    if problem=='role':cfg['evaluation_role']='other'
    elif problem=='duplicate':cfg['readout_configs'][1]=cfg['readout_configs'][0]
    elif problem=='pin':cfg['readout_configs'][0]['sha256']='bad'
    elif problem=='reserved_report':cfg['report']=str(tmp_path/'out'/study.PROOF/'bad.md')
    elif problem=='input_ancestor':cfg['run_dir']=str(tmp_path/'plan.md'/'out')
    with pytest.raises(ValueError):study._config(cfg)


def test_guard_covers_original_capture_and_plan_folders(tmp_path):
    cfg=config(tmp_path)
    for source in (tmp_path/'out',tmp_path/'out'/'capture.npz',tmp_path/'report.md'):
        with pytest.raises(ValueError):study._disjoint(cfg,[source])
    cfg['run_dir']=str(tmp_path/'oldcapture'/'unused'/'new')
    with pytest.raises(ValueError):study._disjoint(cfg,[tmp_path/'oldcapture'])


def test_exact125_output_inventory_and_no_silent_primary_seed_selection(tmp_path,evaluated):
    paths=study._paths(config(tmp_path))
    assert len(paths)==len(set(paths.values()))==125
    assert sum(p.suffix=='.npz' for p in paths.values())==60
    small=study._cell_summary(evaluated[5]);cells=[]
    for model,_,layers,_ in study.saved.PROFILES.values():
        for site in study.SITES:
            for backend,layer in [('hidden',v) for v in layers]+[('surface',-1)]:
                for seed in study.SEEDS:cells.append(dict(model=model,site=site,backend=backend,layer=layer,seed=seed,summary_methods=small))
    result=dict(config_hash='a'*64,source={'snapshot_id':'synthetic'},cells=cells)
    summary=study._summary(result)
    assert summary['score_banks']==60 and summary['saved_score_rows_checked']==345600
    assert summary['development_prediction_rows']==86400 and len(summary['primary'])==2
    text=study._report(result);assert 'Prefix-sham' in text and 'No model or probe' in text
    result['cells']=[c for c in cells if not(c['model']=='llama8b' and c['backend']=='hidden' and c['layer']==24 and c['site']==7 and c['seed']==17)]
    with pytest.raises(ValueError,match='three fixed'):study._summary(result)


def test_exact_objective_tampering_is_detected():
    _,bundle,_=fixture();inputs=study._joint_tables(bundle.y)
    output=study.grammar.decode(*inputs);study._exact_checks(inputs,output,'joint')
    bad=dict(output,score_numerators=tuple('999' for _ in output['score_numerators']))
    with pytest.raises(ValueError,match='path scores'):study._exact_checks(inputs,bad,'joint')


def test_immutable_json_conflict(tmp_path):
    path=tmp_path/'audit.json';study._publish(path,{'synthetic':True});study._publish(path,{'synthetic':True})
    with pytest.raises(ValueError):study._publish(path,{'synthetic':False})


def test_audit_uses_new_scores_only_and_rejects_semantic_tamper_with_new_pin(tmp_path,monkeypatch):
    rows,bundle,control,train,dev,weights,tables=tables_fixture()
    cfg=config(tmp_path);out=tmp_path/'out';out.mkdir()
    name='hidden_layer24_site7_seed17';entry=dict(path='old_never_opened.npz',bytes=123,sha256='d'*64)
    records=[rows[i] for i in dev]
    diagnostic,decoded,free=study._evaluate_bank(study.target.subset(bundle,dev),study.target.subset(control,dev),tables)
    identity=study._bank_identity(cfg,'llama8b',name,entry,records,dict(features_sha256='f'*64))
    bank=out/'scores.npz';study._save_bank(bank,identity,records,tables,decoded,free)
    report=out/'diagnostic.json';study._publish(report,diagnostic)
    fit=dict(name=name,backend='hidden',layer=24,site=7,seed=17,
        metrics=study.original._CORE._score_methods(bundle,control,train,weights,dev,bundle.y,control.y))
    data=dict(records=rows,dev=dev,dev_records=records,fit_map={name:fit},inventory={name:entry})
    cell=dict(model='llama8b',name=name,backend='hidden',layer=24,site=7,seed=17,original_score_bank=entry,
        score_bank=study._pin(bank),diagnostic=study._pin(report),summary_methods=study._cell_summary(diagnostic))
    result=dict(source={'snapshot_id':'synthetic'},input_pins=[],cells=[cell])
    monkeypatch.setenv('SLURM_JOB_ID','synthetic-only')
    monkeypatch.setattr(study,'completed_result',lambda _:result)
    monkeypatch.setattr(study,'_metadata',lambda *a,**k:(result['source'],{'llama8b':data},[]))
    monkeypatch.setattr(study.target,'targets',lambda rows,site:replace(bundle,site=site))
    monkeypatch.setattr(study.target,'control_targets',lambda rows,site,seed:replace(control,site=site))
    monkeypatch.setattr(study.saved,'load_score_bank',lambda *a,**k:pytest.fail('audit reopened OLD score bank'))
    monkeypatch.setattr(study,'_summary',lambda _:dict(synthetic=True))
    monkeypatch.setattr(study,'_report',lambda _:'synthetic\n')
    study._publish(out/'summary.json',dict(synthetic=True));(tmp_path/'report.md').write_text('synthetic\n')
    study._publish(out/study.COMPLETION,dict(artifacts={}))
    proof=study.audit(cfg)
    assert proof['all_grammar_diagnostics_recomputed'] and proof['original_score_banks_reopened'] is False
    changed=deepcopy(diagnostic)
    changed['methods']['direct']['rules']['joint_allow_self']['own_task']['whole']['combined_eight']['accuracy']=.125
    report.write_bytes(study._bytes(changed));cell['diagnostic']=study._pin(report)
    with pytest.raises(ValueError,match='diagnostics differ'):study.audit(cfg)
