#!/usr/bin/env python
"""Do the cache spans land on the intended tokens, for every model, before any GPU time is spent?
Writes results/summary/span_check.json; the probe jobs are gated on that file existing."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.cache import cache_spans, trace_text  # noqa: E402
from codecue.config import DATA_DIR, RESULTS_DIR, load_config, model_entry  # noqa: E402
from codecue.generator import read_jsonl  # noqa: E402
from codecue.layout import spans_to_tokens  # noqa: E402
from codecue.prompts import build_prompt, demos  # noqa: E402

WANT = {"def@v1": "the identifier", "rhs@v1": "end of its right-hand side", "end@v1": "end of the line",
        "call": "the call's )", "pre@v1": "token before the traced value", "anspre": "the Answer colon"}


def main() -> int:
    from transformers import AutoTokenizer
    xs = [x for x in read_jsonl(DATA_DIR / "L5" / "test_sets.jsonl") if x.target == "v1"][:40]
    dem = demos(5, 7, "trace")
    rep, bad = {}, 0
    for mk in load_config("models.yaml")["models"]:
        try:
            tok = AutoTokenizer.from_pretrained(model_entry(mk)["hf_id"])
        except Exception as e:
            rep[mk] = {"error": str(e)[:120]}; continue
        seen, fails = {}, 0
        for x in xs:
            p = build_prompt(x, "trace", dem); g = trace_text(x)
            e = tok(p + g, return_offsets_mapping=True, add_special_tokens=True)
            try:
                pos = spans_to_tokens(cache_spans(p, g, x, "v1"), e["offset_mapping"])
            except Exception:
                fails += 1; continue
            for k, i in pos.items():
                seen.setdefault(k, []).append(tok.decode([e["input_ids"][i]]))
        rep[mk] = {"unresolved": fails, "n": len(xs),
                   "example_tokens": {k: v[:3] for k, v in seen.items()}}
        ok = fails == 0 and all(k in seen for k in WANT)
        bad += not ok
        print(f"{mk:18s} unresolved={fails}/{len(xs)} " +
              " ".join(f"{k}={seen.get(k, ['?'])[0]!r}" for k in WANT))
    (RESULTS_DIR / "summary").mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "summary" / "span_check.json").write_text(json.dumps(rep, indent=1))
    print(f"\n{len(rep) - bad}/{len(rep)} models clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
