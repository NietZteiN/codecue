"""Finite source/target, control, transfer and publication regression checks."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import overnight_relationship_readouts as study
from codecue.binding import relationship_readouts as original
from codecue.binding import relationship_targets as target
from codecue.binding import relationships
from codecue.binding.datasets import digest
from codecue.binding.programs import rename


def row(group=0,parent=1,query=0,lexical=0,computed=False,case=None):
    values=[2+group,3+group,5+group,7+group]
    expressions=[f'32 - {32-value}' for value in values] if computed else list(map(str,values))
    parents=[parent,0,1,2]
    source='\n'.join([*(f'v{i} = {value}' for i,value in enumerate(expressions)),
        *(f'v{i} = v{p}' for i,p in enumerate(parents)),f'v{query}'])
    mapping={f'v{i}':f'{"cell" if lexical else "item"}_{i}' for i in range(4)}
    split='train' if group<2 else 'development'
    return dict(id=case or f'g{group}:p{parent}:q{query}:l{lexical}:f{int(computed)}',
        split=split,condition='neutral',template_id=f'g{group}',cluster_id=f'g{group}',component_id=f'g{group}',
        base_id=f'base{group}',lexical_realization=lexical,query_slot=query,
        source_form='computed' if computed else 'literal',canonical_source=source,source=rename(source,mapping),
        rename_map=mapping,variable_slots={f'v{i}':i for i in range(4)},
        numeric_seed=101,format_pair_id=f'g{group}:p{parent}:q{query}:l{lexical}',
        cohorts=['computed_roots'] if computed else ['query_twins']+(['numeric_replication'] if query==0 else []))


def cases(rows):
    return [dict(record=r,visible_prefixes=['\n'.join(r['source'].splitlines()[:4]),
        '\n'.join(r['source'].splitlines()[:8]),r['source']]) for r in rows]


def cfg(tmp_path,panel='numeric_replication'):
    return dict(evaluation_role=study.ROLE,capture_config=str(tmp_path/'capture.json'),capture_config_sha256='a'*64,
        declared_plan=str(tmp_path/'plan.md'),declared_plan_sha256='b'*64,primary_layer=24,panel=panel,
        run_dir=str(tmp_path/'out'),report=str(tmp_path/'report.md'))


@pytest.mark.parametrize('query',range(4))
@pytest.mark.parametrize('computed',[False,True])
def test_target_only_normalization_preserves_actual_query_ancestry(query,computed):
    actual=row(query=query,computed=computed)
    source_before=actual['source']
    normalized=study.canonical_target_row(actual)
    assert normalized['canonical_source'].splitlines()[:4]==['v0 = 2','v1 = 3','v2 = 5','v3 = 7']
    assert normalized['canonical_source'].endswith('\nv0')
    assert actual['source']==source_before
    b=study.targets([actual],8)
    expected=relationships.labels_at(actual['canonical_source'],7,actual['variable_slots'],output_visible=True)
    ancestors=set(expected['output']['structural_ancestors'])
    for spec in target.COLUMNS:
        if spec['family']=='output_ancestor':assert bool(b.y[0,spec['index']])==(spec['source_node'] in ancestors)
    np.testing.assert_array_equal(b.numeric_truth,[[3,3,3,3]])
    assert b.descriptive['actual_query_output_ancestry'] and b.descriptive['target_only_root_canonicalization']


@pytest.mark.parametrize('problem',['query','roots','parents','surface','literal_expression','computed_expression'])
def test_source_target_metadata_mismatches_fail(problem):
    actual=row(computed=problem=='computed_expression')
    if problem=='query':actual['query_slot']=True
    elif problem=='roots':actual['root_values']=[99]*4
    elif problem=='parents':actual['parent_slots']=[3]*4
    elif problem=='surface':actual['source']=actual['source'].replace(' = 2',' = 9',1)
    elif problem=='literal_expression':
        actual['canonical_source']=actual['canonical_source'].replace('v0 = 2','v0 = 1 + 1');actual['source']=rename(actual['canonical_source'],actual['rename_map'])
    else:
        actual['canonical_source']=actual['canonical_source'].replace('v0 = 32 - 30','v0 = 2');actual['source']=rename(actual['canonical_source'],actual['rename_map'])
    with pytest.raises(ValueError):study.source_facts(actual)


def test_large_target_banks_chunk_old_oracle_without_losing_ids(monkeypatch):
    rows=[row(group=i%4,case=f'case{i}') for i in range(7)]
    monkeypatch.setattr(target,'MAX_ROWS',2)
    bundle=study.targets(rows,7)
    assert bundle.case_ids==tuple(r['id'] for r in rows)
    assert bundle.y.shape==(7,364) and not bundle.y.flags.writeable


def test_panel_selectors_keep_shared_literal_rows_and_computed_twins_separate():
    rows=[row(query=q) for q in range(4)]+[row(computed=True)]
    cap=cases(rows)
    assert study.select_panel(cap,'numeric_replication').tolist()==[0]
    assert study.select_panel(cap,'query_twins').tolist()==[0,1,2,3]
    assert study.select_panel(cap,'computed_roots').tolist()==[4]


@pytest.mark.parametrize('seed',study.SEEDS)
def test_controls_preserve_whole_program_marginals_queries_lexical_ties_and_visibility(seed):
    rows=[study.source_facts(row(group=g,parent=p,query=q,lexical=l))
        for g in range(4) for p in [1,2,3] for l in [0,1] for q in range(4)]
    donor=study.coherent_donors(rows,seed)
    assert set(donor.tolist())==set(range(len(rows)))
    for i,j in enumerate(donor):
        assert rows[i]['split']==rows[j]['split']
        assert rows[i]['template_id']!=rows[j]['template_id']
        assert rows[i]['query_slot']==rows[j]['query_slot']
        assert rows[i]['lexical_realization']==rows[j]['lexical_realization']
    bundles={site:study.targets(rows,site) for site in study.SITES}
    study._verify_prefix_controls(cases(rows),bundles,donor)
    for bundle in bundles.values():
        for split in ['train','development']:
            selected=np.asarray([r['split']==split for r in rows])
            np.testing.assert_array_equal(np.sort(bundle.y[selected],axis=0),np.sort(bundle.y[donor[selected]],axis=0))
    # Query/lexical relatives keep a common donor base and parent variant.
    relatives={}
    for i,r in enumerate(rows):relatives.setdefault((r['base_id'],r['parent_slots'][0]),set()).add((rows[donor[i]]['base_id'],rows[donor[i]]['parent_slots'][0]))
    assert all(len(values)==1 for values in relatives.values())


def test_cross_component_duplicate_initial_states_reject_impossible_control():
    rows=[study.source_facts(row(group=g,parent=p)) for g in range(4) for p in [1,2,3]]
    for r in rows:
        if r['template_id']=='g1':r['root_values']=rows[0]['root_values']
    with pytest.raises(ValueError,match='identical initial'):study.coherent_donors(rows,11)


def test_prefix_consistency_guard_rejects_bad_donor_labels():
    rows=[row(group=g,parent=p) for g in range(4) for p in [1,2,3]]
    bundles={site:study.targets(rows,site) for site in study.SITES}
    cap=cases(rows);donor=np.arange(len(rows));donor[[0,3]]=donor[[3,0]]
    with pytest.raises(ValueError,match='contradictory'):study._verify_prefix_controls(cap,bundles,donor)


def test_query_selection_uses_actual_slot_and_keeps_other_values_separate():
    rows=[row(query=q) for q in range(4)];bundle=study.targets(rows,7);scores=bundle.y.copy()
    for i,r in enumerate(rows):
        columns=[s['index'] for s in target.COLUMNS if s['kind']=='value_class' and s['slots']==[r['query_slot']]]
        scores[i,columns]=0;scores[i,columns[0]]=1
    result=study._selection(bundle,scores,rows)
    np.testing.assert_array_equal(result['queried_value_correct'],0)
    np.testing.assert_array_equal(result['unqueried_value_correct'],1)
    np.testing.assert_array_equal(result['queried_parent_correct'],1)


@pytest.mark.parametrize('problem',['role','extra','layer','sha','report','transfer','transfer_panel','output_contains_input'])
def test_config_guards(problem,tmp_path):
    c=cfg(tmp_path)
    if problem=='role':c['evaluation_role']='final_confirmation'
    elif problem=='extra':c['alpha']=1
    elif problem=='layer':c['primary_layer']=True
    elif problem=='sha':c['capture_config_sha256']='wrong'
    elif problem=='report':c['report']=str(tmp_path/'capture.json')
    elif problem=='transfer':c['transfer_from']='literal.json'
    elif problem=='transfer_panel':c.update(transfer_from='literal.json',transfer_from_sha256='c'*64)
    else:c['run_dir']=str(tmp_path)
    with pytest.raises(ValueError):study._config(c)


def test_guarded_metadata_failures_precede_capture_payload(tmp_path,monkeypatch):
    c=cfg(tmp_path);c['declared_plan_sha256']='c'*64
    Path(c['declared_plan']).write_text('fixed plan')
    monkeypatch.setattr(study,'_source',lambda *args: {'synthetic':True})
    monkeypatch.setattr(study,'_capture',lambda:pytest.fail('plan mismatch before capture'))
    with pytest.raises(ValueError,match='plan'):study._metadata(c)


@pytest.mark.parametrize('reserved',['registration.json','hidden_layer24_site3_seed11.npz'])
def test_report_cannot_be_nested_under_reserved_output_files(tmp_path,reserved):
    c=cfg(tmp_path);c['report']=str(Path(c['run_dir'])/reserved/'report.md')
    with pytest.raises(ValueError,match='nested'):study._config(c)


def test_selected_feature_load_uses_only_needed_chunks_and_exact_panel_order(monkeypatch):
    chunks=[dict(first=0,rows=3,path='first'),dict(first=3,rows=3,path='second')]
    checked=dict(feature_shape=[6,3,4,2],chunks=chunks,cases=list(range(6)),config={'fixed':True})
    called=[]
    def load(entry,cases,config):
        called.append(entry['path']);assert config=={'fixed':True}
        return np.stack([np.full((3,4,2),v,dtype=np.float32) for v in cases]),(0,0.)
    monkeypatch.setattr(study,'_capture',lambda:SimpleNamespace(load_chunk=load))
    result=study._load(checked,np.asarray([1,4,5]))
    assert called==['first','second']
    np.testing.assert_array_equal(result[:,0,0,0],[1,4,5])


def test_literal_transfer_uses_verified_parameters_without_fit(tmp_path,monkeypatch):
    rows=[row(group=i%4,case=f'case{i}') for i in range(8)];bundle=study.targets(rows,7)
    train=np.arange(8)<4;x=np.random.default_rng(19).normal(size=(8,5));donor=np.arange(8)
    p=tmp_path/'literal.npz';model,active,_,_=original._fit_bank(p,x,bundle,train,np.ones(4),donor,'a'*64)
    entry=original._artifact(p)
    monkeypatch.setattr(original,'ridge_fit',lambda *args,**kwargs:pytest.fail('transfer never fits'))
    changed=x+0.25;result=study._transfer_predict(entry,changed,bundle,'a'*64)
    np.testing.assert_array_equal(result[:,active],model.predict(changed)[:,:len(active)])
    assert np.isnan(result[:,~bundle.mask.all(axis=0)]).all()
    bad=dict(entry,sha256='b'*64)
    with pytest.raises(ValueError,match='differs'):study._transfer_predict(bad,changed,bundle,'a'*64)


def test_transfer_publication_resume_is_exact_and_rejects_changed_scores(tmp_path):
    p=tmp_path/'transfer.npz';scores=np.array([[1.,np.nan]])
    study._save_transfer(p,scores,['c'],['a'],'a'*64);before=p.read_bytes()
    study._save_transfer(p,scores,['c'],['a'],'a'*64);assert p.read_bytes()==before
    with pytest.raises(ValueError,match='predictions differ'):study._save_transfer(p,np.array([[0.,np.nan]]),['c'],['a'],'a'*64)


def test_transfer_matches_actual_literal_computed_sources_before_parameter_access(tmp_path,monkeypatch):
    literal=row();computed=row(computed=True)
    checked={'cases':cases([literal,computed])}
    literal_config=cfg(tmp_path/'literal');Path(literal_config['run_dir']).mkdir(parents=True)
    (Path(literal_config['run_dir'])/study.COMPLETION).write_text('{"synthetic":true}')
    p=tmp_path/'literal_config.json';p.write_text(json.dumps(literal_config))
    config=cfg(tmp_path/'computed','computed_roots');config.update(transfer_from=str(p),transfer_from_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    monkeypatch.setattr(study,'completed_result',lambda c:{'verified_without_array_access':True})
    result=study._transfer(config,checked,[study.source_facts(computed)])
    assert result['matched_literal_ids']==[literal['id']]
    bad=study.source_facts(computed);bad['root_values'][0]+=1
    with pytest.raises(ValueError,match='scientific targets differ'):study._transfer(config,checked,[bad])
    mismatch=dict(config,capture_config_sha256='c'*64)
    with pytest.raises(ValueError,match='same pinned'):study._transfer(mismatch,checked,[study.source_facts(computed)])


def test_completed_receipt_tamper_rejected_before_any_array_load(tmp_path,monkeypatch):
    c=cfg(tmp_path);out=Path(c['run_dir']);out.mkdir()
    (out/study.COMPLETION).write_text(json.dumps({'status':'complete_exploratory','evaluation_role':'wrong'}))
    monkeypatch.setattr(study,'_metadata',lambda c:({'source':'fixed'},{},None,None,[{}]))
    monkeypatch.setattr(np,'load',lambda *args,**kwargs:pytest.fail('receipt role before arrays'))
    with pytest.raises(ValueError,match='receipt'):study.completed_result(c)


def result_fixture(tmp_path):
    c=cfg(tmp_path);out=Path(c['run_dir']);out.mkdir()
    original.immutable(out/'registration.json',b'{"synthetic":true}')
    result=dict(status='complete_exploratory',evaluation_role=study.ROLE,config_hash=digest(c),
        analysis_source={'synthetic':True},runtime=dict(threads=1,slurm_job_id='first',wall_seconds=1.),
        panel='numeric_replication',source_form='literal',cases=24,model='synthetic',primary_layer=24,parameter_replay_rows=1080,
        literal_transfer_rows=0,summaries={'3':{'algebraic':{'status':'qualified','methods':{},'comparisons':{}},'per_query':{}},
            '7':{'structural':{'methods':{}},'per_query':{}},'8':{'structural':{'methods':{}},'per_query':{}}},
        primary_training_support_qualified=True)
    return c,result


@pytest.mark.parametrize('failed_file',['results_v1.json','report.md','audit.json'])
def test_finalization_recovers_after_commits_and_preserves_original_runtime(tmp_path,monkeypatch,failed_file):
    c,result=result_fixture(tmp_path);publish=original.immutable
    def fail(path,payload):
        publish(path,payload)
        if Path(path).name==failed_file:raise RuntimeError('injected interruption')
    monkeypatch.setattr(original,'immutable',fail)
    with pytest.raises(RuntimeError):study._finish(c,result,{})
    monkeypatch.setattr(original,'immutable',publish)
    resumed=deepcopy(result);resumed['runtime']=dict(threads=2,slurm_job_id='retry',wall_seconds=2.)
    completed=study._finish(c,resumed,{})
    assert completed['runtime']==result['runtime']
    receipt=json.loads((Path(c['run_dir'])/study.COMPLETION).read_text())
    assert receipt['completion_runtime']==resumed['runtime']


def test_finalization_rejects_changed_scientific_payload(tmp_path):
    c,result=result_fixture(tmp_path);study._finish(c,result,{})
    changed=deepcopy(result);changed['cases']+=1
    with pytest.raises(ValueError,match='scientific result differs'):study._finish(c,changed,{})


def test_tiny_full_grid_publishes_and_audits_all45_banks_without_capture_models(tmp_path,monkeypatch):
    """Exercise controller wiring, queries, rich JSON and receipt end to end."""
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log,'note_artifact',lambda *args,**kwargs:None)
    rows=[]
    for group in range(27):
        for parent in (1,2,3):
            item=row(parent=parent,case=f'group{group}:parent{parent}')
            values=[2,3,5,target.VALUE_CLASSES[group]]
            item.update(template_id=f'group{group}',cluster_id=f'group{group}',component_id=f'group{group}',
                base_id=f'base{group}',split='train' if group<18 else 'development')
            source='\n'.join([*(f'v{i} = {v}' for i,v in enumerate(values)),
                f'v0 = v{parent}','v1 = v0','v2 = v1','v3 = v2','v0'])
            item['canonical_source']=source;item['source']=rename(source,item['rename_map'])
            rows.append(study.source_facts(item))
    capcases=cases(rows);capfolder=tmp_path/'capture';capfolder.mkdir()
    (capfolder/'completion_manifest_v1.json').write_text('{"synthetic":true}')
    config=cfg(tmp_path);n=len(rows)
    checked=dict(config={'run_dir':str(capfolder)},cases=capcases,feature_shape=[n,3,4,4],
        chunks=[],model='synthetic',model_revision='synthetic-v1',layers=[8,16,24,31],summary={'model_prefill_cases':0})
    source={'snapshot':'synthetic','snapshot_id':'unit','source_sha256':'d'*64,'frozen_manifest_sha256':'e'*64}
    monkeypatch.setattr(study,'_metadata',lambda *args,**kwargs:(source,checked,np.arange(n),capcases,rows))
    features=np.random.default_rng(13).normal(size=(n,3,4,4)).astype(np.float32)
    monkeypatch.setattr(study,'_load',lambda *args:features)
    monkeypatch.setenv('SLURM_JOB_ID','synthetic-unit')
    result=study.run(config)
    assert result['factorizations']==45 and result['parameter_replay_rows']==45*n
    assert result['new_model_queries']==0 and result['literal_transfer_rows']==0
    assert len(list(Path(config['run_dir']).glob('*.npz')))==45
    assert study.completed_result(config)==result
    assert study.audit(config)['status']=='passed'
    monkeypatch.setattr(original,'ridge_fit',lambda *args,**kwargs:pytest.fail('completed reuse never fits'))
    assert study.run(config)==result
    assert 'Source-valued' in Path(config['report']).read_text()
