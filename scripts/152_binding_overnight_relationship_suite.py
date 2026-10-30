#!/usr/bin/env python
"""Submit, supervise or inspect the frozen overnight relationship suite."""
import argparse,json
from pathlib import Path
from codecue.binding import relationship_capture as base,overnight_relationship_suite as suite

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('submit','watch','status'));p.add_argument('config');p.add_argument('snapshot',nargs='?')
    args=p.parse_args();config=base._json(args.config)
    if args.command=='submit':
        r=suite.submit(config,args.snapshot,args.config)
    else:r=getattr(suite,args.command)(config)
    print(json.dumps({k:r[k] for k in ('status','evaluation_role','recorded_utc') if k in r},sort_keys=True,indent=2))

if __name__=='__main__':main()
