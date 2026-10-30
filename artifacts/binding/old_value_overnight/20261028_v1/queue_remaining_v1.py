"""Pin overnight helpers and submit gated measurement, recurring checks and morning review."""
from datetime import datetime,timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4];FOLDER=Path(__file__).resolve().parent
source=json.loads((FOLDER/'execution_source_v1.json').read_text());snapshot=Path(source['snapshot'])
sys.path.insert(0,str(snapshot/'src'))
from codecue.binding import relationship_capture as b,preparation,old_value_overnight as checker
from codecue.binding import overnight_relationship_capture as durable,experiment_log_scheduler as scheduler
PYTHON='/work/jvl210002/migration/envs/probe-cu129/bin/python'
def read(p):return json.loads(Path(p).read_text())
def pin(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 return dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=b._sha(p))
def accepted_or_submit(submit,**kwargs):
 # Recover the scheduler-accepted ID if setup stopped before its progress write.
 matches=set()
 for path in (ROOT/'log/slurm').glob('submit_*_'+kwargs['name']+'.json'):
  value=read(path)
  if value.get('argv')==kwargs['argv'] and str(value.get('job_id','')).isdigit():matches.add(str(value['job_id']))
 assert len(matches)<=1,('ambiguous accepted submission',kwargs['name'],sorted(matches))
 return next(iter(matches)) if matches else submit.submit(**kwargs)

