"""No pretrained tokenizers/models: exact integer events use tiny injected fakes."""
from copy import deepcopy
import json
import math
from types import SimpleNamespace

import pytest
import torch

from codecue.binding import candidate_confidence as candidate
from codecue.binding.datasets import digest


class Tokenizer:
    def __init__(self):self.seen=[]
    def __call__(self,text,*,add_special_tokens):
        assert add_special_tokens is False
        self.seen.append(text)
        lookup={**{str(i):i for i in range(10)},'-':10,'Q':11,':':12}
        return {'input_ids':[lookup[character] for character in text]}


class TransitionModel:
    device='cpu';training=False;vocabulary=16

    def __init__(self):self.calls=[]

    def generate(self,*args,**kwargs):raise AssertionError('teacher-forced scorer must never generate')

    def __call__(self,*,input_ids,attention_mask,position_ids,use_cache):
        assert use_cache is False and not torch.is_grad_enabled()
        for mask,positions in zip(attention_mask,position_ids):
            assert positions[mask.bool()].tolist()==list(range(int(mask.sum())))
            assert torch.all(positions[~mask.bool()]==1)
        self.calls.append((input_ids.clone(),attention_mask.clone(),position_ids.clone()))
        offset=input_ids.remainder(3)+position_ids.remainder(4)
        weights=torch.arange(1,self.vocabulary+1,dtype=torch.float32)+offset[:,:,None]
        return SimpleNamespace(logits=weights.log())


def bank(values=(-16,-1,0,1,16),eos=(15,)):
    return candidate.build_events(Tokenizer(),'Q:',[11,12],list(values),list(eos))


def expected_log_probability(event,prefix=(11,12),vocabulary=16):
    history=list(prefix);result=0.
    for token in event['event_token_ids']:
        offset=history[-1]%3+(len(history)-1)%4
        result+=math.log((token+1+offset)/sum(k+1+offset for k in range(vocabulary)))
        history.append(token)
    return result


def test_exact_prompt_multi_token_negative_and_one_sixteen_prefix_events():
    tokenizer=Tokenizer()
    events=candidate.build_events(tokenizer,'Q:',[11,12],[-16,-1,0,1,16],[14,15])
    assert tokenizer.seen==['Q:','Q:-16','Q:-1','Q:0','Q:1','Q:16']
    assert all('\n' not in text for text in tokenizer.seen)
    assert events['input_token_ids']==[11,12]
    assert events['events'][0]['event_token_ids']==[10,1,6,14]
    one=[event for event in events['events'] if event['candidate']==1 and event['eos_token_id']==15][0]
    sixteen=[event for event in events['events'] if event['candidate']==16 and event['eos_token_id']==15][0]
    assert one['continuation_token_ids']==[1] and sixteen['continuation_token_ids']==[1,6]
    assert one['event_token_ids']==[1,15] and sixteen['event_token_ids']==[1,6,15]
    assert sixteen['event_token_ids'][:len(one['event_token_ids'])]!=one['event_token_ids']
    assert events['prefix_free'] is True
    assert len(events['events'])==10


@pytest.mark.parametrize('mode',['saved-prefix','merged-prefix','empty-continuation','duplicate','internal-eos'])
def test_boundary_rejects_merging_empty_continuation_or_duplicate_events(mode):
    class Broken(Tokenizer):
        def __call__(self,text,*,add_special_tokens):
            ids=super().__call__(text,add_special_tokens=add_special_tokens)['input_ids']
            if mode=='saved-prefix':ids[0]=9
            elif text!='Q:':
                if mode=='merged-prefix':ids[1]=9
                elif mode=='empty-continuation':ids=ids[:2]
                elif mode=='duplicate':ids=ids[:2]+[1]
                elif mode=='internal-eos':ids=ids[:2]+[15]
            return {'input_ids':ids}
    with pytest.raises(ValueError):
        candidate.build_events(Broken(),'Q:',[11,12],[1,16],[15])


