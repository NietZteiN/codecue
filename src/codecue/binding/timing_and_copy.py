"""Explicit query timing and semantic-equivalence tests at an earlier copy site."""
import ast
from collections import Counter, defaultdict
import json
from pathlib import Path

from .datasets import digest, read_jsonl, write_json
from .interpreter import execute, python_oracle
from .published_benchmarks import immutable, sha
from .registry import code_identity


COPY_INSTRUCTIONS = (
    'What does this Python 3 program print? Give only the signed integer output, without explanation.',
    'Run this Python 3 code mentally and return only the integer that it prints.',
    'Determine the printed integer after executing these assignments in order. Respond with that integer alone.',
)
TIMING_INSTRUCTIONS = (
    'Execute the Python assignments. Report only the final integer value of the variable named by the Target line.',
    'Track the assignments below in order. Return only the final integer held by the specified Target variable.',
    'Determine the final value of the Target variable after these Python assignments. Give that integer alone.',
)


def anchors(config):
    path = config['generation']['anchor_prepared']
    if sha(path) != config['generation']['anchor_prepared_sha256']:
        raise ValueError('study anchor checksum differs')
    return json.loads(Path(path).read_text())['cases']


def transformed_source(source, form, scratch):
    if form == 'anchor':
        return source
    tree = ast.parse(source)
    if form == 'reordered':
        # The second-variable initialization and saving the first variable commute.
        tree.body[2], tree.body[3] = tree.body[3], tree.body[2]
    elif form == 'renamed':
        class Rename(ast.NodeTransformer):
            def visit_Name(self, node):
                return ast.copy_location(ast.Name(id='cache' if node.id == scratch else node.id, ctx=node.ctx), node)
        tree = Rename().visit(tree)
    else:
        raise ValueError('unknown semantic source form')
    return ast.unparse(ast.fix_missing_locations(tree))


def canonical_final(source, scratch):
    state = execute(source)['execution_trace'][-1]['values']
    return {('__temporary' if key == scratch else key): value for key, value in state.items()}


def make_rows(config):
    rows = []
    timing = config['assay'] == 'query_timing'
    for key, case in sorted(anchors(config).items()):
        original = case['record']
        if not timing and original['family'] != 'ownership':
            continue
        scratch = 'buffer' if original['lexical_realization'] == 0 else 'temp'
        forms = ('early', 'late') if timing else ('anchor', 'reordered', 'renamed')
        for instruction in range(3):
            for form in forms:
                source = original['source'] if timing else transformed_source(original['source'], form, scratch)
                row = {k: original[k] for k in ('family','mapping','query','query_role','numeric_group','lexical_realization')}
                row.update(id='timing-copy:' + digest([config['assay'], key, instruction, form])[:24],
                    anchor_id=key, instruction=instruction, source_form=form, source=source,
                    binding_values=original['literal_values'], expected_answer=execute(source)['expected_answer'],
                    scratch_name='cache' if form == 'renamed' else scratch,
                    split='development', evaluation_role=config['assay']+'_discovery')
                rows.append(row)
    return rows


def pairs_for(config, rows):
    if config['assay'] == 'query_timing':
        return []  # Behavioral timing/capture study; no hidden-state interventions requested.
    groups = defaultdict(dict)
    for row in rows:
        groups[row['anchor_id'], row['instruction']][row['source_form']] = row
    pairs = []
    for (key, instruction), forms in sorted(groups.items()):
        if set(forms) != {'anchor','reordered','renamed'}:
            raise ValueError('copy study must retain all semantic forms')
        for alternate in ('reordered','renamed'):
            for reverse in (False,True):
                a,b=forms['anchor'],forms[alternate]
                recipient,donor=(b,a) if reverse else (a,b)
                pairs.append(dict(id=digest([recipient['id'],donor['id']]),group_id=key,recipient=recipient['id'],donor=donor['id'],
                    slot=1,reverse=reverse,transformation=alternate,instruction=instruction,
                    replacement=recipient['expected_answer'],
                    baseline_answer=next(v for v in recipient['binding_values'] if v!=recipient['expected_answer']),
                    counterfactual_answer=donor['expected_answer'],affected=False,
                    family=recipient['family'],query_role=recipient['query_role'],query=recipient['query'],
                    mapping=recipient['mapping'],numeric_group=recipient['numeric_group'],lexical_realization=recipient['lexical_realization']))
    return pairs


