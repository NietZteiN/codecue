"""Synthetic CPU coverage of the new diversity capture adapter and interfaces."""
from copy import deepcopy
import json
from pathlib import Path
import random
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import diversity_capture as capture
from codecue.binding import overnight_relationship_capture as legacy
from codecue.binding import schedule_capture as previous
from codecue.binding import schedule_diversity_programs as programs
from codecue.binding.datasets import digest
from codecue.binding.programs import rename


class Tokenizer:
    chat_template='synthetic-diversity-template'
    binding_official_boundary=False
    def apply_chat_template(self,messages,**kwargs):return '<s>'+messages[0]['content']+' assistant:'
    def __call__(self,prompt,**kwargs):
        return dict(input_ids=[ord(c) for c in prompt],offset_mapping=[(i,i+1) for i in range(len(prompt))])
    def decode(self,tokens,**kwargs):return ''.join(chr(c) for c in tokens)


def row(query=0,development=False,rotation=0):
    destinations=(0,0,1,2) if not development else (0,0,0,1)
    parents=(1,2,3,0) if not development else (1,2,3,2)
    graph=programs._graph(destinations,parents);profile=programs._profile(destinations)
    component='schedule-diversity-graph:'+graph[:24];seed=751
    values=random.Random(digest([programs.ROLE,graph,seed,'numeric'])).sample(tuple(x for x in range(-12,13) if x),4)
    permutation=tuple((slot+rotation)%4 for slot in range(4));actual_dest=tuple(permutation[x] for x in destinations)
    actual_parents=tuple(permutation[x] for x in parents);actual_values=[0]*4
    for slot,value in enumerate(values):actual_values[permutation[slot]]=value
    canonical=programs.prior._source(actual_values,actual_dest,actual_parents,query)
    mapping={name:f'item_{slot}' for slot,name in enumerate(programs.prior.VARIABLES)}
    source=rename(canonical,mapping);base=f'{component}:numeric{seed}'
    record=dict(id='schedule-diversity:'+digest([seed,source])[:24],source=source,canonical_source=canonical,
        evaluation_role=capture.DATASET_ROLE,condition='neutral',split='development' if development else 'train',
        source_form='literal',variable_slots=programs.prior.SLOTS.copy(),rename_map=mapping,
        component_id=component,cluster_id=component,template_id=component,ssa_graph_canonical_id=component,
        canonical_graph_sha256=graph,graph_selection_index=15 if development else 0,
        profile_id='_'.join(map(str,profile)),update_count_profile=list(profile),
        destination_update_counts=[actual_dest.count(slot) for slot in range(4)],slot_rotation=rotation,
        destination_schedule=list(actual_dest),copy_parent_slots=list(actual_parents),
        parent_pattern='independent_distinct_slot_choices',base_id=base,paired_group_id=base,
        raw_template_id=f'{component}:rotation{rotation}',numeric_seed=seed,lexical_realization=0,
        query_slot=query,query_role=f'v{query}',query_count=1,targets={'secret':True},expected_answer='EXCLUDED')
    family=(profile,record['graph_selection_index'],destinations,parents,record['split'])
    return record,family


@pytest.fixture
def config(tmp_path):
    model='meta-llama/Llama-3.1-8B-Instruct';profile=capture.PROFILES[model]
    return dict(evaluation_role=capture.ROLE,dataset=str(tmp_path/'sources.jsonl'),dataset_sha256=capture.DATASET_SHA256,
        dataset_manifest_sha256='a'*64,run_dir=str(tmp_path/'capture'),model=model,model_revision=profile['revision'],
        tokenizer_revision=profile['revision'],layers=profile['layers'].copy(),hidden_size=profile['hidden_size'],batch_size=2,chunk_size=2)


