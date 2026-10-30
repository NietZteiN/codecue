"""Fresh greedy answers on the balanced overnight discovery subset."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time

import numpy as np

from . import relationship_capture as base
from . import overnight_relationship_capture as capture
from .datasets import digest
from .interpreter import execute

ROLE='discovery_overnight_relationship_behavior_v1'
MAX_RESPONSES=32*1024**2


def protocol():
    return dict(selection='all source rows with numeric_draw == 0',do_sample=False,
        max_new_tokens=12,use_cache=True,parser='full signed decimal integer with whitespace only',
        uncertainty='nine whole development components; computed-minus-literal matched format pairs',
        bootstrap_draws=2000,bootstrap_seed=117)


def _config(config):
    required={'evaluation_role','capture_config','capture_config_sha256','declared_plan','declared_plan_sha256','generation_batch_size','run_dir','report'}
    if not isinstance(config,dict) or set(config)!=required or config.get('evaluation_role')!=ROLE:
        raise ValueError('exact overnight discovery behavior configuration required')
    for key in ('capture_config_sha256','declared_plan_sha256'):
        if not isinstance(config[key],str) or not re.fullmatch('[0-9a-f]{64}',config[key]):raise ValueError('explicit SHA256 required')
    for key in ('capture_config','declared_plan','run_dir','report'):base._safe(config[key])
    if type(config['generation_batch_size']) is not int or config['generation_batch_size']<1:
        raise ValueError('positive declared generation batch size required')
    out,report=Path(config['run_dir']).resolve(),Path(config['report']).resolve()
    reserved={out/name for name in ('manifest.json','registration.json','summary.json','responses.jsonl','completion_manifest_v1.json')}
    if (report.suffix!='.md' or report==out or report in reserved or any(p in report.parents for p in reserved)
            or out in Path(config['capture_config']).resolve().parents):
        raise ValueError('distinct behavior report/source/output paths required')
    if report in {Path(config['declared_plan']).resolve(),Path(config['capture_config']).resolve()}:
        raise ValueError('behavior report cannot replace declared inputs')


def parse_integer(text):
    if not isinstance(text,str) or not re.fullmatch(r'\s*[+-]?\d+\s*',text,flags=re.ASCII):return None
    return int(text)


def select(cases):
    selected=[case for case in cases if case['record']['numeric_draw']==0]
    if (not selected or any(c['record']['split'] not in ('train','development') or c['record']['condition']!='neutral' for c in selected)
            or len({c['record']['id'] for c in selected})!=len(selected)):
        raise ValueError('unique neutral discovery behavior cases required')
    return selected


def _inputs(config):
    _config(config)
    plan=base._bytes(config['declared_plan'],1024**2)
    if hashlib.sha256(plan).hexdigest()!=config['declared_plan_sha256']:raise ValueError('overnight plan changed')
    cap=base._json(config['capture_config'],config['capture_config_sha256'])
    preflight,cases=capture.inputs(cap)
    out,source=Path(config['run_dir']).resolve(),Path(cap['run_dir']).resolve()
    if out==source or out in source.parents or source in out.parents or source==Path(config['report']).resolve() or source in Path(config['report']).resolve().parents:
        raise ValueError('behavior outputs cannot overlap capture preparation')
    return cap,preflight,select(cases)


def _journal(path,value):
    capture._journal(path,value)


def _replace_owned(path,payload):
    """Mutable owned response repair; caller preserves original bytes first."""
    path=base._safe(path)
    if path.is_symlink():raise ValueError('owned response file must not be a symbolic link')
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.'+path.name+'.',suffix='.pending',delete=False) as stream:
            temporary=Path(stream.name);stream.write(payload);stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if temporary is not None and temporary.exists():temporary.unlink()


def _pin(path):
    return dict(path=str(path),sha256=base._sha(path),bytes=Path(path).stat().st_size)


def read_responses(path,cases,*,repair=False):
    """Accept an exact committed prefix; preserve any interrupted tail before repair."""
    path=Path(path)
    if not path.exists():return []
    if path.is_symlink():raise ValueError('response artifact must not be a symbolic link')
    data=base._bytes(path,MAX_RESPONSES);rows=[];committed=0
    for i,line in enumerate(data.splitlines(keepends=True)):
        try:row=json.loads(line)
        except (ValueError,UnicodeError):
            if not repair or line.endswith(b'\n') or i!=len(data.splitlines())-1:
                raise ValueError('malformed committed behavior response')
            backup=path.with_name('responses_interrupted_'+hashlib.sha256(data).hexdigest()[:16]+'.bin')
            base._publish(backup,data)
            _replace_owned(path,data[:committed]);break
        if len(rows)>=len(cases):raise ValueError('extra behavior response')
        record=cases[len(rows)]['record'];expected=execute(record['canonical_source'])['expected_answer']
        if (any(row.get(key)!=record[key] for key in ('id','split','component_id','numeric_seed','numeric_draw','source_form','query_slot','format_pair_id'))
                or row.get('parsed')!=parse_integer(row.get('raw_response'))
                or row.get('expected_answer')!=expected or row.get('correct')!=(row.get('parsed')==expected)
                or row.get('split')!=record['split'] or row.get('source_form')!=record['source_form']
                or row.get('format_pair_id')!=record['format_pair_id']):
            raise ValueError('behavior response source/order/score identity differs')
        tokens=row.get('output_token_ids')
        if not isinstance(tokens,list) or len(tokens)>12 or any(type(t) is not int or t<0 for t in tokens):
            raise ValueError('bounded generated behavior token IDs required')
        rows.append(row);committed+=len(line)
    if repair and rows and path.read_bytes() and not path.read_bytes().endswith(b'\n'):
        with path.open('ab') as stream:stream.write(b'\n');stream.flush();os.fsync(stream.fileno())
    return rows


def summarize(rows):
    groups=defaultdict(list)
    for row in rows:
        for key in [('overall',),('source_form',row['source_form']),('query',row['source_form'],str(row['query_slot'])),
                ('split',row['split'],row['source_form']),('numeric_seed',str(row['numeric_seed']),row['source_form'])]:groups[key].append(row)
    cells={'/'.join(key):dict(rows=len(values),accuracy=sum(v['correct'] for v in values)/len(values),
        invalid_fraction=sum(v['parsed'] is None for v in values)/len(values)) for key,values in groups.items()}
    pairs=defaultdict(dict)
    for row in rows:
        if row['split']=='development' and row['query_slot']==0:pairs[row['format_pair_id']][row['source_form']]=row
    deltas=defaultdict(list)
    for variants in pairs.values():
        if set(variants)!={'literal','computed'}:raise ValueError('complete matched behavior format pairs required')
        a,b=variants['literal'],variants['computed']
        if a['expected_answer']!=b['expected_answer'] or a['component_id']!=b['component_id']:
            raise ValueError('matched behavior states/components differ')
        deltas[a['component_id']].append(int(b['correct'])-int(a['correct']))
    comparison=None
    if deltas:
        names=sorted(deltas);means=np.array([np.mean(deltas[name]) for name in names])
        if len(names)!=9:raise ValueError('nine development components required')
        draws=np.random.default_rng(117).integers(0,9,size=(2000,9))
        comparison=dict(contrast='computed_minus_literal',mean=float(means.mean()),
            conditional_group_bootstrap_95=np.quantile(means[draws].mean(axis=1),[.025,.975]).tolist(),
            development_components=names,matched_pairs=sum(map(len,deltas.values())),
            bootstrap_seed=117,draws=2000,refits=0,multiplicity_adjusted=False)
    return dict(cells=cells,computed_literal=comparison)


def _generate(tokenizer,model,cases):
    import torch
    encoded=tokenizer([case['prompt'] for case in cases],add_special_tokens=False,padding=True,return_tensors='pt')
    for i,case in enumerate(cases):
        if encoded.input_ids[i][encoded.attention_mask[i].bool()].tolist()!=case['input_token_ids']:
            raise ValueError('behavior tokens differ from prepared capture inputs')
    encoded=encoded.to(model.device);width=encoded.input_ids.shape[1]
    with torch.inference_mode():
        outputs=model.generate(**encoded,do_sample=False,max_new_tokens=12,use_cache=True,
            logits_to_keep=1,pad_token_id=tokenizer.pad_token_id)
    eos=model.generation_config.eos_token_id
    if eos is None:eos=tokenizer.eos_token_id
    eos=set(eos if isinstance(eos,list) else [eos])
    result=[]
    for ids in outputs[:,width:].cpu().tolist():
        end=next((i+1 for i,value in enumerate(ids) if value in eos),len(ids));ids=ids[:end]
        result.append((tokenizer.decode(ids,skip_special_tokens=True),ids))
    return result


def run(config):
    from .confidence import _run_lock
    _config(config);base._slurm();source=base._current_source(config)
    cap,preflight,cases=_inputs(config);folder=Path(config['run_dir']);folder.mkdir(parents=True,exist_ok=True)
    with _run_lock(folder):
        if (folder/'completion_manifest_v1.json').exists():return audit(config)
        identity=dict(evaluation_role=ROLE,config=config,config_hash=digest(config),source=source,
            capture_preflight_source=preflight['source'],prepared_sha256=preflight['prepared_sha256'],
            case_ids_sha256=digest([c['record']['id'] for c in cases]),cases=len(cases),protocol=protocol())
        base._put(folder/'registration.json',identity)
        path=folder/'manifest.json';manifest=base._json(path) if path.exists() else {'identity':identity,'attempts':[]}
        if manifest['identity']!=identity:raise ValueError('behavior resume identity differs')
        response_path=folder/'responses.jsonl';rows=read_responses(response_path,cases,repair=True)
        for attempt in manifest['attempts']:
            if 'status' not in attempt:attempt['status']='interrupted'
        attempt=dict(slurm_job_id=os.environ['SLURM_JOB_ID'],prefill_cases_attempted=0,generation_calls=0,model_loaded=False)
        manifest['attempts'].append(attempt);manifest['status']='started';_journal(path,manifest)
        started=time.monotonic()
        try:
            if len(rows)<len(cases):
                tokenizer,model=capture.load_models(cap,max_prompt_tokens=max(len(c['input_token_ids']) for c in cases))
                attempt['model_loaded']=True;_journal(path,manifest)
                batch=config['generation_batch_size']
                import torch
                torch.cuda.empty_cache()
                free,_=torch.cuda.mem_get_info();m=model.config
                kv=2*m.num_hidden_layers*m.num_key_value_heads*(m.hidden_size//m.num_attention_heads)*2*batch*(max(len(c['input_token_ids']) for c in cases)+12)
                margin=(2 if m.hidden_size==4096 else 4)*1024**3
                attempt['generation_memory_review']={'driver_free_bytes':free,'kv_cache_estimate_bytes':kv,'working_margin_bytes':margin}
                _journal(path,manifest)
                if free<kv+margin:raise ValueError('allocated GPU lacks declared generation KV/working memory; cohort and batch unchanged')
                from .gpu_telemetry import UUIDMonitor
                with UUIDMonitor() as monitor:
                    for first in range(len(rows),len(cases),batch):
                        part=cases[first:first+batch];attempt['prefill_cases_attempted']+=len(part);attempt['generation_calls']+=1
                        _journal(path,manifest)
                        generated=_generate(tokenizer,model,part)
                        if len(generated)!=len(part):raise ValueError('complete generated behavior batch required')
                        with response_path.open('ab') as stream:
                            for case,(text,tokens) in zip(part,generated):
                                record=case['record'];truth=execute(record['canonical_source'])['expected_answer'];parsed=parse_integer(text)
                                row={key:record[key] for key in ('id','split','component_id','numeric_seed','numeric_draw','source_form','query_slot','format_pair_id')}
                                row.update(raw_response=text,output_token_ids=tokens,parsed=parsed,expected_answer=truth,correct=parsed==truth)
                                stream.write((json.dumps(row,sort_keys=True)+'\n').encode());rows.append(row)
                            stream.flush();os.fsync(stream.fileno())
                        print(f'overnight behavior {len(rows)}/{len(cases)}',flush=True)
                    attempt['gpu']=monitor.summary()
            attempt.update(status='complete',wall_seconds=time.monotonic()-started);manifest['status']='complete';_journal(path,manifest)
            queries=sum(a['prefill_cases_attempted'] for a in manifest['attempts'])
            if len(rows)!=len(cases) or queries<len(cases):raise ValueError('complete behavior coverage/attempt accounting required')
            result=dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
                model=cap['model'],cases=len(rows),new_model_queries=queries,generated_responses=len(rows),
                metrics=summarize(rows),responses=_pin(response_path),protocol=protocol(),
                generated_holdouts_opened=False,limitation='Adaptive discovery on reused structural components. No causal mechanism or confirmatory claim. Literal/computed formats also differ in tokens and operations.')
            base._put(folder/'summary.json',result)
            text=['# Overnight relationship behavior','',result['limitation'],'',f"{len(rows):,} exact generated responses; {queries:,} prefill attempts.",'',
                '| Cell | Cases | Accuracy | Invalid |','|---|---:|---:|---:|']
            for name,m in result['metrics']['cells'].items():text.append(f"| {name} | {m['rows']} | {100*m['accuracy']:.3f}% | {100*m['invalid_fraction']:.3f}% |")
            text+=['','Computed-minus-literal DEV comparison: `'+json.dumps(result['metrics']['computed_literal'],sort_keys=True)+'`','']
            base._publish(config['report'],'\n'.join(text).encode())
            base._put(folder/'completion_manifest_v1.json',dict(status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),source=source,
                artifacts={k:_pin(p) for k,p in {'registration':folder/'registration.json','manifest':path,'summary':folder/'summary.json','responses':response_path,'report':Path(config['report'])}.items()},
                cases=len(rows),new_model_queries=queries,generated_responses=len(rows),generated_holdouts_opened=False))
            return result
        except BaseException as exc:
            attempt.update(status='failed',error=f'{type(exc).__name__}: {exc}',wall_seconds=time.monotonic()-started)
            manifest['status']='failed';_journal(path,manifest);raise


def audit(config):
    _config(config);cap,preflight,cases=_inputs(config);folder=Path(config['run_dir'])
    receipt=base._json(folder/'completion_manifest_v1.json');base._verify_source(config,receipt['source'])
    expected={'registration':folder/'registration.json','manifest':folder/'manifest.json','summary':folder/'summary.json','responses':folder/'responses.jsonl','report':Path(config['report'])}
    if (receipt.get('status')!='complete_exploratory' or receipt.get('evaluation_role')!=ROLE
            or receipt.get('config_hash')!=digest(config) or set(receipt.get('artifacts',{}))!=set(expected)
            or receipt.get('cases')!=len(cases) or receipt.get('generated_holdouts_opened') is not False):raise ValueError('matching complete behavior receipt required')
    for key,path in expected.items():
        if receipt['artifacts'][key]!=_pin(path):raise ValueError('immutable behavior artifact changed')
    rows=read_responses(expected['responses'],cases)
    summary=base._json(expected['summary']);manifest=base._json(folder/'manifest.json')
    registration=base._json(expected['registration'])
    queries=sum(a['prefill_cases_attempted'] for a in manifest['attempts'])
    if (registration.get('config')!=config or registration.get('config_hash')!=digest(config)
            or registration.get('source')!=receipt['source'] or registration.get('protocol')!=protocol()
            or registration.get('prepared_sha256')!=preflight['prepared_sha256']
            or registration.get('capture_preflight_source')!=preflight['source']
            or registration.get('case_ids_sha256')!=digest([c['record']['id'] for c in cases])
            or registration.get('cases')!=len(cases)
            or manifest.get('identity')!=registration or manifest.get('status')!='complete'
            or summary.get('status')!='complete_exploratory' or summary.get('evaluation_role')!=ROLE
            or summary.get('config_hash')!=digest(config) or summary.get('source')!=receipt['source']
            or summary.get('generated_holdouts_opened') is not False
            or summary.get('cases')!=len(cases) or summary.get('protocol')!=protocol()
            or summary.get('model')!=cap['model'] or summary.get('responses')!=_pin(expected['responses'])
            or len(rows)!=len(cases) or summary.get('metrics')!=summarize(rows) or summary.get('new_model_queries')!=queries
            or receipt.get('new_model_queries')!=queries or queries<len(cases)
            or summary.get('generated_responses')!=len(rows) or receipt.get('generated_responses')!=len(rows)):
        raise ValueError('behavior coverage/metrics/accounting differs')
    return summary
