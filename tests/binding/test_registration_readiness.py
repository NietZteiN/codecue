"""Metadata linter software fixtures never stand for scientific support."""
import json
import os
from pathlib import Path

import pytest

from codecue.binding import registration_readiness as lint
from codecue.binding import registry
from codecue.binding.datasets import digest
from codecue.binding.heldout import REQUIRED

SOURCE = 'a' * 64
DATASET = 'b' * 64
REVISION = 'c' * 40


@pytest.fixture(autouse=True)
def current_source(monkeypatch):
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': SOURCE})


def write(path, data):
    path.write_text(json.dumps(data))
    return str(path)


def fixture(tmp_path):
    # These explicit strings exercise structure only, never actual hypotheses.
    registration = {key: 'software test fixture only' for key in REQUIRED}
    registration.update(status='frozen', model='fixture/model', model_revision=REVISION,
        code_source_sha256=SOURCE, dataset_sha256=DATASET,
        primary_behavioral_endpoint='incorrect_including_invalid',
        registered_utc='2026-10-26T00:00:00Z',
        frozen_fitting_procedure={'fit_manifest_sha256': 'd' * 64},
        feature_information_contract={'features': {
            'A_input': ['length'], 'B_behavior': ['length', 'confidence'],
            'C_measurements': ['length', 'confidence', 'probe'],
            'cheap_stress_test': ['stress']}, 'access': {
                'A_input': {'kind': 'input_only', 'queries_per_target': 0},
                'B_behavior': {'kind': 'behavior', 'queries_per_target': 1}}},
        additional_query_budgets=dict(A_input=0, B_behavior=1, C_measurements=2, cheap_stress_test=1))
    registration_path = tmp_path / 'registration.json'
    run = dict(registration=str(registration_path), registration_sha256=digest(registration),
               model='fixture/model', model_revision=REVISION, dataset=str(tmp_path / 'dataset.jsonl'),
               heldout_responses=str(tmp_path / 'heldout_responses.jsonl'))
    config = dict(registration=write(registration_path, registration),
                  run_config=write(tmp_path / 'run_config.json', run),
                  dataset_manifest={'sha256': DATASET, 'evaluation_role': 'reserved_final_source'},
                  supported_account=True, output_review=str(tmp_path / 'readiness.json'),
                  report=str(tmp_path / 'readiness.md'))
    return config, registration, run


def refresh(config, registration, run):
    write(Path(config['registration']), registration)
    run['registration_sha256'] = digest(registration)
    write(Path(config['run_config']), run)


def failed_checks(result):
    return {item['check'] for item in result['issues']}


def test_draft_enumerates_original_required_fields_and_writes_only_metadata(tmp_path):
    config, registration, run = fixture(tmp_path)
    registration = {key: '' for key in REQUIRED}
    registration['status'] = 'draft'
    refresh(config, registration, run)
    config['supported_account'] = False
    result = lint.build(config)
    assert result['missing_fields'] == list(REQUIRED)
    assert result['status'] == 'draft' and not result['eligibility_ready']
    assert not result['supported_account'] and result['actions_taken'] == []
    assert result['model_loads'] == result['submissions'] == 0
    assert not result['heldout_outcomes_read'] and not result['dataset_body_read']
    assert not result['heldout_authorized'] and not result['automatic_execution_enabled']
    assert json.loads(Path(config['output_review']).read_text()) == result
    assert 'No prerequisite node was executed' in Path(config['report']).read_text()


def test_complete_synthetic_metadata_passes_without_any_execution(tmp_path):
    config, _, _ = fixture(tmp_path)
    result = lint.review(config)
    assert result['status'] == 'metadata_ready' and result['eligibility_ready']
    assert not result['issues'] and not result['missing_fields']
    assert not result['heldout_authorized']
    assert not result['frozen_predictions']['content_hash_verified']
    assert not Path(config['output_review']).exists()
    assert [node['id'] for node in result['prerequisite_dag']] == [
        'registration', 'frozen_measurements_and_forecasts', 'new_heldout_responses', 'scoring']
    previous = []
    for node in result['prerequisite_dag']:
        assert not node['execute'] and node['depends_on'] == previous
        previous = [node['id']]


@pytest.mark.parametrize('support', [False, None, 1, 'true'])
def test_support_attestation_must_be_explicit_boolean_true(tmp_path, support):
    config, _, _ = fixture(tmp_path)
    config['supported_account'] = support
    result = lint.review(config)
    assert not result['eligibility_ready']
    assert 'supported_account' in failed_checks(result)


