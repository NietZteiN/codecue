#!/usr/bin/env python
"""E10: the randomised test. The trace contamination is so far observational — models that write
the lure also get the answer wrong, and we cannot tell which causes which. Here the instruction
is randomised over three variants that differ only in whether the model is TOLD to state the
value it computes, so any difference in written-lure rate is caused by the instruction.

    python scripts/13_force_value.py --model olmo2-7b-it --level 5 [--n-sets 500]

Variants (prose regime, chat template, otherwise identical):
    plain     "Think step by step, then finish with `Answer: <number>`."
    state     ... "State the value of every variable as you compute it."
    recompute ... "For each variable, ignore its name and compute its value from the code."

Prediction (pre-registered 2026-09-15, before this is run): `state` and `recompute` lower the
written-lure rate on the cell where the effect lives (a variable computed as len(xs) but named as
a sum) relative to `plain`, and `recompute` lowers it most. Writes behaviour under
runs/<model>/L<level>_force/<variant>/.
"""
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

VARIANTS = {
    "plain": "What does the call return? Think step by step, then finish with a line of the form `Answer: <number>`.",
    "state": "What does the call return? Think step by step, stating the value of every variable as you compute it, "
             "then finish with a line of the form `Answer: <number>`.",
    "recompute": "What does the call return? Think step by step. For each variable, ignore what its name suggests and "
                 "compute its value from the code, then finish with a line of the form `Answer: <number>`.",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--level", type=int, default=5)
    ap.add_argument("--n-sets", type=int, default=500); ap.add_argument("--batch-size", type=int, default=None)
    a = ap.parse_args()
    import codecue.prompts as P
    xs = read_jsonl(DATA_DIR / f"L{a.level}" / "test_sets.jsonl")
    # select sets by the role their MISLEADING name sits on. Filtering on `target in (None, "v1")`
    # instead keeps every set, because each set also contains neutral instances whose target is
    # None, and then drops all of their misleading instances (bug found 2026-09-15: the first run
    # produced only neutral groups).
    role = args_role = "v1"
    keep = set()
    for x in xs:
        if x.target == role and (len(keep) < a.n_sets or x.set_id in keep):
            keep.add(x.set_id)
    groups = defaultdict(list)
    for x in xs:
        if x.set_id in keep and x.target in (None, role):
            groups[x.condition if x.target is None else f"{x.condition}@{x.target}"].append(x)
    if not any("@" in g for g in groups):
        raise RuntimeError(f"no misleading groups selected for role {role}; groups={sorted(groups)}")
    m = model_entry(a.model); tok, model = load_model(m["hf_id"])
    bs = a.batch_size or m.get("batch_size", 16)
    for variant, text in VARIANTS.items():
        P.PROSE_INSTRUCTION = text                       # the only thing that differs
        for g, rows in groups.items():
            out = OUT_DIR / "runs" / a.model / f"L{a.level}_force" / variant / g
            if (out / "summary.json").exists():
                print(f"skip {variant} {g}"); continue
            s = run_group(tok, model, a.model, a.level, "prose", g, rows, out, bs)
            print(f"{a.model} L{a.level} force/{variant} {g}: n={s['n']} acc={s['accuracy']:.3f} "
                  f"lure={s['lure_rate']:.3f} wrote_true={s['wrote_true_rate']:.2f} {s['seconds']:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
