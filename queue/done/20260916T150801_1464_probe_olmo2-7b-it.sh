#!/bin/bash
# needs: /work/jvl210002/migration/codecue/results/summary/span_check.json
set -uo pipefail
cd "/work/jvl210002/migration/codecue"
python scripts/30_cache_and_probe.py --model olmo2-7b-it --level 5 --role v1 --cell-only --n-train 2000 --n-test 800

# worker=408480 rc=0 finished=2026-09-16T15:13:00Z
