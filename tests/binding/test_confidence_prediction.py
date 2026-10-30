"""Synthetic completed discovery chains; no real outcomes, models or fits."""
from copy import deepcopy
import json
import math
from pathlib import Path

import pytest

from codecue.binding import confidence
from codecue.binding import confidence_prediction as joined
from codecue.binding import discovery_controls as controls
from codecue.binding import discovery_prediction as prediction
from codecue.binding.competition import ROLE as SOURCE_ROLE
from codecue.binding.datasets import digest, read_jsonl
from codecue.binding.published_benchmarks import sha


def write(path, value):
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')
    return path


def jsonl(path, values):
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(value, sort_keys=True)+'\n' for value in values))
    return path


@pytest.fixture
def chain(tmp_path, monkeypatch):
    from codecue.binding import experiment_log, registry
    monkeypatch.setattr(experiment_log, 'note_artifact', lambda *args, **kwargs: None)
    monkeypatch.setattr(registry, 'code_identity', lambda: {'source_sha256': 'synthetic-current-code'})
    model, revision, original_code, measurement_code = 'synthetic/model', 'a'*40, 'b'*64, 'c'*64
    source_dir = tmp_path/'original';source_path = source_dir/'config.json'
    source = dict(model=model, model_revision=revision, tokenizer_revision=revision, dtype='float32',
        protocol='short_answer_chat_v1', tokenization_mode='native', eos_token_ids=[15], device='cpu',
        dataset=str(source_dir/'source.jsonl'), prepared_cases=str(source_dir/'saved_prompt_inputs.jsonl'),
        preflight_result=str(source_dir/'preparation.json'), run_dir=str(source_dir))
    write(source_path, source)
    dm = dict(status='validated', evaluation_role=SOURCE_ROLE, sha256='d'*64, rows=4)
    write(Path(source['dataset']).with_suffix('.manifest.json'), dm)
    source_qa = dict(status='passed', config_hash=digest(source), source_sha256=original_code,
        prepared_cases_sha256='e'*64, cases=4, generated_holdouts_opened=False, model_inference=False)
    write(source['preflight_result'], source_qa)
    origin_identity = dict(config=source, dataset_manifest=dm, code={'source_sha256': original_code},
        model_revision=revision, tokenizer_revision=revision)
    origin = dict(status='complete', identity=origin_identity, identity_hash=digest(origin_identity),
                  responses_sha256='f'*64)
    write(source_dir/'checkpoint_suite/manifest.json', origin)
    origin_audit = dict(status='passed', complete=True, identity_hash=origin['identity_hash'],
        preflight=source_qa, model=model, revision=revision, evaluated=4)
    original_audit_path = write(source_dir/'checkpoint_suite/audit.json', origin_audit)
    provenance = dict(source_config_sha256=sha(source_path), source_dataset_sha256=dm['sha256'],
        source_identity_hash=origin['identity_hash'], source_model=model, source_model_revision=revision,
        source_prepared_sha256=source_qa['prepared_cases_sha256'], source_audit_sha256=sha(original_audit_path),
        original_source_sha256=original_code, source_responses_sha256=origin['responses_sha256'])
    cases = [];rows = [];scalars = []
    _, base_contract = prediction._feature_contract({'feature_profile': controls.PROFILE})
    for index in range(4):
        level = 2 if index < 2 else 4
        case = dict(id=f'case:{index}', base_id=f'base:{index}', template_id=f'template:{index}',
            split='train' if index < 2 else 'development', condition='misleading' if index%2 else 'informative',
            lexical_realization=index%2, available_bindings=level, updates=1,
            tail_placement='after' if index%2 else 'before', query_role='saved' if index%2 else 'current',
            prompt=f'exact synthetic prompt {index}:', input_token_ids=[1, 2, index+3], evaluation_role=confidence.ROLE)
        case.update(prompt_sha256=digest(case['prompt']), input_token_ids_sha256=digest(case['input_token_ids']))
        cases.append(case)
        values = {key: 0 for key in sum(base_contract.values(), [])}
        values.update(prompt_tokens=3, available_bindings=level, updates=1,
            tail_after=index%2, query_saved=index%2, misleading=index%2, lexical_one=index%2,
            neutral_valid=1, neutral_prediction_value=1, neutral_prediction_abs=1,
            oracle_answer_value=1, oracle_answer_abs=1)
        values.update(controls.interaction_features(values))
        rows.append({**{key: case[key] for key in joined.ROW_METADATA if key not in ('reference_id', 'original_split')},
            'reference_id': f'reference:{index//2}', 'original_split': case['split'],
            'label': index%2, 'target_invalid': False, 'features': values})
        scalars.append({**{key: case[key] for key in confidence.CASE_FIELDS},
            'measurement_role': confidence.ROLE, 'prompt_sha256': case['prompt_sha256'],
            'input_token_ids_sha256': case['input_token_ids_sha256'],
            'entropy_nats': math.log(16), 'maximum_next_token_probability': 1/16,
            'top_two_logit_margin': 0., 'eos_probability_mass': 1/16, 'vocabulary_size': 16})
    controls_dir = tmp_path/'controls'
    control_table = jsonl(controls_dir/'features.jsonl', rows)
    feature_manifest = dict(status='passed', evaluation_role=controls.ROLE, profile=controls.PROFILE,
        columns=base_contract, predictor_columns=controls.predictor_columns(), n=4, groups=4,
        feature_table=str(control_table), sha256=sha(control_table), **provenance,
        generated_holdouts_opened=False, mechanism_C_fitted=False,
        target_outcomes_used_as_features=False, target_metadata_labels_references_unchanged=True)
    fm_path = write(controls_dir/'features.manifest.json', feature_manifest)
    parent = dict(model=model, model_revision=revision, feature_profile=controls.PROFILE,
        feature_table=str(control_table), feature_table_sha256=sha(control_table),
        feature_manifest=str(fm_path), feature_manifest_sha256=sha(fm_path),
        feature_information_contract=controls.predictor_columns())
    parent_path = write(controls_dir/'config.json', parent)
    measurement_dir = tmp_path/'measurement';stage = measurement_dir/'confidence'
    cc = {key: source[key] for key in confidence.IDENTITY_FIELDS}
    cc.update(dataset=source['dataset'], source_config=str(source_path), source_config_sha256=sha(source_path),
        prepared_cases=str(measurement_dir/'prepared.jsonl'), preflight_result=str(measurement_dir/'preparation.json'),
        run_dir=str(measurement_dir), device='cpu', batch_size=2, attention_backend='sdpa',
        execution_backend='synthetic Transformers prefill')
    cc_path = write(measurement_dir/'config.json', cc)
    jsonl(cc['prepared_cases'], cases)
    qa = dict(status='passed', evaluation_role=confidence.ROLE, measurement=confidence.MEASUREMENT,
        cases=4, config_hash=digest(cc), source_sha256=measurement_code, source_config_sha256=sha(source_path),
        prepared_cases_sha256=sha(cc['prepared_cases']), case_ids_sha256=digest([case['id'] for case in cases]),
        padded_width=3, model=model, model_revision=revision, tokenizer_revision=revision, eos_token_ids=[15],
        upstream_identity=origin['identity_hash'], smoke_subset=False, source_provenance=provenance,
        generated_holdouts_opened=False, target_outcomes_read=False, generated_tokens=0, oracle_fields_exported=False)
    write(cc['preflight_result'], qa)
    confidence_path = jsonl(stage/'confidence.jsonl', scalars)
    identity = dict(config=cc, config_hash=digest(cc), dataset_manifest=dm, stage='confidence',
        code={'source_sha256': measurement_code}, model_revision=revision, tokenizer_revision=revision)
    manifest = dict(status='complete', identity=identity, identity_hash=digest(identity),
        evaluated=4, planned=4, confidence_sha256=sha(confidence_path))
    manifest_path = write(stage/'manifest.json', manifest)
    summary = dict(status='complete', complete=True, evaluated=4, planned=4, measurement=confidence.MEASUREMENT,
        evaluation_role=confidence.ROLE, confidence_sha256=sha(confidence_path), prepared_cases_sha256=qa['prepared_cases_sha256'],
        case_ids_sha256=qa['case_ids_sha256'], statistics=list(confidence.STATISTICS), model=model, model_revision=revision,
        batch_size=2, attention_backend='sdpa', smoke_subset=False, target_prefill_evaluations=4,
        resumed_cases=0, measured_this_attempt=4, load_seconds=0., gpu=None,
        gpu_scope='current attempt only; committed earlier chunks are reused',
        generated_tokens=0, target_outcomes_read=False, generated_holdouts_opened=False, oracle_fields_exported=False)
    summary_path = write(stage/'summary.json', summary)
    runtime = {key: summary[key] for key in ('batch_size', 'attention_backend', 'resumed_cases',
        'measured_this_attempt', 'load_seconds', 'gpu', 'gpu_scope')}
    runtime.update(status='recorded', padded_width=3, device='cpu', dtype='float32')
    write(stage/'runtime.json', runtime)
    for start in range(0, 4, 2):
        write(stage/f'chunks/{start:08d}.json', dict(config_hash=digest(cc),
            prepared_cases_sha256=qa['prepared_cases_sha256'], start=start, measurement=confidence.MEASUREMENT,
            rows=scalars[start:start+2]))
    audit = dict(status='passed', complete=True, evaluated=4, model=model, model_revision=revision,
        identity_hash=manifest['identity_hash'], confidence_sha256=sha(confidence_path), preparation=qa,
        measurement=confidence.MEASUREMENT, generated_tokens=0, target_outcomes_read=False, generated_holdouts_opened=False,
        audit_scope='schema, numerical ranges, exact input identities, complete chunk/record coverage; no outcome scoring')
    audit_path = write(stage/'audit.json', audit)
    config = dict(model=model, model_revision=revision, controls_config=str(parent_path),
        controls_config_sha256=sha(parent_path), controls_feature_manifest_sha256=sha(fm_path),
        controls_feature_table_sha256=sha(control_table), confidence_config=str(cc_path),
        confidence_config_sha256=sha(cc_path), confidence_manifest_sha256=sha(manifest_path),
        confidence_summary_sha256=sha(summary_path), confidence_audit_sha256=sha(audit_path),
        feature_table=str(tmp_path/'joined/features.jsonl'), feature_manifest=str(tmp_path/'joined/features.manifest.json'))
    return dict(config=config, parent=parent, cc=cc, feature_manifest=feature_manifest,
        qa=qa, manifest=manifest, summary=summary, audit=audit, rows=rows, cases=cases, scalars=scalars)


