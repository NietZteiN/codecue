import subprocess
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[4]
command=[sys.executable,str(root/"artifacts/binding/computation_routing/20261028_v1/publish_results_v1.py")]
for attempt in range(2):subprocess.run(command,cwd=root,check=True)
