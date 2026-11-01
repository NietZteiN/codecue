"""Durable CPU-only single-state/all-variable experiment controller."""
import importlib.util
from . import arithmetic_semantic_controls_suite as semantic_suite

ROLE = 'discovery_global_state_suite_v1'
spec = importlib.util.spec_from_file_location(__package__ + '._global_state_suite_engine', semantic_suite.__file__)
_ENGINE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_ENGINE)
_ENGINE.ROLE = ROLE
_CORE = _ENGINE._CORE
_CORE.ROLE = ROLE
_CORE.SCRIPTS = {'scripts/206_binding_global_state.py'}


def controller(config, state, parent=None):
    module = _CORE._submitter(state['source'])
    argv = ['/work/jvl210002/migration/envs/probe-cu129/bin/python',
        str(module.workspace_root(module.ROOT) / 'scripts/91_binding_frozen_run.py'),
        state['source']['snapshot'], 'scripts/207_binding_global_state_suite.py', 'watch', state['config_path']]
    job = module.submit('global-state-check', 'dev,normal', argv,
        dependency='afterany:' + parent if parent else None, mem='4G', cpus=1,
        time='00:10:00', begin='now+10minutes')
    state['controllers'].append(job); _CORE._save(config, state)
    return job


def report(config, state, errors):
    # Reuse durable terminal-state accounting, then render this experiment's wording.
    result = _ENGINE.report(config, state, errors)
    from pathlib import Path
    from .overnight_relationship_behavior import _replace_owned
    lines = ['# All-variable query-state suite: live status', '',
        f"Status: {result['status']}. Updated: {result['recorded_utc']}.", '',
        '| Stage | State | Job | Reason |', '|---|---|---:|---|']
    for key, value in state['status'].items():
        lines.append(f"| {key} | {value['state']} | {value.get('job_id', '')} | {value.get('reason', '')} |")
    lines += ['', 'Frozen regression gates cache preparation and all seven fit cells. '
        'A separate no-fit audit verifies the completed alternate-semantics study. '
        'All science uses archived features and CPU allocations, with no new model calls. '
        'Ten-minute checks continue subject to scheduler QoS. Scientific failures require review.', '']
    _replace_owned(Path(config['report']), '\n'.join(lines).encode())
    return result


_CORE._submit_controller, _CORE._report = controller, report
submit, watch, status = _CORE.submit, _CORE.watch, _CORE.status
