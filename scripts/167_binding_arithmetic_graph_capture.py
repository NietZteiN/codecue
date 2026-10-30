#!/usr/bin/env python
"""Prepare, capture, audit or validate the arithmetic graph discovery suite."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from codecue.binding import arithmetic_graph_capture as capture, relationship_capture as base
from codecue.binding.datasets import digest


def qa(config):
    source = base._current_source(config)
    root = Path(config['run_dir'])
    root.mkdir(parents=True, exist_ok=True)
    frozen = base._json(Path(source['snapshot'])/'frozen_manifest.json')
    archive_root = Path(config['test_archive']).parents[1]
    for name, expected in {**frozen['code']['source_files'], **frozen['config_files']}.items():
        if hashlib.sha256((archive_root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('regression support source/config differs from frozen snapshot')
    for name, expected in config['test_files'].items():
        if hashlib.sha256((archive_root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('frozen regression source differs')
    junit = root/'regression.xml'
    # Existing regression modules import sibling helper modules by their file
    # names. Pytest's prepend mode resolves those within the frozen archive.
    # Tests exercise both frozen and unfrozen source guards. Import their
    # byte-verified source mirror, which has no frozen_manifest.json, rather
    # than accidentally making the unfrozen fixture a real frozen checkout.
    environment = dict(os.environ, PYTHONPATH=str((archive_root/'src').resolve()))
    result = subprocess.run([sys.executable, '-m', 'pytest', config['test_archive'], '-q',
                             '--import-mode=prepend', '--junitxml='+str(junit)], env=environment, check=False)
    tree = ET.parse(junit).getroot()
    suites = tree.findall('testsuite')
    tests = sum(int(s.attrib['tests']) for s in suites)
    passed = result.returncode == 0 and tests >= config['minimum_tests'] and all(
        int(s.attrib.get(k, 0)) == 0 for s in suites for k in ('errors', 'failures', 'skipped'))
    review = dict(status='passed' if passed else 'failed', config_hash=digest(config),
                  source_sha256=source['source_sha256'], source=source,
                  junit_sha256=base._sha(junit), tests=tests)
    base._put(root/'regression_review.json', review)
    if not passed:
        raise ValueError('frozen arithmetic regression failed')
    return review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('metadata', 'prepare', 'run', 'audit'))
    parser.add_argument('config')
    args = parser.parse_args()
    config = base._json(args.config)
    result = qa(config) if config.get('evaluation_role') == 'arithmetic_graph_software_validation_v1' else getattr(capture, args.command)(config)
    if args.command == 'run':
        capture.audit(config)
    print(json.dumps({k: result[k] for k in ('status', 'cases', 'tests', 'complete') if k in result}))


if __name__ == '__main__':
    main()
