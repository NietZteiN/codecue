#!/usr/bin/env python
"""Summarize completed discovery artifacts; no fits or language-model calls."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'artifacts/binding/arithmetic_graph/20261029_v3'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned(entry):
    path=Path(entry['path'])
    path=path if path.is_absolute() else ROOT/path
    if not path.resolve().is_relative_to(RUN) or path.is_symlink():
        raise ValueError('explicit arithmetic discovery artifact required')
    if path.stat().st_size!=entry['bytes'] or sha(path)!=entry['sha256']:
        raise ValueError('completed artifact pin differs')
    return path


def main():
    dataset=RUN/'sources.jsonl'
    manifest=json.loads(dataset.with_suffix('.manifest.json').read_text())
    if sha(dataset)!=manifest['sha256'] or manifest['evaluation_role']!='discovery_arithmetic_graph_sources_v1':
        raise ValueError('pinned source-only arithmetic discovery cohort required')
    source={r['id']:r for r in map(json.loads,dataset.read_text().splitlines())}
    result=dict(evaluation_role='discovery_arithmetic_graph_findings_v1',status='complete_exploratory',
        dataset_sha256=manifest['sha256'],script_sha256=sha(__file__),models={},new_model_queries=0,new_scientific_fits=0)
    for name in ('llama8b','codellama34b'):
        folder=RUN/name
        receipt=json.loads((folder/'readouts/completion_manifest_v1.json').read_text())
        data_path=pinned(receipt['artifacts']['results'])
        data=json.loads(data_path.read_text())
        if data['cases']!=4608 or data['factorizations']!=18:raise ValueError('complete fixed readout grid required')
        summary=[]
        for site in range(3):
            for backend in ('hidden','source'):
                banks=[b for b in data['fits'] if b['site']==site and b['backend']==backend]
                if sorted(b['seed'] for b in banks)!=[11,29,47]:raise ValueError('three fixed weighting seeds required')
                def mean(key):return sum(b['metrics']['direct'][key] for b in banks)/3
                summary.append(dict(site=site,backend=backend,value_accuracy=mean('value_accuracy'),
                    whole_state_accuracy=mean('whole_state_accuracy'),parent_accuracy=mean('parent_accuracy') if site else None,
                    whole_parent_accuracy=mean('whole_parent_accuracy') if site else None,
                    direct_relations=sum(b['metrics']['direct']['relations']['macro_balanced_accuracy'] for b in banks)/3,
                    value_derived_relations=mean('value_derived_relation_macro_balanced_accuracy')))
        behavior_receipt=json.loads((folder/'behavior/completion_manifest_v1.json').read_text())
        response_path=pinned(behavior_receipt['artifacts']['responses'])
        responses=[json.loads(line) for line in response_path.read_text().splitlines()]
        expected={key for key,row in source.items() if row['numeric_draw']==0}
        if len(responses)!=1152 or {r['id'] for r in responses}!=expected:
            raise ValueError('complete unique declared behavior cohort required')
        cells=defaultdict(list)
        for row in responses:
            original=source[row['id']]
            text=row['raw_response'].strip()
            parsed=int(text) if re.fullmatch(r'[+-]?[0-9]+',text) else None
            correct=parsed==original['expected_answer']
            if parsed!=row['parsed'] or correct!=row['correct'] or row['expected_answer']!=original['expected_answer']:
                raise ValueError('original response/parser score differs')
            if original['split']!='development':continue
            kind='arithmetic_written' if original['oracle']['definitions'][original['query_slot']]>=4 else 'untouched_literal'
            for key in ('all',kind):cells[key].append(row)
        behavior={key:dict(rows=len(rows),correct=sum(r['correct'] for r in rows),
            accuracy=sum(r['correct'] for r in rows)/len(rows),invalid=sum(r['parsed'] is None for r in rows),
            structural_families=len({r['component_id'] for r in rows})) for key,rows in cells.items()}
        if {key:value['rows'] for key,value in behavior.items()}!={'all':288,'arithmetic_written':216,'untouched_literal':72}:
            raise ValueError('prospectively described DEV query strata differ')
        result['models'][name]=dict(readouts=summary,behavior_development=behavior,
            readout_results_sha256=sha(data_path),behavior_responses_sha256=sha(response_path))
    destination=RUN/'findings_review_v1.json'
    payload=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if destination.exists() and destination.read_text()!=payload:raise ValueError('immutable findings differ')
    destination.write_text(payload)
    text=['# Two-input arithmetic relationship discovery: completed first suite','',
        'Both checkpoints completed4,608 captures,1,152 generated answers and18 readout fits. All jobs exited successfully. The table reports the nominated layer at every captured site, averaged across three weighting seeds; no best layer/site is selected. Numeric, lexical and query relatives stay grouped in36 TRAIN /12 DEV structural families.','',
        '| Model | Site | Features | Parent accuracy | All eight parents | Value accuracy | Whole state | Direct relations | Value-derived relations |',
        '|---|---|---|---:|---:|---:|---:|---:|---:|']
    def fmt(v):return '' if v is None else f'{100*v:.2f}%'
    for name,model in result['models'].items():
        for row in model['readouts']:
            numbers=[fmt(row[key]) for key in ('parent_accuracy','whole_parent_accuracy','value_accuracy','whole_state_accuracy','direct_relations','value_derived_relations')]
            text.append('| '+' | '.join([name,('initialization','last assignment','answer preparation')[row['site']],row['backend'],*numbers])+' |')
    text+=['','Direct relation scores are four-family macro balanced accuracies;50% is the constant-prediction reference when both classes exist. Arithmetic-written values and whole graphs are poorly recovered under these global linear readouts. The eight ordered-parent metric is harder than the earlier four-copy-parent task and is not directly comparable. Failure here does not establish representational absence. Source AST tracking and source execution remain100% oracle ceilings; character readouts are a limited source comparator.','',
        '| Model | DEV query type | Cases | Correct | Accuracy | Invalid | Families |','|---|---|---:|---:|---:|---:|---:|']
    for name,model in result['models'].items():
        for key,cell in model['behavior_development'].items():
            text.append(f"| {name} | {key} | {cell['rows']} | {cell['correct']} | {fmt(cell['accuracy'])} | {cell['invalid']} | {cell['structural_families']} |")
    text+=['','The arithmetic-written and untouched-literal strata were required for interpretation in revision3 before model collection. These are descriptive row accuracies; they do not treat relatives as independent trials or claim new significance. The original full results retain fixed-fit family intervals for graph/value contrasts.','',
        'Next decisions: inspect per-operand/version errors before interpreting zero whole-graph accuracy; compare the other archived layers under a separately declared follow-up; evaluate position-conditioned readouts and stronger source parsing controls; seek a reliable computed regime before causal patching or unfamiliar-program forecasts. Preserve these nominated-layer negative findings. Do not turn a layer search into untouched confirmation.','',
        '[Plan](arithmetic_graph_overnight_20261029_plan_v3.md) · [Validation](arithmetic_graph_overnight_debug_v1.md) · [Source coverage](arithmetic_graph_source_readiness_v1.md) · [Execution](arithmetic_graph_overnight_20261029_status_v3.md)','']
    (ROOT/'reports/binding/arithmetic_graph_overnight_findings_v1.md').write_text('\n'.join(text))
    print(json.dumps({name:model['behavior_development'] for name,model in result['models'].items()},indent=2))


if __name__=='__main__':main()
