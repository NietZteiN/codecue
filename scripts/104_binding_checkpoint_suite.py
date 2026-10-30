#!/usr/bin/env python
"""Prepare, execute, or audit a cached-checkpoint discovery suite."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('preflight', 'run', 'audit', 'collect'))
    parser.add_argument('config')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    from codecue.binding import checkpoint_suite as suite
    if args.command != 'collect':
        suite.configure_runtime(config)
    print(json.dumps(getattr(suite, args.command)(config), indent=2))


if __name__ == '__main__':
    main()
