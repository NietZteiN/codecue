"""Prompt formats for the four regimes and the answer parsers.

    direct      program + call, then `Answer:` -> the model writes the value
    trace       three fixed worked examples that trace execution one statement per step,
                `total = 8, v = 6`, then `Answer: 6`; writes every value BY CONSTRUCTION
    prose       one instruction, no worked examples, free text; whether the misleading
                variable's value is written is MEASURED per instance (`value_written`)
    codechain   the model annotates the program with comments, no values, then answers

Demonstrations are fixed per (level, seed) as in the arithmetic paper, and >=3 seeds are run
because the fixed examples were the largest single factor there.

Parsing takes the LAST `Answer: <int>` before a blank line, never the first line: a model that
restates the problem before answering must not be scored as silent (bug found 2026-09-14).
"""
from __future__ import annotations

import random
import re

from .generator import Instance, LEVELS, Program, Stmt, render, sample_sets, trace_steps

REGIMES = ("direct", "trace", "prose", "codechain")
N_DEMOS = 3
MAX_NEW = {"direct": 8, "trace": 96, "prose": 400, "codechain": 448}

PROSE_INSTRUCTION = ("What does the call return? Think step by step, then finish with a line "
                     "of the form `Answer: <number>`.")
CODECHAIN_INSTRUCTION = ("Rewrite the function with a comment on every line explaining what it "
                         "does, without computing any values. Then finish with a line of the form "
                         "`Answer: <number>`.")


def parse_regime(regime: str) -> tuple[str, int]:
    """'trace_s11' -> ('trace', 11); 'trace' -> ('trace', 7)."""
    base, _, s = regime.partition("_s")
    return base, int(s) if s else 7


def _prog(x: Instance) -> Program:
    return Program(x.level, tuple(x.xs), tuple(Stmt(**d) for d in x.stmts), x.query, x.distractor)


def demo_block(x: Instance, regime: str) -> str:
    """One worked example in the given regime's format (neutral names)."""
    prog = _prog(x)
    steps = trace_steps(prog, x.names, x.values)
    if regime == "direct":
        return f"{x.program}\nAnswer: {x.answer}"
    if regime == "trace":
        tr = ", ".join(f"{n} = {v}" for n, v in steps)
        return f"{x.program}\nTrace: {tr}\nAnswer: {x.answer}"
    raise ValueError(regime)


def demos(level: int, seed: int, regime: str) -> list[Instance]:
    """Three fixed neutral instances that never appear in any test set (their own seed space)."""
    rng_seed = 900_000 + seed
    picked = []
    for s in sample_sets(level, N_DEMOS, seed=rng_seed, tag="demo"):
        picked.append(next(i for i in s if i.condition == "neutral"))
        if len(picked) == N_DEMOS:
            break
    return picked


def build_prompt(x: Instance, regime: str, demo_insts: list[Instance]) -> str:
    base, _ = parse_regime(regime)
    if base in ("direct", "trace"):
        blocks = [demo_block(d, base) for d in demo_insts] + [x.program + ("\nTrace:" if base == "trace" else "\nAnswer:")]
        return "\n\n".join(blocks)
    if base == "prose":
        return f"{x.program}\n\n{PROSE_INSTRUCTION}\n"
    if base == "codechain":
        return f"{x.program}\n\n{CODECHAIN_INSTRUCTION}\n"
    raise ValueError(regime)


ANS_RE = re.compile(r"Answer:\s*(-?\d+)")


def parse_answer(text: str) -> int | None:
    """Few-shot regimes: the answer to THIS problem is the last `Answer: <int>` before the first
    blank line. Models that keep going invent new problems after the blank line (CodeLlama in the
    pilot, 2026-09-15); those must never be read."""
    block = text.split("\n\n", 1)[0]
    hits = ANS_RE.findall(block)
    if not hits:
        # direct regime: the continuation after "Answer:" is the number itself
        m = re.match(r"\s*(-?\d+)", block)
        return int(m.group(1)) if m else None
    return int(hits[-1])


def parse_answer_free(text: str) -> int | None:
    """Free-text regimes: the last `Answer: <int>` anywhere; else the last integer on the last
    non-empty line."""
    hits = ANS_RE.findall(text)
    if hits:
        return int(hits[-1])
    lines = [l for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return None
    nums = re.findall(r"-?\d+", lines[-1])
    return int(nums[-1]) if nums else None


# `count = 7`, `count is 7`, `count: 7`, `count -> 7`, and `count = total - 3 = 7` (the value
# after an intermediate expression, within the same clause)
VALUE_RE = r"[^\n.;]{0,40}?(?:=|is|:|->|equals)\s*(-?\d+)\b"


def value_written(text: str, name: str, before: str = "Answer:") -> int | None:
    """The first value the model WRITES for variable `name` before the answer line, or None.

    This is the per-instance measurement behind P3: in a prose chain the misleading variable's
    value is sometimes written (`count = 7`, `count is 7`) and sometimes not."""
    head = text.split(before, 1)[0]
    m = re.search(rf"\b{re.escape(name)}\b{VALUE_RE}", head)
    return int(m.group(1)) if m else None
