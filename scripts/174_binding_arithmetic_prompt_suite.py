#!/usr/bin/env python
"""Submit or inspect the durable matched prompt-control suite."""
import argparse,json
from codecue.binding import arithmetic_prompt_suite as suite,relationship_capture as base
p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['submit','watch','status']);p.add_argument('config');p.add_argument('snapshot',nargs='?');a=p.parse_args()
c=base._json(a.config);r=suite.submit(c,a.snapshot,a.config) if a.command=='submit' else getattr(suite,a.command)(c)
print(json.dumps({k:r[k] for k in ['status','stages','all_terminal','recorded_utc'] if k in r},indent=2))
