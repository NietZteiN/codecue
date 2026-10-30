"""Fresh arithmetic-form and arithmetic-free binding diagnostics for phase two."""
from __future__ import annotations
import ast
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from .datasets import digest,read_jsonl,write_json,diagnostics
from .interpreter import execute,python_oracle

ROLE='phase2_diagnostics'


def without_trailing_distractor(source):
    """Remove only the generated dead trailing copy, preserving the query."""
    tree=ast.parse(source)
    if len(tree.body)>2:
        statement=tree.body[-2]
        query_names={node.id for node in ast.walk(tree.body[-1]) if isinstance(node,ast.Name)}
        if (isinstance(statement,ast.Assign) and len(statement.targets)==1
                and isinstance(statement.targets[0],ast.Name) and statement.targets[0].id=='distractor'
                and isinstance(statement.value,ast.Name) and 'distractor' not in query_names):
            del tree.body[-2]
    return ast.unparse(tree)


def oracle_source(source):
    tree=ast.parse(source)
    if len(tree.body)==1 and isinstance(tree.body[0],ast.Expr):
        result='expression_result = '+ast.unparse(tree.body[0].value)+'\nexpression_result'
        execute(result)
        return result
    execute(source)
    return source


def validate_rows(rows,kind):
    expected=192 if kind=='arithmetic_forms' else 384
    if len(rows)!=expected or len({r['id'] for r in rows})!=expected:
        raise ValueError('diagnostic dataset incomplete or duplicated')
    if any(r['split'] not in ('train','development') or r['evaluation_role']!=ROLE for r in rows):
        raise ValueError('diagnostics cannot include final-test rows')
    seen=set()
    for row in rows:
        canonical=ast.dump(ast.parse(row['source']))
        if canonical in seen:raise ValueError('duplicate diagnostic source')
        seen.add(canonical)
        source=oracle_source(row['source']);truth=execute(source)
        if (source!=row['oracle_source'] or truth['expected_answer']!=row['expected_answer']
                or truth['execution_trace']!=row['execution_trace']):
            raise ValueError('diagnostic oracle mismatch')
        if kind=='arithmetic_free' and any(isinstance(node,ast.BinOp) for node in ast.walk(ast.parse(row['source']))):
            raise ValueError('arithmetic-free binding contains arithmetic')
    return rows


def build(config):
    kind=config['diagnostic_kind'];path=Path(config['dataset'])
    if kind not in ('arithmetic_forms','arithmetic_free'):raise ValueError('unknown diagnostic kind')
    if path.exists() or path.with_suffix('.manifest.json').exists():raise ValueError('diagnostic dataset is immutable')
    rng=random.Random(config['seed']);rows=[];seen=set();prefix_seen=set();proposals=0;exclusions={}
    default_exclusions=('artifacts/binding/prompt_calibration_bank.jsonl','artifacts/binding/difficulty_ladder.jsonl')
    required=config.get('exclude_datasets',[])
    for file in dict.fromkeys((*default_exclusions,*required)):
        if not Path(file).exists():
            if file in required:raise ValueError('required diagnostic exclusion dataset is missing')
            continue
        excluded=read_jsonl(file)
        seen.update(ast.dump(ast.parse(r['source'])) for r in excluded)
        prefix_seen.update(ast.dump(ast.parse(without_trailing_distractor(r['source']))) for r in excluded)
        exclusions[file]=hashlib.sha256(Path(file).read_bytes()).hexdigest()
    def record(source,family,sign,replicate,group,**details):
        truth=execute(oracle_source(source))
        return dict(id='phase2:'+digest(source)[:24],source=source,oracle_source=oracle_source(source),
                    family=family,split='train' if replicate<4 else 'development',evaluation_role=ROLE,
                    answer_sign=sign,paired_group_id=group,replicate=replicate,seed=config['seed'],
                    expected_answer=truth['expected_answer'],execution_trace=truth['execution_trace'],
                    diagnostic_counterfactuals=diagnostics(source,truth) if len(ast.parse(source).body)>1 else [],**details)
    if kind=='arithmetic_forms':
        for op in ('+','-'):
            for sign in (-1,0,1):
                for rep in range(8):
                    target=sign*(1+rep%4)
                    while True:
                        proposals+=1
                        if proposals>100000:raise ValueError('diagnostic proposal cap')
                        a,b=[rng.choice([x for x in range(-12,13) if x]) for _ in range(2)]
                        intermediate=a+b if op=='+' else a-b
                        delta=target-intermediate
                        if abs(intermediate)>16 or not 1<=abs(delta)<=12:continue
                        tail=f'+ {delta}' if delta>0 else f'- {-delta}'
                        expression=f'({a} {op} {b}) {tail}'
                        sources={'expression':expression,'assignment':f'v0 = {expression}\nv0',
                                 'independent':f'v0 = {a} {op} {b}\nv1 = {intermediate} {tail}\nv1',
                                 'dependent':f'v0 = {a} {op} {b}\nv1 = v0 {tail}\nv1'}
                        keys=[ast.dump(ast.parse(s)) for s in sources.values()]
                        if any(key in seen for key in keys):continue
                        seen.update(keys);break
                    group=f'arithmetic:{op}:{sign}:{rep}'
                    rows.extend(record(s,form,sign,rep,group,operator=op,form=form) for form,s in sources.items())
    else:
        for family in ('copy_depth','overwrite_count'):
            for depth in (1,2,4,8):
                for load in (2,4):
                    for sign in (-1,0,1):
                        for rep in range(8):
                            target=sign*(1+rep%4)
                            while True:
                                proposals+=1
                                if proposals>100000:raise ValueError('diagnostic proposal cap')
                                pool=[x for x in range(-12,13) if x!=target]
                                values=rng.sample(pool,load)
                                values[0 if family=='copy_depth' else 1]=target
                                order=list(range(load));rng.shuffle(order)
                                lines=[f'v{i} = {values[i]}' for i in order]
                                query='v0'
                                if family=='copy_depth':
                                    previous='v0'
                                    for i in range(depth-1):
                                        query=f'v{load+i}';lines.append(f'{query} = {previous}');previous=query
                                else:
                                    for i in range(depth):
                                        # Final version always retrieves v1; earlier versions vary.
                                        donor=1 if i==depth-1 else rng.randrange(load)
                                        lines.append(f'v0 = v{donor}')
                                if rep%2:
                                    lines.append(f'distractor = v{load-1}')
                                source='\n'.join(lines+[query]);key=ast.dump(ast.parse(source))
                                if key in seen:continue
                                prefix=ast.dump(ast.parse(without_trailing_distractor(source)))
                                if config.get('unique_distractor_prefixes') and prefix in prefix_seen:continue
                                if execute(source)['expected_answer']!=target:continue
                                seen.add(key);prefix_seen.add(prefix);break
                            group=f'{family}:{depth}:{load}:{sign}:{rep}'
                            rows.append(record(source,family,sign,rep,group,depth=depth,available_bindings=load,
                                               query=query,query_followed_by_distractor=bool(rep%2)))
    validate_rows(rows,kind)
    for first in range(0,len(rows),128):
        batch=rows[first:first+128];actual=python_oracle([r['oracle_source'] for r in batch])
        if any(r['expected_answer']!=o['answer'] or [p['values'] for p in r['execution_trace']]!=o['trace'] for r,o in zip(batch,actual)):
            raise ValueError('independent Python diagnostic mismatch')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    manifest=dict(status='validated',rows=len(rows),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  evaluation_role=ROLE,diagnostic_kind=kind,seed=config['seed'],proposals=proposals,
                  independent_python_programs=len(rows),split_counts=dict(Counter(r['split'] for r in rows)),
                  family_counts=dict(Counter(r['family'] for r in rows)),
                  excluded_datasets=exclusions,unique_distractor_prefixes=bool(config.get('unique_distractor_prefixes')),
                  limitation='Numeric validation shares task structures with training; not a structural generalization experiment')
    write_json(path.with_suffix('.manifest.json'),manifest)
    return manifest


