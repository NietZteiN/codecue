#!/usr/bin/env python
"""Separate activation-replacement effects, digit prediction and disruption by layer.
Two models with token-aligned name pairs; each outcome gets its own axis.

    python scripts/71_mechanism_figure.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import OUT_DIR, PROJECT_ROOT  # noqa: E402
from codecue.reporting import probe_output  # noqa: E402

FIG = PROJECT_ROOT / "paper" / "figures"
RED, GREEN, BLUE, GREY = "#B5321F", "#157A55", "#2B4A9E", "#5B6470"
MODELS = [("olmo2-7b-it", "OLMo-2-7B"), ("llama32-3b-it", "Llama-3.2-3B")]


def main() -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(len(MODELS), 3, figsize=(7.2, 4.3))
    fig.subplots_adjust(left=0.095, right=0.99, top=0.78, bottom=0.24,
                        wspace=0.34, hspace=0.38)
    fig.text(.02, .97, "Replacing internal activity can change wrong sum writes", fontsize=12, weight="bold", va="top")
    headers = ["(a) Incorrect sum writes\nremoved (%)", "(b) Correct digit read (%)\nAll held-out misleading names",
               "(c) Correct writes\nmade wrong (%)"]
    for ax, title in zip(axes[0], headers):
        box = ax.get_position()
        fig.text((box.x0 + box.x1) / 2, 0.83, title, ha="center", fontsize=10)
    for row, (key, label) in enumerate(MODELS):
        ax_patch, ax_probe, ax_damage = axes[row]
        R = OUT_DIR / "runs" / key / "L5" / "patch"
        name = json.loads((R / "main_name.json").read_text()); pre = json.loads((R / "main_pre.json").read_text())
        nL = name["n_layers"]; L = np.arange(nL)
        r_name = [100 * (name["summary"][f"L{l}"]["lure_removed"] or 0) for l in L]
        r_pre = [100 * (pre["summary"][f"L{l}"]["lure_removed"] or 0) for l in L]
        d_name = [100 * (name["summary"][f"L{l}"]["damage"] or 0) for l in L]
        # probe: reads the code's value at the decision token, best layer per layer index
        pj = json.loads(probe_output(key).read_text())
        acc = {}
        for r in pj["results"]:
            if r["position"] == "pre@v1":
                ev = r["eval"].get("incongruent@v1", {}).get("accuracy")
                if ev is not None:
                    acc.setdefault(r["layer"], []).append(ev[0] if isinstance(ev, list) else ev)
        pl = sorted(acc); pa = [100 * np.mean(acc[l]) for l in pl]
        ax_patch.plot(L, r_name, "-o", ms=2.5, lw=1.7, color=RED,
                      label="Replace activity at the name")
        ax_patch.plot(L, r_pre, "-s", ms=2.5, lw=1.7, color=BLUE,
                      label="Replace activity before the value")
        ax_probe.plot(pl, pa, "--", lw=1.7, color=GREEN)
        ax_damage.plot(L, d_name, "-", lw=1.7, color=GREY)
        ax_patch.set_ylim(0, 104); ax_probe.set_ylim(0, 104)
        ax_damage.set_ylim(0, 5); ax_damage.set_yticks([0, 2, 4])
        for ax in axes[row]:
            ax.set_xlim(-0.5, nL - 0.5)
            ax.set_xticks(np.arange(0, nL, 10))
            ax.grid(axis="y", color="0.92", lw=0.7)
            ax.tick_params(labelsize=8.5)
            if row == len(MODELS) - 1:
                ax.set_xlabel("Model layer (early → late)", fontsize=8.5)
        box = ax_patch.get_position()
        fig.text(0.012, (box.y0 + box.y1) / 2, label, rotation=90,
                 ha="center", va="center", fontsize=10)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=9,
               bbox_to_anchor=(0.54, 0.05))
    fig.text(.02, .02, "Replacement uses the ordinary-name twin; removing a sum write can produce another wrong value.", fontsize=8.5)
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "mechanism.pdf", bbox_inches="tight"); fig.savefig(FIG / "mechanism.png", dpi=160, bbox_inches="tight")
    print("wrote", FIG / "mechanism.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
