"""Execute a finite dependency stage from the pinned source and configurations."""
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

manifest = verify(snapshot)
assert manifest['snapshot_id'] == source['snapshot_id']
assert manifest['code']['source_sha256'] == source['code']
model, stage = sys.argv[1:]
assert model in ('llama8b', 'codellama34b')
assert stage in ('prepare', 'capture', 'readouts')
config_root = snapshot / 'configs/binding/diversity_decoding_20261028_v1'
capture_config = str(config_root / f'{model}_capture.json')
readout_config = str(config_root / f'{model}_readouts.json')
capture_script = str(snapshot / 'scripts/160_binding_diversity_capture.py')
readout_script = str(snapshot / 'scripts/161_binding_diversity_readouts.py')
commands = {
    'prepare': [(capture_script, 'prepare', capture_config)],
    'capture': [(capture_script, 'run', capture_config)],
    'readouts': [(capture_script, 'audit', capture_config),
                 (readout_script, 'preflight', readout_config),
                 (readout_script, 'run', readout_config),
                 (readout_script, 'audit', readout_config)],
}[stage]
threads = os.environ.get('SLURM_CPUS_PER_TASK', '8')
environment = dict(os.environ, PYTHONPATH=str(snapshot / 'src'),
                   OPENBLAS_NUM_THREADS=threads, OMP_NUM_THREADS=threads,
                   MKL_NUM_THREADS=threads, NUMEXPR_NUM_THREADS=threads)
for script, command, config in commands:
    subprocess.run([sys.executable, script, command, config], cwd=ROOT,
                   env=environment, check=True)
