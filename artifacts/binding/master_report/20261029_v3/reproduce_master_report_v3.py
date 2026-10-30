"""Build the sourced master document, embedded-figure HTML and archive indices."""
from pathlib import Path
import base64
import csv
import hashlib
import io
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports/binding'
SUITE = ROOT / 'artifacts/binding/old_value_overnight/20261028_v1'
sys.path.insert(0, str(ROOT / 'src'))
from codecue.binding.relationship_capture import _put, _publish
import markdown
import conceptual_figures_v1 as concepts

PINS = {}
FIGURES = []
PROVENANCE = []


def pin(path):
    path = Path(path)
    key = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    data = path.read_bytes()
    value = dict(path=key, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    assert PINS.setdefault(key, value) == value, key
    return value


def read(path):
    path = Path(path)
    relative = path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path('original_dependvar_20261025.txt')
    snapshot = OUT / 'input_snapshot' / relative
    if not snapshot.exists():
        _publish(snapshot, path.read_bytes())
    item = pin(snapshot)
    provenance = dict(original_path=str(path), snapshot=item)
    if provenance not in PROVENANCE: PROVENANCE.append(provenance)
    return snapshot.read_text()


def table(name, index=0):
    lines = read(REPORTS / name).splitlines()
    tables, block = [], []
    for line in lines + ['']:
        if line.startswith('|'):
            block.append(line)
        elif block:
            tables.append('\n'.join(block))
            block = []
    return tables[index]


def figure(relative, caption):
    path = REPORTS / relative
    pin(path)
    FIGURES.append(dict(number=len(FIGURES)+1, path=relative, caption=caption))
    return f'![{caption}]({relative})\n\n*Figure {len(FIGURES)}. {caption}*'


def render_figures(comparison, ceilings):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'binding-master-20261029'})
    fig, axes = plt.subplots(1, 3, figsize=(13.8,4.6), gridspec_kw={'width_ratios':[1.3,1,1]})
    colors = {'llama8b':'#24658a','codellama34b':'#d17b36'}
    names = [('llama8b','Llama 8B'),('codellama34b','CodeLlama 34B')]
    export = {}
    for index,(key,label) in enumerate(names):
        review = comparison['models'][key]['review']
        cells = review['gate_cells']+review['equality_control_cells']
        values=[]
        for mode in ('current','previous'):
            group=[c for c in cells if c['query_mode']==mode]
            n=sum(c['n'] for c in group); correct=sum(c['correct'] for c in group)
            values.append(correct/n*100)
            export.setdefault(key,{})[mode]=dict(n=n,correct=correct,accuracy=correct/n)
        bars=axes[0].bar([index-.18,index+.18],values,width=.32,color=colors[key],alpha=1,
                         hatch=[None,'///'],edgecolor='white')
        axes[0].bar_label(bars,fmt='%.1f%%',padding=4,fontsize=10)
        invalid=review['invalid']/review['n']*100
        bar=axes[1].bar(index,invalid,color=colors[key],width=.5)
        axes[1].bar_label(bar,fmt='%.1f%%',padding=4)
        blocked=ceilings['per_model'][key]['blocked_cells']
        bar=axes[2].bar(index,blocked,color=colors[key],width=.5)
        axes[2].bar_label(bar,labels=[f'{blocked} / 24'],padding=4)
    axes[0].set_title('A  Greedy numeric accuracy',loc='left',fontweight='bold')
    axes[0].set_xticks([0,1],[label for _,label in names]);axes[0].set_ylim(0,105)
    axes[0].set_ylabel('Correct (%)');axes[0].text(.5,-.19,'Solid: current   /   Hatched: previous',transform=axes[0].transAxes,ha='center',fontsize=9)
    axes[1].set_title('B  Invalid saved answers',loc='left',fontweight='bold')
    axes[1].set_xticks([0,1],[label for _,label in names]);axes[1].set_ylim(0,105);axes[1].set_ylabel('Invalid (%)')
    axes[2].set_title('C  Format-only repair cannot pass',loc='left',fontweight='bold',fontsize=10)
    axes[2].set_xticks([0,1],[label for _,label in names]);axes[2].set_ylim(0,28);axes[2].set_yticks([0,8,16,24]);axes[2].set_ylabel('Primary cells still below 90%')
    for ax in axes:
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True)
    fig.suptitle('Historical-value calibration: completed discovery cohort',x=.06,ha='left',fontweight='bold',fontsize=15)
    fig.subplots_adjust(top=.78,bottom=.2,wspace=.43,left=.065,right=.98)
    for suffix in ('png','svg'):
        target=REPORTS/f'figures/master_old_value_20261029_v1.{suffix}'
        stream=io.BytesIO();fig.savefig(stream,format=suffix,dpi=170,metadata={'Date':None} if suffix=='svg' else {'Software':'CodeCue master-report builder'})
        _publish(target,stream.getvalue())
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,3.1));ax.set_xlim(0,12);ax.set_ylim(0,3.2);ax.axis('off')
    cards=[('M0–M1','Audit + semantics','Built / checked','#dceee7'),('M2','Behavioral calibration','Run; reliability mixed','#fff0cf'),('M3','Readouts + controls','Scoped findings','#dceee7'),('M4','Selective intervention','Partial / inconclusive','#fff0cf'),('M5','Frozen unfamiliar prediction','Not reached','#f4dddd'),('M6','Paper decision','Claim still open','#f4dddd')]
    for i,(code,title,status,color) in enumerate(cards):
        row=i//3;column=i%3;x=.15+column*4;y=1.8 if row==0 else .15
        ax.add_patch(FancyBboxPatch((x,y),3.55,1.15,boxstyle='round,pad=.08',facecolor=color,edgecolor='#ccd5da'))
        ax.text(x+.15,y+.89,code,fontweight='bold',fontsize=11);ax.text(x+.15,y+.57,title,fontsize=10);ax.text(x+.15,y+.24,status,fontsize=9,color='#465663')
        if column<2:ax.annotate('',xy=(x+3.9,y+.57),xytext=(x+3.6,y+.57),arrowprops=dict(arrowstyle='->',color='#73828a'))
    ax.plot([8.4,8.4,.55],[1.72,1.55,1.55],color='#73828a',linewidth=1)
    ax.annotate('',xy=(.55,1.38),xytext=(.55,1.55),arrowprops=dict(arrowstyle='->',color='#73828a'))
    ax.text(.1,3.1,'Original plan: execution progress is separate from scientific qualification',fontsize=12,fontweight='bold')
    fig.tight_layout()
    for suffix in ('png','svg'):
        stream=io.BytesIO();fig.savefig(stream,format=suffix,dpi=170,metadata={'Date':None} if suffix=='svg' else {'Software':'CodeCue master-report builder'})
        _publish(REPORTS/f'figures/master_plan_20261029_v2.{suffix}',stream.getvalue())
    plt.close(fig)
    return export


