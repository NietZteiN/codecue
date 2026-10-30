#!/usr/bin/env python
"""Replay saved arithmetic readouts and publish postrun diagnostics."""
import argparse,json,os
from threadpoolctl import threadpool_limits
from codecue.binding import arithmetic_graph_review as review, relationship_capture as base

p=argparse.ArgumentParser(description=__doc__);p.add_argument('config');a=p.parse_args()
with threadpool_limits(limits=int(os.environ.get('SLURM_CPUS_PER_TASK','1'))):
    result=review.run(base._json(a.config))
print(json.dumps({key:result[key] for key in ('status','new_model_queries','new_fits','parameter_application_rows')}))
