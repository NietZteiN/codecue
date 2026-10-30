"""Prefix-visible *numeric target* oracle, separate from structural relationships.

``labels_at(source, statement, canonical_slots=None)`` observes assignments zero
through ``statement`` inclusive. It returns each currently bound canonical slot's
actual integer value and version reference, all ordered distinct-slot pairs, and
all ordered triples of three distinct slots. Pair ``difference`` is the signed
integer ``left-right`` (range [-128,128]); equality/order and the two triple tasks
are booleans. These are different target types and should be evaluated separately.

Canonical slots follow ``relationships``: explicit maps may include unseen future
slots; otherwise first visible definition order determines slots. Only visible
bindings are returned, with at most eight slots before quadratic/cubic expansion.
Repeated values are legitimate equality controls. Relations use actual arithmetic,
including cancellation, rather than syntactic ancestry or functional influence.

All values and labels are oracle TARGETS, including values supplied for a baseline
that derives relations from independently decoded values. They are not readout
features, model responses, correctness labels, decoded graphs, or mechanism-C
features. This module fits no decoder and performs no model queries.

The full restricted source is parsed (so invalid future syntax can be rejected),
but execution contains only visible assignments followed by a literal-zero output
sentinel. The hidden query and future assignments never execute. Actual visible
assignment values must satisfy the existing interpreter's bound of 64. Source,
AST, canonical-map and recursive-ancestry work caps match the structural oracle.
"""
from __future__ import annotations

import ast
from itertools import permutations

from . import interpreter, relationships

SCHEMA_VERSION = 1
MAX_VISIBLE_SLOTS = 8
VALUE_BOUND = 64


def _prefix_guard(prefix: list[ast.Assign]) -> None:
    """Bound the existing interpreter's recursive ancestor work before execution."""
    latest: dict[str, int] = {}
    visits: list[int] = []
    total = 0
    for index, stmt in enumerate(prefix):
        parents = {latest[node.id] for node in ast.walk(stmt.value) if isinstance(node, ast.Name)}
        work = sum(1 + visits[parent] for parent in parents)
        visits.append(work)
        total += work
        if total > relationships.MAX_ANCESTOR_VISITS:
            raise ValueError("prefix exceeds algebraic-label ancestry-work limit")
        latest[stmt.targets[0].id] = index


def labels_at(source: str, statement: int, canonical_slots: dict[str, int] | None = None) -> dict:
    """Return current numeric relation targets, with no future/output labels.

    ``statement`` is a strict zero-based integer assignment checkpoint, excluding
    booleans. Explicit maps and all source limits follow ``relationships``. Numeric
    bounds apply to every visible assignment, not only the final visible state.
    """
    if type(statement) is not int:
        raise ValueError("statement must be a strict integer assignment index")
    tree = relationships._tree(source)
    if not 0 <= statement < len(tree.body) - 1:
        raise ValueError("statement is outside the assignment checkpoints")
    prefix = tree.body[:statement + 1]
    slots = relationships._slots(prefix, canonical_slots)
    visible_names = {stmt.targets[0].id for stmt in prefix}
    if len(visible_names) > MAX_VISIBLE_SLOTS:
        raise ValueError("algebraic labels support at most eight visible slots")
    _prefix_guard(prefix)
    visible = ast.Module(body=[*prefix, ast.Expr(value=ast.Constant(value=0))], type_ignores=[])
    truth = interpreter.execute(ast.unparse(ast.fix_missing_locations(visible)), bound=VALUE_BOUND)
    point = truth["execution_trace"][-1]
    locations = {item["definition"]: item["statement"] for item in truth["execution_trace"]}
    current = []
    for name in sorted(visible_names, key=slots.__getitem__):
        version = int(point["versions"][name].rsplit("@", 1)[1])
        current.append({"canonical_name": f"v{slots[name]}", "slot": slots[name], "version": version,
                        "definition": f"v{slots[name]}@{version}",
                        "statement": locations[point["versions"][name]], "value": point["values"][name]})
    pairs = [{"left": left["canonical_name"], "right": right["canonical_name"],
              "equal": left["value"] == right["value"], "less_than": left["value"] < right["value"],
              "difference": left["value"] - right["value"]}
             for left, right in permutations(current, 2)]
    triples = [{"first": first["canonical_name"], "second": second["canonical_name"],
                "third": third["canonical_name"],
                "sum_equals_third": first["value"] + second["value"] == third["value"],
                "difference_equals_third": first["value"] - second["value"] == third["value"]}
               for first, second, third in permutations(current, 3)]
    return {"schema_version": SCHEMA_VERSION, "checkpoint": statement,
            "target_semantics": "numeric_oracle_targets_not_model_features",
            "current_slots": current, "ordered_pairs": pairs, "ordered_triples": triples}
