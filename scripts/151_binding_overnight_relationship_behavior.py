#!/usr/bin/env python
"""Run or audit fresh answers for the overnight relationship discovery suite."""
import argparse,json
from codecue.binding import relationship_capture as base,overnight_relationship_behavior as behavior

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('run','audit'));p.add_argument('config')
    args=p.parse_args();r=getattr(behavior,args.command)(base._json(args.config))
    print(json.dumps({k:r[k] for k in ('status','evaluation_role','cases','new_model_queries','generated_responses')},sort_keys=True,indent=2))

if __name__=='__main__':main()
