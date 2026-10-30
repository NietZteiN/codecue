"""Runner provenance and exact trie scoring with software-only injected models."""
from copy import deepcopy
import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from codecue.binding import candidate_confidence as event
from codecue.binding import candidate_measurement as measurement
from codecue.binding import confidence
from codecue.binding.datasets import digest,read_jsonl
from codecue.binding.published_benchmarks import sha
from test_candidate_cache import Model as CausalModel,Tokenizer as CharacterTokenizer
from test_confidence import fake_registry


@pytest.fixture(autouse=True)
def restore_process_precision_settings():
    precision=torch.get_float32_matmul_precision()
    cuda=bool(torch.backends.cuda.matmul.allow_tf32);cudnn=bool(torch.backends.cudnn.allow_tf32)
    yield
    torch.set_float32_matmul_precision(precision)
    torch.backends.cuda.matmul.allow_tf32=cuda
    torch.backends.cudnn.allow_tf32=cudnn


class Tokenizer(CharacterTokenizer):
    pad_token_id=23
    all_special_ids=[14,15,16,23]
    def __len__(self):return 24
    def convert_ids_to_tokens(self,values):return [f'special-{value}' for value in values]


def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True))


@pytest.fixture
def setup(tmp_path,monkeypatch):
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log,'note_artifact',lambda *args,**kwargs:None)
    monkeypatch.setattr(measurement,'SOURCE_CASES',3)
    monkeypatch.setattr(measurement,'code_identity',lambda:{'source_sha256':'software-v1'})
    tokenizer=Tokenizer()
    identity=dict(model='fake/checkpoint',model_revision='a'*40,tokenizer_revision='b'*40,
        dtype='bfloat16',protocol='short_answer_chat_v1',tokenization_mode='native',
        eos_token_ids=[14,15,16],dataset=str(tmp_path/'discovery-bank.jsonl'),device='cpu')
    original_path=tmp_path/'original.json';dump(original_path,identity)
    from codecue.binding.competition import ROLE as source_role
    dataset_manifest=dict(status='validated',evaluation_role=source_role,sha256='source-dataset-sha',rows=3)
    dump(Path(identity['dataset']).with_suffix('.manifest.json'),dataset_manifest)
    source=dict(identity,source_config=str(original_path),source_config_sha256=sha(original_path),
        prepared_cases=str(tmp_path/'source/prepared.jsonl'),preflight_result=str(tmp_path/'source/preparation.json'),
        run_dir=str(tmp_path/'source/run'),attention_backend='sdpa',batch_size=32)
    source_path=tmp_path/'confidence-config.json';dump(source_path,source)
    cases=[]
    for index,prompt in enumerate(('Q:','AQ:','AAQ:')):
        ids=tokenizer(prompt,add_special_tokens=False)['input_ids']
        cases.append(dict(id=f'case-{index}',base_id=f'base-{index}',template_id='template',
            split='train' if index%2 else 'development',condition='informative' if index%2 else 'misleading',
            lexical_realization='descriptive',available_bindings=2,updates=1,tail_placement='after',query_role='current',
            prompt=prompt,prompt_sha256=digest(prompt),input_token_ids=ids,input_token_ids_sha256=digest(ids),
            evaluation_role=confidence.ROLE))
    Path(source['prepared_cases']).parent.mkdir(parents=True,exist_ok=True)
    Path(source['prepared_cases']).write_text(''.join(json.dumps(case)+'\n' for case in cases))
    qa=dict(status='passed',evaluation_role=confidence.ROLE,measurement=confidence.MEASUREMENT,
        config_hash=digest(source),source_config_sha256=source['source_config_sha256'],source_sha256='upstream-code',
        model=identity['model'],model_revision=identity['model_revision'],tokenizer_revision=identity['tokenizer_revision'],
        eos_token_ids=identity['eos_token_ids'],prepared_cases_sha256=sha(source['prepared_cases']),
        cases=3,case_ids_sha256=digest([case['id'] for case in cases]),smoke_subset=False,padded_width=4,
        source_provenance={'source_dataset_sha256':dataset_manifest['sha256']},generated_tokens=0,
        target_outcomes_read=False,generated_holdouts_opened=False,oracle_fields_exported=False)
    dump(source['preflight_result'],qa)
    stage=Path(source['run_dir'])/'confidence'
    source_identity=dict(config=source,code={'source_sha256':'upstream-code'},
        model_revision=identity['model_revision'],tokenizer_revision=identity['tokenizer_revision'],dataset_manifest=dataset_manifest)
    manifest=dict(status='complete',identity=source_identity,identity_hash=digest(source_identity),
        confidence_sha256='scalar-payload-is-deliberately-not-created')
    summary=dict(status='complete',complete=True,evaluated=3,planned=3,model=identity['model'],
        model_revision=identity['model_revision'],prepared_cases_sha256=qa['prepared_cases_sha256'],
        case_ids_sha256=qa['case_ids_sha256'],confidence_sha256=manifest['confidence_sha256'],
        evaluation_role=confidence.ROLE,measurement=confidence.MEASUREMENT,target_outcomes_read=False)
    audit=dict(status='passed',complete=True,evaluated=3,model=identity['model'],model_revision=identity['model_revision'],
        identity_hash=manifest['identity_hash'],preparation=qa,confidence_sha256=manifest['confidence_sha256'],
        measurement=confidence.MEASUREMENT,target_outcomes_read=False)
    dump(stage/'manifest.json',manifest);dump(stage/'summary.json',summary);dump(stage/'audit.json',audit)
    declaration=dict(evaluation_role=event.ROLE,bounds=[-16,16],terminator='eos',eos_token_ids=identity['eos_token_ids'],
        output_review=str(tmp_path/'declaration-review.json'))
    declaration_path=tmp_path/'candidate-declaration.json';dump(declaration_path,declaration)
    event.preflight(declaration)
    config=dict(identity,evaluation_role=measurement.ROLE,source_confidence_config=str(source_path),
        source_confidence_config_sha256=sha(source_path),candidate_declaration=str(declaration_path),
        candidate_declaration_sha256=sha(declaration_path),prepared_events=str(tmp_path/'candidate/events.jsonl'),
        preparation_review=str(tmp_path/'candidate/preparation.json'),run_dir=str(tmp_path/'candidate/run'),
        scoring_backend='full_prefix_trie',batch_size=1,event_batch_size=16,prompt_batch_size=2,
        max_active_nodes=4096,attention_backend='sdpa',measurement_dtype='float32')
    monkeypatch.setattr(measurement,'_load_tokenizer',lambda config:tokenizer)
    return SimpleNamespace(config=config,source=source,cases=cases,tokenizer=tokenizer,source_stage=stage,
        manifest=manifest,source_qa=qa,source_summary=summary,source_audit=audit,declaration=declaration)


