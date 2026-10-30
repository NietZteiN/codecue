"""Semantic, leakage, control and engine-isolation regressions for discovery."""
from copy import deepcopy
import json

import numpy as np
import pytest

from codecue.binding import arithmetic_graph_programs as p
from codecue.binding import arithmetic_graph_capture as c
from codecue.binding import arithmetic_graph_readouts as r
from codecue.binding import arithmetic_graph_behavior as b
from codecue.binding import arithmetic_graph_suite as s
from codecue.binding import overnight_relationship_capture as original_capture
from codecue.binding import overnight_relationship_behavior as original_behavior
from codecue.binding import overnight_relationship_suite as original_suite


EXAMPLE = '\n'.join(('v0 = 2', 'v1 = 7', 'v2 = 3', 'v3 = 1',
                     'v2 = v0 + v3', 'v0 = v1 - v0', 'v3 = v0 + v2', 'v1 = v3 - v2', 'v1'))


def test_read_before_write_and_version_identity():
    truth = p.oracle(EXAMPLE)
    assert truth['writes'][5]['parents'] == [1, 0]
    assert truth['writes'][7]['parents'] == [6, 4]
    assert truth['values'] == [5, 5, 3, 8]
    assert truth['versions'] == [2, 2, 2, 2]


def test_prefix_oracle_never_reads_future():
    changed = EXAMPLE.replace('v0 = v1 - v0', 'v0 = v1 + v0')
    assert p.oracle(EXAMPLE, 3) == p.oracle(changed, 3)
    assert p.oracle(EXAMPLE) != p.oracle(changed)


def test_exact_dataset_and_independent_python():
    review = p.validate(p.make_rows())
    assert review['rows'] == 4608
    assert review['components'] == {'train': 36, 'development': 12}
    assert review['split_rows'] == {'train': 3456, 'development': 1152}
    assert review['independent_python_passed']
    assert review['unique_numeric_bodies'] == 576


@pytest.mark.parametrize('field,value', [('split', 'development'), ('expected_answer', 999), ('source', 'v0 = 999')])
def test_tampered_sources_rejected(field, value):
    rows = deepcopy(p.make_rows())
    rows[0][field] = value
    with pytest.raises(ValueError, match='deterministic'):
        p.validate(rows, independent=False)


def test_alpha_canonicalization():
    graph = [(0, 0, 1, '+'), (2, 0, 3, '-'), (3, 2, 1, '+'), (1, 3, 2, '-')]
    permutation = (2, 0, 3, 1)
    renamed = [(permutation[d], permutation[a], permutation[b], op) for d, a, b, op in graph]
    assert p.canonical_key(graph) == p.canonical_key(renamed)
    different = graph.copy()
    different[0] = (0, 0, 1, '-')
    assert p.canonical_key(graph) != p.canonical_key(different)


def test_no_alpha_family_leakage():
    groups = {}
    for row in p.make_rows():
        groups.setdefault(row['component_id'], set()).add(row['split'])
    assert len(groups) == 48
    assert all(len(v) == 1 for v in groups.values())


def test_numeric_bounds_and_two_parents():
    for row in p.make_rows()[::8]:
        assert max(map(abs, row['oracle']['values'])) <= 96
        for write in row['oracle']['writes'][4:]:
            assert len(write['parents']) == 2
            assert all(parent < write['statement'] for parent in write['parents'])


def test_target_prefix_and_categorical_semantics():
    rows = [dict(canonical_source=EXAMPLE)]
    y, binary, values, heads, differences = r.targets(rows, 0)
    assert values.tolist() == [[2, 7, 3, 1]]
    assert not any(h['kind'] == 'parent' for h in heads)
    y, binary, values, heads, differences = r.targets(rows, 1)
    assert r._decode(y, heads, 'parent').tolist() == [[0, 3, 1, 0, 5, 4, 6, 4]]
    assert (r._decode(y, heads, 'value')-96).tolist() == values.tolist()


def test_perfect_predictions_score_perfectly():
    rows = p.make_rows()[:96]
    y, binary, values, heads, differences = r.targets(rows, 1)
    metrics = r.summarize(y, y, binary, values, heads, differences,
                          np.ones(len(r.RELATIONS), bool), np.ones(len(rows), bool))
    assert metrics['whole_parent_accuracy'] == 1.
    assert metrics['whole_unordered_parent_graph_accuracy'] == 1.
    assert metrics['valid_past_parent_graph_fraction'] == 1.
    assert metrics['whole_state_accuracy'] == 1.
    assert metrics['relations']['macro_balanced_accuracy'] == 1.
    assert metrics['value_derived_relation_macro_balanced_accuracy'] == 1.
    assert metrics['signed_difference_mae'] == 0.


def test_invalid_future_parents_detected():
    rows = [dict(canonical_source=EXAMPLE)]
    y, binary, values, heads, differences = r.targets(rows, 1)
    scores = y.copy()
    parent = next(h for h in heads if h['kind'] == 'parent')
    scores[:, parent['start']:parent['stop']] = 0
    scores[:, parent['stop']-1] = 1
    metrics = r.summarize(scores, y, binary, values, heads, differences,
                          np.ones(len(r.RELATIONS), bool), np.ones(1, bool))
    assert metrics['whole_parent_accuracy'] == 0.
    assert metrics['valid_past_parent_graph_fraction'] == 0.


