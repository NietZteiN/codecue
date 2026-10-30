#!/usr/bin/env python
"""Fit or audit shared arithmetic dependency probes."""
import argparse
import json
import os
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_local_probes as probes, relationship_capture as base

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=['run', 'audit'])
parser.add_argument('config')
args = parser.parse_args()
import torch
threads = int(os.environ.get('SLURM_CPUS_PER_TASK', '1'))
torch.set_num_threads(threads)
with threadpool_limits(limits=threads):
    result = getattr(probes, args.command)(base._json(args.config))
print(json.dumps({k: result.get(k) for k in ['status', 'new_model_queries', 'selected_methods']}))
