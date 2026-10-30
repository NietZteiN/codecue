"""Audited exploratory arithmetic/readout feasibility summaries.

All registered cells and both protocols remain visible. Numeric validation is a
separate check after training qualification; it never selects a replacement
protocol or changes historical gates. Only this fresh discovery cohort is read.
"""
from __future__ import annotations

from collections import defaultdict
import json
import math
from pathlib import Path

from .datasets import digest, read_jsonl
from .published_benchmarks import immutable, sha


PROTOCOLS = ('print_direct_v3', 'print_trace_long_v1')
CONTRASTS = (
    ('three_literal_minus_one_literal', 'literal_three', 'literal_one'),
    ('one_bound_minus_literal', 'bound_one', 'literal_one'),
    ('three_stored_intermediates_minus_literal', 'stored_intermediates_three', 'literal_three'),
    ('three_bound_minus_literal', 'bound_three', 'literal_three'),
    ('one_stored_result_minus_literal', 'stored_result_one', 'literal_one'),
    ('zero_stored_minus_literal', 'stored_output', 'literal_output'),
)
LIMITATION = (
    'Fresh numeric calibration on repeated arithmetic structures, not structural '
    'generalization or a causal mechanism test. One versus three operations also '
    'changes intermediate literal exposure; storage forms change assignments, '
    'dependencies and token distances. Trace responses change computation and '
    'generation allowance and are never pooled with direct answers. Intervals '
    'are exploratory without multiplicity adjustment. Historical failed gates '
    'and sealed final/extrapolation outcomes remain unchanged.'
)


def _cell(scores):
    """Counts and a descriptive binomial Wilson interval for one fixed cell."""
    scores=list(scores);n=len(scores)
    correct=sum(bool(s['correct']) for s in scores)
    invalid=sum(not s['valid'] for s in scores)
    bounds=[None,None]
    if n:
        z=1.959963984540054;p=correct/n;denominator=1+z*z/n
        center=(p+z*z/(2*n))/denominator
        half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
        bounds=[max(0.0,center-half),min(1.0,center+half)]
    return dict(n=n,correct=correct,invalid=invalid,valid=n-invalid,
                accuracy=correct/n if n else None,invalid_rate=invalid/n if n else None,
                wilson_95=bounds)


def paired_contrast(name,values,*,draws=2000,seed=913):
    """Bootstrap complete numeric-relative groups, preserving all paired rows."""
    import numpy as np
    if type(draws) is not int or draws<1:raise ValueError('positive bootstrap replicate count required')
    grouped=defaultdict(list)
    for group,value in values:
        if value not in (-1,0,1):raise ValueError('paired accuracy difference must be -1, 0 or 1')
        grouped[str(group)].append(value)
    if not grouped:raise ValueError('paired contrast requires complete groups')
    groups=[grouped[key] for key in sorted(grouped)]
    sums=np.asarray([sum(group) for group in groups],dtype=float)
    sizes=np.asarray([len(group) for group in groups],dtype=float)
    # Recompute the weighted mean after sampling clusters; do not treat paired
    # sign relatives within a cluster as independent bootstrap observations.
    rng=np.random.default_rng(seed)
    indices=rng.integers(0,len(groups),size=(draws,len(groups)))
    means=sums[indices].sum(axis=1)/sizes[indices].sum(axis=1)
    low,high=np.quantile(means,[.025,.975]).tolist()
    return dict(name=name,n=int(sizes.sum()),paired_groups=len(groups),mean=float(sums.sum()/sizes.sum()),
                exploratory_group_bootstrap_95=[low,high],bootstrap_replicates=draws,bootstrap_seed=seed,
                resampling_unit='paired_group_id; mirrored numeric relatives sampled together',
                multiplicity_adjusted=False)


