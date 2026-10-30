from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from codecue.binding import relationship_schedule_programs as study
from codecue.binding import relationships
from codecue.binding.interpreter import execute


@pytest.fixture
def config(tmp_path):
    return dict(evaluation_role=study.ROLE, numeric_seeds=[202610281, 202610283, 202610287],
        dataset=str(tmp_path/'schedules.jsonl'), review=str(tmp_path/'review.json'), report=str(tmp_path/'schedules.md'))


@pytest.fixture(scope='module')
def bank(tmp_path_factory):
    folder = tmp_path_factory.mktemp('schedule-bank')
    config = dict(evaluation_role=study.ROLE, numeric_seeds=[202610281, 202610283, 202610287],
        dataset=str(folder/'schedules.jsonl'), review=str(folder/'review.json'), report=str(folder/'schedules.md'))
    rows = study.make_rows(config)
    return config, rows


@pytest.fixture(scope='module')
def checked(bank):
    config, rows = bank
    return study.validate_rows(config, rows, independent=True)


def test_complete_source_factorial_and_effective_units(bank, checked):
    _, rows = bank
    assert len(rows) == len({row['id'] for row in rows}) == 2016
    assert checked['raw_schedule_count'] == 28
    assert checked['raw_schedule_parent_templates'] == 84
    assert checked['effective_ordered_schedule_units'] == 21
    assert checked['effective_canonical_graph_units'] == 15
    assert checked['split_canonical_graph_units'] == {'train': 10, 'development': 5}
    assert sum(checked['split_rows'].values()) == 2016
    assert checked['maximum_assignment_version'] == 4
    assert checked['obsolete_copy_definitions_across_templates'] > 0
    assert checked['independent_python_passed'] is True
    assert checked['independent_python_programs'] == 3024
    assert checked['prefix_label_checks'] == 2016*8
    assert all(value == 0 for value in checked['cross_split_overlap'].values())
    assert sum(checked['raw_templates_per_canonical_graph'].values()) == 84


def test_all_queries_and_three_numeric_seeds_remain_in_one_graph_split(bank):
    config, rows = bank
    groups = defaultdict(list)
    for row in rows: groups[row['component_id']].append(row)
    for group in groups.values():
        assert len({row['split'] for row in group}) == 1
        assert {row['query_slot'] for row in group} == set(range(4))
        assert {row['numeric_seed'] for row in group} == set(config['numeric_seeds'])
        assert {row['lexical_realization'] for row in group} == {0, 1}
    assert {tuple(row['destination_schedule']) for row in rows if row['schedule_kind']=='permutation'} == set(study.SLOT_PERMUTATIONS)
    assert {tuple(row['destination_schedule']) for row in rows if row['schedule_kind']=='repeated'} == set(study.REPEATED_SCHEDULES)


def test_actual_current_version_parent_and_obsolete_copies(bank):
    _, rows = bank
    row = next(row for row in rows if row['destination_schedule']==[0, 0, 1, 0]
        and row['parent_pattern']=='ring_successor')
    labels = row['targets']['prefix_relationships'][5]
    assert labels['uses'][-1]['referent'] == 'v1@1'
    assert labels['uses'][-1]['consumer'] == 'v0@3'
    nodes = {node['id']: node for node in labels['version_nodes']}
    assert nodes['v0@2']['status'] == 'obsolete'
    assert nodes['v0@3']['status'] == 'current'
    final = row['targets']['prefix_relationships'][7]
    assert [point['definition'] for point in row['targets']['canonical_execution_trace']][-1] == 'v0@4'
    assert any(node['id']=='v0@3' and node['status']=='obsolete' for node in final['version_nodes'])
    assert ['v2@1', 'v0@4'] in final['strict_ancestor_edges']
    assert ['v2@1', 'v0@4'] not in final['direct_def_use_edges']


def test_future_queries_and_assignments_are_absent_from_prefix_labels(bank):
    _, rows = bank
    relatives = [row for row in rows if row['raw_template_id']==rows[0]['raw_template_id']
        and row['numeric_seed']==rows[0]['numeric_seed'] and row['lexical_realization']==0]
    assert len(relatives) == 4
    assert all(row['targets']['prefix_relationships']==relatives[0]['targets']['prefix_relationships'] for row in relatives)
    for checkpoint, labels in enumerate(relatives[0]['targets']['prefix_relationships']):
        assert 'output' not in labels and labels['output_visible'] is False
        assert all(node['statement'] <= checkpoint for node in labels['version_nodes'])
    assert len({tuple(row['targets']['final_query_relationships']['output']['direct_referents']) for row in relatives}) == 4


def test_slot_permuted_graphs_have_one_canonical_component(bank):
    _, rows = bank
    row = rows[0]; labels = row['targets']['prefix_relationships'][-1]
    expected, _ = study._canonical_graph(labels)
    for permutation in study.SLOT_PERMUTATIONS:
        renamed = deepcopy(labels)
        for node in renamed['version_nodes']:
            node['id'] = study._node(node['id'], permutation)
        for key in ('direct_def_use_edges', 'strict_ancestor_edges', 'succession_edges'):
            renamed[key] = [[study._node(a, permutation), study._node(b, permutation)] for a, b in renamed[key]]
        assert study._canonical_graph(renamed)[0] == expected


