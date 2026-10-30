"""Frozen vLLM execution and complete-cell review of computation/routing calibration.

This wrapper adds provenance and assay-specific review around checkpoint_suite.
It never changes historical gates, trains a model, or opens sealed outcomes.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import hashlib
import importlib
import json
import os
from pathlib import Path

from . import checkpoint_suite as suite
from . import relationship_capture as base
from . import overnight_relationship_capture as durable
from .arithmetic_readout_review import _cell, paired_contrast
from .confidence import _run_lock
from .datasets import digest

ROLE = 'discovery_computation_routing_calibration_v1'
MODELS = {
    'meta-llama/Llama-3.1-8B-Instruct': '0e9e39f249a16976918f6564b8830bc894c89659',
    'codellama/CodeLlama-34b-Instruct-hf': 'd4c1c474abcacd32d2a6eda45f9811d38c83e93d',
}
THRESHOLDS = dict(minimum_cell_n=24, minimum_accuracy=.9, maximum_invalid_rate=.05)
LIMITATION = (
    'Fresh numeric calibration on familiar fixed program forms. All three fixed '
    'instructions and all registered cells remain visible; no instruction is '
    'selected after viewing development results. Computation, storage and copying '
    'also change tokens, length and positions. Differences do not establish a '
    'causal mechanism or structural generalization. Intervals condition on these '
    'numeric groups and omit multiplicity correction. Historical gates remain '
    'unchanged; no generated final or extrapolation outcomes are opened.'
)
MAX_TEXT = 128 * 1024**2


def _programs():
    return importlib.import_module('.computation_routing_programs', __package__)


def _variants():
    variants = tuple(_programs().INSTRUCTIONS)
    if len(variants) != 3 or len(set(variants)) != 3:
        raise ValueError('exact three registered computation/routing instructions required')
    return variants


def _pin(path):
    path = base._safe(path)
    return dict(path=str(path), sha256=base._sha(path), bytes=path.stat().st_size)


def _json(path, checksum=None):
    return base._json(path, checksum)


def _config(config):
    required = {'evaluation_role', 'dataset', 'dataset_sha256', 'dataset_manifest_sha256',
        'declared_plan', 'declared_plan_sha256', 'model', 'model_revision', 'tokenizer_revision',
        'device', 'dtype', 'context_limit', 'sections', 'run_dir', 'report', 'review_artifact',
        'prepared_cases', 'preflight_result', 'runtime_manifest', 'runtime_manifest_sha256',
        'cuda_home', 'engine', 'request_chunk_size', 'eos_token_ids', 'reliability_gate',
        'bootstrap_replicates', 'bootstrap_seed'}
    if not isinstance(config, dict) or not required <= set(config) or config.get('evaluation_role') != ROLE:
        raise ValueError('explicit computation/routing discovery configuration required')
    if (config.get('model') not in MODELS or config.get('model_revision') != MODELS[config['model']]
            or config.get('tokenizer_revision') != config['model_revision']
            or config.get('device') != 'cuda' or config.get('dtype') != 'bfloat16'):
        raise ValueError('fixed cached BF16 CUDA checkpoint and tokenizer commits required')
    for name in ('dataset_sha256', 'dataset_manifest_sha256', 'declared_plan_sha256', 'runtime_manifest_sha256'):
        value = config[name]
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('explicit source SHA256 pins required')
    if (config['reliability_gate'] != THRESHOLDS or config['bootstrap_replicates'] != 2000
            or config['bootstrap_seed'] != 913):
        raise ValueError('fixed prospective reliability and uncertainty thresholds required')
    for name in ('context_limit', 'request_chunk_size'):
        if type(config[name]) is not int or config[name] < 1:
            raise ValueError('positive declared context and request chunk required')
    variants = _variants()
    sections = config['sections']
    if (not isinstance(sections, list) or len(sections) != 1 or not isinstance(sections[0], dict)
            or set(sections[0]) != {'name', 'kind', 'dataset', 'sha256', 'variants'}
            or sections[0]['name'] != 'computation_routing' or sections[0]['kind'] != 'computation_routing'
            or sections[0]['dataset'] != config['dataset'] or sections[0]['sha256'] != config['dataset_sha256']
            or sections[0]['variants'] != list(variants)):
        raise ValueError('one complete computation/routing section and all three instructions required')
    sources = [config['dataset'], str(Path(config['dataset']).with_suffix('.manifest.json')),
        config['declared_plan'], config['runtime_manifest']]
    for path in [*sources, config['run_dir'], config['report'], config['review_artifact'],
                 config['prepared_cases'], config['preflight_result']]:
        base._safe(path)
    out = Path(config['run_dir']).resolve()
    owned = [Path(config[k]).resolve() for k in ('prepared_cases', 'preflight_result', 'review_artifact')]
    report = Path(config['report']).resolve()
    output_files = [*owned, report]
    reserved = [out/'routing_preflight_v1.json', out/'routing_preparation_identity_v1.json', out/'routing_attempts_v1.json',
                out/'routing_completion_v1.json', out/'checkpoint_suite']
    if (any(path == out or out not in path.parents for path in owned)
            or len(set(owned)) != len(owned) or report.suffix != '.md'
            or report == out or report in out.parents or report in owned or report in reserved
            or any(a in b.parents or b in a.parents for a, b in combinations(output_files, 2))
            or any(path in report.parents for path in reserved)
            or any(path in p.parents or p == path or p in path.parents
                   for path in reserved for p in owned)
            or any(out == Path(path).resolve() or out in Path(path).resolve().parents
                   or Path(path).resolve() in out.parents
                   or any(p == Path(path).resolve() or p in Path(path).resolve().parents
                          or Path(path).resolve() in p.parents for p in output_files)
                   for path in sources)):
        raise ValueError('assay outputs cannot collide with sources or reserved stage artifacts')
    if len(json.dumps(config).encode()) > 16*1024:
        raise ValueError('bounded assay configuration required')


def _inputs(config):
    _config(config)
    for key in ('declared_plan', 'runtime_manifest', 'dataset'):
        payload = base._bytes(config[key], MAX_TEXT if key == 'dataset' else 1024**2)
        if hashlib.sha256(payload).hexdigest() != config[key+'_sha256']:
            raise ValueError('pinned assay source changed: '+key)
    manifest_path = Path(config['dataset']).with_suffix('.manifest.json')
    manifest = _json(manifest_path, config['dataset_manifest_sha256'])
    if (manifest.get('sha256') != config['dataset_sha256'] or manifest.get('evaluation_role') != _programs().ROLE
            or manifest.get('status') != 'complete' or manifest.get('independent_python_passed') is not True
            or manifest.get('generated_holdouts_opened') is not False):
        raise ValueError('validated discovery-only assay manifest required')
    rows = [json.loads(line) for line in base._bytes(config['dataset'], MAX_TEXT).splitlines() if line.strip()]
    _programs().validate_rows(rows)
    if (manifest.get('rows') != len(rows) or not rows or len({row['id'] for row in rows}) != len(rows)
            or any(row.get('evaluation_role') != _programs().ROLE or row.get('split') not in ('train', 'development') for row in rows)):
        raise ValueError('complete unique TRAIN/DEV calibration cohort required')
    return rows, manifest


def metadata(config):
    rows, manifest = _inputs(config)
    return dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), rows=len(rows),
        scored_cases=len(rows)*3, logical_source_views=len(_programs().analysis_rows(rows)),
        instructions=list(_variants()), dataset_sha256=manifest['sha256'],
        new_model_queries=0, new_fits=0, generated_holdouts_opened=False)


def _source(config, scheduled):
    if scheduled:
        base._slurm()
        return base._current_source(config)
    registration = _json(Path(config['run_dir'])/'routing_preflight_v1.json')
    if registration.get('config_hash') != digest(config):
        raise ValueError('matching frozen assay preparation required')
    base._verify_source(config, registration['source'])
    return registration['source']


def _prepared(config, source):
    registration = _json(Path(config['run_dir'])/'routing_preflight_v1.json')
    if (registration.get('status') != 'passed' or registration.get('evaluation_role') != ROLE
            or registration.get('config_hash') != digest(config) or registration.get('source') != source
            or registration.get('dataset_sha256') != config['dataset_sha256']
            or registration.get('dataset_manifest_sha256') != config['dataset_manifest_sha256']
            or registration.get('declared_plan_sha256') != config['declared_plan_sha256']
            or registration.get('model_inference') is not False
            or registration.get('generated_holdouts_opened') is not False):
        raise ValueError('complete matching frozen assay preparation required')
    for key in ('prepared_cases', 'preflight_result'):
        if registration['artifacts'][key] != _pin(config[key]):
            raise ValueError('prepared assay artifact changed')
    qa, cases = suite.prepared(config, source['source_sha256'])
    rows, _ = _inputs(config)
    expected = [(variant, row['id']) for variant in _variants() for row in rows]
    if ([(case.get('variant'), case.get('id')) for case in cases] != expected
            or qa.get('generated_holdouts_opened') is not False or qa.get('model_inference') is not False
            or any(case.get('kind') != 'computation_routing' or case.get('section') != 'computation_routing'
                   or case.get('record') != rows[i % len(rows)] for i, case in enumerate(cases))):
        raise ValueError('exact three-instruction prepared coverage required')
    return qa, cases


def preflight(config):
    _inputs(config)
    source = _source(config, True)
    folder = Path(config['run_dir']); folder.mkdir(parents=True, exist_ok=True)
    with _run_lock(folder):
        registration_path = folder/'routing_preflight_v1.json'
        if registration_path.exists():
            qa, _ = _prepared(config, source)
            return qa
        identity_path = folder/'routing_preparation_identity_v1.json'
        identity = dict(evaluation_role=ROLE, config_hash=digest(config), source=source,
            dataset_sha256=config['dataset_sha256'], dataset_manifest_sha256=config['dataset_manifest_sha256'],
            declared_plan_sha256=config['declared_plan_sha256'])
        if identity_path.exists():
            if _json(identity_path) != identity:
                raise ValueError('partial assay preparation identity differs')
            # Legacy checkpoint_suite publishes its prepared text directly.
            # Before a completion pin exists, preserve any interrupted owned
            # writes and rebuild them under the identical frozen identity.
            for key in ('prepared_cases', 'preflight_result'):
                path = Path(config[key])
                if path.exists():
                    if path.is_symlink():
                        raise ValueError('uncommitted preparation cannot be a symbolic link')
                    payload = base._bytes(path, MAX_TEXT)
                    backup = path.with_name(path.name+'.uncommitted_'+hashlib.sha256(payload).hexdigest()[:16]+'.bin')
                    base._publish(backup, payload)
                    path.unlink()
        elif Path(config['prepared_cases']).exists() or Path(config['preflight_result']).exists():
            raise ValueError('unregistered assay preparation exists; preserve and inspect it')
        base._put(identity_path, identity)
        suite.configure_runtime(config)
        qa = suite.preflight(config)
        registration = dict(status='passed', evaluation_role=ROLE, config_hash=digest(config), source=source,
            dataset_sha256=config['dataset_sha256'], dataset_manifest_sha256=config['dataset_manifest_sha256'],
            declared_plan_sha256=config['declared_plan_sha256'], model_inference=False,
            generated_holdouts_opened=False,
            artifacts={key: _pin(config[key]) for key in ('prepared_cases', 'preflight_result')})
        base._put(registration_path, registration)
        _prepared(config, source)
        return qa


def _responses(config, cases, *, repair=False):
    """Read an exact response prefix; preserve interrupted uncommitted bytes."""
    path = Path(config['run_dir'])/'checkpoint_suite'/'responses.jsonl'
    if not path.exists():
        return []
    if path.is_symlink():
        raise ValueError('response artifact cannot be a symbolic link')
    payload = base._bytes(path, MAX_TEXT); rows = []; committed = 0
    lines = payload.splitlines(keepends=True)
    for index, line in enumerate(lines):
        try:
            row = json.loads(line)
        except (ValueError, UnicodeError):
            if not repair or index != len(lines)-1 or line.endswith(b'\n'):
                raise ValueError('malformed committed assay response')
            from .overnight_relationship_behavior import _replace_owned
            backup = path.with_name('responses_interrupted_'+hashlib.sha256(payload).hexdigest()[:16]+'.bin')
            base._publish(backup, payload)
            _replace_owned(path, payload[:committed])
            break
        if len(rows) >= len(cases):
            raise ValueError('extra assay response')
        suite.validate_response(cases[len(rows)], row)
        rows.append(row); committed += len(line)
    if repair and rows and path.read_bytes() and not path.read_bytes().endswith(b'\n'):
        with path.open('ab') as stream:
            stream.write(b'\n'); stream.flush(); os.fsync(stream.fileno())
    return rows


def _attempt_history(journal, config, source, total):
    if (not isinstance(journal, dict) or set(journal) != {'config_hash', 'source', 'attempts'}
            or journal.get('config_hash') != digest(config) or journal.get('source') != source
            or not isinstance(journal.get('attempts'), list)):
        raise ValueError('matching assay wrapper resume journal required')
    previous = 0
    for attempt in journal['attempts']:
        if (not isinstance(attempt, dict) or attempt.get('status') not in {'started', 'interrupted', 'failed', 'complete'}
                or not isinstance(attempt.get('slurm_job_id'), str) or not attempt['slurm_job_id'].isdigit()
                or type(attempt.get('saved_response_prefix')) is not int
                or not previous <= attempt['saved_response_prefix'] <= total
                or attempt.get('pending_scored_cases') != total-attempt['saved_response_prefix']
                or attempt.get('warmup_request_ceiling') != min(8, total)
                or (attempt['status'] == 'complete' and attempt.get('confirmed_warmup_requests') != min(8, total))
                or (attempt['status'] != 'complete' and 'confirmed_warmup_requests' in attempt)):
            raise ValueError('bounded ordered assay invocation accounting required')
        previous = attempt['saved_response_prefix']


def summarize(records, config):
    """Map unique generations to declared logical views without inventing trials."""
    records = list(records); variants = _variants(); programs = _programs()
    unique_rows, _ = _inputs(config)
    expected_rows = {row['id']: row for row in unique_rows}
    expected = {(variant, row_id) for variant in variants for row_id in expected_rows}
    physical = {}; geometry = {}
    for case, response in records:
        key = (case.get('variant'), case.get('id'))
        if (key not in expected or key in physical or case.get('kind') != 'computation_routing'
                or case.get('record') != expected_rows[key[1]]):
            raise ValueError('complete unique registered instruction/source identities required')
        suite.validate_response(case, response)
        physical[key] = (case, response)
        geometry[case['prompt_sha256']] = (len(case['input_token_ids']), len(response['output_token_ids']))
    if set(physical) != expected:
        raise ValueError('complete unique registered instruction/source coverage required')
    logical_rows = programs.analysis_rows(unique_rows)
    if (not logical_rows or len({row['id'] for row in logical_rows}) != len(logical_rows)
            or any(row.get('source_id') not in expected_rows or row.get('capture_id') != row.get('source_id')
                   for row in logical_rows)):
        raise ValueError('exact source-linked unique logical memberships required')
    forms = tuple(programs.FORMS); questions = tuple(programs.QUESTIONS)
    groups = defaultdict(set); bases = {}; primary = {}; logical = []
    for variant in variants:
        for row in logical_rows:
            case, response = physical[variant, row['source_id']]
            if (row['form'] not in forms or row['question'] not in questions
                    or row['split'] not in ('train', 'development') or row['operator'] not in ('add', 'sub')
                    or row['answer_sign'] not in (-1, 1) or row['queried_root_slot'] not in range(4)):
                raise ValueError('registered logical form/question/operator/sign factors required')
            groups[row['root_order_cluster']].add(row['split'])
            identity = (row['split'], row['root_order_cluster'], row['expected_answer'])
            if row['base_id'] in bases and bases[row['base_id']] != identity:
                raise ValueError('numeric relatives changed split, root cluster or answer')
            bases[row['base_id']] = identity
            logical.append((variant, row, response['score'], case['prompt_sha256']))
            if row['question'] in ('full_root', 'full_leaf'):
                key = (variant, row['paired_group_id'], row['form'], row['operator'], row['answer_sign'], row['chain_depth'])
                pair = primary.setdefault(key, {})
                if row['question'] in pair:
                    raise ValueError('duplicate full-root/full-leaf logical member')
                pair[row['question']] = (row, response['score'])
    if any(len(splits) != 1 for splits in groups.values()):
        raise ValueError('root-order clusters must remain split disjoint')
    gate_groups = defaultdict(list); diagnostic_groups = defaultdict(list); form_groups = defaultdict(list)
    for variant, row, score, prompt_hash in logical:
        cell = (variant, row['form'], row['question'], row['operator'], row['answer_sign'], row['split'])
        value = (row, score, prompt_hash)
        gate_groups[cell].append(value)
        diagnostic_groups[(*cell, row['queried_root_slot'], row['topology'])].append(value)
        form_groups[variant, row['form'], row['question'], row['split']].append(value)
    expected_gate = {(variant, form, question, op, sign, split) for variant in variants for form in forms
        for question in questions for op in ('add', 'sub') for sign in (-1, 1) for split in ('train', 'development')}
    if set(gate_groups) != expected_gate:
        raise ValueError('complete fixed instruction/form/question/operator/sign/split gate matrix required')
    def cell_stats(values):
        scores = [score for _, score, _ in values]
        result = _cell(scores); result.pop('wilson_95')
        # Logical views and lexical relatives are not independent Bernoulli trials.
        result.update(unique_source_n=len({row['source_id'] for row, _, _ in values}),
            unique_prompt_n=len({prompt_hash for _, _, prompt_hash in values}),
            root_order_clusters=len({row['root_order_cluster'] for row, _, _ in values}),
            uncertainty='Descriptive counts; logical views and lexical relatives are dependent.')
        lengths = [geometry[prompt_hash] for prompt_hash in {p for _, _, p in values}]
        def bounds(index):
            sizes = [value[index] for value in lengths]
            return dict(n=len(sizes), min=min(sizes), max=max(sizes), mean=sum(sizes)/len(sizes))
        result.update(prompt_tokens=bounds(0), generated_tokens=bounds(1),
            token_geometry_scope='Distinct prepared prompt hashes within the reported logical cell.')
        return result
    def describe(key, values, detail=False):
        value = dict(variant=key[0], form=key[1], question=key[2], operator=key[3], answer_sign=key[4],
            split=key[5], **cell_stats(values))
        if detail:value.update(queried_root_slot=key[6], topology=key[7])
        return value
    gate_cells = [describe(key, values) for key, values in sorted(gate_groups.items())]
    cells = [describe(key, values, True) for key, values in sorted(diagnostic_groups.items())]
    form_cells = [dict(variant=key[0], form=key[1], question=key[2], split=key[3], **cell_stats(values))
        for key, values in sorted(form_groups.items())]
    gates = {}
    for variant in variants:
        retained = []
        excluded = []
        for cell in gate_cells:
            if cell['variant'] != variant:continue
            if cell['form'] == 'literal' and cell['question'] == 'arithmetic_only':
                excluded.append(dict(cell, gate_exclusion='Prospectively excluded repeated literal isolated controls.'))
            else:
                retained.append(dict(cell, passed=(cell['n'] >= 24 and cell['unique_prompt_n'] >= 24
                    and cell['accuracy'] >= .9 and cell['invalid_rate'] <= .05)))
        train = bool(retained) and all(cell['passed'] for cell in retained if cell['split'] == 'train')
        dev = bool(retained) and all(cell['passed'] for cell in retained if cell['split'] == 'development')
        gates[variant] = dict(status='passed' if train and dev else 'failed', training_qualified=train,
            development_descriptive_passed=dev, numeric_development_qualified=train and dev,
            cells=retained, excluded_literal_isolated_controls=excluded)
    contrasts = []
    for variant in variants:
        for form in forms:
            for operator in ('add', 'sub'):
                for sign in (-1, 1):
                    depths = sorted({key[5] for key in primary})
                    for depth in depths:
                        for split in ('train', 'development', 'all'):
                            values = []
                            for key, pair in primary.items():
                                if (key[0], key[2], key[3], key[4], key[5]) != (variant, form, operator, sign, depth):continue
                                if set(pair) != {'full_root', 'full_leaf'}:
                                    raise ValueError('complete primary full-root/full-leaf pair required')
                                left, lscore = pair['full_leaf']; right, rscore = pair['full_root']
                                if (any(left[name] != right[name] for name in ('expected_answer', 'split', 'root_order_cluster'))
                                        or left['source'].rsplit('\n', 1)[0] != right['source'].rsplit('\n', 1)[0]):
                                    raise ValueError('primary matched answers, split or root cluster differ')
                                if split != 'all' and left['split'] != split:continue
                                values.append((left['root_order_cluster'], int(lscore['correct'])-int(rscore['correct'])))
                            contrast = paired_contrast('full_leaf_minus_full_root', values, draws=2000, seed=913)
                            contrast['resampling_unit'] = 'root_order_cluster; all numeric, lexical and topology relatives retained together'
                            contrasts.append(dict(variant=variant, form=form, operator=operator, answer_sign=sign,
                                chain_depth=depth, split=split, primary=split == 'development',
                                inference_scope='primary numeric development' if split == 'development' else 'descriptive context', **contrast))
    overall = _cell([response['score'] for _, response in records]); overall.pop('wilson_95')
    return dict(status='complete_audited', complete=True, evaluation_role=ROLE, config_hash=digest(config),
        **overall, scored_unique_cases=len(records), logical_responses=len(logical),
        logical_source_views=len(logical_rows), unique_sources=len(unique_rows), cells=cells, gate_cells=gate_cells,
        form_cells=form_cells, contrasts=contrasts, instructions=list(variants), forms=list(forms),
        questions=list(questions), numeric_bases=len(bases), root_order_clusters=len(groups),
        source_reuse=dict(unique_sources=len(unique_rows), logical_source_views=len(logical_rows),
            additional_logical_memberships=len(logical_rows)-len(unique_rows),
            physical_sources_with_multiple_memberships=sum(len(row['logical_memberships']) > 1 for row in unique_rows),
            cross_split_literal_isolated_controls=sum(len({m['split'] for m in row['logical_memberships']}) > 1 for row in unique_rows)),
        root_order_clusters_by_split={split: sum(splits == {split} for splits in groups.values()) for split in ('train', 'development')},
        reliability_gate=dict(thresholds=THRESHOLDS, instructions=gates,
            status='passed' if all(g['numeric_development_qualified'] for g in gates.values()) else 'failed',
            selection='No instruction selected. All nonisolated literal controls and computed cells enter fixed gates; only repeated literal arithmetic_only controls are prospectively excluded. No fallback after development failure.'),
        new_fits=0, generated_holdouts_opened=False, limitation=LIMITATION)


def _report(result):
    lines = ['# Computation and routing calibration', '', LIMITATION, '',
        f"{result['n']:,} scored responses; {result['correct']:,} correct; {result['invalid']:,} invalid. "
        f"Warm-up requests are recorded separately: {result['accounting']['confirmed_warmup_requests']:,} confirmed.", '',
        'Every instruction × form × question × operator × answer-sign gate cell must have at least 24 responses and 24 unique prompts, at least 90% accuracy '
        'and at most 5% invalid responses on training, followed by the same numeric-development checks. '
        'Query slots, topologies/copy depths and lexical variants are pooled within these fixed gates. '
        'Repeated literal arithmetic_only controls are prospectively excluded; all other cells enter the gates. '
        'All forms and all three instructions remain reported. No instruction is selected.', '',
        '| Instruction | Training qualified | Numeric development qualified |', '|---|---|---|']
    for variant, gate in result['reliability_gate']['instructions'].items():
        lines.append(f"| {variant} | {gate['training_qualified']} | {gate['numeric_development_qualified']} |")
    lines += ['', f"{result['unique_sources']:,} unique sources map to {result['logical_source_views']:,} logical source views. "
        'Shared deterministic outputs are mapped into views explicitly and are not independent trials.', '',
        '| Instruction | Form | Question | Split | Correct / logical n | Unique prompts | Invalid |', '|---|---|---|---|---:|---:|---:|']
    for cell in result['form_cells']:
        lines.append(f"| {cell['variant']} | {cell['form']} | {cell['question']} | {cell['split']} | {cell['correct']}/{cell['n']} | {cell['unique_prompt_n']} | {cell['invalid']} |")
    lines += ['', 'The machine result retains every fixed gate cell and each queried-slot/topology descriptive stratum. '
        'Invalid responses count as wrong. No independent-trial intervals are assigned to repeated controls.', '',
        '| Instruction | Form | Operator | Sign | Depth | Split | Full leaf minus full root | Root-order clusters | Exploratory 95% interval |',
        '|---|---|---|---:|---:|---|---:|---:|---|']
    for contrast in result['contrasts']:
        lo, hi = contrast['exploratory_group_bootstrap_95']
        lines.append(f"| {contrast['variant']} | {contrast['form']} | {contrast['operator']} | {contrast['answer_sign']} | {contrast['chain_depth']} | {contrast['split']} | {100*contrast['mean']:.3f} pp | {contrast['paired_groups']} | [{100*lo:.3f}, {100*hi:.3f}] pp |")
    lines += ['', 'Primary paired intervals resample whole root-order clusters, retaining numeric, lexical and topology relatives. '
        'DEV comparisons are primary; TRAIN/all rows are descriptive context. '
        'Intervals have no multiplicity adjustment and condition on the familiar source forms. '
        'Machine cells also retain prompt and generated-token geometry measured on distinct prompt hashes.', '']
    return '\n'.join(lines)


def _review(config, source, cases):
    checked = suite.audit(config)
    folder = Path(config['run_dir']); stage = folder/'checkpoint_suite'
    rows = _responses(config, cases)
    if (checked.get('status') != 'passed' or not checked.get('complete') or len(rows) != len(cases)
            or checked['preflight']['source_sha256'] != source['source_sha256']):
        raise ValueError('complete audited assay response coverage required')
    result = summarize(zip(cases, rows), config)
    attempts = _json(folder/'routing_attempts_v1.json')
    _attempt_history(attempts, config, source, len(cases))
    if (not attempts['attempts'] or any(a['status'] == 'started' for a in attempts['attempts'])):
        raise ValueError('finished matching wrapper attempt accounting required')
    confirmed = sum(a.get('confirmed_warmup_requests', 0) for a in attempts['attempts'])
    uncertain = sum(a.get('warmup_request_ceiling', 0) for a in attempts['attempts'] if a['status'] != 'complete')
    result.update(source=source, model=config['model'], model_revision=config['model_revision'],
        dataset_sha256=config['dataset_sha256'], dataset_manifest_sha256=config['dataset_manifest_sha256'],
        declared_plan_sha256=config['declared_plan_sha256'],
        accounting=dict(scored_responses=len(rows), confirmed_warmup_requests=confirmed,
            warmup_requests_per_successful_backend_invocation=8, uncertain_failed_invocation_warmup_ceiling=uncertain,
            failed_backend_invocations=sum(a['status'] != 'complete' for a in attempts['attempts']),
            scored_model_queries_exact=len(rows) if all(a['status'] == 'complete' for a in attempts['attempts']) else None,
            scored_model_queries_lower_bound=len(rows),
            scored_model_queries_upper_bound=sum(a['pending_scored_cases'] for a in attempts['attempts']),
            scope='Saved scored cases are exact. Eight warm-ups per successful backend invocation are separate; failed invocation forwards cannot be recovered from the legacy backend journal.'),
        artifacts={name: _pin(path) for name, path in {'backend_audit': stage/'audit.json',
            'responses': stage/'responses.jsonl', 'backend_manifest': stage/'manifest.json',
            'preparation': folder/'routing_preflight_v1.json', 'attempts': folder/'routing_attempts_v1.json'}.items()})
    result.update(generated_responses=len(rows),
        new_model_queries=(len(rows)+confirmed if not result['accounting']['failed_backend_invocations'] else None),
        new_model_queries_lower_bound=len(rows)+confirmed,
        new_model_queries_upper_bound=result['accounting']['scored_model_queries_upper_bound']+confirmed+uncertain)
    report_payload = _report(result).encode()
    result['report_sha256'] = hashlib.sha256(report_payload).hexdigest()
    base._publish(config['report'], report_payload)
    base._put(config['review_artifact'], result)
    receipt = dict(status='complete_audited', evaluation_role=ROLE, config_hash=digest(config), source=source,
        scored_cases=len(cases), generated_holdouts_opened=False, new_fits=0,
        new_model_queries=result['new_model_queries'], new_model_queries_lower_bound=result['new_model_queries_lower_bound'],
        new_model_queries_upper_bound=result['new_model_queries_upper_bound'],
        artifacts={name: _pin(path) for name, path in {'review': config['review_artifact'],
            'report': config['report']}.items()})
    base._put(folder/'routing_completion_v1.json', receipt)
    return result


def _completed(config, source, cases):
    folder = Path(config['run_dir']); receipt = _json(folder/'routing_completion_v1.json')
    if (receipt.get('status') != 'complete_audited' or receipt.get('evaluation_role') != ROLE
            or receipt.get('config_hash') != digest(config) or receipt.get('source') != source
            or receipt.get('scored_cases') != len(cases) or receipt.get('generated_holdouts_opened') is not False
            or receipt.get('new_fits') != 0):
        raise ValueError('complete matching assay receipt required')
    expected = {'review': config['review_artifact'], 'report': config['report']}
    if set(receipt.get('artifacts', {})) != set(expected):
        raise ValueError('exact assay completion inventory required')
    for name, path in expected.items():
        if receipt['artifacts'][name] != _pin(path):
            raise ValueError('completed assay review or report changed')
    # Recompute from already saved text; no model or parameter calls occur.
    result = _review(config, source, cases)
    for key in ('new_model_queries', 'new_model_queries_lower_bound', 'new_model_queries_upper_bound'):
        if receipt.get(key) != result[key]:
            raise ValueError('completed assay query accounting changed')
    return result


def run(config):
    _inputs(config); source = _source(config, True)
    folder = Path(config['run_dir'])
    with _run_lock(folder):
        _, cases = _prepared(config, source)
        if (folder/'routing_completion_v1.json').exists():
            return _completed(config, source, cases)
        journal_path = folder/'routing_attempts_v1.json'
        backend_manifest = folder/'checkpoint_suite'/'manifest.json'
        if backend_manifest.exists() and not journal_path.exists():
            raise ValueError('backend stage has no registered wrapper attempt history')
        response_path = folder/'checkpoint_suite'/'responses.jsonl'
        if response_path.exists() and response_path.stat().st_size and not backend_manifest.exists():
            raise ValueError('saved response prefix has no backend source identity manifest')
        journal = _json(journal_path) if journal_path.exists() else dict(config_hash=digest(config), source=source, attempts=[])
        _attempt_history(journal, config, source, len(cases))
        backend = _json(backend_manifest) if backend_manifest.exists() else None
        if backend is not None and (backend.get('identity', {}).get('config') != config
                or backend['identity'].get('code', {}).get('source_sha256') != source['source_sha256']
                or backend.get('identity_hash') != digest(backend['identity'])):
            raise ValueError('backend source/configuration identity differs')
        backend_complete = backend is not None and backend.get('status') == 'complete'
        rows = _responses(config, cases, repair=not backend_complete)
        if backend_complete:
            suite.audit(config)
            if not journal['attempts']:
                raise ValueError('completed backend requires a registered invocation')
            prior = journal['attempts'][-1]
            if prior.get('status') != 'complete':
                if (prior.get('status') != 'started' or not backend.get('attempts')
                        or backend['attempts'][-1].get('slurm_job_id') != prior.get('slurm_job_id')):
                    raise ValueError('cannot certify interrupted completed backend invocation')
                prior.update(status='complete', confirmed_warmup_requests=prior['warmup_request_ceiling'])
                durable._journal(journal_path, journal)
            return _review(config, source, cases)
        for prior in journal['attempts']:
            if prior.get('status') == 'started':
                prior['status'] = 'interrupted'
        attempt = dict(slurm_job_id=os.environ['SLURM_JOB_ID'], status='started', saved_response_prefix=len(rows),
            pending_scored_cases=len(cases)-len(rows), warmup_request_ceiling=min(8, len(cases)))
        journal['attempts'].append(attempt); durable._journal(journal_path, journal)
        try:
            suite.configure_runtime(config)
            suite.run(config)
            # The successful legacy backend invocation necessarily finished its
            # fixed eight-request warm-up unless it reused a completed stage.
            attempt.update(status='complete', confirmed_warmup_requests=attempt['warmup_request_ceiling'])
            durable._journal(journal_path, journal)
            return _review(config, source, cases)
        except BaseException as exc:
            if attempt['status'] != 'complete':
                attempt.update(status='failed', error=f'{type(exc).__name__}: {exc}')
                durable._journal(journal_path, journal)
            raise


def audit(config):
    _inputs(config); source = _source(config, False)
    with _run_lock(Path(config['run_dir'])):
        _, cases = _prepared(config, source)
        return _completed(config, source, cases)


def review(config):
    return audit(config)
