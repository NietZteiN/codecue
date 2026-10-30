#!/usr/bin/env python
"""Run the fixed discovery-only PCA/rank/alignment sensitivity without a model."""
import argparse
import json
from pathlib import Path

from codecue.binding.representation_sensitivity import preflight, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('preflight', 'run'))
    parser.add_argument('config')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    result = (preflight if args.command == 'preflight' else run)(config)
    print(json.dumps({k: result[k] for k in ('status', 'evaluation_role', 'fits', 'parameter_replay_rows', 'generated_holdouts_opened') if k in result}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
