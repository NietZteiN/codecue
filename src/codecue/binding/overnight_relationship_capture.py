"""Discovery prefill capture for numeric/query/computation relationship cohorts.

No response is generated. Source-only cases, exact tokenizer visibility, durable
attempt counters and immutable chunk pins precede every use of saved features.
Journal updates deliberately do not rebuild the experiment dashboard per batch.
"""
from __future__ import annotations

import ast
from collections import Counter
import hashlib
import io
import json
import math
import os
from pathlib import Path
import tempfile
import time

import numpy as np

from . import relationship_capture as base
from .datasets import digest

ROLE = 'discovery_overnight_relationship_capture_v1'
DATASET_ROLE = 'overnight_relationship_discovery_v1'
SITES = ('statement:3', 'statement:7', 'pre_answer')
INSTRUCTION = base.INSTRUCTION
BACKEND = 'BF16 SDPA decoder-only prefill; left-padding position IDs; no KV cache or generation; one combined selected-tensor CPU transfer'
MAX_JSON = 16 * 1024**2
MAX_PREPARED = 512 * 1024**2
MAX_DATASET = 256 * 1024**2
MAX_ROWS = 25000
PROFILES = {
    'meta-llama/Llama-3.1-8B-Instruct': dict(revision='0e9e39f249a16976918f6564b8830bc894c89659',
        hidden_size=4096, num_hidden_layers=32, layers=[8,16,24,31], batch_size=128,
        tokenization_mode='native', minimum_gpu_bytes=22*1024**3, weight_bytes=16060556376),
    'codellama/CodeLlama-34b-Instruct-hf': dict(revision='d4c1c474abcacd32d2a6eda45f9811d38c83e93d',
        hidden_size=8192, num_hidden_layers=48, layers=[12,24,36,47], batch_size=64,
        tokenization_mode='codellama_official_boundary_v1', minimum_gpu_bytes=72*1024**3, weight_bytes=67487991400),
}
RECORD_FIELDS = ('id','base_id','component_id','cluster_id','template_id','split','condition',
    'lexical_realization','source','canonical_source','rename_map','variable_slots',
    'evaluation_role','family','control_kind','query_role','query_slot','query_count',
    'numeric_seed','numeric_stratum','numeric_draw','source_form','body_id','surface_body_id',
    'format_pair_id','initial_state_id','cohorts')
_safe, _sha, _bytes = base._safe, base._sha, base._bytes


def _json(path, checksum=None):
    data = _bytes(path, MAX_JSON)
    if checksum is not None and hashlib.sha256(data).hexdigest()!=checksum:
        raise ValueError('overnight metadata checksum differs')
    value=json.loads(data)
    if not isinstance(value,dict): raise ValueError('overnight metadata object required')
    return value


def _put(path, value):
    payload=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if len(payload)>MAX_JSON: raise ValueError('bounded overnight metadata required')
    base._publish(path,payload)


def _journal(path,value):
    """Durable atomic mutable journal, with no synchronous dashboard reconciliation."""
    path=_safe(path)
    if path.is_symlink(): raise ValueError('overnight journal must not follow symbolic links')
    data=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if len(data)>MAX_JSON: raise ValueError('bounded overnight journal required')
    path.parent.mkdir(parents=True,exist_ok=True);temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.'+path.name+'.',suffix='.pending',delete=False) as stream:
            temporary=Path(stream.name);stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if temporary is not None and temporary.exists(): temporary.unlink()


def _event(path):
    from .experiment_log import note_artifact
    note_artifact(path)


def _config(config):
    required={'evaluation_role','dataset','dataset_sha256','run_dir','model','model_revision',
        'tokenizer_revision','layers','hidden_size'}
    optional={'dtype','device','tokenization_mode','batch_size','chunk_size','context_limit','prefix_atol'}
    if (not isinstance(config,dict) or config.get('evaluation_role')!=ROLE or required-set(config)
            or set(config)-required-optional or config.get('model') not in PROFILES):
        raise ValueError('explicit supported overnight discovery capture configuration required')
    if len(json.dumps(config,allow_nan=False).encode())>16*1024:
        raise ValueError('bounded overnight configuration required')
    profile=PROFILES[config['model']]
    if (config['model_revision']!=profile['revision'] or config['tokenizer_revision']!=profile['revision']
            or type(config['hidden_size']) is not int or config['hidden_size']!=profile['hidden_size']):
        raise ValueError('cached checkpoint revision or hidden geometry differs')
    layers=config['layers']
    if (not isinstance(layers,list) or not 1<=len(layers)<=8
            or any(type(i) is not int or not 0<=i<profile['num_hidden_layers'] for i in layers)
            or layers!=sorted(set(layers))):
        raise ValueError('ordered unique actual decoder layers required')
    checksum=config['dataset_sha256']
    if not isinstance(checksum,str) or len(checksum)!=64 or any(c not in '0123456789abcdef' for c in checksum):
        raise ValueError('explicit dataset SHA256 required')
    recipe=dict(model=config['model'],model_revision=config['model_revision'],tokenizer_revision=config['tokenizer_revision'],
        layers=layers,hidden_size=config['hidden_size'],num_hidden_layers=profile['num_hidden_layers'],
        dtype='bfloat16',device='cuda',tokenization_mode=profile['tokenization_mode'],
        batch_size=profile['batch_size'],chunk_size=512,context_limit=4096,prefix_atol=1e-5,
        execution_backend=BACKEND)
    for key in optional: recipe[key]=config.get(key,recipe[key])
    if any(recipe[key]!=value for key,value in [('dtype','bfloat16'),('device','cuda'),('tokenization_mode',profile['tokenization_mode'])]):
        raise ValueError('fixed BF16 CUDA/native checkpoint boundary required')
    for key,low,high in [('chunk_size',2,2048),('context_limit',128,4096)]:
        if type(recipe[key]) is not int or not low<=recipe[key]<=high: raise ValueError('bounded strict integer '+key+' required')
    if type(recipe['batch_size']) is not int or not 1<=recipe['batch_size']<=recipe['chunk_size']:
        raise ValueError('positive batch_size no larger than the declared chunk required')
    if (isinstance(recipe['prefix_atol'],bool) or not isinstance(recipe['prefix_atol'],(int,float))
            or not np.isfinite(recipe['prefix_atol']) or not 0<=recipe['prefix_atol']<=1e-3):
        raise ValueError('finite prospective causal-prefix tolerance required')
    dataset,folder=_safe(config['dataset']),_safe(config['run_dir'])
    if dataset.suffix!='.jsonl' or folder.resolve()==dataset.resolve() or folder.resolve() in dataset.resolve().parents:
        raise ValueError('JSONL dataset and separate output directory required')
    if folder.exists() and not folder.is_dir(): raise ValueError('overnight run_dir must be a directory')
    return recipe,folder


