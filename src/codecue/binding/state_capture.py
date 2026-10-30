"""Discovery-only current/saved binding captures with exact causal-prefix checks."""
from collections import defaultdict
import importlib.metadata
import json
from pathlib import Path
import time

from .datasets import digest, read_jsonl, write_json
from .published_benchmarks import immutable, sha
from .registry import code_identity, guarded


def prepare(config):
    from transformers import AutoTokenizer
    from .checkpoint_suite import audit, prepared
    from .hook_preflight import state_position
    from .calibration import printed_source
    from .model_adapter import configure_tokenizer
    if sha(config['upstream_config']) != config['upstream_config_sha256']:
        raise ValueError('capture upstream configuration changed')
    upstream = json.loads(Path(config['upstream_config']).read_text())
    for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype', 'tokenization_mode'):
        if upstream[key] != config[key]:raise ValueError('capture checkpoint differs: '+key)
    proof = json.loads(Path(config['hook_proof']).read_text())
    if sha(config['hook_proof']) != config['hook_proof_sha256'] or proof['status'] != 'passed':
        raise ValueError('passing pinned hook proof required')
    checked = audit(upstream)
    if proof['model']!=config['model'] or proof['upstream_identity']!=checked['identity_hash']:
        raise ValueError('hook proof belongs to a different checkpoint or discovery run')
    _, cases = prepared(upstream, checked['preflight']['source_sha256'])
    tok = AutoTokenizer.from_pretrained(config['model'], revision=config['tokenizer_revision'], local_files_only=True)
    configure_tokenizer(tok, config)
    selected = []
    groups = defaultdict(list)
    for case in cases:
        row = case['record']
        if row['family'] != 'versions':continue
        if row['split'] not in ('train', 'development'):raise ValueError('capture cannot open final outcomes')
        state = state_position(tok, case)
        source = printed_source(row['source'])
        end = case['prompt'].index(source)+len(source)
        encoded = tok(case['prompt'], add_special_tokens=False, return_offsets_mapping=True)
        query = max(i for i, (a, b) in enumerate(encoded['offset_mapping']) if a < end)
        prefix = digest(case['input_token_ids'][:state+1])
        final = row['execution_trace'][-1]['values']
        targets = [final[row['rename_map'][name]] for name in ('v0', 'saved')]
        positions=[state,query]
        sites=config.get('sites',['pre_query_state','after_query'])
        if sites not in (['pre_query_state','after_query'],['pre_query_state','after_query','pre_answer']):
            raise ValueError('unknown capture sites')
        if len(sites)==3:positions.append(len(case['input_token_ids'])-1)
        item = dict(case=case, positions=positions, state_prefix_sha256=prefix, targets=targets,
                    visible_prefixes=[tok.decode(case['input_token_ids'][:p+1], skip_special_tokens=False) for p in positions])
        groups[prefix].append(item)
    for prefix, pair in sorted(groups.items()):
        if (len(pair)!=2 or {p['case']['record']['query_role'] for p in pair}!={'current','saved'}
                or pair[0]['targets']!=pair[1]['targets'] or pair[0]['positions'][0]!=pair[1]['positions'][0]
                or len(pair[0]['case']['input_token_ids'])!=len(pair[1]['case']['input_token_ids'])):
            raise ValueError('capture must pair identical causal prefixes before both queries')
        selected += sorted(pair, key=lambda p:p['case']['record']['query_role'])
    path=Path(config['capture_cases'])
    immutable(path, ''.join(json.dumps(c,sort_keys=True)+'\n' for c in selected).encode())
    result=dict(status='passed',cases=len(selected),unique_state_prefixes=len(groups),
                config_hash=digest(config),source_sha256=code_identity()['source_sha256'],
                cases_sha256=sha(path),upstream_identity=checked['identity_hash'],generated_holdouts_opened=False)
    write_json(config['preflight_result'],result)
    return result


def inputs(config, expected_source=None):
    qa=json.loads(Path(config['preflight_result']).read_text())
    if (qa['status']!='passed' or qa['config_hash']!=digest(config)
            or qa['source_sha256']!=(expected_source or code_identity()['source_sha256'])
            or sha(config['capture_cases'])!=qa['cases_sha256']):
        raise ValueError('capture requires matching actual-tokenizer preflight')
    return qa,read_jsonl(config['capture_cases'])


