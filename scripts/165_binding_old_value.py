#!/usr/bin/env python
"""Prepare and run paired historical/current value discovery calibration."""
import argparse
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('build','metadata','preflight','run','audit','review'))
    p.add_argument('config');args=p.parse_args();path=Path(args.config)
    if path.suffix!='.json' or path.stat().st_size>16*1024:raise ValueError('bounded JSON configuration required')
    config=json.loads(path.read_text())
    if args.command=='build':from codecue.binding import old_value_programs as module
    else:from codecue.binding import old_value_run as module
    result=getattr(module,args.command)(config)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
