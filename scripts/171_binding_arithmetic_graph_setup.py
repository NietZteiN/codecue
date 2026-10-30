#!/usr/bin/env python
"""Prepare and freeze the declared October29 arithmetic discovery suite.

This command is source-only. Submit the resulting suite with script170 after
reviewing its manifest; running it again never replaces differing publications.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

from codecue.binding import arithmetic_graph_programs as programs
from codecue.binding import arithmetic_graph_capture as capture
from codecue.binding import arithmetic_graph_readouts as readouts
from codecue.binding import arithmetic_graph_behavior as behavior
from codecue.binding import arithmetic_graph_suite as suite
from codecue.binding import relationship_capture as base
from codecue.binding.snapshots import freeze

ROOT = Path(__file__).resolve().parents[1]
PYTHON = '/work/jvl210002/migration/envs/probe-cu129/bin/python'


def write(path, value):
    base._publish(path, (json.dumps(value, sort_keys=True, indent=2)+'\n').encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition', type=int, default=3)
    edition = parser.parse_args().edition
    if not 1 <= edition <= 99:
        raise ValueError('bounded explicit run edition required')
    OUT = Path(f'artifacts/binding/arithmetic_graph/20261029_v{edition}')
    CFG = Path(f'configs/binding/arithmetic_graph_20261029_v{edition}')
    PLAN = f'reports/binding/arithmetic_graph_overnight_20261029_plan_v{edition}.md'
    CFG.mkdir(parents=True, exist_ok=True)
    manifest = programs.build(OUT/'sources.jsonl')
    archive = OUT/'regression_sources'
    test_files = {}
    for path in sorted((ROOT/'tests/binding').glob('*.py')):
        relative = path.relative_to(ROOT)
        target = archive/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        # These are Python source files, not discovery outcomes. The outcome
        # publisher correctly rejects /tests/ paths, so archive source directly.
        if target.is_symlink():
            raise ValueError('regression archive cannot follow symbolic links')
        if not target.exists():
            shutil.copyfile(path, target)
        if target.read_bytes() != path.read_bytes():
            raise ValueError('existing regression archive differs')
        test_files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    qa = dict(evaluation_role='arithmetic_graph_software_validation_v1', run_dir=str(OUT/'suite'),
              test_archive=str(archive/'tests/binding'), test_files=test_files, minimum_tests=2000)
    write(CFG/'qa.json', qa)
    nodes = []
    def node(key, script, command, config, dependencies, marker, status, phase, partition,
             mem, cpus, time, time_min, cases):
        nodes.append(dict(key=key, script=script, command=command, config=str(config),
            config_sha256=base._sha(config), dependencies=dependencies, marker=str(marker),
            marker_status=status, phase=phase, partition=partition, mem=mem, cpus=cpus,
            time=time, time_min=time_min, expected_cases=cases))
    node('software_validation', 'scripts/167_binding_arithmetic_graph_capture.py', 'prepare', CFG/'qa.json', [],
         OUT/'suite/regression_review.json', 'passed', 'gpu', 'dev,normal', '24G', 8, '02:00:00', None, 0)
    caps = {}
    for name, model in [('llama8b', 'meta-llama/Llama-3.1-8B-Instruct'),
                        ('codellama34b', 'codellama/CodeLlama-34b-Instruct-hf')]:
        profile = capture.PROFILES[model]
        folder = OUT/name
        cap = dict(evaluation_role=capture.ROLE, dataset=str(OUT/'sources.jsonl'), dataset_sha256=manifest['sha256'],
            dataset_manifest_sha256=base._sha(OUT/'sources.manifest.json'), run_dir=str(folder/'capture'),
            model=model, model_revision=profile['revision'], tokenizer_revision=profile['revision'],
            hidden_size=profile['hidden_size'], layers=profile['layers'], batch_size=profile['batch_size'],
            chunk_size=512, context_limit=4096, prefix_atol=1e-5)
        capfile = CFG/(name+'_capture.json')
        write(capfile, cap)
        caps[name] = cap
        node(name+'_prepare', 'scripts/167_binding_arithmetic_graph_capture.py', 'prepare', capfile, [],
             folder/'capture/preflight.json', 'passed', 'gpu', 'dev,normal', '24G', 4, '02:00:00', None, programs.ROWS)
    for name, cap in caps.items():
        folder = OUT/name
        short = name == 'llama8b'
        partition = 'dev-a30,a30,h100,h200' if short else 'h100,h200'
        time = '02:00:00' if short else '2-00:00:00'
        minimum = '00:15:00' if short else '00:30:00'
        capfile = CFG/(name+'_capture.json')
        node(name+'_capture', 'scripts/167_binding_arithmetic_graph_capture.py', 'run', capfile,
             ['software_validation', name+'_prepare'], folder/'capture/completion_manifest_v1.json',
             'complete_exploratory', 'gpu', partition, '64G', 8, time, minimum, programs.ROWS)
        beh = dict(evaluation_role=behavior.ROLE, capture_config=str(capfile), capture_config_sha256=base._sha(capfile),
            declared_plan=PLAN, declared_plan_sha256=base._sha(PLAN), generation_batch_size=64,
            run_dir=str(folder/'behavior'), report=f'reports/binding/arithmetic_graph_{name}_behavior_v{edition}.md')
        behfile = CFG/(name+'_behavior.json')
        write(behfile, beh)
        node(name+'_behavior', 'scripts/169_binding_arithmetic_graph_behavior.py', 'behavior', behfile,
             [name+'_capture'], folder/'behavior/completion_manifest_v1.json', 'complete_exploratory',
             'gpu', partition, '64G', 8, time, minimum, programs.ROWS//4)
    for name, cap in caps.items():
        folder = OUT/name
        capfile = CFG/(name+'_capture.json')
        read = dict(evaluation_role=readouts.ROLE, alpha=100., seeds=list(readouts.SEEDS),
            capture_config=str(capfile), capture_config_sha256=base._sha(capfile),
            primary_layer=24 if name == 'llama8b' else 36, run_dir=str(folder/'readouts'),
            report=f'reports/binding/arithmetic_graph_{name}_readouts_v{edition}.md')
        readfile = CFG/(name+'_readouts.json')
        write(readfile, read)
        node(name+'_readouts', 'scripts/168_binding_arithmetic_graph_readouts.py', 'readouts', readfile,
             [name+'_capture'], folder/'readouts/completion_manifest_v1.json', 'complete_exploratory',
             'cpu', 'normal', '64G', 16, '2-00:00:00', None, programs.ROWS)
    config = dict(evaluation_role=suite.ROLE, nodes=nodes, run_dir=str(OUT/'suite'),
        report=f'reports/binding/arithmetic_graph_overnight_20261029_status_v{edition}.md',
        morning_at='2026-10-30T08:00:00-05:00', declared_plan=PLAN, declared_plan_sha256=base._sha(PLAN),
        software_validation=dict(review=str(OUT/'suite/regression_review.json'),
                                 junit=str(OUT/'suite/regression.xml'), minimum_tests=2000))
    write(CFG/'suite.json', config)
    suite._CORE._config(config)
    source = freeze()
    frozen = base._json(Path(source['snapshot'])/'frozen_manifest.json')
    for name in {**frozen['code']['source_files'], **frozen['config_files']}:
        target = archive/name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != (Path(source['snapshot'])/name).read_bytes():
            raise ValueError('regression support archive differs')
        if not target.exists():
            shutil.copyfile(Path(source['snapshot'])/name, target)
    write(OUT/'source_pointer.json', source)
    print(json.dumps(dict(source=source, rows=programs.ROWS, source_review=manifest,
                         suite_config=str(CFG/'suite.json')), indent=2))


if __name__ == '__main__':
    main()
