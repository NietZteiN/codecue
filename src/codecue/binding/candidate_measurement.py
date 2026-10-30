"""Audited exact-prefix integer/EOS preparation and scalar-only collection.

Real tokenizer/model loading belongs in scheduled jobs. No upstream model
responses or scalar payloads are read by this runner, and it never generates.
"""
from __future__ import annotations

from collections import Counter
from contextlib import nullcontext
import importlib.metadata
import json
import math
from pathlib import Path
import time

from . import candidate_confidence as event
from . import confidence
from .confidence import CASE_FIELDS,IDENTITY_FIELDS,_atomic,_json,_run_lock
from .datasets import digest,read_jsonl,write_json
from .published_benchmarks import immutable,sha
from .registry import code_identity,guarded

ROLE='discovery_candidate_event_measurement_v1'
MEASUREMENT=event.MEASUREMENT
SOURCE_CASES=6144
SCALARS=('support_mass','support_log_mass','support_conditional_entropy_nats',
    'support_conditional_top_two_probability_margin','support_max_mass','support_conditional_max_probability')
COUNTS=('candidate_count','eos_variant_count','trie_nodes')
ROW_FIELDS=set(CASE_FIELDS)|{'measurement_role','prompt_sha256','input_token_ids_sha256',
    'event_bank_sha256','support_mass_underflowed',*SCALARS,*COUNTS}
PREPARED_FIELDS=set(CASE_FIELDS)|{'evaluation_role','event_bank'}
BACKENDS=('full_prefix_trie','cached_trie')
JOINT_RULE='joint_prompt_candidate_v1'
STANDALONE_RULE='standalone_decode_verified_v2'
TOLERANCE_RULE='max(atol, rtol * max(abs(primary), abs(reference))); Python math.isclose'


def _rule(config):
    rule=config.get('tokenization_rule',JOINT_RULE)
    if rule not in (JOINT_RULE,STANDALONE_RULE):raise ValueError('unsupported explicit candidate tokenization_rule')
    return rule


def _precision(config):
    dtype=config.get('measurement_dtype',config['dtype'])
    if dtype not in ('bfloat16','float32'):raise ValueError('measurement_dtype must be bfloat16 or float32')
    return dict(source_dtype=config['dtype'],measurement_dtype=dtype,
        tf32_policy='disabled_highest_float32' if dtype=='float32' else 'unchanged_bfloat16')


def _apply_precision(config):
    import torch
    precision=_precision(config)
    if precision['measurement_dtype']=='float32':
        torch.set_float32_matmul_precision('highest')
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
    return dict(float32_matmul_precision=torch.get_float32_matmul_precision(),
        cuda_matmul_allow_tf32=bool(torch.backends.cuda.matmul.allow_tf32),
        cudnn_allow_tf32=bool(torch.backends.cudnn.allow_tf32))


def _check_precision(config,record,*,loaded):
    expected=_precision(config)
    if (any(record.get(key)!=value for key,value in expected.items())
            or record.get('actual_model_dtype')!=(expected['measurement_dtype'] if loaded else None)
            or record.get('actual_model_dtype_verified') is not loaded):
        raise ValueError('candidate source/measurement/actual dtype contract differs')
    if loaded:
        settings=record.get('tf32_settings',{})
        if (set(settings)!={'float32_matmul_precision','cuda_matmul_allow_tf32','cudnn_allow_tf32'}
                or settings['float32_matmul_precision'] not in ('highest','high','medium')
                or type(settings['cuda_matmul_allow_tf32']) is not bool or type(settings['cudnn_allow_tf32']) is not bool
                or (expected['measurement_dtype']=='float32' and settings!=dict(float32_matmul_precision='highest',
                    cuda_matmul_allow_tf32=False,cudnn_allow_tf32=False))):
            raise ValueError('candidate TF32 enforcement differs from declared precision')


