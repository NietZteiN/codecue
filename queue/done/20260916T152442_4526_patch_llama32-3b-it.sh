#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/40_patch.py --model llama32-3b-it --level 5 --n-pairs 300

# worker=408480 rc=0 finished=2026-09-16T15:59:33Z
