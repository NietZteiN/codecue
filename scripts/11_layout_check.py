#!/usr/bin/env python
"""E1: with every model's tokenizer, do all probe/patch spans resolve to tokens in every regime?
Also records how many tokens each lure identifier takes (informational; rule 3 needs no
single-token names). Tokenizers only: run on a dev node.

    python scripts/11_layout_check.py [--models all] [--n 200]
Writes results/summary/layout_check.json; flips `verified` in configs/models.yaml for models that pass.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import CONFIG_DIR, DATA_DIR, RESULTS_DIR, load_config  # noqa: E402
from codecue.generator import read_jsonl  # noqa: E402
from codecue.layout import spans, spans_to_tokens  # noqa: E402
from codecue.lures import LURE_NAMES, NEUTRAL_NAMES  # noqa: E402
from codecue.prompts import build_prompt, demos  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--models", nargs="+", default=["all"]); ap.add_argument("--n", type=int, default=200)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    cfg = load_config("models.yaml"); models = list(cfg["models"]) if a.models == ["all"] else a.models
    xs = [x for x in read_jsonl(DATA_DIR / "L3" / "test_sets.jsonl")][: a.n * 6]
    report = {}
    for mk in models:
        try:
            tok = AutoTokenizer.from_pretrained(cfg["models"][mk]["hf_id"])
        except Exception as e:
            report[mk] = {"error": str(e)[:200]}; print(mk, "FAILED to load tokenizer:", str(e)[:120]); continue
        bad = {}; ntok = {}
        for regime in ("direct", "trace", "prose"):
            d = demos(3, 7, regime) if regime != "prose" else []
            unresolved = 0
            for x in xs:
                p = build_prompt(x, regime, d)
                if regime == "prose" and getattr(tok, "chat_template", None):
                    p = tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True)
                try:
                    enc = tok(p, return_offsets_mapping=True, add_special_tokens=True)
                    spans_to_tokens(spans(p, x, x.target or x.query, regime), enc["offset_mapping"])
                except Exception:
                    unresolved += 1
            bad[regime] = unresolved
        for name in LURE_NAMES + NEUTRAL_NAMES:
            ntok[name] = len(tok("    " + name + " = ", add_special_tokens=False)["input_ids"]) - len(tok("     = ", add_special_tokens=False)["input_ids"])
        ok = all(v <= 0.01 * len(xs) for v in bad.values())
        report[mk] = {"unresolved": bad, "n": len(xs), "ok": ok, "name_tokens": ntok, "has_chat_template": bool(getattr(tok, "chat_template", None))}
        print(f"{mk:18s} ok={ok} unresolved={bad} chat={report[mk]['has_chat_template']} multi-token lure names: "
              f"{[n for n in LURE_NAMES if ntok[n] > 1]}")
        if ok:
            cfg["models"][mk]["verified"] = True
    (RESULTS_DIR / "summary").mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "summary" / "layout_check.json").write_text(json.dumps(report, indent=1))
    (CONFIG_DIR / "models.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
