#!/usr/bin/env python
"""The mechanism in one figure: where patching from the neutral twin removes the lure write, by
layer, at the name's tokens (origin) and at the decision token (destination), plus what a probe
reads at the decision token. Two models with token-aligned name pairs.

    python scripts/71_mechanism_figure.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import OUT_DIR, PROJECT_ROOT  # noqa: E402

FIG = PROJECT_ROOT / "paper" / "figures"
RED, GREEN, BLUE, GREY = "#B5321F", "#157A55", "#2B4A9E", "#5B6470"
MODELS = [("olmo2-7b-it", "OLMo-2-7B"), ("llama32-3b-it", "Llama-3.2-3B")]


def main() -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, len(MODELS), figsize=(11.5, 4.0), sharey=True)
    for ax, (key, label) in zip(axes, MODELS):
        R = OUT_DIR / "runs" / key / "L5" / "patch"
        name = json.loads((R / "main_name.json").read_text()); pre = json.loads((R / "main_pre.json").read_text())
        nL = name["n_layers"]; L = np.arange(nL)
        r_name = [100 * (name["summary"][f"L{l}"]["lure_removed"] or 0) for l in L]
        r_pre = [100 * (pre["summary"][f"L{l}"]["lure_removed"] or 0) for l in L]
        d_name = [100 * (name["summary"][f"L{l}"]["damage"] or 0) for l in L]
        # probe: reads the code's value at the decision token, best layer per layer index
        pj = json.loads((OUT_DIR / "probes" / key / "L5" / "trace" / "v1.json").read_text())
        acc = {}
        for r in pj["results"]:
            if r["position"] == "pre@v1":
                ev = r["eval"].get("incongruent@v1", {}).get("accuracy")
                if ev is not None:
                    acc.setdefault(r["layer"], []).append(ev[0] if isinstance(ev, list) else ev)
        pl = sorted(acc); pa = [100 * np.mean(acc[l]) for l in pl]
        ax.plot(L, r_name, "-o", ms=3.5, lw=2, color=RED, label="patch the NAME's tokens")
        ax.plot(L, r_pre, "-s", ms=3.5, lw=2, color=BLUE, label="patch the DECISION token")
        ax.plot(pl, pa, "--", lw=1.6, color=GREEN, label="probe reads the code's value\nat the decision token")
        ax.fill_between(L, 0, d_name, color=GREY, alpha=0.18, lw=0, label="damage from the name patch")
        ax.set_xlabel("layer patched (or probed)"); ax.set_title(label, loc="left", fontsize=11)
        ax.set_ylim(0, 104); ax.set_xlim(-0.5, nL - 0.5); ax.grid(axis="y", color="0.92", lw=0.7)
    axes[0].set_ylabel("% of lure writes removed  /  probe accuracy")
    axes[0].legend(loc="center right", frameon=False, fontsize=8.6)
    fig.suptitle("Where the name's influence lives: it starts in the name's tokens (red falls with depth) and "
                 "arrives at the decision token mid-network (blue rises), where the code's value is already "
                 "decodable (green)", x=0.01, ha="left", fontsize=9.6)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "mechanism.pdf", bbox_inches="tight"); fig.savefig(FIG / "mechanism.png", dpi=160, bbox_inches="tight")
    print("wrote", FIG / "mechanism.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
