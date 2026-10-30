"""Check source-map diagnostics on all actual DEV labels without reading model scores."""
from pathlib import Path
import json
import numpy as np
from codecue.binding import diversity_targets as targets
from codecue.binding import binding_identity_diagnostics as diagnostic
from codecue.binding import relationship_capture as bounded
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).resolve().parent
prepared=ROOT/'artifacts/binding/diversity_decoding/20261028_v1/llama8b/capture/prepared_cases.jsonl'
assert prepared.stat().st_size<256*1024**2
with prepared.open() as stream:records=[json.loads(line)['record'] for line in stream]
assert len(records)==5760 and len({r['id'] for r in records})==5760
records=[r for r in records if r['split']=='development']
assert len(records)==1440
profiles=[r['profile_id'] for r in records]
assert set(profiles)=={'2_1_1_0','3_1_0_0','2_2_0_0'}
case_indices={r['id']:i for i,r in enumerate(records)}
reviews=[]
for site in (3,7,8):
 bundle=targets.targets(records,site)
 prediction=np.full((len(records),len(targets.HEADS)),-1,dtype=np.int16)
 for h,head in enumerate(targets.HEADS):
  indices=list(head['indices']);defined=bundle.mask[:,indices].any(axis=1)
  prediction[defined,h]=np.asarray(head['candidates'])[np.argmax(bundle.y[defined][:,indices],axis=1)]
 result=diagnostic.diagnostics(bundle,prediction,profiles=profiles,include_rows=True)
 assert result['row_count']==1440 and result['graph_groups']==15
 assert result['oracle_assisted'] and result['real_task_truth_only']
 total_defined=0;total_undefined=0;obsolete_final_correct=0
 for stats in result['per_head'].values():
  assert sum(stats['counts'].values())==1440
  assert stats['counts']['exact']==stats['n_defined']
  assert stats['counts']['undefined']==stats['n_undefined']
  assert all(stats['counts'][name]==0 for name in diagnostic.CATEGORIES if name not in ('exact','undefined'))
  total_defined+=stats['n_defined'];total_undefined+=stats['n_undefined']
 for row in result['rows']:
  if row['family']=='copy_parent' and row['defined']:
   case=case_indices[row['case_id']]
   node=bundle.descriptive['version_map_by_case'][case][row['truth']]
   if node['status']=='obsolete':
    obsolete_final_correct+=1
    assert row['category']=='exact' and row['predicted_definition_status']=='current'
 if site in (7,8):assert obsolete_final_correct>0
 for profile in profiles:
  assert profile in result['by_profile']
 reviews.append(dict(site=site,rows=1440,defined_head_labels=total_defined,undefined_head_labels=total_undefined,parent_truth_obsolete_at_capture_but_current_at_read_time=obsolete_final_correct,oracle_truth_predictions_exact=True))
value=dict(status='passed',evaluation_role='discovery_diversity_identity_source_preflight_v1',source_only=True,source_rows=5760,development_rows=1440,development_graph_groups=15,sites=reviews,profiles=sorted(set(profiles)),source_oracle_labels_used_as_predictions=True,learned_outcomes_claimed=False,saved_score_arrays_opened=False,activation_arrays_opened=False,coefficient_arrays_opened=False,model_loaded=False,tokenizer_loaded=False,new_model_queries=0,new_fits=0,parameters_reapplied=0,generated_holdouts_opened=False,prepared_cases_sha256=bounded._sha(prepared),core_sha256=bounded._sha(ROOT/'src/codecue/binding/binding_identity_diagnostics.py'),preflight_runner_sha256=bounded._sha(__file__))
bounded._put(FOLDER/'identity_source_preflight_review_v1.json',value)
print(json.dumps(value,sort_keys=True))
