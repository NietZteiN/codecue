from copy import deepcopy
import pytest
from codecue.binding import arithmetic_paired_programs as p
from codecue.binding import arithmetic_paired_stage as stage
from codecue.binding import arithmetic_paired_calibration as calibration


def example(**kwargs):
    family = dict(id='toy', split='train', depth=0, updates=())
    options = dict(operator='+', mutation='operand', delay=0, lexical=0, order=0)
    options.update(kwargs)
    return p.row(family, 20261101, (2, 5, -1, 9), 9, **options)


def test_retention_is_not_recomputation():
    r = example()
    assert r['expected_answer'] == 7
    assert r['error_candidates']['recomputed_current_operands'] == 14
    assert r['error_candidates']['stale_target'] == -1
    assert p.validate_one(r)
    control = example(mutation='irrelevant')
    assert control['expected_answer'] == 7
    assert control['error_candidates']['recomputed_current_operands'] == 7


def test_same_bag_binding_twins_change_target_without_value_inventory_change():
    first, second = example(binding_swap=False), example(binding_swap=True)
    assert first['expected_answer'] == 7 and second['expected_answer'] == -3
    assert sorted(first['final_values']) == sorted(second['final_values'])
    assert p.token_bag(first['body']) == p.token_bag(second['body'])
    assert second['target_operator'] == '-'


