"""Accounting-only GPU ledger. Project compute and checkpoint limits are disabled."""
from __future__ import annotations
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import uuid

DEFAULT_LEDGER = 'artifacts/binding/gpu_usage_uncapped.json'
HISTORICAL_LEDGER = 'artifacts/binding/gpu_budget.json'


@contextmanager
def locked(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(path.read_text()) if path.exists() else {'cap_seconds': None, 'checkpoint_policy': 'multiple_cached_checkpoints', 'used_seconds': 0., 'active': {}, 'completed': []}
        yield state
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(state, indent=2) + '\n')
        temp.replace(path)


def reserve(config, stage):
    if config['device'] != 'cuda' or stage not in ('behavior','activations','interventions','interface_diagnostics','protocol_calibration','generation_reference','published_behavior','throughput_profile','checkpoint_suite','ownership_controls'):
        return None
    path = config.get('budget_ledger', DEFAULT_LEDGER)
    if str(Path(path)) == HISTORICAL_LEDGER:
        path = DEFAULT_LEDGER  # Preserve historical accounting; never revive its old limits.
    checkpoint = [config['model'], config['model_revision']]
    with locked(path) as state:
        state['cap_seconds'] = None
        state['checkpoint_policy'] = 'multiple_cached_checkpoints'
        if checkpoint not in state.setdefault('checkpoints', []):
            state['checkpoints'].append(checkpoint)
        lease = {'id': uuid.uuid4().hex, 'ledger': path, 'reserved_seconds': 0,
                 'mode': 'accounting_only',
                 'stage': stage, 'run_dir': config['run_dir'], 'checkpoint': checkpoint,
                 'gpu_count': int(os.environ.get('SLURM_GPUS_ON_NODE') or config.get('tensor_parallel_size', 1))}
        state['active'][lease['id']] = lease
    return lease


def release(lease, seconds, status):
    if lease is None:
        return
    with locked(lease['ledger']) as state:
        if lease['id'] not in state['active']:
            raise ValueError('budget lease already closed')
        state['active'].pop(lease['id'])
        charged = seconds * lease.get('gpu_count', 1)
        state['used_seconds'] += charged
        state['completed'].append({**lease, 'actual_seconds': charged, 'wall_seconds': seconds, 'status': status})
