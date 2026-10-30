"""Durable monitored DAG for matched prompt controls, preserving legacy suites."""
from datetime import datetime,timezone
import importlib.util
from pathlib import Path

from . import overnight_relationship_suite as durable

ROLE='discovery_arithmetic_prompt_suite_v1'
spec=importlib.util.spec_from_file_location(__package__+'._prompt_suite_engine',durable.__file__)
_CORE=importlib.util.module_from_spec(spec);spec.loader.exec_module(_CORE)
_CORE.ROLE=ROLE
_CORE.SCRIPTS={'scripts/173_binding_arithmetic_prompt_behavior.py'}
_legacy_collect=_CORE._collect_outputs


def _collect_outputs(config,state):
    return _legacy_collect(dict(config,nodes=[n for n in config['nodes'] if n['command']=='run']),state)


def _submit_controller(config,state,parent=None):
    module=_CORE._submitter(state['source'])
    argv=['/work/jvl210002/migration/envs/probe-cu129/bin/python',
        str(module.workspace_root(module.ROOT)/'scripts/91_binding_frozen_run.py'),
        state['source']['snapshot'],'scripts/174_binding_arithmetic_prompt_suite.py','watch',state['config_path']]
    job=module.submit('prompt-control-check','dev',argv,dependency='afterany:'+parent if parent else None,
        mem='4G',cpus=1,time='00:10:00',begin='now+10minutes')
    state['controllers'].append(job);_CORE._save(config,state);return job


def _report(config,state,errors):
    stages=[v['state'] for v in state['status'].values()]
    complete=bool(stages) and all(v=='complete' for v in stages)
    terminal=bool(stages) and all(v in ('complete','failed','blocked') for v in stages)
    science=[n for n in config['nodes'] if n['command']=='run']
    attempted=0
    for node in science:
        try:manifest=_CORE.capture._json(Path(node['marker']).parent/'manifest.json')
        except (OSError,ValueError):continue
        attempted+=sum(a.get('prefill_cases_attempted',0) for a in manifest.get('attempts',[]))
    result=dict(status='complete_exploratory' if complete else 'needs_attention' if terminal else 'running',
        evaluation_role=ROLE,config_hash=_CORE.digest(config),recorded_utc=datetime.now(timezone.utc).isoformat(),
        stages=state['status'],attempts=state['attempts'],all_terminal=terminal,scheduler_errors=errors,
        source=state['source'],planned_model_prefills=sum(n['expected_cases'] for n in science),
        observed_model_prefill_attempts=attempted,new_model_queries=0,generated_holdouts_opened=False)
    folder=Path(config['run_dir']);_CORE.capture._journal(folder/'status_review_v1.json',result)
    lines=['# Matched arithmetic prompt control: live status','',f"Status: {result['status']}. Recorded: {result['recorded_utc']}.",'',
           '| Stage | State | Job |','|---|---|---:|']
    for key,value in state['status'].items():lines.append(f"| {key} | {value['state']} | {value.get('job_id','')} |")
    lines+=['','Original baseline answers are cached; preparation makes no model calls. New queries and interruptions remain counted in worker manifests. The monitor retries only eligible scheduler interruptions; scientific failures require review.','']
    from .overnight_relationship_behavior import _replace_owned
    _replace_owned(Path(config['report']),'\n'.join(lines).encode())
    if terminal and not (folder/'results_review_v1.json').exists():
        _CORE.base._put(folder/'results_review_v1.json',dict(result,scientific_results=_CORE._collect_outputs(config,state)))
    return result


_CORE._submit_controller=_submit_controller
_CORE._report=_report
_CORE._collect_outputs=_collect_outputs
submit,watch,status=_CORE.submit,_CORE.watch,_CORE.status
