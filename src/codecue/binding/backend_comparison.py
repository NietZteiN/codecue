"""Compare fixed interface runs without collecting or pooling model outcomes."""
from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path

from .behavior import parse_answer
from .datasets import digest, write_json
from .interpreter import execute


def compare(runs):
    """Require identical tasks, token IDs and inference contracts across runs."""
    if len(runs) < 2:
        raise ValueError('comparison needs at least two runs')
    reference = None
    prepared = {}
    summaries = {}
    for label, (manifest, result) in runs.items():
        identity = manifest['identity']
        if manifest['identity_hash'] != digest(identity):
            raise ValueError('run identity checksum mismatch')
        if (manifest['status'] != 'complete' or not result['complete']
                or identity['stage'] != 'interface_diagnostics'
                or result.get('heldout_outcomes_opened') is not False):
            raise ValueError('only complete training-only interface runs are eligible')
        config = identity['config']
        contract = {k: config[k] for k in ('model', 'model_revision', 'tokenizer_revision',
                                          'protocol', 'max_new_tokens')}
        contract['dataset_sha256'] = identity['dataset_manifest']['sha256']
        contract['tokenization_mode'] = config.get('tokenization_mode','native')
        contract['inference_sources'] = {k: identity['code']['source_files'][k] for k in (
            'src/codecue/binding/model_adapter.py', 'src/codecue/models.py')}
        if result['protocol'] != config['protocol']:
            raise ValueError('response protocol differs from manifest')
        if reference is None:
            reference = contract
        elif contract != reference:
            raise ValueError('inference contract mismatch')
        batches = result['responses_by_batch_size']
        if set(batches) != {'1', '4'}:
            raise ValueError('both audited batch sizes are required')
        prepared[label] = {}
        summaries[label] = {'identity_hash': manifest['identity_hash'],
                            'device': config['device'], 'dtype': config['dtype'],
                            'device_name': result.get('device_name'),
                            'gpu_peak_bytes': result.get('gpu_peak_bytes'), 'batches': {}}
        for batch, rows in batches.items():
            mapped = {row['id']: row for row in rows}
            if not rows or len(mapped) != len(rows):
                raise ValueError('nonempty unique case IDs are required')
            for row in rows:
                if row['split'] != 'train':
                    raise ValueError('test or development outcomes are ineligible')
                prediction = parse_answer(row['raw_response'])
                if (row['expected_answer'] != execute(row['source'])['expected_answer']
                        or prediction != row['prediction']
                        or row['correct'] != (prediction == row['expected_answer'])):
                    raise ValueError('stored oracle or response score mismatch')
            prepared[label][batch] = mapped
            summaries[label]['batches'][batch] = {
                'n': len(rows), 'invalid': sum(r['prediction'] is None for r in rows),
                **{kind: {'n': sum(r['kind'] == kind for r in rows),
                          'correct': sum(r['kind'] == kind and r['correct'] for r in rows)}
                   for kind in ('primitive', 'discovery_training')}}
        count = sum(len(rows) for rows in batches.values())
        if manifest['samples_completed'] != count or manifest['samples_planned'] != count:
            raise ValueError('manifest response count mismatch')
    original = next(iter(prepared.values()))['1']
    case_fields = ('source', 'expected_answer', 'input_token_ids', 'kind', 'split')
    for batches in prepared.values():
        for rows in batches.values():
            if set(rows) != set(original) or any(
                    any(rows[key][field] != original[key][field] for field in case_fields)
                    for key in original):
                raise ValueError('case or input token mismatch')
    comparisons = []
    pairs = [(a, batch, b, batch) for a, b in combinations(prepared, 2) for batch in ('1', '4')]
    pairs += [(label, '1', label, '4') for label in prepared]
    for left, lb, right, rb in pairs:
        a, b = prepared[left][lb], prepared[right][rb]
        changed = []
        shared_failures = []
        for key in sorted(original):
            ar, br = a[key], b[key]
            if ar['raw_response'] != br['raw_response']:
                changed.append({'id': key, 'kind': ar['kind'], 'expected_answer': ar['expected_answer'],
                                'left_raw': ar['raw_response'], 'right_raw': br['raw_response'],
                                'left_prediction': ar['prediction'], 'right_prediction': br['prediction']})
            if ar['kind'] == 'primitive' and not ar['correct'] and not br['correct']:
                shared_failures.append(key)
        comparisons.append({'left': left, 'left_batch': int(lb), 'right': right, 'right_batch': int(rb),
                            'n': len(a), 'raw_matches': len(a) - len(changed),
                            'prediction_matches': sum(a[k]['prediction'] == b[k]['prediction'] for k in a),
                            'shared_primitive_failures': shared_failures, 'differences': changed})
    return {'status': 'complete', 'contract': reference, 'runs': summaries, 'comparisons': comparisons,
            'heldout_outcomes_opened': False,
            'interpretation': 'Matched deterministic queries are sensitivity checks, not independent replications. '
                              'Agreement does not validate shared generation code or identify an internal cause.'}


def run(config):
    from .registry import code_identity
    output = Path(config['output'])
    if output.exists():
        raise ValueError('backend comparison is immutable; choose a new output')
    runs = {}
    inputs = {}
    for label, directory in config['runs'].items():
        directory = Path(directory)
        paths = {name: directory / name for name in ('manifest.json', 'responses.json')}
        runs[label] = tuple(json.loads(paths[name].read_text()) for name in paths)
        inputs[label] = {name: {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                         for name, path in paths.items()}
    result = compare(runs)
    result.update(inputs=inputs, analysis_code=code_identity(), config_hash=digest(config))
    write_json(output, result)
    return result
