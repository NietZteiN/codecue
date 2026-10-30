"""Computed retention frontiers: identical arithmetic, 2/3/4 live bindings.

Scheduling independent subtractions around irrelevant code changes the number
of output-relevant bindings crossing the block. It also changes computation
and assignment distances; this is a scheduling/retention assay, not an isolated
memory-capacity manipulation. All new outcomes are calibration/development.
"""
import ast
from collections import Counter, defaultdict
from itertools import permutations, product
import json
from pathlib import Path

from .competition import assign_splits
from .datasets import digest, read_jsonl
from .interpreter import execute, python_oracle
from .programs import rename
from .published_benchmarks import immutable, sha

ROLE='computed_retention_frontier_discovery_v1'


def numeric_bank(config):
    candidates=[]
    for a,b,c,d in permutations(range(1,10),4):
        r,s=a-b,c-d;answer=r-s
        forbidden={a,b,c,d,0,31}
        allowed=[v for v in range(1,10) if v not in {a,b,abs(r),abs(s),abs(answer)}]
        if answer>0 and all(abs(v) not in forbidden for v in (r,s,answer)) and len(allowed)>=3:
            candidates.append((a,b,c,d))
    per=config['numeric_per_template']
    if per<2 or per%2:raise ValueError('numeric count must contain complete sign pairs')
    needed=config['templates']*per//2
    chosen=sorted(candidates,key=lambda v:digest([config['seed'],v]))[:needed]
    if len(chosen)!=needed:raise ValueError('not enough distinct sign-paired computed states')
    result=[]
    for index,(a,b,c,d) in enumerate(chosen):
        forbidden={a,b,abs(a-b),abs(c-d),abs((a-b)-(c-d))}
        allowed=[v for v in range(1,10) if v not in forbidden]
        history=sorted(allowed,key=lambda v:digest([config['seed'],index,v]))[:3]
        for values in ((a,b,c,d),(b,a,d,c)):
            result.append(dict(values=list(values),history=history,sign_pair=index))
    return result


def frontier_source(values,history,init_order,updates,compute_order,early_count,noise_pairs,initialize_results=False):
    a,b,c,d=values;old,middle,penultimate=history
    initial=dict(a=old,b=b,c=c,d=d)
    lines=['spare = 31','buffer = 0']+(['r = 0','s = 0'] if initialize_results else [])+[f'{name} = {initial[name]}' for name in init_order]
    owner='a' if updates==3 else 'buffer'
    lines += [f'{owner} = {middle}',f'{owner} = {penultimate}','buffer = 0',f'a = {a}']
    computations=dict(left='r = a - b',right='s = c - d')
    early=early_count if noise_pairs else 2
    lines += [computations[k] for k in compute_order[:early]]
    checkpoint=len(lines)-1 if noise_pairs else None
    lines += ['buffer = spare','buffer = 0']*noise_pairs
    lines += [computations[k] for k in compute_order[early:]]
    return '\n'.join(lines+['r - s']),checkpoint


def checkpoint_interventions(source,statement):
    """Cut the execution at the checkpoint; never recompute completed ancestors."""
    truth=execute(source);point=truth['execution_trace'][statement];lines=source.splitlines();results=[]
    live=set(truth['liveness'][statement]['live_versions'])
    for name,value in sorted(point['values'].items()):
        changed='\n'.join(lines[:statement+1]+[f'{name} = {value+1}']+lines[statement+1:])
        cf=execute(changed)
        affected=cf['expected_answer']!=truth['expected_answer']
        if affected!=(name in live):raise ValueError('checkpoint functional relevance differs from live binding')
        results.append(dict(variable=name,current_value=value,replacement=value+1,expected_answer=cf['expected_answer'],
                            affected=affected,counterfactual_source=changed))
    return results


def names_for(split,condition,lexical):
    prefix={'train':'train_','development':'dev_','calibration':'cal_'}[split]
    if condition=='neutral':
        values=(['v0','v1','v2','v3','v4','v5','v6','v7'] if lexical==0 else ['n0','n1','n2','n3','n4','n5','n6','n7'])
    else:
        values=(['left_first','left_second','right_first','right_second','left_result','right_result','spare_value','left_other']
                if lexical==0 else ['lhs_first','lhs_second','rhs_first','rhs_second','lhs_result','rhs_result','spare_value','lhs_other'])
        if condition=='misleading':values[4],values[5]=values[5],values[4]
        elif condition!='informative':raise ValueError('unknown naming condition')
    return dict(zip(('a','b','c','d','r','s','spare','buffer'),[prefix+v for v in values]))


def error_alternatives(row):
    a,b,c,d=row['numeric_values'];r,s=a-b,c-d
    options=[dict(label='swapped_final_results',value=s-r),dict(label='combine_with_addition',value=r+s)]
    if row['family']=='retention_frontier':
        old,middle,penultimate=row['history_values']
        obsolete=[('initial',old)]+([('middle',middle),('penultimate',penultimate)] if row['updates']==3 else [])
        options += [dict(label='obsolete_a:'+name,value=(value-b)-(c-d)) for name,value in obsolete]
        options += [dict(label='competing_input_b_as_a',value=-s)]
    return options