def test_full_variant_prefixfree_check_is_explicit():
    with pytest.raises(ValueError,match='prefix-free'):
        candidate._prefix_free([[1,2],[1,2,3],[9]])
    with pytest.raises(ValueError,match='duplicate'):
        candidate._prefix_free([[1,15],[1,15]])


def test_teacher_forced_known_probabilities_include_eos_and_correct_causal_positions():
    events=bank(eos=(14,15));model=TransitionModel()
    result=candidate.score_events(model,events,batch_size=4,pad_token_id=15)
    assert len(model.calls)==3 and result['forward_calls']==3
    for event in result['event_variants']:
        expected=expected_log_probability(event)
        assert event['log_probability']==pytest.approx(expected,abs=2e-6)
        assert event['absolute_event_mass']==pytest.approx(math.exp(expected),rel=3e-6)
    assert result['generated_tokens']==0 and result['target_outcomes_read'] is False
    assert result['teacher_forced_scored_tokens']==sum(len(event['event_token_ids']) for event in events['events'])
    assert 'restricted set' in result['limitation']
    assert result['support_mass']==pytest.approx(sum(row['absolute_event_mass'] for row in result['event_variants']))
    assert sum(row['support_conditional_probability'] for row in result['candidates'])==pytest.approx(1)
    # No EOS is fed as input: the final candidate position predicts it.
    assert all(15 not in ids[mask.bool()].tolist() for ids_batch,masks,_ in model.calls for ids,mask in zip(ids_batch,masks))
    assert any(torch.any(mask==0) for _,mask,_ in model.calls)


def test_padding_and_batch_size_do_not_change_event_scores():
    events=bank(eos=(14,15))
    singleton=candidate.score_events(TransitionModel(),events,batch_size=1)
    padded=candidate.score_events(TransitionModel(),events,batch_size=100,pad_token_id=15)
    assert singleton['event_variants']==padded['event_variants']
    assert singleton['candidates']==padded['candidates']
    assert singleton['support_conditional_entropy_nats']==padded['support_conditional_entropy_nats']


def test_known_absolute_and_support_conditional_masses_aggregate_eos_union():
    events=bank(values=(1,16),eos=(14,15))
    result=candidate.summarize_events(events,[math.log(value) for value in (.1,.2,.15,.05)])
    assert result['support_mass']==pytest.approx(.5)
    assert [row['absolute_event_mass'] for row in result['candidates']]==pytest.approx([.3,.2])
    assert [row['support_conditional_probability'] for row in result['candidates']]==pytest.approx([.6,.4])
    assert result['support_conditional_entropy_nats']==pytest.approx(-.6*math.log(.6)-.4*math.log(.4))
    assert result['support_conditional_top_two_probability_margin']==pytest.approx(.2)


def test_tiny_or_zero_events_keep_stable_conditional_distribution():
    events=bank(values=(1,16))
    tiny=candidate.summarize_events(events,[-1000.,-1001.])
    assert tiny['support_mass']==0 and math.isfinite(tiny['support_log_mass'])
    assert sum(row['support_conditional_probability'] for row in tiny['candidates'])==pytest.approx(1)
    assert tiny['support_conditional_entropy_nats']>0
    partial=candidate.summarize_events(events,[-math.inf,math.log(.2)])
    assert partial['candidates'][0]['absolute_event_mass']==0
    assert partial['support_conditional_entropy_nats']==0
    assert partial['support_conditional_top_two_probability_margin']==1
    with pytest.raises(ValueError,match='zero probability support'):
        candidate.summarize_events(events,[-math.inf,-math.inf])


@pytest.mark.parametrize('values',[[.1,-2.],[math.inf,-2.],[math.nan,-2.],[True,-2.],
    [math.log(.8),math.log(.7)],[-2.]])
def test_reject_positive_nonfinite_impossible_support_or_incomplete_mass(values):
    with pytest.raises(ValueError):candidate.summarize_events(bank(values=(1,16)),values)


