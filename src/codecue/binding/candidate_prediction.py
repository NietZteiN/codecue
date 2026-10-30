"""Discovery-only alternatives using complete finite candidate-event scalars.

Both completed metadata chains, source identity and FP32 policy are checked before
payload access. Existing labels/features are copied from a pinned thirteen-tier
table. No model loading, answer generation or raw target responses are involved.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from . import candidate_measurement as measurement
from . import confidence_prediction as one_token
from .datasets import digest, read_jsonl
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable

PROFILE = 'candidate_event_confidence_v1'
ROLE = 'discovery_failure_prediction_candidate_events_v1'
STATISTICS = measurement.SCALARS
EVENT_COLUMNS = tuple('candidate_event_'+name for name in STATISTICS)
CANDIDATE_COUNT = 33
PREFIX_STATES = 35
PAIRED_TIERS = (
    ('A_input', 'B_input_confidence', 'B_event_input'),
    ('A_interactions', 'B_interactions_confidence', 'B_event_interactions'),
    ('A_interactions_neutral_raw', 'B_interactions_neutral_raw_confidence', 'B_event_interactions_neutral_raw'),
    ('A_interactions_oracle_neutral_raw', 'B_interactions_oracle_neutral_raw_confidence', 'B_event_interactions_oracle_neutral_raw'),
    ('A_interactions_oracle_neutral_scored', 'B_interactions_oracle_neutral_scored_confidence', 'B_event_interactions_oracle_neutral_scored'),
)
LIMITATION = (
    'Exploratory grouped prediction on previously consumed discovery structures, '
    'not mechanism C or unfamiliar-program/final confirmation. All thirteen '
    'existing source, neutral, oracle and BF16 next-token confidence tiers are '
    'retained unchanged. Five event alternatives use only six scalar summaries '
    'of declared finite numeral-plus-EOS token events; no old one-token confidence '
    'scalars are added to those alternatives. Comparing B_event with B_confidence '
    'compares alternative measurement bundles, not a nested information-only '
    'increment: event definition, FP32/no-TF32 versus BF16 numeric execution, '
    'checkpoint-specific tokenization rules, encoding and fitted function-class '
    'effects can all matter. A gain cannot isolate full-answer scoring from those '
    'differences. Event likelihood access is stronger than one-token sign/format '
    'confidence: one FP32 prefix prefill plus all 33 candidate numerals and the '
    'declared EOS union, spanning 35 prefix states per target. KV reuse does not '
    'remove this scientific access cost. Finite-event support mass is separate '
    'from support-conditional summaries; other textual answers/tokenizations are '
    'outside that support. Source-oracle and scored/raw neutral access remain '
    'separately declared. No generated token, token/candidate identity or target '
    'response/correctness is a feature. Correctness is only the existing supervised '
    'label. Repeated partition seeds are not independent replications; bootstrap '
    'intervals condition on saved OOF predictions without refits or multiplicity correction.'
)


def predictor_columns(config=None):
    columns = one_token.predictor_columns()
    columns.update({right: columns[left]+list(EVENT_COLUMNS) for left, _, right in PAIRED_TIERS})
    if config is not None:
        expected = {'seeds': [17, 29, 43], 'outer_folds': 6, 'inner_folds': 5,
                    'l2_grid': [.1, 1., 10., 100.]}
        if any(key in config and config[key] != value for key, value in expected.items()):
            raise ValueError('candidate profile retains the fixed existing grouped CV protocol')
        if config.get('feature_information_contract', columns) != columns:
            raise ValueError('candidate feature declaration differs from the fixed eighteen-tier profile')
        if 'predictor_access' in config and config['predictor_access'] != predictor_access():
            raise ValueError('candidate access declaration differs from fixed scientific costs')
    return columns


def predictor_access():
    access = one_token.predictor_access()
    for left, _, right in PAIRED_TIERS:
        access[right] = {**access[left], 'target_prefills_per_target': 1,
            'target_prefill_measurement_dtype': 'float32', 'tf32_policy': 'disabled_highest_float32',
            'candidate_events_per_target': CANDIDATE_COUNT,
            'candidate_eos_union': 'all declared checkpoint EOS IDs',
            'candidate_prefix_states_per_target': PREFIX_STATES,
            'one_token_confidence_features': False}
    return access


def predictor_comparisons(config=None):
    predictor_columns(config)
    return one_token.predictor_comparisons()+tuple((left, right) for left, _, right in PAIRED_TIERS)+tuple(
        (old, right) for _, old, right in PAIRED_TIERS)+(
        ('B_event_input', 'B_event_interactions'),
        ('B_event_interactions', 'B_event_interactions_neutral_raw'),
        ('B_event_interactions_oracle_neutral_raw', 'B_event_interactions_oracle_neutral_scored'),
    )


def feature_contract(config=None):
    predictor_columns(config)
    _, contract = one_token.feature_contract()
    return ROLE, {**contract, 'candidate_events': list(EVENT_COLUMNS)}


def _metadata(config):
    """Validate complete parent/source/measurement chains, without payload reads."""
    _object, same = one_token._object, one_token._same_path
    _discovery_declaration(config)
    for key in ('source_prediction_config', 'candidate_config', 'feature_table', 'feature_manifest'):
        _discovery_response_path(config[key])
    if (Path(config['feature_table']).suffix != '.jsonl' or Path(config['feature_manifest']).suffix != '.json'
            or same(config['feature_table'], config['feature_manifest'])):
        raise ValueError('distinct JSONL feature and JSON manifest outputs required')
    for key in ('source_prediction_config_sha256', 'candidate_config_sha256',
                'candidate_manifest_sha256', 'candidate_summary_sha256', 'candidate_audit_sha256'):
        if not isinstance(config.get(key), str) or len(config[key]) != 64:
            raise ValueError('explicit pinned source/measurement metadata required: '+key)
    parent = _object(config['source_prediction_config'], config['source_prediction_config_sha256'], 'parent prediction config')
    if parent.get('feature_profile') != one_token.PROFILE:
        raise ValueError('completed thirteen-tier confidence_access_v1 parent required')
    parent_columns = one_token.predictor_columns(parent)
    for key in ('feature_table', 'feature_manifest', 'collection_config'):
        _discovery_response_path(parent[key])
    if any(not isinstance(parent.get(key), str) or len(parent[key]) != 64
           for key in ('feature_manifest_sha256', 'feature_table_sha256')):
        raise ValueError('parent feature manifest and table checksum pins required')
    pm = _object(parent['feature_manifest'], parent.get('feature_manifest_sha256'), 'parent feature manifest')
    role, contract = one_token.feature_contract()
    if (pm.get('status') != 'passed' or pm.get('evaluation_role') != role or pm.get('profile') != one_token.PROFILE
            or pm.get('columns') != contract or pm.get('predictor_columns') != parent_columns
            or pm.get('predictor_access') != one_token.predictor_access()
            or pm.get('sha256') != parent.get('feature_table_sha256')
            or not isinstance(pm.get('sha256'), str) or len(pm['sha256']) != 64
            or not same(pm.get('feature_table', ''), parent['feature_table'])
            or pm.get('n') != measurement.SOURCE_CASES or type(pm.get('groups')) is not int or pm['groups'] < 1
            or pm.get('target_metadata_labels_references_unchanged') is not True
            or any(pm.get(key) is not False for key in
                ('generated_holdouts_opened', 'target_outcomes_used_as_features', 'mechanism_C_fitted'))):
        raise ValueError('completed parent feature/checksum/access contract differs')
    for key, field in (('model', 'source_model'), ('model_revision', 'source_model_revision')):
        if not config.get(key) or config[key] != parent.get(key) or config[key] != pm.get(field):
            raise ValueError('parent checkpoint differs from candidate prediction')
    producer = _object(parent['collection_config'])
    if (digest(producer) != pm.get('config_hash') or any(not same(producer[key], parent[key]) for key in ('feature_table', 'feature_manifest'))):
        raise ValueError('parent feature producer configuration identity differs')
    ancestors = one_token._metadata(producer)
    _, control_manifest, source_confidence, source_qa, _, _ = ancestors
    if any(pm.get(key) != control_manifest.get(key) for key in ('n', 'groups')):
        raise ValueError('parent structural-group coverage differs from pinned controls ancestry')
    if (pm.get('confidence_measurement') != one_token.confidence.MEASUREMENT
            or pm.get('confidence_measurement_backend') != source_confidence.get('execution_backend')):
        raise ValueError('parent one-token measurement/backend declaration differs')
    for key in one_token.SOURCE_KEYS:
        if pm.get(key) != control_manifest.get(key):
            raise ValueError('parent original source provenance differs: '+key)
    for key in ('controls_config_sha256', 'controls_feature_manifest_sha256', 'controls_feature_table_sha256',
                'confidence_config_sha256', 'confidence_manifest_sha256', 'confidence_summary_sha256', 'confidence_audit_sha256'):
        if pm.get(key) != producer.get(key):
            raise ValueError('parent confidence feature provenance differs: '+key)
    cc = _object(config['candidate_config'], config['candidate_config_sha256'], 'candidate config')
    if (cc.get('case_limit') is not None or cc.get('measurement_dtype') != 'float32'
            or any(cc.get(key) != config[key] for key in ('model', 'model_revision'))):
        raise ValueError('complete FP32 matching candidate bank required, not BF16/smoke')
    candidate_source, candidates, eos, provenance = measurement._metadata(cc)
    if (candidate_source != source_confidence or candidates != list(range(-16, 17))
            or cc['source_confidence_config_sha256'] != pm.get('confidence_config_sha256')):
        raise ValueError('candidate and parent confidence source configurations/support differ')
    stage = Path(cc['run_dir'])/'candidate_measurement'
    manifest = _object(stage/'manifest.json', config['candidate_manifest_sha256'], 'candidate manifest')
    summary = _object(stage/'summary.json', config['candidate_summary_sha256'], 'candidate summary')
    audit = _object(stage/'audit.json', config['candidate_audit_sha256'], 'candidate audit')
    qa = _object(cc['preparation_review'])
    runtime = _object(stage/'runtime.json')
    identity = manifest.get('identity', {})
    n = measurement.SOURCE_CASES
    if (manifest.get('status') != 'complete' or manifest.get('identity_hash') != digest(identity)
            or identity.get('config') != cc or identity.get('config_hash') != digest(cc)
            or identity.get('stage') != 'candidate_measurement'
            or any(identity.get(key) != cc[key] for key in ('model_revision', 'tokenizer_revision'))
            or identity.get('dataset_manifest', {}).get('sha256') != pm.get('source_dataset_sha256')
            or any(value.get('evaluated') != n or value.get('planned') != n for value in (manifest, summary))
            or qa.get('status') != 'passed' or qa.get('complete') is not True
            or qa.get('evaluation_role') != measurement.ROLE or qa.get('config_hash') != digest(cc)
            or qa.get('source_sha256') != identity.get('code', {}).get('source_sha256')
            or qa.get('tokenizer_revision') != cc['tokenizer_revision']
            or qa.get('provenance') != provenance or qa.get('source_cases') != n or qa.get('cases') != n
            or qa.get('smoke_subset') is not False or qa.get('boundary_verified') is not True or qa.get('prefix_free') is not True
            or qa.get('candidates') != candidates or qa.get('eos_token_ids') != eos
            or qa.get('candidate_count') != CANDIDATE_COUNT or qa.get('eos_variant_count') != len(eos)
            or qa.get('trie_nodes') != {str(PREFIX_STATES): n} or qa.get('prefix_node_evaluations') != PREFIX_STATES*n
            or qa.get('case_ids_sha256') != pm.get('target_case_ids_sha256')
            or qa.get('case_ids_sha256') != source_qa.get('case_ids_sha256')
            or qa.get('tokenization_rule') != measurement._rule(cc)
            or qa.get('parity_tolerance_rule') != measurement.TOLERANCE_RULE):
        raise ValueError('complete candidate preparation/source/event identity differs')
    links = {'source_confidence_config_sha256': 'confidence_config_sha256',
        'source_confidence_identity_hash': 'confidence_identity_hash',
        'source_prepared_cases_sha256': 'confidence_prepared_cases_sha256',
        'source_case_ids_sha256': 'target_case_ids_sha256',
        'source_confidence_audit_sha256': 'confidence_audit_sha256'}
    if any(provenance.get(left) != pm.get(right) for left, right in links.items()):
        raise ValueError('candidate event provenance does not bind the parent prompt/source bank')
    vocabulary = qa.get('tokenizer', {})
    if (not isinstance(vocabulary, dict) or type(vocabulary.get('vocabulary_size')) is not int
            or vocabulary['vocabulary_size'] < 2 or type(vocabulary.get('pad_token_id')) is not int
            or not 0 <= vocabulary['pad_token_id'] < vocabulary['vocabulary_size']
            or any(not 0 <= token < vocabulary['vocabulary_size'] for token in eos)
            or len(vocabulary.get('eos_token_spellings', [])) != len(eos)
            or any(not isinstance(text, str) or not text for text in vocabulary['eos_token_spellings'])):
        raise ValueError('candidate prepared tokenizer vocabulary/EOS contract differs')
    for value in (qa, summary):
        if (value.get('measurement') != measurement.MEASUREMENT or value.get('generated_tokens') != 0
                or any(value.get(key) is not False for key in
                    ('target_outcomes_read', 'upstream_scalar_payloads_read', 'oracle_fields_exported', 'generated_holdouts_opened'))
                or any(value.get(key) != cc[key] for key in ('model', 'model_revision'))):
            raise ValueError('candidate measurement checkpoint/discovery-only access differs')
    measurement._check_precision(cc, qa, loaded=False)
    measurement._check_precision(cc, runtime, loaded=True)
    measurement._check_precision(cc, summary, loaded=True)
    runtime_fields = {'status', 'scoring_backend', 'attention_backend', 'batch_size', 'event_batch_size',
        'prompt_batch_size', 'max_active_nodes', 'device', 'dtype', 'load_seconds', 'gpu',
        'resumed_cases', 'measured_this_attempt', 'gpu_scope', 'versions', 'source_dtype',
        'measurement_dtype', 'actual_model_dtype', 'actual_model_dtype_verified', 'tf32_policy',
        'tf32_settings', 'tokenization_rule'}
    if (set(runtime) != runtime_fields or runtime.get('status') != 'recorded' or runtime.get('dtype') != 'float32'
            or any(runtime.get(key) != cc[key] for key in ('device', 'scoring_backend'))
            or runtime.get('tokenization_rule') != measurement._rule(cc)
            or any(runtime.get(key) != cc.get(key, default) for key, default in
                (('batch_size', 32), ('event_batch_size', 128), ('prompt_batch_size', 4), ('max_active_nodes', 2048)))
            or type(runtime.get('resumed_cases')) is not int or not 0 <= runtime['resumed_cases'] <= n
            or type(runtime.get('measured_this_attempt')) is not int
            or runtime['measured_this_attempt'] != n-runtime['resumed_cases']
            or isinstance(runtime.get('load_seconds'), bool) or not isinstance(runtime.get('load_seconds'), (int, float))
            or not math.isfinite(runtime['load_seconds']) or runtime['load_seconds'] < 0
            or any(summary.get(key) != value for key, value in runtime.items() if key != 'status')
            or summary.get('status') != 'complete' or summary.get('complete') is not True
            or summary.get('evaluation_role') != measurement.ROLE or summary.get('smoke_subset') is not False
            or summary.get('statistics') != list(STATISTICS)
            or summary.get('tokenization_rule') != measurement._rule(cc)
            or summary.get('scoring_backend') != cc['scoring_backend']
            or summary.get('attention_backend') != cc.get('attention_backend', 'sdpa')
            or summary.get('prefix_node_evaluations') != PREFIX_STATES*n
            or summary.get('parity', {}).get('tolerance_rule') != measurement.TOLERANCE_RULE
            or summary.get('parity', {}).get('status') != ('passed' if cc.get('parity_check', False) else 'not_requested')
            or summary.get('parity', {}).get('cases') != (n if cc.get('parity_check', False) else 0)
            or any(summary.get(key) != qa.get(key) for key in ('prepared_events_sha256', 'case_ids_sha256', 'event_banks_sha256'))
            or audit.get('status') != 'passed' or audit.get('complete') is not True or audit.get('evaluated') != n
            or audit.get('identity_hash') != manifest['identity_hash'] or audit.get('preparation') != qa
            or audit.get('measurement') != measurement.MEASUREMENT
            or any(audit.get(key) != cc[key] for key in ('model', 'model_revision'))
            or audit.get('target_outcomes_read') is not False or audit.get('upstream_scalar_payloads_read') is not False
            or audit.get('generated_tokens') != 0
            or any(value.get('scalar_sha256') != summary.get('scalar_sha256') for value in (manifest, audit))
            or any(not isinstance(value, str) or len(value) != 64 for value in
                (summary.get('scalar_sha256'), qa.get('prepared_events_sha256'), qa.get('event_banks_sha256'), qa.get('source_sha256')))):
        raise ValueError('completed candidate summary/audit/FP32 payload contract differs')
    protected = [config['source_prediction_config'], config['candidate_config'], parent['feature_table'],
        parent['feature_manifest'], parent['collection_config'], cc['prepared_events'], cc['preparation_review'],
        source_confidence['prepared_cases'], source_confidence['preflight_result'],
        *[str(stage/name) for name in ('manifest.json', 'summary.json', 'audit.json', 'runtime.json', 'scalars.jsonl')]]
    if any(same(config[key], path) for key in ('feature_table', 'feature_manifest') for path in protected):
        raise ValueError('candidate feature outputs cannot replace source artifacts')
    return parent, pm, cc, qa, summary, audit, source_confidence, source_qa


def augment_rows(rows, cases, scalars):
    """Append six whitelisted scalars; every old feature and label stays exact."""
    from .discovery_prediction import _rows, _matrix
    rows, _ = _rows(rows);cases = list(cases);scalars = list(scalars)
    if (len({case['id'] for case in cases}) != len(cases) or len({row['id'] for row in scalars}) != len(scalars)
            or {row['id'] for row in rows} != {case['id'] for case in cases}
            or {row['id'] for row in rows} != {row['id'] for row in scalars}):
        raise ValueError('complete identical parent/candidate/scalar ID coverage required')
    by_case = {case['id']: case for case in cases};by_scalar = {row['id']: row for row in scalars}
    measurement.validate_rows(cases, [by_scalar[case['id']] for case in cases])
    _, contract = one_token.feature_contract();expected = set(sum(contract.values(), []))
    mapping = {'id': 'id', 'base_id': 'base_id', 'template_id': 'template_id', 'original_split': 'split',
        'condition': 'condition', 'query_role': 'query_role', 'available_bindings': 'available_bindings',
        'lexical_realization': 'lexical_realization'}
    output = []
    for row in rows:
        if (set(row) != set(one_token.ROW_METADATA)|{'label', 'features'} or type(row['label']) is not int
                or set(row['features']) != expected):
            raise ValueError('parent label/feature whitelist differs; target response scores are forbidden')
        case = by_case[row['id']];values = row['features'];bank = case['event_bank']
        measurement.event.validate_bank(bank)
        if (set(case) != measurement.PREPARED_FIELDS or case['evaluation_role'] != measurement.ROLE
                or any(row[left] != case[right] for left, right in mapping.items())
                or case['tail_placement'] not in ('before', 'after')
                or values['updates'] != case['updates'] or values['tail_after'] != int(case['tail_placement'] == 'after')
                or values['prompt_tokens'] != len(bank['input_token_ids'])
                or values['available_bindings'] != case['available_bindings']
                or values['misleading'] != int(case['condition'] == 'misleading')
                or values['query_saved'] != int(case['query_role'] == 'saved')
                or values['lexical_one'] != case['lexical_realization']
                or bank['candidates'] != list(range(-16, 17))
                or by_scalar[row['id']]['trie_nodes'] != PREFIX_STATES):
            raise ValueError('candidate exact prompt/event/design provenance differs from parent features')
        output.append({**{key: row[key] for key in one_token.ROW_METADATA}, 'label': row['label'],
            'features': {**values, **{column: by_scalar[row['id']][name] for name, column in zip(STATISTICS, EVENT_COLUMNS)}}})
    for columns in predictor_columns().values():
        _matrix(output, columns)
    return output


def collect(config):
    """Join fully audited FP32 events after all metadata and payload pins pass."""
    from .discovery_prediction import load_features
    from .registry import code_identity
    parent, pm, cc, qa, summary, audit, source_confidence, source_qa = _metadata(config)
    scalar_path = Path(cc['run_dir'])/'candidate_measurement/scalars.jsonl'
    for path, expected, name in ((parent['feature_table'], pm['sha256'], 'parent features'),
            (cc['prepared_events'], qa['prepared_events_sha256'], 'prepared candidate events'),
            (scalar_path, summary['scalar_sha256'], 'candidate scalars'),
            (source_confidence['prepared_cases'], source_qa['prepared_cases_sha256'], 'source prompt inputs')):
        one_token._pinned(path, expected, name)
    if measurement.audit(cc) != audit:
        raise ValueError('candidate re-audit differs from pinned completed audit')
    checked, rows = load_features(parent)
    if checked != pm:
        raise ValueError('parent metadata changed after validation')
    prepared, cases = measurement.inputs(cc, expected_source=qa['source_sha256'])
    if prepared != qa:
        raise ValueError('candidate preparation changed after validation')
    one_token._pinned(scalar_path, summary['scalar_sha256'], 'candidate scalars')
    joined = augment_rows(rows, cases, read_jsonl(scalar_path))
    if (len(joined) != measurement.SOURCE_CASES or len({row['template_id'] for row in joined}) != pm['groups']
            or digest([row['id'] for row in joined]) != qa['case_ids_sha256']):
        raise ValueError('joined parent/candidate group or prepared-ID coverage differs')
    table = Path(config['feature_table'])
    payload = ''.join(json.dumps(row, sort_keys=True)+'\n' for row in joined).encode()
    role, contract = feature_contract()
    result = {'status': 'passed', 'profile': PROFILE, 'evaluation_role': role, 'feature_table': str(table),
        'sha256': hashlib.sha256(payload).hexdigest(), 'n': len(joined), 'groups': pm['groups'],
        'columns': contract, 'predictor_columns': predictor_columns(), 'predictor_access': predictor_access(),
        'config_hash': digest(config), 'analysis_source': code_identity(),
        **{key: pm[key] for key in one_token.SOURCE_KEYS},
        'source_prediction_config_sha256': config['source_prediction_config_sha256'],
        'parent_feature_manifest_sha256': parent['feature_manifest_sha256'], 'parent_feature_table_sha256': pm['sha256'],
        **{key: config[key] for key in ('candidate_config_sha256', 'candidate_manifest_sha256', 'candidate_summary_sha256', 'candidate_audit_sha256')},
        'candidate_scalar_sha256': summary['scalar_sha256'], 'candidate_identity_hash': audit['identity_hash'],
        'candidate_prepared_events_sha256': qa['prepared_events_sha256'], 'candidate_event_banks_sha256': qa['event_banks_sha256'],
        'target_case_ids_sha256': qa['case_ids_sha256'], 'candidate_source_provenance': qa['provenance'],
        'candidate_tokenization_rule': qa['tokenization_rule'], 'candidate_scoring_backend': cc['scoring_backend'],
        'candidate_precision': {key: summary[key] for key in ('source_dtype', 'measurement_dtype', 'actual_model_dtype',
            'actual_model_dtype_verified', 'tf32_policy', 'tf32_settings')},
        'parent_confidence_measurement': pm['confidence_measurement'],
        'parent_confidence_measurement_backend': pm['confidence_measurement_backend'],
        'scientific_access_cost': {'candidate_events_per_target': CANDIDATE_COUNT, 'eos_variant_count': len(qa['eos_token_ids']),
            'event_variants_per_target': CANDIDATE_COUNT*len(qa['eos_token_ids']), 'target_prefix_prefills_per_target': 1,
            'prefix_states_per_target': PREFIX_STATES, 'total_prefix_states': PREFIX_STATES*len(joined),
            'measurement_dtype': 'float32', 'tf32_policy': 'disabled_highest_float32',
            'generated_target_tokens': 0, 'neutral_and_oracle_access': 'unchanged and separately declared per tier'},
        'label_counts': {str(key): value for key, value in Counter(row['label'] for row in joined).items()},
        'original_split_counts': dict(Counter(row['original_split'] for row in joined)),
        'conditions': dict(Counter(row['condition'] for row in joined)),
        'old_thirteen_feature_sets_and_labels_unchanged': True, 'target_metadata_labels_references_unchanged': True,
        'target_outcomes_used_as_features': False, 'raw_response_payload_reads': 0, 'new_language_model_queries': 0,
        'generated_holdouts_opened': False, 'mechanism_C_fitted': False, 'limitation': LIMITATION}
    data = {table: payload, Path(config['feature_manifest']): (json.dumps(result, sort_keys=True, indent=2)+'\n').encode()}
    for path, content in data.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError('immutable candidate feature artifact differs: '+str(path))
    for path, content in data.items():
        immutable(path, content)
    return result