def test_shuffle_is_split_preserving_whole_family_derangement():
    rows = p.make_rows()
    donor = r.donor_indices(rows)
    mapping = {}
    for index, source in enumerate(donor):
        a, d = rows[index], rows[source]
        assert a['split'] == d['split']
        assert a['component_id'] != d['component_id']
        assert all(a[k] == d[k] for k in ('numeric_seed', 'numeric_draw', 'lexical_realization', 'query_slot'))
        mapping.setdefault(a['component_id'], set()).add(d['component_id'])
    assert all(len(v) == 1 for v in mapping.values())


def test_rare_relation_cannot_earn_primary_credit():
    rows = p.make_rows()[:96]
    y, binary, values, heads, differences = r.targets(rows, 1)
    metrics = r.summarize(y, y, binary, values, heads, differences,
                          np.zeros(len(r.RELATIONS), bool), np.ones(len(rows), bool))
    assert metrics['relations']['macro_balanced_accuracy'] is None
    assert metrics['relations']['supported_cells'] == 0


def test_private_engines_leave_original_protocols_unchanged():
    assert c._CORE is not original_capture
    assert original_capture.ROLE != c.ROLE
    assert original_behavior.ROLE != b.ROLE
    assert original_suite.ROLE != s.ROLE
    assert original_suite._submit_controller != s._submit_controller
    assert original_behavior.LIMITATION != b._CORE.LIMITATION
    assert original_capture._validate_row != c._validate_row


def test_capture_record_excludes_oracle_targets():
    record = c._CORE._record(p.make_rows()[0])
    assert 'oracle' not in record
    assert 'expected_answer' not in record
    assert 'operation_family' in record


def test_behavior_parser_preserves_strict_contract():
    assert b._CORE.parse_integer(' -12\n') == -12
    assert b._CORE.parse_integer('v0 = -12') is None
    assert b._CORE.parse_integer('```\n-12\n```') is None


def test_behavior_family_interval_and_invalids():
    rows = [dict(split='development', component_id=str(g), correct=bool(i), query_slot=0,
                 parsed=7 if i else None) for g in range(12) for i in range(2)]
    metrics = b.summarize(rows)
    assert metrics['cells']['overall']['accuracy'] == .5
    assert metrics['cells']['overall']['invalid_fraction'] == .5
    assert metrics['computed_literal']['families'] == 12
    assert metrics['computed_literal']['conditional_family_bootstrap_95'] == [.5, .5]


def test_saved_ridge_parameter_replay(tmp_path):
    from codecue.binding.weighted_ridge import fit, from_parameters
    rng = np.random.default_rng(1)
    x, y = rng.normal(size=(12, 5)), rng.normal(size=(12, 3))
    model = fit(x, y, np.ones(12), train_ids=list(map(str, range(12))), split='train', alpha=100.)
    path = tmp_path/'parameters.npz'
    r._npz(path, **model.parameters)
    with np.load(path, allow_pickle=False) as data:
        restored = from_parameters(model.metadata, {k: data[k] for k in model.parameters})
    assert np.array_equal(model.predict(x), restored.predict(x))


def test_complete_readout_grid_resume_and_payload_tamper(tmp_path, monkeypatch):
    from pathlib import Path
    from codecue.binding import relationship_capture as base
    from codecue.binding.datasets import digest
    # A small end-to-end collector fixture exercises actual fits, categorical
    # decoding, saved-model replay, receipt publication, resume and deep audit.
    selected = []
    for split in ('train', 'development'):
        names = sorted({x['component_id'] for x in p.make_rows() if x['split'] == split})[:2]
        selected.extend(x for x in p.make_rows() if x['component_id'] in names and
                        x['numeric_seed'] == p.SEEDS[0] and x['numeric_draw'] == 0)
    capdir = tmp_path/'capture'
    capdir.mkdir()
    cap = dict(run_dir=str(capdir), layers=[24], hidden_size=4, model='fixture')
    capfile = tmp_path/'capture.json'
    capfile.write_text(json.dumps(cap))
    config = dict(evaluation_role=r.ROLE, alpha=100., seeds=list(r.SEEDS),
                  capture_config=str(capfile), capture_config_sha256=base._sha(capfile),
                  run_dir=str(tmp_path/'readouts'), report=str(tmp_path/'report.md'), primary_layer=24)
    source = dict(snapshot_id='fixture')
    cases = [dict(record=x, visible_prefixes=[x['source']]*3) for x in selected]
    (capdir/'summary.json').write_text(json.dumps(dict(chunks=[dict(first=0, rows=len(selected))])))
    monkeypatch.setattr(base, '_slurm', lambda: None)
    monkeypatch.setattr(base, '_safe', Path)
    monkeypatch.setattr(base, '_current_source', lambda config: source)
    monkeypatch.setattr(base, '_verify_source', lambda config, source: None)
    monkeypatch.setattr(c, 'audit', lambda config: None)
    monkeypatch.setattr(c, 'inputs', lambda config: (dict(source=source), cases))
    monkeypatch.setattr(c._CORE, '_dataset', lambda config: (selected, {}))
    features = np.random.default_rng(1).normal(size=(len(selected), 3, 1, 4)).astype(np.float32)
    monkeypatch.setattr(c, 'load_chunk', lambda *args: (features, {}))
    result = r.run(config)
    assert result['factorizations'] == 18
    assert result['cases'] == 32
    assert r.audit(config)['status'] == 'complete_exploratory'
    assert r.run(config)['status'] == 'complete_exploratory'
    bank = Path(result['fits'][0]['artifacts']['parameters']['path'])
    bank.write_bytes(bank.read_bytes()+b'corruption')
    with pytest.raises(ValueError, match='payload changed'):
        r.audit(config)
