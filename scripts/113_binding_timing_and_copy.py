#!/usr/bin/env python
"""Run explicit query-timing and semantically equivalent copy-site studies."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('build','prepare','run','audit','review','patterns'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import timing_and_copy
    print(json.dumps(getattr(timing_and_copy,args.command)(json.loads(Path(args.config).read_text())),indent=2))


if __name__=='__main__':main()
