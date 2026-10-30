#!/usr/bin/env python
"""Prepare or measure label-free confidence at exact saved discovery prompts."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('prepare','run','audit'))
    parser.add_argument('config')
    args=parser.parse_args();config=json.loads(Path(args.config).read_text())
    from codecue.binding import confidence
    print(json.dumps(getattr(confidence,args.command)(config),sort_keys=True,indent=2))


if __name__=='__main__':main()
