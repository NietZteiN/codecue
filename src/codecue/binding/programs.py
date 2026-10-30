"""Three generator families with semantic roles and bijective AST renaming."""
from __future__ import annotations

import ast
import itertools
import keyword
import random
from collections import Counter

from .interpreter import execute, substituted_source

FAMILIES = ("parallel", "snapshot", "accumulator")
CONDITIONS = ("informative", "neutral", "misleading")
ROLES = {
    "parallel": ("left_chain", "right_chain", "plus_value", "minus_value"),
    "snapshot": ("current_value", "saved_value", "left_branch", "right_branch"),
    "accumulator": ("left_total", "right_total", "sum_left", "sum_right"),
}
SYNONYMS = {
    "parallel": ("plus_chain", "minus_chain", "left_branch", "right_branch"),
    "snapshot": ("updated_value", "copy_value", "plus_value", "minus_value"),
    "accumulator": ("plus_total", "minus_total", "left_sum", "right_sum"),
}


def renaming(family, condition, realization, split, variable_count=4):
    roles = (ROLES if realization == 0 else SYNONYMS)[family]
    if variable_count not in (4, 6):
        raise ValueError('supported slot counts are four and six')
    if variable_count == 6:
        roles += ('left_value', 'right_value') if realization == 0 else ('sum_left', 'sum_right')
    # Vocabulary is disjoint by split. Prefixes are lexical markers only.
    prefix = {"train": "", "development": "dev_", "test": "held_"}[split]
    names = tuple(prefix + n for n in roles)
    if condition == "misleading":
        names = tuple(names[i ^ 1] for i in range(variable_count))
    elif condition == "neutral":
        names = tuple(prefix + (f"item_{i}" if realization == 0 else f"cell_{i}") for i in range(variable_count))
    return {f"v{i}": n for i, n in enumerate(names)}


def rename(source, mapping):
    if len(set(mapping.values())) != len(mapping) or any(
        not n.isidentifier() or keyword.iskeyword(n) or n.startswith("_") for n in mapping.values()
    ):
        raise ValueError("renaming must be a bijection to valid nonreserved identifiers")
    tree = ast.parse(source)
    if {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} != set(mapping):
        raise ValueError("rename map does not cover exactly the scope")

    class Renamer(ast.NodeTransformer):
        def visit_Name(self, node):
            return ast.copy_location(ast.Name(id=mapping[node.id], ctx=node.ctx), node)

    return ast.unparse(ast.fix_missing_locations(Renamer().visit(tree)))


def skeleton(source):
    tree = ast.parse(source)
    class Numbers(ast.NodeTransformer):
        def visit_UnaryOp(self, node):
            if isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
                return ast.copy_location(ast.Constant(value=0), node)
            return self.generic_visit(node)

        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant(value=0), node)
    tree = Numbers().visit(tree)
    return ast.dump(tree, include_attributes=False)


