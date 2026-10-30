"""Synthetic CPU checks for the private durable schedule capture adapter."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import overnight_relationship_capture as legacy
from codecue.binding import relationship_schedule_programs as programs
from codecue.binding import relationships
from codecue.binding import schedule_capture as capture
from codecue.binding.datasets import digest


class Tokenizer:
    chat_template='synthetic-native-template'
    binding_official_boundary=False
    def apply_chat_template(self,messages,**kwargs):return '<s>'+messages[0]['content']+' assistant:'
    def __call__(self,prompt,**kwargs):
        return {'input_ids':[ord(c) for c in prompt], 'offset_mapping':[(i,i+1) for i in range(len(prompt))]}
    def decode(self,tokens,**kwargs):return ''.join(chr(c) for c in tokens)


def row(case='one',split='train',query=0,repeated=True):
    destinations=[0,0,1,0] if repeated else [0,1,2,3]
    parents=[(i+1)%4 for i in destinations]
    source='\n'.join(['v0 = 1','v1 = 2','v2 = 3','v3 = 4']
        +[f'v{d} = v{p}' for d,p in zip(destinations,parents)]+[f'v{query}'])
    graph,_=programs._canonical_graph(relationships.labels_at(source,7,programs.SLOTS))
    group='schedule-graph:'+digest(graph)[:24]
    return dict(id=case,base_id='base:'+group,numeric_seed=419,lexical_realization=0,
        template_id=group,component_id=group,cluster_id=group,ssa_graph_canonical_id=group,split=split,
        source=source,canonical_source=source,rename_map={name:name for name in programs.SLOTS},
        variable_slots=programs.SLOTS.copy(),query_role=f'v{query}',query_slot=query,query_count=1,
        condition='neutral',evaluation_role=capture.DATASET_ROLE,source_form='literal',
        family='varied_copy_overwrite_schedule',control_kind='targets_prepared_only',
        raw_template_id='synthetic:'+group,schedule_id='synthetic',schedule_kind='repeated' if repeated else 'permutation',
        destination_schedule=destinations,parent_pattern='ring_successor',copy_parent_slots=parents,
        ordered_schedule_canonical_id='ordered',statement_spans=[],targets={'secret_oracle':True},expected_answer='EXCLUDED')


@pytest.fixture
def config(tmp_path):
    model='meta-llama/Llama-3.1-8B-Instruct';profile=capture.PROFILES[model]
    return dict(evaluation_role=capture.ROLE,dataset=str(tmp_path/'sources.jsonl'),
        dataset_sha256=capture.DATASET_SHA256,dataset_manifest_sha256='a'*64,
        run_dir=str(tmp_path/'capture'),model=model,model_revision=profile['revision'],
        tokenizer_revision=profile['revision'],layers=profile['layers'].copy(),hidden_size=profile['hidden_size'],
        batch_size=2,chunk_size=2)


def prepared(config,monkeypatch):
    core=capture._CORE
    rows=[row('a'),row('b',query=3),row('c','development',repeated=False),row('d','development',query=2,repeated=False)]
    source=dict(snapshot='/synthetic/frozen',snapshot_id='synthetic',source_sha256='b'*64,frozen_manifest_sha256='c'*64)
    monkeypatch.setenv('SLURM_JOB_ID','synthetic')
    monkeypatch.setattr(core.base,'_current_source',lambda config:source)
    monkeypatch.setattr(core.base,'_verify_source',lambda *args:None)
    def dataset(config):
        recipe,_=capture._config(config)
        return rows,dict(dataset_sha256=config['dataset_sha256'],dataset_manifest_sha256=config['dataset_manifest_sha256'],
            source_rows=4,split_rows={'train':2,'development':2},components={'train':1,'development':1},
            ordered_case_ids_sha256=digest([r['id'] for r in rows]),layers=recipe['layers'],sites=list(capture.SITES),
            feature_shape=[4,3,4,4096],recipe=recipe)
    monkeypatch.setattr(core,'_dataset',dataset)
    monkeypatch.setattr(core,'_tokenizer',lambda config:Tokenizer())
    core.prepare(config)
    return core.inputs(config)


def running(config,monkeypatch):
    data=prepared(config,monkeypatch);core=capture._CORE;calls=[]
    monkeypatch.setattr(core,'_models',lambda config,**kwargs:(Tokenizer(),SimpleNamespace()))
    def forward(tokenizer,model,cases,config):
        calls.append([case['record']['id'] for case in cases])
        return np.zeros((len(cases),3,4,4096),np.float32)
    monkeypatch.setattr(core,'_forward',forward)
    class Monitor:
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def summary(self):return {'gpu_uuid':'synthetic'}
    monkeypatch.setattr(core.base,'_monitor',Monitor)
    monkeypatch.setattr(core.base,'_runtime',lambda model:{'gpu_uuid':'synthetic'})
    monkeypatch.setattr(core,'_event',lambda *args:None)
    return data,calls


def test_private_engine_never_mutates_legacy_roles_or_validation():
    assert legacy.ROLE=='discovery_overnight_relationship_capture_v1'
    assert legacy.DATASET_ROLE=='overnight_relationship_discovery_v1'
    assert legacy._validate_row is not capture._CORE._validate_row
    assert legacy._config is not capture._CORE._config
    assert capture._CORE.base is not legacy.base
    assert capture._CORE.PROFILES is not legacy.PROFILES
    assert capture._CORE.PROFILES==legacy.PROFILES


def test_repeated_overwrites_preserve_actual_versions_and_three_sites(config):
    original=row();capture._validate_row(original)
    case=capture.layout_case(Tokenizer(),original,config,0)
    capture._CORE._case_check(case,original,capture._config(config)[0],0)
    assert case['sites']==['statement:3','statement:7','pre_answer']
    assert case['visible_prefixes'][0].endswith('v3 = 4')
    assert case['visible_prefixes'][1].endswith('v0 = v1')
    assert case['visible_prefixes'][-1]==case['prompt']
    assert case['record']['destination_schedule']==[0,0,1,0]
    assert case['record']['ssa_graph_canonical_id']==original['component_id']
    assert not {'targets','expected_answer','canonical_execution_trace'} & case['record'].keys()
    with pytest.raises(ValueError,match='overnight discovery'):legacy._validate_row(original)


def test_capture_record_whitelist_is_compatible_with_actual_schedule_targets(tmp_path):
    from codecue.binding import schedule_targets
    generation=dict(evaluation_role=programs.ROLE,numeric_seeds=[419,521,631],
        dataset=str(tmp_path/'source.jsonl'),review=str(tmp_path/'review.json'),report=str(tmp_path/'report.md'))
    rows=programs.make_rows(generation)
    selected=[rows[0],next(row for row in rows if row['split']=='train')]
    records=[capture._CORE._record(row) for row in selected]
    assert all(record['paired_group_id']==record['base_id'] for record in records)
    for site in (3,7,8):
        bundle=schedule_targets.targets(records,site)
        assert bundle.y.shape==(2,232)
        assert bundle.case_ids==tuple(row['id'] for row in selected)
    assert all('targets' not in record and 'expected_answer' not in record for record in records)


@pytest.mark.parametrize('key,value',[
    ('evaluation_role','final'),('dataset_sha256','a'*64),('dataset_manifest_sha256','bad'),
    ('layers',[8]),('layers',[True,16,24,31]),('hidden_size',8192),('batch_size',True),
    ('chunk_size',1),('prefix_atol',float('nan')),('model_revision','b'*40),('extra',1)])
def test_configuration_guards_precede_any_tokenizer(config,key,value,monkeypatch):
    config[key]=value
    monkeypatch.setattr(capture._CORE,'_tokenizer',lambda *args:pytest.fail('invalid config reached tokenizer'))
    with pytest.raises(ValueError):capture.prepare(config)


def test_manifest_pin_is_mandatory_and_paths_cannot_overlap(config):
    missing=dict(config);missing.pop('dataset_manifest_sha256')
    with pytest.raises(ValueError,match='manifest'):capture._config(missing)
    config['run_dir']=str(Path(config['dataset'])/'child')
    with pytest.raises(ValueError,match='overlap'):capture._config(config)


@pytest.mark.parametrize('problem',['role','split','root_expression','parent','destination','query','family'])
def test_actual_schedule_row_guards(problem):
    original=row()
    if problem=='role':original['evaluation_role']='final'
    if problem=='split':original['split']='held_out'
    if problem=='root_expression':original['canonical_source']=original['source']=original['source'].replace('v0 = 1','v0 = 2 - 1')
    if problem=='parent':original['copy_parent_slots'][0]=3
    if problem=='destination':original['destination_schedule'][1]=2
    if problem=='query':original['query_slot']=3
    if problem=='family':original.update(component_id='other',template_id='other',cluster_id='other',ssa_graph_canonical_id='other')
    with pytest.raises(ValueError):capture._validate_row(original)


def test_native_profiles_layers_batches_memory_and_official_boundary(config):
    config.pop('batch_size');config['chunk_size']=512
    recipe,_=capture._config(config)
    assert recipe['batch_size']==128 and recipe['tokenization_mode']=='native'
    assert capture.PROFILES[config['model']]['minimum_gpu_bytes']==22*1024**3
    model='codellama/CodeLlama-34b-Instruct-hf';profile=capture.PROFILES[model]
    config.update(model=model,model_revision=profile['revision'],tokenizer_revision=profile['revision'],
        hidden_size=8192,layers=profile['layers'].copy())
    recipe,_=capture._config(config)
    assert recipe['batch_size']==64 and recipe['tokenization_mode']=='codellama_official_boundary_v1'
    assert profile['minimum_gpu_bytes']==72*1024**3
    memory=capture.memory_requirements(config,512)
    assert memory['required_free_bytes']<80*1024**3


def test_real_load_entrypoints_require_slurm_and_source(config,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    with pytest.raises(ValueError,match='SLURM'):capture.prepare(config)
    with pytest.raises(ValueError,match='SLURM'):capture.run(config)
    monkeypatch.setenv('SLURM_JOB_ID','synthetic')
    with pytest.raises(ValueError,match='immutable source'):capture.prepare(config)


def test_synthetic_capture_audit_completed_metadata_and_reuse(config,monkeypatch):
    (_,cases),calls=running(config,monkeypatch)
    first=capture.run(config)
    assert first['new_model_queries']==4 and first['generated_responses']==0
    assert calls==[['a','b'],['c','d']]
    assert capture.audit(config)['finite_float32_features'] is True
    checked=capture.completed_metadata(config)
    assert checked['config']==config and checked['feature_shape']==[4,3,4,4096]
    assert checked['sites']==list(capture.SITES) and checked['cases']==cases
    saved=Path(config['run_dir'])/'manifest.json';before=saved.read_bytes()
    monkeypatch.setattr(capture._CORE,'_models',lambda *args,**kwargs:pytest.fail('completed capture reloaded model'))
    assert capture.run(config)==first and saved.read_bytes()==before
    for entry in checked['chunks']:
        selected=cases[entry['first']:entry['first']+entry['rows']]
        features,_=capture.load_chunk(entry,selected,checked['config'])
        assert features.shape==(2,3,4,4096)
    assert legacy.ROLE=='discovery_overnight_relationship_capture_v1'


def test_chunk_pin_and_geometry_checked_before_array_use(config,monkeypatch):
    (_,cases),_=running(config,monkeypatch)
    capture.run(config);capture.audit(config)
    checked=capture.completed_metadata(config);entry=checked['chunks'][0]
    changed=dict(entry,sha256='0'*64)
    with pytest.raises(ValueError,match='checksum'):capture.load_chunk(changed,cases[:2],config)
    bad=dict(config,hidden_size=8192)
    with pytest.raises(ValueError):capture.load_chunk(entry,cases[:2],bad)


def test_source_manifest_pin_checked_before_reading_dataset(config,monkeypatch):
    manifest=Path(config['dataset']).with_suffix('.manifest.json')
    manifest.write_text(json.dumps({'status':'complete'}))
    monkeypatch.setattr(capture,'_durable_dataset',lambda config:pytest.fail('changed manifest reached source rows'))
    with pytest.raises(ValueError,match='checksum'):capture.metadata(config)