def test_fixed_profile_preserves_all_base_columns_and_contrasts_with_declared_access_costs():
    base = controls.predictor_columns();profile = {'feature_profile': joined.PROFILE}
    columns = prediction.predictor_columns(profile)
    assert len(base) == 8 and len(columns) == 13
    assert {name: columns[name] for name in base} == base
    assert prediction.predictor_columns() == prediction.predictor_columns({})
    assert prediction.predictor_columns({'feature_profile': controls.PROFILE}) == base
    for left, right in joined.PAIRED_TIERS:
        assert columns[right] == base[left]+list(joined.CONFIDENCE_COLUMNS)
    comparisons = prediction.predictor_comparisons(profile)
    assert len(comparisons) == len(set(comparisons)) == 24
    assert comparisons[:16] == prediction.predictor_comparisons({'feature_profile': controls.PROFILE})
    assert comparisons[16:21] == joined.PAIRED_TIERS
    role, contract = prediction._feature_contract(profile)
    assert role == joined.ROLE
    assert set(sum(contract.values(), [])) == set(sum(columns.values(), []))
    assert 'vocabulary_size' not in sum(columns.values(), [])
    assert all(not {'label', 'target_invalid', 'prediction', 'correct'} & set(keys) for keys in columns.values())
    access = joined.predictor_access()
    for name, keys in columns.items():
        assert access[name]['target_prefills_per_target'] == int(name.startswith('B_'))
        assert access[name]['neutral_queries'] == int('neutral_valid' in keys)
        assert access[name]['source_oracle_value'] == ('oracle_answer_value' in keys)
        assert access[name]['reference_correctness'] == ('neutral_failure' in keys)
        assert access[name]['target_correctness_feature'] is False
    plan = prediction._plan(profile)
    assert (plan['seeds'], plan['outer_folds'], plan['inner_folds'], plan['l2_grid']) == ([17, 29, 43], 6, 5, [.1, 1., 10., 100.])
    assert 'one target prefill' in prediction._limitation(profile)
    assert 'No mechanism C, confidence' in prediction._limitation()
    with pytest.raises(ValueError):prediction.predictor_columns({**profile, 'seeds': [117]})
    with pytest.raises(ValueError):prediction.predictor_columns({**profile, 'feature_information_contract': {'bad': []}})
    with pytest.raises(ValueError):prediction.predictor_columns({**profile, 'predictor_access': {}})


