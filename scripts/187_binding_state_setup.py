#!/usr/bin/env python
"""Prepare/freeze the CPU-only state follow-up from completed local captures."""
from pathlib import Path
import hashlib
import json
import shutil
import argparse

from codecue.binding import arithmetic_state_audit as audit
from codecue.binding import arithmetic_binding_readouts as binding
from codecue.binding import arithmetic_numeric_readouts as numeric
from codecue.binding import arithmetic_capacity_followup as capacity
from codecue.binding import arithmetic_state_compose as compose
from codecue.binding import arithmetic_state_report as report
from codecue.binding import arithmetic_state_suite as suite
from codecue.binding import relationship_capture as base
from codecue.binding.snapshots import freeze

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('artifacts/binding/arithmetic_state_followup/20261030_v1')
CFG = Path('configs/binding/arithmetic_state_followup_20261030_v1')
PLAN = Path('reports/binding/arithmetic_state_followup_plan_v1.md')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    global OUT, CFG, PLAN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition', type=int, default=1)
    edition = parser.parse_args().edition
    if not 1 <= edition <= 99:
        raise ValueError('explicit bounded run edition required')
    OUT = Path(f'artifacts/binding/arithmetic_state_followup/20261030_v{edition}')
    CFG = Path(f'configs/binding/arithmetic_state_followup_20261030_v{edition}')
    PLAN = Path(f'reports/binding/arithmetic_state_followup_plan_v{edition}.md')
    CFG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    archive = OUT / 'regression_sources'
    test_files = {}
    for path in sorted((ROOT / 'tests/binding').glob('*.py')):
        relative = path.relative_to(ROOT)
        target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise ValueError('regression source cannot follow a symbolic link')
        if not target.exists():
            shutil.copyfile(path, target)
        if sha(target) != sha(path):
            raise ValueError('existing regression source differs')
        test_files[str(relative)] = sha(path)
    qa = dict(evaluation_role='arithmetic_graph_software_validation_v1', run_dir=str(OUT / 'qa'),
        test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=2428)
    base._put(CFG / 'qa.json', qa)
    nodes = []
    def node(key, command, config, dependencies, marker, status, *, partition='normal', cpus=16, mem='32G', time='2-00:00:00', phase='cpu'):
        nodes.append(dict(key=key, script='scripts/185_binding_state_followup.py', command=command,
            config=str(config), config_sha256=sha(config), dependencies=dependencies,
            marker=str(marker), marker_status=status, phase=phase, partition=partition,
            cpus=cpus, mem=mem, time=time, time_min=None, expected_cases=0))
    node('software_validation', 'prepare', CFG / 'qa.json', [], OUT / 'qa/regression_review.json', 'passed',
        partition='dev,normal', mem='24G', cpus=8, time='02:00:00', phase='gpu')
    def fields(role, directory):
        return dict(evaluation_role=role, run_dir=str(directory), seeds=[11, 29, 47],
            declared_plan=str(PLAN), declared_plan_sha256=sha(PLAN))
    audit_items, compose_items, capacity_items = [], [], []
    for name in ('llama8b', 'codellama34b'):
        old = Path('configs/binding/arithmetic_local_20261030_v1')
        config = fields(audit.ROLE, OUT / name / 'audit')
        for kind in ('capture', 'probes', 'behavior'):
            key = 'probe' if kind == 'probes' else kind
            path = old / (name + '_' + kind + '.json')
            config[key + '_config'] = str(path)
            config[key + '_config_sha256'] = sha(path)
            completed = Path(base._json(path)['run_dir']) / 'completion_manifest_v1.json'
            if not completed.exists():
                raise ValueError('original local suite must complete before state follow-up')
        audit_file = CFG / (name + '_audit.json')
        base._put(audit_file, config)
        node(name + '_audit', 'run', audit_file, ['software_validation'], OUT / name / 'audit/completion_manifest_v1.json',
            'complete_exploratory', partition='dev,normal', time='02:00:00')
        audit_items.append(dict(name=name, config=str(audit_file), sha256=sha(audit_file)))
        for kind, role in [('binding', binding.ROLE), ('numeric', numeric.ROLE), ('capacity', capacity.ROLE)]:
            path = CFG / (name + '_' + kind + '.json')
            config = dict(fields(role, OUT / name / kind), audit_config=dict(path=str(audit_file), sha256=sha(audit_file)))
            base._put(path, config)
            node(name + '_' + kind, 'run', path, [name + '_audit'], OUT / name / kind / 'completion_manifest_v1.json', 'complete_exploratory')
            if kind == 'capacity':
                capacity_items.append(dict(name=name, config=str(path), sha256=sha(path)))
        binding_file, numeric_file = CFG / (name + '_binding.json'), CFG / (name + '_numeric.json')
        path = CFG / (name + '_compose.json')
        config = dict(fields(compose.ROLE, OUT / name / 'compose'), audit_config=dict(path=str(audit_file), sha256=sha(audit_file)),
            binding_config=str(binding_file), binding_config_sha256=sha(binding_file),
            numeric_config=str(numeric_file), numeric_config_sha256=sha(numeric_file))
        base._put(path, config)
        node(name + '_compose', 'run', path, [name + '_binding', name + '_numeric'],
            OUT / name / 'compose/completion_manifest_v1.json', 'complete_exploratory',
            partition='dev,normal', mem='16G', cpus=4, time='00:30:00')
        compose_items.append(dict(name=name, config=str(path), sha256=sha(path)))
    path = CFG / 'audit_report.json'
    config = dict(fields(report.AUDIT_ROLE, OUT / 'audit_report'), models=audit_items,
        report='reports/binding/arithmetic_local_dependency_findings_v1.md', figure='reports/binding/figures/arithmetic_local_dependency_v1')
    base._put(path, config)
    node('audit_report', 'run', path, ['llama8b_audit', 'codellama34b_audit'], OUT / 'audit_report/completion_manifest_v1.json',
        'complete_exploratory', partition='dev,normal', mem='8G', cpus=4, time='00:30:00')
    path = CFG / 'state_report.json'
    config = dict(fields(report.STATE_ROLE, OUT / 'state_report'), models=compose_items, capacity_models=capacity_items,
        report='reports/binding/arithmetic_current_state_findings_v1.md')
    base._put(path, config)
    node('state_report', 'run', path, ['llama8b_compose', 'codellama34b_compose', 'llama8b_capacity', 'codellama34b_capacity'],
        OUT / 'state_report/completion_manifest_v1.json', 'complete_exploratory', partition='dev,normal', mem='8G', cpus=4, time='00:30:00')
    config = dict(evaluation_role=suite.ROLE, run_dir=str(OUT / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_state_followup_status_v1.md', morning_at='2026-10-31T08:00:00-05:00',
        declared_plan=str(PLAN), declared_plan_sha256=sha(PLAN), software_validation=dict(
            review=str(OUT / 'qa/regression_review.json'), junit=str(OUT / 'qa/regression.xml'), minimum_tests=2428))
    suite._CORE._config(config)
    base._put(CFG / 'suite.json', config)
    source = freeze()
    snapshot = Path(source['snapshot'])
    manifest = base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(snapshot / name, target)
        if sha(target) != sha(snapshot / name):
            raise ValueError('frozen regression mirror differs')
    base._put(OUT / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__':
    main()
