"""Posthoc controls on pinned relationship scores; no activations or refitting."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path

import numpy as np

from . import relationship_capture as capture, relationship_readouts as readouts
from . import relationship_targets as target
from .datasets import digest

ROLE = 'posthoc_discovery_relationship_score_controls_v1'
MAX_BANK_BYTES = 64 * 1024**2
PAIR_MANIFEST_SHA256 = '3ebb5b5bf637c52b67d1f08cd44b5ee570ba57999e9681ff401258bb43834af1'
LIMITATION = (
    'Posthoc exploratory controls selected after inspecting the original discovery '
    'results, on the same nine development components. These are not new '
    'confirmatory tests. Original primary comparisons and artifacts are preserved. '
    'A strong source-value comparator diagnoses decoder accessibility, not a '
    'dedicated relational representation. State-matched provenance pairs differ '
    'in an explicit source copy and do not establish natural causal use. Seeds '
    'and lexical relatives are not independent replications. No raw activation '
    'arrays, model calls, refits or sealed outcomes are used.'
)


def protocol():
    return dict(layer=24, sites=[3, 7, 8], seeds=list(readouts.SEEDS),
        backends=['hidden', 'surface'], selected_score_banks=18,
        algebraic_contrast='hidden_direct_minus_source_categorical_value_derived',
        bootstrap=readouts.BOOTSTRAP, provenance_sites=[7, 8],
        unconstrained_graph_threshold=0.5, posthoc=True)


def _config(config):
    required = {'evaluation_role', 'pipeline_config', 'pipeline_config_sha256',
        'pipeline_review', 'pipeline_review_sha256', 'readout_completion',
        'readout_completion_sha256', 'declared_plan', 'declared_plan_sha256', 'run_dir', 'report'}
    if not isinstance(config, dict) or set(config) != required or config.get('evaluation_role') != ROLE:
        raise ValueError('exact posthoc discovery score-control configuration required')
    for key in required - {'evaluation_role'}:
        value = config[key]
        if not isinstance(value, str) or not value: raise ValueError('explicit path or SHA256 required')
        if key.endswith('_sha256'):
            if len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
                raise ValueError('explicit SHA256 pins required')
        else: capture._safe(value)
    out, report = Path(config['run_dir']).resolve(), Path(config['report']).resolve()
    reserved = {out/name for name in ('registration.json', 'pairs_review_v1.json',
        'results_v1.json', 'completion_manifest_v1.json')}
    sources = {Path(config[key]).resolve() for key in ('pipeline_config', 'pipeline_review', 'readout_completion', 'declared_plan')}
    if (report.suffix != '.md' or report == out or report in reserved | sources
            or any(p in report.parents for p in reserved)
            or any(out == p or out in p.parents for p in sources)):
        raise ValueError('posthoc output cannot replace source or reserved artifacts')


def _inputs(config):
    _config(config)
    if hashlib.sha256(capture._bytes(config['declared_plan'],1024**2)).hexdigest()!=config['declared_plan_sha256']:
        raise ValueError('declared posthoc control plan checksum differs')
    pipe = capture._json(config['pipeline_config'], config['pipeline_config_sha256'])
    review = capture._json(config['pipeline_review'], config['pipeline_review_sha256'])
    expected_review = Path(pipe['pipeline_run_dir'])/'pipeline_review_v1.json'
    if (pipe.get('evaluation_role') != 'discovery_relationship_pipeline_v1'
            or review.get('evaluation_role') != 'discovery_relationship_pipeline_v1'
            or Path(config['pipeline_review']).resolve() != expected_review.resolve()
            or review.get('status') != 'complete_exploratory' or review.get('config_hash') != digest(pipe)
            or review.get('resolution', {}).get('template') != pipe):
        raise ValueError('complete matching original pipeline review required')
    capture._verify_source(pipe, review['resolution']['pipeline_source'])
    resolved_entry = review['resolution']['resolved_config']
    resolved_path = Path(pipe['pipeline_run_dir'])/'resolved_config.json'
    if Path(resolved_entry['path']).resolve() != resolved_path.resolve():
        raise ValueError('original resolved configuration path differs')
    resolved = capture._json(resolved_path, resolved_entry['sha256'])
    out, report = Path(config['run_dir']).resolve(), Path(config['report']).resolve()
    if report in {Path(pipe['declared_plan']).resolve(), Path(resolved['report']).resolve()}:
        raise ValueError('posthoc report cannot replace original plan or report')
    expected_receipt = Path(resolved['run_dir'])/readouts.COMPLETION_NAME
    if (Path(config['readout_completion']).resolve() != expected_receipt.resolve()
            or review['artifacts']['readout_completion']['sha256'] != config['readout_completion_sha256']):
        raise ValueError('original readout completion binding differs')
    receipt = capture._json(expected_receipt, config['readout_completion_sha256'])
    original = readouts.completed_result(resolved)  # All 49 pins before score-array access.
    checked, records = readouts._capture_metadata(resolved)  # Metadata only.
    if original['primary'] != review['primary']: raise ValueError('original primary result differs')
    for source_folder in (Path(resolved['run_dir']).resolve(), Path(pipe['pipeline_run_dir']).resolve(),
                          Path(json.loads(Path(pipe['capture_config']).read_text())['run_dir']).resolve()):
        if (out == source_folder or out in source_folder.parents or source_folder in out.parents
                or report == source_folder or source_folder in report.parents):
            raise ValueError('posthoc outputs cannot overlap original capture/readout/pipeline')
    return receipt, original, checked, records, resolved


def load_scores(entry, bundle, *, config_hash, weights, donor):
    """Hash bounded immutable bytes before opening only saved scores/identities."""
    path = capture._safe(entry['path'])
    if (type(entry.get('bytes')) is not int or not 0 < entry['bytes'] <= MAX_BANK_BYTES
            or path.stat().st_size != entry['bytes']):
        raise ValueError('bounded saved score bank required')
    payload = capture._bytes(path, MAX_BANK_BYTES)
    if hashlib.sha256(payload).hexdigest() != entry['sha256']:
        raise ValueError('saved score bank checksum differs before array access')
    with np.load(io.BytesIO(payload), allow_pickle=False) as arrays:
        if (str(arrays['config_hash'].item()) != config_hash
                or tuple(arrays['case_ids'].tolist()) != bundle.case_ids
                or not np.array_equal(arrays['targets'], bundle.y, equal_nan=True)
                or not np.array_equal(arrays['target_mask'], bundle.mask)
                or not np.array_equal(arrays['training_weights'], weights)
                or not np.array_equal(arrays['donor_indices'], donor)
                or not np.array_equal(arrays['donor_case_ids'], np.asarray(bundle.case_ids)[donor])
                or not np.array_equal(arrays['active_columns'], np.flatnonzero(bundle.mask.all(axis=0)))):
            raise ValueError('saved score IDs, targets, masks, training weights or donors differ')
        scores = arrays['real_scores'].copy()
    if (scores.dtype != np.float64 or scores.shape != bundle.y.shape
            or not np.isfinite(scores[bundle.mask]).all()
            or not np.isnan(scores[~bundle.mask]).all()):
        raise ValueError('saved scores must be finite for exactly the defined cells')
    return scores


def graph_validity(bundle, scores, indices):
    """Unconstrained candidate edges: zero/multiple incoming parents are invalid."""
    if bundle.site not in (7, 8): raise ValueError('complete graph checkpoints required')
    scores = target._scores(bundle, scores); indices = np.asarray(indices)
    if indices.dtype.kind not in 'iu' or indices.ndim != 1 or not len(indices) or np.any(indices < 0) or np.any(indices >= len(bundle.case_ids)):
        raise ValueError('nonempty valid row indices required')
    incoming, exact = np.zeros((len(indices), 4), dtype=int), np.ones(len(indices), dtype=bool)
    for spec in bundle.columns:
        if spec['family'] != 'direct': continue
        column = spec['index']; defined = bundle.mask[indices, column]
        if not defined.any(): continue
        if not defined.all() or not np.isfinite(scores[indices, column]).all():
            raise ValueError('all possible visible edges require finite scores')
        prediction = scores[indices, column] >= .5
        destination = target.NODE_INDEX[spec['consumer_node']]-4
        incoming[:, destination] += prediction
        exact &= prediction == bundle.y[indices, column]
    return dict(rows=len(indices), valid_graph_fraction=float(np.mean(np.all(incoming == 1, axis=1))),
        invalid_graph_fraction=float(np.mean(np.any(incoming != 1, axis=1))),
        zero_parent_rows=float(np.mean(np.any(incoming == 0, axis=1))),
        multiple_parent_rows=float(np.mean(np.any(incoming > 1, axis=1))),
        raw_binary_exact_graph_accuracy=float(exact.mean()),
        known_schedule_acyclic=True, threshold=.5,
        note='Validity uses the fixed visible candidate scaffold; it is not unconstrained node/version discovery.')


def _pin(path):
    return dict(path=str(path), sha256=capture._sha(path), bytes=Path(path).stat().st_size)


def run(config):
    from . import relationship_contrasts as pairs
    from .confidence import _run_lock
    _config(config); capture._slurm(); source = capture._current_source(config)
    receipt, original, checked, records, resolved = _inputs(config)
    out = Path(config['run_dir']); out.mkdir(parents=True, exist_ok=True)
    with _run_lock(out):
        if (out/'completion_manifest_v1.json').exists(): return _finish_audited(config)
        registration = dict(evaluation_role=ROLE, config=config, config_hash=digest(config), source=source,
            protocol=protocol(), posthoc=True, new_model_queries=0, new_fits=0, generated_holdouts_opened=False,
            original_readout_completion=_pin(config['readout_completion']), limitation=LIMITATION)
        capture._put(out/'registration.json', registration)
        manifest = pairs.build_pairs(records)
        if (manifest['manifest_sha256']!=PAIR_MANIFEST_SHA256
                or manifest['pair_counts']!={'train':144,'development':72}
                or manifest['component_counts']!={'train':18,'development':9}):
            raise ValueError('fixed source-matched provenance registry differs before score access')
        capture._put(out/'pairs_review_v1.json', manifest)
        bundles = {site: target.targets(records, site) for site in (3, 7, 8)}
        train = np.array([row['split'] == 'train' for row in records]); dev = np.flatnonzero(~train)
        train_rows = [row for row in records if row['split'] == 'train']
        groups = np.asarray([row['template_id'] for row in records])[dev]
        donors = {seed: target.coherent_shuffle(records, seed) for seed in readouts.SEEDS}
        algebraic, provenance, validity, selected = {'direct': [], 'source_categorical_value_derived': []}, [], [], {}
        truth, families = None, None
        for site in (3, 7, 8):
            bundle = bundles[site]
            for backend, layer in (('hidden', 24), ('surface', -1)):
                for seed in readouts.SEEDS:
                    name = readouts._name(backend, layer, site, seed); entry = receipt['artifacts'][name]
                    scores = load_scores(entry, bundle, config_hash=digest(resolved),
                        weights=readouts.group_weights(train_rows, seed).astype(np.float64), donor=donors[seed])
                    selected[name] = entry
                    if site == 3:
                        value = scores if backend == 'hidden' else target.derived_categorical_relations(bundle, scores)
                        measured = target.task_correctness(target.subset(bundle, dev), value[dev])
                        key = 'direct' if backend == 'hidden' else 'source_categorical_value_derived'
                        algebraic[key].append(measured['algebraic_correct'])
                        truth, families = measured['algebraic_truth'], measured['algebraic_families']
                    else:
                        predicted = target.reconstruct_parent_graph(bundle, scores)['parent_predictions']
                        ids = dict(zip(bundle.case_ids, predicted.tolist()))
                        provenance.append(dict(backend=backend, site=site, seed=seed,
                            metrics=pairs.score_pairs(manifest, ids, site=site, split='development')))
                        validity.append(dict(backend=backend, site=site, seed=seed,
                            metrics=graph_validity(bundle, scores, dev)))
        methods = {name: np.mean(values, axis=0) for name, values in algebraic.items()}
        comparison = readouts.algebraic_bootstrap(truth, methods, groups, families)
        if abs(comparison['methods']['direct']['score']-original['primary']['algebraic']['methods']['direct']['score']) > 1e-12:
            raise ValueError('original declared algebraic point fails saved-score reproduction')
        result = dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=digest(config),
            source=source, protocol=protocol(), posthoc=True, cases=len(records), development_components=9,
            original_primary=original['primary'], strong_source_control=comparison,
            provenance_pair_evaluations=provenance, unconstrained_graph_diagnostics=validity,
            selected_score_banks=selected, saved_score_rows_read=len(selected)*len(records),
            new_model_queries=0, new_fits=0, parameter_replays=0, raw_activations_loaded=False,
            generated_holdouts_opened=False, source_model_prefill_cases=checked['summary']['model_prefill_cases'],
            limitation=LIMITATION)
        readouts.immutable(out/'results_v1.json', readouts._json_bytes(result))
        readouts.immutable(config['report'], report(result).encode())
        completion = dict(status='complete_exploratory', evaluation_role=ROLE, config_hash=digest(config),
            source=source, protocol=protocol(), artifacts={name:_pin(path) for name,path in {
                'registration':out/'registration.json','pairs':out/'pairs_review_v1.json',
                'results':out/'results_v1.json','report':Path(config['report'])}.items()},
            new_model_queries=0, new_fits=0, generated_holdouts_opened=False)
        capture._put(out/'completion_manifest_v1.json', completion)
        return _finish_audited(config)


def _finish_audited(config):
    result=audit(config)
    capture._put(Path(config['run_dir'])/'followup_review_v1.json',dict(
        status='complete_exploratory',evaluation_role=ROLE,config_hash=digest(config),
        completion=_pin(Path(config['run_dir'])/'completion_manifest_v1.json'),
        metadata_audit='passed',selected_score_banks=18,saved_score_rows_read=18*1944,
        raw_activations_loaded=False,new_model_queries=0,new_fits=0,parameter_replays=0,
        generated_holdouts_opened=False,posthoc=True))
    return result


def audit(config):
    _config(config)
    folder=Path(config['run_dir']); receipt=capture._json(folder/'completion_manifest_v1.json')
    if (receipt.get('status')!='complete_exploratory' or receipt.get('evaluation_role')!=ROLE
            or receipt.get('config_hash')!=digest(config) or receipt.get('protocol')!=protocol()
            or receipt.get('new_model_queries')!=0 or receipt.get('new_fits')!=0
            or receipt.get('generated_holdouts_opened') is not False):
        raise ValueError('complete matching posthoc receipt required')
    capture._verify_source(config,receipt['source'])
    original_receipt, original, checked, _, _ = _inputs(config)  # No score-array access.
    expected={'registration':folder/'registration.json','pairs':folder/'pairs_review_v1.json',
        'results':folder/'results_v1.json','report':Path(config['report'])}
    if set(receipt.get('artifacts',{}))!=set(expected): raise ValueError('exact posthoc output inventory required')
    for name,path in expected.items():
        if receipt['artifacts'][name]!=_pin(path): raise ValueError('posthoc artifact differs')
    registration=capture._json(folder/'registration.json')
    if (registration.get('evaluation_role')!=ROLE or registration.get('config')!=config
            or registration.get('config_hash')!=digest(config) or registration.get('source')!=receipt['source']
            or registration.get('protocol')!=protocol() or registration.get('posthoc') is not True
            or registration.get('new_model_queries')!=0 or registration.get('new_fits')!=0
            or registration.get('generated_holdouts_opened') is not False
            or registration.get('original_readout_completion')!=_pin(config['readout_completion'])):
        raise ValueError('posthoc registration/source/input identity differs')
    result=capture._json(folder/'results_v1.json')
    selected={readouts._name(backend,layer,site,seed):original_receipt['artifacts'][readouts._name(backend,layer,site,seed)]
        for site in (3,7,8) for backend,layer in (('hidden',24),('surface',-1)) for seed in readouts.SEEDS}
    if (result.get('status')!='complete_exploratory' or result.get('evaluation_role')!=ROLE
            or result.get('config_hash')!=digest(config) or result.get('protocol')!=protocol()
            or result.get('source')!=receipt['source'] or result.get('posthoc') is not True
            or result.get('new_model_queries')!=0 or result.get('new_fits')!=0
            or result.get('parameter_replays')!=0 or result.get('raw_activations_loaded') is not False
            or result.get('generated_holdouts_opened') is not False
            or result.get('cases')!=1944 or result.get('development_components')!=9
            or result.get('saved_score_rows_read')!=18*1944 or result.get('selected_score_banks')!=selected
            or result.get('original_primary')!=original['primary']
            or result.get('source_model_prefill_cases')!=checked['summary']['model_prefill_cases']):
        raise ValueError('posthoc scientific result identity differs')
    return result


def report(result):
    control=result['strong_source_control']; methods=control['methods']
    lines=['# Posthoc source and provenance controls','',LIMITATION,'',
        '## Algebraic relations against the stronger source comparator','',
        '| Pipeline | Four-family macro balanced accuracy |','|---|---:|']
    for name,value in methods.items(): lines.append(f"| {name} | {100*value['score']:.3f}% |")
    lines+=['','| Contrast | Percentage points | Conditional group 95% |','|---|---:|---|']
    for name,value in control['comparisons'].items():
        interval=value['conditional_group_bootstrap_95']
        ci='unqualified' if interval is None else f'[{100*interval[0]:+.3f}, {100*interval[1]:+.3f}]'
        lines.append(f"| {name} | {100*value['mean']:+.3f} | {ci} |")
    lines+=['',f"Bootstrap status: {control['status']}; {control['valid_draws']} valid draws. No multiplicity adjustment or refitting.",'',
        '## Unconstrained graph validity','',
        '| Backend | Site | Seed | Valid graphs | Raw exact graphs |','|---|---:|---:|---:|---:|']
    for row in result['unconstrained_graph_diagnostics']:
        m=row['metrics'];lines.append(f"| {row['backend']} | {row['site']} | {row['seed']} | {100*m['valid_graph_fraction']:.3f}% | {100*m['raw_binary_exact_graph_accuracy']:.3f}% |")
    lines+=['','## Programs with equal numeric states and different dependencies','',
        'Development has 72 lexical pairs, 36 numeric bases and nine structural components. The table averages component means over the three weighting seeds; it has no independent pair replication or new confidence interval.','',
        '| Backend | Site | Both first parents correct | First-parent collapse | Both full graphs correct |',
        '|---|---:|---:|---:|---:|']
    for site in (7,8):
        for backend in ('hidden','surface'):
            rows=[row['metrics'] for row in result['provenance_pair_evaluations'] if row['site']==site and row['backend']==backend]
            if len(rows)!=3:raise ValueError('all three fixed paired-control seeds required')
            def mean(key):return 100*float(np.mean([row['component_macro'][key] for row in rows]))
            lines.append(f"| {backend} | {site} | {mean('both_first_parents_correct'):.3f}% | {mean('first_parent_predictions_collapse'):.3f}% | {mean('both_whole_graphs_correct'):.3f}% |")
    lines+=['','State-matched pair identities, per-pair correctness and component denominators are retained in the registry and results JSON. Only sites 7/8 are scored; site 3 precedes the differing copy and cannot reveal that future dependency.','',
        f"Read {result['saved_score_rows_read']:,} saved score rows across 18 banks; zero new model queries, fits or parameter replays. Original capture: {result['source_model_prefill_cases']:,} case prefills.",'']
    return '\n'.join(lines)
