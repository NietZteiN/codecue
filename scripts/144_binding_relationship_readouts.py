#!/usr/bin/env python
"""Fit/audit fixed discovery structural and algebraic relationship readouts."""
import argparse
import json
from pathlib import Path
from codecue.binding import relationship_readouts as readouts

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=('preflight', 'run', 'audit'))
parser.add_argument('config')
args = parser.parse_args(); path = Path(args.config)
if path.stat().st_size > 8*1024**2: raise ValueError('bounded readout config required')
result = getattr(readouts, args.command)(json.loads(path.read_text()))
print(json.dumps({key: result[key] for key in ('status', 'factorizations', 'parameter_replay_rows', 'new_model_queries') if key in result}, sort_keys=True, indent=2))
