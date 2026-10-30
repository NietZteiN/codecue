"""Value-free, prefix-visible structural relationship labels for restricted programs.

``labels_at(source, statement)`` observes assignments 0 through ``statement``
inclusive. Every assignment creates a new version, including constant overwrites.
Canonical node IDs are ``v{slot}@{version}``, with versions starting at one. Edges
point from a definition that is read to its consuming definition. Strict ancestor
edges include direct edges but exclude reflexive edges. A separate succession
relation connects consecutive definitions of the same slot; an overwrite alone
is not a data dependency. All visible obsolete definitions remain in the graph.

An explicit ``canonical_slots`` maps surface identifiers to unique contiguous
nonnegative integer slots. It must cover visible identifiers and may include
future slots, which produce no labels until defined. Without a map, slots follow
first *visible* definition order. Names, literal/computed values, future traces,
answers, and liveness are never returned. Use occurrences follow expression
operand order; ``operand_path`` distinguishes repeated reads, such as ``x-x``.

The output expression is hidden by default, even at the last assignment. With
``output_visible=True`` it is permitted only at that last checkpoint and gets a
separate structural graph. These are syntactic dependencies, not functional
influence: a read in ``x-x`` is retained despite arithmetic cancellation. This
module supplies oracle labels, not a scientific decoder or a causal analysis.

The complete source must pass the existing restricted parser; malformed future
code may therefore be rejected. Returned labels, however, depend only on the
visible prefix (and, when explicitly visible, the output). Source/AST/depth and
ancestry-work limits bound the pure-Python validation. An independently built
prefix graph is cross-checked with ``interpreter.execute`` using zero assignment
substitutions and a literal-zero output sentinel when the query is hidden. No
future assignment or hidden output is executed, and validation values are dropped.
"""
from __future__ import annotations

import ast
import keyword
from collections import Counter

from . import interpreter

SCHEMA_VERSION = 1
MAX_SOURCE_BYTES = 65_536
MAX_AST_NODES = 8_192
MAX_AST_DEPTH = 64
MAX_CANONICAL_SLOTS = 128
# The existing interpreter recursively expands ancestors without memoization.
# Bound that work before invoking it, including all per-definition expansions.
MAX_ANCESTOR_VISITS = 100_000


