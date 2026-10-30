"""Synthetic completed parent chains; never load a model or run study fits."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from codecue.binding import candidate_prediction, confidence_prediction as one_token
from codecue.binding import discovery_prediction as generic, joint_confidence as parent
from codecue.binding import stress_prediction as stress
from codecue.binding.datasets import digest, read_jsonl
from codecue.binding.published_benchmarks import sha
from test_confidence_prediction import chain, write, jsonl
from test_candidate_prediction import completed
from test_joint_confidence import pipeline


def test_profile_retains_all_twenty_three_tiers_and_only_adds_raw_stress_to_next_token():
    old = parent.predictor_columns(); new = stress.predictor_columns()
    assert len(new) == 28 and {key: new[key] for key in old} == old
    comparisons = stress.predictor_comparisons()
    assert len(comparisons) == len(set(comparisons)) == 70
    assert comparisons[:55] == parent.predictor_comparisons()
    assert comparisons[55:60] == stress.PRIMARY_PAIRS
    assert comparisons[60:65] == stress.JOINT_PAIRS
    assert comparisons[65:] == tuple((a, s) for a, _, _, s in stress.PAIRED_TIERS)
    access = stress.predictor_access()
    assert {key: access[key] for key in old} == parent.predictor_access()
    for source, previous, joint, name in stress.PAIRED_TIERS:
        assert new[name] == old[previous]+list(stress.STRESS_COLUMNS)
        assert set(old[previous]) < set(new[name])
        assert not set(candidate_prediction.EVENT_COLUMNS)&set(new[name])
        assert access[name]['stress_queries'] == 1
        assert access[name]['stress_max_new_tokens_per_query'] == 32
        assert access[name]['next_token_prefills_per_target'] == 1
        assert access[name]['stress_correctness_feature'] is False
        assert access[name]['stress_response_identity_features'] is True
        assert access[name]['original_target_response_features'] is False
        assert access[name]['candidate_event_features'] is False
        assert access[name]['neutral_queries'] == access[previous]['neutral_queries']
        assert access[name]['source_oracle_value'] == access[previous]['source_oracle_value']
        assert access[name]['reference_correctness'] == access[previous]['reference_correctness']
    role, contract = stress.feature_contract()
    assert role == stress.ROLE and contract['stress_query'] == list(stress.STRESS_COLUMNS)
    assert {key: value for key, value in contract.items() if key != 'stress_query'} == parent.feature_contract()[1]
    assert len(set(sum(contract.values(), []))) == 68
    assert not set(sum(new.values(), []))&{'label', 'correct', 'stress_correct', 'stress_failure', 'raw_response'}


@pytest.mark.parametrize('change', [dict(seeds=[1]), dict(outer_folds=3), dict(inner_folds=3),
    dict(l2_grid=[1.]), dict(bootstrap_replicates=5), dict(bootstrap_seed=2),
    dict(feature_information_contract={}), dict(predictor_access={})])
def test_profile_rejects_protocol_or_feature_access_changes(change):
    with pytest.raises(ValueError): stress.predictor_columns(change)


@pytest.fixture
def joint_bank(pipeline, tmp_path, monkeypatch):
    config = pipeline['config']
    spec = {key: config[key] for key in ('model', 'model_revision', 'source_pipeline_config',
        'source_pipeline_config_sha256', 'source_pipeline_receipt', 'source_pipeline_receipt_sha256')}
    spec.update(output_dir=str(tmp_path/'joint_completed'), report=str(tmp_path/'joint_report.md'), protocol=parent.protocol())
    def completed_fit(effective):
        summary = dict(status='complete_exploratory', n=4, templates=4, analysis_plan=generic._plan(effective),
            generated_holdouts_opened=False, mechanism_C_fitted=False)
        summary_path = write(Path(effective['output_dir'])/'summary.json', summary)
        manifest = json.loads(Path(effective['feature_manifest']).read_text())
        write(effective['review_artifact'], dict(summary, config_hash=digest(effective), feature_manifest=manifest,
            feature_table_sha256=manifest['sha256'], feature_manifest_sha256=effective['feature_manifest_sha256'],
            artifacts={'summary': {'path': str(summary_path), 'sha256': sha(summary_path)}}))
    with monkeypatch.context() as patch:
        patch.setattr(generic, 'run', completed_fit)
        receipt = parent.fit(spec)
    path = write(tmp_path/'joint_pipeline_config.json', spec)
    effective = json.loads(Path(receipt['effective_config']['path']).read_text())
    return dict(spec=spec, config_path=str(path), receipt=receipt, effective=effective,
        manifest=json.loads(Path(effective['feature_manifest']).read_text()), parent=pipeline)


@pytest.fixture
def stress_bank(joint_bank, tmp_path, monkeypatch):
    from codecue.binding import stress_measurement as measurement
    old = joint_bank['manifest']; source = joint_bank['parent']['completed']['chain']['cases']
    run = tmp_path/'stress_measurement_run'; stage = run/'stress_measurement'
    config = dict(model=joint_bank['spec']['model'], model_revision=joint_bank['spec']['model_revision'],
        source_config_sha256=old['source_config_sha256'], max_new_tokens=32,
        run_dir=str(run), prepared_cases=str(run/'prepared.jsonl'), preflight_result=str(run/'preflight.json'))
    config_path = write(tmp_path/'stress_config.json', config)
    cases, scalars = [], []
    for index, original in enumerate(source):
        case = {key: original[key] for key in one_token.confidence.CASE_FIELDS}
        ids = list(original['input_token_ids'])+[900+index]
        case.update(evaluation_role=measurement.ROLE, original_prompt_sha256=original['prompt_sha256'],
            original_input_token_ids=list(original['input_token_ids']),
            original_input_token_ids_sha256=original['input_token_ids_sha256'],
            prompt_sha256=digest(['synthetic distinct stress prompt', original['id']]),
            input_token_ids=ids, input_token_ids_sha256=digest(ids))
        cases.append(case)
        scalars.append({**{key: case[key] for key in one_token.confidence.CASE_FIELDS},
            'measurement_role': measurement.ROLE,
            **{key: case[key] for key in ('prompt_sha256', 'input_token_ids_sha256', 'original_prompt_sha256', 'original_input_token_ids_sha256')},
            'valid': 1, 'response_chars': 2, 'output_tokens': 2,
            'prediction_value': -index, 'prediction_abs': index})
    jsonl(config['prepared_cases'], cases)
    scalar_path = jsonl(stage/'scalars.jsonl', scalars)
    response_path = jsonl(stage/'responses.jsonl', [dict(row, raw_response=str(row['prediction_value'])) for row in scalars])
    qa = dict(status='passed', evaluation_role=measurement.ROLE, source_sha256='4'*64,
        source_provenance={key: old[key] for key in one_token.SOURCE_KEYS},
        prepared_cases_sha256=sha(config['prepared_cases']), case_ids_sha256=digest([row['id'] for row in cases]))
    write(config['preflight_result'], qa)
    summary = dict(status='complete', complete=True, evaluated=4, planned=4,
        model=config['model'], model_revision=config['model_revision'], evaluation_role=measurement.ROLE,
        measurement=measurement.MEASUREMENT, source_provenance=qa['source_provenance'],
        nominal_distinct_queries_per_target=1, max_new_tokens=32,
        case_ids_sha256=qa['case_ids_sha256'], prepared_cases_sha256=qa['prepared_cases_sha256'],
        scalars_sha256=sha(scalar_path), responses_sha256=sha(response_path))
    manifest = dict(status='complete', complete=True, evaluated=4, planned=4)
    audit = dict(status='passed', complete=True, evaluated=4, identity_hash='5'*64)
    for name, value in [('manifest', manifest), ('summary', summary), ('audit', audit)]:
        write(stage/(name+'.json'), value)
    completed = dict(preparation=qa, manifest=manifest, summary=summary, audit=audit, runtime={})
    monkeypatch.setattr(measurement, 'metadata_preflight', lambda cfg: {'status': 'passed'})
    monkeypatch.setattr(measurement, 'completed_metadata', lambda cfg: deepcopy(completed))
    monkeypatch.setattr(measurement, 'audit', lambda cfg: deepcopy(audit))
    monkeypatch.setattr(measurement, 'inputs', lambda cfg, expected_source=None: (deepcopy(qa), deepcopy(cases)))
    receipt_path = str(Path(joint_bank['spec']['output_dir'])/'pipeline_review_v1.json')
    collector = dict(model=config['model'], model_revision=config['model_revision'],
        source_pipeline_config=joint_bank['config_path'], source_pipeline_config_sha256=sha(joint_bank['config_path']),
        source_pipeline_receipt=receipt_path, source_pipeline_receipt_sha256=sha(receipt_path),
        stress_config=str(config_path), stress_config_sha256=sha(config_path),
        **{f'stress_{name}_sha256': sha(stage/(name+'.json')) for name in ('manifest', 'summary', 'audit')},
        feature_table=str(tmp_path/'stress_prediction/inputs/features.jsonl'),
        feature_manifest=str(tmp_path/'stress_prediction/inputs/features.manifest.json'))
    return dict(config=collector, measurement_config=config, completed=completed, summary=summary,
        qa=qa, cases=cases, scalars=scalars, joint=joint_bank, stage=stage)


def test_join_retains_all_parent_features_labels_and_explicit_extra_response_access(stress_bank):
    result = stress.collect(stress_bank['config'])
    old = read_jsonl(stress_bank['joint']['effective']['feature_table'])
    new = read_jsonl(stress_bank['config']['feature_table'])
    assert result['n'] == result['groups'] == 4
    assert result['old_twenty_three_feature_sets_and_labels_unchanged'] is True
    assert result['all_parent_feature_bytes_unchanged'] is False
    assert result['original_target_response_features'] is False
    assert result['original_target_correctness_features'] is False
    assert result['stress_response_identity_features'] is True and result['stress_correctness_features'] is False
    assert result['original_target_raw_response_payload_reads'] == 0
    assert result['stress_response_payload_read_by_audit'] is True
    assert result['new_queries_during_feature_collection'] == 0 and result['additional_stress_queries_in_bank'] == 4
    assert 'raw_response_payload_reads' not in result and 'new_language_model_queries' not in result
    assert result['scientific_access_cost']['new_stress_tiers']['candidate_event_features'] is False
    for before, after in zip(old, new):
        assert {key: after[key] for key in before if key != 'features'} == {key: before[key] for key in before if key != 'features'}
        assert {key: after['features'][key] for key in before['features']} == before['features']
        assert set(after['features'])-set(before['features']) == set(stress.STRESS_COLUMNS)
    assert stress.collect(stress_bank['config']) == result


@pytest.mark.parametrize('change', ['stress_config_pin', 'stress_summary_pin', 'joint_receipt_pin',
    'reserved_role', 'reserved_output', 'checkpoint', 'smoke', 'query_budget', 'source_identity',
    'source_provenance', 'case_ids', 'query_count', 'alias', 'stress_scalar_alias'])
def test_metadata_rejections_precede_any_parent_feature_or_stress_payload_access(stress_bank, monkeypatch, change):
    from codecue.binding import stress_measurement as measurement
    cfg = stress_bank['config']
    if change == 'stress_config_pin': cfg['stress_config_sha256'] = '0'*64
    elif change == 'stress_summary_pin': cfg['stress_summary_sha256'] = '0'*64
    elif change == 'joint_receipt_pin': cfg['source_pipeline_receipt_sha256'] = '0'*64
    elif change == 'reserved_role': cfg['evaluation_role'] = 'final_evaluation'
    elif change == 'reserved_output': cfg['feature_table'] = '/tmp/final/features.jsonl'
    elif change == 'checkpoint': cfg['model'] = 'wrong/checkpoint'
    elif change in ('smoke', 'query_budget', 'source_identity'):
        sc = stress_bank['measurement_config']
        if change == 'smoke': sc['case_limit'] = 1
        elif change == 'query_budget': sc['max_new_tokens'] = 33
        else: sc['source_config_sha256'] = '0'*64
        write(cfg['stress_config'], sc); cfg['stress_config_sha256'] = sha(cfg['stress_config'])
    elif change in ('source_provenance', 'case_ids', 'query_count'):
        if change == 'source_provenance':
            stress_bank['qa']['source_provenance']['source_identity_hash'] = '0'*64
        elif change == 'case_ids': stress_bank['summary']['case_ids_sha256'] = '0'*64
        else: stress_bank['summary']['nominal_distinct_queries_per_target'] = 2
        write(stress_bank['stage']/'summary.json', stress_bank['summary'])
        cfg['stress_summary_sha256'] = sha(stress_bank['stage']/'summary.json')
    elif change == 'alias': cfg['feature_table'] = stress_bank['joint']['effective']['feature_table']
    else: cfg['feature_table'] = str(stress_bank['stage']/'scalars.jsonl')
    def forbidden(*args, **kwargs): raise AssertionError('bulk payload accessed before metadata rejection')
    monkeypatch.setattr(generic, 'load_features', forbidden)
    monkeypatch.setattr(measurement, 'inputs', forbidden)
    monkeypatch.setattr(measurement, 'audit', forbidden)
    with pytest.raises(ValueError): stress.collect(cfg)
    assert not Path(cfg['feature_manifest']).exists()


@pytest.mark.parametrize('change', ['ids', 'label_feature', 'stress_correctness', 'old_answer_hash',
    'original_ids', 'prompt_length', 'same_query', 'invalid_value', 'bad_abs', 'budget', 'boolean_value'])
def test_join_rejects_identity_leakage_and_invalid_raw_stress_contracts(stress_bank, change):
    rows = read_jsonl(stress_bank['joint']['effective']['feature_table'])
    cases, scalars = deepcopy(stress_bank['cases']), deepcopy(stress_bank['scalars'])
    if change == 'ids': scalars[0]['id'] = scalars[1]['id']
    elif change == 'label_feature': rows[0]['features']['target_correct'] = 1
    elif change == 'stress_correctness': scalars[0]['correct'] = True
    elif change == 'old_answer_hash': scalars[0]['original_prompt_sha256'] = '0'*64
    elif change == 'original_ids': cases[0]['original_input_token_ids'][0] += 1
    elif change == 'prompt_length': rows[0]['features']['prompt_tokens'] += 1
    elif change == 'same_query':
        for key in ('input_token_ids', 'input_token_ids_sha256', 'prompt_sha256'):
            cases[0][key] = deepcopy(cases[0]['original_'+key])
        for key in ('input_token_ids_sha256', 'prompt_sha256'): scalars[0][key] = cases[0][key]
    elif change == 'invalid_value': scalars[1]['valid'] = 0
    elif change == 'bad_abs': scalars[1]['prediction_abs'] += 1
    elif change == 'budget': scalars[0]['output_tokens'] = 33
    else: scalars[0]['prediction_value'] = False
    with pytest.raises(ValueError): stress.augment_rows(rows, cases, scalars)


def test_scalar_payload_corruption_and_repeat_audit_failure_are_visible(stress_bank, monkeypatch):
    from codecue.binding import stress_measurement as measurement
    monkeypatch.setattr(measurement, 'audit', lambda cfg: {'status': 'failed'})
    with pytest.raises(ValueError, match='repeated audit'): stress.collect(stress_bank['config'])
    monkeypatch.setattr(measurement, 'audit', lambda cfg: deepcopy(stress_bank['completed']['audit']))
    Path(stress_bank['stage']/'scalars.jsonl').write_text('{}\n')
    with pytest.raises(ValueError, match='checksum'): stress.collect(stress_bank['config'])


def test_staged_fit_freezes_completed_metadata_and_fixed_fitting_contract(stress_bank, tmp_path, monkeypatch):
    cfg = stress_bank['config']
    spec = {key: cfg[key] for key in ('model', 'model_revision', 'source_pipeline_config',
        'source_pipeline_config_sha256', 'source_pipeline_receipt', 'source_pipeline_receipt_sha256',
        'stress_config', 'stress_config_sha256')}
    spec.update(output_dir=str(tmp_path/'stress_pipeline'), report=str(tmp_path/'stress_report.md'), protocol=stress.protocol())
    seen = []
    def run(effective):
        seen.append(deepcopy(effective)); write(effective['review_artifact'], {'status':'complete_exploratory'})
    monkeypatch.setattr(generic, 'run', run)
    result = stress.fit(spec)
    effective = seen[0]
    assert effective['feature_profile'] == stress.PROFILE
    assert effective['feature_information_contract'] == stress.predictor_columns()
    assert effective['predictor_access'] == stress.predictor_access()
    assert effective['seeds'] == [17, 29, 43] and effective['l2_grid'] == [.1, 1., 10., 100.]
    assert result['effective_config']['sha256'] == sha(result['effective_config']['path'])
    assert result['review']['sha256'] == sha(result['review']['path'])
    collector = json.loads(Path(result['collection_config']['path']).read_text())
    assert collector['stress_audit_sha256'] == sha(stress_bank['stage']/'audit.json')
    assert result['model_loading'] is False
