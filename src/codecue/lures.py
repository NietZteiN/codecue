"""The lure table: what an identifier *says* a variable holds.

A lure is executable. Each misleading name maps to an implied operation over the operands the
variable's TRUE definition uses, and the lure answer is the value of that operation on the
instance's actual input. `implied` says which operands the operation needs:

    list    the function's input list `xs`           (always available)
    unary   one scalar operand, the true definition's first variable operand
    binary  two scalar operands, the true definition's two variable operands

A name whose operation cannot be evaluated for a given definition (a `unary` name on a
variable defined straight from `xs`) is not a legal lure for that variable. Congruent = the
family whose operation equals the true definition. Neutral names imply nothing.

PLAN.md §12 lists the validation this table needs before any result is claimed: each model is
asked, on the neutral twin, what a variable with this name most likely holds, and only names
on which >=80% of the panel agrees with the table survive.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class Family:
    key: str                      # "len", "sum", ...
    kind: str                     # list | unary | binary
    names: tuple[str, ...]        # identifiers that imply this operation
    source: str                   # Python source of the operation, in terms of xs / a / b
    fn: Callable[..., int]


def _f(key, kind, names, source, fn):
    return Family(key, kind, tuple(names), source, fn)


FAMILIES: tuple[Family, ...] = (
    # list-level: the name says "this is <op> of the input"
    _f("len",  "list", ("count", "n_items", "length"),   "len(xs)",  lambda xs: len(xs)),
    _f("sum",  "list", ("total", "sum_all", "acc"),      "sum(xs)",  lambda xs: sum(xs)),
    _f("max",  "list", ("largest", "max_val", "peak"),   "max(xs)",  lambda xs: max(xs)),
    _f("min",  "list", ("smallest", "min_val", "low"),   "min(xs)",  lambda xs: min(xs)),
    # unary: the name says "this is <op> of the previous value"
    _f("double", "unary", ("double", "twice"),   "2 * a",   lambda a: 2 * a),
    _f("half",   "unary", ("half",),             "a // 2",  lambda a: a // 2),
    _f("succ",   "unary", ("succ", "next_val"),  "a + 1",   lambda a: a + 1),
    _f("pred",   "unary", ("pred", "prev_val"),  "a - 1",   lambda a: a - 1),
    # binary: the name says how the two previous values combine
    _f("add",  "binary", ("combined", "both"),   "a + b",  lambda a, b: a + b),
    _f("sub",  "binary", ("diff", "gap"),        "a - b",  lambda a, b: a - b),
    _f("mul",  "binary", ("product", "scaled"),  "a * b",  lambda a, b: a * b),
)

FAMILY_OF_NAME: dict[str, Family] = {n: f for f in FAMILIES for n in f.names}
FAMILY: dict[str, Family] = {f.key: f for f in FAMILIES}
LURE_NAMES: tuple[str, ...] = tuple(FAMILY_OF_NAME)

# names that imply nothing about the value; the neutral condition and every non-target slot.
# No dictionary word, no digit, no table name; two letters so they are not Python builtins
# and so a per-model tokenizer check has a fair chance of finding single-token ones.
NEUTRAL_NAMES: tuple[str, ...] = ("v", "w", "u", "t", "r", "k", "q", "z", "m", "p", "vv", "ww", "qq", "zz")


def implied_value(name: str, xs: Sequence[int], operands: Sequence[int]) -> int | None:
    """Value the name `name` asserts, given the input list and the true definition's variable
    operands (in order). None if the family's operation is not evaluable here."""
    fam = FAMILY_OF_NAME[name]
    if fam.kind == "list":
        return fam.fn(xs)
    if fam.kind == "unary":
        return fam.fn(operands[0]) if len(operands) >= 1 else None
    return fam.fn(operands[0], operands[1]) if len(operands) >= 2 else None


assert len(set(LURE_NAMES)) == len(LURE_NAMES), "a name in two families"
assert not set(LURE_NAMES) & set(NEUTRAL_NAMES)
