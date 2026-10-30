"""Pinned score-reader guards and graph validity, using only finite CPU fixtures."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pytest

from codecue.binding import relationship_followup as study, relationship_targets as target


def bundle(site=7):
    rows=[]
    for i in range(4):
        values=(2,3,3,7);parents=(1 if i%2==0 else 2,0,1,2)
        source='\n'.join([*(f'v{j} = {v}' for j,v in enumerate(values)),
            *(f'v{j} = v{p}' for j,p in enumerate(parents)),'v0'])
        rows.append(dict(id=f'c{i}',split='train' if i<2 else 'development',
            cluster_id=f'g{i//2}',template_id=f'g{i//2}',canonical_source=source,source=source,
            rename_map={f'v{j}':f'v{j}' for j in range(4)},variable_slots={f'v{j}':j for j in range(4)}))
    return target.targets(rows,site)


def bank(tmp_path, change=None):
    b=bundle();donor=np.array([1,0,3,2]);weights=np.array([.7,1.3])
    scores=np.where(b.mask,b.y,np.nan)
    arrays=dict(config_hash=np.array('identity'),case_ids=np.asarray(b.case_ids),targets=b.y,
        target_mask=b.mask,training_weights=weights,donor_indices=donor,
        donor_case_ids=np.asarray(b.case_ids)[donor],active_columns=np.flatnonzero(b.mask.all(axis=0)),real_scores=scores)
    if change:change(arrays)
    stream=io.BytesIO();np.savez(stream,**arrays);payload=stream.getvalue()
    path=tmp_path/'scores.npz';path.write_bytes(payload)
    return dict(path=str(path),bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest()),b,weights,donor


def test_saved_score_reader_needs_no_feature_or_parameter_arrays(tmp_path):
    entry,b,weights,donor=bank(tmp_path)
    scores=study.load_scores(entry,b,config_hash='identity',weights=weights,donor=donor)
    np.testing.assert_equal(scores,np.where(b.mask,b.y,np.nan))


def test_bank_hash_and_bounds_checked_before_array_access(tmp_path,monkeypatch):
    entry,b,weights,donor=bank(tmp_path)
    monkeypatch.setattr(study.np,'load',lambda *a,**kw:pytest.fail('array reader reached before hash guard'))
    for changed in [dict(entry,sha256='a'*64),dict(entry,bytes=entry['bytes']+1),dict(entry,bytes=study.MAX_BANK_BYTES+1)]:
        with pytest.raises(ValueError):study.load_scores(changed,b,config_hash='identity',weights=weights,donor=donor)


@pytest.mark.parametrize('change',[
    lambda a:a.update(config_hash=np.array('other')),
    lambda a:a.update(case_ids=a['case_ids'][::-1]),
    lambda a:a.update(targets=a['targets']+1),
    lambda a:a.update(target_mask=~a['target_mask']),
    lambda a:a.update(training_weights=a['training_weights']+1),
    lambda a:a.update(donor_indices=np.arange(4)),
    lambda a:a.update(donor_case_ids=a['case_ids']),
    lambda a:a.update(active_columns=a['active_columns'][:-1]),
    lambda a:a.update(real_scores=a['real_scores'][:-1]),
    lambda a:a.update(real_scores=np.zeros_like(a['real_scores'])),
    lambda a:a.update(real_scores=np.full_like(a['real_scores'],np.nan)),
])
def test_saved_score_identity_shape_and_visibility_guards(tmp_path,change):
    entry,b,weights,donor=bank(tmp_path,change)
    with pytest.raises(ValueError):study.load_scores(entry,b,config_hash='identity',weights=weights,donor=donor)


def test_graph_validity_distinguishes_missing_multiple_and_wrong_single_parent():
    b=bundle();scores=np.where(b.mask,b.y,np.nan)
    good=study.graph_validity(b,scores,np.arange(4))
    assert good['valid_graph_fraction']==good['raw_binary_exact_graph_accuracy']==1
    cols=[s['index'] for s in b.columns if s['family']=='direct' and s['consumer_node']=='v0@2' and b.mask[0,s['index']]]
    # Missing parent; multiple parents; single lawful but incorrect parent.
    scores[0,cols]=0;scores[1,cols]=1
    scores[2,cols]=0
    wrong=next(j for j in cols if b.y[2,j]==0);scores[2,wrong]=1
    result=study.graph_validity(b,scores,np.arange(4))
    assert result['valid_graph_fraction']==.5
    assert result['raw_binary_exact_graph_accuracy']==.25
    assert result['zero_parent_rows']==result['multiple_parent_rows']==.25


def test_graph_diagnostic_rejects_future_checkpoint_and_undefined_scores():
    early=bundle(3)
    with pytest.raises(ValueError):study.graph_validity(early,np.where(early.mask,early.y,np.nan),np.arange(4))
    b=bundle();scores=np.where(b.mask,b.y,np.nan)
    j=next(s['index'] for s in b.columns if s['family']=='direct' and b.mask[0,s['index']])
    scores[0,j]=np.nan
    with pytest.raises(ValueError):study.graph_validity(b,scores,np.arange(4))


def config(tmp_path):
    return dict(evaluation_role=study.ROLE,pipeline_config=str(tmp_path/'pipeline.json'),pipeline_config_sha256='a'*64,
        pipeline_review=str(tmp_path/'original/pipeline_review_v1.json'),pipeline_review_sha256='b'*64,
        readout_completion=str(tmp_path/'original/completion_manifest_v1.json'),readout_completion_sha256='c'*64,
        declared_plan=str(tmp_path/'posthoc_plan.md'),declared_plan_sha256='d'*64,
        run_dir=str(tmp_path/'followup'),report=str(tmp_path/'followup.md'))


@pytest.mark.parametrize('change',['role','extra','pin','reserved','source','output_parent','report_directory','reserved_parent'])
def test_posthoc_configuration_guards_precede_original_inputs(tmp_path,change,monkeypatch):
    c=config(tmp_path)
    if change=='role':c['evaluation_role']='held_out'
    elif change=='extra':c['select_best_layer']=True
    elif change=='pin':c['pipeline_config_sha256']='unversioned'
    elif change=='reserved':c['report']=str(Path(c['run_dir'])/'registration.json')
    elif change=='source':c['report']=c['pipeline_config']
    elif change=='report_directory':c['run_dir']=str(tmp_path/'output.md');c['report']=c['run_dir']
    elif change=='reserved_parent':c['report']=str(Path(c['run_dir'])/'registration.json'/'nested.md')
    else:c['run_dir']=str(tmp_path)
    monkeypatch.setattr(study.capture,'_json',lambda *a,**k:pytest.fail('original metadata reached before config guard'))
    with pytest.raises(ValueError):study._inputs(c)


def test_real_score_execution_requires_scheduler_before_original_inputs(tmp_path,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    monkeypatch.setattr(study,'_inputs',lambda *a:pytest.fail('sources opened before sbatch guard'))
    with pytest.raises(ValueError,match='SLURM'):study.run(config(tmp_path))


def test_protocol_cannot_select_best_layer_or_change_primary():
    p=study.protocol()
    assert p['posthoc'] is True and p['layer']==24 and p['selected_score_banks']==18
    assert p['sites']==[3,7,8] and p['provenance_sites']==[7,8]
    assert p['seeds']==[11,29,47]


def completed(tmp_path,monkeypatch,change_result=None,change_registration=None):
    from codecue.binding.datasets import digest
    c=config(tmp_path);out=Path(c['run_dir']);out.mkdir()
    Path(c['readout_completion']).parent.mkdir();Path(c['readout_completion']).write_text('original pinned receipt')
    source={'snapshot':'synthetic-frozen'};original={'primary':{'fixed':True}}
    artifacts={study.readouts._name(backend,layer,site,seed):{'synthetic':True}
        for site in (3,7,8) for backend,layer in (('hidden',24),('surface',-1)) for seed in study.readouts.SEEDS}
    monkeypatch.setattr(study,'_inputs',lambda config:({'artifacts':artifacts},original,{'summary':{'model_prefill_cases':1944}},[],{}))
    monkeypatch.setattr(study.capture,'_verify_source',lambda *args:None)
    monkeypatch.setattr(study.np,'load',lambda *a,**k:pytest.fail('audit loaded arrays'))
    registration=dict(evaluation_role=study.ROLE,config=c,config_hash=digest(c),source=source,protocol=study.protocol(),posthoc=True,
        new_model_queries=0,new_fits=0,generated_holdouts_opened=False,
        original_readout_completion=study._pin(c['readout_completion']))
    result=dict(status='complete_exploratory',evaluation_role=study.ROLE,config_hash=digest(c),source=source,protocol=study.protocol(),
        posthoc=True,new_model_queries=0,new_fits=0,parameter_replays=0,raw_activations_loaded=False,
        generated_holdouts_opened=False,cases=1944,development_components=9,saved_score_rows_read=34992,
        selected_score_banks=artifacts,original_primary=original['primary'],source_model_prefill_cases=1944)
    if change_result:change_result(result)
    if change_registration:change_registration(registration)
    paths={'registration':out/'registration.json','pairs':out/'pairs_review_v1.json','results':out/'results_v1.json','report':Path(c['report'])}
    for name,path in paths.items():
        value=registration if name=='registration' else result if name=='results' else {}
        path.write_text(json.dumps(value))
    receipt=dict(status='complete_exploratory',evaluation_role=study.ROLE,config_hash=digest(c),source=source,
        protocol=study.protocol(),artifacts={name:study._pin(path) for name,path in paths.items()},
        new_model_queries=0,new_fits=0,generated_holdouts_opened=False)
    (out/'completion_manifest_v1.json').write_text(json.dumps(receipt))
    return c,result


def test_completed_audit_is_metadata_only(tmp_path,monkeypatch):
    c,result=completed(tmp_path,monkeypatch)
    assert study.audit(c)==result


@pytest.mark.parametrize('key,value',[
    ('status','started'),('evaluation_role','other'),('new_model_queries',1),('new_fits',1),
    ('parameter_replays',1),('raw_activations_loaded',True),('generated_holdouts_opened',True),
    ('cases',1),('development_components',1),('saved_score_rows_read',1),('selected_score_banks',{}),
    ('original_primary',{}),('source_model_prefill_cases',0)])
def test_audit_checks_scientific_status_and_costs_even_with_consistent_file_pins(tmp_path,monkeypatch,key,value):
    c,_=completed(tmp_path,monkeypatch,lambda result:result.update({key:value}))
    with pytest.raises(ValueError,match='scientific result'):study.audit(c)


@pytest.mark.parametrize('change',[{'posthoc':False},{'new_model_queries':1},{'new_fits':1},{'generated_holdouts_opened':True}])
def test_audit_checks_original_registration_identity(tmp_path,monkeypatch,change):
    c,_=completed(tmp_path,monkeypatch,change_registration=lambda r:r.update(change))
    with pytest.raises(ValueError,match='registration'):study.audit(c)
