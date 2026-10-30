#!/usr/bin/env python
"""Check the overnight old-value suite using metadata only."""
import argparse
import json
from pathlib import Path
from codecue.binding.old_value_overnight import check


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('check',));parser.add_argument('config')
    parser.add_argument('--deep',action='store_true');parser.add_argument('--morning',action='store_true')
    args=parser.parse_args();path=Path(args.config)
    if path.stat().st_size>64*1024:raise ValueError('bounded checker configuration required')
    value=check(json.loads(path.read_text()),deep=args.deep,morning=args.morning)
    print(json.dumps({k:value[k] for k in ('status','scientific_status','all_scientific_work_complete','morning_due','issues','scheduler_errors','logging','needs_attention')},sort_keys=True,indent=2))


if __name__=='__main__':main()
