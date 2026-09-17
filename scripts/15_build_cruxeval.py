#!/usr/bin/env python
"""E8 data: CRUXEval functions that assign a variable from `len(...)`, each rendered three ways:
    original    the author's name (often congruent: count, length, n)
    neutral     renamed to `v`
    misleading  renamed to `total`   (sum-family; one token in every tokenizer in the panel)
Renaming is AST-based (every binding and use of that name inside the function), and each
variant is executed on the CRUXEval input to confirm the output is unchanged. The true value of
the variable (the length) and, where the operand is summable, the lure value (its sum) are
recorded by instrumenting the assignment. Writes data/cruxeval_len.jsonl.
"""
from __future__ import annotations

import ast
import glob
import json
import os
import sys
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
ROOT = Path(__file__).resolve().parents[1]


class Rename(ast.NodeTransformer):
    def __init__(self, old, new): self.old, self.new = old, new
    def visit_Name(self, node):
        if node.id == self.old: node.id = self.new
        return node
    def visit_arg(self, node):
        if node.arg == self.old: node.arg = self.new
        return node


def run(code: str, call: str, timeout_ok=True):
    ns = {}
    exec(code, ns)
    return eval(call, ns)


def main() -> int:
    base = glob.glob("/scratch/juno/jvl210002/hf_home/hub/datasets--cruxeval-org--cruxeval/snapshots/*/")[0]
    rows = [json.loads(l) for l in open(base + "test.jsonl")]
    out, skipped = [], {}
    for r in rows:
        try:
            t = ast.parse(r["code"])
        except SyntaxError:
            continue
        target = None
        for node in ast.walk(t):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                v = node.value
                if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in ("len", "max", "min") and len(v.args) == 1:
                    target = (node.targets[0].id, ast.unparse(v.args[0]), v.func.id); break
        if not target:
            # loop counter: `name = 0` then `name += 1` somewhere later (code says COUNT)
            inits = {n.targets[0].id for n in ast.walk(t) if isinstance(n, ast.Assign) and len(n.targets) == 1
                     and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant) and n.value.value == 0}
            for n in ast.walk(t):
                if (isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id in inits
                        and isinstance(n.op, ast.Add) and isinstance(n.value, ast.Constant) and n.value.value == 1):
                    target = (n.target.id, None, "counter"); break
        if not target:
            continue
        name, operand, kind = target
        if name in ("v", "total") or any(n in r["code"] for n in (" v ", "total")):
            skipped[r["id"]] = "name clash"; continue
        call = f"f({r['input']})"
        try:
            gold = run(r["code"], call)
        except Exception as e:
            skipped[r["id"]] = f"exec: {type(e).__name__}"; continue
        # instrument: record the variable's value and the operand's sum at the assignment
        rec = {"len": None, "sum": None}
        probe_code = ast.unparse(t)
        class Instr(ast.NodeTransformer):
            def visit_Assign(self, node):
                if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name
                        and isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) in ("len", "max", "min")):
                    rec_call = ast.parse(f"__rec__({name}, {operand})").body[0]
                    return [node, rec_call]
                return node
        ti = Instr().visit(ast.parse(r["code"])); ast.fix_missing_locations(ti)
        def __rec__(val, opnd):
            if rec["len"] is None:
                rec["len"] = val
                try: rec["sum"] = sum(opnd) if not isinstance(opnd, (str, dict)) else None
                except Exception: rec["sum"] = None
        if kind == "counter":
            rec["len"], rec["sum"] = None, None       # no single "true value" for an accumulator
        else:
            try:
                ns = {"__rec__": __rec__}; exec(ast.unparse(ti), ns); eval(call, ns)
            except Exception as e:
                skipped[r["id"]] = f"instr: {type(e).__name__}"; continue
        variants = {"original": r["code"]}
        ok = True
        for cond, new in (("neutral", "v"), ("misleading", "total")):
            t2 = Rename(name, new).visit(ast.parse(r["code"])); code2 = ast.unparse(t2)
            try:
                if run(code2, call) != gold: ok = False
            except Exception:
                ok = False
            variants[cond] = code2
        if not ok:
            skipped[r["id"]] = "rename changed output"; continue
        for cond, code in variants.items():
            out.append({"id": f"{r['id']}-{cond}", "src": r["id"], "condition": cond, "code": code, "call": call,
                        "output": r["output"], "orig_name": name, "name": {"original": name, "neutral": "v", "misleading": "total"}[cond],
                        "operand": operand, "true_len": rec["len"], "lure_sum": rec["sum"], "kind": kind})
    (ROOT / "data" / "cruxeval_len.jsonl").write_text("".join(json.dumps(x) + "\n" for x in out))
    n = len(out) // 3
    from collections import Counter
    print(f"{n} functions x 3 conditions; by kind: {dict(Counter(x['kind'] for x in out if x['condition']=='misleading'))}; "
          f"lure (sum) defined for {sum(1 for x in out if x['condition']=='misleading' and x['lure_sum'] is not None)}")
    print("skipped:", dict(sorted(__import__('collections').Counter(skipped.values()).items())))
    for x in out[:3]:
        print("---", x["id"], "name", x["name"], "len", x["true_len"], "sum", x["lure_sum"]); print(x["code"][:160])
    return 0


if __name__ == "__main__":
    sys.exit(main())