def _thresholds(config):
    thresholds={'minimum_accuracy':.9,'maximum_invalid_rate':.05,'minimum_cell_n':24,
                **config.get('reliability_gate',{})}
    if (not 0<=thresholds['minimum_accuracy']<=1 or not 0<=thresholds['maximum_invalid_rate']<=1
            or type(thresholds['minimum_cell_n']) is not int or thresholds['minimum_cell_n']<1):
        raise ValueError('invalid fixed reliability thresholds')
    return thresholds


def _passes(cell,thresholds):
    return (cell['n']>=thresholds['minimum_cell_n'] and cell['unique_prompt_n']>=thresholds['minimum_cell_n']
            and cell['accuracy']>=thresholds['minimum_accuracy']
            and cell['invalid_rate']<=thresholds['maximum_invalid_rate'])


def _bounds(values):
    return dict(n=len(values),min=min(values),max=max(values),mean=sum(values)/len(values)) if values else None


def summarize(records,config):
    """Summarize (prepared case, audited response) pairs without selecting cells."""
    from .arithmetic_readout import FORMS
    records=list(records)
    if not records:raise ValueError('arithmetic review requires a complete nonempty cohort')
    cells=defaultdict(list);aggregates=defaultdict(list);protocols=defaultdict(list)
    cell_sources=defaultdict(set);cell_prompts=defaultdict(set)
    aggregate_sources=defaultdict(set);aggregate_prompts=defaultdict(set)
    prompt_lengths=defaultdict(list);generated_lengths=defaultdict(list)
    lookup={};tuples={};group_splits=defaultdict(set);strata=set()
    for case,response in records:
        if case['kind']!='arithmetic_readout':raise ValueError('arithmetic review cannot combine other suites')
        row=case['record'];variant=case['variant'];form=row['form'];split=row['split'];score=response['score']
        if score['correct'] and not score['valid']:raise ValueError('invalid response cannot count as correct')
        if variant not in PROTOCOLS or form not in FORMS or split not in ('train','development'):
            raise ValueError('unexpected arithmetic protocol, form or split')
        if row['operation_count']!=FORMS[form]:raise ValueError('arithmetic operation-count label differs')
        stratum=tuple(row['sign_stratum'])
        if len(stratum)!=3 or any(v not in (-1,1) for v in stratum):raise ValueError('unexpected nonzero sign stratum')
        base=row.get('tuple_id') or row['base_id'];key=(variant,base,form)
        if key in lookup:raise ValueError('duplicated logical arithmetic response')
        lookup[key]=(row,score);strata.add(stratum)
        identity=(split,stratum,row['expected_answer'],row['paired_group_id'])
        if base in tuples and tuples[base]!=identity:raise ValueError('numeric relatives changed split, answer or sign stratum')
        tuples[base]=identity;group_splits[row['paired_group_id']].add(split)
        cells[variant,form,split,stratum].append(score)
        aggregates[variant,form,split].append(score);aggregates[variant,form,'all'].append(score)
        source=row['source'];prompt=case.get('prompt_sha256') or digest(case.get('prompt',source))
        cell_sources[variant,form,split,stratum].add(source);cell_prompts[variant,form,split,stratum].add(prompt)
        for scope in (split,'all'):
            aggregate_sources[variant,form,scope].add(source);aggregate_prompts[variant,form,scope].add(prompt)
            if isinstance(case.get('input_token_ids'),list):prompt_lengths[variant,form,scope].append(len(case['input_token_ids']))
            if isinstance(response.get('output_token_ids'),list):generated_lengths[variant,form,scope].append(len(response['output_token_ids']))
        protocols[variant].append(score)
    if any(len(splits)!=1 for splits in group_splits.values()):raise ValueError('numeric-relative group leaks across splits')
    if len(strata)!=6:raise ValueError('all six registered sign strata are required')
    expected={(variant,base,form) for variant in PROTOCOLS for base in tuples for form in FORMS}
    if set(lookup)!=expected:raise ValueError('arithmetic review requires both protocols and every matched form')
    expected_cells={(variant,form,split,stratum) for variant in PROTOCOLS for form in FORMS
                    for split in ('train','development') for stratum in strata}
    if set(cells)!=expected_cells:raise ValueError('arithmetic sign/form/split matrix is incomplete')
    cell_rows=[dict(variant=key[0],form=key[1],operation_count=FORMS[key[1]],split=key[2],sign_stratum=list(key[3]),
                    unique_source_n=len(cell_sources[key]),unique_prompt_n=len(cell_prompts[key]),
                    **_cell(scores)) for key,scores in sorted(cells.items())]
    form_rows=[dict(variant=key[0],form=key[1],operation_count=FORMS[key[1]],split=key[2],
                    unique_source_n=len(aggregate_sources[key]),unique_prompt_n=len(aggregate_prompts[key]),**_cell(scores))
               for key,scores in sorted(aggregates.items())]
    source_overlap=[dict(variant=variant,form=form,operation_count=FORMS[form],
        train_unique_source_n=len(aggregate_sources[variant,form,'train']),
        development_unique_source_n=len(aggregate_sources[variant,form,'development']),
        shared_train_development_sources=len(aggregate_sources[variant,form,'train']&aggregate_sources[variant,form,'development']))
        for variant in PROTOCOLS for form in FORMS]
    token_geometry=[dict(variant=key[0],form=key[1],split=key[2],
                        prompt_tokens=_bounds(prompt_lengths[key]),generated_tokens=_bounds(generated_lengths[key]))
                    for key in sorted(aggregates)]
    if any(row['shared_train_development_sources'] for row in source_overlap if row['operation_count']>0):
        raise ValueError('nonzero arithmetic prompt sources overlap training and development')
    thresholds=_thresholds(config);gates={}
    for variant in PROTOCOLS:
        required=[dict(cell,passed=_passes(cell,thresholds)) for cell in cell_rows
                  if cell['variant']==variant and cell['operation_count']>0]
        train=[cell for cell in required if cell['split']=='train']
        development=[cell for cell in required if cell['split']=='development']
        train_pass=all(cell['passed'] for cell in train)
        development_pass=all(cell['passed'] for cell in development)
        gates[variant]=dict(status='passed' if train_pass and development_pass else 'failed',
            training_qualified=train_pass,development_descriptive_passed=development_pass,
            numeric_development_qualified=train_pass and development_pass,cells=required,
            zero_operation_controls=[cell for cell in cell_rows if cell['variant']==variant and cell['operation_count']==0],
            rule='Every nonzero-operation form × sign-stratum cell must qualify on training, then on numeric development. No protocol fallback or cell selection.')
    qualified=[variant for variant in PROTOCOLS if gates[variant]['numeric_development_qualified']]
    gate=dict(status='passed' if len(qualified)==len(PROTOCOLS) else 'mixed' if qualified else 'failed',
        protocols=gates,qualified_protocols=qualified,thresholds=thresholds,
        selection='No protocol is selected; both independent fixed gates and all results are retained.')
    contrast_rows=[];draws=config.get('bootstrap_replicates',2000);seed=config.get('bootstrap_seed',913)
    for variant in PROTOCOLS:
        for split in ('all','train','development'):
            bases=[base for base,identity in tuples.items() if split=='all' or identity[0]==split]
            for name,left,right in CONTRASTS:
                values=[]
                for base in sorted(bases):
                    lrow,lscore=lookup[variant,base,left];rrow,rscore=lookup[variant,base,right]
                    if lrow['expected_answer']!=rrow['expected_answer']:raise ValueError('paired form answers differ')
                    values.append((lrow['paired_group_id'],int(lscore['correct'])-int(rscore['correct'])))
                contrast_rows.append(dict(variant=variant,split=split,left_form=left,right_form=right,
                    **paired_contrast(name,values,draws=draws,seed=seed)))
    overall=_cell([response['score'] for _,response in records])
    return dict(status='complete_audited',complete=True,analysis_role='fresh_arithmetic_readout_feasibility',
        **overall,protocol_cells=[dict(variant=variant,**_cell(protocols[variant])) for variant in PROTOCOLS],
        cells=cell_rows,form_cells=form_rows,source_overlap=source_overlap,token_geometry=token_geometry,
        reliability_gate=gate,contrasts=contrast_rows,
        numeric_tuples=len(tuples),paired_groups=len(group_splits),generated_holdouts_opened=False,
        limitation=LIMITATION,
        interval_notes='Cell Wilson intervals are descriptive binomial intervals, not structural-generalization uncertainty. Zero-operation controls repeat exact deterministic prompts, report unique counts, and cannot be treated as independent numeric generalization evidence. Paired contrasts bootstrap whole numeric-relative groups; repeated templates are not independent structural replications.')


