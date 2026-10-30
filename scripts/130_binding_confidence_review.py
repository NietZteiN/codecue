#!/usr/bin/env python
"""Check exact baseline anchors and draw fixed confidence contrasts."""
import argparse
import json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding.confidence_review import run
    print(json.dumps(run(json.loads(Path(args.config).read_text())),sort_keys=True,indent=2))


if __name__=='__main__':main()
