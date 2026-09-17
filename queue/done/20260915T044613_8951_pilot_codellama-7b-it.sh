#!/bin/bash
# needs: /work/jvl210002/migration/codecue/results/summary/layout_check.json
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model codellama-7b-it --level 3 --n-sets 200 --regimes direct trace prose codechain

# worker=401403 rc=0 finished=2026-09-15T06:06:16Z
