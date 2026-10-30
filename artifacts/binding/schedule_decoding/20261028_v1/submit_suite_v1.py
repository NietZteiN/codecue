"""Submit only missing finite schedule stages and retain actual scheduler IDs."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from codecue.binding import overnight_relationship_capture as journal
from codecue.binding.snapshots import verify

FOLDER = Path(__file__).resolve().parent
PYTHON = '/work/jvl210002/migration/envs/probe-cu129/bin/python'
source = json.loads((FOLDER / 'execution_source_v1.json').read_text())
assert verify(source['snapshot'])['code']['source_sha256'] == source['code']
for filename in ('target_preflight_review_v1.json',):
    assert json.loads((FOLDER / filename).read_text())['status'] == 'passed'
spec = importlib.util.spec_from_file_location('schedule_slurm_submission', ROOT / 'scripts/slurm/submit.py')
submission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(submission)
progress = FOLDER / 'submission_progress_v1.json'
state = json.loads(progress.read_text()) if progress.exists() else dict(source=source, jobs={})
assert state['source'] == source
jobs = state['jobs']


def submit(key, **options):
    if key in jobs:
        return jobs[key]
    identity = submission.submit(**options)
    assert identity is not None and identity.isdigit()
    jobs[key] = identity
    journal._journal(progress, state)
    return identity


qa = submit('regression', name='schedule-regression', partition='normal',
            cpus=8, mem='16G', time='02:00:00',
            argv=[PYTHON, str(FOLDER / 'run_validation_v1.py')])
for model in ('llama8b', 'codellama34b'):
    prepare = submit(model + '_prepare', name='schedule-' + model + '-prepare',
                     partition='dev,normal', cpus=4, mem='24G', time='02:00:00',
                     argv=[PYTHON, str(FOLDER / 'run_stage_v1.py'), model, 'prepare'])
    capture = submit(model + '_capture', name='schedule-' + model + '-capture',
                     partition='dev-a30,a30,h100,h200' if model == 'llama8b' else 'h100,h200',
                     dependency='afterok:' + prepare, cpus=8,
                     mem='32G' if model == 'llama8b' else '96G',
                     time='02:00:00' if model == 'llama8b' else '2-00:00:00',
                     time_min='00:05:00' if model == 'llama8b' else '00:10:00',
                     argv=[PYTHON, str(FOLDER / 'run_stage_v1.py'), model, 'capture'])
    submit(model + '_readouts', name='schedule-' + model + '-readouts',
           partition='normal', dependency='afterok:' + capture + ':' + qa,
           cpus=8, mem='16G', time='2-00:00:00',
           argv=[PYTHON, str(FOLDER / 'run_stage_v1.py'), model, 'readouts'])
journal._put(FOLDER / 'jobs_v1.json', jobs)
journal._put(FOLDER / 'submission_review_v1.json', dict(
    status='submitted', evaluation_role='discovery_schedule_submission_v1',
    jobs=jobs, source=source, no_project_compute_cap=True,
    gpu_eligibility='8B BF16 short prefills fit 24GiB A30 and larger GPUs; 34B BF16 requires >=72GiB, so H100/H200 only. H200 is eligible to avoid withholding useful available capacity.',
    preserved_unrelated_jobs=['480098'], cancelled_jobs=[],
    finite_stages='prepare -> capture -> capture audit + readout preflight/run/audit; readouts also require passing full regression',
    stage_harness_sha256=journal._sha(FOLDER / 'run_stage_v1.py'),
    new_model_queries_at_submission=0, generated_holdouts_opened=False))
print(json.dumps(dict(status='submitted', jobs=jobs), sort_keys=True))
