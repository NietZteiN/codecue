#!/usr/bin/env python
"""Submit, supervise, inspect or record the morning arithmetic suite status."""
import argparse
import json
from codecue.binding import arithmetic_graph_suite as suite, relationship_capture as base

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('command', choices=('submit', 'watch', 'status', 'morning'))
p.add_argument('config')
p.add_argument('snapshot', nargs='?')
a = p.parse_args()
c = base._json(a.config)
r = suite.submit(c, a.snapshot, a.config) if a.command == 'submit' else getattr(suite, a.command)(c)
print(json.dumps({k: r[k] for k in ('status', 'recorded_utc', 'stages', 'all_terminal') if k in r}, indent=2))
