#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model llama31-8b-it --level 3 --n-sets 200 --regimes codechain --overwrite

# worker=401403 rc=0 finished=2026-09-15T06:26:31Z
