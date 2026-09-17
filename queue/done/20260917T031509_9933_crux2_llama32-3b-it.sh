#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/21_run_cruxeval.py --model llama32-3b-it

# worker=409808 rc=0 finished=2026-09-17T15:40:42Z