@pytest.fixture
def prepared(setup):
    measurement.prepare(setup.config)
    return setup


def load_fake(monkeypatch,tokenizer,model=None):
    from codecue.binding import model_adapter
    model=model or CausalModel()
    # Match the real adapter's runtime attention switch without loading anything.
    model.set_attn_implementation=lambda backend:setattr(model,'attention_backend',backend)
    calls=[]
    def load(config):
        calls.append(config)
        if not hasattr(model,'dtype'):model.dtype=getattr(torch,config['dtype'])
        return tokenizer,model
    monkeypatch.setattr(model_adapter,'load',load)
    return model,calls


def test_full_prefix_trie_matches_naive_all_candidates_all_eos_and_padding(prepared):
    _,cases=measurement.inputs(prepared.config);banks=[case['event_bank'] for case in cases]
    model=CausalModel();actual=measurement.score_banks(model,banks,event_batch_size=16,pad_token_id=23)
    assert len(actual)==3
    # 35 prefix contexts per prompt, compared with 99 repeated event prefills.
    assert sum(item['trie_node_evaluations'] for item in actual)==105
    assert len(model.calls)==math.ceil(105/16)
    assert all(not call['use_cache'] and call['logits_to_keep']==1 for call in model.calls)
    for result,bank in zip(actual,banks):
        expected=event.score_events(CausalModel(),bank,batch_size=19,pad_token_id=23)
        for field in measurement.SCALARS[:4]:assert result[field]==pytest.approx(expected[field],abs=2e-6,rel=2e-6)
        for left,right in zip(result['event_variants'],expected['event_variants']):
            assert left['log_probability']==pytest.approx(right['log_probability'],abs=2e-6)
    singleton=measurement.score_banks(CausalModel(),banks,event_batch_size=1,pad_token_id=23)
    assert [item['support_mass'] for item in singleton]==pytest.approx([item['support_mass'] for item in actual])


