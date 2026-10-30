#!/usr/bin/env python
"""Inspect completed varied-schedule DEV predictions without parameter application."""
import argparse
import json
from codecue.binding import relationship_capture as bounded
from codecue.binding import schedule_score_review as study


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('preflight','run','audit','completed_result'))
    parser.add_argument('config')
    args=parser.parse_args()
    path=bounded._safe(args.config)
    if path.suffix!='.json' or path.stat().st_size>16*1024:
        raise ValueError('bounded posthoc configuration required')
    result=getattr(study,args.command)(json.loads(path.read_text()))
    print(json.dumps({key:result[key] for key in ('status','evaluation_role','score_banks',
        'development_prediction_rows','new_model_queries','new_fits') if key in result},sort_keys=True,indent=2))


if __name__=='__main__': main()
