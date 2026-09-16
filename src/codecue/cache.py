"""Hidden-state caching for the probe experiments: a forced pass over prompt + the GOLD trace,
recording the residual stream at labelled spans.

Positions (character spans -> token spans, last token), for the target role r:
    def@r       the identifier where it is defined            (`sum_all` in `sum_all = len(xs)`)
    rhs@r       the last token of its right-hand side         (`)` of `len(xs)`)
    end@r       the newline ending its defining statement
    call        the `)` of the call line
    pre@r       the token before the value the trace writes for r  -- the decision point
    anspre      the `:` of the final `Answer:`

`pre@r` is the position the paper is about: the model is one token away from writing r's value
and we ask what it holds. Layout is identical within a group (checked by the runner's guard), so
positions are absolute indices as in Kudo et al.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Sequence

import numpy as np
import torch

from .generator import Instance
from .layout import Span, spans_to_tokens
from .prompts import build_prompt, demo_block, demos, parse_regime


def trace_text(x: Instance) -> str:
    """The gold trace for x in the `trace` format (what the model is forced through)."""
    from .generator import Program, Stmt, trace_steps
    prog = Program(x.level, tuple(x.xs), tuple(Stmt(**d) for d in x.stmts), x.query, x.distractor)
    steps = trace_steps(prog, x.names, x.values)
    return " " + ", ".join(f"{n} = {v}" for n, v in steps) + f"\nAnswer: {x.answer}"


def cache_spans(prompt: str, gen: str, x: Instance, role: str) -> list[Span]:
    """Spans in prompt+gold-trace. The trace is appended, so `pre@r` lives in `gen`."""
    full = prompt + gen
    b = prompt.rfind(x.program)
    name = x.names[role]
    out: list[Span] = []
    m = re.search(rf"^\s*({re.escape(name)}) = (.+)$", x.program, re.M)
    out.append(Span(f"def@{role}", b + m.start(1), b + m.end(1)))
    out.append(Span(f"rhs@{role}", b + m.end(2) - 1, b + m.end(2)))
    line_end = x.program.find("\n", m.end())
    out.append(Span(f"end@{role}", b + line_end - 1, b + line_end))
    out.append(Span("call", b + len(x.program) - 1, b + len(x.program)))
    t = re.search(rf"\b{re.escape(name)} = ", gen)          # the trace's own step for this role
    if t:
        out.append(Span(f"pre@{role}", len(prompt) + t.end() - 2, len(prompt) + t.end() - 1))
    a = full.rfind("Answer:")
    out.append(Span("anspre", a + len("Answer:") - 1, a + len("Answer:")))
    return out


@torch.no_grad()
def cache_group(tok, model, instances: Sequence[Instance], role: str, regime: str, level: int,
                out_dir: Path, batch_size: int, layer_stride: int = 2) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    base, seed = parse_regime(regime)
    dem = demos(level, seed, base)
    prompts = [build_prompt(x, regime, dem) for x in instances]
    gens = [trace_text(x) for x in instances]
    enc = [tok(p + g, return_offsets_mapping=True, add_special_tokens=True) for p, g in zip(prompts, gens)]
    pos = []
    for e, p, g, x in zip(enc, prompts, gens, instances):
        pos.append(spans_to_tokens(cache_spans(p, g, x, role), e["offset_mapping"]))
    labels = sorted(set.intersection(*[set(d) for d in pos]))
    ref = tuple(pos[0][k] for k in labels)
    keep = [i for i, d in enumerate(pos) if tuple(d[k] for k in labels) == ref and len(enc[i]["input_ids"]) == len(enc[0]["input_ids"])]
    if len(keep) < 0.99 * len(instances):
        raise RuntimeError(f"{out_dir.name}: only {len(keep)}/{len(instances)} share a token layout")
    n_layers = model.config.num_hidden_layers + 1
    layers = list(range(0, n_layers, layer_stride))
    H = np.zeros((len(keep), len(labels), len(layers), model.config.hidden_size), dtype=np.float16)
    for i in range(0, len(keep), batch_size):
        chunk = keep[i:i + batch_size]
        ids = torch.tensor([enc[k]["input_ids"] for k in chunk]).to(model.device)
        hs = model(input_ids=ids, output_hidden_states=True).hidden_states
        st = torch.stack([hs[l] for l in layers], dim=2)          # [B, T, L, d]
        for b, k in enumerate(chunk):
            H[i + b] = st[b, [pos[k][lab] for lab in labels]].to(torch.float16).cpu().numpy()
    np.save(out_dir / "hidden.npy", H)
    meta = {"role": role, "level": level, "regime": regime, "pos_labels": labels, "layers": layers,
            "hidden_dim": int(model.config.hidden_size), "n": len(keep),
            "instances": [{"id": instances[k].id, "set_id": instances[k].set_id, "names": instances[k].names,
                           "values": instances[k].values, "lure": instances[k].lure, "target": instances[k].target,
                           "condition": instances[k].condition} for k in keep]}
    (out_dir / "meta.json").write_text(json.dumps(meta))
    return meta
