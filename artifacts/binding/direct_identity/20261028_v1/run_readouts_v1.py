"""Fit and audit direct event-identity probes from immutable saved features."""
import json
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4]
FOLDER=Path(__file__).resolve().parent
source=json.loads((FOLDER/'execution_source_v1.json').read_text())
snapshot=Path(source['snapshot'])
sys.path.insert(0,str(snapshot/'src'))
from codecue.binding import snapshots,relationship_capture as bounded
frozen=snapshots.verify(snapshot)
assert frozen['snapshot_id']==source['snapshot_id'] and frozen['code']['source_sha256']==source['code']
assert os.environ.get('SLURM_JOB_ID'),'CPU allocation required'
qa=json.loads((FOLDER/'software_validation_review_v1.json').read_text())
assert qa['status']=='passed' and qa['source']==source
assert qa['counts']==dict(tests=json.loads((FOLDER/'build_review_v1.json').read_text())['expected_regression_tests'],failures=0,errors=0,skipped=0)
original=ROOT/'artifacts/binding/diversity_decoding/20261028_v1/handoff_review_v1.json'
handoff=json.loads(original.read_text());assert handoff['status']=='complete_audited' and handoff['fit_banks']==90
for item in handoff['pins']:
 p=ROOT/item['path'];assert p.stat().st_size==item['bytes'] and bounded._sha(p)==item['sha256']
model=sys.argv[1];assert model in ('llama8b','codellama34b')
script=snapshot/'scripts/163_binding_direct_identity_readouts.py'
config=snapshot/'configs/binding/direct_identity_20261028_v1'/f'{model}_readouts.json'
threads=os.environ.get('SLURM_CPUS_PER_TASK','16')
env=dict(os.environ,PYTHONPATH=str(snapshot/'src'),OPENBLAS_NUM_THREADS=threads,OMP_NUM_THREADS=threads,MKL_NUM_THREADS=threads)
for command in ('preflight','run','audit'):
 print(f'direct identity {model}: {command} starting',flush=True)
 subprocess.run([sys.executable,str(script),command,str(config)],cwd=ROOT,env=env,check=True)
 print(f'direct identity {model}: {command} completed',flush=True)
