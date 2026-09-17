#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/12_lure_gate.py --model olmo2-1b-it

# worker=404855 rc=0 finished=2026-09-15T23:22:50Z