def _metadata(config):
    """Complete metadata guards before reading any saved input prompt payload."""
    from .forecasting import _discovery_declaration,_discovery_response_path
    _discovery_declaration(config)
    if config.get('evaluation_role',ROLE)!=ROLE:raise ValueError('candidate measurement discovery role required')
    for key in ('source_confidence_config','candidate_declaration','prepared_events','preparation_review','run_dir'):
        _discovery_response_path(config[key])
    for key in ('source_confidence_config','candidate_declaration'):
        path=Path(config[key])
        if path.suffix!='.json' or not path.is_file() or path.stat().st_size>8*1024**2:
            raise ValueError('bounded JSON configuration metadata required before payload access')
        if not config.get(key+'_sha256') or sha(config[key])!=config[key+'_sha256']:
            raise ValueError('pin matching '+key+' metadata before candidate preparation')
    source=json.loads(Path(config['source_confidence_config']).read_text())
    declaration=json.loads(Path(config['candidate_declaration']).read_text())
    _discovery_declaration(source);confidence._source(source)
    candidates,eos=event.declaration(declaration)
    rule=_rule(config);_precision(config)
    if declaration.get('tokenization_rule',JOINT_RULE)!=rule:
        raise ValueError('candidate declaration tokenization_rule differs from measurement')
    if (any(config.get(key)!=source.get(key) for key in IDENTITY_FIELDS)
            or config.get('dataset')!=source.get('dataset') or eos!=config.get('eos_token_ids')):
        raise ValueError('candidate checkpoint/tokenizer/dataset/EOS identity differs from source')
    if source.get('case_limit') is not None:raise ValueError('complete unselected confidence source bank required')
    if config.get('scoring_backend') not in BACKENDS:raise ValueError('declare an explicit supported scoring_backend')
    if config.get('attention_backend','sdpa') not in ('eager','sdpa'):raise ValueError('declare eager or sdpa attention')
    for key,default in (('batch_size',32),('event_batch_size',128),('prompt_batch_size',4),('max_active_nodes',2048)):
        if type(config.get(key,default)) is not int or config.get(key,default)<1:raise ValueError('positive '+key+' required')
    limit=config.get('case_limit')
    if limit is not None and (type(limit) is not int or not 1<=limit<=SOURCE_CASES):raise ValueError('invalid fixed hash smoke case_limit')
    if type(config.get('selection_seed',117)) is not int:raise ValueError('integer hash selection_seed required')
    if type(config.get('parity_check',False)) is not bool:raise ValueError('parity_check must be boolean')
    for key,default in (('parity_atol',1e-4),('parity_rtol',1e-3)):
        value=config.get(key,default)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
            raise ValueError('finite nonnegative '+key+' required')
    review_path=Path(declaration['output_review']);_discovery_response_path(review_path)
    review=json.loads(review_path.read_text())
    if (review.get('status')!='passed' or review.get('evaluation_role')!=event.ROLE
            or review.get('measurement')!=MEASUREMENT or review.get('config_hash')!=digest(declaration)
            or review.get('candidates')!=candidates or review.get('eos_token_ids')!=eos
            or review.get('terminator')!='eos' or review.get('target_outcomes_read') is not False
            or review.get('tokenization_performed') is not False or review.get('boundary_verified') is not False
            or review.get('tokenization_rule',JOINT_RULE)!=rule
            or review.get('toolkit_sha256')!=sha(event.__file__)):
        raise ValueError('matching declaration-only candidate review required')
    continuation_sha=None
    if rule==STANDALONE_RULE:
        from . import candidate_continuation
        continuation_sha=sha(candidate_continuation.__file__)
        if review.get('continuation_toolkit_sha256')!=continuation_sha:
            raise ValueError('matching standalone continuation toolkit review required')
    stage=Path(source['run_dir'])/'confidence';_discovery_response_path(stage)
    manifest=json.loads((stage/'manifest.json').read_text());identity=manifest.get('identity',{})
    _discovery_declaration(identity)
    source_qa=json.loads(Path(source['preflight_result']).read_text())
    summary=json.loads((stage/'summary.json').read_text());audit=json.loads((stage/'audit.json').read_text())
    from .competition import ROLE as source_role
    dataset_manifest=json.loads(Path(source['dataset']).with_suffix('.manifest.json').read_text())
    _discovery_declaration(dataset_manifest)
    source_code=identity.get('code',{}).get('source_sha256')
    if (manifest.get('status')!='complete' or manifest.get('identity_hash')!=digest(identity)
            or identity.get('config')!=source or not source_code
            or identity.get('model_revision')!=source.get('model_revision')
            or identity.get('tokenizer_revision')!=source.get('tokenizer_revision')
            or identity.get('dataset_manifest')!=dataset_manifest
            or dataset_manifest.get('status')!='validated' or dataset_manifest.get('evaluation_role')!=source_role
            or dataset_manifest.get('sha256')!=source_qa.get('source_provenance',{}).get('source_dataset_sha256')
            or source_qa.get('status')!='passed' or source_qa.get('evaluation_role')!=confidence.ROLE
            or source_qa.get('measurement')!=confidence.MEASUREMENT or source_qa.get('source_sha256')!=source_code
            or source_qa.get('config_hash')!=digest(source) or source_qa.get('cases')!=SOURCE_CASES
            or source_qa.get('smoke_subset') is not False
            or any(source_qa.get(key) is not False for key in
                   ('target_outcomes_read','generated_holdouts_opened','oracle_fields_exported'))
            or source_qa.get('generated_tokens')!=0
            or summary.get('status')!='complete' or summary.get('complete') is not True
            or summary.get('evaluation_role')!=confidence.ROLE or summary.get('measurement')!=confidence.MEASUREMENT
            or summary.get('target_outcomes_read') is not False
            or summary.get('evaluated')!=SOURCE_CASES or summary.get('planned')!=SOURCE_CASES
            or summary.get('prepared_cases_sha256')!=source_qa.get('prepared_cases_sha256')
            or summary.get('case_ids_sha256')!=source_qa.get('case_ids_sha256')
            or summary.get('model')!=source['model'] or summary.get('model_revision')!=source['model_revision']
            or audit.get('status')!='passed' or audit.get('complete') is not True
            or audit.get('identity_hash')!=manifest['identity_hash'] or audit.get('evaluated')!=SOURCE_CASES
            or audit.get('model')!=source['model'] or audit.get('model_revision')!=source['model_revision']
            or audit.get('preparation')!=source_qa or audit.get('target_outcomes_read') is not False
            or audit.get('measurement')!=confidence.MEASUREMENT
            or not manifest.get('confidence_sha256')
            or manifest['confidence_sha256']!=summary.get('confidence_sha256')
            or manifest['confidence_sha256']!=audit.get('confidence_sha256')):
        raise ValueError('complete matching full-bank confidence identity and audit required before input prompts')
    provenance=dict(source_confidence_config_sha256=config['source_confidence_config_sha256'],
        candidate_declaration_sha256=config['candidate_declaration_sha256'],
        candidate_review_sha256=sha(review_path),source_confidence_identity_hash=manifest['identity_hash'],
        source_confidence_code_sha256=source_code,source_confidence_audit_sha256=sha(stage/'audit.json'),
        source_prepared_cases_sha256=source_qa['prepared_cases_sha256'],
        source_case_ids_sha256=source_qa['case_ids_sha256'],tokenization_rule=rule,
        continuation_toolkit_sha256=continuation_sha)
    return source,candidates,eos,provenance


def _source_inputs(config):
    source,candidates,eos,provenance=_metadata(config)
    _,cases=confidence.inputs(source,expected_source=provenance['source_confidence_code_sha256'])
    if len(cases)!=SOURCE_CASES:raise ValueError('complete confidence input bank coverage differs')
    limit=config.get('case_limit')
    if limit is not None:
        cases=sorted(cases,key=lambda item:(digest([config.get('selection_seed',117),item['id']]),item['id']))[:limit]
    return candidates,eos,sorted(cases,key=lambda item:item['id']),provenance


