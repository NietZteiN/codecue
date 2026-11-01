from contextlib import nullcontext
from copy import deepcopy
from types import SimpleNamespace
import sys

import pytest
from codecue.binding import arithmetic_paired_exploration as study
from codecue.binding import arithmetic_paired_programs as programs


@pytest.mark.parametrize('scope,text,expected', [
    ('single', 'Answer: -3', [-3]), ('single', 'Answer: +2', [2]),
    ('all', 'Answer: [1, -2, 3, 4]', [1, -2, 3, 4]),
    ('single', 'Answer: 2\nAnswer: -3', [-3]),
    ('single', 'Answer: 2\nAnswer: maybe 3', None),
    ('single', 'The answer is 3', None), ('single', 'v2 = 3', None),
    ('single', 'Answer: 3.0', None), ('single', 'Answer: 3 and 4', None),
    ('all', 'Answer: [1, 2, 3]', None), ('all', 'Answer: (1, 2, 3, 4)', None),
    ('all', 'Answer: [1, 2, 3, 4, 5]', None),
])
def test_independent_strict_grammar_agrees(scope, text, expected):
    assert study.answer_values(text, scope) == expected
    parsed = programs.parse_answer(text, scope)
    assert (parsed['values'] if parsed['valid'] else None) == expected


@pytest.mark.parametrize('scope,text,expected', [
    ('single', '**Answer:** -3', [-3]),
    ('single', '**Final Answer:**\n-3', [-3]),
    ('single', '## Final Answer:\n-3', [-3]),
    ('single', 'Final answer: -3', [-3]),
    ('all', '**Answer:** [1, -2, 3, 4]', [1, -2, 3, 4]),
    ('single', 'Answering the question: -3', None),
    ('single', 'We compute -3. The answer is -3.', None),
    ('single', 'Answer: -3\n**Final Answer:** unknown', None),
    ('single', 'Answer: -3\n**Final Answer:** 5', [5]),
    ('single', '**Final Answer:**\nThe result is -3.', None),
    ('single', '```python\nv2 = -3\n```', None),
])
def test_diagnostic_is_label_based_and_gold_blind(scope, text, expected):
    assert study.answer_values(text, scope, diagnostic=True) == expected


def case(scope='single', protocol='output_only', instruction=0, id='one'):
    return dict(id=id, record_id='source', component_id='family', scope=scope,
        protocol=protocol, instruction=instruction, calibration_kind='arithmetic', depth=0,
        mutation='operand', expected=[-3] if scope == 'single' else [1, 2, -3, 4],
        target_literal_visible=False, forced_prefix='Answer:' if protocol == 'output_only' else '',
        prompt='prompt', input_token_ids=[7, 8])


@pytest.mark.parametrize('truncated', [False, True])
def test_correct_truncated_answer_remains_failure(truncated):
    c = case()
    r = study.independent_score(c, ' -3', [1, 2], truncated)
    assert r['correct'] is (not truncated)
    assert r['accepted'] is (not truncated)
    assert r['per_slot_correct'] == [not truncated]


@pytest.mark.parametrize('scope', ['single', 'all'])
def test_invalid_is_in_denominator_for_every_slot(scope):
    r = study.independent_score(case(scope), ' unknown', [1], False)
    assert not r['correct'] and not r['accepted']
    assert r['per_slot_correct'] == ([False] if scope == 'single' else [False] * 4)


def source():
    return dict(slot_names=['v0', 'v1', 'v2', 'v3'], target_name='v2', final_values=[1, 2, -3, 4],
        numeric_seed=1, error_candidates=dict(correct=-3, stale_target=2, recomputed_current_operands=2))


def response(c, text, truncated=False):
    return dict(raw_response=text, output_token_ids=[1, 2], truncated=truncated,
        **study.independent_score(c, text, [1, 2], truncated))


def test_candidate_collisions_remain_multilabel():
    c = case(); r = study.describe(c, response(c, ' 2'), source())
    assert set(r['wrong_target_candidate_matches']) == {'stale_target', 'recomputed_current_operands', 'other_current_binding'}
    table = study.cells([r])['output_only/single']
    assert table['ambiguous_wrong_candidate_rows'] == 1
    assert table['rows'] == 1 and table['strict_correct'] == 0


def test_diagnostic_never_changes_strict_metric():
    c = case(protocol='stepwise'); r = study.describe(c, response(c, '**Answer:** -3'), source())
    assert r['diagnostic_complete_correct']
    assert not r['strict_correct'] and not r['strict_accepted']


def test_truncated_answer_reported_separately():
    c = case(); r = study.describe(c, response(c, ' -3', True), source())
    out = study.cells([r])['output_only/single']
    assert out['correct_explicit_answer_but_truncated'] == 1
    assert out['strict_correct'] == out['diagnostic_complete_correct'] == 0


def test_scope_comparison_uses_same_target_not_joint_accuracy():
    rows = []
    for protocol in programs.PROTOCOLS:
        for scope in programs.SCOPES:
            c = case(scope, protocol); text = 'Answer: -3' if scope == 'single' else 'Answer: [9, 2, -3, 4]'
            if protocol == 'output_only': text = text.removeprefix('Answer:')
            rows.append(study.describe(c, response(c, text), source()))
    for value in study.paired_scopes(rows).values():
        assert value['single_target_correct'] == value['all_target_correct'] == 1
        assert value['accepted_target_disagreements'] == 0
    assert not rows[1]['strict_correct'] and rows[1]['target_correct']


