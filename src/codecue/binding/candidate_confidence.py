"""Exact-prefix, teacher-forced integer-plus-EOS event probabilities.

This toolkit never loads a tokenizer/model or opens target outcome files. Its
finite integer support is a declared event set, not a claim to cover every answer.
"""
from __future__ import annotations

import math
from pathlib import Path

from .datasets import digest, write_json
from .published_benchmarks import sha

ROLE='candidate_event_preparation_v1'
MEASUREMENT='exact_saved_prompt_integer_plus_explicit_eos_v1'
DOMAIN=(-16,16)
MASS_TOLERANCE=1e-6
LIMITATION=('Absolute masses cover only the declared finite integer-plus-EOS events. '
    'Support-conditional entropy and margin describe that restricted set; they are not overall full-answer confidence.')
BANK_FIELDS={'schema_version','evaluation_role','measurement','prompt_sha256','input_token_ids',
    'input_token_ids_sha256','candidates','eos_token_ids','terminator','events','prefix_free','bank_sha256'}
EVENT_FIELDS={'candidate','surface','continuation_token_ids','eos_token_id','event_token_ids'}


def _ids(values,description,*,nonempty=True):
    if (not isinstance(values,(list,tuple)) or (nonempty and not values)
            or any(type(item) is not int or item<0 for item in values)):
        raise ValueError(description+' must contain nonnegative integer token IDs')
    return list(values)


def _candidates(values):
    if (not isinstance(values,(list,tuple)) or not values
            or any(type(item) is not int or not DOMAIN[0]<=item<=DOMAIN[1] for item in values)
            or list(values)!=sorted(set(values))):
        raise ValueError('candidate integers must be unique, increasing and within -16..16')
    return list(values)


def _eos(values):
    values=_ids(values,'declared EOS IDs')
    if len(set(values))!=len(values):raise ValueError('declared EOS IDs must be unique')
    return values


def declaration(config):
    """Validate metadata alone: no tokenizer, checkpoint, dataset or outcomes."""
    from .forecasting import _discovery_declaration, _discovery_response_path
    _discovery_declaration(config)
    if config.get('evaluation_role',ROLE)!=ROLE:raise ValueError('candidate preparation role required')
    if any(key in config for key in ('expected_answer','prediction','correct','raw_response','target_label')):
        raise ValueError('oracle/outcome fields cannot declare candidate events')
    if config.get('terminator','eos')!='eos':raise ValueError('declare the appended EOS-token terminator')
    if 'candidates' in config and 'bounds' in config:raise ValueError('declare candidates or bounds, not both')
    if 'candidates' in config:values=_candidates(config['candidates'])
    else:
        bounds=config.get('bounds',list(DOMAIN))
        if (not isinstance(bounds,(list,tuple)) or len(bounds)!=2
                or any(type(value) is not int for value in bounds)
                or not DOMAIN[0]<=bounds[0]<=bounds[1]<=DOMAIN[1]):
            raise ValueError('increasing inclusive integer bounds within -16..16 required')
        values=list(range(bounds[0],bounds[1]+1))
    eos=_eos(config.get('eos_token_ids'))
    if config.get('output_review'):_discovery_response_path(config['output_review'])
    return values,eos


def preflight(config):
    """Record a CPU-safe declaration; actual token boundary checks remain pending."""
    candidates,eos=declaration(config)
    if not config.get('output_review'):raise ValueError('output_review metadata path required')
    result=dict(status='passed',evaluation_role=ROLE,measurement=MEASUREMENT,config_hash=digest(config),
        toolkit_sha256=sha(Path(__file__)),candidates=candidates,domain=list(DOMAIN),eos_token_ids=eos,
        terminator='eos',event_definition='canonical integer continuation tokens followed by one declared EOS ID',
        planned_event_variants=len(candidates)*len(eos),candidate_order='increasing numeric order',
        eos_union='distinct disjoint variants, summed for each candidate',tokenizer_loaded=False,model_loaded=False,
        preparation_stage='declaration only; actual prompt/event token preparation remains pending',
        eos_vocabulary_verified=False,
        tokenization_performed=False,boundary_verified=False,probabilities_computed=False,
        generated_tokens=0,target_outcomes_read=False,oracle_fields_read=False,
        access_contract='Only explicit configuration metadata; no model, tokenizer, source labels or response files opened.',
        boundary_contract='Tokenize unchanged prompt plus canonical candidate; reject any saved-prefix mismatch or merging.',
        limitation=LIMITATION)
    write_json(config['output_review'],result);return result


def _prefix_free(sequences):
    sequences=[tuple(item) for item in sequences]
    if len(set(sequences))!=len(sequences):raise ValueError('duplicate candidate-plus-EOS token events')
    ordered=sorted(sequences)
    for left,right in zip(ordered,ordered[1:]):
        if right[:len(left)]==left:raise ValueError('candidate-plus-EOS event variants must be pairwise prefix-free')


