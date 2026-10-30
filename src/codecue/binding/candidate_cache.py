"""Teacher-forced candidate-event tries with one cached prompt prefill.

Models and typed event banks are injected. The cache contract is the modern HF
``batch_select_indices`` in-place API: duplicate indices replicate a parent and
discarded parents are never used again. No tokenizer/model loading or generation
occurs here. Incompatibility or capacity errors are explicit; fallback selection
belongs to the caller and cannot silently change the event definition.
"""
from __future__ import annotations

import inspect

from .candidate_confidence import summarize_events, validate_bank

BACKEND = 'cached_prefix_trie_v1'


def _trie(bank):
    root = {'children': {}, 'event': None}
    widths = []
    for index, event in enumerate(bank['events']):
        node = root
        for depth, token in enumerate(event['event_token_ids']):
            if token not in node['children']:
                node['children'][token] = {'children': {}, 'event': None}
                if depth < len(event['event_token_ids']) - 1:
                    while len(widths) <= depth: widths.append(0)
                    widths[depth] += 1
            node = node['children'][token]
        node['event'] = index
    return root, widths


def _explicit_cache_position(model):
    target = getattr(model, 'forward', model.__call__)
    try: return 'cache_position' in inspect.signature(target).parameters
    except (TypeError, ValueError): return False


def _last_log_probabilities(output, batch):
    import torch
    logits = output.logits
    if logits.ndim != 3 or logits.shape[:2] != (batch, 1) or logits.shape[-1] < 2:
        raise ValueError('cached scorer requires logits_to_keep=1 batch-by-one-by-vocabulary logits')
    logits = logits[:, 0, :].float()
    if torch.isnan(logits).any() or torch.isposinf(logits).any() or not torch.isfinite(logits).any(-1).all():
        raise ValueError('each causal distribution needs finite mass and no NaN or positive infinity')
    return logits.log_softmax(-1)


def _checked_cache(output, expected_length):
    cache = getattr(output, 'past_key_values', None)
    if (cache is None or not callable(getattr(cache, 'batch_select_indices', None))
            or not callable(getattr(cache, 'get_seq_length', None))):
        raise ValueError('modern HF cache with in-place batch_select_indices/get_seq_length required')
    if int(cache.get_seq_length()) != expected_length:
        raise ValueError('cache sequence length differs from the fixed-width padded causal history')
    return cache


