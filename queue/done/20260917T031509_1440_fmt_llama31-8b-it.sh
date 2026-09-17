#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model llama31-8b-it --level 5 --regimes repl repl_s11 repl_s13 comment comment_s11 comment_s13

# worker=409808 rc=0 finished=2026-09-17T13:26:02Z
