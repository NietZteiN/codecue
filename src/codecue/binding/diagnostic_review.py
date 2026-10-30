"""Post-hoc, descriptive audits of already consumed diagnostic programs."""
from __future__ import annotations

import copy
import hashlib
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from .calibration import VARIANTS,parse_completion
from .datasets import digest,read_jsonl,write_json,diagnostics
from .interpreter import execute,python_oracle
from .program_diagnostics import build,validate_rows,without_trailing_distractor


def paired_counts(left,right):
    if not left or set(left)!=set(right):raise ValueError('paired comparison requires complete matching groups')
    if any(left[key]['expected_answer']!=right[key]['expected_answer'] for key in left):
        raise ValueError('paired programs have different expected answers')
    categories={name:[] for name in ('both_correct','left_only_correct','right_only_correct','neither_correct')}
    for key in sorted(left):
        a,b=bool(left[key]['correct']),bool(right[key]['correct'])
        name='both_correct' if a and b else 'left_only_correct' if a else 'right_only_correct' if b else 'neither_correct'
        categories[name].append(key)
    return dict(n=len(left),counts={name:len(keys) for name,keys in categories.items()},ids=categories,
                left_invalid=sum(r['prediction'] is None for r in left.values()),
                right_invalid=sum(r['prediction'] is None for r in right.values()),
                accuracy_difference_left_minus_right=(len(categories['left_only_correct'])-len(categories['right_only_correct']))/len(left))


def distractor_overlap(rows):
    counts=defaultdict(lambda:{'without':0,'with':0})
    for row in rows:
        key=abs(row['expected_answer'])
        counts[key]['with' if row['query_followed_by_distractor'] else 'without']+=1
    table=[dict(absolute_answer=magnitude,**values) for magnitude,values in sorted(counts.items())]
    no_overlap=[r['absolute_answer'] for r in table if not r['with'] or not r['without']]
    return dict(table=table,magnitudes_without_both_levels=no_overlap,
                confounded=bool(no_overlap),
                interpretation='Input-design audit using oracle answer magnitude. No isolated distractor effect is estimable where a magnitude has only one distractor level.')


def load_records(directory):
    root=Path(directory);manifest_path=root/'manifest.json';response_path=root/'responses.jsonl'
    manifest=json.loads(manifest_path.read_text());identity=manifest['identity'];config=identity['config']
    if manifest['identity_hash']!=digest(identity) or manifest['status']!='complete':
        raise ValueError('diagnostic review requires a complete verified run')
    decision_path=root/'diagnostic_decision.json'
    decision=json.loads(decision_path.read_text())
    if (not decision['complete'] or decision['identity_hash']!=manifest['identity_hash']
            or hashlib.sha256(response_path.read_bytes()).hexdigest()!=decision['responses_sha256']):
        raise ValueError('diagnostic review responses differ from the immutable decision')
    dataset=Path(config['dataset'])
    if hashlib.sha256(dataset.read_bytes()).hexdigest()!=identity['dataset_manifest']['sha256']:
        raise ValueError('diagnostic review dataset changed')
    rows=validate_rows(read_jsonl(dataset),config['diagnostic_kind']);gold={r['id']:r for r in rows}
    variants=config['calibration']['variants'];expected={(r['id'],v) for r in rows for v in variants}
    records=read_jsonl(response_path);seen=set()
    for row in records:
        key=(row['id'],row['variant'])
        if key not in expected or key in seen:raise ValueError('review responses are duplicate or unexpected')
        seen.add(key);original=gold[row['id']]
        prediction=parse_completion(row['raw_response'],VARIANTS[row['variant']]['answer_mode'])
        if (any(row[k]!=value for k,value in original.items()) or row['prediction']!=prediction
                or row['correct']!=(prediction==original['expected_answer']) or row['invalid']!=(prediction is None)):
            raise ValueError('review response score or program metadata changed')
    if seen!=expected or manifest['samples_completed']!=len(records) or manifest['samples_planned']!=len(records):
        raise ValueError('review response cohort incomplete')
    contract={k:config[k] for k in ('model','model_revision','tokenizer_revision','dtype','tokenization_mode')}
    inputs={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in (manifest_path,response_path,decision_path,dataset)}
    return records,rows,contract,inputs


