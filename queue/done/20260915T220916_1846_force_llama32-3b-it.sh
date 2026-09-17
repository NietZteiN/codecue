#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/13_force_value.py --model llama32-3b-it --level 5 --n-sets 500

# worker=404855 rc=0 finished=2026-09-15T23:37:00Z
