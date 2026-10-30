#!/usr/bin/env python
"""Control durable, CPU-only SLURM experiment-log reconciliation."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('enable','status','disable','tick'))
    parser.add_argument('--root',required=True,help='Explicit shared project workspace root')
    parser.add_argument('--interval-minutes',type=int,default=10)
    parser.add_argument('--partition',choices=('dev','normal'),default='dev')
    parser.add_argument('--account')
    parser.add_argument('--force',action='store_true',help='Run a manual tick even when the interval is not due')
    args=parser.parse_args()
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
    from codecue.binding import experiment_log_scheduler as scheduler
    if args.command=='enable':result=scheduler.enable(args.root,interval_minutes=args.interval_minutes,partition=args.partition,account=args.account)
    elif args.command=='tick':result=scheduler.tick(args.root,force=args.force)
    else:result=getattr(scheduler,args.command)(args.root)
    print(json.dumps(result,sort_keys=True,indent=2,default=str))
    return 1 if result.get('status') in ('failed','degraded') or result.get('cancellation_failed') else 0


if __name__=='__main__':sys.exit(main())
