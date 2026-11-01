#!/usr/bin/env python
"""Freeze cached-state semantic controls with pinned literature and scratch outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from codecue.binding import arithmetic_semantic_controls as study, arithmetic_semantic_controls_suite as suite
from codecue.binding import relationship_capture as base
from codecue.binding.snapshots import freeze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition', type=int, default=1)
    edition = parser.parse_args().edition
    if not 1 <= edition <= 99: raise ValueError('bounded explicit edition required')
    out = Path(f'artifacts/binding/arithmetic_semantic_controls/20261031_v{edition}')
    cfg = Path(f'configs/binding/arithmetic_semantic_controls_20261031_v{edition}')
    scratch = Path(f'/scratch/juno/jvl210002/codecue/arithmetic_semantic_controls/20261031_v{edition}')
    plan = Path(f'reports/binding/arithmetic_semantic_controls_plan_v{edition}.md')
    references = dict(report=study.storage._pin('reports/binding/probing_literature_review_20261031_v1.md'),
        register=study.storage._pin('artifacts/binding/literature/probing_methods_20261031_review_v1.json'))
    study.literature(dict(literature=references))
    if cfg.exists() or out.exists() or scratch.exists(): raise ValueError('preserve existing experiment editions')
    if shutil.disk_usage(scratch.parent.parent).free < 10 * 1024**3: raise ValueError('scratch capacity preflight failed')
    cfg.mkdir(parents=True); out.mkdir(parents=True); scratch.mkdir(parents=True)
    archive = out / 'regression_sources'; root = Path(__file__).resolve().parents[1]
    test_files = {}
    for path in sorted((root / 'tests/binding').glob('*.py')):
        relative = path.relative_to(root); target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
        test_files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    minimum_tests = 2507
    base._put(cfg / 'qa.json', dict(evaluation_role='arithmetic_graph_software_validation_v1',
        run_dir=str(out / 'qa'), test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=minimum_tests))
    nodes = []
    def node(key, path, deps, *, qa=False, cpus=16, mem='32G', time='2-00:00:00', partition='normal'):
        nodes.append(dict(key=key, script='scripts/203_binding_semantic_controls.py', command='prepare' if qa else 'run',
            config=str(path), config_sha256=base._sha(path), dependencies=deps, phase='gpu' if qa else 'cpu',
            partition=partition, cpus=cpus, mem=mem, time=time, time_min=None, expected_cases=0,
            marker=str(out / ('qa/regression_review.json' if qa else key + '/completion_manifest_v1.json')),
            marker_status='passed' if qa else 'complete_exploratory'))
    node('software_validation', cfg / 'qa.json', [], qa=True, cpus=8, mem='24G', time='02:00:00', partition='dev,normal')
    def fields(role, key, large=False):
        folder = out / key
        if large:
            target = scratch / key; target.mkdir(); folder.symlink_to(target, target_is_directory=True)
        return dict(evaluation_role=role, run_dir=str(folder), seeds=list(study.numeric.SEEDS), literature=references,
            declared_plan=str(plan), declared_plan_sha256=base._sha(plan))
    def audit(name):
        return study.storage._pin(Path('configs/binding/arithmetic_state_followup_20261030_v2') / (name + '_audit.json'))
    views = {}
    for name in ('llama8b', 'codellama34b', 'source'):
        path = cfg / (name + '_cache_view.json')
        old = Path('configs/binding/arithmetic_numeric_exploration_20261031_v1') / (name + '_cache.json')
        base._put(path, dict(fields(study.CACHE, name + '_cache_view'), original_cache=study.storage._pin(old)))
        views[name] = study.storage._pin(path)
    path = cfg / 'labels.json'
    base._put(path, dict(fields(study.PREPARE, 'labels', large=True), audit_config=audit('llama8b'), cache_views=list(views.values())))
    prepared = study.storage._pin(path)
    node('labels', path, ['software_validation'], cpus=8, mem='8G', time='02:00:00', partition='dev,normal')
    comparisons = []
    for name, backend, width in [('llama8b', 'hidden', 4096), ('codellama34b', 'hidden', 8192),
            ('source4096', 'source', 4096), ('source8192', 'source', 8192)]:
        key = name + '_computed_definition'; path = cfg / (key + '.json')
        cache_name = 'source' if backend == 'source' else name
        base._put(path, dict(fields(study.FIT, key, large=True), backend=backend, role='computed_definition',
            widths=[width], semantic='operator_swap', audit_config=audit('llama8b' if backend == 'source' else name),
            cache_config=views[cache_name]))
        ordinary = Path('configs/binding/arithmetic_numeric_exploration_20261031_v1') / (cache_name + '_computed_definition.json')
        comparisons.append(dict(name=name, backend=backend, width=width, ordinary=study.storage._pin(ordinary), alternate=study.storage._pin(path)))
        node(key, path, ['labels'])
    path = cfg / 'report.json'
    base._put(path, dict(fields(study.REPORT, 'report'), audit_config=audit('llama8b'), prepared=prepared,
        comparisons=comparisons, report=f'reports/binding/arithmetic_semantic_controls_findings_v{edition}.md'))
    node('report', path, [n['key'] for n in nodes if n['key'].endswith('_computed_definition')],
        cpus=4, mem='8G', time='02:00:00', partition='dev,normal')
    config = dict(evaluation_role=suite.ROLE, run_dir=str(out / 'suite'), nodes=nodes,
        report=f'reports/binding/arithmetic_semantic_controls_status_v{edition}.md', morning_at='2026-11-01T08:00:00-06:00',
        declared_plan=str(plan), declared_plan_sha256=base._sha(plan), software_validation=dict(
            review=str(out / 'qa/regression_review.json'), junit=str(out / 'qa/regression.xml'), minimum_tests=minimum_tests))
    suite._CORE._config(config); base._put(cfg / 'suite.json', config)
    if (cfg / 'suite.json').stat().st_size > 16 * 1024: raise ValueError('frozen config size limit exceeded')
    source = freeze(); snapshot = Path(source['snapshot']); manifest = base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(snapshot / name, target)
    base._put(out / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__': main()
