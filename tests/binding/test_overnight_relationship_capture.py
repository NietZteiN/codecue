"""Finite CPU fixtures for generic capture visibility, journal and recovery."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from codecue.binding import overnight_relationship_capture as capture


class Tokenizer:
    chat_template='unit-native-template'
    binding_official_boundary=False
    def apply_chat_template(self,messages,**kwargs):return '<s>'+messages[0]['content']+' assistant:'
    def __call__(self,prompt,**kwargs):
        return {'input_ids':[ord(c) for c in prompt],'offset_mapping':[(i,i+1) for i in range(len(prompt))]}
    def decode(self,tokens,**kwargs):return ''.join(chr(c) for c in tokens)


def row(case='one',split='train',query=0,computed=False,parent=1):
    roots=['v0 = 1','v1 = 2','v2 = 2','v3 = 3']
    if computed:roots=['v0 = 4 - 3','v1 = 3 - 1','v2 = 1 + 1','v3 = 5 - 2']
    source='\n'.join([*roots,f'v0 = v{parent}','v1 = v0','v2 = v1','v3 = v2',f'v{query}'])
    return dict(id=case,template_id='train-component' if split=='train' else 'dev-component',split=split,
        source=source,canonical_source=source,rename_map={f'v{i}':f'v{i}' for i in range(4)},
        variable_slots={f'v{i}':i for i in range(4)},query_role=f'v{query}',query_slot=query,
        condition='neutral',evaluation_role=capture.DATASET_ROLE,root_values=[1,2,2,3],expected_answer='DO NOT COPY')


@pytest.fixture(autouse=True)
def no_live_logging(monkeypatch):
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log,'note_artifact',lambda *args,**kwargs:None)


@pytest.fixture
def config(tmp_path):
    return dict(evaluation_role=capture.ROLE,dataset=str(tmp_path/'bank.jsonl'),dataset_sha256='a'*64,
        run_dir=str(tmp_path/'run'),model='meta-llama/Llama-3.1-8B-Instruct',
        model_revision=capture.PROFILES['meta-llama/Llama-3.1-8B-Instruct']['revision'],
        tokenizer_revision=capture.PROFILES['meta-llama/Llama-3.1-8B-Instruct']['revision'],
        layers=[8],hidden_size=4096,batch_size=2,chunk_size=2)


def write_dataset(config,rows):
    path=Path(config['dataset']);payload=''.join(json.dumps(r)+'\n' for r in rows).encode();path.write_bytes(payload)
    config['dataset_sha256']=hashlib.sha256(payload).hexdigest()
    path.with_suffix('.manifest.json').write_text(json.dumps(dict(status='complete',evaluation_role=capture.DATASET_ROLE,
        role=capture.DATASET_ROLE,independent_python_passed=True,
        sha256=config['dataset_sha256'],rows=len(rows),generated_holdouts_opened=False)))


def prepared(config,monkeypatch,rows=None):
    rows=rows or [row('a'),row('b',query=3),row('c','development'),row('d','development',query=2)]
    write_dataset(config,rows)
    source=dict(snapshot='/unit/frozen',snapshot_id='unit',source_sha256='b'*64,frozen_manifest_sha256='c'*64)
    monkeypatch.setenv('SLURM_JOB_ID','unit')
    monkeypatch.setattr(capture.base,'_current_source',lambda config:source)
    monkeypatch.setattr(capture.base,'_verify_source',lambda *args:None)
    monkeypatch.setattr(capture,'_tokenizer',lambda config:Tokenizer())
    capture.prepare(config)
    return capture.inputs(config)


def run_fixture(config,monkeypatch):
    data=prepared(config,monkeypatch);calls=[]
    monkeypatch.setattr(capture,'_models',lambda config,**kwargs:(Tokenizer(),SimpleNamespace()))
    def forward(tokenizer,model,cases,config):
        calls.append([case['record']['id'] for case in cases])
        return np.zeros((len(cases),3,1,4096),np.float32)
    monkeypatch.setattr(capture,'_forward',forward)
    class Monitor:
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def summary(self):return {'gpu_uuid':'unit'}
    monkeypatch.setattr(capture.base,'_monitor',Monitor)
    monkeypatch.setattr(capture.base,'_runtime',lambda model:{'gpu_uuid':'unit'})
    return data,calls


def test_all_queries_and_computed_roots_keep_only_three_causal_sites(config):
    for query in range(4):
        original=row(query=query,computed=True)
        capture._validate_row(original)
        case=capture.layout_case(Tokenizer(),original,config,0)
        capture._case_check(case,original,capture._config(config)[0],0)
        assert case['sites']==['statement:3','statement:7','pre_answer']
        assert case['visible_prefixes'][0].endswith('v3 = 5 - 2')
        assert 'v0 = v1' not in case['visible_prefixes'][0]
        assert case['visible_prefixes'][1].endswith('v3 = v2')
        assert case['visible_prefixes'][-1]==case['prompt']
        assert not {'root_values','expected_answer'} & set(case['record'])


@pytest.mark.parametrize('key,value',[
    ('evaluation_role','final'),('dataset_sha256','unversioned'),('layers',[True]),('layers',[8,8]),
    ('layers',[32]),('hidden_size',8192),('hidden_size',4096.0),('batch_size',True),('batch_size',0),('chunk_size',1),
    ('context_limit',8192),('prefix_atol',float('nan')),('model_revision','a'*40),('extra',1)])
def test_config_guards_precede_loads(config,key,value,monkeypatch):
    config[key]=value
    monkeypatch.setattr(capture,'_tokenizer',lambda *args:pytest.fail('tokenizer reached'))
    with pytest.raises(ValueError):capture.prepare(config)


@pytest.mark.parametrize('problem',['role','split','cross_split','query','name_root','arithmetic_copy','future_code'])
def test_source_guards_precede_tokenizer(config,monkeypatch,problem):
    rows=[row('a'),row('b','development')]
    if problem=='role':rows[0]['evaluation_role']='held_out'
    if problem=='split':rows[0]['split']='final'
    if problem=='cross_split':rows[1]['template_id']=rows[0]['template_id']
    if problem=='query':rows[0]['query_slot']=3
    if problem=='name_root':rows[0]['source']=rows[0]['canonical_source']=rows[0]['source'].replace('v0 = 1','v0 = v1')
    if problem=='arithmetic_copy':rows[0]['source']=rows[0]['canonical_source']=rows[0]['source'].replace('v0 = v1','v0 = v1 + 1')
    if problem=='future_code':rows[0]['source']=rows[0]['canonical_source']=rows[0]['source'].replace('v0 = v1','v0 = v1; v1 = 3')
    write_dataset(config,rows);monkeypatch.setenv('SLURM_JOB_ID','unit')
    monkeypatch.setattr(capture.base,'_current_source',lambda config:{})
    monkeypatch.setattr(capture,'_tokenizer',lambda *args:pytest.fail('invalid dataset reached tokenizer'))
    with pytest.raises(ValueError):capture.prepare(config)


def test_real_tokenizer_and_model_commands_require_slurm_and_frozen_source(config,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    with pytest.raises(ValueError,match='SLURM'):capture.prepare(config)
    with pytest.raises(ValueError,match='SLURM'):capture.run(config)
    monkeypatch.setenv('SLURM_JOB_ID','unit')
    with pytest.raises(ValueError,match='immutable source'):capture.prepare(config)


def test_model_profiles_use_cached_geometry_and_prospective_batches(config):
    assert capture.PROFILES[config['model']]['batch_size']==128
    config.update(model='codellama/CodeLlama-34b-Instruct-hf',hidden_size=8192,layers=[12,24,36,47])
    profile=capture.PROFILES[config['model']]
    config.update(model_revision=profile['revision'],tokenizer_revision=profile['revision'])
    config.pop('batch_size');config['chunk_size']=512;recipe,_=capture._config(config)
    assert recipe['batch_size']==64 and recipe['tokenization_mode']=='codellama_official_boundary_v1'


def test_memory_allowance_uses_actual_tokens_and_leaves_short_prefill_devices_eligible(config):
    config.update(batch_size=128,chunk_size=512)
    short=capture.memory_requirements(config,256)
    assert short['required_free_bytes']<24*1024**3
    long=capture.memory_requirements(config,1024)
    assert long['working_headroom_bytes']>short['working_headroom_bytes']
    config.update(model='codellama/CodeLlama-34b-Instruct-hf',hidden_size=8192,layers=[12,24,36,47],batch_size=64)
    revision=capture.PROFILES[config['model']]['revision'];config.update(model_revision=revision,tokenizer_revision=revision)
    memory=capture.memory_requirements(config,512)
    assert memory['working_headroom_bytes']==8*1024**3 and memory['required_free_bytes']<80*1024**3


def test_positive_batch_is_limited_by_own_chunk_rather_than_model_specific_ceiling(config):
    config.update(batch_size=512,chunk_size=512)
    assert capture._config(config)[0]['batch_size']==512
    config['batch_size']=513
    with pytest.raises(ValueError,match='batch_size'):capture._config(config)


def test_insufficient_actual_free_memory_fails_before_tokenizer_or_weights(config,monkeypatch):
    import torch
    import transformers
    monkeypatch.setenv('SLURM_JOB_ID','unit')
    monkeypatch.setattr(torch.cuda,'is_available',lambda:True)
    monkeypatch.setattr(torch.cuda,'get_device_properties',lambda index:SimpleNamespace(total_memory=80*1024**3))
    monkeypatch.setattr(torch.cuda,'mem_get_info',lambda:(1024,80*1024**3))
    monkeypatch.setattr(capture,'_tokenizer',lambda *args:pytest.fail('insufficient memory reached tokenizer'))
    monkeypatch.setattr(transformers.AutoModelForCausalLM,'from_pretrained',lambda *a,**k:pytest.fail('insufficient memory reached weights'))
    with pytest.raises(ValueError,match='actual 256-token maximum'):
        capture.load_models(config,max_prompt_tokens=256)


def test_companion_loader_requires_slurm_even_with_supplied_layout(config,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    with pytest.raises(ValueError,match='SLURM'):capture.load_models(config,max_prompt_tokens=256)


def test_source_pairing_ids_survive_but_oracle_roots_and_edges_do_not(config):
    original=row();original.update(format_pair_id='format-pair',initial_state_id='state',parent_slots=[1,0,1,2],
        cohorts=['numeric_replication','query_twins'],numeric_seed=101,source_form='literal')
    saved=capture.layout_case(Tokenizer(),original,config,0)['record']
    assert saved['format_pair_id']=='format-pair' and saved['initial_state_id']=='state'
    assert saved['cohorts']==original['cohorts']
    assert not {'root_values','parent_slots','expected_answer'} & set(saved)


def test_journal_is_atomic_durable_and_does_not_reconcile_dashboard(tmp_path,monkeypatch):
    path=tmp_path/'manifest.json';events=[]
    monkeypatch.setattr(capture,'_event',lambda p:events.append(p))
    capture._journal(path,{'counter':1})
    original=path.read_bytes()
    monkeypatch.setattr(capture.os,'fsync',lambda fd:(_ for _ in ()).throw(OSError('injected fsync failure')))
    with pytest.raises(OSError):capture._journal(path,{'counter':2})
    assert path.read_bytes()==original and not list(tmp_path.glob('*.pending')) and events==[]


def test_prepare_inputs_hashes_and_geometry_are_model_specific(config,monkeypatch):
    preflight,cases=prepared(config,monkeypatch)
    assert preflight['cases']==4 and preflight['source_review']['feature_shape']==[4,3,1,4096]
    cases[0]['physical_positions'][0]+=1
    payload=''.join(json.dumps(case)+'\n' for case in cases).encode()
    Path(config['run_dir'],'prepared_cases.jsonl').write_bytes(payload)
    with pytest.raises(ValueError,match='checksum'):capture.inputs(config)


def test_independent_source_validation_is_required_before_tokenizer(config,monkeypatch):
    write_dataset(config,[row('a'),row('b','development')])
    path=Path(config['dataset']).with_suffix('.manifest.json');manifest=json.loads(path.read_text())
    manifest['independent_python_passed']=False;path.write_text(json.dumps(manifest))
    monkeypatch.setenv('SLURM_JOB_ID','unit');monkeypatch.setattr(capture.base,'_current_source',lambda config:{})
    monkeypatch.setattr(capture,'_tokenizer',lambda *args:pytest.fail('unvalidated source reached tokenizer'))
    with pytest.raises(ValueError,match='manifest'):capture.prepare(config)


def test_manifest_membership_metadata_is_pinned_with_the_prepared_source(config,monkeypatch):
    prepared(config,monkeypatch)
    path=Path(config['dataset']).with_suffix('.manifest.json');manifest=json.loads(path.read_text())
    manifest['views']={'changed':True};path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='preflight'):capture.inputs(config)


def test_prefix_geometry_tolerance_and_bounds(config):
    cases=[capture.layout_case(Tokenizer(),row('a'),config,0),capture.layout_case(Tokenizer(),row('b',query=1),config,1)]
    capture.base._batch_geometry(cases,assign=True)
    x=np.zeros((2,3,1,4096),np.float32)
    assert capture.validate_chunk(x,cases,config)[0]==2
    x[1,0,0,0]=2e-5
    with pytest.raises(ValueError,match='causal prefixes'):capture.validate_chunk(x,cases,config)
    with pytest.raises(ValueError,match='dtype'):capture.validate_chunk(x.astype(np.float64),cases,config)


def test_chunk_sha_precedes_array_reader(config,monkeypatch,tmp_path):
    case=capture.layout_case(Tokenizer(),row(),config,0);path=tmp_path/'bad.npz';path.write_bytes(b'bad')
    monkeypatch.setattr(capture.np,'load',lambda *a,**k:pytest.fail('array access before checksum'))
    with pytest.raises(ValueError,match='checksum'):capture.load_chunk(dict(path=str(path),sha256='f'*64),[case],config)


def test_forward_selects_on_device_then_one_cpu_transfer_and_explicit_positions(config,monkeypatch):
    import torch
    import codecue.patching
    cases=[capture.layout_case(Tokenizer(),row('a'),config,0),capture.layout_case(Tokenizer(),row('b',computed=True),config,1)]
    capture.base._batch_geometry(cases,assign=True)
    class Batch(dict):
        def __getattr__(self,k):return self[k]
        def to(self,device):return self
    class Padded:
        def __call__(self,prompts,**kwargs):
            width=max(map(len,prompts));ids=[];masks=[]
            for prompt in prompts:
                pad=width-len(prompt);ids.append([0]*pad+[ord(c) for c in prompt]);masks.append([0]*pad+[1]*len(prompt))
            return Batch(input_ids=torch.tensor(ids),attention_mask=torch.tensor(masks))
    hooks={}
    class Block:
        def register_forward_hook(self,hook):
            hooks[8]=hook
            return SimpleNamespace(remove=lambda:hooks.pop(8))
    class Model:
        device='cpu';finished=False
        def model(self,**kwargs):
            mask=kwargs['attention_mask'];expected=(mask.cumsum(-1)-1).clamp_min(0)
            assert torch.equal(kwargs['position_ids'],expected)
            assert kwargs['use_cache'] is False and kwargs['output_hidden_states'] is False
            hidden=torch.arange(mask.shape[1],dtype=torch.float32)[None,:,None].expand(len(cases),-1,4096)
            hooks[8](None,None,hidden);assert not self.finished;self.finished=True
    model=Model();monkeypatch.setattr(codecue.patching,'decoder_layers',lambda model:[Block() for _ in range(32)])
    original_cpu=torch.Tensor.cpu;copies=[]
    def cpu(tensor,*args,**kwargs):
        assert model.finished;copies.append(tuple(tensor.shape));return original_cpu(tensor,*args,**kwargs)
    monkeypatch.setattr(torch.Tensor,'cpu',cpu)
    x=capture._forward(Padded(),model,cases,config)
    assert x.shape==(2,3,1,4096) and copies==[(2,3,1,4096)] and hooks=={}


def test_full_capture_audit_and_metadata_reader_never_requery_completed_data(config,monkeypatch):
    _,calls=run_fixture(config,monkeypatch);result=capture.run(config)
    assert result['model_prefill_cases']==result['model_prefill_cases_attempted']==4
    assert result['prefill_batch_calls']==2 and len(calls)==2
    audit=capture.audit(config);assert audit['source_model_prefill_cases']==4
    monkeypatch.setattr(capture.np,'load',lambda *a,**k:pytest.fail('metadata reader opened arrays'))
    checked=capture.completed_metadata(config)
    assert checked['feature_shape']==[4,3,1,4096] and len(checked['chunks'])==2
    assert checked['summary']['generated_responses']==0
    assert capture.run(config)==result and len(calls)==2


def test_interrupted_committed_chunk_resumes_with_original_pins_and_attempt_counts(config,monkeypatch):
    _,calls=run_fixture(config,monkeypatch);original=capture.base._commit_chunk
    def interrupt(path,payload):original(path,payload);raise KeyboardInterrupt('injected kill after commit')
    monkeypatch.setattr(capture.base,'_commit_chunk',interrupt)
    with pytest.raises(KeyboardInterrupt):capture.run(config)
    monkeypatch.setattr(capture.base,'_commit_chunk',original)
    result=capture.run(config)
    assert calls==[['a','b'],['c','d']]
    assert result['model_prefill_cases_attempted']==4 and result['collection_attempts'][0]['status']=='interrupted'
    assert capture.audit(config)['status']=='passed'


def test_corrupt_partial_chunk_rejected_before_another_model_load(config,monkeypatch):
    _,calls=run_fixture(config,monkeypatch);original=capture.base._commit_chunk
    def interrupt(path,payload):original(path,payload);raise KeyboardInterrupt('injected')
    monkeypatch.setattr(capture.base,'_commit_chunk',interrupt)
    with pytest.raises(KeyboardInterrupt):capture.run(config)
    path=Path(config['run_dir'])/'chunks/000000.npz';payload=bytearray(path.read_bytes());payload[-10]^=1;path.write_bytes(payload)
    monkeypatch.setattr(capture.base,'_commit_chunk',original)
    monkeypatch.setattr(capture,'_models',lambda *args:pytest.fail('corrupt chunk reached model loader'))
    with pytest.raises(ValueError,match='checksum'):capture.run(config)
    assert len(calls)==1


def test_summary_completion_recovers_without_more_prefills(config,monkeypatch):
    _,calls=run_fixture(config,monkeypatch);original=capture._journal
    def fail_complete(path,value):
        if Path(path).name=='manifest.json' and value.get('status')=='complete':raise OSError('injected final manifest failure')
        original(path,value)
    monkeypatch.setattr(capture,'_journal',fail_complete)
    with pytest.raises(OSError,match='injected'):capture.run(config)
    before=Path(config['run_dir'],'summary.json').read_bytes()
    monkeypatch.setattr(capture,'_journal',original)
    monkeypatch.setattr(capture,'_models',lambda *args:pytest.fail('summary recovery loaded model'))
    result=capture.run(config)
    assert result['model_prefill_cases']==4 and len(calls)==2
    assert Path(config['run_dir'],'summary.json').read_bytes()==before
    assert capture.audit(config)['status']=='passed'


def test_wrong_summary_case_count_rejected_even_with_updated_manifest_hash(config,monkeypatch):
    run_fixture(config,monkeypatch);capture.run(config)
    folder=Path(config['run_dir']);path=folder/'summary.json';summary=json.loads(path.read_text())
    summary['cases']=1;path.write_text(json.dumps(summary))
    manifest=json.loads((folder/'manifest.json').read_text());manifest['summary_sha256']=capture._sha(path)
    (folder/'manifest.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(capture.np,'load',lambda *a,**k:pytest.fail('wrong coverage reached arrays'))
    with pytest.raises(ValueError,match='coverage'):capture.audit(config)
