#!/usr/bin/env python
"""Every number the paper will cite, computed from results on disk and written to
paper/numbers.tex as \\NUM{key} definitions. Nothing in the paper is typed by hand.

    python scripts/51_numbers.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import DATA_DIR, OUT_DIR, PROJECT_ROOT, RESULTS_DIR, load_config  # noqa: E402
from codecue.lures import FAMILY_OF_NAME  # noqa: E402

SHORT = {"olmo2-7b-it": "olmo7", "llama32-3b-it": "llama3", "llama31-8b-it": "llama8", "codellama-7b-it": "codellama",
         "codegemma-7b-it": "codegemma", "gemma3-4b-it": "gemma4", "olmo2-1b-it": "olmo1"}
N = {}


def pct(x, signed=False, d=1):
    return (f"{100*x:+.{d}f}" if signed else f"{100*x:.{d}f}")


def main() -> int:
    models = list(load_config("models.yaml")["models"])
    with_runs = [m for m in models if (OUT_DIR / "runs" / m / "L3").exists()]
    N["n-models"] = {6: "six", 7: "seven", 8: "eight"}.get(len(with_runs), str(len(with_runs)))
    # ---- behaviour sweeps
    for L in (3, 5):
        f = RESULTS_DIR / "summary" / f"sweep_L{L}.json"
        if not f.exists(): continue
        sw = json.loads(f.read_text())
        for m in with_runs:
            for reg in ("direct", "trace"):
                r = sw.get(f"{m}/{reg}")
                if not r: continue
                for k, c in r["contrasts"].items():
                    key = f"{SHORT[m]}-L{L}-{reg}-{k.replace('@', '-').replace('_', '')}"
                    N[key] = pct(c["pooled_mean"], True); N[key + "-lo"] = pct(c["ci95"][0], True); N[key + "-hi"] = pct(c["ci95"][1], True)
                    N[key + "-claim"] = "yes" if c["claimable"] else "no"
                N[f"{SHORT[m]}-L{L}-{reg}-acc"] = pct(np.mean(list(r["acc"].values())))
        # direct lure excess: how many models claimable on at least one target
        dl = [any(sw[f"{m}/direct"]["contrasts"].get(f"lure_excess@{t}", {}).get("claimable") for t in ("v1", "v3"))
              for m in with_runs if f"{m}/direct" in sw]
        N[f"direct-lure-claimable-L{L}"] = str(sum(dl)); N[f"direct-cells-L{L}"] = str(len(dl))
        vals = [sw[f"{m}/direct"]["contrasts"][f"lure_excess@{t}"]["pooled_mean"] for m in with_runs if f"{m}/direct" in sw
                for t in ("v1", "v3") if f"lure_excess@{t}" in sw[f"{m}/direct"]["contrasts"]]
        N[f"direct-lure-min-L{L}"] = pct(min(vals), True); N[f"direct-lure-max-L{L}"] = pct(max(vals), True)
    # ---- the cell: len -> sum (and max -> sum), written-lure excess, L5, per model and per format
    #      keys: cell-<m>-{wrote,excess,lo,hi,n} (trace), cell-<m>-<reg>-{wrote,excess,lo,hi,n,claim,acc} for repl/comment/trace_expr,
    #      cell34-{len,max}-{excess,lo,hi,n} and cell34-acc for CodeLlama-34B (L5 only, so outside with_runs)
    progs = {json.loads(l)["id"]: json.loads(l) for l in (DATA_DIR / "L5" / "test_sets.jsonl").open()}
    rng = np.random.default_rng(0)

    def cell(m, reg, op, fam="sum"):
        """paired per-set (hit - twin_hit) for the (op -> fam) cell at v1, plus by-seed means and neutral accuracy"""
        deltas, by_seed, acc = [], {}, []
        for sfx in ("", "_s11", "_s13"):
            gi = OUT_DIR / "runs" / m / "L5" / f"{reg}{sfx}" / "incongruent@v1" / "behavior.jsonl"
            gn = OUT_DIR / "runs" / m / "L5" / f"{reg}{sfx}" / "neutral" / "behavior.jsonl"
            if not gi.exists() or not gn.exists(): continue
            neu = {json.loads(l)["set_id"]: json.loads(l) for l in gn.open()}
            acc += [r["correct"] for r in neu.values()]; sd = []
            for l in gi.open():
                r = json.loads(l); t = neu.get(r["set_id"])
                if not t or progs[r["id"]]["stmts"][0]["op"] != op or FAMILY_OF_NAME[r["lure_name"]].key != fam: continue
                sd.append((int(r["value_written"] == r["lure"]), int(t.get("values_written", {}).get("v1") == r["lure"])))
            if sd: by_seed[sfx or "_s7"] = sd; deltas += sd
        if not deltas: return None
        d = np.array(deltas); ex = d[:, 0] - d[:, 1]
        boot = [rng.choice(ex, len(ex)).mean() for _ in range(2000)]
        seeds = [np.mean([a - b for a, b in v]) for v in by_seed.values()]
        lo, hi = np.percentile(boot, 2.5), np.percentile(boot, 97.5)
        claim = len(seeds) >= 3 and (all(x > 0 for x in seeds) or all(x < 0 for x in seeds)) and (lo > 0 or hi < 0)
        return dict(wrote=d[:, 0].mean(), excess=ex.mean(), lo=lo, hi=hi, n=len(ex), claim=claim, acc=np.mean(acc))

    for m in with_runs:
        for reg in ("trace", "repl", "comment", "trace_expr"):
            c = cell(m, reg, "len")
            if c is None: continue
            pre = f"cell-{SHORT[m]}" if reg == "trace" else f"cell-{SHORT[m]}-{reg.replace('_', '')}"
            N[f"{pre}-wrote"] = pct(c["wrote"], d=0); N[f"{pre}-excess"] = pct(c["excess"], True); N[f"{pre}-n"] = str(c["n"])
            N[f"{pre}-lo"] = pct(c["lo"], True); N[f"{pre}-hi"] = pct(c["hi"], True); N[f"{pre}-claim"] = "yes" if c["claim"] else "no"
            N[f"{pre}-acc"] = pct(c["acc"])
            if reg != "trace":
                t = cell(m, "trace", "len")
                N[f"{pre}-ratio"] = f"{t['excess'] / c['excess']:.0f}" if c["excess"] > 0.005 else "--"
    if (OUT_DIR / "runs" / "codellama-34b-it" / "L5").exists():
        for op in ("len", "max"):
            c = cell("codellama-34b-it", "trace", op)
            if c is None: continue
            N[f"cell34-{op}-excess"] = pct(c["excess"], True); N[f"cell34-{op}-lo"] = pct(c["lo"], True); N[f"cell34-{op}-hi"] = pct(c["hi"], True)
            N[f"cell34-{op}-n"] = str(c["n"]); N[f"cell34-{op}-claim"] = "yes" if c["claim"] else "no"; N["cell34-acc"] = pct(c["acc"])
    # ---- R3b: level 6, unary middle step, overall written-lure excess on v2 (trace, 3 seeds)
    f6 = RESULTS_DIR / "summary" / "sweep_L6.json"
    if f6.exists():
        sw6 = json.loads(f6.read_text()); claim6 = []
        for m in with_runs:
            r = sw6.get(f"{m}/trace")
            if not r or "wlure_excess@v2" not in r["contrasts"]: continue
            c = r["contrasts"]["wlure_excess@v2"]
            N[f"l6-{SHORT[m]}-excess"] = pct(c["pooled_mean"], True); N[f"l6-{SHORT[m]}-lo"] = pct(c["ci95"][0], True)
            N[f"l6-{SHORT[m]}-hi"] = pct(c["ci95"][1], True); N[f"l6-{SHORT[m]}-acc"] = pct(np.mean(list(r["acc"].values())))
            claim6.append(c["pooled_mean"] if c["claimable"] else None)
        N["l6-models"] = str(len(claim6)); N["l6-max-excess"] = pct(max(abs(sw6[f"{m}/trace"]["contrasts"]["wlure_excess@v2"]["pooled_mean"])
                                                                        for m in with_runs if f"{m}/trace" in sw6 and m != "olmo2-1b-it"), True)
    # ---- E10b: trace vs trace_expr, paired, the cell
    for m in ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it"):
        pa = pb = n = 0
        for sfx in ("", "_s11", "_s13"):
            A = OUT_DIR / "runs" / m / "L5" / f"trace{sfx}" / "incongruent@v1" / "behavior.jsonl"
            B = OUT_DIR / "runs" / m / "L5" / f"trace_expr{sfx}" / "incongruent@v1" / "behavior.jsonl"
            if not A.exists() or not B.exists(): continue
            b = {json.loads(l)["id"]: json.loads(l) for l in B.open()}
            for l in A.open():
                r = json.loads(l); q = b.get(r["id"])
                if not q or progs[r["id"]]["stmts"][0]["op"] != "len" or FAMILY_OF_NAME[r["lure_name"]].key != "sum": continue
                n += 1; pa += r["value_written"] == r["lure"]; pb += q["value_written"] == q["lure"]
        if n:
            N[f"expr-{SHORT[m]}-plain"] = pct(pa / n, d=0); N[f"expr-{SHORT[m]}-expr"] = pct(pb / n, d=0); N[f"expr-{SHORT[m]}-drop"] = pct((pa - pb) / n, d=0)
    # ---- gate
    gf = RESULTS_DIR / "summary" / "lure_gate_v2.json"
    if gf.exists():
        g = json.loads(gf.read_text()); ms = sorted(g); names = [k for k in g[ms[0]] if "/" not in k]
        passed = [k for k in names if np.mean([g[m][k]["pass"] for m in ms if k in g[m]]) >= 0.8]
        N["gate-pass"] = str(len(passed)); N["gate-names"] = str(len(names))
        N["gate-sum-len-readers"] = str(sum(1 for m in ms if g[m]["total"]["argmax"] == "len"))
    # ---- probes at the decision token (best layer by neutral accuracy)
    for m in ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it"):
        pj = OUT_DIR / "probes" / m / "L5" / "trace" / "v1.json"
        if not pj.exists(): continue
        d = json.loads(pj.read_text()); by = {}
        for r in d["results"]:
            if r["position"] == "pre@v1": by.setdefault(r["layer"], []).append(r)
        def agg(rs, cond, key):
            v = [r["eval"][cond][key] for r in rs if cond in r["eval"] and r["eval"][cond].get(key) is not None]
            v = [x[0] if isinstance(x, list) else x for x in v]; return float(np.mean(v)) if v else 0.0
        best = max(by, key=lambda L: agg(by[L], "neutral", "accuracy"))
        N[f"probe-{SHORT[m]}-code"] = pct(agg(by[best], "incongruent@v1", "accuracy"), d=0)
        N[f"probe-{SHORT[m]}-name"] = pct(max(agg(by[L], "incongruent@v1", "lure_rate") for L in by), d=0)
        N[f"probe-{SHORT[m]}-layer"] = str(best)
        ctl = [r["control_acc"]["neutral"] for r in by[best] if isinstance(r.get("control_acc"), dict)]
        N[f"probe-{SHORT[m]}-ctl"] = f"{np.mean(ctl):.2f}" if ctl else "--"
    # ---- patching
    for m in ("olmo2-7b-it", "llama32-3b-it", "llama31-8b-it"):
        for site in ("pre", "name"):
            f = OUT_DIR / "runs" / m / "L5" / "patch" / f"main_{site}.json"
            if not f.exists(): continue
            d = json.loads(f.read_text()); S = d["summary"]; nL = d["n_layers"]
            rem = [S[f"L{l}"]["lure_removed"] or 0 for l in range(nL)]
            N[f"patch-{SHORT[m]}-{site}-all"] = pct(S["ALL"]["lure_removed"] or 0, d=0)
            N[f"patch-{SHORT[m]}-{site}-alldamage"] = pct(S["ALL"]["damage"] or 0, d=0)
            N[f"patch-{SHORT[m]}-{site}-best"] = pct(max(rem), d=0)
            N[f"patch-{SHORT[m]}-{site}-bestlayer"] = str(int(np.argmax(rem)))
            half = next((l for l in range(nL) if rem[l] >= 0.5), None)
            N[f"patch-{SHORT[m]}-{site}-half"] = str(half) if half is not None else "--"
            N[f"patch-{SHORT[m]}-{site}-n"] = str(S["ALL"]["n"])
            if site == "name": N[f"patch-{SHORT[m]}-name-skipped"] = str(d.get("n_skipped_unaligned", 0))
        c = OUT_DIR / "runs" / m / "L5" / "patch" / "ctl_word_name.json"
        if c.exists(): N[f"patch-{SHORT[m]}-wordctl"] = pct(json.loads(c.read_text())["summary"]["ALL"]["damage"] or 0)
    # ---- E8 cruxeval
    rows = [json.loads(l) for l in (DATA_DIR / "cruxeval_len.jsonl").open()] if (DATA_DIR / "cruxeval_len.jsonl").exists() else []
    if rows:
        N["crux-n"] = str(len({r["src"] for r in rows})); N["crux-used"] = str(len({r["src"] for r in rows if r["used"]}))
        for k in ("len", "counter", "max"): N[f"crux-kind-{k}"] = str(len({r["src"] for r in rows if r["kind"] == k}))
        for m in with_runs:
            for reg in ("direct", "prose"):
                f = OUT_DIR / "runs" / m / "cruxeval" / reg / "behavior.jsonl"
                if not f.exists(): continue
                rr = [json.loads(l) for l in f.open()]
                by = {c: {x["src"]: x for x in rr if x["condition"] == c} for c in ("original", "neutral", "misleading")}
                for c in by:
                    N[f"crux-{SHORT[m]}-{reg}-{c}"] = pct(np.mean([x["correct"] for x in by[c].values()]), d=0)
                used = {r["src"]: r["used"] for r in rows}      # join from the dataset: early runs predate the flag
                common = [s for s in by["neutral"] if s in by["misleading"] and used.get(s)]
                d = [by["misleading"][s]["correct"] - by["neutral"][s]["correct"] for s in common]
                N[f"crux-{SHORT[m]}-{reg}-delta"] = pct(np.mean(d), True) if d else "--"
                kind = {r["src"]: r["kind"] for r in rows}
                for lab, dd in (("", d), ("-len", [x for x, s_ in zip(d, common) if kind[s_] == "len"]),
                                ("-counter", [x for x, s_ in zip(d, common) if kind[s_] == "counter"])):
                    if not dd: continue
                    dd = np.array(dd); boot = [rng.choice(dd, len(dd)).mean() for _ in range(2000)]
                    N[f"crux-{SHORT[m]}-{reg}{lab}-delta"] = pct(dd.mean(), True); N[f"crux-{SHORT[m]}-{reg}{lab}-lo"] = pct(np.percentile(boot, 2.5), True)
                    N[f"crux-{SHORT[m]}-{reg}{lab}-hi"] = pct(np.percentile(boot, 97.5), True); N[f"crux-{SHORT[m]}-{reg}{lab}-n"] = str(len(dd))
                if reg == "prose":
                    ws = [x["wrote_sum"] for s, x in by["misleading"].items() if x["lure_sum"] is not None]
                    wn = [x["wrote_sum"] for s, x in by["neutral"].items() if x["lure_sum"] is not None]
                    N[f"crux-{SHORT[m]}-wrotesum-mis"] = pct(np.mean(ws), d=0) if ws else "--"
                    N[f"crux-{SHORT[m]}-wrotesum-neu"] = pct(np.mean(wn), d=0) if wn else "--"
    out = PROJECT_ROOT / "paper" / "numbers.tex"
    with out.open("w") as f:
        f.write("% generated by scripts/51_numbers.py; do not edit\n")
        for k, v in sorted(N.items()):
            f.write(f"\\expandafter\\def\\csname NUMval@{k}\\endcsname{{{v}}}\n")
        f.write("\\newcommand{\\NUM}[1]{\\ifcsname NUMval@#1\\endcsname\\csname NUMval@#1\\endcsname\\else\\textcolor{red}{$\\langle\\langle$\\texttt{#1}$\\rangle\\rangle$}\\fi}\n")
    print(f"wrote {len(N)} numbers to {out}")
    for k in ("cell-olmo7-excess", "cell-olmo7-repl-excess", "cell-olmo7-comment-excess", "cell-llama3-comment-claim", "cell34-len-excess", "cell34-max-excess", "l6-max-excess", "crux-olmo7-direct-lo", "expr-olmo7-drop", "probe-olmo7-code", "probe-olmo7-name", "patch-olmo7-pre-half", "patch-olmo7-name-best", "gate-pass"):
        print(f"  {k} = {N.get(k)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
