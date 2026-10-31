"""Durable, CPU-only controller for compression/encoding experiments."""
from datetime import datetime, timezone
import importlib.util
from pathlib import Path

from . import overnight_relationship_suite as durable

ROLE = 'discovery_numeric_exploration_suite_v1'
spec = importlib.util.spec_from_file_location(__package__ + '._numeric_exploration_engine', durable.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.ROLE = ROLE
_CORE.SCRIPTS = {'scripts/192_binding_numeric_exploration.py'}


def controller(config, state, parent=None):
    module = _CORE._submitter(state['source'])
    argv = ['/work/jvl210002/migration/envs/probe-cu129/bin/python',
        str(module.workspace_root(module.ROOT) / 'scripts/91_binding_frozen_run.py'),
        state['source']['snapshot'], 'scripts/193_binding_numeric_exploration_suite.py', 'watch', state['config_path']]
    job = module.submit('numeric-exploration-check', 'dev', argv,
        dependency='afterany:' + parent if parent else None, mem='4G', cpus=1,
        time='00:10:00', begin='now+10minutes')
    state['controllers'].append(job)
    _CORE._save(config, state)
    return job


def report(config, state, errors):
    values = [v['state'] for v in state['status'].values()]
    complete = bool(values) and all(v == 'complete' for v in values)
    terminal = bool(values) and all(v in ('complete', 'failed', 'blocked') for v in values)
    result = dict(status='complete_exploratory' if complete else 'needs_attention' if terminal else 'running',
        evaluation_role=ROLE, source=state['source'], config_hash=_CORE.digest(config),
        recorded_utc=datetime.now(timezone.utc).isoformat(), all_terminal=terminal,
        stages=state['status'], attempts=state['attempts'], scheduler_errors=errors,
        new_model_queries=0, generated_holdouts_opened=False)
    folder = Path(config['run_dir'])
    _CORE.capture._journal(folder / 'status_review_v1.json', result)
    lines = ['# Compression and encoding: live status', '',
        f"Status: {result['status']}. Updated: {result['recorded_utc']}.", '',
        '| Stage | State | Job | Reason |', '|---|---|---:|---|']
    for key, value in state['status'].items():
        lines.append(f"| {key} | {value['state']} | {value.get('job_id', '')} | {value.get('reason', '')} |")
    lines += ['', 'CPU-only cached-state work. Full frozen regression precedes caches and readouts. '
        'The fixed-layer role-specific assay retains source/prior/coherent-family controls. '
        'Only eligible scheduler interruptions are retried; scientific failures require review. '
        'Completed fits and unrelated jobs are preserved.', '']
    from .overnight_relationship_behavior import _replace_owned
    _replace_owned(Path(config['report']), '\n'.join(lines).encode())
    if terminal and not (folder / 'results_review_v1.json').exists():
        _CORE.base._put(folder / 'results_review_v1.json', result)
    return result


_CORE._submit_controller = controller
_CORE._report = report
submit, watch, status = _CORE.submit, _CORE.watch, _CORE.status