def test_completed_join_reaudits_confidence_and_exports_only_whitelisted_features_and_original_labels(chain):
    original = deepcopy(chain['rows'])
    result = joined.collect(chain['config'])
    assert result['status'] == 'passed' and result['n'] == result['groups'] == 4
    assert result['scientific_access_cost']['cached_target_prefills'] == 4
    assert result['new_language_model_queries'] == result['raw_response_payload_reads'] == 0
    assert result['target_outcomes_used_as_features'] is result['generated_holdouts_opened'] is False
    rows = read_jsonl(chain['config']['feature_table'])
    assert rows == joined.augment_rows(chain['rows'], list(reversed(chain['cases'])), list(reversed(chain['scalars'])))
    for old, new in zip(original, rows):
        assert new['label'] == old['label']
        assert {key: new['features'][key] for key in old['features']} == old['features']
        assert set(new) == set(joined.ROW_METADATA)|{'label', 'features'}
        assert set(new['features'])-set(old['features']) == set(joined.CONFIDENCE_COLUMNS)
    fit_config = dict(feature_profile=joined.PROFILE, model=chain['config']['model'],
        model_revision=chain['config']['model_revision'], feature_table=chain['config']['feature_table'],
        feature_table_sha256=result['sha256'], feature_manifest=chain['config']['feature_manifest'],
        feature_manifest_sha256=sha(chain['config']['feature_manifest']),
        feature_information_contract=joined.predictor_columns(), predictor_access=joined.predictor_access())
    checked, loaded = prediction.load_features(fit_config)
    assert checked == result and loaded == rows
    assert joined.collect(chain['config']) == result
    assert chain['rows'] == original


