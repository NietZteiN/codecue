"""Synthetic completed chains only: no study fits, model loads or raw responses."""
from copy import deepcopy
import json
import math
from pathlib import Path

import pytest

from codecue.binding import candidate_confidence as event
from codecue.binding import candidate_measurement as measurement
from codecue.binding import candidate_prediction as prediction
from codecue.binding import confidence
from codecue.binding import confidence_prediction as parent_features
from codecue.binding import discovery_prediction as generic
from codecue.binding.datasets import digest, read_jsonl
from codecue.binding.published_benchmarks import sha
from test_confidence_prediction import chain, write, jsonl


@pytest.fixture
def completed(chain, tmp_path, monkeypatch):
    """Build four synthetic complete cases, retaining every real guard/code path."""
    monkeypatch.setattr(measurement, 'SOURCE_CASES', 4)
    producer = chain['config'];pm = parent_features.collect(producer)
    producer_path = write(tmp_path/'parent_collection.json', producer)
    parent = dict(model=producer['model'], model_revision=producer['model_revision'],
        feature_profile=parent_features.PROFILE, collection_config=str(producer_path),
        feature_table=producer['feature_table'], feature_table_sha256=pm['sha256'],
        feature_manifest=producer['feature_manifest'], feature_manifest_sha256=sha(producer['feature_manifest']),
        feature_information_contract=parent_features.predictor_columns(), predictor_access=parent_features.predictor_access(),
        seeds=[17, 29, 43], outer_folds=6, inner_folds=5, l2_grid=[.1, 1., 10., 100.])
    parent_path = write(tmp_path/'parent_prediction.json', parent)
    declaration = dict(evaluation_role=event.ROLE, bounds=[-16, 16], eos_token_ids=chain['cc']['eos_token_ids'],
        terminator='eos', tokenization_rule=measurement.JOINT_RULE, output_review=str(tmp_path/'event_declaration_review.json'))
    declaration_path = write(tmp_path/'event_declaration.json', declaration);event.preflight(declaration)
    folder = tmp_path/'event_collection';stage = folder/'candidate_measurement'
    cc = {key: chain['cc'][key] for key in confidence.IDENTITY_FIELDS}
    cc.update(evaluation_role=measurement.ROLE, dataset=chain['cc']['dataset'], device='cpu',
        source_confidence_config=producer['confidence_config'], source_confidence_config_sha256=producer['confidence_config_sha256'],
        candidate_declaration=str(declaration_path), candidate_declaration_sha256=sha(declaration_path),
        prepared_events=str(folder/'events.jsonl'), preparation_review=str(folder/'preparation.json'), run_dir=str(folder),
        tokenization_rule=measurement.JOINT_RULE, measurement_dtype='float32', attention_backend='sdpa',
        scoring_backend='cached_trie', batch_size=2, event_batch_size=16, prompt_batch_size=2, max_active_nodes=128)
    cc_path = write(tmp_path/'candidate_config.json', cc)
    _, candidates, eos, provenance = measurement._metadata(cc)
    cases = [];scalars = []
    for source in chain['cases']:
        events = []
        for value in candidates:
            continuation = [20+value] if value >= 0 else [10, 20+abs(value)]
            for ending in eos:
                events.append(dict(candidate=value, surface=str(value), continuation_token_ids=continuation,
                    eos_token_id=ending, event_token_ids=continuation+[ending]))
        bank = dict(schema_version=1, evaluation_role=event.ROLE, measurement=event.MEASUREMENT,
            prompt_sha256=source['prompt_sha256'], input_token_ids=source['input_token_ids'],
            input_token_ids_sha256=source['input_token_ids_sha256'], candidates=candidates, eos_token_ids=eos,
            terminator='eos', events=events, prefix_free=True)
        bank['bank_sha256'] = digest(bank);event.validate_bank(bank)
        case = {**{key: source[key] for key in confidence.CASE_FIELDS}, 'evaluation_role': measurement.ROLE, 'event_bank': bank}
        assert len(measurement.trie(bank)) == 35
        cases.append(case)
        scalars.append({**{key: case[key] for key in confidence.CASE_FIELDS}, 'measurement_role': measurement.ROLE,
            'prompt_sha256': bank['prompt_sha256'], 'input_token_ids_sha256': bank['input_token_ids_sha256'],
            'event_bank_sha256': bank['bank_sha256'], 'support_mass_underflowed': False,
            'candidate_count': 33, 'eos_variant_count': len(eos), 'trie_nodes': 35,
            'support_mass': .5, 'support_log_mass': math.log(.5), 'support_conditional_entropy_nats': math.log(33),
            'support_conditional_top_two_probability_margin': 0., 'support_max_mass': .5/33,
            'support_conditional_max_probability': 1/33})
    jsonl(cc['prepared_events'], cases)
    prepared_sha = sha(cc['prepared_events']);candidate_code = '1'*64
    qa = dict(status='passed', complete=True, evaluation_role=measurement.ROLE, measurement=measurement.MEASUREMENT,
        config_hash=digest(cc), source_sha256=candidate_code, provenance=provenance,
        model=cc['model'], model_revision=cc['model_revision'], tokenizer_revision=cc['tokenizer_revision'],
        candidates=candidates, eos_token_ids=eos, source_cases=4, cases=4, smoke_subset=False,
        generated_tokens=0, target_outcomes_read=False, upstream_scalar_payloads_read=False,
        oracle_fields_exported=False, generated_holdouts_opened=False, tokenization_rule=measurement.JOINT_RULE,
        **measurement._precision(cc), actual_model_dtype=None, actual_model_dtype_verified=False,
        parity_tolerance_rule=measurement.TOLERANCE_RULE, prepared_events_sha256=prepared_sha,
        case_ids_sha256=digest([case['id'] for case in cases]), event_banks_sha256=digest([case['event_bank']['bank_sha256'] for case in cases]),
        candidate_count=33, eos_variant_count=len(eos), prefix_free=True, boundary_verified=True,
        tokenizer=dict(vocabulary_size=64, pad_token_id=15, eos_token_spellings=['<eos>']),
        trie_nodes={'35': 4}, prefix_node_evaluations=140)
    write(cc['preparation_review'], qa)
    scalar_path = jsonl(stage/'scalars.jsonl', scalars)
    dm = json.loads(Path(cc['dataset']).with_suffix('.manifest.json').read_text())
    identity = dict(config=cc, config_hash=digest(cc), stage='candidate_measurement',
        model_revision=cc['model_revision'], tokenizer_revision=cc['tokenizer_revision'],
        dataset_manifest=dm, code={'source_sha256': candidate_code})
    manifest = dict(status='complete', identity=identity, identity_hash=digest(identity), evaluated=4, planned=4,
        scalar_sha256=sha(scalar_path))
    manifest_path = write(stage/'manifest.json', manifest)
    precision = dict(measurement._precision(cc), actual_model_dtype='float32', actual_model_dtype_verified=True,
        tf32_settings=dict(float32_matmul_precision='highest', cuda_matmul_allow_tf32=False, cudnn_allow_tf32=False))
    runtime = dict(status='recorded', scoring_backend=cc['scoring_backend'], attention_backend='sdpa',
        batch_size=2, event_batch_size=16, prompt_batch_size=2, max_active_nodes=128, device='cpu', dtype='float32',
        load_seconds=0., gpu=None, **precision, tokenization_rule=measurement.JOINT_RULE,
        resumed_cases=0, measured_this_attempt=4, gpu_scope='current attempt only', versions={'torch': 'synthetic', 'transformers': 'synthetic'})
    write(stage/'runtime.json', runtime)
    executions = []
    for start in (0, 2):
        execution = dict(scoring_backend='cached_trie', cases=2, prefix_nodes=70, naive_event_variants=66,
            forward_calls=3, parity_reference_forward_calls=0, parity=measurement._empty_parity(), precision=precision)
        executions.append(execution)
        write(stage/f'chunks/{start:08d}.json', dict(config_hash=digest(cc), prepared_events_sha256=prepared_sha,
            measurement=measurement.MEASUREMENT, start=start, rows=scalars[start:start+2], execution=execution))
    summary = dict(runtime, status='complete', complete=True, evaluated=4, planned=4,
        evaluation_role=measurement.ROLE, measurement=measurement.MEASUREMENT, scalar_sha256=sha(scalar_path),
        prepared_events_sha256=prepared_sha, case_ids_sha256=qa['case_ids_sha256'], event_banks_sha256=qa['event_banks_sha256'],
        model=cc['model'], model_revision=cc['model_revision'], statistics=list(measurement.SCALARS),
        generated_tokens=0, target_outcomes_read=False, upstream_scalar_payloads_read=False,
        oracle_fields_exported=False, generated_holdouts_opened=False, smoke_subset=False,
        prefix_node_evaluations=140, backend_forward_calls=6, parity_reference_forward_calls=0,
        parity=measurement._parity_summary(cc, executions, 4), wall_seconds=0.)
    summary_path = write(stage/'summary.json', summary)
    audit = dict(status='passed', complete=True, evaluated=4, model=cc['model'], model_revision=cc['model_revision'],
        identity_hash=manifest['identity_hash'], scalar_sha256=sha(scalar_path), preparation=qa,
        measurement=measurement.MEASUREMENT, generated_tokens=0, target_outcomes_read=False, upstream_scalar_payloads_read=False,
        audit_scope='schema, finite numerical domains, exact input identities, chunk/record coverage and configured parity; no outcome scoring')
    audit_path = write(stage/'audit.json', audit)
    config = dict(model=cc['model'], model_revision=cc['model_revision'], source_prediction_config=str(parent_path),
        source_prediction_config_sha256=sha(parent_path), candidate_config=str(cc_path), candidate_config_sha256=sha(cc_path),
        candidate_manifest_sha256=sha(manifest_path), candidate_summary_sha256=sha(summary_path), candidate_audit_sha256=sha(audit_path),
        feature_table=str(tmp_path/'event_features/features.jsonl'), feature_manifest=str(tmp_path/'event_features/features.manifest.json'))
    return dict(config=config, parent=parent, pm=pm, cc=cc, qa=qa, manifest=manifest, summary=summary, audit=audit,
        cases=cases, scalars=scalars, rows=read_jsonl(parent['feature_table']), producer=producer, chain=chain)


