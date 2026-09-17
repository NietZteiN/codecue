#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/12_lure_gate.py --model codellama-7b-it

# worker=401403 rc=0 finished=2026-09-15T07:46:54Z
