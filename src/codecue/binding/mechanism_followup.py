"""Fresh numeric ownership and common-final-query discovery controls.

The numeric bank excludes both orientations of every previous literal pair.
These remain familiar program structures, not a structural generalization set.
"""
import ast
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
import time

from .datasets import digest, read_jsonl, write_json
from .interpreter import execute, python_oracle, substituted_source
from .published_benchmarks import immutable, sha
from .registry import code_identity, guarded
from . import timing_and_copy as prior

CONDITIONS = ('first_copy', 'second_copy', 'both_copies', 'identity_sham',
              'nearby_position', 'unrelated_position', 'wrong_version',
              'random_11', 'random_29', 'random_47',
              'random_both_11', 'random_both_29', 'random_both_47', 'answer_vector')


def anchor_cases(config):
    path = config['generation']['anchor_prepared']
    if sha(path) != config['generation']['anchor_prepared_sha256']:
        raise ValueError('follow-up anchor checksum differs')
    return json.loads(Path(path).read_text())['cases']


def fresh_values(config):
    seen = {tuple(c['record']['literal_values']) for c in anchor_cases(config).values()}
    return [(a, b) for a, b in product(range(1, 10), repeat=2)
            if a != b and (a, b) not in seen and (b, a) not in seen]


def names(row):
    return [('v0', 'v1', 'buffer'), ('n0', 'n1', 'temp')][row['lexical_realization']]


def make_rows(config):
    rows = []
    if config['assay'] == 'cue_control':
        for key, case in sorted(anchor_cases(config).items()):
            for common in (False, True):
                row = dict(case['record'], timing_anchor_id=key, common_final_query=common,
                           evaluation_role='common_final_query_discovery')
                row['id'] = 'cue-control:' + digest([key, common])[:24]
                rows.append(row)
        return rows
    for (a, b), lexical, mapping, query, instruction, form in product(
            fresh_values(config), range(2), range(2), range(2), range(3), ('anchor', 'reordered', 'wrong_version')):
        row = dict(family='ownership', mapping=mapping, query=query, query_role=['v0', 'v1'][query],
                   lexical_realization=lexical, instruction=instruction, source_form=form,
                   literal_values=[a, b], numeric_group=f'{a}:{b}', split='development',
                   evaluation_role='fresh_numeric_ownership_discovery')
        x, y, scratch = names(row)
        lines = [f'{scratch} = 0', f'{x} = {a}', f'{y} = {b}', f'{scratch} = {x}',
                 f'{x} = {y if mapping else x}', f'{y} = {scratch if mapping else y}', f'{scratch} = 0']
        if form == 'reordered':
            lines[2], lines[3] = lines[3], lines[2]
        elif form == 'wrong_version':
            lines[3], lines[4] = lines[4], lines[3]
        source = '\n'.join(lines + [[x, y][query]])
        row.update(source=source, expected_answer=execute(source)['expected_answer'],
                   id='owner-control:' + digest([source, instruction, form])[:24])
        rows.append(row)
    return rows


def pair_key(row, values=None, form=None):
    return (tuple(row['literal_values'] if values is None else values), row['lexical_realization'],
            row['mapping'], row['query'], row['instruction'], row['source_form'] if form is None else form)


def pairs_for(config, rows):
    if config['assay'] == 'cue_control':
        return []
    lookup = {pair_key(r): r for r in rows}
    pairs = []
    for r in rows:
        if r['source_form'] == 'wrong_version':
            continue
        reversed_values = r['literal_values'][::-1]
        donor = lookup[pair_key(r, reversed_values)]
        wrong = lookup[pair_key(r, reversed_values, 'wrong_version')]
        x, y, _ = names(r)
        state = execute(donor['source'])['execution_trace'][-1]['values']
        wrong_state = execute(wrong['source'])['execution_trace'][-1]['values']
        changes = dict(first_copy={x+'@2': state[x]}, second_copy={y+'@2': state[y]},
                       both_copies={x+'@2': state[x], y+'@2': state[y]}, wrong_version={y+'@2': wrong_state[y]})
        counterfactuals = {}
        for condition, substitutions in changes.items():
            truth = execute(r['source'], substitutions)
            counterfactuals[condition] = dict(substitutions=substitutions, answer=truth['expected_answer'],
                final_state=truth['execution_trace'][-1]['values'])
        pairs.append(dict(id=digest([r['id'], donor['id']]), recipient=r['id'], donor=donor['id'],
                          wrong_donor=wrong['id'], counterfactuals=counterfactuals))
    return sorted(pairs, key=lambda p:p['id'])