def make_rows(config):
    if type(config['noise_pairs']) is not int or not 1<=config['noise_pairs']<=16:raise ValueError('nonempty bounded irrelevant block required')
    bank=numeric_bank(config);orders=list(permutations(('a','b','c','d')))
    if not 1<=config['templates']<=len(orders):raise ValueError('template count exceeds initialization orders')
    raw=[];calibration=[];per=config['numeric_per_template']
    for index,draw in enumerate(bank):
        template=index//per;base=f'frontier:{template}:{index%per}';values=draw['values'];history=draw['history']
        for updates,compute_order in product((1,3),(('left','right'),('right','left'))):
            for noise_pairs,early in [(0,None),(config['noise_pairs'],0),(config['noise_pairs'],1),(config['noise_pairs'],2)]:
                source,checkpoint=frontier_source(values,history,orders[template],updates,compute_order,early,noise_pairs,config.get('initialize_results',False))
                raw.append(dict(base_id=base,structural_group=f'frontier:{template}',family='retention_frontier',
                    canonical_source=source,numeric_values=values,history_values=history,sign_pair=draw['sign_pair'],
                    initialization_order=list(orders[template]),updates=updates,compute_order=list(compute_order),
                    noise_pairs=noise_pairs,early_count=early,checkpoint_statement=checkpoint,
                    live_bindings=4-early if noise_pairs else None))
        a,b,c,d=values
        calibration.append(dict(base_id=base,family='literal_arithmetic',source=f'direct = ({a} - {b}) - ({c} - {d})\ndirect',numeric_values=values,
                                history_values=history,sign_pair=draw['sign_pair'],condition='neutral',lexical_realization=0))
        for lexical in (0,1):
            x,y=('r0','r1') if lexical==0 else ('s0','s1')
            calibration.append(dict(base_id=base,family='decomposed_arithmetic',source=f'{x} = {a} - {b}\n{y} = {c} - {d}\n{x} - {y}',
                numeric_values=values,history_values=history,sign_pair=draw['sign_pair'],condition='neutral',lexical_realization=lexical))
    if config.get('initialize_results'):
        for row in raw:row['fixed_defined_variables']=8
    components=assign_splits(raw);rows=[]
    for base in raw:
        truth=execute(base['canonical_source']);cp=base['checkpoint_statement']
        interventions=checkpoint_interventions(base['canonical_source'],cp) if cp is not None else []
        if cp is not None and truth['liveness'][cp]['count']!=base['live_bindings']:raise ValueError('retention frontier does not have registered live count')
        if cp is not None and base.get('fixed_defined_variables') and len(truth['execution_trace'][cp]['values'])!=base['fixed_defined_variables']:raise ValueError('defined variable count differs')
        for condition,lexical in product(('neutral','informative','misleading'),(0,1)):
            mapping=names_for(base['split'],condition,lexical);source=rename(base['canonical_source'],mapping);executed=execute(source)
            live={} if cp is None else {mapping[n]:v for n,v in truth['execution_trace'][cp]['values'].items() if n in truth['liveness'][cp]['live_versions']}
            cf=[dict(variable=mapping[c['variable']],current_value=c['current_value'],replacement=c['replacement'],expected_answer=c['expected_answer'],affected=c['affected']) for c in interventions]
            row=dict(base,condition=condition,lexical_realization=lexical,rename_map=mapping,source=source,
                id='live-load:'+digest([source,'retention_frontier'])[:24],evaluation_role=ROLE,paired_group_id=base['base_id'],
                expected_answer=executed['expected_answer'],execution_trace=executed['execution_trace'],
                live_values_at_checkpoint=live,checkpoint_counterfactuals=cf)
            row['error_alternatives']=error_alternatives(row);rows.append(row)
    for item in calibration:
        source=ast.unparse(ast.parse(item['source']));truth=execute(source)
        row=dict(item,source=source,canonical_source=source,id='live-load:'+digest([source,item['family']])[:24],
                 split='calibration',evaluation_role=ROLE,paired_group_id=item['base_id'],expected_answer=truth['expected_answer'],
                 execution_trace=truth['execution_trace'],template_id='calibration:'+item['family'])
        row['error_alternatives']=error_alternatives(row);rows.append(row)
    return rows,components


