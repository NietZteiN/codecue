#!/usr/bin/env python
"""Profile the balanced smoke, then run the complete eligible discovery cohort.

No optional training. Final test remains sealed. Representations/interventions need
separate predeclared allocations after behavioral inspection.
"""
import json
import subprocess
import sys
import time
from pathlib import Path
from codecue.binding.behavior import run, select
from codecue.binding.analysis import report
from codecue.binding.datasets import read_jsonl, write_json, digest

smoke_path, pilot_path = map(Path, sys.argv[1:3])
smoke, pilot = [json.loads(p.read_text()) for p in (smoke_path, pilot_path)]
if smoke['model'] != pilot['model'] or smoke['model_revision'] != pilot['model_revision']:
    raise ValueError('the smoke profile must match the pilot checkpoint')
started = time.monotonic()
summary = run(smoke)
if not summary['complete']:
    raise SystemExit('smoke incomplete; inspect raw outputs and failures before pilot')
report(Path(smoke['run_dir']))
manifest = json.loads((Path(smoke['run_dir'])/'behavior/manifest.json').read_text())
if summary['accuracy']['estimate'] < 0.1 or summary['accuracy']['estimate'] > 0.95:
    write_json(Path(pilot['run_dir'])/'difficulty_review.json',
        {'status':'development_redesign_needed', 'smoke_accuracy':summary['accuracy'],
         'reason':'near floor or ceiling; inspect development before scaling'})
    raise SystemExit('smoke near floor/ceiling; no larger pilot launched')
profile_path = Path(pilot['run_dir'])/'profile.json'
requested_config_hash = digest(pilot)
if profile_path.exists():
    previous = json.loads(profile_path.read_text())
    if previous['requested_config_hash'] != requested_config_hash:
        raise ValueError('pipeline resume requested configuration mismatch')
    run(previous['effective_config'])
    report(Path(previous['effective_config']['run_dir']))
    raise SystemExit(0)
all_rows = select(read_jsonl(pilot['dataset']), pilot)
# Conservative throughput from actual end-to-end elapsed, plus 50% headroom.
estimated_seconds = manifest['wall_seconds_total'] / summary['n'] * len(all_rows) * 1.5
original_per_cell = len({r['base_id'] for r in all_rows}) // 12
chosen = original_per_cell
pilot['max_gpu_seconds'] = None
profile = {'smoke_samples': summary['n'], 'smoke_wall_seconds': manifest['wall_seconds_total'],
           'full_discovery_samples': len(all_rows), 'full_discovery_estimated_seconds_with_headroom': estimated_seconds,
           'requested_config_hash': requested_config_hash, 'remaining_seconds': None, 'bases_per_cell': chosen, 'full_bases_per_cell': original_per_cell,
           'scientific_status': 'all outputs discovery; heldout test untouched', 'effective_config': pilot}
write_json(profile_path, profile)
write_json(Path(pilot['run_dir'])/'effective_config.json', pilot)
# Reloading after run() releases its local model references; clear allocator caches.
import gc, torch
gc.collect()
torch.cuda.empty_cache()
run(pilot)
report(Path(pilot['run_dir']))
write_json(Path(pilot['run_dir'])/'pipeline_resource.json',
           {'wall_seconds':time.monotonic()-started, 'cap_seconds':None})