def test_profile_retains_thirteen_tiers_and_adds_only_five_event_alternatives():
    cfg = {'feature_profile': prediction.PROFILE};columns = generic.predictor_columns(cfg)
    old = parent_features.predictor_columns();access = prediction.predictor_access()
    assert len(columns) == 18 and {name: columns[name] for name in old} == old
    assert {name: access[name] for name in old} == parent_features.predictor_access()
    for source, previous, new in prediction.PAIRED_TIERS:
        assert columns[new] == old[source]+list(prediction.EVENT_COLUMNS)
        assert not set(parent_features.CONFIDENCE_COLUMNS)&set(columns[new])
        assert access[new]['neutral_queries'] == access[source]['neutral_queries']
        assert access[new]['source_oracle_value'] == access[source]['source_oracle_value']
        assert access[new]['reference_correctness'] == access[source]['reference_correctness']
        assert access[new]['target_prefills_per_target'] == 1
        assert access[new]['candidate_events_per_target'] == 33
        assert access[new]['candidate_prefix_states_per_target'] == 35
        assert access[new]['target_prefill_measurement_dtype'] == 'float32'
        assert access[new]['target_correctness_feature'] is False
    pairs = generic.predictor_comparisons(cfg)
    assert len(pairs) == len(set(pairs)) == 37
    assert pairs[:24] == parent_features.predictor_comparisons()
    assert pairs[24:29] == tuple((a, c) for a, _, c in prediction.PAIRED_TIERS)
    assert pairs[29:34] == tuple((b, c) for _, b, c in prediction.PAIRED_TIERS)
    role, contract = generic._feature_contract(cfg)
    assert role == prediction.ROLE and len(set(sum(contract.values(), []))) == 63
    assert set(sum(contract.values(), [])) == set(sum(columns.values(), []))
    assert all(not set(keys)&{'label', 'correct', 'candidate', 'event_bank_sha256', 'trie_nodes', 'eos_variant_count'} for keys in columns.values())
    plan = generic._plan(cfg)
    assert (plan['seeds'], plan['outer_folds'], plan['inner_folds'], plan['l2_grid']) == ([17, 29, 43], 6, 5, [.1, 1., 10., 100.])
    assert generic.predictor_columns({'feature_profile': parent_features.PROFILE}) == old
    assert 'alternative measurement bundles' in generic._limitation(cfg)
    assert 'FP32/no-TF32 versus BF16' in generic._limitation(cfg)
    assert 'No mechanism C, confidence' in generic._limitation()
    for patch in ({'l2_grid': [1.]}, {'seeds': [1]}, {'feature_information_contract': {}}, {'predictor_access': {}}):
        with pytest.raises(ValueError):generic.predictor_columns({**cfg, **patch})


