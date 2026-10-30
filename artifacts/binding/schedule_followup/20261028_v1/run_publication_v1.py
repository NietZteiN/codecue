"""Publish and reproduce the completed posthoc metadata without model work."""
import hashlib
from pathlib import Path
import subprocess
import sys

folder = Path(__file__).resolve().parent
root = folder.parents[3]
publisher = folder / 'publish_score_review_v1.py'
assert hashlib.sha256(publisher.read_bytes()).hexdigest() == '90565d2c0ff0e7759d32e6079b007b5fd5bb83664675ce7e1b52b969f1e002b4'
for attempt in range(2):
    subprocess.run([sys.executable, str(publisher)], cwd=root, check=True)