def validate_rows(rows,generation=None,independent=False):
    if not rows or len({r['id'] for r in rows})!=len(rows):raise ValueError('missing or duplicated frontier identities')
    groups=defaultdict(list);base_splits=defaultdict(set);skeleton_splits=defaultdict(set);counterfactual_cache={}
    from .competition import alpha_skeleton
    for row in rows:
        if row['evaluation_role']!=ROLE or row['split'] not in ('train','development','calibration'):raise ValueError('final outcomes cannot enter frontier study')
        if row['family'] not in ('retention_frontier','literal_arithmetic','decomposed_arithmetic'):
            raise ValueError('unknown live-load family')
        if (row['family']=='retention_frontier')!=(row['split'] in ('train','development')):
            raise ValueError('program/calibration split roles differ')
        source=row['source'];truth=execute(source)
        if row['id']!='live-load:'+digest([source,row['family']])[:24] or truth['expected_answer']!=row['expected_answer'] or truth['execution_trace']!=row['execution_trace']:
            raise ValueError('frontier identity or execution trace differs')
        a,b,c,d=row['numeric_values'];r,s=a-b,c-d
        if row['expected_answer']!=r-s or r-s==0:raise ValueError('noncommutative output or sign design differs')
        if sum(isinstance(n,ast.BinOp) for n in ast.walk(ast.parse(source)))!=3:raise ValueError('arithmetic operation count must remain three')
        if row['error_alternatives']!=error_alternatives(row):raise ValueError('error alternatives differ')
        if row['family']!='retention_frontier':continue
        if row['rename_map']!=names_for(row['split'],row['condition'],row['lexical_realization']) or rename(row['canonical_source'],row['rename_map'])!=source:
            raise ValueError('semantic naming differs')
        literals={abs(n.value) for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Constant)}
        if any(abs(v) in literals for v in (r,s,r-s)):raise ValueError('computed intermediate/output magnitude appears as literal')
        owner=row['rename_map']['a']
        if sum(p['definition'].split('@')[0]==owner for p in truth['execution_trace'])-1!=row['updates']:
            raise ValueError('reassignment count differs')
        cp=row['checkpoint_statement']
        if cp is not None:
            key=(row['canonical_source'],cp)
            if key not in counterfactual_cache:counterfactual_cache[key]=checkpoint_interventions(*key)
            expected=[dict(variable=row['rename_map'][c['variable']],current_value=c['current_value'],replacement=c['replacement'],expected_answer=c['expected_answer'],affected=c['affected']) for c in counterfactual_cache[key]]
            if row['checkpoint_counterfactuals']!=expected:raise ValueError('checkpoint counterfactual labels differ')

            if truth['liveness'][cp]['count']!=row['live_bindings']:raise ValueError('registered live load differs')
            if row.get('fixed_defined_variables') and len(truth['execution_trace'][cp]['values'])!=row['fixed_defined_variables']:raise ValueError('defined variable count differs')
            actual={n:truth['execution_trace'][cp]['values'][n] for n in truth['liveness'][cp]['live_versions']}
            if row['live_values_at_checkpoint']!=actual:raise ValueError('live values differ')
        groups[row['base_id'],row['condition'],row['lexical_realization']].append(row)
        base_splits[row['base_id']].add(row['split']);skeleton_splits[alpha_skeleton(row['canonical_source'])].add(row['split'])
    if any(len(v)!=1 for v in [*base_splits.values(),*skeleton_splits.values()]):raise ValueError('structural or numeric-relative split leakage')
    for group in groups.values():
        if len(group)!=16:raise ValueError('incomplete update/order/frontier contrasts')
        if len({r['expected_answer'] for r in group})!=1:raise ValueError('schedule/update contrasts changed answer')
        states={digest(execute(r['source'])['execution_trace'][-1]['values']) for r in group}
        if len(states)!=1:raise ValueError('schedule/update contrasts changed complete final state')
        for noise in {r['noise_pairs'] for r in group}:
            subset=[r for r in group if r['noise_pairs']==noise]
            # Changing reassignment owner is deliberate; schedule alone reorders an identical multiset.
            for updates in (1,3):
                bags={tuple(sorted(ast.dump(s,include_attributes=False) for s in ast.parse(r['source']).body)) for r in subset if r['updates']==updates}
                if len(bags)!=1:raise ValueError('scheduling changed statement multiset')
            literal_bags={tuple(sorted(n.value for n in ast.walk(ast.parse(r['source'])) if isinstance(n,ast.Constant))) for r in subset}
            if len(literal_bags)!=1:raise ValueError('updates changed literal exposure')
    if generation is not None:
        expected,_=make_rows(generation)
        if rows!=expected:raise ValueError('frontier dataset differs from registered full generation')
    if independent:
        sources=[r['source'] for r in rows]
        truths=[dict(expected_answer=r['expected_answer'],execution_trace=r['execution_trace']) for r in rows]
        # Counterfactual execution checks use canonical representatives once per schedule,
        # then bijective AST renaming carries the verified relation to every rendering.
        seen=set()
        for row in rows:
            if row['family']!='retention_frontier' or row['checkpoint_statement'] is None:continue
            key=row['canonical_source']
            if key in seen:continue
            seen.add(key)
            for cf in checkpoint_interventions(key,row['checkpoint_statement']):
                sources.append(cf['counterfactual_source']);truths.append(execute(cf['counterfactual_source']))
        for start in range(0,len(sources),128):
            for truth,oracle in zip(truths[start:start+128],python_oracle(sources[start:start+128])):
                if truth['expected_answer']!=oracle['answer'] or [p['values'] for p in truth['execution_trace']]!=oracle['trace']:
                    raise ValueError('independent Python full trace differs')
    return rows


