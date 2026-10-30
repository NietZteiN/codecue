#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from codecue.binding.throughput_audit import run

parser = argparse.ArgumentParser()
parser.add_argument('config')
args = parser.parse_args()
print(json.dumps(run(json.loads(Path(args.config).read_text())), indent=2))