def test_completed_join_reaudits_and_keeps_every_old_feature_label_and_identity(completed):
    before = deepcopy(completed['rows']);result = prediction.collect(completed['config'])
    rows = read_jsonl(completed['config']['feature_table'])
    assert result['n'] == result['groups'] == 4
    assert result['scientific_access_cost']['total_prefix_states'] == 140
    assert result['raw_response_payload_reads'] == result['new_language_model_queries'] == 0
    assert result['old_thirteen_feature_sets_and_labels_unchanged'] is True
    assert result['candidate_precision']['actual_model_dtype_verified'] is True
    assert result['candidate_precision']['tf32_settings']['cuda_matmul_allow_tf32'] is False
    assert rows == prediction.augment_rows(before, list(reversed(completed['cases'])), list(reversed(completed['scalars'])))
    for old, new in zip(before, rows):
        assert {key: new[key] for key in old if key != 'features'} == {key: old[key] for key in old if key != 'features'}
        assert {key: new['features'][key] for key in old['features']} == old['features']
        assert set(new['features'])-set(old['features']) == set(prediction.EVENT_COLUMNS)
    fit = dict(feature_profile=prediction.PROFILE, model=completed['config']['model'], model_revision=completed['config']['model_revision'],
        feature_table=completed['config']['feature_table'], feature_table_sha256=result['sha256'],
        feature_manifest=completed['config']['feature_manifest'], feature_manifest_sha256=sha(completed['config']['feature_manifest']),
        feature_information_contract=prediction.predictor_columns(), predictor_access=prediction.predictor_access())
    assert generic.load_features(fit) == (result, rows)
    assert prediction.collect(completed['config']) == result
    assert completed['rows'] == before