def validate_bank(bank):
    if (not isinstance(bank,dict) or set(bank)!=BANK_FIELDS or bank.get('schema_version')!=1 or bank.get('evaluation_role')!=ROLE
            or bank.get('measurement')!=MEASUREMENT or bank.get('terminator')!='eos'
            or bank.get('prefix_free') is not True):
        raise ValueError('candidate event bank schema/access contract differs')
    candidates=_candidates(bank['candidates']);eos=_eos(bank['eos_token_ids'])
    prefix=_ids(bank['input_token_ids'],'saved prompt')
    if (bank['input_token_ids_sha256']!=digest(prefix) or not isinstance(bank['prompt_sha256'],str)
            or len(bank['prompt_sha256'])!=64
            or bank['bank_sha256']!=digest({key:value for key,value in bank.items() if key!='bank_sha256'})):
        raise ValueError('candidate bank exact input or content hash differs')
    events=bank['events']
    if not isinstance(events,list) or len(events)!=len(candidates)*len(eos):
        raise ValueError('candidate/EOS event coverage differs')
    continuation_by_candidate={}
    for event,(candidate,ending) in zip(events,((value,end) for value in candidates for end in eos)):
        if (not isinstance(event,dict) or set(event)!=EVENT_FIELDS or type(event['candidate']) is not int
                or event['candidate']!=candidate or event['surface']!=str(candidate)
                or type(event['eos_token_id']) is not int or event['eos_token_id']!=ending):
            raise ValueError('candidate/EOS event order or identity differs')
        continuation=_ids(event['continuation_token_ids'],'candidate continuation')
        sequence=_ids(event['event_token_ids'],'candidate-plus-EOS event')
        if (set(continuation).intersection(eos) or sequence!=continuation+[ending]
                or continuation_by_candidate.setdefault(candidate,continuation)!=continuation):
            raise ValueError('candidate event must contain its complete continuation and one explicit EOS')
    _prefix_free([event['event_token_ids'] for event in events])
    return bank


def build_events(tokenizer,prompt,input_token_ids,candidates,eos_token_ids):
    """Use an injected tokenizer; never repair/rewrite the saved prompt boundary."""
    candidates=_candidates(candidates);eos=_eos(eos_token_ids)
    prefix=_ids(input_token_ids,'saved prompt')
    if not isinstance(prompt,str) or not prompt:raise ValueError('unchanged nonempty prompt string required')
    actual=_ids(tokenizer(prompt,add_special_tokens=False)['input_ids'],'tokenized prompt')
    if actual!=prefix:raise ValueError('saved prompt IDs differ from exact prompt tokenization')
    events=[]
    for candidate in candidates:
        surface=str(candidate)
        whole=_ids(tokenizer(prompt+surface,add_special_tokens=False)['input_ids'],'prompt-plus-candidate')
        if whole[:len(prefix)]!=prefix or len(whole)<=len(prefix):
            raise ValueError('candidate merges or retokenizes the exact saved prompt boundary')
        continuation=whole[len(prefix):]
        if set(continuation).intersection(eos):raise ValueError('candidate text contains a declared EOS token')
        for ending in eos:
            events.append(dict(candidate=candidate,surface=surface,continuation_token_ids=continuation,
                eos_token_id=ending,event_token_ids=continuation+[ending]))
    _prefix_free([event['event_token_ids'] for event in events])
    bank=dict(schema_version=1,evaluation_role=ROLE,measurement=MEASUREMENT,prompt_sha256=digest(prompt),
        input_token_ids=prefix,input_token_ids_sha256=digest(prefix),candidates=candidates,
        eos_token_ids=eos,terminator='eos',events=events,prefix_free=True)
    bank['bank_sha256']=digest(bank);return validate_bank(bank)


def _logsumexp(values):
    largest=max(values)
    if largest==-math.inf:return -math.inf
    return largest+math.log(math.fsum(math.exp(value-largest) for value in values))


def summarize_events(bank,event_log_probabilities):
    """Aggregate disjoint EOS variants, keeping absolute and conditional masses."""
    validate_bank(bank)
    values=list(event_log_probabilities)
    if len(values)!=len(bank['events']):raise ValueError('one log probability per declared event required')
    if any(isinstance(value,bool) or not isinstance(value,(int,float)) or math.isnan(value)
           or value>math.log1p(MASS_TOLERANCE) for value in values):
        raise ValueError('event log probabilities must be nonpositive, finite or negative infinity')
    values=[min(float(value),0.) for value in values]
    log_support=_logsumexp(values)
    if log_support==-math.inf:raise ValueError('zero probability support has no conditional distribution')
    if log_support>math.log1p(MASS_TOLERANCE):
        raise ValueError('impossible total mass above one for disjoint candidate events')
    event_rows=[dict(event,log_probability=value,absolute_event_mass=math.exp(value))
                for event,value in zip(bank['events'],values)]
    candidates=[];width=len(bank['eos_token_ids'])
    for index,candidate in enumerate(bank['candidates']):
        logmass=_logsumexp(values[index*width:(index+1)*width])
        conditional=math.exp(logmass-log_support)
        candidates.append(dict(candidate=candidate,surface=str(candidate),log_event_mass=logmass,
            absolute_event_mass=math.exp(logmass),support_conditional_probability=conditional))
    entropy=-math.fsum(row['support_conditional_probability']*(row['log_event_mass']-log_support)
                      for row in candidates if row['support_conditional_probability']>0)
    ordered=sorted((row['support_conditional_probability'] for row in candidates),reverse=True)
    margin=ordered[0]-(ordered[1] if len(ordered)>1 else 0.)
    return dict(status='scored',evaluation_role=ROLE,measurement=MEASUREMENT,bank_sha256=bank['bank_sha256'],
        prompt_sha256=bank['prompt_sha256'],input_token_ids_sha256=bank['input_token_ids_sha256'],
        candidates=candidates,event_variants=event_rows,support_mass=min(1.,math.exp(log_support)),
        support_log_mass=min(0.,log_support),support_mass_roundoff_tolerance=MASS_TOLERANCE,
        support_mass_underflowed=math.exp(log_support)==0,
        support_conditional_entropy_nats=max(0.,entropy),support_conditional_top_two_probability_margin=margin,
        generated_tokens=0,target_outcomes_read=False,oracle_fields_read=False,limitation=LIMITATION)


