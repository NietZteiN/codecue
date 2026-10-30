#!/usr/bin/env python
"""Prepare conditional structural-group precision scenarios from discovery OOF."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('collect','run'))
    parser.add_argument('config')
    args=parser.parse_args()
    from codecue.binding import precision_planning
    result=getattr(precision_planning,args.command)(json.loads(Path(args.config).read_text()))
    if args.command=='collect':
        result={**result,'series':[{key:value for key,value in series.items() if key!='groups'}
                                  for series in result['series']]}
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
