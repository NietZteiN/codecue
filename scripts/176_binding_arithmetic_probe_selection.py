#!/usr/bin/env python
"""Select archived arithmetic probes with grouped validation inside TRAIN."""
import argparse
import json
import os
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_probe_selection as selection, relationship_capture as base

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=['run', 'audit'])
parser.add_argument('config')
args = parser.parse_args()
with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))):
    result = getattr(selection, args.command)(base._json(args.config))
print(json.dumps({k: result.get(k) for k in ['status', 'new_model_queries', 'choices']}))
