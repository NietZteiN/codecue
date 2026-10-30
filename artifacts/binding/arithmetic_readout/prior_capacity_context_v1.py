#!/usr/bin/env python
"""Reproduce audited prior arithmetic-form cells without model/tokenizer loads.

This is a post-hoc context analysis of the already completed capacity study,
not a new arithmetic experiment or a causal two-versus-three-operation test.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import json
from itertools import zip_longest
from pathlib import Path
import sys


ROOT=Path(__file__).absolute().parents[3]
sys.path.insert(0,str(ROOT/'src'))

from codecue.binding.calibration import VARIANTS, parse_completion
from codecue.binding.datasets import digest
from codecue.binding.program_diagnostics import validate_rows
from codecue.binding.published_benchmarks import immutable, sha


PROTOCOLS=('print_direct_v3','print_trace_long_v1')
MODEL_CONFIGS={name:ROOT/'configs/binding/capacity'/f'{name}_v1.json'
               for name in ('llama31_8b','codellama34b')}
EXPECTED_COUNTS={'llama31_8b':{'print_direct_v3':163,'print_trace_long_v1':176},
                 'codellama34b':{'print_direct_v3':57,'print_trace_long_v1':148}}
OUTPUT=ROOT/'artifacts/binding/arithmetic_readout/prior_capacity_context_review_v1.json'
REPORT=ROOT/'reports/binding/arithmetic_readout_prior_context.md'
LIMITATION=(
    'Post-hoc description of previously consumed training/numeric-development data. '
    'These values, signs, forms, operand range and data-generation rules differ '
    'from the new arithmetic/readout bank. This comparison cannot isolate an '
    'effect of two versus three operations or establish a causal mechanism. '
    'Trace prompting also changes computation and generation allowance. '
    'Historical gates are unchanged; no original final/extrapolation outcomes '
    'or new model responses are used.'
)


def resolve(path):
    path=Path(path)
    return path if path.is_absolute() else ROOT/path


def metadata(config_path):
    """Check the old run and cohort's declared access roles before responses."""
    config=json.loads(config_path.read_text());folder=resolve(config['run_dir'])/'checkpoint_suite'
    manifest_path=folder/'manifest.json';audit_path=folder/'audit.json';summary_path=folder/'summary.json'
    manifest=json.loads(manifest_path.read_text());audit=json.loads(audit_path.read_text())
    summary=json.loads(summary_path.read_text());identity=manifest['identity']
    if (manifest['status']!='complete' or digest(identity)!=manifest['identity_hash']
            or identity['config']!=config or identity['config_hash']!=digest(config)
            or audit['status']!='passed' or not audit['complete']
            or audit['identity_hash']!=manifest['identity_hash'] or not summary['complete']
            or audit.get('generated_holdouts_opened') is not False
            or summary.get('generated_holdouts_opened') is not False
            or audit['model']!=config['model'] or audit['revision']!=config['model_revision']):
        raise ValueError('Prior context requires matching complete audited capacity metadata')
    sections=[section for section in config['sections'] if section['name']=='arithmetic_forms']
    if (len(sections)!=1 or sections[0]['kind']!='diagnostic'
            or sections[0]['diagnostic_kind']!='arithmetic_forms' or tuple(sections[0]['variants'])!=PROTOCOLS):
        raise ValueError('Expected the registered arithmetic_forms section and both existing protocols')
    section=sections[0];dataset=resolve(section['dataset']);dataset_manifest_path=dataset.with_suffix('.manifest.json')
    dataset_manifest=json.loads(dataset_manifest_path.read_text())
    if (dataset_manifest['status']!='validated' or dataset_manifest['evaluation_role']!='phase2_diagnostics'
            or dataset_manifest['diagnostic_kind']!='arithmetic_forms'
            or set(dataset_manifest['split_counts'])!={'train','development'}
            or dataset_manifest['sha256']!=section['sha256'] or sha(dataset)!=section['sha256']):
        raise ValueError('Only the audited training/development arithmetic diagnostic bank is eligible')
    preflight_path=resolve(config['preflight_result']);preflight=json.loads(preflight_path.read_text())
    prepared=resolve(config['prepared_cases']);responses=folder/'responses.jsonl'
    if (preflight['status']!='passed' or preflight['config_hash']!=digest(config)
            or preflight['source_sha256']!=identity['code']['source_sha256']
            or preflight.get('generated_holdouts_opened') is not False
            or audit['preflight']!=preflight or sha(prepared)!=preflight['prepared_cases_sha256']
            or sha(responses)!=manifest['responses_sha256']
            or summary['responses_sha256']!=manifest['responses_sha256']):
        raise ValueError('Prepared-case or response hashes differ from the prior audited run')
    paths=(config_path,manifest_path,audit_path,summary_path,dataset,dataset_manifest_path,preflight_path,prepared,responses)
    inputs={str(path.relative_to(ROOT)):sha(path) for path in paths}
    return config,section,dataset,prepared,responses,audit,inputs


