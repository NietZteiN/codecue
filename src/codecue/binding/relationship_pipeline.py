"""Frozen CPU continuation from completed capture to the fixed readout recipe.

Only completed capture metadata hashes are resolved at runtime. Features,
targets, fitting policy, output paths and protocol cannot be changed by that
resolution. The controller calls no scheduler and loads no model or tokenizer.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import relationship_capture as capture
from .datasets import digest

ROLE = 'discovery_relationship_pipeline_v1'


def _readouts():
    from . import relationship_readouts
    return relationship_readouts


def _guards(config, *, scheduled):
    required = {'evaluation_role', 'capture_config', 'capture_config_sha256', 'readout_run_dir',
        'readout_report', 'pipeline_run_dir', 'expected_readout_protocol_sha256', 'declared_plan', 'declared_plan_sha256'}
    if not isinstance(config, dict) or set(config) != required or config.get('evaluation_role') != ROLE:
        raise ValueError('exact discovery relationship pipeline template required')
    if len(json.dumps(config, allow_nan=False).encode()) > 16 * 1024:
        raise ValueError('bounded pipeline template required')
    for key in ('capture_config_sha256', 'expected_readout_protocol_sha256', 'declared_plan_sha256'):
        value = config[key]
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('explicit source, plan and protocol SHA256 pins required')
    for key in ('capture_config', 'readout_run_dir', 'readout_report', 'pipeline_run_dir', 'declared_plan'):
        if not isinstance(config[key], str): raise ValueError('explicit pipeline source/output paths required')
        capture._safe(config[key])
    if scheduled:
        capture._slurm()
        source = capture._current_source(config)  # Exact frozen template for execution.
    else:
        # A read-only workspace audit follows the original frozen source rather
        # than demanding that today's reader itself execute inside that snapshot.
        # Validate the bounded resolution/template before trusting its pointer.
        saved = capture._json(Path(config['pipeline_run_dir'])/'resolution_review.json')
        if (saved.get('status') != 'passed' or saved.get('evaluation_role') != ROLE
                or saved.get('config_hash') != digest(config) or saved.get('template') != config):
            raise ValueError('original pipeline resolution/template identity differs')
        source = saved.get('pipeline_source')
        source_keys = {'snapshot', 'snapshot_id', 'source_sha256', 'frozen_manifest_sha256'}
        if (not isinstance(source, dict) or set(source) != source_keys
                or any(not isinstance(value, str) or not value for value in source.values())):
            raise ValueError('explicit original frozen pipeline source required')
        capture._verify_source(config, source)
    if digest(_readouts().protocol()) != config['expected_readout_protocol_sha256']:
        raise ValueError('declared fixed readout protocol differs')
    plan = capture._bytes(config['declared_plan'], 1024**2)
    if hashlib.sha256(plan).hexdigest() != config['declared_plan_sha256']:
        raise ValueError('declared prospective plan checksum differs')
    cap = capture._json(config['capture_config'], config['capture_config_sha256'])
    _, capture_folder = capture._config(cap)
    folders = [Path(config[key]).resolve() for key in ('readout_run_dir', 'pipeline_run_dir')] + [capture_folder.resolve()]
    if any(a == b or a in b.parents or b in a.parents for i, a in enumerate(folders) for b in folders[i + 1:]):
        raise ValueError('pipeline, readout and capture directories must not overlap')
    report = Path(config['readout_report']).resolve()
    if (report.suffix != '.md' or report == Path(config['declared_plan']).resolve()
            or report == Path(config['capture_config']).resolve() or folders[2] in report.parents):
        raise ValueError('readout report cannot replace a source artifact')
    return cap, source


def _resolve(config, *, scheduled):
    cap, source = _guards(config, scheduled=scheduled)
    checked = capture.completed_metadata(cap)
    folder = Path(cap['run_dir']); metadata = checked['receipt']['metadata']
    resolved = dict(evaluation_role=_readouts().ROLE, capture_config=config['capture_config'],
        capture_config_sha256=config['capture_config_sha256'], run_dir=config['readout_run_dir'],
        report=config['readout_report'], **_readouts().protocol())
    for key, filename in (('capture_audit', 'audit.json'), ('capture_registration', 'registration.json'), ('capture_summary', 'summary.json')):
        entry = metadata[filename]
        if entry['path'] != str(folder/filename) or capture._sha(entry['path']) != entry['sha256']:
            raise ValueError('resolved capture metadata must match its named completion entry')
        resolved[key], resolved[key + '_sha256'] = entry['path'], entry['sha256']
    payload = (json.dumps(resolved, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    resolution = dict(status='passed', evaluation_role=ROLE, config_hash=digest(config),
        template=config, pipeline_source=source, protocol_sha256=config['expected_readout_protocol_sha256'],
        declared_plan={'path': config['declared_plan'], 'sha256': config['declared_plan_sha256']},
        capture_completion={'path': str(folder/'completion_manifest_v1.json'), 'sha256': capture._sha(folder/'completion_manifest_v1.json')},
        resolved_config={'path': str(Path(config['pipeline_run_dir'])/'resolved_config.json'),
            'sha256': hashlib.sha256(payload).hexdigest(), 'config_hash': digest(resolved)},
        resolved_metadata={key: metadata[key] for key in ('audit.json', 'registration.json', 'summary.json')},
        capture_source=checked['source'], source_model_prefill_cases=checked['summary']['model_prefill_cases'],
        new_model_queries=0, nested_jobs_submitted=0, generated_holdouts_opened=False)
    return resolved, resolution, payload


def _pin(path):
    return {'path': str(path), 'sha256': capture._sha(path)}


def _audit(config, resolved, resolution):
    folder = Path(config['pipeline_run_dir'])
    if capture._json(folder/'resolution_review.json') != resolution:
        raise ValueError('pipeline resolution identity differs')
    if capture._json(folder/'resolved_config.json', resolution['resolved_config']['sha256']) != resolved:
        raise ValueError('resolved fixed readout configuration differs')
    review = capture._json(folder/'pipeline_review_v1.json')
    if (review.get('status') != 'complete_exploratory' or review.get('evaluation_role') != ROLE
            or review.get('config_hash') != digest(config) or review.get('resolution') != resolution
            or review.get('new_model_queries') != 0 or review.get('nested_jobs_submitted') != 0
            or review.get('generated_holdouts_opened') is not False):
        raise ValueError('complete matching discovery pipeline review required')
    expected = {'resolution': folder/'resolution_review.json', 'preflight': folder/'preflight_review.json',
        'readout_completion': Path(resolved['run_dir'])/'completion_manifest_v1.json',
        'readout_audit': Path(resolved['run_dir'])/'audit.json'}
    if set(review.get('artifacts', {})) != set(expected): raise ValueError('exact pipeline evidence inventory required')
    for key, path in expected.items():
        if review['artifacts'][key] != _pin(path): raise ValueError('pipeline evidence checksum differs')
    result = _readouts().completed_result(resolved)
    checked = _readouts().audit(resolved)
    if (checked.get('status') != 'passed' or result.get('status') != 'complete_exploratory'
            or review.get('readout_verification') != checked
            or any(review.get(key) != result.get(key) for key in ('factorizations', 'parameter_replay_rows', 'primary'))):
        raise ValueError('completed readout verification failed')
    return review


def run(config):
    resolved, resolution, _ = _resolve(config, scheduled=True)
    folder = Path(config['pipeline_run_dir'])
    if (folder/'pipeline_review_v1.json').exists(): return _audit(config, resolved, resolution)
    capture._put(folder/'resolved_config.json', resolved)
    capture._put(folder/'resolution_review.json', resolution)
    preflight = _readouts().preflight(resolved)
    if preflight.get('status') != 'passed': raise ValueError('fixed readout preflight failed')
    capture._put(folder/'preflight_review.json', preflight)
    result = _readouts().run(resolved)
    checked = _readouts().audit(resolved)
    if result.get('status') != 'complete_exploratory' or checked.get('status') != 'passed':
        raise ValueError('fixed readout run/audit failed')
    paths = {'resolution': folder/'resolution_review.json', 'preflight': folder/'preflight_review.json',
        'readout_completion': Path(resolved['run_dir'])/'completion_manifest_v1.json',
        'readout_audit': Path(resolved['run_dir'])/'audit.json'}
    review = dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=digest(config),
        resolution=resolution, artifacts={key: _pin(path) for key, path in paths.items()},
        readout_verification=checked, factorizations=result['factorizations'],
        parameter_replay_rows=result['parameter_replay_rows'], primary=result['primary'],
        new_model_queries=0, nested_jobs_submitted=0, generated_holdouts_opened=False)
    capture._put(folder/'pipeline_review_v1.json', review)
    return review


def audit(config):
    resolved, resolution, _ = _resolve(config, scheduled=False)
    return _audit(config, resolved, resolution)
