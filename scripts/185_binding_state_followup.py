#!/usr/bin/env python
"""Frozen CPU-only state audit, readouts, composition and reports."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path

from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_state_audit as audit
from codecue.binding import arithmetic_state_common as common
from codecue.binding import arithmetic_binding_readouts as binding
from codecue.binding import arithmetic_numeric_readouts as numeric
from codecue.binding import arithmetic_capacity_followup as capacity
from codecue.binding import arithmetic_state_compose as compose
from codecue.binding import arithmetic_state_report as reports
from codecue.binding import relationship_capture as base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'audit'])
    parser.add_argument('config')
    args = parser.parse_args()
    config = base._json(args.config)
    threads = int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))
    import torch
    torch.set_num_threads(threads)
    try:
        with threadpool_limits(limits=threads):
            if config['evaluation_role'] == 'arithmetic_graph_software_validation_v1':
                path = Path(__file__).with_name('167_binding_arithmetic_graph_capture.py')
                spec = importlib.util.spec_from_file_location('state_frozen_qa', path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                result = module.qa(config)
            elif args.command == 'audit':
                result = audit.audit(config) if config['evaluation_role'] == audit.ROLE else common.completed(config)
            else:
                workers = {audit.ROLE: audit.run, binding.ROLE: binding.run, numeric.ROLE: numeric.run,
                    capacity.ROLE: capacity.run, compose.ROLE: compose.run,
                    reports.AUDIT_ROLE: reports.audit_report, reports.STATE_ROLE: reports.state_report}
                result = workers[config['evaluation_role']](config)
        print(json.dumps(dict(status=result.get('status'), role=config['evaluation_role'],
            completed_banks=len(result.get('fits', [])), new_model_queries=0)))
    except Exception as exc:
        job = os.environ.get('SLURM_JOB_ID', 'manual')
        base._put(Path(config['run_dir']) / f'failure_{job}_review.json', dict(status='failed',
            recorded_utc=datetime.now(timezone.utc).isoformat(), slurm_job_id=job,
            error=f'{type(exc).__name__}: {exc}', new_model_queries=0, partial_results_preserved=True))
        raise
    try:
        from codecue.binding.experiment_log_scheduler import tick
        from codecue.binding.registry import ROOT
        from codecue.binding.snapshots import workspace_root
        tick(workspace_root(ROOT), force=True)
    except Exception as exc:
        print(f'Experiment logging refresh deferred: {type(exc).__name__}: {exc}', flush=True)


if __name__ == '__main__':
    main()
