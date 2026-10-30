"""Bounded arithmetic/interface checks on fixed fixtures and training programs."""
from __future__ import annotations
import time
from .datasets import read_jsonl,write_json
from .interpreter import execute,python_oracle
from .registry import guarded


def cases(rows):
    sources=[('literal','v0 = 7\nv0'),('negative_literal','v0 = -4\nv0'),
             ('addition','v0 = 2 + 3\nv0'),('subtraction','v0 = 9 - 4\nv0'),
             ('overwrite','v0 = 4\nv0 = 9\nv0'),('update','v0 = 2 + 3\nv0 = v0 + 2\nv0'),
             ('two_bindings','v0 = 2 + 3\nv1 = 8 - 1\nv0 - v1'),
             ('copy_dependency','v0 = 4\nv1 = v0 + 3\nv1')]
    result=[{'id':'sanity:'+name,'kind':'primitive','split':'train','source':source,
             'expected_answer':execute(source)['expected_answer']} for name,source in sources]
    training=sorted([r for r in rows if r['split']=='train' and r['control_kind']=='primary'
                     and r['condition']=='neutral' and r['lexical_realization']==0],key=lambda r:r['id'])[:4]
    result += [{k:r[k] for k in ('id','source','split','expected_answer')} | {'kind':'discovery_training'} for r in training]
    return result


@guarded
def run(config):
    import torch
    from codecue.models import generate_free
    from .model_adapter import load,prompt_for
    from .behavior import parse_answer
    from .registry import begin,finish
    out,manifest=begin(config,'interface_diagnostics')
    if (out/'responses.json').exists():
        raise ValueError('interface diagnostic is immutable; choose a new run directory')
    started=time.monotonic()
    selected=cases(read_jsonl(config['dataset']))
    oracle=python_oracle([r['source'] for r in selected])
    if any(r['expected_answer']!=o['answer'] for r,o in zip(selected,oracle)):
        raise ValueError('independent arithmetic oracle mismatch')
    tokenizer,model=load(config)
    prompts=[prompt_for(tokenizer,r,config['protocol']) for r in selected]
    input_ids=[tokenizer(p,add_special_tokens=False)['input_ids'] for p in prompts]
    if any(tokenizer(p)['input_ids']!=ids or ids.count(tokenizer.bos_token_id)!=1 for p,ids in zip(prompts,input_ids)):
        raise ValueError('diagnostic generation must use one BOS and audited input tokens')
    responses={}
    for batch in (1,4):
        raw=generate_free(tokenizer,model,prompts,config['max_new_tokens'],batch,
                          stop_at_blank_line=config['protocol']=='short_answer_prefill_v2')
        responses[str(batch)]=[dict(row,raw_response=text,prediction=parse_answer(text),
                                    correct=parse_answer(text)==row['expected_answer'],input_token_ids=ids)
                               for row,text,ids in zip(selected,raw,input_ids)]
        print(f'interface check batch={batch}; {len(raw)} responses',flush=True)
    complete=len(responses)==2
    result={'complete':complete,'model_experiment':True,'protocol':config['protocol'],
            'selection':'eight fixed primitive cases plus first four training neutral primary IDs; no outcomes used for selection',
            'responses_by_batch_size':responses,'heldout_outcomes_opened':False,
            'actual_model_dtype':str(next(model.parameters()).dtype),
            'actual_device':str(model.device),
            'device_name':torch.cuda.get_device_name() if config['device']=='cuda' else 'cpu',
            'gpu_peak_bytes':torch.cuda.max_memory_allocated() if config['device']=='cuda' else None}
    if complete:
        result['batch_exact_response_matches']=sum(a['raw_response']==b['raw_response'] for a,b in zip(responses['1'],responses['4']))
        result['cases']=len(selected)
        result['primitive_correct_by_batch']={b:sum(r['correct'] for r in rows if r['kind']=='primitive') for b,rows in responses.items()}
        result['training_correct_by_batch']={b:sum(r['correct'] for r in rows if r['kind']=='discovery_training') for b,rows in responses.items()}
    write_json(out/'responses.json',result)
    finish(out,manifest,time.monotonic()-started,'complete' if complete else 'budget_limited',
           samples_completed=sum(len(r) for r in responses.values()),samples_planned=2*len(selected))
    return result