def _load_tokenizer(config):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    tokenizer=AutoTokenizer.from_pretrained(config['model'],revision=config['tokenizer_revision'],local_files_only=True)
    return configure_tokenizer(tokenizer,config)


def _tokenizer_contract(tokenizer,eos):
    size=len(tokenizer);special=set(tokenizer.all_special_ids)
    # HF's role-based special-token map can omit other explicitly marked EOS
    # variants. AddedToken.special is authoritative vocabulary metadata too.
    decoder=getattr(tokenizer,'added_tokens_decoder',{})
    added={token:decoder.get(token) for token in eos}
    special.update(token for token,value in added.items() if getattr(value,'special',False) is True)
    if (type(size) is not int or size<2
            or any(type(token) is not int or not 0<=token<size or token not in special for token in eos)):
        raise ValueError('declared EOS IDs must be in the tokenizer vocabulary and special-token set')
    pad=tokenizer.pad_token_id
    if type(pad) is not int or not 0<=pad<size:raise ValueError('valid configured tokenizer pad token required')
    spellings=tokenizer.convert_ids_to_tokens(eos)
    if len(spellings)!=len(eos) or any(not isinstance(text,str) or not text for text in spellings):
        raise ValueError('declared EOS tokens require explicit vocabulary spellings')
    if any(getattr(added[token],'special',False) is True and getattr(added[token],'content',None)!=text
           for token,text in zip(eos,spellings)):
        raise ValueError('declared EOS spelling differs from authoritative added-token metadata')
    reverse=getattr(tokenizer,'convert_tokens_to_ids',None)
    if callable(reverse) and reverse(spellings)!=list(eos):
        raise ValueError('declared EOS vocabulary spellings do not round-trip to their IDs')
    return dict(vocabulary_size=size,pad_token_id=pad,eos_token_spellings=spellings)


def trie(bank):
    """Every proper event prefix maps to its distinct outgoing token edges."""
    event.validate_bank(bank);nodes={}
    for item in bank['events']:
        sequence=item['event_token_ids']
        for index,token in enumerate(sequence):nodes.setdefault(tuple(sequence[:index]),set()).add(token)
    return {prefix:tuple(sorted(nodes[prefix])) for prefix in sorted(nodes,key=lambda value:(len(value),value))}


def prepare(config):
    candidates,eos,cases,provenance=_source_inputs(config)
    base=dict(evaluation_role=ROLE,measurement=MEASUREMENT,config_hash=digest(config),
        source_sha256=code_identity()['source_sha256'],provenance=provenance,
        model=config['model'],model_revision=config['model_revision'],tokenizer_revision=config['tokenizer_revision'],
        candidates=candidates,eos_token_ids=eos,source_cases=SOURCE_CASES,smoke_subset=config.get('case_limit') is not None,
        generated_tokens=0,target_outcomes_read=False,upstream_scalar_payloads_read=False,
        oracle_fields_exported=False,generated_holdouts_opened=False,limitation=event.LIMITATION,
        tokenization_rule=_rule(config),**_precision(config),actual_model_dtype=None,
        actual_model_dtype_verified=False,parity_tolerance_rule=TOLERANCE_RULE)
    prepared=[];current=None
    try:
        tokenizer=_load_tokenizer(config);vocabulary=_tokenizer_contract(tokenizer,eos)
        build_events=event.build_events
        if _rule(config)==STANDALONE_RULE:
            from .candidate_continuation import build_events
        for case in cases:
            current=case['id']
            bank=build_events(tokenizer,case['prompt'],case['input_token_ids'],candidates,eos)
            if any(token>=vocabulary['vocabulary_size'] for token in bank['input_token_ids']
                   +[token for item in bank['events'] for token in item['event_token_ids']]):
                raise ValueError('prepared prompt/event IDs exceed pinned tokenizer vocabulary')
            prepared.append({**{key:case[key] for key in CASE_FIELDS},'evaluation_role':ROLE,'event_bank':bank})
    except Exception as exc:
        failed=dict(base,status='failed',complete=False,boundary_verified=False,failed_case=current,
            cases_checked=len(prepared),error=f'{type(exc).__name__}: {exc}',
            boundary_policy='Exact saved prefix required; no newline, whitespace repair or prompt rewrite is permitted.')
        immutable(config['preparation_review'],_json(failed));raise
    payload=''.join(json.dumps(item,sort_keys=True)+'\n' for item in prepared).encode()
    _atomic(config['prepared_events'],payload)
    nodes=[len(trie(case['event_bank'])) for case in prepared]
    result=dict(base,status='passed',complete=True,cases=len(prepared),boundary_verified=True,
        prepared_events_sha256=sha(config['prepared_events']),case_ids_sha256=digest([case['id'] for case in prepared]),
        event_banks_sha256=digest([case['event_bank']['bank_sha256'] for case in prepared]),
        tokenizer=vocabulary,trie_nodes=dict(Counter(nodes)),prefix_node_evaluations=sum(nodes),
        candidate_count=len(candidates),eos_variant_count=len(eos),
        prefix_free=True,tokenizer_loaded=True,model_loaded=False)
    immutable(config['preparation_review'],_json(result));return result