def test_real_cached_backend_parity_integration_and_execution_counters(prepared):
    _,cases=measurement.inputs(prepared.config)
    config=dict(prepared.config,scoring_backend='cached_trie',parity_check=True,parity_atol=2e-6,parity_rtol=2e-6)
    model=CausalModel();rows,execution=measurement.measure_cases(model,cases,config,23)
    assert len(rows)==3 and execution['parity']['status']=='passed'
    assert execution['forward_calls']==8  # two prompt batches, four forwards each
    assert execution['parity_reference_forward_calls']==7
    assert execution['prefix_nodes']==105 and execution['naive_event_variants']==297
    assert all(value<2e-6 for value in execution['parity']['max_absolute_error'].values())
    assert execution['parity']['event_variants']==297
    assert execution['parity']['max_event_log_probability_absolute_error']<2e-6
    assert all(set(row)==measurement.ROW_FIELDS for row in rows)
    assert all(not {'candidate','candidates','prediction','expected_answer','event_variants'}&set(row) for row in rows)
    assert any(call['use_cache'] for call in model.calls) and any(not call['use_cache'] for call in model.calls)


def test_zero_partial_event_probabilities_match_cached_and_finite_scalars(prepared):
    _,cases=measurement.inputs(prepared.config);banks=[case['event_bank'] for case in cases]
    full=measurement.score_banks(CausalModel(zero_tokens=(0,14)),banks,event_batch_size=16,pad_token_id=23)
    from codecue.binding.candidate_cache import score_banks as cached
    fast=cached(CausalModel(zero_tokens=(0,14)),banks,prompt_batch_size=2,pad_token_id=23)
    for left,right in zip(full,fast):
        for field in measurement.SCALARS[:4]:assert left[field]==pytest.approx(right[field],abs=2e-6)
        assert next(item for item in left['candidates'] if item['candidate']==0)['absolute_event_mass']==0
    rows=measurement.scalar_rows(cases,full)
    assert all(math.isfinite(row[field]) for row in rows for field in measurement.SCALARS)
    with pytest.raises(ValueError,match='zero probability support'):
        measurement.score_banks(CausalModel(zero_tokens=(14,15,16)),banks,event_batch_size=16)


def test_preparation_is_exact_label_free_immutable_and_never_reads_scalar_payload(prepared):
    config=prepared.config;qa,cases=measurement.inputs(config)
    assert qa['cases']==3 and qa['prefix_node_evaluations']==105
    assert qa['boundary_verified'] is True and qa['model_loaded'] is False
    assert qa['upstream_scalar_payloads_read'] is False and qa['target_outcomes_read'] is False
    assert not (prepared.source_stage/'confidence.jsonl').exists()
    assert all(set(case)==measurement.PREPARED_FIELDS for case in cases)
    before=Path(config['preparation_review']).read_bytes()
    measurement.prepare(config)
    assert Path(config['preparation_review']).read_bytes()==before
    assert [case['event_bank']['input_token_ids'] for case in cases]==[case['input_token_ids'] for case in prepared.cases]
    Path(config['prepared_events']).write_text('{}\n')
    with pytest.raises(ValueError,match='immutable confidence artifact differs'):measurement.prepare(config)


def test_boundary_failure_records_failed_qa_and_no_rewrite_or_partial_bank(setup,monkeypatch):
    class Merging(Tokenizer):
        def __call__(self,text,*,add_special_tokens):
            result=super().__call__(text,add_special_tokens=add_special_tokens)
            if text.endswith('1'):result['input_ids'][1]=9
            return result
    monkeypatch.setattr(measurement,'_load_tokenizer',lambda config:Merging())
    with pytest.raises(ValueError,match='retokenizes'):measurement.prepare(setup.config)
    review=json.loads(Path(setup.config['preparation_review']).read_text())
    assert review['status']=='failed' and review['boundary_verified'] is False
    assert review['failed_case']=='case-0' and review['cases_checked']==0
    assert 'no newline' in review['boundary_policy']
    assert not Path(setup.config['prepared_events']).exists()


