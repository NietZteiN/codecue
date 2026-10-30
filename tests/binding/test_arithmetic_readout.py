"""Arithmetic feasibility checks use generated programs, never model fixtures."""
import ast
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path

import pytest

from codecue.binding import arithmetic_readout as study
from codecue.binding.interpreter import execute, python_oracle
from codecue.binding.published_benchmarks import sha


OPERATIONS = {
    'literal_output': 0, 'stored_output': 0,
    'literal_one': 1, 'bound_one': 1, 'stored_result_one': 1,
    'literal_three': 3, 'bound_three': 3, 'stored_intermediates_three': 3,
}


@pytest.fixture(scope='module')
def generated():
    generation = dict(seed=20261027, numeric_per_stratum=4, operand_max=17,
                      excluded_numeric_values=[])
    rows = study.make_rows(generation)
    return generation, rows


def sign(value):
    return 1 if value > 0 else -1


def test_same_answer_forms_have_independently_checked_subtraction_counts(generated):
    generation, rows = generated
    assert len(rows) == 6 * 4 * 8
    assert study.validate_rows(rows, generation, independent=True) == rows
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row['numeric_values'])].append(row)
    assert len(groups) == 24
    oracle = python_oracle([r['oracle_source'] for r in rows])
    for row, independent in zip(rows, oracle):
        a, b, c, d = row['numeric_values']
        expected = (a - b) - (c - d)
        assert expected != 0
        assert row['expected_answer'] == expected == independent['answer']
        assert execute(row['oracle_source'])['expected_answer'] == expected
        assert [point['values'] for point in row['execution_trace']] == independent['trace']
        operators = [node.op for node in ast.walk(ast.parse(row['source']))
                     if isinstance(node, ast.BinOp)]
        assert len(operators) == OPERATIONS[row['form']]
        assert all(isinstance(operator, ast.Sub) for operator in operators)
    for relatives in groups.values():
        assert Counter(r['form'] for r in relatives) == Counter(OPERATIONS.keys())
        assert len({r['expected_answer'] for r in relatives}) == 1


def test_signed_strata_and_mirror_groups_are_balanced_and_splits_are_disjoint(generated):
    _, rows = generated
    expected_strata = {(1, 1, 1), (1, 1, -1), (1, -1, 1),
                       (-1, 1, -1), (-1, -1, 1), (-1, -1, -1)}
    tuples = {tuple(r['numeric_values']): r for r in rows}
    strata = Counter()
    split_strata = Counter()
    paired_splits = defaultdict(set)
    forms = defaultdict(set)
    for values, row in tuples.items():
        a, b, c, d = values
        stratum = (sign(a - b), sign(c - d), sign((a - b) - (c - d)))
        assert tuple(row['sign_stratum']) == stratum
        strata[stratum] += 1
        split_strata[row['split'], stratum] += 1
        mirror = tuples[b, a, d, c]
        assert mirror['expected_answer'] == -row['expected_answer']
        assert mirror['paired_group_id'] == row['paired_group_id']
        assert mirror['split'] == row['split']
    assert set(strata) == expected_strata
    assert set(strata.values()) == {4}
    assert set(split_strata) == {(split, stratum) for split in ('train', 'development')
                                for stratum in expected_strata}
    assert set(split_strata.values()) == {2}
    for row in rows:
        paired_splits[row['paired_group_id']].add(row['split'])
        forms[row['base_id']].add(row['form'])
    assert all(len(splits) == 1 for splits in paired_splits.values())
    assert all(set(group) == set(OPERATIONS) for group in forms.values())
    assert {r['split'] for r in rows} == {'train', 'development'}


def test_nonzero_operation_prompts_are_unique_and_never_cross_splits(generated):
    _, rows = generated
    for form, operations in OPERATIONS.items():
        selected = [r for r in rows if r['form'] == form]
        if not operations:
            # Answer-only controls deliberately repeat a small answer domain.
            continue
        assert len({r['source'] for r in selected}) == len(selected)
        train = {r['source'] for r in selected if r['split'] == 'train'}
        development = {r['source'] for r in selected if r['split'] == 'development'}
        assert not train & development