def prepared(config,monkeypatch):
    core=capture._CORE;rows=[row(0)[0],row(3)[0],row(0,True)[0],row(2,True)[0]]
    source=dict(snapshot='/synthetic/frozen',snapshot_id='synthetic',source_sha256='b'*64,frozen_manifest_sha256='c'*64)
    monkeypatch.setenv('SLURM_JOB_ID','synthetic')
    monkeypatch.setattr(core.base,'_current_source',lambda config:source)
    monkeypatch.setattr(core.base,'_verify_source',lambda *args:None)
    def dataset(config):
        recipe,_=capture._config(config)
        return rows,dict(dataset_sha256=config['dataset_sha256'],dataset_manifest_sha256=config['dataset_manifest_sha256'],source_rows=4,
            split_rows={'train':2,'development':2},components={'train':1,'development':1},ordered_case_ids_sha256=digest([r['id'] for r in rows]),
            layers=recipe['layers'],sites=list(capture.SITES),feature_shape=[4,3,4,4096],recipe=recipe)
    monkeypatch.setattr(core,'_dataset',dataset);monkeypatch.setattr(core,'_tokenizer',lambda config:Tokenizer())
    capture.prepare(config);return capture.inputs(config)


def running(config,monkeypatch):
    data=prepared(config,monkeypatch);core=capture._CORE;calls=[]
    monkeypatch.setattr(core,'_models',lambda config,**kwargs:(Tokenizer(),SimpleNamespace()))
    def forward(tokenizer,model,cases,config):
        calls.append([case['record']['id'] for case in cases]);return np.zeros((len(cases),3,4,4096),np.float32)
    monkeypatch.setattr(core,'_forward',forward)
    class Monitor:
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def summary(self):return {'gpu_uuid':'synthetic'}
    monkeypatch.setattr(core.base,'_monitor',Monitor);monkeypatch.setattr(core.base,'_runtime',lambda model:{'gpu_uuid':'synthetic'})
    monkeypatch.setattr(core,'_event',lambda *args:None)
    return data,calls


def test_private_engine_does_not_change_either_previous_capture():
    assert legacy.ROLE=='discovery_overnight_relationship_capture_v1'
    assert previous.ROLE=='discovery_schedule_capture_v1'
    assert capture._CORE is not previous._CORE and capture._CORE.base is not previous._CORE.base
    assert capture._CORE.PROFILES is not previous._CORE.PROFILES
    assert capture._CORE.PROFILES==legacy.PROFILES==previous.PROFILES


def test_doubled_default_batches_retain_original_hardware_reference(config):
    config.pop('batch_size');config['chunk_size']=512
    recipe,_=capture._config(config)
    assert recipe['batch_size']==256 and recipe['tokenization_mode']=='native'
    assert capture._CORE.PROFILES[config['model']]['batch_size']==128
    assert capture.PROFILES[config['model']]['minimum_gpu_bytes']==22*1024**3
    memory=capture.memory_requirements(config,512)
    assert memory['working_headroom_bytes']==6*1024**3
    assert capture.memory_requirements(config,128)['required_free_bytes']<24*1024**3
    model='codellama/CodeLlama-34b-Instruct-hf';profile=capture.PROFILES[model]
    config.update(model=model,model_revision=profile['revision'],tokenizer_revision=profile['revision'],hidden_size=8192,layers=profile['layers'].copy())
    recipe,_=capture._config(config)
    assert recipe['batch_size']==128 and recipe['tokenization_mode']=='codellama_official_boundary_v1'
    assert capture._CORE.PROFILES[model]['batch_size']==64 and profile['minimum_gpu_bytes']==72*1024**3
    assert capture.memory_requirements(config,512)['working_headroom_bytes']==16*1024**3
    assert capture.memory_requirements(config,128)['required_free_bytes']<80*1024**3


def test_all_source_identity_fields_survive_and_target_api_accepts_record(config,monkeypatch):
    from codecue.binding import diversity_targets
    rows=[];families={}
    for development,rotation in ((False,0),(True,3)):
        original,family=row(development=development,rotation=rotation)
        capture._validate_row(original);rows.append(original);families[original['canonical_graph_sha256']]=family
    monkeypatch.setattr(diversity_targets,'_family_map',lambda:families)
    records=[capture._CORE._record(original) for original in rows]
    required=('paired_group_id','canonical_graph_sha256','graph_selection_index','profile_id','update_count_profile',
        'destination_update_counts','slot_rotation','destination_schedule','copy_parent_slots','parent_pattern')
    assert all(all(record[key]==original[key] for key in required) for record,original in zip(records,rows))
    assert all('targets' not in record and 'expected_answer' not in record for record in records)
    for site in (3,7,8):
        bundle=diversity_targets.targets(records,site)
        assert bundle.y.shape==(2,232) and bundle.case_ids==tuple(r['id'] for r in rows)