@pytest.mark.parametrize('delay', [0, 4, 12])
@pytest.mark.parametrize('lexical,order', [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_delay_rename_and_root_order_preserve_values_and_group_keys(delay, lexical, order):
    first = example(); other = example(delay=delay, lexical=lexical, order=order)
    assert first['final_values'] == other['final_values']
    assert first['expected_answer'] == other['expected_answer']
    assert first['structural_keys'] == other['structural_keys']
    assert p.validate_one(other)


def test_connected_components_include_bridging_relatives():
    assert p.closure([{'a'}, {'b'}, {'a', 'b'}, {'c'}]) == [[0, 1, 2], [3]]


def test_live_key_drops_dead_context_and_full_key_retains_it():
    a = 'v0 = 1\nv1 = 2\nv2 = 3\nv3 = 4\nv2 = v0 + v1'
    b = 'v0 = 8\nv1 = -9\nv2 = 0\nv3 = 1\nv3 = v0 - v1\nv2 = v0 + v1'
    assert p.structural_keys(a)[0] != p.structural_keys(b)[0]
    assert p.structural_keys(a)[1] == p.structural_keys(b)[1]


def test_actual_closed_families_and_copy_collapse():
    families, review = p.families()
    assert len(families) == 128
    assert review['split_components'] == {'train': 96, 'development': 32}
    assert review['components_if_copy_relatives_joined'] < 128
    seen = set()
    for family in families:
        assert p.all_prefix_live(family['updates'])
        assert p.nondegenerate(family['updates'])
        assert not seen.intersection(family['closure_keys'])
        seen.update(family['closure_keys'])


def test_symbolic_zero_targets_are_not_independent_hard_families():
    assert not p.nondegenerate(((0, 0, 1, '+'), (1, 0, 0, '-')))


def test_full_one_family_factorial_pair_checks_and_independent_oracle():
    rows = list(p.iter_rows(p.families()[0][:1]))
    assert len(rows) == 216 and len({r['id'] for r in rows}) == 216
    assert stage.paired_checks(rows) == {'retention_pairs': 72, 'same_bag_pairs': 36}
    truths = p.interpreter.python_oracle([r['body'] + '\n' + r['target_name'] for r in rows])
    for row, truth in zip(rows, truths): assert p.validate_one(row, truth)
    broken = deepcopy(rows); broken[0]['expected_answer'] += 1
    with pytest.raises(ValueError): stage.paired_checks(broken)


def test_calibration_stays_outside_fits_and_all_sources_validate():
    rows = list(p.calibration_rows())
    assert len(rows) == 216
    for r in rows:
        assert r['split'] == 'calibration'
        assert p.validate_one(r)


def test_later_use_labels_parent_before_self_assignment():
    row = example(delay=4)
    point = p.sites(row)[2]
    last = row['oracle']['execution_trace'][-1]
    before = row['oracle']['execution_trace'][-2]
    assert point['read_definitions'] == [before['versions'][row['target_name']]]
    assert point['read_definitions'][0] != last['definition']
    assert all(v['value'] == 7 for v in p.sites(row))
    assert not p.sites(row)[0]['target_literal_visible']


@pytest.mark.parametrize('scope,text,expected', [
    ('single', 'Answer: 1\n\nwork\nAnswer: -7', [-7]),
    ('single', 'Answer: +3', [3]),
    ('all', 'Answer: [2, -5, +7, 0]', [2, -5, 7, 0]),
])
def test_answer_parsers_use_last_answer_and_order(scope, text, expected):
    assert p.parse_answer(text, scope) == dict(valid=True, values=expected)


@pytest.mark.parametrize('scope,text', [('single', '7'), ('single', 'Answer: 7.0'),
    ('single', 'Answer: 7 extra'), ('all', 'Answer: [1,2,3]'), ('all', 'Answer: [1,2,3,4,5]'),
    ('all', 'Answer: [1,2,true,4]'), ('all', 'Answer: [1,2,3.5,4]')])
def test_invalid_outputs_are_retained_as_invalid(scope, text):
    assert not p.parse_answer(text, scope)['valid']


class CharacterTokenizer:
    chat_template = 'fake native character tokenizer for source-boundary tests'
    def __init__(self, merge_newline=False, swallow=False):
        self.merge_newline, self.swallow = merge_newline, swallow
        self.ids, self.text = {}, {}
    def apply_chat_template(self, messages, **kwargs):
        return 'USER\n' + messages[0]['content'] + '\nASSISTANT\n'
    def __call__(self, prompt, **kwargs):
        tokens, offsets = [], []; i = 0
        while i < len(prompt):
            stop = i + 1
            if self.merge_newline and prompt[stop:stop + 1] == '\n':
                stop += 1
                if self.swallow and stop < len(prompt): stop += 1
            part = prompt[i:stop]
            if part not in self.ids:
                token = len(self.ids) + 1; self.ids[part] = token; self.text[token] = part
            tokens.append(self.ids[part]); offsets.append((i, stop)); i = stop
        return dict(input_ids=tokens, offset_mapping=offsets)
    def decode(self, tokens, **kwargs): return ''.join(self.text[t] for t in tokens)


def test_prompt_contains_source_but_not_oracle_or_metadata():
    row = example(); content = p.prompt_content(row, 'single', 'output_only', 0)
    assert row['body'] in content and 'print(v2)' in content
    assert 'oracle' not in content and 'component_id' not in content and 'expected_answer' not in content
    assert 'Answer: 7' not in content
    assert content[:content.index('print(')] == p.prompt_content(row, 'all', 'output_only', 2).split('print(')[0]


def test_native_matched_prefixes_and_protocol_generation_boundaries():
    tokenizer = CharacterTokenizer(); row = example()
    first = stage.layout(tokenizer, row, 'single', 'output_only', 0)
    for protocol in p.PROTOCOLS:
        for scope in p.SCOPES:
            other = stage.layout(tokenizer, row, scope, protocol, 2)
            assert [x['prefix_sha256'] for x in first['sites']] == [x['prefix_sha256'] for x in other['sites']]
            assert other['generated_answer_site_available'] == (protocol == 'output_only')
            assert other['expected'] == ([7] if scope == 'single' else row['final_values'])


def test_native_newline_collapse_and_future_exposure_are_explicit():
    row = example()
    case = stage.layout(CharacterTokenizer(merge_newline=True), row, 'single', 'output_only', 0)
    assert case['rhs_newline_collapsed']
    assert case['sites'][0]['position'] == case['sites'][1]['position']
    bad = stage.layout(CharacterTokenizer(merge_newline=True, swallow=True), row, 'single', 'output_only', 0)
    assert not bad['sites'][0]['available']
    assert bad['sites'][0]['unavailable_reason'] == 'native_token_contains_future_source'


def test_truncation_and_invalid_answers_remain_in_accuracy_denominator():
    case = stage.layout(CharacterTokenizer(), example(), 'single', 'output_only', 0)
    case['calibration_kind'] = None
    a = calibration.score_response(case, ' 7', [1], False)
    b = calibration.score_response(case, ' 7', [1], True)
    c = calibration.score_response(case, ' seven', [1], False)
    assert a['correct'] and not b['correct'] and not c['correct']
    summary = calibration.summarize([a, b, c])
    assert summary['cells']['overall']['rows'] == 3
    assert summary['cells']['overall']['joint_accuracy'] == 1/3
    assert summary['cells']['overall']['invalid_or_truncated'] == 2
    assert not summary['output_only_competence_passed']


def test_batch_resume_order_keeps_protocol_limits_separate():
    cases = [dict(id=str(i), scope='single', instruction=0, protocol=protocol)
        for i, protocol in enumerate(['stepwise', 'output_only', 'intermediate_query', 'output_only'])]
    result = list(calibration.batches(cases, 16))
    assert [i for i, _ in result] == [0, 2, 3]
    assert [rows[0]['protocol'] for _, rows in result] == list(p.PROTOCOLS)


def test_calibration_gate_requires_every_wording_and_scope():
    rows = []
    for scope in p.SCOPES:
        template = stage.layout(CharacterTokenizer(), example(), scope, 'output_only', 0)
        for kind in ('literal', 'copy', 'arithmetic'):
            for instruction in range(3):
                case = dict(template, calibration_kind=kind, instruction=instruction)
                text = ' 7' if scope == 'single' else ' [9, 5, 7, 9]'
                rows.append(calibration.score_response(case, text, [1], False))
    assert calibration.summarize(rows)['output_only_competence_passed']
    broken = deepcopy(rows); broken[0]['correct'] = False
    assert not calibration.summarize(broken)['output_only_competence_passed']
    assert not calibration.summarize(rows[1:])['output_only_competence_passed']