def test_generation_is_deterministic_and_excludes_old_tuples_and_mirrors(generated):
    generation, rows = generated
    assert study.make_rows(generation) == rows
    assert study.make_rows({**generation, 'seed': generation['seed'] + 1}) != rows
    old = list(rows[0]['numeric_values'])
    a, b, c, d = old
    excluded = study.make_rows({**generation, 'excluded_numeric_values': [old]})
    values = {tuple(r['numeric_values']) for r in excluded}
    assert tuple(old) not in values
    assert (b, a, d, c) not in values
    assert len(excluded) == len(rows)
    study.validate_rows(excluded, {**generation, 'excluded_numeric_values': [old]})


def test_default_numeric_bank_has_64_unique_prompts_per_signed_stratum():
    rows = study.make_rows(dict(seed=20261027, operand_max=17,
                                excluded_numeric_values=[]))
    tuples = {tuple(row['numeric_values']): row for row in rows}
    assert len(rows) == 6 * 64 * 8
    assert len(tuples) == 6 * 64
    assert set(Counter(tuple(r['sign_stratum']) for r in tuples.values()).values()) == {64}
    assert set(Counter((r['split'], tuple(r['sign_stratum'])) for r in tuples.values()).values()) == {32}
    assert all(len(set(values)) == 4 and all(1 <= value <= 17 for value in values)
               for values in tuples)
    folded = {(a - b, c - d) for a, b, c, d in tuples}
    assert len(folded) == len(tuples)
    for form, count in OPERATIONS.items():
        if count:
            prompts = [r['source'] for r in rows if r['form'] == form]
            assert len(set(prompts)) == len(prompts)


def test_small_numeric_bank_and_compatible_count_alias(generated):
    generation, rows = generated
    alias = {k: v for k, v in generation.items() if k != 'numeric_per_stratum'}
    aliased_rows = study.make_rows({**alias, 'tuples_per_stratum': 4})
    # The spelling of the supplied configuration remains in its provenance hash.
    assert [{k: v for k, v in r.items() if k != 'generation_config_hash'} for r in aliased_rows] == [
        {k: v for k, v in r.items() if k != 'generation_config_hash'} for r in rows]
    assert len(study.make_rows({**generation, 'operand_max': 9})) == len(rows)
    with pytest.raises(ValueError):
        study.make_rows({**generation, 'tuples_per_stratum': 6})
    with pytest.raises(ValueError):
        study.make_rows({**generation, 'numeric_per_stratum': 64, 'operand_max': 9})


@pytest.mark.parametrize('count', [0, 1, 3, -2, True])
def test_numeric_count_requires_complete_even_sign_groups(count):
    with pytest.raises(ValueError):
        study.make_rows(dict(seed=17, numeric_per_stratum=count, operand_max=17,
                             excluded_numeric_values=[]))


@pytest.mark.parametrize('change', ['answer', 'trace', 'duplicate', 'split', 'form', 'operations'])
def test_validation_rejects_changed_semantics_and_broken_relative_groups(generated, change):
    generation, rows = generated
    bad = deepcopy(rows)
    index = next(i for i, r in enumerate(bad) if r['form'] == 'bound_three')
    if change == 'answer':
        bad[index]['expected_answer'] += 1
    elif change == 'trace':
        bad[index]['execution_trace'][0]['value'] += 1
    elif change == 'duplicate':
        bad.append(deepcopy(bad[index]))
    elif change == 'split':
        bad[index]['split'] = 'development' if bad[index]['split'] == 'train' else 'train'
    elif change == 'form':
        bad[index]['form'] = 'literal_one'
    elif change == 'operations':
        bad[index]['operation_count'] = 1
    with pytest.raises(ValueError):
        study.validate_rows(bad, generation)


def test_dataset_build_is_idempotent_and_refuses_a_changed_generation(tmp_path, generated):
    generation, rows = generated
    path = tmp_path / 'arithmetic.jsonl'
    config = dict(dataset=str(path), generation=generation)
    first = study.build(config)
    manifest = path.with_suffix('.manifest.json')
    original = path.read_bytes(), manifest.read_bytes()
    assert first['rows'] == len(rows)
    assert first['sha256'] == sha(path)
    assert first['evaluation_role'] == study.ROLE
    assert json.loads(manifest.read_text()) == first
    assert study.build(config) == first
    assert (path.read_bytes(), manifest.read_bytes()) == original
    with pytest.raises(ValueError):
        study.build({**config, 'generation': {**generation, 'seed': generation['seed'] + 1}})
    assert (path.read_bytes(), manifest.read_bytes()) == original


