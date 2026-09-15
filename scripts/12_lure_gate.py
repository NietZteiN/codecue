#!/usr/bin/env python
"""E2b, the lure-table gate, v2 (2026-09-15). v1 asked for a free completion of `count = ` and
every model wrote `0` (a counter initialised to zero), which says nothing about which list
operation the name evokes. v2 SCORES candidate continuations: given `def f(xs):\n    <name> = `,
the log-probability of each family's expression (`len(xs)`, `sum(xs)`, `max(xs)`, `min(xs)`, and
for unary/binary families their forms over earlier variables). A name passes when its table
family is the argmax; the same scoring on neutral names gives the baseline preference.

    python scripts/12_lure_gate.py --model codellama-7b-it
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import RESULTS_DIR, model_entry  # noqa: E402
from codecue.lures import FAMILIES, NEUTRAL_NAMES  # noqa: E402
from codecue.models import load_model  # noqa: E402

CANDS = {"list": {"len": "len(xs)", "sum": "sum(xs)", "max": "max(xs)", "min": "min(xs)"},
         "unary": {"double": "a * 2", "half": "a // 2", "succ": "a + 1", "pred": "a - 1"},
         "binary": {"add": "a + b", "sub": "a - b", "mul": "a * b"}}
CTX = {"list": "def f(xs):\n    {n} = ", "unary": "def f(xs):\n    a = sum(xs)\n    {n} = ", "binary": "def f(xs):\n    a = sum(xs)\n    b = min(xs)\n    {n} = "}


@torch.no_grad()
def logprob(tok, model, prefix: str, cont: str) -> float:
    ids_p = tok(prefix, return_tensors="pt", add_special_tokens=True)["input_ids"]
    ids_c = tok(cont, return_tensors="pt", add_special_tokens=False)["input_ids"]
    ids = torch.cat([ids_p, ids_c], dim=1).to(model.device)
    lp = torch.log_softmax(model(input_ids=ids).logits.float(), dim=-1)[0]
    n = ids_p.shape[1]
    return float(sum(lp[n - 1 + i, ids[0, n + i]] for i in range(ids_c.shape[1])))


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); a = ap.parse_args()
    m = model_entry(a.model); tok, model = load_model(m["hf_id"])
    out = {}
    for fam in FAMILIES:
        cands = CANDS[fam.kind]
        for name in fam.names:
            scores = {k: logprob(tok, model, CTX[fam.kind].format(n=name), c) for k, c in cands.items()}
            best = max(scores, key=scores.get)
            out[name] = {"family": fam.key, "kind": fam.kind, "argmax": best, "pass": best == fam.key, "scores": scores}
            print(f"{name:10s} table={fam.key:7s} argmax={best:7s} {'PASS' if best == fam.key else 'fail'}  "
                  + " ".join(f"{k}:{v:6.1f}" for k, v in scores.items()))
    for name in NEUTRAL_NAMES[:6]:
        for kind, cands in CANDS.items():
            scores = {k: logprob(tok, model, CTX[kind].format(n=name), c) for k, c in cands.items()}
            out[f"{name}/{kind}"] = {"family": None, "kind": kind, "argmax": max(scores, key=scores.get), "scores": scores}
    p = RESULTS_DIR / "summary" / "lure_gate_v2.json"
    allm = json.loads(p.read_text()) if p.exists() else {}
    allm[a.model] = out; p.write_text(json.dumps(allm, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
