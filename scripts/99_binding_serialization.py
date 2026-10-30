#!/usr/bin/env python
"""Verify native replay or summarize a fixed CRUXEval serialization comparison."""
import argparse
import json
from pathlib import Path
from codecue.binding.serialization_comparison import compare, replay, smoke, finalize, preflight_all

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=('replay', 'compare', 'smoke', 'finalize', 'preflight'))
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps({'replay': replay, 'compare': compare, 'smoke': smoke, 'finalize': finalize,
                  'preflight': preflight_all}[args.command](
    json.loads(Path(args.config).read_text())), indent=2))
