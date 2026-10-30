"""Standalone continuation checks use injected tiny decoders, never HF loads."""
from copy import deepcopy
import json
import math
from pathlib import Path

import pytest

from codecue.binding import candidate_confidence as event
from codecue.binding import candidate_continuation as continuation
from codecue.binding.datasets import digest
from codecue.binding.published_benchmarks import sha


class Tokenizer:
    all_special_ids = [14, 15]
    bos_token_id = 14
    eos_token_id = 15

    def __init__(self):
        self.encoded = [];self.decoded = []
        self.characters = {**{str(index): index for index in range(10)}, '-': 10, 'Q': 11, ':': 12, ' ': 13}

    def __call__(self, text, *, add_special_tokens):
        assert add_special_tokens is False
        self.encoded.append(text)
        # This mimics a joint encoder merging the prompt's last token with '-'.
        if text.startswith('Q:-'):
            return {'input_ids': [11, 99]+[self.characters[c] for c in text[3:]]}
        return {'input_ids': [self.characters[c] for c in text]}

    def decode(self, tokens, *, skip_special_tokens, clean_up_tokenization_spaces):
        assert skip_special_tokens is False and clean_up_tokenization_spaces is False
        self.decoded.append(list(tokens))
        reverse = {value: key for key, value in self.characters.items()}
        return ''.join(reverse.get(token, '<special>') for token in tokens)


def test_explicit_standalone_rule_succeeds_when_joint_negative_tokenization_merges():
    old_hash = sha(Path(event.__file__))
    with pytest.raises(ValueError, match='merges'):
        event.build_events(Tokenizer(), 'Q:', [11, 12], [-16, -1, 0, 1, 16], [14, 15])
    tokenizer = Tokenizer();prefix = [11, 12]
    bank = continuation.build_events(tokenizer, 'Q:', prefix, list(range(-16, 17)), [14, 15])
    assert event.validate_bank(bank) is bank
    assert prefix == [11, 12] and bank['input_token_ids'] == prefix
    assert bank['bank_sha256'] == digest({key: value for key, value in bank.items() if key != 'bank_sha256'})
    assert len(bank['events']) == 66 and bank['candidates'] == list(range(-16, 17))
    assert tokenizer.encoded == ['Q:']+[str(value) for value in range(-16, 17)]
    assert all(text == 'Q:' or not text.startswith('Q:') for text in tokenizer.encoded)
    by_candidate = {row['candidate']: row for row in bank['events'] if row['eos_token_id'] == 15}
    assert by_candidate[-16]['event_token_ids'] == [10, 1, 6, 15]
    assert by_candidate[-1]['event_token_ids'] == [10, 1, 15]
    assert by_candidate[0]['event_token_ids'] == [0, 15]
    assert by_candidate[1]['event_token_ids'] == [1, 15]
    assert by_candidate[16]['event_token_ids'] == [1, 6, 15]
    assert 'tokenization_rule' not in bank  # Rule belongs in registration; schema1 stays strict.
    assert sha(Path(event.__file__)) == old_hash


def test_signed_multitoken_events_use_existing_exact_causal_scorer():
    from test_candidate_confidence import TransitionModel, expected_log_probability
    bank = continuation.build_events(Tokenizer(), 'Q:', [11, 12], [-16, -1, 0, 1, 16], [14, 15])
    result = event.score_events(TransitionModel(), bank, batch_size=4, pad_token_id=15)
    for row in result['event_variants']:
        expected = expected_log_probability(row)
        assert row['log_probability'] == pytest.approx(expected, abs=2e-6)
        assert row['absolute_event_mass'] == pytest.approx(math.exp(expected), rel=3e-6)
    assert result['generated_tokens'] == 0 and result['target_outcomes_read'] is False


@pytest.mark.parametrize('mode', ['dummy-prefix', 'trailing-space', 'decoder-edit', 'prefix-edit',
    'empty', 'special', 'eos', 'saved-prefix', 'noninteger'])
def test_rejects_whitespace_special_tokens_saved_prefix_changes_and_contextual_decoder_edits(mode):
    class Broken(Tokenizer):
        def __call__(self, text, *, add_special_tokens):
            result = super().__call__(text, add_special_tokens=add_special_tokens)
            if text == 'Q:' and mode == 'saved-prefix':result['input_ids'] = [11, 13]
            elif text == '1':
                if mode == 'dummy-prefix':result['input_ids'] = [13, 1]
                elif mode == 'trailing-space':result['input_ids'] = [1, 13]
                elif mode == 'empty':result['input_ids'] = []
                elif mode == 'special':result['input_ids'] = [14]
                elif mode == 'eos':result['input_ids'] = [15]
                elif mode == 'noninteger':result['input_ids'] = [1.]
            return result

        def decode(self, tokens, **kwargs):
            text = super().decode(tokens, **kwargs)
            if mode == 'decoder-edit' and tokens == [11, 12, 1]:return 'Q :1'
            if mode == 'prefix-edit' and tokens == [11, 12, 1]:return 'Q1'
            return text
    with pytest.raises(ValueError):
        continuation.build_events(Broken(), 'Q:', [11, 12], [1], [15])


