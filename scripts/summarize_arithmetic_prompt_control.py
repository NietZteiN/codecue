#!/usr/bin/env python
"""Render checksum-verified matched prompt-control results without new inference."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from codecue.binding import arithmetic_prompt_control as control,relationship_capture as base

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/binding/arithmetic_prompt_control/20261030_v1'


def main():
    models={}
    for name in ['llama8b','codellama34b']:
        cfg=base._json(ROOT/f'configs/binding/arithmetic_prompt_control_20261030_v1/{name}.json')
        data=control.audit(cfg)
        models[name]=dict(metrics=data['metrics'],new_model_queries=data['new_model_queries'],
            generated_responses=data['generated_responses'],summary_sha256=base._sha(OUT/name/'summary.json'),source=data['source'])
    total=sum(m['generated_responses'] for m in models.values())
    if total!=11520:raise ValueError('complete five-new-arm cohorts required')
    report=dict(status='complete_exploratory',evaluation_role='discovery_arithmetic_prompt_control_findings_v1',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),models=models,
        new_model_queries=0,new_fits=0,source_generated_responses=total,cached_baseline_responses=2304,
        limitations='Adaptive discovery on reused families. Changed syntax and wording also change token context. Parser and original scores unchanged; no mechanism or untouched-confirmation claim.')
    text=['# Matched print/query semantics control: findings','',report['limitations'],'',
        f'{total:,} new generated responses and2,304 cached baseline responses cover two source forms × three instructions for both models. Original bare/I0 answers were not recollected.','',
        '| Model | Arm | Arithmetic DEV accuracy | Invalid | Literal DEV accuracy | Invalid |',
        '|---|---|---:|---:|---:|---:|']
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.4),constrained_layout=True)
    plt.rcParams['svg.fonttype']='none'
    for ax,(name,model) in zip(axes,models.items()):
        cells=model['metrics']['cells']
        for arm in control.ARMS:
            a=cells['development/arithmetic_written/'+arm];b=cells['development/untouched_literal/'+arm]
            text.append(f"| {name} | {arm} | {100*a['accuracy']:.2f}% | {100*a['invalid_fraction']:.2f}% | {100*b['accuracy']:.2f}% | {100*b['invalid_fraction']:.2f}% |")
        x=np.arange(2);width=.34
        for index,arm in enumerate(['bare_i0','print_i0']):
            values=[100*cells['development/'+kind+'/'+arm]['accuracy'] for kind in ['untouched_literal','arithmetic_written']]
            bars=ax.bar(x+(index-.5)*width,values,width,label=['Original bare query','Explicit print'][index],color=['#4b82b8','#c47845'][index])
            ax.bar_label(bars,fmt='%.1f',padding=3,fontsize=9)
        ax.set(title=name,ylabel='DEV answer accuracy (%)',ylim=(0,105))
        ax.set_xticks(x,['Untouched literal\n72 queries','Arithmetic-written\n216 queries']);ax.legend(frameon=False,fontsize=9)
    fig.suptitle('Explicit printing clarifies literal queries; arithmetic remains unreliable')
    figure=ROOT/'reports/binding/figures/arithmetic_prompt_control_v1.png'
    fig.savefig(figure,dpi=180);fig.savefig(figure.with_suffix('.svg'));plt.close(fig)
    text+=['','The figure uses the prospectively fixed original instruction I0. I1 and I2 are the two clarified instructions, all retained above. Printing raises untouched-literal accuracy substantially in I0 while leaving arithmetic-written accuracy low. Clear wording does not produce a reliable arithmetic regime; I2 also produces many invalid Llama responses. These are prompt-specific results, not evidence that the hidden representation lacks values or relationships.','',
        '| Model | DEV stratum | Paired contrast | Row difference (pp) | Family-macro difference (pp) | Conditional family95% interval (pp) | Families |',
        '|---|---|---|---:|---:|---|---:|']
    for name,model in models.items():
        for kind in ['arithmetic_written','untouched_literal']:
            key=kind+':print_i0_minus_bare_i0';v=model['metrics']['computed_literal'][key]
            lo,hi=v['conditional_family_bootstrap_95']
            text.append(f"| {name} | {kind} | print_i0 − bare_i0 | {100*v['row_weighted_difference']:.2f} | {100*v['family_macro_difference']:.2f} | [{100*lo:.2f}, {100*hi:.2f}] | {v['families']} |")
    text+=['','Each contrast pairs the exact same original case. Intervals resample whole families, conditional on these outcomes, with no refits or multiplicity correction. Arithmetic comparisons use12 families; literal comparisons use the9 families with untouched queried variables. All other predeclared contrasts are retained in the machine-readable summaries.','',
        'Decision: use explicit printed queries for the next discovery calibration, retain all wording results, and establish a reliable shorter arithmetic regime before causal patching. Preserve the original bare-query scores and the graph-readout TRAIN/DEV gap. This control diagnoses an interface effect on literal reporting; it does not rescue arithmetic performance.','',
        '[Original overnight findings](arithmetic_graph_overnight_findings_v1.md) · [Morning replay audit](arithmetic_graph_morning_review_v2.md) · [Control plan](arithmetic_prompt_control_plan_v1.md)','']
    path=ROOT/'reports/binding/arithmetic_prompt_control_findings_v1.md'
    path.write_text('\n'.join(text))
    report['outputs']={str(p.relative_to(ROOT)):base._sha(p) for p in [path,figure,figure.with_suffix('.svg')]}
    target=OUT/'findings_review_v1.json';payload=json.dumps(report,sort_keys=True,indent=2)+'\n'
    if target.exists() and target.read_text()!=payload:raise ValueError('immutable findings differ')
    target.write_text(payload)
    print(json.dumps(dict(status=report['status'],new_generated_responses=total,cached_responses=2304)))


if __name__=='__main__':main()