def collect(config):
    from .checkpoint_suite import audit, prepared, validate_response
    checked=audit(config);root=Path(config['run_dir'])/'checkpoint_suite'
    manifest=json.loads((root/'manifest.json').read_text())
    if (checked.get('status')!='passed' or not checked.get('complete') or manifest.get('status')!='complete'
            or manifest['identity_hash']!=digest(manifest['identity'])
            or manifest['identity']['config']!=config or checked['identity_hash']!=manifest['identity_hash']):
        raise ValueError('completed matching audited arithmetic run required')
    if sha(root/'responses.jsonl')!=manifest['responses_sha256']:raise ValueError('audited arithmetic responses changed')
    _,cases=prepared(config,checked['preflight']['source_sha256']);responses=read_jsonl(root/'responses.jsonl')
    if len(cases)!=len(responses):raise ValueError('arithmetic review response coverage differs')
    for case,response in zip(cases,responses):validate_response(case,response)
    result=summarize(zip(cases,responses),config)
    result.update(model=config['model'],revision=config['model_revision'],identity_hash=checked['identity_hash'],
        config_hash=digest(config),audit_sha256=sha(root/'audit.json'),responses_sha256=sha(root/'responses.jsonl'),
        dataset_sha256=sha(config['dataset']))
    return result


