"""Fresh, paired arithmetic/root-survival/copy-routing discovery sources.

The unit for full-context paired uncertainty is root initialization order, not
topology, lexical form, sign mirror, instruction or a reused baseline. Identical
control programs are emitted once with explicit logical memberships.
"""
from __future__ import annotations

import ast
from collections import Counter,defaultdict
import hashlib
from itertools import permutations
import json
from pathlib import Path
import random
import re

from .datasets import digest
from .interpreter import execute,python_oracle
from .programs import rename
from .relationship_programs import _safe_path,_python_validate,_json_bytes
from .relationship_capture import _publish
from .registry import code_identity

ROLE='discovery_computation_routing_isolation_v1'
FORMS=('literal','small','cancellation')
QUESTIONS=('arithmetic_only','roots_only','full_root','full_leaf')
DEPTHS=(1,2,4)
INSTRUCTIONS={
    'routing_output_v1':'What does this Python 3 program print? Give only the signed integer output, without explanation.',
    'routing_execute_v1':'Execute the Python 3 program in order. Return only the signed integer it prints.',
    'routing_value_v1':'Determine the integer printed by the final line of this Python 3 program. Respond with that integer only.',
}
LIMITATIONS=[
    'Fresh discovery diagnostic after the earlier failed arithmetic gates; not an untouched confirmatory experiment.',
    'There are 24 root-order clusters, split12TRAIN/12DEV. Three copy topologies per order are related, not72 independent families.',
    'Only the queried root is computed; other roots are literal distractors. All forms preserve every matched root/copy state and answer.',
    'Small and cancellation forms share binary operator and operand-sign pattern, but differ in operand magnitude, tokenization and cancellation extent.',
    'Full-root versus full-leaf queries share identical body and answer; they still differ in queried identifier, location and recency.',
    'Only literal arithmetic-only controls may be shared acrossTRAIN/DEV, and they are descriptive and excluded from prospective gates.',
    'Repeated control responses and logical memberships must not be treated as independent observations or as independent structural replications.',
    'No causal owner/version mechanism, model training, sealed final evaluation or unfamiliar-program prediction follows from this source preparation.',
]


def instruction_spec(variant):
    if variant not in INSTRUCTIONS:raise ValueError('unknown computation/routing instruction')
    return dict(max_new_tokens=16,stop_at_blank_line=True,answer_mode='integer')


def prompt(tokenizer,row,variant):
    instruction_spec(variant)
    from .calibration import printed_source
    from .model_adapter import normalize_prompt
    source=printed_source(row['source'])
    messages=[dict(role='user',content=INSTRUCTIONS[variant]+'\n\n```python\n'+source+'\n```'),
        dict(role='assistant',content='Output:\n')]
    rendered=tokenizer.apply_chat_template(messages,tokenize=False,continue_final_message=True)
    return normalize_prompt(tokenizer,rendered),source


def score_case(case,raw):
    row=case.get('record',case)
    prediction=int(raw.strip()) if isinstance(raw,str) and re.fullmatch(r'\s*[+-]?\d+\s*',raw,flags=re.ASCII) else None
    return dict(prediction=prediction,valid=prediction is not None,correct=prediction==row['expected_answer'])


def _generation(config):
    if not isinstance(config,dict) or config.get('evaluation_role')!=ROLE:
        raise ValueError('explicit computation/routing discovery role required')
    allowed={'evaluation_role','numeric_seeds','dataset','review','report','exclude_datasets'}
    seeds=config.get('numeric_seeds')
    if (set(config)-allowed or not isinstance(seeds,list) or len(seeds)!=3
            or any(type(seed)is not int or not 0<=seed<2**63 for seed in seeds) or len(set(seeds))!=3):
        raise ValueError('three distinct bounded numeric seeds and exact generation fields required')
    exclusions=config.get('exclude_datasets',[])
    if not isinstance(exclusions,list) or any(not isinstance(path,str) or not path for path in exclusions):
        raise ValueError('explicit source-only exclusion dataset paths required')
    return seeds


