"""Program generator: levels, naming conditions, matched twins, executable lures.

An INSTANCE is one program in one naming condition. A MATCHED SET is the same program under
every condition: identical statements, operations and input, differing only in ONE identifier
(rule 1). Every comparison in the paper is within matched sets.

Programs are straight-line Python functions of one list `xs`, returning one variable:

    L1  v1 = L(xs)                                  ; return v1        1 step
    L2  v1 = L(xs); v2 = U(v1)                      ; return v2        2-step chain (in order)
    L3  v1 = L(xs); v2 = L'(xs); v3 = B(v1, v2)     ; return v3        two branches, combined  <- main
    L4  L3 with an unused distractor v4 = L''(xs) between v2 and v3
    L5  v1 = L(xs); v2 = U(v1); v3 = U'(v2)         ; return v3        3-step chain

L = list op (sum/len/max/min), U = unary op (+c, -c, *2, //2), B = binary op (+, -, *).
Every variable's value and the answer are in D = {0..9}; `xs` has 2–4 distinct ints in 0..6.
Probe targets are therefore single digits, as in the arithmetic paper.

Conditions:
    neutral          every name from NEUTRAL_NAMES                       (comparison point)
    congruent        the TARGET is named by a name whose implied op IS its definition
    incongruent      the TARGET is named by a name whose implied value differs (the lure)
    irrelevant       (L4) the DISTRACTOR carries the misleading name; the chain is neutral
    neutral_alt      neutral with a different neutral name in the target slot (patch control)
    incongruent_alt  incongruent with a different lure                    (patch control)

Rules, tested in tests/test_generator.py:
    R1  exactly one table name per instance; twins differ in exactly one identifier
    R2  the lure value is in D, differs from EVERY variable's value, from every element of xs
        and from every constant in the program: a lure answer can only come from the name,
        and the lure is never written anywhere in the prompt
    R3  no table name appears in the program other than as the target's identifier
    R4  the true and lure values are both obtained by EXECUTING the program (`execute`)
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from .lures import FAMILY, FAMILY_OF_NAME, LURE_NAMES, NEUTRAL_NAMES, implied_value

DIGITS = range(10)
LIST_OPS = ("sum", "len", "max", "min")
UNARY_OPS = ("+c", "-c", "*2", "//2")
BINARY_OPS = ("+", "-", "*")
CONDITIONS = ("neutral", "congruent", "incongruent", "irrelevant", "neutral_alt", "incongruent_alt")
LURE_CONDITIONS = ("congruent", "incongruent", "irrelevant", "incongruent_alt")


@dataclass(frozen=True)
class Stmt:
    lhs: str                    # role: v1..v4
    kind: str                   # list | unary | binary
    op: str                     # one of LIST_OPS / UNARY_OPS / BINARY_OPS
    args: tuple[str, ...]       # roles used (unary: 1, binary: 2, list: none)
    const: int | None = None    # the c in +c / -c

    def source(self, names: dict[str, str]) -> str:
        if self.kind == "list":
            return f"{names[self.lhs]} = {self.op}(xs)"
        a = names[self.args[0]]
        if self.kind == "unary":
            rhs = {"+c": f"{a} + {self.const}", "-c": f"{a} - {self.const}", "*2": f"{a} * 2", "//2": f"{a} // 2"}[self.op]
            return f"{names[self.lhs]} = {rhs}"
        return f"{names[self.lhs]} = {a} {self.op} {names[self.args[1]]}"

    def family_key(self) -> str | None:
        """The lure family whose operation equals this definition, if any (congruent name)."""
        if self.kind == "list":
            return self.op
        if self.kind == "unary":
            return {"*2": "double", "//2": "half"}.get(self.op) or (
                "succ" if (self.op, self.const) == ("+c", 1) else "pred" if (self.op, self.const) == ("-c", 1) else None)
        return {"+": "add", "-": "sub", "*": "mul"}[self.op]


LEVELS: dict[int, dict] = {
    1: {"stmts": [("v1", "list", ())], "query": "v1", "distractor": None, "steps": 1},
    2: {"stmts": [("v1", "list", ()), ("v2", "unary", ("v1",))], "query": "v2", "distractor": None, "steps": 2},
    3: {"stmts": [("v1", "list", ()), ("v2", "list", ()), ("v3", "binary", ("v1", "v2"))], "query": "v3", "distractor": None, "steps": 3},
    4: {"stmts": [("v1", "list", ()), ("v2", "list", ()), ("v4", "list", ()), ("v3", "binary", ("v1", "v2"))], "query": "v3", "distractor": "v4", "steps": 3},
    5: {"stmts": [("v1", "list", ()), ("v2", "unary", ("v1",)), ("v3", "unary", ("v2",))], "query": "v3", "distractor": None, "steps": 3},
    # 6 = the level-5 program with the MIDDLE unary step as the target (added 2026-09-16 to test
    # whether strong-prior unary names — double/half/succ/pred, gate 100% — contaminate a
    # middle step the way sum-names contaminate the first). Same prompts as level 5.
    6: {"stmts": [("v1", "list", ()), ("v2", "unary", ("v1",)), ("v3", "unary", ("v2",))], "query": "v3", "distractor": None, "steps": 3},
}


@dataclass
class Program:
    level: int
    xs: tuple[int, ...]
    stmts: tuple[Stmt, ...]
    query: str
    distractor: str | None = None

    @property
    def roles(self) -> list[str]:
        return [s.lhs for s in self.stmts]

    def stmt(self, role: str) -> Stmt:
        return next(s for s in self.stmts if s.lhs == role)

    def constants(self) -> set[int]:
        return {s.const for s in self.stmts if s.const is not None} | ({2} if any(s.op in ("*2", "//2") for s in self.stmts) else set())


@dataclass
class Instance:
    id: str
    set_id: str
    level: int
    condition: str
    target: str | None          # role carrying the table name (None for neutral)
    names: dict[str, str]
    xs: list[int]
    program: str                # the rendered function + call, exactly as prompted
    values: dict[str, int]      # role -> executed value
    answer: int
    lure: int | None            # implied value of the target's name, or None
    lure_name: str | None
    query: str
    distractor: str | None
    stmts: list[dict] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


# ---------------------------------------------------------------- rendering and execution

def render_function(prog: Program, names: dict[str, str], fname: str = "f") -> str:
    body = "\n".join("    " + s.source(names) for s in prog.stmts)
    return f"def {fname}(xs):\n{body}\n    return {names[prog.query]}"


def render_call(prog: Program, fname: str = "f") -> str:
    return f"{fname}({list(prog.xs)})"


def render(prog: Program, names: dict[str, str]) -> str:
    return render_function(prog, names) + "\n" + render_call(prog)


def execute(prog: Program, names: dict[str, str], override: dict[str, str] | None = None) -> dict[str, int]:
    """Run the program (rule R4) and return every variable's value plus 'return'.

    `override` maps a role to replacement Python source for its right-hand side, which is how a
    lure is executed: the misleading name's implied operation is substituted for the true
    definition and the program is run again."""
    ns: dict = {"xs": list(prog.xs)}
    for s in prog.stmts:
        src = s.source(names)
        if override and s.lhs in override:
            src = f"{names[s.lhs]} = {override[s.lhs]}"
        exec(src, {"__builtins__": {"sum": sum, "len": len, "max": max, "min": min}}, ns)
    vals = {r: ns[names[r]] for r in prog.roles}
    vals["return"] = ns[names[prog.query]]
    return vals


def evaluate(prog: Program) -> dict[str, int]:
    """Values under role names (independent of the naming condition)."""
    ident = {r: r for r in prog.roles}
    return execute(prog, ident)


def trace_steps(prog: Program, names: dict[str, str], values: dict[str, int]) -> list[tuple[str, int]]:
    """(name, value) per statement in program order: what the trace regime writes."""
    return [(names[s.lhs], values[s.lhs]) for s in prog.stmts]


# ---------------------------------------------------------------- sampling

def sample_program(level: int, rng: random.Random, max_tries: int = 10_000) -> Program:
    spec = LEVELS[level]
    for _ in range(max_tries):
        n = rng.choice((2, 3, 4))
        xs = tuple(rng.sample(range(0, 7), n))
        stmts = []
        for lhs, kind, args in spec["stmts"]:
            if kind == "list":
                stmts.append(Stmt(lhs, kind, rng.choice(LIST_OPS), ()))
            elif kind == "unary":
                op = rng.choice(UNARY_OPS)
                stmts.append(Stmt(lhs, kind, op, args, rng.randint(1, 4) if op in ("+c", "-c") else None))
            else:
                stmts.append(Stmt(lhs, kind, rng.choice(BINARY_OPS), args))
        prog = Program(level, xs, tuple(stmts), spec["query"], spec["distractor"])
        vals = evaluate(prog)
        if all(v in DIGITS for v in vals.values()) and len(set(vals[r] for r in prog.roles)) == len(prog.roles):
            # distinct variable values, so a probe target is never ambiguous and rule R2 is meaningful
            return prog
    raise RuntimeError(f"no legal program at level {level} after {max_tries} tries")


def legal_lures(prog: Program, target: str, values: dict[str, int]) -> list[tuple[str, int]]:
    """(name, lure value) pairs satisfying R2 for `target`."""
    s = prog.stmt(target)
    operands = [values[a] for a in s.args]
    forbidden = set(values[r] for r in prog.roles) | set(prog.xs) | prog.constants()
    out = []
    for name in LURE_NAMES:
        fam = FAMILY_OF_NAME[name]
        if fam.key == s.family_key():
            continue                                        # that is the congruent name
        # a unary or binary name is only a clear assertion when the definition has the same
        # shape (`double = ww + p` does not clearly assert 2*ww); list names assert something
        # about xs and are clear anywhere (hand check, 2026-09-14)
        if fam.kind != "list" and fam.kind != s.kind:
            continue
        lv = implied_value(name, prog.xs, operands)
        if lv is None or lv not in DIGITS or lv in forbidden:
            continue
        # R4: the lure must also be what the program returns when the implied op is substituted
        out.append((name, lv))
    return out


def congruent_names(prog: Program, target: str) -> tuple[str, ...]:
    key = prog.stmt(target).family_key()
    return FAMILY[key].names if key else ()


def lure_by_execution(prog: Program, names: dict[str, str], target: str, name: str) -> int:
    """The lure as executed: substitute the implied operation for the target's definition."""
    fam = FAMILY_OF_NAME[name]
    s = prog.stmt(target)
    src = fam.source
    if fam.kind == "unary":
        src = src.replace("a", names[s.args[0]])
    elif fam.kind == "binary":
        src = src.replace("a", names[s.args[0]]).replace("b", names[s.args[1]])
    return execute(prog, names, {target: src})[target]


