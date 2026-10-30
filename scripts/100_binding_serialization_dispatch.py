#!/usr/bin/env python
"""Check the measured smoke runtime, then invoke unchanged frozen inference."""
import argparse
import json
from pathlib import Path
from codecue.binding.serialization_comparison import dispatch_full

parser = argparse.ArgumentParser()
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps(dispatch_full(json.loads(Path(args.config).read_text())), indent=2))
