#!/usr/bin/env python
"""Run or audit one frozen overnight relationship readout panel."""
import argparse
import json
from codecue.binding import overnight_relationship_readouts as study
from codecue.binding import relationship_capture as bounded


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('preflight','run','audit'))
    parser.add_argument('config')
    args=parser.parse_args();path=bounded._safe(args.config)
    if path.suffix!='.json' or path.stat().st_size>16*1024:raise ValueError('bounded overnight config required')
    result=getattr(study,args.command)(json.loads(path.read_text()))
    print(json.dumps({key:result[key] for key in ('status','evaluation_role','cases','factorizations','parameter_replay_rows','literal_transfer_rows','new_model_queries') if key in result},sort_keys=True,indent=2))


if __name__=='__main__':main()
