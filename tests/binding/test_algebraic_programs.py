from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

import pytest

from codecue.binding import algebraic_programs as study


@pytest.fixture
def config(tmp_path):
    return dict(evaluation_role=study.ROLE, seed=20261027, numeric_instances=1,
                dataset=str(tmp_path / 'algebraic.jsonl'), review=str(tmp_path / 'review.json'),
                report=str(tmp_path / 'algebraic.md'))


def test_balanced_strata_components_graphs_and_independent_full_python_traces(config):
    rows = study.make_rows(config)
    assert study.make_rows(config) == rows
    result = study.validate_rows(config, rows, independent=True)
    assert result['rows'] == 486 and len({row['id'] for row in rows}) == 486
    assert result['split_rows'] == dict(train=324, development=162)
    assert result['split_components'] == dict(train=18, development=9)
    assert result['split_definition_graphs'] == dict(train=54, development=27)
    assert result['numeric_stratum_rows'] == dict.fromkeys(study.STRATA, 162)
    assert result['split_numeric_stratum_rows'] == {'train': dict.fromkeys(study.STRATA, 108),
                                                   'development': dict.fromkeys(study.STRATA, 54)}
    assert result['cross_split_overlap'] == dict(source=0, canonical_ast=0, alpha_structure=0)
    assert result['equal_pair_same_values_different_graph'] == 54
    assert result['independent_python_passed'] and result['independent_python_programs'] == 729


def test_each_stratum_has_valid_literal_targets_and_all_relatives_stay_component(config):
    rows = study.make_rows(config)
    balance, splits, values = Counter(), defaultdict(set), defaultdict(set)
    for row in rows:
        target = row['targets']; a, b, c, d = target['initial_values']; stratum = target['numeric_stratum']
        assert all(v and abs(v) <= 12 for v in (a, b, c, d))
        if stratum == 'distinct_uniform': assert len({a, b, c, d}) == 4
        elif stratum == 'additive_triplet': assert a + b == c and len({a, b, c, d}) == 4
        else: assert b == c and len({a, b, d}) == 3
        balance[row['component_id'], stratum] += 1
        splits[row['component_id']].add(row['split'])
        values[row['component_id']].add(tuple(target['initial_values']))
        assert len(row['execution_trace']) == 8 and len(row['versioned_bindings']) == 8
        assert row['query_role'] == 'v0' and row['query_count'] == 1
    assert len(balance) == 81 and set(balance.values()) == {6}
    assert all(len(s) == 1 for s in splits.values())
    assert all(len(v) == 3 for v in values.values())


def test_default_four_draws_produces_1944_rows_with_1296_train_and_648_dev(config):
    config.pop('numeric_instances')
    rows = study.make_rows(config)
    assert len(rows) == 1944 and Counter(row['split'] for row in rows) == dict(train=1296, development=648)
    assert Counter(row['targets']['numeric_stratum'] for row in rows) == dict.fromkeys(study.STRATA, 648)


@pytest.mark.parametrize('field,value', [('evaluation_role', 'final'), ('seed', True), ('seed', -1),
    ('numeric_instances', True), ('numeric_instances', 0), ('numeric_instances', 65), ('extra', 1)])
def test_invalid_schema_and_reserved_paths_fail_before_writes(config, field, value):
    config[field] = value
    with pytest.raises(ValueError): study.build(config)
    assert not Path(config['dataset']).exists()


def test_reserved_symlink_and_overlapping_outputs_are_rejected(config, tmp_path):
    target = tmp_path / 'heldout.jsonl'; target.write_text('sealed')
    Path(config['dataset']).symlink_to(target)
    with pytest.raises(ValueError, match='reserved'): study.make_rows(config)
    Path(config['dataset']).unlink()
    config['review'] = str(Path(config['dataset']).with_suffix('.manifest.json'))
    with pytest.raises(ValueError, match='distinct'): study.make_rows(config)


@pytest.mark.parametrize('change', ['answer', 'stratum', 'values', 'graph', 'split', 'missing'])
def test_target_corruption_or_missing_factorial_rows_are_refused(config, change):
    rows = deepcopy(study.make_rows(config))
    if change == 'answer': rows[0]['expected_answer'] += 1
    elif change == 'stratum': rows[0]['targets']['numeric_stratum'] = 'equal_pair'
    elif change == 'values': rows[0]['targets']['initial_values'][0] = 0
    elif change == 'graph': rows[0]['dependency_edges'].pop()
    elif change == 'split': rows[0]['split'] = 'train'
    else: rows.pop()
    with pytest.raises(ValueError, match='fixed source/target factorial'): study.validate_rows(config, rows)


def test_immutable_build_and_review_logging(config, monkeypatch):
    from codecue.binding import experiment_log
    logged = []
    monkeypatch.setattr(experiment_log, 'note_artifact', lambda path: logged.append(str(path)))
    monkeypatch.setattr(study, 'code_identity', lambda: {'source_sha256': 'b' * 64})
    result = study.build(config)
    paths = [Path(config[k]) for k in ('dataset', 'review', 'report')]
    paths.append(Path(config['dataset']).with_suffix('.manifest.json'))
    original = {path: path.read_bytes() for path in paths}
    assert study.build(config) == result and {path: path.read_bytes() for path in paths} == original
    assert str(Path(config['review']).resolve()) in logged
    assert not result['relation_decoding_performed'] and result['new_model_queries'] == 0
    with pytest.raises(ValueError, match='immutable'): study.build(dict(config, seed=config['seed'] + 1))
    assert {path: path.read_bytes() for path in paths} == original
