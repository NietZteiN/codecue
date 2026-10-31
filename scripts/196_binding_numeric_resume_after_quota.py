#!/usr/bin/env python
"""Resume only the six reviewed EDQUOT jobs, retaining scheduler history."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('numeric_quota_recovery', Path(__file__).with_name('195_binding_numeric_storage_recovery.py'))
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
base, suite, study = recovery.base, recovery.suite, recovery.study


def main():
    proof = base._json(recovery.ROOT / 'storage_recovery_review_v1.json')
    if proof['status'] != 'recovered_verified' or proof['new_fits'] != 0:
        raise ValueError('successful no-fit recovery review required')
    if base._sha(proof['recovery_script']['path']) != proof['recovery_script']['sha256']:
        raise ValueError('original recovery source changed')
    config = base._json(recovery.CFG / 'suite.json')
    with suite._CORE._lock(Path(config['run_dir'])):
        suite._CORE._config(config)
        state = base._json(Path(config['run_dir']) / 'jobs_live_v1.json')
        if state.get('storage_recovery_rearmed'):
            raise ValueError('owned recovery has already been rearmed')
        source = suite._CORE._source(recovery.SNAPSHOT, config)
        if state['source'] != source: raise ValueError('suite source identity differs')
        ids = [attempts[-1]['job_id'] for attempts in state['attempts'].values() if attempts]
        observed, errors = suite._CORE.scheduler(ids)
        if errors: raise ValueError('scheduler inspection failed: ' + str(errors))
        suite._CORE.reconcile(config, state, observed)
        for key, job in recovery.FAILED.items():
            if state['attempts'][key][-1]['job_id'] != job or observed[job]['state'] != 'FAILED':
                raise ValueError('only the reviewed failed jobs can be resumed')
        for name in ['llama8b_cache', 'codellama34b_cache', 'source_cache']:
            study.common.completed(base._json(recovery.CFG / (name + '.json')))
        state['storage_recovery_rearmed'] = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
            reviewed_jobs=recovery.FAILED, review=study.storage._pin(recovery.ROOT / 'storage_recovery_review_v1.json'),
            retry_script=study.storage._pin(Path(__file__)),
            rationale='Reviewed EDQUOT: caches verified, outputs relocated, saved banks preserved. Frozen protocol unchanged.')
        suite._CORE._save(config, state)
        suite.controller(config, state)
        for node in config['nodes']:
            if node['key'] in recovery.FAILED:
                suite._CORE._submit_node(config, state, node)
        suite._CORE._save(config, state)
    print(json.dumps(suite.status(config)['stages']), flush=True)


if __name__ == '__main__':
    main()
