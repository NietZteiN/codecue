"""Cache branching and exact causal offsets with injected software-only models."""
from types import SimpleNamespace

import pytest
import torch

from codecue.binding.candidate_cache import score_banks
from codecue.binding.candidate_confidence import build_events, score_events


class Tokenizer:
    def __call__(self, text, *, add_special_tokens):
        assert add_special_tokens is False
        chars = {**{str(i): i for i in range(10)}, '-': 10, 'Q': 11, ':': 12, 'A': 13}
        return {'input_ids': [chars[char] for char in text]}


def bank(prompt='Q:', candidates=None, eos=(14, 15, 16)):
    tokenizer = Tokenizer()
    ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
    return build_events(tokenizer, prompt, ids,
                        list(range(-16, 17)) if candidates is None else candidates, list(eos))


class Cache:
    """HF-style mutation: every selection makes a new independently indexed batch."""
    def __init__(self, histories, masks, log):
        self.histories = histories.clone(); self.masks = masks.clone(); self.log = log

    def get_seq_length(self): return self.histories.shape[1]

    def batch_select_indices(self, indices):
        self.log.append(indices.cpu().tolist())
        self.histories = self.histories.index_select(0, indices)
        self.masks = self.masks.index_select(0, indices)


class Model:
    device = 'cpu'; training = False
    config = SimpleNamespace(max_position_embeddings=512)

    def __init__(self, zero_tokens=(), bad=None):
        self.calls = []; self.selections = []; self.zero_tokens = zero_tokens; self.bad = bad

    def __call__(self, *, input_ids, attention_mask, position_ids, use_cache,
                 past_key_values=None, logits_to_keep=0, cache_position=None):
        assert not torch.is_grad_enabled()
        assert input_ids.ndim == 2 and attention_mask.ndim == 2
        length = input_ids.shape[1]
        if past_key_values is None:
            history = input_ids
            expected_positions = (attention_mask.cumsum(-1) - 1).masked_fill(attention_mask == 0, 1)
            assert torch.equal(position_ids, expected_positions)
            if use_cache:
                assert logits_to_keep == 1
                assert torch.equal(cache_position, torch.arange(length))
        else:
            assert use_cache and logits_to_keep == length == 1
            previous = past_key_values.get_seq_length()
            assert torch.equal(cache_position, torch.tensor([previous]))
            assert torch.equal(attention_mask[:, :-1], past_key_values.masks)
            assert attention_mask[:, -1].eq(1).all()
            assert torch.equal(position_ids, attention_mask.sum(-1, keepdim=True) - 1)
            history = torch.cat((past_key_values.histories, input_ids), dim=1)
        assert history.shape == attention_mask.shape
        # Prefix dependence includes token order and semantic positions, so wrong
        # parent selection, padding or 1-vs-16 offsets changes event probabilities.
        semantic = attention_mask.cumsum(-1)
        prefix_hash = (history * semantic * attention_mask).cumsum(-1)
        bases = prefix_hash + 5 * semantic
        vocabulary = torch.arange(24)[None, None, :]
        logits = ((bases[:, :, None] * (vocabulary + 3) + vocabulary * 7) % 31).float() / 7 - 2
        logits = logits[:, -length:, :]
        if logits_to_keep: logits = logits[:, -logits_to_keep:, :]
        for token in self.zero_tokens: logits[:, :, token] = -torch.inf
        if self.bad == 'nan': logits[:, :, 3] = torch.nan
        elif self.bad == 'positive_infinity': logits[:, :, 3] = torch.inf
        elif self.bad == 'no_mass': logits[:] = -torch.inf
        cache = None
        if use_cache:
            cache = past_key_values or Cache(history, attention_mask, self.selections)
            cache.histories = history.clone(); cache.masks = attention_mask.clone()
        self.calls.append(dict(input_ids=input_ids.clone(), attention_mask=attention_mask.clone(),
                               position_ids=position_ids.clone(), root=past_key_values is None,
                               use_cache=use_cache, logits_to_keep=logits_to_keep))
        return SimpleNamespace(logits=logits, past_key_values=cache)

    def generate(self, *args, **kwargs): raise AssertionError('candidate scoring must never generate')