def _constant(expr):
    if isinstance(expr,ast.Constant) and type(expr.value) is int: return expr.value
    if isinstance(expr,ast.UnaryOp) and isinstance(expr.op,(ast.UAdd,ast.USub)):
        value=_constant(expr.operand);return value if isinstance(expr.op,ast.UAdd) else -value
    if isinstance(expr,ast.BinOp) and isinstance(expr.op,(ast.Add,ast.Sub)):
        a,b=_constant(expr.left),_constant(expr.right);return a+b if isinstance(expr.op,ast.Add) else a-b
    raise ValueError('roots must be integer literals or independent constant +/- expressions')


def _validate_row(row):
    from .programs import rename
    if (not isinstance(row,dict) or row.get('evaluation_role')!=DATASET_ROLE
            or row.get('split') not in ('train','development') or row.get('condition')!='neutral'):
        raise ValueError('neutral TRAIN/DEV overnight discovery rows required')
    for key in ('id','template_id','source','canonical_source'):
        if not isinstance(row.get(key),str) or not row[key] or len(row[key])>16384: raise ValueError('bounded source identity required')
    if (row.get('query_role') not in ('v0','v1','v2','v3') or type(row.get('query_slot')) is not int
            or row['query_slot']!=int(row['query_role'][1])):
        raise ValueError('explicit v0..v3 query identity required')
    if row.get('variable_slots')!={f'v{i}':i for i in range(4)}: raise ValueError('canonical four-slot map required')
    mapping=row.get('rename_map')
    if not isinstance(mapping,dict) or set(mapping)!=set(row['variable_slots']) or len(set(mapping.values()))!=4:
        raise ValueError('bijective canonical/surface variable names required')
    canonical,surface=ast.parse(row['canonical_source']),ast.parse(row['source'])
    if len(row['source'].splitlines())!=9 or len(canonical.body)!=9:
        raise ValueError('eight single-line assignments plus a query required')
    if ast.dump(ast.parse(rename(row['canonical_source'],mapping)))!=ast.dump(surface):
        raise ValueError('canonical/surface source differs')
    names={f'v{i}' for i in range(4)}
    for i,node in enumerate(canonical.body[:8]):
        if (not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name)
                or node.targets[0].id!=f'v{i%4}'):
            raise ValueError('fixed four-root/four-copy destination schedule required')
        if i<4:
            if not -64<=_constant(node.value)<=64: raise ValueError('visible root value exceeds supported bounds')
        elif not isinstance(node.value,ast.Name) or node.value.id not in names-{f'v{i%4}'}:
            raise ValueError('distinct-slot copy expression required')
    query=canonical.body[-1]
    if not isinstance(query,ast.Expr) or not isinstance(query.value,ast.Name) or query.value.id!=row['query_role']:
        raise ValueError('final query differs from declared slot')


def _record(row):
    return {key:row[key] for key in RECORD_FIELDS if key in row}


def _dataset(config):
    recipe,_=_config(config);path=_safe(config['dataset'])
    manifest=_json(path.with_suffix('.manifest.json'))
    if (manifest.get('status')!='complete' or manifest.get('evaluation_role')!=DATASET_ROLE
            or manifest.get('role')!=DATASET_ROLE or manifest.get('independent_python_passed') is not True
            or manifest.get('sha256')!=config['dataset_sha256'] or manifest.get('generated_holdouts_opened') is not False):
        raise ValueError('complete pinned overnight discovery dataset manifest required')
    payload=_bytes(path,MAX_DATASET)
    if hashlib.sha256(payload).hexdigest()!=config['dataset_sha256']: raise ValueError('overnight dataset checksum differs')
    rows=[json.loads(line) for line in payload.splitlines() if line.strip()]
    if not 1<=len(rows)<=MAX_ROWS or manifest.get('rows')!=len(rows): raise ValueError('bounded complete dataset coverage required')
    seen=set();group_splits={}
    for row in rows:
        _validate_row(row)
        if row['id'] in seen: raise ValueError('duplicate source case identity')
        seen.add(row['id']);group=row['template_id']
        if group in group_splits and group_splits[group]!=row['split']: raise ValueError('structural component crosses splits')
        group_splits[group]=row['split']
    if set(group_splits.values())!={'train','development'}: raise ValueError('both TRAIN and DEV discovery components required')
    review=dict(dataset_sha256=config['dataset_sha256'],dataset_manifest_sha256=_sha(path.with_suffix('.manifest.json')),
        source_rows=len(rows),split_rows=dict(Counter(r['split'] for r in rows)),
        components=dict(Counter(group_splits.values())),query_rows=dict(Counter(r['query_role'] for r in rows)),
        ordered_case_ids_sha256=digest([r['id'] for r in rows]),layers=recipe['layers'],sites=list(SITES),
        feature_shape=[len(rows),3,len(recipe['layers']),recipe['hidden_size']],recipe=recipe)
    return rows,review


