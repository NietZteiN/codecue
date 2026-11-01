#!/usr/bin/env python
"""Run frozen prior preparation, extended readouts, numerical audit or report."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_penalty_path as study, arithmetic_penalty_review as review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'audit']); parser.add_argument('config')
    args = parser.parse_args(); config = study.base._json(args.config)
    try:
        with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))):
            role = config['evaluation_role']
            if role == 'arithmetic_graph_software_validation_v1':
                spec = importlib.util.spec_from_file_location('penalty_qa', Path(__file__).with_name('167_binding_arithmetic_graph_capture.py'))
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); result = module.qa(config)
            elif args.command == 'audit': result = study.common.completed(config)
            else: result = {study.PRIORS: study.prepare_priors, study.FIT: study.run, study.AUDIT: review.audit, study.REPORT: review.report}[role](config)
        print(json.dumps(dict(status=result.get('status'), role=role, new_model_queries=0,
            new_readout_fits=result.get('new_readout_fits', 0), reused_readout_banks=result.get('reused_readout_banks', 0))), flush=True)
    except Exception as exc:
        study.base._put(Path(config['run_dir']) / f"failure_{os.environ.get('SLURM_JOB_ID', 'manual')}_review.json",
            dict(status='failed', error=f'{type(exc).__name__}: {exc}', partial_results_preserved=True))
        raise


if __name__ == '__main__': main()
