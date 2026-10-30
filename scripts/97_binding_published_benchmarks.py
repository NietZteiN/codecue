#!/usr/bin/env python
"""Pinned published benchmark preparation, tokenizer QA and greedy evaluation."""
import argparse
import json
from pathlib import Path

from codecue.binding.published_benchmarks import build, preflight, run, rescore_smoke

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=('build', 'preflight', 'run', 'rescore-smoke'))
parser.add_argument('config')
args = parser.parse_args()
result = {'build': build, 'preflight': preflight, 'run': run, 'rescore-smoke': rescore_smoke}[args.command](
    json.loads(Path(args.config).read_text()))
print(json.dumps(result, indent=2))
