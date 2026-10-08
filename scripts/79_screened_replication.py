#!/usr/bin/env python
"""Screen fresh names before a fixed, independent len-to-sum replication."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from codecue.config import DATA_DIR, OUT_DIR, RESULTS_DIR, model_entry
from codecue.generator import Instance, evaluate, execute, read_jsonl, render, sample_program
from codecue.lures import NEUTRAL_NAMES
from codecue.probe_data import program_key
from codecue.prompts import build_prompt, demos, parse_answer, value_written
from codecue.round6 import select_identifiers

MANIFEST = ROOT.parent/'probing/log/round6_2026-10-03/manifest.json'
BASE = OUT_DIR/'round6_identifiers'


def write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp'); temp.write_text(json.dumps(data,indent=2)+'\n'); temp.replace(path)


def protocol():
    return json.loads(MANIFEST.read_text())['identifier_replication']


def fresh_programs(n=200):
    """Select computations without reading any behavioral outcomes or gate scores."""
    excluded = {program_key(x) for p in (DATA_DIR/'L5').glob('*.jsonl') for x in read_jsonl(p)}
    excluded |= {program_key(x) for seed in (7,11,13) for x in demos(5,seed,'trace')}
    rng=random.Random(61003)
    selected=[]
    for attempt in range(300000):
        prog=sample_program(5,rng)
        if prog.stmt('v1').op!='len':
            continue
        values=evaluate(prog); lure=sum(prog.xs)
        forbidden=set(values.values()) | set(prog.xs) | prog.constants()
        if lure not in range(10) or lure in forbidden:
            continue
        names=dict(zip(prog.roles,rng.sample(NEUTRAL_NAMES,len(prog.roles))))
        key=json.dumps({'xs':list(prog.xs),'stmts':[asdict(s) for s in prog.stmts],'query':prog.query},sort_keys=True)
        if key in excluded:
            continue
        excluded.add(key)
        vals=execute(prog,names)
        if vals['v1']!=len(prog.xs) or execute(prog,names,{'v1':'sum(xs)'})['v1']!=lure:
            raise ValueError('executable label check failed')
        selected.append({'program_key':key,'names':names,'xs':list(prog.xs),
                         'stmts':[asdict(s) for s in prog.stmts], 'query':prog.query,
                         'values':{r:vals[r] for r in prog.roles},'answer':vals['return'],'lure':lure,
                         'program':render(prog,names)})
        if len(selected)==n:
            # Stmt.args is a tuple in memory and a list in JSON. Return the persisted
            # representation so rerun and collector comparisons are stable.
            return json.loads(json.dumps(selected))
    raise ValueError(f'only {len(selected)}/{n} fresh legal programs after fixed attempt budget')


def prepare():
    path=BASE/'fresh_programs.json'
    data={'seed':61003,'n':200,'programs':fresh_programs()}
    if path.exists() and json.loads(path.read_text())!=data:
        raise ValueError('existing replication program list differs')
    write(path,data); print('prepared',path,flush=True)


def screen(model_key):
    from codecue.models import load_model
    spec=importlib.util.spec_from_file_location('original_gate',ROOT/'scripts/12_lure_gate.py')
    gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
    cfg=protocol(); path=BASE/'screen'/f'{model_key}.json'
    signature=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
    if path.exists():
        old=json.loads(path.read_text())
        if old.get('complete') and old['protocol_signature']==signature:
            print('skip',path,flush=True); return
        raise ValueError('inconsistent existing name-screen result')
    tok,model=load_model(model_entry(model_key)['hf_id'])
    contexts={'canonical':'def f(xs):\n    {n} = ',
              'calculate':'def calculate(xs):\n    {n} = ',
              'process':'def process_values(xs):\n    {n} = '}
    result={'model':model_key,'protocol_signature':signature,'contexts':contexts,'complete':False}
    for context,prefix in contexts.items():
        result[context]={}
        for name in cfg['candidates']+['v','w','zz']:
            scores={op:gate.logprob(tok,model,prefix.format(n=name),continuation)
                    for op,continuation in gate.CANDS['list'].items()}
            if not all(__import__('math').isfinite(x) for x in scores.values()):
                raise ValueError('nonfinite gate score')
            result[context][name]={'scores':scores,'argmax':max(scores,key=scores.get),
                                   'name_tokens':tok(name,add_special_tokens=False)['input_ids']}
        print(model_key,context,'screen complete',flush=True)
    result['complete']=True; write(path,result)


def freeze():
    cfg=protocol()
    gates={model:json.loads((BASE/'screen'/f'{model}.json').read_text()) for model in cfg['panel']}
    if not all(g['complete'] for g in gates.values()):
        raise ValueError('incomplete meaning-screen panel')
    names,scores=select_identifiers(gates,cfg['panel'],cfg['candidates'])
    data={'complete':True,'selected_names':names,'scores':scores,'panel':cfg['panel'],
          'threshold':.8,'selection':'first three passing names in fixed candidate order; no behavioral outcomes',
          'screen_sha256':{m:hashlib.sha256((BASE/'screen'/f'{m}.json').read_bytes()).hexdigest() for m in cfg['panel']}}
    path=BASE/'frozen_names.json'
    if path.exists() and json.loads(path.read_text())!=data:
        raise ValueError('frozen name set changed')
    write(path,data)
    write(RESULTS_DIR/'summary/round6_identifier_screen.json',data)
    print('frozen names',names if names else 'NONE: replication unavailable',flush=True)


def instances(names):
    from codecue.generator import Program, Stmt
    data=json.loads((BASE/'fresh_programs.json').read_text())
    rows=[]
    for index,row in enumerate(data['programs']):
        prog=Program(5,tuple(row['xs']),tuple(Stmt(**s) for s in row['stmts']),row['query'])
        set_id=f'R6-L5-{index:04d}'
        for name in [None]+names:
            naming={**row['names'],**({'v1':name} if name else {})}
            vals=execute(prog,naming)
            if {r:vals[r] for r in prog.roles}!=row['values'] or vals['return']!=row['answer']:
                raise ValueError('renaming changed executed values')
            rows.append(Instance(id=f'{set_id}-{name or "neutral"}',set_id=set_id,level=5,
                condition='incongruent' if name else 'neutral',target='v1' if name else None,
                names=naming,xs=row['xs'],program=render(prog,naming),values=row['values'],
                answer=row['answer'],lure=row['lure'] if name else None,lure_name=name,
                query=row['query'],distractor=None,stmts=row['stmts']))
    return rows


def run(model_key):
    from codecue.models import load_model,generate_free
    cfg=protocol(); frozen=json.loads((BASE/'frozen_names.json').read_text())
    names=frozen['selected_names']
    if not names:
        write(BASE/'runs'/model_key/'unavailable.json',{'status':'unavailable','reason':'no candidate passed the fixed panel meaning gate'})
        print('no gated names; skipped behavioral replication',flush=True); return
    rows=instances(names); tok,model=load_model(model_entry(model_key)['hf_id'])
    for seed in cfg['demo_seeds']:
        for fmt in cfg['formats']:
            path=BASE/'runs'/model_key/f's{seed}'/f'{fmt}.json'
            prompts=[build_prompt(x,fmt,demos(5,seed,fmt)) for x in rows]
            fingerprint=hashlib.sha256(json.dumps(prompts).encode()).hexdigest()
            if path.exists():
                saved=json.loads(path.read_text())
                if saved['complete'] and saved['fingerprint']==fingerprint and len(saved['records'])==len(rows):
                    print('skip',path,flush=True); continue
                raise ValueError('inconsistent existing replication')
            output=[]
            # Save batch progress for diagnosis; only the final complete file is collectible.
            for offset in range(0,len(rows),32):
                batch=rows[offset:offset+32]
                gens=generate_free(tok,model,prompts[offset:offset+32],160,8,stop_at_blank_line=True)
                if len(gens)!=len(batch):
                    raise ValueError('incomplete generated batch')
                for x,generation in zip(batch,gens):
                    output.append({'id':x.id,'set_id':x.set_id,'name':x.lure_name,'condition':x.condition,
                                   'true_value':x.values['v1'],'lure':x.lure,'written_value':value_written(generation,x.names['v1']),
                                   'answer':x.answer,'prediction':parse_answer(generation),'generation':generation,
                                   'program_key':program_key(x),'model':model_key,'seed':seed,'format':fmt})
                print(model_key,seed,fmt,len(output),'/',len(rows),flush=True)
            write(path,{'complete':True,'model':model_key,'demo_seed':seed,'format':fmt,'fingerprint':fingerprint,
                        'selected_names':names,'n_programs':200,'records':output,
                        'frozen_names_sha256':hashlib.sha256((BASE/'frozen_names.json').read_bytes()).hexdigest()})


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--stage',choices=['prepare','screen','freeze','run'],required=True)
    ap.add_argument('--model'); a=ap.parse_args()
    if a.stage in ('screen','run') and not a.model: ap.error('--model is required')
    {'prepare':prepare,'screen':lambda:screen(a.model),'freeze':freeze,'run':lambda:run(a.model)}[a.stage]()


if __name__=='__main__': main()