def summarize(records_by_kind,rows_by_kind):
    protocols=[];form_pairs=[]
    for kind,records in records_by_kind.items():
        groups=defaultdict(list)
        for row in records:groups[(row['split'],row['family'],row.get('depth'))].append(row)
        for (split,family,depth),group in sorted(groups.items()):
            left={r['id']:r for r in group if r['variant']=='print_direct_v3'}
            right={r['id']:r for r in group if r['variant']=='print_trace_long_v1'}
            protocols.append(dict(diagnostic_kind=kind,split=split,family=family,depth=depth,
                                  left='print_direct_v3',right='print_trace_long_v1',**paired_counts(left,right)))
    arithmetic=records_by_kind['arithmetic_forms']
    forms=('expression','assignment','independent','dependent')
    for variant in ('print_direct_v3','print_trace_long_v1'):
        for split in ('train','development'):
            subset=[r for r in arithmetic if r['variant']==variant and r['split']==split]
            for left_form,right_form in combinations(forms,2):
                left={r['paired_group_id']:r for r in subset if r['family']==left_form}
                right={r['paired_group_id']:r for r in subset if r['family']==right_form}
                form_pairs.append(dict(variant=variant,split=split,left=left_form,right=right_form,**paired_counts(left,right)))
    binding=records_by_kind['arithmetic_free'];strata=defaultdict(list)
    for row in binding:
        key=(row['variant'],row['split'],row['family'],row['depth'],row['available_bindings'],
             row['answer_sign'],abs(row['expected_answer']),row['query_followed_by_distractor'])
        strata[key].append(row)
    fields=('variant','split','family','depth','available_bindings','answer_sign','absolute_answer','trailing_distractor')
    stratified=[dict(zip(fields,key),n=len(group),correct=sum(r['correct'] for r in group),
                     invalid=sum(r['invalid'] for r in group)) for key,group in sorted(strata.items())]
    return dict(status='complete',analysis_role='posthoc_descriptive_diagnostic_review',protocol_pairs=protocols,
                arithmetic_form_pairs=form_pairs,binding_strata=stratified,
                distractor_design=distractor_overlap(rows_by_kind['arithmetic_free']),
                features_not_eligible_for_forecasts=True,heldout_outcomes_opened=False,
                interpretation='Exact within-cohort counts only. No population intervals, significance tests, mechanism selection or changes to the completed gate. Protocol comparisons jointly change readout and generation budget. Copy and overwrite families are not matched numerical twins.')


