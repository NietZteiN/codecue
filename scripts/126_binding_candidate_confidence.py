#!/usr/bin/env python
"""Declare finite integer-plus-EOS events or run their software-only selfcheck."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('preflight','selfcheck'))
    parser.add_argument('config',nargs='?')
    args=parser.parse_args()
    from codecue.binding import candidate_confidence
    if args.command=='preflight':
        if not args.config:parser.error('preflight requires a JSON config')
        result=candidate_confidence.preflight(json.loads(Path(args.config).read_text()))
    else:
        if args.config:parser.error('selfcheck uses its built-in tiny fixtures and takes no config')
        result=candidate_confidence.selfcheck()
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
