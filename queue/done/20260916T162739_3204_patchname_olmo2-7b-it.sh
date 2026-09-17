#!/bin/bash
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/40_patch.py --model olmo2-7b-it --level 5 --n-pairs 300 --sites name --contrasts main ctl_word

# worker=408480 rc=0 finished=2026-09-16T16:40:41Z
