"""Execute a frozen, finite source-preparation or saved-score CPU stage."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
FOLDER = Path(__file__).resolve().parent
source = json.loads((FOLDER / 'execution_source_v1.json').read_text())
snapshot = Path(source['snapshot'])
sys.path.insert(0, str(snapshot / 'src'))
from codecue.binding.snapshots import verify
assert verify(snapshot)['code']['source_sha256'] == source['code']
stage = sys.argv[1]
assert stage in ('score_review', 'source_diversity')
if stage == 'score_review':
    script = str(snapshot / 'scripts/158_binding_schedule_score_review.py')
    config = str(snapshot / 'configs/binding/schedule_followup_20261028_v1/score_review.json')
    commands = [[script, command, config] for command in ('preflight', 'run', 'audit')]
else:
    commands = [[str(snapshot / 'scripts/159_binding_schedule_diversity_programs.py'),
                 str(snapshot / 'configs/binding/relationships/schedule_diversity_generation_v1.json')]]
env = dict(os.environ, PYTHONPATH=str(snapshot / 'src'), OPENBLAS_NUM_THREADS='4',
           OMP_NUM_THREADS='4', MKL_NUM_THREADS='4')
for command in commands:
    subprocess.run([sys.executable, *command], cwd=ROOT, env=env, check=True)
