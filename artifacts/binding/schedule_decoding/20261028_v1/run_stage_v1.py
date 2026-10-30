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
config_root = snapshot / 'configs/binding/schedule_decoding_20261028_v1'
capture_config = str(config_root / f'{model}_capture.json')
readout_config = str(config_root / f'{model}_readouts.json')
capture_script = str(snapshot / 'scripts/156_binding_schedule_capture.py')
readout_script = str(snapshot / 'scripts/157_binding_schedule_readouts.py')
commands = {
    'prepare': [(capture_script, 'prepare', capture_config)],
    'capture': [(capture_script, 'run', capture_config)],
    'readouts': [(capture_script, 'audit', capture_config),
                 (readout_script, 'preflight', readout_config),
                 (readout_script, 'run', readout_config),
                 (readout_script, 'audit', readout_config)],
}[stage]
environment = dict(os.environ, PYTHONPATH=str(snapshot / 'src'),
                   OPENBLAS_NUM_THREADS='8', OMP_NUM_THREADS='8',
                   MKL_NUM_THREADS='8', NUMEXPR_NUM_THREADS='8')
for script, command, config in commands:
    subprocess.run([sys.executable, script, command, config], cwd=ROOT,
                   env=environment, check=True)