def assert_equivalent(left, right):
    assert left['bank_sha256'] == right['bank_sha256']
    for key in ('support_mass', 'support_log_mass', 'support_conditional_entropy_nats',
                'support_conditional_top_two_probability_margin'):
        assert left[key] == pytest.approx(right[key], abs=2e-7, rel=2e-6)
    assert [row['candidate'] for row in left['candidates']] == [row['candidate'] for row in right['candidates']]
    for a, b in zip(left['event_variants'], right['event_variants']):
        assert a['event_token_ids'] == b['event_token_ids']
        assert a['log_probability'] == pytest.approx(b['log_probability'], abs=2e-6)


def test_all_33_integers_and_three_eos_match_direct_teacher_forcing():
    events = bank()
    model = Model()
    actual = score_banks(model, [events], prompt_batch_size=1)[0]
    expected = score_events(Model(), events, batch_size=19)
    assert_equivalent(actual, expected)
    assert len(model.calls) == 4  # root plus '-', '-1' and '-16' max depth
    assert sum(call['root'] for call in model.calls) == 1
    assert all(call['input_ids'].shape[1] == 1 for call in model.calls[1:])
    assert actual['root_prefill_calls'] == 1 and actual['continuation_forward_calls'] == 3
    assert actual['forward_calls'] == 4 and actual['use_cache']
    assert actual['unique_continuation_nodes'] == 34  # plus one root = 35 trie states
    assert len(events['events']) == 99 and actual['generated_tokens'] == 0
    assert any(len(indices) != len(set(indices)) for indices in model.selections)


@pytest.mark.parametrize('prompt_batch_size', [1, 2, 4, 8])
def test_unequal_prompt_lengths_and_chunked_batches_preserve_exact_events(prompt_batch_size):
    banks = [bank('Q:'), bank('AQQ:'), bank('AQ:'), bank('AAAAQ:'), bank('Q:')]
    model = Model()
    actual = score_banks(model, banks, prompt_batch_size=prompt_batch_size, pad_token_id=23)
    assert [item['bank_sha256'] for item in actual] == [item['bank_sha256'] for item in banks]
    for observed, events in zip(actual, banks):
        assert_equivalent(observed, score_events(Model(), events, batch_size=13, pad_token_id=23))
    batches = (len(banks) + prompt_batch_size - 1) // prompt_batch_size
    assert sum(call['root'] for call in model.calls) == batches
    assert len(model.calls) == 4 * batches
    assert all(call['logits_to_keep'] == 1 and call['use_cache'] for call in model.calls)


def test_terminal_one_eos_and_longer_sixteen_are_separate_complete_events():
    events = bank(candidates=[1, 16], eos=(14, 15))
    model = Model()
    actual = score_banks(model, [events])[0]
    expected = score_events(Model(), events)
    assert_equivalent(actual, expected)
    assert actual['forward_calls'] == 3
    assert actual['unique_continuation_nodes'] == 2
    assert model.calls[1]['input_ids'].tolist() == [[1]]
    assert model.calls[2]['input_ids'].tolist() == [[6]]
    assert all(not set(call['input_ids'].flatten().tolist()) & {14, 15} for call in model.calls)
    for candidate in actual['candidates']:
        variants = [row for row in actual['event_variants'] if row['candidate'] == candidate['candidate']]
        assert candidate['absolute_event_mass'] == pytest.approx(sum(row['absolute_event_mass'] for row in variants))


def test_finished_prompt_branches_are_removed_while_deeper_prompts_continue():
    banks = [bank('AQQ:', candidates=[1], eos=(14,)),
             bank('Q:', candidates=[-16], eos=(14, 15)),
             bank('AAQ:', candidates=[0, 16], eos=(16,))]
    model = Model()
    actual = score_banks(model, banks, prompt_batch_size=3)
    for observed, events in zip(actual, banks):
        assert_equivalent(observed, score_events(Model(), events))
    assert model.calls[0]['input_ids'].shape == (3, 4)
    assert model.calls[-1]['input_ids'].tolist() == [[6]]
    assert len(model.selections) == 3