def _mapping(lexical):
    roots='root' if lexical==0 else 'datum';copies='copy' if lexical==0 else 'link'
    return {**{f'v{i}':f'{roots}_{chr(97+i)}' for i in range(4)},
            **{f'c{i}':f'{copies}_{chr(97+i)}' for i in range(4)}}


def _expression(target,form,operator,split,rng):
    if form=='literal':return str(target)
    magnitude=abs(target);sign=1 if target>0 else -1
    low,high=(1,16-magnitude) if form=='small' else (13,32-magnitude)
    parity=1 if split=='train' else 0
    candidates=[right for right in range(low,high+1) if right%2==parity and right!=magnitude]
    if not candidates:raise ValueError('matched one-operation source is infeasible')
    right=rng.choice(candidates);left=sign*(magnitude+right)
    right=sign*right*(-1 if operator=='add' else 1)
    return f'{left} {"+" if operator=="add" else "-"} {right}'


def _copies(order,depth):
    root=order[0];a,b,c=order[1:]
    if depth==1:return [f'c0 = v{a}',f'c1 = v{b}',f'c2 = v{c}',f'c3 = v{root}']
    if depth==2:return [f'c0 = v{root}',f'c1 = v{a}',f'c2 = v{b}','c3 = c0']
    return [f'c0 = v{root}','c1 = c0','c2 = c1','c3 = c2']


