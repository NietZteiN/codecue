"""HF adapter using CodeCue generation and decoder hooks, with pinned provenance."""
from __future__ import annotations

from codecue.layout import Span, spans_to_tokens

PROTOCOLS = ("short_answer_chat_v1", "short_answer_prefill_v2")


def normalize_prompt(tokenizer, prompt):
    """Explicitly opt in to the independently audited CodeLlama BOS boundary."""
    if not getattr(tokenizer, 'binding_official_boundary', False):
        return prompt
    marker=tokenizer.bos_token+'[INST]'
    corrected=tokenizer.bos_token+' [INST]'
    if prompt.startswith(corrected):
        rendered=prompt
    elif prompt.startswith(marker):
        rendered=corrected+prompt[len(marker):]
    else:
        raise ValueError('official CodeLlama correction requires the audited single-turn chat prefix')
    reference=getattr(tokenizer,'binding_sp_model',None)
    if reference is not None:
        expected=[reference.bos_id()]+reference.encode(rendered[len(tokenizer.bos_token)+1:])
        if tokenizer(rendered,add_special_tokens=False)['input_ids']!=expected:
            raise ValueError('complete prompt differs from official SentencePiece tokenization')
    return rendered


def prompt_for(tokenizer, record, protocol='short_answer_chat_v1'):
    content = ("Execute this straight-line Python program. The final expression is the output. "
               "Reply with only its signed integer value.\n\n```python\n" + record["source"] + "\n```")
    if protocol not in PROTOCOLS:
        raise ValueError('unknown prompt protocol')
    if not getattr(tokenizer, "chat_template", None):
        raise ValueError("the frozen short_answer_chat_v1 protocol requires a chat template")
    if protocol == 'short_answer_prefill_v2':
        return normalize_prompt(tokenizer,tokenizer.apply_chat_template([{'role':'user', 'content':content},
                                             {'role':'assistant', 'content':'Answer:'}],
                                            tokenize=False, continue_final_message=True))
    return normalize_prompt(tokenizer,tokenizer.apply_chat_template([{"role": "user", "content": content}], tokenize=False, add_generation_prompt=True))


def configure_tokenizer(tokenizer,config):
    default='codellama_official_boundary_v1' if config['model'].startswith('codellama/') else 'native'
    mode=config.get('tokenization_mode',default)
    if mode not in ('native','codellama_official_boundary_v1') or (mode!='native' and not config['model'].startswith('codellama/')):
        raise ValueError('unsupported tokenizer boundary mode for this checkpoint')
    tokenizer.binding_official_boundary=mode=='codellama_official_boundary_v1'
    if tokenizer.binding_official_boundary:
        import sentencepiece
        from huggingface_hub import try_to_load_from_cache
        path=try_to_load_from_cache(config['model'],'tokenizer.model',revision=config['tokenizer_revision'])
        if not isinstance(path,str):
            raise ValueError('official SentencePiece file must already be cached')
        tokenizer.binding_sp_model=sentencepiece.SentencePieceProcessor(model_file=path)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    if hasattr(tokenizer, 'add_bos_token'):
        tokenizer.add_bos_token = False  # chat templates already contain BOS
    return tokenizer


def load(config):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if config['device'] == 'cpu':
        torch.set_num_threads(config.get('cpu_threads', 4))
    if config["protocol"] not in PROTOCOLS:
        raise ValueError("unknown prompt protocol")
    for key in ("model_revision", "tokenizer_revision"):
        if len(config[key]) != 40 or any(c not in "0123456789abcdef" for c in config[key]):
            raise ValueError("pin model and tokenizer to exact 40-character commits")
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=config["tokenizer_revision"], local_files_only=True)
    configure_tokenizer(tokenizer,config)
    model = AutoModelForCausalLM.from_pretrained(config["model"], revision=config["model_revision"],
        dtype=getattr(torch, config["dtype"]), device_map=config["device"], local_files_only=True,
        attn_implementation="eager")
    model.eval()
    return tokenizer, model


def layout(tokenizer, record, prompt):
    encoded = tokenizer(prompt, return_offsets_mapping=True, add_special_tokens=False)
    start = prompt.rfind(record["source"])
    if start < 0:
        raise ValueError("source not found in prompt")
    spans = [Span(f"statement:{s['statement']}", start + s["end"] - 1, start + s["end"])
             for s in record["statement_spans"][:-1]]
    output = record["statement_spans"][-1]
    spans.append(Span("source_final", start + output["end"] - 1, start + output["end"]))
    mapped = spans_to_tokens(spans, encoded["offset_mapping"])
    # A token straddling the next statement would leak its future assignment.
    offsets = encoded["offset_mapping"]
    for span in spans:
        a, b = offsets[mapped[span.key]]
        if b > span.end:
            raise ValueError(f"token crosses checkpoint boundary: {span.key}")
    identifier_counts = {}
    import re
    for name in record["rename_map"].values():
        occurrences = list(re.finditer(rf"\b{re.escape(name)}\b", record["source"]))
        identifier_counts[name] = [sum(a < start + m.end() and b > start + m.start() for a, b in offsets)
                                   for m in occurrences]
    return {"input_ids": encoded["input_ids"], "offsets": offsets, "positions": mapped,
            "token_counts": {"prompt": len(encoded["input_ids"]),
                             "source": len(tokenizer(record["source"], add_special_tokens=False)["input_ids"]),
                             "identifiers": identifier_counts},
            "hook_convention": "raw decoder block output, zero-based block index; no final normalization"}


def score_answers(tokenizer, model, prompt, candidates):
    """Unnormalized sum of log probabilities of COMPLETE answer strings.

    Explicit newline boundary prevents silent prefix retokenization. Candidate set,
    boundary and all token IDs accompany every score. No digit-only scoring.
    """
    import torch
    boundary = prompt + "\n"
    prefix = tokenizer(boundary, add_special_tokens=False)["input_ids"]
    result = []
    with torch.inference_mode():
        for answer in sorted(set(candidates)):
            completion = str(answer)
            ids = tokenizer(boundary + completion, add_special_tokens=False)["input_ids"]
            if ids[:len(prefix)] != prefix or len(ids) == len(prefix):
                raise ValueError("candidate retokenizes the frozen boundary")
            output = model(input_ids=torch.tensor([ids], device=model.device), use_cache=False)
            logp = output.logits[0, len(prefix)-1:-1].float().log_softmax(-1)
            targets = torch.tensor(ids[len(prefix):], device=model.device)
            result.append({"answer": answer, "completion": completion, "token_ids": ids[len(prefix):],
                           "log_likelihood_sum": float(logp.gather(1, targets[:, None]).sum())})
    return {"boundary": "prompt plus newline", "normalization": "none", "scores": result}