def test_scope_pair_duplicates_fail():
    c = case(); r = study.describe(c, response(c, ' -3'), source())
    with pytest.raises(ValueError, match='duplicate'):
        study.paired_scopes([r, r])


def test_scope_missing_relative_fails():
    c = case(); r = study.describe(c, response(c, ' -3'), source())
    with pytest.raises(ValueError, match='incomplete'):
        study.paired_scopes([r])


def test_continuation_selects_all_and_only_truncated_outputs():
    cases = {}; records = {}
    for i in range(150):
        key = str(i); cases[key] = case(protocol=programs.PROTOCOLS[i % 3], id=key)
        records[key] = dict(truncated=i % 2 == 0)
    before = deepcopy(records)
    groups = list(study.continuation_plan(cases, records, 32))
    assert {k for g in groups for k in g} == {k for k, r in records.items() if r['truncated']}
    assert len([k for g in groups for k in g]) == 75
    assert all(len(g) <= 32 and len({cases[k]['protocol'] for k in g}) == 1 for g in groups)
    assert before == records


def test_continuation_batch_cannot_silently_change():
    with pytest.raises(ValueError, match='fixed'):
        list(study.continuation_plan({}, {}, 1))


def test_continuation_accounting_uses_registered_stage(tmp_path, monkeypatch):
    monkeypatch.setenv('SLURM_GPUS_ON_NODE', '1')
    path = tmp_path / 'ledger.json'
    lease = study.budget.reserve(dict(device='cuda', model='fixture', model_revision='fixed',
        run_dir=str(tmp_path), budget_ledger=str(path)), study.LEASE_STAGE)
    assert lease is not None and lease['mode'] == 'accounting_only'
    study.budget.release(lease, 1.25, 'complete')
    import json
    state = json.loads(path.read_text())
    assert not state['active'] and state['used_seconds'] == 1.25
    assert state['cap_seconds'] is None and state['completed'][0]['stage'] == study.LEASE_STAGE


class Tensor:
    def __init__(self, data): self.data = data
    def __getitem__(self, item):
        rows, cols = item
        return Tensor([r[cols] for r in self.data[rows]])
    def cpu(self): return self
    def tolist(self): return self.data


def test_continuation_preserves_exact_tokens_and_masks_left_padding(monkeypatch):
    monkeypatch.setitem(sys.modules, 'torch', SimpleNamespace(
        tensor=lambda data, device: Tensor(data), inference_mode=nullcontext))
    c1 = case(id='a'); c2 = case(id='b'); c2['input_token_ids'] = [7]
    class Tokenizer:
        eos_token_id = 99; pad_token_id = 0
        def __call__(self, prompt, add_special_tokens):
            return dict(input_ids=[7, 8] if prompt == 'prompt' else [7])
        def decode(self, ids, skip_special_tokens): return ' -3' if ids == [2, 3] else ' -3\n'
    c2['prompt'] = 'other'
    rows = {key: dict(id=key, truncated=True, raw_response=' -3', output_token_ids=[2, 3]) for key in ('a', 'b')}
    def generate(**kwargs):
        assert kwargs['input_ids'].data == [[7, 8, 2, 3], [0, 7, 2, 3]]
        assert kwargs['attention_mask'].data == [[1, 1, 1, 1], [0, 1, 1, 1]]
        assert kwargs['max_new_tokens'] == study.CAP - 2
        assert not kwargs['do_sample'] and kwargs['use_cache']
        return Tensor([[7, 8, 2, 3, 99, 0], [0, 7, 2, 3, 99, 0]])
    model = SimpleNamespace(device='fake', generation_config=SimpleNamespace(eos_token_id=[99]), generate=generate)
    out = study.continuation_output(Tokenizer(), model, ['a', 'b'], dict(a=c1, b=c2), rows)
    assert all(r['output_token_ids'] == [2, 3, 99] and r['correct'] and not r['truncated'] for r in out)
    assert all(r['prefix_tokens'] == 2 and r['added_tokens'] == 1 for r in out)
    assert rows['a']['output_token_ids'] == [2, 3]


@pytest.mark.parametrize('fault', ['prompt', 'text', 'eos', 'completed', 'length'])
def test_continuation_rejects_invalid_saved_prefixes(monkeypatch, fault):
    monkeypatch.setitem(sys.modules, 'torch', SimpleNamespace())
    c = case(); r = dict(truncated=True, raw_response=' -3', output_token_ids=[2, 3])
    tokenizer = SimpleNamespace(eos_token_id=99)
    class Tokenizer:
        eos_token_id = 99
        def __call__(self, *args, **kwargs): return dict(input_ids=[0] if fault == 'prompt' else [7, 8])
        def decode(self, *args, **kwargs): return 'wrong' if fault == 'text' else ' -3'
    if fault == 'eos': r['output_token_ids'] = [99]
    if fault == 'completed': r['truncated'] = False
    if fault == 'length': r['output_token_ids'] = [2] * study.CAP
    model = SimpleNamespace(generation_config=SimpleNamespace(eos_token_id=99))
    with pytest.raises(ValueError): study.continuation_output(Tokenizer(), model, ['one'], {'one': c}, {'one': r})
