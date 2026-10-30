"""Training-only prompt calibration, separate from the binding study protocols."""
from __future__ import annotations
import ast
import json
import random
import re
import time
from collections import Counter
from pathlib import Path
from .datasets import digest,read_jsonl,write_json
from .interpreter import execute,parse,python_oracle
from .registry import guarded

VARIANTS={
    'print_direct_v3':{'max_new_tokens':16,'stop_at_blank_line':True,'answer_mode':'integer'},
    'print_trace_v1':{'max_new_tokens':256,'stop_at_blank_line':False,'answer_mode':'final_answer_line'},
    'print_trace_long_v1':{'max_new_tokens':512,'stop_at_blank_line':False,'answer_mode':'final_answer_line'},
}


def choose_variant(summary):
    """Predeclared training-only gate; prefer the short protocol when both pass."""
    if not summary.get('complete'):
        return None
    by_name={r['variant']:r for r in summary['variants']}
    for name in ('print_direct_v3','print_trace_v1','print_trace_long_v1'):
        row=by_name.get(name,{})
        if (row.get('n')==12 and row.get('primitive_n')==8 and row.get('training_n')==4 and
            row.get('invalid')==0 and row.get('primitive_correct',0)>=7 and row.get('training_correct',0)>=2):
            return name
    return None


def select_bank(rows,per_family_sign=None):
    if any(r['split']!='train' or r['evaluation_role']!='prompt_calibration_only' for r in rows):
        raise ValueError('training-bank calibration cannot include other evaluation roles or splits')
    if per_family_sign is None:
        return rows
    if type(per_family_sign) is not int or per_family_sign<1:
        raise ValueError('positive integer required for bank subset')
    groups={}
    for row in rows:
        groups.setdefault((row['family'],row['answer_sign']),[]).append(row)
    keep=set()
    for group in groups.values():
        if len(group)<per_family_sign:
            raise ValueError('insufficient examples for balanced bank subset')
        keep.update(r['id'] for r in sorted(group,key=lambda r:r['id'])[:per_family_sign])
    return [r for r in rows if r['id'] in keep]


def printed_source(source):
    tree=ast.parse(source)
    if len(tree.body)==1 and isinstance(tree.body[0],ast.Expr):
        from .program_diagnostics import oracle_source
        oracle_source(source)  # restricted expression audit; no arbitrary calls or names
    else:
        tree=parse(source)
    if any(isinstance(stmt,ast.Assign) and stmt.targets[0].id=='print' for stmt in tree.body):
        raise ValueError('print readout requires an unshadowed builtin')
    tree.body[-1]=ast.Expr(value=ast.Call(func=ast.Name(id='print',ctx=ast.Load()),
                                       args=[tree.body[-1].value],keywords=[]))
    return ast.unparse(ast.fix_missing_locations(tree))


def parse_completion(raw,mode):
    if mode=='integer':
        from .behavior import parse_answer
        return parse_answer(raw)
    if mode!='final_answer_line':
        raise ValueError('unknown calibration answer mode')
    lines=[line.strip() for line in raw.splitlines() if line.strip()]
    found=re.fullmatch(r'Answer:\s*([+-]?\d+)',lines[-1],flags=re.IGNORECASE) if lines else None
    return int(found.group(1)) if found else None


def prompt(tokenizer,row,variant):
    source=printed_source(row['source'])
    if variant=='print_direct_v3':
        instruction='What does this Python 3 program print? Give only the signed integer output, without explanation.'
    elif variant in ('print_trace_v1','print_trace_long_v1'):
        instruction=('Work through this Python 3 program, tracking the assignments in order. '
                     'Explain briefly, then end with a line exactly in the form Answer: <integer> for the printed output.')
    else:
        raise ValueError('unknown calibration variant')
    messages=[{'role':'user','content':instruction+'\n\n```python\n'+source+'\n```'}]
    if variant=='print_direct_v3':
        messages.append({'role':'assistant','content':'Output:\n'})
        rendered=tokenizer.apply_chat_template(messages,tokenize=False,continue_final_message=True)
    else:
        rendered=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    from .model_adapter import normalize_prompt
    return normalize_prompt(tokenizer,rendered),source


