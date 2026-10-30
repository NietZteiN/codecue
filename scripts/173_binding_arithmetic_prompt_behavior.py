#!/usr/bin/env python
"""Prepare, collect or audit matched arithmetic output/query controls."""
import argparse,json
from codecue.binding import arithmetic_prompt_control as control,relationship_capture as base

p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','run','audit']);p.add_argument('config');a=p.parse_args()
cfg=base._json(a.config);r=getattr(control,a.command)(cfg)
if a.command=='run':control.audit(cfg)
print(json.dumps({k:r[k] for k in ('status','cases','new_model_queries','generated_responses') if k in r}))