def metadata(config):
    _,review=_dataset(config)
    return dict(review,status='passed',evaluation_role=ROLE,config_hash=digest(config),new_model_queries=0,generated_holdouts_opened=False)


def _tokenizer(config):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    recipe,_=_config(config)
    tokenizer=AutoTokenizer.from_pretrained(recipe['model'],revision=recipe['tokenizer_revision'],local_files_only=True,use_fast=True)
    configure_tokenizer(tokenizer,recipe)
    if not tokenizer.is_fast or not tokenizer.chat_template: raise ValueError('cached native fast chat tokenizer required')
    return tokenizer


def layout_case(tokenizer,row,config,index,*,recipe=None):
    from .model_adapter import normalize_prompt
    if recipe is None: recipe,_=_config(config)
    prompt=normalize_prompt(tokenizer,tokenizer.apply_chat_template([{'role':'user','content':INSTRUCTION+'\n\n'+row['source']}],
        tokenize=False,add_generation_prompt=True)+'Output:')
    if prompt.count(row['source'])!=1: raise ValueError('source must occur exactly once in native prompt')
    encoded=tokenizer(prompt,add_special_tokens=False,return_offsets_mapping=True)
    tokens,offsets=encoded['input_ids'],encoded['offset_mapping']
    if (not tokens or len(tokens)!=len(offsets) or len(tokens)>recipe['context_limit']
            or any(type(i) is not int or i<0 for i in tokens)):
        raise ValueError('bounded valid native token layout required')
    start=prompt.index(row['source']);lines=row['source'].splitlines();positions=[];ends=[]
    for statement in (3,7):
        end=start+sum(len(line)+1 for line in lines[:statement])+len(lines[statement].rstrip())
        matches=[i for i,(a,b) in enumerate(offsets) if a<=end-1<b]
        if len(matches)!=1: raise ValueError('checkpoint final character must have exactly one token')
        position=matches[0];stop=offsets[position][1]
        if stop<end or prompt[end:stop].strip(): raise ValueError('checkpoint exposes future code')
        positions.append(position);ends.append(stop)
    positions.append(len(tokens)-1);ends.append(len(prompt))
    if positions!=sorted(set(positions)): raise ValueError('strictly increasing capture positions required')
    prefixes=[tokens[:p+1] for p in positions]
    texts=[tokenizer.decode(p,skip_special_tokens=False,clean_up_tokenization_spaces=False) for p in prefixes]
    if any(text!=prompt[:end] for text,end in zip(texts,ends)): raise ValueError('native token prefix visibility differs')
    first=index//recipe['chunk_size']*recipe['chunk_size']
    return dict(record=_record(row),prompt=prompt,input_token_ids=tokens,token_offsets=[list(pair) for pair in offsets],
        source_start=start,sites=list(SITES),positions=positions,visible_prefixes=texts,prefix_character_ends=ends,
        prefix_token_ids=prefixes,prefix_sha256=[digest(p) for p in prefixes],
        capture_batch_start=first+(index-first)//recipe['batch_size']*recipe['batch_size'],
        batch_padded_width=len(tokens),physical_positions=positions.copy())


def prepare(config):
    recipe,folder=_config(config);base._slurm();source=base._current_source(config)
    rows,review=_dataset(config)
    registration=dict(schema_version=1,evaluation_role=ROLE,config=config,config_hash=digest(config),source=source,
        source_review=review,new_model_queries=0,generated_holdouts_opened=False)
    _put(folder/'registration.json',registration)
    tokenizer=_tokenizer(config)
    cases=[layout_case(tokenizer,row,config,i,recipe=recipe) for i,row in enumerate(rows)]
    base._batch_geometry(cases,assign=True)
    payload=''.join(json.dumps(case,sort_keys=True)+'\n' for case in cases).encode()
    if len(payload)>MAX_PREPARED: raise ValueError('prepared overnight layouts exceed byte bound')
    base._publish(folder/'prepared_cases.jsonl',payload)
    result=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),source=source,
        registration_sha256=_sha(folder/'registration.json'),dataset_sha256=config['dataset_sha256'],cases=len(cases),
        prepared_sha256=hashlib.sha256(payload).hexdigest(),chat_template_sha256=hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        recipe=recipe,source_review=review,new_model_queries=0,generated_holdouts_opened=False)
    _put(folder/'preflight.json',result)
    return result


