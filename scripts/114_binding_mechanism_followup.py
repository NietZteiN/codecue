#!/usr/bin/env python
"""Run fresh numeric ownership and common-final-query controls."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('build','prepare','run','audit','review'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import mechanism_followup
    print(json.dumps(getattr(mechanism_followup,args.command)(json.loads(Path(args.config).read_text())),indent=2))


if __name__=='__main__':main()