@pytest.mark.parametrize('which',['manifest','audit','summary','source-qa','dataset-role','declaration','source-config','role'])
def test_source_metadata_guards_precede_input_prompt_open(setup,monkeypatch,which):
    if which=='manifest':
        value=deepcopy(setup.manifest);value['status']='failed';dump(setup.source_stage/'manifest.json',value)
    elif which=='audit':
        value=deepcopy(setup.source_audit);value['identity_hash']='wrong';dump(setup.source_stage/'audit.json',value)
    elif which=='summary':
        value=deepcopy(setup.source_summary);value['evaluated']=2;dump(setup.source_stage/'summary.json',value)
    elif which=='source-qa':
        value=deepcopy(setup.source_qa);value['smoke_subset']=True;dump(setup.source['preflight_result'],value)
    elif which=='dataset-role':
        path=Path(setup.source['dataset']).with_suffix('.manifest.json')
        value=json.loads(path.read_text());value['evaluation_role']='heldout';dump(path,value)
    elif which=='declaration':setup.config['candidate_declaration_sha256']='wrong'
    elif which=='source-config':setup.config['source_confidence_config_sha256']='wrong'
    else:setup.config['evaluation_role']='final'
    monkeypatch.setattr(confidence,'inputs',lambda *args,**kwargs:pytest.fail('opened input prompts before guard'))
    monkeypatch.setattr(measurement,'_load_tokenizer',lambda *args:pytest.fail('loaded tokenizer before guard'))
    with pytest.raises(ValueError):measurement.prepare(setup.config)


def test_hash_smoke_is_reproducible_without_outcomes(setup):
    setup.config['case_limit']=2;setup.config['selection_seed']=23
    measurement.prepare(setup.config)
    qa,cases=measurement.inputs(setup.config)
    selected=sorted(setup.cases,key=lambda case:(digest([23,case['id']]),case['id']))[:2]
    assert [case['id'] for case in cases]==sorted(case['id'] for case in selected)
    assert qa['smoke_subset'] is True and qa['source_cases']==3


@pytest.mark.parametrize('patch',[
    {'scoring_backend':'automatic'}, {'event_batch_size':0}, {'prompt_batch_size':'auto'},
    {'case_limit':0}, {'parity_check':'yes'}, {'parity_atol':float('nan')},
    {'measurement_dtype':'float16'}, {'measurement_dtype':None}, {'tokenization_rule':'repair_whitespace'},
    {'model_revision':'c'*40}, {'run_dir':'artifacts/binding/final/candidates'},
])
def test_invalid_runner_contract_is_rejected_before_tokenization(setup,monkeypatch,patch):
    setup.config.update(patch)
    monkeypatch.setattr(measurement,'_load_tokenizer',lambda *args:pytest.fail('invalid config loaded tokenizer'))
    with pytest.raises(ValueError):measurement.prepare(setup.config)


def test_resume_preserves_committed_chunks_and_complete_reuse_loads_nothing(prepared,monkeypatch):
    fake_registry(monkeypatch)
    class Interrupted(CausalModel):
        def __call__(self,**kwargs):
            if len(self.calls)==3:raise RuntimeError('interrupted second case')
            return super().__call__(**kwargs)
    load_fake(monkeypatch,prepared.tokenizer,Interrupted())
    with pytest.raises(RuntimeError,match='interrupted'):measurement.run(prepared.config)
    out=Path(prepared.config['run_dir'])/'candidate_measurement'
    first=(out/'chunks/00000000.json').read_bytes()
    assert json.loads((out/'manifest.json').read_text())['status']=='failed'
    model,calls=load_fake(monkeypatch,prepared.tokenizer)
    summary=measurement.run(prepared.config)
    assert len(calls)==1 and len(model.calls)==6 and model.attention_backend=='sdpa'
    assert summary['resumed_cases']==1 and summary['measured_this_attempt']==2
    assert summary['evaluated']==summary['planned']==3 and summary['prefix_node_evaluations']==105
    assert (out/'chunks/00000000.json').read_bytes()==first
    assert measurement.audit(prepared.config)['status']=='passed'
    from codecue.binding import model_adapter
    monkeypatch.setattr(model_adapter,'load',lambda *args:pytest.fail('completed run loaded a model'))
    before={path:path.read_bytes() for path in out.rglob('*') if path.is_file()}
    assert measurement.run(prepared.config)==summary
    assert all(path.read_bytes()==content for path,content in before.items())


