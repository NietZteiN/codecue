#!/usr/bin/env python
"""E2b, the lure-table gate: does the model's own prior agree with the table? For each lure name
the model completes `def f(xs):\n    <name> = ` greedily; the completion is scored by which
family's expression it starts with (len(xs), sum(xs), max(xs), min(xs), ...). Names on which the
panel agrees with the table below 80% are flagged in results/summary/lure_gate.json and dropped
from analysis (PREREGISTRATION.md).

    python scripts/12_lure_gate.py --model codellama-7b-it
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import RESULTS_DIR, model_entry  # noqa: E402
from codecue.lures import FAMILIES, FAMILY_OF_NAME, NEUTRAL_NAMES  # noqa: E402
from codecue.models import generate_free, load_model  # noqa: E402

PATTERNS = {"len": r"len\(", "sum": r"sum\(", "max": r"max\(", "min": r"min\(",
            "double": r"2\s*\*|\*\s*2", "half": r"//\s*2|/\s*2", "succ": r"\+\s*1\b", "pred": r"-\s*1\b",
            "add": r"\w+\s*\+\s*\w+", "sub": r"\w+\s*-\s*\w+", "mul": r"\w+\s*\*\s*\w+"}


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args()
    m = model_entry(a.model); tok, model = load_model(m["hf_id"])
    # several contexts per name, so a single lucky completion does not decide
    ctx = ["def f(xs):\n    {n} = ", "def g(xs):\n    a = max(xs)\n    {n} = ", "def h(xs):\n    total_len = len(xs)\n    {n} = ",
           "def k(xs):\n    s = sum(xs)\n    m = min(xs)\n    {n} = "]
    out = {}
    for fam in FAMILIES:
        for name in fam.names:
            prompts = [c.format(n=name) for c in ctx][: a.n]
            gens = generate_free(tok, model, prompts, 12, len(prompts), stop_at_blank_line=False)
            hits = {}
            for g in gens:
                first = g.split("\n", 1)[0]
                for key, pat in PATTERNS.items():
                    if re.search(pat, first):
                        hits[key] = hits.get(key, 0) + 1; break
            agree = hits.get(fam.key, 0) / len(gens)
            out[name] = {"family": fam.key, "agree": agree, "completions": [g.split("\n", 1)[0][:40] for g in gens]}
            print(f"{name:10s} table={fam.key:7s} agree={agree:.2f}  {out[name]['completions'][:2]}")
    for name in NEUTRAL_NAMES[:6]:
        gens = generate_free(tok, model, [c.format(n=name) for c in ctx], 12, 4, stop_at_blank_line=False)
        out[name] = {"family": None, "completions": [g.split("\n", 1)[0][:40] for g in gens]}
    p = RESULTS_DIR / "summary" / "lure_gate.json"
    allm = json.loads(p.read_text()) if p.exists() else {}
    allm[a.model] = out; p.write_text(json.dumps(allm, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
