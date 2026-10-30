"""Evidence-linked execution status for the user-authorized ten-experiment program."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
from .datasets import digest,write_json


def figure(decisions,target):
    if not all(r is not None and r['complete'] for r in decisions.values()):return None
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    import numpy as np
    variants=('print_direct_v3','print_trace_long_v1')
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    arithmetic=decisions['arithmetic_forms']['cells'];binding=decisions['arithmetic_free']['cells']
    for col,variant in enumerate(variants):
        top=axes[0,col];forms=('expression','assignment','independent','dependent');x=np.arange(4)
        for offset,split,color in ((-.18,'train','#2364aa'),(.18,'development','#b87515')):
            cells=[next(r for r in arithmetic if r['variant']==variant and r['split']==split and r['family']==family) for family in forms]
            top.bar(x+offset,[r['correct']/r['n'] for r in cells],width=.34,color=color,label='Training' if split=='train' else 'Fresh numeric validation')
        top.set_xticks(x,forms,rotation=15);top.set_title('Print direct · 16 tokens' if col==0 else 'Print trace · 512 tokens')
        bottom=axes[1,col]
        for family,color in (('copy_depth','#2364aa'),('overwrite_count','#b87515')):
            for split,style in (('train',':'),('development','-')):
                cells=[next(r for r in binding if r['variant']==variant and r['split']==split and r['family']==family and r['depth']==depth) for depth in (1,2,4,8)]
                bottom.plot((1,2,4,8),[r['correct']/r['n'] for r in cells],marker='o',linestyle=style,color=color,
                            label=family.replace('_',' ')+' · '+('training' if split=='train' else 'validation'))
        bottom.set_xticks((1,2,4,8));bottom.set_xlabel('Copy depth or overwrite count')
        for axis in axes[:,col]:
            axis.set_ylim(0,1.04);axis.yaxis.set_major_formatter(PercentFormatter(1));axis.grid(axis='y',alpha=.2)
        bottom.legend(fontsize=8,loc='lower left')
    axes[0,0].set_ylabel('Arithmetic-form exact accuracy');axes[1,0].set_ylabel('Arithmetic-free exact accuracy')
    axes[0,0].legend(fontsize=8)
    fig.suptitle('Reference-tokenized CodeLlama diagnostics\n24 programs per cell; repeated structures are calibration data')
    path=target.with_name('experiment_program.png')
    for suffix in ('png','svg'):fig.savefig(path.with_suffix('.'+suffix),dpi=170)
    plt.close(fig)
    return str(path)


def load_verified_decision(path):
    path=Path(path)
    if not path.exists():return None
    decision=json.loads(path.read_text());manifest=json.loads(path.with_name('manifest.json').read_text())
    if (manifest['identity_hash']!=digest(manifest['identity']) or decision['identity_hash']!=manifest['identity_hash']):
        raise ValueError('program diagnostic provenance mismatch')
    response=path.with_name('responses.jsonl')
    if hashlib.sha256(response.read_bytes()).hexdigest()!=decision['responses_sha256']:
        raise ValueError('program diagnostic responses changed')
    dataset=Path(manifest['identity']['config']['dataset'])
    if hashlib.sha256(dataset.read_bytes()).hexdigest()!=manifest['identity']['dataset_manifest']['sha256']:
        raise ValueError('program diagnostic dataset changed')
    return decision


def status(config):
    root=Path(config.get('artifact_root','artifacts/binding/phase2'))
    plan_path=Path(config['plan']);plan=json.loads(plan_path.read_text())
    audit=json.loads((root/'checkpoint_audit.json').read_text()) if (root/'checkpoint_audit.json').exists() else None
    boundary=json.loads((root/'tokenizer_boundary_audit.json').read_text()) if (root/'tokenizer_boundary_audit.json').exists() else None
    paired=json.loads((root/'boundary_validation/comparison.json').read_text()) if (root/'boundary_validation/comparison.json').exists() else None
    audit_ok=(audit is not None and all(r['match'] for r in audit['files']) and boundary is not None and boundary['status']=='passed')
    decisions={name:load_verified_decision(root/name/'protocol_calibration/diagnostic_decision.json')
               for name in ('arithmetic_forms','arithmetic_free')}
    token_path=root/'all_prompt_token_audit.json'
    token_audit=json.loads(token_path.read_text()) if token_path.exists() else None
    token_ok=token_audit is not None and token_audit['status']=='passed' and token_audit['n']==1152
    if token_ok:
        for file,expected in token_audit['input_hashes'].items():
            if hashlib.sha256(Path(file).read_bytes()).hexdigest()!=expected:
                raise ValueError('full reference-token audit is stale')
    candidate=next(({'task':name,'protocol':r['selected_protocol'],'identity_hash':r['identity_hash']}
                for name,r in decisions.items() if r is not None and r['status']=='validated_for_discovery'),None)
    ready=candidate if token_ok and audit_ok else None
    done=all(r is not None and r['complete'] for r in decisions.values())
    stages=[]
    for experiment in plan['experiments']:
        identifier=experiment['id'];entry=dict(experiment)
        if identifier==1:
            entry['status']='completed_with_boundary_correction' if audit_ok and paired else 'audit_incomplete_or_failed'
            entry['interpretation']='Artifact integrity passed; native token boundary disagreed with reference and an explicit correction was verified. Paired behavior measures its limited empirical effect.'
        elif identifier in (2,3):
            key='arithmetic_forms' if identifier==2 else 'arithmetic_free';result=decisions[key]
            entry['status']='completed' if result is not None and result['complete'] else 'pending_or_running'
            entry['decision']=result
        else:
            entry['status']=('waiting_for_reference_token_audit' if candidate and not token_ok else
                             'ready_for_frozen_discovery_design' if ready and identifier==4 else
                             'waiting_for_upstream_experiment' if ready or not done else
                             'not_run_failed_behavioral_prerequisite')
            if done and candidate is None:
                entry['reason']='Neither diagnostic produced a protocol meeting the predeclared training and fresh-validation arithmetic/binding gate.'
            if identifier==9:entry['registration']='No empirical explanatory registration or C features have been invented.'
            if identifier==10:entry['replication_scope']='The user authorized a second family; execution still requires an observed effect and a reserved global allowance.'
        stages.append(entry)
    result=dict(generated_utc=datetime.now(timezone.utc).isoformat(),plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),
                experiments=stages,discovery_candidate=ready,diagnostics_complete=done,
                full_reference_token_audit=token_audit,heldout_outcomes_opened=False,
                prior_pilot='Preserved separately; this program follows the user request to execute the proposed experiments.')
    ledger=Path(plan['resources']['primary_ledger'])
    if ledger.exists():
        budget=json.loads(ledger.read_text())
        result['resources']={k:budget[k] for k in ('used_seconds','cap_seconds','active')}
    review_path=root/'diagnostic_review.json'
    if review_path.exists():
        review=json.loads(review_path.read_text())
        for file,expected in review['inputs'].items():
            if hashlib.sha256(Path(file).read_bytes()).hexdigest()!=expected:
                raise ValueError('diagnostic review inputs changed')
        result['posthoc_review']={'artifact':str(review_path),'report':'reports/binding/diagnostic_review.md',
                                 'distractor_confound':review['distractor_design']['confounded']}
    prepared_path=root/'counterbalanced_followup.manifest.json'
    if prepared_path.exists():
        prepared=json.loads(prepared_path.read_text())
        if (prepared['evaluation_role']!='counterbalanced_followup_only' or prepared['model_inference_performed']
                or hashlib.sha256(prepared_path.with_name('counterbalanced_followup.jsonl').read_bytes()).hexdigest()!=prepared['sha256']):
            raise ValueError('prepared counterbalanced dataset provenance differs')
        result['prepared_counterbalanced_data']=prepared
    write_json(root/'program_status.json',result)
    text=['# Authorized experiment program','',f"Generated {result['generated_utc']}.", '',
          'The user authorized all ten proposed experiments. Scientific prerequisites determine which model runs are eligible. '
          'The earlier pilot is retained separately. The new checkpoint audit verifies public artifact hashes and discovers a tokenizer boundary discrepancy; '
          'the explicit correction is independently checked against raw SentencePiece. Its effect is measured on paired same-GPU runs.', '',
          '| Experiment | State |', '|---|---|']
    text += [f"| {r['id']}. {r['name']} | `{r['status']}` |" for r in stages]
    text += ['', '## New behavioral diagnostics','',
             'Protocol selection uses only training elementary cells at at least 90% exact accuracy and at most 5% invalid outputs, '
             'with at least 24 examples per cell. The chosen protocol must independently pass fresh numeric validation. '
             'No fallback is allowed after validation failure. These numeric sets share task structures and are not confirmatory structural tests.', '']
    for name,decision in decisions.items():
        if decision is None:continue
        text += [f'### {name}', '',f"Decision: `{decision['status']}`. Queries: {decision['queries_completed']}/{decision['queries_planned']}.", '',
                 '| Protocol | Split | Family | Depth | Correct / n | Invalid |', '|---|---|---|---:|---:|---:|']
        text += [f"| {r['variant']} | {r['split']} | {r['family']} | {r['depth'] or '—'} | {r['correct']}/{r['n']} | {r['invalid']} |" for r in decision['cells']]
        text += ['']
    text += ['## Resources and deferred work','',
             'All model weights are existing local checkpoints. The user removed project compute and checkpoint limits; '
             'new work uses the uncapped usage ledger, while earlier resource records remain historical. '
             'Final outcomes remain sealed until a genuine registration and frozen forecasts exist. '
             'No language-model training or unlearning is included.', '',
             'The machine-readable plan is `configs/binding/phase2/program_plan.json`; current evidence and decisions are in '
             '`artifacts/binding/phase2/program_status.json`. Exact stage configurations and source/job pointers are retained.', '']
    if result.get('posthoc_review'):
        text+=['## Review and unqueried follow-up data','',
               'The [post-hoc diagnostic review](diagnostic_review.md) reports paired readout/form counts and identifies '
               'a confound: trailing distractors in the consumed binding dataset are tied to nonzero answer magnitude. '
               'Those data cannot isolate a trailing-distractor effect. The earlier gate and cell accuracies remain unchanged.','']
    if result.get('prepared_counterbalanced_data'):
        prepared=result['prepared_counterbalanced_data']
        text += [f"Prepared {prepared['paired_programs']} fresh numeric matched pairs ({prepared['rows']} programs), "
                 f"with {prepared['independent_python_programs']} independent Python trace checks. "
                 'Each pair shares its assignment prefix and answer, differing by one irrelevant trailing copy. '
                 'Both levels occur at every answer magnitude. These repeated structures are future calibration candidates; '
                 'no model inference or confirmatory evaluation has run on them.','']
    target=Path(config.get('report','reports/binding/experiment_program.md'));target.parent.mkdir(parents=True,exist_ok=True)
    plotted=figure(decisions,target)
    if plotted:
        text+=['![Fresh reference-tokenized diagnostics](experiment_program.png)','',
               'Invalid outputs count as incorrect and remain separately tabulated. Training and fresh numeric validation share task structures; '
               'these plots do not establish independent structural generalization or a causal mechanism.','']
    if result.get('resources'):
        resources=result['resources']
        text += [f"Completed model-stage ledger time: {resources['used_seconds']:.2f}/{resources['cap_seconds']} seconds; "
                 f"active reservations: {len(resources['active'])}. SLURM allocated elapsed time includes additional batch startup.",'']
    target.write_text('\n'.join(text))
    return {'report':str(target),'discovery_candidate':ready,'diagnostics_complete':done}
