#!/usr/bin/env python
"""Fresh arithmetic/readout calibration; preserves historical and sealed outcomes."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('build','preflight','run','audit','review','compare'))
    parser.add_argument('config')
    args=parser.parse_args();config=json.loads(Path(args.config).read_text())
    if args.command=='build':
        from codecue.binding.arithmetic_readout import build
        result=build(config)
    elif args.command in ('review','compare'):
        from codecue.binding import arithmetic_readout_review
        result=getattr(arithmetic_readout_review,args.command)(config)
    else:
        from codecue.binding import checkpoint_suite
        if args.command in ('preflight','run'):checkpoint_suite.configure_runtime(config)
        result=getattr(checkpoint_suite,args.command)(config)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