def inputs(config,expected_source=None):
    candidates,eos,sources,provenance=_source_inputs(config)
    qa=json.loads(Path(config['preparation_review']).read_text())
    _check_precision(config,qa,loaded=False)
    if (qa.get('status')!='passed' or qa.get('complete') is not True or qa.get('evaluation_role')!=ROLE
            or qa.get('measurement')!=MEASUREMENT or qa.get('config_hash')!=digest(config)
            or qa.get('source_sha256')!=(expected_source or code_identity()['source_sha256'])
            or qa.get('provenance')!=provenance or qa.get('candidates')!=candidates or qa.get('eos_token_ids')!=eos
            or any(qa.get(key)!=config[key] for key in ('model','model_revision','tokenizer_revision'))
            or qa.get('source_cases')!=SOURCE_CASES or qa.get('smoke_subset')!=(config.get('case_limit') is not None)
            or qa.get('tokenization_rule')!=_rule(config) or qa.get('parity_tolerance_rule')!=TOLERANCE_RULE
            or qa.get('candidate_count')!=len(candidates) or qa.get('eos_variant_count')!=len(eos)
            or qa.get('generated_tokens')!=0 or any(qa.get(key) is not False for key in
                ('target_outcomes_read','upstream_scalar_payloads_read','oracle_fields_exported','generated_holdouts_opened'))
            or qa.get('boundary_verified') is not True or qa.get('prefix_free') is not True
            or qa.get('prepared_events_sha256')!=sha(config['prepared_events'])):
        raise ValueError('matching immutable candidate preparation and provenance required')
    vocabulary=qa.get('tokenizer',{})
    if (type(vocabulary.get('vocabulary_size')) is not int or vocabulary['vocabulary_size']<2
            or type(vocabulary.get('pad_token_id')) is not int
            or not 0<=vocabulary['pad_token_id']<vocabulary['vocabulary_size']
            or len(vocabulary.get('eos_token_spellings',[]))!=len(eos)):
        raise ValueError('prepared tokenizer vocabulary contract differs')
    cases=read_jsonl(config['prepared_events'])
    if (len(cases)!=len(sources) or qa.get('cases')!=len(cases)
            or qa.get('case_ids_sha256')!=digest([case['id'] for case in cases])
            or qa.get('event_banks_sha256')!=digest([case['event_bank']['bank_sha256'] for case in cases])):
        raise ValueError('candidate event preparation coverage differs')
    for case,source in zip(cases,sources):
        bank=event.validate_bank(case['event_bank'])
        if (set(case)!=PREPARED_FIELDS or case['evaluation_role']!=ROLE
                or any(case[key]!=source[key] for key in CASE_FIELDS)
                or bank['candidates']!=candidates or bank['eos_token_ids']!=eos
                or bank['prompt_sha256']!=source['prompt_sha256']
                or bank['input_token_ids_sha256']!=source['input_token_ids_sha256']
                or bank['input_token_ids']!=source['input_token_ids']):
            raise ValueError('prepared candidate bank differs from exact permitted source input')
        if any(token>=qa['tokenizer']['vocabulary_size'] for token in bank['input_token_ids']
               +[token for item in bank['events'] for token in item['event_token_ids']]):
            raise ValueError('prepared candidate vocabulary geometry differs')
    if sum(len(trie(case['event_bank'])) for case in cases)!=qa['prefix_node_evaluations']:
        raise ValueError('prepared candidate trie coverage differs')
    return qa,cases


def score_banks(model,banks,*,event_batch_size=128,pad_token_id=0):
    """Reference trie scorer: one full causal prefill per distinct token prefix.

    EOS variants and shared partial continuations reuse their node distribution.
    All distinct nodes are independently batched; KV caching is deliberately off.
    """
    import torch
    if type(event_batch_size) is not int or event_batch_size<1:raise ValueError('positive event_batch_size required')
    if type(pad_token_id) is not int or pad_token_id<0:raise ValueError('valid pad token ID required')
    if getattr(model,'training',False):raise ValueError('candidate model must be in evaluation mode')
    plans=[trie(bank) for bank in banks];tables=[{} for bank in banks]
    jobs=[(index,prefix,targets,bank['input_token_ids']+list(prefix))
          for index,(bank,plan) in enumerate(zip(banks,plans)) for prefix,targets in plan.items()]
    jobs.sort(key=lambda job:(len(job[3]),job[0],len(job[1]),job[1]));calls=0
    with torch.inference_mode():
        for start in range(0,len(jobs),event_batch_size):
            block=jobs[start:start+event_batch_size];width=max(len(job[3]) for job in block)
            encoded=dict(input_ids=torch.tensor([[pad_token_id]*(width-len(job[3]))+job[3] for job in block],
                dtype=torch.long,device=model.device),attention_mask=torch.tensor(
                    [[0]*(width-len(job[3]))+[1]*len(job[3]) for job in block],dtype=torch.long,device=model.device))
            positions=encoded['attention_mask'].cumsum(-1)-1
            encoded['position_ids']=positions.masked_fill(encoded['attention_mask']==0,1)
            logits=model(**encoded,use_cache=False,logits_to_keep=1).logits;calls+=1
            if logits.ndim!=3 or logits.shape[:2]!=(len(block),1) or logits.shape[-1]<2:
                raise ValueError('trie scorer requires one final-position distribution per node')
            selected=logits[:,-1].float()
            if (torch.isnan(selected).any() or torch.isposinf(selected).any()
                    or not torch.isfinite(selected).any(-1).all()
                    or any(token>=selected.shape[-1] for job in block for token in job[2])):
                raise ValueError('valid node probability distributions and vocabulary IDs required')
            logp=selected.log_softmax(-1);degree=max(len(job[2]) for job in block)
            targets=torch.tensor([list(job[2])+[0]*(degree-len(job[2])) for job in block],
                dtype=torch.long,device=logits.device)
            values=logp.gather(1,targets).cpu().tolist()
            for job,row in zip(block,values):
                index,prefix,tokens,_=job
                tables[index][prefix]={token:float(value) for token,value in zip(tokens,row)}
    result=[]
    for bank,plan,table in zip(banks,plans,tables):
        values=[]
        for item in bank['events']:
            sequence=item['event_token_ids']
            values.append(math.fsum(table[tuple(sequence[:index])][token] for index,token in enumerate(sequence)))
        summary=event.summarize_events(bank,values)
        summary.update(scoring_backend='full_prefix_trie',trie_node_evaluations=len(plan),
            forward_calls=calls,counter_scope='whole score_banks call',use_cache=False)
        result.append(summary)
    return result


