#!/usr/bin/env python
"""Inspect/rebuild the automatic metadata-only experiment log."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from codecue.binding import experiment_log


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('refresh','list','show'))
    parser.add_argument('record_id',nargs='?')
    parser.add_argument('--root')
    parser.add_argument('--scheduler',action='store_true',help='Reconcile actual SLURM job states, including canceled jobs')
    parser.add_argument('--kind',choices=('run','analysis','dataset','job'))
    parser.add_argument('--status')
    args=parser.parse_args()
    if args.command=='refresh':result=experiment_log.refresh(args.root,reconcile_scheduler=args.scheduler)
    else:
        result=experiment_log.list_records(args.root,kind=args.kind)
        if args.status:result=[r for r in result if r['status']==args.status]
        if args.command=='show':
            result=[r for r in result if r['id']==args.record_id]
            if not result:parser.error('record not found')
            result=result[0]
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