@guarded
def run(config):
    from codecue.models import generate_free
    from .diagnostics import cases
    from .model_adapter import load
    from .registry import begin,finish
    variants=config['calibration']['variants']
    if not variants or len(set(variants))!=len(variants) or not set(variants)<=set(VARIANTS):
        raise ValueError('predeclare valid unique calibration variants')
    out,manifest=begin(config,'protocol_calibration')
    output=out/'responses.jsonl'
    if output.exists():
        raise ValueError('calibration output is immutable; inspect before repeating')
    started=time.monotonic()
    dataset_rows=read_jsonl(config['dataset'])
    case_source=config['calibration'].get('case_source')
    if case_source=='training_bank':
        if (manifest['identity']['dataset_manifest'].get('evaluation_role')!='prompt_calibration_only' or
            any(r['split']!='train' or r['evaluation_role']!='prompt_calibration_only' for r in dataset_rows)):
            raise ValueError('training-bank calibration cannot include other evaluation roles or splits')
        rows=[dict(r,kind='calibration_bank') for r in select_bank(dataset_rows,
              config['calibration'].get('per_family_sign_limit'))]
    elif case_source=='difficulty_ladder':
        from .ladder import load_plan,validate_rows,ROLE
        plan=load_plan(config)
        if (variants!=plan['variants']
                or manifest['identity']['dataset_manifest'].get('evaluation_role')!=ROLE
                or manifest['identity']['dataset_manifest'].get('plan_sha256')!=config['calibration']['ladder_plan_sha256']):
            raise ValueError('difficulty ladder plan differs from inference configuration or dataset')
        rows=[dict(r,kind='difficulty_ladder') for r in validate_rows(dataset_rows,plan)]
    elif case_source=='phase2_diagnostics':
        from .program_diagnostics import validate_rows,ROLE
        if manifest['identity']['dataset_manifest'].get('evaluation_role')!=ROLE:
            raise ValueError('phase-two diagnostic role mismatch')
        rows=[dict(r,kind='phase2_diagnostics') for r in validate_rows(dataset_rows,config['diagnostic_kind'])]
    elif case_source in (None,'fixed_suite'):
        rows=cases(dataset_rows)
    else:
        raise ValueError('unknown calibration case source')
    oracle=[]
    for first in range(0,len(rows),128):
        oracle+=python_oracle([r.get('oracle_source',r['source']) for r in rows[first:first+128]])
    if any(r['expected_answer']!=o['answer'] for r,o in zip(rows,oracle)):
        raise ValueError('independent oracle mismatch')
    tokenizer,model=load(config)
    actual_dtype=str(next(model.parameters()).dtype)
    planned=len(rows)*len(variants)
    completed=0
    for variant in variants:
        spec=VARIANTS[variant]
        for first in range(0,len(rows),config['batch_size']):
            batch=rows[first:first+config['batch_size']]
            rendered=[prompt(tokenizer,row,variant) for row in batch]
            prompts=[p for p,_ in rendered]
            ids=[tokenizer(p,add_special_tokens=False)['input_ids'] for p in prompts]
            if any(tokenizer(p)['input_ids']!=tokens or tokens.count(tokenizer.bos_token_id)!=1
                   for p,tokens in zip(prompts,ids)):
                raise ValueError('calibration generation tokenization mismatch')
            raw=generate_free(tokenizer,model,prompts,spec['max_new_tokens'],config['batch_size'],
                              stop_at_blank_line=spec['stop_at_blank_line'])
            with output.open('a') as stream:
                for row,text,(full_prompt,source),tokens in zip(batch,raw,rendered,ids):
                    prediction=parse_completion(text,spec['answer_mode'])
                    stream.write(json.dumps(dict(row,variant=variant,prompt=full_prompt,rendered_source=source,
                        input_token_ids=tokens,raw_response=text,prediction=prediction,
                        correct=prediction==row['expected_answer'],invalid=prediction is None,
                        generation_spec=spec,actual_model_dtype=actual_dtype,
                        completion_token_count_reencoded=len(tokenizer(text,add_special_tokens=False)['input_ids'])))+'\n')
            completed+=len(batch)
            print(f'calibration {variant}: {min(first+len(batch),len(rows))}/{len(rows)}',flush=True)
    observed=read_jsonl(output) if output.exists() else []
    summaries=[]
    for variant in variants:
        selected=[r for r in observed if r['variant']==variant]
        primitive=[r for r in selected if r['kind']=='primitive']
        training=[r for r in selected if r['kind'] in ('discovery_training','calibration_bank','difficulty_ladder','phase2_diagnostics')]
        good_primitive=sum(r['correct'] for r in primitive)
        good_training=sum(r['correct'] for r in training)
        invalid=sum(r['invalid'] for r in selected)
        entry={'variant':variant,'n':len(selected),'primitive_n':len(primitive),
                          'primitive_correct':good_primitive,'training_n':len(training),'training_correct':good_training,
                          'invalid':invalid,'promising_for_training_bank_only':len(selected)==12 and invalid==0
                          and good_primitive>=7 and good_training>=2}
        entry['families']={family:{'n':len(group),'correct':sum(r['correct'] for r in group),
                                   'invalid':sum(r['invalid'] for r in group)}
                           for family in sorted({r.get('family',r['kind']) for r in selected})
                           if (group:=[r for r in selected if r.get('family',r['kind'])==family])}
        summaries.append(entry)
    result={'complete':completed==planned,'model_experiment':True,'variants':summaries,
            'interpretation':'training-only calibration; explicit reasoning changes computation and is kept separate from short answers',
            'gate':('Fresh phase-two diagnostics use their own training/validation selection rule' if case_source=='phase2_diagnostics' else
                    'The separately hashed difficulty-ladder plan governs selection; the original bank gate remains unchanged'
                    if case_source=='difficulty_ladder' else
                    'At least 7/8 primitive and 2/4 training answers correct, all 12 parsed, only motivates a fresh training-bank check'),
            'heldout_outcomes_opened':False,'actual_model_dtype':actual_dtype}
    write_json(out/'summary.json',result)
    finish(out,manifest,time.monotonic()-started,'complete' if completed==planned else 'budget_limited',
           samples_completed=completed,samples_planned=planned)
    return result


