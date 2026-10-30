#!/usr/bin/env python
"""Run or audit fixed posthoc controls on existing relationship score banks."""
import argparse
import json
from codecue.binding import relationship_capture as capture, relationship_followup as followup

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('run','audit'));parser.add_argument('config')
    args=parser.parse_args();config=capture._json(args.config)
    if len(json.dumps(config).encode())>16*1024:raise ValueError('bounded posthoc configuration required')
    result=getattr(followup,args.command)(config)
    print(json.dumps({key:result[key] for key in ('status','evaluation_role','saved_score_rows_read','new_model_queries','new_fits')},sort_keys=True,indent=2))

if __name__=='__main__':main()
