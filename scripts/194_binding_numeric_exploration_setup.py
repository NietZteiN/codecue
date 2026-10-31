#!/usr/bin/env python
"""Freeze the first compression/encoding wave and full regression sources."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from codecue.binding import arithmetic_numeric_exploration as study
from codecue.binding import arithmetic_numeric_exploration_suite as suite
from codecue.binding import relationship_capture as base
from codecue.binding.snapshots import freeze


def source_sha(path):
    # Test source filenames may mention final outcomes; these are code files,
    # not outcome artifacts, and are intentionally included in regression.
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition', type=int, default=1)
    edition = parser.parse_args().edition
    if not 1 <= edition <= 99:
        raise ValueError('bounded explicit edition required')
    out = Path(f'artifacts/binding/arithmetic_numeric_exploration/20261031_v{edition}')
    cfg = Path(f'configs/binding/arithmetic_numeric_exploration_20261031_v{edition}')
    plan = Path(f'reports/binding/arithmetic_numeric_exploration_plan_v{edition}.md')
    if ((cfg.exists() and any(cfg.iterdir())) or
            (out.exists() and any(p.name != 'regression_sources' for p in out.iterdir()))):
        raise ValueError('existing experiment editions must be preserved')
    cfg.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    archive = out / 'regression_sources'
    test_files = {}
    root = Path(__file__).resolve().parents[1]
    for path in sorted((root / 'tests/binding').glob('*.py')):
        relative = path.relative_to(root); target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and source_sha(target) != source_sha(path):
            raise ValueError('partial regression archive source differs')
        if not target.exists(): shutil.copyfile(path, target)
        test_files[str(relative)] = source_sha(path)
    qa = dict(evaluation_role='arithmetic_graph_software_validation_v1', run_dir=str(out / 'qa'),
        test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=2446)
    base._put(cfg / 'qa.json', qa)
    nodes = []
    def node(key, file, deps, marker, *, phase='cpu', cpus=16, mem='64G', time='2-00:00:00', partition='normal'):
        nodes.append(dict(key=key, script='scripts/192_binding_numeric_exploration.py',
            command='prepare' if phase == 'gpu' else 'run', config=str(file), config_sha256=base._sha(file),
            dependencies=deps, phase=phase, partition=partition, cpus=cpus, mem=mem, time=time,
            time_min=None, expected_cases=0, marker=str(marker), marker_status='passed' if phase == 'gpu' else 'complete_exploratory'))
    node('software_validation', cfg / 'qa.json', [], out / 'qa/regression_review.json',
        phase='gpu', cpus=8, mem='24G', time='02:00:00', partition='dev,normal')
    def fields(role, directory):
        return dict(evaluation_role=role, run_dir=str(directory), seeds=list(study.SEEDS),
            declared_plan=str(plan), declared_plan_sha256=base._sha(plan))
    def audit_config(name):
        path = Path('configs/binding/arithmetic_state_followup_20261030_v2') / (name + '_audit.json')
        return dict(path=str(path), sha256=base._sha(path))
    caches = {}
    for name, backend in [('llama8b', 'hidden'), ('codellama34b', 'hidden'), ('source', 'source')]:
        key = name + '_cache'; path = cfg / (key + '.json'); folder = out / key
        config = dict(fields(study.PREPARE, folder), backend=backend, audit_config=audit_config('llama8b' if name == 'source' else name))
        base._put(path, config); caches[name] = dict(path=str(path), sha256=base._sha(path))
        node(key, path, ['software_validation'], folder / 'completion_manifest_v1.json', partition='dev,normal', time='02:00:00')
    workers = []
    for name, backend, widths in [('llama8b', 'hidden', [64, 256, 1024, 4096]),
            ('codellama34b', 'hidden', [64, 256, 1024, 8192]), ('source', 'source', [64, 256, 1024, 4096, 8192])]:
        for role in study.ROLES:
            key = name + '_' + role; folder = out / key; path = cfg / (key + '.json')
            config = dict(fields(study.FIT, folder), backend=backend, role=role, widths=widths,
                audit_config=audit_config('llama8b' if name == 'source' else name), cache_config=caches[name])
            base._put(path, config); workers.append(dict(path=str(path), sha256=base._sha(path)))
            node(key, path, [name + '_cache'], folder / 'completion_manifest_v1.json')
    path = cfg / 'report.json'; folder = out / 'report'
    config = dict(fields(study.REPORT, folder), workers=workers, report='reports/binding/arithmetic_numeric_exploration_findings_v1.md')
    base._put(path, config)
    node('report', path, [n['key'] for n in nodes if n['key'].endswith(study.ROLES)],
        folder / 'completion_manifest_v1.json', cpus=4, mem='8G', time='02:00:00', partition='dev,normal')
    config = dict(evaluation_role=suite.ROLE, run_dir=str(out / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_numeric_exploration_status_v1.md', morning_at='2026-11-01T08:00:00-06:00',
        declared_plan=str(plan), declared_plan_sha256=base._sha(plan), software_validation=dict(
            review=str(out / 'qa/regression_review.json'), junit=str(out / 'qa/regression.xml'), minimum_tests=2446))
    suite._CORE._config(config); base._put(cfg / 'suite.json', config)
    source = freeze(); snapshot = Path(source['snapshot']); manifest = base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(snapshot / name, target)
    base._put(out / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__':
    main()
