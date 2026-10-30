#!/usr/bin/env python
"""Prepare, collect or audit the fixed label-free discovery stress query."""
import argparse
import json
from pathlib import Path

from codecue.binding import stress_measurement as stress


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('metadata-preflight', 'prepare', 'collect', 'audit'))
    parser.add_argument('config')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    command = 'metadata_preflight' if args.command == 'metadata-preflight' else args.command
    result = getattr(stress, command)(config)
    print(json.dumps({k: result[k] for k in ('status', 'evaluation_role', 'cases', 'evaluated',
        'measurement', 'generated_tokens', 'case_request_attempts', 'target_outcomes_read') if k in result}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
