#!/usr/bin/env python
"""Build, validate, run and audit the finite discovery value-transfer assay."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('build', 'prepare', 'run', 'audit'))
    parser.add_argument('config')
    args = parser.parse_args()
    from codecue.binding import value_transfer
    print(json.dumps(getattr(value_transfer, args.command)(json.loads(Path(args.config).read_text())), indent=2))


if __name__ == '__main__':
    main()
