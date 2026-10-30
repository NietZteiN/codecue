#!/usr/bin/env python
"""Run or audit short printed arithmetic calibration."""
import argparse
import json
from codecue.binding import arithmetic_local_behavior as behavior, relationship_capture as base

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=['run', 'audit'])
parser.add_argument('config')
args = parser.parse_args()
result = getattr(behavior, args.command)(base._json(args.config))
print(json.dumps({k: result.get(k) for k in ['status', 'cases', 'metrics']}))
