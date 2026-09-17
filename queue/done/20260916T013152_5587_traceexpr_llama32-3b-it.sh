#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model llama32-3b-it --level 5 --regimes trace_expr trace_expr_s11 trace_expr_s13

# worker=404855 rc=0 finished=2026-09-16T02:33:45Z