def _backend(model,banks,config,pad_token_id,name):
    if name=='full_prefix_trie':
        scores=score_banks(model,banks,event_batch_size=config.get('event_batch_size',128),pad_token_id=pad_token_id)
        expected='full_prefix_trie';cache=False
    elif name=='cached_trie':
        from .candidate_cache import score_banks as cached
        scores=cached(model,banks,prompt_batch_size=config.get('prompt_batch_size',4),pad_token_id=pad_token_id,
            max_active_nodes=config.get('max_active_nodes',2048))
        expected='cached_prefix_trie_v1';cache=True
    else:raise ValueError('unsupported candidate scoring backend')
    if any(score.get('scoring_backend')!=expected or score.get('use_cache') is not cache for score in scores):
        raise ValueError('candidate backend silently changed its declared execution contract')
    return scores


def scalar_rows(cases,scores):
    if len(cases)!=len(scores):raise ValueError('candidate scorer case coverage differs')
    rows=[]
    for case,score in zip(cases,scores):
        bank=case['event_bank']
        if (score.get('status')!='scored' or score.get('measurement')!=MEASUREMENT
                or score.get('bank_sha256')!=bank['bank_sha256'] or score.get('evaluation_role')!=event.ROLE
                or score.get('generated_tokens')!=0 or score.get('target_outcomes_read') is not False
                or score.get('oracle_fields_read') is not False
                or [item['candidate'] for item in score.get('candidates',[])]!=bank['candidates']):
            raise ValueError('candidate score/input/access identity differs')
        row={**{key:case[key] for key in CASE_FIELDS},'measurement_role':ROLE,
            'prompt_sha256':bank['prompt_sha256'],'input_token_ids_sha256':bank['input_token_ids_sha256'],
            'event_bank_sha256':bank['bank_sha256'],**{key:score[key] for key in SCALARS[:4]},
            'support_max_mass':max(item['absolute_event_mass'] for item in score['candidates']),
            'support_conditional_max_probability':max(item['support_conditional_probability'] for item in score['candidates']),
            'support_mass_underflowed':score['support_mass_underflowed'],'candidate_count':len(bank['candidates']),
            'eos_variant_count':len(bank['eos_token_ids']),'trie_nodes':len(trie(bank))}
        rows.append(row)
    validate_rows(cases,rows);return rows


def validate_rows(cases,rows):
    if len(cases)!=len(rows):raise ValueError('candidate scalar coverage differs')
    for case,row in zip(cases,rows):
        bank=case['event_bank']
        if (set(row)!=ROW_FIELDS or row.get('measurement_role')!=ROLE
                or any(row[key]!=case[key] for key in CASE_FIELDS)
                or row['prompt_sha256']!=bank['prompt_sha256']
                or row['input_token_ids_sha256']!=bank['input_token_ids_sha256']
                or row['event_bank_sha256']!=bank['bank_sha256']
                or any(type(row[key]) is not int or row[key]<1 for key in COUNTS)
                or row['candidate_count']!=len(bank['candidates']) or row['eos_variant_count']!=len(bank['eos_token_ids'])
                or row['trie_nodes']!=len(trie(bank))):raise ValueError('candidate scalar schema/input/count identity differs')
        if any(isinstance(row[key],bool) or not isinstance(row[key],(int,float)) or not math.isfinite(row[key]) for key in SCALARS):
            raise ValueError('candidate summary scalars must be finite')
        if (not 0<=row['support_mass']<=1 or row['support_log_mass']>0
                or not math.isclose(row['support_mass'],math.exp(row['support_log_mass']),rel_tol=1e-6,abs_tol=1e-12)
                or type(row['support_mass_underflowed']) is not bool
                or row['support_mass_underflowed']!=(row['support_mass']==0)
                or not 0<=row['support_max_mass']<=row['support_mass']+event.MASS_TOLERANCE
                or not 1/row['candidate_count']-1e-6<=row['support_conditional_max_probability']<=1+event.MASS_TOLERANCE
                or not 0<=row['support_conditional_entropy_nats']<=math.log(row['candidate_count'])+1e-5
                or not 0<=row['support_conditional_top_two_probability_margin']<=row['support_conditional_max_probability']+1e-6):
            raise ValueError('candidate scalar outside its mathematical domain')
        if row['support_mass']>1e-300 and not math.isclose(row['support_max_mass']/row['support_mass'],
                row['support_conditional_max_probability'],rel_tol=2e-6,abs_tol=1e-7):
            raise ValueError('absolute and support-conditional maximum masses differ')


def _forward_calls(scores):
    groups={}
    for score in scores:
        key=score.get('prompt_batch_index',0)
        counters={field:score[field] for field in ('forward_calls','root_prefill_calls','continuation_forward_calls') if field in score}
        if key in groups and groups[key]!=counters:raise ValueError('inconsistent shared backend execution counters')
        groups[key]=counters
    return sum(group.get('forward_calls',0) for group in groups.values())


def _empty_parity():
    return dict(status='not_requested',cases=0,max_absolute_error={key:0. for key in SCALARS},
        max_scalar_tolerance_utilization={key:0. for key in SCALARS},tolerance_rule=TOLERANCE_RULE,
        scope='per-event identity, log probability and mass plus exported scalar summaries',event_variants=0,
        max_event_log_probability_absolute_error=0.,max_event_mass_absolute_error=0.,max_event_tolerance_utilization=0.)