def test_float32_measurement_overrides_load_only_and_enforces_no_tf32(prepared,monkeypatch):
    fake_registry(monkeypatch);model,calls=load_fake(monkeypatch,prepared.tokenizer)
    original=deepcopy(prepared.config)
    torch.set_float32_matmul_precision('high')
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True
    summary=measurement.run(prepared.config)
    assert prepared.config==original and prepared.config['dtype']=='bfloat16'
    assert calls[0] is not prepared.config and calls[0]['dtype']=='float32'
    assert calls[0]['model_revision']==prepared.config['model_revision']
    assert model.dtype==torch.float32
    assert summary['source_dtype']=='bfloat16' and summary['measurement_dtype']==summary['actual_model_dtype']=='float32'
    assert summary['dtype']=='float32' and summary['actual_model_dtype_verified'] is True
    assert summary['tf32_settings']==dict(float32_matmul_precision='highest',
        cuda_matmul_allow_tf32=False,cudnn_allow_tf32=False)
    assert summary['tf32_policy']=='disabled_highest_float32'
    qa,_=measurement.inputs(prepared.config)
    assert qa['source_dtype']=='bfloat16' and qa['measurement_dtype']=='float32'
    assert qa['actual_model_dtype'] is None and qa['actual_model_dtype_verified'] is False
    path=Path(prepared.config['run_dir'])/'candidate_measurement/manifest.json'
    assert json.loads(path.read_text())['identity']['config']['dtype']=='bfloat16'
    assert measurement.audit(prepared.config)['status']=='passed'


def test_measurement_dtype_defaults_to_original_source_without_precision_fallback(setup,monkeypatch):
    setup.config.pop('measurement_dtype')
    qa=measurement.prepare(setup.config)
    assert qa['source_dtype']==qa['measurement_dtype']=='bfloat16'
    assert qa['tf32_policy']=='unchanged_bfloat16'
    fake_registry(monkeypatch);_,calls=load_fake(monkeypatch,setup.tokenizer)
    summary=measurement.run(setup.config)
    assert calls[0]['dtype']=='bfloat16' and summary['actual_model_dtype']=='bfloat16'
    assert measurement.audit(setup.config)['status']=='passed'


def test_loaded_model_dtype_mismatch_is_rejected_before_measurement(prepared,monkeypatch):
    fake_registry(monkeypatch);model=CausalModel();model.dtype=torch.bfloat16
    load_fake(monkeypatch,prepared.tokenizer,model)
    with pytest.raises(ValueError,match='actual dtype differs'):measurement.run(prepared.config)
    assert not model.calls


@pytest.mark.parametrize('field,value',[('measurement_dtype','bfloat16'),('source_dtype','float32'),
    ('actual_model_dtype','float32'),('actual_model_dtype_verified',True),('tokenization_rule',measurement.STANDALONE_RULE)])
def test_preparation_precision_and_rule_metadata_cannot_be_changed(prepared,field,value):
    path=Path(prepared.config['preparation_review']);qa=json.loads(path.read_text());qa[field]=value;dump(path,qa)
    with pytest.raises(ValueError):measurement.inputs(prepared.config)


def test_runtime_and_chunk_tf32_policy_are_audited(prepared,monkeypatch):
    fake_registry(monkeypatch);load_fake(monkeypatch,prepared.tokenizer);measurement.run(prepared.config)
    out=Path(prepared.config['run_dir'])/'candidate_measurement';path=out/'runtime.json'
    original=path.read_bytes();runtime=json.loads(original)
    runtime['tf32_settings']['cuda_matmul_allow_tf32']=True;dump(path,runtime)
    with pytest.raises(ValueError,match='TF32 enforcement'):measurement.audit(prepared.config)
    path.write_bytes(original);path=out/'chunks/00000000.json';chunk=json.loads(path.read_text())
    chunk['execution']['precision']['actual_model_dtype']='bfloat16';dump(path,chunk)
    with pytest.raises(ValueError,match='actual dtype contract'):measurement.audit(prepared.config)


