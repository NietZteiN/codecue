#!/usr/bin/env python
"""Check train-only alignment/reduced-rank helpers without reading activations."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('preflight').add_argument('config')
    commands.add_parser('selfcheck').add_argument('--review', required=True)
    args = parser.parse_args()
    from codecue.binding import probe_sensitivities
    if args.command == 'preflight':
        result = probe_sensitivities.preflight(json.loads(Path(args.config).read_text()))
        review = result['config']['output_review']
    else:
        result = probe_sensitivities.selfcheck(args.review)
        review = args.review
    print(json.dumps({key: result[key] for key in ('status', 'evaluation_role',
        'study_fits_performed', 'activation_payloads_opened', 'new_model_queries')}
        | {'review': review}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
