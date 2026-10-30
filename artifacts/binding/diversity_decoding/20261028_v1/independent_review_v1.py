"""Independently review completed diversity execution using pinned metadata only.

Both capture/readout receipts and saved-parameter replay proofs must exist. Binary
artifacts are streamed only for SHA256; no arrays, responses, model or fitting
code is loaded. --self-test uses synthetic metadata and never opens outcomes.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
from itertools import product
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

REL=Path('artifacts/binding/diversity_decoding/20261028_v1')
GENERATION_SNAPSHOT='76f592842abcad4d62c63857'
GENERATION_SOURCE_SHA='61c7104734cf8d7d4c5868983550bdf3a3cfe6f41dd89eca448d52fe191b7f5d'
MANIFEST_SHA='e6a778b1bdab4dbb7666795a9baed63a4410184b4d0a9458afa8ce3ce13ee12f'
DATA_SHA='d43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1'
MODELS={'llama8b':dict(model='meta-llama/Llama-3.1-8B-Instruct',revision='0e9e39f249a16976918f6564b8830bc894c89659',layers=[8,16,24,31],hidden=4096,batch=256,reference_batch=128,boundary='native'),
 'codellama34b':dict(model='codellama/CodeLlama-34b-Instruct-hf',revision='d4c1c474abcacd32d2a6eda45f9811d38c83e93d',layers=[12,24,36,47],hidden=8192,batch=128,reference_batch=64,boundary='codellama_official_boundary_v1')}
SITES=(3,7,8);SEEDS=(17,29,43);METHODS=('direct','training_prior','random_prefix_control')
DOMAINS={'current_definition':tuple(range(8)),'current_version':(1,2,3,4),'copy_parent':tuple(range(8))}
PINS={};MAX_JSON=192*1024**2


def need(value,message):
 if not value:raise ValueError(message)


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def root_path():
 for parent in Path(__file__).resolve().parents:
  if (parent/REL/'execution_source_v1.json').is_file() and (parent/'src/codecue/binding').is_dir():return parent
  frozen=parent/'frozen_manifest.json'
  if frozen.is_file():
   candidate=Path(json.loads(frozen.read_text())['workspace_root']).resolve()
   if (candidate/REL/'execution_source_v1.json').is_file():return candidate
 raise ValueError('Cannot resolve original diversity workspace')


def path_in(root,path):
 path=Path(path);path=(root/path).resolve() if not path.is_absolute() else path.resolve()
 need(root in path.parents,'Artifact must remain inside the schedule workspace')
 return path


def pin(root,path,expected=None):
 path=path_in(root,path);need(path.is_file(),'Required completed artifact missing: '+str(path))
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for block in iter(lambda:stream.read(1024**2),b''):h.update(block)
 entry=dict(path=str(path.relative_to(root)),sha256=h.hexdigest(),bytes=path.stat().st_size)
 if expected is not None:
  if isinstance(expected,str):need(entry['sha256']==expected,'SHA256 mismatch: '+str(path))
  else:
   need(entry['sha256']==expected['sha256'] and ('bytes' not in expected or entry['bytes']==expected['bytes'])
    and path==path_in(root,expected['path']),'Pinned artifact mismatch: '+str(path))
 need(PINS.setdefault(entry['path'],entry)==entry,'Input changed during metadata review')
 return entry


def read(root,path,expected=None):
 path=path_in(root,path);need(path.suffix=='.json' and path.stat().st_size<=MAX_JSON,'Bounded JSON metadata required')
 pin(root,path,expected);value=json.loads(path.read_bytes());need(isinstance(value,dict),'Metadata object required');return value


def close(left,right):
 return left is None and right is None or isinstance(left,(int,float)) and isinstance(right,(int,float)) and math.isclose(left,right,abs_tol=1e-12,rel_tol=1e-12)


def expected_heads():return {f'{family}/{slot}':(family,classes) for family,classes in DOMAINS.items() for slot in range(4)}


def group_statistics(item,expected_groups,n):
 need(item['n']==n,'Defined DEV denominator was dropped')
 groups=item['per_group'];need(set(groups)==(set(expected_groups) if n else set()),'Missing or unexpected DEV graph family')
 need(sum(v['n'] for v in groups.values())==n,'Per-group denominator differs')
 if n:
  need(all(v['n']==expected_groups[g] for g,v in groups.items()),'DEV family size differs')
  need(all(isinstance(v['accuracy'],(int,float)) and 0<=v['accuracy']<=1 for v in groups.values()),'Invalid group accuracy')
  weighted=sum(v['n']*v['accuracy'] for v in groups.values())/n
  macro=statistics.mean(v['accuracy'] for v in groups.values())
  need(close(item['accuracy'],weighted) and close(item['group_macro_accuracy'],macro),'Published row/group mean differs from per-group metrics')
 else:need(item['accuracy'] is None and item['group_macro_accuracy'] is None,'Undefined task was scored as success')


def review_metrics(metrics,site,expected_groups,columns,marginals,real_task=True):
 need(set(metrics)=={'boolean_cells','categorical_heads','boolean_families','whole_categorical_families'},'Exact metric inventory required')
 heads=metrics['categorical_heads'];need(set(heads)==set(expected_heads()),'Every four-head categorical family must remain reported')
 by_head={}
 for column in columns:
  if column['kind']=='categorical':by_head.setdefault(column['head'],{})[str(column['candidate'])]=column['index']
 for name,(family,choices) in expected_heads().items():
  head=heads[name];n=0 if site==3 and family=='copy_parent' else 1440
  need(head['family']==family and set(head['classes'])==set(map(str,choices)),'Absent/unsupported categorical choices were removed')
  need(sum(c['n'] for c in head['classes'].values())==n,'Categorical class denominators differ')
  group_statistics(head,expected_groups,n)
  need(0<=head['missing_predictions']<=n,'Invalid missing-score count')
  for choice,cell in head['classes'].items():
   need(cell['n']==marginals[by_head[name][choice]]['positive_rows'],'Class counts differ from audited target marginals')
   need((cell['accuracy'] is None if not cell['n'] else isinstance(cell['accuracy'],(int,float)) and 0<=cell['accuracy']<=1),'Invalid class accuracy')
   if real_task and site in (7,8) and family=='current_version':
    need(cell['n']>0,'Every real DEV version class1..4 must remain present in every slot')
  if n:need(close(sum(c['n']*c['accuracy'] for c in head['classes'].values() if c['n'])/n,head['accuracy']),'Class-weighted accuracy differs')
  support=head['train_support']
  need(set(support['class_group_support'])==set(map(str,choices)),'TRAIN support omitted a declared class')
  need(set(support['dev_only_classes'])<=set(choices),'Invalid DEV-only class metadata')
 boolean=metrics['boolean_cells'];need({c['index'] for c in boolean}==set(range(152)) and len(boolean)==152,'Complete fixed boolean inventory required')
 for cell in boolean:
  j=cell['index'];m=marginals[j]
  need((cell['n'],cell['positives'],cell['negatives'])==(m['defined_rows'],m['positive_rows'],m['negative_rows']),'Boolean denominator/marginal mismatch')
  need(cell['positives']+cell['negatives']==cell['n'],'Boolean classes do not cover defined rows')
  need((cell['accuracy'] is None if not cell['n'] else 0<=cell['accuracy']<=1),'Invalid boolean accuracy')
  need(cell['balanced_accuracy'] is None if not cell['positives'] or not cell['negatives'] else 0<=cell['balanced_accuracy']<=1,'Invalid prevalence-aware score')
 whole=metrics['whole_categorical_families'];need(set(whole)==set(DOMAINS),'All whole-head families required')
 for family,item in whole.items():
  need(item['heads']==4,'Whole recovery dropped a categorical head')
  group_statistics(item,expected_groups,0 if site==3 and family=='copy_parent' else 1440)


def check_support(support,site):
 need(support['eligibility_split']=='train' and support['minimum_class_groups']==3
  and support['structural_groups']==45 and support['absent_domain_choices_retained'] is True
  and support['development_labels_used_for_eligibility'] is False,'TRAIN-only support contract differs')
 heads={h['head']:h for h in support['categorical_heads']};need(set(heads)==set(expected_heads()),'Complete TRAIN head support required')
 for name,(_,choices) in expected_heads().items():
  head=heads[name];need(tuple(head['candidates'])==choices and head['evaluated_choices_removed'] is False,'Support diagnostics removed candidates')
  classes=head['classes'];need(tuple(c['candidate'] for c in classes)==choices,'Per-class TRAIN inventory differs')
  observed=[c for c in classes if c['train_rows']]
  need(head['eligible_categorical']==(len(observed)>=2 and all(c['train_groups']>=3 for c in observed)),'Eligibility used more than TRAIN support')
  if site in (7,8) and name.startswith('current_version/'):
   need(len(observed)==4 and all(c['train_groups']>=15 and c['development_rows']>0 for c in classes),
    'Slot-complete version1..4 support differs from the fixed source design')


def bank_name(backend,layer,site,seed):return f'{backend}_layer{layer}_site{site}_seed{seed}'


def check_result(result,summary,profile,expected_groups):
 need(result['status']=='complete_exploratory' and result['evaluation_role']=='discovery_diversity_readouts_v1','Complete schedule result required')
 need((result['cases'],result['training_rows'],result['development_rows'],result['training_groups'],result['development_groups'])==(5760,4320,1440,45,15),'Readout cohort differs')
 need(result['new_model_queries']==0 and result['generated_holdouts_opened'] is False
  and result['oracle_target_features'] is False and result['behavioral_response_features'] is False,'Unexpected model query or target feature')
 columns=result['target_columns'];need(len(columns)==232 and [c['index'] for c in columns]==list(range(232)),'Fixed 232-column schema required')
 need(sum(c['kind']=='boolean' for c in columns)==152,'Boolean schema differs')
 for site in SITES:check_support(result['training_support'][str(site)],site)
 expected={(backend,layer,site,seed) for site in SITES for backend,layer in [('hidden',l) for l in profile['layers']]+[('surface',-1)] for seed in SEEDS}
 fits={}
 for fit in result['fits']:
  key=tuple(fit[k] for k in ('backend','layer','site','seed'));need(key not in fits,'Duplicate feature/site/seed bank')
  need(fit['name']==bank_name(*key) and fit['factorizations']==1 and fit['exact_parameter_score_replay'] is True,'Unexpected masked factorization or replay inventory')
  need(set(fit['metrics'])==set(METHODS),'All three methods required')
  control=result['control_descriptive_metadata'][str(fit['site'])][str(fit['seed'])]
  need(control['control'] is True and control['lawful_joint_ssa_graph'] is False and control['marginals_preserved'] is False,'Control semantics changed')
  for method in METHODS:
   marginals=control['control_marginals' if method=='random_prefix_control' else 'real_marginals']['development']
   need(len(marginals)==232 and [m['index'] for m in marginals]==list(range(232)),'Complete audited control/real marginals required')
   review_metrics(fit['metrics'][method],fit['site'],expected_groups,columns,marginals,method!='random_prefix_control')
  fits[key]=fit
 need(set(fits)==expected and result['fit_banks']==45 and result['factorizations']==45
  and result['parameter_replay_rows']==5760*45,'Complete 45-bank one-mask-group grid required')
 need(result['primary']['layer']==24 and result['primary']['site']==7,'Prospective primary was changed')
 need(result['protocol']['alpha']==100 and result['protocol']['seeds']==list(SEEDS)
  and result['protocol']['sites']==list(SITES) and result['protocol']['binary_threshold']==.5,'Fixed fit recipe differs')
 recomputed={};group_macro={}
 for backend in ('hidden','surface'):
  recomputed[backend]={};group_macro[backend]={}
  for method in METHODS:
   recomputed[backend][method]={};group_macro[backend][method]={}
   for family in DOMAINS:
    selected=[fits[(backend,24 if backend=='hidden' else -1,7,seed)]['metrics'][method]['whole_categorical_families'][family] for seed in SEEDS]
    recomputed[backend][method][family]=statistics.mean(x['accuracy'] for x in selected)
    group_macro[backend][method][family]=statistics.mean(x['group_macro_accuracy'] for x in selected)
    need(close(summary['primary'][backend][method][family],recomputed[backend][method][family])
     and close(summary['primary_group_macro'][backend][method][family],group_macro[backend][method][family]),'Published primary mean-seed summary differs')
 need(summary['fit_banks']==45 and summary['factorizations']==45 and summary['parameter_replay_rows']==5760*45
  and summary['new_model_queries']==0,'Compact result accounting differs')
 return dict(primary=recomputed,primary_group_macro=group_macro,fit_banks=45,factorizations=45,parameter_replay_rows=5760*45)


def source_equal(actual,expected):
 need(actual['snapshot_id']==expected['snapshot_id'] and actual['source_sha256']==expected['code'],
  'Frozen source identity differs')
 need(Path(actual['snapshot']).resolve()==Path(expected['snapshot']).resolve(),
  'Frozen source snapshot path differs')


def record_metadata(root,path,prepared=False):
 """Read bounded JSONL case identities without constructing or executing programs."""
 path=path_in(root,path);need(path.suffix=='.jsonl' and path.stat().st_size<=512*1024**2,'Bounded source/prepared metadata required')
 rows=[];seen=set()
 with path.open('rb') as stream:
  for line in stream:
   need(len(line)<=256*1024,'Bounded case metadata line required')
   if not line.strip():continue
   item=json.loads(line)
   if prepared:
    need(isinstance(item,dict) and item.get('sites')==['statement:3','statement:7','pre_answer'],
     'Prepared site inventory differs')
    item=item['record']
    need('targets' not in item and 'expected_answer' not in item,'Oracle fields leaked into prepared feature records')
   need(isinstance(item,dict) and item.get('evaluation_role')=='discovery_relationship_schedule_diversity_sources_v1',
    'Diversity source role differs')
   case=item.get('id');group=item.get('component_id');split=item.get('split');graph=item.get('canonical_graph_sha256')
   need(isinstance(case,str) and case.startswith('schedule-diversity:') and len(case)==43 and case not in seen,
    'Unique explicit diversity case identities required')
   need(isinstance(graph,str) and len(graph)==64 and all(c in '0123456789abcdef' for c in graph)
    and group=='schedule-diversity-graph:'+graph[:24] and item.get('template_id')==group
    and split in ('train','development'),'Canonical source graph/split identity differs')
   need(item.get('condition')=='neutral' and type(item.get('query_slot')) is int
    and item['query_slot'] in range(4),'Neutral four-query source metadata required')
   seen.add(case);rows.append(dict(id=case,group=group,split=split,graph=graph,query=item['query_slot']))
 need(len(rows)==5760,'Complete source/prepared case inventory required')
 pin(root,path)
 return rows


def source_cohort(root):
 manifest_path='artifacts/binding/schedule_diversity/20261028_v1/sources.manifest.json'
 manifest=read(root,manifest_path,MANIFEST_SHA)
 need(manifest['status']=='complete' and manifest['sha256']==DATA_SHA and manifest['rows']==5760
  and manifest['canonical_graph_families']==60 and manifest['split_rows']=={'train':4320,'development':1440}
  and manifest['split_canonical_graph_units']=={'train':45,'development':15}
  and manifest['canonical_graph_overlap_with_named_banks']==0
  and not any(manifest['cross_split_overlap'].values())
  and manifest['slot_complete_version_domain'] is True and manifest['independent_python_passed'] is True,
  'Pinned source diversity and overlap qualification differs')
 need(manifest['targets_prepared_only'] is True and manifest['learned_readout_compatible'] is False
  and manifest['generated_holdouts_opened'] is False and manifest['model_queries']==manifest['new_model_queries']==0,
  'Historical source-only generation contract differs')
 need(manifest['count_profiles']==[[2,1,1,0],[3,1,0,0],[2,2,0,0]]
  and manifest['fully_class_balanced'] is False
  and manifest['design_deviation']['decision_before_generation'] is True
  and manifest['design_deviation']['initial_profile_generated'] is False
  and manifest['design_deviation']['initial_profile_counted_as_new'] is False,
  'Fixed diversity profiles or exhausted initial-design accounting differs')
 old=root/'artifacts/binding/sources'/GENERATION_SNAPSHOT
 frozen=read(root,old/'frozen_manifest.json')
 need(frozen['snapshot_id']==GENERATION_SNAPSHOT and frozen['code']['source_sha256']==GENERATION_SOURCE_SHA
  and manifest['source']==frozen['code'] and digest(frozen['code']['source_files'])==GENERATION_SOURCE_SHA,
  'Original source builderS2 provenance differs')
 for name,checksum in frozen['code']['source_files'].items():pin(root,old/name,checksum)
 generation='configs/binding/relationships/schedule_diversity_generation_v1.json'
 cfg=read(root,old/generation,frozen['config_files'][generation])
 need(cfg==manifest['generation_config'] and digest(cfg)==manifest['generation_config_hash'],
  'Original frozen generation configuration differs')
 review=read(root,manifest['review'])
 need(review['source']==frozen['code'] and review['dataset_sha256']==DATA_SHA
  and review['rows']==5760 and review['canonical_graph_families']==60
  and review['split_canonical_graph_units']=={'train':45,'development':15}
  and review['train_minimum_current_version_class_graph_groups']>=15
  and review['independent_python_passed'] is True and review['new_fits']==review['new_model_queries']==0,
  'Original source review differs')
 dataset=manifest['generation_config']['dataset'];pin(root,dataset,DATA_SHA)
 rows=record_metadata(root,dataset);counts={};splits={}
 for row in rows:
  counts[row['group']]=counts.get(row['group'],0)+1
  need(splits.setdefault(row['group'],row['split'])==row['split'],'Source graph crossesTRAIN/DEV')
 need(len(counts)==60 and set(counts.values())=={96}
  and sum(s=='train' for s in splits.values())==45 and sum(s=='development' for s in splits.values())==15,
  'Sixty equal-size source graph families required')
 return dict(rows=rows,ordered_ids_sha256=digest([row['id'] for row in rows]),
  development_groups={g:n for g,n in counts.items() if splits[g]=='development'},
  original_source_snapshot=GENERATION_SNAPSHOT,original_source_sha256=GENERATION_SOURCE_SHA,
  source_manifest=manifest)


def model_review(root,model,source,frozen,cohort):
 groups=cohort['development_groups']
 profile=MODELS[model];base=root/REL/model
 cap_rel=f'configs/binding/diversity_decoding_20261028_v1/{model}_capture.json'
 out_rel=f'configs/binding/diversity_decoding_20261028_v1/{model}_readouts.json'
 snapshot=path_in(root,source['snapshot'])
 cap=read(root,snapshot/cap_rel,frozen['config_files'][cap_rel]);cfg=read(root,snapshot/out_rel,frozen['config_files'][out_rel])
 need(cap['evaluation_role']=='discovery_diversity_capture_v1' and cap['dataset_sha256']==DATA_SHA
  and cap['model']==profile['model'] and cap['model_revision']==cap['tokenizer_revision']==profile['revision']
  and cap['layers']==profile['layers'] and cap['hidden_size']==profile['hidden']
  and cap['batch_size']==profile['batch'] and cap['chunk_size']==512,'Frozen capture native geometry differs')
 need(cap.get('tokenization_mode',profile['boundary'])==profile['boundary'],'Native tokenizer boundary differs')
 pin(root,cap['dataset'],DATA_SHA)
 source_manifest=read(root,Path(cap['dataset']).with_suffix('.manifest.json'),cap['dataset_manifest_sha256'])
 need(source_manifest['sha256']==DATA_SHA and source_manifest['rows']==5760
  and source_manifest['canonical_graph_families']==60
  and source_manifest['split_canonical_graph_units']=={'train':45,'development':15}
  and source_manifest['independent_python_passed'] is True,'Actual source manifest differs')
 need(cap['dataset_manifest_sha256']==MANIFEST_SHA and source_manifest==cohort['source_manifest'],
  'Both models must use the same historical diversity source manifest')
 need(cfg['capture_config_sha256']==frozen['config_files'][cap_rel] and cfg['primary_layer']==24,'Frozen readout profile differs')
 pin(root,cfg['declared_plan'],cfg['declared_plan_sha256'])
 capdir=path_in(root,cap['run_dir']);out=path_in(root,cfg['run_dir'])
 receipt=read(root,capdir/'completion_manifest_v1.json')
 need(receipt['evaluation_role']=='discovery_diversity_capture_v1' and receipt['status']=='complete_exploratory'
  and receipt['config_hash']==digest(cap) and receipt['dataset_sha256']==DATA_SHA,'Completed matching capture receipt required')
 source_equal(receipt['source'],source)
 pin(root,snapshot/'frozen_manifest.json',receipt['source']['frozen_manifest_sha256'])
 meta={}
 names={'registration.json','preflight.json','prepared_cases.jsonl','manifest.json','summary.json','audit.json'}
 need(set(receipt['metadata'])==names,'Exact capture metadata inventory required')
 for name in names:
  entry=receipt['metadata'][name];need(path_in(root,entry['path'])==capdir/name,'Capture metadata path differs')
  pin(root,capdir/name,entry)
  if name.endswith('.json'):meta[name]=read(root,capdir/name,entry)
 prep=meta['preflight.json'];registration=meta['registration.json'];manifest=meta['manifest.json'];capture=meta['summary.json'];audit=meta['audit.json']
 need(registration['source']==prep['source']==capture['source']==audit['source']==receipt['source']
  and manifest['identity']['config']==cap and manifest['identity']['config_hash']==digest(cap),'Capture stage source/config identities differ')
 need(registration['config']==cap and registration['config_hash']==digest(cap) and prep['config_hash']==digest(cap)
  and prep['status']=='passed' and prep['cases']==5760 and prep['recipe']['tokenization_mode']==profile['boundary'],'Prepared native profile differs')
 need(prep['recipe']['dtype']=='bfloat16' and prep['recipe']['device']=='cuda' and prep['new_model_queries']==0,'Preparation queried a model or changed precision')
 need(prep['source_review']['source_rows']==5760 and prep['source_review']['components']=={'train':45,'development':15}
  and prep['source_review']['split_rows']=={'train':4320,'development':1440}
  and prep['source_review']['dataset_manifest_sha256']==cap['dataset_manifest_sha256'],'Capture source cohort/pins differ')
 need(prep['recipe']['batch_size']==profile['batch']
  and prep['source_review']['hardware_headroom_reference_batch']==profile['reference_batch']
  and prep['source_review']['ordered_case_ids_sha256']==cohort['ordered_ids_sha256'],
  'Effective/reference batch or ordered case identity differs')
 need(prep['prepared_sha256']==receipt['metadata']['prepared_cases.jsonl']['sha256'],'Prepared layout identity differs')
 prepared=record_metadata(root,capdir/'prepared_cases.jsonl',prepared=True)
 need(prepared==cohort['rows'],'Prepared capture case order/group/query identity differs from source')
 shape=[5760,3,4,profile['hidden']]
 for item in (receipt,capture,audit):
  need(item['feature_shape']==shape and item['generated_responses']==0 and item['generation_calls']==0
   and item['generated_holdouts_opened'] is False,'Capture shape or zero-generation contract differs')
 need(manifest['status']=='complete' and capture['complete'] is True and audit['status']=='passed'
  and audit['finite_float32_features'] is True and audit['new_model_queries']==0,'Capture audit incomplete')
 chunks=receipt['chunks'];need(chunks==manifest['chunks']==capture['chunks']==audit['chunks'],'Capture chunk pin inventories differ')
 need(len(chunks)==12,'Expected twelve contiguous capture chunks')
 for i,entry in enumerate(chunks):
  need(entry['first']==512*i and entry['rows']==min(512,5760-512*i),'Contiguous capture row inventory differs')
  pin(root,entry['path'],entry)
 attempts=capture['collection_attempts'];attempted=sum(a['prefill_cases_attempted'] for a in attempts);calls=sum(a['prefill_batch_calls'] for a in attempts)
 need(attempted>=5760 and calls>=math.ceil(5760/profile['batch']) and attempts[-1]['status']=='complete','Incomplete capture invocation accounting')
 need(all(a['prefill_cases_returned']<=a['prefill_cases_attempted'] for a in attempts),'Returned prefills exceed attempts')
 need(capture['new_model_queries']==receipt['new_model_queries']==attempted
  and capture['model_prefill_cases']==receipt['model_prefill_cases']==5760 and capture['prefill_batch_calls']==calls,'Distinct versus attempted prefill counters differ')
 completed=read(root,out/'completion_manifest_v1.json');need(completed['status']=='complete_exploratory'
  and completed['evaluation_role']=='discovery_diversity_readouts_v1' and completed['config_hash']==digest(cfg)
  and completed['new_model_queries']==0 and completed['generated_holdouts_opened'] is False,'Complete readout receipt required')
 source_equal(completed['fit_source'],source);source_equal(completed['capture_source'],source)
 expected={bank_name(backend,layer,site,seed):out/(bank_name(backend,layer,site,seed)+'.npz')
  for site in SITES for backend,layer in [('hidden',l) for l in profile['layers']]+[('surface',-1)] for seed in SEEDS}
 expected.update(registration=out/'registration.json',results=out/'results_v1.json',audit=out/'audit.json',summary=out/'summary.json',report=path_in(root,cfg['report']))
 need(set(completed['artifacts'])==set(expected),'Every fit bank and metadata artifact must be pinned')
 for name,path in expected.items():pin(root,path,completed['artifacts'][name])
 result=read(root,out/'results_v1.json',completed['artifacts']['results']);summary=read(root,out/'summary.json',completed['artifacts']['summary'])
 need(result['config_hash']==digest(cfg) and result['dataset_sha256']==DATA_SHA and result['model']==profile['model'],'Result profile/source differs')
 need(result['fit_source']==completed['fit_source'] and result['capture_source']==completed['capture_source']
  and completed['fit_banks']==completed['factorizations']==45 and completed['parameter_replay_rows']==5760*45,'Readout source or receipt counters differ')
 registration=read(root,out/'registration.json',completed['artifacts']['registration'])
 need(registration['config']==cfg and registration['fixed_recipe']==result['protocol'],'Readout registration differs')
 values=check_result(result,summary,profile,groups)
 proof=read(root,out/'parameter_replay_review_v1.json')
 need(proof['status']=='passed' and proof['config_hash']==digest(cfg) and proof['fit_banks']==45
  and proof['factorizations']==45 and proof['parameter_replay_rows']==5760*45
  and proof['new_fits']==proof['new_model_queries']==0 and proof['generated_holdouts_opened'] is False,'Independent parameter replay proof incomplete')
 for key in ('exact_saved_parameter_score_replays','all_real_and_control_scores_replayed','all_scientific_metrics_recomputed','train_support_and_control_marginals_recomputed'):
  need(proof[key] is True,'Missing actual replay/control proof: '+key)
 need(proof['source_artifacts']==completed['artifacts'],'Replay proof artifact pins differ')
 need(proof['fit_source']==completed['fit_source'] and proof['capture_source']==completed['capture_source'],'Replay proof sources differ')
 return dict(model=profile['model'],capture_distinct_cases=5760,capture_attempted_cases=attempted,
  capture_retry_case_attempts=attempted-5760,capture_prefill_batch_calls=calls,capture_generation_calls=0,
  readout_model_queries=0,parameter_audit_new_fits=0,capture_attempts=attempts,
  readout_runtime=result['runtime'],**values)


def sacct(jobs):
 command=['sacct','-j',','.join(jobs.values()),'--parsable2','--noheader','--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,NodeList']
 for attempt in range(6):
  process=subprocess.run(command,capture_output=True,text=True,check=True,timeout=30);rows={}
  for line in process.stdout.splitlines():
   parts=line.split('|')
   if len(parts)>=6 and parts[0] in jobs.values():rows[parts[0]]=dict(state=parts[1].split()[0].rstrip('+'),exit_code=parts[2],elapsed_seconds=int(parts[3]),allocated_tres=parts[4],nodes=parts[5])
  if set(rows)==set(jobs.values()) and all(r['state']=='COMPLETED' and r['exit_code']=='0:0' for r in rows.values()):
   return dict(command=command,stdout_sha256=hashlib.sha256(process.stdout.encode()).hexdigest(),jobs={name:dict(job_id=job,**rows[job]) for name,job in jobs.items()})
  if attempt<5:time.sleep(2)
 raise ValueError('All seven scientific stage jobs must be accounted COMPLETED with exit 0:0: '+json.dumps(rows))


def publish(path,value):
 payload=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode();need(len(payload)<=8*1024**2,'Compact independent review required')
 need(not path.is_symlink(),'Review cannot follow output symlink');path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():need(path.read_bytes()==payload,'Immutable independent review already differs');return
 temporary=None
 try:
  with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.'+path.name,suffix='.pending',delete=False) as stream:
   temporary=Path(stream.name);stream.write(payload);stream.flush();os.fsync(stream.fileno())
  try:os.link(temporary,path)
  except FileExistsError:need(path.read_bytes()==payload,'Concurrent independent review differs')
 finally:
  if temporary is not None and temporary.exists():temporary.unlink()


def review(root):
 PINS.clear();base=root/REL
 required=[base/model/kind/name for model in MODELS for kind,name in [('capture','completion_manifest_v1.json'),('readouts','completion_manifest_v1.json'),('readouts','parameter_replay_review_v1.json')]]
 need(all(p.is_file() for p in required),'Execution is incomplete: both captures, 45-bank results and actual parameter replay proofs are required before reviewing outcomes')
 source=read(root,base/'execution_source_v1.json')
 need(set(source)=={'snapshot_id','snapshot','code'} and isinstance(source['snapshot_id'],str)
  and len(source['snapshot_id'])==24 and isinstance(source['code'],str) and len(source['code'])==64
  and all(c in '0123456789abcdef' for c in source['snapshot_id']+source['code']),
  'Explicit frozen execution source pointer required')
 frozen=read(root,path_in(root,source['snapshot'])/'frozen_manifest.json')
 need(frozen['snapshot_id']==source['snapshot_id'] and frozen['code']['source_sha256']==source['code'],
  'Frozen execution code differs')
 need(digest(frozen['code']['source_files'])==source['code'],'Frozen source-file inventory digest differs')
 for name,checksum in frozen['code']['source_files'].items():pin(root,path_in(root,source['snapshot'])/name,checksum)
 software=read(root,base/'software_validation_review_v1.json');counts=software['counts']
 need(software['status']=='passed' and counts=={'tests':2044,'failures':0,'errors':0,'skipped':0} and software['source']==source,'Full frozen 2044-test QA required')
 xml=base/'regression_v1.xml';pin(root,xml,software['junit_sha256']);tree=ET.parse(xml).getroot()
 actual={k:sum(int(s.attrib.get(k,0)) for s in tree.findall('testsuite')) for k in counts};need(actual==counts,'JUnit totals differ')
 cohort=source_cohort(root);groups=cohort['development_groups']
 need(len(groups)==15 and sum(groups.values())==1440 and set(groups.values())=={96},
  'Fifteen DEV graph families with96rows each required')
 models={model:model_review(root,model,source,frozen,cohort) for model in MODELS}
 jobs=read(root,base/'jobs_v1.json');need(set(jobs)=={'regression',*(model+'_'+stage for model in MODELS for stage in ('prepare','capture','readouts'))},'Exactly seven scientific stage job IDs required')
 need(all(isinstance(v,str) and v.isdigit() for v in jobs.values()),'Actual SLURM job IDs required')
 accounting=sacct(jobs);pin(root,Path(__file__).resolve())
 output=dict(status='passed',issues=[],evaluation_role='discovery_diversity_independent_execution_review_v1',source=source,
  software_tests=counts,models=models,fit_banks=90,factorizations=90,parameter_replay_rows=5760*90,
  distinct_capture_prefills=11520,attempted_capture_prefills=sum(m['capture_attempted_cases'] for m in models.values()),
  source_graph_families={'train':45,'development':15},development_group_rows=groups,
  original_generation_source=dict(snapshot_id=GENERATION_SNAPSHOT,source_sha256=GENERATION_SOURCE_SHA),
  ordered_source_case_ids_sha256=cohort['ordered_ids_sha256'],
  scheduler=accounting,input_pins=sorted(PINS.values(),key=lambda p:p['path']),
  array_loading_performed=False,binary_artifacts_stream_hashed_only=True,model_or_tokenizer_loaded=False,
  source_and_prepared_identity_metadata_read=True,source_or_graph_regeneration_performed=False,
  new_model_queries=0,new_fits=0,generated_holdouts_opened=False,
  limitations=['Metadata and checksums were independently reviewed; actual saved-parameter and metric replay is certified by the pinned CPU-worker proof, not repeated here.',
   'Fifteen equal-size DEV graph families support descriptive discovery only; class-conditional support is not fully balanced.',
   'Publication and final review jobs are separate from these seven scientific stage jobs.'])
 publish(base/'independent_execution_review_v1.json',output)
 return dict(status='passed',issues=[],models=2,fit_banks=90,factorizations=90,software_tests=counts,scientific_jobs_all_exit_zero=True)


def self_test():
 groups={f'g{i}':96 for i in range(15)}
 item=dict(n=1440,accuracy=.5,group_macro_accuracy=.5,per_group={g:dict(n=n,accuracy=.5) for g,n in groups.items()})
 group_statistics(item,groups,1440)
 failures=[]
 bad=deepcopy(item);bad['n']=1439;failures.append(bad)
 bad=deepcopy(item);bad['group_macro_accuracy']=.8;failures.append(bad)
 bad=deepcopy(item);bad['per_group'].pop('g14');failures.append(bad)
 for bad in failures:
  try:group_statistics(bad,groups,1440)
  except ValueError:pass
  else:raise ValueError('Synthetic corrupt denominator/group summary was accepted')
 group_statistics(dict(n=0,accuracy=None,group_macro_accuracy=None,per_group={}),groups,0)
 need(len(expected_heads())==12 and all(sum(name.startswith(family+'/') for name in expected_heads())==4 for family in DOMAINS),'Head contract differs')
 need(len({bank_name(backend,layer,site,seed) for site in SITES for backend,layer in [('hidden',x) for x in MODELS['llama8b']['layers']]+[('surface',-1)] for seed in SEEDS})==45,'Grid contract differs')
 support=dict(eligibility_split='train',minimum_class_groups=3,structural_groups=45,
  absent_domain_choices_retained=True,development_labels_used_for_eligibility=False,categorical_heads=[])
 for name,(family,choices) in expected_heads().items():
  support['categorical_heads'].append(dict(head=name,family=family,candidates=list(choices),
   evaluated_choices_removed=False,eligible_categorical=True,
   classes=[dict(candidate=c,train_rows=100,train_groups=15,development_rows=20) for c in choices]))
 check_support(support,7)
 for kind in ('missing_version','rare_version'):
  bad=deepcopy(support);head=next(h for h in bad['categorical_heads'] if h['head']=='current_version/0')
  head['classes'][2]['train_rows']=0 if kind=='missing_version' else 100
  head['classes'][2]['train_groups']=0 if kind=='missing_version' else 14
  try:check_support(bad,7)
  except ValueError:pass
  else:raise ValueError('Synthetic absent/rare version-class source support accepted')
 synthetic_source=dict(snapshot='/tmp/synthetic-snapshot',snapshot_id='a'*24,code='b'*64)
 source_equal(dict(snapshot=synthetic_source['snapshot'],snapshot_id='a'*24,source_sha256='b'*64),synthetic_source)
 with tempfile.TemporaryDirectory(prefix='diversity-review-') as temp:
  path=Path(temp)/'review.json';publish(path,{'status':'synthetic'});publish(path,{'status':'synthetic'})
  try:publish(path,{'status':'changed'})
  except ValueError:pass
  else:raise ValueError('Immutable review conflict accepted')
  cases=[]
  for i in range(5760):
   graph=hashlib.sha256(str(i//96).encode()).hexdigest();group='schedule-diversity-graph:'+graph[:24]
   cases.append(dict(id=f'schedule-diversity:{i:024x}',evaluation_role='discovery_relationship_schedule_diversity_sources_v1',
    condition='neutral',canonical_graph_sha256=graph,component_id=group,template_id=group,
    split='train' if i<4320 else 'development',query_slot=i%4))
  data=Path(temp)/'cases.jsonl';data.write_text(''.join(json.dumps(case)+'\n' for case in cases))
  need(len(record_metadata(Path(temp),data))==5760,'Synthetic ordered-case metadata validation failed')
  cases[-1]['id']=cases[0]['id'];data.write_text(''.join(json.dumps(case)+'\n' for case in cases))
  try:record_metadata(Path(temp),data)
  except ValueError:pass
  else:raise ValueError('Duplicate source case identity accepted')
  try:review(Path(temp))
  except ValueError as exc:need('Execution is incomplete' in str(exc),'Incomplete-run refusal must precede outcome access')
  else:raise ValueError('Incomplete synthetic execution was reviewed as complete')
 return dict(status='passed_synthetic_self_test',scientific_inputs_opened=False,actual_review_executed=False,model_queries=0,new_fits=0)


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
 try:result=self_test() if args.self_test else review(root_path())
 except (ValueError,KeyError,OSError,subprocess.SubprocessError) as exc:
  print(json.dumps(dict(status='review_not_written',error=f'{type(exc).__name__}: {exc}')),file=sys.stderr);raise SystemExit(2)
 print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