def review(config):
    from .registry import code_identity
    output=Path(config['output'])
    if output.exists():raise ValueError('diagnostic review is immutable')
    records={};rows={};inputs={};reference=None
    for kind,directory in config['runs'].items():
        records[kind],rows[kind],contract,files=load_records(directory)
        if reference is None:reference=contract
        elif contract!=reference:raise ValueError('diagnostic review inference contracts differ')
        inputs.update(files)
    result=summarize(records,rows)
    result.update(inputs=inputs,analysis_code=code_identity(),config_hash=digest(config))
    write_json(output,result)
    target=Path(config['report']);target.parent.mkdir(parents=True,exist_ok=True)
    text=['# Review of consumed diagnostic results','',result['interpretation'],'',
          'This analysis uses completed training and numeric-validation outcomes. It is exploratory and does not reopen the fixed gate or final model outcomes.', '',
          '## Distractor-design audit','',
          '| Absolute oracle answer | Without trailing distractor | With trailing distractor |','|---:|---:|---:|']
    text += [f"| {r['absolute_answer']} | {r['without']} | {r['with']} |" for r in result['distractor_design']['table']]
    text += ['', 'The original generator tied trailing distractors to replicate parity. For nonzero answers, parity also determined target magnitude. '
             'The completed accuracies and selection decisions remain valid descriptions of their stated mixtures; '
             'differences between distractor strata cannot isolate an irrelevant-statement effect.', '',
             '## Paired readouts on identical programs','',
             '| Task | Split | Family | Depth | n | Both correct | Direct only correct | Trace only correct | Neither correct |',
             '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for row in result['protocol_pairs']:
        c=row['counts']
        text.append(f"| {row['diagnostic_kind']} | {row['split']} | {row['family']} | {row['depth'] or '—'} | {row['n']} | "
                    f"{c['both_correct']} | {c['left_only_correct']} | {c['right_only_correct']} | {c['neither_correct']} |")
    text += ['', '## Matched arithmetic-form comparisons','',
             'Each row compares exactly the same numeric groups and expected answers. The independent form substitutes an executed intermediate as a literal, '
             'so the comparison changes literal cues and functional dependencies. These are descriptive contrasts, not a pure binding intervention.', '',
             '| Protocol | Split | Left form | Right form | n | Left only correct | Right only correct |',
             '|---|---|---|---|---:|---:|---:|']
    for row in result['arithmetic_form_pairs']:
        text.append(f"| {row['variant']} | {row['split']} | {row['left']} | {row['right']} | {row['n']} | "
                    f"{row['counts']['left_only_correct']} | {row['counts']['right_only_correct']} |")
    text += ['', 'Full case IDs, invalid counts and binding strata are retained in the review artifact. Oracle answer magnitude is used only '
             'for this design audit and is not an eligible forecast feature. A fresh counterbalanced dataset is prepared separately without model inference.', '']
    target.write_text('\n'.join(text))
    return {'report':str(target),'confounded':result['distractor_design']['confounded']}


def build_counterbalanced(config):
    output=Path(config['output'])
    if output.exists() or output.with_suffix('.manifest.json').exists():raise ValueError('counterbalanced dataset is immutable')
    base_config=config['base'];base_path=Path(base_config['dataset'])
    if not base_config.get('unique_distractor_prefixes') or not base_config.get('exclude_datasets'):
        raise ValueError('fresh follow-up requires explicit exclusions and unique assignment prefixes')
    if not base_path.exists():build(base_config)
    manifest=json.loads(base_path.with_suffix('.manifest.json').read_text())
    if manifest['seed']!=base_config['seed'] or hashlib.sha256(base_path.read_bytes()).hexdigest()!=manifest['sha256']:
        raise ValueError('counterbalanced base provenance changed')
    base=validate_rows(read_jsonl(base_path),'arithmetic_free')
    exclusions=set();input_hashes={}
    for file in base_config['exclude_datasets']:
        path=Path(file)
        input_hashes[file]=hashlib.sha256(path.read_bytes()).hexdigest()
        exclusions.update(without_trailing_distractor(r['source']) for r in read_jsonl(path))
    rows=[];prefixes=set()
    for original in base:
        prefix=without_trailing_distractor(original['source'])
        if prefix in exclusions or prefix in prefixes:raise ValueError('counterbalanced prefix was previously consumed or duplicated')
        prefixes.add(prefix);group='counterbalanced:'+digest(prefix)[:24]
        for trailing in (False,True):
            lines=prefix.splitlines()
            if trailing:lines.insert(-1,f"distractor = v{original['available_bindings']-1}")
            source='\n'.join(lines);truth=execute(source)
            if truth['expected_answer']!=original['expected_answer']:raise ValueError('irrelevant assignment changes output')
            row=copy.deepcopy(original)
            row.update(id='counterbalanced:'+digest(source)[:24],source=source,oracle_source=source,
                       evaluation_role='counterbalanced_followup_only',paired_group_id=group,
                       source_base_id=original['id'],query_followed_by_distractor=trailing,
                       execution_trace=truth['execution_trace'],diagnostic_counterfactuals=diagnostics(source,truth))
            rows.append(row)
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('duplicate counterbalanced rendering')
    for first in range(0,len(rows),128):
        batch=rows[first:first+128];oracle=python_oracle([r['source'] for r in batch])
        if any(r['expected_answer']!=o['answer'] or [p['values'] for p in r['execution_trace']]!=o['trace'] for r,o in zip(batch,oracle)):
            raise ValueError('counterbalanced Python mismatch')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows))
    result=dict(status='validated',rows=len(rows),paired_programs=len(base),seed=base_config['seed'],
                evaluation_role='counterbalanced_followup_only',sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                independent_python_programs=len(rows),base_sha256=manifest['sha256'],excluded_datasets=input_hashes,
                model_inference_performed=False,heldout_outcomes_opened=False,
                interpretation='Fresh numeric paired calibration candidates. Repeated structures; no confirmatory or model-performance claim. Adding an irrelevant assignment changes length and context as well as position.')
    write_json(output.with_suffix('.manifest.json'),result)
    return result
