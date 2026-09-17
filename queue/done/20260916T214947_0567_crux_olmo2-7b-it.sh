#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/21_run_cruxeval.py --model olmo2-7b-it

# worker=408480 rc=0 finished=2026-09-16T21:55:20Z