def validate(config, rows, independent=False):
    if rows != make_rows(config) or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('follow-up data differ from registered complete design')
    pairs = pairs_for(config, rows)
    by_id = {r['id']: r for r in rows}
    sources, truths = [], []
    for row in rows:
        truth = execute(row['source'])
        if truth['expected_answer'] != row['expected_answer']:
            raise ValueError('incorrect follow-up oracle')
        sources.append(row['source']); truths.append(truth)
    for pair in pairs:
        r, donor = (by_id[pair[k]] for k in ('recipient', 'donor'))
        x, y, _ = names(r)
        before = execute(r['source'])['execution_trace'][-1]['values']
        after = execute(donor['source'])['execution_trace'][-1]['values']
        if sorted(before.values()) != sorted(after.values()) or any(before[k] == after[k] for k in (x,y)):
            raise ValueError('primary donors must reverse ownership preserving the whole value multiset')
        for condition, cf in pair['counterfactuals'].items():
            truth = execute(r['source'], cf['substitutions'])
            source = r['source']
            for definition, value in cf['substitutions'].items():
                source = substituted_source(source, definition, value)
            if cf['final_state'] != truth['execution_trace'][-1]['values'] or cf['answer'] != truth['expected_answer']:
                raise ValueError('counterfactual full state mismatch')
            if condition == 'both_copies' and cf['final_state'] != after:
                raise ValueError('joint copy substitution does not reproduce donor state')
            if condition in ('first_copy','second_copy'):
                unchanged = y if condition == 'first_copy' else x
                if cf['final_state'][unchanged] != before[unchanged]:
                    raise ValueError('single-site oracle changed unrelated quantity')
            sources.append(source); truths.append(truth)
    if independent:
        for start in range(0,len(sources),128):
            for truth, oracle in zip(truths[start:start+128],python_oracle(sources[start:start+128])):
                if truth['expected_answer']!=oracle['answer'] or [p['values'] for p in truth['execution_trace']]!=oracle['trace']:
                    raise ValueError('independent Python full trace differs')
    return pairs