def update_parent(completed, cfg, manifest):
    parent = deepcopy(completed['parent']);write(parent['feature_manifest'], manifest)
    parent['feature_manifest_sha256'] = sha(parent['feature_manifest'])
    write(cfg['source_prediction_config'], parent);cfg['source_prediction_config_sha256'] = sha(cfg['source_prediction_config'])


@pytest.mark.parametrize('change', ['parent_pin', 'candidate_pin', 'parent_role', 'missing_parent_pin',
    'incomplete', 'audit_failed', 'smoke', 'bf16', 'dtype_unverified', 'tf32', 'source_identity',
    'case_ids', 'events', 'checkpoint', 'reserved', 'alias', 'groups',
    'runtime_device', 'runtime_batch', 'tokenizer_revision', 'identity_revision', 'vocabulary'])
def test_metadata_failures_are_rejected_before_payload_hashes_parsing_or_reaudit(completed, monkeypatch, change):
    cfg = deepcopy(completed['config']);stage = Path(completed['cc']['run_dir'])/'candidate_measurement'
    if change == 'parent_pin':cfg['source_prediction_config_sha256'] = '0'*64
    elif change == 'candidate_pin':cfg['candidate_audit_sha256'] = '0'*64
    elif change in ('parent_role', 'source_identity', 'groups'):
        pm = deepcopy(completed['pm'])
        if change == 'parent_role':pm['evaluation_role'] = 'final_evaluation'
        elif change == 'groups':pm['groups'] += 1
        else:pm['confidence_identity_hash'] = '0'*64
        update_parent(completed, cfg, pm)
    elif change == 'missing_parent_pin':
        parent = deepcopy(completed['parent']);parent.pop('feature_manifest_sha256')
        write(cfg['source_prediction_config'], parent);cfg['source_prediction_config_sha256'] = sha(cfg['source_prediction_config'])
    elif change == 'incomplete':
        data = deepcopy(completed['manifest']);data['status'] = 'started';write(stage/'manifest.json', data)
        cfg['candidate_manifest_sha256'] = sha(stage/'manifest.json')
    elif change == 'audit_failed':
        data = deepcopy(completed['audit']);data['status'] = 'failed';write(stage/'audit.json', data)
        cfg['candidate_audit_sha256'] = sha(stage/'audit.json')
    elif change in ('smoke', 'bf16', 'reserved'):
        cc = deepcopy(completed['cc'])
        if change == 'smoke':cc['case_limit'] = 1
        elif change == 'bf16':cc['measurement_dtype'] = 'bfloat16'
        else:cc['run_dir'] = str(Path(cc['run_dir'])/'final')
        write(cfg['candidate_config'], cc);cfg['candidate_config_sha256'] = sha(cfg['candidate_config'])
    elif change == 'dtype_unverified':
        data = deepcopy(completed['summary']);data['actual_model_dtype_verified'] = False;write(stage/'summary.json', data)
        cfg['candidate_summary_sha256'] = sha(stage/'summary.json')
    elif change == 'tf32':
        data = json.loads((stage/'runtime.json').read_text());data['tf32_settings']['cuda_matmul_allow_tf32'] = True
        write(stage/'runtime.json', data)
    elif change in ('runtime_device', 'runtime_batch'):
        key, value = ('device', 'different_device') if change == 'runtime_device' else ('batch_size', 3)
        runtime = json.loads((stage/'runtime.json').read_text());runtime[key] = value;write(stage/'runtime.json', runtime)
        summary = deepcopy(completed['summary']);summary[key] = value;write(stage/'summary.json', summary)
        cfg['candidate_summary_sha256'] = sha(stage/'summary.json')
    elif change in ('tokenizer_revision', 'vocabulary'):
        qa = deepcopy(completed['qa'])
        if change == 'tokenizer_revision':qa['tokenizer_revision'] = 'z'*40
        else:qa['tokenizer']['vocabulary_size'] = 2
        write(completed['cc']['preparation_review'], qa)
        audit = deepcopy(completed['audit']);audit['preparation'] = qa;write(stage/'audit.json', audit)
        cfg['candidate_audit_sha256'] = sha(stage/'audit.json')
    elif change == 'identity_revision':
        manifest = deepcopy(completed['manifest']);manifest['identity']['model_revision'] = 'z'*40
        manifest['identity_hash'] = digest(manifest['identity']);write(stage/'manifest.json', manifest)
        cfg['candidate_manifest_sha256'] = sha(stage/'manifest.json')
        audit = deepcopy(completed['audit']);audit['identity_hash'] = manifest['identity_hash'];write(stage/'audit.json', audit)
        cfg['candidate_audit_sha256'] = sha(stage/'audit.json')
    elif change in ('case_ids', 'events'):
        qa = deepcopy(completed['qa']);qa['case_ids_sha256' if change == 'case_ids' else 'event_banks_sha256'] = '0'*64
        write(completed['cc']['preparation_review'], qa)
    elif change == 'checkpoint':cfg['model_revision'] = 'z'*40
    elif change == 'alias':cfg['feature_table'] = completed['parent']['feature_table']
    paths = {Path(completed['parent']['feature_table']), Path(completed['cc']['prepared_events']),
        stage/'scalars.jsonl', Path(completed['chain']['cc']['prepared_cases'])}
    real_bytes = Path.read_bytes
    def guarded_bytes(path, *args, **kwargs):
        if path in paths:pytest.fail('metadata failure hash-opened a raw payload')
        return real_bytes(path, *args, **kwargs)
    def forbidden(*args, **kwargs):pytest.fail('metadata failure reached parsing or re-audit')
    monkeypatch.setattr(Path, 'read_bytes', guarded_bytes)
    monkeypatch.setattr(prediction, 'read_jsonl', forbidden)
    monkeypatch.setattr(generic, 'read_jsonl', forbidden)
    monkeypatch.setattr(measurement, 'read_jsonl', forbidden)
    monkeypatch.setattr(measurement, 'audit', forbidden)
    with pytest.raises(ValueError):prediction.collect(cfg)


