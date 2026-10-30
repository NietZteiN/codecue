#!/usr/bin/env python
"""Run grouped discovery prediction from one distinct ungraded stress query."""
import argparse
import json
from pathlib import Path

from codecue.binding import stress_prediction

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=('collect', 'fit', 'compare'))
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps(getattr(stress_prediction, args.command)(json.loads(Path(args.config).read_text())),
                 sort_keys=True, indent=2))
