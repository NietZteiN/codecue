#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/12_lure_gate.py --model llama32-3b-it

# worker=404855 rc=0 finished=2026-09-15T23:25:55Z