def make_set(prog: Program, set_id: str, rng: random.Random, target: str) -> list[Instance] | None:
    """All conditions for one program and one target role, or None if no legal lure exists."""
    values = evaluate(prog)
    lures = legal_lures(prog, target, values)
    cong = congruent_names(prog, target)
    if len(lures) < 2 or not cong:
        return None
    roles = prog.roles
    neutral_pool = list(NEUTRAL_NAMES)
    rng.shuffle(neutral_pool)
    base = {r: neutral_pool[i] for i, r in enumerate(roles)}
    alt_neutral = neutral_pool[len(roles)]
    (l1, lv1), (l2, lv2) = rng.sample(lures, 2)
    cname = rng.choice(cong)
    out = []

    def inst(cond, tgt, names, lure, lure_name):
        text = render(prog, names)
        vals = execute(prog, names)
        assert vals == values, "renaming changed the semantics"
        if lure is not None:
            assert lure_by_execution(prog, names, tgt, lure_name) == lure, "table lure != executed lure"
        return Instance(id=f"{set_id}-{cond}", set_id=set_id, level=prog.level, condition=cond, target=tgt,
                        names=dict(names), xs=list(prog.xs), program=text, values={r: values[r] for r in roles},
                        answer=values["return"], lure=lure, lure_name=lure_name, query=prog.query,
                        distractor=prog.distractor, stmts=[asdict(s) for s in prog.stmts])

    out.append(inst("neutral", None, base, None, None))
    out.append(inst("neutral_alt", None, {**base, target: alt_neutral}, None, None))
    out.append(inst("congruent", target, {**base, target: cname}, None, cname))
    out.append(inst("incongruent", target, {**base, target: l1}, lv1, l1))
    out.append(inst("incongruent_alt", target, {**base, target: l2}, lv2, l2))
    if prog.distractor and target == prog.query:
        dl = legal_lures(prog, prog.distractor, values)
        if dl:
            dn, dv = rng.choice(dl)
            out.append(inst("irrelevant", prog.distractor, {**base, prog.distractor: dn}, dv, dn))
    return out


