from copy import deepcopy

import numpy as np
import pytest

from codecue.binding import arithmetic_local_programs as programs
from codecue.binding import arithmetic_local_capture as capture
from codecue.binding import arithmetic_state_audit as audit
from codecue.binding import arithmetic_state_common as common
from codecue.binding import arithmetic_binding_readouts as binding
from codecue.binding import arithmetic_numeric_readouts as numeric
from codecue.binding import arithmetic_state_compose as compose
from codecue.binding import arithmetic_capacity_followup as capacity
from test_arithmetic_local_programs import CharacterTokenizer


@pytest.fixture(scope='module')
def cohort():
    rows = programs.make_rows()
    selected = [next(r for r in rows if r['depth'] == depth and r['lexical_realization'] == lexical)
        for depth, lexical in [(1, 0), (2, 1), (4, 0), (6, 1)]]
    cases = [capture.layout(CharacterTokenizer(), r) for r in selected]
    return selected, cases


def test_independent_trace_handles_renaming_overwrites_and_read_before_write(cohort):
    rows, _ = cohort
    for row in rows:
        audit.independent_trace(row)
    bad = deepcopy(rows[-1])
    bad['oracle']['writes'][4]['parents'][0] = 99
    with pytest.raises(ValueError):
        audit.independent_trace(bad)


def test_independent_metrics_separate_family_micro_and_complete_graphs():
    table = [dict(group=g, case_id=g, depth=2, side='left') for g in ['a', 'a', 'a', 'b']]
    logits = np.tile([2., 1.], (4, 1))
    result = audit.independent_metrics(logits, np.asarray([0, 0, 0, 1]), table)
    assert result['individual_accuracy'] == .75
    assert result['family_macro_accuracy'] == result['whole_program_graph_accuracy'] == .5
    assert result['family_whole_program'] == dict(a=1., b=0.)


@pytest.mark.parametrize('change', ['decision', 'large', 'mask', 'nan'])
def test_independent_score_replay_rejects_failures(change):
    actual = np.asarray([[.5, .5, -1e9]])
    saved = actual.copy()
    mask = np.asarray([[True, True, False]])
    if change == 'decision':
        saved[0, 1] += 1e-13
    elif change == 'large':
        saved[0, 0] += .1
    elif change == 'mask':
        saved[0, -1] = -1e8
    else:
        saved[0, 0] = np.nan
    with pytest.raises(ValueError):
        audit.replay_check(actual, saved, mask)


def test_small_replay_roundoff_is_allowed_with_identical_decisions():
    a = np.asarray([[1., .2, -1e9]])
    b = a.copy();b[0, 0] += 1e-7
    assert audit.replay_check(a, b, np.asarray([[True, True, False]])) < 1e-6


def test_family_control_is_complete_and_stays_within_split_and_stratum():
    rows = programs.make_rows()
    donor = common.donors(rows)
    assert len(set(donor.tolist())) == len(rows)
    for i, j in enumerate(donor):
        assert rows[i]['component_id'] != rows[j]['component_id']
        assert all(rows[i][k] == rows[j][k] for k in ['split', 'family_stratum', 'numeric_seed', 'numeric_draw', 'lexical_realization'])


def test_family_balancing_does_not_count_numeric_relatives_as_new_families():
    table = [dict(group='a') for _ in range(10)] + [dict(group='b') for _ in range(2)]
    w = common.weights(table, 11)
    small = common.weights([dict(group='a'), dict(group='b')], 11)
    np.testing.assert_allclose(w[:10].sum() / w[10:].sum(), small[0] / small[1], rtol=1e-6)
    assert np.isclose(w.mean(), 1.)


def test_binding_features_use_all_candidate_nodes_without_gold_pruning(cohort):
    rows, cases = cohort
    table = binding.examples(rows, cases)
    nodes = np.arange(len(rows) * 23 * 64, dtype=np.float32).reshape(len(rows), 23, 64)
    for backend in binding.BACKENDS:
        q, c, mask = binding.features(nodes, table, cases, backend)
        for i, e in enumerate(table):
            assert mask[i].sum() == 4 + e['depth']
            assert mask[i, e['parent']]
        if backend == 'position_only':
            assert not q[:, :64].any() and not c[:, :, :64].any()
        poisoned = [dict(e, parent=99) for e in table]
        actual = binding.features(nodes, poisoned, cases, backend)
        for a, b in zip((q, c, mask), actual):
            np.testing.assert_array_equal(a, b)


def test_binding_anchor_and_answer_queries_use_distinct_requested_states(cohort):
    rows, cases = cohort
    table = binding.examples(rows, cases)
    nodes = np.arange(len(rows) * 23 * 64, dtype=np.float32).reshape(len(rows), 23, 64)
    anchor, _, _ = binding.features(nodes, table, cases, 'anchor_query')
    answer, _, _ = binding.features(nodes, table, cases, 'answer_query')
    for i, e in enumerate(table):
        np.testing.assert_array_equal(anchor[i, :64], nodes[e['row'], e['slot']])
        np.testing.assert_array_equal(answer[i, :64], nodes[e['row'], cases[e['row']]['point_count'] - 1])


def binding_records():
    return [dict(backend=b, method=m, fold=f, seed=s, validation=dict(family_macro_accuracy=.5))
        for b in binding.BACKENDS for m in ('linear', 'bilinear', 'mlp') for f in range(3) for s in common.SEEDS]


