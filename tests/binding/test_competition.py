from collections import defaultdict
from copy import deepcopy

import pytest

from codecue.binding.competition import build, read_jsonl, validate_rows, alpha_skeleton
from codecue.binding.checkpoint_suite import score_case


@pytest.fixture(scope='module')
def bank(tmp_path_factory):
    path = tmp_path_factory.mktemp('competition') / 'bank.jsonl'
    manifest = build(dict(dataset=str(path), seed=2026102601, numeric_per_template=1))
    return read_jsonl(path), manifest


def test_competition_pairs_preserve_semantics_and_exclude_structural_split_leakage(bank):
    rows, manifest = bank
    assert len(rows) == 1248 and manifest['independent_python_programs'] == 1248
    assert manifest['structural_components'] > 1
    split_by_shape = defaultdict(set)
    for row in rows:split_by_shape[alpha_skeleton(row['canonical_source'])].add(row['split'])
    assert all(len(splits) == 1 for splits in split_by_shape.values())
    assert {r['split'] for r in rows} == {'train', 'development'}
    assert validate_rows(rows) == rows


@pytest.mark.parametrize('change,reason', [('answer', 'oracle'), ('updates', 'version count'),
                                        ('role', 'semantic naming'), ('split', 'split leakage')])
def test_competition_rejects_corrupt_semantics_roles_and_group_splits(bank, change, reason):
    rows = deepcopy(bank[0])
    row = next(r for r in rows if r['family'] == 'versions')
    if change == 'answer':row['expected_answer'] += 1
    elif change == 'updates':row['updates'] = 9
    elif change == 'role':row['condition'] = 'neutral' if row['condition'] != 'neutral' else 'misleading'
    else:
        row['split'] = 'development' if row['split'] == 'train' else 'train'
        # Keep this row's surface metadata consistent to exercise split grouping.
        from codecue.binding.competition import names_for, rename, execute, digest, error_alternatives
        row['rename_map'] = names_for(row, row['condition'], row['lexical_realization'])
        row['source'] = rename(row['canonical_source'], row['rename_map'])
        row['id'] = 'competition:' + digest([row['source'], row['family']])[:24]
        row['execution_trace'] = execute(row['source'])['execution_trace']
        row['error_alternatives'] = error_alternatives(row['source'])
    with pytest.raises(ValueError, match=reason):validate_rows(rows)


def test_error_labels_are_semantic_alternatives_rather_than_claimed_causes(bank):
    row = next(r for r in bank[0] if r['family'] == 'versions' and r['updates'] == 3 and r['query_role'] == 'current')
    value = next(a['value'] for a in row['error_alternatives'] if a['label'].startswith('obsolete_assignment:'))
    result = score_case(dict(kind='competition', variant='print_direct_v3', record=row), str(value))
    assert result['valid'] and not result['correct']
    assert any(label.startswith('obsolete_assignment:') for label in result['compatible_error_labels'])
