#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/12_lure_gate.py --model llama32-3b-it

# worker=401403 rc=0 finished=2026-09-15T07:45:40Z
