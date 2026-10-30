#!/usr/bin/env python
"""Prepare exact integer/EOS events, collect scalar confidence, or audit records."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('prepare','run','audit'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import candidate_measurement
    result=getattr(candidate_measurement,args.command)(json.loads(Path(args.config).read_text()))
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
