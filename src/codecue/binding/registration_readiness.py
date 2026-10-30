"""Metadata-only registration lint and an inert prerequisite DAG.

No dataset body, target feature table, predictions, responses or scores is opened.
A successful review is a metadata prerequisite check, not scientific support or
permission to collect a final outcome. Query budgets concern information access;
they never impose a GPU or project compute limit.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import stat

from .datasets import digest, write_json
from .heldout import REQUIRED

ROLE = 'forecast_registration_metadata_readiness_v1'
MAX_METADATA_BYTES = 1024 * 1024
PREDICTORS = ('A_input', 'B_behavior', 'C_measurements', 'cheap_stress_test')
_HASH = re.compile(r'^[0-9a-f]{64}$')
_REVISION = re.compile(r'^(?:[0-9a-f]{40}|[0-9a-f]{64})$')
_BULK_KEYS = {'raw_response', 'raw_responses', 'prediction', 'predictions', 'responses',
              'observed_outcomes', 'outcomes', 'scores', 'metrics', 'summary', 'results',
              'expected_answer', 'target_label', 'labels'}
_PLACEHOLDERS = {'tbd', 'todo', 'pending', 'unknown', 'not selected', 'not specified',
                 'placeholder', 'n/a', 'draft'}


def _present(value):
    if isinstance(value, str): return bool(value.strip()) and value.strip().lower() not in _PLACEHOLDERS
    return bool(value)


def _metadata_path(value):
    original = Path(value)
    resolved = original.resolve()
    for path in (original, resolved):
        if path.suffix.lower() != '.json':
            raise ValueError('metadata inputs must be JSON objects, never bulk payload files')
        stem = path.stem.lower().replace('-', '_')
        if re.search(r'(?:^|_)(?:raw|responses?|predictions?|outcomes?|scores?|summary|metrics|results)(?:_|$)', stem):
            raise ValueError('outcome, prediction and summary files cannot be metadata inputs')
    return resolved


def _reject_bulk_content(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in _BULK_KEYS or (key in ('rows', 'records') and isinstance(child, (list, dict))):
                raise ValueError('metadata input contains outcome or bulk-summary content: ' + str(key))
            _reject_bulk_content(child)
    elif isinstance(value, list):
        for child in value: _reject_bulk_content(child)


def _read_metadata(path, limit, reads):
    path = _metadata_path(path)
    metadata = path.stat()
    if not stat.S_ISREG(metadata.st_mode): raise ValueError('metadata input must be a regular JSON file')
    if metadata.st_size > limit: raise ValueError('metadata input exceeds byte limit')
    with path.open('rb') as stream: payload = stream.read(limit + 1)
    if len(payload) > limit: raise ValueError('metadata input exceeds byte limit')
    result = json.loads(payload)
    if not isinstance(result, dict): raise ValueError('metadata input must contain one JSON object')
    _reject_bulk_content(result)
    reads.append({'path': str(path), 'bytes': len(payload), 'kind': 'bounded_metadata_json'})
    return result


def load_config(path):
    """Apply the same bounded metadata boundary to the CLI configuration file."""
    config = _read_metadata(path, MAX_METADATA_BYTES, [])
    config['_configuration_path'] = str(Path(path).resolve())
    return config


def _dag():
    return [
        {'id': 'registration', 'depends_on': [], 'prerequisite': 'scientific choices supported and registration frozen', 'execute': False},
        {'id': 'frozen_measurements_and_forecasts', 'depends_on': ['registration'], 'prerequisite': 'registered access contract; forecasts frozen and hash pinned before new target outcomes', 'execute': False},
        {'id': 'new_heldout_responses', 'depends_on': ['frozen_measurements_and_forecasts'], 'prerequisite': 'separate authorized collection after forecast freeze; no previous target-outcome access', 'execute': False},
        {'id': 'scoring', 'depends_on': ['new_heldout_responses'], 'prerequisite': 'registered evaluator and exact primary-ID coverage', 'execute': False},
    ]


def review(config):
    """Read only declared bounded metadata and return an inert readiness review."""
    limit = config.get('max_metadata_bytes', MAX_METADATA_BYTES)
    if type(limit) is not int or not 1 <= limit <= MAX_METADATA_BYTES:
        raise ValueError('max_metadata_bytes must be an integer from 1 to 1048576')
    reads = []; issues = []; checks = []
    def check(name, valid, detail):
        checks.append({'check': name, 'passed': bool(valid), 'detail': detail})
        if not valid: issues.append({'check': name, 'detail': detail})

    frozen = _read_metadata(config['registration'], limit, reads)
    run = _read_metadata(config['run_config'], limit, reads) if config.get('run_config') else {}
    missing = [key for key in REQUIRED if not _present(frozen.get(key))]
    check('required_fields', not missing, 'missing or placeholder fields: ' + ', '.join(missing))
    invalid_types = [key for key in REQUIRED if _present(frozen.get(key))
                     and not isinstance(frozen[key], (str, list, dict))]
    check('required_field_types', not invalid_types, 'scientific choices must be explicit text or structured metadata: ' + ', '.join(invalid_types))
    state = frozen.get('status', 'draft')
    check('frozen_status', state == 'frozen', 'status must explicitly be frozen; draft never passes')
    check('supported_account', config.get('supported_account') is True,
          'supported_account must explicitly be true; this utility does not establish a mechanism')
    check('run_config', bool(run), 'run_config metadata is required to check evaluator bindings')
    registration_hash = digest(frozen)
    if run:
        check('registration_sha256', bool(_HASH.fullmatch(str(run.get('registration_sha256', ''))))
              and run.get('registration_sha256') == registration_hash,
              'run.registration_sha256 must pin the semantic digest of registration JSON')
        if run.get('registration'):
            check('registration_path', Path(run['registration']).resolve() == Path(config['registration']).resolve(),
                  'run registration path must identify the reviewed registration')

    revision = frozen.get('model_revision')
    check('model_revision_pinned', bool(_REVISION.fullmatch(str(revision or ''))),
          'model_revision must be an immutable 40- or 64-character hexadecimal revision')
    if run:
        check('model_revision_matches', revision == run.get('model_revision') and _present(revision),
              'registration and run must identify the same checkpoint revision')
        if frozen.get('model'):
            check('model_name_matches', frozen['model'] == run.get('model'), 'registered model name must match run model')
    checkpoint = frozen.get('checkpoint_identity')
    if checkpoint is not None:
        check('checkpoint_identity', isinstance(checkpoint, dict) and _present(checkpoint.get('model'))
              and checkpoint.get('revision') == revision
              and checkpoint.get('model') == run.get('model', frozen.get('model')),
              'declared checkpoint identity must bind the same model and pinned revision')
    if frozen.get('tokenizer_revision') is not None:
        tokenizer = frozen['tokenizer_revision']
        check('tokenizer_revision', bool(_REVISION.fullmatch(str(tokenizer)))
              and (not run or tokenizer == run.get('tokenizer_revision')),
              'declared tokenizer revision must be pinned and agree with the run')

    from .registry import code_identity
    current_source = code_identity()['source_sha256']
    source_hash = frozen.get('code_source_sha256')
    check('code_source_sha256', bool(_HASH.fullmatch(str(source_hash or ''))) and source_hash == current_source,
          'registration code digest must match current analysis source identity')
    if run.get('code_source_sha256') is not None:
        check('run_code_source_sha256', run['code_source_sha256'] == source_hash,
              'run code source declaration must agree with registration')

    manifest_ref = config.get('dataset_manifest', run.get('dataset_manifest'))
    if manifest_ref is None and run.get('dataset'):
        manifest_ref = str(Path(run['dataset']).with_suffix('.manifest.json'))
    if isinstance(manifest_ref, dict):
        _reject_bulk_content(manifest_ref); manifest = dict(manifest_ref)
        check('inline_manifest_size', len(json.dumps(manifest).encode()) <= limit, 'inline dataset metadata must fit byte limit')
    elif manifest_ref is not None: manifest = _read_metadata(manifest_ref, limit, reads)
    else: manifest = {}
    check('dataset_manifest_metadata', bool(_HASH.fullmatch(str(manifest.get('sha256', ''))))
          and isinstance(manifest.get('evaluation_role'), str) and bool(manifest.get('evaluation_role', '').strip()),
          'dataset manifest metadata must declare a SHA-256 and evaluation_role; dataset body is not read')
    dataset_hash = frozen.get('dataset_sha256')
    check('dataset_sha256', bool(_HASH.fullmatch(str(dataset_hash or ''))) and dataset_hash == manifest.get('sha256'),
          'registration dataset digest must match declared dataset manifest metadata')
    if run.get('dataset_sha256') is not None:
        check('run_dataset_sha256', run['dataset_sha256'] == dataset_hash, 'run dataset digest must agree with registration')
    declared_role = frozen.get('dataset_evaluation_role', run.get('dataset_evaluation_role'))
    if declared_role is not None:
        check('dataset_evaluation_role', declared_role == manifest.get('evaluation_role'), 'dataset role declarations must match')

    check('behavioral_endpoint', frozen.get('primary_behavioral_endpoint') == 'incorrect_including_invalid',
          'existing heldout evaluator implements incorrect_including_invalid')
    registered = frozen.get('registered_utc')
    try:
        timestamp = datetime.fromisoformat(str(registered).replace('Z', '+00:00'))
        valid_timestamp = timestamp.utcoffset() is not None and timestamp.utcoffset().total_seconds() == 0
    except (TypeError, ValueError): valid_timestamp = False
    check('registered_utc', valid_timestamp, 'registered_utc must be an explicit UTC timestamp')

    procedure = frozen.get('frozen_fitting_procedure')
    check('fit_manifest_digest', isinstance(procedure, dict)
          and bool(_HASH.fullmatch(str(procedure.get('fit_manifest_sha256', '')))),
          'forecasting requires a pinned fit_manifest_sha256; fitted model contents are not read')
    contract = frozen.get('feature_information_contract')
    features = contract.get('features') if isinstance(contract, dict) else None
    try:
        from .forecasting import validate_contract
        validate_contract(features)
        valid_features = True; feature_detail = 'four existing predictors have nested, outcome-free feature lists'
    except (ValueError, TypeError, KeyError) as exc:
        valid_features = False; feature_detail = str(exc)
    check('feature_information_contract', valid_features, feature_detail)
    _check_costs(contract, frozen.get('additional_query_budgets'), check)

    predictions = {'declared': False, 'contents_read': False, 'content_hash_verified': False}
    prediction_path = run.get('frozen_predictions', config.get('frozen_predictions'))
    prediction_hash = run.get('frozen_predictions_sha256', config.get('frozen_predictions_sha256'))
    if prediction_path:
        path = Path(prediction_path)
        exists = path.exists(); regular = path.is_file() if exists else False
        predictions.update(declared=True, path=str(path), exists=exists, is_file=regular,
                           declared_sha256=prediction_hash,
                           declared_hash_shape_valid=bool(_HASH.fullmatch(str(prediction_hash or ''))))
        if exists: predictions['size_bytes'] = path.stat().st_size
        check('frozen_predictions_declaration', regular and predictions['declared_hash_shape_valid'],
              'declared forecasts must exist with a SHA-256-shaped hash; content and hash remain unverified')
    elif prediction_hash is not None:
        check('frozen_predictions_declaration', False, 'a forecast hash without its declared path is incomplete')

    eligibility = not issues
    return {'status': 'metadata_ready' if eligibility else ('draft' if state != 'frozen' else 'frozen_not_ready'),
        'evaluation_role': ROLE, 'registration_state': state, 'missing_fields': missing,
        'required_fields': list(REQUIRED), 'checks': checks, 'issues': issues,
        'eligibility_ready': eligibility, 'supported_account': config.get('supported_account') is True,
        'registration': str(config['registration']), 'registration_semantic_sha256': registration_hash,
        'current_code_source_sha256': current_source, 'dataset_metadata': {
            'sha256': manifest.get('sha256'), 'evaluation_role': manifest.get('evaluation_role'), 'body_read': False},
        'frozen_predictions': predictions, 'metadata_reads': reads, 'prerequisite_dag': _dag(),
        'declared_payload_paths': {key: run[key] for key in
            ('dataset', 'heldout_responses', 'frozen_predictions') if run.get(key)},
        'actions_taken': [], 'model_loads': 0, 'submissions': 0,
        'dataset_body_read': False, 'heldout_outcomes_read': False, 'raw_predictions_read': False,
        'heldout_authorized': False, 'automatic_execution_enabled': False,
        'query_budget_scope': 'information-access query costs only; no project compute or GPU limit',
        'limitation': 'Metadata readiness does not verify scientific support, forecast contents, first-access ordering or primary-ID coverage. It does not authorize or execute final collection, scoring, pooling or model inference.'}


def _check_costs(contract, budgets, check):
    def amount(value, names):
        if isinstance(value, dict):
            candidates = [value[key] for key in names if key in value]
            if not candidates or any(item != candidates[0] for item in candidates): return None
            value = candidates[0]
        return value if type(value) in (int, float) and 0 <= value < float('inf') else None
    if not isinstance(budgets, dict): budgets = {}
    maxima = {name: amount(budgets.get(name), ('maximum_queries_per_target', 'max_queries_per_target', 'queries_per_target'))
              for name in PREDICTORS}
    check('query_budget_declarations', all(value is not None for value in maxima.values()),
          'declare nonnegative per-target additional-query budgets for all four predictors')
    if not isinstance(contract, dict): return
    check('target_outcome_access', contract.get('target_outcomes_allowed') is not True,
          'forecast features cannot permit target outcomes before forecast freeze')
    access = contract.get('access', {})
    if not isinstance(access, dict):
        check('access_contract', False, 'optional access declarations must be a predictor mapping'); return
    for name, declaration in access.items():
        if name not in PREDICTORS or not isinstance(declaration, dict):
            check('access_' + str(name), False, 'access declarations must identify a registered predictor'); continue
        cost = amount(declaration, ('queries_per_target', 'additional_queries_per_target'))
        check('access_cost_' + name, cost is not None and maxima[name] is not None and cost <= maxima[name],
              'declared access cost must be nonnegative and fit its registered information-query budget')
        if declaration.get('kind') == 'input_only':
            check('input_only_access_' + name, cost == 0, 'input-only access cannot require model queries')
        check('access_outcomes_' + name, declaration.get('target_outcomes') is not True,
              'access declarations cannot use target outcomes before forecast freeze')


def build(config):
    """Write only the requested review/report; never execute prerequisite nodes."""
    result = review(config)
    output = Path(config['output_review']); report = Path(config['report']) if config.get('report') else None
    if output.suffix != '.json' or (report is not None and report.suffix != '.md'):
        raise ValueError('readiness outputs must be JSON review and optional Markdown report')
    inputs = {Path(item['path']).resolve() for item in result['metadata_reads']}
    inputs.add(Path(config['registration']).resolve())
    if config.get('_configuration_path'): inputs.add(Path(config['_configuration_path']).resolve())
    if result['frozen_predictions'].get('path'): inputs.add(Path(result['frozen_predictions']['path']).resolve())
    inputs.update(Path(path).resolve() for path in result['declared_payload_paths'].values())
    outputs = [output.resolve()] + ([report.resolve()] if report else [])
    if len(set(outputs)) != len(outputs) or any(path in inputs for path in outputs):
        raise ValueError('readiness outputs must not overwrite metadata or declared payload inputs')
    write_json(output, result)
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        lines = ['# Forecast registration metadata readiness', '',
                 f"State: {result['status']}; metadata eligibility ready: {result['eligibility_ready']}.", '',
                 result['limitation'], '', 'Missing scientific choices: ' + (', '.join(result['missing_fields']) or 'none'), '',
                 '| Check | Passed | Detail |', '|---|---|---|']
        lines += [f"| {item['check']} | {item['passed']} | {item['detail'].replace('|', '/')} |" for item in result['checks']]
        lines += ['', 'Dry-run ordering: registration → frozen measurements/forecasts → new heldout responses → scoring.',
                  'No prerequisite node was executed. No model, dataset body, forecast content or outcome was read.', '']
        report.write_text('\n'.join(lines))
    return result
