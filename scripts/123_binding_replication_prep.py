#!/usr/bin/env python
"""Plan, build and audit generated discovery cohort preparation."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('plan','build','audit'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import replication_prep
    config=json.loads(Path(args.config).read_text())
    print(json.dumps(getattr(replication_prep,args.command)(config),sort_keys=True,indent=2))


if __name__=='__main__':main()