def measure_cases(model,cases,config,pad_token_id):
    banks=[case['event_bank'] for case in cases];name=config['scoring_backend']
    scores=_backend(model,banks,config,pad_token_id,name);rows=scalar_rows(cases,scores)
    execution=dict(scoring_backend=name,cases=len(cases),prefix_nodes=sum(row['trie_nodes'] for row in rows),
        naive_event_variants=sum(len(bank['events']) for bank in banks),
        forward_calls=_forward_calls(scores),parity_reference_forward_calls=0,parity=_empty_parity())
    if config.get('parity_check',False):
        other='cached_trie' if name=='full_prefix_trie' else 'full_prefix_trie'
        reference_scores=_backend(model,banks,config,pad_token_id,other)
        reference=scalar_rows(cases,reference_scores);errors={key:0. for key in SCALARS}
        execution['parity_reference_forward_calls']=_forward_calls(reference_scores)
        parity=_empty_parity();atol=config.get('parity_atol',1e-4);rtol=config.get('parity_rtol',1e-3)
        for primary,alternative in zip(rows,reference):
            for key in SCALARS:
                distance=abs(primary[key]-alternative[key]);errors[key]=max(errors[key],distance)
                if not math.isclose(primary[key],alternative[key],abs_tol=config.get('parity_atol',1e-4),rel_tol=config.get('parity_rtol',1e-3)):
                    raise ValueError('candidate backend parity failed for '+key+' at case '+primary['id'])
                tolerance=max(atol,rtol*max(abs(primary[key]),abs(alternative[key])))
                utilization=distance/tolerance if tolerance else 0.
                parity['max_scalar_tolerance_utilization'][key]=max(parity['max_scalar_tolerance_utilization'][key],utilization)
        for bank,primary,alternative in zip(banks,scores,reference_scores):
            expected=bank['events'];left=primary.get('event_variants',[]);right=alternative.get('event_variants',[])
            if len(left)!=len(expected) or len(right)!=len(expected):raise ValueError('candidate per-event parity coverage differs')
            for specification,one,two in zip(expected,left,right):
                if any(one.get(key)!=specification[key] or two.get(key)!=specification[key]
                       for key in ('candidate','eos_token_id','event_token_ids')):
                    raise ValueError('candidate per-event parity identity/order differs')
                for key,target in (('log_probability','max_event_log_probability_absolute_error'),
                                   ('absolute_event_mass','max_event_mass_absolute_error')):
                    a,b=one[key],two[key]
                    if a==b:distance=0.
                    elif not math.isfinite(a) or not math.isfinite(b):raise ValueError('candidate per-event parity finite support differs')
                    else:distance=abs(a-b)
                    if not math.isclose(a,b,abs_tol=atol,rel_tol=rtol):raise ValueError('candidate per-event parity failed for '+key)
                    parity[target]=max(parity[target],distance)
                    tolerance=max(atol,rtol*max(abs(a),abs(b))) if math.isfinite(a) and math.isfinite(b) else math.inf
                    utilization=distance/tolerance if tolerance else 0.
                    parity['max_event_tolerance_utilization']=max(parity['max_event_tolerance_utilization'],utilization)
                parity['event_variants']+=1
        parity.update(status='passed',cases=len(cases),reference_backend=other,max_absolute_error=errors,atol=atol,rtol=rtol)
        execution['parity']=parity
    return rows,execution


def _chunks(config,qa,cases,out):
    folder=out/'chunks';folder.mkdir(exist_ok=True);batch=config.get('batch_size',32)
    expected={f'{start:08d}.json' for start in range(0,len(cases),batch)}
    if any(path.name not in expected for path in folder.glob('*.json')):raise ValueError('unexpected candidate chunk identity')
    rows=[];pending=[];executions=[];gap=False
    for start in range(0,len(cases),batch):
        part=cases[start:start+batch];path=folder/f'{start:08d}.json'
        if not path.exists():gap=True;pending.append((start,part,path));continue
        if gap:raise ValueError('candidate chunks must form a contiguous completed prefix')
        chunk=json.loads(path.read_text())
        if (chunk.get('config_hash')!=digest(config) or chunk.get('prepared_events_sha256')!=qa['prepared_events_sha256']
                or chunk.get('measurement')!=MEASUREMENT or chunk.get('start')!=start):raise ValueError('candidate chunk provenance differs')
        validate_rows(part,chunk['rows']);execution=chunk['execution'];parity=execution.get('parity',{})
        _check_precision(config,execution.get('precision',{}),loaded=True)
        if (execution.get('scoring_backend')!=config['scoring_backend'] or execution.get('cases')!=len(part)
                or execution.get('prefix_nodes')!=sum(row['trie_nodes'] for row in chunk['rows'])
                or execution.get('naive_event_variants')!=sum(len(case['event_bank']['events']) for case in part)
                or type(execution.get('forward_calls')) is not int or execution['forward_calls']<1
                or type(execution.get('parity_reference_forward_calls')) is not int
                or execution['parity_reference_forward_calls']<int(config.get('parity_check',False))
                or parity.get('status')!=('passed' if config.get('parity_check',False) else 'not_requested')
                or parity.get('cases')!=(len(part) if config.get('parity_check',False) else 0)
                or set(parity.get('max_absolute_error',{}))!=set(SCALARS)
                or any(not isinstance(value,(int,float)) or not math.isfinite(value) or value<0
                       for value in parity['max_absolute_error'].values())):
            raise ValueError('candidate execution/parity chunk contract differs')
        if (parity.get('scope')!=_empty_parity()['scope']
                or parity.get('tolerance_rule')!=TOLERANCE_RULE
                or set(parity.get('max_scalar_tolerance_utilization',{}))!=set(SCALARS)
                or any(isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)
                       or not 0<=value<=1+1e-12 for value in parity.get('max_scalar_tolerance_utilization',{}).values())
                or parity.get('event_variants')!=(execution['naive_event_variants'] if config.get('parity_check',False) else 0)
                or any(isinstance(parity.get(key),bool) or not isinstance(parity.get(key),(int,float))
                    or not math.isfinite(parity[key]) or parity[key]<0 for key in
                    ('max_event_log_probability_absolute_error','max_event_mass_absolute_error','max_event_tolerance_utilization'))
                or parity['max_event_tolerance_utilization']>1+1e-12):
            raise ValueError('candidate per-event parity audit contract differs')
        if config.get('parity_check',False):
            other='cached_trie' if config['scoring_backend']=='full_prefix_trie' else 'full_prefix_trie'
            if (parity.get('reference_backend')!=other or parity.get('atol')!=config.get('parity_atol',1e-4)
                    or parity.get('rtol')!=config.get('parity_rtol',1e-3)):
                raise ValueError('candidate parity backend/tolerance declaration differs')
            for key,error in parity['max_absolute_error'].items():
                upper=max(config.get('parity_atol',1e-4),config.get('parity_rtol',1e-3)*(max(abs(row[key]) for row in chunk['rows'])+error))
                if error>upper+1e-12:raise ValueError('saved candidate parity error exceeds declared tolerance')
        elif (any(parity['max_absolute_error'].values()) or any(parity['max_scalar_tolerance_utilization'].values())
                or execution['parity_reference_forward_calls']
                or any(parity[key] for key in ('max_event_log_probability_absolute_error',
                    'max_event_mass_absolute_error','max_event_tolerance_utilization'))):
            raise ValueError('unrequested candidate parity has nonzero errors')
        rows.extend(chunk['rows']);executions.append(execution)
    return rows,pending,executions


