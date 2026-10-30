"""Durable DAG for local arithmetic capture, calibration and shared probes."""
from datetime import datetime, timezone
import importlib.util
from pathlib import Path

from . import overnight_relationship_suite as durable

ROLE = 'discovery_arithmetic_local_suite_v1'
spec = importlib.util.spec_from_file_location(__package__ + '._local_suite_engine', durable.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.ROLE = ROLE
_CORE.SCRIPTS = {'scripts/167_binding_arithmetic_graph_capture.py', 'scripts/177_binding_arithmetic_local_capture.py',
                 'scripts/178_binding_arithmetic_local_probes.py', 'scripts/179_binding_arithmetic_local_behavior.py'}
_legacy_reconcile = _CORE.reconcile


def reconcile(config, state, observed):
    actions = _legacy_reconcile(config, state, observed)
    # Local CPU probes can use a completed capture while other GPU work runs.
    # Actual scheduler QoS decides capacity; no additional phase barrier.
    for node in config['nodes']:
        if (node['phase'] == 'cpu' and node['key'] not in actions
                and state['status'][node['key']]['state'] in ('planned', 'retry')
                and all(state['status'][key]['state'] == 'complete' for key in node['dependencies'])):
            actions.append(node['key'])
    return actions


def _submit_controller(config, state, parent=None):
    module = _CORE._submitter(state['source'])
    argv = ['/work/jvl210002/migration/envs/probe-cu129/bin/python',
        str(module.workspace_root(module.ROOT) / 'scripts/91_binding_frozen_run.py'),
        state['source']['snapshot'], 'scripts/180_binding_arithmetic_local_suite.py', 'watch', state['config_path']]
    job = module.submit('arithmetic-local-check', 'dev', argv,
        dependency='afterany:' + parent if parent else None, mem='4G', cpus=1, time='00:10:00', begin='now+10minutes')
    state['controllers'].append(job)
    _CORE._save(config, state)
    return job


def _collect_outputs(config, state):
    result = {}
    for node in config['nodes']:
        if state['status'].get(node['key'], {}).get('state') != 'complete' or node['command'] != 'run':
            continue
        cfg = _CORE.base._json(node['config'])
        receipt = _CORE.base._json(Path(cfg['run_dir']) / 'completion_manifest_v1.json')
        label = 'results' if node['script'].endswith('probes.py') else 'summary'
        entry = receipt['artifacts'][label]
        data = _CORE.base._json(entry['path'], entry['sha256'])
        result[node['key']] = dict(source_result=entry, model=data.get('model'), cases=data.get('cases'),
            selected_methods=data.get('selected_methods'), metrics=data.get('metrics'))
    return result


def _report(config, state, errors):
    stages = [v['state'] for v in state['status'].values()]
    complete = bool(stages) and all(v == 'complete' for v in stages)
    terminal = bool(stages) and all(v in ('complete', 'failed', 'blocked') for v in stages)
    prefills, answers = 0, 0
    for node in config['nodes']:
        if node['command'] != 'run':
            continue
        try:
            cfg = _CORE.base._json(node['config'])
            journal = _CORE.base._json(Path(cfg['run_dir']) / 'manifest.json')
        except (OSError, ValueError):
            continue
        prefills += sum(a.get('prefill_cases_attempted', 0) for a in journal.get('attempts', []))
        answers += sum(a.get('generated_answers_attempted', 0) for a in journal.get('attempts', []))
    result = dict(status='complete_exploratory' if complete else 'needs_attention' if terminal else 'running',
        evaluation_role=ROLE, source=state['source'], config_hash=_CORE.digest(config),
        recorded_utc=datetime.now(timezone.utc).isoformat(), all_terminal=terminal,
        stages=state['status'], attempts=state['attempts'], scheduler_errors=errors,
        observed_capture_prefill_attempts=prefills, observed_generated_answers_attempted=answers,
        planned_capture_prefills=10584, planned_generated_answers=11016, generated_holdouts_opened=False)
    folder = Path(config['run_dir'])
    _CORE.capture._journal(folder / 'status_review_v1.json', result)
    lines = ['# Local arithmetic discovery: live status', '', f"Status: {result['status']}. Updated: {result['recorded_utc']}.", '',
        '| Stage | State | Job | Reason |', '|---|---|---:|---|']
    for key, value in state['status'].items():
        lines.append(f"| {key} | {value['state']} | {value.get('job_id', '')} | {value.get('reason', '')} |")
    lines += ['', 'Whole structural families stay grouped. Scientific failures require review. Only resumable scheduler interruptions are retried; repeated interruptions without committed progress stop retries. Existing jobs outside the suite are preserved.', '']
    from .overnight_relationship_behavior import _replace_owned
    _replace_owned(Path(config['report']), '\n'.join(lines).encode())
    if terminal and not (folder / 'results_review_v1.json').exists():
        _CORE.base._put(folder / 'results_review_v1.json', dict(result, scientific_results=_collect_outputs(config, state)))
    return result


_CORE._submit_controller = _submit_controller
_CORE._collect_outputs = _collect_outputs
_CORE._report = _report
_CORE.reconcile = reconcile
submit, watch, status = _CORE.submit, _CORE.watch, _CORE.status
