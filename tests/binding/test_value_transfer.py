from copy import deepcopy

import numpy as np
import pytest
import torch

from codecue.binding.value_transfer import (CONDITIONS, directed_pairs, make_rows,
    matched_perturbation, patch_prefill, validate_chunk, validate_dataset, validate_layouts,
    verify_answer_boundary)


def test_counterfactuals_have_correct_oracles_both_queries_and_reciprocal_controls():
    config = {'generation': {'strides': [1]}}
    rows = make_rows(config)
    pairs = validate_dataset(config, rows, independent=True)
    assert len(rows) == 432
    assert len(pairs) == 576
    assert sum(p['affected'] for p in pairs) == 288
    assert {p['query_role'] for p in pairs} == {'current', 'saved', 'v0', 'v1'}
    assert {p['reverse'] for p in pairs} == {False, True}
    lookup = {(p['recipient'], p['donor']): p for p in pairs}
    for pair in pairs:
        reverse = lookup[pair['donor'], pair['recipient']]
        assert reverse['affected'] == pair['affected']
        assert reverse['counterfactual_answer'] == pair['baseline_answer']
    corrupted = deepcopy(rows)
    corrupted[0]['expected_answer'] += 1
    with pytest.raises(ValueError, match='registered'):
        validate_dataset(config, corrupted)


def test_counterfactual_group_must_keep_every_variant():
    rows = make_rows({'generation': {'strides': [1]}})
    with pytest.raises(ValueError, match='incomplete'):
        directed_pairs(rows[:-1])


def test_token_layout_refuses_unrelated_prompt_changes_or_shifted_sites():
    cases = {'a': {'input_token_ids': [0, 1, 2, 3, 4], 'positions': [1, 2, 0, 4]},
             'b': {'input_token_ids': [0, 9, 2, 3, 4], 'positions': [1, 2, 0, 4]}}
    pairs = [{'recipient': 'a', 'donor': 'b', 'slot': 0}]
    validate_layouts(cases, pairs)
    cases['b']['input_token_ids'][-1] = 8
    with pytest.raises(ValueError, match='layouts'):
        validate_layouts(cases, pairs)


@pytest.mark.parametrize('dtype', [torch.float32, torch.bfloat16])
def test_norm_matching_measures_actual_dtype_rounded_perturbations(dtype):
    generator = torch.Generator().manual_seed(97)
    base = torch.randn(8, 256, generator=generator).to(dtype)
    direction = torch.randn(8, 256, generator=generator)
    targets = torch.tensor([0., 0.1, 0.2, 0.5, 1., 2., 4., 16.])
    changed, actual = matched_perturbation(base, direction, targets)
    assert changed.dtype == base.dtype
    assert torch.equal(changed[0], base[0])
    assert torch.allclose(actual, (changed.float() - base.float()).norm(dim=-1))
    assert torch.all((actual - targets).abs() <= 0.03 * targets + 1e-6)


def test_patch_is_restricted_to_prefill_and_registered_positions():
    hidden = torch.zeros(2, 5, 3)
    result = patch_prefill(hidden, 5, torch.tensor([1, 3]), torch.ones(2, 3))
    assert result[0, 1].sum() == 3 and result[1, 3].sum() == 3
    assert result.sum() == 6 and hidden.sum() == 0
    decode = torch.zeros(2, 1, 3)
    assert patch_prefill(decode, 5, torch.tensor([1, 3]), torch.ones(2, 3)) is decode


def test_answer_boundary_rejects_whitespace_even_when_complete_integer_is_valid():
    baselines = {'a': dict(prediction=2, first_token=220, correct=True)}
    with pytest.raises(ValueError, match='answer-digit boundary'):
        verify_answer_boundary({'require_digit_first': True}, baselines, {'2': 17})
    # The guard checks format/alignment, not whether the predicted digit is correct.
    baselines['a'].update(first_token=17, correct=False)
    verify_answer_boundary({'require_digit_first': True}, baselines, {'2': 17})


def test_chunk_audit_rejects_wrong_targets_norms_and_nonidentity_shams():
    pair = dict(id='pair', recipient='a', donor='b', slot=0, replacement=3, baseline_answer=2)
    data = dict(cases={'a': dict(positions=[1, 2, 0, 4])}, answer_token_ids={'2': 12, '3': 13})
    row = dict(pair_id='pair', layer=8, condition='random_11', recipient='a', donor='b',
        position=1, target_token=13, original_token=12, target_logprob=-1., original_logprob=-2.,
        target_effective_norm=1., actual_effective_norm=1., first_token=13)
    config = {'norm_tolerance': 0.03}
    replays = {'pair': {'first_token': 12}}
    validate_chunk(config, data, 8, 'random_11', [pair], [row], replays)
    for field, value, message in [('target_token', 14, 'target'), ('actual_effective_norm', 2., 'mismatch'),
                                   ('target_logprob', np.nan, 'nonfinite')]:
        bad = dict(row, **{field: value})
        with pytest.raises(ValueError, match=message):
            validate_chunk(config, data, 8, 'random_11', [pair], [bad], replays)
    sham = dict(row, condition='identity_sham', actual_effective_norm=0.)
    with pytest.raises(ValueError, match='sham'):
        validate_chunk(config, data, 8, 'identity_sham', [pair], [sham], replays)
    sham['first_token'] = 12
    validate_chunk(config, data, 8, 'identity_sham', [pair], [sham], replays)
    assert len(CONDITIONS) == 7
