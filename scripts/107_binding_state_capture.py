#!/usr/bin/env python
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('prepare','extract','audit'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import state_capture
    print(json.dumps(getattr(state_capture,args.command)(json.loads(Path(args.config).read_text())),indent=2))


if __name__=='__main__':main()
