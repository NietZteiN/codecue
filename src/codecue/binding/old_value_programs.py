"""Fresh historical/current value questions on pinned copy-graph families.

Only source programs and independently checked targets are built here. Historical
questions refer to the value immediately before the target's last write; their
ordinary-Python oracle therefore executes a prefix, while the model always sees
the complete eight-assignment body. Numeric values and questions never become
representation features in this module.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import random
import re

from .datasets import digest
from .relationship_programs import _safe_path
from .relationship_capture import _publish
from .registry import code_identity

ROLE = 'discovery_old_value_sources_v1'
SOURCE_ROLE = 'discovery_relationship_schedule_diversity_sources_v1'
SOURCE_SHA256 = 'd43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1'
NUMERIC_SEEDS = (1151, 1297, 1459)
PROFILES = ('2_1_1_0', '3_1_0_0', '2_2_0_0')
MODES = ('current', 'previous')
STORAGE = ('equal_current', 'absent_all_current', 'retained_other_current')
MAX_BYTES = 128 * 1024**2
N_ROWS = 6720
INSTRUCTIONS = {
    'old_value_output_v1': 'Read the assignments in order and answer the question. Give only the signed integer value, without explanation.',
    'old_value_execute_v1': 'Follow the Python 3 assignments in order. Answer the question with only the signed integer value.',
    'old_value_history_v1': 'Use the complete assignment history to answer the question. Return a signed integer only, without explanation.',
}
LIMITATIONS = [
    'Fresh adaptive discovery on the same60graph families; numeric seeds, rotations, lexical forms and query pairs are dependent relatives, not independent structural replication.',
    'The previous-value question is a historical task, not Python current-variable print semantics. Models see the complete body; an independently executed prefix supplies historical truth only.',
    'Old values can equal the final own value or survive in other current slots. Equal-value controls and absent-versus-retained distinct-value strata remain separate.',
    'Literal history can be reread or reconstructed. Accurate answers do not establish maintained neural state or natural causal use.',
    'Each graph retains its original TRAIN/DEV split; no original final/extrapolation outcomes, model training, downloads or selective interventions are included.',
]


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def _config(config):
    required = {'evaluation_role','source_graphs','numeric_seeds','dataset','review','report'}
    if not isinstance(config,dict) or set(config)!=required or config.get('evaluation_role')!=ROLE:
        raise ValueError('exact old-value discovery source configuration required')
    if len(_json_bytes(config))>16*1024 or config['numeric_seeds']!=list(NUMERIC_SEEDS) or any(type(v) is not int for v in config['numeric_seeds']):
        raise ValueError('the three fixed old-value numeric seeds are required')
    source=config['source_graphs']
    if (not isinstance(source,dict) or set(source)!={'path','sha256'}
            or source.get('sha256')!=SOURCE_SHA256):
        raise ValueError('the pinned completed diversity graph bank is required')
    inputs=_safe_path(source['path'],'.jsonl')
    outputs={name:_safe_path(config[name],suffix) for name,suffix in
             (('dataset','.jsonl'),('review','.json'),('report','.md'))}
    outputs['manifest']=_safe_path(str(outputs['dataset'].with_suffix('.manifest.json')),'.json')
    paths=[inputs,*outputs.values()]
    if (any(path.is_symlink() or path.exists() and not path.is_file() for path in paths)
            or len({p.resolve() for p in paths})!=len(paths)
            or any(a.resolve() in b.resolve().parents for a in paths for b in paths if a!=b)):
        raise ValueError('distinct nonsymlink source and output files required')
    return inputs,outputs


def _literal(expression):
    if isinstance(expression,ast.Constant) and type(expression.value) is int:
        return expression.value
    if (isinstance(expression,ast.UnaryOp) and isinstance(expression.op,ast.USub)
            and isinstance(expression.operand,ast.Constant) and type(expression.operand.value) is int):
        return -expression.operand.value
    raise ValueError('only signed integer root constants are permitted')


def trace_body(body, *, independent=False):
    """Restricted custom execution, optionally checked statement by statement by Python."""
    if not isinstance(body,str) or not 0<len(body)<=4096:
        raise ValueError('bounded eight-assignment body required')
    try: tree=ast.parse(body)
    except (ValueError,SyntaxError) as exc: raise ValueError('valid restricted assignment body required') from exc
    if len(tree.body)!=8: raise ValueError('exactly four roots and four copies required')
    state={};versions={};history=[];names=[];roots=[];destinations=[];parents=[]
    for index,node in enumerate(tree.body):
        if (not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name)
                or node.type_comment is not None): raise ValueError('only simple single-target assignments permitted')
        name=node.targets[0].id
        before=dict(state)
        if index<4:
            if name in state: raise ValueError('four distinct roots required')
            value=_literal(node.value)
            if not -12<=value<=12: raise ValueError('root constants must be in[-12,12]')
            names.append(name);roots.append(value)
        else:
            if name not in state or not isinstance(node.value,ast.Name) or node.value.id not in state or node.value.id==name:
                raise ValueError('copy source must be a distinct defined owner')
            value=state[node.value.id];destinations.append(names.index(name));parents.append(names.index(node.value.id))
        state[name]=value;versions[name]=versions.get(name,0)+1
        history.append(dict(statement=index,name=name,before=before,after=dict(state),value=value,version=versions[name]))
    if len(set(roots))!=4: raise ValueError('four pairwise-distinct root values required')
    checked=0
    if independent:
        namespace={}
        for index,node in enumerate(tree.body):
            before=dict(namespace)
            exec(compile(ast.Module(body=[node],type_ignores=[]),'<old-value-source>','exec'),{'__builtins__':{}},namespace)
            if before!=history[index]['before'] or namespace!=history[index]['after']:
                raise ValueError('independent ordinary-Python trace differs')
            checked+=1
    return dict(names=names,root_values=roots,destinations=destinations,parents=parents,
                history=history,current=dict(state),versions=versions,independent_python_statements=checked)


@lru_cache(maxsize=256)
def _graph(destinations,parents):
    from .schedule_diversity_programs import _graph as graph
    return graph(tuple(destinations),tuple(parents))


def _load_templates(config):
    path,_=_config(config)
    if not path.is_file() or path.stat().st_size>MAX_BYTES:
        raise ValueError('bounded completed diversity source bank required')
    payload=path.read_bytes()
    if hashlib.sha256(payload).hexdigest()!=SOURCE_SHA256:
        raise ValueError('pinned diversity source SHA differs')
    exemplars={};splits={};counts=Counter();physical=0
    for line in payload.splitlines():
        row=json.loads(line);physical+=1
        graph=row.get('canonical_graph_sha256');split=row.get('split');profile=row.get('profile_id')
        if (row.get('evaluation_role')!=SOURCE_ROLE or row.get('condition')!='neutral'
                or split not in ('train','development') or profile not in PROFILES
                or not isinstance(graph,str) or not re.fullmatch('[0-9a-f]{64}',graph)):
            raise ValueError('original source-only diversity rows required')
        if graph in splits and splits[graph]!=(split,profile):
            raise ValueError('canonical graph relatives cannot cross source splits')
        splits[graph]=(split,profile)
        if row.get('slot_rotation')==0 and graph not in exemplars:
            lines=row['canonical_source'].splitlines();body='\n'.join(lines[:8]);trace=trace_body(body)
            d,p=trace['destinations'],trace['parents']
            if (d!=row.get('destination_schedule') or p!=row.get('copy_parent_slots')
                    or _graph(tuple(d),tuple(p))!=graph):
                raise ValueError('original graph/body routing identity differs')
            exemplars[graph]=dict(canonical_graph_sha256=graph,split=split,profile_id=profile,
                destinations=d,parents=p,component_id=row['component_id'])
    if physical!=5760 or len(splits)!=60 or set(exemplars)!=set(splits):
        raise ValueError('the complete5760-row60-family graph bank is required')
    for item in exemplars.values():counts[item['split'],item['profile_id']]+=1
    if counts!={(split,profile):(15 if split=='train' else 5) for split in ('train','development') for profile in PROFILES}:
        raise ValueError('preserved45TRAIN/15DEV families and profile allocation required')
    return [exemplars[key] for key in sorted(exemplars)]


def _mapping(lexical):
    return {f'v{i}':f'{"item" if lexical==0 else "cell"}_{i}' for i in range(4)}


def _body(values,destinations,parents,names):
    return '\n'.join([f'{names[i]} = {values[i]}' for i in range(4)]
        +[f'{names[d]} = {names[p]}' for d,p in zip(destinations,parents)])


def question(row):
    name=row['target_name'];mode=row['query_mode']
    if mode=='previous':return f'What was {name} immediately before its LAST assignment?'
    if mode=='current':return f'What is {name} after all assignments?'
    raise ValueError('current or previous historical query required')


def _row(template,seed,rotation,lexical,values,destinations,parents,slot,mode):
    mapping=_mapping(lexical);names=[mapping[f'v{i}'] for i in range(4)]
    body=_body(values,destinations,parents,names);trace=trace_body(body)
    name=names[slot];writes=[h for h in trace['history'] if h['name']==name]
    if len(writes)<2: raise ValueError('the queried owner must be overwritten')
    last=writes[-1];previous=writes[-2];old=last['before'][name];current=trace['current'][name]
    storage='equal_current' if old==current else ('absent_all_current' if old not in trace['current'].values() else 'retained_other_current')
    prefix=body.splitlines()[:last['statement']] if mode=='previous' else body.splitlines()
    defining=previous if mode=='previous' else last
    graph=template['canonical_graph_sha256'];pair='old-value-pair:'+digest([ROLE,graph,seed,rotation,lexical,slot])[:24]
    row=dict(schema_version=1,evaluation_role=ROLE,condition='neutral',source_form='literal',family='historical_copy_value',
        id='old-value:'+digest([pair,mode])[:24],pair_id=pair,paired_group_id=pair,
        base_id='old-value-body:'+digest([ROLE,graph,seed,rotation,lexical])[:24],
        canonical_graph_sha256=graph,component_id=template['component_id'],cluster_id=template['component_id'],
        template_id=template['component_id'],split=template['split'],profile_id=template['profile_id'],
        numeric_seed=seed,slot_rotation=rotation,lexical_realization=lexical,root_values=list(values),
        destination_schedule=list(destinations),copy_parent_slots=list(parents),rename_map=mapping,
        body=body,source=body+'\n'+name,canonical_source=_body(values,destinations,parents,[f'v{i}' for i in range(4)])+'\n'+f'v{slot}',
        oracle_source='\n'.join([*prefix,name]),query_mode=mode,query_role=mode,query_slot=slot,target_slot=slot,target_name=name,
        target_update_count=len(writes)-1,last_write_statement=last['statement'],last_write_lag=7-last['statement'],
        query_statement=last['statement']-1 if mode=='previous' else 7,target_definition_statement=defining['statement'],
        target_assignment_version=defining['version'],current_assignment_version=last['version'],read_lag=7-defining['statement'],
        previous_value=old,current_value=current,current_values=[trace['current'][n] for n in names],
        old_storage=storage,primary_distinct=old!=current,
        old_retained_in_other_slots=[i for i,n in enumerate(names) if i!=slot and trace['current'][n]==old],
        expected_answer=old if mode=='previous' else current)
    row['question']=question(row)
    return row


def make_rows(config):
    templates=_load_templates(config);rows=[]
    for template in templates:
        for seed in NUMERIC_SEEDS:
            rng=random.Random(digest([ROLE,template['canonical_graph_sha256'],seed,'root_values']))
            root_values=rng.sample(range(-12,13),4)
            for rotation in range(4):
                values=[0]*4
                for i,value in enumerate(root_values):values[(i+rotation)%4]=value
                destinations=[(d+rotation)%4 for d in template['destinations']]
                parents=[(p+rotation)%4 for p in template['parents']]
                for lexical in (0,1):
                    for slot in sorted(set(destinations)):
                        for mode in MODES:
                            rows.append(_row(template,seed,rotation,lexical,values,destinations,parents,slot,mode))
    return rows


def _validate_row(row):
    if not isinstance(row,dict) or row.get('evaluation_role')!=ROLE or row.get('split') not in ('train','development'):
        raise ValueError('old-value TRAIN/DEV source rows required')
    graph=row.get('canonical_graph_sha256');rotation=row.get('slot_rotation');lexical=row.get('lexical_realization')
    if (not isinstance(graph,str) or not re.fullmatch('[0-9a-f]{64}',graph)
            or type(rotation) is not int or rotation not in range(4) or type(lexical) is not int or lexical not in (0,1)
            or type(row.get('numeric_seed')) is not int or row['numeric_seed'] not in NUMERIC_SEEDS
            or type(row.get('target_slot')) is not int or row['target_slot'] not in range(4) or row.get('query_mode') not in MODES):
        raise ValueError('fixed graph/seed/rotation/lexical/query identities required')
    if (row.get('component_id')!='schedule-diversity-graph:'+graph[:24]
            or row.get('profile_id') not in PROFILES
            or not isinstance(row.get('root_values'),list) or len(row['root_values'])!=4
            or any(type(v) is not int or not -12<=v<=12 for v in row['root_values'])
            or any(not isinstance(row.get(key),list) or len(row[key])!=4
                   or any(type(v) is not int or v not in range(4) for v in row[key])
                   for key in ('destination_schedule','copy_parent_slots'))):
        raise ValueError('bounded canonical owner/value metadata required')
    template={k:row[k] for k in ('canonical_graph_sha256','component_id','split','profile_id')}
    expected=_row(template,row['numeric_seed'],rotation,lexical,row['root_values'],row['destination_schedule'],row['copy_parent_slots'],row['target_slot'],row['query_mode'])
    if row!=expected:raise ValueError('source, historical truth, labels or deterministic row identity differ')
    trace=trace_body(row['body'])
    if ('_'.join(map(str,sorted(Counter(trace['destinations']).values(),reverse=True)+[0]*(4-len(set(trace['destinations'])))))!=row['profile_id']
            or row['profile_id'] not in PROFILES or _graph(tuple(trace['destinations']),tuple(trace['parents']))!=graph):
        raise ValueError('canonical graph or overwrite profile differs')
    return trace


def _validation(rows,generation=None,independent=False):
    if not isinstance(rows,list) or len(rows)!=N_ROWS:raise ValueError('the full6720-row old-value cohort is required')
    ids=set();pairs=defaultdict(list);bodies={};graphs={};grid=Counter();support=defaultdict(set);checked=0
    for row in rows:
        trace=_validate_row(row)
        if row['id'] in ids:raise ValueError('duplicate old-value row')
        ids.add(row['id']);pairs[row['pair_id']].append(row)
        graph=row['canonical_graph_sha256'];signature=(row['split'],row['profile_id'],row['component_id'])
        if graph in graphs and graphs[graph]!=signature:raise ValueError('graph family crosses source partitions')
        graphs[graph]=signature;grid[graph,row['numeric_seed'],row['slot_rotation'],row['lexical_realization'],row['target_slot'],row['query_mode']]+=1
        body=row['body'];bodies[body]=trace
        support[row['split'],row['query_mode'],row['old_storage']].add(_user_text(row,next(iter(INSTRUCTIONS))))
    if len(graphs)!=60 or len({v[2] for v in graphs.values()})!=60:raise ValueError('exactly60 distinct canonical graph families required')
    profile_counts=Counter((split,profile) for split,profile,_ in graphs.values())
    if profile_counts!={(split,profile):(15 if split=='train' else 5) for split in ('train','development') for profile in PROFILES}:
        raise ValueError('preserved source graph/profile split required')
    if len(pairs)!=3360 or len(bodies)!=1440 or set(grid.values())!={1}:
        raise ValueError('complete paired6720-row1440-body factorial required')
    for pair in pairs.values():
        if len(pair)!=2 or {r['query_mode'] for r in pair}!=set(MODES) or len({r['body'] for r in pair})!=1:
            raise ValueError('same-body current/previous question pairs required')
    for graph in graphs:
        selected=[r for r in rows if r['canonical_graph_sha256']==graph]
        expected={ (seed,rotation,lexical,slot,mode) for seed in NUMERIC_SEEDS for rotation in range(4) for lexical in (0,1)
                   for slot in next(r for r in selected if r['slot_rotation']==rotation)['destination_schedule'] for mode in MODES}
        observed={(r['numeric_seed'],r['slot_rotation'],r['lexical_realization'],r['target_slot'],r['query_mode']) for r in selected}
        if observed!=expected:raise ValueError('every seed/rotation/lexical/overwritten-owner/mode relative required')
    cells=[]
    for split in ('train','development'):
        for mode in MODES:
            for storage in STORAGE:
                n=len(support[split,mode,storage]);primary=storage!='equal_current'
                if primary and n<24:raise ValueError('each predeclared primary source cell needs24 distinct prompts')
                cells.append(dict(split=split,query_mode=mode,old_storage=storage,primary=primary,unique_prompts=n))
    if generation is not None:
        templates=_load_templates(generation)
        if {(r['canonical_graph_sha256'],r['split'],r['profile_id'],r['component_id']) for r in templates}!={(g,*v) for g,v in graphs.items()}:
            raise ValueError('rows differ from the SHA-pinned source graph allocation')
        expected=make_rows(generation)
        if rows!=expected:raise ValueError('frozen numeric source generator/order differs')
    if independent:
        for body in bodies:
            trace=trace_body(body,independent=True);checked+=trace['independent_python_statements']
    return dict(status='passed',rows=len(rows),pairs=len(pairs),bodies=len(bodies),canonical_graph_families=60,
        split_rows=dict(Counter(r['split'] for r in rows)),split_graph_families=dict(Counter(v[0] for v in graphs.values())),
        old_storage_counts=dict(Counter(r['old_storage'] for r in rows)),source_support_cells=cells,
        source_support_minimum=min(c['unique_prompts'] for c in cells if c['primary']),
        independent_python_passed=bool(independent),independent_python_statements=checked,
        expected_answer_is_historical_prefix_for_previous=True,model_or_tokenizer_loaded=False,
        new_model_queries=0,new_fits=0,generated_holdouts_opened=False)


def validate_rows(rows,generation=None,independent=False):
    _validation(rows,generation,independent)
    return rows


def analysis_rows(rows):
    return rows


def instruction_spec(variant):
    if variant not in INSTRUCTIONS:raise ValueError('unknown old-value instruction')
    return dict(max_new_tokens=16,stop_at_blank_line=True,answer_mode='integer')


def _user_text(row,variant):
    instruction_spec(variant)
    return INSTRUCTIONS[variant]+'\n\n```python\n'+row['body']+'\n```\n\n'+question(row)


def prompt(tokenizer,row,variant):
    from .model_adapter import normalize_prompt
    text=_user_text(row,variant)
    rendered=tokenizer.apply_chat_template([dict(role='user',content=text),dict(role='assistant',content='Output:\n')],
        tokenize=False,continue_final_message=True)
    return normalize_prompt(tokenizer,rendered),row['body']


def score_case(case,raw):
    row=case.get('record',case)
    prediction=int(raw.strip()) if (isinstance(raw,str) and len(raw)<=128 and re.fullmatch(r'\s*[+-]?\d+\s*',raw,flags=re.ASCII)) else None
    return dict(prediction=prediction,valid=prediction is not None,correct=prediction==row['expected_answer'])


def build(config):
    _,paths=_config(config);rows=make_rows(config);review=_validation(rows,config,independent=True)
    review.update(evaluation_role=ROLE,generation_config=config,generation_config_hash=digest(config),
        source_graphs=config['source_graphs'],source=code_identity(),instructions=INSTRUCTIONS,limitations=LIMITATIONS)
    data=''.join(json.dumps(row,sort_keys=True,allow_nan=False)+'\n' for row in rows).encode()
    if len(data)>MAX_BYTES:raise ValueError('old-value source cohort exceeds declared bound')
    checksum=hashlib.sha256(data).hexdigest();review['dataset_sha256']=checksum
    manifest=dict(schema_version=1,status='complete',evaluation_role=ROLE,role=ROLE,sha256=checksum,rows=len(rows),
        generation_config=config,generation_config_hash=digest(config),source_graphs=config['source_graphs'],
        canonical_graph_families=60,split_graph_families=review['split_graph_families'],independent_python_passed=True,
        source=review['source'],instructions=INSTRUCTIONS,generated_holdouts_opened=False)
    report='\n'.join(['# Historical/current value source preparation','',
        f'{len(rows):,} questions form3,360current/previous pairs over1,440bodies and60preserved canonical graph families (45TRAIN/15DEV).',
        f'Minimum unique-prompt support per primary split/query/storage cell: {review["source_support_minimum"]}.',
        f'Independent Python checked {review["independent_python_statements"]:,} assignment steps. Models always see the complete body; historical oracle prefixes are never shown.','',
        *['- '+s for s in LIMITATIONS],''])
    for a,b in [('form3,360current','form 3,360 current'),('over1,440bodies','over 1,440 bodies'),('and60preserved','and 60 preserved'),('45TRAIN/15DEV','45 TRAIN / 15 DEV'),('same60graph','same 60 graph')]:report=report.replace(a,b)
    outputs=[(paths['dataset'],data),(paths['manifest'],_json_bytes(manifest)),(paths['review'],_json_bytes(review)),(paths['report'],report.encode())]
    for path,payload in outputs:
        if path.exists() and path.read_bytes()!=payload:raise ValueError('immutable old-value source output differs: '+str(path))
    for path,payload in outputs:_publish(path,payload)
    return review