def synthetic_review_records(rows):
    """Complete fake score matrix for software checks, never model evidence."""
    from codecue.binding.arithmetic_readout_review import PROTOCOLS
    return [(dict(kind='arithmetic_readout', variant=protocol, record=deepcopy(row)),
             dict(score=dict(correct=True, valid=True)))
            for protocol in PROTOCOLS for row in rows]


def test_review_retains_both_protocols_all_cells_and_a_failed_development_gate(generated):
    from codecue.binding.arithmetic_readout_review import summarize
    _, rows = generated
    records = synthetic_review_records(rows)
    for case, response in records:
        row = case['record']
        if not OPERATIONS[row['form']]:
            response['score'].update(correct=False, valid=False)
        if (case['variant'] == 'print_direct_v3' and row['split'] == 'development'
                and row['form'] == 'literal_three' and tuple(row['sign_stratum']) == (1, 1, 1)):
            response['score']['correct'] = False
    result = summarize(records, dict(reliability_gate=dict(minimum_cell_n=2),
                                     bootstrap_replicates=128, bootstrap_seed=9))
    assert result['complete'] and result['status'] == 'complete_audited'
    assert len(result['cells']) == 2 * 8 * 2 * 6
    assert len(result['form_cells']) == 2 * 8 * 3
    assert len(result['contrasts']) == 2 * 3 * 6
    assert result['n'] == len(records)
    gate = result['reliability_gate']
    assert gate['status'] == 'mixed'
    direct = gate['protocols']['print_direct_v3']
    trace = gate['protocols']['print_trace_long_v1']
    assert direct['training_qualified'] and not direct['numeric_development_qualified']
    assert direct['status'] == 'failed'
    assert trace['training_qualified'] and trace['numeric_development_qualified']
    assert trace['status'] == 'passed'
    assert all(c['operation_count'] > 0 for c in direct['cells'])
    assert all(c['invalid_rate'] == 1 for c in direct['zero_operation_controls'])
    contrast = next(c for c in result['contrasts']
                    if c['variant'] == 'print_direct_v3' and c['split'] == 'development'
                    and c['name'] == 'three_literal_minus_one_literal')
    assert contrast['n'] == 12 and contrast['paired_groups'] == 6
    assert contrast['mean'] == pytest.approx(-1 / 6)
    assert not result['generated_holdouts_opened']


def test_paired_uncertainty_keeps_whole_numeric_relative_groups():
    from codecue.binding.arithmetic_readout_review import paired_contrast
    values = [('positive_group', 1)] * 20 + [('negative_group', -1)] * 20
    result = paired_contrast('software_check', values, draws=1000, seed=9)
    assert result['n'] == 40 and result['paired_groups'] == 2
    assert result['mean'] == 0
    assert result['exploratory_group_bootstrap_95'] == [-1., 1.]
    assert 'paired_group_id' in result['resampling_unit']
    assert paired_contrast('software_check', values, draws=1000, seed=9) == result


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'source_overlap'])
def test_review_refuses_incomplete_or_duplicated_cells_and_nonzero_prompt_leakage(generated, change):
    from codecue.binding.arithmetic_readout_review import summarize
    _, rows = generated
    records = synthetic_review_records(rows)
    if change == 'missing':
        records.pop()
    elif change == 'duplicate':
        records.append(deepcopy(records[0]))
    else:
        train = next(c['record'] for c, _ in records
                     if c['variant'] == 'print_direct_v3' and c['record']['split'] == 'train'
                     and c['record']['form'] == 'literal_one')
        development = next(c['record'] for c, _ in records
                           if c['variant'] == 'print_direct_v3' and c['record']['split'] == 'development'
                           and c['record']['form'] == 'literal_one')
        development['source'] = train['source']
    with pytest.raises(ValueError):
        summarize(records, dict(reliability_gate=dict(minimum_cell_n=2), bootstrap_replicates=128))
