#!/usr/bin/env python
"""E7: build the code-generation dataset (PLAN.md 3.3). CPU, seconds.

    python scripts/16_build_gentask.py [--n 300] [--seed 7]

Writes data/gentask/sets.jsonl (three instances per matched set: neutral, congruent,
incongruent) and data/gentask/manifest.json with a content hash the runner checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import DATA_DIR  # noqa: E402
from codecue.gentask import CONDITIONS, render, sample_sets  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    sets = sample_sets(a.n, seed=a.seed)
    d = DATA_DIR / "gentask"
    d.mkdir(parents=True, exist_ok=True)
    lines = [x.to_json() for g in sets for x in g]
    (d / "sets.jsonl").write_text("\n".join(lines) + "\n")
    h = hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]

    # validity assertions, the same shape as the rest of the project
    for g in sets:
        assert len(g) == len(CONDITIONS), "a set must hold one instance per condition"
        # Compare the sets by re-rendering each member under one placeholder name. A plain
        # string replace would also hit the letter inside `multiplied`, which is why the neutral
        # names are single letters and this check is done structurally.
        canon = {render("@", x.op, x.transform) for x in g}
        assert len(canon) == 1, "twins differ by more than the identifier"
        inc = [x for x in g if x.condition == "incongruent"][0]
        assert inc.lure is not None and all(c != l for c, l in zip(inc.correct, inc.lure)), "lure equals correct"
    (d / "manifest.json").write_text(json.dumps({
        "n_sets": len(sets), "n_instances": len(lines), "seed": a.seed, "content_sha": h,
        "conditions": list(CONDITIONS)}, indent=1))
    ops = {}
    for g in sets:
        inc = [x for x in g if x.condition == "incongruent"][0]
        ops[f"{inc.op}->{inc.lure_op}"] = ops.get(f"{inc.op}->{inc.lure_op}", 0) + 1
    print(f"{len(sets)} sets, {len(lines)} instances, sha {h}")
    print("  (code op -> name's implied op):", dict(sorted(ops.items(), key=lambda kv: -kv[1])))
    print(f"  wrote {d/'sets.jsonl'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