def summarize(config):
    from .calibration import parse_completion,VARIANTS
    root=Path(config['run_dir'])/'protocol_calibration'
    output=root/'diagnostic_decision.json'
    if output.exists():raise ValueError('diagnostic decision immutable')
    manifest=json.loads((root/'manifest.json').read_text());identity=manifest['identity']
    if identity['config']!=config or manifest['identity_hash']!=digest(identity):raise ValueError('diagnostic identity changed')
    rows=validate_rows(read_jsonl(config['dataset']),config['diagnostic_kind']);gold={r['id']:r for r in rows}
    variants=config['calibration']['variants'];path=root/'responses.jsonl'
    observed=read_jsonl(path) if path.exists() else []
    planned={(r['id'],v) for r in rows for v in variants};seen=set();cells=[]
    for r in observed:
        key=(r['id'],r['variant'])
        if key not in planned or key in seen:raise ValueError('diagnostic response IDs differ')
        seen.add(key);original=gold[r['id']]
        prediction=parse_completion(r['raw_response'],VARIANTS[r['variant']]['answer_mode'])
        if (r['prediction']!=prediction or r['correct']!=(prediction==original['expected_answer'])
                or any(r[k]!=original[k] for k in ('source','split','family','expected_answer','evaluation_role'))):
            raise ValueError('diagnostic response metadata or score mismatch')
    for variant in variants:
        for split in ('train','development'):
            for family in sorted({r['family'] for r in rows}):
                depths=(None,) if config['diagnostic_kind']=='arithmetic_forms' else (1,2,4,8)
                for depth in depths:
                    group=[r for r in observed if r['variant']==variant and r['split']==split and r['family']==family and (depth is None or r['depth']==depth)]
                    cells.append(dict(variant=variant,split=split,family=family,depth=depth,n=len(group),
                                      correct=sum(r['correct'] for r in group),invalid=sum(r['prediction'] is None for r in group)))
    complete=seen==planned and manifest['status']=='complete'
    families=('expression','assignment') if config['diagnostic_kind']=='arithmetic_forms' else ('copy_depth','overwrite_count')
    def passes(variant,split):
        required=[r for r in cells if r['variant']==variant and r['split']==split and r['family'] in families
                  and (config['diagnostic_kind']=='arithmetic_forms' or r['depth']==1)]
        return len(required)==2 and all(r['n']>=24 and r['correct']/r['n']>=.9 and r['invalid']/r['n']<=.05 for r in required)
    candidate=next((v for v in variants if passes(v,'train')),None) if complete else None
    validated=candidate is not None and passes(candidate,'development')
    result=dict(status='validated_for_discovery' if validated else 'failed_validation' if candidate else 'no_training_candidate' if complete else 'incomplete',
                selected_protocol=candidate if validated else None,training_candidate=candidate,complete=complete,
                queries_completed=len(seen),queries_planned=len(planned),cells=cells,identity_hash=manifest['identity_hash'],
                responses_sha256=hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None,
                heldout_outcomes_opened=False,
                rule='Prefer direct on training-only elementary cells >=90% correct and <=5% invalid; validate that choice on fresh numeric examples, no fallback after validation failure')
    write_json(output,result);return result
