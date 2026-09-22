#!/usr/bin/env python
"""E7: run the code-generation task (PLAN.md 3.3).

    python scripts/22_run_gentask.py --model llama31-8b-it [--limit N] [--no-chat]

The model completes a function whose docstring names a variable that is already defined under a
misleading identifier. The completion is executed on hidden inputs in a separate process
(`codecue.sandbox`) and classified as correct, lure, other or error. Writes
runs/<model>/gentask/behavior.jsonl and summary.json under $CODECUE_OUT.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from codecue.config import DATA_DIR, OUT_DIR, model_entry  # noqa: E402
from codecue.gentask import GenInstance, classify  # noqa: E402
from codecue.models import generate_free, load_model  # noqa: E402
from codecue.runner import chat_wrap  # noqa: E402
from codecue.sandbox import assemble, run_completion  # noqa: E402

INSTRUCTION = ("Complete the function. Write only the rest of the `return` line, nothing else.\n\n")
MAX_NEW = 40


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=None)
    ap.add_argument("--no-chat", action="store_true", help="raw completion instead of the chat template")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    d = DATA_DIR / "gentask"
    manifest = json.loads((d / "manifest.json").read_text())
    rows = [GenInstance(**json.loads(l)) for l in (d / "sets.jsonl").open()]
    if a.limit:
        keep = {x.set_id for x in rows[: a.limit * 3]}
        rows = [x for x in rows if x.set_id in keep]
    out = OUT_DIR / "runs" / a.model / "gentask"
    if (out / "summary.json").exists() and not a.overwrite:
        print(f"{out} already done; --overwrite to redo")
        return 0
    out.mkdir(parents=True, exist_ok=True)

    m = model_entry(a.model)
    tok, model = load_model(m["hf_id"])
    prompts = [INSTRUCTION + x.prompt_body for x in rows]
    if not a.no_chat:
        prompts = [chat_wrap(tok, p) for p in prompts]
    t0 = time.time()
    gens = generate_free(tok, model, prompts, MAX_NEW, a.batch_size or m.get("batch_size", 16),
                         stop_at_blank_line=True)
    counts: dict[str, int] = {}
    with (out / "behavior.jsonl").open("w") as f:
        for x, g in zip(rows, gens):
            code = assemble(x.prompt_body, g)
            res = run_completion(code, x.inputs)
            verdict = classify(res.get("outputs"), x)
            counts[f"{x.condition}/{verdict}"] = counts.get(f"{x.condition}/{verdict}", 0) + 1
            f.write(json.dumps({"id": x.id, "set_id": x.set_id, "condition": x.condition,
                                "name": x.name, "op": x.op, "lure_op": x.lure_op,
                                "verdict": verdict, "outputs": res.get("outputs"),
                                "error": res.get("error"), "generation": g, "code": code,
                                "correct_expected": x.correct, "lure_expected": x.lure}) + "\n")
    n_by_cond = {c: sum(v for k, v in counts.items() if k.startswith(c + "/")) for c in ("neutral", "congruent", "incongruent")}
    summary = {"model": a.model, "task": "gentask", "n": len(rows), "counts": counts,
               "n_by_condition": n_by_cond, "content_sha": manifest["content_sha"],
               "chat_template": not a.no_chat, "seconds": round(time.time() - t0, 1)}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    for c in ("neutral", "congruent", "incongruent"):
        n = max(1, n_by_cond[c])
        cells = {v: counts.get(f"{c}/{v}", 0) for v in ("correct", "lure", "other", "error")}
        print(f"  {c:12s} " + "  ".join(f"{k} {100*v/n:5.1f}%" for k, v in cells.items()))
    print(f"wrote {out/'summary.json'} in {summary['seconds']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
