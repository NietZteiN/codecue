#!/usr/bin/env python
"""Freeze paired source/native/calibration gates with scratch-first artifacts."""
import hashlib
import json
import os
from pathlib import Path
import shutil
from codecue.binding import arithmetic_paired_stage as study, arithmetic_paired_suite as suite
from codecue.binding import arithmetic_paired_calibration as calibration
from codecue.binding.snapshots import freeze


def main():
    out = Path('artifacts/binding/arithmetic_paired/20261101_v1')
    cfg = Path('configs/binding/arithmetic_paired_20261101_v1')
    scratch = Path('/scratch/juno/jvl210002/codecue/arithmetic_paired/20261101_v1')
    plan = Path('reports/binding/arithmetic_paired_plan_20261101_v1.md')
    if any(p.exists() for p in (out, cfg, scratch)): raise ValueError('preserve existing paired experiment editions')
    if shutil.disk_usage(scratch.parent.parent).free < 20 * 1024**3: raise ValueError('scratch capacity preflight failed')
    cfg.mkdir(parents=True); out.mkdir(parents=True); scratch.mkdir(parents=True)
    check = scratch / 'storage_probe.bin'
    with check.open('xb') as stream:
        stream.write(b'paired experiment scratch write/fsync check\n'); stream.flush(); os.fsync(stream.fileno())
    if check.read_bytes() != b'paired experiment scratch write/fsync check\n': raise ValueError('scratch roundtrip failed')
    references = dict(report=study.storage._pin('reports/binding/probing_literature_review_20261031_v1.md'),
        register=study.storage._pin('artifacts/binding/literature/probing_methods_20261031_review_v1.json'))
    study.semantic.literature(dict(literature=references))
    archive = out / 'regression_sources'; root = Path(__file__).resolve().parents[1]
    test_files = {}
    for path in sorted((root / 'tests/binding').glob('*.py')):
        relative = path.relative_to(root); target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
        test_files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    minimum_tests = 2570
    study.base._put(cfg / 'qa.json', dict(evaluation_role='arithmetic_graph_software_validation_v1',
        run_dir=str(out / 'qa'), test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=minimum_tests))
    if (cfg / 'qa.json').stat().st_size > 16 * 1024: raise ValueError('QA config exceeds frozen verification limit')
    nodes = []
    def node(key, path, deps, *, qa=False, cpus=8, mem='24G', time='02:00:00', partition='dev,normal'):
        nodes.append(dict(key=key, script='scripts/211_binding_paired_state.py', command='prepare' if qa else 'run',
            config=str(path), config_sha256=study.base._sha(path), dependencies=deps, phase='gpu' if qa else 'cpu',
            partition=partition, cpus=cpus, mem=mem, time=time, time_min=None, expected_cases=0,
            marker=str(out / ('qa/regression_review.json' if qa else key + '/completion_manifest_v1.json')),
            marker_status='passed' if qa else 'complete_exploratory'))
    node('software_validation', cfg / 'qa.json', [], qa=True)
    def fields(role, key, large=True):
        folder = out / key
        if large:
            target = scratch / key; target.mkdir(); folder.symlink_to(target, target_is_directory=True)
        return dict(evaluation_role=role, run_dir=str(folder), seeds=[11, 29, 47], literature=references,
            declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan))
    path = cfg / 'sources.json'
    study.base._put(path, fields(study.PREPARE, 'sources'))
    dataset = study.storage._pin(path); node('sources', path, ['software_validation'])
    native = {}
    profiles = {}
    for name in ('llama8b', 'codellama34b'):
        profile = study.storage._pin(f'configs/binding/arithmetic_graph_20261029_v3/{name}_capture.json')
        profiles[name] = profile
        key = name + '_native'; path = cfg / (key + '.json')
        study.base._put(path, dict(fields(study.NATIVE, key), dataset_config=dataset, profile=profile))
        native[name] = study.storage._pin(path); node(key, path, ['sources'], cpus=16, mem='32G')
    workers = []
    for name, batch in [('llama8b', 128), ('codellama34b', 64)]:
        key = name + '_calibration'; path = cfg / (key + '.json')
        study.base._put(path, dict(fields(calibration.ROLE, key), native_config=native[name], profile=profiles[name],
            generation_batch_size=batch, max_new_tokens=calibration.LIMITS))
        workers.append(study.storage._pin(path))
        node(key, path, [name + '_native' for name in native], partition='h200', cpus=8, mem='96G', time='2-00:00:00')
    path = cfg / 'report.json'
    study.base._put(path, dict(fields('discovery_arithmetic_paired_report_v1', 'report', large=False), workers=workers,
        report='reports/binding/arithmetic_paired_calibration_findings_20261101_v1.md'))
    node('report', path, [name + '_calibration' for name in native], cpus=4, mem='8G')
    config = dict(evaluation_role=suite.ROLE, run_dir=str(out / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_paired_status_20261101_v1.md', morning_at='2026-11-02T08:00:00-06:00',
        declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan), software_validation=dict(
            review=str(out / 'qa/regression_review.json'), junit=str(out / 'qa/regression.xml'), minimum_tests=minimum_tests))
    suite._CORE._config(config); study.base._put(cfg / 'suite.json', config)
    if (cfg / 'suite.json').stat().st_size > 16 * 1024: raise ValueError('frozen config size exceeded')
    source = freeze(); snapshot = Path(source['snapshot']); manifest = study.base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(snapshot / name, target)
    study.base._put(out / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__': main()
