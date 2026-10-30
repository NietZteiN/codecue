#!/usr/bin/env python
"""Build and independently validate the overnight relationship source union."""
import argparse
import json

from codecue.binding import overnight_relationship_programs as programs
from codecue.binding.relationship_capture import _safe


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    args=parser.parse_args()
    path=_safe(args.config)
    if path.suffix!='.json' or path.stat().st_size>16*1024:raise ValueError('bounded JSON source configuration required')
    result=programs.build(json.loads(path.read_text()))
    print(json.dumps({key:result[key] for key in ['status','evaluation_role','rows','split_rows','cohort_rows',
        'numeric_bases','globally_unique_initial_states','numeric_bases_rejection_resampled','query_twin_bodies',
        'literal_computed_pairs','independent_python_programs','dataset_sha256','new_model_queries']},sort_keys=True,indent=2))


if __name__=='__main__':main()
