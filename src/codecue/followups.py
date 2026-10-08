"""Outcome-independent prompt controls and boundaries for the reviewer follow-ups."""
from __future__ import annotations

import re

from .generator import Program, Stmt, trace_steps
from .prompts import demo_block


def first_value_boundary(generation, name):
    match = re.match(rf"\s*{re.escape(name)}\s*(?P<marker>=)\s*(?P<value>-?\d+)\b(?=\s*(?:,|\n|$))", generation)
    if match is None:
        return None
    return {"marker": match.start("marker"), "value_start": match.start("value"),
            "value": int(match.group("value"))}


def write_class(written, true, lure):
    if written == lure:
        return "lure_write"
    if written == true:
        return "correct_write"
    return "other_error"


def _steps(x):
    program = Program(x.level, tuple(x.xs), tuple(Stmt(**d) for d in x.stmts), x.query, x.distractor)
    return trace_steps(program, x.names, x.values)


def control_demo(x, kind, tokenizer):
    """Match full demonstration token counts using neutral text, never behavioral outcomes."""
    steps = _steps(x)
    if kind == "numeric_elaboration":
        trace = ", ".join(f"{name} = {value} + 0 = {value}" for name, value in steps)
        block = f"{x.program}\nTrace: {trace}\nAnswer: {x.answer}"
    elif kind == "neutral_annotation":
        target = len(tokenizer(demo_block(x, "trace_expr"), add_special_tokens=True)["input_ids"])
        fillers = ["" for _ in steps]
        def render():
            trace = ", ".join(f"{name} = {value}{fillers[i]}" for i, (name, value) in enumerate(steps))
            return f"{x.program}\nTrace: {trace}\nAnswer: {x.answer}"
        block = render()
        count = len(tokenizer(block, add_special_tokens=True)["input_ids"])
        for iteration in range(256):
            if count == target:
                break
            choices = []
            site = iteration % len(steps)
            for piece in (" checked", " noted", " done", " ok", " .", " ;", " !"):
                old = fillers[site]
                fillers[site] += piece
                candidate = render()
                n = len(tokenizer(candidate, add_special_tokens=True)["input_ids"])
                fillers[site] = old
                if count < n <= target:
                    choices.append((n, piece, candidate))
            if not choices:
                raise ValueError(f"cannot match neutral annotation tokens: {count} -> {target}")
            count, piece, block = min(choices, key=lambda choice: choice[0])
            fillers[site] += piece
        if count != target:
            raise ValueError("neutral annotation length did not converge")
    else:
        raise ValueError(f"unknown control: {kind}")
    return block


def control_prompt(x, demonstrations, kind, tokenizer):
    blocks = [control_demo(d, kind, tokenizer) for d in demonstrations]
    return "\n\n".join(blocks + [x.program + "\nTrace:"])
