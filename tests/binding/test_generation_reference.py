from types import SimpleNamespace

import pytest
import torch

from codecue.binding.generation_reference import greedy_reference


class Tokenizer:
    eos_token_id = 0

    def decode(self, ids, skip_special_tokens=True):
        return ''.join({0: '', 1: '7', 2: '9', 3: '\n', 4: 'x'}[i] for i in ids)


class Model:
    device = 'cpu'

    def __init__(self, sequence):
        self.sequence = sequence
        self.prefixes = []

    def __call__(self, input_ids, attention_mask, use_cache):
        assert use_cache is False
        assert torch.equal(attention_mask, torch.ones_like(input_ids))
        self.prefixes.append(input_ids[0].tolist())
        token = self.sequence[len(self.prefixes)-1]
        logits = torch.zeros((1, input_ids.shape[1], 5))
        logits[0, -1, token] = 9
        return SimpleNamespace(logits=logits)


@pytest.mark.parametrize('sequence,limit,raw,reason', [
    ([1, 0], 4, '7', 'eos'),
    ([1, 3, 3], 4, '7\n\n', 'blank_line'),
    ([2, 4], 2, '9x', 'token_limit'),
])
def test_reference_recomputes_full_prefix_and_records_stop_boundary(sequence, limit, raw, reason):
    model = Model(sequence)
    result = greedy_reference(Tokenizer(), model, [99], limit)
    assert result['raw_response'] == raw and result['stop_reason'] == reason
    assert result['token_ids'] == sequence
    assert model.prefixes == [[99] + sequence[:i] for i in range(len(sequence))]
    assert all(s['top_two_margin'] == 9 for s in result['steps'])
    assert result['prediction'] == (7 if raw.startswith('7') else None)