def make_rows(generation):
    seeds=_generation(generation);physical={};seen_states=set()
    for seed_index,seed in enumerate(seeds):
        for order_index,order in enumerate(permutations(range(4))):
            cluster='computation-root-order:'+''.join(map(str,order))
            split='train' if order_index%2==0 else 'development'
            rng=random.Random(digest([ROLE,seed,list(order),'initial_values']))
            magnitudes=tuple(rng.sample(range(1,9),4))
            while magnitudes in seen_states:magnitudes=tuple(rng.sample(range(1,9),4))
            seen_states.add(magnitudes)
            operator='add' if (order_index//2+seed_index)%2==0 else 'sub'
            root=order[0]
            for numeric_draw,sign in enumerate((1,-1)):
                values=tuple(sign*value for value in magnitudes);target=values[root]
                base=f'computation:{seed}:{cluster}:mirror{numeric_draw}'
                expressions={form:_expression(target,form,operator,split,
                    random.Random(digest([ROLE,seed,cluster,form,'operands']))) for form in FORMS}
                for lexical in (0,1):
                    mapping=_mapping(lexical);paired=base+f':lexical{lexical}'
                    for form in FORMS:
                        roots=[f'v{i} = {expressions[form] if i==root else values[i]}' for i in order]
                        for question in QUESTIONS:
                            for depth in ((0,) if question in ('arithmetic_only','roots_only') else DEPTHS):
                                if question=='arithmetic_only':lines=[f'v{root} = {expressions[form]}']
                                else:lines=list(roots)
                                if depth:lines+=_copies(order,depth)
                                query='c3' if question=='full_leaf' else f'v{root}'
                                canonical='\n'.join([*lines,query])
                                scope={node.id for node in ast.walk(ast.parse(canonical)) if isinstance(node,ast.Name)}
                                active_mapping={name:value for name,value in mapping.items() if name in scope}
                                source=rename(canonical,active_mapping)
                                topology='none' if depth==0 else f'depth{depth}'
                                logical=dict(id='computation-routing-logical:'+digest([base,lexical,form,question,depth])[:24],
                                    base_id=base,paired_group_id=paired,root_order_cluster=cluster,
                                    structural_unit=cluster+':'+topology,split=split,form=form,question=question,
                                    operator=operator,answer_sign=sign,queried_root_slot=root,topology=topology,chain_depth=depth,
                                    numeric_seed=seed,numeric_draw=numeric_draw,lexical_realization=lexical,
                                    root_order=list(order),target_value=target)
                                if source not in physical:
                                    truth=execute(source)
                                    physical[source]=dict(logical,id='computation-routing:'+digest([ROLE,source])[:24],
                                        evaluation_role=ROLE,condition='neutral',control_kind='primary',family='computation_routing_isolation',
                                        source=source,oracle_source=source,canonical_source=canonical,rename_map=active_mapping,
                                        expected_answer=truth['expected_answer'],execution_trace=truth['execution_trace'],logical_memberships=[])
                                row=physical[source]
                                if row['expected_answer']!=target:raise ValueError('matched source has inconsistent target')
                                row['logical_memberships'].append(logical)
    rows=list(physical.values())
    for row in rows:
        splits=sorted({member['split'] for member in row['logical_memberships']})
        row['logical_splits']=splits;row['shared_control_across_splits']=len(splits)>1
        row['split']='train' if 'train' in splits else 'development'
        if len(splits)>1 and not(row['form']=='literal' and row['question']=='arithmetic_only'):
            raise ValueError('nonliteral source shared acrossTRAIN/DEV')
    return rows


def analysis_rows(unique_rows):
    result=[]
    for row in unique_rows:
        for member in row['logical_memberships']:
            result.append({**{k:v for k,v in row.items() if k!='logical_memberships'},**member,
                'source_id':row['id'],'capture_id':row['id'],'physical_split':row['split']})
    return result


def _validation(rows,generation=None,independent=False):
    if not isinstance(rows,list) or not rows or len(rows)>10000:raise ValueError('bounded nonempty unique discovery sources required')
    if generation is None:
        seeds=sorted({m['numeric_seed'] for row in rows for m in row.get('logical_memberships',[])})
        generation=dict(evaluation_role=ROLE,numeric_seeds=seeds)
    if rows!=make_rows(generation):raise ValueError('source rows differ from the fixed deterministic discovery factorial')
    logical=analysis_rows(rows)
    if len(logical)!=6912 or len({row['id'] for row in rows})!=len(rows) or len({row['id'] for row in logical})!=6912:
        raise ValueError('unique physical and complete logical records required')
    sources={};clusters=defaultdict(set);groups=defaultdict(dict);programs=set()
    for row in rows:
        if row['evaluation_role']!=ROLE or row['split'] not in ('train','development'):raise ValueError('discovery source role/split required')
        truth=execute(row['oracle_source'])
        if truth['expected_answer']!=row['expected_answer'] or truth['execution_trace']!=row['execution_trace']:
            raise ValueError('stored source oracle differs')
        if row['source'] in sources:raise ValueError('duplicate physical source')
        sources[row['source']]=row['id'];programs.update((row['source'],row['canonical_source']))
    gate=defaultdict(set)
    for row in logical:
        clusters[row['root_order_cluster']].add(row['split'])
        key=(row['paired_group_id'],row['form'],row['chain_depth'])
        groups[key][row['question']]=row
        if not(row['form']=='literal' and row['question']=='arithmetic_only'):
            gate[(row['split'],row['form'],row['question'],row['operator'],row['answer_sign'])].add(row['source_id'])
    if len(clusters)!=24 or any(len(v)!=1 for v in clusters.values()):raise ValueError('root order clusters must remain split-tied')
    for variants in groups.values():
        if 'full_leaf' in variants or 'full_root' in variants:
            if set(variants)!={'full_leaf','full_root'}:raise ValueError('complete matched full-context queries required')
            a,b=variants['full_leaf'],variants['full_root']
            if a['source'].rsplit('\n',1)[0]!=b['source'].rsplit('\n',1)[0] or a['expected_answer']!=b['expected_answer']:
                raise ValueError('full context root/leaf pair must share body and answer')
    python_count=_python_validate(programs) if independent else 0
    return dict(status='passed',rows=len(rows),logical_rows=len(logical),logical_split_rows=dict(Counter(row['split'] for row in logical)),
        unique_split_rows=dict(Counter(row['split'] for row in rows)),root_order_clusters=24,
        split_root_order_clusters=dict(Counter(next(iter(v)) for v in clusters.values())),topology_units=72,
        shared_literal_arithmetic_controls=sum(row['shared_control_across_splits'] for row in rows),
        nonzero_cross_split_source_overlap=0,source_support_minimum=min(map(len,gate.values())),
        source_support=[dict(split=k[0],form=k[1],question=k[2],operator=k[3],answer_sign=k[4],unique_sources=len(v)) for k,v in sorted(gate.items())],
        independent_python_programs=python_count,independent_python_passed=bool(independent))


def validate_rows(rows,generation=None,independent=False):
    _validation(rows,generation,independent)
    return rows


def _exclusions(config,rows):
    from .forecasting import _discovery_declaration
    wanted={ast.dump(ast.parse(row['source'])):row for row in rows};reviews=[]
    for name in config.get('exclude_datasets',[]):
        path=_safe_path(name,'.jsonl')
        if not path.exists():raise ValueError('required prior discovery source bank is missing')
        if path.stat().st_size>256*1024**2:raise ValueError('bounded prior source exclusion bank required')
        data=path.read_bytes();matches=set();control=set();count=0
        for line in data.splitlines():
            row=json.loads(line);_discovery_declaration(row)
            if not isinstance(row.get('source'),str):raise ValueError('exclusions must contain source records, not model outcomes')
            count+=1;key=ast.dump(ast.parse(row['source']))
            if key in wanted:
                match=wanted[key]
                (control if match['form']=='literal' and match['question']=='arithmetic_only' else matches).add(match['id'])
        reviews.append(dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),prior_rows=count,
            noncontrol_overlaps=len(matches),literal_control_repetitions=len(control)))
        if matches:raise ValueError('a proposed non-control source repeats a prior completed source bank')
    return reviews


