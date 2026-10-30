#!/usr/bin/env python
"""Fit or audit the fixed arithmetic relationship readout banks."""
import argparse
import json
import os
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_graph_readouts as readouts, relationship_capture as base

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('command', choices=('readouts', 'audit'))
p.add_argument('config')
a = p.parse_args()
threads = int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))
if threads < 1:
    raise ValueError('positive allocated CPU count required')
with threadpool_limits(limits=threads):
    r = readouts.run(base._json(a.config)) if a.command == 'readouts' else readouts.audit(base._json(a.config))
    if a.command == 'readouts':
        readouts.audit(base._json(a.config))
print(json.dumps({k: r[k] for k in ('status', 'cases', 'factorizations') if k in r}))
