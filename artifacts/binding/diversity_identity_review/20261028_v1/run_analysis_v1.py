"""Run source-oracle-assisted posthoc review from frozen source on a CPU worker."""
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
from codecue.binding import snapshots
from codecue.binding import relationship_capture as bounded
frozen=snapshots.verify(snapshot)
assert frozen['snapshot_id']==source['snapshot_id']
assert frozen['code']['source_sha256']==source['code']
assert os.environ.get('SLURM_JOB_ID'), 'CPU allocation required'
qa=json.loads((FOLDER/'software_validation_review_v1.json').read_text())
assert qa['status']=='passed' and qa['source']==source
assert qa['counts']==dict(tests=json.loads((FOLDER/'build_review_v1.json').read_text())['expected_regression_tests'],failures=0,errors=0,skipped=0)
original=ROOT/'artifacts/binding/diversity_decoding/20261028_v1/handoff_review_v1.json'
completed=json.loads(original.read_text())
assert completed['status']=='complete_audited' and completed['fit_banks']==90
for item in completed['pins']:
 p=ROOT/item['path'];assert p.stat().st_size==item['bytes'] and bounded._sha(p)==item['sha256']
script=snapshot/'scripts/162_binding_diversity_identity_review.py'
config=snapshot/'configs/binding/diversity_identity_review_v1.json'
threads=os.environ.get('SLURM_CPUS_PER_TASK','4')
env=dict(os.environ,PYTHONPATH=str(snapshot/'src'),OPENBLAS_NUM_THREADS=threads,OMP_NUM_THREADS=threads,MKL_NUM_THREADS=threads)
for command in ('preflight','run','audit'):
 subprocess.run([sys.executable,str(script),command,str(config)],cwd=ROOT,env=env,check=True)