def score_banks(model, banks, *, prompt_batch_size=4, pad_token_id=0, max_active_nodes=2048):
    """Return event summaries in bank order with shared-batch execution counters.

    Root prompt padding remains in the physical KV sequence. Semantic RoPE
    positions count only unmasked tokens; optional ``cache_position`` counts the
    physical padded width. Each continuation call appends exactly one non-EOS
    token per trie node. Terminal EOS probabilities are read without forwarding
    EOS. All branches at one depth are selected together before cache mutation.
    """
    import torch
    for value, label in ((prompt_batch_size, 'prompt_batch_size'), (max_active_nodes, 'max_active_nodes')):
        if type(value) is not int or value < 1: raise ValueError('positive integer ' + label + ' required')
    if type(pad_token_id) is not int or pad_token_id < 0: raise ValueError('nonnegative pad token ID required')
    if getattr(model, 'training', False): raise ValueError('teacher-forced model must be in evaluation mode')
    banks = list(banks)
    for bank in banks: validate_bank(bank)
    prepared = [_trie(bank) for bank in banks]
    # Check all batches before any expensive model call, rather than failing mid-bank.
    capacity = getattr(getattr(model, 'config', None), 'max_position_embeddings', None)
    for start in range(0, len(banks), prompt_batch_size):
        block = banks[start:start + prompt_batch_size]
        tries = prepared[start:start + prompt_batch_size]
        depth = max((len(widths) for _, widths in tries), default=0)
        active = [len(block)] + [sum(widths[d] if d < len(widths) else 0 for _, widths in tries) for d in range(depth)]
        if max(active) > max_active_nodes:
            raise ValueError('candidate trie exceeds max_active_nodes; reduce prompt_batch_size or explicitly raise capacity')
        required = max(len(bank['input_token_ids']) for bank in block) + depth
        if type(capacity) is int and capacity > 0 and required > capacity:
            raise ValueError('prompt plus candidate continuation exceeds declared model context capacity')
    results = []
    explicit_positions = _explicit_cache_position(model)
    with torch.inference_mode():
        for start in range(0, len(banks), prompt_batch_size):
            block = banks[start:start + prompt_batch_size]
            tries = prepared[start:start + prompt_batch_size]
            width = max(len(bank['input_token_ids']) for bank in block)
            prompts = [bank['input_token_ids'] for bank in block]
            input_ids = torch.tensor([[pad_token_id] * (width - len(ids)) + ids for ids in prompts],
                                     dtype=torch.long, device=model.device)
            masks = torch.tensor([[0] * (width - len(ids)) + [1] * len(ids) for ids in prompts],
                                 dtype=torch.long, device=model.device)
            positions = (masks.cumsum(-1) - 1).masked_fill(masks == 0, 1)
            encoded = dict(input_ids=input_ids, attention_mask=masks, position_ids=positions,
                           use_cache=True, logits_to_keep=1)
            if explicit_positions: encoded['cache_position'] = torch.arange(width, device=model.device)
            output = model(**encoded)
            cache = _checked_cache(output, width)
            probabilities = _last_log_probabilities(output, len(block))
            # Each active entry owns one row in the current cache, mask and logits.
            active = [(index, root, 0.) for index, (root, _) in enumerate(tries)]
            values = [[None] * len(bank['events']) for bank in block]
            calls = 1; depth = 0; maximum = len(active)
            while active:
                parents = []; tokens = []; next_active = []
                edge_rows = []; edge_tokens = []; edges = []
                for parent_index, (bank_index, node, accumulated) in enumerate(active):
                    for token, child in sorted(node['children'].items()):
                        if token >= probabilities.shape[-1]: raise ValueError('candidate token outside model vocabulary')
                        edge_rows.append(parent_index); edge_tokens.append(token)
                        edges.append((parent_index, bank_index, child, accumulated, token))
                # Transfer only needed edge probabilities, once per trie depth.
                rows = torch.tensor(edge_rows, dtype=torch.long, device=probabilities.device)
                targets = torch.tensor(edge_tokens, dtype=torch.long, device=probabilities.device)
                log_values = probabilities[rows, targets].double().cpu().tolist()
                for (parent_index, bank_index, child, accumulated, token), value in zip(edges, log_values):
                    joint = accumulated + value
                    if child['event'] is not None:
                        values[bank_index][child['event']] = joint
                    if child['children']:
                        parents.append(parent_index); tokens.append(token)
                        next_active.append((bank_index, child, joint))
                if not next_active: break
                if len(next_active) > max_active_nodes:
                    raise ValueError('candidate trie exceeds max_active_nodes before cache replication')
                indices = torch.tensor(parents, dtype=torch.long, device=model.device)
                # Modern HF DynamicCache mutates every layer; repeated indices
                # produce distinct rows. Never reuse the previous parent cache.
                cache.batch_select_indices(indices)
                masks = torch.cat((masks.index_select(0, indices),
                    torch.ones((len(indices), 1), dtype=masks.dtype, device=masks.device)), dim=1)
                positions = masks.sum(-1, keepdim=True) - 1
                encoded = dict(input_ids=torch.tensor(tokens, dtype=torch.long, device=model.device)[:, None],
                    attention_mask=masks, position_ids=positions, past_key_values=cache,
                    use_cache=True, logits_to_keep=1)
                if explicit_positions: encoded['cache_position'] = torch.tensor([width + depth], device=model.device)
                del probabilities, output
                output = model(**encoded); calls += 1; depth += 1
                cache = _checked_cache(output, width + depth)
                probabilities = _last_log_probabilities(output, len(next_active))
                active = next_active; maximum = max(maximum, len(active))
            for index, bank in enumerate(block):
                if any(value is None for value in values[index]): raise ValueError('candidate trie left an event unscored')
                result = summarize_events(bank, values[index])
                result.update(scoring_backend=BACKEND, use_cache=True, prompt_batch_size=prompt_batch_size,
                    prompt_batch_index=start // prompt_batch_size, pad_token_id=pad_token_id,
                    forward_calls=calls, root_prefill_calls=1, continuation_forward_calls=calls - 1,
                    execution_counters_scope='shared_prompt_batch; repeated for every bank in that batch',
                    prompt_batch_members=len(block), prompt_batch_padded_width=width,
                    prompt_batch_prefill_padded_tokens=len(block) * width,
                    unique_continuation_nodes=sum(tries[index][1]), max_active_nodes_observed=maximum,
                    teacher_forced_scored_tokens=sum(len(event['event_token_ids']) for event in bank['events']),
                    position_ids='semantic unmasked positions; physical padded cache_position only when explicit in model signature')
                results.append(result)
            del cache, output, probabilities, encoded
    return results
