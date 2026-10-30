"""Frozen prediction scoring. Does not discover a mechanism or fit on final data."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from .datasets import digest, read_jsonl, write_json

REQUIRED = ('hypothesis', 'competing_explanations', 'primary_behavioral_endpoint',
            'primary_intervention_endpoint', 'intervention_controls', 'model_revision',
            'layers_and_sites', 'frozen_fitting_procedure', 'structural_predictions',
            'ambiguity_and_exclusion_rules', 'multiplicity_and_uncertainty',
            'feature_information_contract', 'additional_query_budgets', 'code_source_sha256',
            'dataset_sha256', 'registered_utc')


def registration(config, require_predictions=False):
    from .registry import code_identity
    path = Path(config['registration'])
    frozen = json.loads(path.read_text())
    if config.get('registration_sha256') != digest(frozen):
        raise ValueError('registration hash mismatch; freeze its contents in the run config')
    missing = [k for k in REQUIRED if not frozen.get(k)]
    if missing or frozen.get('status') != 'frozen':
        raise ValueError(f'analysis must be frozen with all scientific choices specified; missing={missing}')
    if frozen['model_revision'] != config['model_revision']:
        raise ValueError('registration model mismatch')
    if frozen['code_source_sha256'] != code_identity()['source_sha256']:
        raise ValueError('source changed after registration')
    manifest = json.loads(Path(config['dataset']).with_suffix('.manifest.json').read_text())
    if frozen['dataset_sha256'] != manifest['sha256']:
        raise ValueError('registered dataset mismatch')
    if frozen['primary_behavioral_endpoint'] != 'incorrect_including_invalid':
        raise ValueError('this evaluator implements incorrect_including_invalid; invalid outputs also reported separately')
    if require_predictions:
        forecasts = Path(config['frozen_predictions'])
        if config.get('frozen_predictions_sha256') != hashlib.sha256(forecasts.read_bytes()).hexdigest():
            raise ValueError('freeze forecast file before opening heldout behavior')
    return frozen, digest(frozen)


def probability_scores(probabilities, labels):
    p, y = np.asarray(probabilities, dtype=float), np.asarray(labels, dtype=float)
    if p.shape != y.shape or not len(p) or not np.isfinite(p).all() or ((p < 0) | (p > 1)).any() or not np.isin(y, [0,1]).all():
        raise ValueError('invalid forecast probabilities')
    safe = p.clip(1e-12, 1 - 1e-12)
    calibration = []
    bin_ids = np.minimum((p * 10).astype(int), 9)
    for i in range(10):
        mask = bin_ids == i
        calibration.append({'bin_start': i / 10, 'n': int(mask.sum()),
                            'mean_forecast': float(p[mask].mean()) if mask.any() else None,
                            'observed_error': float(y[mask].mean()) if mask.any() else None})
    return {'brier_score': float(((p - y)**2).mean()),
            'log_loss': float(-(y * np.log(safe) + (1-y) * np.log1p(-safe)).mean()),
            'calibration': calibration}


def evaluate(config):
    from .analysis import interval
    frozen, frozen_hash = registration(config)
    directory = Path(config['run_dir']) / 'heldout_evaluation'
    directory.mkdir(parents=True, exist_ok=True)
    forecast_path = Path(config['frozen_predictions'])
    file_hash = hashlib.sha256(forecast_path.read_bytes()).hexdigest()
    if config.get('frozen_predictions_sha256') != file_hash:
        raise ValueError('forecast file hash mismatch; freeze before observing behavior')
    forecasts = read_jsonl(forecast_path)
    observed = read_jsonl(config['heldout_responses'])
    records = {r['id']: r for r in read_jsonl(config['dataset']) if r['split'] == 'test'
               and r['control_kind'] == 'primary'}
    pred = {r['id']: r for r in forecasts}
    behavior = {r['id']: r for r in observed}
    if len(pred) != len(forecasts) or len(behavior) != len(observed) or set(pred) != set(records) or set(behavior) != set(records):
        raise ValueError('all primary heldout IDs must appear exactly once; no post-hoc exclusions')
    predictors = ('A_input', 'B_behavior', 'C_measurements', 'cheap_stress_test')
    ids = sorted(records)
    labels = [behavior[i]['prediction'] != records[i]['expected_answer'] for i in ids]
    clusters = [records[i]['cluster_id'] for i in ids]
    result = {'registration_sha256': frozen_hash, 'predictions_sha256': file_hash, 'n': len(ids),
              'invalid_outputs': sum(behavior[i]['prediction'] is None for i in ids),
              'error_rate': sum(labels)/len(labels), 'predictors': {},
              'additional_query_budgets': frozen['additional_query_budgets']}
    losses = {}
    for name in predictors:
        p = np.array([pred[i][name] for i in ids])
        result['predictors'][name] = probability_scores(p, labels)
        losses[name] = (p - np.array(labels)) ** 2
    result['brier_improvement_of_C'] = {
        name: interval(losses[name] - losses['C_measurements'], clusters)
        for name in ('A_input', 'B_behavior', 'cheap_stress_test')}
    result['interpretation'] = 'forecast scoring only; evidence of mechanism depends on registered intervention specificity'
    write_json(directory / 'scores.json', result)
    return result
