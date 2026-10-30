"""Run the complete binding regression and certify the frozen continuation source."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from codecue.binding import relationship_capture as base, snapshots
from codecue.binding.datasets import digest

folder = ROOT / 'artifacts/binding/overnight_relationships/20261028_completion_v1'
source = json.loads((folder / 'execution_source_v1.json').read_text())
snapshots.verify(source['snapshot'])
assert digest(snapshots.hashes(ROOT)) == source['code'], 'working source differs before regression'
test_files = sorted((ROOT / 'tests/binding').rglob('*.py'))
test_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in test_files}
readiness = json.loads((ROOT / 'configs/binding/preparation/readiness_v13.json').read_text())
expected = next(i for i in readiness['items'] if i['id'] == 'regression')['evidence'][0]['minimum_tests']
xml = folder / 'regression_v1.xml'
stdout = folder / 'regression_stdout_v1.txt'
assert not xml.exists() and not stdout.exists(), 'validation outputs already exist'
with stdout.open('wb') as stream:
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/binding', '-q', '--junitxml=' + str(xml)],
        cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')), stdout=stream, stderr=subprocess.STDOUT)
if result.returncode:
    raise SystemExit(result.returncode)
assert digest(snapshots.hashes(ROOT)) == source['code'], 'working source changed during regression'
assert test_hashes == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted((ROOT / 'tests/binding').rglob('*.py'))}, 'tests changed during regression'
suites = ET.parse(xml).getroot().findall('testsuite')
counts = {key: sum(int(s.attrib.get(key, 0)) for s in suites) for key in ('tests', 'failures', 'errors', 'skipped')}
assert counts == dict(tests=expected, failures=0, errors=0, skipped=0), counts
review = dict(status='passed', evaluation_role='discovery_relationship_continuation_software_validation_v1',
    recorded_utc=datetime.now(timezone.utc).isoformat(), source=source, source_sha256=source['code'],
    counts=counts, junit_sha256=base._sha(xml), test_source_sha256=digest(test_hashes),
    validation_runner_sha256=base._sha(__file__), slurm_job_id=os.environ.get('SLURM_JOB_ID'),
    new_model_queries=0, new_fits=0, generated_holdouts_opened=False)
base._put(folder / 'software_validation_review_v1.json', review)
print(json.dumps(dict(status='passed', counts=counts, snapshot_id=source['snapshot_id']), sort_keys=True))
