"""Behaviour runs: prompt every instance of a group in one regime, decode greedily, parse the
answer, record whether the chain wrote the target's value, and write behavior.jsonl + summary.json.

Layout guard (rule 3): every span the analysis will need must resolve to a token in every
instance; a group with more than 1% unresolved instances is refused, as in the arithmetic paper.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Sequence

from .generator import Instance
from .layout import spans, spans_to_tokens
from .models import generate_free
from .prompts import MAX_NEW, build_prompt, demos, parse_answer, parse_answer_free, parse_regime, value_written


def chat_wrap(tok, prompt: str) -> str:
    """Instruct models see the free-text regimes through their chat template; the few-shot
    regimes stay raw completions, as in the arithmetic paper."""
    if getattr(tok, "chat_template", None):
        return tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True)
    return prompt


def run_group(tok, model, model_key: str, level: int, regime: str, group: str, instances: Sequence[Instance],
              out_dir: Path, batch_size: int, use_chat: bool = True) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    base, seed = parse_regime(regime)
    few_shot = base in ("direct", "trace", "trace_expr")
    demo_insts = demos(level, seed, base) if few_shot else []
    prompts = [build_prompt(x, regime, demo_insts) for x in instances]
    if not few_shot and use_chat:
        prompts = [chat_wrap(tok, p) for p in prompts]
    # layout guard on the prompt spans (target role only; None for neutral)
    unresolved = 0
    for x, p in zip(instances, prompts):
        role = x.target or x.query
        try:
            enc = tok(p, return_offsets_mapping=True, add_special_tokens=True)
            spans_to_tokens(spans(p, x, role, base), enc["offset_mapping"])
        except Exception:
            unresolved += 1
    if unresolved > 0.01 * len(instances):
        raise RuntimeError(f"{model_key} L{level} {regime} {group}: {unresolved}/{len(instances)} instances have unresolvable spans")
    t0 = time.time()
    gens = generate_free(tok, model, prompts, MAX_NEW[base], batch_size, stop_at_blank_line=few_shot)
    rows, n_correct, n_lure, n_parsed, n_wrote = [], 0, 0, 0, 0
    with (out_dir / "behavior.jsonl").open("w") as f:
        for x, p, g in zip(instances, prompts, gens):
            pred = parse_answer(g) if few_shot else parse_answer_free(g)
            correct = pred == x.answer
            is_lure = x.lure is not None and pred == x.lure
            role = x.target or x.query
            # per-role written values: the neutral twin has no target, and comparing it on the
            # QUERIED variable while its sibling is compared on the INTERMEDIATE mis-specified
            # every written-lure baseline until 2026-09-16
            values_written = ({r: value_written(g, nm) for r, nm in x.names.items()} if base != "direct"
                              else {r: None for r in x.names})
            wrote = values_written[role]
            wrote_true = (wrote == x.values[role]) if wrote is not None else False
            n_correct += correct; n_lure += is_lure; n_parsed += pred is not None; n_wrote += wrote_true
            rows.append({"id": x.id, "set_id": x.set_id, "condition": x.condition, "target": x.target, "query": x.query,
                         "answer": x.answer, "lure": x.lure, "lure_name": x.lure_name, "pred": pred, "correct": bool(correct),
                         "pred_is_lure": bool(is_lure), "value_written": wrote, "wrote_true_value": bool(wrote_true),
                         "values_written": values_written,
                         "generation": g, "names": x.names, "values": x.values, "level": x.level})
            f.write(json.dumps(rows[-1]) + "\n")
    n = len(rows)
    s = {"model": model_key, "level": level, "regime": regime, "group": group, "n": n, "unresolved": unresolved,
         "accuracy": n_correct / n, "lure_rate": n_lure / n, "parse_rate": n_parsed / n, "wrote_true_rate": n_wrote / n,
         "seconds": time.time() - t0, "chat_template": bool(not few_shot and use_chat and getattr(tok, "chat_template", None)),
         "prompt_example": prompts[0]}
    (out_dir / "summary.json").write_text(json.dumps(s, indent=1))
    return s
