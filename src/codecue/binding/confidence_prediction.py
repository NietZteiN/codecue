"""Discovery-only joins of pinned capacity controls and label-free confidence.

Both metadata chains are checked before a feature/scalar payload is opened. This
collector never loads a model or reads raw target responses. Existing labels are
copied only from the pinned controls table, never inferred from confidence.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from . import confidence, discovery_controls as controls
from .datasets import digest, read_jsonl
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable, sha

PROFILE = 'confidence_access_v1'
ROLE = 'discovery_failure_prediction_confidence_v1'
STATISTICS = confidence.STATISTICS[:-1]
CONFIDENCE_COLUMNS = tuple('confidence_'+name for name in STATISTICS)
PAIRED_TIERS = (
    ('A_input', 'B_input_confidence'),
    ('A_interactions', 'B_interactions_confidence'),
    ('A_interactions_neutral_raw', 'B_interactions_neutral_raw_confidence'),
    ('A_interactions_oracle_neutral_raw', 'B_interactions_oracle_neutral_raw_confidence'),
    ('A_interactions_oracle_neutral_scored', 'B_interactions_oracle_neutral_scored_confidence'),
)
SOURCE_KEYS = ('source_config_sha256', 'source_dataset_sha256', 'source_identity_hash',
    'source_model', 'source_model_revision', 'source_prepared_sha256',
    'source_audit_sha256', 'original_source_sha256', 'source_responses_sha256')
ROW_METADATA = ('id', 'reference_id', 'template_id', 'base_id', 'original_split',
                'condition', 'query_role', 'available_bindings', 'lexical_realization')
LIMITATION = (
    'Exploratory nested grouped cross-validation on previously consumed discovery '
    'data. Scalar next-token confidence is allowed in explicitly labelled B tiers; '
    'no mechanism C or unfamiliar-program/final confirmation is claimed. The new '
    'Transformers BF16 prefill measurement backend differs from the original vLLM '
    'outcome backend. Confidence is next-token sign/format confidence, not complete '
    'integer-answer confidence. Its scientific access cost is one target prefill '
    'per target, even when cached: no target response, generated token, target '
    'correctness or token identity is a feature. Raw neutral tiers separately use '
    'one distinct reference query; scored tiers also require reference correctness; '
    'source-oracle tiers separately receive the source oracle value. Adding neutral '
    'correctness to source-oracle plus raw-neutral features adds an encoding of '
    'existing information, not a new observation. Repeated partition seeds reuse '
    'the same targets, not independent replications. Template bootstrap intervals '
    'condition on saved OOF probabilities without refitting or multiplicity adjustment.'
)


def predictor_columns(config=None):
    columns = controls.predictor_columns()
    columns.update({right: columns[left]+list(CONFIDENCE_COLUMNS) for left, right in PAIRED_TIERS})
    _profile_declarations(config, columns)
    return columns


def predictor_access():
    result = {}
    for name, columns in predictor_columns().items():
        result[name] = {'neutral_queries': int('neutral_valid' in columns),
            'source_oracle_value': 'oracle_answer_value' in columns,
            'reference_correctness': 'neutral_failure' in columns,
            'target_prefills_per_target': int(CONFIDENCE_COLUMNS[0] in columns),
            'generated_target_tokens': 0, 'target_correctness_feature': False}
    return result


def _profile_declarations(config, columns):
    if config is None:
        return
    expected = {'seeds': [17, 29, 43], 'outer_folds': 6, 'inner_folds': 5,
                'l2_grid': [.1, 1., 10., 100.]}
    if any(key in config and config[key] != value for key, value in expected.items()):
        raise ValueError('confidence profile retains the fixed existing grouped CV protocol')
    if config.get('feature_information_contract', columns) != columns:
        raise ValueError('confidence predictor feature declaration differs from the fixed profile')
    if 'predictor_access' in config and config['predictor_access'] != predictor_access():
        raise ValueError('confidence predictor access declaration differs from fixed scientific costs')


def predictor_comparisons(config=None):
    from .discovery_prediction import predictor_comparisons as base_comparisons
    predictor_columns(config)
    return base_comparisons({'feature_profile': controls.PROFILE})+PAIRED_TIERS+(
        ('B_input_confidence', 'B_interactions_confidence'),
        ('B_interactions_confidence', 'B_interactions_neutral_raw_confidence'),
        ('B_interactions_oracle_neutral_raw_confidence', 'B_interactions_oracle_neutral_scored_confidence'),
    )


def feature_contract(config=None):
    from .discovery_prediction import _feature_contract
    predictor_columns(config)
    _, contract = _feature_contract({'feature_profile': controls.PROFILE})
    return ROLE, {**contract, 'confidence': list(CONFIDENCE_COLUMNS)}


def _object(path, expected=None, description='metadata'):
    path = Path(path)
    _discovery_response_path(path)
    if not path.is_file() or path.suffix != '.json' or path.stat().st_size > 8*1024**2:
        raise ValueError('bounded discovery JSON '+description+' required')
    if expected is not None:
        _pinned(path, expected, description)
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(description+' must be an object')
    _discovery_declaration(value)
    return value


def _pinned(path, expected, description):
    if not isinstance(expected, str) or len(expected) != 64 or sha(path) != expected:
        raise ValueError(description+' checksum changed or is unpinned')


def _same_path(left, right):
    return Path(left).resolve() == Path(right).resolve()


def _metadata(config):
    """Validate both full discovery chains without reading/hash-opening payloads."""
    from .competition import ROLE as source_role
    from .discovery_prediction import _feature_contract
    _discovery_declaration(config)
    for key in ('controls_config', 'confidence_config', 'feature_table', 'feature_manifest'):
        _discovery_response_path(config[key])
    if (Path(config['feature_table']).suffix != '.jsonl' or Path(config['feature_manifest']).suffix != '.json'
            or _same_path(config['feature_table'], config['feature_manifest'])):
        raise ValueError('declare distinct JSONL feature and JSON manifest output paths')
    for key in ('controls_config_sha256', 'controls_feature_manifest_sha256',
                'controls_feature_table_sha256', 'confidence_config_sha256',
                'confidence_manifest_sha256', 'confidence_summary_sha256', 'confidence_audit_sha256'):
        if not isinstance(config.get(key), str) or len(config[key]) != 64:
            raise ValueError('explicit pinned metadata/payload checksum required: '+key)
    parent = _object(config['controls_config'], config['controls_config_sha256'], 'controls configuration')
    if parent.get('feature_profile') != controls.PROFILE:
        raise ValueError('completed capacity_oracle_v1 controls required')
    for key in ('feature_manifest', 'feature_table'):
        _discovery_response_path(parent[key])
    if parent.get('feature_manifest_sha256') != config['controls_feature_manifest_sha256']:
        raise ValueError('controls feature manifest pin differs from source configuration')
    features = _object(parent['feature_manifest'], config['controls_feature_manifest_sha256'], 'controls manifest')
    role, columns = _feature_contract(parent)
    if (features.get('status') != 'passed' or features.get('evaluation_role') != role
            or features.get('profile') != controls.PROFILE or features.get('columns') != columns
            or features.get('predictor_columns') != controls.predictor_columns()
            or parent.get('feature_information_contract', controls.predictor_columns()) != controls.predictor_columns()
            or features.get('generated_holdouts_opened') is not False
            or features.get('target_outcomes_used_as_features') is not False
            or features.get('mechanism_C_fitted') is not False
            or features.get('target_metadata_labels_references_unchanged') is not True
            or features.get('sha256') != config['controls_feature_table_sha256']
            or parent.get('feature_table_sha256') != features.get('sha256')
            or not _same_path(features.get('feature_table', ''), parent['feature_table'])):
        raise ValueError('pinned completed discovery controls feature contract differs')
    for key, field in (('model', 'source_model'), ('model_revision', 'source_model_revision')):
        if not config.get(key) or config[key] != parent.get(key) or config[key] != features.get(field):
            raise ValueError('controls checkpoint identity differs')
    cc = _object(config['confidence_config'], config['confidence_config_sha256'], 'confidence configuration')
    protected = [config['controls_config'], config['confidence_config'], parent['feature_table'],
        parent['feature_manifest'], cc['prepared_cases'], cc['preflight_result'],
        *[str(Path(cc['run_dir'])/'confidence'/name) for name in
          ('confidence.jsonl', 'manifest.json', 'summary.json', 'audit.json', 'runtime.json')]]
    if any(_same_path(config[key], path) for key in ('feature_table', 'feature_manifest') for path in protected):
        raise ValueError('confidence feature outputs cannot replace source artifacts')
    if cc.get('case_limit') is not None or any(cc.get(key) != config[key] for key in ('model', 'model_revision')):
        raise ValueError('complete matching checkpoint confidence bank required, not a smoke subset')
    original = confidence._source(cc)  # metadata only; never prepare/audit original responses
    for key in ('dataset', 'prepared_cases', 'preflight_result', 'run_dir'):
        _discovery_response_path(original[key])
    if cc['source_config_sha256'] != features.get('source_config_sha256'):
        raise ValueError('confidence and controls original source configurations differ')
    dataset_manifest = _object(Path(original['dataset']).with_suffix('.manifest.json'))
    stage = Path(cc['run_dir'])/'confidence'
    manifest = _object(stage/'manifest.json', config['confidence_manifest_sha256'], 'confidence manifest')
    summary = _object(stage/'summary.json', config['confidence_summary_sha256'], 'confidence summary')
    audit = _object(stage/'audit.json', config['confidence_audit_sha256'], 'confidence audit')
    qa = _object(cc['preflight_result'])
    identity = manifest.get('identity', {})
    if (manifest.get('status') != 'complete' or manifest.get('identity_hash') != digest(identity)
            or identity.get('config') != cc or identity.get('config_hash') != digest(cc)
            or identity.get('stage') != 'confidence'
            or identity.get('dataset_manifest') != dataset_manifest
            or dataset_manifest.get('status') != 'validated'
            or dataset_manifest.get('evaluation_role') != source_role
            or dataset_manifest.get('sha256') != features.get('source_dataset_sha256')
            or identity.get('model_revision') != cc['model_revision']
            or identity.get('tokenizer_revision') != cc['tokenizer_revision']):
        raise ValueError('completed confidence manifest/source identity differs')
    for value in (qa, summary, audit):
        if (value.get('measurement') != confidence.MEASUREMENT
                or value.get('generated_holdouts_opened') is not False
                or value.get('target_outcomes_read') is not False or value.get('generated_tokens') != 0
                or value.get('model') != config['model'] or value.get('model_revision') != config['model_revision']):
            raise ValueError('confidence checkpoint, measurement or discovery-only access contract differs')
    if (qa.get('status') != 'passed' or qa.get('evaluation_role') != confidence.ROLE
            or qa.get('config_hash') != digest(cc) or qa.get('smoke_subset') is not False
            or qa.get('source_sha256') != identity.get('code', {}).get('source_sha256')
            or qa.get('source_config_sha256') != cc['source_config_sha256']
            or qa.get('tokenizer_revision') != cc['tokenizer_revision']
            or qa.get('eos_token_ids') != cc['eos_token_ids']
            or qa.get('upstream_identity') != features.get('source_identity_hash')
            or qa.get('oracle_fields_exported') is not False
            or audit.get('preparation') != qa or audit.get('status') != 'passed'
            or audit.get('complete') is not True or audit.get('identity_hash') != manifest['identity_hash']):
        raise ValueError('complete pinned confidence audit/preparation chain differs')
    for key in SOURCE_KEYS:
        if not features.get(key) or qa.get('source_provenance', {}).get(key) != features[key]:
            raise ValueError('controls/confidence original source provenance differs: '+key)
    n = features.get('n')
    if (type(n) is not int or n < 1 or type(features.get('groups')) is not int or features['groups'] < 1
            or qa.get('cases') != n or audit.get('evaluated') != n
            or summary.get('status') != 'complete' or summary.get('complete') is not True
            or summary.get('evaluation_role') != confidence.ROLE or summary.get('smoke_subset') is not False
            or any(value.get('evaluated') != n or value.get('planned') != n for value in (manifest, summary))
            or summary.get('target_prefill_evaluations') != n
            or summary.get('statistics') != list(confidence.STATISTICS)
            or summary.get('attention_backend') != cc.get('attention_backend', 'sdpa')
            or summary.get('batch_size') != cc.get('batch_size', 32)
            or summary.get('oracle_fields_exported') is not False
            or summary.get('prepared_cases_sha256') != qa.get('prepared_cases_sha256')
            or summary.get('case_ids_sha256') != qa.get('case_ids_sha256')
            or any(value.get('confidence_sha256') != summary.get('confidence_sha256') for value in (manifest, audit))
            or any(not isinstance(value, str) or len(value) != 64 for value in
                (summary.get('confidence_sha256'), qa.get('prepared_cases_sha256'),
                 qa.get('case_ids_sha256'), qa.get('source_sha256')))):
        raise ValueError('complete confidence coverage, payload pins or summary differ')
    origin_stage = Path(original['run_dir'])/'checkpoint_suite'
    origin = _object(origin_stage/'manifest.json')
    origin_identity = origin.get('identity', {})
    origin_audit = _object(origin_stage/'audit.json', features['source_audit_sha256'], 'original discovery audit')
    origin_qa = _object(original['preflight_result'])
    if (origin.get('status') != 'complete' or origin.get('identity_hash') != digest(origin_identity)
            or origin.get('identity_hash') != features['source_identity_hash']
            or origin_identity.get('config') != original
            or origin_identity.get('dataset_manifest') != dataset_manifest
            or origin_identity.get('code', {}).get('source_sha256') != features['original_source_sha256']
            or origin.get('responses_sha256') != features['source_responses_sha256']
            or origin_audit.get('status') != 'passed' or origin_audit.get('complete') is not True
            or origin_audit.get('identity_hash') != origin['identity_hash']
            or origin_audit.get('model') != config['model'] or origin_audit.get('revision') != config['model_revision']
            or origin_audit.get('evaluated') != origin_qa.get('cases')
            or origin_qa.get('cases') != dataset_manifest.get('rows')
            or origin_audit.get('preflight') != origin_qa
            or origin_qa.get('status') != 'passed' or origin_qa.get('config_hash') != digest(original)
            or origin_qa.get('prepared_cases_sha256') != features['source_prepared_sha256']
            or origin_qa.get('source_sha256') != features['original_source_sha256']):
        raise ValueError('original discovery/prepared identity does not bind both source chains')
    return parent, features, cc, qa, summary, audit


def augment_rows(rows, cases, scalars):
    """Join exact IDs/design/prompt tokens; only four whitelisted scalars are added."""
    from .discovery_prediction import _rows, _matrix, _feature_contract
    rows, _ = _rows(rows)
    cases = list(cases);scalars = list(scalars)
    if (len({row['id'] for row in cases}) != len(cases)
            or len({row['id'] for row in scalars}) != len(scalars)
            or {row['id'] for row in rows} != {row['id'] for row in cases}
            or {row['id'] for row in rows} != {row['id'] for row in scalars}):
        raise ValueError('complete identical feature/prepared/scalar target ID coverage required')
    by_case = {row['id']: row for row in cases};by_scalar = {row['id']: row for row in scalars}
    confidence.validate_rows(cases, [by_scalar[row['id']] for row in cases])
    _, old_contract = _feature_contract({'feature_profile': controls.PROFILE})
    expected = set(sum(old_contract.values(), []))
    result = []
    mapping = {'id': 'id', 'base_id': 'base_id', 'template_id': 'template_id',
        'original_split': 'split', 'condition': 'condition', 'lexical_realization': 'lexical_realization',
        'available_bindings': 'available_bindings', 'query_role': 'query_role'}
    for row in rows:
        if set(row) != set(ROW_METADATA)|{'features', 'label', 'target_invalid'}:
            raise ValueError('controls row has unregistered target response/score fields')
        if type(row['label']) is not int or type(row['target_invalid']) is not bool or set(row['features']) != expected:
            raise ValueError('controls feature/label whitelist differs; target scores cannot enter features')
        case = by_case[row['id']];values = row['features']
        allowed_case = set(confidence.CASE_FIELDS)|{'prompt', 'input_token_ids', 'prompt_sha256',
            'input_token_ids_sha256', 'evaluation_role'}
        if (set(case) != allowed_case or case['evaluation_role'] != confidence.ROLE
                or not isinstance(case['prompt'], str) or not case['prompt']
                or not isinstance(case['input_token_ids'], list) or not case['input_token_ids']
                or any(type(token) is not int or token < 0 for token in case['input_token_ids'])
                or case['updates'] not in (1, 3) or case['lexical_realization'] not in (0, 1)):
            raise ValueError('exact confidence prepared input role/schema differs')
        if (any(row[left] != case[right] for left, right in mapping.items())
                or values['updates'] != case['updates']
                or case['tail_placement'] not in ('before', 'after')
                or values['tail_after'] != int(case['tail_placement'] == 'after')
                or values['misleading'] != int(case['condition'] == 'misleading')
                or values['query_saved'] != int(case['query_role'] == 'saved')
                or values['lexical_one'] != case['lexical_realization']
                or values['available_bindings'] != case['available_bindings']
                or values['prompt_tokens'] != len(case['input_token_ids'])
                or digest(case['prompt']) != case['prompt_sha256']
                or digest(case['input_token_ids']) != case['input_token_ids_sha256']):
            raise ValueError('feature and exact confidence prompt/design provenance differ')
        added = {column: by_scalar[row['id']][name] for name, column in zip(STATISTICS, CONFIDENCE_COLUMNS)}
        result.append({**{key: row[key] for key in ROW_METADATA}, 'label': row['label'],
                       'features': {**values, **added}})
    for columns in predictor_columns().values():
        _matrix(result, columns)
    return result


def collect(config):
    """Export discovery confidence features after all metadata guards have passed."""
    from .discovery_prediction import load_features
    from .registry import code_identity
    parent, metadata, cc, qa, summary, audit = _metadata(config)
    scalar_path = Path(cc['run_dir'])/'confidence/confidence.jsonl'
    # Verify all three payload pins before re-audit/JSONL parsing opens any one.
    _pinned(parent['feature_table'], config['controls_feature_table_sha256'], 'controls feature payload')
    _pinned(cc['prepared_cases'], qa['prepared_cases_sha256'], 'confidence prepared prompt payload')
    _pinned(scalar_path, summary['confidence_sha256'], 'confidence scalar payload')
    # Re-audit the confidence scalar run only after both metadata chains pass.
    if confidence.audit(cc) != audit:
        raise ValueError('confidence re-audit differs from its pinned completed audit')
    checked, rows = load_features(parent)
    if checked != metadata:
        raise ValueError('controls feature metadata changed after validation')
    prepared, cases = confidence.inputs(cc, qa['source_sha256'])
    if prepared != qa:
        raise ValueError('confidence preparation changed after validation')
    _pinned(scalar_path, summary['confidence_sha256'], 'confidence scalar payload')
    joined = augment_rows(rows, cases, read_jsonl(scalar_path))
    if (len(joined) != metadata['n'] or len({row['template_id'] for row in joined}) != metadata['groups']
            or digest([row['id'] for row in joined]) != qa['case_ids_sha256']):
        raise ValueError('joined target/group/prepared ID coverage differs')
    table = Path(config['feature_table'])
    payload = ''.join(json.dumps(row, sort_keys=True)+'\n' for row in joined).encode()
    role, columns = feature_contract()
    references = {row['reference_id'] for row in joined}
    manifest = {'status': 'passed', 'evaluation_role': role, 'profile': PROFILE,
        'feature_table': str(table), 'n': len(joined), 'groups': metadata['groups'],
        'columns': columns, 'predictor_columns': predictor_columns(), 'predictor_access': predictor_access(),
        'config_hash': digest(config), 'analysis_source': code_identity(),
        **{key: metadata[key] for key in SOURCE_KEYS},
        'controls_config_sha256': config['controls_config_sha256'],
        'controls_feature_manifest_sha256': config['controls_feature_manifest_sha256'],
        'controls_feature_table_sha256': config['controls_feature_table_sha256'],
        'confidence_config_sha256': config['confidence_config_sha256'],
        'confidence_manifest_sha256': config['confidence_manifest_sha256'],
        'confidence_summary_sha256': config['confidence_summary_sha256'],
        'confidence_audit_sha256': config['confidence_audit_sha256'],
        'confidence_identity_hash': audit['identity_hash'], 'confidence_sha256': summary['confidence_sha256'],
        'confidence_prepared_cases_sha256': qa['prepared_cases_sha256'],
        'target_case_ids_sha256': qa['case_ids_sha256'],
        'conditions': dict(Counter(row['condition'] for row in joined)),
        'original_split_counts': dict(Counter(row['original_split'] for row in joined)),
        'label_counts': {str(key): value for key, value in Counter(row['label'] for row in joined).items()},
        'target_metadata_labels_references_unchanged': True, 'target_outcomes_used_as_features': False,
        'generated_holdouts_opened': False, 'mechanism_C_fitted': False,
        'new_language_model_queries': 0, 'raw_response_payload_reads': 0,
        'confidence_measurement': confidence.MEASUREMENT,
        'confidence_measurement_backend': cc.get('execution_backend'),
        'scientific_access_cost': {'target_prefills_per_target_with_confidence': 1,
            'cached_target_prefills': len(joined), 'generated_target_tokens': 0,
            'maximum_reference_queries_per_target_in_neutral_tiers': 1,
            'distinct_reference_queries': len(references),
            'amortized_reference_queries_per_target': len(references)/len(joined),
            'reference_oracle_access': 'scored neutral tiers only',
            'source_oracle_access': 'explicit source-oracle tiers only'},
        'limitation': LIMITATION}
    manifest['sha256'] = hashlib.sha256(payload).hexdigest()
    data = {table: payload, Path(config['feature_manifest']): (json.dumps(manifest, sort_keys=True, indent=2)+'\n').encode()}
    for path, content in data.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError('immutable confidence feature artifact differs: '+str(path))
    for path, content in data.items():
        immutable(path, content)
    return manifest
