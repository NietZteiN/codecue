"""Generate the decision and handoff from audited outputs, never model queries."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src'))
from codecue.binding.datasets import write_json
from codecue.binding.experiment_status import query_scheduler
from codecue.binding.published_benchmarks import immutable,sha


def main():
    folder=ROOT/'artifacts/binding/arithmetic_readout'
    result=json.loads((folder/'comparison_v1.json').read_text())
    assert result['status']=='passed' and result['complete'] and result['total_predictions']==12288
    jobs=json.loads((folder/'jobs_v1.json').read_text())
    accounting,errors=query_scheduler(list(jobs.values()))
    assert not errors and all(accounting[jid]['state']=='COMPLETED' for jid in jobs.values())
    models=('llama31_8b','codellama34b');variants=('print_direct_v3','print_trace_long_v1')
    labels={'llama31_8b':'Llama 3.1 8B','codellama34b':'CodeLlama 34B'}
    lines=['# Arithmetic/readout discovery decision','',
        f"Both cached checkpoints completed and passed all artifact audits: **{result['total_predictions']:,} scored responses** from 3,072 independently checked sources, 384 numeric tuples and 192 mirrored numeric groups. All four fixed model/protocol reliability gates failed. Completed execution is separate from scientific qualification.",'',
        'The source/configuration/dataset were frozen before model responses. Training calibration and numeric development have distinct nonzero-operation prompts, with every sign-reversed relative grouped. The two answer-copy controls repeat exact prompts and are excluded from qualification. Numeric development shares the same eight task structures; it is not a structural holdout.','',
        '## Complete protocol summaries','',
        '| Checkpoint | Protocol | Correct / n | Invalid | Training qualified | Numeric development qualified |',
        '|---|---|---:|---:|---|---|']
    for name in models:
        review=result['models'][name]
        assert review['status']=='complete_audited' and review['complete']
        for cell in review['protocol_cells']:
            gate=review['reliability_gate']['protocols'][cell['variant']]
            lines.append(f"| {labels[name]} | {cell['variant']} | {cell['correct']}/{cell['n']} | {cell['invalid']} | {gate['training_qualified']} | {gate['numeric_development_qualified']} |")
    forms=('literal_output','stored_output','literal_one','bound_one','stored_result_one','literal_three','bound_three','stored_intermediates_three')
    lines+=['','## All numeric-development forms','',
        '| Form | Llama direct | Llama trace | CodeLlama direct | CodeLlama trace |',
        '|---|---:|---:|---:|---:|']
    for form in forms:
        cells=[]
        for name in models:
            for variant in variants:
                cell=next(c for c in result['models'][name]['form_cells'] if c['form']==form and c['variant']==variant and c['split']=='development')
                cells.append(f"{cell['correct']}/{cell['n']}")
        lines.append('| '+form+' | '+' | '.join(cells)+' |')
    lines+=['','![Development form accuracy](arithmetic_readout_results_v1.svg)','',
        '## Interpretation and next decision','',
        'Arithmetic composition and source/readout form both matter in this cohort. Direct-answer three-operation forms are substantially weaker than their folded one-operation counterparts. Trace prompting improves several three-operation forms, while its effects on one-operation forms depend on storage and checkpoint. A universal operation-count explanation is therefore insufficient. These observations do not identify an internal cause or a binding-specific mechanism.','',
        'The full six-sign-stratum matrices and every registered paired contrast, including null and reversed effects, remain in the [combined report](arithmetic_readout_results_v1.md) and individual reports. Bootstrap groups preserve numeric sign relatives; intervals are exploratory and unadjusted for multiplicity. Operand range, intermediate literal exposure, assignment count, source length and reasoning access differ across the declared factors.','',
        'The all-cell training-then-development rule remains in force: no favorable form/sign subset or alternate protocol rescues a failed gate. Any narrower arithmetic regime or equivalent-rendering diagnostic requires its own prospective design and fresh validation. The current result does not authorize computed causal interventions, optional checkpoint training, a mechanism C predictor or final-test evaluation. Original failed gates and final/extrapolation outcomes remain unchanged.','',
        'The [prior two-operation context](arithmetic_readout_prior_context.md) separately reproduces 768 already observed scores. Its different numeric bank and partly dead first operations prevent a clean two-versus-three-operation causal comparison.','',
        '## Software and resources','',
        'The arithmetic source passed 322 full regression tests. The subsequent forecasting-access maintenance passed 44 fitting/measurement checks. It rejects declared reserved paths/roles and dataset/checkpoint mismatches before reading response outcomes; untyped legacy response IDs still require strict checks after parsing. This maintenance fits no empirical forecaster and uses a separate frozen source pointer.','',
        '| Checkpoint | Allocated seconds | Engine load/warmup seconds | Generation seconds | Generation requests/s | Mean generation GPU utilization |',
        '|---|---:|---:|---:|---:|---:|']
    resources={}
    for name in models:
        stage=folder/(name+'_v1')/'checkpoint_suite'
        summary=json.loads((stage/'summary.json').read_text());runtime=json.loads((stage/'runtime.json').read_text())
        seconds=sum(t['generation_seconds'] for t in summary['timings'])
        entry={'allocated_seconds':accounting[jobs['run_'+name]]['elapsed_seconds'],
               'engine_load_warmup_seconds':runtime['load_warmup_seconds'],
               'generation_seconds':seconds,'generation_requests_per_second':summary['evaluated']/seconds,
               'mean_generation_gpu_utilization_percent':summary['gpu']['mean_gpu_utilization_percent']}
        resources[name]=entry
        lines.append(f"| {labels[name]} | {entry['allocated_seconds']} | {entry['engine_load_warmup_seconds']:.2f} | {seconds:.2f} | {entry['generation_requests_per_second']:.1f} | {entry['mean_generation_gpu_utilization_percent']:.2f}% |")
    lines+=['','Both runs used H200s, BF16 and one continuously batched engine for the complete direct and trace cohorts. Generation rates/utilization exclude model loading and process startup; allocated seconds include them. Usage accounting is uncapped. No large checkpoint download or language-model training occurred.','',
        '[Plan](arithmetic_readout_plan.md) · [Completed status](arithmetic_readout_status_v1.md) · [Automatic experiment log](experiment_log.md)','']
    report=ROOT/'reports/binding/arithmetic_readout_decision.md'
    immutable(report,'\n'.join(lines).encode())
    tests={}
    for filename in ('regression_v1.xml','forecasting_access_tests_v1.xml'):
        suites=list(ET.parse(folder/filename).getroot().iter('testsuite'))
        tests[filename]={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
    handoff={'status':'complete_audited','total_predictions':result['total_predictions'],
        'reliability':{name:{variant:result['models'][name]['reliability_gate']['protocols'][variant]['status'] for variant in variants} for name in models},
        'jobs':jobs,'scheduler_accounting':accounting,'resources':resources,'tests':tests,
        'source':json.loads((folder/'source_v1.json').read_text()),
        'forecasting_maintenance_source':json.loads((folder/'forecasting_access_source_v1.json').read_text()),
        'comparison_sha256':sha(folder/'comparison_v1.json'),'decision':str(report),'decision_sha256':sha(report),
        'summary_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'generated_holdouts_opened':False,'language_model_training':False,'empirical_forecasters_fitted':False}
    write_json(folder/'handoff_review_v1.json',handoff)
    print(json.dumps({'status':handoff['status'],'total_predictions':handoff['total_predictions'],'reliability':handoff['reliability'],'tests':tests,'report':str(report)},indent=2))


if __name__=='__main__':main()
