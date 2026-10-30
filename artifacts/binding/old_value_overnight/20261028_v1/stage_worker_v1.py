"""Execute one fixed overnight stage from frozen source and explicit dependencies."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).resolve().parent
source=json.loads((FOLDER/'execution_source_v1.json').read_text());snapshot=Path(source['snapshot'])
sys.path.insert(0,str(snapshot/'src'))
from codecue.binding import relationship_capture as b,snapshots

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=('preflight','behavior','publication','morning'));p.add_argument('--model',choices=('llama8b','codellama34b'));args=p.parse_args()
 assert os.environ.get('SLURM_JOB_ID'),'SLURM allocation required'
 frozen=snapshots.verify(snapshot);assert frozen['snapshot_id']==source['snapshot_id'] and frozen['code']['source_sha256']==source['code']
 env=dict(os.environ,PYTHONPATH=str(snapshot/'src'),HF_HUB_OFFLINE='1',OMP_NUM_THREADS=os.environ.get('SLURM_CPUS_PER_TASK','8'),OPENBLAS_NUM_THREADS=os.environ.get('SLURM_CPUS_PER_TASK','8'))
 if args.stage in ('preflight','behavior'):
  assert args.model;config=snapshot/'configs/binding/old_value_overnight_20261028_v1'/f'{args.model}.json';script=snapshot/'scripts/165_binding_old_value.py'
  if args.stage=='preflight':commands=['preflight']
  else:
   qa=json.loads((FOLDER/'software_validation_review_v1.json').read_text());build=json.loads((FOLDER/'build_review_v1.json').read_text())
   assert qa['status']=='passed' and qa['source']==source and qa['counts']==dict(tests=build['expected_regression_tests'],failures=0,errors=0,skipped=0)
   assert qa['test_source_sha256']==build['test_source_sha256']
   cfg=json.loads(config.read_text());native=json.loads((ROOT/cfg['preflight_result']).read_text());registration=json.loads((ROOT/cfg['run_dir']/'routing_preflight_v1.json').read_text())
   assert native['status']=='passed' and native['cases']==20160 and native['source_sha256']==source['code'] and native['model_inference'] is False
   assert registration['source']['snapshot_id']==source['snapshot_id'] and registration['source']['source_sha256']==source['code']
   commands=['run','audit']
  for command in commands:subprocess.run([sys.executable,str(script),command,str(config)],cwd=ROOT,env=env,check=True)
 elif args.stage=='publication':
  pipeline=json.loads((FOLDER/'completion_pipeline_v1.json').read_text());assert pipeline['source']==source
  for item in pipeline['helper_pins']:
   path=ROOT/item['path'];assert path.stat().st_size==item['bytes'] and b._sha(path)==item['sha256']
  for _ in range(2):subprocess.run([sys.executable,str(FOLDER/'publish_overnight_v1.py')],cwd=ROOT,env=env,check=True)
 else:
  from codecue.binding import old_value_overnight as checker
  config=json.loads((snapshot/'configs/binding/old_value_overnight_20261028_v1/check.json').read_text())
  result=checker.check(config,deep=True,morning=True,root=ROOT)
  print(json.dumps({k:result[k] for k in ('status','scientific_status','needs_attention','checked_at','morning_review_v1')},sort_keys=True))

if __name__=='__main__':main()
