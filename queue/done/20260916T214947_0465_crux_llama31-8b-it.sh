#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/21_run_cruxeval.py --model llama31-8b-it

# worker=408480 rc=0 finished=2026-09-16T21:52:38Z
