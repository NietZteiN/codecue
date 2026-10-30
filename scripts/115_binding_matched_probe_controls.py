#!/usr/bin/env python
"""Frequency-matched grouped probe controls using saved activations only."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('run','audit','review'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import matched_probe_controls
    print(json.dumps(getattr(matched_probe_controls,args.command)(json.loads(Path(args.config).read_text())),indent=2))


if __name__=='__main__':main()
