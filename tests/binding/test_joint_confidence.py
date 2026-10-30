"""Synthetic completed discovery chains; no model loads or scientific fits."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from codecue.binding import candidate_pipeline, candidate_prediction as parent
from codecue.binding import confidence_prediction as one_token
from codecue.binding import discovery_prediction as generic
from codecue.binding import joint_confidence as joint
from codecue.binding.datasets import digest, read_jsonl
from codecue.binding.published_benchmarks import sha
from test_confidence_prediction import chain, write
from test_candidate_prediction import completed


@pytest.fixture
def pipeline(completed, tmp_path):
    producer = deepcopy(completed['config'])
    ancestor_path = producer['source_prediction_config']
    ancestor = json.loads(Path(ancestor_path).read_text())
    ancestor['output_dir'] = str(tmp_path/'thirteen_tier_cv')
    write(ancestor_path, ancestor)
    producer['source_prediction_config_sha256'] = sha(ancestor_path)
    manifest = parent.collect(producer)
    out = tmp_path/'parent_pipeline'
    producer_path = write(out/'collection_config.json', producer)
    effective = {key: value for key, value in candidate_pipeline.protocol().items() if key != 'comparisons'}
    effective.update(model=producer['model'], model_revision=producer['model_revision'],
        feature_table=producer['feature_table'], feature_table_sha256=manifest['sha256'],
        feature_manifest=producer['feature_manifest'], feature_manifest_sha256=sha(producer['feature_manifest']),
        output_dir=str(out/'cv'), run_dir=str(out/'cv'), collection_config=str(producer_path),
        review_artifact=str(out/'review_v1.json'), report=str(tmp_path/'parent_report.md'))
    effective_path = write(out/'effective_config.json', effective)
    spec = dict(model=producer['model'], model_revision=producer['model_revision'],
        source_prediction_config=producer['source_prediction_config'],
        source_prediction_config_sha256=producer['source_prediction_config_sha256'],
        candidate_config=producer['candidate_config'], candidate_config_sha256=producer['candidate_config_sha256'],
        output_dir=str(out), report=effective['report'], protocol=candidate_pipeline.protocol())
    spec_path = write(tmp_path/'parent_pipeline_config.json', spec)
    summary = dict(status='complete_exploratory', n=4, templates=4, analysis_plan=generic._plan(effective),
        generated_holdouts_opened=False, mechanism_C_fitted=False)
    summary_path = write(out/'cv/summary.json', summary)
    review = dict(summary, config_hash=digest(effective), feature_manifest=manifest,
        feature_table_sha256=manifest['sha256'], feature_manifest_sha256=effective['feature_manifest_sha256'],
        artifacts={'summary': {'path':str(summary_path), 'sha256':sha(summary_path)}})
    review_path = write(effective['review_artifact'], review)
    receipt = dict(status='complete_exploratory', config_hash=digest(spec), protocol_hash=digest(candidate_pipeline.protocol()),
        collection_config=dict(path=str(producer_path), sha256=sha(producer_path)),
        effective_config=dict(path=str(effective_path), sha256=sha(effective_path)),
        review=dict(path=str(review_path), sha256=sha(review_path)),
        generated_holdouts_opened=False, mechanism_C_fitted=False, model_loading=False)
    receipt_path = write(out/'pipeline_review_v1.json', receipt)
    config = dict(model=producer['model'], model_revision=producer['model_revision'],
        source_pipeline_config=str(spec_path), source_pipeline_config_sha256=sha(spec_path),
        source_pipeline_receipt=str(receipt_path), source_pipeline_receipt_sha256=sha(receipt_path),
        feature_table=str(tmp_path/'joint/inputs/features.jsonl'), feature_manifest=str(tmp_path/'joint/inputs/features.manifest.json'))
    return dict(config=config, spec=spec, receipt=receipt, effective=effective, manifest=manifest,
                review=review, producer=producer, completed=completed)


def test_fixed_nested_profile_retains_all_eighteen_parent_tiers_and_contrasts():
    columns = joint.predictor_columns(); old = parent.predictor_columns()
    assert len(columns) == 23 and {key:columns[key] for key in old} == old
    assert len(joint.predictor_comparisons()) == len(set(joint.predictor_comparisons())) == 55
    assert joint.predictor_comparisons()[:37] == parent.predictor_comparisons()
    access = joint.predictor_access()
    assert {key:access[key] for key in old} == parent.predictor_access()
    for source, previous, event, new in joint.PAIRED_TIERS:
        assert columns[new] == columns[previous]+list(parent.EVENT_COLUMNS)
        assert set(columns[previous]) < set(columns[new])
        assert set(columns[event]) < set(columns[new])
        assert set(columns[new]) == set(columns[source])|set(one_token.CONFIDENCE_COLUMNS)|set(parent.EVENT_COLUMNS)
        assert len(columns[new]) == len(set(columns[new]))
        assert access[new]['target_prefills_per_target'] == 2
        assert access[new]['candidate_events_per_target'] == 33
        assert access[new]['candidate_prefix_states_per_target'] == 35
        assert access[new]['next_token_prefills_per_target'] == access[new]['candidate_prefix_prefills_per_target'] == 1
        assert access[new]['generated_target_tokens'] == 0
        assert access[new]['target_correctness_feature'] is False
        assert access[new]['target_prefill_measurement_dtype'] == ['bfloat16', 'float32']
    role, contract = joint.feature_contract()
    assert role == joint.ROLE and contract == parent.feature_contract()[1]
    assert len(set(sum(contract.values(), []))) == 63
    assert not set(sum(columns.values(), []))&{'label', 'target_answer', 'candidate', 'argmax_token_id', 'correct'}
    assert joint.PRIMARY_PAIRS == tuple((b, d) for _, b, _, d in joint.PAIRED_TIERS)
    assert joint.EVENT_PAIRS == tuple((c, d) for _, _, c, d in joint.PAIRED_TIERS)


@pytest.mark.parametrize('patch', [dict(seeds=[1]), dict(outer_folds=3), dict(inner_folds=2),
    dict(l2_grid=[1.]), dict(bootstrap_replicates=5), dict(bootstrap_seed=1),
    dict(feature_information_contract={}), dict(predictor_access={})])
def test_fixed_plan_rejects_every_declared_protocol_change(patch):
    with pytest.raises(ValueError): joint.predictor_columns(patch)


def test_completed_collection_preserves_every_parent_byte_label_and_feature(pipeline):
    cfg = pipeline['config']; result = joint.collect(cfg)
    assert result['status'] == 'passed' and result['n'] == result['groups'] == 4
    assert result['evaluation_role'] == joint.ROLE and result['profile'] == joint.PROFILE
    assert result['all_parent_feature_bytes_unchanged'] is True
    assert result['old_eighteen_feature_sets_and_labels_unchanged'] is True
    assert result['new_language_model_queries'] == result['raw_response_payload_reads'] == 0
    assert result['target_outcomes_used_as_features'] is False
    assert Path(cfg['feature_table']).read_bytes() == Path(pipeline['effective']['feature_table']).read_bytes()
    assert read_jsonl(cfg['feature_table']) == read_jsonl(pipeline['effective']['feature_table'])
    assert result['sha256'] == pipeline['manifest']['sha256']
    assert result['parent_effective_config_sha256'] == pipeline['receipt']['effective_config']['sha256']
    assert result['scientific_access_cost']['total_target_prefills_per_target'] == 2
    assert result['scientific_access_cost']['next_token_measurement_dtype'] == 'bfloat16'
    assert result['scientific_access_cost']['candidate_measurement_dtype'] == 'float32'
    assert joint.collect(cfg) == result
    Path(cfg['feature_manifest']).write_text('{}')
    with pytest.raises(ValueError, match='immutable joint'): joint.collect(cfg)


def rewrite_receipt(pipeline):
    cfg = pipeline['config']; write(cfg['source_pipeline_receipt'], pipeline['receipt'])
    cfg['source_pipeline_receipt_sha256'] = sha(cfg['source_pipeline_receipt'])


def rewrite_effective(pipeline):
    path = pipeline['receipt']['effective_config']['path']
    write(path, pipeline['effective']); pipeline['receipt']['effective_config']['sha256'] = sha(path)
    rewrite_receipt(pipeline)


def rewrite_manifest(pipeline):
    path = pipeline['effective']['feature_manifest']; write(path, pipeline['manifest'])
    pipeline['effective']['feature_manifest_sha256'] = sha(path)
    rewrite_effective(pipeline)


@pytest.mark.parametrize('change', ['source_pin', 'receipt_pin', 'missing_receipt_pin', 'sealed_role',
    'sealed_source_path', 'sealed_output_path', 'incomplete', 'wrong_protocol', 'review_pin',
    'producer_pin', 'effective_pin', 'feature_role', 'feature_identity', 'feature_profile', 'feature_precision',
    'candidate_scalar_hash', 'outcome_feature_declaration', 'model', 'alias', 'scalar_alias', 'receipt_path'])
def test_metadata_failures_precede_feature_payload_or_completed_fit_reads(pipeline, monkeypatch, change):
    cfg = pipeline['config']
    if change == 'source_pin': cfg['source_pipeline_config_sha256'] = '0'*64
    elif change == 'receipt_pin': cfg['source_pipeline_receipt_sha256'] = '0'*64
    elif change == 'missing_receipt_pin': cfg.pop('source_pipeline_receipt_sha256')
    elif change == 'sealed_role': cfg['evaluation_role'] = 'final_evaluation'
    elif change == 'sealed_source_path': cfg['source_pipeline_config'] = '/tmp/final/source.json'
    elif change == 'sealed_output_path': cfg['feature_table'] = '/tmp/final/features.jsonl'
    elif change in ('incomplete', 'wrong_protocol', 'review_pin', 'producer_pin', 'effective_pin'):
        if change == 'incomplete': pipeline['receipt']['status'] = 'started'
        elif change == 'wrong_protocol': pipeline['receipt']['protocol_hash'] = '0'*64
        else:
            key = {'review_pin':'review', 'producer_pin':'collection_config', 'effective_pin':'effective_config'}[change]
            pipeline['receipt'][key]['sha256'] = '0'*64
        rewrite_receipt(pipeline)
    elif change in ('feature_role', 'feature_identity', 'feature_profile', 'feature_precision',
                    'candidate_scalar_hash', 'outcome_feature_declaration'):
        data = pipeline['manifest']
        if change == 'feature_role': data['evaluation_role'] = 'final_evaluation'
        elif change == 'feature_identity': data['source_identity_hash'] = '0'*64
        elif change == 'feature_profile': data['profile'] = 'confidence_access_v1'
        elif change == 'feature_precision': data['candidate_precision']['actual_model_dtype'] = 'bfloat16'
        elif change == 'candidate_scalar_hash': data['candidate_scalar_sha256'] = '0'*64
        else: data['target_outcomes_used_as_features'] = True
        rewrite_manifest(pipeline)
    elif change == 'model': cfg['model'] = 'wrong/checkpoint'
    elif change == 'alias': cfg['feature_table'] = pipeline['effective']['feature_table']
    elif change == 'scalar_alias':
        cfg['feature_table'] = str(Path(pipeline['completed']['cc']['run_dir'])/'candidate_measurement/scalars.jsonl')
    else: cfg['source_pipeline_receipt'] = str(Path(cfg['source_pipeline_receipt']).parent/'other.json')
    def forbidden(*args, **kwargs): raise AssertionError('payload/fit access occurred before metadata rejection')
    monkeypatch.setattr(generic, 'load_features', forbidden)
    monkeypatch.setattr(generic, '_reuse', forbidden)
    with pytest.raises(ValueError): joint.collect(cfg)
    assert not Path(cfg['feature_manifest']).exists()


def test_parent_feature_payload_tampering_rejected_before_new_artifacts(pipeline):
    Path(pipeline['effective']['feature_table']).write_text('{}\n')
    with pytest.raises(ValueError, match='checksum'): joint.collect(pipeline['config'])
    assert not Path(pipeline['config']['feature_manifest']).exists()


def test_parent_fitting_summary_tampering_rejected_before_new_artifacts(pipeline):
    path = pipeline['review']['artifacts']['summary']['path']; Path(path).write_text('{}')
    with pytest.raises(ValueError, match='summary artifact changed'): joint.collect(pipeline['config'])
    assert not Path(pipeline['config']['feature_manifest']).exists()


def test_pipeline_validate_rejects_changed_protocol_and_overlapping_output(pipeline, tmp_path):
    cfg = pipeline['config']
    spec = {key: cfg[key] for key in ('model', 'model_revision', 'source_pipeline_config',
        'source_pipeline_config_sha256', 'source_pipeline_receipt', 'source_pipeline_receipt_sha256')}
    spec.update(output_dir=str(tmp_path/'joint_run'), report=str(tmp_path/'joint.md'), protocol=joint.protocol())
    assert joint.validate(spec) == pipeline['spec']
    for path in (pipeline['spec']['output_dir'], str(Path(pipeline['spec']['output_dir'])/'nested'), str(tmp_path)):
        with pytest.raises(ValueError): joint.validate({**spec, 'output_dir':path})
    with pytest.raises(ValueError, match='fixed joint'): joint.validate({**spec, 'protocol':{}})


def test_fit_stages_fixed_effective_config_and_immutable_completed_receipt(pipeline, tmp_path, monkeypatch):
    cfg = pipeline['config']
    spec = {key: cfg[key] for key in ('model', 'model_revision', 'source_pipeline_config',
        'source_pipeline_config_sha256', 'source_pipeline_receipt', 'source_pipeline_receipt_sha256')}
    spec.update(output_dir=str(tmp_path/'joint_run'), report=str(tmp_path/'joint.md'), protocol=joint.protocol())
    seen = []
    def run(effective):
        seen.append(deepcopy(effective)); write(effective['review_artifact'], {'status':'complete_exploratory'})
    monkeypatch.setattr(generic, 'run', run)
    result = joint.fit(spec)
    assert result['status'] == 'complete_exploratory' and result['model_loading'] is False
    effective = seen[0]
    assert effective['feature_profile'] == joint.PROFILE
    assert effective['feature_information_contract'] == joint.predictor_columns()
    assert effective['predictor_access'] == joint.predictor_access()
    assert effective['seeds'] == [17, 29, 43]
    assert result['effective_config']['sha256'] == sha(result['effective_config']['path'])
    assert result['review']['sha256'] == sha(result['review']['path'])
    assert Path(effective['feature_table']).read_bytes() == Path(pipeline['effective']['feature_table']).read_bytes()
