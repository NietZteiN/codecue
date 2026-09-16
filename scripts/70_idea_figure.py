#!/usr/bin/env python
"""The whole idea in one picture: a real program, what the model writes under each demonstration
format, and how much the format changes it across models.

    python scripts/70_idea_figure.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import DATA_DIR, OUT_DIR, PROJECT_ROOT  # noqa: E402
from codecue.lures import FAMILY_OF_NAME  # noqa: E402

FIG = PROJECT_ROOT / "paper" / "figures"
RED, GREEN, GREY, BLUE = "#B5321F", "#157A55", "#5B6470", "#2B4A9E"
EXAMPLE = "L5-5-v1-00012"          # chosen in the text below; any paired flip works


def main() -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    progs = {json.loads(l)["id"]: json.loads(l) for l in (DATA_DIR / "L5" / "test_sets.jsonl").open()}
    R = OUT_DIR / "runs"

    # --- pick a real instance the format change flips, on the model with the largest effect
    m = "olmo2-7b-it"
    a = {json.loads(l)["id"]: json.loads(l) for l in (R / m / "L5" / "trace" / "incongruent@v1" / "behavior.jsonl").open()}
    b = {json.loads(l)["id"]: json.loads(l) for l in (R / m / "L5" / "trace_expr" / "incongruent@v1" / "behavior.jsonl").open()}
    pick = None
    for i, r in a.items():
        p = progs[i]
        if p["stmts"][0]["op"] != "len" or FAMILY_OF_NAME[r["lure_name"]].key != "sum":
            continue
        q = b.get(i)
        if q and r["value_written"] == r["lure"] and not r["correct"] and q["correct"] and len(p["xs"]) == 2:
            pick = (p, r, q); break
    p, r, q = pick
    name = r["names"]["v1"]

    fig = plt.figure(figsize=(12.6, 4.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.25, 0.9], wspace=0.24)
    axl, axm, axr = (fig.add_subplot(gs[i]) for i in range(3))
    for ax in (axl, axm):
        ax.axis("off")

    # --- (a) the problem
    axl.set_title("(a)  one variable, two stories", loc="left", fontsize=11.5)
    axl.text(0, 0.90, p["program"], family="monospace", fontsize=10.5, va="top", transform=axl.transAxes)
    axl.text(0, 0.40, f"the code says   {name} = len(xs) = {r['values']['v1']}", family="monospace",
             fontsize=10.5, color=GREEN, va="top", transform=axl.transAxes)
    axl.text(0, 0.31, f"the name says   {name} = sum(xs) = {r['lure']}", family="monospace",
             fontsize=10.5, color=RED, va="top", transform=axl.transAxes)
    axl.text(0, 0.16, f"the call returns {r['answer']}", fontsize=10.5, color="0.3", va="top",
             style="italic", transform=axl.transAxes)

    # --- (b) what the model writes, under each demonstration format
    axm.set_title("(b)  what the model then writes", loc="left", fontsize=11.5)
    rows = [("worked examples write  “v = 3”", r["generation"].split("\n")[0].strip(), r["pred"], RED),
            ("worked examples write  “v = len(xs) = 3”", q["generation"].split("\n")[0].strip(), q["pred"], GREEN)]
    y = 0.86
    for lab, gen, pred, col in rows:
        axm.text(0, y, lab, fontsize=10, color="0.25", transform=axm.transAxes)
        axm.text(0, y - 0.11, gen[:64], family="monospace", fontsize=9.6, color=col, transform=axm.transAxes)
        mark = "wrong" if pred != r["answer"] else "correct"
        axm.text(0, y - 0.21, f"answers {pred}  ({mark})", fontsize=10, color=col, weight="bold", transform=axm.transAxes)
        y -= 0.42
    axm.text(0, 0.03, "Same problem, same model, same three worked examples.\n"
                      "Only the format of those examples differs.", fontsize=9.4, color="0.4",
             style="italic", transform=axm.transAxes)

    # --- (c) the effect across models
    models = [("olmo2-7b-it", "OLMo-2-7B"), ("llama32-3b-it", "Llama-3.2-3B"), ("llama31-8b-it", "Llama-3.1-8B")]
    plain, expr = [], []
    for key, _ in models:
        pa = pb = n = 0
        for sfx in ("", "_s11", "_s13"):
            A = [json.loads(l) for l in (R / key / "L5" / f"trace{sfx}" / "incongruent@v1" / "behavior.jsonl").open()]
            B = {json.loads(l)["id"]: json.loads(l) for l in (R / key / "L5" / f"trace_expr{sfx}" / "incongruent@v1" / "behavior.jsonl").open()}
            for rr in A:
                pp = progs[rr["id"]]
                if pp["stmts"][0]["op"] != "len" or FAMILY_OF_NAME[rr["lure_name"]].key != "sum" or rr["id"] not in B:
                    continue
                n += 1; pa += rr["value_written"] == rr["lure"]; pb += B[rr["id"]]["value_written"] == B[rr["id"]]["lure"]
        plain.append(100 * pa / n); expr.append(100 * pb / n)
    y = np.arange(len(models))
    axr.barh(y + 0.19, plain, 0.36, color=RED, label="“v = 3”")
    axr.barh(y - 0.19, expr, 0.36, color=GREEN, label="“v = len(xs) = 3”")
    for i, (pv, ev) in enumerate(zip(plain, expr)):
        axr.text(pv + 1.5, i + 0.19, f"{pv:.0f}%", va="center", fontsize=9.5, color=RED)
        axr.text(ev + 1.5, i - 0.19, f"{ev:.0f}%", va="center", fontsize=9.5, color=GREEN)
    axr.set_yticks(y); axr.set_yticklabels([lab for _, lab in models], fontsize=10)
    axr.invert_yaxis(); axr.set_xlim(0, max(plain) * 1.25)
    axr.set_xlabel("how often the model writes the value\nthe NAME implies instead of the code's", fontsize=9.6)
    axr.set_title("(c)  across models, 3 example sets", loc="left", fontsize=11.5)
    axr.legend(frameon=False, fontsize=9.2, loc="lower right")
    axr.grid(axis="x", color="0.92", lw=0.7)

    FIG.mkdir(parents=True, exist_ok=True)
    stem = FIG / "idea"
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=160, bbox_inches="tight")
    print(f"wrote {stem}.png using {r['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
