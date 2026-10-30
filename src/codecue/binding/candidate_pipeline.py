"""Frozen, staged CPU prediction after complete candidate-event measurements.

Metadata SHAs become known only when upstream runs finish. The feature/tier,
fold, cost and contrast policy is fixed in advance; effective configs pin the
completed inputs immutably before any fitting. This module never loads models.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import candidate_prediction as profile
from .datasets import digest,write_json
from .forecasting import _discovery_declaration,_discovery_response_path
from .published_benchmarks import immutable,sha


def protocol():
    return dict(feature_profile=profile.PROFILE,feature_information_contract=profile.predictor_columns(),
        predictor_access=profile.predictor_access(),comparisons=[list(pair) for pair in profile.predictor_comparisons()],
        seeds=[17,29,43],outer_folds=6,inner_folds=5,l2_grid=[.1,1.,10.,100.],
        bootstrap_replicates=2000,bootstrap_seed=117)


def _json(path,value):
    immutable(path,(json.dumps(value,sort_keys=True,indent=2)+'\n').encode())


def _object(path,expected=None):
    from .confidence_prediction import _object as read
    return read(path,expected)


def validate(spec):
    _discovery_declaration(spec)
    if spec.get('protocol')!=protocol():raise ValueError('fixed candidate-prediction protocol differs')
    for key in ('source_prediction_config','candidate_config','output_dir','report'):
        _discovery_response_path(spec[key])
    parent=_object(spec['source_prediction_config'],spec['source_prediction_config_sha256'])
    candidate=_object(spec['candidate_config'],spec['candidate_config_sha256'])
    for key in ('model','model_revision'):
        if spec.get(key)!=parent.get(key) or spec.get(key)!=candidate.get(key):
            raise ValueError('pipeline checkpoints differ')
    if parent.get('feature_profile')!='confidence_access_v1':raise ValueError('completed thirteen-tier parent required')
    if candidate.get('case_limit') is not None or candidate.get('measurement_dtype')!='float32':
        raise ValueError('complete FP32 candidate collection required')
    out=Path(spec['output_dir']).resolve()
    for path in (parent['output_dir'],candidate['run_dir']):
        if out==Path(path).resolve():raise ValueError('new pipeline output directory required')
    return parent,candidate


def fit(spec):
    from . import discovery_prediction
    parent,candidate=validate(spec);out=Path(spec['output_dir']);stage=Path(candidate['run_dir'])/'candidate_measurement'
    # Validate compact completion metadata before collector configs or payload reads.
    manifest=_object(stage/'manifest.json');summary=_object(stage/'summary.json');audit=_object(stage/'audit.json')
    if (manifest.get('status')!='complete' or summary.get('complete') is not True
            or audit.get('status')!='passed' or audit.get('evaluated')!=6144):
        raise ValueError('complete candidate measurement and audit required before staged fitting')
    collect=dict(model=spec['model'],model_revision=spec['model_revision'],
        source_prediction_config=spec['source_prediction_config'],
        source_prediction_config_sha256=spec['source_prediction_config_sha256'],
        candidate_config=spec['candidate_config'],candidate_config_sha256=spec['candidate_config_sha256'],
        candidate_manifest_sha256=sha(stage/'manifest.json'),candidate_summary_sha256=sha(stage/'summary.json'),
        candidate_audit_sha256=sha(stage/'audit.json'),
        feature_table=str(out/'inputs/features.jsonl'),feature_manifest=str(out/'inputs/features.manifest.json'))
    collect_path=out/'collection_config.json';_json(collect_path,collect)
    profile.collect(collect);metadata=_object(collect['feature_manifest'])
    effective={key:value for key,value in spec['protocol'].items() if key!='comparisons'}
    effective.update(model=spec['model'],model_revision=spec['model_revision'],
        feature_table=collect['feature_table'],feature_table_sha256=metadata['sha256'],
        feature_manifest=collect['feature_manifest'],feature_manifest_sha256=sha(collect['feature_manifest']),
        output_dir=str(out/'cv'),run_dir=str(out/'cv'),review_artifact=str(out/'review_v1.json'),report=spec['report'],
        collection_config=str(collect_path),source_prediction_config=spec['source_prediction_config'],
        source_prediction_config_sha256=spec['source_prediction_config_sha256'])
    config=out/'effective_config.json';_json(config,effective)
    discovery_prediction.run(effective)
    result=dict(status='complete_exploratory',config_hash=digest(spec),protocol_hash=digest(spec['protocol']),
        collection_config=dict(path=str(collect_path),sha256=sha(collect_path)),
        effective_config=dict(path=str(config),sha256=sha(config)),
        review=dict(path=effective['review_artifact'],sha256=sha(effective['review_artifact'])),
        generated_holdouts_opened=False,mechanism_C_fitted=False,model_loading=False)
    _json(out/'pipeline_review_v1.json',result)
    return result


def compare(spec):
    from . import discovery_prediction,confidence_review
    _discovery_declaration(spec)
    if spec.get('protocol')!=protocol():raise ValueError('fixed comparison protocol differs')
    for key in ('output_dir','comparison_report','decision_report','baseline_comparison','figure_png','figure_svg'):
        _discovery_response_path(spec[key])
    runs={}
    for name,binding in spec['runs'].items():
        run_spec=_object(binding['config'],binding['sha256']);validate(run_spec)
        out=Path(run_spec['output_dir']);review=_object(out/'pipeline_review_v1.json')
        if review.get('status')!='complete_exploratory' or review.get('config_hash')!=digest(run_spec):
            raise ValueError('completed matching model pipeline required')
        config=out/'effective_config.json'
        if review['effective_config']!={'path':str(config),'sha256':sha(config)}:
            raise ValueError('effective fitting config identity changed')
        effective=_object(config)
        artifact=effective['review_artifact'];_discovery_response_path(artifact)
        if review.get('review')!={'path':artifact,'sha256':sha(artifact)}:
            raise ValueError('completed fitting review identity changed')
        runs[name]=dict(config=str(config),sha256=sha(config))
    if len(runs)!=2:raise ValueError('two fixed checkpoints required')
    out=Path(spec['output_dir']);comparison=dict(runs=runs,
        comparison_artifact=str(out/'comparison_v1.json'),report=spec['comparison_report'])
    _json(out/'comparison_config.json',comparison);discovery_prediction.compare(comparison)
    rendering=dict(comparison_profile='candidate_event_v1',comparison=comparison['comparison_artifact'],
        comparison_sha256=sha(comparison['comparison_artifact']),
        baseline_comparison=spec['baseline_comparison'],baseline_comparison_sha256=spec['baseline_comparison_sha256'],
        figure_png=spec['figure_png'],figure_svg=spec['figure_svg'],review_artifact=str(out/'anchor_figure_review_v1.json'))
    _json(out/'review_config.json',rendering);confidence_review.run(rendering)
    checked=_object(rendering['review_artifact'])
    lines=['# Candidate-event versus next-token confidence bundles','',profile.LIMITATION,'',
        '| Checkpoint | Context | Next-token Brier | Event Brier | Improvement [conditional 95%] | Next-token log loss | Event log loss |',
        '|---|---|---:|---:|---|---:|---:|']
    for name,result in checked['models'].items():
        for row in result['contrasts']:
            left=result['metrics'][row['left']];right=result['metrics'][row['right']];delta=row['brier_score']
            low,high=delta['exploratory_template_bootstrap_95']
            lines.append(f"| {name} | {row['left']} → {row['right']} | {left['brier_score']:.6f} | {right['brier_score']:.6f} | {delta['mean']:+.6f} [{low:+.6f}, {high:+.6f}] | {left['log_loss']:.6f} | {right['log_loss']:.6f} |")
    anchors=sum(model['anchors']['probability_values_compared'] for model in checked['models'].values())
    lines+=['',f'All {anchors:,} parent-tier OOF probabilities reproduce exactly, as do saved fitting parameters, normalizers, penalties, inner curves, group assignments and baseline fallback records.','',
        'Every one of the 18 tiers, 37 fixed contrasts, descriptive cells and calibration bins remains in the full comparison and per-checkpoint reports. No best seed, checkpoint or context is selected. These are alternatives changing finite-event support, FP32 execution and encoding; they do not identify a pure information increment or a causal binding mechanism.','']
    immutable(spec['decision_report'],'\n'.join(lines).encode())
    result=dict(status='complete_exploratory',complete=True,config_hash=digest(spec),
        comparison=rendering['comparison'],comparison_sha256=rendering['comparison_sha256'],
        anchor_review=rendering['review_artifact'],anchor_review_sha256=sha(rendering['review_artifact']),
        parent_probability_values_reproduced=anchors,decision_report=spec['decision_report'],
        generated_holdouts_opened=False,mechanism_C_fitted=False,model_loading=False)
    _json(out/'pipeline_review_v1.json',result)
    return result