def declare_standalone(setup):
    from codecue.binding import candidate_continuation
    setup.config['tokenization_rule']=measurement.STANDALONE_RULE
    setup.declaration['tokenization_rule']=measurement.STANDALONE_RULE
    path=Path(setup.config['candidate_declaration']);dump(path,setup.declaration)
    setup.config['candidate_declaration_sha256']=sha(path)
    return candidate_continuation.preflight(setup.declaration)


def test_standalone_rule_dispatch_keeps_saved_ids_and_checks_toolkit_pin(setup,monkeypatch):
    review=declare_standalone(setup)
    class DecodeVerified(Tokenizer):
        def __init__(self):self.seen=[]
        def __call__(self,text,*,add_special_tokens):
            self.seen.append(text)
            assert not any(text.startswith(case['prompt']) and text!=case['prompt'] for case in setup.cases)
            return super().__call__(text,add_special_tokens=add_special_tokens)
        def decode(self,ids,*,skip_special_tokens,clean_up_tokenization_spaces):
            assert skip_special_tokens is False and clean_up_tokenization_spaces is False
            characters={**{value:str(value) for value in range(10)},10:'-',11:'Q',12:':',13:'A'}
            return ''.join(characters[token] for token in ids)
    tokenizer=DecodeVerified();monkeypatch.setattr(measurement,'_load_tokenizer',lambda config:tokenizer)
    qa=measurement.prepare(setup.config)
    assert qa['tokenization_rule']==measurement.STANDALONE_RULE
    assert qa['provenance']['continuation_toolkit_sha256']==review['continuation_toolkit_sha256']
    _,cases=measurement.inputs(setup.config)
    assert [case['event_bank']['input_token_ids'] for case in cases]==[case['input_token_ids'] for case in setup.cases]
    assert '1' in tokenizer.seen and 'Q:1' not in tokenizer.seen
    path=Path(setup.declaration['output_review']);review['continuation_toolkit_sha256']='wrong';dump(path,review)
    with pytest.raises(ValueError,match='standalone continuation toolkit'):measurement.inputs(setup.config)


def test_rule_mismatch_is_rejected_before_prompt_open(setup,monkeypatch):
    setup.config['tokenization_rule']=measurement.STANDALONE_RULE
    monkeypatch.setattr(confidence,'inputs',lambda *args,**kwargs:pytest.fail('mismatched rule opened prompts'))
    with pytest.raises(ValueError,match='tokenization_rule differs'):measurement.prepare(setup.config)


def test_max_rule_remains_stricter_than_additive_probability_tolerance(prepared,monkeypatch):
    _,cases=measurement.inputs(prepared.config);cases=cases[:1];bank=cases[0]['event_bank']
    def controlled(model,banks,config,pad_token_id,name):
        values=[-math.inf]*len(bank['events']);values[0]=math.log(.2)
        values[len(bank['eos_token_ids'])]=math.log(.3 if name=='full_prefix_trie' else .315)
        score=event.summarize_events(bank,values);score['forward_calls']=1
        return [score]
    monkeypatch.setattr(measurement,'_backend',controlled)
    config=dict(prepared.config,parity_check=True,parity_atol=.01,parity_rtol=.01)
    assert abs(.5-.515)<.01+.01*.515
    with pytest.raises(ValueError,match='parity failed for support_mass'):
        measurement.measure_cases(None,cases,config,23)


def test_recorded_scalar_and_event_utilization_use_exact_live_max_rule(prepared,monkeypatch):
    _,cases=measurement.inputs(prepared.config);cases=cases[:1];bank=cases[0]['event_bank']
    baseline=measurement.score_banks(CausalModel(),[bank])[0]
    shifted=event.summarize_events(bank,[row['log_probability']+.005 for row in baseline['event_variants']])
    shifted['forward_calls']=1
    monkeypatch.setattr(measurement,'_backend',lambda model,banks,config,pad,name:
        [baseline if name=='full_prefix_trie' else shifted])
    _,execution=measurement.measure_cases(None,cases,dict(prepared.config,parity_check=True,parity_atol=.01,parity_rtol=.01),23)
    parity=execution['parity'];a=baseline['support_log_mass'];b=shifted['support_log_mass']
    assert parity['tolerance_rule']==measurement.TOLERANCE_RULE
    assert parity['max_scalar_tolerance_utilization']['support_log_mass']==pytest.approx(abs(a-b)/max(.01,.01*max(abs(a),abs(b))))
    expected=max(abs(left[key]-right[key])/max(.01,.01*max(abs(left[key]),abs(right[key])))
        for left,right in zip(baseline['event_variants'],shifted['event_variants'])
        for key in ('log_probability','absolute_event_mass'))
    assert parity['max_event_tolerance_utilization']==pytest.approx(expected)


