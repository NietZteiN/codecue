#!/usr/bin/env python
"""E6: patch the name (or the decision token) from a twin and read what the model would write.

    python scripts/40_patch.py --model olmo2-7b-it --level 5 --n-pairs 300

Reads the digit the model would write at `pre@v1` before and after each patch, per layer set.
Writes runs/<model>/L<level>/patch/<contrast>_<site>.json with per-pair records + a summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.cache import cache_spans, trace_text  # noqa: E402
from codecue.config import DATA_DIR, OUT_DIR, model_entry  # noqa: E402
from codecue.generator import read_jsonl  # noqa: E402
from codecue.layout import spans_to_tokens  # noqa: E402
from codecue.lures import FAMILY_OF_NAME  # noqa: E402
from codecue.models import load_model  # noqa: E402
from codecue.patching import decoder_layers, digit_scores, digit_token_ids, hidden_at, layer_sets, patch_hooks  # noqa: E402
from codecue.prompts import build_prompt, demos  # noqa: E402

CONTRASTS = {"main": ("neutral", "incongruent"), "ctl_word": ("neutral_alt", "neutral"), "ctl_lure": ("incongruent_alt", "incongruent")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--level", type=int, default=5)
    ap.add_argument("--role", default="v1"); ap.add_argument("--n-pairs", type=int, default=300)
    ap.add_argument("--sites", nargs="+", default=["name", "pre"]); ap.add_argument("--contrasts", nargs="+", default=list(CONTRASTS))
    a = ap.parse_args()
    xs = read_jsonl(DATA_DIR / f"L{a.level}" / "test_sets.jsonl")
    in_cell = lambda x: x.stmts[0]["op"] == "len" and (x.lure_name is None or FAMILY_OF_NAME[x.lure_name].key == "sum")
    by_set = defaultdict(dict)
    for x in xs:
        if x.target in (None, a.role) and in_cell(x):
            by_set[x.set_id][x.condition] = x
    m = model_entry(a.model); tok, model = load_model(m["hf_id"])
    dem = demos(a.level, 7, "trace"); tokd = digit_token_ids(tok)
    n_layers = len(decoder_layers(model)); sets = layer_sets(n_layers)
    out_dir = OUT_DIR / "runs" / a.model / f"L{a.level}" / "patch"; out_dir.mkdir(parents=True, exist_ok=True)

    import re
    def prep(x):
        p = build_prompt(x, "trace", dem); g = trace_text(x)
        # the decision token is the LAST prompt token once "Trace: name = " has been written by
        # the model; feed prompt + that prefix so the next token IS the value
        prefix = g[: g.index(" = ") + 3] if g.startswith(" " + x.names[a.role] + " = ") else None
        text = p + (prefix or "")
        e = tok(text, return_offsets_mapping=True, add_special_tokens=True)
        # EVERY occurrence of the name inside the instance region (definition, each use, the trace
        # prefix), every token of each. Patching the definition alone left later uses referring
        # to an undefined variable and broke the program at layer 0 (2026-09-16).
        b = p.rfind(x.program); name = x.names[a.role]
        occ = [(b + m_.start(), b + m_.end()) for m_ in re.finditer(rf"\b{re.escape(name)}\b", text[b:])]
        name_pos = [i for (cs, ce) in occ for i, (ts, te) in enumerate(e["offset_mapping"]) if ts < ce and te > cs]
        return e["input_ids"], sorted(set(name_pos)), len(e["input_ids"]) - 1   # ids, name positions, decision pos

    for contrast in a.contrasts:
        src_c, dst_c = CONTRASTS[contrast]
        pairs = [(v[src_c], v[dst_c]) for v in by_set.values() if src_c in v and dst_c in v][: a.n_pairs]
        for site in a.sites:
            recs, agg = [], defaultdict(lambda: defaultdict(int))
            n_skipped = 0
            for src, dst in pairs:
                s_ids, s_name, s_pre = prep(src); d_ids, d_name, d_pre = prep(dst)
                if site == "name":
                    # token-aligned only: the name must occupy the same number of tokens in both
                    # twins at every occurrence (`sum_all` is 2 tokens, no neutral name is; those
                    # pairs are skipped and counted)
                    if len(s_name) != len(d_name):
                        n_skipped += 1; continue
                    s_pos, d_pos = s_name, d_name
                else:
                    s_pos, d_pos = [s_pre], [d_pre]
                src_h = hidden_at(model, s_ids, range(n_layers), s_pos)
                base = digit_scores(model, tokd, d_ids, d_pre); b = max(base, key=base.get)
                true, lure = str(dst.values[a.role]), (str(dst.lure) if dst.lure is not None else None)
                new_lure = str(src.lure) if (contrast == "ctl_lure" and src.lure is not None) else None
                rec = {"set_id": dst.set_id, "true": true, "lure": lure, "new_lure": new_lure, "base": b, "patched": {}}
                for sname, lids in sets:
                    with patch_hooks(model, lids, d_pos, {l: src_h[l] for l in lids}):
                        sc = digit_scores(model, tokd, d_ids, d_pre)
                    p_ = max(sc, key=sc.get); rec["patched"][sname] = p_
                    A = agg[sname]; A["n"] += 1
                    A["base_lure"] += b == lure; A["base_true"] += b == true
                    A["patched_lure"] += p_ == lure; A["patched_true"] += p_ == true
                    if b == lure: A["lure_before"] += 1; A["lure_removed"] += p_ != lure
                    if b == true: A["true_before"] += 1; A["damage"] += p_ != true
                    if new_lure: A["follows_new_lure"] += p_ == new_lure
                recs.append(rec)
            summary = {s: {"n": A["n"], "base_lure_rate": A["base_lure"] / A["n"], "patched_lure_rate": A["patched_lure"] / A["n"],
                           "base_true_rate": A["base_true"] / A["n"], "patched_true_rate": A["patched_true"] / A["n"],
                           "lure_removed": (A["lure_removed"] / A["lure_before"]) if A["lure_before"] else None,
                           "damage": (A["damage"] / A["true_before"]) if A["true_before"] else None,
                           "follows_new_lure": (A["follows_new_lure"] / A["n"]) if new_lure else None}
                       for s, A in agg.items()}
            (out_dir / f"{contrast}_{site}.json").write_text(json.dumps({"contrast": contrast, "site": site, "n_layers": n_layers,
                                                                          "n_skipped_unaligned": n_skipped, "summary": summary, "rows": recs}))
            best = max((s for s in summary if s.startswith("L")), key=lambda s: summary[s]["lure_removed"] or 0) if contrast != "ctl_word" else "ALL"
            print(f"{a.model} {contrast}/{site}: n={len(pairs)} base lure {100*summary['ALL']['base_lure_rate']:.0f}% -> ALL-layers {100*summary['ALL']['patched_lure_rate']:.0f}%; "
                  f"best single layer {best}: removed {summary[best]['lure_removed']}, damage {summary['ALL']['damage']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
