#!/usr/bin/env python
"""Render discovery evidence from existing artifacts; never runs a model or opens test outcomes."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from codecue.binding.analysis import interval
from codecue.binding.datasets import digest, read_jsonl, write_json
from codecue.binding.snapshots import workspace_root

ROOT = workspace_root(Path(__file__).resolve().parents[1])
DATA = ROOT / 'artifacts/binding'
REPORT = ROOT / 'reports/binding/pilot_report.md'


def read(path):
    return json.loads(path.read_text())


def percent(value):
    return '—' if value is None else f'{100 * value:.1f}%'


def probe_figure(results, intervals):
    """Plot every predeclared neutral development site/layer; no selection."""
    import importlib.util
    if importlib.util.find_spec('matplotlib') is None:
        return None
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    selected=[r for r in results if r['train_condition']==r['evaluation_condition']=='neutral']
    cis={(r['site'],r['task'],r['layer']):r for r in intervals}
    sites=('last_assignment','source_final')
    tasks=('current','previous','multiset')
    maximum=max(c['ci95'][1] for c in intervals if c['ci95'] is not None)
    fig,axes=plt.subplots(2,3,figsize=(11,6),sharex=True,sharey=True,layout='constrained')
    for row_index,site in enumerate(sites):
        for column,task in enumerate(tasks):
            ax=axes[row_index,column]
            rows=sorted([r for r in selected if r['site']==site and r['task']==task],key=lambda r:r['layer'])
            layers=[r['layer'] for r in rows]
            hidden=np.array([r['linear']['slot_exact_accuracy'] for r in rows])
            ci=[cis[(site,task,r['layer'])]['ci95'] for r in rows]
            ax.errorbar(layers,hidden,yerr=np.maximum(0,np.array([[p-c[0],c[1]-p] for p,c in zip(hidden,ci)]).T),
                        marker='o',capsize=3,label='Hidden ridge',color='#2364aa')
            for key,label,color in (('surface','Surface ridge','#b87515'),('majority','Training mode','#777777')):
                ax.plot(layers,[r[key]['slot_exact_accuracy'] for r in rows],linestyle='--',label=label,color=color)
            ax.plot(layers,[np.mean([c['slot_exact_accuracy'] for c in r['randomized_label_controls']]) for r in rows],
                    linestyle=':',label='Random-label task',color='#a34c83')
            ax.set_title(f'{site.replace("_"," ")} · {task}')
            ax.set_ylim(0,min(1,max(.25,maximum+.05)))
            ax.set_xticks(layers)
            ax.yaxis.set_major_formatter(PercentFormatter(1))
            ax.grid(alpha=.2)
            if row_index==1:
                ax.set_xlabel('Zero-based decoder block')
            if column==0:
                ax.set_ylabel('Exact defined-slot accuracy')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=4,frameon=False)
    fig.suptitle('CodeLlama CPU discovery: neutral train → neutral development')
    for suffix in ('png','svg'):
        fig.savefig(REPORT.with_name('probe_curves.'+suffix),dpi=170)
    plt.close(fig)
    return {'path':'reports/binding/probe_curves.png',
            'sha256':hashlib.sha256(REPORT.with_name('probe_curves.png').read_bytes()).hexdigest()}


def training_recovery(base,stage,index,results):
    from codecue.binding.probes import predict,metrics
    scores={}
    train=[r for r in index if r['split']=='train' and r['condition']=='neutral']
    captured={}
    for row in results:
        if row['train_condition'] != 'neutral' or row['evaluation_condition'] != 'neutral':
            continue
        key=(row['site'],row['layer'])
        pi=-2 if row['site']=='last_assignment' else -1
        if key not in captured:
            vectors=[]
            for r in train:
                with np.load(base/'activations'/r['file']) as chunk:
                    vectors.append(chunk['hidden'][pi,r['layers'].index(row['layer'])].astype(float))
            captured[key]=np.array(vectors)
        path=base/stage/f"{row['site']}_L{row['layer']}_{row['task']}_neutral.npz"
        with np.load(path) as saved:
            fitted=tuple(saved[k] for k in ('mu','sd','weights','intercept'))
        gold=np.array([[np.nan if v is None else v for v in r['checkpoints'][pi][row['task']]] for r in train])
        prediction=predict(fitted,captured[key])
        if row['task']=='multiset':
            prediction=np.sort(prediction,axis=1)
        scores[(*key,row['task'])]={'metrics':metrics(prediction,gold),'n':len(train),
                                  'weights_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return scores


def calibration_figure():
    import importlib.util
    baseline=DATA/'interface_cpu_fp32_prefill_v2/interface_diagnostics/responses.json'
    if not baseline.exists() or importlib.util.find_spec('matplotlib') is None:
        return None
    original=read(baseline)['responses_by_batch_size']['4']
    columns=[('Answer prefix\n12 tokens',{r['id']:r for r in original})]
    for directory,variant,title in (
        ('protocol_calibration_fp32','print_direct_v3','Print direct\n16 tokens'),
        ('protocol_calibration_fp32','print_trace_v1','Print trace\n256 tokens'),
        ('protocol_calibration_long_fp32','print_trace_long_v1','Print trace\n512 tokens')):
        root=DATA/directory/'protocol_calibration'
        if not (root/'summary.json').exists() or not read(root/'summary.json')['complete']:
            continue
        rows=[r for r in read_jsonl(root/'responses.jsonl') if r['variant']==variant]
        by_id={r['id']:r for r in rows}
        if set(by_id)!={r['id'] for r in original} or any(
            by_id[r['id']]['source']!=r['source'] or by_id[r['id']]['expected_answer']!=r['expected_answer'] for r in original):
            raise ValueError('calibration figure requires matching underlying programs and labels')
        columns.append((title,by_id))
    if len(columns)==1:
        return None
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    colors=['#dddddd','#f0c49b','#acd5b4']
    grid=np.array([[0 if data[r['id']]['prediction'] is None else
                    (2 if data[r['id']]['prediction']==r['expected_answer'] else 1)
                    for _,data in columns] for r in original])
    fig,ax=plt.subplots(figsize=(8.8,7),layout='constrained')
    ax.imshow(grid,cmap=ListedColormap(colors),vmin=0,vmax=2,aspect='auto')
    labels=[]; training_number=0
    for i,r in enumerate(original):
        if r['kind']=='primitive':
            name=r['id'].removeprefix('sanity:').replace('_',' ')
        else:
            training_number+=1;name=f'training program {training_number}'
        labels.append(f"{name} (expected {r['expected_answer']})")
        for j,(_,data) in enumerate(columns):
            value=data[r['id']]['prediction']
            ax.text(j,i,'invalid' if value is None else str(value),ha='center',va='center',fontsize=10)
    ax.set_yticks(range(len(original)),labels)
    ax.set_xticks(range(len(columns)),[title for title,_ in columns])
    ax.tick_params(length=0)
    ax.set_title('Training-only readout calibration\nFP32, greedy decoding, batch size 4')
    fig.legend(handles=[Patch(facecolor=c,label=l) for c,l in zip(colors,('Invalid format','Incorrect integer','Correct integer'))],
               loc='outside lower center',ncol=3,frameon=False)
    for suffix in ('png','svg'):
        fig.savefig(REPORT.with_name('calibration_readouts.'+suffix),dpi=170)
    plt.close(fig)
    return {'path':'reports/binding/calibration_readouts.png',
            'sha256':hashlib.sha256(REPORT.with_name('calibration_readouts.png').read_bytes()).hexdigest()}


def ladder_figure(decision):
    import importlib.util
    if not decision['complete'] or importlib.util.find_spec('matplotlib') is None:
        return None
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    styles=('reassigned_chain','fresh_chain','independent_arithmetic')
    variants=('print_direct_v3','print_trace_long_v1')
    values={(r['variant'],r['style'],r['assignment_count']):r for r in decision['cells']}
    fig,axes=plt.subplots(2,2,figsize=(10,6),layout='constrained',sharex=True,sharey='row')
    for column,variant in enumerate(variants):
        for style,color in zip(styles,('#2364aa','#b87515','#6a8f3a')):
            points=[values[(variant,'computed_baseline',1)]]+[values[(variant,style,n)] for n in (2,4,8)]
            for axis,key in ((axes[0,column],'correct'),(axes[1,column],'invalid')):
                axis.plot((1,2,4,8),[r[key]/r['n'] for r in points],marker='o',color=color,label=style.replace('_',' '))
        axes[0,column].set_title('Print direct · 16 tokens' if column==0 else 'Print trace · 512 tokens')
        axes[1,column].set_xlabel('Assignments')
        for axis in axes[:,column]:
            axis.set_ylim(-.04,1.04)
            axis.set_xticks((1,2,4,8))
            axis.yaxis.set_major_formatter(PercentFormatter(1))
            axis.grid(alpha=.2)
    axes[0,0].set_ylabel('Exact-answer accuracy')
    axes[1,0].set_ylabel('Invalid-output fraction')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=3,frameon=False)
    fig.suptitle('Training difficulty ladder · GPU BF16 · 12 programs per cell\nOne-assignment baseline is shared; repeated structures are calibration data')
    for suffix in ('png','svg'):
        fig.savefig(REPORT.with_name('difficulty_ladder.'+suffix),dpi=170)
    plt.close(fig)
    return {'path':'reports/binding/difficulty_ladder.png',
            'sha256':hashlib.sha256(REPORT.with_name('difficulty_ladder.png').read_bytes()).hexdigest()}


def handoff(evidence):
    stopped=evidence.get('difficulty_ladder',{}).get('status')=='stop_no_usable_regime'
    scientific_next=(
        'The complete fixed difficulty ladder found no qualifying regime. Its stopping rule ends this checkpoint/protocol '
        'feasibility pilot. Preserve the null/mixed results and reusable software; any further model experiment requires '
        'a newly specified scientific plan rather than automatic prompt or intervention expansion. '
        'No explanatory hypothesis or empirical C predictor is supported; final model outcomes remain sealed.'
        if stopped else
        'Inspect the larger behavior cohort, corrected development curves and all causal negative controls before choosing H1–H5. '
        'A train/development decoding gap is a measurement-generalization issue, not evidence of missing model state. '
        'A full-residual value-transfer effect requires ownership and path specificity before a binding-mechanism claim. '
        'Only then fit supported mechanistic predictors and freeze unfamiliar-program forecasts. '
        'Final test behavior remains sealed. A null or mixed result is valid.')
    jobs=[]
    for path in sorted(DATA.glob('*jobs.json')):
        values=read(path)
        for role,value in values.items():
            if isinstance(value,str) and value.isdigit():
                jobs.append({'job_id':value,'role':role,'manifest':str(path.relative_to(ROOT)),
                             'snapshot':values.get('snapshot')})
    ids=sorted({r['job_id'] for r in jobs})
    states={}
    if ids:
        result=subprocess.run(['sacct','-j',','.join(ids),'--format=JobIDRaw,State,ElapsedRaw,AllocCPUS,AllocTRES','-P','-n'],
                              capture_output=True,text=True,check=True)
        for line in result.stdout.splitlines():
            fields=line.split('|')
            if fields[0] in ids:
                gpu=re.search(r'(?:^|,)gres/gpu=(\d+)(?:,|$)',fields[4])
                states[fields[0]]={'state':fields[1],'elapsed_seconds':int(fields[2]),'allocated_cpus':int(fields[3]),
                                   'allocated_gpus':int(gpu.group(1)) if gpu else 0}
    for row in jobs:
        row.update(states.get(row['job_id'],{'state':'not available'}))
    evidence['jobs']=jobs
    log=DATA/'tests_phase2.log'
    tests=re.findall(r'(\d+) passed in ([0-9.]+)s',log.read_text()) if log.exists() else []
    evidence['tests']={'passed':int(tests[-1][0]),'wall_seconds':float(tests[-1][1])} if tests else None
    evidence['code_test_log']='artifacts/binding/tests_phase2.log'
    text=['# Binding-study handoff','',f"Generated {evidence['generated_utc']}. Read [the empirical pilot report](pilot_report.md), "
          '[reproduction commands](README.md), [research decisions](research_decisions.md), '
          '[implementation checklist](implementation_checklist.md), and [forecaster contracts](predictors.md).','',
          '## Completed and interpretation','',
          'Real CPU BF16 CodeLlama behavior, activation extraction and development probe fits now exist. '
          'Their scope, uncertainty and exact identities are in the generated pilot report. '
          'The original unprefilled protocol was interrupted for parsing redesign; its raw responses remain separate. '
          'The original behavior runs use the assistant `Answer:` prefix; subsequent printed and reasoning readouts are separate protocols. '
          'Completed CPU/GPU interface checks remain distinct sensitivity runs.','',
          'The generator supports the original four-variable pilot and four reserved structural extrapolation cohorts. '
          'The full reserved cohorts are validated and their model outcomes remain sealed. '
          'Version 5 regenerated byte-for-byte after the structural generalization. '
          'Source/configuration snapshots are immutable and verified before each queued run.','',
          'The fitting interfaces cover state probes and nested logistic failure predictors. '
          'No empirical C predictor, frozen explanatory hypothesis, binding-specific pathway or confirmatory result is established. '
          'No optional checkpoint training, second model, unlearning or empirical paper abstract has been launched.','']
    if evidence['tests']:
        text += [f"Latest full suite: **{evidence['tests']['passed']} passed** in {evidence['tests']['wall_seconds']} seconds. "
                 'Random-network and synthetic-predictor tests are software checks, excluded from model results.','']
    if (ROOT/'reports/binding/experiment_program.md').exists():
        text += ['A later user-authorized [ten-experiment program](experiment_program.md) has separate diagnostics and '
                 'a [reference-tokenizer correction](tokenizer_boundary_correction.md). '
                 'Its stage table distinguishes completed runs from unmet scientific prerequisites. '
                 'The earlier native-tokenization pilot and its stopping decision remain historical records.','']
    text += ['## Current jobs','', '| Job | Role / manifest | State | Allocated elapsed seconds |', '|---|---|---|---:|']
    seen=set()
    for row in jobs:
        if row['job_id'] in seen:
            continue
        seen.add(row['job_id'])
        text.append(f"| {row['job_id']} | {row['role']} · `{row['manifest']}` | {row['state']} | {row.get('elapsed_seconds','—')} |")
    text += ['', 'The corrected small-cohort probe analysis fixes masked-label intercepts and the surface baseline information boundary. '
             'The main-data supplement retains neutral training and every development naming condition, with fixed blocks and ridge penalty. '
             'The larger behavioral subset retains all twelve factorial cells, all six naming realizations, both tasks and the primary magnitude-bin mixture. '
             'Selection plans and source pointers are recorded beside the job manifests.','',
             'CPU jobs run under the cluster quota. Full GPU expansion was cancelled before allocation after near-floor CPU discovery; '
             'a usable arithmetic/interface calibration is required before resubmission. '
             'GPU stage time is recorded in `artifacts/binding/gpu_budget.json`, in the historical ledger; current work uses uncapped accounting. '
             'Allocated GPU elapsed time, including batch startup, is reported separately below when available. '
             'CPU limits are explicit in each config/job; aggregate interactive CPU time was not instrumented. '
             'Retained activation bytes and measured forward times are in stage manifests. No unrelated caches were deleted.','',
             '## Next scientific decision','',
             scientific_next,'',
             'Regenerate this handoff and evidence after jobs finish with `python scripts/92_binding_progress_report.py`. '
             'The phase-one `implementation_manifest.json` is historical; `phase2_evidence.json` records this continuation.','']
    if evidence.get('difficulty_ladder'):
        ladder=evidence['difficulty_ladder']
        text += ['## Difficulty-ladder decision','',
                 f"Status: `{ladder['status']}`; queries completed: {ladder['queries_completed']}/{ladder['queries_planned']}. "
                 'See the [fixed plan](difficulty_ladder_plan.md) and the full cell table in the pilot report. '
                 'The original conditional calibration bank remains skipped; final-test outcomes remain sealed.','']
    ledger=DATA/'gpu_budget.json'
    if ledger.exists():
        charged=read(ledger)
        gpu_jobs={row['job_id']:row for row in jobs if row.get('allocated_gpus',0)}
        allocated=sum(row.get('elapsed_seconds',0)*row['allocated_gpus'] for row in gpu_jobs.values())
        evidence['gpu_resources']={'ledger_used_seconds':charged['used_seconds'],
                                   'allocated_gpu_seconds':allocated,'allocated_gpu_jobs':list(gpu_jobs),
                                   'cap_seconds':charged['cap_seconds'],'active_reservations':len(charged['active'])}
        text += ['## GPU resource accounting','',
                 f"Completed GPU stages charged {charged['used_seconds']:.2f} seconds to the model-stage ledger "
                 f"of {charged['cap_seconds']} seconds; active reservations: {len(charged['active'])}. "
                 f"Recorded GPU jobs allocated {allocated} GPU-seconds including batch startup. "
                 'These clocks have different boundaries and are not added together.','']
    (REPORT.parent/'handoff.md').write_text('\n'.join(text))


def main():
    evidence = {'generated_utc': datetime.now(timezone.utc).isoformat(),
                'report_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'scope': 'discovery only; no heldout responses read', 'datasets': []}
    text = ['# Binding-study discovery pilot', '',
            'This report is generated from recorded artifacts. Results concern one cached CodeLlama checkpoint. '
            'No primary explanation among H1–H5 or confirmatory claim has been selected.', '',
            '## Behavioral feasibility', '']
    larger=DATA/'cpu_discovery_subset_prefill_v2/behavior'
    use_larger=(larger/'manifest.json').exists() and read(larger/'manifest.json')['status']=='complete'
    run = larger if use_larger else DATA / 'cpu_smoke_bf16_prefill_v2/behavior'
    if (run / 'summary.json').exists():
        summary, manifest = read(run / 'summary.json'), read(run / 'manifest.json')
        config = manifest['identity']['config']
        rows = read_jsonl(run / 'responses.jsonl')
        if any(r['split'] == 'test' for r in rows):
            raise ValueError('progress reports must not inspect heldout outcomes')
        evidence['behavior'] = {'manifest': str((run/'manifest.json').relative_to(ROOT)),
                                'identity_hash': manifest['identity_hash'], 'summary': summary}
        text += [f"Model `{config['model']}`, revision `{config['model_revision']}`; {config['dtype']}, "
                 f"{config['device']}, greedy `{config['protocol']}` with an assistant `Answer:` prefix. "
                 'The earlier unprefilled protocol produced explanations outside the strict integer parser; '
                 'its interrupted run is retained separately and excluded here.', '',
                 f"The completed {'balanced discovery subset' if use_larger else 'balanced smoke'} has {len(rows)} responses across {summary['bases']} bases and "
                 f"{summary['independent_template_clusters']} parent-template clusters. "
                 f"Invalid outputs: {summary['invalid_count']}. All six naming renderings and both primary/arithmetic tasks are retained.", '',
                 '| Task | Responses | Exact accuracy | Cluster bootstrap 95% interval |',
                 '|---|---:|---:|---|']
        for kind, values in sorted(summary['by_control_kind'].items()):
            text.append(f"| {kind} | {values['n']} | {percent(values['accuracy']['estimate'])} | {values['accuracy']['ci95']} |")
        primary = [r for r in rows if r['control_kind'] == 'primary']
        text += ['', '| Primary naming | Responses | Correct |', '|---|---:|---:|']
        for condition in ('neutral', 'informative', 'misleading'):
            subset = [r for r in primary if r['condition'] == condition]
            text.append(f"| {condition} | {len(subset)} | {sum(r['correct'] for r in subset)} |")
        design_note=('The larger subset preserves the primary 40/40/20 magnitude-bin mixture within every factorial cell. '
                     'It overlaps some earlier smoke examples and is not an independent replication. '
                     if use_larger else 'The smoke contains only the lowest answer-magnitude bin; the full pilot covers three bins. ')
        text += ['', 'Naming contrasts in this discovery sample do not establish equivalence. ' + design_note +
                 'Arithmetic-control performance also leaves arithmetic and output selection as live explanations.', '',
                 '| Compatible error label (nonexclusive) | Responses | Independent bases |', '|---|---:|---:|---:|']
        for label, count in sorted(summary['counterfactual_consistent_error_counts_nonexclusive'].items()):
            bases = {r['base_id'] for r in rows if label in r['classification']['compatible_labels']}
            text.append(f'| {label} | {count} | {len(bases)} |')
        text += ['', f"Ambiguous errors: {summary['ambiguous_error_count']}. Compatible labels describe answers, "
                 'not identified internal causes. Lexical relatives are not independent replications.', '',
                 f"Behavior wall time: {manifest.get('wall_seconds_total', 0):.1f} s; "
                 f"CPU forward/generation time: {manifest.get('device_seconds', 0):.1f} s. "
                 'Raw responses, prompts, token IDs and exact identities are retained in the behavior directory.', '']
        reference_path=run.parent/'diagnostic_null.json'
        if reference_path.exists():
            reference=read(reference_path)
            if reference['behavior_identity_hash']!=manifest['identity_hash']:
                raise ValueError('diagnostic reference does not match reported behavior')
            evidence['diagnostic_prediction_prior']=reference
            text += ['### Prediction-prior control', '',
                     'Complete base prediction vectors are shuffled within family/load/update/split cells, retaining naming, lexical '
                     'and task pairing. This measures accidental compatibility under the observed output prior. '
                     'The reference bands are within-cohort permutation ranges, not population confidence intervals or significance tests.', '',
                     '| Task | Compatible label | Observed rate | Shuffled mean | Shuffled 95% reference range |',
                     '|---|---|---:|---:|---|']
            for row in reference['endpoints']:
                lo,hi=row['shuffled_reference95']
                text.append(f"| {row['control_kind']} | {row['label']} | {percent(row['observed_rate'])} | "
                            f"{percent(row['shuffled_mean_rate'])} | {percent(lo)}–{percent(hi)} |")
            text += ['',f"The control uses {reference['repetitions']} permutations and {reference['permutable_bases']} "
                     f"permutable bases; {reference['singleton_strata']} singleton cells cannot vary. "
                     'Numeric bases can share structural parents and prompt effects within a cell remain uncontrolled. '
                     'Counterfactual matches resembling this output-prior reference do not establish binding interference.', '']
    text += ['## Representation measurements', '']
    base = DATA / 'cpu_representations_prefill_v2'
    supplement=DATA/'cpu_representations_main_neutral_prefill_v2'
    if (supplement/'probes/manifest.json').exists() and read(supplement/'probes/manifest.json')['status']=='complete':
        base=supplement
    probe_stage = 'probes_centered_v3' if (base/'probes_centered_v3/development_curves.json').exists() else 'probes'
    curves = base / probe_stage / 'development_curves.json'
    if curves.exists():
        cache_manifest = read(base/'activations/manifest.json')
        probe_manifest = read(base/probe_stage/'manifest.json')
        if cache_manifest['status'] != 'complete' or probe_manifest['status'] != 'complete':
            raise ValueError('do not report incomplete measurements as completed results')
        index = read_jsonl(base/'activations/index.jsonl')
        if any(r['split'] == 'test' for r in index):
            raise ValueError('probe report cannot read test activations')
        by_id = {r['id']:r for r in index}
        curve_metadata=read(curves)
        results = curve_metadata['results']
        corrected=bool(curve_metadata.get('masked_intercept'))
        train_scores=training_recovery(base,probe_stage,index,results)
        evidence['probes'] = {'manifest': str((base/probe_stage/'manifest.json').relative_to(ROOT)),
                              'identity_hash': probe_manifest['identity_hash'], 'development_intervals': [],
                              'training_recovery':[{'site':s,'layer':l,'task':t,**values} for (s,l,t),values in train_scores.items()]}
        text += [f"Extraction completed on {len(index)} primary train/development renderings "
                 f"({len({r['base_id'] for r in index})} bases), using {cache_manifest['artifact_bytes']:,} retained bytes. "
                 'Probes use fixed-alpha ridge, train-only normalization, integer rounding and separate current/previous/multiset fits. '
                 'All supplied sites and layers are reported; none is selected as a primary mechanism.', '',
                 '| Site | Block | Task | Hidden train / dev | Dev 95% cluster interval | Surface dev | Mode dev | Random-label dev |',
                 '|---|---:|---|---:|---|---:|---:|---:|']
        for row in results:
            if row['train_condition'] != 'neutral' or row['evaluation_condition'] != 'neutral':
                continue
            values, clusters = [], []
            for identifier, prediction in zip(row['ids'], row['predictions']):
                example = by_id[identifier]
                pi = -2 if row['site'] == 'last_assignment' else -1
                gold = example['checkpoints'][pi][row['task']]
                for observed, target in zip(prediction, gold):
                    if target is not None:
                        values.append(observed == target)
                        clusters.append(example['cluster_id'])
            ci = interval(values, clusters)
            evidence['probes']['development_intervals'].append({
                **{k:row[k] for k in ('site','layer','task')}, **ci})
            random_mean = np.mean([r['slot_exact_accuracy'] for r in row['randomized_label_controls']])
            train_accuracy=train_scores[(row['site'],row['layer'],row['task'])]['metrics']['slot_exact_accuracy']
            text.append(f"| {row['site']} | {row['layer']} | {row['task']} | "
                        f"{percent(train_accuracy)} / {percent(row['linear']['slot_exact_accuracy'])} | {ci['ci95']} | "
                        f"{percent(row['surface']['slot_exact_accuracy'])} | {percent(row['majority']['slot_exact_accuracy'])} | "
                        f"{percent(random_mean)} |")
        surface_note = ('The surface baseline uses the same visible source prefix as each hidden site. '
                        if corrected else
                        'The surface baseline reads the full source even at the last-assignment site; this gives that baseline the later query. ')
        text += ['', 'The table uses neutral training and neutral development. The complete JSON contains every within-condition fit '
                 'and cross-condition transfer, MAE, whole-state scores, capacity and label priors. '
                 'Intervals resample parent-template clusters and are descriptive, without correction for selecting among sites/layers. '
                 'Random-label accuracy concerns a different target task and is not a paired improvement estimate. '
                 + surface_note + 'Training scores are recomputed from saved weights, without refitting. '
                 'A large train/development gap indicates weak generalization of this estimator on this small cohort; '
                 'it does not establish an internal tracking failure. '
                 'These measurements establish neither natural causal use nor information absence when decoding fails.', '']
        if corrected:
            figure=probe_figure(results,evidence['probes']['development_intervals'])
            if figure:
                evidence['probe_figure']=figure
                text += ['![All predeclared probe curves and controls](probe_curves.png)', '',
                         'Error bars are descriptive cluster bootstrap intervals for hidden decoding. '
                         'Random-label control points concern separate tasks. All plotted sites and blocks were fixed before extraction.', '']
    else:
        text += ['Activation extraction or probe fitting is pending; no recovery result is claimed.', '']
    sensitivity=DATA/'cpu_representations_main_neutral_prefill_v2/regularization_sensitivity.json'
    if sensitivity.exists():
        sweep=read(sensitivity)
        evidence['probe_regularization']={'artifact':str(sensitivity.relative_to(ROOT)),
                                          'alpha_grid':sweep['alpha_grid'],'selection':sweep['selection']}
        table={}
        for analysis in sweep['analyses']:
            for row in analysis['results']:
                if row['train_condition']==row['evaluation_condition']=='neutral':
                    table.setdefault((row['site'],row['layer'],row['task']),{})[analysis['alpha']]=row
        text += ['### Fixed regularization sensitivity', '',
                 'The following grid changes the ridge penalty while retaining decoder capacity, extraction cache and train-only preprocessing. '
                 'Every task, site and block is retained. The complete artifact also includes naming transfer, surface and randomized-label controls. '
                 'This development sensitivity selects no primary site or penalty.', '',
                 '| Site | Block | Task | α=1 accuracy / MAE | α=100 accuracy / MAE | α=10000 accuracy / MAE |',
                 '|---|---:|---|---|---|---|']
        for (site,layer,task),values in sorted(table.items()):
            metrics=[values[a]['linear'] for a in sweep['alpha_grid']]
            text.append(f'| {site} | {layer} | {task} | '+' | '.join(
                f"{percent(m['slot_exact_accuracy'])} / {m['mae']:.2f}" for m in metrics)+' |')
        text += ['', 'Regularization can improve a measurement estimator without establishing natural state use. '
                 'The original fixed-penalty results remain the earlier experiment, and final-test outcomes remain sealed.', '']
    text += ['## Causal assay', '']
    assay = DATA/'cpu_value_assay_prefill_v2/interventions'
    if (assay/'summary.json').exists() and read(assay/'manifest.json')['status'] == 'complete':
        result = read(assay/'summary.json')
        raw=read_jsonl(assay/'assays.jsonl')
        no_op={r['id']:r for r in raw if r['control']=='no_op'}
        assay_config=read(assay/'manifest.json')['identity']['config']
        all_records=read_jsonl(assay_config['dataset'])
        selection=assay_config['intervention']
        candidate_cells={}
        for r in all_records:
            if (r['split']=='development' and r['condition']=='neutral' and r['lexical_realization']==0 and
                r['control_kind']=='primary' and r['family'] in selection.get('families',('parallel','snapshot','accumulator'))):
                candidate_cells.setdefault((r['family'],r['load'],r['updates']),[]).append(r)
        planned=sum(min(len(group),selection.get('per_cell_limit',1)) for group in candidate_cells.values())
        if len(no_op) != planned or len(raw) != 9*planned:
            raise ValueError('legacy assay manifest says complete but planned controls are missing; inspect before reporting')
        self_rows=[r for r in raw if r['control']=='self_patch']
        result['self_patch_exact_response_matches']=sum(r['raw_response']==no_op[r['id']]['raw_response'] for r in self_rows)
        result['self_patch_comparisons']=len(self_rows)
        for entry in result['controls']:
            paired=[r for r in raw if r['control']==entry['control'] and r['control']!='reciprocal_value_donor']
            if paired:
                entry['paired_accuracy_change_from_no_op']=interval(
                    [float(r['exact_counterfactual'])-float(no_op[r['id']]['exact_counterfactual']) for r in paired],
                    [r['cluster_id'] for r in paired])
        evidence['value_assay'] = result
        text += ['This development calibration uses one predeclared block, computed donors and accumulator programs. '
                 'Recipients were selected by stable ID within factorial cells rather than by successful patching. '
                 'Late quantity queries can trigger reconstruction; full-residual transfer does not isolate a natural pathway.', '',
                 '| Control | Recipients | Counterfactual output | Dependent quantities | Independent quantities |',
                 '|---|---:|---:|---:|---:|']
        for control in result['controls']:
            text.append(f"| {control['control']} | {control['n']} | "
                        f"{percent(control['counterfactual_accuracy']['estimate'])} | "
                        f"{percent(control.get('dependent_quantity_accuracy',{}).get('estimate'))} | "
                        f"{percent(control.get('independent_quantity_accuracy',{}).get('estimate'))} |")
        text += ['', 'Complete likelihood margins, bootstrap intervals, baseline-correct counts and raw responses are retained. '
                 f"Self-patch responses exactly matched no-op in {result['self_patch_exact_response_matches']}/{result['self_patch_comparisons']} comparisons. "
                 'Ownership-matched intervention and path specificity are not established by this calibration.', '']
    else:
        text += ['The development value-transfer assay is queued or running. No causal result is claimed.', '']
    text += ['## Reserved structural data', '',
             '| Cohort | Bases | Renderings | Independent Python checks | Dataset SHA-256 |',
             '|---|---:|---:|---:|---|']
    for axis in ('depth','distance','competition','combined'):
        path = DATA/f'extrapolation_{axis}_full.manifest.json'
        if not path.exists():
            continue
        manifest = read(path)
        validation = read(path.with_name(path.name.replace('.manifest.', '.validation.')))
        if validation['status'] != 'passed':
            raise ValueError('reserved dataset did not pass validation')
        evidence['datasets'].append({'cohort':axis,'manifest':str(path.relative_to(ROOT)),
                                    'sha256':manifest['sha256'],'validation':validation})
        text.append(f"| {axis} | {manifest['base_instances']} | {manifest['rows']} | "
                    f"{validation['independent_python_programs']} | `{manifest['sha256']}` |")
    text += ['', 'All these cohorts are test-only. Generator version 6 checks actual primary and control skeletons against '
             'the discovery dataset, verifies independent Python traces and downstream counterfactual states, and rejects '
             'cross-base duplicate numeric ASTs. Their model outcomes remain unopened. Increased competition uses six variables; '
             'distance padding adds arithmetic identities and is not a pure timing manipulation. The smaller structural smoke '
             'fixtures are separate from the full cohorts. No new-family extrapolation has been implemented yet.', '']
    for label,directory in (('CPU BF16','interface_cpu_prefill_v2'),('CPU FP32','interface_cpu_fp32_prefill_v2'),
                            ('GPU BF16','interface_gpu_prefill_v2')):
        diagnostic=DATA/directory/'interface_diagnostics/responses.json'
        if not diagnostic.exists():
            continue
        interface=read(diagnostic)
        evidence.setdefault('interface_diagnostics',{})[label]=interface
        text += [f'## Arithmetic and interface calibration: {label}', '',
                 'Eight fixed primitive programs and four training programs selected by ID use the same checkpoint and prompt. '
                 'Expected values are independently checked in Python. Single-example and padded-batch generation are compared; '
                 'no heldout outcomes are read.', '',
                 '| Batch size | Primitive correct / 8 | Training correct / 4 |', '|---:|---:|---:|']
        for batch in sorted(interface.get('primitive_correct_by_batch',{})):
            text.append(f"| {batch} | {interface['primitive_correct_by_batch'][batch]} | {interface['training_correct_by_batch'][batch]} |")
        if interface.get('complete'):
            text += ['',f"Exact response agreement across batch sizes: {interface['batch_exact_response_matches']}/{interface['cases']}. "
                     'Primitive success does not establish competence on the complete task; batch differences require inspection '
                     'before assigning errors to a mechanism.','']
    comparison_path=DATA/'backend_comparison.json'
    if comparison_path.exists():
        comparison=read(comparison_path)
        for inputs in comparison['inputs'].values():
            for record in inputs.values():
                if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']:
                    raise ValueError('backend comparison input changed; refuse stale report')
        evidence['backend_comparison']={'artifact':str(comparison_path.relative_to(ROOT)),**comparison}
        text += ['## Matched backend comparison','',
                 'The comparison verifies identical case IDs, source, oracle answers, unpadded input tokens, checkpoint, '
                 'tokenizer, generation cap and inference source files. Scores are recomputed from raw responses. '
                 'Only batch size, device and precision vary in the comparisons shown. Other captured source files '
                 'and host environments can differ; this is not a controlled hardware benchmark.', '',
                 '| Left run / batch | Right run / batch | Exact raw matches / n | Parsed matches / n |',
                 '|---|---|---:|---:|']
        for row in comparison['comparisons']:
            text.append(f"| {row['left']} / {row['left_batch']} | {row['right']} / {row['right_batch']} | "
                        f"{row['raw_matches']}/{row['n']} | {row['prediction_matches']}/{row['n']} |")
        shared=set.intersection(*(set(row['shared_primitive_failures']) for row in comparison['comparisons']))
        text += ['', 'Primitive fixtures incorrect in every compared run and batch: '+', '.join(f'`{name}`' for name in sorted(shared))+'.', '',
                 'The observed primitive failures are not confined to CPU inference or BF16. Batch-sensitive longer answers '
                 'remain visible in the artifact; deterministic greedy outputs are not independent replications. '
                 'Agreement cannot rule out a shared adapter problem or identify a binding mechanism.', '']
        gpu=comparison['runs'].get('GPU BF16',{})
        if gpu.get('gpu_peak_bytes'):
            text += [f"GPU device: {gpu['device_name']}; peak allocated tensor memory: "
                     f"{gpu['gpu_peak_bytes']/2**30:.2f} GiB. This excludes non-tensor device allocations.", '']
    reference_path=DATA/'gpu_generation_reference/generation_reference/summary.json'
    if reference_path.exists():
        reference=read(reference_path)
        evidence['generation_reference']={'artifact':str(reference_path.relative_to(ROOT)),**reference}
        if reference['complete']:
            text += ['## Independent generation reference','',
                     'The same training-only prompts are decoded by direct full-prefix forward passes with '
                     '`use_cache=False` and raw-logit argmax, without `model.generate` or the production generation wrapper. '
                     'EOS and blank-line boundaries are explicit; every chosen token and top-two logit margin is saved.', '',
                     f"Exact raw response matches with the earlier GPU batch-one run: {reference['raw_matches']}/{len(reference['results'])}; "
                     f"parsed matches: {reference['prediction_matches']}/{len(reference['results'])}. "
                     'This is an implementation sensitivity check on the same checkpoint and prompts, not a new accuracy cohort.', '',
                     '| Case | Expected | Cached baseline | Uncached reference | Stop |', '|---|---:|---|---|---|']
            for row in reference['results']:
                base='invalid' if row['baseline_prediction'] is None else row['baseline_prediction']
                prediction=row['reference']['prediction']
                prediction='invalid' if prediction is None else prediction
                text.append(f"| `{row['id']}` | {row['expected_answer']} | {base} | {prediction} | {row['reference']['stop_reason']} |")
            text += ['', 'Matching primitive failures across these paths narrow the implementation checks; '
                     'they cannot validate the shared tokenizer, checkpoint or prompt interpretation. '
                     'Any longer-program differences remain a cache/backend sensitivity and require inspection before causal claims.', '']
    stop=DATA/'gpu_floor_stop.json'
    if stop.exists():
        evidence['gpu_floor_stop']=read(stop)
    calibration_summaries=[DATA/'protocol_calibration_fp32/protocol_calibration/summary.json',
                           DATA/'protocol_calibration_long_fp32/protocol_calibration/summary.json']
    for directory in ('protocol_training_bank','protocol_training_bank_long'):
        calibration_summaries+=sorted((DATA/directory).glob('*/protocol_calibration/summary.json'))
    available=[path for path in calibration_summaries if path.exists()]
    if available:
        text += ['## Training-only prompt calibration', '',
                 'The print readout wraps only the final expression. Direct-output and explicitly reasoned protocols are distinct '
                 'experiments and are not pooled with each other or with the original behavior cohort. '
                 'Only fixed primitive cases, existing training cases and the separate training-only calibration bank are eligible.', '',
                 '| Cohort | Variant | Responses | Primitive correct / n | Other training correct / n | Invalid |',
                 '|---|---|---:|---|---|---:|']
        evidence['protocol_calibration']=[]
        for path in available:
            summary=read(path)
            evidence['protocol_calibration'].append({'artifact':str(path.relative_to(ROOT)),**summary})
            cohort='fixed suite' if path.parent.parent.name.startswith('protocol_calibration') else 'fresh training bank'
            for row in summary['variants']:
                text.append(f"| {cohort} | {row['variant']} | {row['n']} | "
                            f"{row['primitive_correct']}/{row['primitive_n']} | {row['training_correct']}/{row['training_n']} | {row['invalid']} |")
            text += ['']
        text += ['Passing the predeclared small-suite gate only permits a fresh training-bank check. '
                 'It does not establish a binding mechanism or qualify final-test evaluation. '
                 'Reasoning changes the computation; original prefix probes and interventions do not transfer automatically.', '']
        figure=calibration_figure()
        if figure:
            evidence['calibration_figure']=figure
            text += ['![Readout calibration with the same underlying training programs](calibration_readouts.png)', '',
                     'Cell text is the parsed integer; invalid output is shown separately. '
                     'Token budgets and the use of explicit reasoning differ as labeled, so these are separate protocol measurements.', '']
    decision=DATA/'protocol_training_bank/pipeline_decision.json'
    if decision.exists():
        evidence['calibration_pipeline_decision']=read(decision)
    decision_long=DATA/'protocol_training_bank_long/pipeline_decision.json'
    if decision_long.exists():
        evidence['long_calibration_pipeline_decision']=read(decision_long)
    ladder_path=DATA/'difficulty_ladder_bf16/protocol_calibration/ladder_decision.json'
    if ladder_path.exists():
        ladder=read(ladder_path)
        manifest=read(ladder_path.with_name('manifest.json'))
        response_path=ladder_path.with_name('responses.jsonl')
        if (manifest['identity_hash']!=digest(manifest['identity'])
                or ladder['identity_hash']!=manifest['identity_hash']
                or (hashlib.sha256(response_path.read_bytes()).hexdigest() if response_path.exists() else None)!=ladder['responses_sha256']):
            raise ValueError('difficulty ladder evidence identity changed')
        evidence['difficulty_ladder']={'artifact':str(ladder_path.relative_to(ROOT)),**ladder}
        text += ['## Fresh training difficulty ladder','',
                 'The [fixed plan](difficulty_ladder_plan.md) declares a new training-only calibration with both existing readouts. '
                 'Within a depth, all three styles share assignment-result values, operation counts and answers. '
                 'The independent-arithmetic control substitutes preceding values as literals, altering surface cues and functional dependencies. '
                 'Twelve answer targets repeat across depths; these are not independent confirmatory programs. '
                 'GPU BF16 results remain separate from earlier CPU FP32 prompt calibration.', '',
                 f"Decision: `{ladder['status']}`; completed queries {ladder['queries_completed']}/{ladder['queries_planned']}.", '',
                 '| Protocol | Style | Assignments | Correct / n | Invalid | Negative correct / n | Zero correct / n | Positive correct / n |',
                 '|---|---|---:|---:|---:|---:|---:|---:|']
        for row in ladder['cells']:
            signs=[f"{row['by_sign'][str(s)]['correct']}/{row['by_sign'][str(s)]['n']}" for s in (-1,0,1)]
            text.append(f"| {row['variant']} | {row['style']} | {row['assignment_count']} | {row['correct']}/{row['n']} | "
                        f"{row['invalid']} | "+' | '.join(signs)+' |')
        if ladder['selected']:
            selected=ladder['selected']
            text += ['', f"The fixed rule selects `{selected['variant']}` at {selected['assignment_count']} assignments "
                     'for fresh discovery design only. This is not evidence of a binding mechanism or permission to open final model outcomes.', '']
        elif ladder['complete']:
            text += ['', 'No regime passes the fixed arithmetic, parsing and nondegenerate chain-accuracy gate. '
                     'The declared stopping rule ends this checkpoint/protocol feasibility pilot; no further prompt search or '
                     'automatic intervention expansion follows.', '']
        figure=ladder_figure(ladder)
        if figure:
            evidence['difficulty_ladder_figure']=figure
            text += ['![Training difficulty ladder](difficulty_ladder.png)', '',
                     'The one-assignment baseline is shared across curves. Invalid outputs count as incorrect in exact accuracy '
                     'and appear separately in the lower panels. No population confidence intervals are inferred from these training cells.', '']
    stopped=evidence.get('difficulty_ladder',{}).get('status')=='stop_no_usable_regime'
    next_action=('The fixed training difficulty ladder also failed its predeclared gate. End this checkpoint/protocol '
                 'feasibility pilot and preserve the result. A new scientific plan is needed for further model experiments. '
                 if stopped else
                 'Establish a usable arithmetic/interface calibration before scaling behavior or launching ownership/path-specific follow-ups. ')
    text += ['## Decision and remaining work', '',
             'The larger behavioral cohort is near floor, so full GPU expansion was stopped before allocation. '+next_action+
             'Current results do not justify a binding-repair or binding-interference claim. Probe generalization remains weak '
             'despite greater numeric diversity. A supported hypothesis, frozen predictor fitting and unfamiliar-program forecasts '
             'are still required before opening final model outcomes. No optional training, second checkpoint or empirical paper '
             'abstract has been started.', '',
             'Queued-job identities and immutable source pointers are recorded in the adjacent handoff and artifact manifests. '
             'The earlier four-hour ledger is historical. Current model work has no project compute cap; CPU and GPU results remain separately labeled.', '']
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    program=DATA/'phase2/program_status.json'
    if program.exists():
        current=read(program)
        evidence['authorized_experiment_program']={'report':'reports/binding/experiment_program.md',
                 'manifest':'artifacts/binding/phase2/program_status.json',
                 'stages':[{k:r[k] for k in ('id','name','status')} for r in current['experiments']],
                 'diagnostics_complete':current['diagnostics_complete']}
        text += ['## Later authorized experiment program','',
                 'The user subsequently authorized a [ten-experiment follow-up](experiment_program.md). '
                 'It audits the cached checkpoint, corrects an instruction-marker tokenization mismatch and runs fresh arithmetic '
                 'and arithmetic-free diagnostics. That correction restores reference input IDs; it does not resolve the observed '
                 'primitive failure. These new results remain separate from the native-tokenization pilot above. '
                 'See the linked stage table for completed and unexecuted experiments.','']
    REPORT.write_text('\n'.join(text))
    handoff(evidence)
    write_json(DATA/'phase2_evidence.json', evidence)
    if evidence.get('behavior'):
        recorded=read(ROOT/evidence['behavior']['manifest'])
        model_config=recorded['identity']['config']
        ledger=DATA/'gpu_budget.json'
        write_json(DATA/'model_manifest.json',{
            'status':('Checkpoint/protocol feasibility pilot stopped after fixed difficulty-ladder gate failed' if stopped else
                      'CPU discovery completed; full GPU expansion stopped pending arithmetic/interface calibration'),
            'hf_id':model_config['model'],'model_revision':model_config['model_revision'],
            'tokenizer_revision':model_config['tokenizer_revision'],'dtype':model_config['dtype'],
            'protocol':model_config['protocol'],'backend':'transformers/eager','cache_only':True,
            'behavior_identity_hash':recorded['identity_hash'],'behavior_manifest':evidence['behavior']['manifest'],
            'resource_snapshot_utc':evidence['generated_utc'],
            'gpu_used_seconds_at_snapshot':read(ledger)['used_seconds'] if ledger.exists() else 0,
            'gpu_cap_seconds':None,'activation_cap_bytes':68719476736,
            'checkpoint_training_performed':False,'additional_checkpoint_downloaded':False,
            'live_evidence_manifest':'artifacts/binding/phase2_evidence.json'})
    print(json.dumps({'report':str(REPORT), 'evidence':str(DATA/'phase2_evidence.json')},indent=2))


if __name__ == '__main__':
    main()