def _case_check(case,row,recipe,index):
    if case.get('record')!=_record(row) or case.get('sites')!=list(SITES): raise ValueError('prepared overnight row identity differs')
    tokens,offsets,prompt=case['input_token_ids'],case['token_offsets'],case['prompt']
    if (not isinstance(prompt,str) or not prompt.endswith('Output:') or len(prompt)>32768 or not tokens
            or len(tokens)!=len(offsets) or len(tokens)>recipe['context_limit']
            or any(type(i) is not int or i<0 for i in tokens)
            or prompt.count(row['source'])!=1 or case['source_start']!=prompt.index(row['source'])):
        raise ValueError('prepared prompt/token geometry differs')
    positions=case['positions']
    if (len(positions)!=3 or positions!=sorted(set(positions)) or positions[-1]!=len(tokens)-1
            or any(type(p) is not int or not 0<=p<len(tokens) for p in positions)
            or any(len(case[k])!=3 for k in ('visible_prefixes','prefix_character_ends','prefix_token_ids','prefix_sha256'))):
        raise ValueError('prepared overnight checkpoint coverage differs')
    for pair in offsets:
        if (not isinstance(pair,list) or len(pair)!=2 or any(type(i) is not int for i in pair)
                or not 0<=pair[0]<=pair[1]<=len(prompt)): raise ValueError('bounded token offsets required')
    lines=row['source'].splitlines()
    for j,(position,end,text,prefix,pin) in enumerate(zip(positions,case['prefix_character_ends'],case['visible_prefixes'],case['prefix_token_ids'],case['prefix_sha256'])):
        if (type(end) is not int or text!=prompt[:end] or prefix!=tokens[:position+1] or pin!=digest(prefix)):
            raise ValueError('prepared causal prefix identity differs')
        if j<2:
            statement=(3,7)[j];stop=case['source_start']+sum(len(line)+1 for line in lines[:statement])+len(lines[statement].rstrip())
            a,b=offsets[position]
            if not a<=stop-1<b or b!=end or prompt[stop:b].strip(): raise ValueError('prepared checkpoint exposes future code')
        elif end!=len(prompt): raise ValueError('final checkpoint must observe the full prompt')
    first=index//recipe['chunk_size']*recipe['chunk_size']
    if case['capture_batch_start']!=first+(index-first)//recipe['batch_size']*recipe['batch_size']:
        raise ValueError('prepared batch identity differs')


def inputs(config):
    recipe,folder=_config(config);registration=_json(folder/'registration.json')
    if (registration.get('evaluation_role')!=ROLE or registration.get('config')!=config
            or registration.get('config_hash')!=digest(config) or registration.get('generated_holdouts_opened') is not False):
        raise ValueError('overnight registration identity differs')
    base._verify_source(config,registration['source'])
    rows,review=_dataset(config);preflight=_json(folder/'preflight.json')
    if (registration.get('source_review')!=review or preflight.get('status')!='passed'
            or preflight.get('evaluation_role')!=ROLE or preflight.get('source')!=registration['source']
            or preflight.get('config_hash')!=digest(config) or preflight.get('recipe')!=recipe
            or preflight.get('source_review')!=review or preflight.get('cases')!=len(rows)
            or preflight.get('registration_sha256')!=_sha(folder/'registration.json')
            or preflight.get('dataset_sha256')!=config['dataset_sha256']
            or preflight.get('new_model_queries')!=0 or preflight.get('generated_holdouts_opened') is not False):
        raise ValueError('passing matching overnight preflight required')
    payload=_bytes(folder/'prepared_cases.jsonl',MAX_PREPARED)
    if hashlib.sha256(payload).hexdigest()!=preflight['prepared_sha256']: raise ValueError('prepared overnight layout checksum differs')
    cases=[json.loads(line) for line in payload.splitlines() if line.strip()]
    if len(cases)!=len(rows): raise ValueError('prepared overnight row coverage differs')
    for i,(case,row) in enumerate(zip(cases,rows)): _case_check(case,row,recipe,i)
    base._batch_geometry(cases)
    return preflight,cases


def _prefix_check(features,cases,atol):
    seen={};comparisons=0;maximum=0.
    for i,case in enumerate(cases):
        for site,prefix in enumerate(case['prefix_token_ids']):
            key=(case['capture_batch_start'],len(case['input_token_ids']),case['physical_positions'][site],tuple(prefix))
            if key in seen:
                other,j=seen[key];difference=float(np.max(np.abs(features[i,site]-features[other,j])))
                comparisons+=1;maximum=max(maximum,difference)
                if difference>atol: raise ValueError('identical causal prefixes differ at matching prefill geometry')
            else: seen[key]=(i,site)
    return comparisons,maximum


def validate_chunk(features,cases,config):
    recipe,_=_config(config)
    if (features.dtype!=np.float32 or features.shape!=(len(cases),3,len(recipe['layers']),recipe['hidden_size'])
            or not np.isfinite(features).all()): raise ValueError('overnight capture shape, dtype or finiteness differs')
    return _prefix_check(features,cases,recipe['prefix_atol'])


def load_chunk(entry,cases,config):
    recipe,_=_config(config)
    maximum=len(cases)*3*len(recipe['layers'])*recipe['hidden_size']*4+MAX_JSON+65536
    payload=_bytes(entry['path'],maximum)
    if hashlib.sha256(payload).hexdigest()!=entry['sha256']: raise ValueError('overnight capture chunk checksum differs')
    with np.load(io.BytesIO(payload),allow_pickle=False) as saved:
        if set(saved.files)!={'features','metadata'}: raise ValueError('exact overnight chunk array inventory required')
        metadata=saved['metadata']
        if metadata.dtype!=np.uint8 or metadata.ndim!=1 or metadata.size>MAX_JSON:
            raise ValueError('bounded overnight chunk identities required')
        if json.loads(metadata.tobytes())!=cases: raise ValueError('overnight chunk row identities differ')
        features=saved['features']
    return features,validate_chunk(features,cases,config)