def test_support_domain_has_explicit_small_numerical_tolerance():
    result=candidate.summarize_events(bank(values=(1,16)),[math.log(.5+1e-8)]*2)
    assert result['support_mass']==1 and result['support_log_mass']==0
    assert result['support_mass_roundoff_tolerance']==candidate.MASS_TOLERANCE


@pytest.mark.parametrize('patch',[
    {'candidates':[1,1]}, {'candidates':[16,1]}, {'candidates':[-17,1]}, {'candidates':[True]},
    {'bounds':[-16,17]}, {'bounds':[2,-2]}, {'bounds':[-1,True]}, {'bounds':[0]},
    {'candidates':[1],'bounds':[0,1]}, {'eos_token_ids':[]}, {'eos_token_ids':[1,1]},
    {'eos_token_ids':[-1]}, {'eos_token_ids':[True]}, {'eos_token_ids':None},
    {'terminator':'newline'}, {'evaluation_role':'final'}, {'expected_answer':object()},
])
def test_declaration_rejects_invalid_candidate_order_bounds_eos_or_oracle(patch):
    config=dict(evaluation_role=candidate.ROLE,eos_token_ids=[15],terminator='eos',**{})
    config.update(patch)
    with pytest.raises(ValueError):candidate.declaration(config)


def test_metadata_preflight_does_not_tokenize_load_or_read_source_labels(tmp_path,monkeypatch):
    from codecue.binding import experiment_log,model_adapter
    logged=[]
    monkeypatch.setattr(experiment_log,'note_artifact',lambda path:logged.append(path))
    monkeypatch.setattr(model_adapter,'load',lambda *args:pytest.fail('metadata preflight loaded a model'))
    config=dict(evaluation_role=candidate.ROLE,eos_token_ids=[128001,128008,128009],terminator='eos',
        source_labels=str(tmp_path/'does-not-exist-labels.jsonl'),output_review=str(tmp_path/'review.json'))
    result=candidate.preflight(config)
    assert result['candidates']==list(range(-16,17)) and result['planned_event_variants']==99
    assert result['tokenizer_loaded'] is False and result['model_loaded'] is False
    assert result['tokenization_performed'] is False and result['boundary_verified'] is False
    assert result['probabilities_computed'] is False and result['oracle_fields_read'] is False
    assert result['target_outcomes_read'] is False
    assert json.loads((tmp_path/'review.json').read_text())==result and len(logged)==1
    assert result['config_hash']==digest(config)
    assert candidate.declaration(dict(eos_token_ids=[15],bounds=[-1,1]))[0]==[-1,0,1]
    with pytest.raises(ValueError,match='reserved outcome paths'):
        candidate.preflight(dict(config,output_review='artifacts/binding/final/review.json'))


def test_bank_identity_schema_and_order_cannot_be_changed():
    original=bank()
    for change in ('input','event','role','oracle','order'):
        altered=deepcopy(original)
        if change=='input':altered['input_token_ids'][0]=99
        elif change=='event':altered['events'][0]['event_token_ids'][-1]=1
        elif change=='role':altered['evaluation_role']='final'
        elif change=='oracle':altered['expected_answer']=1
        else:altered['events'].reverse()
        with pytest.raises(ValueError):candidate.validate_bank(altered)


@pytest.mark.parametrize('mode',['shape','nan','invalid-eos','training'])
def test_model_contract_rejects_invalid_shape_nonfinite_or_vocab(mode):
    class Broken(TransitionModel):
        def __call__(self,**kwargs):
            output=super().__call__(**kwargs)
            if mode=='shape':output.logits=output.logits[:,:-1]
            elif mode=='nan':output.logits[:]=math.nan
            return output
    model=Broken();model.training=mode=='training'
    events=bank(eos=(99,)) if mode=='invalid-eos' else bank()
    with pytest.raises(ValueError):candidate.score_events(model,events)


def test_runnable_selfcheck_uses_only_software_fixtures():
    result=candidate.selfcheck()
    assert result['status']=='passed' and result['candidates']==33
    assert result['pretrained_artifacts_used'] is False and result['generated_tokens']==0
