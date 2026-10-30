#!/usr/bin/env python
"""Build and independently validate discovery-only copy/overwrite schedule targets."""
import argparse
import json

from codecue.binding import relationship_schedule_programs as programs
from codecue.binding.relationship_capture import _safe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    args = parser.parse_args()
    path = _safe(args.config)
    if path.suffix != '.json' or path.stat().st_size > 16*1024:
        raise ValueError('bounded JSON schedule source configuration required')
    result = programs.build(json.loads(path.read_text()))
    keys = ('status', 'evaluation_role', 'rows', 'split_rows', 'raw_schedule_count',
        'raw_schedule_parent_templates', 'effective_ordered_schedule_units', 'effective_canonical_graph_units',
        'split_canonical_graph_units', 'maximum_assignment_version', 'independent_python_programs',
        'dataset_sha256', 'learned_readout_compatible', 'model_queries')
    print(json.dumps({key: result[key] for key in keys}, sort_keys=True, indent=2))


if __name__ == '__main__': main()