def targets_for(level: int) -> list[str]:
    if level == 6:
        return ["v2"]
    spec = LEVELS[level]
    q = spec["query"]
    inter = [r for r, _, _ in spec["stmts"] if r != q and r != spec["distractor"]]
    return [q] + inter[:1]          # queried variable, and the first intermediate


def sample_sets(level: int, n: int, seed: int, tag: str = "", strict: bool = True) -> Iterator[list[Instance]]:
    """`n` matched sets per target role, unique at the rendered-program level. Level 1 has only
    ~1,800 distinct programs (one list op over short inputs); with strict=False the generator
    yields what exists and the caller records the shortfall."""
    rng = random.Random(seed * 1000 + level)
    for target in targets_for(level):
        seen: set[str] = set()
        made = tries = 0
        while made < n:
            tries += 1
            if tries > 200 * n:
                if strict:
                    raise RuntimeError(f"L{level}/{target}: only {made}/{n} unique sets after {tries} tries")
                import warnings
                warnings.warn(f"L{level}/{target}: only {made}/{n} unique sets exist; using them")
                break
            prog = sample_program(level, rng)
            key = render(prog, {r: r for r in prog.roles})
            if key in seen:
                continue
            s = make_set(prog, f"L{level}{tag}-{seed}-{target}-{made:05d}", rng, target)
            if s is None:
                continue
            seen.add(key)
            made += 1
            yield s


# ---------------------------------------------------------------- io

def write_jsonl(path: Path, instances: Iterable[Instance]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w") as f:
        for x in instances:
            f.write(x.to_json() + "\n")
            n += 1
    return n


def read_jsonl(path: Path) -> list[Instance]:
    return [Instance(**json.loads(l)) for l in path.open()]


def content_hash(instances: Iterable[Instance]) -> str:
    h = hashlib.sha256()
    for x in instances:
        h.update(x.to_json().encode())
    return h.hexdigest()[:16]
