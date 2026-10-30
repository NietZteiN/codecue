#!/usr/bin/env python
"""Join audited discovery confidence scalars into fixed grouped predictor tiers."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('collect',))
    parser.add_argument('config')
    args = parser.parse_args()
    from codecue.binding.confidence_prediction import collect
    result = collect(json.loads(Path(args.config).read_text()))
    print(json.dumps({key: result[key] for key in ('status', 'profile', 'n', 'groups',
        'sha256', 'new_language_model_queries', 'generated_holdouts_opened')}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
