#!/usr/bin/env python
"""Freeze geometry comparisons; create large output locations on scratch first."""
import hashlib
import json
from pathlib import Path
import shutil
from codecue.binding import arithmetic_numeric_geometry as study, arithmetic_numeric_geometry_suite as suite
from codecue.binding import relationship_capture as base
from codecue.binding.snapshots import freeze


def main():
    out = Path('artifacts/binding/arithmetic_numeric_geometry/20261031_v1')
    cfg = Path('configs/binding/arithmetic_numeric_geometry_20261031_v1')
    scratch = Path('/scratch/juno/jvl210002/codecue/arithmetic_numeric_geometry/20261031_v1')
    plan = Path('reports/binding/arithmetic_numeric_geometry_plan_v1.md')
    if cfg.exists() or out.exists() or scratch.exists(): raise ValueError('preserve existing editions')
    if shutil.disk_usage(scratch.parent.parent).free < 30 * 1024**3: raise ValueError('scratch free space preflight failed')
    cfg.mkdir(parents=True); out.mkdir(parents=True); scratch.mkdir(parents=True)
    archive = out / 'regression_sources'; root = Path(__file__).resolve().parents[1]
    test_files = {}
    for path in sorted((root / 'tests/binding').glob('*.py')):
        relative = path.relative_to(root); target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
        test_files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    minimum_tests = 2486
    base._put(cfg / 'qa.json', dict(evaluation_role='arithmetic_graph_software_validation_v1',
        run_dir=str(out / 'qa'), test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=minimum_tests))
    nodes = []
    def node(key, path, deps, *, qa=False, cpus=16, mem='32G', time='2-00:00:00', partition='normal'):
        folder = out / ('qa' if qa else key)
        nodes.append(dict(key=key, script='scripts/200_binding_numeric_geometry.py', command='prepare' if qa else 'run',
            config=str(path), config_sha256=base._sha(path), dependencies=deps, phase='gpu' if qa else 'cpu',
            partition=partition, cpus=cpus, mem=mem, time=time, time_min=None, expected_cases=0,
            marker=str(folder / ('regression_review.json' if qa else 'completion_manifest_v1.json')),
            marker_status='passed' if qa else 'complete_exploratory'))
    node('software_validation', cfg / 'qa.json', [], qa=True, cpus=8, mem='24G', time='02:00:00', partition='dev,normal')
    def fields(role, key, large=True):
        folder = out / key
        if large:
            target = scratch / key; target.mkdir(); folder.symlink_to(target, target_is_directory=True)
        return dict(evaluation_role=role, run_dir=str(folder), seeds=list(study.original.SEEDS),
            declared_plan=str(plan), declared_plan_sha256=base._sha(plan))
    def pin_audit(name):
        return study.storage._pin(Path('configs/binding/arithmetic_state_followup_20261030_v2') / (name + '_audit.json'))
    workers = []
    for name, backend, width in [('llama8b', 'hidden', 4096), ('codellama34b', 'hidden', 8192),
            ('source4096', 'source', 4096), ('source8192', 'source', 8192)]:
        for role in study.original.ROLES:
            key = name + '_' + role; path = cfg / (key + '.json')
            cached = Path('configs/binding/arithmetic_numeric_exploration_20261031_v1') / (('source' if backend == 'source' else name) + '_cache.json')
            config = dict(fields(study.FIT, key), backend=backend, role=role, widths=[width],
                audit_config=pin_audit('llama8b' if backend == 'source' else name), cache_config=study.storage._pin(cached))
            base._put(path, config); workers.append(study.storage._pin(path))
            node(key, path, ['software_validation'])
    for name in ('llama8b', 'codellama34b'):
        key = name + '_query_cache'; path = cfg / (key + '.json')
        base._put(path, dict(fields(study.QUERY_CACHE, key), audit_config=pin_audit(name)))
        node(key, path, ['software_validation'], cpus=8, mem='8G', time='02:00:00', partition='dev,normal')
    path = cfg / 'report.json'
    base._put(path, dict(fields(study.REPORT, 'report', large=False), workers=workers,
        report='reports/binding/arithmetic_numeric_geometry_findings_v1.md'))
    node('report', path, [n['key'] for n in nodes if n['key'] != 'software_validation'],
        cpus=4, mem='8G', time='02:00:00', partition='dev,normal')
    config = dict(evaluation_role=suite.ROLE, run_dir=str(out / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_numeric_geometry_status_v1.md', morning_at='2026-11-01T08:00:00-06:00',
        declared_plan=str(plan), declared_plan_sha256=base._sha(plan), software_validation=dict(
            review=str(out / 'qa/regression_review.json'), junit=str(out / 'qa/regression.xml'), minimum_tests=minimum_tests))
    suite._CORE._config(config); base._put(cfg / 'suite.json', config)
    if (cfg / 'suite.json').stat().st_size > 16 * 1024: raise ValueError('frozen config identity size limit exceeded')
    source = freeze(); snapshot = Path(source['snapshot']); manifest = base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(snapshot / name, target)
    base._put(out / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__': main()