def test_actual_diversity_schedule_keeps_only_three_exact_prefix_sites(config):
    original,_=row(rotation=2);case=capture.layout_case(Tokenizer(),original,config,0)
    capture._CORE._case_check(case,original,capture._config(config)[0],0)
    assert case['sites']==['statement:3','statement:7','pre_answer']
    assert case['visible_prefixes'][0].endswith(original['source'].splitlines()[3])
    assert case['visible_prefixes'][1].endswith(original['source'].splitlines()[7])
    assert case['visible_prefixes'][-1]==case['prompt']


@pytest.mark.parametrize('key,value',[
    ('evaluation_role','final'),('dataset_sha256',previous.DATASET_SHA256),('dataset_manifest_sha256','bad'),
    ('layers',[8]),('hidden_size',8192),('batch_size',True),('batch_size',0),('chunk_size',1),
    ('prefix_atol',float('nan')),('model_revision','a'*40),('extra',1)])
def test_configuration_rejected_before_any_tokenizer(config,key,value,monkeypatch):
    config[key]=value
    monkeypatch.setattr(capture._CORE,'_tokenizer',lambda *args:pytest.fail('invalid config reached tokenizer'))
    with pytest.raises(ValueError):capture.prepare(config)


@pytest.mark.parametrize('problem',['role','split','profile','counts','rotation','pairing','graph','query','parent'])
def test_diversity_source_guards(problem):
    original,_=row()
    if problem=='role':original['evaluation_role']=previous.DATASET_ROLE
    if problem=='split':original['split']='development'
    if problem=='profile':original['profile_id']='1_1_1_1'
    if problem=='counts':original['destination_update_counts']=[1,1,1,1]
    if problem=='rotation':original['slot_rotation']=4
    if problem=='pairing':original.pop('paired_group_id')
    if problem=='graph':original['canonical_graph_sha256']='a'*64
    if problem=='query':original['query_slot']=3
    if problem=='parent':original['copy_parent_slots'][0]=0
    with pytest.raises(ValueError):capture._validate_row(original)


def test_manifest_pin_and_path_collisions_precede_source_read(config,monkeypatch):
    changed=dict(config);changed.pop('dataset_manifest_sha256')
    with pytest.raises(ValueError,match='manifest'):capture._config(changed)
    changed=dict(config,run_dir=str(Path(config['dataset'])/'child'))
    with pytest.raises(ValueError,match='overlap'):capture._config(changed)
    manifest=Path(config['dataset']).with_suffix('.manifest.json');manifest.write_text('{}')
    monkeypatch.setattr(capture,'_durable_dataset',lambda config:pytest.fail('changed manifest reached source rows'))
    with pytest.raises(ValueError,match='checksum'):capture.metadata(config)


def test_load_entrypoints_require_slurm(config,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    with pytest.raises(ValueError,match='SLURM'):capture.prepare(config)
    with pytest.raises(ValueError,match='SLURM'):capture.run(config)


def test_synthetic_run_audit_receipt_geometry_and_model_free_reuse(config,monkeypatch):
    (_,cases),calls=running(config,monkeypatch)
    first=capture.run(config);assert first['new_model_queries']==4 and first['generated_responses']==0 and len(calls)==2
    capture.audit(config);checked=capture.completed_metadata(config)
    assert checked['config']==config and checked['feature_shape']==[4,3,4,4096] and checked['cases']==cases
    manifest=Path(config['run_dir'])/'manifest.json';before=manifest.read_bytes()
    monkeypatch.setattr(capture._CORE,'_models',lambda *args,**kwargs:pytest.fail('completed capture reloaded model'))
    assert capture.run(config)==first and manifest.read_bytes()==before
    entry=checked['chunks'][0];features,_=capture.load_chunk(entry,cases[:2],checked['config'])
    assert features.shape==(2,3,4,4096)
    with pytest.raises(ValueError,match='checksum'):capture.load_chunk(dict(entry,sha256='0'*64),cases[:2],config)
    with pytest.raises(ValueError):capture.load_chunk(entry,cases[:2],dict(config,hidden_size=8192))
