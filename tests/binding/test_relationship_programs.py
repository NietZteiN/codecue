from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path

import pytest

from codecue.binding import relationship_programs as study
from codecue.binding.interpreter import execute


@pytest.fixture
def config(tmp_path):
    return {'evaluation_role': study.ROLE, 'seed': 20261027, 'numeric_instances': 1,
            'dataset': str(tmp_path / 'routing.jsonl'), 'review': str(tmp_path / 'review.json'),
            'report': str(tmp_path / 'routing.md')}


@pytest.fixture(scope='module')
def rows(tmp_path_factory):
    folder = tmp_path_factory.mktemp('relationship-routing')
    config = {'evaluation_role': study.ROLE, 'seed': 20261027, 'numeric_instances': 1,
              'dataset': str(folder / 'routing.jsonl'), 'review': str(folder / 'review.json'),
              'report': str(folder / 'routing.md')}
    return config, study.make_rows(config)


def test_complete_factorial_has_varied_disjoint_graphs_and_independent_full_traces(rows):
    config, bank = rows
    result = study.validate_rows(config, bank, independent=True)
    assert result['rows'] == 162
    assert result['split_rows'] == {'train': 108, 'development': 54}
    assert result['split_components'] == {'train': 18, 'development': 9}
    assert result['split_definition_graphs'] == {'train': 54, 'development': 27}
    assert result['distinct_definition_graphs'] == 81
    assert result['paired_same_values_different_graph'] == 54
    assert result['paired_descendant_sensitivity_checks'] == 108
    assert result['cross_split_overlap'] == dict(source=0, canonical_ast=0, alpha_structure=0)
    assert result['independent_python_passed'] and result['independent_python_programs'] > 162


def test_rewired_twins_match_every_numeric_state_but_root_intervention_distinguishes_ancestry(rows):
    _, bank = rows
    groups = defaultdict(dict)
    for row in bank:
        if row['lexical_realization'] == 0:
            groups[row['base_id']][row['targets']['parent_by_destination']['v0']] = row
    for variants in groups.values():
        left, right, other = [variants[name] for name in ('v1', 'v2', 'v3')]
        ltruth, rtruth = [row['targets']['canonical_oracle'] for row in (left, right)]
        assert [p['values'] for p in ltruth['execution_trace']] == [p['values'] for p in rtruth['execution_trace']]
        assert ltruth['dependency_edges'] != rtruth['dependency_edges']
        assert left['expected_answer'] == right['expected_answer'] != other['expected_answer']
        b = left['targets']['initial_values']['b']
        for root in ('v1@1', 'v2@1'):
            alternatives = [execute(row['canonical_source'], {root: b + 1}) for row in (left, right)]
            assert alternatives[0]['execution_trace'][4]['value'] != alternatives[1]['execution_trace'][4]['value']
            # Store all final values, including paths reset by later copies.
            assert all(set(item['final_values']) == set(study.VARIABLES)
                       for row in (left, right) for item in row['targets']['functional_counterfactuals'])


def test_obsolete_nodes_preserved_and_neutral_identifiers_disjoint_across_splits(rows):
    _, bank = rows
    names = defaultdict(set)
    for row in bank:
        names[row['split']].update(row['rename_map'].values())
        oracle = row['targets']['canonical_oracle']
        assert len(oracle['versioned_bindings']) == 8
        assert len(oracle['dependency_edges']) == 5  # four copies plus output.
        assert all(name in oracle['versioned_bindings'] for name in ('v0@1', 'v0@2', 'v1@1', 'v1@2'))
        assert row['condition'] == 'neutral' and row['query_count'] == 1 and row['query_role'] == 'v0'
    assert not names['train'] & names['development']


def test_default_eight_draws_gives_1296_rows_and_numeric_draws_unique_within_component(config):
    config.pop('numeric_instances')
    bank = study.make_rows(config)
    assert len(bank) == 1296
    draws = defaultdict(set)
    groups = defaultdict(set)
    for row in bank:
        draws[row['component_id']].add(tuple(row['targets']['initial_values'].values()))
        groups[row['component_id']].add(row['base_id'])
    assert all(len(values) == 8 for values in draws.values())
    assert all(len(values) == 8 for values in groups.values())


@pytest.mark.parametrize('field,value', [('evaluation_role', 'final'), ('seed', True),
    ('seed', -1), ('numeric_instances', True), ('numeric_instances', 0),
    ('numeric_instances', 65), ('numeric_instances', 1.0), ('extra', 'ignored')])
def test_config_fails_before_any_artifact_write(config, field, value):
    config[field] = value
    with pytest.raises(ValueError): study.build(config)
    assert not Path(config['dataset']).exists()


@pytest.mark.parametrize('reserved', ['final.jsonl', 'heldout.jsonl', 'routing_test.jsonl'])
def test_reserved_output_paths_rejected_before_program_generation(config, reserved, monkeypatch):
    config['dataset'] = str(Path(config['dataset']).with_name(reserved))
    monkeypatch.setattr(study, 'make_rows', lambda config: pytest.fail('reserved path reached generation'))
    with pytest.raises(ValueError, match='reserved'): study.build(config)


def test_resolved_reserved_symlink_and_manifest_collision_are_rejected(config, tmp_path):
    target = tmp_path / 'heldout.jsonl'; target.write_text('sealed')
    link = tmp_path / 'routing.jsonl'; link.symlink_to(target)
    with pytest.raises(ValueError, match='reserved'): study.make_rows(config)
    link.unlink()
    config['review'] = str(Path(config['dataset']).with_suffix('.manifest.json'))
    with pytest.raises(ValueError, match='distinct'): study.make_rows(config)


@pytest.mark.parametrize('change', ['graph', 'answer', 'split', 'counterfactual', 'missing'])
def test_corrupt_target_or_grouping_is_refused(rows, change):
    config, original = rows
    bank = deepcopy(original)
    if change == 'graph': bank[0]['targets']['canonical_oracle']['dependency_edges'][0][0] = 'v3@1'
    elif change == 'answer': bank[0]['expected_answer'] += 1
    elif change == 'split': bank[0]['split'] = 'train'
    elif change == 'counterfactual': bank[0]['targets']['functional_counterfactuals'][0]['replacement'] += 1
    else: bank.pop()
    with pytest.raises(ValueError, match='fixed source/target factorial'): study.validate_rows(config, bank)


def test_build_is_immutable_logged_and_does_not_create_partial_conflicting_outputs(config, monkeypatch):
    from codecue.binding import experiment_log
    logged = []
    monkeypatch.setattr(experiment_log, 'note_artifact', lambda path: logged.append(str(path)))
    monkeypatch.setattr(study, 'code_identity', lambda: {'source_sha256': 'a' * 64})
    first = study.build(config)
    paths = [Path(config[key]) for key in ('dataset', 'review', 'report')]
    paths.append(Path(config['dataset']).with_suffix('.manifest.json'))
    before = {path: path.read_bytes() for path in paths}
    assert study.build(config) == first
    assert {path: path.read_bytes() for path in paths} == before
    assert str(Path(config['review']).resolve()) in logged
    review = json.loads(Path(config['review']).read_text())
    assert review['new_model_queries'] == 0 and not review['graph_decoding_performed']
    changed = dict(config, seed=config['seed'] + 1)
    with pytest.raises(ValueError, match='immutable'): study.build(changed)
    assert {path: path.read_bytes() for path in paths} == before
    other = dict(config, dataset=str(Path(config['dataset']).with_name('other.jsonl')))
    with pytest.raises(ValueError, match='immutable'): study.build(other)
    assert not Path(other['dataset']).exists()