@pytest.mark.parametrize('change', ['controls_pin', 'confidence_pin', 'controls_role', 'incomplete',
    'smoke', 'checkpoint', 'provenance', 'reserved', 'original_prepared', 'output_alias'])
def test_both_metadata_chains_reject_before_any_payload_hash_read_or_reaudit(chain, monkeypatch, change):
    cfg = deepcopy(chain['config'])
    if change == 'controls_pin':cfg['controls_feature_manifest_sha256'] = '0'*64
    elif change == 'confidence_pin':cfg['confidence_audit_sha256'] = '0'*64
    elif change == 'controls_role':
        data = deepcopy(chain['feature_manifest']);data['evaluation_role'] = 'final_evaluation'
        write(chain['parent']['feature_manifest'], data)
        parent = deepcopy(chain['parent']);parent['feature_manifest_sha256'] = sha(parent['feature_manifest'])
        write(cfg['controls_config'], parent)
        cfg.update(controls_config_sha256=sha(cfg['controls_config']),
            controls_feature_manifest_sha256=parent['feature_manifest_sha256'])
    elif change == 'incomplete':
        data = deepcopy(chain['manifest']);data['status'] = 'started'
        path = Path(chain['cc']['run_dir'])/'confidence/manifest.json';write(path, data)
        cfg['confidence_manifest_sha256'] = sha(path)
    elif change == 'smoke':
        data = deepcopy(chain['summary']);data['smoke_subset'] = True
        path = Path(chain['cc']['run_dir'])/'confidence/summary.json';write(path, data)
        cfg['confidence_summary_sha256'] = sha(path)
    elif change == 'checkpoint':cfg['model_revision'] = 'z'*40
    elif change == 'provenance':
        qa = deepcopy(chain['qa']);qa['source_provenance']['source_dataset_sha256'] = '0'*64
        write(chain['cc']['preflight_result'], qa)
        audit = deepcopy(chain['audit']);audit['preparation'] = qa
        path = Path(chain['cc']['run_dir'])/'confidence/audit.json';write(path, audit)
        cfg['confidence_audit_sha256'] = sha(path)
    elif change == 'reserved':
        cc = deepcopy(chain['cc']);cc['run_dir'] = str(Path(cc['run_dir'])/'final')
        write(cfg['confidence_config'], cc);cfg['confidence_config_sha256'] = sha(cfg['confidence_config'])
    elif change == 'original_prepared':
        qa_path = Path(chain['cc']['source_config']).parent/'preparation.json'
        qa = json.loads(qa_path.read_text());qa['prepared_cases_sha256'] = '0'*64;write(qa_path, qa)
    elif change == 'output_alias':cfg['feature_table'] = chain['parent']['feature_table']
    paths = {Path(chain['parent']['feature_table']), Path(chain['cc']['prepared_cases']),
             Path(chain['cc']['run_dir'])/'confidence/confidence.jsonl'}
    real_bytes = Path.read_bytes
    def forbid_bytes(path, *args, **kwargs):
        if path in paths:pytest.fail('metadata failure opened a payload to hash it')
        return real_bytes(path, *args, **kwargs)
    def forbidden(*args, **kwargs):pytest.fail('metadata failure opened a payload or re-audited prematurely')
    monkeypatch.setattr(Path, 'read_bytes', forbid_bytes)
    monkeypatch.setattr(joined, 'read_jsonl', forbidden)
    monkeypatch.setattr(prediction, 'read_jsonl', forbidden)
    monkeypatch.setattr(confidence, 'read_jsonl', forbidden)
    monkeypatch.setattr(confidence, 'audit', forbidden)
    with pytest.raises(ValueError):joined.collect(cfg)