def _reusable(config):
    """Validate completed provenance without loading/recomputing response rows."""
    path=Path(config['review_artifact'])
    if not path.exists():return None
    result=json.loads(path.read_text());root=Path(config['run_dir'])/'checkpoint_suite'
    manifest=json.loads((root/'manifest.json').read_text())
    audit=json.loads((root/'audit.json').read_text())
    if (result.get('status')!='complete_audited' or not result.get('complete')
            or manifest.get('status')!='complete' or manifest['identity_hash']!=digest(manifest['identity'])
            or manifest['identity']['config']!=config or result.get('config_hash')!=digest(config)
            or result['identity_hash']!=manifest['identity_hash'] or audit.get('status')!='passed'
            or audit.get('identity_hash')!=manifest['identity_hash'] or not audit.get('complete')
            or result['audit_sha256']!=sha(root/'audit.json')
            or result['responses_sha256']!=sha(root/'responses.jsonl')
            or manifest['responses_sha256']!=result['responses_sha256']
            or result['dataset_sha256']!=sha(config['dataset'])
            or result['report_sha256']!=sha(config['report'])):
        raise ValueError('completed arithmetic review provenance changed')
    return result


def _cell_table(lines,cells,*,signs):
    columns='| Protocol | Form | Split | '+('Signs (r,s,y) | ' if signs else '')+'Correct / n | Unique prompts | Invalid | Accuracy Wilson 95% |'
    divider='|---|---|---|'+('---|' if signs else '')+'---:|---:|---:|---|'
    lines.extend([columns,divider])
    for cell in cells:
        low,high=cell['wilson_95'];interval=f'[{low:.1%}, {high:.1%}]' if low is not None else '—'
        values=[cell['variant'],cell['form'],cell['split']]
        if signs:values.append(','.join('+' if v>0 else '−' for v in cell['sign_stratum']))
        values.extend([f"{cell['correct']}/{cell['n']}",str(cell['unique_prompt_n']),str(cell['invalid']),interval])
        lines.append('| '+' | '.join(values)+' |')


