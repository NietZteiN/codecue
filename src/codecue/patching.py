"""Activation patching for the code task, adapted from the arithmetic project.

The twins do NOT share a token layout here (`sum_all` and `v` tokenize to different lengths and
shift everything after them), so positions are resolved per instance from spans and the patch is
span-to-span: the residual stream at the SOURCE's span (last token) is written into the
DESTINATION's span (last token). Two patch sites, read at the decision token `pre@v1`:

    name    the identifier's last token at its definition (`def@v1`): is the name the cause?
    pre     the decision token itself: at which layer does the readout diverge?

Contrasts:
    main      source neutral twin       -> dest incongruent   lure removed?
    ctl_word  source neutral_alt        -> dest neutral        damage of an arbitrary swap
    ctl_lure  source incongruent_alt    -> dest incongruent    does the output follow the NEW lure?
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Sequence

import torch


def decoder_layers(model):
    for attr in ("model.layers", "model.language_model.layers", "language_model.model.layers", "transformer.h"):
        obj = model
        try:
            for a in attr.split("."):
                obj = getattr(obj, a)
            return list(obj)
        except AttributeError:
            continue
    raise AttributeError("cannot find decoder layers")


@contextmanager
def patch_hooks(model, layer_ids: Sequence[int], positions: Sequence[int], source: dict[int, torch.Tensor]):
    layers = decoder_layers(model); handles = []; pos_t = torch.tensor(list(positions))
    def make_hook(l):
        def hook(module, args, output):
            hs = output[0] if isinstance(output, tuple) else output
            hs[:, pos_t, :] = source[l].to(hs.dtype).to(hs.device)
            return output
        return hook
    for l in layer_ids:
        handles.append(layers[l].register_forward_hook(make_hook(l)))
    try:
        yield
    finally:
        for h in handles:
            h.remove()


@torch.no_grad()
def hidden_at(model, input_ids: list[int], layer_ids: Sequence[int], positions: Sequence[int]) -> dict[int, torch.Tensor]:
    out = model(input_ids=torch.tensor([input_ids], device=model.device), output_hidden_states=True)
    return {l: out.hidden_states[l + 1][0, list(positions), :].clone() for l in layer_ids}


def digit_token_ids(tok) -> dict[str, list[int]]:
    out = {}
    for d in "0123456789":
        ids = set()
        for s in (d, " " + d):
            e = tok(s, add_special_tokens=False)["input_ids"]
            if len(e) == 1: ids.add(e[0])
        out[d] = sorted(ids)
    return out


@torch.no_grad()
def digit_scores(model, tok_digits: dict[str, list[int]], input_ids: list[int], pos: int) -> dict[str, float]:
    out = model(input_ids=torch.tensor([input_ids], device=model.device))
    lp = torch.log_softmax(out.logits[0, pos].float(), -1)
    return {d: float(torch.logsumexp(lp[ids], 0)) if ids else -1e9 for d, ids in tok_digits.items()}


def layer_sets(n_layers: int, window: int = 4) -> list[tuple[str, list[int]]]:
    sets = [(f"L{l}", [l]) for l in range(n_layers)]
    sets += [(f"W{a}-{min(a + window, n_layers) - 1}", list(range(a, min(a + window, n_layers)))) for a in range(0, n_layers, window)]
    sets.append(("ALL", list(range(n_layers))))
    return sets