def test_fabricated_frozen_status_or_complete_draft_never_passes(tmp_path):
    config, registration, run = fixture(tmp_path)
    registration['status'] = 'draft'
    refresh(config, registration, run)
    assert not lint.review(config)['eligibility_ready']
    registration = dict(status='frozen')
    refresh(config, registration, run)
    result = lint.review(config)
    assert result['status'] == 'frozen_not_ready'
    assert result['missing_fields'] == list(REQUIRED)


@pytest.mark.parametrize('mutation,check_name', [
    ('registration_hash','registration_sha256'), ('revision','model_revision_matches'),
    ('model','model_name_matches'), ('code','code_source_sha256'),
    ('dataset','dataset_sha256'), ('dataset_role','dataset_evaluation_role'),
    ('checkpoint','checkpoint_identity'), ('tokenizer','tokenizer_revision'),
])
def test_bound_identities_and_manifest_mismatches_are_enumerated(tmp_path, mutation, check_name):
    config, registration, run = fixture(tmp_path)
    if mutation == 'registration_hash': run['registration_sha256'] = 'e' * 64
    elif mutation == 'revision': run['model_revision'] = 'e' * 40
    elif mutation == 'model': run['model'] = 'other/model'
    elif mutation == 'code': registration['code_source_sha256'] = 'e' * 64
    elif mutation == 'dataset': config['dataset_manifest']['sha256'] = 'e' * 64
    elif mutation == 'dataset_role': registration['dataset_evaluation_role'] = 'discovery'
    elif mutation == 'checkpoint': registration['checkpoint_identity'] = {'model': 'wrong', 'revision': REVISION}
    else: registration['tokenizer_revision'] = 'main'
    if mutation == 'registration_hash':
        write(Path(config['run_config']), run)
    else: refresh(config, registration, run)
    result = lint.review(config)
    assert not result['eligibility_ready'] and check_name in failed_checks(result)


@pytest.mark.parametrize('field,value,check_name', [
    ('model_revision','main','model_revision_pinned'),
    ('code_source_sha256','bad','code_source_sha256'),
    ('dataset_sha256','bad','dataset_sha256'),
    ('registered_utc','2026-10-26T00:00:00','registered_utc'),
    ('registered_utc','2026-10-26T01:00:00+01:00','registered_utc'),
    ('primary_behavioral_endpoint','correct_only','behavioral_endpoint'),
    ('hypothesis',True,'required_field_types'),
])
def test_invalid_digest_checkpoint_timestamp_and_endpoint_shapes_fail(tmp_path, field, value, check_name):
    config, registration, run = fixture(tmp_path)
    registration[field] = value
    refresh(config, registration, run)
    assert check_name in failed_checks(lint.review(config))


def test_placeholder_and_missing_fit_hash_are_not_a_finished_registration(tmp_path):
    config, registration, run = fixture(tmp_path)
    registration['hypothesis'] = '  TBD  '
    registration['frozen_fitting_procedure'] = {'procedure': 'software fixture'}
    refresh(config, registration, run)
    result = lint.review(config)
    assert 'hypothesis' in result['missing_fields']
    assert 'fit_manifest_digest' in failed_checks(result)


@pytest.mark.parametrize('mutation,check_name', [
    ('over_budget','access_cost_B_behavior'), ('input_query','input_only_access_A_input'),
    ('target','target_outcome_access'), ('access_target','access_outcomes_B_behavior'),
    ('missing_budget','query_budget_declarations'), ('negative_budget','query_budget_declarations'),
    ('infinite_budget','query_budget_declarations'), ('forbidden_feature','feature_information_contract'),
])
def test_information_access_costs_cannot_contradict_registered_contract(tmp_path, mutation, check_name):
    config, registration, run = fixture(tmp_path)
    contract = registration['feature_information_contract']
    if mutation == 'over_budget': contract['access']['B_behavior']['queries_per_target'] = 2
    elif mutation == 'input_query': contract['access']['A_input']['queries_per_target'] = 1
    elif mutation == 'target': contract['target_outcomes_allowed'] = True
    elif mutation == 'access_target': contract['access']['B_behavior']['target_outcomes'] = True
    elif mutation == 'missing_budget': del registration['additional_query_budgets']['C_measurements']
    elif mutation == 'negative_budget': registration['additional_query_budgets']['C_measurements'] = -1
    elif mutation == 'infinite_budget': registration['additional_query_budgets']['C_measurements'] = float('inf')
    else: contract['features']['C_measurements'].append('expected_answer')
    refresh(config, registration, run)
    assert check_name in failed_checks(lint.review(config))