def validate(config, rows, independent=False):
    if rows != make_rows(config) or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('study data differ from registered sources or identities')
    source_anchors = anchors(config)
    for row in rows:
        original = source_anchors[row['anchor_id']]['record']
        old_scratch = 'buffer' if row['lexical_realization']==0 else 'temp'
        if (row['expected_answer'] != original['expected_answer']
                or canonical_final(row['source'],row['scratch_name']) != canonical_final(original['source'],old_scratch)):
            raise ValueError('semantic source form changed final canonical state or answer')
        old_literals = sorted(n.value for n in ast.walk(ast.parse(original['source'])) if isinstance(n,ast.Constant))
        new_literals = sorted(n.value for n in ast.walk(ast.parse(row['source'])) if isinstance(n,ast.Constant))
        if old_literals != new_literals or len(ast.parse(row['source']).body) != len(ast.parse(original['source']).body):
            raise ValueError('semantic control changed literal exposure or statement count')
    if independent:
        for first in range(0,len(rows),128):
            part=rows[first:first+128]
            for row,oracle in zip(part,python_oracle([r['source'] for r in part])):
                truth=execute(row['source'])
                if (row['expected_answer']!=oracle['answer']
                        or [point['values'] for point in truth['execution_trace']]!=oracle['trace']):
                    raise ValueError('independent study oracle or full trace disagrees')
    return pairs_for(config,rows)


