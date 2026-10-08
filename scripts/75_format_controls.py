#!/usr/bin/env python
"""Run the two registered-in-manifest demonstration controls on the same 285 pairs."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codecue.config import DATA_DIR, OUT_DIR, RESULTS_DIR, model_entry
from codecue.followups import control_demo, control_prompt
from codecue.generator import read_jsonl
from codecue.lures import FAMILY_OF_NAME
from codecue.models import generate_free, load_model
from codecue.prompts import demos, demo_block, parse_answer, value_written


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True)
    args = ap.parse_args()
    instances = read_jsonl(DATA_DIR / "L5/test_sets.jsonl")
    misleading = [x for x in instances if x.condition == "incongruent" and x.target == "v1"
                  and x.stmts[0]["op"] == "len" and FAMILY_OF_NAME[x.lure_name].key == "sum"]
    if len(misleading) != 285:
        raise ValueError("unexpected main-cell evaluation population")
    keys = {x.set_id for x in misleading}
    neutral = [x for x in instances if x.condition == "neutral" and x.set_id in keys]
    if len(neutral) != 285:
        raise ValueError("missing neutral twins")
    rows = neutral + misleading
    tok, model = load_model(model_entry(args.model)["hf_id"])
    for seed in (7, 11, 13):
        demonstrations = demos(5, seed, "trace")
        for kind in ("neutral_annotation", "numeric_elaboration"):
            destination = OUT_DIR / "round5_formats" / args.model / f"s{seed}" / kind
            destination.mkdir(parents=True, exist_ok=True)
            prompts = [control_prompt(x, demonstrations, kind, tok) for x in rows]
            fingerprint = hashlib.sha256(json.dumps(prompts).encode()).hexdigest()
            meta_path = destination / "summary.json"
            if meta_path.exists():
                previous = json.loads(meta_path.read_text())
                if previous["fingerprint"] != fingerprint:
                    raise ValueError("existing control run uses different prompts")
                if len((destination / "behavior.jsonl").read_text().splitlines()) == 570:
                    print(f"skip {destination}", flush=True); continue
            generations = generate_free(tok, model, prompts, 160, 8, stop_at_blank_line=True)
            output = []
            for x, generation in zip(rows, generations):
                written = value_written(generation, x.names["v1"])
                pred = parse_answer(generation)
                output.append({"id": x.id, "set_id": x.set_id, "condition": x.condition,
                    "target": x.target, "lure": x.lure, "lure_name": x.lure_name,
                    "names": x.names, "values": x.values, "value_written": written,
                    "values_written": {"v1": written}, "pred": pred, "correct": pred == x.answer,
                    "generation": generation, "regime": kind, "demo_seed": seed})
            if len(output) != 570:
                raise ValueError("incomplete generation output")
            temporary = destination / "behavior.jsonl.tmp"
            temporary.write_text("".join(json.dumps(row) + "\n" for row in output))
            temporary.replace(destination / "behavior.jsonl")
            counts = lambda block: len(tok(block, add_special_tokens=True)["input_ids"])
            meta = {"model": args.model, "kind": kind, "demo_seed": seed, "fingerprint": fingerprint,
                "n": len(output), "n_pairs": 285, "n_neutral": 285, "n_misleading": 285,
                "greedy": True, "max_new_tokens": 160, "batch_size": 8,
                "demo_counts": [{"source_expression": counts(demo_block(x, "trace_expr")),
                    "control": counts(control_demo(x, kind, tok))} for x in demonstrations],
                "prompt_example": prompts[0], "ids": [x.id for x in rows]}
            if kind == "neutral_annotation" and any(c["source_expression"] != c["control"] for c in meta["demo_counts"]):
                raise ValueError("annotation length mismatch")
            meta_path.write_text(json.dumps(meta, indent=2) + "\n")
            print(f"completed {args.model} seed {seed} {kind}: {len(output)}", flush=True)


if __name__ == "__main__":
    main()