def test_unknown_special_token_is_rejected_even_if_decoder_hides_its_special_status():
    class Special(Tokenizer):
        all_special_ids = [7, 14, 15]
        def __call__(self, text, **kwargs):
            if text == '1':return {'input_ids': [7]}
            return super().__call__(text, **kwargs)
        def decode(self, tokens, **kwargs):
            if tokens == [7]:return '1'
            if tokens == [11, 12, 7]:return 'Q:1'
            return super().decode(tokens, **kwargs)
    with pytest.raises(ValueError, match='special'):
        continuation.build_events(Special(), 'Q:', [11, 12], [1], [15])


def test_duplicate_events_are_rejected_even_for_a_stateful_nonfaithful_decoder():
    class Aliasing(Tokenizer):
        def __init__(self):super().__init__();self.last = None
        def __call__(self, text, **kwargs):
            if text in ('1', '16'):
                self.last = text
                return {'input_ids': [1]}
            return super().__call__(text, **kwargs)
        def decode(self, tokens, **kwargs):
            if tokens == [1]:return self.last
            if tokens == [11, 12, 1]:return 'Q:'+self.last
            return super().decode(tokens, **kwargs)
    with pytest.raises(ValueError, match='duplicate'):
        continuation.build_events(Aliasing(), 'Q:', [11, 12], [1, 16], [15])


def test_existing_schema_still_rejects_nonprefixfree_and_corrupt_event_banks():
    bank = continuation.build_events(Tokenizer(), 'Q:', [11, 12], [1, 16], [15])
    with pytest.raises(ValueError, match='prefix-free'):
        event._prefix_free([[1, 15], [1, 15, 6, 15]])
    changed = deepcopy(bank);changed['events'][0]['event_token_ids'][0] = 9
    with pytest.raises(ValueError):event.validate_bank(changed)


def test_preflight_logs_explicit_rule_and_both_toolkit_hashes_without_loading_or_tokenizing(tmp_path, monkeypatch):
    from codecue.binding import experiment_log, model_adapter
    logged = []
    monkeypatch.setattr(experiment_log, 'note_artifact', lambda path: logged.append(path))
    monkeypatch.setattr(model_adapter, 'load', lambda *args: pytest.fail('preflight loaded a model'))
    monkeypatch.setattr(continuation, 'build_events', lambda *args: pytest.fail('metadata declaration tokenized inputs'))
    config = dict(evaluation_role=event.ROLE, tokenization_rule=continuation.TOKENIZATION_RULE,
        eos_token_ids=[128001, 128008, 128009], bounds=[-16, 16], terminator='eos',
        source_labels=str(tmp_path/'absent-labels.jsonl'), output_review=str(tmp_path/'review.json'))
    result = continuation.preflight(config)
    assert result['status'] == 'passed' and result['measurement'] == event.MEASUREMENT
    assert result['tokenization_rule'] == 'standalone_decode_verified_v2'
    assert result['toolkit_sha256'] == sha(Path(event.__file__))
    assert result['continuation_toolkit_sha256'] == sha(Path(continuation.__file__))
    assert result['config_hash'] == digest(config) and result['planned_event_variants'] == 99
    assert result['candidates'] == list(range(-16, 17))
    for name in ('tokenizer_loaded', 'model_loaded', 'target_outcomes_read', 'tokenization_performed',
                 'boundary_verified', 'probabilities_computed', 'oracle_fields_read'):
        assert result[name] is False
    assert 'numeral alone' in result['boundary_contract']
    assert 'decode(prefix+continuation)==decode(prefix)+surface' in result['boundary_contract']
    assert 'skip_special_tokens=False' in result['boundary_contract']
    assert 'does not jointly tokenize' in result['boundary_contract']
    assert json.loads((tmp_path/'review.json').read_text()) == result and len(logged) == 1
    for rule in (None, 'joint_prompt_candidate_v1', 'standalone_approximate'):
        with pytest.raises(ValueError, match='tokenization_rule'):
            continuation.preflight({**config, 'tokenization_rule': rule})
    with pytest.raises(ValueError):
        continuation.preflight({**config, 'output_review': 'artifacts/binding/final/review.json'})