def validate_chunk(config, expected, features, rows):
    import numpy as np
    from .checkpoint_suite import score_case
    if (len(expected)!=len(rows) or len(rows)%2 or
            features.shape!=(len(rows),len(config['layers']),len(config.get('sites',['pre_query_state','after_query'])),config['hidden_size'])
            or not np.isfinite(features).all()):
        raise ValueError('capture tensor shape, coverage or values differ')
    fields=('id','base_id','template_id','split','condition','lexical_realization',
            'available_bindings','updates','tail_placement','query_role')
    for row,item in zip(rows,expected):
        if (len(item['positions'])!=features.shape[2] or len(item['visible_prefixes'])!=features.shape[2]
                or any(row[key]!=item['case']['record'][key] for key in fields)
                or row['targets']!=item['targets'] or row['positions']!=item['positions']
                or row['state_prefix_sha256']!=item['state_prefix_sha256']
                or row['input_token_ids_sha256']!=digest(item['case']['input_token_ids'])
                or row['visible_prefixes']!=item['visible_prefixes']
                or item['case']['record']['expected_answer']!=item['targets'][0 if row['query_role']=='current' else 1]
                or len(row['output_token_ids'])>16
                or row['score']!=score_case(item['case'],row['raw_response'])):
            raise ValueError('capture row identity, visibility or score differs')
        if config.get('verify_first_token') and row['prefill_argmax_token']!=row['first_generation_token']:
            raise ValueError('prefill logits do not match the generated first token')
    for i in range(0,len(rows),2):
        if not np.array_equal(features[i,:,0],features[i+1,:,0]):
            raise ValueError('capture causal-prefix invariant differs')