def review(config):
    from .registry import code_identity
    reused=_reusable(config)
    if reused:return dict(status='complete_reused',report=config['report'],reliability_gate=reused['reliability_gate']['status'])
    result=collect(config);result['analysis_source']=code_identity()
    lines=['# Arithmetic and readout feasibility: '+config['model'],'',
        f"All {result['n']:,} registered responses retained: {result['correct']:,} correct and {result['invalid']:,} invalid across {result['numeric_tuples']} numeric tuples. Execution/audit status: complete and passed.",'',
        LIMITATION,'',
        'Each protocol has its own fixed gate. Every nonzero-operation form × split × sign-stratum cell must reach at least '
        f"{result['reliability_gate']['thresholds']['minimum_accuracy']:.0%} accuracy, at most {result['reliability_gate']['thresholds']['maximum_invalid_rate']:.0%} invalid responses and n ≥ {result['reliability_gate']['thresholds']['minimum_cell_n']}. "
        'Numeric development qualifies only after training qualification; no alternate protocol is substituted after failure. Zero-operation controls remain visible separately.','',
        '| Protocol | Training qualified | Numeric development qualified | Reliability |','|---|---|---|---|']
    for variant,gate in result['reliability_gate']['protocols'].items():
        lines.append(f"| {variant} | {gate['training_qualified']} | {gate['numeric_development_qualified']} | {gate['status']} |")
    lines.extend(['','## All forms by protocol and split','']);_cell_table(lines,result['form_cells'],signs=False)
    lines.extend(['','## Complete sign-stratified cells','',result['interval_notes'],''])
    _cell_table(lines,result['cells'],signs=True)
    lines.extend(['','## Exact-source overlap audit','',
        'Zero-operation controls repeat answers as literal prompts and do not support independent numeric validation. Nonzero forms must have no exact training/development source overlap.','',
        '| Protocol | Form | Unique training sources | Unique development sources | Shared sources |',
        '|---|---|---:|---:|---:|'])
    for cell in result['source_overlap']:
        lines.append(f"| {cell['variant']} | {cell['form']} | {cell['train_unique_source_n']} | {cell['development_unique_source_n']} | {cell['shared_train_development_sources']} |")
    lines.extend(['','## Token geometry','',
        'Lengths use saved prompt and generated token IDs, including invalid completions. Missing token IDs in software fixtures remain unreported. Different forms and protocols change token geometry.','',
        '| Protocol | Form | Split | Prompt tokens min/max/mean | Generated tokens min/max/mean |',
        '|---|---|---|---|---|'])
    for cell in result['token_geometry']:
        def display(value):return f"{value['min']}/{value['max']}/{value['mean']:.2f}" if value else '—'
        lines.append(f"| {cell['variant']} | {cell['form']} | {cell['split']} | {display(cell['prompt_tokens'])} | {display(cell['generated_tokens'])} |")
    lines.extend(['','## Paired form contrasts','',
        'Positive differences favor the left form. Sign-mirrored relatives are sampled together using paired_group_id; all registered contrasts remain reported. These intervals have no multiplicity adjustment.','',
        '| Protocol | Split | Contrast (left minus right) | Pairs | Numeric-relative groups | Difference | Exploratory 95% interval |',
        '|---|---|---|---:|---:|---:|---|'])
    for contrast in result['contrasts']:
        low,high=contrast['exploratory_group_bootstrap_95']
        lines.append(f"| {contrast['variant']} | {contrast['split']} | {contrast['name']} | {contrast['n']} | {contrast['paired_groups']} | {contrast['mean']:+.2%} | [{low:+.2%}, {high:+.2%}] |")
    lines.extend(['','No new mechanism claim, model training, frozen forecast or original final/extrapolation evaluation follows automatically from these descriptive results.',''])
    immutable(config['report'],'\n'.join(lines).encode())
    result.update(report=config['report'],report_sha256=sha(config['report']))
    immutable(config['review_artifact'],(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status='complete_audited',report=config['report'],reliability_gate=result['reliability_gate']['status'])


def compare(config):
    """Combine pinned reviews without rereading or selecting response cohorts."""
    from .registry import code_identity
    target=config.get('comparison_artifact') or config.get('output')
    if not target:raise ValueError('comparison_artifact or output path required')
    results={};checksums={};common=None
    for name,spec in config['runs'].items():
        if sha(spec['config'])!=spec['sha256']:raise ValueError('arithmetic comparison model configuration changed')
        effective=json.loads(Path(spec['config']).read_text());result=_reusable(effective)
        if result is None:raise ValueError('arithmetic comparison requires complete audited reviews')
        identity=(result['dataset_sha256'],effective.get('generation'),effective['sections'],
                  result['reliability_gate']['thresholds'],effective.get('bootstrap_replicates',2000),effective.get('bootstrap_seed',913))
        if common is not None and identity!=common:raise ValueError('arithmetic comparison cohorts, protocols or analysis plans differ')
        common=identity;results[name]=result;checksums[effective['review_artifact']]=sha(effective['review_artifact'])
    if len(results)!=2:raise ValueError('registered two-checkpoint arithmetic comparison required')
    if Path(target).exists():
        previous=json.loads(Path(target).read_text())
        if (previous.get('status')!='passed' or not previous.get('complete')
                or previous.get('config_hash')!=digest(config) or previous.get('review_checksums')!=checksums
                or previous.get('report_sha256')!=sha(config['report'])):
            raise ValueError('completed arithmetic comparison provenance changed')
        return dict(status='complete_reused',report=config['report'],total_predictions=previous['total_predictions'])
    lines=['# Arithmetic and readout feasibility comparison','',
        f"Both cached checkpoints completed the registered cohort: {sum(result['n'] for result in results.values()):,} responses. Complete execution and passed artifact audits are separate from reliability qualification.",'',
        LIMITATION,'',
        '| Checkpoint | Protocol | Correct / n | Invalid | Training qualified | Numeric development qualified | Reliability |',
        '|---|---|---:|---:|---|---|---|']
    for name,result in results.items():
        for cell in result['protocol_cells']:
            gate=result['reliability_gate']['protocols'][cell['variant']]
            lines.append(f"| {name} | {cell['variant']} | {cell['correct']}/{cell['n']} | {cell['invalid']} | {gate['training_qualified']} | {gate['numeric_development_qualified']} | {gate['status']} |")
    lines.extend(['','## All paired arithmetic/storage contrasts','',
        '| Checkpoint | Protocol | Split | Contrast | Pairs | Relative groups | Difference | Exploratory 95% interval |',
        '|---|---|---|---|---:|---:|---:|---|'])
    for name,result in results.items():
        for contrast in result['contrasts']:
            low,high=contrast['exploratory_group_bootstrap_95']
            lines.append(f"| {name} | {contrast['variant']} | {contrast['split']} | {contrast['name']} | {contrast['n']} | {contrast['paired_groups']} | {contrast['mean']:+.2%} | [{low:+.2%}, {high:+.2%}] |")
    lines.extend(['','Complete form × protocol × split × sign cells, including zero-operation controls, appear in each report and the machine-readable comparison.',''])
    for name,spec in config['runs'].items():
        effective=json.loads(Path(spec['config']).read_text());lines.append(f"- [{name}]({Path(effective['report']).name})")
    lines.extend(['','The same numeric cohort is shared by the two checkpoints. Numeric examples and sign-relative bootstrap groups do not provide independent structural or program-family replications. No protocol/cell winner is selected.',''])
    immutable(config['report'],'\n'.join(lines).encode())
    result=dict(status='passed',complete=True,models=results,review_checksums=checksums,
        total_predictions=sum(value['n'] for value in results.values()),analysis_source=code_identity(),
        config_hash=digest(config),report=config['report'],report_sha256=sha(config['report']),generated_holdouts_opened=False)
    immutable(target,(json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    return dict(status='complete_audited',report=config['report'],total_predictions=result['total_predictions'])