def _tree(source: str) -> ast.Module:
    if not isinstance(source, str):
        raise ValueError("source must be a string")
    try:
        size = len(source.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise ValueError("source must be valid UTF-8") from exc
    if size > MAX_SOURCE_BYTES:
        raise ValueError("source exceeds relationship-label byte limit")
    try:
        tree = interpreter.parse(source)
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("invalid restricted program") from exc
    stack = [(tree, 0)]
    count = 0
    while stack:
        node, depth = stack.pop()
        count += 1
        if count > MAX_AST_NODES or depth > MAX_AST_DEPTH:
            raise ValueError("program exceeds relationship-label AST limits")
        stack.extend((child, depth + 1) for child in ast.iter_child_nodes(node))
    return tree


def _slots(prefix: list[ast.Assign], supplied: dict[str, int] | None) -> dict[str, int]:
    visible = {node.id for stmt in prefix for node in ast.walk(stmt)
               if isinstance(node, ast.Name)}
    if supplied is None:
        result: dict[str, int] = {}
        for stmt in prefix:
            name = stmt.targets[0].id
            if name not in result:
                result[name] = len(result)
        return result
    if not isinstance(supplied, dict):
        raise ValueError("canonical_slots must be a dictionary or None")
    if len(supplied) > MAX_CANONICAL_SLOTS:
        raise ValueError("canonical_slots exceeds relationship-label slot limit")
    for name, slot in supplied.items():
        if (not isinstance(name, str) or not name.isidentifier()
                or keyword.iskeyword(name) or name.startswith("_")):
            raise ValueError("canonical slot keys must be valid nonreserved identifiers")
        if type(slot) is not int or not 0 <= slot < MAX_CANONICAL_SLOTS:
            raise ValueError("canonical slots must be strict bounded nonnegative integers")
    if set(supplied.values()) != set(range(len(supplied))):
        raise ValueError("canonical slots must be unique and contiguous from zero")
    if not visible.issubset(supplied):
        raise ValueError("canonical_slots does not cover visible identifiers")
    return dict(supplied)


def _uses(expr: ast.expr, current: dict[str, str], slots: dict[str, int],
          statement: int, consumer: str) -> list[dict]:
    result: list[dict] = []

    def visit(node: ast.expr, path: list[str]) -> None:
        if isinstance(node, ast.Name):
            referent = current[node.id]
            result.append({"statement": statement, "consumer": consumer,
                           "occurrence": len(result), "operand_path": path,
                           "referent": referent, "canonical_name": f"v{slots[node.id]}",
                           "slot": slots[node.id], "version": int(referent.rsplit("@", 1)[1])})
        elif isinstance(node, ast.UnaryOp):
            visit(node.operand, path + ["operand"])
        elif isinstance(node, ast.BinOp):
            visit(node.left, path + ["left"])
            visit(node.right, path + ["right"])
        elif not isinstance(node, ast.Constant):
            raise ValueError("unsupported relationship expression")

    visit(expr, [])
    return result


def _validate(prefix: list[ast.Assign], output: ast.expr, slots: dict[str, int],
              nodes: list[dict], uses: list[dict], direct: set[tuple[str, str]],
              expected_versions: list[dict[str, str]], output_uses: list[dict]) -> None:
    """Check structural labels against the existing oracle, never its values."""
    validation_tree = ast.Module(body=[*prefix, ast.Expr(value=output)], type_ignores=[])
    source = ast.unparse(ast.fix_missing_locations(validation_tree))
    counts: dict[str, int] = {}
    substitutions: dict[str, int] = {}
    canonical: dict[str, str] = {}
    for stmt in prefix:
        name = stmt.targets[0].id
        counts[name] = counts.get(name, 0) + 1
        surface = f"{name}@{counts[name]}"
        substitutions[surface] = 0
        canonical[surface] = f"v{slots[name]}@{counts[name]}"
    oracle = interpreter.execute(source, substitutions=substitutions)
    trace = oracle["execution_trace"]
    if len(trace) != len(prefix):
        raise ValueError("relationship/oracle prefix length mismatch")
    ordered_nodes = sorted(nodes, key=lambda node: node["statement"])
    for i, (point, node) in enumerate(zip(trace, ordered_nodes)):
        if point["statement"] != i or canonical[point["definition"]] != node["id"]:
            raise ValueError("relationship/oracle definition mismatch")
        versions = {f"v{slots[name]}": canonical[definition]
                    for name, definition in point["versions"].items()}
        if versions != expected_versions[i]:
            raise ValueError("relationship/oracle current-version mismatch")
        expected = Counter(use["referent"] for use in uses if use["statement"] == i)
        if Counter(canonical[use["definition"]] for use in point["uses"]) != expected:
            raise ValueError("relationship/oracle use-occurrence mismatch")
    oracle_edges = {(canonical[parent], canonical[child])
                    for parent, child in oracle["dependency_edges"] if child != "output"}
    if oracle_edges != direct:
        raise ValueError("relationship/oracle direct-edge mismatch")
    if (Counter(canonical[use["definition"]] for use in oracle["output_uses"])
            != Counter(use["referent"] for use in output_uses)):
        raise ValueError("relationship/oracle output-use mismatch")


def labels_at(source: str, statement: int, canonical_slots: dict[str, int] | None = None,
              *, output_visible: bool = False) -> dict:
    """Return only visible, value-free version/relationship labels.

    ``statement`` is the zero-based index of the last visible assignment, not a
    source line or output index. Strict integer checkpoints exclude booleans.
    Output visibility must be explicitly boolean and is allowed only at the final
    assignment. Extra explicitly mapped future slots are not included in output.
    """
    if type(statement) is not int:
        raise ValueError("statement must be a strict integer assignment index")
    if type(output_visible) is not bool:
        raise ValueError("output_visible must be a boolean")
    tree = _tree(source)
    assignments = tree.body[:-1]
    if not 0 <= statement < len(assignments):
        raise ValueError("statement is outside the assignment checkpoints")
    if output_visible and statement != len(assignments) - 1:
        raise ValueError("output can be visible only at the final assignment checkpoint")
    prefix = assignments[:statement + 1]
    slots = _slots(prefix, canonical_slots)
    current: dict[str, str] = {}
    counts: dict[str, int] = {}
    nodes: list[dict] = []
    uses: list[dict] = []
    direct: set[tuple[str, str]] = set()
    succession: set[tuple[str, str]] = set()
    ancestors: dict[str, set[str]] = {}
    recursive_work: dict[str, int] = {}
    expected_versions: list[dict[str, str]] = []
    work = 0
    for i, stmt in enumerate(prefix):
        name = stmt.targets[0].id
        version = counts.get(name, 0) + 1
        key = f"v{slots[name]}@{version}"
        occurrences = _uses(stmt.value, current, slots, i, key)
        parents = {use["referent"] for use in occurrences}
        direct.update((parent, key) for parent in parents)
        ancestors[key] = parents | {ancestor for parent in parents for ancestor in ancestors[parent]}
        recursive_work[key] = sum(1 + recursive_work[parent] for parent in parents)
        work += recursive_work[key]
        if work > MAX_ANCESTOR_VISITS:
            raise ValueError("prefix exceeds relationship-label ancestry-work limit")
        if name in current:
            succession.add((current[name], key))
        counts[name] = version
        current[name] = key
        uses.extend(occurrences)
        nodes.append({"id": key, "canonical_name": f"v{slots[name]}", "slot": slots[name],
                      "version": version, "statement": i})
        expected_versions.append({f"v{slots[n]}": k for n, k in current.items()})
    current_ids = set(current.values())
    for node in nodes:
        node["status"] = "current" if node["id"] in current_ids else "obsolete"
    output_expr = tree.body[-1].value if output_visible else ast.Constant(value=0)
    output_uses = _uses(output_expr, current, slots, len(prefix), "output")
    output_parents = {use["referent"] for use in output_uses}
    if work + sum(1 + recursive_work[parent] for parent in output_parents) > MAX_ANCESTOR_VISITS:
        raise ValueError("visible output exceeds relationship-label ancestry-work limit")
    _validate(prefix, output_expr, slots, nodes, uses, direct, expected_versions, output_uses)
    result = {"schema_version": SCHEMA_VERSION, "checkpoint": statement,
              "output_visible": output_visible,
              "version_nodes": sorted(nodes, key=lambda node: (node["slot"], node["version"])),
              "direct_def_use_edges": [list(edge) for edge in sorted(direct)],
              "strict_ancestor_edges": [list(edge) for edge in sorted(
                  (ancestor, key) for key, parents in ancestors.items() for ancestor in parents)],
              "succession_edges": [list(edge) for edge in sorted(succession)], "uses": uses}
    if output_visible:
        result["output"] = {
            "direct_uses": output_uses, "direct_referents": sorted(output_parents),
            "structural_ancestors": sorted(output_parents | {
                ancestor for parent in output_parents for ancestor in ancestors[parent]}),
            "semantics": "syntactic_dependencies_not_functional_influence"}
    return result
