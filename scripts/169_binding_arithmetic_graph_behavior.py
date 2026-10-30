#!/usr/bin/env python
"""Collect or audit exact-prompt arithmetic generated answers."""
import argparse
import json
from codecue.binding import arithmetic_graph_behavior as behavior, relationship_capture as base

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('command', choices=('behavior', 'audit'))
p.add_argument('config')
a = p.parse_args()
r = behavior.run(base._json(a.config)) if a.command == 'behavior' else behavior.audit(base._json(a.config))
if a.command == 'behavior':
    behavior.audit(base._json(a.config))
print(json.dumps({k: r[k] for k in ('status', 'cases', 'generated_responses') if k in r}))
