#!/usr/bin/env python
"""Prepare, capture or audit the frozen varied copy/overwrite source cohort."""
import argparse
import json

from codecue.binding import schedule_capture as capture


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('metadata','prepare','run','audit'))
    parser.add_argument('config')
    args=parser.parse_args()
    config=capture._json(args.config)
    if len(json.dumps(config,allow_nan=False).encode())>16*1024:
        raise ValueError('bounded schedule capture configuration required')
    value=getattr(capture,args.command)(config)
    print(json.dumps({key:value[key] for key in ('status','evaluation_role','cases','source_rows',
        'feature_shape','new_model_queries','model_prefill_cases','prefix_comparisons') if key in value},sort_keys=True,indent=2))


if __name__=='__main__': main()