def make_program(family, load, updates, template, rng: random.Random, *, variable_count=4, distance_padding=0):
    """All cells execute four chains; load changes the number relevant to output.

    Five initialization orders x two arithmetic signs define ten skeletons per cell.
    Low-load unused branches control source length/operation budget. Output always
    has four binary operations. Snapshot's saved slot has a genuine copy role.
    """
    if family not in FAMILIES or variable_count not in (4, 6) or load not in (2,4,6) or load > variable_count:
        raise ValueError('unsupported family/load/slot configuration')
    if not 1 <= updates <= 7 or not 0 <= distance_padding <= 16:
        raise ValueError('updates/padding outside bounded generator envelope')
    orders = list(itertools.permutations(range(variable_count)))
    order = orders[template // 2]
    sign = "+" if template % 2 == 0 else "-"
    lines = []
    for i in order:
        lines.append(f"v{i} = {rng.randint(-12, 12)} {sign} {rng.randint(1, 6)}")
    if family == "snapshot":
        lines.append("v1 = v0")
    # Total target displacement has the same distribution for one and three
    # updates. The high-update condition includes cancelling intermediate steps.
    total = rng.randint(1, 5)
    deltas = [total] if updates == 1 else [rng.randint(1, 5) for _ in range(updates-1)]
    if updates > 1:
        deltas.append(total - sum(deltas))
    for step, delta in enumerate(deltas):
        lines.append(f"v0 = v0 {sign} ({delta})")
        if family == "accumulator":
            for i in range(variable_count-1, 0, -1):
                lines.append(f"v{i} = v{i} {sign} {rng.randint(1, 5)}")
    if family == "parallel":
        for i in range(1, variable_count):
            lines.append(f"v{i} = v{i} {sign} {rng.randint(1, 5)}")
    # Repeated use of the saved binding prevents the snapshot answer from
    # reducing to just the net update. Both loads have four output operations.
    # Additional independent identity updates lengthen the target's assignment
    # distance while preserving all final values. They also change other versions
    # and arithmetic work, so they are explicitly labelled a structural stressor.
    lines.extend([f'v{variable_count-1} = v{variable_count-1} + (1 - 1)'] * distance_padding)
    output = "(v0 - (v1 + v1)) + (1 - 1)" if load == 2 else "(v0 - (v1 + v1)) + (v2 - v3)"
    if load == 6:
        output += ' + (v4 - v5)'
    lines.append(output)
    return "\n".join(lines)


def swap_final_bindings(source):
    """Lawful semantic control: swap final ownership of v0 and v1.

    Replace their LAST definitions with constants computed by the oracle. Later
    statements might depend on these versions: only accept exact final-state swaps.
    This control is labelled literalized; computed analogues swap whole chains by
    an AST name permutation and use the unchanged query (see computed_swap).
    """
    state = execute(source)["execution_trace"][-1]
    changed = source
    for a, b in (("v0", "v1"), ("v1", "v0")):
        changed = substituted_source(changed, state["versions"][a], state["values"][b])
    return changed


def computed_swap(source):
    mapping = {n.id: n.id for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Name)}
    mapping.update(v0="v1", v1="v0")
    renamed = rename(source, mapping).splitlines()
    renamed[-1] = source.splitlines()[-1]
    return "\n".join(renamed)


def features(source, trace):
    tree = ast.parse(source)
    literals = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)]
    assignments = tree.body[:-1]
    last = trace["execution_trace"][-1]
    computed = [p for p, stmt in zip(trace["execution_trace"], assignments) if isinstance(stmt.value, ast.BinOp)]
    output_uses = trace["output_uses"]
    distances = [len(assignments) - 1 - next(p["statement"] for p in trace["execution_trace"]
                 if p["definition"] == u["definition"]) for u in output_uses]
    return {"arithmetic_operations": sum(isinstance(n, ast.BinOp) for n in ast.walk(tree)),
            "statements": len(assignments), "dependency_depth": trace["dependency_depth"],
            "max_liveness": max(p["count"] for p in trace["liveness"]),
            "assignment_distance": max(distances, default=0), "answer_magnitude": abs(trace["expected_answer"]),
            "target_reassignments": sum(p["definition"].startswith("v0@") for p in trace["execution_trace"]) - 1,
            "target_net_update": last["values"]["v0"] - next(p["value"] for p in trace["execution_trace"] if p["definition"] == "v0@1"),
            "computed_values_absent_from_literals": sum(p["value"] not in literals for p in computed),
            "computed_assignments": len(computed),
            "copy_assignments": sum(isinstance(s.value, ast.Name) for s in assignments),
            "literal_assignments": sum(isinstance(s.value, ast.Constant) or
                isinstance(s.value, ast.UnaryOp) and isinstance(s.value.operand, ast.Constant) for s in assignments),
            "final_value_multiset": sorted(last["values"].values()),
            "repeated_final_values": any(n > 1 for n in Counter(last["values"].values()).values())}
