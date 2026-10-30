"""Independent metadata review, balanced interpretation and shared checklist update."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from codecue.binding import relationship_capture as b,experiment_log,experiment_log_scheduler as scheduler

def read(path):return json.loads(Path(path).read_text())
def pin(path):
 p=Path(path);p=p if p.is_absolute() else ROOT/p
 return dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=b._sha(p))

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--visual-reviewed',action='store_true',required=True);parser.parse_args()
 handoff=read(FOLDER/'handoff_review_v1.json');assert handoff['status']=='complete_audited'
 for item in handoff['pins']:assert pin(item['path'])==item
 jobs=read(FOLDER/'jobs_v1.json');jobs['publication']=read(FOLDER/'closure_job_v1.json')['job_id']
 raw=subprocess.run(['sacct','-n','-X','-P','-j',','.join(jobs.values()),'--format=JobIDRaw,State,ExitCode'],text=True,capture_output=True,check=True).stdout
 states={row[0]:row[1:3] for line in raw.splitlines() if (row:=line.split('|')) and row[0]}
 assert all(states[job]==['COMPLETED','0:0'] for job in jobs.values()),states
 comparison=read(FOLDER/'comparison_v1.json');rows=comparison['rows'];assert len(rows)==960
 def selected(model,method,rule):
  values=[r for r in rows if r['model']==model and r['backend']=='hidden' and r['layer']==24 and r['site']==7 and r['method']==method and r['rule']==rule]
  assert len(values)==3 and {r['seed'] for r in values}=={17,29,43};return values
 def mean(values,view='own_task'):return sum(v[view]['combined_eight']['accuracy'] for v in values)/3
 points={};transitions={};labels={'llama8b':'Llama 8B','codellama34b':'CodeLlama 34B'}
 for model in labels:
  broad=selected(model,'direct','joint_allow_self');points[model]=dict(free_joint=mean(broad,'free_joint'),free_marginal=mean(broad,'free_marginal'),joint_allow_self=mean(broad),joint_no_self=mean(selected(model,'direct','joint_no_self')),owner_marginal_allow_self=mean(selected(model,'direct','owner_marginal_allow_self')),owner_marginal_no_self=mean(selected(model,'direct','owner_marginal_no_self')),source_prior_joint_grammar=mean(selected(model,'source_owner_version_prior','joint_allow_self')),source_prior_owner_grammar=mean(selected(model,'source_owner_version_prior','owner_marginal_allow_self')))
  assert points[model]['source_prior_owner_grammar']==1.
  assert points[model]['source_prior_joint_grammar']>points[model]['joint_allow_self']
  transitions[model]={r:{ref:{name:sum(v['transitions'][ref]['combined_eight'][name]['correct'] for v in selected(model,'direct',r)) for name in ['corrected','harmed']} for ref in ['free_joint','free_marginal']} for r in ['joint_allow_self','owner_marginal_allow_self']}
 assert points['codellama34b']['joint_allow_self']<points['codellama34b']['free_marginal']
 lines=['# Interpreting the completed grammar diagnostic','','All 60 banks and the independent retained-score replay passed. This table uses the fixed hidden layer24/site7 endpoint, averaging all three weighting seeds. All-eight accuracy requires every write and parent identity correct.','','| Decision rule | Llama 8B | CodeLlama 34B |','|---|---:|---:|']
 for label,key in [('Original free joint','free_joint'),('Original free marginal','free_marginal'),('Broad joint-score grammar','joint_allow_self'),('No-self joint-score grammar (secondary)','joint_no_self'),('Broad owner-only grammar','owner_marginal_allow_self'),('No-self owner-only grammar (secondary)','owner_marginal_no_self'),('Source-owner/TRAIN-version prior + broad joint grammar','source_prior_joint_grammar'),('Source-owner scores + broad owner-only grammar','source_prior_owner_grammar')]:
  lines.append('| '+label+' | '+' | '.join(f'{100*points[m][key]:.3f}%' for m in labels)+' |')
 lines+=['','Joint-score constraints improve the original free-joint endpoint, whose whole-eight monotonicity is guaranteed on these finite lawful cases. That does not guarantee improvement over the original marginal rule: CodeLlama34B joint grammar is lower than that reference. The stronger source-owner/TRAIN-version-prior comparator with the same joint grammar also exceeds both hidden joint endpoints.','',
 'Owner-only decoding removes version-specific score evidence while the external counter rule supplies versions. Its larger recovery therefore does not require version-sensitive neural scores. Visible source owners plus counters reconstruct all identities at100% without hidden-state decoding. These outcomes support decoder-assisted reconstruction, with maintained state, natural causal use, old-value retrieval and unfamiliar-program generalization unresolved.','',
 'The no-self condition is a separately declared global cohort prior. Sham truth may violate either grammar; its constrained exact ceiling and own-task accuracy remain separate from the same predictions evaluated against real truth. No matched-selectivity claim or new confidence interval is made.','',
 'Joint grammar versus original marginal argmax, across three dependent estimator views of1,440DEVcases:']
 for model in labels:
  t=transitions[model]['joint_allow_self']['free_marginal'];lines.append(f'- {labels[model]}: {t["corrected"]} whole-eight corrections and {t["harmed"]} harms among4,320bank-case views. These are repeated views of the same1,440cases, not4,320independent programs.')
 lines+=['',f'All2,191tests passed; the exact106-file test archive verified; all three jobs completed with exit0:0. There were zero new model calls, fits or parameter applications. The full960-cell grid, all60 detailed diagnostics and exact objective pairs remain linked by the [publication proof](../../artifacts/binding/identity_grammar/20261028_v1/publication_review_v1.json). The [summary](identity_grammar_summary_v1.md) and [decision](identity_grammar_decision_v1.md) retain the original declared scope.','']
 text='\n'.join(lines)
 for a,z in [('layer24/site7','layer 24/site 7'),('CodeLlama34B','CodeLlama 34B'),('at100%','at 100%'),('of1,440DEVcases','of 1,440 DEV cases'),('among4,320bank-case','among 4,320 bank-case'),('same1,440cases','same 1,440 cases'),('not4,320independent','not 4,320 independent'),('All2,191tests','All 2,191 tests'),('exact106-file','exact 106-file'),('exit0:0','exit 0:0'),('full960-cell','full 960-cell'),('all60 detailed','all 60 detailed')]:text=text.replace(a,z)
 report=ROOT/'reports/binding/identity_grammar_interpretation_v1.md';b._publish(report,text.encode())
 for name,prefix in [('README.md','reports/binding/'),('reports/binding/implementation_checklist.md',''),('reports/binding/research_backlog.md','')]:
  path=ROOT/name;content=path.read_text();start=content.index('\nThe [bounded saved-score grammar diagnostic]');end=content.index('\n',start+1)
  intro=f'\nThe [bounded saved-score grammar diagnostic]({prefix}identity_grammar_interpretation_v1.md) is complete and audited across **60 banks and 86,400 DEV bank-case rows**, with **zero new model calls, fits or parameter applications**. All **2,191 tests** and the exact **106-file source archive** passed. Owner-only grammar gives **{100*points["llama8b"]["owner_marginal_allow_self"]:.3f}% / {100*points["codellama34b"]["owner_marginal_allow_self"]:.3f}%** all-eight recovery for 8B / 34B; explicit source owners plus counters give **100%**. Joint grammar improves free joint but falls below the original marginal rule on 34B. These are decoder-assisted reconstruction results, with natural causal use unresolved. The [updated inventory]({prefix}preparation_readiness.md) records **71 tasks: 59 ready / 9 scientific / 3 optional**. Earlier completed studies below retain their historical counts.'
  content=content[:start]+intro+content[end:]
  if name.endswith('implementation_checklist.md'):
   section='\n### Saved-score grammar continuation (October 28)\n\n- [x] Build the exact score-only copy/version DP with broad and no-self grammars and joint/owner-only evidence.\n- [x] Pass 62 focused checks and independent source/synthetic review.\n- [x] Freeze source, pass all 2,191 regression tests and verify the exact 106-file source archive.\n- [x] Reproduce original metrics for all 60 banks and preserve all 86,400 DEV bank-case rows.\n- [x] Independently replay every prediction, exact objective and metric from retained scores without reopening original score banks.\n- [x] Pass 14 publication checks, retain all 960 rule cells and reproduce publication bytes.\n- [x] Verify all artifact pins, inspect the chart, log completion and refresh readiness to 59 ready out of 71.\n\n'
   anchor='\n### Direct identity continuation'
   if '### Saved-score grammar continuation' not in content:content=content.replace(anchor,section+anchor,1)
  if name.endswith('research_backlog.md'):content=content.replace('Latest continuation, 2026-10-28: direct','Earlier continuation, 2026-10-28: direct',1)
  path.write_text(content)
 status=ROOT/'reports/binding/identity_grammar_status_v1.md';status.write_text('# Completed saved-score grammar diagnostic\n\nAll three jobs completed with exit 0:0: regression '+jobs['regression']+', score analysis/audit '+jobs['analysis']+', and publication '+jobs['publication']+'. All 2,191 tests and the exact 106-file test archive passed. All 60 banks, 345,600 original score rows and 86,400 DEV bank-case rows were checked. Publication retained all 960 method/rule cells and reproduced identical bytes.\n\nRead the [balanced interpretation](identity_grammar_interpretation_v1.md), [summary](identity_grammar_summary_v1.md), and [completed inventory](preparation_readiness.md). This finite diagnostic is closed. The nine scientific decisions and three optional extensions remain open.\n')
 health=scheduler.ensure_enabled(ROOT,force=True);assert health['enabled'] and health['healthy'] and health['pending_guards']>=2
 records=experiment_log.list_records(ROOT,kind='analysis');matching=[r for r in records if Path(r['path']).resolve()==(FOLDER/'analysis').resolve()]
 assert len(matching)==1 and matching[0]['status']=='complete_exploratory' and matching[0]['audit_status']=='passed',[(r['status'],r['audit_status']) for r in matching]
 note=dict(status='passed',evaluation_role='discovery_identity_grammar_independent_completion_review_v1',source=handoff['source'],handoff_sha256=b._sha(FOLDER/'handoff_review_v1.json'),handoff_pins_verified=len(handoff['pins']),all_three_jobs_completed=True,software_tests=2191,test_archive_files=106,plot_visually_reviewed=True,headlines=points,whole8_transitions_across_dependent_seed_views=transitions,logging_enabled=True,logging_healthy=True,index_record_id=matching[0]['id'],index_status=matching[0]['status'],pending_guards=health['pending_guards'],new_fits=0,new_model_queries=0,parameters_reapplied=0,score_arrays_opened=False,pins=[pin(p) for p in [report,status,FOLDER/'review_completion_v1.py',ROOT/'README.md',ROOT/'reports/binding/implementation_checklist.md',ROOT/'reports/binding/research_backlog.md']])
 b._put(FOLDER/'completion_followup_review_v1.json',note)
 print(json.dumps(dict(status='complete_independently_reviewed',pins_verified=note['handoff_pins_verified'],headlines=points,logging_index=matching[0]['id']),sort_keys=True))

if __name__=='__main__':main()
