#!/usr/bin/env python
"""Refresh experiment health without loading a model or changing run artifacts."""
import argparse
import json
from pathlib import Path
from codecue.binding.experiment_status import run

parser = argparse.ArgumentParser()
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps(run(json.loads(Path(args.config).read_text())), indent=2))
