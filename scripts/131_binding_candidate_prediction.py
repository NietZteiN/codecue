#!/usr/bin/env python
"""Discovery event-feature collection and the unchanged generic grouped protocol."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('collect', 'run', 'compare'))
    parser.add_argument('config')
    args = parser.parse_args();config = json.loads(Path(args.config).read_text())
    if args.command == 'collect':
        from codecue.binding.candidate_prediction import collect
        full = collect(config)
        result = {key: full[key] for key in ('status', 'profile', 'n', 'groups', 'sha256', 'new_language_model_queries')}
    else:
        from codecue.binding import discovery_prediction
        result = getattr(discovery_prediction, args.command)(config)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
