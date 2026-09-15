#!/usr/bin/env python
"""Behaviour for one model: every regime × every group of a level.

    python scripts/20_run_model.py --model codellama-7b-it --level 3 --regimes direct trace prose codechain [--n-sets 200]

Groups: neutral, neutral_alt@r, congruent@r, incongruent@r, incongruent_alt@r (and irrelevant@v4
at level 4) for each target role r. Skips a group whose summary.json exists (resumable)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import DATA_DIR, OUT_DIR, model_entry  # noqa: E402
from codecue.generator import read_jsonl  # noqa: E402
from codecue.models import load_model  # noqa: E402
from codecue.runner import run_group  # noqa: E402


def group_key(x) -> str:
    return x.condition if x.target is None else f"{x.condition}@{x.target}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--level", type=int, default=3)
    ap.add_argument("--regimes", nargs="+", default=["direct", "trace", "prose", "codechain"])
    ap.add_argument("--groups", nargs="+", default=None)
    ap.add_argument("--n-sets", type=int, default=None, help="limit to the first N matched sets per target (pilot)")
    ap.add_argument("--batch-size", type=int, default=None); ap.add_argument("--no-chat", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    m = model_entry(a.model)
    d = DATA_DIR / f"L{a.level}"
    man = json.loads((d / "manifest.json").read_text())
    xs = read_jsonl(d / "test_sets.jsonl")
    if a.n_sets:
        keep = defaultdict(set)
        for x in xs:
            if len(keep[x.target or "q"]) < a.n_sets or x.set_id in keep[x.target or "q"]:
                keep[x.target or "q"].add(x.set_id)
        allowed = set().union(*keep.values())
        xs = [x for x in xs if x.set_id in allowed]
    groups = defaultdict(list)
    for x in xs:
        groups[group_key(x)].append(x)
    if a.groups:
        groups = {g: groups[g] for g in a.groups}
    tok, model = load_model(m["hf_id"])
    bs = a.batch_size or m.get("batch_size", 16)
    tag = f"_n{a.n_sets}" if a.n_sets else ""
    for regime in a.regimes:
        for g, rows in groups.items():
            out = OUT_DIR / "runs" / a.model / f"L{a.level}{tag}" / regime / g
            if (out / "summary.json").exists() and not a.overwrite:
                print(f"skip {a.model} L{a.level} {regime} {g} (done)"); continue
            s = run_group(tok, model, a.model, a.level, regime, g, rows, out, bs, use_chat=not a.no_chat)
            print(f"{a.model} L{a.level}{tag} {regime} {g}: n={s['n']} acc={s['accuracy']:.3f} lure={s['lure_rate']:.3f} "
                  f"parsed={s['parse_rate']:.2f} wrote_true={s['wrote_true_rate']:.2f} {s['seconds']:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
