"""Span-based positions (rule 3): every probe/patch position is a character span in the prompt,
mapped to tokens with the tokenizer's offset mapping, last token of the span.

Positions for the target role `t` in a prompt built by `prompts.build_prompt`:

    def@t       the identifier where it is defined (`count` in `count = total - 3`)
    end@t       the last character of its defining statement (the newline before the next line)
    use@t       the identifier at its first use after definition (an operand or the `return`)
    call        the closing parenthesis of the call line `f([4, 1, 3])`
    tracepre@t  (trace regime) the `=` of `t = ` in the trace, i.e. the token before the value
    anspre      the `:` of the final `Answer:` (direct: last char of the prompt)

Character spans are computed on the test instance's own program text, which is the LAST
program in the prompt (demonstrations use the same neutral vocabulary and can contain the same
identifiers, so the search is confined to that final block).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .generator import Instance


@dataclass(frozen=True)
class Span:
    key: str
    start: int   # char offset in the prompt, inclusive
    end: int     # exclusive


def _last_block_start(prompt: str, program: str) -> int:
    i = prompt.rfind(program)
    if i < 0:
        raise ValueError("instance program not found in prompt")
    return i


def spans(prompt: str, x: Instance, role: str, regime_base: str, generation: str = "") -> list[Span]:
    """Spans for `role` in `prompt` (+ `generation` for positions inside the model's output)."""
    name = x.names[role]
    b = _last_block_start(prompt, x.program)
    prog = x.program
    out = []
    m = re.search(rf"^\s*({re.escape(name)}) = ", prog, re.M)
    if not m:
        raise ValueError(f"{role}={name} not defined in program")
    out.append(Span(f"def@{role}", b + m.start(1), b + m.end(1)))
    line_end = prog.find("\n", m.end())
    out.append(Span(f"end@{role}", b + line_end - 1, b + line_end))
    u = re.search(rf"\b{re.escape(name)}\b", prog[line_end:])
    if u:
        out.append(Span(f"use@{role}", b + line_end + u.start(), b + line_end + u.end()))
    call_end = b + len(prog)
    out.append(Span("call", call_end - 1, call_end))
    full = prompt + generation
    if regime_base == "trace":
        t = re.search(rf"\b{re.escape(name)} (=) ", full[b:])
        if t:
            out.append(Span(f"tracepre@{role}", b + t.start(1), b + t.end(1)))
    a = full.rfind("Answer:")
    if a >= b:
        out.append(Span("anspre", a + len("Answer:") - 1, a + len("Answer:")))
    elif regime_base == "direct":
        out.append(Span("anspre", len(prompt) - 1, len(prompt)))
    return out


def spans_to_tokens(spans_: list[Span], offsets: list[tuple[int, int]]) -> dict[str, int]:
    """Map each span to the index of the LAST token overlapping it, given the tokenizer's
    `return_offsets_mapping` output for the same string."""
    pos = {}
    for s in spans_:
        toks = [i for i, (a, b) in enumerate(offsets) if a < s.end and b > s.start]
        if not toks:
            raise ValueError(f"no token covers span {s}")
        pos[s.key] = toks[-1]
    return pos
