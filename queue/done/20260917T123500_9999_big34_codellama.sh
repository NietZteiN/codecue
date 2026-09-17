#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model codellama-34b-it --level 5 --regimes trace trace_s11 trace_s13 --groups neutral neutral_alt congruent@v1 incongruent@v1 incongruent_alt@v1 --batch-size 4

# worker=409808 rc=0 finished=2026-09-17T17:03:20Z
