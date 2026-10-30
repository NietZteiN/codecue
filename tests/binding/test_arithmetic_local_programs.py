from copy import deepcopy
from collections import Counter

import numpy as np
import pytest

from codecue.binding import arithmetic_local_programs as programs
from codecue.binding import arithmetic_local_capture as capture
from codecue.binding import arithmetic_graph_programs as original


@pytest.fixture(scope='module')
def rows():
    return programs.make_rows()


def test_more_independent_structures_with_no_old_or_new_split_overlap(rows):
    families = {r['component_id']: r['split'] for r in rows}
    assert Counter(families.values()) == dict(train=216, development=72, calibration=6)
    assert len(rows) == 5292
    keys = {original.canonical_key(updates) for _, _, _, updates in programs.structures()}
    old_keys = {original.canonical_key(updates) for _, _, updates in original.structures()}
    assert not keys & old_keys
    assert len(keys) == 294


def test_independent_execution_and_every_span_pass(rows):
    result = programs.validate(rows)
    assert result['independent_python_passed']
    assert result['canonical_split_overlap'] == result['exact_body_overlap'] == 0


def test_cached_generation_cannot_hide_mutated_targets(rows):
    changed = deepcopy(rows)
    changed[0]['oracle']['writes'][4]['parents'][0] = 99
    with pytest.raises(ValueError):
        programs.validate(changed, independent=False)
    assert programs.make_rows()[0]['oracle']['writes'][4]['parents'][0] != 99


def test_operand_read_precedes_destination_update_and_uses_are_causal(rows):
    for row in rows:
        points = programs.points(row)
        for i, point in enumerate(points):
            if point['kind'] != 'use':
                continue
            assert point['parent'] < point['statement']
            assert point['candidate_definitions'] == list(range(point['statement']))
            assert all(p < i and points[p]['kind'] == 'definition' for p in point['candidate_points'])
            assert row['source'][point['start']:point['stop']] == point['name']
            assert points[point['candidate_points'][point['parent']]]['statement'] == point['parent']


def test_one_operation_calibration_queries_computed_variable(rows):
    selected = [r for r in rows if r['split'] == 'calibration']
    assert len(selected) == 108
    assert all(r['depth'] == 1 and r['query_kind'] == 'arithmetic_written' for r in selected)


class CharacterTokenizer:
    def apply_chat_template(self, messages, **kwargs):
        return '<user>' + messages[0]['content'] + '</user><assistant>'

    def __call__(self, prompt, **kwargs):
        return dict(input_ids=[ord(c) for c in prompt], offset_mapping=[(i, i + 1) for i in range(len(prompt))])

    def decode(self, ids, **kwargs):
        return ''.join(chr(i) for i in ids)


@pytest.mark.parametrize('depth', [1, 2, 4, 6])
def test_native_layout_last_token_spans_and_padding(rows, depth):
    row = next(r for r in rows if r['depth'] == depth)
    case = capture.layout(CharacterTokenizer(), row)
    capture.validate_case(case, row)
    assert case['point_count'] == 4 + 3 * depth + 1
    assert len(case['positions']) == programs.MAX_POINTS
    assert len(set(case['positions'])) < programs.MAX_POINTS  # RHS end shares a token with definition end.


def test_modified_causal_prefix_and_future_span_are_rejected(rows):
    row = rows[0]
    case = capture.layout(CharacterTokenizer(), row)
    case['prefix_sha256'][0] = 'bad'
    with pytest.raises(ValueError):
        capture.validate_case(case, row)
    case = capture.layout(CharacterTokenizer(), row)
    case['positions'][0] += 1
    from codecue.binding.datasets import digest
    case['prefix_sha256'][0] = digest(case['input_token_ids'][:case['positions'][0] + 1])
    with pytest.raises(ValueError):
        capture.validate_case(case, row)


def test_feature_padding_shape_and_finiteness_are_enforced(rows):
    case = capture.layout(CharacterTokenizer(), rows[0])
    profile = dict(layers=[1, 2], hidden_size=3)
    x = np.zeros((1, programs.MAX_POINTS, 2, 3), np.float32)
    capture.validate_features(x, [case], profile)
    x[0, -1] = 1
    with pytest.raises(ValueError, match='padding'):
        capture.validate_features(x, [case], profile)
    x[:] = np.nan
    with pytest.raises(ValueError, match='finite'):
        capture.validate_features(x, [case], profile)


def test_forward_uses_native_left_padding_and_exact_point_positions(rows):
    import torch
    from types import SimpleNamespace

    class Batch(dict):
        def __getattr__(self, key):
            return self[key]

        def to(self, device):
            return Batch({k: v.to(device) for k, v in self.items()})

    class PaddedTokenizer(CharacterTokenizer):
        def __call__(self, prompts, **kwargs):
            width = max(map(len, prompts))
            ids = [[0] * (width - len(p)) + [ord(c) for c in p] for p in prompts]
            masks = [[0] * (width - len(p)) + [1] * len(p) for p in prompts]
            return Batch(input_ids=torch.tensor(ids), attention_mask=torch.tensor(masks))

    class Block(torch.nn.Module):
        def forward(self, x):
            return x + 1

    class Backbone(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = torch.nn.ModuleList([Block(), Block()])

        def forward(self, input_ids, attention_mask, position_ids, **kwargs):
            x = torch.stack((input_ids.float(), position_ids.float(), attention_mask.float()), dim=-1)
            for block in self.layers:
                x = block(x)
            return x

    chosen = [next(r for r in rows if r['depth'] == d) for d in [1, 6]]
    cases = [capture.layout(CharacterTokenizer(), r) for r in chosen]
    model = SimpleNamespace(model=Backbone(), device=torch.device('cpu'))
    features = capture.forward(PaddedTokenizer(), model, cases, dict(layers=[0, 1], hidden_size=3))
    for i, case in enumerate(cases):
        for j in range(case['point_count']):
            position = case['positions'][j]
            np.testing.assert_array_equal(features[i, j, 0], [case['input_token_ids'][position] + 1, position + 1, 2])
            np.testing.assert_array_equal(features[i, j, 1], [case['input_token_ids'][position] + 2, position + 2, 3])
