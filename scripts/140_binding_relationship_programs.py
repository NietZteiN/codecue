#!/usr/bin/env python
"""Build an immutable discovery-only varied-copy relationship source bank."""
import argparse
import json
from pathlib import Path

from codecue.binding.relationship_programs import build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    args = parser.parse_args()
    path = Path(args.config)
    from codecue.binding.experiment_log import _protected_outcome
    if (_protected_outcome(path) or _protected_outcome(path.resolve())
            or path.suffix != '.json' or path.stat().st_size > 16 * 1024):
        raise ValueError('bounded discovery JSON configuration required')
    result = build(json.loads(path.read_text()))
    print(json.dumps({key: result[key] for key in ('status', 'evaluation_role', 'rows',
        'split_rows', 'structural_components', 'distinct_definition_graphs',
        'paired_same_values_different_graph', 'new_model_queries')}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
