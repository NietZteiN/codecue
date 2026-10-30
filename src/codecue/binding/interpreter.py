"""Restricted AST oracle with explicit assignment versions and causal substitutions.

Only internally generated programs enter the independent Python subprocess. This is
an allowlist for this study, not a sandbox for arbitrary submitted Python.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import defaultdict


def parse(source: str) -> ast.Module:
    tree = ast.parse(source)
    if not 2 <= len(tree.body) <= 128 or not isinstance(tree.body[-1], ast.Expr):
        raise ValueError("expected assignments followed by one output expression")
    defined = set()
    for i, stmt in enumerate(tree.body):
        if i < len(tree.body) - 1:
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                raise ValueError("only simple assignments are allowed")
            name = stmt.targets[0].id
            if not name.isidentifier() or name.startswith("_"):
                raise ValueError("invalid identifier")
            expr = stmt.value
        else:
            expr = stmt.value
        for node in ast.walk(expr):
            if isinstance(node, ast.Name):
                if node.id not in defined:
                    raise ValueError(f"undefined variable {node.id}")
            elif isinstance(node, ast.Constant):
                if type(node.value) is not int or abs(node.value) > 64:
                    raise ValueError("integer literal outside [-64,64]")
            elif isinstance(node, ast.BinOp):
                if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
                    raise ValueError("unsupported operator")
                if isinstance(node.op, ast.Mult) and not (
                    isinstance(node.right, ast.Constant) and type(node.right.value) is int
                    and abs(node.right.value) <= 3
                ):
                    raise ValueError("multiplication requires a small right constant")
            elif not isinstance(node, (ast.Load, ast.Add, ast.Sub, ast.Mult, ast.UnaryOp, ast.USub)):
                raise ValueError(f"unsupported AST {type(node).__name__}")
            if isinstance(node, ast.UnaryOp) and not isinstance(node.op, ast.USub):
                raise ValueError("unsupported unary operator")
        if i < len(tree.body) - 1:
            defined.add(name)
    return tree


def value(expr, state):
    if isinstance(expr, ast.Constant):
        return expr.value
    if isinstance(expr, ast.Name):
        return state[expr.id]
    if isinstance(expr, ast.UnaryOp):
        return -value(expr.operand, state)
    a, b = value(expr.left, state), value(expr.right, state)
    if isinstance(expr.op, ast.Add):
        return a + b
    if isinstance(expr.op, ast.Sub):
        return a - b
    return a * b


def execute(source: str, substitutions: dict[str, int] | None = None, bound=64) -> dict:
    """Substitute a defining assignment's result; recompute every downstream use.

    Version labels are NAME@N, starting at 1. Dependencies remain syntactic;
    counterfactual output changes measure functional influence separately.
    """
    tree = parse(source)
    substitutions = substitutions or {}
    state, versions, history, trace, uses = {}, {}, {}, [], []
    counts = defaultdict(int)
    parents, depth = {}, {}
    for i, stmt in enumerate(tree.body):
        expr = stmt.value
        defining = [versions[n.id] for n in ast.walk(expr) if isinstance(n, ast.Name)]
        uses.append([{"name": n.id, "definition": versions[n.id]} for n in ast.walk(expr) if isinstance(n, ast.Name)])
        v = value(expr, state)
        if isinstance(stmt, ast.Expr):
            parents["output"] = sorted(set(defining))
            answer = v
            break
        name = stmt.targets[0].id
        counts[name] += 1
        key = f"{name}@{counts[name]}"
        v = substitutions.get(key, v)
        if type(v) is not int or abs(v) > bound:
            raise ValueError("live value outside configured bounds")
        parents[key] = sorted(set(defining))
        depth[key] = 1 + max((depth[p] for p in defining), default=0)
        state[name], versions[name], history[key] = v, key, v
        trace.append({"statement": i, "definition": key, "value": v,
                      "values": dict(state), "versions": dict(versions), "uses": uses[-1]})
    unknown = set(substitutions) - set(history)
    if unknown:
        raise ValueError(f"unknown substitutions: {unknown}")

    def ancestors(key):
        result = set()
        for p in parents[key]:
            result.add(p)
            result.update(ancestors(p))
        return result

    # Liveness at each checkpoint: present versions read by any future statement,
    # excluding dead computations via ancestry under the selected output.
    output_ancestors = ancestors("output")
    liveness = []
    for i, point in enumerate(trace):
        future = {u["definition"] for group in uses[i + 1:] for u in group}
        live = {n: k for n, k in point["versions"].items() if k in future and k in output_ancestors}
        liveness.append({"statement": i, "live_versions": live, "count": len(live)})
    edges = [[p, k] for k, ps in parents.items() for p in ps]
    return {"execution_trace": trace, "versioned_bindings": history,
            "dependency_edges": edges,
            "transitive_dependencies": {k: sorted(ancestors(k)) for k in parents},
            "liveness": liveness, "expected_answer": answer,
            "dependency_depth": max(depth.values(), default=0), "output_uses": uses[-1]}


HARNESS = '''import ast,json,sys
out=[]
for source in json.load(sys.stdin):
 tree=ast.parse(source)
 ns={"__builtins__": {}}
 trace=[]
 for stmt in tree.body[:-1]:
  exec(compile(ast.Module(body=[stmt],type_ignores=[]),"<generated>","exec"),ns)
  trace.append({k:v for k,v in ns.items() if k!="__builtins__"})
 answer=eval(compile(ast.Expression(tree.body[-1].value),"<generated>","eval"),ns)
 out.append({"answer":answer,"trace":trace})
print(json.dumps(out))
'''


def python_oracle(sources: list[str], timeout=30) -> list[dict]:
    """Independent ordinary-Python execution after complete AST validation."""
    if len(sources) > 256:
        raise ValueError("oracle batches limited to 256")
    for source in sources:
        parse(source)
    result = subprocess.run([sys.executable, "-I", "-c", HARNESS], input=json.dumps(sources),
                            capture_output=True, text=True, timeout=timeout, check=True)
    return json.loads(result.stdout)


def substituted_source(source: str, definition: str, replacement: int) -> str:
    """Independent executable counterpart of an assignment-result substitution."""
    tree = parse(source)
    counts = defaultdict(int)
    found = False
    for stmt in tree.body[:-1]:
        name = stmt.targets[0].id
        counts[name] += 1
        if f"{name}@{counts[name]}" == definition:
            stmt.value = ast.parse(str(replacement), mode="eval").body
            found = True
    if not found:
        raise ValueError(definition)
    return ast.unparse(ast.fix_missing_locations(tree))
