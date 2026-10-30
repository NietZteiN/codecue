#!/usr/bin/env python
"""Run fixed nested joint-confidence discovery controls using saved scalar banks."""
import argparse
import json
from pathlib import Path

from codecue.binding import joint_confidence

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('command', choices=('collect', 'fit', 'compare'))
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps(getattr(joint_confidence, args.command)(json.loads(Path(args.config).read_text())),
                 sort_keys=True, indent=2))
