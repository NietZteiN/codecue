#!/usr/bin/env python
"""Freeze the seven-cell cached global-state suite, with scratch-first storage."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from codecue.binding import arithmetic_global_state as study, arithmetic_global_state_suite as suite
from codecue.binding import arithmetic_semantic_audit
from codecue.binding.snapshots import freeze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition', type=int, default=1)
    edition = parser.parse_args().edition
    if edition != 1: raise ValueError('this implementation freezes explicit edition one only')
    out = Path('artifacts/binding/arithmetic_global_state/20261031_v1')
    cfg = Path('configs/binding/arithmetic_global_state_20261031_v1')
    scratch = Path('/scratch/juno/jvl210002/codecue/arithmetic_global_state/20261031_v1')
    plan = Path('reports/binding/arithmetic_global_state_plan_v1.md')
    references = dict(report=study.storage._pin('reports/binding/probing_literature_review_20261031_v1.md'),
        register=study.storage._pin('artifacts/binding/literature/probing_methods_20261031_review_v1.json'))
    study.semantic.literature(dict(literature=references))
    if cfg.exists() or out.exists() or scratch.exists(): raise ValueError('preserve existing experiment editions')
    if shutil.disk_usage(scratch.parent.parent).free < 30 * 1024**3: raise ValueError('scratch capacity preflight failed')
    cfg.mkdir(parents=True); out.mkdir(parents=True); scratch.mkdir(parents=True)
    archive = out / 'regression_sources'; root = Path(__file__).resolve().parents[1]
    test_files = {}
    for path in sorted((root / 'tests/binding').glob('*.py')):
        relative = path.relative_to(root); target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
        test_files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    minimum_tests = 2533
    study.base._put(cfg / 'qa.json', dict(evaluation_role='arithmetic_graph_software_validation_v1',
        run_dir=str(out / 'qa'), test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=minimum_tests))
    if (cfg / 'qa.json').stat().st_size > 16 * 1024: raise ValueError('QA config exceeds frozen verification limit')
    nodes = []
    def node(key, path, deps, *, qa=False, cpus=16, mem='32G', time='2-00:00:00', partition='normal'):
        nodes.append(dict(key=key, script='scripts/206_binding_global_state.py', command='prepare' if qa else 'run',
            config=str(path), config_sha256=study.base._sha(path), dependencies=deps, phase='gpu' if qa else 'cpu',
            partition=partition, cpus=cpus, mem=mem, time=time, time_min=None, expected_cases=0,
            marker=str(out / ('qa/regression_review.json' if qa else key + '/completion_manifest_v1.json')),
            marker_status='passed' if qa else 'complete_exploratory'))
    node('software_validation', cfg / 'qa.json', [], qa=True, cpus=8, mem='24G', time='02:00:00', partition='dev,normal')
    def fields(role, key, large=False):
        folder = out / key
        if large:
            target = scratch / key; target.mkdir(); folder.symlink_to(target, target_is_directory=True)
        return dict(evaluation_role=role, run_dir=str(folder), seeds=list(study.numeric.SEEDS), literature=references,
            declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan))
    def audit(name):
        return study.storage._pin(Path('configs/binding/arithmetic_state_followup_20261030_v2') / (name + '_audit.json'))
    path = cfg / 'semantic_audit.json'
    study.base._put(path, dict(fields(arithmetic_semantic_audit.ROLE, 'semantic_audit'),
        semantic_report=study.storage._pin('configs/binding/arithmetic_semantic_controls_20261031_v2/report.json'),
        report='reports/binding/arithmetic_semantic_postrun_review_v1.md'))
    node('semantic_audit', path, ['software_validation'], cpus=8, mem='32G', time='02:00:00', partition='dev,normal')
    path = cfg / 'cache.json'
    study.base._put(path, dict(fields(study.PREPARE, 'cache', large=True), audit_config=audit('llama8b'),
        labels=study.storage._pin('configs/binding/arithmetic_semantic_controls_20261031_v2/labels.json'),
        query_caches={name: study.storage._pin(f'configs/binding/arithmetic_numeric_geometry_20261031_v1/{name}_query_cache.json')
            for name in ('llama8b', 'codellama34b')}, layers=dict(llama8b=24, codellama34b=36)))
    cache = study.storage._pin(path)
    node('cache', path, ['semantic_audit'], cpus=16, mem='16G', time='02:00:00', partition='dev,normal')
    workers = []
    for name, backend, full, width in [('llama8b', 'hidden', 4096, 1024), ('llama8b', 'hidden', 4096, 4096),
            ('codellama34b', 'hidden', 8192, 1024), ('codellama34b', 'hidden', 8192, 8192),
            ('source', 'source', 8192, 1024), ('source', 'source', 8192, 4096), ('source', 'source', 8192, 8192)]:
        key = name + '_width' + str(width); path = cfg / (key + '.json')
        study.base._put(path, dict(fields(study.FIT, key, large=True), backend=backend, alias=name, width=width,
            full_width=full, audit_config=audit('llama8b' if backend == 'source' else name), cache_config=cache))
        workers.append(study.storage._pin(path)); node(key, path, ['cache'])
    path = cfg / 'report.json'
    study.base._put(path, dict(fields(study.REPORT, 'report'), workers=workers,
        report='reports/binding/arithmetic_global_state_findings_v1.md'))
    node('report', path, [n['key'] for n in nodes if '_width' in n['key']], cpus=4, mem='8G', time='02:00:00', partition='dev,normal')
    config = dict(evaluation_role=suite.ROLE, run_dir=str(out / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_global_state_status_v1.md', morning_at='2026-11-01T08:00:00-06:00',
        declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan), software_validation=dict(
            review=str(out / 'qa/regression_review.json'), junit=str(out / 'qa/regression.xml'), minimum_tests=minimum_tests))
    suite._CORE._config(config); study.base._put(cfg / 'suite.json', config)
    if (cfg / 'suite.json').stat().st_size > 16 * 1024: raise ValueError('frozen suite config size limit exceeded')
    source = freeze(); snapshot = Path(source['snapshot']); manifest = study.base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(snapshot / name, target)
    study.base._put(out / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__': main()