def test_scalar_schema_forbids_candidates_oracles_and_nonfinite_values(prepared):
    _,cases=measurement.inputs(prepared.config)
    rows=measurement.scalar_rows(cases,measurement.score_banks(CausalModel(),[case['event_bank'] for case in cases]))
    for field,value in [('prediction',1),('candidate',1),('support_log_mass',float('-inf')),
                        ('support_mass',1.1),('trie_nodes',1),('event_bank_sha256','wrong')]:
        altered=deepcopy(rows);altered[0][field]=value
        with pytest.raises(ValueError):measurement.validate_rows(cases,altered)


def test_parity_failure_is_explicit_and_never_falls_back(prepared,monkeypatch):
    _,cases=measurement.inputs(prepared.config)
    original=measurement._backend
    def changed(model,banks,config,pad_token_id,name):
        result=original(model,banks,config,pad_token_id,name)
        if name=='cached_trie':result[0]['support_conditional_entropy_nats']+=.2
        return result
    monkeypatch.setattr(measurement,'_backend',changed)
    config=dict(prepared.config,parity_check=True,parity_atol=0.,parity_rtol=0.)
    with pytest.raises(ValueError,match='parity failed'):measurement.measure_cases(CausalModel(),cases,config,23)


def test_event_permutation_cannot_hide_behind_equal_scalar_summaries(prepared,monkeypatch):
    _,cases=measurement.inputs(prepared.config);original=measurement._backend
    def permuted(model,banks,config,pad_token_id,name):
        scores=original(model,banks,config,pad_token_id,name)
        if name=='cached_trie':scores[0]['event_variants'].reverse()
        return scores
    monkeypatch.setattr(measurement,'_backend',permuted)
    with pytest.raises(ValueError,match='identity/order differs'):
        measurement.measure_cases(CausalModel(),cases,dict(prepared.config,parity_check=True),23)


def test_cached_collection_parity_audit_and_reference_work_are_logged(setup,monkeypatch):
    setup.config.update(scoring_backend='cached_trie',parity_check=True,batch_size=3,parity_atol=2e-6,parity_rtol=2e-6)
    measurement.prepare(setup.config);fake_registry(monkeypatch);load_fake(monkeypatch,setup.tokenizer)
    summary=measurement.run(setup.config)
    assert summary['backend_forward_calls']==8 and summary['parity_reference_forward_calls']==7
    assert summary['parity']['event_variants']==297 and summary['parity']['status']=='passed'
    assert summary['parity']['max_event_tolerance_utilization']<=1
    assert measurement.audit(setup.config)['status']=='passed'
    path=Path(setup.config['run_dir'])/'candidate_measurement/chunks/00000000.json'
    chunk=json.loads(path.read_text());chunk['execution']['parity']['event_variants']=1;dump(path,chunk)
    with pytest.raises(ValueError,match='per-event parity audit'):measurement.audit(setup.config)


def test_preparation_rejects_eos_outside_special_token_vocabulary(setup,monkeypatch):
    class MissingEOS(Tokenizer):all_special_ids=[14,15,23]
    monkeypatch.setattr(measurement,'_load_tokenizer',lambda config:MissingEOS())
    with pytest.raises(ValueError,match='special-token set'):measurement.prepare(setup.config)
    assert json.loads(Path(setup.config['preparation_review']).read_text())['status']=='failed'


