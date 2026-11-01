"""Durable CPU-only conditional readout experiment DAG."""
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
from . import overnight_relationship_suite as durable

ROLE = 'discovery_arithmetic_conditional_suite_v1'
spec = importlib.util.spec_from_file_location(__package__ + '._conditional_suite_engine', durable.__file__)
_CORE = importlib.util.module_from_spec(spec); spec.loader.exec_module(_CORE)
_CORE.ROLE = ROLE
_CORE.SCRIPTS = {'scripts/220_binding_conditional_state.py'}


def controller(config, state, parent=None):
    module = _CORE._submitter(state['source'])
    argv = ['/work/jvl210002/migration/envs/probe-cu129/bin/python',
        str(module.workspace_root(module.ROOT) / 'scripts/91_binding_frozen_run.py'), state['source']['snapshot'],
        'scripts/221_binding_conditional_suite.py', 'watch', state['config_path']]
    job = module.submit('conditional-state-check', 'dev,normal', argv,
        dependency='afterany:' + parent if parent else None, mem='4G', cpus=1, time='00:10:00', begin='now+10minutes')
    state['controllers'].append(job); _CORE._save(config, state)
    return job


def report(config, state, errors):
    values = [v['state'] for v in state['status'].values()]
    complete = bool(values) and all(v == 'complete' for v in values)
    terminal = bool(values) and all(v in ('complete', 'failed', 'blocked') for v in values)
    result = dict(status='complete_exploratory' if complete else 'needs_attention' if terminal else 'running',
        evaluation_role=ROLE, source=state['source'], config_hash=_CORE.digest(config),
        recorded_utc=datetime.now(timezone.utc).isoformat(), all_terminal=terminal, stages=state['status'],
        attempts=state['attempts'], scheduler_errors=errors, generated_holdouts_opened=False, new_model_queries=0)
    folder = Path(config['run_dir']); _CORE.capture._journal(folder / 'status_review_v1.json', result)
    lines = ['# Conditional numeric readouts: live status', '', f"Status: {result['status']}. Updated: {result['recorded_utc']}.", '',
        '| Stage | State | Job | Reason |', '|---|---|---:|---|']
    for key, value in state['status'].items():
        lines.append(f"| {key} | {value['state']} | {value.get('job_id', '')} | {value.get('reason', '')} |")
    lines += ['', 'Frozen regression gates eight independently TRAIN-selected CPU readout cells using archived states. '
        'Source-only, nominal-capacity source, hidden-only, joint and independently fitted shuffled-hidden controls '
        'test predictive gain within declared feature classes. No new language-model queries, layer search or sealed-final access. '
        'Immutable banks resume on scheduler retries; scientific errors stop dependencies. Ten-minute checks stop at terminal completion.', '']
    from .overnight_relationship_behavior import _replace_owned
    _replace_owned(Path(config['report']), '\n'.join(lines).encode())
    if terminal and not (folder / 'results_review_v1.json').exists(): _CORE.base._put(folder / 'results_review_v1.json', result)
    return result


_CORE._submit_controller, _CORE._report = controller, report
submit, watch, status = _CORE.submit, _CORE.watch, _CORE.status
