#!/usr/bin/env python
"""Freeze regression, calibration diagnostics, and length-continuation assays."""
import hashlib
import json
import os
from pathlib import Path
import shutil
from codecue.binding import arithmetic_paired_exploration as study, arithmetic_paired_exploration_suite as suite
from codecue.binding.snapshots import freeze


def main():
    out = Path('artifacts/binding/arithmetic_paired_exploration/20261101_v2')
    cfg = Path('configs/binding/arithmetic_paired_exploration_20261101_v2')
    scratch = Path('/scratch/juno/jvl210002/codecue/arithmetic_paired_exploration/20261101_v2')
    plan = Path('reports/binding/arithmetic_paired_exploration_plan_20261101_v2.md')
    if any(p.exists() for p in (out, cfg, scratch)): raise ValueError('preserve existing experiment editions')
    if shutil.disk_usage(scratch.parent.parent).free < 10 * 1024**3: raise ValueError('scratch capacity check failed')
    cfg.mkdir(parents=True); out.mkdir(parents=True); scratch.mkdir(parents=True)
    check = scratch / 'storage_probe.bin'
    with check.open('xb') as stream:
        stream.write(b'paired exploration write/fsync check\n'); stream.flush(); os.fsync(stream.fileno())
    if check.read_bytes() != b'paired exploration write/fsync check\n': raise ValueError('scratch roundtrip differs')
    references = dict(report=study.storage._pin('reports/binding/probing_literature_review_20261031_v1.md'),
        register=study.storage._pin('artifacts/binding/literature/probing_methods_20261031_review_v1.json'))
    study.semantic.literature(dict(literature=references))
    archive = out / 'regression_sources'; root = Path(__file__).resolve().parents[1]; test_files = {}
    for path in sorted((root / 'tests/binding').glob('*.py')):
        relative = path.relative_to(root); target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
        test_files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    minimum_tests = 2612
    study.base._put(cfg / 'qa.json', dict(evaluation_role='arithmetic_graph_software_validation_v1',
        run_dir=str(out / 'qa'), test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=minimum_tests))
    if (cfg / 'qa.json').stat().st_size > 16 * 1024: raise ValueError('QA config size exceeded')
    nodes = []
    def node(key, path, deps, *, qa=False, cpus=4, mem='12G', partition='dev,normal', gpu=False):
        nodes.append(dict(key=key, script='scripts/214_binding_paired_exploration.py', command='prepare' if qa else 'run',
            config=str(path), config_sha256=study.base._sha(path), dependencies=deps, phase='gpu' if qa else 'cpu',
            partition=partition, cpus=cpus, mem=mem, time='2-00:00:00' if gpu else '02:00:00',
            time_min='00:30:00' if gpu else None, expected_cases=0,
            marker=str(out / ('qa/regression_review.json' if qa else key + '/completion_manifest_v1.json')),
            marker_status='passed' if qa else 'complete_exploratory'))
    node('software_validation', cfg / 'qa.json', [], qa=True, cpus=8, mem='24G')
    def fields(role, key):
        target = scratch / key; target.mkdir(); (out / key).symlink_to(target, target_is_directory=True)
        return dict(evaluation_role=role, run_dir=str(out / key), seeds=[11, 29, 47], literature=references,
            declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan))
    pilots = {name: study.storage._pin(f'configs/binding/arithmetic_paired_20261101_v1/{name}_calibration.json')
        for name in ('llama8b', 'codellama34b')}
    path = cfg / 'error_audit.json'
    study.base._put(path, dict(fields(study.AUDIT, 'error_audit'), pilots=pilots))
    audit = study.storage._pin(path); node('error_audit', path, ['software_validation'])
    path = cfg / 'audit_report.json'
    study.base._put(path, dict(fields(study.REPORT, 'audit_report'), audit=audit, continuations={},
        report='reports/binding/arithmetic_paired_error_audit_20261101_v2.md'))
    node('audit_report', path, ['error_audit'])
    workers = {}
    for name, batch, partition in [('llama8b', 64, 'h100,h200'), ('codellama34b', 32, 'h200')]:
        key = name + '_continuation'; path = cfg / (key + '.json')
        study.base._put(path, dict(fields(study.CONTINUE, key), pilot=pilots[name],
            total_generated_token_ceiling=study.CAP, generation_batch_size=batch))
        workers[name] = study.storage._pin(path)
        node(key, path, ['error_audit'], cpus=8, mem='96G', partition=partition, gpu=True)
    path = cfg / 'report.json'
    study.base._put(path, dict(fields(study.REPORT, 'report'), audit=audit, continuations=workers,
        report='reports/binding/arithmetic_paired_exploration_findings_20261101_v2.md'))
    node('report', path, [name + '_continuation' for name in pilots])
    config = dict(evaluation_role=suite.ROLE, run_dir=str(out / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_paired_exploration_status_20261101_v2.md', morning_at='2026-11-02T08:00:00-06:00',
        declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan), software_validation=dict(
            review=str(out / 'qa/regression_review.json'), junit=str(out / 'qa/regression.xml'), minimum_tests=minimum_tests))
    suite._CORE._config(config); study.base._put(cfg / 'suite.json', config)
    source = freeze(); snapshot = Path(source['snapshot']); manifest = study.base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(snapshot / name, target)
    study.base._put(out / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__': main()
