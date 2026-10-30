"""Freeze/debug the new overnight suite and submit QA plus native preparations."""
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4];FOLDER=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from codecue.binding import snapshots,relationship_capture as b,overnight_relationship_capture as durable
from codecue.binding.datasets import digest
PYTHON='/work/jvl210002/migration/envs/probe-cu129/bin/python'
def read(p):return json.loads(Path(p).read_text())
def main():
 progress=read(FOLDER/'submission_progress_v1.json') if (FOLDER/'submission_progress_v1.json').exists() else {}
 if 'source' not in progress:
  before=snapshots.hashes(ROOT);old=read(ROOT/'artifacts/binding/sources/b75fedb03895e8f9d28e29c3/frozen_manifest.json')
  changed=[name for name,h in old['code']['source_files'].items() if before[name]!=h];assert changed==['src/codecue/binding/snapshots.py'],changed
  from codecue.binding import old_value_run
  metadata={}
  for model in ['llama8b','codellama34b']:
   cfg=read(ROOT/'configs/binding/old_value_overnight_20261028_v1'/f'{model}.json');metadata[model]=old_value_run.metadata(cfg);assert metadata[model]['scored_cases']==20160
  checksums={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'tests/binding').rglob('*.py'))};assert len(checksums)==109
  result=subprocess.run([PYTHON,'-m','pytest','tests/binding','--collect-only','-q'],cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'src')),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  b._publish(FOLDER/'collection_stdout_v1.txt',result.stdout);assert result.returncode==0,result.stdout[-4000:]
  count=int(re.findall(rb'(\d+) tests? collected',result.stdout)[0]);assert count==2280,count;assert snapshots.hashes(ROOT)==before
  cfgpath=ROOT/'configs/binding/preparation/readiness_v24.json';cfg=read(cfgpath);next(i for i in cfg['items'] if i['id']=='regression')['evidence'][0]['minimum_tests']=count;cfgpath.write_text(json.dumps(cfg,sort_keys=True,indent=2)+'\n')
  source=snapshots.freeze();b._put(FOLDER/'execution_source_v1.json',source)
  b._put(FOLDER/'build_review_v1.json',dict(status='passed',evaluation_role='discovery_old_value_build_v1',recorded_utc=datetime.now(timezone.utc).isoformat(),source=source,expected_regression_tests=count,test_source_files=len(checksums),test_source_sha256=digest(checksums),new_focused_tests=89,new_modules=['old_value_programs','old_value_run','old_value_overnight'],historical_source_changes=changed,metadata=metadata,source_rows=6720,planned_scored_responses_per_model=20160,new_fits=0,model_inference=False,generated_holdouts_opened=False))
  progress=dict(source=source,expected_tests=count,jobs={});durable._journal(FOLDER/'submission_progress_v1.json',progress)
 spec=importlib.util.spec_from_file_location('oldvalue_submit',ROOT/'scripts/slurm/submit.py');submit=importlib.util.module_from_spec(spec);spec.loader.exec_module(submit)
 for stage in ['regression','llama8b_preflight','codellama34b_preflight']:
  if stage in progress['jobs']:continue
  if stage=='regression':argv=[PYTHON,str(FOLDER/'run_validation_v1.py')]
  else:argv=[PYTHON,str(FOLDER/'stage_worker_v1.py'),'preflight','--model',stage.removesuffix('_preflight')]
  job=submit.submit(name='oldvalue-'+stage,partition='dev,normal',cpus=8,mem='16G',time='02:00:00',argv=argv)
  progress['jobs'][stage]=job;durable._journal(FOLDER/'submission_progress_v1.json',progress)
 durable._journal(FOLDER/'jobs_v1.json',progress['jobs'])
 print(json.dumps(dict(status='QA_and_native_preparations_submitted',**progress),sort_keys=True))
if __name__=='__main__':main()
