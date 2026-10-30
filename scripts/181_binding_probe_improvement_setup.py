#!/usr/bin/env python
"""Build, validate and freeze probe-improvement sources/configs without model loads."""
from pathlib import Path
import hashlib
import json
import shutil

from codecue.binding import arithmetic_local_programs as programs
from codecue.binding import arithmetic_local_capture as capture
from codecue.binding import arithmetic_local_behavior as behavior
from codecue.binding import arithmetic_local_probes as probes
from codecue.binding import arithmetic_local_suite as suite
from codecue.binding import arithmetic_probe_reuse as reuse
from codecue.binding import relationship_capture as base
from codecue.binding.snapshots import freeze

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('artifacts/binding/arithmetic_local/20261030_v1')
CFG = Path('configs/binding/arithmetic_local_20261030_v1')
AOUT = Path('artifacts/binding/arithmetic_probe_selection/20261030_v2')
ACFG = Path('configs/binding/arithmetic_probe_selection_20261030_v2')
PLAN = Path('reports/binding/arithmetic_local_probe_plan_v1.md')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    base._put(path, value)


def main():
    for folder in (CFG, ACFG, OUT, AOUT):
        folder.mkdir(parents=True, exist_ok=True)
    programs.build(OUT / 'sources.jsonl')
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
        if target.read_bytes() != path.read_bytes():
            raise ValueError('existing regression source differs')
        test_files[str(relative)] = sha(path)
    qa = dict(evaluation_role='arithmetic_graph_software_validation_v1', run_dir=str(OUT / 'qa'),
        test_archive=str(archive / 'tests/binding'), test_files=test_files, minimum_tests=2400)
    write(CFG / 'qa.json', qa)

    nodes = []
    def node(key, script, command, config, dependencies, marker, status, phase, partition, mem, cpus, time, minimum, cases):
        nodes.append(dict(key=key, script=script, command=command, config=str(config), config_sha256=sha(config),
            dependencies=dependencies, marker=str(marker), marker_status=status, phase=phase,
            partition=partition, mem=mem, cpus=cpus, time=time, time_min=minimum, expected_cases=cases))

    node('software_validation', 'scripts/167_binding_arithmetic_graph_capture.py', 'prepare', CFG / 'qa.json', [],
        OUT / 'qa/regression_review.json', 'passed', 'gpu', 'dev,normal', '24G', 8, '02:00:00', None, 0)
    for name in ('llama8b', 'codellama34b'):
        old_config = Path(f'configs/binding/arithmetic_probe_selection_20261030_v1/{name}.json')
        old = base._json(old_config)
        old_dir = Path(old['run_dir'])
        entries = [dict(path=str(p), sha256=sha(p)) for p in sorted(old_dir.glob('cv_*.json'))]
        if len(entries) != 45:
            raise ValueError('all original CV banks must finish before recovery setup')
        old_source = base._json(entries[0]['path'])['source']
        recipe = reuse.recipe(Path(old_source['snapshot']) / 'src/codecue/binding/arithmetic_probe_selection.py')
        if recipe != reuse.recipe(ROOT / 'src/codecue/binding/arithmetic_probe_selection.py'):
            raise ValueError('selection recipe changed; refusing CV reuse')
        reuse_manifest = AOUT / (name + '_cv_reuse_review_v1.json')
        write(reuse_manifest, dict(status='verified_cache_inventory', original_config=str(old_config),
            original_config_sha256=sha(old_config), original_source=old_source, recipe_sha256=recipe,
            entries=entries, original_selection=dict(path=str(old_dir / 'selection_review_v1.json'),
                sha256=sha(old_dir / 'selection_review_v1.json')), reason='Publication-only reserved filename repair; all CV fits preserved'))
        write(ACFG / (name + '.json'), dict(old, run_dir=str(AOUT / name),
            cv_reuse=dict(manifest=str(reuse_manifest), sha256=sha(reuse_manifest))))

        profile = Path(f'configs/binding/arithmetic_graph_20261029_v3/{name}_capture.json')
        cap = dict(evaluation_role=capture.ROLE, dataset=str(OUT / 'sources.jsonl'),
            dataset_sha256=sha(OUT / 'sources.jsonl'), dataset_manifest_sha256=sha(OUT / 'sources.manifest.json'),
            profile_config=str(profile), profile_config_sha256=sha(profile), batch_size=16, chunk_size=32,
            instruction=0, declared_plan=str(PLAN), declared_plan_sha256=sha(PLAN), run_dir=str(OUT / name / 'capture'))
        capfile = CFG / (name + '_capture.json')
        write(capfile, cap)
        node(name + '_prepare', 'scripts/177_binding_arithmetic_local_capture.py', 'prepare', capfile, [],
            OUT / name / 'capture/preflight.json', 'passed', 'gpu', 'dev,normal', '24G', 4, '02:00:00', None, 5292)
        short = name == 'llama8b'
        partition = 'dev-a30,a30,h100,h200' if short else 'h100,h200'
        time, minimum = ('02:00:00', '00:15:00') if short else ('2-00:00:00', '00:30:00')
        node(name + '_capture', 'scripts/177_binding_arithmetic_local_capture.py', 'run', capfile,
            ['software_validation', name + '_prepare'], OUT / name / 'capture/completion_manifest_v1.json',
            'complete_exploratory', 'gpu', partition, '64G', 8, time, minimum, 5292)
        behfile = CFG / (name + '_behavior.json')
        write(behfile, dict(evaluation_role=behavior.ROLE, capture_config=str(capfile), capture_config_sha256=sha(capfile),
            generation_batch_size=32, max_new_tokens=12, run_dir=str(OUT / name / 'behavior')))
        node(name + '_behavior', 'scripts/179_binding_arithmetic_local_behavior.py', 'run', behfile,
            [name + '_capture'], OUT / name / 'behavior/completion_manifest_v1.json',
            'complete_exploratory', 'gpu', partition, '64G', 8, time, minimum, 5508)
        probefile = CFG / (name + '_probes.json')
        write(probefile, dict(evaluation_role=probes.ROLE, capture_config=str(capfile), capture_config_sha256=sha(capfile),
            epochs=25, seeds=list(probes.SEEDS), projection_rank=64, layer=24 if short else 36,
            run_dir=str(OUT / name / 'probes')))
        node(name + '_probes', 'scripts/178_binding_arithmetic_local_probes.py', 'run', probefile,
            [name + '_capture'], OUT / name / 'probes/completion_manifest_v1.json',
            'complete_exploratory', 'cpu', 'normal', '64G', 16, '2-00:00:00', None, 0)
    # The durable engine requires the deferred CPU phase after all early nodes.
    nodes = [n for n in nodes if n['phase'] == 'gpu'] + [n for n in nodes if n['phase'] == 'cpu']
    config = dict(evaluation_role=suite.ROLE, run_dir=str(OUT / 'suite'), nodes=nodes,
        report='reports/binding/arithmetic_local_probe_status_v1.md', morning_at='2026-10-31T08:00:00-05:00',
        declared_plan=str(PLAN), declared_plan_sha256=sha(PLAN),
        software_validation=dict(review=str(OUT / 'qa/regression_review.json'), junit=str(OUT / 'qa/regression.xml'), minimum_tests=2400))
    suite._CORE._config(config)
    write(CFG / 'suite.json', config)
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
    write(OUT / 'source_review_v1.json', source)
    write(AOUT / 'source_review_v1.json', source)
    print(json.dumps(source))


if __name__ == '__main__':
    main()
