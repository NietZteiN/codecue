"""Explicit standalone, decode-verified candidate token continuations.

This is a separately registered event construction rule. It neither repairs nor
relaxes the original joint prompt-plus-candidate tokenization contract. Saved
prompt tokens are never rewritten. Tokenizers/models are injected, never loaded.
"""
from __future__ import annotations

from pathlib import Path

from . import candidate_confidence as event
from .datasets import digest, write_json
from .published_benchmarks import sha

TOKENIZATION_RULE = 'standalone_decode_verified_v2'
LIMITATION = (event.LIMITATION+' Each event uses one declared standalone token '
    'sequence. Other tokenizations producing equivalent text are outside this '
    'event set. Exact saved prompt IDs and decoded concatenation are verified; '
    'joint prompt-plus-candidate retokenization is not required by this rule.')


def _decode(tokenizer, tokens):
    text = tokenizer.decode(tokens, skip_special_tokens=False,
                            clean_up_tokenization_spaces=False)
    if not isinstance(text, str):
        raise ValueError('tokenizer decode must return the exact text string')
    return text


def _special_ids(tokenizer):
    """Reject every tokenizer-declared special ID, including the EOS union."""
    special = event._ids(getattr(tokenizer, 'all_special_ids', []),
                         'tokenizer special IDs', nonempty=False)
    for name in ('bos_token_id', 'eos_token_id', 'pad_token_id', 'unk_token_id',
                 'sep_token_id', 'cls_token_id', 'mask_token_id'):
        value = getattr(tokenizer, name, None)
        if value is not None:
            special.extend(event._ids([value], name))
    return set(special)


def build_events(tokenizer, prompt, input_token_ids, candidates, eos_token_ids):
    """Append standalone numeral IDs after verifying both exact decoder equalities.

    Required: encode(prompt)==saved IDs, decode(encode(surface))==surface and
    decode(prefix+continuation)==decode(prefix)+surface. Decoder cleanup and
    special-token skipping are explicitly disabled for every comparison.
    """
    candidates = event._candidates(candidates)
    eos = event._eos(eos_token_ids)
    prefix = event._ids(input_token_ids, 'saved prompt')
    if not isinstance(prompt, str) or not prompt:
        raise ValueError('unchanged nonempty prompt string required')
    actual = event._ids(tokenizer(prompt, add_special_tokens=False)['input_ids'], 'tokenized prompt')
    if actual != prefix:
        raise ValueError('saved prompt IDs differ from exact prompt tokenization')
    decoded_prefix = _decode(tokenizer, prefix)
    forbidden = _special_ids(tokenizer)|set(eos)
    events = []
    for candidate in candidates:
        surface = str(candidate)
        continuation = event._ids(tokenizer(surface, add_special_tokens=False)['input_ids'],
                                  'standalone candidate continuation')
        if forbidden.intersection(continuation):
            raise ValueError('standalone numeral contains a special or declared EOS token')
        if _decode(tokenizer, continuation) != surface:
            raise ValueError('standalone numeral decode differs from canonical surface; whitespace/dummy prefixes are forbidden')
        if _decode(tokenizer, prefix+continuation) != decoded_prefix+surface:
            raise ValueError('candidate continuation decoder changes the saved prompt boundary')
        for ending in eos:
            events.append(dict(candidate=candidate, surface=surface,
                continuation_token_ids=list(continuation), eos_token_id=ending,
                event_token_ids=continuation+[ending]))
    event._prefix_free([value['event_token_ids'] for value in events])
    bank = dict(schema_version=1, evaluation_role=event.ROLE, measurement=event.MEASUREMENT,
        prompt_sha256=digest(prompt), input_token_ids=prefix,
        input_token_ids_sha256=digest(prefix), candidates=candidates, eos_token_ids=eos,
        terminator='eos', events=events, prefix_free=True)
    bank['bank_sha256'] = digest(bank)
    return event.validate_bank(bank)


def preflight(config):
    """Write only a declaration; real-tokenizer decoder checks remain pending."""
    if config.get('tokenization_rule') != TOKENIZATION_RULE:
        raise ValueError('explicit tokenization_rule='+TOKENIZATION_RULE+' required')
    candidates, eos = event.declaration(config)
    if not config.get('output_review'):
        raise ValueError('output_review metadata path required')
    result = dict(status='passed', evaluation_role=event.ROLE, measurement=event.MEASUREMENT,
        config_hash=digest(config), toolkit_sha256=sha(Path(event.__file__)),
        continuation_toolkit_sha256=sha(Path(__file__)), tokenization_rule=TOKENIZATION_RULE,
        candidates=candidates, domain=list(event.DOMAIN), eos_token_ids=eos, terminator='eos',
        event_definition='decode-verified standalone canonical integer tokens followed by one declared EOS ID',
        planned_event_variants=len(candidates)*len(eos), candidate_order='increasing numeric order',
        eos_union='distinct disjoint variants, summed for each candidate',
        tokenizer_loaded=False, model_loaded=False,
        preparation_stage='declaration only; actual prompt/standalone-token decoder checks remain pending',
        eos_vocabulary_verified=False, tokenization_performed=False, boundary_verified=False,
        probabilities_computed=False, generated_tokens=0, target_outcomes_read=False, oracle_fields_read=False,
        access_contract='Only explicit configuration metadata; no model, tokenizer, source labels or response files opened.',
        boundary_contract='Verify encode(prompt)==saved prefix IDs without rewriting them. Tokenize each canonical '
            'numeral alone without special tokens; require decode(continuation)==surface and '
            'decode(prefix+continuation)==decode(prefix)+surface, with skip_special_tokens=False and '
            'clean_up_tokenization_spaces=False. Reject special/EOS numeral tokens and decoder boundary edits. '
            'This explicitly declared standalone rule does not jointly tokenize prompt+candidate.',
        limitation=LIMITATION)
    write_json(config['output_review'], result)
    return result
