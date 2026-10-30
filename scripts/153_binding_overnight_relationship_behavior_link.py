#!/usr/bin/env python
"""Run or audit the posthoc saved-score/answer join on CPU only."""
import argparse
import json
from codecue.binding import overnight_relationship_behavior_link as link
from codecue.binding.relationship_capture import _safe


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('run','audit'));parser.add_argument('config')
    args=parser.parse_args();path=_safe(args.config)
    if path.suffix!='.json' or path.stat().st_size>16*1024:raise ValueError('bounded explicit analysis configuration required')
    result=getattr(link,args.command)(json.loads(path.read_text()))
    print(json.dumps({key:result[key] for key in ('status','evaluation_role','development_cases','original_responses_validated',
        'new_model_queries','new_fits','parameter_replays','raw_activations_loaded') if key in result},sort_keys=True,indent=2))


if __name__=='__main__':main()
