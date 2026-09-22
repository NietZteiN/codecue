"""E7: the code-generation task (PLAN.md 3.3).

The output-prediction task asks the model to say what a program returns. This one asks it to
WRITE code against a docstring, with one variable already defined under a misleading name:

    def f(xs):
        '''Return total multiplied by 2.'''
        total = len(xs)
        return

The docstring names the variable, so the correct completion is `return total * 2`. The lure is
to write what the NAME says instead, `return sum(xs) * 2`, which is also valid Python and also
runs. We score by execution: the completion is run on hidden inputs and compared against the
correct program's outputs and against the lure program's outputs.

Validity rules carried from the rest of the project:

R1  Exactly one table identifier per instance, on the defined variable.
R2  The lure output differs from the correct output on EVERY test input, so a completion cannot
    be scored as the lure by coincidence, and neither equals the transform of any other
    aggregate of the same input (`len`, `sum`, `max`, `min`), so a wrong-but-not-lure completion
    is not counted as the lure.
R3  Twins are byte-identical up to the one identifier.

Nothing here executes model output. `run_completion` does, in a separate process with a timeout
and a namespace holding only the builtins the task needs; see `sandbox.py`.
"""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from typing import Callable, Sequence

from .lures import FAMILIES, FAMILY_OF_NAME

AGGREGATES: dict[str, Callable[[list[int]], int]] = {
    "len": len, "sum": sum, "max": max, "min": min,
}
# (docstring phrase, python expression template, function of the variable's value)
TRANSFORMS: list[tuple[str, str, Callable[[int], int]]] = [
    ("multiplied by 2", "{v} * 2", lambda a: a * 2),
    ("increased by 3", "{v} + 3", lambda a: a + 3),
    ("decreased by 1", "{v} - 1", lambda a: a - 1),
    ("multiplied by 3", "{v} * 3", lambda a: a * 3),
]
NEUTRAL_NAMES = ("v", "w", "r", "m", "k", "q")
CONDITIONS = ("neutral", "congruent", "incongruent")


@dataclass
class GenInstance:
    id: str
    set_id: str
    condition: str
    name: str                      # the identifier on the defined variable
    op: str                        # the aggregate the code actually computes
    lure_op: str | None            # the aggregate the NAME implies, None when not misleading
    transform: str                 # docstring phrase
    expr: str                      # the right-hand side the correct completion should produce
    inputs: list[list[int]]        # hidden test inputs
    correct: list[int]             # expected outputs
    lure: list[int] | None         # outputs of the lure reading, None when not misleading
    prompt_body: str               # the function text shown to the model, ending at `return`

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def render(name: str, op: str, phrase: str) -> str:
    return (f"def f(xs):\n"
            f'    """Return {name} {phrase}."""\n'
            f"    {name} = {op}(xs)\n"
            f"    return")


def _names_for(op: str) -> tuple[list[str], list[str]]:
    """(names whose implied operation IS op, names implying a different list aggregate)."""
    same, other = [], []
    for f in FAMILIES:
        if f.kind != "list":
            continue
        (same if f.key == op else other).append(list(f.names))
    return [n for g in same for n in g], [n for g in other for n in g]


def sample_sets(n: int, seed: int = 7, strict: bool = True) -> list[list[GenInstance]]:
    """Matched sets of three, differing only in the identifier on the defined variable."""
    rng = random.Random(seed)
    sets: list[list[GenInstance]] = []
    tries = 0
    while len(sets) < n and tries < n * 200:
        tries += 1
        op = rng.choice(list(AGGREGATES))
        same, other = _names_for(op)
        if not same or not other:
            continue
        lure_name = rng.choice(other)
        lure_op = FAMILY_OF_NAME[lure_name].key
        if lure_op not in AGGREGATES:
            continue
        phrase, tmpl, fn = rng.choice(TRANSFORMS)
        inputs = [sorted(rng.sample(range(1, 10), rng.randint(2, 5))) for _ in range(3)]
        try:
            correct = [fn(AGGREGATES[op](x)) for x in inputs]
            lure = [fn(AGGREGATES[lure_op](x)) for x in inputs]
        except ValueError:
            continue
        # R2: the lure must be distinguishable from the correct answer on every input, and from
        # every other aggregate of the same input, so a wrong completion cannot masquerade as it.
        if any(c == l for c, l in zip(correct, lure)):
            continue
        if strict:
            confusable = False
            for x, l in zip(inputs, lure):
                others = {fn(AGGREGATES[o](x)) for o in AGGREGATES if o not in (op, lure_op)}
                if l in others:
                    confusable = True
            if confusable:
                continue
        sid = f"G-{len(sets):05d}"
        neutral_name = rng.choice(NEUTRAL_NAMES)
        cong_name = rng.choice(same)
        group = []
        for cond, nm in (("neutral", neutral_name), ("congruent", cong_name), ("incongruent", lure_name)):
            group.append(GenInstance(
                id=f"{sid}-{cond}", set_id=sid, condition=cond, name=nm, op=op,
                lure_op=lure_op if cond == "incongruent" else None,
                transform=phrase, expr=tmpl.format(v=nm), inputs=inputs,
                correct=correct, lure=lure if cond == "incongruent" else None,
                prompt_body=render(nm, op, phrase)))
        sets.append(group)
    if len(sets) < n:
        raise RuntimeError(f"only {len(sets)} sets after {tries} tries; loosen the R2 filter")
    return sets


def classify(outputs: Sequence[int | None], x: GenInstance) -> str:
    """correct | lure | other | error, from the completion's outputs on the hidden inputs."""
    if outputs is None or any(o is None for o in outputs):
        return "error"
    if list(outputs) == list(x.correct):
        return "correct"
    if x.lure is not None and list(outputs) == list(x.lure):
        return "lure"
    return "other"