def _counts(rows):
    rows=list(rows);n=len(rows);correct=sum(row['score']['correct'] for row in rows)
    invalid=sum(not row['score']['valid'] for row in rows)
    return dict(n=n,correct=correct,invalid=invalid,accuracy=correct/n if n else None,
                unique_source_n=len({row['record']['source'] for row in rows}))


def collect(name,config_path):
    config,section,dataset,prepared,responses,audit,inputs=metadata(config_path)
    rows=[]
    with dataset.open() as stream:
        for line in stream:
            row=json.loads(line)
            if row['split'] not in ('train','development') or row['evaluation_role']!='phase2_diagnostics':
                raise ValueError('Ineligible outcome access role in arithmetic diagnostic dataset')
            rows.append(row)
    validate_rows(rows,'arithmetic_forms');gold={row['id']:row for row in rows}
    expected={(identity,protocol) for identity in gold for protocol in PROTOCOLS};seen=set();observed=[];scanned=0
    with prepared.open() as cases, responses.open() as outputs:
        for case_line,response_line in zip_longest(cases,outputs):
            if case_line is None or response_line is None:raise ValueError('Prior suite case/response coverage differs')
            scanned+=1;case=json.loads(case_line)
            if case['section']!='arithmetic_forms':continue
            row=case['record'];variant=case['variant']
            # Check the eligible role and immutable case before opening its
            # model response. Other sections' response JSON is never parsed.
            if (case['kind']!='diagnostic' or row['split'] not in ('train','development')
                    or row['evaluation_role']!='phase2_diagnostics' or variant not in PROTOCOLS
                    or row['id'] not in gold or row!=gold[row['id']]):
                raise ValueError('Prepared arithmetic case differs from its eligible diagnostic cohort')
            key=(row['id'],variant)
            if key not in expected or key in seen:raise ValueError('Duplicated or unexpected arithmetic case')
            seen.add(key);response=json.loads(response_line)
            if (any(response[field]!=case[field] for field in ('section','task','id','input_token_ids','prompt_sha256'))
                    or response['record_sha256']!=digest(row)
                    or case['prompt_sha256']!=digest(case['prompt'])
                    or case['max_new_tokens']!=VARIANTS[variant]['max_new_tokens']
                    or len(response['output_token_ids'])>case['max_new_tokens']):
                raise ValueError('Prior arithmetic response identity or token contract differs')
            prediction=parse_completion(response['raw_response'],VARIANTS[variant]['answer_mode'])
            score=dict(prediction=prediction,valid=prediction is not None,correct=prediction==row['expected_answer'])
            if response['score']!=score:raise ValueError('Prior arithmetic score differs from its registered parser')
            observed.append(dict(variant=variant,record=row,score=score))
    if seen!=expected or scanned!=audit['evaluated'] or scanned!=audit['planned']:
        raise ValueError('Prior arithmetic response or full-suite coverage differs')
    totals=[];cells=defaultdict(list)
    for variant in PROTOCOLS:
        total=dict(variant=variant,**_counts(row for row in observed if row['variant']==variant))
        prior=[cell for cell in audit['cells'] if cell['section']=='arithmetic_forms' and cell['task']==variant]
        if (len(prior)!=1 or total['n']!=192 or total['correct']!=EXPECTED_COUNTS[name][variant]
                or any(total[field]!=prior[0][field] for field in ('n','correct'))
                or total['n']-total['invalid']!=prior[0]['valid']):
            raise ValueError('Recomputed arithmetic totals differ from the original audited counts')
        totals.append(total)
    for row in observed:
        original=row['record'];sign=(original['expected_answer']>0)-(original['expected_answer']<0)
        if sign!=original['answer_sign']:raise ValueError('Prior arithmetic output-sign label differs')
        if original['operator'] not in ('+','-') or original['family'] not in ('expression','assignment','independent','dependent'):
            raise ValueError('Unexpected arithmetic form or operator')
        cells[row['variant'],original['family'],original['operator'],sign,original['split']].append(row)
    expected_cells={(protocol,form,operator,sign,split) for protocol in PROTOCOLS
                    for form in ('expression','assignment','independent','dependent')
                    for operator in ('+','-') for sign in (-1,0,1) for split in ('train','development')}
    if set(cells)!=expected_cells:raise ValueError('Prior arithmetic cell matrix is incomplete')
    result=dict(model=config['model'],revision=config['model_revision'],status='complete_audited',
        identity_hash=audit['identity_hash'],dataset=section['dataset'],dataset_sha256=section['sha256'],
        protocol_totals=totals,n=len(observed),numeric_groups=len({row['paired_group_id'] for row in rows}),
        cells=[dict(variant=key[0],form=key[1],operator=key[2],answer_sign=key[3],split=key[4],**_counts(values))
               for key,values in sorted(cells.items())],
        syntactic_operation_count_distribution=dict(Counter(sum(isinstance(node,ast.BinOp) for node in ast.walk(ast.parse(row['source']))) for row in rows)),
        inputs=inputs,original_totals_reproduced=True)
    return result


