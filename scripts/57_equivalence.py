#!/usr/bin/env python
"""E9: the equivalence bound as a test rather than a stated margin. CPU only.

    python scripts/57_equivalence.py [--delta 0.02] [--levels 3 5 6]

Every "no effect" in this paper is read off a bootstrap interval against a margin of
delta = 2 points fixed in PREREGISTRATION.md. That is the right margin but it was applied by
eye. This runs the two one-sided tests properly: a cell is EQUIVALENT when its 90% cluster
bootstrap interval lies entirely inside [-delta, +delta], which is the same as rejecting both
one-sided nulls at 5%. Cells whose interval is neither inside the margin nor excluding zero are
INCONCLUSIVE, and saying so is the point of the exercise.

Reads results/summary/sweep_L<level>.json (written by 50_sweep.py, which already stores the
per-seed values and the pooled cluster bootstrap) and writes results/summary/equivalence.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import RESULTS_DIR  # noqa: E402

CONTRASTS = ("lure_excess", "wlure_excess")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=float, default=0.02)
    ap.add_argument("--levels", type=int, nargs="+", default=[3, 5, 6])
    a = ap.parse_args()
    out = {"delta": a.delta, "cells": {}}
    print(f"equivalence bound delta = {100*a.delta:.0f} points; the interval must lie inside it\n")
    print(f"{'level':6s} {'model/regime':28s} {'contrast':20s} {'mean':>7s} {'interval':>18s}  verdict")
    for L in a.levels:
        p = RESULTS_DIR / "summary" / f"sweep_L{L}.json"
        if not p.exists():
            continue
        sw = json.loads(p.read_text())
        for key, rec in sorted(sw.items()):
            for name, c in sorted(rec.get("contrasts", {}).items()):
                if not name.startswith(CONTRASTS):
                    continue
                lo, hi = c["ci95"]
                inside = abs(lo) < a.delta and abs(hi) < a.delta
                claim = bool(c.get("claimable"))
                verdict = "EQUIVALENT" if inside else ("effect" if claim else "inconclusive")
                out["cells"][f"L{L}/{key}/{name}"] = {
                    "mean": c["pooled_mean"], "ci95": c["ci95"],
                    "equivalent": bool(inside), "claimable": claim, "verdict": verdict}
                print(f"L{L:<5d} {key:28s} {name:20s} {100*c['pooled_mean']:+6.2f} "
                      f"[{100*lo:+6.2f},{100*hi:+6.2f}]  {verdict}")
    cells = out["cells"]
    trace = {k: v for k, v in cells.items() if "/trace" in k and "trace_expr" not in k}
    out["summary"] = {
        "cells": len(cells),
        "equivalent": sum(v["equivalent"] for v in cells.values()),
        "with_effect": sum(v["claimable"] and not v["equivalent"] for v in cells.values()),
        "inconclusive": sum(not v["equivalent"] and not v["claimable"] for v in cells.values()),
        "trace_cells": len(trace),
        "trace_with_effect": sum(v["claimable"] and not v["equivalent"] for v in trace.values()),
    }
    print("\n" + json.dumps(out["summary"], indent=1))
    f = RESULTS_DIR / "summary" / "equivalence.json"
    f.write_text(json.dumps(out, indent=1))
    print(f"wrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