@guarded
def extract(config):
    import numpy as np
    import torch
    from transformers import StopStringCriteria,StoppingCriteriaList
    from codecue.patching import decoder_layers
    from .checkpoint_suite import score_case
    from .model_adapter import load
    from .registry import begin,finish
    qa,cases=inputs(config)
    if config['batch_size']%2:raise ValueError('paired capture batches must be even')
    out,manifest=begin(config,'activations',reuse_complete=True)
    if manifest['status']=='complete':return json.loads((out/'summary.json').read_text())
    started=time.monotonic();folder=out/'chunks';folder.mkdir(exist_ok=True)
    completed=0
    for path in sorted(folder.glob('*.npz')):
        with np.load(path,allow_pickle=False) as data:
            rows=json.loads(data['metadata'].tobytes())
            validate_chunk(config,cases[completed:completed+len(rows)],data['features'],rows)
            completed+=len(rows)
    tokenizer,model=load(config);model.set_attn_implementation('sdpa')
    blocks=decoder_layers(model)
    criterion=StopStringCriteria(tokenizer,['\n\n'])
    for first in range(completed,len(cases),config['batch_size']):
        batch=cases[first:first+config['batch_size']]
        encoded=tokenizer([c['case']['prompt'] for c in batch],add_special_tokens=False,padding=True,return_tensors='pt').to(model.device)
        width=encoded.input_ids.shape[1]
        physical=[]
        for i,item in enumerate(batch):
            expected=item['case']['input_token_ids']
            if encoded.input_ids[i][encoded.attention_mask[i].bool()].tolist()!=expected:
                raise ValueError('capture generation prompt differs')
            physical.append([width-len(expected)+p for p in item['positions']])
        positions=torch.tensor(physical,device=model.device)
        indices=torch.arange(len(batch),device=model.device)[:,None]
        captured,handles={},[]
        first_tokens={}
        for layer in config['layers']:
            def hook(module,args,output,layer=layer):
                hidden=output[0] if isinstance(output,tuple) else output
                if layer not in captured and hidden.shape[1]==width:
                    captured[layer]=hidden[indices,positions].detach().float().cpu().numpy()
            handles.append(blocks[layer].register_forward_hook(hook))
        if config.get('verify_first_token'):
            def logits_hook(module,args,output):
                if 'ids' not in first_tokens:
                    first_tokens['ids']=output.logits[:,-1].argmax(-1).detach().cpu().tolist()
            handles.append(model.register_forward_hook(logits_hook))
        try:
            with torch.inference_mode():
                output=model.generate(**encoded,do_sample=False,num_beams=1,use_cache=True,max_new_tokens=16,
                    eos_token_id=config['eos_token_ids'],pad_token_id=tokenizer.pad_token_id,
                    stopping_criteria=StoppingCriteriaList([criterion]))
        finally:
            for handle in handles:handle.remove()
        if set(captured)!=set(config['layers']):raise ValueError('missing capture layer')
        features=np.stack([captured[layer] for layer in config['layers']],axis=1)
        if not np.isfinite(features).all():raise ValueError('nonfinite captured activation')
        for i in range(0,len(batch),2):
            if not np.array_equal(features[i,:,0],features[i+1,:,0]):
                raise ValueError('paired pre-query states differ; inspect causal masking and padding')
        rows=[]
        for batch_index,(item,tail) in enumerate(zip(batch,output[:,width:].tolist())):
            generated_first=tail[0] if tail else None
            for i,token in enumerate(tail):
                if token in config['eos_token_ids']:tail=tail[:i];break
            case=item['case'];record=case['record'];raw=tokenizer.decode(tail,skip_special_tokens=True)
            row={key:record[key] for key in ('id','base_id','template_id','split','condition','lexical_realization','available_bindings','updates','tail_placement','query_role')}
            row.update(targets=item['targets'],state_prefix_sha256=item['state_prefix_sha256'],
                       visible_prefixes=item['visible_prefixes'],positions=item['positions'],
                       input_token_ids_sha256=digest(case['input_token_ids']),raw_response=raw,
                       output_token_ids=tail,score=score_case(case,raw))
            if config.get('verify_first_token'):
                row.update(prefill_argmax_token=first_tokens['ids'][batch_index],first_generation_token=generated_first)
            rows.append(row)
        validate_chunk(config,batch,features,rows)
        path=folder/f'{first:06d}.npz';temp=path.with_suffix('.tmp')
        with temp.open('wb') as stream:
            np.savez(stream,features=features,metadata=np.frombuffer(json.dumps(rows,sort_keys=True).encode(),dtype=np.uint8))
        temp.replace(path)
        write_json(out/'progress.json',dict(complete=False,evaluated=first+len(batch),planned=len(cases)))
        print(f'capture {first+len(batch)}/{len(cases)}',flush=True)
    summary=dict(complete=True,evaluated=len(cases),planned=len(cases),preflight=qa,layers=config['layers'],
                 sites=config.get('sites',['pre_query_state','after_query']),target_slots=['current','saved'],stored_dtype='float32',
                 device_name=torch.cuda.get_device_name(),storage_bytes=sum(p.stat().st_size for p in folder.glob('*.npz')),
                 torch_peak_memory_bytes=torch.cuda.max_memory_allocated(),
                 versions={name:importlib.metadata.version(name) for name in ('torch','transformers')},
                 generated_holdouts_opened=False,interpretation='Discovery captures only; no decoding or mechanism claim.')
    write_json(out/'summary.json',summary);finish(out,manifest,time.monotonic()-started)
    return summary


def audit(config):
    import numpy as np
    out=Path(config['run_dir'])/'activations';manifest=json.loads((out/'manifest.json').read_text())
    if (manifest['status']!='complete' or manifest['identity_hash']!=digest(manifest['identity'])
            or manifest['identity']['config']!=config):raise ValueError('complete pinned capture required')
    qa,cases=inputs(config,manifest['identity']['code']['source_sha256'])
    seen=0;checksums={};correct=0
    for path in sorted((out/'chunks').glob('*.npz')):
        with np.load(path,allow_pickle=False) as data:
            features=data['features'];rows=json.loads(data['metadata'].tobytes())
            validate_chunk(config,cases[seen:seen+len(rows)],features,rows)
            correct+=sum(row['score']['correct'] for row in rows)
            seen+=len(rows);checksums[str(path)]=sha(path)
    if seen!=len(cases):raise ValueError('capture coverage incomplete')
    result=dict(status='passed',cases=seen,hf_correct=correct,identity_hash=manifest['identity_hash'],
                preflight=qa,chunk_checksums=checksums,generated_holdouts_opened=False,
                interpretation='Raw decoder-block output, before final normalization. Train probes on neutral training cases only; deduplicate pre-query rows by state_prefix_sha256. No final outcomes.')
    if config.get('verify_first_token'):result['prefill_argmax_matches_generation_cases']=seen
    immutable(out/'audit.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return result