def test_dataset_body_targets_forecasts_and_responses_are_never_opened(tmp_path, monkeypatch):
    config, registration, run = fixture(tmp_path)
    payloads = [Path(run['dataset']), Path(run['heldout_responses']),
                tmp_path / 'forecasts.jsonl', tmp_path / 'target_features.jsonl']
    for path in payloads: path.write_bytes(b'not parsed; private software fixture payload')
    run.update(frozen_predictions=str(payloads[2]), frozen_predictions_sha256='f' * 64,
               forecasting={'target_feature_table': str(payloads[3])})
    refresh(config, registration, run)
    del config['dataset_manifest']
    write(Path(run['dataset']).with_suffix('.manifest.json'),
          {'sha256': DATASET, 'evaluation_role': 'reserved_final_source'})
    original_open = Path.open
    def guarded_open(path, *args, **kwargs):
        if path.resolve() in {item.resolve() for item in payloads}: pytest.fail('payload opened: ' + str(path))
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded_open)
    result = lint.build(config)
    assert result['eligibility_ready']
    declared = result['frozen_predictions']
    assert declared['exists'] and declared['declared_hash_shape_valid']
    assert not declared['contents_read'] and not declared['content_hash_verified']
    assert len(result['metadata_reads']) == 3
    assert all(item['kind'] == 'bounded_metadata_json' for item in result['metadata_reads'])


@pytest.mark.parametrize('name', ['disguised.jsonl', 'table.csv', 'weights.pt', 'summary.json',
                                  'raw_responses.json', 'predictions.json'])
def test_disguised_bulk_or_summary_input_paths_rejected_before_open(tmp_path, monkeypatch, name):
    config, _, _ = fixture(tmp_path)
    path = tmp_path / name
    path.write_text('{}')
    config['registration'] = str(path)
    original_open = Path.open
    def guarded_open(value, *args, **kwargs):
        if value == path: pytest.fail('forbidden file opened')
        return original_open(value, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded_open)
    with pytest.raises(ValueError): lint.review(config)


def test_metadata_symlink_cannot_disguise_bulk_suffix(tmp_path):
    config, _, _ = fixture(tmp_path)
    target = tmp_path / 'bulk.jsonl'
    target.write_text('{}')
    link = tmp_path / 'innocent.json'
    link.symlink_to(target)
    config['registration'] = str(link)
    with pytest.raises(ValueError, match='bulk payload'): lint.review(config)


@pytest.mark.parametrize('payload', [{'scores': {'accuracy': 1}}, {'rows': [{'prediction': 2}]}, []])
def test_metadata_cannot_contain_raw_or_summary_payloads(tmp_path, payload):
    config, _, _ = fixture(tmp_path)
    write(Path(config['registration']), payload)
    with pytest.raises(ValueError): lint.review(config)


def test_metadata_reads_are_bounded_before_file_open(tmp_path, monkeypatch):
    config, _, _ = fixture(tmp_path)
    config['max_metadata_bytes'] = 16
    monkeypatch.setattr(Path, 'open', lambda *args, **kwargs: pytest.fail('oversized metadata opened'))
    with pytest.raises(ValueError, match='byte limit'): lint.review(config)


def test_configuration_loader_is_bounded_and_cannot_be_overwritten(tmp_path):
    config, _, _ = fixture(tmp_path)
    path = tmp_path / 'readiness_config.json'
    config['output_review'] = str(path)
    write(path, config)
    loaded = lint.load_config(path)
    with pytest.raises(ValueError, match='overwrite'): lint.build(loaded)
    path.write_bytes(b' ' * (lint.MAX_METADATA_BYTES + 1))
    with pytest.raises(ValueError, match='byte limit'): lint.load_config(path)


def test_named_pipe_cannot_bypass_metadata_file_size_bound(tmp_path):
    config, _, _ = fixture(tmp_path)
    path = tmp_path / 'pipe.json'
    os.mkfifo(path)
    config['registration'] = str(path)
    with pytest.raises(ValueError, match='regular JSON file'): lint.review(config)


@pytest.mark.parametrize('limit', [0, True, -1, lint.MAX_METADATA_BYTES + 1])
def test_metadata_limit_cannot_be_disabled(tmp_path, limit):
    config, _, _ = fixture(tmp_path)
    config['max_metadata_bytes'] = limit
    with pytest.raises(ValueError, match='max_metadata_bytes'): lint.review(config)


def test_review_never_overwrites_registration_or_declared_payload(tmp_path):
    config, _, run = fixture(tmp_path)
    original = Path(config['registration']).read_bytes()
    config['output_review'] = config['registration']
    with pytest.raises(ValueError, match='overwrite'): lint.build(config)
    assert Path(config['registration']).read_bytes() == original
    # A declared response filename may be JSON; output collisions still refuse.
    run['heldout_responses'] = str(tmp_path / 'private.json')
    write(Path(config['run_config']), run)
    config['output_review'] = run['heldout_responses']
    with pytest.raises(ValueError, match='overwrite'): lint.build(config)
    assert not Path(run['heldout_responses']).exists()
