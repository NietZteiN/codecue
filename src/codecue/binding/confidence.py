"""Label-free next-token confidence at exact, previously audited prompt IDs.

Only scalar distribution summaries are exported. This never generates an answer,
reads target model outcomes, or pretends next-token confidence is complete-answer
confidence. The preparation contract is separate from any future fitted model.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager, nullcontext
import fcntl
import importlib.metadata
import json
import math
import os
from pathlib import Path
import time
import uuid

from .datasets import digest, read_jsonl, write_json
from .published_benchmarks import immutable, sha
from .registry import code_identity, guarded

ROLE='discovery_prefill_confidence_v1'
MEASUREMENT='exact_saved_prompt_next_token_distribution_v1'
STATISTICS=('entropy_nats','maximum_next_token_probability','top_two_logit_margin',
            'eos_probability_mass','vocabulary_size')
CASE_FIELDS=('id','base_id','template_id','split','condition','lexical_realization',
             'available_bindings','updates','tail_placement','query_role')
ROW_FIELDS=set(CASE_FIELDS)|{'prompt_sha256','input_token_ids_sha256','measurement_role',*STATISTICS}
IDENTITY_FIELDS=('model','model_revision','tokenizer_revision','dtype','protocol','tokenization_mode','eos_token_ids')


def _atomic(path,content):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=content:raise ValueError('immutable confidence artifact differs: '+str(path))
        return
    temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temporary.open('xb') as stream:
            stream.write(content);stream.flush();os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary.exists():temporary.unlink()


def _json(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def _source(config):
    from .forecasting import _discovery_declaration, _discovery_response_path
    _discovery_declaration(config)
    for key in ('prepared_cases','preflight_result','run_dir'):_discovery_response_path(config[key])
    path=Path(config['source_config'])
    _discovery_response_path(path)
    if not config.get('source_config_sha256') or sha(path)!=config['source_config_sha256']:
        raise ValueError('pin the original discovery configuration before confidence preparation')
    source=json.loads(path.read_text());_discovery_declaration(source)
    if any(config.get(key)!=source.get(key) for key in IDENTITY_FIELDS):
        raise ValueError('confidence checkpoint/tokenizer/protocol identity differs from source')
    if config.get('dataset')!=source.get('dataset'):
        raise ValueError('confidence registry dataset must match the source discovery bank')
    eos=config.get('eos_token_ids')
    if (not isinstance(eos,list) or any(type(value) is not int or value<0 for value in eos)
            or len(set(eos))!=len(eos)):
        raise ValueError('declare unique nonnegative integer EOS IDs')
    batch=config.get('batch_size',32)
    if type(batch) is not int or batch<1:raise ValueError('positive confidence batch_size required')
    if config.get('attention_backend','sdpa') not in ('eager','sdpa'):
        raise ValueError('confidence supports declared eager or sdpa attention only')
    limit=config.get('case_limit')
    if limit is not None and (type(limit) is not int or limit<1):
        raise ValueError('case_limit is a positive, hash-selected software-smoke count')
    if type(config.get('selection_seed',117)) is not int:raise ValueError('integer selection seed required')
    return source


def select_cases(cases,config):
    """Strip oracle/response fields rather than forwarding source records."""
    from .competition import ROLE as SOURCE_ROLE
    selected=[];seen=set()
    for case in cases:
        record=case['record']
        if (case.get('kind')!='competition' or record.get('evaluation_role')!=SOURCE_ROLE
                or record.get('split') not in ('train','development')):
            raise ValueError('only declared competition discovery inputs may be prepared')
        if record.get('family')!='versions' or record.get('condition') not in ('informative','misleading'):
            continue
        if case['id']!=record['id'] or case['id'] in seen:
            raise ValueError('duplicate or mismatched confidence source identities')
        seen.add(case['id'])
        ids=case['input_token_ids'];prompt=case['prompt']
        if (not isinstance(prompt,str) or not prompt or not ids
                or any(type(token) is not int or token<0 for token in ids) or digest(prompt)!=case['prompt_sha256']):
            raise ValueError('saved confidence prompt or exact token IDs differ')
        item={key:record[key] for key in CASE_FIELDS}
        item.update(prompt=prompt,input_token_ids=list(ids),prompt_sha256=case['prompt_sha256'],
                    input_token_ids_sha256=digest(ids),evaluation_role=ROLE)
        selected.append(item)
    if not selected:raise ValueError('nonneutral version-discovery inputs required')
    limit=config.get('case_limit')
    if limit is not None:
        if limit>len(selected):raise ValueError('smoke count exceeds the complete eligible confidence bank')
        selected=sorted(selected,key=lambda item:(digest([config.get('selection_seed',117),item['id']]),item['id']))[:limit]
    return sorted(selected,key=lambda item:item['id'])


def prepare(config):
    source=_source(config)
    from .discovery_features import _source_inputs
    # This guard reads source programs, saved preparation and audit METADATA.
    # It deliberately does not call checkpoint_suite.audit or read responses.
    _,manifest,cases,provenance=_source_inputs(dict(source_config=config['source_config'],
        source_config_sha256=config['source_config_sha256'],model=source['model'],model_revision=source['model_revision']))
    selected=select_cases(cases,config);path=Path(config['prepared_cases'])
    immutable(path,''.join(json.dumps(item,sort_keys=True)+'\n' for item in selected).encode())
    result=dict(status='passed',evaluation_role=ROLE,measurement=MEASUREMENT,cases=len(selected),
        config_hash=digest(config),source_sha256=code_identity()['source_sha256'],
        source_config_sha256=config['source_config_sha256'],
        prepared_cases_sha256=sha(path),case_ids_sha256=digest([item['id'] for item in selected]),
        padded_width=max(len(item['input_token_ids']) for item in selected),
        model=source['model'],model_revision=source['model_revision'],tokenizer_revision=source['tokenizer_revision'],
        eos_token_ids=config['eos_token_ids'],upstream_identity=manifest['identity_hash'],
        conditions=dict(Counter(item['condition'] for item in selected)),
        original_splits=dict(Counter(item['split'] for item in selected)),
        smoke_subset=config.get('case_limit') is not None,selection='fixed hash of selection_seed and case ID, no outcomes',
        source_provenance=provenance,generated_holdouts_opened=False,target_outcomes_read=False,
        generated_tokens=0,oracle_fields_exported=False,
        limitation='Next-token sign/format confidence at the exact saved prompt; not full integer-answer confidence. '
                   'A new Transformers measurement backend is distinct from the original vLLM outcome backend.')
    immutable(config['preflight_result'],_json(result))
    return result


def inputs(config,expected_source=None):
    _source(config)
    qa=json.loads(Path(config['preflight_result']).read_text())
    if (qa.get('status')!='passed' or qa.get('evaluation_role')!=ROLE or qa.get('measurement')!=MEASUREMENT
            or qa.get('config_hash')!=digest(config)
            or qa.get('source_config_sha256')!=config['source_config_sha256']
            or qa.get('source_sha256')!=(expected_source or code_identity()['source_sha256'])
            or any(qa.get(key)!=config[key] for key in ('model','model_revision','tokenizer_revision','eos_token_ids'))
            or qa.get('prepared_cases_sha256')!=sha(config['prepared_cases'])):
        raise ValueError('confidence requires matching frozen preparation and exact prompt IDs')
    cases=read_jsonl(config['prepared_cases'])
    allowed=set(CASE_FIELDS)|{'prompt','input_token_ids','prompt_sha256','input_token_ids_sha256','evaluation_role'}
    if (not cases or len(cases)!=qa['cases'] or len({item['id'] for item in cases})!=len(cases)
            or digest([item['id'] for item in cases])!=qa['case_ids_sha256']):
        raise ValueError('prepared confidence coverage differs')
    for item in cases:
        if (set(item)!=allowed or item['evaluation_role']!=ROLE or item['split'] not in ('train','development')
                or item['condition'] not in ('informative','misleading')
                or not isinstance(item['prompt'],str) or not item['prompt']
                or digest(item['prompt'])!=item['prompt_sha256']
                or not item['input_token_ids']
                or any(type(token) is not int or token<0 for token in item['input_token_ids'])
                or digest(item['input_token_ids'])!=item['input_token_ids_sha256']):
            raise ValueError('prepared confidence schema, access role or prompt identity differs')
    if max(len(item['input_token_ids']) for item in cases)!=qa['padded_width']:
        raise ValueError('prepared confidence padding geometry differs')
    return qa,cases


def next_token_statistics(logits,eos_token_ids):
    """Stable scalar summaries; argmax token identities are never returned."""
    import torch
    if (not isinstance(logits,torch.Tensor) or logits.ndim!=2 or logits.shape[0]<1 or logits.shape[1]<2
            or not torch.isfinite(logits).all()):
        raise ValueError('finite batch-by-vocabulary logits with at least two tokens required')
    eos=list(eos_token_ids);vocabulary=logits.shape[1]
    if any(type(value) is not int or not 0<=value<vocabulary for value in eos) or len(set(eos))!=len(eos):
        raise ValueError('EOS IDs must be unique members of the model vocabulary')
    logp=torch.log_softmax(logits.float(),dim=-1);p=logp.exp()
    # The masked product handles underflowed zero probabilities without 0*(-inf).
    entropy=-torch.where(p>0,p*logp,torch.zeros_like(p)).sum(-1)
    largest=torch.topk(logits.float(),2,dim=-1).values
    margin=largest[:,0].double()-largest[:,1].double()
    eos_mass=p[:,eos].sum(-1).clamp(0,1) if eos else torch.zeros_like(entropy)
    result=[]
    for values in zip(entropy.clamp_min(0).tolist(),p.max(-1).values.tolist(),margin.tolist(),eos_mass.tolist()):
        row=dict(zip(STATISTICS[:-1],values));row['vocabulary_size']=int(vocabulary)
        validate_statistics(row);result.append(row)
    return result


def validate_statistics(row):
    vocabulary=row['vocabulary_size']
    if type(vocabulary) is not int or vocabulary<2:raise ValueError('invalid confidence vocabulary size')
    if any(isinstance(row[key],bool) or not isinstance(row[key],(int,float)) or not math.isfinite(row[key]) for key in STATISTICS[:-1]):
        raise ValueError('confidence scalar must be finite')
    if (not 0<=row['entropy_nats']<=math.log(vocabulary)+1e-5
            or not 0<row['maximum_next_token_probability']<=1
            or row['top_two_logit_margin']<0 or not 0<=row['eos_probability_mass']<=1):
        raise ValueError('confidence scalar outside its mathematical range')


def validate_rows(cases,rows):
    if len(cases)!=len(rows):raise ValueError('confidence batch coverage differs')
    for case,row in zip(cases,rows):
        if (set(row)!=ROW_FIELDS or row['measurement_role']!=ROLE
                or any(row[key]!=case[key] for key in CASE_FIELDS)
                or row['prompt_sha256']!=case['prompt_sha256']
                or row['input_token_ids_sha256']!=case['input_token_ids_sha256']):
            raise ValueError('confidence scalar row schema or exact prompt identity differs')
        validate_statistics(row)


def measure_batch(tokenizer,model,cases,padded_width,eos_token_ids):
    import torch
    from .value_transfer import _encode
    encoded=_encode(tokenizer,cases,model.device,padded_width)
    with torch.inference_mode():
        output=model(**encoded,use_cache=False,logits_to_keep=1)
        logits=output.logits
        if logits.ndim!=3 or logits.shape[0]!=len(cases) or logits.shape[1]!=1:
            raise ValueError('model must return one final-position distribution per case')
        statistics=next_token_statistics(logits[:,-1],eos_token_ids)
    rows=[]
    for case,values in zip(cases,statistics):
        rows.append({**{key:case[key] for key in CASE_FIELDS},'measurement_role':ROLE,
            'prompt_sha256':case['prompt_sha256'],'input_token_ids_sha256':case['input_token_ids_sha256'],**values})
    validate_rows(cases,rows);return rows


@contextmanager
def _run_lock(out):
    out.mkdir(parents=True,exist_ok=True)
    with (out/'.run.lock').open('a') as stream:
        try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise RuntimeError('a confidence worker already owns this run directory') from exc
        try:yield
        finally:fcntl.flock(stream,fcntl.LOCK_UN)


def _chunks(config,qa,cases,out):
    batch=config.get('batch_size',32);folder=out/'chunks';folder.mkdir(exist_ok=True)
    expected={f'{start:08d}.json' for start in range(0,len(cases),batch)}
    if any(path.name not in expected for path in folder.glob('*.json')):
        raise ValueError('unexpected confidence chunk identity')
    rows=[];pending=[];gap=False
    for start in range(0,len(cases),batch):
        part=cases[start:start+batch];path=folder/f'{start:08d}.json'
        if not path.exists():gap=True;pending.append((start,part,path));continue
        if gap:raise ValueError('confidence chunks are not a contiguous completed prefix')
        data=json.loads(path.read_text())
        if (data.get('config_hash')!=digest(config) or data.get('prepared_cases_sha256')!=qa['prepared_cases_sha256']
                or data.get('start')!=start or data.get('measurement')!=MEASUREMENT):
            raise ValueError('confidence chunk configuration/input identity differs')
        validate_rows(part,data['rows']);rows.extend(data['rows'])
    return rows,pending


@guarded
def run(config):
    qa,cases=inputs(config);out=Path(config['run_dir'])/'confidence'
    with _run_lock(out):
        from .registry import begin,finish
        out,manifest=begin(config,'confidence',reuse_complete=True)
        rows,pending=_chunks(config,qa,cases,out)
        if manifest['status']=='complete':
            audit(config)
            return json.loads((out/'summary.json').read_text())
        started=time.monotonic();load_seconds=0.;gpu=None;resumed_cases=len(rows)
        if pending:
            from .model_adapter import load
            before=time.monotonic();tokenizer,model=load(config)
            backend=config.get('attention_backend','sdpa')
            if hasattr(model,'set_attn_implementation'):model.set_attn_implementation(backend)
            elif backend!='eager':raise ValueError('model cannot select the registered attention backend')
            load_seconds=time.monotonic()-before
            is_cuda=str(config['device']).startswith('cuda')
            if is_cuda:
                from .gpu_telemetry import UUIDMonitor
                context=UUIDMonitor()
            else:context=nullcontext(None)
            with context as monitor:
                for start,part,path in pending:
                    block=measure_batch(tokenizer,model,part,qa['padded_width'],config['eos_token_ids'])
                    _atomic(path,_json({'config_hash':digest(config),'prepared_cases_sha256':qa['prepared_cases_sha256'],
                        'measurement':MEASUREMENT,'start':start,'rows':block}))
                    rows.extend(block)
                    write_json(out/'progress.json',dict(status='running',evaluated=len(rows),planned=len(cases),
                        complete=False,generated_tokens=0,target_outcomes_read=False))
            if monitor is not None:gpu=monitor.summary()
        validate_rows(cases,rows)
        payload=''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows).encode();path=out/'confidence.jsonl'
        _atomic(path,payload)
        runtime=dict(status='recorded',load_seconds=load_seconds,batch_size=config.get('batch_size',32),
            padded_width=qa['padded_width'],attention_backend=config.get('attention_backend','sdpa'),
            device=config['device'],dtype=config['dtype'],gpu=gpu,
            resumed_cases=resumed_cases,measured_this_attempt=len(rows)-resumed_cases,
            gpu_scope='current attempt only; committed earlier chunks are reused',
            versions={name:importlib.metadata.version(name) for name in ('torch','transformers')})
        write_json(out/'runtime.json',runtime)
        summary=dict(status='complete',complete=True,evaluated=len(rows),planned=len(cases),
            measurement=MEASUREMENT,evaluation_role=ROLE,confidence_sha256=sha(path),
            prepared_cases_sha256=qa['prepared_cases_sha256'],case_ids_sha256=qa['case_ids_sha256'],
            statistics=list(STATISTICS),model=config['model'],model_revision=config['model_revision'],
            batch_size=config.get('batch_size',32),attention_backend=config.get('attention_backend','sdpa'),
            load_seconds=load_seconds,wall_seconds=time.monotonic()-started,gpu=gpu,
            resumed_cases=resumed_cases,measured_this_attempt=len(rows)-resumed_cases,
            gpu_scope='current attempt only; committed earlier chunks are reused',
            generated_tokens=0,target_prefill_evaluations=len(rows),target_outcomes_read=False,
            generated_holdouts_opened=False,oracle_fields_exported=False,smoke_subset=qa['smoke_subset'],
            limitation=qa['limitation'])
        write_json(out/'summary.json',summary)
        finish(out,manifest,time.monotonic()-started,confidence_sha256=sha(path),evaluated=len(rows),planned=len(cases))
        return summary


def audit(config):
    _source(config)
    out=Path(config['run_dir'])/'confidence';manifest=json.loads((out/'manifest.json').read_text())
    identity=manifest.get('identity',{})
    if (manifest.get('status')!='complete' or manifest.get('identity_hash')!=digest(identity)
            or identity.get('config')!=config):
        raise ValueError('complete matching confidence run required')
    qa,cases=inputs(config,identity['code']['source_sha256']);rows=read_jsonl(out/'confidence.jsonl')
    validate_rows(cases,rows);chunk_rows,pending=_chunks(config,qa,cases,out)
    if pending or chunk_rows!=rows:raise ValueError('confidence chunks and final scalar records differ')
    summary=json.loads((out/'summary.json').read_text())
    if (not summary.get('complete') or summary.get('status')!='complete'
            or summary.get('evaluated')!=len(cases) or summary.get('planned')!=len(cases)
            or summary.get('measurement')!=MEASUREMENT or summary.get('evaluation_role')!=ROLE
            or summary.get('statistics')!=list(STATISTICS)
            or summary.get('model')!=config['model'] or summary.get('model_revision')!=config['model_revision']
            or summary.get('batch_size')!=config.get('batch_size',32)
            or summary.get('attention_backend')!=config.get('attention_backend','sdpa')
            or summary.get('smoke_subset')!=qa['smoke_subset']
            or summary.get('target_prefill_evaluations')!=len(cases)
            or type(summary.get('resumed_cases')) is not int or type(summary.get('measured_this_attempt')) is not int
            or not 0<=summary['resumed_cases']<=len(cases)
            or summary['measured_this_attempt']!=len(cases)-summary['resumed_cases']
            or summary.get('confidence_sha256')!=sha(out/'confidence.jsonl')
            or manifest.get('confidence_sha256')!=summary['confidence_sha256']
            or summary.get('prepared_cases_sha256')!=qa['prepared_cases_sha256']
            or summary.get('case_ids_sha256')!=qa['case_ids_sha256']
            or summary.get('target_outcomes_read') is not False or summary.get('generated_tokens')!=0
            or summary.get('generated_holdouts_opened') is not False or summary.get('oracle_fields_exported') is not False):
        raise ValueError('confidence summary/hash/access contract differs')
    runtime=json.loads((out/'runtime.json').read_text())
    if (runtime.get('status')!='recorded' or runtime.get('padded_width')!=qa['padded_width']
            or any(runtime.get(key)!=config[key] for key in ('device','dtype'))
            or any(runtime.get(key)!=summary[key] for key in
                   ('batch_size','attention_backend','load_seconds','gpu','resumed_cases','measured_this_attempt','gpu_scope'))):
        raise ValueError('confidence runtime provenance differs')
    result=dict(status='passed',complete=True,evaluated=len(rows),model=config['model'],
        model_revision=config['model_revision'],identity_hash=manifest['identity_hash'],
        confidence_sha256=sha(out/'confidence.jsonl'),preparation=qa,measurement=MEASUREMENT,
        generated_tokens=0,target_outcomes_read=False,generated_holdouts_opened=False,
        audit_scope='schema, numerical ranges, exact input identities, complete chunk/record coverage; no outcome scoring')
    immutable(out/'audit.json',_json(result));return result