def test_model_without_explicit_cache_position_uses_positions_and_cache_length():
    class NoCachePosition(Model):
        def __call__(self, *, input_ids, attention_mask, position_ids, use_cache,
                     past_key_values=None, logits_to_keep=0):
            physical = (torch.arange(input_ids.shape[1]) if past_key_values is None
                        else torch.tensor([past_key_values.get_seq_length()]))
            return super().__call__(input_ids=input_ids, attention_mask=attention_mask,
                position_ids=position_ids, use_cache=use_cache, past_key_values=past_key_values,
                logits_to_keep=logits_to_keep, cache_position=physical)
    events = bank()
    assert_equivalent(score_banks(NoCachePosition(), [events])[0], score_events(Model(), events))


def test_zero_partial_event_masses_preserve_stable_eos_union():
    events = bank(candidates=[0, 1, 16], eos=(14, 15))
    result = score_banks(Model(zero_tokens=(1, 14)), [events])[0]
    assert result['support_mass'] > 0
    by_candidate = {row['candidate']: row for row in result['candidates']}
    assert by_candidate[0]['support_conditional_probability'] == 1
    assert by_candidate[1]['absolute_event_mass'] == by_candidate[16]['absolute_event_mass'] == 0
    assert all(row['absolute_event_mass'] == 0 for row in result['event_variants'] if row['eos_token_id'] == 14)
    with pytest.raises(ValueError, match='zero probability support'):
        score_banks(Model(zero_tokens=(14, 15)), [events])


def test_capacity_is_checked_before_any_model_call():
    model = Model()
    with pytest.raises(ValueError, match='max_active_nodes'):
        score_banks(model, [bank(), bank()], prompt_batch_size=2, max_active_nodes=2)
    assert not model.calls
    model.config = SimpleNamespace(max_position_embeddings=4)
    with pytest.raises(ValueError, match='context capacity'): score_banks(model, [bank()])
    assert not model.calls


@pytest.mark.parametrize('bad', ['nan', 'positive_infinity', 'no_mass'])
def test_invalid_distributions_fail_visibly(bad):
    with pytest.raises(ValueError, match='causal distribution'): score_banks(Model(bad=bad), [bank()])


def test_cache_api_incompatibility_never_silently_falls_back():
    class NoCache(Model):
        def __call__(self, **kwargs):
            # This deliberately incompatible model has no explicit cache_position.
            kwargs['cache_position'] = torch.arange(kwargs['input_ids'].shape[1])
            output = super().__call__(**kwargs)
            output.past_key_values = ('legacy tuple is not supported',)
            return output
    model = NoCache()
    with pytest.raises(ValueError, match='modern HF cache'): score_banks(model, [bank()])
    assert len(model.calls) == 1


def test_candidate_vocabulary_mismatch_fails_visibly():
    with pytest.raises(ValueError, match='outside model vocabulary'):
        score_banks(Model(), [bank(candidates=[1], eos=(25,))])


@pytest.mark.parametrize('kwargs', [{'prompt_batch_size': 0}, {'max_active_nodes': True},
                                  {'max_active_nodes': 0}, {'pad_token_id': -1}])
def test_invalid_capacity_declarations_are_rejected(kwargs):
    with pytest.raises(ValueError): score_banks(Model(), [bank()], **kwargs)


def test_training_mode_and_changed_bank_hash_are_rejected():
    model = Model(); model.training = True
    with pytest.raises(ValueError, match='evaluation mode'): score_banks(model, [bank()])
    events = bank(); events['input_token_ids'][0] += 1
    with pytest.raises(ValueError, match='content hash'): score_banks(Model(), [events])
    assert score_banks(Model(), []) == []
