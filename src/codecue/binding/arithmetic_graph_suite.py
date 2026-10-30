"""Isolated durable scheduler for arithmetic graph discovery and morning audit."""
from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path

from . import overnight_relationship_suite as durable

ROLE = 'discovery_arithmetic_graph_suite_v1'
spec = importlib.util.spec_from_file_location(__package__+'._arithmetic_suite_engine', durable.__file__)
_CORE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_CORE)
_CORE.ROLE = ROLE
_CORE.SCRIPTS = {'scripts/167_binding_arithmetic_graph_capture.py',
                 'scripts/168_binding_arithmetic_graph_readouts.py',
                 'scripts/169_binding_arithmetic_graph_behavior.py'}


def _submit_controller(config, state, parent=None):
    module = _CORE._submitter(state['source'])
    argv = ['/work/jvl210002/migration/envs/probe-cu129/bin/python',
            str(module.workspace_root(module.ROOT)/'scripts/91_binding_frozen_run.py'),
            state['source']['snapshot'], 'scripts/170_binding_arithmetic_graph_suite.py', 'watch', state['config_path']]
    job = module.submit('arithmetic-night-controller', 'dev', argv,
                        dependency='afterany:'+parent if parent else None,
                        mem='4G', cpus=1, time='00:10:00', begin='now+10minutes')
    state['controllers'].append(job)
    _CORE._save(config, state)
    return job


def _collect_outputs(config, state):
    result = {}
    for node in config['nodes']:
        if state['status'].get(node['key'], {}).get('state') != 'complete':
            continue
        cfg = _CORE.base._json(node['config'])
        if node['command'] not in ('readouts', 'behavior'):
            continue
        receipt = _CORE.base._json(Path(cfg['run_dir'])/'completion_manifest_v1.json')
        label = 'results' if node['command'] == 'readouts' else 'summary'
        entry = receipt['artifacts'][label]
        if _CORE.base._sha(entry['path']) != entry['sha256']:
            raise ValueError('completed arithmetic summary changed')
        data = _CORE.base._json(entry['path'])
        result[node['key']] = dict(model=data.get('model'), cases=data.get('cases'),
            contrasts=data.get('contrasts'), metrics=data.get('metrics'), source_result=entry)
    return result


def morning(config):
    result = _CORE.status(config)
    path = Path(config['run_dir'])/'actual_morning_review_v1.json'
    _CORE.base._put(path, dict(result, actual_morning_utc=datetime.now(timezone.utc).isoformat(),
                              scientific_results=_collect_outputs(config, _CORE.capture._json(Path(config['run_dir'])/'jobs_live_v1.json'))))
    return result


_CORE._submit_controller, _CORE._collect_outputs = _submit_controller, _collect_outputs
submit, watch, status = _CORE.submit, _CORE.watch, _CORE.status
