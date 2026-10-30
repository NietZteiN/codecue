#!/usr/bin/env python
"""Continue a frozen relationship capture through fixed CPU readout fitting."""
import argparse
import json

from codecue.binding import relationship_capture as capture
from codecue.binding import relationship_pipeline as pipeline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('run', 'audit'))
    parser.add_argument('config')
    args = parser.parse_args()
    path = capture._safe(args.config)
    if path.suffix != '.json' or path.stat().st_size > 16 * 1024:
        raise ValueError('bounded discovery pipeline configuration required')
    result = getattr(pipeline, args.command)(json.loads(path.read_text()))
    print(json.dumps({key: result[key] for key in ('status', 'evaluation_role', 'factorizations',
        'parameter_replay_rows', 'new_model_queries', 'nested_jobs_submitted')}, sort_keys=True, indent=2))


if __name__ == '__main__': main()
