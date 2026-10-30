#!/usr/bin/env python
"""Audit and summarize an immutable completed public benchmark run."""
import argparse
import json
from pathlib import Path

from codecue.binding.published_review import review

parser = argparse.ArgumentParser()
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps(review(json.loads(Path(args.config).read_text())), indent=2))
