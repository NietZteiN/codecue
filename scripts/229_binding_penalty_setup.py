#!/usr/bin/env python
"""Freeze a penalty continuation that references, rather than repeats, old fits."""
import hashlib
import json
import os
from pathlib import Path
import shutil
from codecue.binding import arithmetic_penalty_path as study, arithmetic_penalty_suite as suite
from codecue.binding.snapshots import freeze


def main():
    out = Path('artifacts/binding/arithmetic_penalty_path/20261101_v1')
    cfg = Path('configs/binding/arithmetic_penalty_path_20261101_v1')
    scratch = Path('/scratch/juno/jvl210002/codecue/arithmetic_penalty_path/20261101_v1')
    plan = Path('reports/binding/arithmetic_penalty_path_plan_20261101_v1.md')
    if any(p.exists() for p in (out, cfg, scratch)): raise ValueError('preserve existing penalty-path editions')
    if shutil.disk_usage(scratch.parent.parent).free < 10 * 1024**3: raise ValueError('scratch capacity check failed')
    cfg.mkdir(parents=True); out.mkdir(parents=True); scratch.mkdir(parents=True)
    check = scratch / 'storage_probe.bin'; payload = b'penalty path scratch write/fsync check\n'
    with check.open('xb') as stream: stream.write(payload); stream.flush(); os.fsync(stream.fileno())
    if check.read_bytes() != payload: raise ValueError('scratch roundtrip differs')
    references = dict(report=study.storage._pin('reports/binding/probing_literature_review_20261031_v1.md'),
        register=study.storage._pin('artifacts/binding/literature/probing_methods_20261031_review_v1.json'))
    study.semantic.literature(dict(literature=references))
    archive = out / 'regression_sources'; root = Path(__file__).resolve().parents[1]; test_files = {}
    for path in sorted((root / 'tests/binding').glob('*.py')):
        relative = path.relative_to(root); target = archive / relative
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
        test_files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    minimum_tests = 2697
    study.base._put(cfg / 'qa.json', dict(evaluation_role='arithmetic_graph_software_validation_v1',
        run_dir=str(out / 'qa'), test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=minimum_tests))
    if (cfg / 'qa.json').stat().st_size > 16 * 1024: raise ValueError('QA config size exceeded')
    nodes = []
    def node(key, path, deps, *, qa=False, cpus=16, mem='32G'):
        nodes.append(dict(key=key, script='scripts/227_binding_penalty_path.py', command='prepare' if qa else 'run',
            config=str(path), config_sha256=study.base._sha(path), dependencies=deps, phase='gpu' if qa else 'cpu',
            partition='dev,normal', cpus=cpus, mem=mem, time='02:00:00', time_min=None, expected_cases=0,
            marker=str(out / ('qa/regression_review.json' if qa else key + '/completion_manifest_v1.json')),
            marker_status='passed' if qa else 'complete_exploratory'))
    node('software_validation', cfg / 'qa.json', [], qa=True, cpus=8, mem='24G')
    def fields(role, key, large=True):
        if large:
            target = scratch / key; target.mkdir(); (out / key).symlink_to(target, target_is_directory=True)
        return dict(evaluation_role=role, run_dir=str(out / key), seeds=[11, 29, 47], literature=references,
            declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan))
    old_dir = Path('configs/binding/arithmetic_conditional_20261101_v1')
    old_audit = study.storage._pin('artifacts/binding/arithmetic_conditional/20261101_v1/postrun_audit/results.json')
    path = cfg / 'priors.json'
    study.base._put(path, dict(fields(study.PRIORS, 'priors'), reference_worker=study.storage._pin(old_dir / 'source_source1024.json'), reference_audit=old_audit))
    prior = study.storage._pin(path); node('priors', path, ['software_validation'], cpus=8, mem='16G')
    workers = []
    conditions = [('source', 'source1024'), ('source', 'source2048')] + [
        (alias, condition) for alias in ('llama8b', 'codellama34b') for condition in ('hidden', 'joint', 'shuffled_joint')]
    for alias, condition in conditions:
        key = alias + '_' + condition; path = cfg / (key + '.json')
        study.base._put(path, dict(fields(study.FIT, key), reference_worker=study.storage._pin(old_dir / (key + '.json')),
            reference_audit=old_audit, prior_config=prior, alphas=list(study.ALPHAS)))
        workers.append(study.storage._pin(path)); node(key, path, ['priors'])
    path = cfg / 'audit.json'
    study.base._put(path, dict(fields(study.AUDIT, 'audit', large=False), workers=workers))
    audit = study.storage._pin(path); node('audit', path, [n['key'] for n in nodes if n['key'] not in ('software_validation', 'priors')])
    path = cfg / 'report.json'
    study.base._put(path, dict(fields(study.REPORT, 'report', large=False), workers=workers, audit_config=audit,
        report='reports/binding/arithmetic_penalty_path_findings_20261101_v1.md'))
    node('report', path, ['audit'], cpus=8, mem='16G')
    config = dict(evaluation_role=suite.ROLE, run_dir=str(out / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_penalty_path_status_20261101_v1.md', morning_at='2026-11-02T08:00:00-06:00',
        declared_plan=str(plan), declared_plan_sha256=study.base._sha(plan), software_validation=dict(
            review=str(out / 'qa/regression_review.json'), junit=str(out / 'qa/regression.xml'), minimum_tests=minimum_tests))
    suite._CORE._config(config); study.base._put(cfg / 'suite.json', config)
    source = freeze(); snapshot = Path(source['snapshot']); manifest = study.base._json(snapshot / 'frozen_manifest.json')
    for name in [*manifest['code']['source_files'], *manifest['config_files']]:
        target = archive / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(snapshot / name, target)
    study.base._put(out / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__': main()