def check_publication(value):
    original=json.loads((OUT/'publication_review_v1.json').read_text())
    for key in original:
        if key != 'builder': assert original[key] == value[key], key
    assert pin(ROOT/original['builder']['path']) == original['builder']
    for item in original['outputs']: assert pin(ROOT/item['path']) == item



def main():
    comparison=json.loads(read(SUITE/'comparison_v1.json'))
    completion=json.loads(read(SUITE/'completion_review_v1.json'))
    ceiling=json.loads(read(SUITE/'format_ceiling_review_v1.json'))
    daytime=json.loads(read(SUITE/'daytime_check_review_20261029_v1.json'))
    readiness=json.loads(read(SUITE/'readiness_at_completion_v1.json'))
    source=read(REPORTS/'master_research_report_source.md')
    original=read(ROOT.parent/'dependvar.txt')
    assert comparison['status']==completion['status']=='complete_audited'
    assert daytime['all_seven_suite_stages_completed'] and comparison['total_scored_responses']==40320
    for expected in completion['output_pins']:
        if expected['path'].endswith('comparison_v1.json'):assert pin(ROOT/expected['path'])==expected
    conceptual_data=concepts.build_figures(_publish)
    plot_data=render_figures(comparison,ceiling)
    latest=['| Latest old/current calibration | Llama 8B | CodeLlama 34B |','|---|---:|---:|']
    reviews=[comparison['models'][key]['review'] for key in ('llama8b','codellama34b')]
    for label,values in [('Scored responses',[f"{r['n']:,}" for r in reviews]),('Overall exact accuracy',[f"{r['accuracy']:.2%}" for r in reviews]),('Invalid responses',[f"{r['invalid']:,}" for r in reviews]),('Primary reliability cells passed',[f"{sum(c['passed'] for c in r['gate_cells'])} / {len(r['gate_cells'])}" for r in reviews])]:
        latest.append('| '+label+' | '+' | '.join(values)+' |')
    counts=completion['readiness']['counts'];assert sum(counts.values())==74
    source=source.replace('{{latest_summary}}','\n'.join(latest)).replace('{{readiness_summary}}',f"**74 tracked tasks: {counts['ready']} ready, {counts['needs_scientific_decision']} requiring scientific decisions, {counts['deferred_optional']} optional/deferred**")
    old=['| Model | Question | Correct / n | Accuracy | Invalid |','|---|---|---:|---:|---:|']
    for model in ('llama8b','codellama34b'):
        review=comparison['models'][model]['review']
        for mode in ('current','previous'):
            cells=[c for c in review['gate_cells']+review['equality_control_cells'] if c['query_mode']==mode]
            n=sum(c['n'] for c in cells);correct=sum(c['correct'] for c in cells);invalid=sum(c['invalid'] for c in cells)
            old.append(f'| {model} | {mode} | {correct:,} / {n:,} | {correct/n:.2%} | {invalid:,} |')
    source=source.replace('{{old_value_table}}','\n'.join(old))
    bounds=['| Model | Fixed primary cells | Still below 90% even with every invalid answer correct |','|---|---:|---:|']
    for model,item in sorted(ceiling['per_model'].items()):bounds.append(f"| {model} | {item['cells']} | {item['blocked_cells']} |")
    source=source.replace('{{format_table}}','\n'.join(bounds))
    diversity=table('diversity_decoding_findings_v1.md',0).splitlines()
    source=source.replace('{{diversity_table}}','\n'.join(diversity[:2]+[r for r in diversity[2:] if '| hidden | direct |' in r]))
    for token,index in [('original_branch_table',0),('experiment_coverage_table',1),('extension_table',2)]:source=source.replace('{{'+token+'}}',table('research_backlog.md',index))
    tasks=table('preparation_readiness.md',0).splitlines()
    decisions=[row for row in tasks[2:] if '| needs_scientific_decision |' in row]
    assert len(decisions)==9
    source=source.replace('{{open_decisions_table}}','\n'.join(tasks[:2]+decisions))
    source=source.replace('{{milestone_figure}}','{{figure:figures/master_plan_20261029_v2.png|The original milestones and current evidence status. Engineering completion does not imply causal or confirmatory qualification.}}')
    source=re.sub(r'\{\{table:([^:}]+):(\d+)\}\}',lambda m:table(m[1],int(m[2])),source)
    source=re.sub(r'\{\{figure:([^|}]+)\|([^}]+)\}\}',lambda m:figure(m[1],m[2]),source)
    source=source.replace('{{archive_links}}','[report archive CSV](master_report_archive_20261029_v3.csv) and [figure archive CSV](master_figure_archive_20261029_v3.csv)')
    catalog=[]
    historical={'figures/master_plan_20261029_v1.png':'Retired draft diagram with an incorrect wraparound connector; use master_plan_20261029_v2.png.', 'value_transfer_effects.png':'Superseded formatting-space transfer; use value_transfer_effects_v2.png.', 'discovery_confidence_increments_v1.png':'Earlier comparison; corrected v2 is current.', 'discovery_prediction_results_v1.png':'Earlier figure revision; v2 is current.'}
    historical.update({f'figures/{stem}.png':'Conceptual illustration, not an experimental result.' for stem in ('concept_binding_timeline_v1','concept_relationship_types_v1','concept_evidence_ladder_v1')})
    shown={entry['path'] for entry in FIGURES}
    appendix=['### Complete figure index','', '| Figure | Context |','|---|---|']
    original_catalog=json.loads((OUT/'master_report_data_v1.json').read_text())['figure_catalog']
    for path in [REPORTS/item['figure'] for item in original_catalog]:
        relative=str(path.relative_to(REPORTS));entry=dict(figure=relative,context=historical.get(relative,'See originating report for endpoint, cohort and qualifications.'),**pin(path));catalog.append(entry)
        appendix.append(f"| [{relative}]({relative}) | {entry['context']} |")
    others=[entry for entry in catalog if entry['figure'] not in shown]
    appendix+=['','### Additional figures from completed and historical studies','', 'The main sections show the central figures. The following gallery preserves the other figure revisions. Earlier/superseded outputs are labeled and do not replace corrected results.','']
    for entry in others:
        appendix+=['<details markdown="1">',f"<summary>{entry['figure']} — {entry['context']}</summary>",'',f"![{entry['context']}]({entry['figure']})",'', '</details>','']
    source=source.replace('{{figure_catalog}}','\n'.join(appendix))
    assert '{{' not in source
    archive=[]
    for path in sorted(REPORTS.glob('*.md')):
        if path.name.startswith('master_research_report'):continue
        text=path.read_text();title=next((line.lstrip('# ').strip() for line in text.splitlines() if line.startswith('#')),'Untitled')
        archive.append(dict(file=path.name,title=title,bytes=path.stat().st_size,sha256=hashlib.sha256(text.encode()).hexdigest()))
    saved_archive=OUT/'archive_snapshot_v1.json'
    if saved_archive.exists():
        archive=json.loads(saved_archive.read_text())['reports']
    else:
        _put(saved_archive,dict(reports=archive))
    for name,rows in [('master_report_archive_20261029_v3.csv',archive),('master_figure_archive_20261029_v3.csv',catalog)]:
        buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=['file','title','bytes','sha256'] if 'report_archive' in name else ['figure','context','path','bytes','sha256']);writer.writeheader();writer.writerows(rows);_publish(REPORTS/name,buffer.getvalue().encode())
    _publish(REPORTS/'master_research_report_v3.md',source.encode())
    body=markdown.markdown(source,extensions=['tables','fenced_code','toc','sane_lists','md_in_html'])
    def embedded(match):
        path=REPORTS/match[2];pin(path);encoded=base64.b64encode(path.read_bytes()).decode()
        return match[1]+'data:image/png;base64,'+encoded+match[3]
    body=body.replace('<!-- BINDING_STEPPER -->', concepts.stepper_html())
    body=re.sub(r'(<img\b[^>]*\bsrc=")([^"]+)(")',embedded,body)
    with_toc=markdown.Markdown(extensions=['tables','fenced_code','toc','sane_lists','md_in_html']);with_toc.convert(source)
    original_html=markdown.markdown(original,extensions=['tables','fenced_code'])
    css='''body{font:16px/1.65 system-ui,-apple-system,Segoe UI,sans-serif;color:#203441;background:#f4f7f9;margin:0}main{max-width:1080px;margin:0 auto;background:white;padding:38px 52px}h1{font-size:2.25em;line-height:1.2;color:#153e54}h2{margin-top:2.6em;padding-top:.7em;border-top:2px solid #dce6eb;color:#174b65;scroll-margin-top:20px}h3{margin-top:1.8em;color:#28596d}p,li{max-width:100%}a{color:#126b91}table{border-collapse:collapse;width:100%;font-size:.86em;margin:24px 0;display:block;overflow-x:auto}th,td{border:1px solid #d6e1e7;padding:9px 11px;text-align:left;vertical-align:top}th{background:#e9f1f5}tr:nth-child(even){background:#f8fafb}img{width:auto;max-width:100%;height:auto;margin-top:16px}pre{overflow-x:auto;background:#eef3f6;padding:18px;border-radius:6px;font-size:.82em}code{overflow-wrap:anywhere}.toc{background:#edf4f6;border-left:5px solid #367e99;padding:20px 28px}.toc ul{padding-left:22px}.toc li{margin:5px 0}details{border:1px solid #d9e2e8;padding:12px 18px;margin:14px 0;border-radius:6px}summary{cursor:pointer;font-weight:600}.notice{background:#e3f1e9;padding:14px 18px;border-radius:6px;font-size:.9em}@media(max-width:700px){main{padding:20px}h1{font-size:1.8em}table{font-size:.8em}}@media print{body{background:white;font-size:10pt}main{max-width:none;padding:0}h2{break-before:page}table,figure,img{break-inside:avoid}a{color:inherit}.toc{break-after:page}details:not([open])>summary{display:block}}'''
    css += concepts.CSS
    toc=re.sub(r'<li>\s*<a[^>]*>.*?</a>\s*<ul>',lambda m:m[0],with_toc.toc)
    html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Variable binding — master research report, October 29 2026</title><style>'+css+'</style></head><body><main><div class="notice">Evidence snapshot: October 29, 2026. All figures are embedded. Linked detailed reports and artifact evidence resolve within the project workspace. Use your browser’s Print command for a PDF copy.</div><nav aria-label="Contents">'+toc+'</nav>'+body+'<h2 id="complete-original-plan">Full original plan</h2><details><summary>Open the unchanged dependvar.txt plan (version October 25, 2026)</summary>'+original_html+'</details></main></body></html>'
    _publish(REPORTS/'master_research_report_v3.html',html.encode())
    for value in list(PINS.values()):
        path=Path(value['path']);path=path if path.is_absolute() else ROOT/path
        assert pin(path)==value
    selected=dict(evaluation_role='binding_master_report_data_v1',status='complete_audited',evidence_cutoff=daytime['checked_at'],readiness=completion['readiness'],old_value_plot=plot_data,format_ceiling=ceiling['per_model'],figures=FIGURES,figure_catalog=catalog,report_catalog=archive,input_provenance=PROVENANCE,conceptual_illustration_data=conceptual_data)
    _put(OUT/'master_report_data_v1.json',selected)
    outputs=[REPORTS/'master_research_report_v3.md',REPORTS/'master_research_report_v3.html',REPORTS/'master_report_archive_20261029_v3.csv',REPORTS/'master_figure_archive_20261029_v3.csv',OUT/'master_report_data_v1.json']
    check_publication(dict(evaluation_role='binding_master_report_publication_v1',status='complete_audited',new_model_queries=0,new_fits=0,scientific_results_changed=False,supersedes='20261029_v2',revision_reason='Add three conceptual figures and an interactive Python-ground-truth walkthrough; scientific results unchanged',full_original_plan_embedded_in_html=True,figures_embedded=True,main_figures=len(FIGURES),all_png_figures=len(catalog),archive_reports=len(archive),inputs=sorted(PINS.values(),key=lambda value:value['path']),builder=pin(Path(__file__).resolve()),conceptual_builder=pin(Path(concepts.__file__).resolve()),outputs=[pin(path) for path in outputs]))
    print(json.dumps(dict(status='complete_audited',main_figures=len(FIGURES),all_figures=len(catalog),archive_reports=len(archive),markdown_bytes=(REPORTS/'master_research_report_v3.md').stat().st_size,html_bytes=(REPORTS/'master_research_report_v3.html').stat().st_size),sort_keys=True))


if __name__=='__main__':main()
