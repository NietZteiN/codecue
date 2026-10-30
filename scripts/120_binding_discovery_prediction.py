#!/usr/bin/env python
"""Discovery-only predictive baselines with explicit neutral-query access."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('collect','collect_controls','run','compare'))
    parser.add_argument('config')
    args=parser.parse_args();config=json.loads(Path(args.config).read_text())
    if args.command=='collect':
        from codecue.binding.discovery_features import collect
        result=collect(config)
    elif args.command=='collect_controls':
        from codecue.binding.discovery_controls import collect
        result=collect(config)
    else:
        from codecue.binding import discovery_prediction
        result=getattr(discovery_prediction,args.command)(config)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
