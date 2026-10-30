import ast
import json
import random
from pathlib import Path
import pytest
from codecue.binding.interpreter import execute, parse, python_oracle, substituted_source
from codecue.binding.programs import make_program, rename, skeleton, FAMILIES
from codecue.binding.datasets import generate, validate
from codecue.binding.behavior import classify, parse_answer, select


def test_versioned_uses_liveness_and_counterfactual_propagation():
    source = 'x = 2\ny = x + 3\nx = 7\nz = y - x\nz'
    result = execute(source)
    assert result['expected_answer'] == -2
    assert result['execution_trace'][1]['uses'] == [{'name': 'x', 'definition': 'x@1'}]
    assert ['x@1', 'y@1'] in result['dependency_edges']
    assert ['x@2', 'z@1'] in result['dependency_edges']
    assert result['liveness'][1]['live_versions'] == {'y': 'y@1'}
    cf = execute(source, {'x@1': 4})
    assert cf['execution_trace'][-1]['values'] == dict(x=7, y=7, z=0)
    independent = python_oracle([source, substituted_source(source, 'x@1', 4)])
    assert [r['answer'] for r in independent] == [-2, 0]


def test_syntactic_dependency_is_not_functional_influence():
    source = 'x = 8\ny = x - x\ny'
    assert ['x@1', 'y@1'] in execute(source)['dependency_edges']
    assert execute(source, {'x@1': 42})['expected_answer'] == 0


@pytest.mark.parametrize('source', ['import os\nx = 1\nx', 'x = open("bad")\nx',
    'x = True\nx', 'x = 1\nx ** 2', 'x = 1\nx / 2', 'x = 1\nx = x * x\nx',
    'x = [1]\nx', 'x = missing\nx', 'x = 65\nx'])
def test_restricted_language_rejects_unsupported_syntax(source):
    with pytest.raises(ValueError):
        parse(source)


def test_negative_literals_do_not_create_structural_templates():
    assert skeleton('x = -3\ny = x - 4\ny') == skeleton('x = 7\ny = x - 2\ny')
    assert skeleton('x = 3\ny = x + 4\ny') != skeleton('x = 3\ny = x - 4\ny')


def test_bijection_and_oracle_fuzz():
    rng = random.Random(71)
    sources = []
    for family in FAMILIES:
        for load in (2, 4):
            for updates in (1, 3):
                for t in range(10):
                    s = make_program(family, load, updates, t, rng)
                    r = rename(s, {f'v{i}': f'word_{3-i}' for i in range(4)})
                    assert execute(s)['expected_answer'] == execute(r)['expected_answer']
                    assert max(p['count'] for p in execute(s)['liveness']) == load
                    assert sum(p['definition'].startswith('v0@') for p in execute(s)['execution_trace']) - 1 == updates
                    sources.extend([s, r])
    for i in range(0, len(sources), 128):
        batch = sources[i:i+128]
        assert [r['answer'] for r in python_oracle(batch)] == [execute(s)['expected_answer'] for s in batch]
    with pytest.raises(ValueError):
        rename(sources[0], {f'v{i}': 'same' for i in range(4)})


def test_complete_grouped_dataset_and_tamper_detection(tmp_path):
    path = tmp_path / 'data.jsonl'
    config = dict(seed=4, instances_per_cell=10, templates_per_cell=10, algorithm_version=5,
                  answer_magnitude_bins=[[0,5],[6,10],[11,15]],
                  counterfactual_pairs=True, arithmetic_controls=True)
    manifest = generate(config, path)
    assert manifest['base_instances'] == 120
    assert manifest['structural_templates'] == 120
    assert manifest['independent_template_clusters'] == 60
    assert manifest['rows'] == 2160
    assert manifest['split_rows'] == dict(train=1296, development=432, test=432)
    validation = validate(path)
    assert validation['status'] == 'passed'
    assert validation['ambiguous_alternatives'] > 0
    assert generate(config, path) == manifest
    row = json.loads(path.read_text().splitlines()[0])
    selected = select([row], dict(splits=[row['split']], control_kinds=[row['control_kind']], per_cell_limit=None,
                                 discovery_test_acknowledged=True))
    assert selected == [row]
    path.write_text(path.read_text().replace('"expected_answer":', '"expected_answer": 123, "old_answer":', 1))
    with pytest.raises(ValueError, match='hash mismatch'):
        validate(path)


def test_parsing_and_ambiguity_are_explicit():
    assert parse_answer(' -12\n') == -12
    assert parse_answer('Answer: -12') is None
    assert parse_answer('12 or 13') is None
    row = dict(expected_answer=3, diagnostic_counterfactuals=[
        dict(label='obsolete_assignment', expected_answer=5),
        dict(label='competing_variable', expected_answer=5)])
    error = classify(row, 5)
    assert error['ambiguous']
    assert len(error['compatible_labels']) == 2
    assert classify(row, None)['status'] == 'invalid'
    assert classify(row, 3)['status'] == 'correct'
