#!/usr/bin/env python
"""Pooled contrasts over demonstration seeds (7, 11, 13) at one level, every model with runs.

Per (model, regime base, target) against the matched neutral twin, per seed and pooled:
  acc_int        accuracy interference: incongruent minus neutral accuracy
  lure_excess    answer is the lure, minus the twin's rate of that digit
  wlure_excess   (trace/prose) the chain WRITES the lure as the target's value, minus the twin's rate
  facilitation   congruent minus neutral accuracy
Claim rule as in the arithmetic paper: same sign in every seed and a cluster bootstrap (sets)
over the pooled paired differences excluding zero. Writes results/summary/sweep_L<k>.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import OUT_DIR, RESULTS_DIR, load_config  # noqa: E402

SEEDS = (7, 11, 13)


def boot(d: np.ndarray, sets: np.ndarray, n=2000, seed=0):
    rng = np.random.default_rng(seed); u = np.unique(sets); idx = {s: np.where(sets == s)[0] for s in u}
    means = []
    for _ in range(n):
        pick = rng.choice(u, len(u), replace=True); means.append(np.mean(np.concatenate([d[idx[s]] for s in pick])))
    return float(d.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def rows_of(p: Path):
    return {r["set_id"]: r for r in (json.loads(l) for l in p.open())} if p.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--level", type=int, default=3); ap.add_argument("--tag", default="")
    a = ap.parse_args()
    out = {}
    for m in load_config("models.yaml")["models"]:
        base = OUT_DIR / "runs" / m / f"L{a.level}{a.tag}"
        if not base.exists(): continue
        for reg in ("direct", "trace", "prose"):
            per = {}
            for sd in SEEDS:
                d = base / (reg if sd == 7 else f"{reg}_s{sd}")
                neu = rows_of(d / "neutral" / "behavior.jsonl")
                if not neu: continue
                per[sd] = {"neutral": neu}
                for g in d.glob("*@*"):
                    per[sd][g.name] = rows_of(g / "behavior.jsonl")
            if not per: continue
            targets = sorted({k.split("@")[1] for sd in per for k in per[sd] if "@" in k})
            rec = {"seeds": sorted(per), "n_neutral": {sd: len(per[sd]["neutral"]) for sd in per},
                   "acc": {sd: float(np.mean([r["correct"] for r in per[sd]["neutral"].values()])) for sd in per}, "contrasts": {}}
            for t in targets:
                for name, fn in (("acc_int", lambda r, n: (r["correct"] - n["correct"])),
                                 ("facilitation", None),
                                 ("lure_excess", lambda r, n: (r["pred_is_lure"] - (n["pred"] == r["lure"]))),
                                 ("wlure_excess", lambda r, n: ((r["value_written"] == r["lure"])
                                                                - (n.get("values_written", {}).get(r["target"]) == r["lure"])))):
                    if name == "wlure_excess" and reg == "direct": continue
                    cond = "congruent" if name == "facilitation" else "incongruent"
                    if name == "facilitation": fn = lambda r, n: (r["correct"] - n["correct"])
                    ds, ss, by = [], [], {}
                    for sd in per:
                        inc = per[sd].get(f"{cond}@{t}"); neu = per[sd]["neutral"]
                        if not inc: continue
                        dd = [float(fn(r, neu[s])) for s, r in inc.items() if s in neu]
                        if dd: by[sd] = float(np.mean(dd)); ds += dd; ss += [s for s in inc if s in neu]
                    if not ds: continue
                    mean, lo, hi = boot(np.array(ds), np.array(ss))
                    sign = all(v > 0 for v in by.values()) or all(v < 0 for v in by.values())
                    rec["contrasts"][f"{name}@{t}"] = {"pooled_mean": mean, "ci95": [lo, hi], "by_seed": by,
                                                       "claimable": len(by) >= 3 and sign and (lo > 0 or hi < 0)}
            out[f"{m}/{reg}"] = rec
            print(f"=== L{a.level} {m} {reg}: seeds {rec['seeds']}  neutral acc " + " ".join(f"{sd}:{100*v:.1f}" for sd, v in rec["acc"].items()))
            for k, c in rec["contrasts"].items():
                print(f"   {k:18s} {100*c['pooled_mean']:+6.2f} [{100*c['ci95'][0]:+.2f},{100*c['ci95'][1]:+.2f}] by seed "
                      + " ".join(f"{sd}:{100*v:+.1f}" for sd, v in c["by_seed"].items()) + ("   CLAIMABLE" if c["claimable"] else ""))
    (RESULTS_DIR / "summary").mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "summary" / f"sweep_L{a.level}{a.tag}.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
