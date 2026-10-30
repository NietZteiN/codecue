"""Publish deterministic overnight findings from pinned JSON and text responses.

No model, fit, parameter replay, NPZ file or raw activation is opened.  Every
scientific input is pinned; existing outputs must have exactly identical bytes.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import statistics
import tempfile
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'overnight_relationships_v1'
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT/'artifacts/binding/overnight_relationships/20261027_v1'
OUT = Path(__file__).resolve().parent
REPORT = ROOT/'reports/binding/overnight_20261027_findings_v1.md'
FIGURE = ROOT/'reports/binding/figures/overnight_relationships_v1'
MODEL_KEYS = ('llama8b', 'codellama34b')
PANELS = ('numeric_replication', 'query_twins', 'computed_roots')
LABELS = {'llama8b':'Llama 3.1 8B', 'codellama34b':'CodeLlama 34B'}
INPUTS = {}


def publish(path, payload):
    path = Path(path)
    if path.is_symlink(): raise ValueError('Publication cannot follow an output symlink')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload: raise ValueError('Immutable publication differs: '+str(path))
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.'+path.name+'.', suffix='.pending', delete=False) as stream:
            temporary=Path(stream.name); stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        try: os.link(temporary, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes()!=payload: raise ValueError('Concurrent publication differs')
    finally:
        if temporary is not None and temporary.exists(): temporary.unlink()


def pin(path, payload=None):
    path = Path(path)
    if not path.is_absolute(): path=ROOT/path
    if payload is None:
        h=hashlib.sha256()
        with path.open('rb') as stream:
            for part in iter(lambda:stream.read(1024**2), b''):h.update(part)
        checksum=h.hexdigest()
    else: checksum=hashlib.sha256(payload).hexdigest()
    entry=dict(path=str(path.relative_to(ROOT)), sha256=checksum, bytes=path.stat().st_size)
    previous=INPUTS.setdefault(entry['path'], entry)
    if previous!=entry: raise ValueError('Input changed during publication: '+entry['path'])
    return entry


def read(path, expected=None, limit=128*1024**2):
    path=Path(path)
    if not path.is_absolute():path=ROOT/path
    if path.stat().st_size>limit:raise ValueError('Bounded publication input required')
    with path.open('rb') as stream:payload=stream.read(limit+1)
    if len(payload)>limit:raise ValueError('Publication input grew beyond byte bound')
    entry=pin(path,payload)
    if expected is not None and (entry['sha256']!=expected['sha256'] or ('bytes' in expected and entry['bytes']!=expected['bytes'])):
        raise ValueError('Pinned scientific input differs: '+str(path))
    return payload


def json_input(path, expected=None): return json.loads(read(path, expected))


def receipt_input(path, role):
    value=json_input(path)
    if value.get('status')!='complete_exploratory' or value.get('evaluation_role')!=role:
        raise ValueError('Completed matching scientific receipt required: '+str(path))
    return value


def load_sources():
    manifest=json_input(BASE/'union.manifest.json')
    dataset=BASE/'union.jsonl'; entry=pin(dataset)
    if entry['sha256']!=manifest['sha256'] or manifest['rows']!=16038 or manifest['independent_python_passed'] is not True:
        raise ValueError('Validated overnight source identity differs')
    wanted=('id','split','component_id','numeric_seed','numeric_draw','source_form','query_slot','format_pair_id','expected_answer')
    records={}
    with dataset.open() as stream:
        for line in stream:
            row=json.loads(line); records[row['id']]={key:row[key] for key in wanted}
    if len(records)!=16038:raise ValueError('Unique source coverage differs')
    read(ROOT/'reports/binding/overnight_20261027_plan_v1.md')
    validation=json_input(BASE/'software_validation_review_v1.json')
    proof=read(BASE/'regression_v1.xml')
    if hashlib.sha256(proof).hexdigest()!=validation['junit_sha256'] or validation['status']!='passed':
        raise ValueError('Original execution software proof differs')
    suites=ET.fromstring(proof).findall('testsuite')
    counts={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    if counts!=dict(tests=1733,failures=0,errors=0,skipped=0):raise ValueError('Original execution regression counts differ')
    frozen=ROOT/'artifacts/binding/sources'/validation['snapshot_id']/'frozen_manifest.json'
    source=json_input(frozen)
    if source['code']['source_sha256']!=validation['source_sha256']:raise ValueError('Frozen execution source differs')
    return manifest,records,dict(snapshot_id=validation['snapshot_id'],source_sha256=validation['source_sha256'],regression=counts,
        test_scope='Original frozen overnight execution only; later fixes and follow-up tests are tracked separately.')


def load_readout(model,panel):
    folder=BASE/model/('readouts_'+panel)
    receipt=receipt_input(folder/'completion_manifest_v1.json','discovery_overnight_relationship_readouts_v1')
    registration=json_input(receipt['artifacts']['registration']['path'],receipt['artifacts']['registration'])
    result=json_input(receipt['artifacts']['results']['path'],receipt['artifacts']['results'])
    audit=json_input(receipt['artifacts']['audit']['path'],receipt['artifacts']['audit'])
    read(receipt['artifacts']['report']['path'],receipt['artifacts']['report'])
    mirror=json_input(folder/'summary.json')
    if (result['status']!='complete_exploratory' or result['panel']!=panel or result['cases']!=5832
            or result['factorizations']!=45 or result['parameter_replay_rows']!=262440
            or result['new_model_queries']!=0 or result['generated_holdouts_opened'] is not False
            or result['primary_training_support_qualified'] is not True or audit['status']!='passed'
            or audit['exact_parameter_replays'] is not True
            or registration['analysis_source']!=result['analysis_source']):
        raise ValueError('Completed overnight readout identity/counts differ')
    if mirror['scientific_completion']['sha256']!=pin(folder/'completion_manifest_v1.json')['sha256']:
        raise ValueError('Derived logging summary names another scientific receipt')
    algebraic=result['summaries']['3']['algebraic']
    if algebraic['valid_draws']!=2000 or algebraic['invalid_draws']!=0:raise ValueError('Qualified fixed primary bootstrap differs')
    for name,value in algebraic['methods'].items():
        if mirror['algebraic_methods'][name]!=value['score']:raise ValueError('Compact algebraic point differs')
    for site in ('7','8'):
        if mirror['structural_methods'][site]!=result['summaries'][site]['structural']['methods']:
            raise ValueError('Compact structural point differs')
    controls=[]
    for fit in result['fits']:
        if fit['backend']=='hidden' and fit['layer']==result['primary_layer']:
            metric=fit['metrics']['development']['coherent_shuffle_task']
            controls.append(dict(site=fit['site'],seed=fit['seed'],algebraic=metric['algebraic_family_macro_balanced_accuracy']['value'],
                whole_graph=(metric['parent_graph'] or {}).get('whole_graph_accuracy')))
    return dict(model_key=model,model=result['model'],panel=panel,source_form=result['source_form'],
        cases=result['cases'],training_rows=result['training_rows'],development_rows=result['development_rows'],
        primary_layer=result['primary_layer'],feature_dimensions=result['feature_dimensions'],
        factorizations=result['factorizations'],parameter_replay_rows=result['parameter_replay_rows'],literal_transfer_rows=result['literal_transfer_rows'],
        source=result['analysis_source'],source_result=pin(folder/'results_v1.json'),summaries=result['summaries'],coherent_control_points=controls)


def load_capture(model):
    folder=BASE/model/'capture'
    receipt=receipt_input(folder/'completion_manifest_v1.json','discovery_overnight_relationship_capture_v1')
    entry=receipt['metadata']['summary.json']; summary=json_input(entry['path'],entry)
    if summary['model_prefill_cases']!=16038 or summary['generated_responses']!=0:raise ValueError('Union capture coverage differs')
    return dict(model_prefill_cases=summary['model_prefill_cases'],prefill_attempts=summary['new_model_queries'],
        generated_responses=summary['generated_responses'],source=summary['source'],receipt=pin(folder/'completion_manifest_v1.json'))


def load_behavior(model,source_records):
    folder=BASE/model/'behavior'
    receipt=receipt_input(folder/'completion_manifest_v1.json','discovery_overnight_relationship_behavior_v1')
    summary=json_input(receipt['artifacts']['summary']['path'],receipt['artifacts']['summary'])
    data=read(receipt['artifacts']['responses']['path'],receipt['artifacts']['responses'],limit=16*1024**2)
    rows=[json.loads(line) for line in data.splitlines() if line.strip()]
    expected_ids={key for key,value in source_records.items() if value['numeric_draw']==0}
    if len(rows)!=7290 or {r['id'] for r in rows}!=expected_ids:raise ValueError('Behavior ID coverage differs')
    for row in rows:
        if any(row[key]!=value for key,value in source_records[row['id']].items()):raise ValueError('Behavior metadata differs from pinned source')
        if row['correct']!=(row['parsed']==row['expected_answer']):raise ValueError('Stored behavior score differs')
    pairs=defaultdict(dict)
    for row in rows:
        if row['split']=='development' and row['query_slot']==0:
            if row['source_form'] in pairs[row['format_pair_id']]:raise ValueError('Duplicate matched behavior form')
            pairs[row['format_pair_id']][row['source_form']]=row
    if len(pairs)!=486 or any(set(forms)!={'literal','computed'} for forms in pairs.values()):raise ValueError('Exactly486 matched DEVq0 pairs required')
    components=defaultdict(list);matched=[]
    for pair_id,forms in sorted(pairs.items()):
        literal,computed=forms['literal'],forms['computed']
        if literal['expected_answer']!=computed['expected_answer'] or literal['component_id']!=computed['component_id']:
            raise ValueError('Paired source/output identities differ')
        item=dict(format_pair_id=pair_id,component=literal['component_id'],literal_id=literal['id'],computed_id=computed['id'],
            literal_correct=literal['correct'],computed_correct=computed['correct'],
            literal_invalid=literal['parsed'] is None,computed_invalid=computed['parsed'] is None)
        components[item['component']].append(item);matched.append(item)
    if len(components)!=9 or {len(v) for v in components.values()}!={54}:raise ValueError('Nine balanced behavior components required')
    def point(key):return statistics.mean(statistics.mean(int(r[key]) for r in values) for values in components.values())
    component_means={name:dict(literal_accuracy=statistics.mean(int(v['literal_correct']) for v in values),
        computed_accuracy=statistics.mean(int(v['computed_correct']) for v in values),pairs=len(values)) for name,values in sorted(components.items())}
    contrast=summary['metrics']['computed_literal'];delta=point('computed_correct')-point('literal_correct')
    means=np.array([value['computed_accuracy']-value['literal_accuracy'] for value in component_means.values()])
    draws=np.random.default_rng(117).integers(0,9,size=(2000,9));interval=np.quantile(means[draws].mean(axis=1),[.025,.975]).tolist()
    if (abs(delta-contrast['mean'])>1e-14 or not np.allclose(interval,contrast['conditional_group_bootstrap_95'],atol=1e-14,rtol=0)
            or contrast['matched_pairs']!=486):raise ValueError('Published matched behavior contrast differs')
    return dict(model_key=model,model=summary['model'],cases=7290,new_model_queries=summary['new_model_queries'],
        generated_responses=summary['generated_responses'],source=summary['source'],source_summary=pin(folder/'summary.json'),
        matched_dev_q0=dict(pairs=486,components=9,literal_accuracy=point('literal_correct'),computed_accuracy=point('computed_correct'),
            literal_invalid_fraction=point('literal_invalid'),computed_invalid_fraction=point('computed_invalid'),
            contrast=contrast,per_component=component_means,matched_response_ids=matched),
        all_reported_behavior_cells=summary['metrics']['cells'])


def query_aggregate(readout,site):
    values=[v['direct']['query_selection'] for v in readout['summaries'][str(site)]['per_component'].values()]
    means={key:statistics.mean(value[key] for value in values) for key in values[0]}
    means['queried_minus_other_value']=means['queried_value_correct']-means['unqueried_value_correct']
    if 'queried_parent_correct' in means:means['queried_minus_other_parent']=means['queried_parent_correct']-means['unqueried_parent_correct']
    return means


def csv_bytes(summary):
    rows=[]
    def add(kind,item,site,metric,value,ci=None,unit='percent',query='',note=''):
        rows.append(dict(kind=kind,model=item['model_key'],panel=item.get('panel','matched_DEV_q0'),source_form=item.get('source_form','paired'),
            site=site,query=query,metric=metric,value=100*value,lower='' if ci is None else 100*ci[0],upper='' if ci is None else 100*ci[1],unit=unit,note=note))
    for model in MODEL_KEYS:
        for panel in PANELS:
            item=summary['readouts'][model][panel]
            for site in ('3','7','8'):
                measured=item['summaries'][site]['algebraic' if site=='3' else 'structural']
                for name,value in measured['methods'].items():add('algebraic' if site=='3' else 'graph',item,site,name,value['score'] if site=='3' else value)
                for name,value in measured.get('comparisons',{}).items():add('contrast',item,site,name,value['mean'],value['conditional_group_bootstrap_95'],'percentage_points',note='conditional9component;2000draws;no_refit;unadjusted')
            if panel=='query_twins':
                for site in ('3','7','8'):
                    for query,methods in item['summaries'][site]['per_query'].items():
                        metrics=methods['direct'];selection=metrics['query_selection']
                        if metrics['whole_graph_accuracy'] is not None:add('query',item,site,'whole_graph_accuracy',metrics['whole_graph_accuracy'],query=query,note='descriptive_no_query_effect_interval')
                        for key,value in selection.items():add('query',item,site,key,value,query=query,note='descriptive_no_query_effect_interval')
                    for key,value in query_aggregate(item,site).items():add('query_aggregate',item,site,key,value,query='all',note='descriptive_component_mean;prequery_slot_effects_not_query_modulation')
        behavior=summary['behavior'][model];matched=behavior['matched_dev_q0']
        for name in ('literal_accuracy','computed_accuracy','literal_invalid_fraction','computed_invalid_fraction'):add('behavior',behavior,'answer',name,matched[name],note='486matched_DEV_q0_pairs')
        contrast=matched['contrast'];add('behavior_contrast',behavior,'answer','computed_minus_literal',contrast['mean'],contrast['conditional_group_bootstrap_95'],'percentage_points',note='486pairs;9components;2000draws;unadjusted')
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=('kind','model','panel','source_form','site','query','metric','value','lower','upper','unit','note'),lineterminator='\n')
    writer.writeheader();writer.writerows(rows);return stream.getvalue().encode()


def pct(value):return f'{100*value:.3f}%'
def contrast_text(value):
    interval=value['conditional_group_bootstrap_95']
    return f"{100*value['mean']:+.3f} pp [{100*interval[0]:+.3f}, {100*interval[1]:+.3f}]" if interval else f"{100*value['mean']:+.3f} pp; interval unqualified"


def report_text(summary):
    counts=summary['counts']
    lines=['# Overnight relationship findings: October 27–28, 2026','',
        'All 14 stages completed. Copy-parent structure remains accessible under the known scaffold, while computed-root numeric readouts and actual execution are much weaker. These results do not establish that the model has a complete correct scalar state and then fails to use it.','',
        f"The suite used {counts['distinct_capture_cases']:,} distinct capture-case prefills across two checkpoints and generated {counts['generated_responses']:,} greedy responses. It saved {counts['factorizations']} ridge factorizations, checked {counts['parameter_replay_rows']:,} saved-parameter score rows, and made {counts['literal_transfer_rows']:,} literal-to-computed parameter applications without new fitting.",
        'The union has 16,038 distinct source rows. Each panel has 5,832 rows (3,888 TRAIN / 1,944 DEV). Shared literal/query rows were captured once per checkpoint and are not independent examples across panels.','',
        '## Algebraic relations after initialization','',
        'The metric is the fixed 18-cell, four-family macro balanced accuracy at nominated layer24 for Llama8B and36 for CodeLlama34B. All fixed TRAIN support checks passed.','',
        '| Model | Root format | Hidden direct | Hidden values → relations | Source values → relations |','|---|---|---:|---:|---:|']
    for model in MODEL_KEYS:
        for panel,form in [('numeric_replication','literal'),('computed_roots','computed')]:
            methods=summary['readouts'][model][panel]['summaries']['3']['algebraic']['methods']
            lines.append(f"| {LABELS[model]} | {form} | {pct(methods['direct']['score'])} | {pct(methods['categorical_value_derived']['score'])} | {pct(methods['source_categorical_value_derived']['score'])} |")
    lines+=['','The stronger source-value pipeline outperforms direct hidden readouts on literal roots in both models. CodeLlama\'s literal direct-minus-hidden-values interval includes zero, so the earlier 8B advantage is not a clear two-model result. On computed roots, direct scores are only about55–57%; CodeLlama\'s comparison with its own value-derived decoder also has an interval crossing zero.','',
        '| Model | Format | Direct minus hidden values | Direct minus source values |','|---|---|---|---|']
    for model in MODEL_KEYS:
        for panel,form in [('numeric_replication','literal'),('computed_roots','computed')]:
            c=summary['readouts'][model][panel]['summaries']['3']['algebraic']['comparisons']
            lines.append(f"| {LABELS[model]} | {form} | {contrast_text(c['direct_minus_categorical_value_derived'])} | {contrast_text(c['direct_minus_source_categorical_value_derived'])} |")
    lines+=['','Intervals are conditional 95% component bootstraps: 2,000 valid draws, nine DEV components, fixed saved fits, no refitting or multiplicity adjustment. The direct18-output and categorical128-output pipelines have different task difficulty and total parameter counts. A hidden/source comparison concerns decoder accessibility, not information absent from the input. Selected sum/subtraction cells encode equivalent events; the relation cells are not independent replications.','',
        '## Complete parent graphs and literal-to-computed transfer','',
        '| Model | Format | Last assignment | Final prompt |','|---|---|---:|---:|']
    for model in MODEL_KEYS:
        for panel,form in [('numeric_replication','literal'),('computed_roots','computed')]:
            r=summary['readouts'][model][panel]['summaries']
            lines.append(f"| {LABELS[model]} | {form} | {pct(r['7']['structural']['methods']['direct'])} | {pct(r['8']['structural']['methods']['direct'])} |")
    lines+=['','These are exact four-parent reconstructions under supplied node/version identities, not general node/version discovery. Direct source ngram controls remain in the result files; a strong symbolic source parser can recover these explicitly written copies. Graph decodability is not evidence of natural causal use.','',
        '| Model | Computed metric | Within-computed fit | Frozen literal parameters on computed inputs | Within minus transfer, conditional95% |','|---|---|---:|---:|---|']
    for model in MODEL_KEYS:
        r=summary['readouts'][model]['computed_roots']['summaries']
        for site,label in [('3','initialization algebraic'),('7','last-assignment graph'),('8','final-prompt graph')]:
            metric=r[site]['algebraic' if site=='3' else 'structural'];methods=metric['methods']
            direct=methods['direct']['score'] if site=='3' else methods['direct']
            transfer=methods['literal_transfer_direct']['score'] if site=='3' else methods['literal_transfer_direct']
            lines.append(f"| {LABELS[model]} | {label} | {pct(direct)} | {pct(transfer)} | {contrast_text(metric['comparisons']['direct_minus_literal_transfer_direct'])} |")
    lines+=['','Algebraic transfer is near the constant-predictor balanced-accuracy baseline of50%, while graph transfer is substantially stronger. CodeLlama\'s within-computed minus transferred graph intervals cross zero at both sites; do not claim a clear adaptation gain there. Root formats differ in arithmetic operations, token counts, positions and visible operands.','',
        'At the computed final prompt, queried categorical-value accuracy is only7.493% for8B and6.927% for34B, against a6.173% TRAIN prior in both. The corresponding source points are6.550% and7.596%. Strong routing readouts therefore do not imply that all necessary numeric quantities were correctly decoded.','',
        '## Query conditioning','',
        'PanelB uses the same bodies with all four queries, but fewer unique numeric draws than panelA. Before the query is visible (sites3/7), whole-graph and algebraic results are identical across future query slots. Per-slot queried/other accuracy differences at those sites measure which slot is scored, not modulation by a future query.','',
        '| Model | Query | Final whole graph | Queried value | Other values | Queried parent | Other parents |','|---|---:|---:|---:|---:|---:|---:|']
    for model in MODEL_KEYS:
        r=summary['readouts'][model]['query_twins']
        for query,methods in r['summaries']['8']['per_query'].items():
            item=methods['direct'];s=item['query_selection']
            lines.append(f"| {LABELS[model]} | v{query} | {pct(item['whole_graph_accuracy'])} | {pct(s['queried_value_correct'])} | {pct(s['unqueried_value_correct'])} | {pct(s['queried_parent_correct'])} | {pct(s['unqueried_parent_correct'])} |")
    lines+=['','Averaged over all four query choices and nine components, final queried-minus-other value accuracy is+0.857pp for8B and−0.400pp for34B; parent differences are+3.589pp and+3.149pp. These are descriptive point summaries with no query-effect interval. Individual slot contrasts can reflect slot difficulty, and other slots may be ancestors of the queried output. Same-body, fixed-slot effects require a separate matched analysis.','',
        '## Actual generated answers on matched DEV query-v0 programs','',
        'Each model generated7,290 responses, but this predeclared root-format contrast uses exactly486 matched DEV query-v0 pairs across nine components. The literal rates below use those same pairs, not all-query or pooled TRAIN/DEV literal rates.','',
        '| Model | Matched literal accuracy | Computed accuracy | Computed minus literal, conditional95% | Literal invalid | Computed invalid |','|---|---:|---:|---|---:|---:|']
    for model in MODEL_KEYS:
        m=summary['behavior'][model]['matched_dev_q0']
        lines.append(f"| {LABELS[model]} | {pct(m['literal_accuracy'])} | {pct(m['computed_accuracy'])} | {contrast_text(m['contrast'])} | {pct(m['literal_invalid_fraction'])} | {pct(m['computed_invalid_fraction'])} |")
    lines+=['','The format penalty is large under both checkpoints. CodeLlama\'s computed responses are valid integers yet mostly wrong; this is not solely a response-format failure. The literal baseline is also unreliable. Arithmetic difficulty, operation count and context/position changes remain confounded with root format; these results do not isolate a binding mechanism.','',
        '## Evidence and scope','',
        'The frozen overnight execution used snapshot`'+summary['original_execution']['snapshot_id']+'` and source`'+summary['original_execution']['source_sha256']+'`. Its full binding regression passed1,733tests with no failures, errors or skips. That count describes the original execution; later fixes and follow-up tests are tracked separately.','',
        'All evidence remains adaptive discovery on the reused27structural components and81graphs. Three numeric seeds, three weighting seeds, lexical relatives, query siblings and paired formats are not independent structural replications. No sealed final outcomes were opened. No causal intervention, mechanism-C error predictor, broad ownership/version resolution or new-family confirmation is established.','',
        'The reproducible [publication script](../../artifacts/binding/overnight_relationships/20261028_completion_v1/publish_overnight_results_v1.py), [exact summary JSON](../../artifacts/binding/overnight_relationships/20261028_completion_v1/results_summary_v1.json), [CSV](../../artifacts/binding/overnight_relationships/20261028_completion_v1/results_summary_v1.csv) and [publication manifest](../../artifacts/binding/overnight_relationships/20261028_completion_v1/publication_review_v1.json) retain input checksums and output identities.','',
        '![Overnight relationship results](figures/overnight_relationships_v1.png)','']
    return '\n'.join(lines)


def figure_bytes(summary,suffix):
    colors=['#2878b5','#8b929a','#278a67'];orange='#e38a32'
    fig,axes=plt.subplots(1,3,figsize=(16.8,5.7));cells=[(m,p) for m in MODEL_KEYS for p in ('numeric_replication','computed_roots')]
    x=np.arange(4);width=.24
    for offset,method,color,label in zip((-width,0,width),('direct','categorical_value_derived','source_categorical_value_derived'),colors,('Hidden direct','Hidden values → relations','Source values → relations')):
        values=[100*summary['readouts'][m][p]['summaries']['3']['algebraic']['methods'][method]['score'] for m,p in cells]
        bars=axes[0].bar(x+offset,values,width,color=color,label=label);axes[0].bar_label(bars,fmt='%.1f',padding=2,fontsize=8)
    labels=['8B\nliteral','8B\ncomputed','34B\nliteral','34B\ncomputed']
    axes[0].set_xticks(x,labels);axes[0].set_title('Algebraic relations after initialization');axes[0].set_ylabel('Four-family macro balanced accuracy (%)')
    axes[0].axhline(50,color='#bbbbbb',linestyle=':',linewidth=.8);axes[0].legend(frameon=False,fontsize=8,loc='lower left')
    for offset,site,color,label in [(-.17,'7',colors[0],'Last assignment'),(.17,'8',orange,'Final prompt')]:
        values=[100*summary['readouts'][m][p]['summaries'][site]['structural']['methods']['direct'] for m,p in cells]
        bars=axes[1].bar(x+offset,values,.34,color=color,label=label);axes[1].bar_label(bars,fmt='%.1f',padding=2,fontsize=8)
    axes[1].set_xticks(x,labels);axes[1].set_title('Complete parent graph');axes[1].set_ylabel('Hidden whole-graph accuracy (%)');axes[1].legend(frameon=False,fontsize=8,loc='lower left')
    bx=np.arange(2)
    for offset,field,color,label in [(-.17,'literal_accuracy',colors[0],'Literal roots'),(.17,'computed_accuracy',orange,'Computed roots')]:
        values=[100*summary['behavior'][m]['matched_dev_q0'][field] for m in MODEL_KEYS]
        bars=axes[2].bar(bx+offset,values,.34,color=color,label=label);axes[2].bar_label(bars,fmt='%.1f',padding=2,fontsize=8)
    axes[2].set_xticks(bx,['Llama 8B','CodeLlama 34B']);axes[2].set_title('Matched DEV query-v0 behavior');axes[2].set_ylabel('Exact generated integer accuracy (%)');axes[2].legend(frameon=False,fontsize=8,loc='upper right')
    for ax in axes:
        ax.set_ylim(0,108);ax.set_yticks([0,25,50,75,100]);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Overnight relationship experiments: fixed-scaffold discovery',fontsize=14,y=.99)
    intervals=[]
    for m in MODEL_KEYS:
        c=summary['behavior'][m]['matched_dev_q0']['contrast'];lo,hi=c['conditional_group_bootstrap_95']
        intervals.append(f"{('8B' if m=='llama8b' else '34B')}: {100*c['mean']:+.1f} pp [{100*lo:+.1f}, {100*hi:+.1f}]")
    foot=('Nominated hidden layers24/36; three weighting seeds; nine DEV components. Bars are point estimates, not absolute confidence intervals.\n'
          'Behavior uses486 matched DEV query-v0 pairs per model. Computed − literal conditional95% contrasts: '+'; '.join(intervals)+'.\n'
          'Known graph scaffold; formats differ in operations/tokens/positions. Correlated seeds/relatives are not replications; no causal-use claim.')
    fig.text(.018,.012,foot,ha='left',va='bottom',fontsize=8.4);fig.tight_layout(rect=(0,.17,1,.94))
    stream=io.BytesIO();metadata={'Date':None,'Creator':'publish_overnight_results_v1.py'} if suffix=='svg' else {'Software':'publish_overnight_results_v1.py'}
    fig.savefig(stream,format=suffix,dpi=180,bbox_inches='tight',metadata=metadata);plt.close(fig)
    return stream.getvalue()


def main():
    pin(Path(__file__))
    manifest,source_records,execution=load_sources()
    readouts={model:{panel:load_readout(model,panel) for panel in PANELS} for model in MODEL_KEYS}
    behavior={model:load_behavior(model,source_records) for model in MODEL_KEYS}
    captures={model:load_capture(model) for model in MODEL_KEYS}
    for model in MODEL_KEYS:
        for panel in PANELS:
            if readouts[model][panel]['source']['source_sha256']!=execution['source_sha256']:raise ValueError('Mixed readout execution source')
    counts=dict(source_union_rows=16038,rows_per_panel=5832,distinct_capture_cases=sum(c['model_prefill_cases'] for c in captures.values()),
        capture_prefill_attempts=sum(c['prefill_attempts'] for c in captures.values()),behavior_prefill_attempts=sum(c['new_model_queries'] for c in behavior.values()),
        generated_responses=sum(c['generated_responses'] for c in behavior.values()),
        factorizations=sum(r['factorizations'] for models in readouts.values() for r in models.values()),
        parameter_replay_rows=sum(r['parameter_replay_rows'] for models in readouts.values() for r in models.values()),
        literal_transfer_rows=sum(r['literal_transfer_rows'] for models in readouts.values() for r in models.values()))
    summary=dict(evaluation_role='overnight_relationship_publication_v1',status='complete_exploratory',
        original_execution=execution,counts=counts,dataset_manifest_summary={k:manifest[k] for k in ('rows','split_rows','cohort_rows','globally_unique_initial_states','independent_python_passed')},
        readouts=readouts,behavior=behavior,captures=captures,
        uncertainty='Existing conditional difference intervals only: nine DEV components,2000draws,seed117,no refitting or multiplicity adjustment; no new absolute intervals.',
        publication_new_model_queries=0,publication_new_fits=0,publication_parameter_replays=0,npz_arrays_opened=False,generated_holdouts_opened=False,
        input_pins=[INPUTS[key] for key in sorted(INPUTS)])
    outputs={OUT/'results_summary_v1.json':(json.dumps(summary,sort_keys=True,indent=2,allow_nan=False)+'\n').encode(),
        OUT/'results_summary_v1.csv':csv_bytes(summary),REPORT:report_text(summary).encode(),
        FIGURE.with_suffix('.png'):figure_bytes(summary,'png'),FIGURE.with_suffix('.svg'):figure_bytes(summary,'svg')}
    for path,payload in outputs.items():publish(path,payload)
    review=dict(evaluation_role='overnight_relationship_publication_review_v1',status='passed',input_pins=summary['input_pins'],
        output_pins=[dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload)) for path,payload in outputs.items()],
        counts=counts,matched_behavior_pairs_per_model=486,point_bars_only=True,conditional_contrast_intervals_only=True,
        source_and_seed_dependence_explicit=True,new_model_queries=0,new_fits=0,parameter_replays=0,raw_arrays_opened=False,generated_holdouts_opened=False)
    publish(OUT/'publication_review_v1.json',(json.dumps(review,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps(dict(status='published',counts=counts,input_pins=len(INPUTS),outputs=[str(path.relative_to(ROOT)) for path in outputs]),sort_keys=True))


if __name__=='__main__':main()
