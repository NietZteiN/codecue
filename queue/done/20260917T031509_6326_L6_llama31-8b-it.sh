#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model llama31-8b-it --level 6 --regimes trace trace_s11 trace_s13

# worker=409808 rc=0 finished=2026-09-17T15:24:01Z
