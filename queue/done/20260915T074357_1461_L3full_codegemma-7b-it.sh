#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model codegemma-7b-it --level 3 --regimes direct trace direct_s11 trace_s11 direct_s13 trace_s13 prose

# worker=401403 rc=0 finished=2026-09-15T11:05:57Z