def build(config):
    rows=make_rows(config);pairs=validate(config,rows,independent=True)
    path=Path(config['dataset'])
    immutable(path,''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows).encode())
    result=dict(sha256=sha(path),generation_config_hash=digest(config['generation']),rows=len(rows),directed_pairs=len(pairs),
                independent_oracle_passed=True,role=config['assay']+'_discovery',generated_holdouts_opened=False)
    immutable(path.with_suffix('.manifest.json'),(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return result


def prompt(tokenizer, row, config):
    from .calibration import printed_source
    from .model_adapter import normalize_prompt
    if config['assay']=='query_timing':
        assignments,target=row['source'].rsplit('\n',1)
        before,after=(target,'not_set') if row['source_form']=='early' else ('not_set',target)
        content=(TIMING_INSTRUCTIONS[row['instruction']]+' A Target of not_set supplies no query at that point.\n\n'
                 +'Target: '+before+'\n\n```python\n'+assignments+'\n```\n\nTarget: '+after+'\n\nNow give the requested value.')
        if row.get('common_final_query'):
            content += '\n\nFinal target: '+target+'. Give its final value.'
        body=assignments
    else:
        body=printed_source(row['source'])
        content=COPY_INSTRUCTIONS[row['instruction']]+'\n\n```python\n'+body+'\n```'
    text=tokenizer.apply_chat_template([dict(role='user',content=content),dict(role='assistant',content='Output:\n')],
        tokenize=False,continue_final_message=True)+config['answer_prefix_suffix']
    return normalize_prompt(tokenizer,text),body


def layout(tokenizer,row,config):
    text,body=prompt(tokenizer,row,config)
    encoded=tokenizer(text,add_special_tokens=False,return_offsets_mapping=True)
    start,lines=text.index(body),body.splitlines(keepends=True)
    indices=([len(lines)-2,len(lines)-1,0] if config['assay']=='query_timing' else [4,5,0])
    positions=[]
    for line_index in indices:
        end=start+sum(map(len,lines[:line_index]))+len(lines[line_index].rstrip('\n'))
        matches=[i for i,(a,b) in enumerate(encoded['offset_mapping']) if a<end==b]
        if len(matches)!=1:raise ValueError('study position crosses a statement boundary')
        positions.append(matches[0])
    positions.append(len(encoded['input_ids'])-1)
    return dict(record=row,prompt=text,input_token_ids=encoded['input_ids'],positions=positions)


def validate_layouts(config,cases,pairs):
    if config['assay']=='query_timing':
        groups=defaultdict(dict)
        for case in cases.values():
            row=case['record'];groups[row['anchor_id'],row['instruction']][row['source_form']]=case
        for forms in groups.values():
            if set(forms)!={'early','late'}:raise ValueError('query timing pair incomplete')
            a,b=forms['early'],forms['late']
            if (len(a['input_token_ids'])!=len(b['input_token_ids']) or a['positions']!=b['positions']
                    or Counter(a['input_token_ids'])!=Counter(b['input_token_ids'])):
                raise ValueError('early/late cue must preserve token multiset, length and measurement positions')
    else:
        for pair in pairs:
            a,b=[cases[pair[key]] for key in ('recipient','donor')]
            if len(a['input_token_ids'])!=len(b['input_token_ids']) or a['positions']!=b['positions']:
                raise ValueError('semantic copy pairs must preserve token length and capture positions')
            if pair['transformation']=='reordered' and Counter(a['input_token_ids'])!=Counter(b['input_token_ids']):
                raise ValueError('independent reordering changed token exposure')


def prepare(config):
    from transformers import AutoTokenizer
    from .model_adapter import configure_tokenizer
    if sha(config['hook_proof'])!=config['hook_proof_sha256']:
        raise ValueError('hook proof changed')
    rows=read_jsonl(config['dataset']);pairs=validate(config,rows)
    tokenizer=AutoTokenizer.from_pretrained(config['model'],revision=config['tokenizer_revision'],local_files_only=True)
    configure_tokenizer(tokenizer,config)
    cases={r['id']:layout(tokenizer,r,config) for r in rows}
    validate_layouts(config,cases,pairs)
    if len(cases)%config['batch_size'] or len(pairs)%config['batch_size']:
        raise ValueError('study requires complete equal-size batches')
    source_anchors=anchors(config)
    if config['assay']=='copy_path':
        for c in cases.values():
            r=c['record']
            if r['instruction']==0 and r['source_form']=='anchor' and c['input_token_ids']!=source_anchors[r['anchor_id']]['input_token_ids']:
                raise ValueError('original copy anchor interface changed')
    answer_ids={}
    for value in range(10):
        ids=tokenizer(str(value),add_special_tokens=False)['input_ids']
        if len(ids)!=1:raise ValueError('one-token digit required')
        answer_ids[str(value)]=ids[0]
    payload=dict(cases=cases,pairs=pairs,answer_token_ids=answer_ids,padded_width=max(len(c['input_token_ids']) for c in cases.values()))
    immutable(config['prepared_cases'],(json.dumps(payload,sort_keys=True)+'\n').encode())
    result=dict(status='passed',config_hash=digest(config),source_sha256=code_identity()['source_sha256'],dataset_sha256=sha(config['dataset']),
                prepared_sha256=sha(config['prepared_cases']),cases=len(cases),directed_pairs=len(pairs),generated_holdouts_opened=False)
    write_json(config['preflight_result'],result);return result


def inputs(config,source_hash=None):
    qa=json.loads(Path(config['preflight_result']).read_text())
    if (qa['status']!='passed' or qa['config_hash']!=digest(config)
            or qa['source_sha256']!=(source_hash or code_identity()['source_sha256'])
            or qa['prepared_sha256']!=sha(config['prepared_cases']) or qa['dataset_sha256']!=sha(config['dataset'])):
        raise ValueError('matching frozen timing/copy tokenizer preflight required')
    data=json.loads(Path(config['prepared_cases']).read_text());rows=read_jsonl(config['dataset'])
    if data['pairs']!=validate(config,rows) or {r['id']:r for r in rows}!={k:c['record'] for k,c in data['cases'].items()}:
        raise ValueError('prepared timing/copy identities differ')
    validate_layouts(config,data['cases'],data['pairs'])
    if data['padded_width']!=max(len(c['input_token_ids']) for c in data['cases'].values()):raise ValueError('padding width differs')
    return qa,data


def run(config):
    from .value_transfer import run as engine
    return engine(config)


def audit(config):
    from .routing_extension import audit as checked_engine
    return checked_engine(config)


def paired_answer_patterns(cases, baselines):
    """Describe paired outputs without identifying an internal state or cause."""
    grouped=defaultdict(list)
    for key,c in cases.items():
        row=c['record']
        grouped[row['source'].rsplit('\n',1)[0],row['instruction'],row['source_form']].append((key,row))
    counts=Counter()
    for (body,instruction,form),rows in grouped.items():
        if len(rows)!=2 or {row['query'] for _,row in rows}!={0,1}:
            raise ValueError('paired-answer patterns require exactly both queries on one assignment body')
        rows=sorted(rows,key=lambda item:item[1]['query'])
        truth=tuple(row['expected_answer'] for _,row in rows)
        observed=tuple(baselines[key]['prediction'] for key,_ in rows)
        if len(set(truth))!=2:raise ValueError('pattern categories require distinct oracle query values')
        if any(value is None for value in observed):category='invalid'
        elif observed==truth:category='both_correct'
        elif observed==truth[::-1]:category='both_swapped'
        elif observed==(truth[0],truth[0]):category='duplicate_query0_value'
        elif observed==(truth[1],truth[1]):category='duplicate_query1_value'
        else:category='other'
        row=rows[0][1]
        counts[row['family'],instruction,form,row['mapping'],category]+=1
    return [dict(family=key[0],instruction=key[1],form=key[2],mapping=key[3],category=key[4],n=n)
            for key,n in sorted(counts.items())]


def patterns(config):
    root=Path(config['run_dir'])/'interventions'
    checked=json.loads((root/'audit.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
    if (checked['status']!='passed' or manifest['status']!='complete' or manifest['identity']['config']!=config
            or checked['identity_hash']!=manifest['identity_hash'] or checked['baseline_sha256']!=sha(root/'baselines.json')):
        raise ValueError('pinned complete baseline audit required')
    _,data=inputs(config,manifest['identity']['code']['source_sha256'])
    baselines=json.loads((root/'baselines.json').read_text())
    rows=paired_answer_patterns(data['cases'],baselines)
    result=dict(status='complete_descriptive',audit_sha256=sha(root/'audit.json'),analysis_source_sha256=code_identity()['source_sha256'],
                paired_query_groups=sum(r['n'] for r in rows),counts=rows,generated_holdouts_opened=False,
                interpretation='Post-hoc paired-output categories. Duplicating a value across two queries differs from swapping ownership. Neither output pattern identifies an internal stored state or its causal mechanism.')
    immutable(root/'paired_answer_patterns.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return {key:value for key,value in result.items() if key!='counts'}


def review(config):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from .value_transfer import conditions
    root=Path(config['run_dir'])/'interventions'
    checked=json.loads((root/'audit.json').read_text());manifest=json.loads((root/'manifest.json').read_text())
    if (checked['status']!='passed' or manifest['status']!='complete' or manifest['identity']['config']!=config
            or manifest['identity_hash']!=digest(manifest['identity']) or checked['identity_hash']!=manifest['identity_hash']
            or checked['baseline_sha256']!=sha(root/'baselines.json') or checked['vector_bank_sha256']!=sha(root/'baseline_vectors.npz')):
        raise ValueError('complete pinned study audit required')
    _,data=inputs(config,manifest['identity']['code']['source_sha256'])
    baselines=json.loads((root/'baselines.json').read_text());cases=data['cases']
    timing=config['assay']=='query_timing'
    lines=['# '+config['report_title'],'',
        f"Audited {checked['baseline_cases']:,} complete baseline responses ({checked['baseline_correct']} correct), with "
        f"{checked['intervention_forwards']:,} intervention forwards. All three instruction variants, two lexical realizations and all registered cases remain included. "
        'These are discovery data; final/extrapolation outcomes remain sealed.', '']
    groups=defaultdict(dict)
    for key,case in cases.items():
        r=case['record'];groups[r['anchor_id'],r['instruction']][r['source_form']]=key
    baseline_cells=[]
    forms=('early','late') if timing else ('anchor','reordered','renamed')
    for instruction in range(3):
        for family in sorted({c['record']['family'] for c in cases.values()}):
            for mapping in (0,1):
                for query in (0,1):
                    for form in forms:
                        selected=[baselines[k] for k,c in cases.items() if c['record']['instruction']==instruction and c['record']['family']==family
                                  and c['record']['mapping']==mapping and c['record']['query']==query and c['record']['source_form']==form]
                        baseline_cells.append(dict(instruction=instruction,family=family,mapping=mapping,query=query,form=form,
                            n=len(selected),correct=sum(b['correct'] for b in selected),invalid=sum(b['prediction'] is None for b in selected)))
    lines += ['| Instruction | Family | Mapping | Query | Form | Correct / n | Invalid |','|---:|---|---:|---:|---|---:|---:|']
    for c in baseline_cells:
        lines.append(f"| {c['instruction']} | {c['family']} | {c['mapping']} | {c['query']} | {c['form']} | {c['correct']}/{c['n']} | {c['invalid']} |")
    pair_changes=[]
    for instruction in range(3):
        for family in sorted({c['record']['family'] for c in cases.values()}):
            for mapping in (0,1):
                for query in (0,1):
                    for alternate in (('early',) if timing else ('reordered','renamed')):
                        chosen=[]
                        for (anchor,inst),form_keys in groups.items():
                            a,b=(form_keys['late'],form_keys['early']) if timing else (form_keys['anchor'],form_keys[alternate])
                            r=cases[a]['record']
                            if (inst,r['family'],r['mapping'],r['query'])==(instruction,family,mapping,query):
                                chosen.append((baselines[a],baselines[b]))
                        pair_changes.append(dict(instruction=instruction,family=family,mapping=mapping,query=query,alternate=alternate,n=len(chosen),
                            both_correct=sum(a['correct'] and b['correct'] for a,b in chosen),
                            reference_only_correct=sum(a['correct'] and not b['correct'] for a,b in chosen),
                            alternate_only_correct=sum(not a['correct'] and b['correct'] for a,b in chosen),
                            both_wrong=sum(not a['correct'] and not b['correct'] for a,b in chosen)))
    lines += ['', 'Paired changes use late-query prompts as the timing reference, and original programs as the copy-study reference.', '',
        '| Instruction | Family | Mapping | Query | Alternate | n | Both correct | Reference only | Alternate only | Both wrong |',
        '|---:|---|---:|---:|---|---:|---:|---:|---:|---:|']
    for c in pair_changes:
        lines.append('| '+' | '.join(str(c[k]) for k in ('instruction','family','mapping','query','alternate','n','both_correct','reference_only_correct','alternate_only_correct','both_wrong'))+' |')
    sensitivity=[];details=[];control_result=dict(status='not_requested')
    if timing:
        with np.load(root/'baseline_vectors.npz',allow_pickle=False) as cache:
            bank=cache['vectors'];ids=cache['case_ids'].tolist()
        index={key:i for i,key in enumerate(ids)}
        query_groups=defaultdict(dict)
        for key,c in cases.items():
            r=c['record'];body=r['source'].rsplit('\n',1)[0]
            query_groups[body,r['instruction'],r['source_form']][r['query']]=key
        grouped_distances=defaultdict(list)
        for (body,instruction,form),query_keys in query_groups.items():
            if set(query_keys)!={0,1}:raise ValueError('timing capture must retain both queries on every assignment prefix')
            a,b=[cases[query_keys[q]] for q in (0,1)]
            if form=='late' and (a['input_token_ids'][:a['positions'][1]+1]!=b['input_token_ids'][:b['positions'][1]+1]
                                or a['positions'][:3]!=b['positions'][:3]):
                raise ValueError('late query leaked into the assignment prefix')
            delta=bank[index[query_keys[0]]]-bank[index[query_keys[1]]]
            if form=='late' and np.any(delta[:,:3]!=0):raise ValueError('late-query causal-prefix invariance failed')
            distances=np.linalg.norm(delta,axis=-1)
            for l,layer in enumerate(config['layers']):
                for site,name in enumerate(('copy_end','state_end','initial_literal','answer_prefill')):
                    grouped_distances[instruction,form,layer,name].append(float(distances[l,site]))
        for (instruction,form,layer,site),values in sorted(grouped_distances.items()):
            sensitivity.append(dict(instruction=instruction,form=form,layer=layer,site=site,n=len(values),
                exactly_equal=sum(v==0 for v in values),mean_l2=sum(values)/len(values),max_l2=max(values)))
        lines += ['', 'Late-query paired prefixes and all three earlier capture sites are exactly invariant across the two future queries. '
            'Early-query representations may differ because the target is already in the context. '
            'That difference is not evidence of a particular memory algorithm. No hidden-state interventions or probe fitting were requested in this timing/capture phase.', '',
            '| Instruction | Timing | Block | Site | Paired states | Exact equals | Mean L2 |', '|---:|---|---:|---|---:|---:|---:|']
        for c in sensitivity:
            if c['site'] in ('state_end','answer_prefill'):
                lines.append(f"| {c['instruction']} | {c['form']} | {c['layer']} | {c['site']} | {c['n']} | {c['exactly_equal']} | {c['mean_l2']:.4f} |")
        fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained')
        for i,family in enumerate(('ownership','versions')):
            for q in (0,1):
                ax=axes[i,q]
                for j,form in enumerate(forms):
                    rates=[]
                    for instruction in range(3):
                        cell=[c for c in baseline_cells if c['instruction']==instruction and c['family']==family and c['query']==q and c['form']==form]
                        rates.append(100*sum(c['correct'] for c in cell)/sum(c['n'] for c in cell))
                    ax.bar(np.arange(3)+(j-.5)*.32,rates,width=.32,label=form)
                ax.set_title(f'{family}, query {q} (both mappings)');ax.set_xticks(range(3),['Instruction 0','Instruction 1','Instruction 2']);ax.set_ylim(0,105);ax.set_ylabel('Complete-answer accuracy (%)');ax.legend()
        fig.suptitle('Same assignments and token multiset; target revealed early or late')
        fig.savefig(config['figure']);fig.savefig(Path(config['figure']).with_suffix('.png'),dpi=150);plt.close(fig)
    else:
        replays=json.loads((root/'replays.json').read_text());pair_lookup={p['id']:p for p in data['pairs']}
        collected=[];positive=negative=shams=0;max_error=0.
        for path,checksum in checked['chunk_checksums'].items():
            if sha(path)!=checksum:raise ValueError('copy intervention chunk changed')
            for row in json.loads(Path(path).read_text()):
                pair=pair_lookup[row['pair_id']];collected.append((pair,row))
                if row['layer']==31 and row['condition']=='answer_vector':
                    if row['first_token']!=baselines[pair['donor']]['first_token']:raise ValueError('answer-copy positive control failed')
                    positive+=1
                elif row['condition']=='identity_sham' or row['layer']==31:
                    if row['first_token']!=replays[pair['id']]['first_token']:raise ValueError('analytic zero-effect control changed answer')
                    if row['condition']=='identity_sham':shams+=1
                    else:negative+=1
                if row['condition']=='unrelated_position' or row['condition'].startswith('random_'):
                    target=row['target_effective_norm'];error=abs(row['actual_effective_norm']-target)
                    max_error=max(max_error,error/target if target else error)
        n_pairs=len(data['pairs'])
        if (positive,negative,shams)!=(n_pairs,5*n_pairs,len(config['layers'])*n_pairs):raise ValueError('analytic copy-control coverage incomplete')
        control_result=dict(status='passed',answer_vector_donor_matches=positive,final_earlier_token_unchanged=negative,
                            identity_shams_unchanged=shams,max_relative_norm_error=max_error)
        grouped=defaultdict(list)
        for p,r in collected:
            grouped[p['transformation'],p['instruction'],p['mapping'],p['query'],p['reverse'],r['layer'],r['condition']].append((p,r))
        for (transformation,instruction,mapping,query,reverse,layer,condition),rows in sorted(grouped.items()):
            n=len(rows);before=sum(replays[p['id']]['first_token']==r['target_token'] for p,r in rows)/n
            after=sum(r['first_token']==r['target_token'] for p,r in rows)/n
            change=sum(r['target_logprob']-r['original_logprob']-(replays[p['id']]['digit_logprobs'][p['replacement']-1]-replays[p['id']]['digit_logprobs'][p['baseline_answer']-1]) for p,r in rows)/n
            details.append(dict(transformation=transformation,instruction=instruction,mapping=mapping,query=query,reverse=reverse,
                layer=layer,condition=condition,n=n,unpatched_correct_rate=before,patched_correct_rate=after,logodds_change=change))
        lines += ['', 'The primary intervention is at the end of the earlier assignment that restores the second variable from the temporary. '
            'Source forms preserve the complete canonical final state, literal exposure and measurement positions. '
            'No correct/error cases are selected; complete instruction-specific mapping/query controls and all seven conditions are in the JSON artifact. '
            'The table below shows the previously nominated swapped second-variable cell, with both donor directions.', '',
            '| Form | Instruction | Donor → recipient | Block | n | Unpatched (%) | Primary (%) | Unrelated (%) | Random range (%) |',
            '|---|---:|---|---:|---:|---:|---:|---:|---:|']
        lookup={(r['transformation'],r['instruction'],r['reverse'],r['layer'],r['condition']):r for r in details if r['mapping']==1 and r['query']==1}
        for form in ('reordered','renamed'):
            for instruction in range(3):
                for reverse in (False,True):
                    for layer in config['layers']:
                        main=lookup[form,instruction,reverse,layer,config['primary_condition']]
                        unrelated=lookup[form,instruction,reverse,layer,'unrelated_position']
                        noise=[100*lookup[form,instruction,reverse,layer,'random_'+str(seed)]['patched_correct_rate'] for seed in (11,29,47)]
                        direction='anchor → alternate' if reverse else 'alternate → anchor'
                        lines.append(f"| {form} | {instruction} | {direction} | {layer} | {main['n']} | {100*main['unpatched_correct_rate']:.2f} | {100*main['patched_correct_rate']:.2f} | {100*unrelated['patched_correct_rate']:.2f} | {min(noise):.2f}–{max(noise):.2f} |")
        fig,axes=plt.subplots(2,2,figsize=(12,7),layout='constrained')
        for i,form in enumerate(('reordered','renamed')):
            for j,reverse in enumerate((False,True)):
                ax=axes[i,j];values=[]
                for layer in config['layers']:
                    values.append([100*sum(lookup[form,instruction,reverse,layer,condition]['patched_correct_rate'] for instruction in range(3))/3 for condition in conditions(config)])
                values=np.array(values);ax.imshow(values,vmin=0,vmax=100,cmap='viridis',aspect='auto')
                ax.set_title(form+(': anchor → alternate' if reverse else ': alternate → anchor'))
                ax.set_xticks(range(7),['Copy','Unrelated','Answer','Sham','Random 11','Random 29','Random 47'],rotation=35,ha='right');ax.set_yticks(range(len(config['layers'])),config['layers']);ax.set_ylabel('Raw block')
                for x in range(len(config['layers'])):
                    for y in range(7):ax.text(y,x,f'{values[x,y]:.1f}',ha='center',va='center',color='black' if values[x,y]>55 else 'white',fontsize=9)
        fig.suptitle('Swapped second-variable token accuracy (%), all three instructions')
        fig.savefig(config['figure']);fig.savefig(Path(config['figure']).with_suffix('.png'),dpi=150);plt.close(fig)
        lines += ['',f'Analytic controls passed: {positive} donor answer copies, {negative} final-block earlier-token controls and {shams} identity shams. '
            f'Maximum relative effective-norm mismatch: {100*max_error:.4f}% (allowed 3%). '
            'Answer-vector transfers are software controls for copying an answer, not binding-mechanism evidence.']
    lines += ['', '![Registered study results]('+Path(config['figure']).name+')', '',
        'Instruction, numeric and lexical variants are not independent structural replications. Paired counts are descriptive; no confirmatory significance or best-layer claim is made. '
        'Query timing can alter attention or task strategy. A successful local patch does not establish natural causal use, a general binding register or a validated explanation-transfer method. '
        'No optional language-model training, unlearning or separate-paper project was started.', '',
        f"Audit: `{root/'audit.json'}`. [Design](timing_and_copy_plan.md). Reproduce with "
        f"`PYTHONPATH=src ../envs/probe-cu129/bin/python scripts/113_binding_timing_and_copy.py review {config['config_path']}`."]
    immutable(config['report'],('\n'.join(lines)+'\n').encode())
    result=dict(status='complete_audited',assay=config['assay'],audit=str(root/'audit.json'),audit_sha256=sha(root/'audit.json'),report=config['report'],
        baseline_cases=checked['baseline_cases'],baseline_correct=checked['baseline_correct'],intervention_forwards=checked['intervention_forwards'],
        baseline_cells=baseline_cells,paired_changes=pair_changes,query_sensitivity=sensitivity,intervention_cells=details,analytic_controls=control_result,
        generated_holdouts_opened=False)
    immutable(config['review_artifact'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return {k:v for k,v in result.items() if k not in ('baseline_cells','paired_changes','query_sensitivity','intervention_cells')}
