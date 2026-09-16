#!/usr/bin/env python
"""E8: output prediction on renamed CRUXEval, direct and prose regimes.

    python scripts/21_run_cruxeval.py --model olmo2-7b-it

Answers are Python literals; a prediction is correct when it evaluates equal to the gold output.
For prose, `value_written` records the first value the reasoning states for the renamed variable.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import OUT_DIR, model_entry  # noqa: E402
from codecue.models import generate_free, load_model  # noqa: E402
from codecue.prompts import value_written  # noqa: E402
from codecue.runner import chat_wrap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DIRECT = "{code}\nassert {call} == "
PROSE = ("{code}\n\nWhat does `{call}` return? Think step by step, then finish with a line of the form "
         "`Answer: <python literal>`.")


def parse_literal(text: str, regime: str):
    if regime == "prose":
        m = re.findall(r"Answer:\s*(.+)", text)
        cand = m[-1].strip().rstrip(".") if m else text.strip().splitlines()[-1] if text.strip() else ""
    else:
        cand = text.split("\n")[0].strip()
    cand = cand.strip("` ")
    try:
        return ast.literal_eval(cand)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--batch-size", type=int, default=None)
    a = ap.parse_args()
    rows = [json.loads(l) for l in (ROOT / "data" / "cruxeval_len.jsonl").open()]
    m = model_entry(a.model); tok, model = load_model(m["hf_id"]); bs = a.batch_size or m.get("batch_size", 16)
    for regime in ("direct", "prose"):
        out = OUT_DIR / "runs" / a.model / "cruxeval" / regime; out.mkdir(parents=True, exist_ok=True)
        prompts = [(DIRECT if regime == "direct" else PROSE).format(code=r["code"], call=r["call"]) for r in rows]
        if regime == "prose":
            prompts = [chat_wrap(tok, p) for p in prompts]
        gens = generate_free(tok, model, prompts, 48 if regime == "direct" else 512, bs, stop_at_blank_line=(regime == "direct"))
        recs = []
        for r, g in zip(rows, gens):
            pred = parse_literal(g, regime)
            try: gold = ast.literal_eval(r["output"])
            except Exception: gold = r["output"]
            correct = pred == gold
            vw = value_written(g, r["name"]) if regime == "prose" else None
            recs.append({**r, "regime": regime, "pred": repr(pred), "correct": bool(correct), "parsed": pred is not None,
                         "value_written": vw, "wrote_len": vw is not None and vw == r["true_len"],
                         "wrote_sum": vw is not None and r["lure_sum"] is not None and vw == r["lure_sum"], "generation": g})
        (out / "behavior.jsonl").write_text("".join(json.dumps(x) + "\n" for x in recs))
        for cond in ("original", "neutral", "misleading"):
            rr = [x for x in recs if x["condition"] == cond]
            print(f"{a.model} cruxeval {regime:6s} {cond:10s}: n={len(rr)} acc={sum(x['correct'] for x in rr)/len(rr):.3f} "
                  f"parsed={sum(x['parsed'] for x in rr)/len(rr):.2f}" + (f" wrote_len={sum(x['wrote_len'] for x in rr)/len(rr):.2f} wrote_sum={sum(x['wrote_sum'] for x in rr)/len(rr):.2f}" if regime == "prose" else ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
