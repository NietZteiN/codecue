"""Run a model's completion on hidden inputs, out of process.

E7 is the only place in either project that executes text a model wrote, so it does not run it
in the analysis process. `run_completion` starts a fresh interpreter with `-I` (ignore the
environment and the user site directory), hands it the code on stdin rather than argv, and gives
it a wall-clock timeout. Inside, the code is compiled and executed in a namespace holding only
the builtins this task needs, with no import machinery, so an `import` in a completion raises
rather than reaching the filesystem or the network.

This is a guard against a model emitting something silly on our own cluster, not a security
boundary. Nothing here should ever be pointed at untrusted input from outside the project.
"""
from __future__ import annotations

import json
import subprocess
import sys

ALLOWED_BUILTINS = ("len", "sum", "max", "min", "abs", "sorted", "range", "list", "int",
                    "enumerate", "zip", "reversed", "map", "filter", "round", "bool", "all", "any")

HARNESS = r'''
import json, sys
payload = json.loads(sys.stdin.read())
allowed = %r
bi = {k: getattr(__builtins__, k, None) if not isinstance(__builtins__, dict) else __builtins__.get(k)
      for k in allowed}
bi = {k: v for k, v in bi.items() if v is not None}
ns = {"__builtins__": bi}
out = []
try:
    exec(compile(payload["code"], "<completion>", "exec"), ns)
    f = ns.get("f")
    if f is None:
        print(json.dumps({"error": "no function f"})); sys.exit(0)
    for x in payload["inputs"]:
        try:
            v = f(list(x))
            out.append(int(v) if isinstance(v, (int, bool)) else None)
        except Exception as e:
            out.append(None)
except Exception as e:
    print(json.dumps({"error": "%%s: %%s" %% (type(e).__name__, e)})); sys.exit(0)
print(json.dumps({"outputs": out}))
''' % (ALLOWED_BUILTINS,)


def run_completion(code: str, inputs, timeout: float = 5.0) -> dict:
    """{'outputs': [int|None, ...]} or {'error': str}. Never raises."""
    try:
        p = subprocess.run([sys.executable, "-I", "-c", HARNESS],
                           input=json.dumps({"code": code, "inputs": [list(x) for x in inputs]}),
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    if p.returncode != 0:
        return {"error": f"exit {p.returncode}: {p.stderr.strip()[:200]}"}
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return {"error": f"unparsable harness output: {p.stdout[:200]}"}


def assemble(prompt_body: str, completion: str) -> str:
    """The function the model actually wrote: its prefix plus the first line it generated.

    The prompt ends at a bare `return`, so the completion is the expression that follows it. We
    keep only the first line and stop at a blank line, the same rule the answer parser uses, and
    fall back to treating the completion as a whole body when it restates `def f`.
    """
    c = completion.split("\n\n", 1)[0]
    if "def f(" in c:                        # the model rewrote the function
        start = c.index("def f(")
        return c[start:]
    first = c.split("\n", 1)[0].strip()
    return f"{prompt_body} {first}\n"