def memory_requirements(config,max_prompt_tokens):
    """Prospective short-prefill headroom uses actual prepared length, never its cap."""
    recipe,_=_config(config);profile=PROFILES[recipe['model']]
    if type(max_prompt_tokens) is not int or not 1<=max_prompt_tokens<=recipe['context_limit']:
        raise ValueError('actual prepared maximum token count required')
    floor,reference=(2,3) if profile['hidden_size']==4096 else (4,8)
    headroom=max(floor,reference*recipe['batch_size']/profile['batch_size']*max_prompt_tokens/512)*1024**3
    return dict(actual_max_prompt_tokens=max_prompt_tokens,weight_bytes=profile['weight_bytes'],
        working_headroom_bytes=math.ceil(headroom),required_free_bytes=profile['weight_bytes']+math.ceil(headroom),
        headroom_scope='Prospective short-prefill working allowance; scales with actual tokens and declared batch, not context_limit.')


def _models(config,*,max_prompt_tokens=None):
    import torch
    from transformers import AutoModelForCausalLM
    recipe,_=_config(config);base._slurm()
    if max_prompt_tokens is None:
        _,cases=inputs(config)
        max_prompt_tokens=max(len(case['input_token_ids']) for case in cases)
    memory=memory_requirements(config,max_prompt_tokens)
    profile=PROFILES[recipe['model']]
    if not torch.cuda.is_available() or torch.cuda.get_device_properties(0).total_memory<profile['minimum_gpu_bytes']:
        raise ValueError('allocated GPU does not meet checkpoint memory requirements')
    free_bytes,_=torch.cuda.mem_get_info()
    if free_bytes<memory['required_free_bytes']:
        raise ValueError(f"allocated GPU has {free_bytes} free bytes, below {memory['required_free_bytes']} required for the declared fixed batch and actual {max_prompt_tokens}-token maximum; no cohort or batch reduction was applied")
    tokenizer=_tokenizer(config)
    model=AutoModelForCausalLM.from_pretrained(recipe['model'],revision=recipe['model_revision'],local_files_only=True,
        dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa')
    model.eval()
    model.overnight_memory_review=dict(memory,observed_free_bytes=free_bytes,
        observed_total_bytes=torch.cuda.get_device_properties(0).total_memory)
    if (model.config.hidden_size!=recipe['hidden_size'] or model.config.num_hidden_layers!=recipe['num_hidden_layers']
            or model.config._attn_implementation!='sdpa' or next(model.parameters()).dtype!=torch.bfloat16):
        raise ValueError('actual overnight checkpoint geometry/dtype/backend differs')
    return tokenizer,model


def load_models(config,*,max_prompt_tokens=None):
    """Load the same cached tokenizer/model for sbatch-only companion assays."""
    return _models(config,max_prompt_tokens=max_prompt_tokens)


def _forward(tokenizer,model,cases,config):
    import torch
    from codecue.patching import decoder_layers
    recipe,_=_config(config)
    encoded=tokenizer([c['prompt'] for c in cases],add_special_tokens=False,padding=True,return_tensors='pt')
    width=encoded.input_ids.shape[1];physical=[]
    for i,case in enumerate(cases):
        mask=encoded.attention_mask[i].bool();padding=width-len(case['input_token_ids'])
        if (encoded.input_ids[i][mask].tolist()!=case['input_token_ids']
                or encoded.attention_mask[i].tolist()!=[0]*padding+[1]*len(case['input_token_ids'])
                or case['batch_padded_width']!=width
                or case['physical_positions']!=[padding+p for p in case['positions']]):
            raise ValueError('actual left-padded overnight inputs differ')
        physical.append(case['physical_positions'])
    encoded=encoded.to(model.device)
    position_ids=encoded.attention_mask.long().cumsum(-1)-1;position_ids.masked_fill_(encoded.attention_mask==0,0)
    positions=torch.tensor(physical,device=model.device);indices=torch.arange(len(cases),device=model.device)[:,None]
    captured={};handles=[];blocks=decoder_layers(model)
    for layer in recipe['layers']:
        def hook(module,args,output,layer=layer):
            hidden=output[0] if isinstance(output,tuple) else output
            if hidden.shape!=(len(cases),width,recipe['hidden_size']) or layer in captured:
                raise ValueError('unexpected overnight decoder hook geometry')
            captured[layer]=hidden[indices,positions].detach()
        handles.append(blocks[layer].register_forward_hook(hook))
    try:
        with torch.inference_mode():
            model.model(**encoded,position_ids=position_ids,use_cache=False,output_hidden_states=False,return_dict=True)
    finally:
        for handle in handles: handle.remove()
    if set(captured)!=set(recipe['layers']): raise ValueError('missing overnight decoder layer')
    # A single combined device-to-host transfer, after the entire prefill.
    features=torch.stack([captured[layer] for layer in recipe['layers']],dim=2).float().cpu().numpy()
    validate_chunk(features,cases,config)
    return features


def _entry(folder,first,rows):
    return dict(path=str(folder/'chunks'/f'{first:06d}.npz'),first=first,rows=rows)


def _identity(config,preflight):
    recipe,_=_config(config)
    return dict(evaluation_role=ROLE,config=config,config_hash=digest(config),source=preflight['source'],
        preflight_sha256=_sha(Path(config['run_dir'])/'preflight.json'),dataset_sha256=config['dataset_sha256'],
        model=recipe['model'],model_revision=recipe['model_revision'],layers=recipe['layers'],sites=list(SITES),
        hidden_size=recipe['hidden_size'],execution_backend=BACKEND,stored_dtype='float32',
        prefix_atol=recipe['prefix_atol'],prefix_check_scope=base.PREFIX_SCOPE,
        generated_responses=0,generation_calls=0,generated_holdouts_opened=False)


def _counts(attempts,cases,entries,recipe):
    return dict(model_prefill_cases=len(cases),model_prefill_cases_attempted=sum(a['prefill_cases_attempted'] for a in attempts),
        prefill_batch_calls=sum(a['prefill_batch_calls'] for a in attempts),
        new_model_queries=sum(a['prefill_cases_attempted'] for a in attempts),
        distinct_committed_prefill_rows=len(cases),committed_batch_groups=sum(math.ceil(e['rows']/recipe['batch_size']) for e in entries),
        model_loaded=any(base._attempt_loaded(a) for a in attempts),generated_responses=0,generation_calls=0)


def _completed_base(config,*,manifest=None,input_data=None):
    recipe,folder=_config(config);preflight,cases=inputs(config) if input_data is None else input_data
    if manifest is None: manifest=_json(folder/'manifest.json')
    if manifest.get('status')!='complete' or manifest.get('identity')!=_identity(config,preflight):
        raise ValueError('complete matching overnight manifest required')
    summary=_json(folder/'summary.json',manifest.get('summary_sha256'));entries=manifest.get('chunks',[])
    expected=[_entry(folder,i,min(recipe['chunk_size'],len(cases)-i)) for i in range(0,len(cases),recipe['chunk_size'])]
    if (len(entries)!=len(expected) or summary.get('chunks')!=entries or summary.get('complete') is not True
            or summary.get('cases')!=len(cases)
            or summary.get('feature_shape')!=[len(cases),3,len(recipe['layers']),recipe['hidden_size']]
            or any(summary.get(k)!=v for k,v in manifest['identity'].items())):
        raise ValueError('complete overnight coverage/identity differs')
    for entry,wanted in zip(entries,expected):
        if (set(entry)!=set(wanted)|{'sha256'} or any(entry.get(k)!=v for k,v in wanted.items())
                or not isinstance(entry['sha256'],str) or len(entry['sha256'])!=64):
            raise ValueError('canonical overnight chunk inventory required')
    attempts=manifest.get('attempts',[])
    if (not attempts or attempts[-1].get('status')!='complete'
            or any(not isinstance(a,dict) or a.get('status') not in ('complete','failed','interrupted')
                or any(type(a.get(k)) is not int or a[k]<0 for k in ('prefill_batch_calls','prefill_cases_attempted','prefill_cases_returned'))
                or a['prefill_cases_returned']>a['prefill_cases_attempted']
                or not a['prefill_batch_calls']<=a['prefill_cases_attempted']<=a['prefill_batch_calls']*recipe['batch_size'] for a in attempts)):
        raise ValueError('overnight attempt accounting differs')
    counts=_counts(attempts,cases,entries,recipe)
    if (summary.get('collection_attempts')!=attempts or not counts['model_loaded']
            or counts['model_prefill_cases_attempted']<len(cases) or counts['prefill_batch_calls']<counts['committed_batch_groups']
            or any(summary.get(k)!=v or manifest.get(k)!=v for k,v in counts.items())):
        raise ValueError('completed overnight counters differ')
    if {p.resolve() for p in (folder/'chunks').iterdir()}!={Path(e['path']).resolve() for e in entries}:
        raise ValueError('overnight chunk directory inventory differs')
    return folder,preflight,cases,manifest,summary


def _recover_summary(config,previous,identity,input_data):
    folder=Path(config['run_dir']);summary=_json(folder/'summary.json')
    candidate=dict(previous,status='complete',identity=identity,chunks=summary.get('chunks'),
        attempts=summary.get('collection_attempts'),summary_sha256=_sha(folder/'summary.json'))
    recipe,_=_config(config)
    candidate.update(_counts(candidate['attempts'],input_data[1],candidate['chunks'],recipe))
    _,_,cases,_,_=_completed_base(config,manifest=candidate,input_data=input_data)
    for entry in candidate['chunks']:load_chunk(entry,cases[entry['first']:entry['first']+entry['rows']],config)
    candidate.pop('error',None);_journal(folder/'manifest.json',candidate);_event(folder/'manifest.json')
    return summary


def run(config):
    import fcntl
    recipe,folder=_config(config);base._slurm();source=base._current_source(config)
    preflight,cases=inputs(config)
    if source!=preflight['source']: raise ValueError('running source differs from prepared overnight source')
    identity=_identity(config,preflight);manifest_path=folder/'manifest.json'
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'capture.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise ValueError('another overnight capture owns this run') from exc
        previous=_json(manifest_path) if manifest_path.exists() else dict(identity=identity,attempts=[])
        if previous.get('identity')!=identity: raise ValueError('overnight resume identity differs')
        if previous.get('status')=='complete':return _completed_base(config,input_data=(preflight,cases))[-1]
        if (folder/'summary.json').exists():return _recover_summary(config,previous,identity,(preflight,cases))
        for attempt in previous['attempts']:
            if attempt.get('status') is None:attempt.update(status='interrupted',completion_observation='Durable counters retained after an interrupted worker.')
        manifest=dict(previous,status='started',attempts=[*previous['attempts'],dict(slurm_job_id=os.environ['SLURM_JOB_ID'],
            model_loaded=False,prefill_batch_calls=0,prefill_cases_attempted=0,prefill_cases_returned=0)])
        manifest.pop('error',None);_journal(manifest_path,manifest);_event(manifest_path)
        started=time.monotonic()
        try:
            (folder/'chunks').mkdir(exist_ok=True)
            expected_names={f'{first:06d}.npz' for first in range(0,len(cases),recipe['chunk_size'])}
            pending_names={'.'+name+'.pending' for name in expected_names}
            if any(p.name not in expected_names|pending_names for p in (folder/'chunks').iterdir()):
                raise ValueError('unexpected overnight chunk artifact')
            for p in (folder/'chunks').iterdir():
                if p.name in pending_names:p.unlink()
            pins={}
            for entry in previous.get('chunks',[]):
                first=entry['first'];wanted=_entry(folder,first,min(recipe['chunk_size'],len(cases)-first))
                if (first in pins or first not in range(0,len(cases),recipe['chunk_size']) or set(entry)!=set(wanted)|{'sha256'}
                        or any(entry.get(k)!=v for k,v in wanted.items()) or not isinstance(entry['sha256'],str) or len(entry['sha256'])!=64):
                    raise ValueError('partial overnight checksum inventory differs')
                pins[first]=entry
            entries=[];pending=[];comparisons=0;maximum=0.;padding_comparisons=0;padding_maximum=0.
            for first in range(0,len(cases),recipe['chunk_size']):
                selected=cases[first:first+recipe['chunk_size']];entry=_entry(folder,first,len(selected))
                if Path(entry['path']).exists():
                    if first not in pins:raise ValueError('committed overnight chunk lacks durable checksum pin')
                    entry=pins[first];features,(checks,difference)=load_chunk(entry,selected,config)
                    comparisons+=checks;maximum=max(maximum,difference)
                    checks,difference=base._padding_diagnostics(features,selected)
                    padding_comparisons+=checks;padding_maximum=max(padding_maximum,difference);entries.append(entry)
                else:pending.append((first,selected))
            if pending:
                manifest['attempts'][-1]['model_load_attempted']=True;_journal(manifest_path,manifest)
                tokenizer,model=_models(config,max_prompt_tokens=max(len(c['input_token_ids']) for c in cases))
                manifest['attempts'][-1]['model_loaded']=True;_journal(manifest_path,manifest)
                if hashlib.sha256(tokenizer.chat_template.encode()).hexdigest()!=preflight['chat_template_sha256']:
                    raise ValueError('runtime overnight tokenizer template differs')
                with base._monitor() as monitor:
                    try:
                        for first,selected in pending:
                            batches=[]
                            for offset in range(0,len(selected),recipe['batch_size']):
                                batch=selected[offset:offset+recipe['batch_size']];attempt=manifest['attempts'][-1]
                                attempt['prefill_batch_calls']+=1;attempt['prefill_cases_attempted']+=len(batch)
                                _journal(manifest_path,manifest)
                                batches.append(_forward(tokenizer,model,batch,config));attempt['prefill_cases_returned']+=len(batch)
                            features=np.concatenate(batches);checks,difference=validate_chunk(features,selected,config)
                            comparisons+=checks;maximum=max(maximum,difference)
                            checks,difference=base._padding_diagnostics(features,selected)
                            padding_comparisons+=checks;padding_maximum=max(padding_maximum,difference)
                            stream=io.BytesIO();metadata=np.frombuffer(json.dumps(selected,sort_keys=True).encode(),dtype=np.uint8)
                            if metadata.size>MAX_JSON:raise ValueError('bounded chunk metadata required')
                            np.savez(stream,features=features,metadata=metadata);payload=stream.getvalue()
                            entry=dict(_entry(folder,first,len(selected)),sha256=hashlib.sha256(payload).hexdigest())
                            pins[first]=entry;manifest['chunks']=[pins[i] for i in sorted(pins)]
                            _journal(manifest_path,manifest)  # Durable expected SHA BEFORE chunk publication.
                            base._commit_chunk(Path(entry['path']),payload);entries.append(entry)
                            _journal(folder/'progress.json',dict(complete=False,captured_rows=sum(e['rows'] for e in entries),planned=len(cases)))
                            print(f'overnight capture {sum(e["rows"] for e in entries)}/{len(cases)}',flush=True)
                    finally:manifest['attempts'][-1]['runtime']=dict(base._runtime(model),gpu=monitor.summary(),
                        preload_memory=getattr(model,'overnight_memory_review',None))
            entries.sort(key=lambda entry:entry['first']);manifest['attempts'][-1].update(status='complete',wall_seconds=time.monotonic()-started)
            counts=_counts(manifest['attempts'],cases,entries,recipe)
            summary=dict(identity,complete=True,cases=len(cases),feature_shape=[len(cases),3,len(recipe['layers']),recipe['hidden_size']],
                chunks=entries,collection_attempts=manifest['attempts'],storage_bytes=sum(Path(e['path']).stat().st_size for e in entries),
                prefix_comparisons=comparisons,prefix_max_abs_diff=maximum,different_padding_prefix_comparisons=padding_comparisons,
                different_padding_prefix_max_abs_diff=padding_maximum,new_model_queries_semantics='Durable source-case prefill attempts, including retry work; zero generation.',**counts)
            _put(folder/'summary.json',summary)
            manifest.update(status='complete',chunks=entries,summary_sha256=_sha(folder/'summary.json'),**counts)
            _journal(manifest_path,manifest);_event(manifest_path);return summary
        except Exception as exc:
            finalizing=(folder/'summary.json').exists();manifest.update(status='finalizing' if finalizing else 'failed',error=f'{type(exc).__name__}: {exc}')
            if not finalizing:manifest['attempts'][-1].update(status='failed',error=manifest['error'],wall_seconds=time.monotonic()-started)
            _journal(manifest_path,manifest);_event(manifest_path);raise


def _receipt(config,folder,preflight,manifest,summary,audit):
    return dict(schema_version=1,status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),
        source=preflight['source'],dataset_sha256=config['dataset_sha256'],model=config['model'],model_revision=config['model_revision'],
        cases=summary['cases'],feature_shape=summary['feature_shape'],chunks=manifest['chunks'],
        metadata={name:dict(path=str(folder/name),sha256=_sha(folder/name)) for name in
            ('registration.json','preflight.json','prepared_cases.jsonl','manifest.json','summary.json','audit.json')},
        prefix_comparisons=audit['prefix_comparisons'],prefix_max_abs_diff=audit['prefix_max_abs_diff'],
        model_prefill_cases=summary['model_prefill_cases'],model_prefill_cases_attempted=summary['model_prefill_cases_attempted'],
        prefill_batch_calls=summary['prefill_batch_calls'],new_model_queries=summary['new_model_queries'],
        generated_responses=0,generation_calls=0,generated_holdouts_opened=False)


