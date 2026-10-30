#!/usr/bin/env python
"""Execute separately registered computed and dead-reference routing discovery."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('build', 'prepare', 'run', 'audit', 'review', 'audit-names'))
    parser.add_argument('config')
    parser.add_argument('--analysis-revision')
    args = parser.parse_args()
    from codecue.binding import routing_extension
    config=json.loads(Path(args.config).read_text())
    if args.analysis_revision is not None and args.command != 'review':
        parser.error('--analysis-revision applies only to review')
    result=(routing_extension.review(config,analysis_revision=args.analysis_revision) if args.command=='review'
            else getattr(routing_extension,args.command.replace('-','_'))(config))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
