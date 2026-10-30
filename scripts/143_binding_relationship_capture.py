#!/usr/bin/env python
"""Prepare, run or audit discovery relationship prefill captures."""
import argparse
import json
from pathlib import Path

from codecue.binding import relationship_capture as capture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('metadata', 'prepare', 'run', 'audit'))
    parser.add_argument('config')
    args = parser.parse_args()
    path = capture._safe(args.config)
    if path.suffix != '.json' or path.stat().st_size > 16 * 1024:
        raise ValueError('bounded discovery configuration required')
    result = getattr(capture, args.command)(json.loads(Path(path).read_text()))
    print(json.dumps({key: result[key] for key in ('status', 'complete', 'evaluation_role',
        'cases', 'source_rows', 'feature_shape', 'prefix_comparisons', 'prefix_max_abs_diff',
        'new_model_queries') if key in result}, sort_keys=True, indent=2))


if __name__ == '__main__': main()
