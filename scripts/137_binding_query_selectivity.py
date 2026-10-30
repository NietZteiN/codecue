#!/usr/bin/env python
"""Fixed queried/unqueried discovery readouts; numerical fits belong in sbatch."""
import argparse
import json
from pathlib import Path

from codecue.binding import query_selectivity as query


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('preflight', 'run', 'audit', 'seal'))
    parser.add_argument('config')
    parser.add_argument('--review-sha256', help='Explicit existing full-review SHA256 for seal only')
    parser.add_argument('--fit-source-snapshot', help='Original immutable fit source directory for seal only')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    if args.command == 'seal':
        if not args.review_sha256 or not args.fit_source_snapshot:
            parser.error('seal requires --review-sha256 and --fit-source-snapshot')
        result = query.seal(config, args.review_sha256, args.fit_source_snapshot)
    else:
        result = getattr(query, args.command)(config)
    print(json.dumps({key: result[key] for key in ('status', 'evaluation_role', 'cases',
        'factorizations', 'independent_heads', 'parameter_replay_rows', 'new_model_queries') if key in result}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
