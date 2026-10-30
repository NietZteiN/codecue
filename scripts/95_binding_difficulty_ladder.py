#!/usr/bin/env python
"""Execute the frozen ladder once, then apply its predeclared gate."""
import json
import sys
from pathlib import Path

from codecue.binding.calibration import run
from codecue.binding.ladder import analyze

config=json.loads(Path(sys.argv[1]).read_text())
run(config)
print(json.dumps(analyze(config),indent=2))
