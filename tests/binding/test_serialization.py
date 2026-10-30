from copy import deepcopy
from types import SimpleNamespace

import pytest

from codecue.binding.published_benchmarks import WRAPPERS, plan, render, SCORER


def test_native_completion_preserves_content_ids_with_exactly_one_bos():
    class Native:
        bos_token = '<BOS>'
        bos_token_id = 1
        def __call__(self, text, add_special_tokens):
            assert not add_special_tokens
            ids = ([1] if text.startswith(self.bos_token) else [])
            return {'input_ids': ids + [ord(c) + 10 for c in text.removeprefix(self.bos_token)]}
    assert render(Native(), 'assert f(2) ==', WRAPPERS[2]) == '<BOS>assert f(2) =='
    with pytest.raises(ValueError, match='limited to CRUXEval'):
        plan(dict(scorer=SCORER, prompt_wrapper=WRAPPERS[2], tasks=['bbh_tracking_3']))
from codecue.binding.serialization_comparison import matched_config, paired_counts, profile_budget


def test_completion_preserves_all_author_text_and_checks_reference_ids():
    content = 'Released task\n[ANSWER]\n'
    observed = []
    reference = SimpleNamespace(bos_id=lambda: 1, encode=lambda s: observed.append(s) or [55])

    class Tokenizer:
        bos_token = '<s>'
        binding_sp_model = reference
        binding_official_boundary = True

        def __call__(self, prompt, add_special_tokens):
            assert prompt == '<s> ' + content
            assert add_special_tokens is False
            return {'input_ids': [1, 55]}

        def apply_chat_template(self, *args, **kwargs):
            raise AssertionError('completion must not render a chat turn')

    assert render(Tokenizer(), content, WRAPPERS[1]) == '<s> ' + content
    assert observed == [content]


def test_completion_rejects_missing_reference_and_token_boundary_mismatch():
    with pytest.raises(ValueError, match='audited CodeLlama'):
        render(SimpleNamespace(), 'text', WRAPPERS[1])

    class BadTokenizer:
        bos_token = '<s>'
        binding_official_boundary = True
        binding_sp_model = SimpleNamespace(bos_id=lambda: 1, encode=lambda s: [55])

        def __call__(self, *args, **kwargs):
            return {'input_ids': [1, 999]}

    with pytest.raises(ValueError, match='differs from one BOS'):
        render(BadTokenizer(), 'text', WRAPPERS[1])
    with pytest.raises(ValueError, match='unknown published serialization'):
        render(BadTokenizer(), 'text', 'unknown')


def test_unplanned_bbh_completion_is_rejected_before_reading_data():
    with pytest.raises(ValueError, match='limited to CRUXEval-O'):
        plan(dict(scorer=SCORER, prompt_wrapper=WRAPPERS[1], tasks=['bbh_tracking_3']))


def test_pairing_counts_every_joint_outcome_and_rejects_missing_questions():
    chat = {str(i): {'score': {'correct': v}} for i, v in enumerate([False, True, False, True])}
    raw = {str(i): {'score': {'correct': v}} for i, v in enumerate([False, False, True, True])}
    result = paired_counts(chat, raw, 'correct')
    assert result == dict(n=4, both_correct=1, chat_only_correct=1, completion_only_correct=1,
                          both_incorrect=1, chat_correct=2, completion_correct=2, delta_percentage_points=0.)
    with pytest.raises(ValueError, match='pairing differs'):
        paired_counts(chat, {'other': next(iter(raw.values()))}, 'correct')


def test_serialization_arms_must_match_model_budget_and_batch_contract():
    chat = {key: 'same' for key in ('model', 'model_revision', 'tokenizer_revision', 'dtype',
                                  'device', 'protocol', 'tokenization_mode', 'batch_size',
                                  'context_limit', 'scorer')}
    chat.update(prompt_wrapper=WRAPPERS[0], max_new_tokens={'cruxeval_o_direct': 512, 'cruxeval_o_cot': 1024})
    raw = deepcopy(chat)
    raw['prompt_wrapper'] = WRAPPERS[1]
    matched_config(chat, raw)
    for key in ('model', 'tokenizer_revision', 'batch_size'):
        with pytest.raises(ValueError, match='contract differs'):
            matched_config(chat, {**raw, key: 'different'})
    raw['max_new_tokens']['cruxeval_o_direct'] = 513
    with pytest.raises(ValueError, match='ceilings differ'):
        matched_config(chat, raw)


def test_dispatch_estimates_runtime_without_rejecting_work_against_old_budgets():
    assert profile_budget(12, 10000, 5000, 120)['projected_seconds'] == 1200
    assert profile_budget(50, 1, 0, 120)['projected_seconds'] == 5000
    assert profile_budget(12, None, None, 120)['stage_ceiling_seconds'] is None
    with pytest.raises(ValueError, match='positive measured'):
        profile_budget(0, 10000, 5000, 120)