@pytest.mark.parametrize('change', ['missing', 'extra', 'duplicate', 'group', 'split', 'design',
    'prompt', 'tokens', 'row_score', 'feature_score', 'scalar_score', 'nonfinite'])
def test_exact_join_rejects_coverage_identity_design_hash_or_target_score_leakage(chain, change):
    rows, cases, scalars = deepcopy(chain['rows']), deepcopy(chain['cases']), deepcopy(chain['scalars'])
    if change == 'missing':scalars.pop()
    elif change == 'extra':cases.append({**cases[0], 'id': 'unexpected'})
    elif change == 'duplicate':rows.append(rows[0])
    elif change == 'group':rows[0]['template_id'] = 'another-group'
    elif change == 'split':rows[0]['original_split'] = 'development'
    elif change == 'design':rows[0]['features']['updates'] = 3
    elif change == 'prompt':cases[0]['prompt'] += ' changed'
    elif change == 'tokens':cases[0]['input_token_ids'][0] = 99
    elif change == 'row_score':rows[0]['correct'] = True
    elif change == 'feature_score':rows[0]['features']['target_invalid'] = 0
    elif change == 'scalar_score':scalars[0]['prediction'] = 1
    elif change == 'nonfinite':scalars[0]['entropy_nats'] = math.nan
    with pytest.raises(ValueError):joined.augment_rows(rows, cases, scalars)


def test_reserved_output_is_rejected_before_config_or_payload_open(chain, monkeypatch):
    def forbidden(*args, **kwargs):pytest.fail('reserved output opened metadata or payload')
    monkeypatch.setattr(joined, '_object', forbidden)
    with pytest.raises(ValueError):joined.collect({**chain['config'], 'feature_manifest': 'artifacts/binding/final/join.json'})


@pytest.mark.parametrize('payload', ['features', 'prepared', 'scalars'])
def test_payload_hash_failure_is_rejected_before_any_jsonl_parse_or_reaudit(chain, monkeypatch, payload):
    paths = {'features': chain['parent']['feature_table'], 'prepared': chain['cc']['prepared_cases'],
        'scalars': str(Path(chain['cc']['run_dir'])/'confidence/confidence.jsonl')}
    Path(paths[payload]).write_text('checksum changed before joining\n')
    def forbidden(*args, **kwargs):pytest.fail('a bad payload pin reached parsing or re-audit')
    monkeypatch.setattr(joined, 'read_jsonl', forbidden)
    monkeypatch.setattr(prediction, 'read_jsonl', forbidden)
    monkeypatch.setattr(confidence, 'read_jsonl', forbidden)
    monkeypatch.setattr(confidence, 'audit', forbidden)
    with pytest.raises(ValueError, match='checksum'):joined.collect(chain['config'])
