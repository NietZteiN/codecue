#!/usr/bin/env python
"""Prepare, run or audit local arithmetic capture."""
import argparse
import json
from codecue.binding import arithmetic_local_capture as capture, relationship_capture as base

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=['prepare', 'run', 'audit'])
parser.add_argument('config')
args = parser.parse_args()
result = getattr(capture, args.command)(base._json(args.config))
print(json.dumps({k: result.get(k) for k in ['status', 'cases', 'new_generated_answers']}))