@pytest.mark.parametrize('field,value', [
    ('evaluation_role', 'final'), ('numeric_seeds', []), ('numeric_seeds', [1, 1, 2]),
    ('numeric_seeds', [True, 2, 3]), ('numeric_seeds', [1, 2, {}]),
    ('numeric_seeds', [-1, 2, 3]), ('numeric_seeds', [1, 2, 2**63]), ('extra', 'ignored')])
def test_bad_config_rejected_before_generation(config, field, value, monkeypatch):
    config[field] = value
    monkeypatch.setattr(study, '_templates', lambda: pytest.fail('generation must not begin'))
    with pytest.raises(ValueError): study.make_rows(config)
    assert not Path(config['dataset']).exists()


@pytest.mark.parametrize('value', ['final.jsonl', 'heldout.jsonl', 'schedule_test.jsonl'])
def test_reserved_paths_rejected(config, value):
    config['dataset'] = str(Path(config['dataset']).with_name(value))
    with pytest.raises(ValueError): study.make_rows(config)


def test_output_ancestor_collision_and_symlinks_rejected(config):
    config['review'] = str(Path(config['dataset'])/'review.json')
    with pytest.raises(ValueError): study.make_rows(config)


@pytest.mark.parametrize('field', ['source', 'expected_answer', 'component_id', 'targets'])
def test_mutated_source_targets_or_grouping_rejected(bank, field):
    config, rows = bank
    damaged = list(rows); damaged[0] = deepcopy(rows[0])
    if field == 'targets': damaged[0][field]['prefix_relationships'][5]['direct_def_use_edges'] = []
    elif field == 'expected_answer': damaged[0][field] += 1
    else: damaged[0][field] = 'changed'
    with pytest.raises(ValueError, match='complete exact'): study.validate_rows(config, damaged)


def test_old_source_overlap_is_pinned_and_metadata_only(config, bank, tmp_path):
    _, rows = bank
    prior = tmp_path/'prior.jsonl'
    old = {key: rows[0][key] for key in ('source', 'canonical_source', 'split')}
    old['evaluation_role'] = 'discovery_relationship_routing_v1'
    prior.write_text(json.dumps(old)+'\n')
    config['overlap_sources'] = [dict(path=str(prior), sha256=hashlib.sha256(prior.read_bytes()).hexdigest())]
    study._config(config)
    review = study._overlap(config, rows)
    assert review[0]['exact_surface_sources'] == review[0]['canonical_ast_sources'] == 1
    assert review[0]['metadata_only'] is True
    config['overlap_sources'][0]['sha256'] = '0'*64
    with pytest.raises(ValueError, match='checksum'): study._overlap(config, rows)


def test_old_source_roles_cannot_open_sealed_outcomes(config, bank, tmp_path):
    _, rows = bank
    prior = tmp_path/'prior.jsonl'
    old = {key: rows[0][key] for key in ('source', 'canonical_source')}
    old.update(split='final', evaluation_role='final')
    prior.write_text(json.dumps(old)+'\n')
    config['overlap_sources'] = [dict(path=str(prior), sha256=hashlib.sha256(prior.read_bytes()).hexdigest())]
    with pytest.raises(ValueError, match='only bounded old discovery'): study._overlap(config, rows)


def test_independent_python_disagreement_fails(monkeypatch):
    source = 'x = 2\nx'
    monkeypatch.setattr(study, 'python_oracle', lambda sources: [dict(answer=3, trace=[{'x': 2}])])
    with pytest.raises(ValueError, match='independent Python'): study._python_validate({source})


def test_build_immutable_qualification_and_partial_completion(config, bank, checked, monkeypatch):
    _, rows = bank
    monkeypatch.setattr(study, 'make_rows', lambda config: rows)
    monkeypatch.setattr(study, 'validate_rows', lambda config, rows, independent=False: deepcopy(checked))
    monkeypatch.setattr(study, 'code_identity', lambda: {'source_sha256': 'a'*64})
    from codecue.binding import experiment_log
    monkeypatch.setattr(experiment_log, 'note_artifact', lambda path: None)
    first = study.build(config)
    paths = study._config(config)
    pins = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    assert first['model_queries'] == 0 and first['targets_prepared_only'] is True
    manifest = json.loads(paths['manifest'].read_text())
    assert manifest['learned_readout_compatible'] is False
    assert manifest['effective_canonical_graph_units'] == 15
    paths['review'].unlink()
    assert study.build(config) == first
    assert pins == {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    assert study.build(config) == first


def test_existing_different_publication_prevents_any_new_write(config, bank, checked, monkeypatch):
    _, rows = bank
    monkeypatch.setattr(study, 'make_rows', lambda config: rows)
    monkeypatch.setattr(study, 'validate_rows', lambda config, rows, independent=False: deepcopy(checked))
    monkeypatch.setattr(study, 'code_identity', lambda: {'source_sha256': 'a'*64})
    Path(config['report']).write_text('existing different report')
    with pytest.raises(ValueError, match='immutable schedule artifact'): study.build(config)
    assert not Path(config['dataset']).exists()
    assert not Path(config['review']).exists()