def _parity_summary(config,executions,count):
    result=_empty_parity()
    result.update(status='passed' if config.get('parity_check',False) else 'not_requested',
        cases=count if config.get('parity_check',False) else 0,
        max_absolute_error={key:max(item['parity']['max_absolute_error'][key] for item in executions) for key in SCALARS},
        max_scalar_tolerance_utilization={key:max(item['parity']['max_scalar_tolerance_utilization'][key]
            for item in executions) for key in SCALARS},
        event_variants=sum(item['parity']['event_variants'] for item in executions))
    for key in ('max_event_log_probability_absolute_error','max_event_mass_absolute_error','max_event_tolerance_utilization'):
        result[key]=max(item['parity'][key] for item in executions)
    if config.get('parity_check',False):
        result.update(atol=config.get('parity_atol',1e-4),rtol=config.get('parity_rtol',1e-3),
            reference_backend='cached_trie' if config['scoring_backend']=='full_prefix_trie' else 'full_prefix_trie')
    return result


@guarded
def run(config):
    qa,cases=inputs(config);out=Path(config['run_dir'])/'candidate_measurement'
    with _run_lock(out):
        from .registry import begin,finish
        out,manifest=begin(config,'candidate_measurement',reuse_complete=True)
        rows,pending,executions=_chunks(config,qa,cases,out)
        if manifest['status']=='complete':audit(config);return json.loads((out/'summary.json').read_text())
        started=time.monotonic();resumed=len(rows);load_seconds=0.;gpu=None
        precision=dict(_precision(config),tf32_settings=_apply_precision(config))
        precision.update(actual_model_dtype=precision['measurement_dtype'],actual_model_dtype_verified=True)
        if pending:
            from .model_adapter import load
            load_config=dict(config,dtype=precision['measurement_dtype'])
            before=time.monotonic();tokenizer,model=load(load_config)
            actual_dtype=str(getattr(model,'dtype',None)).removeprefix('torch.')
            if actual_dtype!=precision['measurement_dtype']:
                raise ValueError('loaded model actual dtype differs from declared measurement_dtype')
            precision['actual_model_dtype']=actual_dtype
            _check_precision(config,precision,loaded=True)
            if _tokenizer_contract(tokenizer,config['eos_token_ids'])!=qa['tokenizer']:
                raise ValueError('loaded tokenizer vocabulary/EOS/pad identity differs from preparation')
            backend=config.get('attention_backend','sdpa')
            if hasattr(model,'set_attn_implementation'):model.set_attn_implementation(backend)
            elif backend!='eager':raise ValueError('model cannot select declared attention backend')
            load_seconds=time.monotonic()-before
            if str(config['device']).startswith('cuda'):
                from .gpu_telemetry import UUIDMonitor
                context=UUIDMonitor()
            else:context=nullcontext(None)
            with context as monitor:
                for start,part,path in pending:
                    block,execution=measure_cases(model,part,config,qa['tokenizer']['pad_token_id'])
                    execution['precision']=dict(precision)
                    _atomic(path,_json(dict(config_hash=digest(config),prepared_events_sha256=qa['prepared_events_sha256'],
                        measurement=MEASUREMENT,start=start,rows=block,execution=execution)))
                    rows.extend(block);executions.append(execution)
                    write_json(out/'progress.json',dict(status='running',complete=False,evaluated=len(rows),planned=len(cases),
                        generated_tokens=0,target_outcomes_read=False,scoring_backend=config['scoring_backend']))
            if monitor is not None:gpu=monitor.summary()
        validate_rows(cases,rows);path=out/'scalars.jsonl'
        _atomic(path,''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows).encode())
        parity=_parity_summary(config,executions,len(rows))
        runtime=dict(status='recorded',scoring_backend=config['scoring_backend'],attention_backend=config.get('attention_backend','sdpa'),
            batch_size=config.get('batch_size',32),event_batch_size=config.get('event_batch_size',128),
            prompt_batch_size=config.get('prompt_batch_size',4),max_active_nodes=config.get('max_active_nodes',2048),
            device=config['device'],dtype=precision['actual_model_dtype'],load_seconds=load_seconds,gpu=gpu,
            **precision,tokenization_rule=_rule(config),
            resumed_cases=resumed,measured_this_attempt=len(rows)-resumed,gpu_scope='current attempt only',
            versions={name:importlib.metadata.version(name) for name in ('torch','transformers')})
        write_json(out/'runtime.json',runtime)
        summary=dict(runtime,status='complete',complete=True,evaluated=len(rows),planned=len(cases),evaluation_role=ROLE,
            measurement=MEASUREMENT,scalar_sha256=sha(path),prepared_events_sha256=qa['prepared_events_sha256'],
            case_ids_sha256=qa['case_ids_sha256'],event_banks_sha256=qa['event_banks_sha256'],
            model=config['model'],model_revision=config['model_revision'],statistics=list(SCALARS),
            generated_tokens=0,target_outcomes_read=False,upstream_scalar_payloads_read=False,oracle_fields_exported=False,
            generated_holdouts_opened=False,smoke_subset=qa['smoke_subset'],limitation=event.LIMITATION,
            prefix_node_evaluations=sum(item['prefix_nodes'] for item in executions),
            backend_forward_calls=sum(item['forward_calls'] for item in executions),parity=parity,
            parity_reference_forward_calls=sum(item['parity_reference_forward_calls'] for item in executions),
            wall_seconds=time.monotonic()-started)
        write_json(out/'summary.json',summary)
        finish(out,manifest,time.monotonic()-started,scalar_sha256=sha(path),evaluated=len(rows),planned=len(cases))
        return summary


