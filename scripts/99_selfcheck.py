#!/usr/bin/env python
"""Standing validity checks over datasets and runs. Zero failures is the bar before any number
reaches the paper. Warnings are printed and counted but do not fail.

    python scripts/99_selfcheck.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import DATA_DIR, OUT_DIR, RESULTS_DIR  # noqa: E402
from codecue.generator import DIGITS, read_jsonl  # noqa: E402
from codecue.lures import LURE_NAMES, NEUTRAL_NAMES  # noqa: E402
from codecue.prompts import parse_regime  # noqa: E402

FAIL, WARN = [], []
def check(ok, msg, warn=False):
    (WARN if warn else FAIL).append(msg) if not ok else None
NAME_RE = re.compile(r"\b[A-Za-z_][A-Za-z_0-9]*\b")


def check_dataset(L: int):
    d = DATA_DIR / f"L{L}"
    if not (d / "test_sets.jsonl").exists(): return
    xs = read_jsonl(d / "test_sets.jsonl"); man = json.loads((d / "manifest.json").read_text())
    check(len(xs) == man["n_test_instances"], f"L{L}: manifest count {man['n_test_instances']} != {len(xs)} rows")
    sets = defaultdict(list)
    for x in xs: sets[x.set_id].append(x)
    for sid, s in sets.items():
        neu = [x for x in s if x.condition == "neutral"]
        check(len(neu) == 1, f"L{L} {sid}: {len(neu)} neutral twins"); 
        if not neu: continue
        neu = neu[0]
        for x in s:
            table = [n for n in x.names.values() if n in LURE_NAMES]
            check(len(table) == (0 if x.condition.startswith("neutral") else 1), f"L{L} {x.id}: {len(table)} table names (R1)")
            diff = [r for r in x.names if x.names[r] != neu.names[r]]
            check(len(diff) <= 1, f"L{L} {x.id}: twins differ in {len(diff)} names (R1)")
            check(x.values == neu.values and x.answer == neu.answer, f"L{L} {x.id}: renaming changed values")
            if x.lure is not None:
                check(x.lure in DIGITS and x.lure not in x.values.values() and x.lure not in x.xs, f"L{L} {x.id}: lure {x.lure} violates R2")
                consts = {int(c) for c in re.findall(r"\b\d+\b", x.program.rsplit("\n", 1)[0])}
                check(x.lure not in consts, f"L{L} {x.id}: lure equals a constant (R2)")
            idents = NAME_RE.findall(x.program)
            for n in LURE_NAMES:
                if n != x.lure_name: check(idents.count(n) == 0, f"L{L} {x.id}: table name {n} elsewhere (R3)")
            ns = {}; exec(x.program.rsplit("\n", 1)[0], {}, ns)
            check(ns["f"](x.xs) == x.answer, f"L{L} {x.id}: program does not return the stored answer (R4)")


def check_runs():
    for sf in sorted(OUT_DIR.glob("runs/*/L*/*/*/summary.json")):
        s = json.loads(sf.read_text()); tag = str(sf.parent.relative_to(OUT_DIR / "runs"))
        rows = [json.loads(l) for l in (sf.parent / "behavior.jsonl").open()]
        check(len(rows) == s["n"], f"{tag}: summary n={s['n']} rows={len(rows)}")
        acc = sum(r["correct"] for r in rows) / len(rows)
        check(abs(acc - s["accuracy"]) < 1e-6, f"{tag}: summary accuracy {s['accuracy']:.4f} != rows {acc:.4f} (stale summary)")
        check(s["unresolved"] <= 0.01 * s["n"], f"{tag}: {s['unresolved']} unresolved spans")
        pr = sum(r["pred"] is not None for r in rows) / len(rows)
        check(pr >= 0.97, f"{tag}: parse rate {pr:.3f}", warn=True)
        for r in rows[:200]:
            check(r["pred_is_lure"] == (r["lure"] is not None and r["pred"] == r["lure"]), f"{tag} {r['id']}: pred_is_lure inconsistent")
            check(r["correct"] == (r["pred"] == r["answer"]), f"{tag} {r['id']}: correct inconsistent")
        base = parse_regime(sf.parents[1].name)[0]
        if base == "direct":
            check(all(r["value_written"] is None for r in rows), f"{tag}: value_written set in the direct regime")
        # a group must have a neutral twin with the same set ids, or every contrast is undefined
        if "@" in sf.parent.name:
            neu = sf.parent.parent / "neutral" / "behavior.jsonl"
            if neu.exists():
                nsets = {json.loads(l)["set_id"] for l in neu.open()}
                miss = sum(r["set_id"] not in nsets for r in rows)
                check(miss == 0, f"{tag}: {miss} rows have no neutral twin")


def check_sweeps():
    for f in sorted((RESULTS_DIR / "summary").glob("sweep_L*.json")):
        sw = json.loads(f.read_text())
        for k, r in sw.items():
            for n, c in r["contrasts"].items():
                if c["claimable"]:
                    by = list(c["by_seed"].values())
                    check(len(by) >= 3 and (all(v > 0 for v in by) or all(v < 0 for v in by)) and (c["ci95"][0] > 0 or c["ci95"][1] < 0),
                          f"{f.name} {k} {n}: marked claimable but fails the rule")
                if len(r["seeds"]) < 3 and k.split("/")[1] != "prose":
                    check(False, f"{f.name} {k}: only {len(r['seeds'])} seeds", warn=True)


def main() -> int:
    for L in (1, 2, 3, 4, 5): check_dataset(L)
    check_runs(); check_sweeps()
    for m in FAIL: print("FAIL", m)
    for m in WARN[:15]: print("warn", m)
    print(f"\nchecks complete: {len(FAIL)} failures, {len(WARN)} warnings")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