def build(config):
    rows,components=make_rows(config['generation'])
    print(f'Generated {len(rows)} rows in {components} structural components; checking semantic and independent Python traces.',flush=True)
    validate_rows(rows,independent=True)
    path=Path(config['dataset']);content=''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows).encode();immutable(path,content)
    manifest=dict(sha256=sha(path),rows=len(rows),evaluation_role=ROLE,generation=config['generation'],generation_config_hash=digest(config['generation']),
        structural_components=components,counts=dict(Counter(r['family'] for r in rows)),
        independent_python_traces_passed=True,checkpoint_functional_relevance_passed=True,generated_holdouts_opened=False)
    immutable(path.with_suffix('.manifest.json'),(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode());return manifest


def statement_end_token(text,offsets,end):
    """A token may finish with whitespace, but must not include later code."""
    matches=[j for j,(a,b) in enumerate(offsets) if a<end<=b and not text[end:b].strip()]
    if len(matches)!=1:raise ValueError('statement end token crosses later code or is missing')
    return matches[0]


def validate_token_layouts(cases,tokenizer=None):
    """All schedule contrasts preserve full token bags; naming pair lengths match."""
    schedules=defaultdict(list);naming=defaultdict(dict);updates=defaultdict(list)
    for case in cases:
        row=case['record']
        if row['family']!='retention_frontier':continue
        if tokenizer is not None:
            from .calibration import printed_source
            body=printed_source(row['source']);text=case['prompt'];start=text.index(body)
            encoded=tokenizer(text,add_special_tokens=False,return_offsets_mapping=True)
            if encoded['input_ids']!=case['input_token_ids']:raise ValueError('offset encoding differs from registered prompt')
            lines=body.splitlines(keepends=True);ends=[]
            for i,line in enumerate(lines):
                end=start+sum(map(len,lines[:i]))+len(line.rstrip('\n'))
                ends.append(statement_end_token(text,encoded['offset_mapping'],end))
            cp=row['checkpoint_statement'];layout=dict(statement_end_positions=ends,query_end=ends[-1])
            if cp is not None:
                trace=row['execution_trace'];latest={p['definition']:p['statement'] for p in trace[:cp+1]}
                point=execute(row['source'])['liveness'][cp]
                ages={name:ends[cp]-ends[latest[definition]] for name,definition in point['live_versions'].items()}
                layout.update(checkpoint_end=ends[cp],noise_end=ends[cp+2*row['noise_pairs']],
                    checkpoint_to_query_tokens=ends[-1]-ends[cp],live_definition_ages=ages)
            case['live_load_token_layout']=layout
        key=(row['base_id'],row['condition'],row['lexical_realization'],row['updates'],row['noise_pairs'])
        schedules[key].append(case)
        key=(row['base_id'],row['lexical_realization'],row['updates'],tuple(row['compute_order']),row['noise_pairs'],row['early_count'])
        naming[key][row['condition']]=case
        key=(row['base_id'],row['condition'],row['lexical_realization'],tuple(row['compute_order']),row['noise_pairs'],row['early_count'])
        updates[key].append(case)
    for group in schedules.values():
        lengths={len(c['input_token_ids']) for c in group};bags={tuple(sorted(Counter(c['input_token_ids']).items())) for c in group}
        if len(lengths)!=1 or len(bags)!=1:raise ValueError('schedule contrasts changed full token multiset/length')
    for group in naming.values():
        if set(group)!={'neutral','informative','misleading'} or len(group['informative']['input_token_ids'])!=len(group['misleading']['input_token_ids']):
            raise ValueError('informative/misleading naming token lengths differ')
    for group in updates.values():
        if len(group)!=2 or len({len(c['input_token_ids']) for c in group})!=1:raise ValueError('reassignment contrasts changed prompt length')
    return dict(status='passed',schedule_groups=len(schedules),naming_groups=len(naming),update_groups=len(updates),
                note='Neutral naming may have a different token length. Noise versus clean length intentionally differs; comparisons share clean anchors.')


def paired_contrast(name,records,seed=907,draws=2000):
    """Records contain paired scalar correctness differences, never row bootstrap."""
    import numpy as np
    clusters=defaultdict(list)
    for template,value in records:clusters[template].append(value)
    if not clusters:raise ValueError('empty paired contrast')
    keys=sorted(clusters);totals=np.array([sum(clusters[k]) for k in keys],float);counts=np.array([len(clusters[k]) for k in keys],float)
    rng=np.random.default_rng(seed);sample=rng.integers(0,len(keys),size=(draws,len(keys)))
    estimates=totals[sample].sum(1)/counts[sample].sum(1)
    low,high=np.quantile(estimates,[.025,.975])
    return dict(name=name,n=int(counts.sum()),structural_components=len(keys),mean=float(totals.sum()/counts.sum()),
                exploratory_component_bootstrap_95=[float(low),float(high)],draws=draws,seed=seed,
                interpretation='Exploratory structural-component resampling; no multiplicity-adjusted confirmatory claim.')


def collect(config):
    """Compute every fixed contrast from audited responses without model selection."""
    from .checkpoint_suite import prepared
    root=Path(config['run_dir'])/'checkpoint_suite';checked=json.loads((root/'audit.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
    if checked['status']!='passed' or checked['identity_hash']!=manifest['identity_hash'] or manifest['identity']['config']!=config or checked['identity_hash']!=digest(manifest['identity']):
        raise ValueError('completed pinned live-load audit required')
    if sha(root/'responses.jsonl')!=manifest['responses_sha256']:raise ValueError('audited responses changed')
    _,cases=prepared(config,checked['preflight']['source_sha256']);responses=read_jsonl(root/'responses.jsonl')
    records=[(c['record'],r['score'],c) for c,r in zip(cases,responses)]
    cells=defaultdict(list);geometry=defaultdict(list);lookup={};families=defaultdict(list)
    for row,score,case in records:
        families[row['family']].append(score)
        if row['family']!='retention_frontier':continue
        load=row['live_bindings'];key=(row['split'],row['condition'],row['updates'],tuple(row['compute_order']),load)
        cells[key].append(score)
        key=(row['base_id'],row['condition'],row['lexical_realization'],row['updates'],tuple(row['compute_order']),load)
        if key in lookup:raise ValueError('duplicate logical condition')
        lookup[key]=(row,score)
        key=(row['condition'],row['updates'],load)
        layout=case['live_load_token_layout'];geometry[key].append(dict(prompt_tokens=len(case['input_token_ids']),
            checkpoint_to_query=layout.get('checkpoint_to_query_tokens'),live_ages=list(layout.get('live_definition_ages',{}).values())))
    gate_cells=[]
    for family in ('literal_arithmetic','decomposed_arithmetic'):
        values=families[family];gate_cells.append(dict(cell=[family,'calibration'],n=len(values),correct=sum(s['correct'] for s in values),invalid=sum(not s['valid'] for s in values)))
    for key,values in sorted(cells.items(),key=lambda kv:repr(kv[0])):
        split,condition,updates,order,load=key
        if condition=='neutral' and load is None:
            gate_cells.append(dict(cell=['clean_program',split,updates,list(order)],n=len(values),correct=sum(s['correct'] for s in values),invalid=sum(not s['valid'] for s in values)))
    thresholds=config['reliability_gate']
    for cell in gate_cells:
        cell['passed']=(cell['n']>=thresholds['minimum_cell_n'] and cell['correct']/cell['n']>=thresholds['minimum_accuracy'] and cell['invalid']/cell['n']<=thresholds['maximum_invalid_rate'])
    gate=dict(status='passed' if all(c['passed'] for c in gate_cells) else 'failed',cells=gate_cells,thresholds=thresholds,
              purpose='Fixed calibration/clean-program reliability description for future follow-up; all behavior remains in the analysis regardless of result.')
    contrasts=defaultdict(list)
    # A shared no-noise response is reused as an anchor, never inferred three times.
    for key,(row,score) in lookup.items():
        base,condition,lexical,updates,order,load=key;component=row['template_id'];correct=int(score['correct'])
        if load==2:
            for other in (3,4):
                alternate=lookup[base,condition,lexical,updates,order,other][1]
                contrasts[f'live{other}_minus_live2:{condition}:updates{updates}'].append((component,int(alternate['correct'])-correct))
        if load is not None:
            clean=lookup[base,condition,lexical,updates,order,None][1]
            contrasts[f'noise_minus_clean:live{load}:{condition}:updates{updates}'].append((component,correct-int(clean['correct'])))
        if updates==1:
            high=lookup[base,condition,lexical,3,order,load][1]
            contrasts[f'updates3_minus1:{condition}:live{load}'].append((component,int(high['correct'])-correct))
        if condition=='informative':
            misleading=lookup[base,'misleading',lexical,updates,order,load][1]
            contrasts[f'misleading_minus_informative:updates{updates}:live{load}'].append((component,int(misleading['correct'])-correct))
        if load==2 and condition=='informative':
            def truth(c,u,l):return int(lookup[base,c,lexical,u,order,l][1]['correct'])
            def naming_load(u):return (truth('misleading',u,4)-truth('misleading',u,2))-(truth('informative',u,4)-truth('informative',u,2))
            contrasts[f'naming_by_load:updates{updates}'].append((component,naming_load(updates)))
            if updates==1:contrasts['naming_by_load_by_updates'].append((component,naming_load(3)-naming_load(1)))
        if load==2 and updates==1:
            effect=(int(lookup[base,condition,lexical,3,order,4][1]['correct'])-int(lookup[base,condition,lexical,3,order,2][1]['correct']))-(int(lookup[base,condition,lexical,1,order,4][1]['correct'])-correct)
            contrasts[f'updates_by_load:{condition}'].append((component,effect))
    output_cells=[dict(split=k[0],condition=k[1],updates=k[2],compute_order=list(k[3]),live_bindings=k[4],
        n=len(v),correct=sum(s['correct'] for s in v),invalid=sum(not s['valid'] for s in v)) for k,v in sorted(cells.items(),key=lambda kv:repr(kv[0]))]
    geometry_rows=[]
    for key,values in sorted(geometry.items(),key=lambda kv:repr(kv[0])):
        def bounds(v):return dict(min=min(v),max=max(v),mean=sum(v)/len(v)) if v else None
        geometry_rows.append(dict(condition=key[0],updates=key[1],live_bindings=key[2],prompt_tokens=bounds([v['prompt_tokens'] for v in values]),
            checkpoint_to_query_tokens=bounds([v['checkpoint_to_query'] for v in values if v['checkpoint_to_query'] is not None]),
            live_definition_token_age=bounds([a for v in values for a in v['live_ages']])))
    alternatives=Counter(label for row,score,_ in records for label in score.get('compatible_error_labels',[]))
    return dict(status='complete_audited',model=config['model'],revision=config['model_revision'],identity_hash=checked['identity_hash'],
        audit_sha256=sha(root/'audit.json'),responses_sha256=sha(root/'responses.jsonl'),n=len(records),primary_contrasts=config['primary_contrasts'],
        correct=sum(s['correct'] for _,s,_ in records),invalid=sum(not s['valid'] for _,s,_ in records),
        family_cells=[dict(family=k,n=len(v),correct=sum(s['correct'] for s in v),invalid=sum(not s['valid'] for s in v)) for k,v in sorted(families.items())],
        program_cells=output_cells,reliability_gate=gate,token_geometry=geometry_rows,
        contrasts=[paired_contrast(name,values) for name,values in sorted(contrasts.items())],
        compatible_error_label_counts=dict(alternatives),generated_holdouts_opened=False,
        limitation='Scheduling changes true live bindings and computation/assignment distances together. Numeric literal values exclude computed magnitudes, not every digit subtoken. These are exploratory discovery results, not an isolated capacity or causal-mechanism test.')


def review(config):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from .registry import code_identity
    existing=Path(config['review_artifact'])
    if existing.exists():
        result=json.loads(existing.read_text());root=Path(config['run_dir'])/'checkpoint_suite'
        if result['audit_sha256']!=sha(root/'audit.json') or result['responses_sha256']!=sha(root/'responses.jsonl') or result['report_sha256']!=sha(config['report']) or result['figure_sha256']!=sha(config['figure']):
            raise ValueError('completed live-load review changed')
        return dict(status='complete_reused',report=config['report'])
    result=collect(config);result['analysis_source']=code_identity()
    lines=['# Computed retention-frontier discovery: '+config['model'],'',
        f"All {result['n']:,} responses retained; {result['correct']:,} correct and {result['invalid']:,} invalid. Reliability gate: **{result['reliability_gate']['status']}**. A failed gate does not remove behavioral results or qualify causal follow-up.",'',
        result['limitation'],'','Predeclared primary exploratory contrasts: '+', '.join(result['primary_contrasts'])+'.','','The same two independent subtractions move across an irrelevant eight-assignment block. The frontier contains 2, 3 or 4 functionally output-relevant bindings. Exact token and statement multisets, arithmetic counts, complete final states and answers are preserved within schedule contrasts. Controls without the block share one response per computation order rather than duplicate identical prompts. Informative/misleading lengths and reassignment-pair lengths match; neutral naming may differ.','',
        '| Calibration family | Correct / n | Invalid |','|---|---:|---:|']
    for cell in result['family_cells']:lines.append(f"| {cell['family']} | {cell['correct']}/{cell['n']} | {cell['invalid']} |")
    lines+=['','| Contrast | Paired n | Components | Accuracy difference | Exploratory 95% interval |','|---|---:|---:|---:|---|']
    for contrast in result['contrasts']:
        lo,hi=contrast['exploratory_component_bootstrap_95'];lines.append(f"| {contrast['name']} | {contrast['n']} | {contrast['structural_components']} | {contrast['mean']:+.2%} | [{lo:+.2%}, {hi:+.2%}] |")
    conditions=('neutral','informative','misleading');fig,axes=plt.subplots(1,3,figsize=(13,4),sharey=True)
    for condition,ax in zip(conditions,axes):
        for updates in (1,3):
            ys=[]
            for load in (2,3,4):
                cells=[c for c in result['program_cells'] if c['condition']==condition and c['updates']==updates and c['live_bindings']==load]
                ys.append(sum(c['correct'] for c in cells)/sum(c['n'] for c in cells))
            ax.plot([2,3,4],ys,marker='o',label=f'{updates} reassignments')
        ax.set(title=condition,xlabel='Functionally live bindings across irrelevant block',ylabel='Accuracy',xticks=[2,3,4],ylim=(0,1));ax.legend()
    figure=Path(config['figure']);figure.parent.mkdir(parents=True,exist_ok=True);fig.tight_layout();fig.savefig(figure);fig.savefig(figure.with_suffix('.png'),dpi=150);plt.close(fig)
    lines+=['',f'![All naming/update curves]({figure.name})','',
        'Full split/order cells, reliability cells, token distances, label ambiguities and all registered contrasts are saved in the review artifact. Intervals resample structural components and are exploratory without multiplicity adjustment. Initialization orders are not independent model or program-family replications. No final/extrapolation outcomes or language-model training were used.','']
    immutable(config['report'],('\n'.join(lines)).encode())
    result.update(report=config['report'],report_sha256=sha(config['report']),figure=str(figure),figure_sha256=sha(figure))
    immutable(existing,(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status='complete_audited',report=config['report'],reliability_gate=result['reliability_gate']['status'])


def compare(config):
    """Combine the two complete audited reviews without selecting a winner."""
    from .registry import code_identity
    results={};checksums={};common=None
    for name,spec in config['runs'].items():
        if sha(spec['config'])!=spec['sha256']:raise ValueError('comparison model configuration changed')
        model_config=json.loads(Path(spec['config']).read_text());path=Path(model_config['review_artifact'])
        review=json.loads(path.read_text());root=Path(model_config['run_dir'])/'checkpoint_suite'
        manifest=json.loads((root/'manifest.json').read_text())
        if (review['status']!='complete_audited' or review['identity_hash']!=manifest['identity_hash']
                or review['audit_sha256']!=sha(root/'audit.json') or review['responses_sha256']!=sha(root/'responses.jsonl')
                or review['report_sha256']!=sha(model_config['report']) or review['figure_sha256']!=sha(model_config['figure'])):
            raise ValueError('comparison requires unchanged audited model reviews')
        identity=(model_config['dataset'],model_config['generation'],model_config['primary_contrasts'])
        if common is not None and identity!=common:raise ValueError('comparison cohorts or primary contrasts differ')
        common=identity;checksums[str(path)]=sha(path);results[name]=review
    if len(results)!=2:raise ValueError('fixed two-model comparison required')
    lines=['# Computed retention-frontier results','',
        f"Both preselected cached models completed the full cohort: {sum(r['n'] for r in results.values()):,} predictions. All cases remain in the results regardless of the fixed clean/arithmetic reliability gate.",'',
        'The program retains 2, 3 or 4 functionally relevant bindings across irrelevant code while all eight variables remain defined. Arithmetic, final states, answers and token multisets are matched within scheduling contrasts. Scheduling also changes computation timing and definition/query distances, so the result does not isolate a memory-capacity or binding mechanism. This is behavioral comparison, not causal-mechanism replication.','',
        '| Model | Correct / n | Invalid | Reliability gate |','|---|---:|---:|---|']
    for name,result in results.items():lines.append(f"| {name} | {result['correct']}/{result['n']} | {result['invalid']} | {result['reliability_gate']['status']} |")
    lines+=['','| Model | Predeclared primary contrast | Paired n | Difference | Exploratory component interval |','|---|---|---:|---:|---|']
    for name,result in results.items():
        contrasts={c['name']:c for c in result['contrasts']}
        for primary in result['primary_contrasts']:
            c=contrasts[primary];lo,hi=c['exploratory_component_bootstrap_95']
            lines.append(f"| {name} | {primary} | {c['n']} | {c['mean']:+.2%} | [{lo:+.2%}, {hi:+.2%}] |")
    lines+=['','All 56 fixed contrasts per model, complete reliability cells, token geometry and naming/update/load curves are in the individual reports. Intervals resample structural components and are exploratory without multiplicity adjustment. Models share the same generated bank; two checkpoints do not represent independent program-family replications.','']
    for name,spec in config['runs'].items():
        cfg=json.loads(Path(spec['config']).read_text());lines.append(f"- [{name}]({Path(cfg['report']).name})")
    lines+=['','The first dataset revision was retired before model inference to hold defined-variable counts fixed. Historical failed gates and original final/extrapolation outcomes remain unchanged. No language-model training, final forecast or optional extension was run.','']
    immutable(config['report'],('\n'.join(lines)).encode())
    result=dict(status='passed',complete=True,models=results,review_checksums=checksums,report=config['report'],report_sha256=sha(config['report']),
                total_predictions=sum(r['n'] for r in results.values()),analysis_source=code_identity(),generated_holdouts_opened=False)
    immutable(config['comparison_artifact'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status='complete_audited',report=config['report'],total_predictions=result['total_predictions'])


def backend_sample(cases,seed=117):
    """One complete sign pair per structural split, selected without model scores."""
    selected=set()
    for split in ('train','development'):
        eligible={c['record']['sign_pair'] for c in cases if c['record']['family']=='retention_frontier'
                  and c['record']['split']==split and c['record']['expected_answer']>0}
        if not eligible:raise ValueError('backend sample needs both structural splits')
        selected.add(min(eligible,key=lambda k:digest([seed,split,k])))
    result=[c for c in cases if c['record']['sign_pair'] in selected]
    if len(result)!=396 or len({c['record']['base_id'] for c in result})!=4:
        raise ValueError('backend sample must preserve all 396 sign-pair relatives and controls')
    return result


def prepare_backend(config):
    from .checkpoint_suite import prepared
    from .registry import code_identity
    if sha(config['upstream_config'])!=config['upstream_config_sha256']:raise ValueError('backend upstream configuration changed')
    upstream=json.loads(Path(config['upstream_config']).read_text());root=Path(upstream['run_dir'])/'checkpoint_suite'
    audit=json.loads((root/'audit.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
    if audit['status']!='passed' or audit['identity_hash']!=manifest['identity_hash'] or sha(root/'responses.jsonl')!=manifest['responses_sha256']:
        raise ValueError('backend comparison needs complete audited upstream responses')
    _,all_cases=prepared(upstream,audit['preflight']['source_sha256']);cases=backend_sample(all_cases,config['selection_seed'])
    for key in ('model','model_revision','tokenizer_revision','dtype','tokenization_mode'):
        if config[key]!=upstream[key]:raise ValueError('backend checkpoint contract differs')
    keys={c['id'] for c in cases};references={r['id']:r for r in read_jsonl(root/'responses.jsonl') if r['id'] in keys}
    if set(references)!=keys:raise ValueError('backend reference coverage differs')
    bundle=dict(cases=cases,references=references,padded_width=max(len(c['input_token_ids']) for c in cases))
    immutable(config['backend_cases'],(json.dumps(bundle,sort_keys=True)+'\n').encode())
    result=dict(status='passed',cases=len(cases),config_hash=digest(config),source_sha256=code_identity()['source_sha256'],
        bundle_sha256=sha(config['backend_cases']),upstream_identity=manifest['identity_hash'],upstream_audit_sha256=sha(root/'audit.json'),
        purpose='Post-hoc software diagnosis. Complete groups selected by split/sign-pair hashes, without response accuracy.',generated_holdouts_opened=False)
    immutable(config['backend_preflight'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode());return result


def backend_inputs(config,expected_source=None):
    from .registry import code_identity
    qa=json.loads(Path(config['backend_preflight']).read_text())
    if qa['status']!='passed' or qa['config_hash']!=digest(config) or qa['source_sha256']!=(expected_source or code_identity()['source_sha256']) or qa['bundle_sha256']!=sha(config['backend_cases']):
        raise ValueError('matching backend preparation required')
    upstream=json.loads(Path(config['upstream_config']).read_text())
    if sha(config['upstream_config'])!=config['upstream_config_sha256'] or sha(Path(upstream['run_dir'])/'checkpoint_suite/audit.json')!=qa['upstream_audit_sha256']:raise ValueError('backend upstream evidence changed')
    return qa,json.loads(Path(config['backend_cases']).read_text())


def backend_summary(config,records):
    groups=defaultdict(list)
    for row in records:groups[row['family']].append(row)
    return dict(status='complete',cases=len(records),hf_correct=sum(r['score']['correct'] for r in records),
        vllm_correct=sum(r['reference_score']['correct'] for r in records),
        parsed_prediction_matches=sum(r['parsed_prediction_matches'] for r in records),
        first_token_matches=sum(r['first_token'] is not None and bool(r['reference_output_token_ids']) and r['first_token']==r['reference_output_token_ids'][0] for r in records),
        hf_invalid=sum(not r['score']['valid'] for r in records),vllm_invalid=sum(not r['reference_score']['valid'] for r in records),
        uncached_cases=sum('uncached' in r for r in records),
        uncached_raw_matches=sum(r['uncached']['raw_response']==r['raw_response'] for r in records if 'uncached' in r),
        uncached_invalid=sum(not r['uncached']['valid'] for r in records if 'uncached' in r),
        uncached_prediction_matches=sum(r['uncached']['valid'] and r['score']['valid'] and r['uncached']['prediction']==r['score']['prediction'] for r in records if 'uncached' in r),
        family_cells=[dict(family=k,n=len(v),hf_correct=sum(r['score']['correct'] for r in v),vllm_correct=sum(r['reference_score']['correct'] for r in v),
                          prediction_matches=sum(r['parsed_prediction_matches'] for r in v)) for k,v in sorted(groups.items())],
        interpretation='Post-hoc backend/cache diagnostic on two complete structural groups. Agreement does not establish correct execution or a mechanism; differences are retained.',
        generated_holdouts_opened=False)


def run_backend(config):
    from .registry import guarded
    return guarded(_run_backend)(config)


def generated_stop_flags(tokenizer,token_rows,prompt_width,stop_strings=('\n\n',)):
    """Stop strings apply to generated text, never across the prompt boundary."""
    return [any(stop in tokenizer.decode(row[prompt_width:],skip_special_tokens=True) for stop in stop_strings) for row in token_rows]


def _run_backend(config):
    import torch,time
    from transformers import StoppingCriteria,StoppingCriteriaList
    from .checkpoint_suite import score_case
    from .model_adapter import load
    from .registry import begin,finish
    from .value_transfer import _encode
    qa,data=backend_inputs(config);out,manifest=begin(config,'interface_diagnostics',reuse_complete=True)
    if manifest['status']=='complete':return json.loads((out/'summary.json').read_text())
    started=time.monotonic();tok,model=load(config);model.set_attn_implementation('sdpa');records=[]
    class GeneratedOnlyStop(StoppingCriteria):
        def __call__(self,input_ids,scores,**kwargs):
            flags=generated_stop_flags(tok,input_ids[:,data['padded_width']:].tolist(),0)
            return torch.tensor(flags,device=input_ids.device,dtype=torch.bool)
    criterion=GeneratedOnlyStop();cases=data['cases']
    for start in range(0,len(cases),config['batch_size']):
        part=cases[start:start+config['batch_size']];encoded=_encode(tok,part,model.device,data['padded_width'])
        with torch.inference_mode():
            output=model.generate(**encoded,do_sample=False,num_beams=1,use_cache=True,max_new_tokens=16,repetition_penalty=1.,
                eos_token_id=config['eos_token_ids'],pad_token_id=tok.pad_token_id,stopping_criteria=StoppingCriteriaList([criterion]))
        for case,tail in zip(part,output[:,encoded.input_ids.shape[1]:].tolist()):
            first_token=tail[0] if tail else None
            for i,token in enumerate(tail):
                if token in config['eos_token_ids']:tail=tail[:i];break
            raw=tok.decode(tail,skip_special_tokens=True);reference=data['references'][case['id']];observed=score_case(case,raw)
            row=dict(id=case['id'],family=case['record']['family'],raw_response=raw,output_token_ids=tail,first_token=first_token,
                score=observed,reference_score=reference['score'],reference_output_token_ids=reference['output_token_ids'],
                parsed_prediction_matches=observed['valid'] and reference['score']['valid'] and observed['prediction']==reference['score']['prediction'])
            if row['family']!='retention_frontier':
                generated=[]
                with torch.inference_mode():
                    for _ in range(16):
                        ids=torch.tensor([case['input_token_ids']+generated],device=model.device)
                        logits=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=1).logits[0,-1]
                        token=int(logits.argmax());generated.append(token)
                        if token in config['eos_token_ids'] or '\n\n' in tok.decode(generated[-6:],skip_special_tokens=True):break
                uncached_raw=tok.decode(generated,skip_special_tokens=True)
                row['uncached']=dict(raw_response=uncached_raw,output_token_ids=generated,**score_case(case,uncached_raw))
            records.append(row)
        print(f'Backend replay {len(records)}/{len(cases)}',flush=True)
    result=backend_summary(config,records);result.update(preflight=qa,device_name=torch.cuda.get_device_name(),
        torch_peak_memory_bytes=torch.cuda.max_memory_allocated(),model_generation_config=model.generation_config.to_dict())
    from .datasets import write_json
    write_json(out/'responses.json',records);result['responses_sha256']=sha(out/'responses.json');write_json(out/'summary.json',result)
    finish(out,manifest,time.monotonic()-started);return result


def audit_backend(config):
    from .checkpoint_suite import score_case
    out=Path(config['run_dir'])/'interface_diagnostics';manifest=json.loads((out/'manifest.json').read_text());summary=json.loads((out/'summary.json').read_text())
    if manifest['status']!='complete' or manifest['identity']['config']!=config or manifest['identity_hash']!=digest(manifest['identity']) or sha(out/'responses.json')!=summary['responses_sha256']:
        raise ValueError('complete pinned backend replay required')
    qa,data=backend_inputs(config,manifest['identity']['code']['source_sha256']);rows=json.loads((out/'responses.json').read_text())
    if [r['id'] for r in rows]!=[c['id'] for c in data['cases']]:raise ValueError('backend replay coverage differs')
    for case,row in zip(data['cases'],rows):
        ref=data['references'][case['id']];observed=score_case(case,row['raw_response'])
        if row['score']!=observed or row['reference_score']!=ref['score'] or row['reference_output_token_ids']!=ref['output_token_ids']:
            raise ValueError('backend score, reference or output differs')
        if row['parsed_prediction_matches']!=(observed['valid'] and ref['score']['valid'] and observed['prediction']==ref['score']['prediction']):raise ValueError('backend agreement score differs')
        if 'uncached' in row:
            if any(row['uncached'][k]!=v for k,v in score_case(case,row['uncached']['raw_response']).items()):raise ValueError('uncached reference score differs')
    expected=backend_summary(config,rows)
    if any(summary.get(k)!=v for k,v in expected.items()):raise ValueError('backend summary differs')
    result=dict(status='passed',identity_hash=manifest['identity_hash'],summary_sha256=sha(out/'summary.json'),**{k:v for k,v in expected.items() if k!='status'})
    immutable(out/'audit.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode());return result


def backend_report(config):
    """Publish the corrected diagnostic after both replay audits complete."""
    from .registry import code_identity
    results={};proofs={}
    for name,spec in config['runs'].items():
        if sha(spec['config'])!=spec['sha256']:raise ValueError('backend report configuration changed')
        cfg=json.loads(Path(spec['config']).read_text())
        if cfg.get('stopping_policy')!='generated_text_only_v2':raise ValueError('corrected completion-only stopping required')
        results[name]=audit_backend(cfg)
        folder=Path(cfg['run_dir'])/'interface_diagnostics';proofs[str(folder/'audit.json')]=sha(folder/'audit.json')
    lines=['# Corrected cross-backend and cache diagnostic','',
        'This post-hoc software check replays 396 exact inputs per model: one complete sign pair in training and one in development, with every naming/update/order/frontier and arithmetic-control relative retained. Selection used fixed hashes rather than response accuracy. These two structural components do not estimate full-cohort accuracy or provide independent replication.','',
        'The first CodeLlama Transformers diagnostic was truncated by a stop-string match spanning the prompt and first generated newline. Its original responses remain preserved. The corrected harness checks stop strings only in generated text; the original 76,032-response vLLM study already used generated-text stopping and remains unchanged.','',
        '| Model | Transformers correct / 396 | vLLM correct / 396 | Parsed predictions matching | HF invalid | vLLM invalid |','|---|---:|---:|---:|---:|---:|']
    for name,r in results.items():lines.append(f"| {name} | {r['hf_correct']} | {r['vllm_correct']} | {r['parsed_prediction_matches']}/396 | {r['hf_invalid']} | {r['vllm_invalid']} |")
    lines+=['','| Model | Uncached controls | Raw decoded text matching cached generation | Valid parsed predictions matching | Uncached invalid |','|---|---:|---:|---:|---:|']
    for name,r in results.items():lines.append(f"| {name} | {r['uncached_cases']} | {r['uncached_raw_matches']} | {r['uncached_prediction_matches']} | {r['uncached_invalid']} |")
    lines+=['','Raw agreement and valid parsed-answer agreement are different: two identical malformed responses count as raw agreement, but never as a valid prediction match. First-token agreement and every raw response are retained in the machine-readable audits.','',
        'Both full-cohort models failed the fixed arithmetic/clean-program reliability gate. These diagnostics report backend and cache sensitivity without altering those gates or selecting a favorable subset as the scientific result. See the [full study comparison](live_load_results_v2.md). No selective binding mechanism, final-test forecast or language-model training is claimed.','']
    immutable(config['report'],('\n'.join(lines)).encode())
    result=dict(status='passed',complete=True,models=results,audit_checksums=proofs,report=config['report'],report_sha256=sha(config['report']),
                analysis_source=code_identity(),primary_vllm_results_changed=False,generated_holdouts_opened=False)
    immutable(config['artifact'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status='complete_audited',report=config['report'])