def audit(config):
    _metadata(config);out=Path(config['run_dir'])/'candidate_measurement'
    manifest=json.loads((out/'manifest.json').read_text());identity=manifest.get('identity',{})
    if (manifest.get('status')!='complete' or manifest.get('identity_hash')!=digest(identity)
            or identity.get('config')!=config):raise ValueError('complete matching candidate measurement required')
    qa,cases=inputs(config,expected_source=identity['code']['source_sha256']);rows=read_jsonl(out/'scalars.jsonl')
    validate_rows(cases,rows);chunk_rows,pending,executions=_chunks(config,qa,cases,out)
    if pending or rows!=chunk_rows:raise ValueError('candidate chunks/final scalar coverage differs')
    summary=json.loads((out/'summary.json').read_text());runtime=json.loads((out/'runtime.json').read_text())
    runtime_fields={'status','scoring_backend','attention_backend','batch_size','event_batch_size','prompt_batch_size',
        'max_active_nodes','device','dtype','load_seconds','gpu','resumed_cases','measured_this_attempt','gpu_scope','versions',
        'source_dtype','measurement_dtype','actual_model_dtype','actual_model_dtype_verified','tf32_policy','tf32_settings',
        'tokenization_rule'}
    _check_precision(config,runtime,loaded=True)
    if (set(runtime)!=runtime_fields or runtime.get('status')!='recorded'
            or any(runtime.get(key)!=config[key] for key in ('device','scoring_backend'))
            or runtime.get('dtype')!=_precision(config)['measurement_dtype'] or runtime.get('tokenization_rule')!=_rule(config)
            or any(runtime.get(key)!=config.get(key,default) for key,default in
                (('batch_size',32),('event_batch_size',128),('prompt_batch_size',4),('max_active_nodes',2048)))
            or isinstance(runtime.get('load_seconds'),bool) or not isinstance(runtime.get('load_seconds'),(int,float))
            or not math.isfinite(runtime['load_seconds']) or runtime['load_seconds']<0):
        raise ValueError('candidate runtime/configuration provenance differs')
    if (summary.get('status')!='complete' or summary.get('complete') is not True or summary.get('evaluation_role')!=ROLE
            or summary.get('measurement')!=MEASUREMENT or summary.get('evaluated')!=len(cases) or summary.get('planned')!=len(cases)
            or summary.get('scalar_sha256')!=sha(out/'scalars.jsonl') or summary['scalar_sha256']!=manifest.get('scalar_sha256')
            or any(summary.get(key)!=qa[key] for key in ('prepared_events_sha256','case_ids_sha256','event_banks_sha256','smoke_subset'))
            or summary.get('model')!=config['model'] or summary.get('model_revision')!=config['model_revision']
            or summary.get('statistics')!=list(SCALARS) or summary.get('scoring_backend')!=config['scoring_backend']
            or summary.get('attention_backend')!=config.get('attention_backend','sdpa')
            or summary.get('prefix_node_evaluations')!=sum(item['prefix_nodes'] for item in executions)
            or summary.get('backend_forward_calls')!=sum(item['forward_calls'] for item in executions)
            or summary.get('parity_reference_forward_calls')!=sum(item['parity_reference_forward_calls'] for item in executions)
            or summary.get('generated_tokens')!=0
            or any(summary.get(key) is not False for key in
                   ('target_outcomes_read','upstream_scalar_payloads_read','oracle_fields_exported','generated_holdouts_opened'))
            or type(summary.get('resumed_cases')) is not int or not 0<=summary['resumed_cases']<=len(cases)
            or type(summary.get('measured_this_attempt')) is not int
            or summary.get('measured_this_attempt')!=len(cases)-summary['resumed_cases']
            or any(runtime.get(key)!=summary.get(key) for key in runtime if key!='status')):
        raise ValueError('candidate summary/runtime/hash/access contract differs')
    expected_parity=_parity_summary(config,executions,len(rows))
    if summary.get('parity')!=expected_parity:raise ValueError('candidate parity summary differs')
    result=dict(status='passed',complete=True,evaluated=len(rows),model=config['model'],model_revision=config['model_revision'],
        identity_hash=manifest['identity_hash'],scalar_sha256=sha(out/'scalars.jsonl'),preparation=qa,measurement=MEASUREMENT,
        generated_tokens=0,target_outcomes_read=False,upstream_scalar_payloads_read=False,
        audit_scope='schema, finite numerical domains, exact input identities, chunk/record coverage and configured parity; no outcome scoring')
    immutable(out/'audit.json',_json(result));return result
