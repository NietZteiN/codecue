"""Publish completed fixed-target query diagnostics from pinned metadata only.

No prediction/score NPZ, source/prepared records, coefficients, activations,
tokenizer or model is opened. --self-test uses synthetic metadata exclusively.
Default publication requires both completed analysis and prediction replay proof.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
import hashlib
import io
from itertools import product
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile

REL=Path('artifacts/binding/schedule_followup/20261028_v1')
ROLE='discovery_schedule_score_review_v1'
PUB_ROLE='discovery_schedule_score_publication_v1'
SNAPSHOT='76f592842abcad4d62c63857'
SOURCE_SHA='61c7104734cf8d7d4c5868983550bdf3a3cfe6f41dd89eca448d52fe191b7f5d'
MODELS=('llama8b','codellama34b')
LABELS={'llama8b':'Llama 3.1 8B','codellama34b':'CodeLlama 34B'}
LAYERS={'llama8b':(8,16,24,31),'codellama34b':(12,24,36,47)}
TASKS=('current_definition','current_version')
TASK_LABELS={'current_definition':'Current defining statement','current_version':'Current version number'}
METHODS=('direct','training_prior','random_prefix_control')
SITES=(3,7,8);SEEDS=(17,29,43);MAX_JSON=64*1024**2
INPUTS={}
LIMITATIONS=[
 'Posthoc discovery after the aggregate results were known; no untouched confirmation or historical reliability-gate rescue.',
 'Every fixed target slot is held constant across its exact body’s four queried variables; this is not a comparison between different target slots.',
 'There are 174 DEV assignment bodies and five graph families. Each pooled point contains 696 dependent body/target units, not 696 independent bodies.',
 'The three weighting seeds, numeric/lexical/query relatives and source bodies are dependent; no new confidence interval, bootstrap or favorable layer selection is used.',
 'Site7 precedes the query and is a placebo. Padding or numerical prediction differences there cannot be attributed to unseen query text.',
 'Site8 observes the queried identifier; a saved-readout effect is decoder-specific query sensitivity, not natural causal use or a state-tracking mechanism.',
 'Source-keyed sham targets have different class marginals and need not form lawful SSA graphs; their effects are a separate task.',
 'Stored margins are unsigned top-two class-score gaps, not true-target margins; ridge scores are uncalibrated.',
 'Version3 is absent from original DEV, version4 appears only in slot0 and slot1 has constant version2; this follow-up does not repair that domain coverage.',
 'Statement-index definition heads do not decode complete natural variable@version identities.',
]


def need(value,message):
 if not value:raise ValueError(message)


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def close(a,b):return isinstance(a,(int,float)) and isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)


def sha(value):return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def workspace():
 for parent in Path(__file__).resolve().parents:
  if (parent/REL/'execution_source_v1.json').is_file() and (parent/'src/codecue/binding').is_dir():return parent
  manifest=parent/'frozen_manifest.json'
  if manifest.is_file():
   candidate=Path(json.loads(manifest.read_text())['workspace_root']).resolve()
   if (candidate/REL/'execution_source_v1.json').is_file():return candidate
 raise ValueError('Cannot resolve the original follow-up workspace independently of cwd')


def inside(root,path):
 path=Path(path);path=(root/path).resolve() if not path.is_absolute() else path.resolve()
 need(root in path.parents,'Publication path must remain in the workspace');return path


def metadata_bytes(root,path,expected=None):
 path=inside(root,path)
 need(path.suffix in ('.json','.md','.py'),'Only JSON/report/script metadata may be opened; all arrays and record banks are excluded')
 need(path.is_file() and path.stat().st_size<=MAX_JSON,'Bounded completed metadata required: '+str(path))
 with path.open('rb') as stream:data=stream.read(MAX_JSON+1)
 need(len(data)<=MAX_JSON,'Metadata grew beyond byte bound')
 entry=dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
 need(INPUTS.setdefault(entry['path'],entry)==entry,'Input changed during publication')
 if expected is not None:
  if isinstance(expected,str):need(entry['sha256']==expected,'Metadata SHA256 differs: '+str(path))
  else:need(entry['sha256']==expected['sha256'] and entry['bytes']==expected['bytes']
   and path==inside(root,expected['path']),'Pinned metadata differs: '+str(path))
 return data


def read(root,path,expected=None):
 need(Path(path).suffix=='.json','JSON metadata object required')
 result=json.loads(metadata_bytes(root,path,expected));need(isinstance(result,dict),'Metadata object required');return result


def zero_work(value):
 need(all(value.get(key)==0 for key in ('new_fits','new_model_queries','parameters_reapplied'))
  and value.get('generated_holdouts_opened') is False,'Zero-query/fit/parameter-application contract differs')


def validate_point(point,bodies,units,expected_groups=None):
 need(point['matched_bodies']==bodies and point['comparison_units']==units
  and point['queried_total']==units and point['unqueried_total']==3*units,'Bodies, fixed-target units or queried denominators differ')
 q,u=point['queried_correct'],point['unqueried_correct']
 need(type(q) is int and type(u) is int and 0<=q<=units and 0<=u<=3*units,'Invalid paired query correctness counts')
 need(close(point['queried_accuracy'],q/units) and close(point['unqueried_accuracy'],u/(3*units))
  and close(point['effect'],q/units-u/(3*units)),'Query effect differs from the preserved counts')
 if expected_groups is not None:
  groups=point['per_group'];need(set(groups)==set(expected_groups),'All five DEV graph families must remain represented')
  for group,item in groups.items():validate_point(item,expected_groups[group]['bodies'],expected_groups[group]['units'])
  need(sum(g['comparison_units'] for g in groups.values())==units
   and sum(g['matched_bodies'] for g in groups.values())==bodies
   and sum(g['queried_correct'] for g in groups.values())==q
   and sum(g['unqueried_correct'] for g in groups.values())==u,'Per-family counts do not cover the paired population')
  need(close(point['group_macro_effect'],statistics.mean(g['effect'] for g in groups.values())),'Equal-family query effect differs')


def bank_name(backend,layer,site,seed):return f'{backend}_layer{layer}_site{site}_seed{seed}'


def extract(result,summary):
 for value in (result,summary):
  need(value['status']=='complete_exploratory' and value['evaluation_role']==ROLE,'Completed matching analysis metadata required')
  zero_work(value)
  need(value['score_banks']==90 and value['development_rows_per_bank']==696
   and value['development_prediction_rows']==62640 and value['saved_score_rows_checked']==181440
   and value['matched_bodies']==174 and value['graph_groups']==5,'Complete 90-bank DEV accounting required')
 need(result['original_metrics_exact'] is True,'Original metric agreement is required')
 expected={(model,backend,layer,site,seed) for model in MODELS for site in SITES
  for backend,layer in [('hidden',layer) for layer in LAYERS[model]]+[('surface',-1)] for seed in SEEDS}
 observed=set();rows=[];group_units=None
 for cell in result['cells']:
  key=tuple(cell[k] for k in ('model','backend','layer','site','seed'))
  need(key in expected and key not in observed,'Undeclared or duplicate score diagnostic bank');observed.add(key)
  need(cell['name']==bank_name(*key[1:]) and cell['original_metrics_exact'] is True
   and set(cell['methods'])==set(METHODS),'Fixed diagnostic bank identity/method inventory differs')
  for method in METHODS:
   effects=cell['methods'][method]['fixed_target_query_effects'];need(set(effects)==set(TASKS),'Both fixed-target diagnostic tasks required')
   for task in TASKS:
    value=effects[task];point=value['pooled_fixed_target_comparisons']
    need(set(value['fixed_target_slots'])=={'0','1','2','3'},'All four fixed target slots required')
    if group_units is None:
     need(len(point['per_group'])==5,'Five DEV graph families required')
     group_units={g:dict(bodies=p['matched_bodies'],units=p['comparison_units']) for g,p in point['per_group'].items()}
     need(sorted(p['units'] for p in group_units.values())==[24,24,72,192,384]
      and all(p['units']==4*p['bodies'] for p in group_units.values()),'Original DEV graph-family populations differ')
    validate_point(point,174,696,group_units)
    slot_groups={g:dict(bodies=p['bodies'],units=p['bodies']) for g,p in group_units.items()}
    for p in value['fixed_target_slots'].values():validate_point(p,174,174,slot_groups)
    need(close(point['effect'],statistics.mean(p['effect'] for p in value['fixed_target_slots'].values()))
     and close(point['group_macro_effect'],statistics.mean(p['group_macro_effect'] for p in value['fixed_target_slots'].values())),'Pooled fixed-target effect differs from four equally weighted target slots')
    rows.append(dict(model=key[0],backend=key[1],layer=key[2],site=key[3],seed=key[4],method=method,task=task,
     **{k:v for k,v in point.items() if k!='per_group'},effect_percentage_points=100*point['effect'],
     group_macro_effect_percentage_points=100*point['group_macro_effect'],per_graph_counts=point['per_group'],fixed_target_slots=value['fixed_target_slots']))
 need(observed==expected and len(rows)==540,'All 540 query-effect cells must be retained')
 for model,backend,site,method,task in product(MODELS,('hidden','surface'),(7,8),METHODS,TASKS):
  selected=[r for r in rows if (r['model'],r['backend'],r['layer'],r['site'],r['method'],r['task'])
   ==(model,backend,24 if backend=='hidden' else -1,site,method,task)]
  need(len(selected)==3 and {r['seed'] for r in selected}==set(SEEDS),'All three primary seeds required')
  p=summary['primary'][model][backend][str(site)][method][task]
  need(close(p['effect'],statistics.mean(r['effect'] for r in selected))
   and close(p['group_macro_effect'],statistics.mean(r['group_macro_effect'] for r in selected))
   and p['matched_bodies_per_seed']==174 and p['fixed_target_comparisons_per_seed']==696
   and p['seeds']==list(SEEDS),'Primary mean-seed summary differs from complete effect cells')
 return rows,group_units


def load(root):
 base=root/REL;analysis=base/'analysis'
 need((analysis/'completion_manifest_v1.json').is_file() and (analysis/'prediction_replay_review_v1.json').is_file(),
  'Publication incomplete: completed analysis and actual prediction-replay proof are required; no partial publication is written')
 receipt=read(root,analysis/'completion_manifest_v1.json')
 need(receipt['status']=='complete_exploratory' and receipt['evaluation_role']==ROLE and receipt['score_banks']==90,'Completed score-review receipt required');zero_work(receipt)
 source=receipt['source'];need(source['snapshot_id']==SNAPSHOT and source['source_sha256']==SOURCE_SHA,'Frozen posthoc source identity differs')
 snapshot=inside(root,source['snapshot']);frozen=read(root,snapshot/'frozen_manifest.json',source['frozen_manifest_sha256'])
 need(frozen['snapshot_id']==SNAPSHOT and frozen['code']['source_sha256']==SOURCE_SHA,'Frozen manifest differs')
 profile='configs/binding/schedule_followup_20261028_v1/score_review.json'
 cfg=read(root,snapshot/profile,frozen['config_files'][profile]);need(digest(cfg)==receipt['config_hash'] and cfg['evaluation_role']==ROLE,'Frozen analysis profile differs')
 need(inside(root,cfg['run_dir'])==analysis,'Analysis output folder differs')
 expected={model+'_'+bank_name(backend,layer,site,seed):analysis/f'predictions_{model}_{bank_name(backend,layer,site,seed)}.npz'
  for model in MODELS for site in SITES for backend,layer in [('hidden',l) for l in LAYERS[model]]+[('surface',-1)] for seed in SEEDS}
 expected.update(registration=analysis/'registration.json',results=analysis/'results_v1.json',summary=analysis/'summary.json',audit=analysis/'audit.json',report=inside(root,cfg['report']))
 inventory=receipt['artifacts'];need(set(inventory)==set(expected),'Ninety prediction-bank and five metadata inventory entries required')
 for name,path in expected.items():
  entry=inventory[name]
  need(set(entry)=={'path','sha256','bytes'} and inside(root,entry['path'])==path and sha(entry['sha256'])
   and type(entry['bytes']) is int and entry['bytes']>0,'Prediction/metadata pin inventory differs')
  if path.suffix!='.npz':metadata_bytes(root,path,entry)
 result=read(root,analysis/'results_v1.json',inventory['results']);summary=read(root,analysis/'summary.json',inventory['summary'])
 registration=read(root,analysis/'registration.json',inventory['registration']);audit=read(root,analysis/'audit.json',inventory['audit'])
 need(registration['config']==cfg and registration['source']==source and registration['config_hash']==receipt['config_hash'], 'Analysis registration differs')
 for value in (result,summary,audit):need(value['config_hash']==receipt['config_hash'],'Analysis metadata configuration differs')
 need(result['source']==source and audit['status']=='passed' and audit['score_banks']==90
  and audit['original_metrics_exact'] is True and audit['prediction_banks_reopened_and_checked'] is True,'Actual completed diagnostic audit required');zero_work(audit)
 proof=read(root,analysis/'prediction_replay_review_v1.json')
 need(proof['status']=='passed' and proof['evaluation_role']==ROLE and proof['config_hash']==receipt['config_hash']
  and proof['source']==source and proof['score_banks']==90 and proof['prediction_rows']==62640
  and proof['all_diagnostics_recomputed'] is True and proof['original_score_banks_reopened'] is False
  and proof['activation_arrays_opened'] is False and proof['coefficient_arrays_opened'] is False,'Completed prediction replay proof required');zero_work(proof)
 for cell in result['cells']:
  name=cell['model']+'_'+cell['name'];need(cell['prediction_bank']==inventory[name],'Scientific prediction-bank pin differs from receipt')
  identity=cell['prediction_identity'];need(identity['model']==cell['model'] and identity['bank_name']==cell['name']
   and identity['evaluation_role']==ROLE and identity['config_hash']==receipt['config_hash']
   and identity['input_bank']==cell['original_score_bank'],'Prediction provenance identity differs')
 rows,groups=extract(result,summary)
 return receipt,result,summary,rows,groups


def csv_data(rows):
 columns=['model','backend','layer','site','seed','method','task','matched_bodies','comparison_units',
  'queried_correct','queried_total','unqueried_correct','unqueried_total','queried_accuracy','unqueried_accuracy',
  'effect','effect_percentage_points','group_macro_effect','group_macro_effect_percentage_points','per_graph_counts_json','fixed_target_slots_json']
 stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore',lineterminator='\n');writer.writeheader()
 for row in sorted(rows,key=lambda r:tuple(r[k] for k in ('model','backend','layer','site','seed','method','task'))):
  writer.writerow(dict(row,per_graph_counts_json=json.dumps(row['per_graph_counts'],sort_keys=True,separators=(',',':')),
   fixed_target_slots_json=json.dumps(row['fixed_target_slots'],sort_keys=True,separators=(',',':'))))
 return stream.getvalue().encode()


def figure_values(rows):
 values={}
 def point(model,task,backend,layer,site,method):
  selected=[r for r in rows if (r['model'],r['task'],r['backend'],r['layer'],r['site'],r['method'])==(model,task,backend,layer,site,method)]
  need(len(selected)==3 and {r['seed'] for r in selected}==set(SEEDS),'Complete figure seed support required')
  return 100*statistics.mean(r['group_macro_effect'] for r in selected)
 for model,task in product(MODELS,TASKS):
  prior=[point(model,task,'hidden',layer,8,'training_prior') for layer in LAYERS[model]]
  need(all(close(prior[0],v) for v in prior),'TRAIN-only prior unexpectedly depends on hidden layer')
  values[model+'_'+task]=dict(model=model,task=task,layers=list(LAYERS[model]),
   hidden_postquery_direct=[point(model,task,'hidden',layer,8,'direct') for layer in LAYERS[model]],
   hidden_prequery_direct=[point(model,task,'hidden',layer,7,'direct') for layer in LAYERS[model]],
   hidden_postquery_sham=[point(model,task,'hidden',layer,8,'random_prefix_control') for layer in LAYERS[model]],
   surface_postquery_direct=point(model,task,'surface',-1,8,'direct'),training_prior=prior[0])
 return values


def figure_bytes(values):
 import matplotlib
 matplotlib.use('Agg',force=True)
 matplotlib.rcParams.update({'svg.hashsalt':'schedule_score_review_v1','font.family':'DejaVu Sans','font.size':10})
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(12,8),sharey=True)
 allpoints=[v for p in values.values() for k in ('hidden_postquery_direct','hidden_prequery_direct','hidden_postquery_sham') for v in p[k]]
 allpoints += [p[k] for p in values.values() for k in ('surface_postquery_direct','training_prior')]
 lower=min(0,min(allpoints));upper=max(0,max(allpoints));pad=max(1,(upper-lower)*.12)
 for i,model in enumerate(MODELS):
  for j,task in enumerate(TASKS):
   ax=axes[i,j];p=values[model+'_'+task];x=p['layers']
   ax.plot(x,p['hidden_postquery_direct'],color='#2166ac',marker='o',lw=2,label='Hidden direct · after query')
   ax.plot(x,p['hidden_prequery_direct'],color='#666666',marker='s',ls='--',lw=1.7,label='Hidden direct · before query')
   ax.plot(x,p['hidden_postquery_sham'],color='#d47524',marker='^',ls=':',lw=1.8,label='Hidden sham · after query')
   ax.axhline(p['surface_postquery_direct'],color='#087e72',ls='--',lw=1.6,label='Text direct · after query')
   ax.axhline(p['training_prior'],color='#222222',ls='-.',lw=1.1,label='TRAIN prior')
   ax.axvline(24,color='#9e8eb7',ls=':',lw=1.1,zorder=0)
   ax.set_xticks(x);ax.set_ylim(lower-pad,upper+pad);ax.set_xlabel('Captured decoder layer (24 nominated)')
   ax.set_title(LABELS[model]+' · '+TASK_LABELS[task],fontsize=11)
   ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
 handles,labels=axes[0,0].get_legend_handles_labels()
 fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.54,.032),fontsize=9)
 fig.supylabel('Equal-family queried-minus-other effect (percentage points)',x=.016,fontsize=11)
 fig.suptitle('Fixed-target query sensitivity of completed readouts',y=.975,fontsize=15)
 fig.text(.53,.012,'Mean of three dependent weighting seeds · five DEV families · no confidence intervals',ha='center',fontsize=9)
 fig.subplots_adjust(left=.09,right=.985,bottom=.19,top=.91,wspace=.20,hspace=.38)
 png=io.BytesIO();svg=io.BytesIO()
 fig.savefig(png,format='png',dpi=170,metadata={'Software':'CodeCue deterministic saved-score publisher'})
 fig.savefig(svg,format='svg',metadata={'Date':None,'Creator':'CodeCue deterministic saved-score publisher'})
 plt.close(fig);return png.getvalue(),svg.getvalue(),matplotlib.__version__


def report_bytes(summary):
 lines=['# Fixed-target query sensitivity from completed saved scores','',
  'The posthoc saved-score analysis and prediction replay audit completed. Every original score bank reproduced its original scientific metrics. '
  'This publication reads only pinned metadata; it performs no score analysis rerun, model query, parameter application or fitting.','',
  'Each comparison holds the target slot and its truth fixed across all four final queries on an identical eight-assignment body. '
  'Each pooled point uses 174 DEV bodies and 696 body/target comparison units: one query of that target versus its other three queries. '
  'Five unequal graph families remain the structural units. This avoids comparing different queried targets, while retaining the dependence among related cases.','',
  '![All-layer equal-family query effects](figures/schedule_score_review_v1.svg)','',
  'The four panels retain all captured layers. Site 7 precedes the query; site 8 observes it. The vertical line marks the previously nominated layer 24. '
  'Curves average three weighting seeds; overlapping zero lines remain represented. No confidence interval, bootstrap or favorable layer selection is added.','',
  '| Model | Backend | Site | Method | Definition effect: rows / families (pp) | Version effect: rows / families (pp) |',
  '|---|---|---:|---|---:|---:|']
 for model,backend,site,method in product(MODELS,('hidden','surface'),('7','8'),METHODS):
  points=summary['primary'][model][backend][site][method]
  a,b=points['current_definition'],points['current_version']
  lines.append(f"| {LABELS[model]} | {backend} | {site} | {method} | {100*a['effect']:.3f} / {100*a['group_macro_effect']:.3f} | {100*b['effect']:.3f} / {100*b['group_macro_effect']:.3f} |")
 lines+=['','[query_effects_v1.csv](../../artifacts/binding/schedule_followup/20261028_v1/query_effects_v1.csv) retains all 540 '
  'model/backend/layer/site/seed/method/task cells, including site 3, every target-slot comparison and per-graph correctness/denominator counts. '
  'The original analysis retains class confusion, joint correctness mass and pre-query prediction/score disagreements. Stored margins are unsigned '
  'top-two class-score gaps, not true-target margins.','',
  'The source bank still has no final DEV version-3 examples, version 4 only in slot 0, and constant version 2 in slot 1. '
  'A nonzero final-boundary effect measures sensitivity of this saved decoder to the queried identifier; it does not establish a natural causal '
  'binding or tracking mechanism. Any pre-query disagreement must retain its numerical/padding qualification. Source-keyed sham labels are a '
  'different task with different marginals, rather than a matched lawful graph control.','',
  'All 90 score banks supplied 181,440 saved-score case rows and 62,640 DEV prediction rows. The CPU audit rederived actual-source truth/visibility '
  'and recomputed the diagnostics from prediction-only banks. This publisher opens none of those NPZs, original activations, coefficients or source records. '
  '[publication_review_v1.json](../../artifacts/binding/schedule_followup/20261028_v1/publication_review_v1.json) pins the inputs and every new output.','',
  *['- '+value for value in LIMITATIONS],'']
 return '\n'.join(lines).encode()


def publish(path,data):
 path=Path(path);need(not path.is_symlink(),'Immutable output must not follow a symlink');path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():need(path.is_file() and path.read_bytes()==data,'Immutable publication differs: '+str(path));return
 temporary=None
 try:
  with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.'+path.name,suffix='.pending',delete=False) as stream:
   temporary=Path(stream.name);stream.write(data);stream.flush();os.fsync(stream.fileno())
  try:os.link(temporary,path)
  except FileExistsError:need(not path.is_symlink() and path.read_bytes()==data,'Concurrent publication differs')
 finally:
  if temporary is not None and temporary.exists():temporary.unlink()


def publication(root):
 INPUTS.clear();receipt,result,summary,rows,groups=load(root)
 metadata_bytes(root,Path(__file__).resolve());script=INPUTS[str(Path(__file__).resolve().relative_to(root))]
 values=figure_values(rows);png,svg,version=figure_bytes(values);png2,svg2,_=figure_bytes(values)
 need((png,svg)==(png2,svg2),'Repeated figure rendering was not byte identical')
 base=root/REL;outputs={base/'query_effects_v1.csv':csv_data(rows),
  root/'reports/binding/schedule_score_review_summary_v1.md':report_bytes(summary),
  root/'reports/binding/figures/schedule_score_review_v1.png':png,
  root/'reports/binding/figures/schedule_score_review_v1.svg':svg}
 review=dict(status='passed',evaluation_role=PUB_ROLE,publisher_script=script,
  input_pins=sorted(INPUTS.values(),key=lambda p:p['path']),output_pins=[dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)) for path,data in outputs.items()],
  query_effect_cells=540,matched_dev_bodies=174,fixed_target_comparison_units_per_cell=696,graph_families=5,
  prediction_bank_inventory_entries_checked=90,prediction_banks_opened=False,figure_data=values,development_group_units=groups,
  checks=dict(completed_prediction_replay_proof_required=True,all_540_query_cells_preserved=True,
   all_four_target_slots_and_graph_counts_retained=True,primary_layer24_seed_means_recomputed=True,
   no_prediction_or_original_npz_opened=True,repeated_png_svg_byte_identical=True),
  plotting_version=version,reproduction='Every rerun regenerates outputs and must match existing bytes exactly.',
  new_model_queries=0,new_fits=0,parameters_reapplied=0,new_bootstraps=0,raw_activation_arrays_opened=False,
  coefficient_arrays_opened=False,source_or_response_records_opened=False,generated_holdouts_opened=False,limitations=LIMITATIONS)
 payload=(json.dumps(review,sort_keys=True,indent=2,allow_nan=False)+'\n').encode();need(len(payload)<=8*1024**2,'Compact publication review required')
 outputs[base/'publication_review_v1.json']=payload
 existed=all(path.is_file() for path in outputs)
 for path,data in outputs.items():need(not path.is_symlink() and (not path.exists() or path.read_bytes()==data),'Immutable publication differs before any write: '+str(path))
 for path,data in outputs.items():publish(path,data)
 return dict(status='byte_identical_reproduction' if existed else 'published',query_effect_cells=540,prediction_banks_opened=False,new_model_queries=0,new_fits=0)


def synthetic_point(groups,units_per_body=4,positive=False):
 per_group={}
 for g,bodies in groups.items():
  n=bodies*units_per_body;q=n if positive else n//2;u=3*(n//2)
  per_group[g]=dict(matched_bodies=bodies,comparison_units=n,queried_correct=q,queried_total=n,unqueried_correct=u,
   unqueried_total=3*n,queried_accuracy=q/n,unqueried_accuracy=u/(3*n),effect=q/n-u/(3*n))
 n=sum(v['comparison_units'] for v in per_group.values());q=sum(v['queried_correct'] for v in per_group.values());u=sum(v['unqueried_correct'] for v in per_group.values())
 return dict(matched_bodies=sum(groups.values()),comparison_units=n,queried_correct=q,queried_total=n,
  unqueried_correct=u,unqueried_total=3*n,queried_accuracy=q/n,unqueried_accuracy=u/(3*n),effect=q/n-u/(3*n),
  per_group=per_group,group_macro_effect=statistics.mean(v['effect'] for v in per_group.values()))


def synthetic():
 groups={'a':48,'b':96,'c':6,'d':18,'e':6};cells=[]
 for model in MODELS:
  for site in SITES:
   for backend,layer in [('hidden',layer) for layer in LAYERS[model]]+[('surface',-1)]:
    for seed in SEEDS:
     methods={}
     for method in METHODS:
      effects={}
      for task in TASKS:
       positive=site==8 and method=='direct'
       effects[task]=dict(pooled_fixed_target_comparisons=synthetic_point(groups,4,positive),
        fixed_target_slots={str(slot):synthetic_point(groups,1,positive) for slot in range(4)})
      methods[method]={'fixed_target_query_effects':effects}
     cells.append(dict(model=model,backend=backend,layer=layer,site=site,seed=seed,name=bank_name(backend,layer,site,seed),original_metrics_exact=True,methods=methods))
 common=dict(status='complete_exploratory',evaluation_role=ROLE,score_banks=90,development_rows_per_bank=696,
  development_prediction_rows=62640,saved_score_rows_checked=181440,matched_bodies=174,graph_groups=5,
  new_fits=0,new_model_queries=0,parameters_reapplied=0,generated_holdouts_opened=False)
 result=dict(common,original_metrics_exact=True,cells=cells);primary={}
 for model in MODELS:
  primary[model]={}
  for backend in ('hidden','surface'):
   primary[model][backend]={}
   for site in (7,8):
    primary[model][backend][str(site)]={method:{task:dict(effect=.5 if site==8 and method=='direct' else 0.,
     group_macro_effect=.5 if site==8 and method=='direct' else 0.,seeds=list(SEEDS),matched_bodies_per_seed=174,fixed_target_comparisons_per_seed=696) for task in TASKS} for method in METHODS}
 return result,dict(common,primary=primary)


def self_test():
 result,summary=synthetic();rows,_=extract(result,summary);need(len(rows)==540,'Synthetic row coverage failed')
 need(len(list(csv.DictReader(io.StringIO(csv_data(rows).decode()))))==540,'CSV lost query cells')
 values=figure_values(rows);png,svg,_=figure_bytes(values);png2,svg2,_=figure_bytes(values);need((png,svg)==(png2,svg2),'Synthetic figure repeatability failed')
 for mutation in ('missing_bank','wrong_bodies','wrong_macro','missing_slot','changed_summary'):
  r,s=deepcopy(result),deepcopy(summary)
  if mutation=='missing_bank':r['cells'].pop()
  elif mutation=='changed_summary':s['primary']['llama8b']['hidden']['8']['direct']['current_definition']['effect']=.9
  else:
   effects=r['cells'][0]['methods']['direct']['fixed_target_query_effects']['current_definition']
   if mutation=='wrong_bodies':effects['pooled_fixed_target_comparisons']['matched_bodies']=696
   if mutation=='wrong_macro':effects['pooled_fixed_target_comparisons']['group_macro_effect']=.9
   if mutation=='missing_slot':effects['fixed_target_slots'].pop('3')
  try:extract(r,s)
  except ValueError:pass
  else:raise ValueError('Corrupt synthetic case was accepted: '+mutation)
 with tempfile.TemporaryDirectory(prefix='score-publication-') as temp:
  root=Path(temp);path=root/'out.json';publish(path,b'fixed\n');publish(path,b'fixed\n')
  try:publish(path,b'changed\n')
  except ValueError:pass
  else:raise ValueError('Immutable publication conflict accepted')
  try:metadata_bytes(root,root/'predictions.npz')
  except ValueError:pass
  else:raise ValueError('Prediction-array input was accepted')
 return dict(status='passed_synthetic_self_test',checks=10,query_effect_cells=540,scientific_inputs_opened=False,
  actual_publication_executed=False,png_svg_repeated_bytes_identical=True,new_model_queries=0,new_fits=0)


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 try:result=self_test() if args.self_test else publication(workspace())
 except (ValueError,KeyError,OSError) as exc:
  print(json.dumps(dict(status='publication_not_written',error=f'{type(exc).__name__}: {exc}')),file=sys.stderr);raise SystemExit(2)
 print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
