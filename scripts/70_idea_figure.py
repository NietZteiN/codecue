#!/usr/bin/env python
"""A real program and what the model writes under each demonstration format.

    python scripts/70_idea_figure.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import DATA_DIR, OUT_DIR, PROJECT_ROOT  # noqa: E402
from codecue.lures import FAMILY_OF_NAME  # noqa: E402

FIG = PROJECT_ROOT / "paper" / "figures"
RED, GREEN, GREY, BLUE = "#B5321F", "#157A55", "#5B6470", "#2B4A9E"


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
    if pick is None:
        raise RuntimeError("No paired length-to-sum example changes from wrong to correct")
    p, r, q = pick

    # Match manuscript width so labels retain their intended point size in the PDF.
    # The aggregate rates are already reported in the formats table.
    fig = plt.figure(figsize=(7.2, 3.1))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.15], wspace=0.25)
    axl, axv, axe = (fig.add_subplot(gs[i]) for i in range(3))
    for ax in (axl, axv, axe):
        ax.axis("off")

    # --- (a) the problem
    axl.set_title("(a) Same Python\nprogram", loc="left", fontsize=10.5)
    axl.text(0, 0.88, p["program"], family="monospace", fontsize=10.5,
             va="top", linespacing=1.3, transform=axl.transAxes)
    axl.text(0, 0.35, f"Correct length: {r['values']['v1']}", fontsize=10.5,
             color=GREEN, va="top", transform=axl.transAxes)
    axl.text(0, 0.22, f"Name suggests sum: {r['lure']}", fontsize=10.5,
             color=RED, va="top", transform=axl.transAxes)
    axl.text(0, 0.09, f"Correct final answer: {r['answer']}", fontsize=10.5,
             color=GREY, va="top", transform=axl.transAxes)

    # --- (b) what the model writes, under each demonstration format
    rows = [(axv, "(b) Examples show\nvalues only", r, RED),
            (axe, "(c) Examples show\noperation and value", q, GREEN)]
    for ax, title, record, color in rows:
        ax.set_title(title, loc="left", fontsize=10.5)
        ax.text(0, 0.88, "OLMo-2-7B writes:", fontsize=10.5,
                color=GREY, va="top", transform=ax.transAxes)
        assignments = record["generation"].split("\n")[0].strip().split(", ")
        if len(assignments) != 3:
            raise ValueError("Expected three complete generated assignments")
        for k, assignment in enumerate(assignments):
            ax.text(0, 0.68 - 0.15 * k, assignment, family="monospace", fontsize=10.0,
                    color=color, weight="bold" if k == 0 else "normal",
                    va="top", transform=ax.transAxes)
        mark = "wrong" if record["pred"] != r["answer"] else "correct"
        ax.text(0, 0.15, f"Final answer: {record['pred']}\n({mark})", fontsize=10.5,
                color=color, weight="bold", va="top", transform=ax.transAxes)
    fig.text(0.5, -0.015, "Same program and model; only the worked examples' format changes.",
             ha="center", fontsize=9.5, color=GREY)

    FIG.mkdir(parents=True, exist_ok=True)
    stem = FIG / "idea"
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=160, bbox_inches="tight")
    print(f"wrote {stem}.png using {r['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