def audit(config):
    folder,preflight,cases,manifest,summary=_completed_base(config)
    comparisons=0;maximum=0.;padding_comparisons=0;padding_maximum=0.
    for entry in manifest['chunks']:
        selected=cases[entry['first']:entry['first']+entry['rows']]
        features,(checks,difference)=load_chunk(entry,selected,config)
        comparisons+=checks;maximum=max(maximum,difference)
        checks,difference=base._padding_diagnostics(features,selected)
        padding_comparisons+=checks;padding_maximum=max(padding_maximum,difference)
    for key,value in [('prefix_comparisons',comparisons),('prefix_max_abs_diff',maximum),
            ('different_padding_prefix_comparisons',padding_comparisons),('different_padding_prefix_max_abs_diff',padding_maximum)]:
        if summary.get(key)!=value:raise ValueError('overnight prefix diagnostics differ from saved summary')
    result=dict(status='passed',evaluation_role=ROLE,config_hash=digest(config),source=preflight['source'],
        cases=len(cases),feature_shape=summary['feature_shape'],chunks=manifest['chunks'],finite_float32_features=True,
        prefix_comparisons=comparisons,prefix_max_abs_diff=maximum,prefix_atol=summary['prefix_atol'],prefix_check_scope=base.PREFIX_SCOPE,
        different_padding_prefix_comparisons=padding_comparisons,different_padding_prefix_max_abs_diff=padding_maximum,
        source_model_prefill_cases=summary['model_prefill_cases'],source_prefill_batch_calls=summary['prefill_batch_calls'],
        new_model_queries=0,generated_responses=0,generation_calls=0,generated_holdouts_opened=False)
    _put(folder/'audit.json',result);_put(folder/'completion_manifest_v1.json',_receipt(config,folder,preflight,manifest,summary,result))
    return result


