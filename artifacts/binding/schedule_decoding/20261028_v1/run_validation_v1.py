"""Certify all binding checks against the frozen dynamic-schedule source."""
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
from codecue.binding import relationship_capture as bounded, snapshots
from codecue.binding.datasets import digest

folder = Path(__file__).resolve().parent
source = json.loads((folder / 'execution_source_v1.json').read_text())
snapshots.verify(source['snapshot'])
assert digest(snapshots.hashes(ROOT)) == source['code']
files = sorted((ROOT / 'tests/binding').rglob('*.py'))
checksums = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
xml = folder / 'regression_v1.xml'
stdout = folder / 'regression_stdout_v1.txt'
assert not xml.exists() and not stdout.exists(), 'regression outputs already exist'
with stdout.open('wb') as stream:
    process = subprocess.run([sys.executable, '-m', 'pytest', 'tests/binding', '-q',
                              '--junitxml=' + str(xml)], cwd=ROOT,
                             env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')),
                             stdout=stream, stderr=subprocess.STDOUT)
assert process.returncode == 0, 'binding regression failed; see saved stdout and JUnit'
assert digest(snapshots.hashes(ROOT)) == source['code'], 'working source changed during regression'
assert checksums == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted((ROOT / 'tests/binding').rglob('*.py'))}
suites = ET.parse(xml).getroot().findall('testsuite')
counts = {key: sum(int(s.attrib.get(key, 0)) for s in suites)
          for key in ('tests', 'failures', 'errors', 'skipped')}
assert counts['tests'] > 1843 and counts['failures'] == counts['errors'] == counts['skipped'] == 0
review = dict(status='passed', evaluation_role='discovery_schedule_software_validation_v1',
              recorded_utc=datetime.now(timezone.utc).isoformat(), source=source,
              counts=counts, junit_sha256=bounded._sha(xml),
              test_source_sha256=digest(checksums), software_file_sha256=checksums,
              validation_runner_sha256=bounded._sha(__file__),
              slurm_job_id=os.environ.get('SLURM_JOB_ID'), new_model_queries=0,
              new_fits=0, generated_holdouts_opened=False)
bounded._put(folder / 'software_validation_review_v1.json', review)
print(json.dumps(dict(status='passed', counts=counts), sort_keys=True))
