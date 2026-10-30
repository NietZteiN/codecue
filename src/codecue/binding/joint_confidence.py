"""Nested discovery confidence controls using both already-measured bundles.

All eighteen parent predictors remain unchanged. Five fixed joint tiers add the
six FP32 finite-event scalars to the corresponding BF16 next-token confidence
tier. This module loads no language model and reads no raw target responses.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import candidate_pipeline, candidate_prediction as parent
from . import confidence_prediction as one_token
from .datasets import digest
from .forecasting import _discovery_declaration, _discovery_response_path
from .published_benchmarks import immutable, sha

PROFILE = 'joint_confidence_v1'
ROLE = 'discovery_failure_prediction_joint_confidence_v1'
PAIRED_TIERS = tuple((*row, row[2].replace('B_event_', 'B_joint_')) for row in parent.PAIRED_TIERS)
PRIMARY_PAIRS = tuple((old, joint) for _, old, _, joint in PAIRED_TIERS)
EVENT_PAIRS = tuple((event, joint) for _, _, event, joint in PAIRED_TIERS)
LIMITATION = (
    'Exploratory nested grouped prediction on already-consumed discovery targets; '
    'not mechanism C or unfamiliar-program/final confirmation. All eighteen '
    'existing source, neutral, oracle, next-token confidence and finite-event '
    'alternative tiers are retained unchanged. Five fixed joint tiers combine '
    'the four existing BF16 next-token scalars and six existing FP32/no-TF32 '
    'finite numeral-plus-EOS scalars in each declared context. Those tiers are '
    'feature-nested in both corresponding confidence alternatives. No new '
    'language-model query is performed; scientific access remains the union of '
    'the two measurement contracts: one BF16 next-token prefill plus one FP32 '
    'event prefix prefill and 33 numerals with the declared EOS union across '
    '35 prefix states. Saved caches do not remove that scientific cost. '
    'A predictive increment can reflect encoding, fitted function class and '
    'numerical execution, rather than a pure information or causal mechanism '
    'effect. Finite-event support excludes other textual answers and is not '
    'task-correctness probability. Source-oracle, raw-neutral and oracle-scored '
    'neutral access stay separately declared. No candidate/token identity, '
    'generated answer, target response or correctness is a feature; correctness '
    'is only the existing supervised label. Repeated partition seeds reuse '
    'the same structural groups. Bootstrap intervals condition on saved OOF '
    'probabilities without refitting or multiplicity adjustment.'
)


def predictor_columns(config=None):
    columns = parent.predictor_columns()
    columns.update({joint: columns[old]+list(parent.EVENT_COLUMNS)
                    for _, old, _, joint in PAIRED_TIERS})
    if config is not None:
        fixed = dict(seeds=[17, 29, 43], outer_folds=6, inner_folds=5,
                     l2_grid=[.1, 1., 10., 100.], bootstrap_replicates=2000, bootstrap_seed=117)
        if any(key in config and config[key] != value for key, value in fixed.items()):
            raise ValueError('joint profile retains the fixed grouped fitting and bootstrap protocol')
        if config.get('feature_information_contract', columns) != columns:
            raise ValueError('joint feature declaration differs from fixed twenty-three-tier profile')
        if 'predictor_access' in config and config['predictor_access'] != predictor_access():
            raise ValueError('joint access declaration differs from fixed scientific costs')
    return columns


def predictor_access():
    access = parent.predictor_access()
    for _, _, event, joint in PAIRED_TIERS:
        access[joint] = {**access[event], 'target_prefills_per_target': 2,
            'target_prefill_measurement_dtype': ['bfloat16', 'float32'],
            'one_token_confidence_features': True,
            'next_token_prefills_per_target': 1, 'candidate_prefix_prefills_per_target': 1}
    return access


def predictor_comparisons(config=None):
    predictor_columns(config)
    return parent.predictor_comparisons()+PRIMARY_PAIRS+EVENT_PAIRS+tuple(
        (source, joint) for source, _, _, joint in PAIRED_TIERS)+(
        ('B_joint_input', 'B_joint_interactions'),
        ('B_joint_interactions', 'B_joint_interactions_neutral_raw'),
        ('B_joint_interactions_oracle_neutral_raw', 'B_joint_interactions_oracle_neutral_scored'),
    )


def feature_contract(config=None):
    predictor_columns(config)
    return ROLE, parent.feature_contract()[1]


def protocol():
    return dict(feature_profile=PROFILE, feature_information_contract=predictor_columns(),
        predictor_access=predictor_access(), comparisons=[list(pair) for pair in predictor_comparisons()],
        seeds=[17, 29, 43], outer_folds=6, inner_folds=5, l2_grid=[.1, 1., 10., 100.],
        bootstrap_replicates=2000, bootstrap_seed=117)


def _json(path, value):
    immutable(path, (json.dumps(value, sort_keys=True, indent=2)+'\n').encode())


def _pin(value, name):
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError('explicit pinned metadata checksum required: '+name)


def _metadata(config):
    """Validate the completed parent and scalar ancestry before payload access."""
    from . import discovery_prediction as generic
    _discovery_declaration(config)
    for key in ('source_pipeline_config', 'source_pipeline_receipt', 'feature_table', 'feature_manifest'):
        _discovery_response_path(config[key])
    for key in ('source_pipeline_config_sha256', 'source_pipeline_receipt_sha256'):
        _pin(config.get(key), key)
    if (Path(config['feature_table']).suffix != '.jsonl'
            or Path(config['feature_manifest']).suffix != '.json'
            or one_token._same_path(config['feature_table'], config['feature_manifest'])):
        raise ValueError('distinct JSONL feature and JSON manifest outputs required')
    spec = one_token._object(config['source_pipeline_config'], config['source_pipeline_config_sha256'])
    candidate_pipeline.validate(spec)
    out = Path(spec['output_dir'])
    if not one_token._same_path(config['source_pipeline_receipt'], out/'pipeline_review_v1.json'):
        raise ValueError('parent pipeline receipt path differs from its output directory')
    receipt = one_token._object(config['source_pipeline_receipt'], config['source_pipeline_receipt_sha256'])
    if (receipt.get('status') != 'complete_exploratory' or receipt.get('config_hash') != digest(spec)
            or receipt.get('protocol_hash') != digest(candidate_pipeline.protocol())
            or any(receipt.get(key) is not False for key in
                   ('generated_holdouts_opened', 'mechanism_C_fitted', 'model_loading'))):
        raise ValueError('complete matching discovery parent pipeline receipt required')
    bindings = dict(collection_config=out/'collection_config.json', effective_config=out/'effective_config.json')
    loaded = {}
    for key, path in bindings.items():
        link = receipt.get(key, {})
        _discovery_response_path(path)
        if not one_token._same_path(link.get('path', ''), path):
            raise ValueError('parent pipeline '+key+' path differs')
        _pin(link.get('sha256'), key)
        loaded[key] = one_token._object(path, link['sha256'], key)
    effective, producer = loaded['effective_config'], loaded['collection_config']
    if effective.get('feature_profile') != parent.PROFILE:
        raise ValueError('completed eighteen-tier candidate-event parent required')
    parent.predictor_columns(effective)
    if generic._plan(effective) != generic._plan(candidate_pipeline.protocol()):
        raise ValueError('parent completed fitting protocol differs')
    if not one_token._same_path(effective.get('collection_config', ''), bindings['collection_config']):
        raise ValueError('parent feature producer link differs')
    for key in ('feature_table', 'feature_manifest', 'review_artifact'):
        _discovery_response_path(effective[key])
    for key in ('feature_table_sha256', 'feature_manifest_sha256'):
        _pin(effective.get(key), key)
    link = receipt.get('review', {})
    if not one_token._same_path(link.get('path', ''), effective['review_artifact']):
        raise ValueError('completed parent prediction review path differs')
    _pin(link.get('sha256'), 'parent review')
    review = one_token._object(effective['review_artifact'], link['sha256'], 'completed parent review')
    manifest = one_token._object(effective['feature_manifest'], effective['feature_manifest_sha256'])
    source_parent, pm, cc, qa, summary, audit, source_confidence, _ = parent._metadata(producer)
    role, contract = parent.feature_contract()
    if (manifest.get('status') != 'passed' or manifest.get('evaluation_role') != role
            or manifest.get('profile') != parent.PROFILE or manifest.get('columns') != contract
            or manifest.get('predictor_columns') != parent.predictor_columns()
            or manifest.get('predictor_access') != parent.predictor_access()
            or manifest.get('sha256') != effective['feature_table_sha256']
            or manifest.get('config_hash') != digest(producer)
            or not one_token._same_path(manifest.get('feature_table', ''), effective['feature_table'])
            or any(not one_token._same_path(producer[key], effective[key]) for key in ('feature_table', 'feature_manifest'))
            or any(manifest.get(key) != pm[key] for key in (*one_token.SOURCE_KEYS, 'n', 'groups'))
            or manifest.get('n') != parent.measurement.SOURCE_CASES
            or manifest.get('old_thirteen_feature_sets_and_labels_unchanged') is not True
            or manifest.get('target_metadata_labels_references_unchanged') is not True
            or any(manifest.get(key) is not False for key in
                   ('generated_holdouts_opened', 'target_outcomes_used_as_features', 'mechanism_C_fitted'))):
        raise ValueError('completed parent feature whitelist/source/coverage contract differs')
    for key in ('source_prediction_config_sha256', 'candidate_config_sha256', 'candidate_manifest_sha256',
                'candidate_summary_sha256', 'candidate_audit_sha256'):
        if manifest.get(key) != producer[key]:
            raise ValueError('parent candidate feature metadata pin differs: '+key)
    expected = dict(parent_feature_manifest_sha256=source_parent['feature_manifest_sha256'],
        parent_feature_table_sha256=pm['sha256'], candidate_scalar_sha256=summary['scalar_sha256'],
        candidate_identity_hash=audit['identity_hash'], candidate_prepared_events_sha256=qa['prepared_events_sha256'],
        candidate_event_banks_sha256=qa['event_banks_sha256'], target_case_ids_sha256=qa['case_ids_sha256'],
        candidate_source_provenance=qa['provenance'], candidate_tokenization_rule=qa['tokenization_rule'],
        candidate_scoring_backend=cc['scoring_backend'], parent_confidence_measurement=pm['confidence_measurement'],
        parent_confidence_measurement_backend=pm['confidence_measurement_backend'],
        candidate_precision={key: summary[key] for key in ('source_dtype', 'measurement_dtype', 'actual_model_dtype',
            'actual_model_dtype_verified', 'tf32_policy', 'tf32_settings')})
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError('parent scalar provenance/precision declaration differs')
    if (review.get('status') != 'complete_exploratory' or review.get('config_hash') != digest(effective)
            or review.get('feature_manifest') != manifest
            or review.get('feature_table_sha256') != manifest['sha256']
            or review.get('feature_manifest_sha256') != effective['feature_manifest_sha256']
            or review.get('analysis_plan') != generic._plan(effective)
            or review.get('n') != manifest['n'] or review.get('templates') != manifest['groups']
            or any(review.get(key) is not False for key in ('generated_holdouts_opened', 'mechanism_C_fitted'))):
        raise ValueError('completed parent prediction/manifest/protocol identity differs')
    for value in (spec, effective, producer):
        if any(config.get(key) != value.get(key) or not config.get(key) for key in ('model', 'model_revision')):
            raise ValueError('joint parent checkpoint differs')
    if any(manifest.get(field) != config[key] for key, field in
           (('model', 'source_model'), ('model_revision', 'source_model_revision'))):
        raise ValueError('joint manifest checkpoint differs')
    protected = [config['source_pipeline_config'], config['source_pipeline_receipt'], *bindings.values(),
        effective['review_artifact'], effective['feature_table'], effective['feature_manifest'],
        producer['source_prediction_config'], producer['candidate_config'], cc['prepared_events'], cc['preparation_review'],
        source_parent['feature_table'], source_parent['feature_manifest'], source_parent['collection_config'],
        source_confidence['prepared_cases'], source_confidence['preflight_result'],
        *[Path(cc['run_dir'])/'candidate_measurement'/name for name in
          ('manifest.json', 'summary.json', 'audit.json', 'runtime.json', 'scalars.jsonl')]]
    for artifact in review.get('artifacts', {}).values():
        _discovery_response_path(artifact['path'])
        protected.append(artifact['path'])
    if any(one_token._same_path(config[key], path) for key in ('feature_table', 'feature_manifest') for path in protected):
        raise ValueError('joint feature outputs cannot replace parent/source artifacts')
    return effective, manifest, receipt


def collect(config):
    """Copy all parent feature bytes unchanged under a new explicit joint role."""
    from . import discovery_prediction as generic
    from .registry import code_identity
    effective, manifest, receipt = _metadata(config)
    checked, rows = generic.load_features(effective)
    if checked != manifest:
        raise ValueError('parent feature metadata changed after validation')
    expected = set(sum(feature_contract()[1].values(), []))
    for row in rows:
        if (set(row) != set(one_token.ROW_METADATA)|{'label', 'features'}
                or type(row['label']) is not int or set(row['features']) != expected):
            raise ValueError('parent label/feature whitelist differs; target response features are forbidden')
    if generic._reuse(effective, manifest) is None:
        raise ValueError('complete parent fitted artifacts required')
    # Recheck before byte copying; never serialize or recompute parent values.
    one_token._pinned(effective['feature_table'], manifest['sha256'], 'parent feature table')
    payload = Path(effective['feature_table']).read_bytes()
    result = {**manifest, 'profile': PROFILE, 'evaluation_role': ROLE,
        'feature_table': config['feature_table'], 'columns': feature_contract()[1],
        'predictor_columns': predictor_columns(), 'predictor_access': predictor_access(),
        'config_hash': digest(config), 'analysis_source': code_identity(),
        'source_pipeline_config_sha256': config['source_pipeline_config_sha256'],
        'source_pipeline_receipt_sha256': config['source_pipeline_receipt_sha256'],
        'parent_effective_config_sha256': receipt['effective_config']['sha256'],
        'parent_feature_manifest_sha256': effective['feature_manifest_sha256'],
        'parent_feature_table_sha256': effective['feature_table_sha256'],
        'parent_scientific_access_cost': manifest['scientific_access_cost'],
        'scientific_access_cost': {
            'total_target_prefills_per_target': 2, 'next_token_target_prefills_per_target': 1,
            'candidate_target_prefix_prefills_per_target': 1,
            'next_token_measurement_dtype': 'bfloat16', 'candidate_measurement_dtype': 'float32',
            'candidate_tf32_policy': 'disabled_highest_float32',
            'candidate_events_per_target': parent.CANDIDATE_COUNT,
            'candidate_eos_variant_count': manifest['scientific_access_cost']['eos_variant_count'],
            'candidate_prefix_states_per_target': parent.PREFIX_STATES,
            'generated_target_tokens': 0, 'neutral_and_oracle_access': 'unchanged and separately declared per tier'},
        'old_eighteen_feature_sets_and_labels_unchanged': True,
        'all_parent_feature_bytes_unchanged': True, 'new_language_model_queries': 0,
        'raw_response_payload_reads': 0, 'limitation': LIMITATION}
    data = {Path(config['feature_table']): payload,
        Path(config['feature_manifest']): (json.dumps(result, sort_keys=True, indent=2)+'\n').encode()}
    for path, content in data.items():
        if path.exists() and path.read_bytes() != content:
            raise ValueError('immutable joint feature artifact differs: '+str(path))
    for path, content in data.items():
        immutable(path, content)
    return result


def validate(spec):
    _discovery_declaration(spec)
    if spec.get('protocol') != protocol():
        raise ValueError('fixed joint prediction protocol differs')
    for key in ('source_pipeline_config', 'source_pipeline_receipt', 'output_dir', 'report'):
        _discovery_response_path(spec[key])
    for key in ('source_pipeline_config_sha256', 'source_pipeline_receipt_sha256'):
        _pin(spec.get(key), key)
    source = one_token._object(spec['source_pipeline_config'], spec['source_pipeline_config_sha256'])
    candidate_pipeline.validate(source)
    if any(spec.get(key) != source.get(key) for key in ('model', 'model_revision')):
        raise ValueError('joint pipeline checkpoint differs')
    out = Path(spec['output_dir']).resolve()
    source_out = Path(source['output_dir']).resolve()
    if out == source_out or source_out in out.parents or out in source_out.parents:
        raise ValueError('distinct nonoverlapping joint pipeline output directory required')
    return source


def fit(spec):
    from . import discovery_prediction as generic
    validate(spec)
    out = Path(spec['output_dir'])
    keys = ('model', 'model_revision', 'source_pipeline_config', 'source_pipeline_config_sha256',
            'source_pipeline_receipt', 'source_pipeline_receipt_sha256')
    collector = {key: spec[key] for key in keys}
    collector.update(feature_table=str(out/'inputs/features.jsonl'),
                     feature_manifest=str(out/'inputs/features.manifest.json'))
    # Metadata is validated before any new config/artifact is written.
    _metadata(collector)
    collector_path = out/'collection_config.json'
    _json(collector_path, collector)
    metadata = collect(collector)
    effective = {key: value for key, value in spec['protocol'].items() if key != 'comparisons'}
    effective.update(model=spec['model'], model_revision=spec['model_revision'],
        feature_table=collector['feature_table'], feature_table_sha256=metadata['sha256'],
        feature_manifest=collector['feature_manifest'], feature_manifest_sha256=sha(collector['feature_manifest']),
        collection_config=str(collector_path), output_dir=str(out/'cv'), run_dir=str(out/'cv'),
        review_artifact=str(out/'review_v1.json'), report=spec['report'])
    config = out/'effective_config.json'
    _json(config, effective)
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
        raise ValueError('fixed joint comparison protocol differs')
    for key in ('output_dir', 'comparison_report', 'decision_report', 'baseline_comparison', 'figure_png', 'figure_svg'):
        _discovery_response_path(spec[key])
    runs = {}
    for name, binding in spec['runs'].items():
        _discovery_response_path(binding['config'])
        run_spec = one_token._object(binding['config'], binding['sha256'])
        validate(run_spec)
        out = Path(run_spec['output_dir'])
        receipt = one_token._object(out/'pipeline_review_v1.json')
        if (receipt.get('status') != 'complete_exploratory' or receipt.get('config_hash') != digest(run_spec)
                or receipt.get('protocol_hash') != digest(protocol())):
            raise ValueError('completed matching joint model pipeline required')
        path = out/'effective_config.json'
        if receipt.get('effective_config') != {'path': str(path), 'sha256': sha(path)}:
            raise ValueError('joint effective fitting config identity changed')
        effective = one_token._object(path)
        artifact = effective['review_artifact']
        _discovery_response_path(artifact)
        if receipt.get('review') != {'path': artifact, 'sha256': sha(artifact)}:
            raise ValueError('completed joint fitting review identity changed')
        runs[name] = dict(config=str(path), sha256=sha(path))
    if len(runs) != 2:
        raise ValueError('two fixed checkpoint reviews required')
    out = Path(spec['output_dir'])
    comparison = dict(runs=runs, comparison_artifact=str(out/'comparison_v1.json'), report=spec['comparison_report'])
    _json(out/'comparison_config.json', comparison)
    generic.compare(comparison)
    rendering = dict(comparison_profile=PROFILE, comparison=comparison['comparison_artifact'],
        comparison_sha256=sha(comparison['comparison_artifact']), baseline_comparison=spec['baseline_comparison'],
        baseline_comparison_sha256=spec['baseline_comparison_sha256'], figure_png=spec['figure_png'],
        figure_svg=spec['figure_svg'], review_artifact=str(out/'anchor_figure_review_v1.json'))
    _json(out/'review_config.json', rendering)
    confidence_review.run(rendering)
    checked = one_token._object(rendering['review_artifact'])
    # A bounded per-model review is sufficient; the rich paired JSON can exceed
    # the metadata-reader limit and is not loaded to make the decision table.
    lines = ['# Joint next-token and finite-event confidence controls', '', LIMITATION, '',
        '| Checkpoint | Contrast | Left Brier | Joint Brier | Improvement [conditional 95%] | Left log loss | Joint log loss |',
        '|---|---|---:|---:|---|---:|---:|']
    table_pairs = set(PRIMARY_PAIRS+EVENT_PAIRS+tuple((a, j) for a, _, _, j in PAIRED_TIERS))
    for name, binding in runs.items():
        effective = one_token._object(binding['config'], binding['sha256'])
        review = one_token._object(effective['review_artifact'])
        metrics = next(row['metrics'] for row in review['per_seed_and_ensemble'] if row['scope'] == 'ensemble')
        rows = [row for row in review['contrasts'] if row['scope'] == 'ensemble' and (row['left'], row['right']) in table_pairs]
        if len(rows) != 15:
            raise ValueError('all fifteen fixed confidence/source-to-joint contrasts required')
        for row in rows:
            left, right = metrics[row['left']], metrics[row['right']]
            delta = row['brier_score']; low, high = delta['exploratory_template_bootstrap_95']
            lines.append(f"| {name} | {row['left']} → {row['right']} | {left['brier_score']:.6f} | {right['brier_score']:.6f} | {delta['mean']:+.6f} [{low:+.6f}, {high:+.6f}] | {left['log_loss']:.6f} | {right['log_loss']:.6f} |")
    count = sum(value['anchors']['probability_values_compared'] for value in checked['models'].values())
    lines += ['', f'All {count:,} parent-tier OOF probability values reproduce exactly, as do every saved parent fit, normalizer, penalty, inner curve, group assignment and fallback record.', '',
        'All 23 tiers and 55 contrasts, every fixed seed, calibration bin and descriptive cell remain in the full comparison and per-checkpoint reports. No checkpoint, seed or context was selected by result.', '']
    immutable(spec['decision_report'], '\n'.join(lines).encode())
    result = dict(status='complete_exploratory', complete=True, config_hash=digest(spec),
        comparison=rendering['comparison'], comparison_sha256=rendering['comparison_sha256'],
        anchor_review=rendering['review_artifact'], anchor_review_sha256=sha(rendering['review_artifact']),
        parent_probability_values_reproduced=count, decision_report=spec['decision_report'],
        generated_holdouts_opened=False, mechanism_C_fitted=False, model_loading=False)
    _json(out/'pipeline_review_v1.json', result)
    return result
