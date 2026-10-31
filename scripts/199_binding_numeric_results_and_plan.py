#!/usr/bin/env python
"""Publish a pinned results snapshot and a non-launchable next-run plan."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
RUN = Path('artifacts/binding/arithmetic_numeric_exploration/20261031_v1')
OUT = Path('artifacts/binding/arithmetic_next_runs/20261031_v1')
PLAN = Path('reports/binding/arithmetic_next_runs_20261031_plan_v1.md')


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest())


def read(entry):
    if pin(Path(entry['path']))['sha256'] != entry['sha256']:
        raise ValueError('planning input checksum differs')
    return json.loads((ROOT/entry['path']).read_text())


def scores(data, width, encoding):
    banks = [b for b in data['fits'] if b['width'] == width and encoding in b['selected_formats']]
    if sorted(b['seed'] for b in banks) != [11, 29, 47]: raise ValueError('three selected seeds required')
    return {key: {metric: mean(b['development'][key][encoding][metric] for b in banks)
        for metric in b0 if isinstance(b0[metric], (int, float))}
        for key in ['real', 'control', 'prior'] for b0 in [banks[0]['development'][key][encoding]]}


def publish(path, value):
    target = ROOT/path
    if target.exists(): raise ValueError('preserve existing planning edition: '+str(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')


def main():
    output = Path('reports/binding/arithmetic_results_for_next_runs_v1.md')
    cfg = Path('configs/binding/arithmetic_next_runs_20261031_v1.json')
    if any((ROOT/p).exists() for p in [OUT, output, cfg]): raise ValueError('existing plan outputs must be preserved')
    audit_entry = pin(RUN/'postrun_audit/completion_review_v1.json'); audit = read(audit_entry)
    if audit['status'] != 'passed': raise ValueError('audited completed inputs required')
    data, inputs = {}, dict(audit=audit_entry, prospective_plan=pin(PLAN))
    for worker in audit['workers']:
        config = read(worker['config']); result = read(worker['results'])
        key = Path(worker['config']['path']).stem
        data[key] = result; inputs[key] = worker['results']
    summary, models = {}, []
    for alias, label in [('llama8b', 'Llama 8B'), ('codellama34b', 'CodeLlama 34B')]:
        computed, roots = data[alias+'_computed_definition'], data[alias+'_root_definition']
        width = computed['widths'][-1]
        summary[alias] = dict(label=label, full_width=width,
            categorical64=scores(computed, 64, 'categorical'), categorical_full=scores(computed, width, 'categorical'),
            scalar64=scores(computed, 64, 'scalar'), scalar_full=scores(computed, width, 'scalar'),
            digits_full=scores(computed, width, 'digits_joint'), root_full=scores(roots, width, 'categorical'),
            components={name:scores(computed, width, name) for name in ['sign','magnitude','units','tens','parity','mod5','mod10']})
        profile_path = Path('configs/binding/arithmetic_graph_20261029_v3')/(alias+'_capture.json')
        profile = read(pin(profile_path))
        models.append(dict(alias=alias, profile=pin(profile_path), model=profile['model'], revision=profile['model_revision'],
            archived_layers=profile['layers'], primary_layer=24 if alias=='llama8b' else 36, width=width))
    stages = [
        dict(id='global_cached', depends_on=[], resource='CPU', question='All four values and 48 direct relations from one final state',
            data='existing inspected local cohort', hidden_widths='1024 and model full width', shared_source_widths=[1024,4096,8192],
            reuse='Existing 64-wide fixed-alpha scalar/relation banks are read-only historical references',
            cache_sites='actual answer point_count-1 at all archived layers; primary fits at fixed layer',
            feature_inputs='one hidden vector plus intercept; no candidate history or gold pointer',
            real_target_columns=824, cv_factorizations=189, maximum_selected_factorizations=63,
            new_model_queries=0),
        dict(id='paired_data', depends_on=[], resource='CPU', question='Separate arithmetic, binding and retention',
            target_train_components=96, target_dev_components=32, counts_validated=False,
            grouping='connected closure over canonical skeletons of every numeric/lexical/counterfactual relative',
            calibration='finite one-hop/literal skeletons excluded from fits; actual available counts determined before inference',
            numeric_generation_seeds=[20261101,20261102,20261103], delay_statements=[0,4,12],
            controls=['irrelevant write','operand mutation after computed assignment','same-bag binding twins','semantic-preserving renaming/root order']),
        dict(id='native_preflight', depends_on=['paired_data'], resource='CPU SLURM for tokenizers',
            checks=['independent oracles','counterfactual collisions','canonical split closure','native distinct sites','causal token prefixes','scratch write/capacity']),
        dict(id='calibration', depends_on=['native_preflight'], resource='GPU',
            checks=['parser','copying positive control','arithmetic competence','native layout','batch/memory profile'],
            rule='preserve pilot; freeze any protocol revision before formal cohort; no DEV-based wording choice'),
        dict(id='temporal_capture', depends_on=['calibration'], resource='GPU',
            sites=['RHS end','newline/delimiter if native-distinct','later use','pre-answer query'],
            protocols=['output-only','explicit intermediate query','model-generated stepwise'],
            query_scopes=['single requested variable','all four current variables'],
            primary='within-site full-width scalar/categorical', secondary='cross-site transfer and 1024-wide sensitivity',
            value_visibility='source/trace-visible targets separately flagged; no gold intermediate in main assay'),
        dict(id='behavior', depends_on=['calibration'], resource='GPU',
            multi_value_output='separately validated ordered four-value parser; per-slot/joint accuracy; emitted-value visibility flags',
            instruction_variants=3, retain=['all invalid/truncated responses','attempted/returned counts','same-instruction links to hidden states']),
        dict(id='analysis', depends_on=['global_cached','temporal_capture','behavior'], resource='CPU',
            outputs=['within-site/transfer curves','arithmetic versus overwrite versus delay contrasts','direct versus derived relations',
                'group-cross-fitted error prediction versus input difficulty and output uncertainty']),
        dict(id='confirmation', depends_on=['analysis'], resource='CPU/GPU',
            gate='freeze primary measurement and contrasts before new independent structural families',
            sample_size='chosen from meaningful effect and structural-family variance; not fitted-seed count'),
        dict(id='causal_gate', depends_on=['confirmation'], resource='not scheduled',
            gate='robust readouts, behavioral positive controls, functional counterfactuals and exact native donor layout')]
    plan = dict(status='planned_not_submitted', evaluation_role='planning_only_arithmetic_next_runs_v1',
        launchable=False, created_utc=datetime.now(timezone.utc).isoformat(), inputs=inputs, models=models,
        fitting_seeds=[11,29,47], folds=3, alphas=[1,100,10000], stages=stages,
        storage='large artifacts on verified scratch from outset; small metadata/logs on work; existing automatic logger',
        compute='finite scientific workloads; no cumulative project allowance; actual scheduler/hardware limits only',
        sealed_final_access=False, backbone_training=False, script=pin(Path(__file__).relative_to(ROOT)))
    lines=['# Results informing the next runs','',
        'Generated from the independently audited numeric sweep. Existing DEV remains discovery; three weighting seeds are sensitivity runs, not independent datasets. Arrows compare64-wide and full-width features within the same role-specific assay.','',
        '| Measurement | Llama 8B | CodeLlama 34B |','|---|---:|---:|']
    a,b=summary['llama8b'],summary['codellama34b']
    percent=lambda x:f'{100*x:.2f}%'
    lines += [f"| Literal categorical exact, full width | {percent(a['root_full']['real']['exact'])} | {percent(b['root_full']['real']['exact'])} |",
        f"| Computed categorical exact,64 → full | {percent(a['categorical64']['real']['exact'])} → {percent(a['categorical_full']['real']['exact'])} | {percent(b['categorical64']['real']['exact'])} → {percent(b['categorical_full']['real']['exact'])} |",
        f"| Computed scalar MAE,64 → full | {a['scalar64']['real']['mae']:.3f} → {a['scalar_full']['real']['mae']:.3f} | {b['scalar64']['real']['mae']:.3f} → {b['scalar_full']['real']['mae']:.3f} |",
        f"| Computed joint-digit exact, full width | {percent(a['digits_full']['real']['exact'])} | {percent(b['digits_full']['real']['exact'])} |",
        f"| Computed categorical TRAIN prior exact | {percent(a['categorical_full']['prior']['exact'])} | {percent(b['categorical_full']['prior']['exact'])} |",'',
        '| Computed-value component, full width: balanced accuracy | Llama 8B | CodeLlama 34B | TRAIN prior |','|---|---:|---:|---:|']
    for name in ['sign','magnitude','units','tens','parity','mod5','mod10']:
        x,y=a['components'][name],b['components'][name]
        lines.append(f"| {name} | {percent(x['real']['balanced_accuracy'])} | {percent(y['real']['balanced_accuracy'])} | {percent(x['prior']['balanced_accuracy'])} |")
    lines += ['', 'Wider features help, copying is strong, and coarse numeric properties are more accessible than precise computed values. Current exact-value accuracy remains low. Component balanced accuracy and whole-value exact accuracy measure different targets. These definition-level probes do not yet establish a shared all-variable state or natural causal use.', '',
        'The next priority is the [full-width global-state/direct-relation test, then timing and matched-mechanism runs](arithmetic_next_runs_20261031_plan_v1.md). No new experiment has been submitted by this planning step. The prior low-rank composed-state results remain a separate assay until updated global/pipeline measurements exist.', '',
        '[Audited review and figure](arithmetic_numeric_postrun_review_v1.md) · [Full panels](arithmetic_numeric_exploration_findings_v1.md).','']
    (ROOT/output).parent.mkdir(parents=True,exist_ok=True);(ROOT/output).write_text('\n'.join(lines))
    publish(cfg,plan)
    publish(OUT/'planning_review_v1.json',dict(status='planned_not_submitted',inputs=inputs,summary=summary,
        report=pin(output),plan=pin(PLAN),manifest=pin(cfg),script=plan['script'],new_fits=0,new_model_queries=0))
    print('Results snapshot and non-launchable next-run manifest generated; no new fits or jobs.')


if __name__=='__main__':main()
