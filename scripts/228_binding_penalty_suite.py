#!/usr/bin/env python
"""Submit or inspect the extended penalty path and shared-prior DAG."""
import argparse
import json
from codecue.binding import arithmetic_penalty_suite as suite, relationship_capture as base

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=['submit', 'watch', 'status']); parser.add_argument('config')
parser.add_argument('snapshot', nargs='?')
args = parser.parse_args(); config = base._json(args.config)
result = suite.submit(config, args.snapshot, args.config) if args.command == 'submit' else getattr(suite, args.command)(config)
print(json.dumps({k: result.get(k) for k in ['status', 'all_terminal']}))