def build(config):
    rows=make_rows(config);pairs=validate(config,rows,True)
    path=Path(config['dataset'])
    immutable(path, ''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows).encode())
    manifest=dict(sha256=sha(path),generation_config_hash=digest(config['generation']),rows=len(rows),
                  control_pairs=len(pairs),independent_oracle_passed=True,generated_holdouts_opened=False)
    immutable(path.with_suffix('.manifest.json'),(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())
    return manifest


def layout(tokenizer,row,config):
    if config['assay']=='cue_control':
        return prior.layout(tokenizer,row,dict(config,assay='query_timing'))
    text,body=prior.prompt(tokenizer,row,dict(config,assay='copy_path'))
    encoded=tokenizer(text,add_special_tokens=False,return_offsets_mapping=True)
    x,y,_=names(row)
    trace=execute(row['source'])['execution_trace']
    indices=[next(p['statement'] for p in trace if p['definition']==name+'@2') for name in (x,y)]+[0]
    lines=body.splitlines(keepends=True);start=text.index(body);positions=[]
    for index in indices:
        end=start+sum(map(len,lines[:index]))+len(lines[index].rstrip('\n'))
        matches=[i for i,(a,b) in enumerate(encoded['offset_mapping']) if a<end==b]
        if len(matches)!=1:raise ValueError('copy definition not at a token boundary')
        positions.append(matches[0])
    positions.append(len(encoded['input_ids'])-1)
    return dict(record=row,prompt=text,input_token_ids=encoded['input_ids'],positions=positions)


def validate_layouts(config,cases,pairs):
    if config['assay']=='cue_control':
        for common in (False,True):
            subset={k:c for k,c in cases.items() if c['record']['common_final_query']==common}
            prior.validate_layouts(dict(config,assay='query_timing'),subset,[])
        original=anchor_cases(config)
        for c in cases.values():
            if not c['record']['common_final_query'] and c['input_token_ids']!=original[c['record']['timing_anchor_id']]['input_token_ids']:
                raise ValueError('original timing interface changed')
    for p in pairs:
        r,d,w=[cases[p[k]] for k in ('recipient','donor','wrong_donor')]
        if (len(r['input_token_ids'])!=len(d['input_token_ids']) or r['positions']!=d['positions']
                or Counter(r['input_token_ids'])!=Counter(d['input_token_ids'])):
            raise ValueError('ownership donors changed token geometry or exposure')
        if len(r['input_token_ids'])!=len(w['input_token_ids']) or r['positions'][1]!=w['positions'][1]:
            raise ValueError('wrong-version control must match second-copy position and full length')


def prepare(config):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    if sha(config['hook_proof'])!=config['hook_proof_sha256']:raise ValueError('hook proof changed')
    rows=read_jsonl(config['dataset']);pairs=validate(config,rows)
    tok=AutoTokenizer.from_pretrained(config['model'],revision=config['tokenizer_revision'],local_files_only=True)
    configure_tokenizer(tok,config)
    cases={r['id']:layout(tok,r,config) for r in rows};validate_layouts(config,cases,pairs)
    if len(cases)%config['batch_size'] or len(pairs)%config['batch_size']:raise ValueError('complete batches required')
    answer_ids={str(v):tok(str(v),add_special_tokens=False)['input_ids'] for v in range(10)}
    if any(len(ids)!=1 for ids in answer_ids.values()):raise ValueError('single-token digits required')
    payload=dict(cases=cases,pairs=[],control_pairs=pairs,answer_token_ids={k:v[0] for k,v in answer_ids.items()},
                 padded_width=max(len(c['input_token_ids']) for c in cases.values()))
    immutable(config['prepared_cases'],(json.dumps(payload,sort_keys=True)+'\n').encode())
    qa=dict(status='passed',config_hash=digest(config),source_sha256=code_identity()['source_sha256'],
            prepared_sha256=sha(config['prepared_cases']),dataset_sha256=sha(config['dataset']),
            cases=len(cases),control_pairs=len(pairs),generated_holdouts_opened=False)
    write_json(config['preflight_result'],qa);return qa


def inputs(config,source_hash=None):
    qa=json.loads(Path(config['preflight_result']).read_text())
    if (qa['status']!='passed' or qa['config_hash']!=digest(config)
            or qa['source_sha256']!=(source_hash or code_identity()['source_sha256'])
            or qa['prepared_sha256']!=sha(config['prepared_cases']) or qa['dataset_sha256']!=sha(config['dataset'])):
        raise ValueError('matching frozen follow-up preflight required')
    data=json.loads(Path(config['prepared_cases']).read_text());rows=read_jsonl(config['dataset'])
    if data['pairs'] or data['control_pairs']!=validate(config,rows) or {r['id']:r for r in rows}!={k:c['record'] for k,c in data['cases'].items()}:
        raise ValueError('prepared follow-up identities differ')
    validate_layouts(config,data['cases'],data['control_pairs'])
    if data['padded_width']!=max(len(c['input_token_ids']) for c in data['cases'].values()):raise ValueError('padding width changed')
    return qa,data


def target_answer(pair, condition, cases):
    if condition in pair['counterfactuals']:
        return pair['counterfactuals'][condition]['answer']
    return cases[pair['donor' if condition=='answer_vector' else 'recipient']]['record']['expected_answer']


def patch_sites(condition):
    if condition in ('both_copies','random_both_11','random_both_29','random_both_47'):
        return [0,1]
    return [0 if condition in ('first_copy','nearby_position') else
            2 if condition=='unrelated_position' else 3 if condition=='answer_vector' else 1]


def check_chunk(config,data,layer,condition,part,rows,replays,baselines):
    import math
    if len(rows)!=len(part):raise ValueError('ownership chunk coverage differs')
    for p,row in zip(part,rows):
        expected=target_answer(p,condition,data['cases'])
        if (row['pair_id']!=p['id'] or row['layer']!=layer or row['condition']!=condition
                or row['target_answer']!=expected or row['sites']!=patch_sites(condition)):
            raise ValueError('ownership chunk identity, site or semantic target differs')
        numbers=row['norms']+row['reference_norms']+[row['target_logprob'],row['donor_logprob'],row['recipient_logprob']]
        if not all(math.isfinite(v) for v in numbers) or any(v<0 for v in row['norms']):raise ValueError('nonfinite or negative ownership measurement')
        if len(row['norms'])!=len(row['sites']) or len(row['reference_norms'])!=len(row['sites']):raise ValueError('norm count differs')
        for actual,goal in zip(row['norms'],row['reference_norms']):
            if abs(actual-goal)>config['norm_tolerance']*max(goal,1e-8):raise ValueError('effective BF16 norm matching failed')
        if condition=='identity_sham' and (row['first_token']!=replays[p['id']]['first_token'] or any(row['norms'])):
            raise ValueError('identity sham changed output or vectors')
        if layer==31 and condition!='answer_vector' and row['first_token']!=replays[p['id']]['first_token']:
            raise ValueError('final-layer earlier-token patch changed answer')
        if layer==31 and condition=='answer_vector' and row['first_token']!=baselines[p['donor']]['first_token']:
            raise ValueError('final answer-vector software control failed')


@guarded
def run(config):
    from .value_transfer import run as capture_engine
    capture=capture_engine(config)
    if config['assay']=='cue_control':return capture
    import gc
    import numpy as np
    import torch
    from codecue.patching import decoder_layers
    from .model_adapter import load
    from .registry import begin,finish
    from .value_transfer import _encode,matched_perturbation
    gc.collect();torch.cuda.empty_cache()
    qa,data=inputs(config)
    out,manifest=begin(config,'ownership_controls',reuse_complete=True)
    if manifest['status']=='complete':return json.loads((out/'summary.json').read_text())
    started=time.monotonic()
    base_root=Path(config['run_dir'])/'interventions'
    captured=json.loads((base_root/'summary.json').read_text())
    for name,key in (('baselines.json','baseline_sha256'),('baseline_vectors.npz','vector_bank_sha256')):
        if sha(base_root/name)!=captured[key]:raise ValueError('baseline artifact changed')
    proof=out/'cache_checksums.json'
    if proof.exists():
        for name,expected in json.loads(proof.read_text()).items():
            if sha(out/name)!=expected:raise ValueError('ownership replay cache changed')
    with np.load(base_root/'baseline_vectors.npz',allow_pickle=False) as saved:
        bank=saved['vectors'];ids=saved['case_ids'].tolist()
    baselines=json.loads((base_root/'baselines.json').read_text())
    ix={k:i for i,k in enumerate(ids)};pairs=data['control_pairs'];cases=data['cases']
    tok,model=load(config);model.set_attn_implementation('sdpa');blocks=decoder_layers(model)
    replay_path=out/'replay_vectors.npz';meta_path=out/'replays.json'
    if replay_path.exists() and meta_path.exists():
        with np.load(replay_path,allow_pickle=False) as saved:
            replay=saved['vectors']
            if saved['pair_ids'].tolist()!=[p['id'] for p in pairs]:raise ValueError('replay identities differ')
        replays=json.loads(meta_path.read_text())
    else:
        all_vectors=[];replays={}
        for start in range(0,len(pairs),config['batch_size']):
            part=pairs[start:start+config['batch_size']];batch=[cases[p['recipient']] for p in part]
            enc=_encode(tok,batch,model.device,data['padded_width']);width=enc.input_ids.shape[1]
            positions=torch.tensor([[width-len(c['input_token_ids'])+p for p in c['positions']] for c in batch],device=model.device)
            arange=torch.arange(len(batch),device=model.device);captures={};handles=[]
            for layer in config['layers']:
                def capture_hook(module,args,output,layer=layer):
                    h=output[0] if isinstance(output,tuple) else output
                    captures[layer]=h[arange[:,None],positions].detach().float().cpu().numpy()
                handles.append(blocks[layer].register_forward_hook(capture_hook))
            try:
                with torch.inference_mode():result=model(**enc,use_cache=False,logits_to_keep=1)
            finally:
                for h in handles:h.remove()
            all_vectors.append(np.stack([captures[l] for l in config['layers']],axis=1))
            lp=torch.log_softmax(result.logits[:,-1].float(),-1)
            first=lp.argmax(-1).tolist();digit=lp[:,[data['answer_token_ids'][str(v)] for v in range(1,10)]].tolist()
            for i,p in enumerate(part):replays[p['id']]=dict(first_token=first[i],digit_logprobs=digit[i])
        replay=np.concatenate(all_vectors)
        temp=replay_path.with_suffix('.tmp')
        with temp.open('wb') as stream:np.savez(stream,vectors=replay,pair_ids=np.array([p['id'] for p in pairs]))
        temp.replace(replay_path);write_json(meta_path,replays)
    if replay.shape!=(len(pairs),len(config['layers']),4,config['hidden_size']) or not np.isfinite(replay).all() or set(replays)!={p['id'] for p in pairs}:
        raise ValueError('ownership replay geometry, coverage or finiteness differs')
    immutable(proof,(json.dumps({p.name:sha(p) for p in (replay_path,meta_path)},sort_keys=True,indent=2)+'\n').encode())
    folder=out/'chunks';folder.mkdir(exist_ok=True)
    for li,layer in enumerate(config['layers']):
        for condition in CONDITIONS:
            for start in range(0,len(pairs),config['batch_size']):
                part=pairs[start:start+config['batch_size']]
                path=folder/f'l{layer:02d}_{condition}_{start:06d}.json'
                if path.exists():
                    check_chunk(config,data,layer,condition,part,json.loads(path.read_text()),replays,baselines);continue
                batch=[cases[p['recipient']] for p in part]
                enc=_encode(tok,batch,model.device,data['padded_width']);width=enc.input_ids.shape[1]
                recipient=torch.tensor(replay[start:start+len(part),li],device=model.device,dtype=model.dtype)
                donor=torch.tensor(np.stack([bank[ix[p['donor']],li] for p in part]),device=model.device,dtype=model.dtype)
                delta=donor.float()-recipient.float();norms=delta.norm(dim=-1)
                sites=patch_sites(condition);patches=[];actuals=[];references=[]
                for site in sites:
                    base=recipient[:,site]
                    if condition in ('first_copy','second_copy','both_copies','answer_vector'):
                        patch=donor[:,site];actual=norms[:,site];goal=actual
                    elif condition=='identity_sham':
                        patch=base;actual=goal=torch.zeros(len(part),device=model.device)
                    else:
                        goal=norms[:,site if condition.startswith('random_both_') else 1]
                        direction=delta[:,1]
                        if condition=='wrong_version':
                            wrong=torch.tensor(np.stack([bank[ix[p['wrong_donor']],li,1] for p in part]),device=model.device)
                            direction=wrong-recipient[:,1].float()
                        if condition.startswith('random_'):
                            seed=int(condition.rsplit('_',1)[1]);directions=[]
                            for p in part:
                                rng=torch.Generator(device='cpu').manual_seed(int(digest([p['id'],layer,seed,site])[:15],16))
                                directions.append(torch.randn(config['hidden_size'],generator=rng))
                            direction=torch.stack(directions).to(model.device)
                        patch,actual=matched_perturbation(base,direction,goal,config['norm_tolerance'])
                    patches.append(patch);actuals.append(actual.tolist());references.append(goal.tolist())
                arange=torch.arange(len(part),device=model.device)
                positions=[torch.tensor([width-len(c['input_token_ids'])+c['positions'][site] for c in batch],device=model.device) for site in sites]
                calls=[]
                def patch_hook(module,args,output):
                    hidden=output[0] if isinstance(output,tuple) else output
                    for site,pos in zip(sites,positions):
                        if not torch.equal(hidden[arange,pos],recipient[:,site]):raise ValueError('actual ownership destination differs from same-batch replay')
                    changed=hidden.clone()
                    for pos,patch in zip(positions,patches):changed[arange,pos]=patch
                    calls.append(True)
                    return (changed,*output[1:]) if isinstance(output,tuple) else changed
                handle=blocks[layer].register_forward_hook(patch_hook)
                try:
                    with torch.inference_mode():result=model(**enc,use_cache=False,logits_to_keep=1)
                finally:handle.remove()
                if len(calls)!=1:raise ValueError('ownership hook must fire once')
                lp=torch.log_softmax(result.logits[:,-1].float(),-1);first=lp.argmax(-1).tolist();rows=[]
                for i,p in enumerate(part):
                    original=cases[p['recipient']]['record']['expected_answer'];target=target_answer(p,condition,cases)
                    donor_answer=cases[p['donor']]['record']['expected_answer']
                    rows.append(dict(pair_id=p['id'],layer=layer,condition=condition,sites=sites,first_token=first[i],
                        target_answer=target,target_logprob=float(lp[i,data['answer_token_ids'][str(target)]]),
                        donor_logprob=float(lp[i,data['answer_token_ids'][str(donor_answer)]]),
                        recipient_logprob=float(lp[i,data['answer_token_ids'][str(original)]]),
                        norms=[n[i] for n in actuals],reference_norms=[n[i] for n in references]))
                check_chunk(config,data,layer,condition,part,rows,replays,baselines);write_json(path,rows)
                write_json(out/'progress.json',dict(layer=layer,condition=condition,pairs_completed=start+len(part),pairs_planned=len(pairs)))
            print(f'ownership layer {layer} {condition}: {len(pairs)} pairs',flush=True)
    summary=dict(complete=True,control_pairs=len(pairs),intervention_forwards=len(pairs)*len(config['layers'])*len(CONDITIONS),
                 conditions=list(CONDITIONS),layers=config['layers'],baseline_cases=len(cases),
                 baseline_summary_sha256=sha(base_root/'summary.json'),cache_checksums=json.loads(proof.read_text()),
                 chunk_checksums={str(p):sha(p) for p in sorted(folder.glob('*.json'))},
                 generation_replay_first_token_matches=sum(replays[p['id']]['first_token']==baselines[p['recipient']]['first_token'] for p in pairs),
                 device_name=torch.cuda.get_device_name(),torch_peak_memory_bytes=torch.cuda.max_memory_allocated(),generated_holdouts_opened=False)
    write_json(out/'summary.json',summary);finish(out,manifest,time.monotonic()-started);return summary


def audit(config):
    import numpy as np
    from .routing_extension import audit as baseline_audit
    baseline=baseline_audit(config)
    if config['assay']=='cue_control':return baseline
    out=Path(config['run_dir'])/'ownership_controls'
    manifest=json.loads((out/'manifest.json').read_text());summary=json.loads((out/'summary.json').read_text())
    if manifest['status']!='complete' or manifest['identity_hash']!=digest(manifest['identity']) or manifest['identity']['config']!=config:
        raise ValueError('complete pinned ownership run required')
    _,data=inputs(config,manifest['identity']['code']['source_sha256']);pairs=data['control_pairs']
    if summary['baseline_summary_sha256']!=sha(Path(config['run_dir'])/'interventions/summary.json'):raise ValueError('baseline summary changed')
    for name,expected in summary['cache_checksums'].items():
        if sha(out/name)!=expected:raise ValueError('ownership replay checksum differs')
    with np.load(out/'replay_vectors.npz',allow_pickle=False) as saved:
        vectors=saved['vectors']
        if saved['pair_ids'].tolist()!=[p['id'] for p in pairs] or vectors.shape!=(len(pairs),len(config['layers']),4,config['hidden_size']) or not np.isfinite(vectors).all():
            raise ValueError('audited replay geometry differs')
    replays=json.loads((out/'replays.json').read_text());baselines=json.loads((Path(config['run_dir'])/'interventions/baselines.json').read_text())
    expected_paths=[];count=0;max_error=0.
    for layer,condition in product(config['layers'],CONDITIONS):
        for start in range(0,len(pairs),config['batch_size']):
            path=out/'chunks'/f'l{layer:02d}_{condition}_{start:06d}.json';expected_paths.append(str(path))
            if sha(path)!=summary['chunk_checksums'].get(str(path)):raise ValueError('ownership chunk checksum differs')
            rows=json.loads(path.read_text());check_chunk(config,data,layer,condition,pairs[start:start+config['batch_size']],rows,replays,baselines)
            count+=len(rows)
            for row in rows:
                for actual,goal in zip(row['norms'],row['reference_norms']):max_error=max(max_error,abs(actual-goal)/max(goal,1e-8))
    if set(expected_paths)!=set(summary['chunk_checksums']) or set(expected_paths)!={str(p) for p in (out/'chunks').glob('*.json')} or count!=summary['intervention_forwards']:
        raise ValueError('ownership chunk total or complete coverage differs')
    result=dict(status='passed',identity_hash=manifest['identity_hash'],baseline_audit=baseline,
                intervention_forwards=count,maximum_relative_norm_error=max_error,summary_sha256=sha(out/'summary.json'),generated_holdouts_opened=False)
    immutable(out/'audit.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode());return result


def review(config):
    """Retain every registered cell; report before/after adoption and semantic accuracy."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=Path(config['run_dir'])
    stage=root/('interventions' if config['assay']=='cue_control' else 'ownership_controls')
    checked=json.loads((stage/'audit.json').read_text());manifest=json.loads((stage/'manifest.json').read_text())
    if checked['status']!='passed' or checked['identity_hash']!=manifest['identity_hash']:raise ValueError('completed audit required')
    _,data=inputs(config,manifest['identity']['code']['source_sha256'])
    baselines=json.loads((root/'interventions/baselines.json').read_text());cases=data['cases']
    baseline_groups=defaultdict(list)
    for key,c in cases.items():
        r=c['record']
        group=([r['common_final_query']] if config['assay']=='cue_control' else [])+[r['source_form'],r['instruction'],r['family'],r['mapping'],r['query']]
        baseline_groups[tuple(group)].append(baselines[key])
    cells=[dict(group=list(k),n=len(v),correct=sum(x['correct'] for x in v),invalid=sum(x['prediction'] is None for x in v)) for k,v in sorted(baseline_groups.items())]
    lines=['# '+config['report_title'],'',config['interpretation'],'',
           f"All {len(cases)} baseline cases retained; {sum(b['correct'] for b in baselines.values())} correct. Generated final/extrapolation holdouts remain sealed.",'']
    result=dict(status='complete_audited',baseline_cells=cells,audit_sha256=sha(stage/'audit.json'),generated_holdouts_opened=False)
    if config['assay']=='cue_control':
        groups=defaultdict(dict);overall=[];flips=[]
        for key,c in cases.items():
            r=c['record'];groups[r['anchor_id'],r['instruction'],r['common_final_query']][r['source_form']]=key
        for (anchor,instruction,common),forms in groups.items():
            if set(forms)!={'early','late'}:raise ValueError('incomplete common-query timing pair')
            a,b=(baselines[forms[f]]['correct'] for f in ('early','late'))
            flips.append(dict(anchor_id=anchor,instruction=instruction,common_final_query=common,early_correct=a,late_correct=b))
        fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
        for common,ax in zip((False,True),axes):
            for form in ('early','late'):
                chosen=[baselines[k] for k,c in cases.items() if c['record']['common_final_query']==common and c['record']['source_form']==form]
                overall.append(dict(common_final_query=common,source_form=form,n=len(chosen),correct=sum(b['correct'] for b in chosen)))
            for i,form in enumerate(('early','late')):
                ys=[]
                for instruction in range(3):
                    chosen=[baselines[k] for k,c in cases.items() if (c['record']['common_final_query'],c['record']['source_form'],c['record']['instruction'])==(common,form,instruction)]
                    ys.append(sum(b['correct'] for b in chosen)/len(chosen))
                ax.bar([x+(i-.5)*.36 for x in range(3)],ys,width=.36,label=form)
            ax.set(xticks=range(3),xticklabels=['Instruction 0','Instruction 1','Instruction 2'],ylim=(0,1),title='Common final query' if common else 'Original timing cues',ylabel='Accuracy');ax.legend()
        def gap(common):
            selected={r['source_form']:r['correct']/r['n'] for r in overall if r['common_final_query']==common}
            return selected['late']-selected['early']
        did=gap(True)-gap(False)
        original=anchor_cases(config)
        old_path=Path(config['generation']['anchor_baselines'])
        if sha(old_path)!=config['generation']['anchor_baselines_sha256']:raise ValueError('old timing outcomes changed')
        old=json.loads(old_path.read_text())
        replay_matches=sum(baselines[k]['first_token']==old[c['record']['timing_anchor_id']]['first_token'] for k,c in cases.items() if not c['record']['common_final_query'])
        result.update(overall=overall,paired_flips=flips,original_late_minus_early=gap(False),common_final_late_minus_early=gap(True),
                      difference_in_differences=did,original_input_replay_first_token_matches=replay_matches,original_input_replay_n=len(original))
        lines+=['| Common final cue | Early correct | Late correct | Late − early |','|---|---:|---:|---:|']
        for common in (False,True):
            chosen={r['source_form']:r for r in overall if r['common_final_query']==common}
            lines.append(f"| {common} | {chosen['early']['correct']}/{chosen['early']['n']} | {chosen['late']['correct']}/{chosen['late']['n']} | {gap(common):+.2%} |")
        lines+=['',f'Difference in differences: {did:+.2%}. This is a descriptive prompt-control contrast, not an estimate of a tracking algorithm.',
                f'Identical original-input first tokens replayed in {replay_matches}/{len(original)} cases across the changed batch/hardware profile.',
                '','All instruction/family/mapping/query cells and paired flips are saved in the review artifact. Earlier-prefix invariance is enforced by the capture audit.']
    else:
        summary=json.loads((stage/'summary.json').read_text())
        if checked['summary_sha256']!=sha(stage/'summary.json'):raise ValueError('audited summary changed')
        pairs={p['id']:p for p in data['control_pairs']};replays=json.loads((stage/'replays.json').read_text())
        groups=defaultdict(list);detailed=defaultdict(list);paired=defaultdict(dict)
        for path,checksum in summary['chunk_checksums'].items():
            if sha(path)!=checksum:raise ValueError('audited chunk changed')
            for row in json.loads(Path(path).read_text()):
                p=pairs[row['pair_id']];r=cases[p['recipient']]['record'];b=replays[p['id']]
                original=r['expected_answer'];donor=cases[p['donor']]['record']['expected_answer'];target=row['target_answer'];answer_ids=data['answer_token_ids']
                measure=dict(cf_correct=row['first_token']==answer_ids[str(target)],cf_before=b['first_token']==answer_ids[str(target)],
                    recipient_correct=row['first_token']==answer_ids[str(original)],recipient_before=b['first_token']==answer_ids[str(original)],
                    donor_adoption=row['first_token']==answer_ids[str(donor)],donor_before=b['first_token']==answer_ids[str(donor)],
                    changed=row['first_token']!=b['first_token'],logodds_change=(row['donor_logprob']-row['recipient_logprob'])-(b['digit_logprobs'][donor-1]-b['digit_logprobs'][original-1]))
                group=(row['layer'],row['condition']);groups[group].append(measure)
                detailed[group+(r['instruction'],r['source_form'],r['mapping'],r['query'])].append(measure)
                paired[group+(r['source'].rsplit('\n',1)[0],r['instruction'])][r['query']]=measure
        def aggregate(key,values):
            return dict(group=list(key),n=len(values),**{k:sum(v[k] for v in values) for k in values[0]})
        aggregate_rows=[aggregate(k,v) for k,v in sorted(groups.items())]
        detailed_rows=[aggregate(k,v) for k,v in sorted(detailed.items())]
        paired_groups=defaultdict(list)
        for key,queries in paired.items():
            if set(queries)!={0,1}:raise ValueError('paired-output group incomplete')
            paired_groups[key[:2]].append(dict(both_cf_correct=all(m['cf_correct'] for m in queries.values()),
                both_cf_before=all(m['cf_before'] for m in queries.values()),both_original_correct=all(m['recipient_correct'] for m in queries.values())))
        result.update(aggregate=aggregate_rows,intervention_cells=detailed_rows,paired_query_outputs=[aggregate(k,v) for k,v in sorted(paired_groups.items())],
                      intervention_forwards=summary['intervention_forwards'],maximum_relative_norm_error=checked['maximum_relative_norm_error'])
        lines+=['The primary block 8 candidate was selected from the prior study. Blocks 4 and 12 measure sensitivity; block 31 checks software controls. Fresh numbers use familiar templates and do not test structural generalization.',
                '', 'Both-copies transfers preserve the full donor value multiset. Single-copy semantic substitutions change one final variable only. Wrong-version directions are norm matched; their oracle describes a substituted assignment result, not a guaranteed neural representation.',
                '', '| Block | Condition | Semantic target before → after | Donor answer before → after | Mean donor log-odds change |',
                '|---:|---|---:|---:|---:|']
        for row in aggregate_rows:
            layer,condition=row['group'];n=row['n']
            lines.append(f"| {layer} | {condition} | {row['cf_before']}/{n} → {row['cf_correct']}/{n} | {row['donor_before']}/{n} → {row['donor_adoption']}/{n} | {row['logodds_change']/n:+.3f} |")
        lines+=['','All instruction/order/mapping/query cells and paired-query output counts are retained in the review artifact. Paired outputs do not identify stored states. Adoption is always compared with unpatched replay to avoid mistaking pre-existing errors for transfer.',
                '',f"{summary['intervention_forwards']:,} intervention forwards; maximum effective BF16 norm mismatch {checked['maximum_relative_norm_error']:.3%} (registered tolerance {config['norm_tolerance']:.0%})."]
        fig,axes=plt.subplots(1,len(config['layers']),figsize=(16,7),sharey=True)
        for layer,ax in zip(config['layers'],axes):
            selected={r['group'][1]:r for r in aggregate_rows if r['group'][0]==layer}
            ys=[(selected[c]['cf_correct']-selected[c]['cf_before'])/selected[c]['n'] for c in CONDITIONS]
            ax.barh(range(len(CONDITIONS)),ys);ax.axvline(0,color='k',linewidth=.5)
            ax.set(yticks=range(len(CONDITIONS)),yticklabels=CONDITIONS,title=f'Block {layer}',xlabel='Semantic target accuracy change')
    figure=Path(config['figure']);figure.parent.mkdir(parents=True,exist_ok=True)
    fig.tight_layout();fig.savefig(figure);fig.savefig(figure.with_suffix('.png'),dpi=150);plt.close(fig)
    result['figure']=str(figure);result['figure_sha256']=sha(figure)
    lines+=['',f'![Registered controls]({figure.name})','']
    immutable(config['report'],('\n'.join(lines)).encode())
    immutable(config['review_artifact'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status=result['status'],report=config['report'],review_artifact=config['review_artifact'])
