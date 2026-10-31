"""Durable CPU DAG for audit, binding, numeric and composition follow-ups."""
from datetime import datetime, timezone
import importlib.util
from pathlib import Path

from . import overnight_relationship_suite as durable

ROLE = 'discovery_arithmetic_state_suite_v1'
spec = importlib.util.spec_from_file_location(__package__ + '._state_suite_engine', durable.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.ROLE = ROLE
_CORE.SCRIPTS = {'scripts/185_binding_state_followup.py'}


def _submit_controller(config, state, parent=None):
    module = _CORE._submitter(state['source'])
    argv = ['/work/jvl210002/migration/envs/probe-cu129/bin/python',
        str(module.workspace_root(module.ROOT) / 'scripts/91_binding_frozen_run.py'),
        state['source']['snapshot'], 'scripts/186_binding_state_suite.py', 'watch', state['config_path']]
    job = module.submit('arithmetic-state-check', 'dev', argv,
        dependency='afterany:' + parent if parent else None, mem='4G', cpus=1, time='00:10:00', begin='now+10minutes')
    state['controllers'].append(job)
    _CORE._save(config, state)
    return job


def _collect_outputs(config, state):
    result = {}
    for node in config['nodes']:
        if state['status'].get(node['key'], {}).get('state') != 'complete' or node['command'] == 'prepare':
            continue
        cfg = _CORE.base._json(node['config'])
        receipt = _CORE.base._json(Path(cfg['run_dir']) / 'completion_manifest_v1.json')
        entry = receipt['artifacts'].get('results', receipt['artifacts'].get('summary'))
        if entry:
            data = _CORE.base._json(entry['path'], entry['sha256'])
            result[node['key']] = dict(source_result=entry, model=data.get('model'),
                new_model_queries=data.get('new_model_queries', 0), summary=data.get('summary'))
    return result


def _report(config, state, errors):
    stages = [v['state'] for v in state['status'].values()]
    complete = bool(stages) and all(v == 'complete' for v in stages)
    terminal = bool(stages) and all(v in ('complete', 'failed', 'blocked') for v in stages)
    result = dict(status='complete_exploratory' if complete else 'needs_attention' if terminal else 'running',
        evaluation_role=ROLE, source=state['source'], config_hash=_CORE.digest(config),
        recorded_utc=datetime.now(timezone.utc).isoformat(), all_terminal=terminal,
        stages=state['status'], attempts=state['attempts'], scheduler_errors=errors,
        new_model_queries=0, generated_holdouts_opened=False)
    folder = Path(config['run_dir'])
    _CORE.capture._journal(folder / 'status_review_v1.json', result)
    lines = ['# Cached-state discovery: live status', '', f"Status: {result['status']}. Updated: {result['recorded_utc']}.", '',
        '| Stage | State | Job | Reason |', '|---|---|---:|---|']
    for key, value in state['status'].items():
        lines.append(f"| {key} | {value['state']} | {value.get('job_id', '')} | {value.get('reason', '')} |")
    lines += ['', 'All work is CPU-only on existing immutable captures. The early validation phase uses CPU allocations. Scientific failures require review; only eligible scheduler interruptions are retried. Completed fits are preserved. Other running work and the editor allocation are preserved.', '']
    from .overnight_relationship_behavior import _replace_owned
    _replace_owned(Path(config['report']), '\n'.join(lines).encode())
    if terminal and not (folder / 'results_review_v1.json').exists():
        _CORE.base._put(folder / 'results_review_v1.json', dict(result, scientific_results=_collect_outputs(config, state)))
    return result


_CORE._submit_controller = _submit_controller
_CORE._collect_outputs = _collect_outputs
_CORE._report = _report
submit, watch, status = _CORE.submit, _CORE.watch, _CORE.status
