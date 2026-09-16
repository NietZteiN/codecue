#!/usr/bin/env python
"""Cache hidden states over the gold trace and train neutral-only probes for one model.

    python scripts/30_cache_and_probe.py --model olmo2-7b-it --level 5 --role v1

Trains on neutral programs, evaluates on every condition. The question the paper needs answered:
at `pre@v1`, one token before the trace writes the variable's value, does the state hold the
code's value or the value the name implies?
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.cache import cache_group  # noqa: E402
from codecue.config import DATA_DIR, OUT_DIR, model_entry  # noqa: E402
from codecue.generator import read_jsonl  # noqa: E402
from codecue.lures import FAMILY_OF_NAME  # noqa: E402
from codecue.models import load_model  # noqa: E402
from codecue.probes import train_and_eval  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--level", type=int, default=5)
    ap.add_argument("--role", default="v1"); ap.add_argument("--regime", default="trace")
    ap.add_argument("--n-train", type=int, default=3000); ap.add_argument("--n-test", type=int, default=1000)
    ap.add_argument("--cell-only", action="store_true", help="restrict tests to the len->sum cell")
    ap.add_argument("--batch-size", type=int, default=None); ap.add_argument("--layer-stride", type=int, default=2)
    a = ap.parse_args()
    xs = read_jsonl(DATA_DIR / f"L{a.level}" / "test_sets.jsonl")
    sel = [x for x in xs if x.target in (None, a.role)]
    # the probe TRAINS on every neutral program (it learns "the value of v1" in general, as in the
    # arithmetic paper); `--cell-only` restricts only the TEST groups to the affected cell
    in_cell = lambda x: x.stmts[0]["op"] == "len" and (x.lure_name is None or FAMILY_OF_NAME[x.lure_name].key == "sum")
    groups, train_pool = defaultdict(list), []
    for x in sel:
        if x.condition == "neutral":
            train_pool.append(x)
        if not a.cell_only or in_cell(x):
            groups[x.condition if x.target is None else f"{x.condition}@{x.target}"].append(x)
    m = model_entry(a.model); tok, model = load_model(m["hf_id"])
    bs = a.batch_size or max(4, m.get("batch_size", 16) // 2)
    root = OUT_DIR / "probecache" / a.model / f"L{a.level}" / a.regime
    # train on neutral, test on everything (neutral included, as the accuracy reference)
    tr = train_pool[: a.n_train]
    cache_group(tok, model, tr, a.role, a.regime, a.level, root / "train_neutral", bs, a.layer_stride)
    print(f"cached train_neutral: {len(tr)}", flush=True)
    tests = {}
    for g in ("neutral", "congruent@" + a.role, "incongruent@" + a.role, "incongruent_alt@" + a.role):
        rows = groups.get(g, [])[: a.n_test]
        if not rows: continue
        d = root / g
        cache_group(tok, model, rows, a.role, a.regime, a.level, d, bs, a.layer_stride)
        tests[g] = d
        print(f"cached {g}: {len(rows)}", flush=True)
    del model
    import torch; torch.cuda.empty_cache()
    out = OUT_DIR / "probes" / a.model / f"L{a.level}" / a.regime / f"{a.role}.json"
    train_and_eval(root / "train_neutral", tests, a.role, out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
