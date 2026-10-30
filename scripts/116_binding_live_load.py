#!/usr/bin/env python
"""Generate and evaluate matched computed-retention frontiers."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('build','preflight','run','audit','review','compare','prepare_backend','run_backend','audit_backend','backend_report'))
    parser.add_argument('config')
    args=parser.parse_args();config=json.loads(Path(args.config).read_text())
    from codecue.binding import live_load
    if args.command in ('build','review','compare','prepare_backend','run_backend','audit_backend','backend_report'):
        result=getattr(live_load,args.command)(config)
    else:
        from codecue.binding import checkpoint_suite
        checkpoint_suite.configure_runtime(config)
        result=getattr(checkpoint_suite,args.command)(config)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
