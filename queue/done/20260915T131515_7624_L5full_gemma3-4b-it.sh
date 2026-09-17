#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/20_run_model.py --model gemma3-4b-it --level 5 --regimes direct trace direct_s11 trace_s11 direct_s13 trace_s13 prose

# worker=404855 rc=0 finished=2026-09-15T23:18:33Z
