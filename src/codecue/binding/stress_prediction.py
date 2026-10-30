"""Discovery prediction from a distinct, ungraded program stress query.

Every existing joint-confidence tier remains an exact replay. Five fixed new
tiers combine next-token confidence with a raw response to a separately
declared stress query; stress correctness and original target responses are
never exposed as features. All model execution is performed upstream.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from . import joint_confidence as parent
from . import confidence_prediction as one_token
from .datasets import digest, read_jsonl
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable, sha

PROFILE = 'stress_query_confidence_v1'
ROLE = 'discovery_failure_prediction_stress_query_v1'
SCALARS = ('valid', 'response_chars', 'output_tokens', 'prediction_value', 'prediction_abs')
NEW_PREDICTOR_MAX_ITERATIONS = 1000
STRESS_COLUMNS = tuple('stress_'+key for key in SCALARS)
PAIRED_TIERS = tuple((source, previous, joint, joint.replace('B_joint_', 'B_stress_'))
    for source, previous, _, joint in parent.PAIRED_TIERS)
PRIMARY_PAIRS = tuple((previous, stress) for _, previous, _, stress in PAIRED_TIERS)
JOINT_PAIRS = tuple((joint, stress) for _, _, joint, stress in PAIRED_TIERS)
LIMITATION = (
    'Exploratory nested grouped prediction on already-consumed discovery targets; '
    'not mechanism C or unfamiliar-program/final confirmation. All twenty-three '
    'existing tiers are retained unchanged. Five new fixed tiers add only five '
    'raw scalar properties of one distinct stress-query response to the matching '
    'source-context plus BF16 next-token confidence tier. New tiers exclude the '
    'six finite-event likelihood scalars. The stress query is an additional '
    'observation, with its scientific access cost declared even when responses '
    'are cached: one BF16 next-token prefill plus one distinct stress query '
    'generating at most 32 tokens. Neutral-query and source-oracle access stay '
    'separately declared per context. Stress correctness, original target '
    'responses, original correctness and original generated-answer identity are not features; '
    'original correctness is only the existing supervised label. Stress validity, '
    'raw character/token lengths and parsed signed-integer value/magnitude are '
    'features of the additional response without grading it; its parsed response '
    'identity is explicitly available. Comparisons with '
    'next-token tiers are feature-nested; comparisons with joint finite-event '
    'tiers are alternatives with different observations, encoding and access '
    'costs. A gain does not identify a pure information increment or causal '
    'binding mechanism. Repeated partition seeds reuse the same structures, '
    'and bootstrap intervals condition on saved OOF probabilities without '
    'refitting or multiplicity correction. The five new stress tiers allow '
    '1000 Newton iterations with the original objective, initialization, '
    'normalization, backtracking and 1e-8 stopping tolerance. All twenty-three '
    'parent tiers retain their original 100-iteration allowance.'
)


def predictor_columns(config=None):
    columns = parent.predictor_columns()
    columns.update({stress: columns[previous]+list(STRESS_COLUMNS)
                    for _, previous, _, stress in PAIRED_TIERS})
    if config is not None:
        fixed = dict(seeds=[17, 29, 43], outer_folds=6, inner_folds=5,
            l2_grid=[.1, 1., 10., 100.], bootstrap_replicates=2000, bootstrap_seed=117,
            new_predictor_max_iterations=NEW_PREDICTOR_MAX_ITERATIONS)
        if any(key in config and config[key] != value for key, value in fixed.items()):
            raise ValueError('stress profile retains fixed grouped fitting and bootstrap protocol')
        if config.get('feature_information_contract', columns) != columns:
            raise ValueError('stress feature declaration differs from fixed twenty-eight-tier profile')
        if 'predictor_access' in config and config['predictor_access'] != predictor_access():
            raise ValueError('stress access declaration differs from fixed scientific costs')
    return columns


def predictor_access():
    access = parent.predictor_access()
    for _, previous, _, stress in PAIRED_TIERS:
        access[stress] = {**access[previous], 'stress_queries': 1,
            'stress_max_new_tokens_per_query': 32, 'stress_correctness_feature': False,
            'original_target_response_features': False, 'stress_response_identity_features': True,
            'stress_response_features': list(SCALARS), 'candidate_event_features': False,
            'next_token_prefills_per_target': 1, 'target_prefill_measurement_dtype': 'bfloat16'}
    return access


def predictor_comparisons(config=None):
    predictor_columns(config)
    return parent.predictor_comparisons()+PRIMARY_PAIRS+JOINT_PAIRS+tuple(
        (source, stress) for source, _, _, stress in PAIRED_TIERS)


def feature_contract(config=None):
    predictor_columns(config)
    return ROLE, {**parent.feature_contract()[1], 'stress_query': list(STRESS_COLUMNS)}


def protocol():
    return dict(feature_profile=PROFILE, feature_information_contract=predictor_columns(),
        predictor_access=predictor_access(), comparisons=[list(pair) for pair in predictor_comparisons()],
        seeds=[17, 29, 43], outer_folds=6, inner_folds=5, l2_grid=[.1, 1., 10., 100.],
        bootstrap_replicates=2000, bootstrap_seed=117,
        new_predictor_max_iterations=NEW_PREDICTOR_MAX_ITERATIONS)


def _json(path, value):
    immutable(path, (json.dumps(value, sort_keys=True, indent=2)+'\n').encode())


def _parent_metadata(config):
    """Validate the completed joint bank and its complete candidate ancestry."""
    from . import discovery_prediction as generic
    _discovery_declaration(config)
    for key in ('source_pipeline_config', 'source_pipeline_receipt', 'feature_table', 'feature_manifest'):
        _discovery_response_path(config[key])
    for key in ('source_pipeline_config_sha256', 'source_pipeline_receipt_sha256'):
        parent._pin(config.get(key), key)
    if (Path(config['feature_table']).suffix != '.jsonl' or Path(config['feature_manifest']).suffix != '.json'
            or one_token._same_path(config['feature_table'], config['feature_manifest'])):
        raise ValueError('distinct JSONL feature and JSON manifest outputs required')
    spec = one_token._object(config['source_pipeline_config'], config['source_pipeline_config_sha256'])
    parent.validate(spec)
    out = Path(spec['output_dir'])
    if not one_token._same_path(config['source_pipeline_receipt'], out/'pipeline_review_v1.json'):
        raise ValueError('parent joint pipeline receipt path differs')
    receipt = one_token._object(config['source_pipeline_receipt'], config['source_pipeline_receipt_sha256'])
    if (receipt.get('status') != 'complete_exploratory' or receipt.get('config_hash') != digest(spec)
            or receipt.get('protocol_hash') != digest(parent.protocol())
            or any(receipt.get(key) is not False for key in
                   ('generated_holdouts_opened', 'mechanism_C_fitted', 'model_loading'))):
        raise ValueError('complete matching discovery joint pipeline receipt required')
    loaded = {}
    for key in ('collection_config', 'effective_config'):
        expected = out/(key+'.json')
        link = receipt.get(key, {})
        if not one_token._same_path(link.get('path', ''), expected):
            raise ValueError('joint pipeline '+key+' path differs')
        parent._pin(link.get('sha256'), key)
        loaded[key] = one_token._object(expected, link['sha256'], key)
    effective, producer = loaded['effective_config'], loaded['collection_config']
    if effective.get('feature_profile') != parent.PROFILE:
        raise ValueError('completed twenty-three-tier joint-confidence parent required')
    parent.predictor_columns(effective)
    if generic._plan(effective) != generic._plan(parent.protocol()):
        raise ValueError('parent joint fitting protocol differs')
    if not one_token._same_path(effective.get('collection_config', ''), out/'collection_config.json'):
        raise ValueError('joint feature producer link differs')
    for key in ('feature_table', 'feature_manifest', 'review_artifact'):
        _discovery_response_path(effective[key])
    for key in ('feature_table_sha256', 'feature_manifest_sha256'):
        parent._pin(effective.get(key), key)
    link = receipt.get('review', {})
    if not one_token._same_path(link.get('path', ''), effective['review_artifact']):
        raise ValueError('parent joint fitting review path differs')
    parent._pin(link.get('sha256'), 'joint parent review')
    review = one_token._object(effective['review_artifact'], link['sha256'], 'joint parent review')
    manifest = one_token._object(effective['feature_manifest'], effective['feature_manifest_sha256'])
    ancestor, ancestor_manifest, ancestor_receipt = parent._metadata(producer)
    if (manifest.get('status') != 'passed' or manifest.get('profile') != parent.PROFILE
            or manifest.get('evaluation_role') != parent.ROLE or manifest.get('columns') != parent.feature_contract()[1]
            or manifest.get('predictor_columns') != parent.predictor_columns()
            or manifest.get('predictor_access') != parent.predictor_access()
            or manifest.get('sha256') != effective['feature_table_sha256']
            or manifest.get('config_hash') != digest(producer)
            or not one_token._same_path(manifest.get('feature_table', ''), effective['feature_table'])
            or any(not one_token._same_path(producer[key], effective[key]) for key in ('feature_table', 'feature_manifest'))
            or any(manifest.get(key) != ancestor_manifest[key] for key in (*one_token.SOURCE_KEYS, 'n', 'groups'))
            or any(manifest.get(key) is not True for key in ('old_eighteen_feature_sets_and_labels_unchanged',
                'all_parent_feature_bytes_unchanged', 'target_metadata_labels_references_unchanged'))
            or any(manifest.get(key) is not False for key in
                ('generated_holdouts_opened', 'target_outcomes_used_as_features', 'mechanism_C_fitted'))):
        raise ValueError('joint parent feature/source/coverage contract differs')
    if (manifest.get('source_pipeline_config_sha256') != producer['source_pipeline_config_sha256']
            or manifest.get('source_pipeline_receipt_sha256') != producer['source_pipeline_receipt_sha256']
            or manifest.get('parent_effective_config_sha256') != ancestor_receipt['effective_config']['sha256']
            or manifest.get('parent_feature_manifest_sha256') != ancestor['feature_manifest_sha256']
            or manifest.get('parent_feature_table_sha256') != ancestor['feature_table_sha256']):
        raise ValueError('joint parent feature pipeline provenance differs')
    for key in ('candidate_config_sha256', 'candidate_manifest_sha256', 'candidate_summary_sha256',
        'candidate_audit_sha256', 'candidate_scalar_sha256', 'candidate_identity_hash',
        'candidate_prepared_events_sha256', 'candidate_event_banks_sha256', 'target_case_ids_sha256',
        'candidate_source_provenance', 'candidate_tokenization_rule', 'candidate_scoring_backend',
        'candidate_precision', 'parent_confidence_measurement', 'parent_confidence_measurement_backend'):
        if manifest.get(key) != ancestor_manifest[key]:
            raise ValueError('joint parent original scalar provenance differs: '+key)
    if (review.get('status') != 'complete_exploratory' or review.get('config_hash') != digest(effective)
            or review.get('feature_manifest') != manifest
            or review.get('feature_table_sha256') != manifest['sha256']
            or review.get('feature_manifest_sha256') != effective['feature_manifest_sha256']
            or review.get('analysis_plan') != generic._plan(effective)
            or review.get('n') != manifest['n'] or review.get('templates') != manifest['groups']
            or any(review.get(key) is not False for key in ('generated_holdouts_opened', 'mechanism_C_fitted'))):
        raise ValueError('completed joint prediction/manifest/protocol identity differs')
    for value in (spec, effective, producer):
        if any(not config.get(key) or config[key] != value.get(key) for key in ('model', 'model_revision')):
            raise ValueError('stress parent checkpoint differs')
    if any(manifest.get(field) != config[key] for key, field in
           (('model', 'source_model'), ('model_revision', 'source_model_revision'))):
        raise ValueError('stress parent feature checkpoint differs')
    protected = [config['source_pipeline_config'], config['source_pipeline_receipt'],
        effective['feature_table'], effective['feature_manifest'], effective['review_artifact'],
        out/'collection_config.json', out/'effective_config.json', producer['source_pipeline_config'],
        producer['source_pipeline_receipt'], ancestor['feature_table'], ancestor['feature_manifest']]
    for artifact in review.get('artifacts', {}).values():
        _discovery_response_path(artifact['path']); protected.append(artifact['path'])
    if any(one_token._same_path(config[key], path) for key in ('feature_table', 'feature_manifest') for path in protected):
        raise ValueError('stress feature outputs cannot replace parent/source artifacts')
    return effective, manifest, receipt


def _metadata(config):
    """Complete both independent metadata chains before any bulk payload read."""
    from . import stress_measurement as measurement
    if tuple(measurement.SCALARS) != SCALARS:
        raise ValueError('stress scalar whitelist differs from fixed prediction profile')
    _discovery_declaration(config)
    for key in ('stress_config', 'feature_table', 'feature_manifest'):
        _discovery_response_path(config[key])
    for key in ('stress_config_sha256', 'stress_manifest_sha256', 'stress_summary_sha256', 'stress_audit_sha256'):
        parent._pin(config.get(key), key)
    effective, manifest, receipt = _parent_metadata(config)
    sc = one_token._object(config['stress_config'], config['stress_config_sha256'], 'stress measurement config')
    if (sc.get('case_limit') is not None or sc.get('max_new_tokens') != 32
            or any(sc.get(key) != config[key] for key in ('model', 'model_revision'))
            or sc.get('source_config_sha256') != manifest['source_config_sha256']):
        raise ValueError('matching complete distinct-query stress configuration required')
    measurement.metadata_preflight(sc)
    stage = Path(sc['run_dir'])/'stress_measurement'
    pinned = {key: one_token._object(stage/(key+'.json'), config['stress_'+key+'_sha256'])
              for key in ('manifest', 'summary', 'audit')}
    completed = measurement.completed_metadata(sc)
    if any(pinned[key] != completed[key] for key in pinned):
        raise ValueError('stress metadata changed after pinned completion validation')
    qa, summary, audit = completed['preparation'], completed['summary'], completed['audit']
    provenance = qa.get('source_provenance', {})
    if any(provenance.get(key) != manifest[key] for key in one_token.SOURCE_KEYS):
        raise ValueError('stress original-program/source provenance differs from parent')
    if (summary.get('source_provenance') != provenance or summary.get('evaluated') != manifest['n']
            or summary.get('planned') != manifest['n'] or audit.get('evaluated') != manifest['n']
            or summary.get('case_ids_sha256') != manifest['target_case_ids_sha256']
            or qa.get('case_ids_sha256') != manifest['target_case_ids_sha256']
            or summary.get('nominal_distinct_queries_per_target') != 1 or summary.get('max_new_tokens') != 32):
        raise ValueError('stress complete prompt bank/query budget differs from parent targets')
    protected = [config['stress_config'], sc['prepared_cases'], sc['preflight_result'],
        *[stage/name for name in ('manifest.json', 'summary.json', 'audit.json', 'runtime.json', 'scalars.jsonl', 'responses.jsonl')]]
    if any(one_token._same_path(config[key], path) for key in ('feature_table', 'feature_manifest') for path in protected):
        raise ValueError('stress feature outputs cannot replace measurement artifacts')
    return effective, manifest, receipt, sc, completed


def augment_rows(rows, cases, scalars):
    """Add exactly five distinct-query scalars without changing parent values."""
    from . import discovery_prediction as generic, stress_measurement as measurement
    rows, _ = generic._rows(rows); cases = list(cases); scalars = list(scalars)
    if (len({case['id'] for case in cases}) != len(cases) or len({row['id'] for row in scalars}) != len(scalars)
            or {row['id'] for row in rows} != {case['id'] for case in cases}
            or {row['id'] for row in rows} != {row['id'] for row in scalars}):
        raise ValueError('complete identical parent/stress input/scalar ID coverage required')
    by_case = {case['id']: case for case in cases}; by_scalar = {row['id']: row for row in scalars}
    columns = set(sum(parent.feature_contract()[1].values(), []))
    case_fields = set(one_token.confidence.CASE_FIELDS)
    hash_fields = ('prompt_sha256', 'input_token_ids_sha256', 'original_prompt_sha256', 'original_input_token_ids_sha256')
    scalar_fields = case_fields|{'measurement_role', *hash_fields, *SCALARS}
    mapping = {'id': 'id', 'base_id': 'base_id', 'template_id': 'template_id', 'original_split': 'split',
        'condition': 'condition', 'query_role': 'query_role', 'available_bindings': 'available_bindings',
        'lexical_realization': 'lexical_realization'}
    output = []
    for row in rows:
        case, scalar = by_case[row['id']], by_scalar[row['id']]
        if (set(row) != set(one_token.ROW_METADATA)|{'label', 'features'} or type(row['label']) is not int
                or set(row['features']) != columns or set(scalar) != scalar_fields
                or scalar['measurement_role'] != measurement.ROLE
                or any(row[left] != case[right] for left, right in mapping.items())
                or any(scalar[key] != case[key] for key in (*case_fields, *hash_fields))):
            raise ValueError('stress scalar whitelist/design/source prompt identity differs from parent')
        original = case.get('original_input_token_ids')
        if (not isinstance(original, list) or not original or any(type(v) is not int or v < 0 for v in original)
                or digest(original) != case['original_input_token_ids_sha256']
                or digest(case['input_token_ids']) != case['input_token_ids_sha256']
                or case['original_input_token_ids_sha256'] == case['input_token_ids_sha256']
                or case['original_prompt_sha256'] == case['prompt_sha256']
                or row['features']['prompt_tokens'] != len(original)
                or row['features']['updates'] != case['updates']
                or row['features']['tail_after'] != int(case['tail_placement'] == 'after')
                or row['features']['misleading'] != int(case['condition'] == 'misleading')
                or row['features']['query_saved'] != int(case['query_role'] == 'saved')
                or row['features']['lexical_one'] != case['lexical_realization']):
            raise ValueError('stress exact original prompt tokens/target design differs from parent')
        if (any(type(scalar[key]) is not int for key in SCALARS)
                or scalar['valid'] not in (0, 1) or scalar['response_chars'] < 0
                or not 0 <= scalar['output_tokens'] <= 32
                or scalar['prediction_abs'] != abs(scalar['prediction_value'])
                or not scalar['valid'] and (scalar['prediction_value'] != 0 or scalar['prediction_abs'] != 0)):
            raise ValueError('stress raw response scalar numerical/invalid-value contract differs')
        output.append({**{key: row[key] for key in one_token.ROW_METADATA}, 'label': row['label'],
            'features': {**row['features'], **{column: scalar[key] for key, column in zip(SCALARS, STRESS_COLUMNS)}}})
    for names in predictor_columns().values():
        generic._matrix(output, names)
    return output


def collect(config):
    """Join fully audited additional responses after both metadata chains pass."""
    from . import discovery_prediction as generic, stress_measurement as measurement
    from .registry import code_identity
    effective, manifest, receipt, sc, completed = _metadata(config)
    stage = Path(sc['run_dir'])/'stress_measurement'
    summary, audit, qa = completed['summary'], completed['audit'], completed['preparation']
    checked, rows = generic.load_features(effective)
    if checked != manifest or generic._reuse(effective, manifest) is None:
        raise ValueError('parent feature metadata/completed fitting changed')
    for path, expected, name in ((stage/'scalars.jsonl', summary['scalars_sha256'], 'stress scalars'),
            (sc['prepared_cases'], summary['prepared_cases_sha256'], 'stress prepared inputs')):
        one_token._pinned(path, expected, name)
    # This reads the NEW extra response bank to verify its raw scalar parsing.
    # Original target response payloads are never opened.
    if measurement.audit(sc) != audit:
        raise ValueError('stress repeated audit differs from pinned completed audit')
    prepared, cases = measurement.inputs(sc, expected_source=qa['source_sha256'])
    if prepared != qa:
        raise ValueError('stress prepared input metadata changed after completion validation')
    one_token._pinned(stage/'scalars.jsonl', summary['scalars_sha256'], 'stress scalars')
    joined = augment_rows(rows, cases, read_jsonl(stage/'scalars.jsonl'))
    if (len(joined) != manifest['n'] or len({row['template_id'] for row in joined}) != manifest['groups']
            or digest([row['id'] for row in joined]) != manifest['target_case_ids_sha256']):
        raise ValueError('stress joined target/group coverage differs')
    payload = ''.join(json.dumps(row, sort_keys=True)+'\n' for row in joined).encode()
    result = {**manifest, 'status': 'passed', 'profile': PROFILE, 'evaluation_role': ROLE,
        'feature_table': config['feature_table'], 'sha256': hashlib.sha256(payload).hexdigest(),
        'columns': feature_contract()[1], 'predictor_columns': predictor_columns(),
        'predictor_access': predictor_access(), 'config_hash': digest(config), 'analysis_source': code_identity(),
        'source_pipeline_config_sha256': config['source_pipeline_config_sha256'],
        'source_pipeline_receipt_sha256': config['source_pipeline_receipt_sha256'],
        'parent_effective_config_sha256': receipt['effective_config']['sha256'],
        'parent_feature_manifest_sha256': effective['feature_manifest_sha256'],
        'parent_feature_table_sha256': effective['feature_table_sha256'],
        **{key: config[key] for key in ('stress_config_sha256', 'stress_manifest_sha256', 'stress_summary_sha256', 'stress_audit_sha256')},
        'stress_scalars_sha256': summary['scalars_sha256'], 'stress_responses_sha256': summary['responses_sha256'],
        'stress_prepared_cases_sha256': summary['prepared_cases_sha256'], 'stress_source_provenance': qa['source_provenance'],
        'stress_measurement': measurement.MEASUREMENT, 'stress_identity_hash': audit['identity_hash'],
        'parent_scientific_access_cost': manifest['scientific_access_cost'],
        'scientific_access_cost': {'old_twenty_three_tiers': 'unchanged; separately declared per tier',
            'new_stress_tiers': {'next_token_target_prefills_per_target': 1,
                'next_token_measurement_dtype': 'bfloat16', 'distinct_stress_queries_per_target': 1,
                'stress_max_new_tokens_per_query': 32, 'candidate_event_features': False,
                'neutral_and_oracle_access': 'unchanged and separately declared per tier'}},
        'old_twenty_three_feature_sets_and_labels_unchanged': True,
        'all_parent_feature_bytes_unchanged': False,
        'original_target_response_features': False, 'original_target_correctness_features': False,
        'stress_response_identity_features': True, 'stress_correctness_features': False,
        'original_target_raw_response_payload_reads': 0, 'stress_response_payload_read_by_audit': True,
        'new_queries_during_feature_collection': 0, 'additional_stress_queries_in_bank': len(joined),
        'label_counts': {str(key): value for key, value in Counter(row['label'] for row in joined).items()},
        'generated_holdouts_opened': False, 'mechanism_C_fitted': False, 'limitation': LIMITATION}
    # These inherited unqualified counters would obscure the deliberate NEW
    # extra-query responses, so replace them with the explicit counters above.
    result.pop('raw_response_payload_reads', None)
    result.pop('new_language_model_queries', None)
    data = {Path(config['feature_table']): payload,
        Path(config['feature_manifest']): (json.dumps(result, sort_keys=True, indent=2)+'\n').encode()}
    for path, content in data.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError('immutable stress feature artifact differs: '+str(path))
    for path, content in data.items():
        immutable(path, content)
    return result


def validate(spec):
    _discovery_declaration(spec)
    if spec.get('protocol') != protocol():
        raise ValueError('fixed stress prediction protocol differs')
    for key in ('source_pipeline_config', 'source_pipeline_receipt', 'stress_config', 'output_dir', 'report'):
        _discovery_response_path(spec[key])
    for key in ('source_pipeline_config_sha256', 'source_pipeline_receipt_sha256', 'stress_config_sha256'):
        parent._pin(spec.get(key), key)
    source = one_token._object(spec['source_pipeline_config'], spec['source_pipeline_config_sha256'])
    parent.validate(source)
    stress = one_token._object(spec['stress_config'], spec['stress_config_sha256'])
    if (any(spec.get(key) != source.get(key) or spec.get(key) != stress.get(key) for key in ('model', 'model_revision'))
            or stress.get('case_limit') is not None or stress.get('max_new_tokens') != 32):
        raise ValueError('matching complete fixed-budget stress bank required')
    out = Path(spec['output_dir']).resolve()
    for path in (source['output_dir'], stress['run_dir']):
        source_out = Path(path).resolve()
        if out == source_out or source_out in out.parents or out in source_out.parents:
            raise ValueError('distinct nonoverlapping stress pipeline output directory required')
    return source, stress


def fit(spec):
    from . import discovery_prediction as generic, stress_measurement as measurement
    _, sc = validate(spec)
    measurement.completed_metadata(sc)
    stage = Path(sc['run_dir'])/'stress_measurement'; out = Path(spec['output_dir'])
    keys = ('model', 'model_revision', 'source_pipeline_config', 'source_pipeline_config_sha256',
        'source_pipeline_receipt', 'source_pipeline_receipt_sha256', 'stress_config', 'stress_config_sha256')
    collector = {key: spec[key] for key in keys}
    collector.update({f'stress_{key}_sha256': sha(stage/(key+'.json')) for key in ('manifest', 'summary', 'audit')})
    collector.update(feature_table=str(out/'inputs/features.jsonl'), feature_manifest=str(out/'inputs/features.manifest.json'))
    _metadata(collector)
    collector_path = out/'collection_config.json'; _json(collector_path, collector)
    metadata = collect(collector)
    effective = {key: value for key, value in spec['protocol'].items() if key != 'comparisons'}
    effective.update(model=spec['model'], model_revision=spec['model_revision'],
        feature_table=collector['feature_table'], feature_table_sha256=metadata['sha256'],
        feature_manifest=collector['feature_manifest'], feature_manifest_sha256=sha(collector['feature_manifest']),
        collection_config=str(collector_path), output_dir=str(out/'cv'), run_dir=str(out/'cv'),
        review_artifact=str(out/'review_v1.json'), report=spec['report'])
    config = out/'effective_config.json'; _json(config, effective)
    generic.run(effective)
    result = dict(status='complete_exploratory', config_hash=digest(spec), protocol_hash=digest(protocol()),
        collection_config=dict(path=str(collector_path), sha256=sha(collector_path)),
        effective_config=dict(path=str(config), sha256=sha(config)),
        review=dict(path=effective['review_artifact'], sha256=sha(effective['review_artifact'])),
        generated_holdouts_opened=False, mechanism_C_fitted=False, model_loading=False)
    _json(out/'pipeline_review_v1.json', result)
    return result


def compare(spec):
    from . import discovery_prediction as generic, confidence_review
    _discovery_declaration(spec)
    if spec.get('protocol') != protocol():
        raise ValueError('fixed stress comparison protocol differs')
    for key in ('output_dir', 'comparison_report', 'decision_report', 'baseline_comparison', 'figure_png', 'figure_svg'):
        _discovery_response_path(spec[key])
    runs = {}
    for name, binding in spec['runs'].items():
        run_spec = one_token._object(binding['config'], binding['sha256']); validate(run_spec)
        out = Path(run_spec['output_dir']); receipt = one_token._object(out/'pipeline_review_v1.json')
        if (receipt.get('status') != 'complete_exploratory' or receipt.get('config_hash') != digest(run_spec)
                or receipt.get('protocol_hash') != digest(protocol())):
            raise ValueError('completed matching stress model pipeline required')
        path = out/'effective_config.json'
        if receipt.get('effective_config') != {'path': str(path), 'sha256': sha(path)}:
            raise ValueError('stress effective fitting configuration changed')
        effective = one_token._object(path); artifact = effective['review_artifact']
        _discovery_response_path(artifact)
        if receipt.get('review') != {'path': artifact, 'sha256': sha(artifact)}:
            raise ValueError('completed stress fitting review changed')
        runs[name] = dict(config=str(path), sha256=sha(path))
    if len(runs) != 2:
        raise ValueError('two fixed checkpoint reviews required')
    out = Path(spec['output_dir'])
    comparison = dict(runs=runs, comparison_artifact=str(out/'comparison_v1.json'), report=spec['comparison_report'])
    _json(out/'comparison_config.json', comparison); generic.compare(comparison)
    rendering = dict(comparison_profile=PROFILE, comparison=comparison['comparison_artifact'],
        comparison_sha256=sha(comparison['comparison_artifact']), baseline_comparison=spec['baseline_comparison'],
        baseline_comparison_sha256=spec['baseline_comparison_sha256'], figure_png=spec['figure_png'],
        figure_svg=spec['figure_svg'], review_artifact=str(out/'anchor_figure_review_v1.json'))
    _json(out/'review_config.json', rendering); confidence_review.run(rendering)
    checked = one_token._object(rendering['review_artifact'])
    pairs = set(PRIMARY_PAIRS+JOINT_PAIRS+tuple((a, s) for a, _, _, s in PAIRED_TIERS))
    lines = ['# Distinct ungraded stress-query prediction controls', '', LIMITATION, '',
        '| Checkpoint | Contrast | Left Brier | Stress Brier | Improvement [conditional 95%] | Left log loss | Stress log loss |',
        '|---|---|---:|---:|---|---:|---:|']
    for name, binding in runs.items():
        effective = one_token._object(binding['config'], binding['sha256'])
        review = one_token._object(effective['review_artifact'])
        metrics = next(row['metrics'] for row in review['per_seed_and_ensemble'] if row['scope'] == 'ensemble')
        rows = [row for row in review['contrasts'] if row['scope'] == 'ensemble' and (row['left'], row['right']) in pairs]
        if len(rows) != 15:
            raise ValueError('all fifteen fixed next-token/joint/source-to-stress contrasts required')
        for row in rows:
            left, right = metrics[row['left']], metrics[row['right']]
            delta = row['brier_score']; low, high = delta['exploratory_template_bootstrap_95']
            lines.append(f"| {name} | {row['left']} → {row['right']} | {left['brier_score']:.6f} | {right['brier_score']:.6f} | {delta['mean']:+.6f} [{low:+.6f}, {high:+.6f}] | {left['log_loss']:.6f} | {right['log_loss']:.6f} |")
    count = sum(value['anchors']['probability_values_compared'] for value in checked['models'].values())
    lines += ['', f'All {count:,} parent-tier OOF probability values reproduce exactly, as do every saved parent fit, normalizer, penalty, inner curve, group assignment and fallback record.', '',
        'All 28 tiers and 70 contrasts, fixed seeds, calibration bins and descriptive cells remain in the full comparison and per-checkpoint reports. Original target outcomes were already consumed discovery labels; no untouched final score or mechanism C was fitted.', '']
    immutable(spec['decision_report'], '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', complete=True, config_hash=digest(spec),
        comparison=rendering['comparison'], comparison_sha256=rendering['comparison_sha256'],
        anchor_review=rendering['review_artifact'], anchor_review_sha256=sha(rendering['review_artifact']),
        parent_probability_values_reproduced=count, decision_report=spec['decision_report'],
        generated_holdouts_opened=False, mechanism_C_fitted=False, model_loading=False)
    _json(out/'pipeline_review_v1.json', result)
    return result