def score_events(model,bank,*,batch_size=16,pad_token_id=0):
    """Score every continuation AND EOS with direct causal forward passes.

    The supplied model must already be loaded/evaluating. Inputs omit the final
    EOS because its probability is read from the preceding causal position.
    """
    import torch
    validate_bank(bank)
    if type(batch_size) is not int or batch_size<1:raise ValueError('positive event batch_size required')
    if type(pad_token_id) is not int or pad_token_id<0:raise ValueError('nonnegative pad token ID required')
    if getattr(model,'training',False):raise ValueError('teacher-forced model must be in evaluation mode')
    prefix=bank['input_token_ids'];events=bank['events'];values=[];calls=0
    with torch.inference_mode():
        for start in range(0,len(events),batch_size):
            block=events[start:start+batch_size]
            sequences=[prefix+event['event_token_ids'][:-1] for event in block]
            width=max(map(len,sequences))
            encoded=dict(input_ids=torch.tensor([[pad_token_id]*(width-len(ids))+ids for ids in sequences],
                dtype=torch.long,device=model.device),
                attention_mask=torch.tensor([[0]*(width-len(ids))+[1]*len(ids) for ids in sequences],
                    dtype=torch.long,device=model.device))
            positions=encoded['attention_mask'].cumsum(-1)-1
            encoded['position_ids']=positions.masked_fill(encoded['attention_mask']==0,1)
            output=model(**encoded,use_cache=False);calls+=1;logits=output.logits
            if logits.ndim!=3 or logits.shape[:2]!=(len(block),width) or logits.shape[-1]<2:
                raise ValueError('teacher-forced model must return batch-by-position-by-vocabulary logits')
            for index,(sequence,event) in enumerate(zip(sequences,block)):
                targets=event['event_token_ids'];first=width-len(sequence)+len(prefix)-1
                selected=logits[index,first:first+len(targets)].float()
                if (selected.shape[0]!=len(targets) or not torch.isfinite(selected).all()
                        or any(token>=logits.shape[-1] for token in targets)):
                    raise ValueError('finite complete continuation/EOS distributions and valid vocabulary IDs required')
                logp=selected.log_softmax(-1)
                target_ids=torch.tensor(targets,dtype=torch.long,device=logits.device)
                values.append(float(logp.gather(1,target_ids[:,None]).double().sum()))
    result=summarize_events(bank,values)
    result.update(batch_size=batch_size,pad_token_id=pad_token_id,forward_calls=calls,
        teacher_forced_scored_tokens=sum(len(event['event_token_ids']) for event in events),
        use_cache=False,position_ids='left-padding-aware cumulative attention positions, pad positions=1')
    return result


def selfcheck():
    """A runnable tiny uniform-model check; no pretrained artifacts are used."""
    import torch
    from types import SimpleNamespace

    class Tokenizer:
        def __call__(self,text,*,add_special_tokens):
            assert add_special_tokens is False
            lookup={**{str(i):i for i in range(10)},'-':10,'Q':11,':':12}
            return {'input_ids':[lookup[character] for character in text]}

    class Model:
        device='cpu';training=False
        def __call__(self,*,input_ids,attention_mask,position_ids,use_cache):
            assert use_cache is False and not torch.is_grad_enabled()
            return SimpleNamespace(logits=torch.zeros(*input_ids.shape,16))
        def generate(self,*args,**kwargs):raise AssertionError('selfcheck must never generate')

    bank=build_events(Tokenizer(),'Q:',[11,12],list(range(-16,17)),[15])
    result=score_events(Model(),bank,batch_size=7,pad_token_id=15)
    for event in result['event_variants']:
        if not math.isclose(event['absolute_event_mass'],16.**-len(event['event_token_ids']),rel_tol=2e-6):
            raise AssertionError('teacher-forced causal offset or EOS score differs')
    return dict(status='passed',evaluation_role=ROLE,candidates=33,event_variants=33,
        generated_tokens=0,tokenizer_loaded=False,model_loaded=False,pretrained_artifacts_used=False,
        target_outcomes_read=False,software_only=True,support_mass=result['support_mass'],limitation=LIMITATION)