def main():
 progress=read(FOLDER/'submission_progress_v1.json');assert progress['source']==source
 for name,key,filename in [('monitor','helper_sha256','watch_running_v1.py'),('publisher','publisher_sha256','publish_overnight_v1.py')]:
  review=read(FOLDER/(name+'_build_review_v1.json'));assert review['status']=='passed' and review['synthetic_checks']>0 and review[key]==b._sha(FOLDER/filename)
 if not (FOLDER/'readiness_at_submission_v1.json').exists():
  ready_cfg=read(snapshot/'configs/binding/preparation/readiness_v24.json');ready=preparation.run(ready_cfg)
  b._put(FOLDER/'readiness_at_submission_v1.json',ready)
 helpers=[FOLDER/p for p in ['prepare_submission_v1.py','queue_remaining_v1.py','run_validation_v1.py','stage_worker_v1.py','publish_overnight_v1.py','watch_running_v1.py','monitor_build_review_v1.json','publisher_build_review_v1.json']]
 pipeline=dict(status='ready',evaluation_role='discovery_old_value_completion_pipeline_v1',source=source,helper_pins=[pin(p) for p in helpers],readiness_config=pin('configs/binding/preparation/readiness_v24.json'),queued_readiness_report_sha256=b._sha(ROOT/'reports/binding/preparation_readiness.md'),new_fits=0,causal_follow_on=False)
 if (FOLDER/'completion_pipeline_v1.json').exists():
  previous=read(FOLDER/'completion_pipeline_v1.json');assert previous['source']==source
  for item in previous['helper_pins']+[previous['readiness_config']]:assert pin(item['path'])==item
 else:b._put(FOLDER/'completion_pipeline_v1.json',pipeline)
 subprocess.run([PYTHON,str(FOLDER/'publish_overnight_v1.py'),'--check-setup'],cwd=ROOT,check=True)
 spec=importlib.util.spec_from_file_location('overnight_submit',ROOT/'scripts/slurm/submit.py');submit=importlib.util.module_from_spec(spec);spec.loader.exec_module(submit)
 for model,partition,time,minimum in [('llama8b','dev-a30,a30,h100,h200','02:00:00','00:10:00'),('codellama34b','h100,h200','2-00:00:00','00:20:00')]:
  stage=model+'_behavior'
  if stage not in progress['jobs']:
   prerequisite_ids=[progress['jobs']['regression'],progress['jobs'][model+'_preflight']]
   raw=subprocess.run(['sacct','-n','-X','-P','-j',','.join(prerequisite_ids),'--format=JobIDRaw,State%32,ExitCode'],text=True,capture_output=True,check=True).stdout
   states={v[0]:v[1:3] for line in raw.splitlines() if (v:=line.split('|')) and v[0]}
   unfinished=[]
   for jid in prerequisite_ids:
    state,exit_code=states[jid]
    if state=='COMPLETED':assert exit_code=='0:0',states
    else:
     assert state in ('PENDING','RUNNING','CONFIGURING','COMPLETING'),states
     unfinished.append(jid)
   # Completed prerequisites are verified again by stage_worker; avoid stale scheduler dependency IDs.
   dep='afterok:'+':'.join(unfinished) if unfinished else None
   job=accepted_or_submit(submit,name='oldvalue-'+stage,partition=partition,cpus=8,mem='48G' if model=='llama8b' else '64G',time=time,time_min=minimum,dependency=dep,argv=[PYTHON,str(FOLDER/'stage_worker_v1.py'),'behavior','--model',model])
   progress['jobs'][stage]=job;durable._journal(FOLDER/'submission_progress_v1.json',progress);durable._journal(FOLDER/'jobs_v1.json',progress['jobs'])
 if 'publication' not in progress['jobs']:
  dep='afterany:'+progress['jobs']['llama8b_behavior']+':'+progress['jobs']['codellama34b_behavior']
  job=accepted_or_submit(submit,name='oldvalue-publication',partition='dev,normal',cpus=4,mem='16G',time='02:00:00',dependency=dep,argv=[PYTHON,str(FOLDER/'stage_worker_v1.py'),'publication'])
  progress['jobs']['publication']=job;durable._journal(FOLDER/'submission_progress_v1.json',progress);durable._journal(FOLDER/'jobs_v1.json',progress['jobs'])
 if 'morning' not in progress['jobs']:
  job=accepted_or_submit(submit,name='oldvalue-morning',partition='dev,normal',cpus=2,mem='8G',time='02:00:00',begin='2026-10-29T08:00:00',argv=[PYTHON,str(FOLDER/'stage_worker_v1.py'),'morning'])
  progress['jobs']['morning']=job;durable._journal(FOLDER/'submission_progress_v1.json',progress);durable._journal(FOLDER/'jobs_v1.json',progress['jobs'])
 initial=FOLDER/'monitor_initial_job_v1.json'
 if not initial.exists():
  job=accepted_or_submit(submit,name='oldvalue-watch-start',partition='dev,normal',cpus=1,mem='4G',time='00:10:00',argv=[PYTHON,str(FOLDER/'watch_running_v1.py')])
  b._put(initial,dict(status='submitted',job_id=job,interval_minutes=10,stage_jobs_separate=True))
 reconciliation=scheduler.tick(ROOT,force=True)
 assert reconciliation['status'] in ('complete','busy'),reconciliation
 guards=scheduler.ensure_enabled(ROOT,force=True);assert guards['enabled'] and guards['healthy']
 cfg=read(snapshot/'configs/binding/old_value_overnight_20261028_v1/check.json');check=checker.check(cfg,deep=True,root=ROOT)
 assert check['source']==source and check['baseline']['status']=='passed' and not check['issues'],check['issues']
 # Execution may already be running or waiting. No completion or qualification is inferred.
 if not (FOLDER/'queue_handoff_review_v1.json').exists():b._put(FOLDER/'queue_handoff_review_v1.json',dict(status='passed',evaluation_role='discovery_old_value_submitted_handoff_v1',recorded_utc=datetime.now(timezone.utc).isoformat(),source=source,jobs=progress['jobs'],monitor_initial_job=read(initial)['job_id'],intermittent_checks_enabled=True,interval_minutes=10,morning_check_independent=True,morning_at=cfg['morning_at'],planned_scored_responses=40320,planned_warmup_requests=16,source_rows=6720,primary_gate_cells_per_model=24,causal_follow_on=False,new_fits=0,model_measurement_pending=True,immutable_baseline_check=check['baseline'],logging=check['logging'],pins=[pin(p) for p in [FOLDER/'execution_source_v1.json',FOLDER/'build_review_v1.json',FOLDER/'jobs_v1.json',FOLDER/'completion_pipeline_v1.json',FOLDER/'source_review_v1.json',ROOT/'configs/binding/old_value_overnight_20261028_v1/check.json',ROOT/'reports/binding/old_value_overnight_plan_v1.md']]))
 print(json.dumps(dict(status='overnight_suite_submitted',jobs=progress['jobs'],monitor=read(initial)['job_id'],check_status=check['status'],needs_attention=check['needs_attention'],morning_at=cfg['morning_at']),sort_keys=True))
if __name__=='__main__':main()