def main():
    models={name:collect(name,path) for name,path in MODEL_CONFIGS.items()}
    lines=['# Prior arithmetic capacity context','',LIMITATION,'',
        'This analysis reproduces the already completed two-operation arithmetic-form section. Its 192 distinct sources comprise four forms, two first-operator labels, three output signs and training/development splits. '
        'Every source has two syntactic binary operations. In the independent form the first computed assignment is dead for the final answer; the second expression substitutes an oracle intermediate literal. '
        'The operator column labels the first operation only. Signs here describe the expected output; the new study also stratifies intermediate signs.','',
        '| Checkpoint | Protocol | Correct / n | Invalid | Unique sources |','|---|---|---:|---:|---:|']
    for name,result in models.items():
        for total in result['protocol_totals']:
            lines.append(f"| {name} | {total['variant']} | {total['correct']}/{total['n']} | {total['invalid']} | {total['unique_source_n']} |")
    lines.extend(['','## Complete prior cells','',
        'Each cell contains four numeric cases. Exact source uniqueness does not make repeated structures independent replications. These are descriptive counts without hypothesis selection or inferential intervals.','',
        '| Checkpoint | Protocol | Form | First operator | Output sign | Split | Correct / n | Invalid | Unique sources |',
        '|---|---|---|---|---:|---|---:|---:|---:|'])
    for name,result in models.items():
        for cell in result['cells']:
            lines.append(f"| {name} | {cell['variant']} | {cell['form']} | {cell['operator']} | {cell['answer_sign']:+d} | {cell['split']} | {cell['correct']}/{cell['n']} | {cell['invalid']} | {cell['unique_source_n']} |")
    lines.extend(['','All original run manifests, tokenizer proofs, responses, source snapshots, scores and gates remain unchanged. '
        'The new study differs in numeric range, matched final answers, operation/storage forms, sign strata and grouping. Cross-bank accuracy differences therefore do not identify an operation-count effect.',''])
    immutable(REPORT,'\n'.join(lines).encode())
    result=dict(status='complete_audited',complete=True,analysis_role='posthoc_prior_capacity_context',
        models=models,n=sum(model['n'] for model in models.values()),report=str(REPORT.relative_to(ROOT)),report_sha256=sha(REPORT),
        analysis_source={'path':str(Path(__file__).absolute().relative_to(ROOT)),'source_sha256':sha(Path(__file__))},
        generated_holdouts_opened=False,model_or_tokenizer_loads=False,new_model_responses=0,
        unrelated_response_sections_parsed=False,limitation=LIMITATION)
    immutable(OUTPUT,(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps({'status':result['status'],'responses_reviewed':result['n'],
                      'original_totals_reproduced':True,'output':str(OUTPUT),'report':str(REPORT)},indent=2))


if __name__=='__main__':main()
