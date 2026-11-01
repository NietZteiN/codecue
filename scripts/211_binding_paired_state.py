#!/usr/bin/env python
"""Execute frozen paired source, native preflight and calibration stages."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_paired_stage as study, arithmetic_paired_calibration as calibration

REPORT = 'discovery_arithmetic_paired_report_v1'


def report(config):
    source = study.common.validate_role(config, REPORT); study.semantic.literature(config)
    folder = Path(config['run_dir'])
    if (folder / 'completion_manifest_v1.json').exists(): return study.common.completed(config)
    lines = ['# Paired timing/overwrite/query-scope calibration', '',
        'Discovery calibration only; formal-cohort inference remains unscheduled. '
        'All wording variants are retained. No best wording is selected from DEV or calibration. '
        'Accuracy includes every invalid/truncated response in its denominator. '
        'Finite template/seed cases are correlated and are not confirmation evidence.', '',
        '| Model | Protocol | Scope | Cases | Joint accuracy | Per-slot accuracy | Invalid/truncated |',
        '|---|---|---|---:|---:|---:|---:|']
    inputs, model_gates, calls = {}, {}, 0
    for request in config['workers']:
        worker = study.base._json(request['path'], request['sha256']); study.common.completed(worker)
        path = Path(worker['run_dir']) / 'results.json'; data = study.base._json(path)
        inputs[request['path']] = study.storage._pin(path); calls += data['new_model_queries']
        model_gates[data['model']] = data['summary']['gates']
        # Reconstruct the planned intersections from immutable response batches.
        rows = []
        for batch in sorted(Path(worker['run_dir']).glob('batch_*.json')): rows.extend(study.base._json(batch)['records'])
        if calibration.summarize(rows) != data['summary']: raise ValueError('saved calibration metrics differ')
        for protocol in study.programs.PROTOCOLS:
            for scope in study.programs.SCOPES:
                selected = [r for r in rows if r['protocol'] == protocol and r['scope'] == scope]
                metrics = calibration.summarize(selected)['cells']['overall']
                lines.append(f"| {data['model']} | {protocol} | {scope} | {metrics['rows']} | "
                    f"{100*metrics['joint_accuracy']:.2f}% | {100*metrics['slot_accuracy']:.2f}% | {metrics['invalid_or_truncated']} |")
    lines += ['', '## Frozen output-only competence gates', '',
        'Each scope and instruction must separately pass literal ≥95%, copy ≥90%, and one-hop arithmetic ≥70% joint accuracy '
        'on depth-zero calibration cases. These are feasibility thresholds, not significance tests. '
        'Stepwise and intermediate-query protocols remain separate diagnostics.', '',
        '| Model | Scope | Task | Instruction | Cases | Accuracy | Required | Pass |',
        '|---|---|---|---:|---:|---:|---:|---|']
    for model, gates in model_gates.items():
        for gate in gates:
            value = f"{100*gate['accuracy']:.2f}%" if gate['accuracy'] is not None else 'undefined'
            lines.append(f"| {model} | {gate['scope']} | {gate['kind']} | {gate['instruction']} | {gate['rows']} | "
                f"{value} | {100*gate['threshold']:.0f}% | {gate['passed']} |")
    lines += ['', 'Passing calibration alone does not validate global readouts or causal use. '
        'Any protocol revision retains this pilot and must be frozen before formal collection. '
        'Pre-trace generation boundaries are not pre-answer states for stepwise/intermediate protocols. '
        'No gold intermediate is teacher-forced. Native RHS/newline collapse and value visibility remain explicit in preflight records.', '']
    path = Path(config['report']); study.base._publish(path, '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', evaluation_role=REPORT, source=source, config_hash=study.digest(config),
        inputs=inputs, competence_gates=model_gates, new_model_queries=0, total_calibration_prompts=calls, formal_capture_submitted=False,
        generated_holdouts_opened=False)
    # This is a report of prior calls, not an additional inference stage.
    return study.common.receipt(config, source, result, dict(report=study.storage._pin(path)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run', 'audit']); parser.add_argument('config')
    args = parser.parse_args(); config = study.base._json(args.config)
    try:
        with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))):
            role = config['evaluation_role']
            if role == 'arithmetic_graph_software_validation_v1':
                spec = importlib.util.spec_from_file_location('paired_state_qa', Path(__file__).with_name('167_binding_arithmetic_graph_capture.py'))
                module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); result = module.qa(config)
            elif args.command == 'audit': result = study.common.completed(config)
            else: result = {study.PREPARE: study.prepare, study.NATIVE: study.native, calibration.ROLE: calibration.run, REPORT: report}[role](config)
        print(json.dumps(dict(status=result.get('status'), role=role, new_model_queries=result.get('new_model_queries', 0))), flush=True)
    except Exception as exc:
        study.base._put(Path(config['run_dir']) / f"failure_{os.environ.get('SLURM_JOB_ID', 'manual')}_review.json",
            dict(status='failed', error=f'{type(exc).__name__}: {exc}', partial_results_preserved=True))
        raise


if __name__ == '__main__': main()