def completed_metadata(config):
    _,folder=_config(config);receipt=_json(folder/'completion_manifest_v1.json')
    if (receipt.get('status')!='complete_exploratory' or receipt.get('evaluation_role')!=ROLE
            or receipt.get('config_hash')!=digest(config) or receipt.get('dataset_sha256')!=config['dataset_sha256']):
        raise ValueError('complete matching overnight capture receipt required')
    names=('registration.json','preflight.json','prepared_cases.jsonl','manifest.json','summary.json','audit.json')
    if set(receipt.get('metadata',{}))!=set(names):raise ValueError('exact overnight completion metadata inventory required')
    folder,preflight,cases,manifest,summary=_completed_base(config)
    for name in names:
        if receipt['metadata'][name]!=dict(path=str(folder/name),sha256=_sha(folder/name)):
            raise ValueError('overnight completion metadata pin differs')
    checked=_json(folder/'audit.json')
    if (checked.get('status')!='passed' or checked.get('evaluation_role')!=ROLE or checked.get('config_hash')!=digest(config)
            or checked.get('source')!=preflight['source'] or checked.get('finite_float32_features') is not True
            or checked.get('cases')!=len(cases) or checked.get('feature_shape')!=summary['feature_shape']
            or checked.get('chunks')!=manifest['chunks'] or checked.get('generated_holdouts_opened') is not False
            or checked.get('new_model_queries')!=0 or checked.get('generated_responses')!=0 or checked.get('generation_calls')!=0
            or any(checked.get(k)!=summary.get(k) for k in ('prefix_comparisons','prefix_max_abs_diff',
                'different_padding_prefix_comparisons','different_padding_prefix_max_abs_diff'))
            or receipt!=_receipt(config,folder,preflight,manifest,summary,checked)):
        raise ValueError('overnight capture audit/receipt differs')
    return dict(config=config,model=config['model'],model_revision=config['model_revision'],source=preflight['source'],
        dataset_sha256=config['dataset_sha256'],layers=config['layers'],sites=list(SITES),feature_shape=summary['feature_shape'],
        chunks=manifest['chunks'],cases=cases,preflight=preflight,summary=summary,audit=checked,receipt=receipt)
