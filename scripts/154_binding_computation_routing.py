#!/usr/bin/env python
"""Frozen continuously batched computation/routing calibration and review."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'metadata', 'preflight', 'run', 'audit', 'review'))
    parser.add_argument('config')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    if args.command == 'build':
        from codecue.binding import computation_routing_programs
        result = computation_routing_programs.build(config)
    else:
        from codecue.binding import computation_routing_run
        result = getattr(computation_routing_run, args.command)(config)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