def test_added_special_eos_variants_are_valid_when_hf_role_list_omits_them(setup,monkeypatch):
    class RoleListOmitsEOS(Tokenizer):
        all_special_ids=[16,23]  # Only the role-mapped EOT and BOS/pad entries.
        added_tokens_decoder={token:SimpleNamespace(content=f'special-{token}',special=True)
                              for token in (14,15,16)}
        def convert_tokens_to_ids(self,spellings):return [int(text.split('-')[-1]) for text in spellings]
    tokenizer=RoleListOmitsEOS()
    contract=measurement._tokenizer_contract(tokenizer,[14,15,16])
    assert contract==dict(vocabulary_size=24,pad_token_id=23,
        eos_token_spellings=['special-14','special-15','special-16'])
    monkeypatch.setattr(measurement,'_load_tokenizer',lambda config:tokenizer)
    review=measurement.prepare(setup.config)
    assert review['status']=='passed' and review['tokenizer']==contract
    assert measurement.inputs(setup.config)[0]['tokenizer']==contract


@pytest.mark.parametrize('special',[False,None,'true',1])
def test_added_token_without_explicit_special_boolean_cannot_authorize_eos(special):
    class NonSpecial(Tokenizer):
        all_special_ids=[16,23]
        added_tokens_decoder={14:SimpleNamespace(content='special-14',special=special)}
    with pytest.raises(ValueError,match='special-token set'):
        measurement._tokenizer_contract(NonSpecial(),[14])


@pytest.mark.parametrize('mode',['out-of-vocabulary','negative','wrong-content','wrong-reverse'])
def test_added_special_eos_still_requires_valid_id_and_consistent_spelling(mode):
    class Inconsistent(Tokenizer):
        all_special_ids=[16,23]
        added_tokens_decoder={token:SimpleNamespace(content=f'special-{token}',special=True)
                              for token in (-1,14,24)}
        def convert_tokens_to_ids(self,spellings):return [15 for text in spellings]
    tokenizer=Inconsistent()
    if mode=='out-of-vocabulary':eos=[24]
    elif mode=='negative':eos=[-1]
    else:
        eos=[14]
        if mode=='wrong-content':tokenizer.added_tokens_decoder[14]=SimpleNamespace(content='different',special=True)
    with pytest.raises(ValueError):measurement._tokenizer_contract(tokenizer,eos)


def test_resume_refuses_noncontiguous_or_wrong_input_chunks(prepared,monkeypatch):
    fake_registry(monkeypatch);load_fake(monkeypatch,prepared.tokenizer)
    measurement.run(prepared.config);out=Path(prepared.config['run_dir'])/'candidate_measurement'
    qa,cases=measurement.inputs(prepared.config)
    first=out/'chunks/00000000.json';content=first.read_bytes();first.unlink()
    with pytest.raises(ValueError,match='contiguous'):measurement._chunks(prepared.config,qa,cases,out)
    first.write_bytes(content);chunk=json.loads(content);chunk['prepared_events_sha256']='wrong';dump(first,chunk)
    with pytest.raises(ValueError,match='chunk provenance'):measurement._chunks(prepared.config,qa,cases,out)


@pytest.mark.parametrize('mode',['summary','row','chunk','manifest','runtime'])
def test_audit_rejects_changed_provenance_or_scalar_payload(prepared,monkeypatch,mode):
    fake_registry(monkeypatch);load_fake(monkeypatch,prepared.tokenizer)
    measurement.run(prepared.config);out=Path(prepared.config['run_dir'])/'candidate_measurement'
    if mode=='row':
        path=out/'scalars.jsonl';rows=read_jsonl(path);rows[0]['support_mass']=float('nan')
        path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    else:
        path=out/('chunks/00000000.json' if mode=='chunk' else mode+'.json')
        value=json.loads(path.read_text())
        if mode=='summary':value['model']='other/checkpoint'
        elif mode=='chunk':value['execution']['scoring_backend']='cached_trie'
        elif mode=='manifest':value['identity_hash']='wrong'
        else:value['attention_backend']='eager'
        dump(path,value)
    with pytest.raises(ValueError):measurement.audit(prepared.config)


@pytest.mark.parametrize('bad',['nan','positive_infinity','no_mass'])
def test_reference_rejects_invalid_causal_distributions(prepared,bad):
    _,cases=measurement.inputs(prepared.config)
    with pytest.raises(ValueError,match='probability distributions'):
        measurement.score_banks(CausalModel(bad=bad),[cases[0]['event_bank']])