def build_bank(path,seed=20261025,per_family=12):
    """Balanced-sign difficulty ladder, exclusively for further training calibration."""
    if not 3<=per_family<=12 or per_family%3:
        raise ValueError('calibration family size must be 3..12 and divisible by three')
    path=Path(path)
    if path.exists():
        raise ValueError('calibration bank is immutable')
    rng=random.Random(seed)
    families=('literal','addition','subtraction','overwrite','update','two_bindings','copy_dependency','interleaved')
    records=[]; seen=set(); attempts=0
    for family in families:
        for sign in (-1,0,1):
            accepted=0
            while accepted<per_family//3:
                attempts+=1
                if attempts>100000:
                    raise ValueError('calibration generator exhausted bounded proposals')
                a,b,c,d,e,f=[rng.randint(-12,12) for _ in range(6)]
                literal_target=f'v{rng.randrange(4)}'
                sources={'literal':f'{literal_target} = {a}\n{literal_target}',
                         'addition':f'v0 = {a} + {b}\nv0',
                         'subtraction':f'v0 = {a} - {b}\nv0',
                         'overwrite':f'v0 = {a}\nv0 = {b}\nv0',
                         'update':f'v0 = {a} + {b}\nv0 = v0 + {c}\nv0',
                         'two_bindings':f'v0 = {a} + {b}\nv1 = {c} - {d}\nv0 - v1',
                         'copy_dependency':f'v0 = {a}\nv1 = v0 + {b}\nv1',
                         'interleaved':f'v0 = {a}\nv1 = {b}\nv2 = {c}\nv3 = {d}\nv1 = v1 + {e}\nv0 = v0 - {f}\nv0 - v1 + v2 - v3'}
                source=sources[family]
                truth=execute(source)
                answer=truth['expected_answer']
                if (answer>0)-(answer<0)!=sign or source in seen:
                    continue
                seen.add(source); accepted+=1
                records.append(dict(id='calibration:'+digest(source)[:24],split='train',evaluation_role='prompt_calibration_only',
                    family=family,answer_sign=sign,seed=seed,source=source,expected_answer=answer,
                    execution_trace=truth['execution_trace'],independence='numeric variants share family structure'))
    oracle=python_oracle([r['source'] for r in records])
    if any(r['expected_answer']!=o['answer'] or [p['values'] for p in r['execution_trace']]!=o['trace']
           for r,o in zip(records,oracle)):
        raise ValueError('calibration bank Python mismatch')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in records))
    import hashlib
    result={'schema_version':1,'status':'validated','rows':len(records),'seed':seed,'per_family':per_family,
            'attempts':attempts,'split':'train','evaluation_role':'prompt_calibration_only',
            'independent_python_programs':len(records),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'family_counts':dict(Counter(r['family'] for r in records)),
            'limitations':'not a confirmatory set; family structures are repeated and calibrating on these outcomes consumes them'}
    write_json(path.with_suffix('.manifest.json'),result)
    return result