def test_binding_selection_requires_all_folds_and_seeds_and_has_fixed_tie_rule():
    assert set(binding.choose(binding_records()).values()) == {'linear'}
    with pytest.raises(ValueError):
        binding.choose(binding_records()[:-1])


def test_numeric_role_blocks_distinguish_read_and_write_at_same_token(cohort):
    rows, cases = cohort
    table = numeric.examples(rows, cases)
    nodes = np.ones((len(rows), 23, 64), np.float32)
    x = numeric.features(nodes, table)
    assert x.shape == (len(table), 272)
    for i, e in enumerate(table):
        block = numeric.ROLES.index(e['role'])
        assert x[i, block * 64:(block + 1) * 64].sum() == 64
        assert x[i, :256].sum() == 64
    # Point-role requests differ even when their raw hidden vectors are equal.
    written = next(i for i, e in enumerate(table) if e['role'] == 'computed_definition')
    read = next(i for i, e in enumerate(table) if e['role'] == 'right_use')
    assert not np.array_equal(x[written], x[read])
    poisoned = [dict(e, value=99999, target_kind='poison') for e in table]
    np.testing.assert_array_equal(x, numeric.features(nodes, poisoned))


def test_integer_encodings_round_trip_at_domain_boundaries():
    values = np.asarray([-96, -1, 0, 96])
    target = numeric.labels(values)
    assert target.shape == (4, 194)
    np.testing.assert_array_equal(numeric.decode(target, 'regression'), values)
    np.testing.assert_array_equal(numeric.decode(target, 'categorical'), values)
    with pytest.raises(ValueError):
        numeric.labels(np.asarray([97]))


def test_numeric_prior_cannot_use_development_values():
    table, values, training = [], [], []
    for role in numeric.ROLES:
        for value, is_train in [(1, True), (3, True), (90, False)]:
            table.append(dict(role=role));values.append(value);training.append(is_train)
    values, training = np.asarray(values), np.asarray(training)
    expected = numeric.prior(values, table, training, np.ones(training.sum()), 'regression')
    assert (expected == 2).all()
    values[~training] = -96
    np.testing.assert_array_equal(expected, numeric.prior(values, table, training, np.ones(training.sum()), 'regression'))


def numeric_records():
    return [dict(representation=r, fold=f, seed=s, candidates=[dict(alpha=a, format=k,
        metrics=dict(per_kind=dict(computed_definition=dict(family_macro_mae=2.)))) for a in numeric.ALPHAS for k in numeric.FORMATS])
        for r in ['hidden_layer_24', 'source_char'] for f in range(3) for s in common.SEEDS]


def test_numeric_selection_uses_declared_computed_target_and_complete_grid():
    chosen = numeric.choose(numeric_records(), ['hidden_layer_24', 'source_char'])
    assert chosen['hidden']['regression']['alpha'] == 10000.
    with pytest.raises(ValueError):
        numeric.choose(numeric_records()[:-1], ['hidden_layer_24', 'source_char'])


def test_routing_uses_predicted_nodes_not_oracle_values(cohort):
    rows, cases = cohort
    pointers = np.tile(np.arange(4), (len(rows), 1))
    predictions = np.arange(len(rows) * 23, dtype=float).reshape(len(rows), 23)
    actual = compose.route_values(pointers, predictions, cases)
    expected = predictions[:, :4]
    np.testing.assert_array_equal(actual, expected)
    poisoned = deepcopy(cases)
    for case in poisoned:
        for d in case['descriptors']:
            d['value'] = -99999
    np.testing.assert_array_equal(actual, compose.route_values(pointers, predictions, poisoned))
    pointers[0, 0] = 99
    with pytest.raises(ValueError):
        compose.route_values(pointers, predictions, cases)


def test_operand_composition_uses_decoded_reads_and_operator_only(cohort):
    rows, cases = cohort
    values = np.full((len(rows), 23), 2.)
    actual = compose.operand_composition(values, rows, cases)
    for i, case in enumerate(cases):
        for point, descriptor in enumerate(case['descriptors']):
            if descriptor['kind'] == 'definition' and descriptor['statement'] >= 4:
                assert actual[i, point] in (0., 4.)
    poisoned = deepcopy(cases)
    for case in poisoned:
        for d in case['descriptors']:
            d['value'] = 987654
    np.testing.assert_array_equal(actual, compose.operand_composition(values, rows, poisoned))


def test_composed_state_and_relation_metrics_have_correct_oracle_ceiling():
    truth = np.asarray([[1, 2, 3, 5], [3, 1, 4, 4], [0, -2, -2, 1]])
    result = compose.metrics(truth.astype(float), truth, np.asarray(['a', 'a', 'b']), np.ones(48, bool))
    assert result['whole_state_accuracy'] == result['family_macro_value_accuracy'] == 1.
    assert result['family_macro_mae'] == 0
    assert result['relations']['macro_balanced_accuracy'] == 1.
    altered = truth.astype(float);altered[0, 0] += 1
    assert compose.metrics(altered, truth, np.asarray(['a', 'a', 'b']), np.ones(48, bool))['whole_state_accuracy'] == 2 / 3


def test_capacity_followup_only_fills_missing_architecture_counterparts():
    assert capacity.missing_cells(dict(hidden_local='bilinear', hidden_global='linear', source_local='bilinear')) == [('hidden_global', 'bilinear')]
    assert capacity.missing_cells(dict(hidden_local='mlp', hidden_global='bilinear', source_local='bilinear')) == [('hidden_global', 'mlp'), ('source_local', 'mlp')]