def build(config):
    _generation(config)
    paths={key:_safe_path(config[key],suffix) for key,suffix in [('dataset','.jsonl'),('review','.json'),('report','.md')]}
    paths['manifest']=paths['dataset'].with_suffix('.manifest.json')
    if len({path.resolve() for path in paths.values()})!=4:raise ValueError('distinct source outputs required')
    rows=make_rows(config);review=_validation(rows,config,independent=True)
    review.update(evaluation_role=ROLE,generation_config=config,generation_config_hash=digest(config),
        exclusions=_exclusions(config,rows),source=code_identity(),new_model_queries=0,model_or_tokenizer_loaded=False,
        generated_holdouts_opened=False,limitations=LIMITATIONS)
    data=''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows).encode()
    if len(data)>128*1024**2:raise ValueError('bounded computation/routing source bank exceeded')
    checksum=hashlib.sha256(data).hexdigest();review['dataset_sha256']=checksum
    manifest=dict(schema_version=1,status='complete',evaluation_role=ROLE,role=ROLE,sha256=checksum,rows=len(rows),
        logical_rows=review['logical_rows'],generation_config=config,generation_config_hash=digest(config),
        root_order_clusters=24,split_root_order_clusters=review['split_root_order_clusters'],
        independent_python_passed=True,source=review['source'],instructions=INSTRUCTIONS,generated_holdouts_opened=False)
    report='\n'.join(['# Computation and routing isolation source preparation','',
        f"{len(rows):,} unique source programs represent {review['logical_rows']:,} logical matched records, with24root-order clusters (12TRAIN/12DEV).",
        f"Minimum distinct source support over prospective gate cells: {review['source_support_minimum']}.",
        f"Independent ordinary Python checked {review['independent_python_programs']:,} canonical/surface programs.",'',
        *['- '+item for item in LIMITATIONS],''])
    outputs=[(paths['dataset'],data),(paths['manifest'],_json_bytes(manifest)),(paths['review'],_json_bytes(review)),(paths['report'],report.encode())]
    for path,payload in outputs:
        if path.exists() and path.read_bytes()!=payload:raise ValueError('immutable source output differs: '+str(path))
    for path,payload in outputs:_publish(path,payload)
    return review