@pytest.mark.parametrize('which', ['parent', 'events', 'scalars', 'prompts'])
def test_every_payload_pin_passes_before_any_jsonl_parse(completed, monkeypatch, which):
    paths = {'parent': completed['parent']['feature_table'], 'events': completed['cc']['prepared_events'],
        'scalars': str(Path(completed['cc']['run_dir'])/'candidate_measurement/scalars.jsonl'),
        'prompts': completed['chain']['cc']['prepared_cases']}
    Path(paths[which]).write_text('changed payload\n')
    def forbidden(*args, **kwargs):pytest.fail('bad payload hash reached parsing or re-audit')
    monkeypatch.setattr(prediction, 'read_jsonl', forbidden);monkeypatch.setattr(measurement, 'audit', forbidden)
    with pytest.raises(ValueError, match='checksum'):prediction.collect(completed['config'])


@pytest.mark.parametrize('change', ['missing', 'extra', 'duplicate', 'group', 'split', 'design', 'prompt',
    'event', 'row_score', 'feature_score', 'candidate_identity', 'nonfinite'])
def test_exact_join_rejects_wrong_coverage_design_events_or_score_leakage(completed, change):
    rows, cases, scalars = deepcopy(completed['rows']), deepcopy(completed['cases']), deepcopy(completed['scalars'])
    if change == 'missing':scalars.pop()
    elif change == 'extra':cases.append({**cases[0], 'id': 'extra'})
    elif change == 'duplicate':rows.append(rows[0])
    elif change == 'group':rows[0]['template_id'] = 'unregistered'
    elif change == 'split':rows[0]['original_split'] = 'development'
    elif change == 'design':rows[0]['features']['updates'] = 3
    elif change == 'prompt':scalars[0]['prompt_sha256'] = '0'*64
    elif change == 'event':scalars[0]['event_bank_sha256'] = '0'*64
    elif change == 'row_score':rows[0]['correct'] = True
    elif change == 'feature_score':rows[0]['features']['prediction'] = 1
    elif change == 'candidate_identity':scalars[0]['candidate'] = 1
    elif change == 'nonfinite':scalars[0]['support_log_mass'] = -math.inf
    with pytest.raises(ValueError):prediction.augment_rows(rows, cases, scalars)


def test_reserved_output_is_rejected_before_source_metadata_open(completed, monkeypatch):
    def forbidden(*args, **kwargs):pytest.fail('reserved output opened a source')
    monkeypatch.setattr(parent_features, '_object', forbidden)
    with pytest.raises(ValueError):prediction.collect({**completed['config'], 'feature_manifest': 'artifacts/binding/final/events.json'})
