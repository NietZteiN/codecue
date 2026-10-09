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

    # Layout reads left to right: task, conflict, two observed responses.
    fig = plt.figure(figsize=(7.2, 3.45))
    fig.text(.02, .96, "Examples with code expressions change the reported values",
             fontsize=12, weight="bold", va="top")
    fig.text(.02, .88, "Task: write each assigned value, then the function's final answer.", fontsize=10)
    axes = [fig.add_axes(box) for box in
            [(.02, .10, .31, .67), (.36, .10, .27, .67), (.66, .10, .33, .67)]]
    for ax in axes:
        ax.axis("off")
    axl, axv, axe = axes
    axl.text(0, 1, "Same program and input", weight="bold", fontsize=10, va="top")
    axl.text(0, .87, p["program"], family="monospace", fontsize=9,
             va="top", linespacing=1.25)
    axl.text(0, .31, "len counts items: 2", color=GREEN, fontsize=10, weight="bold")
    axl.text(0, .18, "sum_all suggests 5 + 3 = 8", color=RED, fontsize=9)
    axl.text(0, .05, "Correct final answer: 9", fontsize=10)
    for ax, title, fmt, record, color in [
        (axv, "Examples show values", "name = value", r, RED),
        (axe, "Examples include expressions", "name = expression = value", q, GREEN),
    ]:
        ax.text(0, 1, title, weight="bold", fontsize=10, va="top")
        ax.text(0, .87, fmt, fontsize=8.5, family="monospace", color=GREY, va="top")
        ax.text(0, .73, "Actual OLMo-2-7B output:", fontsize=9, color=GREY)
        assignments = record["generation"].split("\n")[0].strip().split(", ")
        assert len(assignments) == 3
        for j, assignment in enumerate(assignments):
            # Only line breaks change; preserve all observed assignment text.
            if record is q and j > 0:
                lhs, value = assignment.rsplit(" = ", 1)
                assignment = lhs + "\n     = " + value
            ax.text(0, .61 - j*.18, assignment, family="monospace", fontsize=8.8,
                    color=color if j == 0 else "#252525", va="top", linespacing=1.1)
        ax.text(0, .02, f"Answer: {record['pred']}  ({'correct' if record['correct'] else 'wrong'})",
                color=color, fontsize=10, weight="bold")
    fig.text(.02, .025, "Only the worked-example format changes; the model solves the same program.",
             fontsize=9, color=GREY)

    FIG.mkdir(parents=True, exist_ok=True)
    stem = FIG / "idea"
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=160, bbox_inches="tight")
    (FIG / "idea_data.json").write_text(json.dumps({
        "id": r["id"], "program": p["program"], "correct_values": r["values"],
        "correct_answer": r["answer"], "name_suggested_digit": r["lure"],
        "values_only_generation": r["generation"],
        "operation_and_value_generation": q["generation"],
    }, indent=2) + "\n")
    print(f"wrote {stem}.png using {r['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
