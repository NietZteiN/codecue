"""Model loading and greedy generation (copied from probing/src/cueconf/runner.py so the two
projects do not depend on each other's tree)."""
from __future__ import annotations

from typing import Sequence

import torch


def load_model(hf_id: str, dtype=torch.bfloat16, device: str = "cuda"):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(hf_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    try:
        model = AutoModelForCausalLM.from_pretrained(hf_id, dtype=dtype, device_map=device)
    except ValueError:
        from transformers import AutoModel
        model = AutoModel.from_pretrained(hf_id, dtype=dtype, device_map=device)
    model.eval()
    return tok, model


@torch.no_grad()
def generate_free(tok, model, prompts: Sequence[str], max_new_tokens: int, batch_size: int,
                  stop_at_blank_line: bool = True) -> list[str]:
    """Greedy decoding. For the few-shot regimes we stop at a blank line (the separator between
    worked examples), so a model that starts a new problem does not run to the token limit."""
    from transformers import StoppingCriteria, StoppingCriteriaList

    class BlankLine(StoppingCriteria):
        """Llama-2-family tokenizers emit a blank line as two '\\n' tokens, so no single eos id
        catches it; look at the decoded tail of every sequence instead."""
        def __init__(self, start: int):
            self.start = start
        def __call__(self, input_ids, scores, **kw):
            import torch as _t
            done = []
            for row in input_ids:
                tail = tok.decode(row[self.start:][-6:], skip_special_tokens=True)
                done.append("\n\n" in tail or "\n \n" in tail)
            return _t.tensor(done, device=input_ids.device)

    outs: list[str] = []
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        enc = tok(batch, return_tensors="pt", padding=True).to(model.device)
        crit = StoppingCriteriaList([BlankLine(enc["input_ids"].shape[1])]) if stop_at_blank_line else None
        gen = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                             pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id,
                             stopping_criteria=crit)
        outs.extend(tok.batch_decode(gen[:, enc["input_ids"].shape[1]:], skip_special_tokens=True))
    return outs
