"""New numeric, query and computed-root discovery cohorts for relationship readouts.

All graph components and their TRAIN/DEV partition are reused deliberately.
Numeric seeds are new draws, not independent topology replications. This builder
never loads a tokenizer/model, reads activations, or collects model outcomes.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import random

from . import algebraic_programs as algebraic
from . import relationship_programs as routing
from .datasets import digest
from .interpreter import execute
from .programs import rename
from .registry import code_identity

ROLE = 'overnight_relationship_discovery_v1'
COHORTS = ('numeric_replication', 'query_twins', 'computed_roots')
MAX_ROWS = 25_000
MAX_DATASET_BYTES = 128 * 1024**2
LIMITATIONS = [
    'Adaptive discovery follow-up designed after inspecting earlier relationship results; not an untouched confirmation.',
    'The same 27 structural components, 18/9 TRAIN/DEV split and 81 full graphs are reused; numeric seeds are not independent topologies.',
    'The query panel uses one balanced numeric draw per stratum/component/seed, while numeric and root-format panels use all configured draws.',
    'Rows shared by cohorts are captured once and must not be pooled as independent examples across analyses.',
    'Global initial-state uniqueness is a declared source-only rejection rule for attainable coherent shuffle controls.',
    'Computed roots each use one independent constant binary addition/subtraction with signed operands; the remaining body only copies.',
    'Arithmetic source and literal source have different visible forms; value-derived source controls remain necessary.',
    'Oracle values, graphs, numeric strata and root metadata are targets/validation only, never hidden-probe input features.',
    'No model outcome, causal-mechanism claim, optional training, sealed final evaluation or new-family confirmation follows from this preparation.',
]


def _config(config):
    required = {'evaluation_role','numeric_seeds','dataset','review','report'}
    if (not isinstance(config,dict) or set(config)-required-{'numeric_instances'} or required-set(config)
            or config.get('evaluation_role') != ROLE):
        raise ValueError('exact overnight discovery source configuration required')
    seeds = config['numeric_seeds']; n = config.get('numeric_instances',4)
    if (not isinstance(seeds,list) or not 3 <= len(seeds) <= 4
            or any(type(seed) is not int or not 0 <= seed < 2**63 for seed in seeds)
            or len(set(seeds)) != len(seeds)):
        raise ValueError('three or four distinct bounded numeric seeds required')
    if type(n) is not int or not 1 <= n <= 4: raise ValueError('one through four numeric draws per stratum required')
    expected = len(seeds)*(972*n+1458)
    if expected > MAX_ROWS: raise ValueError('declared overnight source cohort exceeds bounded row count')
    translated = dict(evaluation_role=routing.ROLE,seed=seeds[0],numeric_instances=n,
        dataset=config['dataset'],review=config['review'],report=config['report'])
    _,paths = routing._config(translated)
    return seeds,n,expected,paths


def _numeric_state(seed, original, n, seen):
    values = tuple(original['targets']['initial_values']); attempt=0; effective=seed
    while values in seen:
        attempt += 1
        if attempt > 10_000: raise ValueError('numeric-state uniqueness rejection exhausted')
        effective = int(digest([ROLE,seed,original['base_id'],attempt])[:15],16)
        values = tuple(algebraic._draws(effective,original['targets']['component_digits'],n)
            [original['targets']['numeric_stratum']][original['targets']['numeric_draw']])
    seen.add(values)
    return values,effective,attempt


@lru_cache(maxsize=4096)
def _computed_roots(values, seed, base):
    # Every target magnitude is <=12. Larger signed operands ensure no target
    # occurs as a signed literal or even as an absolute literal magnitude.
    pool = tuple(range(-32,-12)) + tuple(range(13,33))
    rng = random.Random(digest([ROLE,'computed_roots',seed,base]))
    expressions=[]
    for slot,target in enumerate(values):
        operator = '+' if (rng.randrange(2)+slot)%2 else '-'
        candidates = [(left,right) for left in pool for right in pool
            if (left+right if operator=='+' else left-right)==target]
        if not candidates: raise ValueError('one-operation literal-absent root is infeasible')
        left,right = rng.choice(candidates)
        expressions.append(f'{left} {operator} {right}')
    return tuple(expressions)


def _row(original, seed, values, effective, attempts, source_form, query_slot):
    base='overnight:'+original['base_id']
    expressions = ([str(value) for value in values] if source_form=='literal'
        else list(_computed_roots(tuple(values),seed,base)))
    parents=original['targets']['parent_by_destination']
    body='\n'.join([*(f'v{i} = {expression}' for i,expression in enumerate(expressions)),
        *(f'v{i} = {parents[f"v{i}"]}' for i in range(4))])
    canonical=body+f'\nv{query_slot}'
    mapping=original['rename_map']; surface=rename(canonical,mapping)
    lexical=original['lexical_realization']; numeric=original['targets']['numeric_draw']
    cohorts=[]
    if source_form=='literal' and query_slot==0: cohorts.append('numeric_replication')
    if source_form=='literal' and numeric==0: cohorts.append('query_twins')
    if source_form=='computed': cohorts.append('computed_roots')
    offset=0;spans=[]
    for statement,line in enumerate(surface.splitlines()):
        spans.append(dict(statement=statement,start=offset,end=offset+len(line)));offset+=len(line)+1
    return dict(schema_version=1,evaluation_role=ROLE,
        id='overnight-relationship:'+digest([ROLE,seed,source_form,surface])[:24],
        base_id=base,paired_group_id=base,counterfactual_group_id=base,
        template_id=original['template_id'],component_id=original['component_id'],cluster_id=original['cluster_id'],
        split=original['split'],family='overnight_relationship_copy_routing',condition='neutral',control_kind='primary',
        numeric_seed=seed,numeric_effective_seed=effective,numeric_rejection_attempts=attempts,
        numeric_stratum=original['targets']['numeric_stratum'],numeric_draw=numeric,
        lexical_realization=lexical,source_form=source_form,query_role=f'v{query_slot}',query_slot=query_slot,query_count=1,
        cohorts=cohorts,source=surface,canonical_source=canonical,rename_map=mapping,
        variable_slots={f'v{i}':i for i in range(4)},statement_spans=spans,
        body_id='overnight-body:'+digest([seed,source_form,body])[:24],
        surface_body_id='overnight-surface-body:'+digest(surface.rsplit('\n',1)[0])[:24],
        format_pair_id='overnight-format-pair:'+digest([seed,base,parents,lexical,query_slot])[:24],
        initial_state_id=digest(list(values)),root_values=list(values),root_expressions=expressions,
        parent_slots=[int(parents[f'v{i}'][1:]) for i in range(4)],
        **execute(canonical))


def make_rows(config):
    seeds,n,expected,_ = _config(config)
    rows=[];seen=set()
    for seed in seeds:
        translated=dict(evaluation_role=algebraic.ROLE,seed=seed,numeric_instances=n,
            dataset=config['dataset'],review=config['review'],report=config['report'])
        bases={}
        for original in algebraic.make_rows(translated):
            base=original['base_id']
            if base not in bases: bases[base]=_numeric_state(seed,original,n,seen)
            values,effective,attempts=bases[base]
            rows.append(_row(original,seed,values,effective,attempts,'literal',0))
            rows.append(_row(original,seed,values,effective,attempts,'computed',0))
            if original['targets']['numeric_draw']==0:
                rows.extend(_row(original,seed,values,effective,attempts,'literal',query) for query in (1,2,3))
    if len(rows)!=expected: raise ValueError('overnight source factorial row count differs')
    return rows


def view_indices(rows):
    """Source-only union indices; C pairs reference A without duplicate rows."""
    views={cohort:dict(indices=[i for i,row in enumerate(rows) if cohort in row['cohorts']]) for cohort in COHORTS}
    for view in views.values():
        view['rows']=len(view['indices'])
        view['split_rows']=dict(Counter(rows[i]['split'] for i in view['indices']))
    literals={row['format_pair_id']:i for i,row in enumerate(rows)
        if row['source_form']=='literal' and row['query_slot']==0}
    matched=[]
    for index in views['computed_roots']['indices']:
        key=rows[index]['format_pair_id']
        if key not in literals:raise ValueError('computed row lacks its matching A literal source')
        matched.append(literals[key])
    views['computed_roots']['matched_literal_indices']=matched
    views['computed_roots']['matched_literal_ids']=[rows[i]['id'] for i in matched]
    return views


def validate_rows(config,rows,independent=False):
    seeds,n,expected,_ = _config(config)
    if rows != make_rows(config): raise ValueError('overnight sources differ from their deterministic factorial')
    if len(rows)!=expected or len({row['id'] for row in rows})!=expected: raise ValueError('unique complete overnight source rows required')
    programs=set();bases={};state_bases=defaultdict(set);components=defaultdict(set);graphs=defaultdict(set)
    queries=defaultdict(dict);formats=defaultdict(dict);cohorts=Counter();strata=Counter();rejections={};absent=0
    for row in rows:
        truth=execute(row['canonical_source']);surface=execute(row['source'])
        if truth['expected_answer']!=surface['expected_answer'] or truth!=execute(rename(row['source'],{v:k for k,v in row['rename_map'].items()})):
            raise ValueError('canonical and surface semantics differ')
        if any(row.get(key)!=value for key,value in truth.items()): raise ValueError('stored source oracle differs')
        state=tuple(row['root_values']);base=row['base_id'];identity=(row['split'],row['component_id'],state)
        if base in bases and bases[base]!=identity: raise ValueError('numeric relatives cross split, component or root state')
        bases[base]=identity;state_bases[state].add(base);rejections[base]=row['numeric_rejection_attempts']
        components[row['split']].add(row['component_id'])
        graphs[row['split']].add(tuple(row['parent_slots']))
        cohorts.update(row['cohorts']);strata[row['numeric_stratum']]+=1
        if row['source_form']=='computed':
            operands=[]
            for expression,value in zip(row['root_expressions'],row['root_values']):
                node=ast.parse(expression,mode='eval').body
                if not isinstance(node,ast.BinOp) or not isinstance(node.op,(ast.Add,ast.Sub)):
                    raise ValueError('computed roots need exactly one constant addition/subtraction')
                terms=[ast.literal_eval(node.left),ast.literal_eval(node.right)]
                if any(type(term)is not int or not 13<=abs(term)<=32 for term in terms): raise ValueError('computed operand domain differs')
                if (terms[0]+terms[1] if isinstance(node.op,ast.Add) else terms[0]-terms[1])!=value:
                    raise ValueError('computed root does not match the paired literal value')
                operands.extend(terms)
            if {abs(value) for value in row['root_values']} & {abs(value) for value in operands}:
                raise ValueError('an initial target occurs in the computed literal operands')
            absent+=1
        if 'query_twins' in row['cohorts']:queries[row['surface_body_id']][row['query_slot']]=row
        if row['query_slot']==0:formats[row['format_pair_id']][row['source_form']]=row
        programs.update((row['canonical_source'],row['source']))
    if len(bases)!=len(seeds)*81*n or any(len(group)!=1 for group in state_bases.values()):
        raise ValueError('numeric bases do not have globally unique initial states')
    if {k:len(v) for k,v in components.items()}!={'train':18,'development':9} or graphs['train'] & graphs['development']:
        raise ValueError('structural component/full-graph split differs')
    if {k:len(v) for k,v in graphs.items()}!={'train':54,'development':27}:raise ValueError('expected 81 copy-parent graphs')
    for variants in queries.values():
        if set(variants)!={0,1,2,3}:raise ValueError('query twins must cover all four slots')
        traces=[row['execution_trace'] for row in variants.values()]
        if any(trace!=traces[0] for trace in traces[1:]):raise ValueError('query changed the identical program body state')
    for variants in formats.values():
        if set(variants)!={'literal','computed'}:raise ValueError('complete literal/computed root pairs required')
        left,right=variants['literal'],variants['computed']
        if (left['parent_slots']!=right['parent_slots'] or left['expected_answer']!=right['expected_answer']
                or [point['values'] for point in left['execution_trace']]!=[point['values'] for point in right['execution_trace']]):
            raise ValueError('literal/computed root pairs differ in states or copy graph')
    python_count=routing._python_validate(programs) if independent else 0
    return dict(status='passed',rows=len(rows),numeric_seeds=seeds,numeric_instances_per_stratum=n,
        split_rows=dict(Counter(row['split'] for row in rows)),cohort_rows=dict(cohorts),numeric_stratum_rows=dict(strata),
        structural_components=27,split_components={k:len(v) for k,v in components.items()},
        distinct_definition_graphs=81,split_definition_graphs={k:len(v) for k,v in graphs.items()},
        numeric_bases=len(bases),globally_unique_initial_states=len(state_bases),
        numeric_bases_rejection_resampled=sum(value>0 for value in rejections.values()),
        numeric_rejection_attempts=sum(rejections.values()),query_twin_bodies=len(queries),literal_computed_pairs=len(formats),
        views=view_indices(rows),
        computed_rows_with_all_target_magnitudes_absent=absent,independent_python_programs=python_count,
        independent_python_passed=bool(independent),
        activation_raw_bytes_3sites_4layers_4096_float32=len(rows)*3*4*4096*4,
        activation_raw_bytes_9sites_4layers_4096_float32=len(rows)*9*4*4096*4)


def build(config):
    _,_,_,paths=_config(config)
    rows=make_rows(config);review=validate_rows(config,rows,independent=True)
    payload=''.join(json.dumps(row,sort_keys=True)+'\n' for row in rows).encode()
    if len(payload)>MAX_DATASET_BYTES:raise ValueError('bounded overnight JSONL exceeded')
    checksum=hashlib.sha256(payload).hexdigest()
    review.update(evaluation_role=ROLE,config=config,config_hash=digest(config),dataset=str(paths['dataset']),dataset_sha256=checksum,
        source=code_identity(),new_model_queries=0,model_or_tokenizer_loaded=False,activation_arrays_read=False,
        relation_decoding_performed=False,generated_holdouts_opened=False,limitations=LIMITATIONS)
    manifest=dict(schema_version=1,status='complete',evaluation_role=ROLE,role=ROLE,sha256=checksum,rows=len(rows),
        generation_config=config,generation_config_hash=digest(config),split_rows=review['split_rows'],
        cohort_rows=review['cohort_rows'],views=review['views'],numeric_seeds=review['numeric_seeds'],structural_components=27,
        globally_unique_initial_states=review['globally_unique_initial_states'],independent_python_passed=True,
        generated_holdouts_opened=False,source=review['source'],review=str(paths['review']))
    report=('\n'.join(['# Overnight relationship discovery source cohorts','',
        f"Prepared {len(rows):,} unique rows across {len(config['numeric_seeds'])} numeric seeds, reusing 27 structural components and 81 graphs.",
        f"Cohort row memberships (shared baseline rows count in multiple panels): {json.dumps(review['cohort_rows'],sort_keys=True)}.",
        f"Query-twin bodies: {review['query_twin_bodies']:,}; literal/computed pairs: {review['literal_computed_pairs']:,}.",
        f"Globally unique initial states: {review['globally_unique_initial_states']:,}; rejection-resampled bases: {review['numeric_bases_rejection_resampled']}.",
        f"All {review['computed_rows_with_all_target_magnitudes_absent']:,} computed rows exclude every initial target magnitude from literal operands.",
        f"Independent ordinary Python validated {review['independent_python_programs']:,} distinct canonical/surface programs.",
        f"Dataset SHA256: `{checksum}`.",'',*['- '+item for item in LIMITATIONS],''])).encode()
    review['report']=dict(path=str(paths['report']),sha256=hashlib.sha256(report).hexdigest())
    from .relationship_capture import _publish
    outputs=[(paths['dataset'],payload),(paths['manifest'],routing._json_bytes(manifest)),
        (paths['review'],routing._json_bytes(review)),(paths['report'],report)]
    for path,data in outputs:
        if path.exists() and path.read_bytes()!=data:raise ValueError('immutable overnight source output differs: '+str(path))
    for path,data in outputs:_publish(path,data)
    return review
