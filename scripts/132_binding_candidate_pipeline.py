#!/usr/bin/env python
"""Run an immutable CPU prediction stage after complete event measurements."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('fit','compare'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import candidate_pipeline
    result=getattr(candidate_pipeline,args.command)(json.loads(Path(args.config).read_text()))
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
