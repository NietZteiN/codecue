#!/usr/bin/env python
"""Render the complete verified descriptive query-selectivity grid."""
import argparse
import json
from pathlib import Path

from codecue.binding.query_selectivity_review import run

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps(run(json.loads(Path(args.config).read_text())), sort_keys=True, indent=2))
