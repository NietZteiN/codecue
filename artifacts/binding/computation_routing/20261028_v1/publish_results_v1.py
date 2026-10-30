"""Publish immutable calibration comparisons from completed, pinned metadata only.

No responses, source/prepared JSONL records, tokenizer, model, NPZ or activation
array is opened. Both completed model receipts are required before publication.
Run with --self-test for bounded synthetic checks without scientific inputs.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
import hashlib
import io
from itertools import product
import json
import math
import os
from pathlib import Path
import sys
import tempfile

ROLE = 'discovery_computation_routing_calibration_v1'
PUBLICATION_ROLE = 'discovery_computation_routing_publication_v1'
MODEL_KEYS = ('llama8b', 'codellama34b')
MODELS = {'llama8b': ('Llama 3.1 8B', 'meta-llama/Llama-3.1-8B-Instruct',
        '0e9e39f249a16976918f6564b8830bc894c89659'),
    'codellama34b': ('CodeLlama 34B', 'codellama/CodeLlama-34b-Instruct-hf',
        'd4c1c474abcacd32d2a6eda45f9811d38c83e93d')}
VARIANTS = ('routing_output_v1', 'routing_execute_v1', 'routing_value_v1')
FORMS = ('literal', 'small', 'cancellation')
QUESTIONS = ('arithmetic_only', 'roots_only', 'full_root', 'full_leaf')
FORM_LABELS = {'literal': 'Literal', 'small': 'Compact one-op', 'cancellation': 'Larger cancellation'}
QUESTION_LABELS = {'arithmetic_only': 'Single assignment', 'roots_only': 'Roots only',
    'full_root': 'Full: root', 'full_leaf': 'Full: copied leaf'}
THRESHOLDS = dict(minimum_cell_n=24, minimum_accuracy=.9, maximum_invalid_rate=.05)
MAX_JSON = 8*1024**2
SUITE_REL = Path('artifacts/binding/computation_routing/20261028_v1')
INPUTS = {}
LIMITATIONS = [
    'Fresh adaptive discovery calibration on familiar restricted forms; no independent confirmation or unfamiliar-program prediction.',
    'arithmetic_only is one assignment followed by its variable readout, not a pure expression calculation.',
    'Only the queried root is computed; the other three roots are literal distractors.',
    'Compact and larger expressions share operator and operand-sign patterns; magnitude ranges partly overlap and tokenization/cancellation extent change.',
    'Full-root and full-leaf questions have identical bodies and correct answers; query identifier and definition recency still differ.',
    'Literal isolated controls can be shared across splits; reused logical views are dependent and excluded only where prospectively specified.',
    'Question/form curves pool query slots, signs, operators and copy depths and are descriptive point estimates, not qualification gates.',
    'Primary DEV contrasts resample 12 whole root-order clusters, conditional on fixed numeric/templates, with 2000 draws and no multiplicity adjustment.',
    'Numeric seeds, lexical forms, copy topologies and instruction variants are related cases, not independent structural replications.',
    'Behavioral differences do not observe an intermediate internal state or identify a copying, binding or selection mechanism.',
    'Historical failed gates, sealed final/extrapolation outcomes, optional training and mechanism claims are unchanged.',
]


def require(condition, message):
    if not condition: raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def json_bytes(value):
    data = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
    require(len(data) <= MAX_JSON, 'Publication metadata exceeds 8 MiB')
    return data


def workspace():
    """Resolve the real workspace from this file or a frozen snapshot, never cwd."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        frozen = parent/'frozen_manifest.json'
        if frozen.is_file():
            require(frozen.stat().st_size <= MAX_JSON, 'Bounded frozen manifest required')
            candidate = Path(json.loads(frozen.read_text())['workspace_root']).resolve()
            if (candidate/SUITE_REL/'execution_source_v1.json').is_file(): return candidate
        if ((parent/'src/codecue/binding').is_dir()
                and (parent/SUITE_REL/'execution_source_v1.json').is_file()): return parent
    raise ValueError('Cannot resolve the calibration workspace from publisher/snapshot metadata')


def resolve(root, path):
    path = Path(path)
    path = (root/path).resolve() if not path.is_absolute() else path.resolve()
    require(path == root or root in path.parents, 'Publication input/output must stay in this workspace')
    return path


def pin(root, path, payload):
    path = resolve(root, path)
    value = dict(path=str(path.relative_to(root)), sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload))
    previous = INPUTS.setdefault(value['path'], value)
    require(previous == value, 'Publication input changed during one invocation: '+value['path'])
    return value


def read_json(root, path, expected=None):
    path = resolve(root, path)
    require(path.suffix == '.json', 'Only JSON metadata may be read; response/source/prepared JSONL and arrays are excluded')
    require(path.is_file() and path.stat().st_size <= MAX_JSON, 'Bounded JSON metadata required: '+str(path))
    with path.open('rb') as stream: data = stream.read(MAX_JSON+1)
    require(len(data) <= MAX_JSON, 'JSON metadata grew beyond byte bound')
    entry = pin(root, path, data)
    if expected is not None:
        if isinstance(expected, str): require(entry['sha256'] == expected, 'Input SHA256 differs: '+str(path))
        else:
            require(entry['sha256'] == expected['sha256'] and entry['bytes'] == expected['bytes']
                and path == resolve(root, expected['path']), 'Pinned metadata differs: '+str(path))
    value = json.loads(data)
    require(isinstance(value, dict), 'JSON metadata object required')
    return value


def validate_scores(cell):
    require(all(type(cell.get(k)) is int for k in ('n', 'correct', 'invalid', 'valid', 'unique_prompt_n', 'unique_source_n')),
        'Integer cell counts required')
    n = cell['n']
    require(n > 0 and 0 <= cell['correct'] <= cell['valid'] <= n and cell['invalid'] == n-cell['valid'], 'Invalid cell counts')
    require(0 < cell['unique_prompt_n'] <= n and 0 < cell['unique_source_n'] <= n, 'Invalid unique source/prompt support')
    require(math.isclose(cell['accuracy'], cell['correct']/n, abs_tol=1e-14)
        and math.isclose(cell['invalid_rate'], cell['invalid']/n, abs_tol=1e-14), 'Cell rates do not match counts')
    require('wilson_95' not in cell, 'Dependent logical cells must not carry independent-trial intervals')


def scientific_summary(review):
    """Verify the full declared tables and recompute all prospective decisions."""
    require(review.get('status') == 'complete_audited' and review.get('complete') is True
        and review.get('evaluation_role') == ROLE and review.get('generated_holdouts_opened') is False,
        'Completed discovery-only review required')
    require(review['instructions'] == list(VARIANTS) and review['forms'] == list(FORMS)
        and review['questions'] == list(QUESTIONS), 'Fixed instruction/form/question coverage differs')
    require(review['n'] == review['scored_unique_cases'] == 20100 and review['unique_sources'] == 6700
        and review['logical_source_views'] == 6912 and review['logical_responses'] == 20736,
        'Unique/logical calibration coverage differs')
    require(review['root_order_clusters'] == 24 and review['root_order_clusters_by_split'] == {'train': 12, 'development': 12},
        'Root-order cluster coverage differs')
    require(review['source_reuse'] == dict(unique_sources=6700, logical_source_views=6912,
        additional_logical_memberships=212, physical_sources_with_multiple_memberships=116,
        cross_split_literal_isolated_controls=68), 'Registered source-reuse metadata differs')
    expected_form = set(product(VARIANTS, FORMS, QUESTIONS, ('train', 'development')))
    actual_form = {}
    for cell in review['form_cells']:
        key = tuple(cell[k] for k in ('variant', 'form', 'question', 'split'))
        require(key not in actual_form, 'Duplicate aggregate form cell')
        validate_scores(cell); require(cell['root_order_clusters'] == 12, 'Form cell cluster support differs')
        actual_form[key] = cell
    require(set(actual_form) == expected_form and len(actual_form) == 72, 'All 72 aggregate form cells required')
    require(sum(cell['n'] for cell in actual_form.values()) == 20736, 'Logical form denominators differ')
    expected_gate = set(product(VARIANTS, FORMS, QUESTIONS, ('add', 'sub'), (-1, 1), ('train', 'development')))
    actual_gate = {}
    for cell in review['gate_cells']:
        key = tuple(cell[k] for k in ('variant', 'form', 'question', 'operator', 'answer_sign', 'split'))
        require(key not in actual_gate, 'Duplicate prospective gate cell')
        validate_scores(cell); actual_gate[key] = cell
    require(set(actual_gate) == expected_gate and len(actual_gate) == 288, 'All 288 prospective cells required')
    require(review['reliability_gate']['thresholds'] == THRESHOLDS, 'Prospective thresholds changed')
    require(set(review['reliability_gate']['instructions']) == set(VARIANTS), 'Every instruction gate required')
    gates = []
    for variant in VARIANTS:
        expected = [dict(cell, passed=cell['n'] >= 24 and cell['unique_prompt_n'] >= 24
            and cell['accuracy'] >= .9 and cell['invalid_rate'] <= .05)
            for key, cell in actual_gate.items() if key[0] == variant and key[1:3] != ('literal', 'arithmetic_only')]
        supplied = review['reliability_gate']['instructions'][variant]
        supplied_cells = {tuple(c[k] for k in ('form', 'question', 'operator', 'answer_sign', 'split')):c for c in supplied['cells']}
        require(len(supplied_cells) == len(expected) == 88, 'Complete required gate cells missing')
        for cell in expected:
            key = tuple(cell[k] for k in ('form', 'question', 'operator', 'answer_sign', 'split'))
            require(supplied_cells.get(key) == cell, 'Reported gate decision differs from saved cell counts')
        excluded = supplied['excluded_literal_isolated_controls']
        require(len(excluded) == 8 and all(c['form'] == 'literal' and c['question'] == 'arithmetic_only' for c in excluded),
            'Only predeclared repeated literal isolated controls may be excluded')
        train = all(c['passed'] for c in expected if c['split'] == 'train')
        dev = all(c['passed'] for c in expected if c['split'] == 'development')
        require(supplied['training_qualified'] == train and supplied['development_descriptive_passed'] == dev
            and supplied['numeric_development_qualified'] == (train and dev)
            and supplied['status'] == ('passed' if train and dev else 'failed'), 'Instruction qualification differs')
        gates.append(dict(variant=variant, status=supplied['status'], training_qualified=train,
            development_cells_passed=dev, numeric_development_qualified=train and dev,
            required_train_cells=44, failed_train_cells=sum(not c['passed'] for c in expected if c['split']=='train'),
            required_dev_cells=44, failed_dev_cells=sum(not c['passed'] for c in expected if c['split']=='development')))
    require(review['reliability_gate']['status'] == ('passed' if all(g['numeric_development_qualified'] for g in gates) else 'failed'),
        'Overall model gate status differs')
    expected_contrasts = set(product(VARIANTS, FORMS, ('add', 'sub'), (-1, 1), (1, 2, 4), ('train', 'development', 'all')))
    actual_contrasts = {}
    for cell in review['contrasts']:
        key = tuple(cell[k] for k in ('variant', 'form', 'operator', 'answer_sign', 'chain_depth', 'split'))
        require(key not in actual_contrasts, 'Duplicate contrast')
        lo, hi = cell['exploratory_group_bootstrap_95']
        require(-1 <= lo <= hi <= 1 and -1 <= cell['mean'] <= 1 and cell['n'] > 0,
            'Contrast bounds or means invalid')
        require(cell['name'] == 'full_leaf_minus_full_root' and cell['bootstrap_replicates'] == 2000
            and cell['bootstrap_seed'] == 913 and cell['multiplicity_adjusted'] is False
            and cell['primary'] == (cell['split'] == 'development')
            and cell['paired_groups'] == (24 if cell['split'] == 'all' else 12), 'Declared contrast scope differs')
        actual_contrasts[key] = cell
    require(set(actual_contrasts) == expected_contrasts and len(actual_contrasts) == 324, 'All 324 saved contrasts required')
    require(sum(c['primary'] for c in actual_contrasts.values()) == 108, 'All 108 primary DEV contrasts required')
    accounting = review['accounting']
    require(accounting['scored_responses'] == 20100 and accounting['scored_model_queries_lower_bound'] >= 20100
        and accounting['scored_model_queries_upper_bound'] >= accounting['scored_model_queries_lower_bound']
        and accounting['confirmed_warmup_requests'] >= 8, 'Scored/warm-up accounting differs')
    return dict(prospective_gates=gates, form_cells=list(actual_form.values()),
        primary_dev_contrasts=[cell for cell in actual_contrasts.values() if cell['primary']],
        context_contrasts=[cell for cell in actual_contrasts.values() if not cell['primary']])


def load_model(root, model):
    base = root/SUITE_REL/model
    receipt = read_json(root, base/'routing_completion_v1.json')
    require(receipt.get('status') == 'complete_audited' and receipt.get('evaluation_role') == ROLE
        and receipt.get('generated_holdouts_opened') is False and receipt.get('new_fits') == 0,
        'Completed matching calibration receipt required: '+model)
    require(set(receipt.get('artifacts', {})) == {'review', 'report'}, 'Exact completion inventory required')
    require(resolve(root, receipt['artifacts']['review']['path']) == base/'review_v1.json', 'Review path differs')
    review = read_json(root, base/'review_v1.json', receipt['artifacts']['review'])
    source = receipt['source']
    require(review['source'] == source and review['config_hash'] == receipt['config_hash']
        and review['n'] == receipt['scored_cases'] == 20100, 'Receipt and review identities differ')
    frozen_root = resolve(root, source['snapshot'])
    frozen = read_json(root, frozen_root/'frozen_manifest.json', source['frozen_manifest_sha256'])
    require(frozen['snapshot_id'] == source['snapshot_id']
        and frozen['code']['source_sha256'] == source['source_sha256'], 'Frozen code identity differs')
    profile_rel = Path('configs/binding/computation_routing_20261028_v1')/(model+'.json')
    require(str(profile_rel) in frozen['config_files'], 'Exact model profile was not frozen')
    profile = read_json(root, frozen_root/profile_rel, frozen['config_files'][str(profile_rel)])
    require(digest(profile) == receipt['config_hash'] and profile['model'] == review['model'] == MODELS[model][1]
        and profile['model_revision'] == review['model_revision'] == MODELS[model][2]
        and profile['tokenizer_revision'] == profile['model_revision'], 'Frozen model profile differs')
    require(profile['evaluation_role'] == ROLE and profile['reliability_gate'] == THRESHOLDS,
        'Model profile role or thresholds differ')
    artifacts = review['artifacts']
    metadata = {}
    for name, relative in [('backend_audit', 'checkpoint_suite/audit.json'),
            ('backend_manifest', 'checkpoint_suite/manifest.json'), ('preparation', 'routing_preflight_v1.json')]:
        path = base/relative
        require(resolve(root, artifacts[name]['path']) == path, 'Typed metadata path differs: '+name)
        metadata[name] = read_json(root, path, artifacts[name])
    backend = metadata['backend_manifest']; audit = metadata['backend_audit']; prep = metadata['preparation']
    require(backend['status'] == 'complete' and backend['identity']['config'] == profile
        and digest(backend['identity']) == backend['identity_hash'] == audit['identity_hash']
        and backend['identity']['code']['source_sha256'] == source['source_sha256'], 'Backend identity differs')
    require(audit['status'] == 'passed' and audit['complete'] is True and audit['evaluated'] == 20100
        and audit['model'] == review['model'] and audit['revision'] == review['model_revision'], 'Completed backend audit required')
    require(prep['status'] == 'passed' and prep['source'] == source and prep['config_hash'] == receipt['config_hash']
        and prep['model_inference'] is False and prep['generated_holdouts_opened'] is False, 'Preparation identity differs')
    for name in ('dataset_sha256', 'dataset_manifest_sha256', 'declared_plan_sha256'):
        require(review[name] == prep[name] == profile[name], 'Pinned dataset/plan metadata differs: '+name)
    require(resolve(root, prep['artifacts']['preflight_result']['path']) == resolve(root, profile['preflight_result']),
        'Prepared preflight metadata path differs')
    qa = read_json(root, profile['preflight_result'], prep['artifacts']['preflight_result'])
    require(qa == audit['preflight'] and qa['cases'] == 20100 and qa['config_hash'] == receipt['config_hash']
        and qa['source_sha256'] == source['source_sha256']
        and qa['prepared_cases_sha256'] == prep['artifacts']['prepared_cases']['sha256'], 'Prepared metadata proof differs')
    runtime = read_json(root, base/'checkpoint_suite/runtime.json')
    summary = read_json(root, base/'checkpoint_suite/summary.json')
    require(runtime == audit['runtime'], 'Runtime metadata differs from pinned backend audit')
    for name in ('cells', 'complete', 'evaluated', 'planned', 'generated_holdouts_opened', 'gpu', 'timings', 'interpretation'):
        require(summary[name] == audit[name], 'Summary metadata differs from pinned backend audit: '+name)
    require(summary['responses_sha256'] == backend['responses_sha256'] == artifacts['responses']['sha256'],
        'Audited response checksum metadata differs; raw responses are not opened')
    require(sum(c['n'] for c in summary['cells']) == 20100
        and sum(c['correct'] for c in summary['cells']) == review['correct']
        and sum(c['n']-c['valid'] for c in summary['cells']) == review['invalid'], 'Physical counts differ')
    for name in ('new_model_queries', 'new_model_queries_lower_bound', 'new_model_queries_upper_bound'):
        require(receipt[name] == review[name], 'Receipt query accounting differs')
    extracted = scientific_summary(review)
    seconds = sum(t['generation_seconds'] for t in summary['timings'])
    return dict(model=model, label=MODELS[model][0], checkpoint=review['model'], model_revision=review['model_revision'],
        status='complete_audited', source=source, config_hash=receipt['config_hash'], profile=str((frozen_root/profile_rel).relative_to(root)),
        dataset_sha256=review['dataset_sha256'], dataset_manifest_sha256=review['dataset_manifest_sha256'],
        declared_plan_sha256=review['declared_plan_sha256'], receipt=str((base/'routing_completion_v1.json').relative_to(root)),
        original_review=receipt['artifacts']['review'], physical_counts={key:review[key] for key in ('n','correct','valid','invalid','accuracy','invalid_rate')},
        scored_unique_cases=review['scored_unique_cases'], logical_responses=review['logical_responses'],
        unique_sources=review['unique_sources'], logical_source_views=review['logical_source_views'], source_reuse=review['source_reuse'],
        source_gate_details=review['reliability_gate'], accounting=review['accounting'],
        new_model_queries=review['new_model_queries'], new_model_queries_lower_bound=review['new_model_queries_lower_bound'],
        new_model_queries_upper_bound=review['new_model_queries_upper_bound'],
        resources=dict(device_name=runtime['device_name'], engine=runtime['engine'], versions=runtime['versions'],
            load_warmup_seconds=runtime['load_warmup_seconds'], generation_seconds=seconds,
            generation_requests_per_second=20100/seconds, backend_wall_seconds_total=backend['wall_seconds_total'],
            gpu=summary['gpu'], scope='Generation timing/utilization excludes engine loading; GPU memory includes allocator reservations/KV cache.'),
        **extracted)


def csv_bytes(rows, columns):
    stream = io.StringIO(newline=''); writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n', extrasaction='ignore')
    writer.writeheader(); writer.writerows(rows)
    return stream.getvalue().encode()


def tables(models):
    form_rows = []; contrast_rows = []
    for model in MODEL_KEYS:
        value = models[model]
        for cell in value['form_cells']:
            row = dict(model=model, **cell)
            for kind in ('prompt_tokens','generated_tokens'):
                for field in ('n','min','max','mean'): row[kind+'_'+field] = cell[kind][field]
            form_rows.append(row)
        for cell in value['primary_dev_contrasts']+value['context_contrasts']:
            lo, hi = cell['exploratory_group_bootstrap_95']
            contrast_rows.append(dict(model=model, **cell, mean_percentage_points=100*cell['mean'],
                ci_low=lo, ci_high=hi, ci_low_percentage_points=100*lo, ci_high_percentage_points=100*hi))
    form_rows.sort(key=lambda r: (MODEL_KEYS.index(r['model']), VARIANTS.index(r['variant']), FORMS.index(r['form']), r['split'], QUESTIONS.index(r['question'])))
    contrast_rows.sort(key=lambda r: (MODEL_KEYS.index(r['model']), VARIANTS.index(r['variant']), FORMS.index(r['form']), r['split'], r['operator'], r['answer_sign'], r['chain_depth']))
    form_columns = ['model','variant','form','question','split','correct','n','valid','invalid','accuracy','invalid_rate',
        'unique_source_n','unique_prompt_n','root_order_clusters','prompt_tokens_n','prompt_tokens_min','prompt_tokens_max','prompt_tokens_mean',
        'generated_tokens_n','generated_tokens_min','generated_tokens_max','generated_tokens_mean','uncertainty']
    contrast_columns = ['model','variant','form','operator','answer_sign','chain_depth','split','primary','inference_scope','name',
        'n','paired_groups','mean','mean_percentage_points','ci_low','ci_high','ci_low_percentage_points','ci_high_percentage_points',
        'bootstrap_replicates','bootstrap_seed','multiplicity_adjusted','resampling_unit']
    return form_rows, contrast_rows, csv_bytes(form_rows,form_columns), csv_bytes(contrast_rows,contrast_columns)


def figure_bytes(models):
    import matplotlib
    matplotlib.use('Agg', force=True)
    matplotlib.rcParams.update({'svg.hashsalt':'computation_routing_v1', 'font.family':'DejaVu Sans', 'font.size':10})
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 2, figsize=(12, 10), sharex=True, sharey=True)
    colors = {'literal':'#087e8b','small':'#2463ad','cancellation':'#c45426'}
    markers = {'literal':'o','small':'s','cancellation':'^'}
    for i, variant in enumerate(VARIANTS):
        for j, model in enumerate(MODEL_KEYS):
            ax=axes[i,j]
            for form in FORMS:
                cells={c['question']:c for c in models[model]['form_cells'] if c['variant']==variant and c['form']==form and c['split']=='development'}
                ax.plot(range(4), [100*cells[q]['accuracy'] for q in QUESTIONS], color=colors[form], marker=markers[form],
                    linewidth=1.8, markersize=5, label=FORM_LABELS[form])
            ax.set_ylim(0,103); ax.set_xlim(-.15,3.15); ax.set_yticks([0,20,40,60,80,100])
            ax.grid(axis='y',alpha=.2); ax.spines[['top','right']].set_visible(False)
            ax.set_title(MODELS[model][0]+' · instruction '+str(i+1), fontsize=11)
            ax.text(.02,.04,variant,transform=ax.transAxes,fontsize=8,color='#444444')
            if j==0:ax.set_ylabel('DEV correct (%)')
            ax.set_xticks(range(4), ['Single\nassignment','Roots\nonly','Full:\nroot','Full:\ncopied leaf'])
            ax.tick_params(labelbottom=True)
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(.5,.037))
    fig.suptitle('Computation and routing calibration: all fixed instructions',fontsize=15,y=.985)
    fig.text(.5,.012,'Descriptive pooled DEV point estimates. Reused controls have no independent-trial intervals.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.08,1,.965),h_pad=2,w_pad=2)
    png=io.BytesIO(); svg=io.BytesIO()
    fig.savefig(png,format='png',dpi=170,metadata={'Software':'CodeCue deterministic calibration publisher'})
    fig.savefig(svg,format='svg',metadata={'Date':None,'Creator':'CodeCue deterministic calibration publisher'})
    plt.close(fig)
    return png.getvalue(),svg.getvalue(),matplotlib.__version__


def report_bytes(models):
    qualified=sum(g['numeric_development_qualified'] for m in models.values() for g in m['prospective_gates'])
    reuse=models[MODEL_KEYS[0]]['source_reuse']
    lines=['# Computation and routing discovery calibration', '',
        f"Both checkpoints completed and passed their artifact audits. **{qualified}/6 prospective instruction gates qualified.** "
        'Execution completion and scientific qualification are separate.', '',
        'Each model generated 20,100 unique scored responses from 6,700 sources under three fixed instructions. '
        'These map to 20,736 logical responses from 6,912 logical source views. '
        'Every reused response retains its explicit membership; logical views are dependent.', '',
        '| Model | Unique correct / n | Invalid | Confirmed warm-ups | New model requests |', '|---|---:|---:|---:|---:|']
    for model in MODEL_KEYS:
        m=models[model];c=m['physical_counts'];exact=m['new_model_queries']
        requests=str(exact) if exact is not None else f"[{m['new_model_queries_lower_bound']}, {m['new_model_queries_upper_bound']}]"
        lines.append(f"| {m['label']} | {c['correct']:,}/{c['n']:,} | {c['invalid']:,} | {m['accounting']['confirmed_warmup_requests']} | {requests} |")
    lines+=['','A gate requires at least 24 evaluated and 24 unique prompts, at least 90% accuracy and at most 5% invalid '
        'in every registered form × question × operator × answer-sign cell, first on TRAIN and then DEV. '
        'Query slots, copy depths/topologies and lexical forms are pooled prospectively. '
        'Only repeated literal single-assignment controls are excluded. All three instructions remain reported; no fallback is selected.', '',
        '| Model | Instruction | TRAIN qualified | DEV cells passed | TRAIN→DEV qualified | Failed TRAIN / DEV cells |',
        '|---|---|---|---|---|---:|']
    for model in MODEL_KEYS:
        for g in models[model]['prospective_gates']:
            lines.append(f"| {models[model]['label']} | {g['variant']} | {g['training_qualified']} | {g['development_cells_passed']} | "
                f"{g['numeric_development_qualified']} | {g['failed_train_cells']}/44 / {g['failed_dev_cells']}/44 |")
    lines+=['','![DEV accuracy across all instructions and root forms](figures/computation_routing_v1.svg)', '',
        'The single-assignment condition (`arithmetic_only`) assigns the queried expression to a variable and reads it. '
        'Roots-only adds the three literal distractor roots. Full-root and full-leaf have the same four roots, four copies and correct answer; '
        'the final queried identifier changes. Recency and query selection still differ. Compact and larger expressions both use one operation; '
        'their operand ranges partly overlap, and magnitude, cancellation extent and tokenization change together.', '',
        'The table reports DEV correct/logical n; invalid answers count as wrong. Full-context points pool depths 1, 2 and 4. '
        'All TRAIN and DEV counts, invalids, unique prompt support and token geometry are retained in '
        '[form_cells_v1.csv](../../artifacts/binding/computation_routing/20261028_v1/form_cells_v1.csv).', '',
        '| Model | Instruction | Root form | Single assignment | Roots only | Full: root | Full: copied leaf |',
        '|---|---|---|---:|---:|---:|---:|']
    for model in MODEL_KEYS:
        for variant in VARIANTS:
            for form in FORMS:
                cells={c['question']:c for c in models[model]['form_cells'] if c['variant']==variant and c['form']==form and c['split']=='development'}
                points=[f"{cells[q]['correct']}/{cells[q]['n']} ({100*cells[q]['accuracy']:.1f}%)" for q in QUESTIONS]
                lines.append('| '+' | '.join([models[model]['label'],variant,FORM_LABELS[form],*points])+' |')
    lines+=['','Every model retains all **108 primary DEV full-leaf minus full-root contrasts**, separately by instruction, root form, '
        'operator, answer sign and copy depth. Their saved 95% exploratory intervals use 2,000 whole root-order-cluster bootstraps '
        '(seed 913; 12 DEV clusters). No refit, new bootstrap or multiplicity adjustment was performed for this publication. '
        '[contrasts_v1.csv](../../artifacts/binding/computation_routing/20261028_v1/contrasts_v1.csv) retains all 216 primary DEV '
        'contrasts plus 432 TRAIN/all descriptive-context rows. No binomial intervals are assigned to reused control views.', '',
        f"Each instruction maps {reuse['unique_sources']:,} physical sources to {reuse['logical_source_views']:,} logical views: "
        f"{reuse['additional_logical_memberships']} additional memberships, {reuse['physical_sources_with_multiple_memberships']} sources with multiple "
        f"memberships and {reuse['cross_split_literal_isolated_controls']} literal isolated controls shared across splits. "
        'These repeated controls do not establish independent generalization. '
        'A failure in a larger context does not identify whether arithmetic, copying or selection caused the response; '
        'separate invalid counts preserve interface failures.', '',
        '| Model | GPU | Load + warm-up (s) | Timed generation (s) | Generation requests/s | Mean generation GPU util. |',
        '|---|---|---:|---:|---:|---:|']
    for model in MODEL_KEYS:
        r=models[model]['resources']
        lines.append(f"| {models[model]['label']} | {r['device_name']} | {r['load_warmup_seconds']:.2f} | {r['generation_seconds']:.2f} | "
            f"{r['generation_requests_per_second']:.1f} | {r['gpu']['mean_gpu_utilization_percent']:.2f}% |")
    lines+=['','Generation timing/utilization covers the monitored generation loop and excludes model loading. '
        'Device-memory metadata includes allocator reservations and KV cache. These figures are workload-specific.', '',
        'This is a narrower adaptive discovery calibration on familiar forms. Numeric, lexical, topology and instruction relatives '
        'are not independent structural replications. No general arithmetic guarantee, causal owner/version mechanism, '
        'new scientific model family or unfamiliar-program prediction is established. Historical gates and sealed outcomes remain unchanged.', '',
        'The publisher reads only completed receipts, SHA-pinned reviews, frozen profiles and audited preparation/runtime/summary metadata. '
        'It opens no raw responses, prepared/source JSONL, activation arrays or model. '
        '[comparison_v1.json](../../artifacts/binding/computation_routing/20261028_v1/comparison_v1.json) contains the consolidated values '
        'and input pins; [publication_review_v1.json](../../artifacts/binding/computation_routing/20261028_v1/publication_review_v1.json) pins every output.', '']
    return '\n'.join(lines).encode()


def publish(path, data):
    path=Path(path)
    require(not path.is_symlink(), 'Publication must not follow output symlinks')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.is_file() and path.read_bytes()==data, 'Immutable publication differs: '+str(path)); return
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.'+path.name+'.',suffix='.pending',delete=False) as stream:
            temporary=Path(stream.name);stream.write(data);stream.flush();os.fsync(stream.fileno())
        try:os.link(temporary,path)
        except FileExistsError:require(not path.is_symlink() and path.read_bytes()==data,'Concurrent publication differs')
    finally:
        if temporary is not None and temporary.exists():temporary.unlink()


def publication(root):
    INPUTS.clear(); base=root/SUITE_REL
    missing=[m for m in MODEL_KEYS if not (base/m/'routing_completion_v1.json').is_file()]
    require(not missing, 'Publication incomplete: both completed model receipts are required; missing '+', '.join(missing))
    models={model:load_model(root,model) for model in MODEL_KEYS}
    for key in ('dataset_sha256','dataset_manifest_sha256','declared_plan_sha256'):
        require(models['llama8b'][key]==models['codellama34b'][key], 'Model panels do not share registered inputs')
    script=Path(__file__).resolve();script_pin=pin(root,script,script.read_bytes())
    form_rows, contrast_rows, form_csv, contrast_csv = tables(models)
    png,svg,plot_version=figure_bytes(models)
    png2,svg2,_=figure_bytes(models)
    require((png,svg)==(png2,svg2),'Repeated figure render is not byte reproducible')
    require(len(form_rows)==144 and len(contrast_rows)==648 and sum(r['primary'] for r in contrast_rows)==216,
        'Publication table coverage differs')
    comparison=dict(status='complete_metadata_publication',evaluation_role=PUBLICATION_ROLE,
        models=models, model_count=2, prospective_instruction_gates=6,
        qualified_instruction_gates=sum(g['numeric_development_qualified'] for m in models.values() for g in m['prospective_gates']),
        scored_unique_responses=40200,logical_responses=41472,form_cell_rows=144,contrast_rows=648,primary_dev_contrast_rows=216,
        scientific_model_requests_exact=(sum(m['new_model_queries'] for m in models.values())
            if all(m['new_model_queries'] is not None for m in models.values()) else None),
        scientific_model_requests_lower_bound=sum(m['new_model_queries_lower_bound'] for m in models.values()),
        scientific_model_requests_upper_bound=sum(m['new_model_queries_upper_bound'] for m in models.values()),
        scientific_confirmed_warmup_requests=sum(m['accounting']['confirmed_warmup_requests'] for m in models.values()),
        input_pins=sorted(INPUTS.values(),key=lambda p:p['path']),publisher_script=script_pin,
        new_model_queries=0,new_fits=0,raw_responses_opened=False,source_or_prepared_records_opened=False,
        activation_arrays_opened=False,generated_holdouts_opened=False,limitations=LIMITATIONS)
    outputs={base/'comparison_v1.json':json_bytes(comparison),base/'form_cells_v1.csv':form_csv,
        base/'contrasts_v1.csv':contrast_csv,root/'reports/binding/computation_routing_findings_v1.md':report_bytes(models),
        root/'reports/binding/figures/computation_routing_v1.png':png,root/'reports/binding/figures/computation_routing_v1.svg':svg}
    review=dict(status='passed',evaluation_role=PUBLICATION_ROLE,publisher_script=script_pin,
        input_pins=sorted(INPUTS.values(),key=lambda p:p['path']),output_pins=[dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)) for path,data in outputs.items()],
        checks=dict(both_completed_receipts_required=True,receipt_review_sha256_verified=True,frozen_profile_identities_verified=True,
            audited_metadata_matches=True,all_144_form_cells_preserved=True,all_216_primary_dev_contrasts_preserved=True,
            all_432_context_contrasts_preserved=True,all_6_prospective_gates_recomputed=True,
            dependent_control_binomial_intervals_absent=True,repeated_figure_render_byte_identical=True),
        plotting_version=plot_version,reproduction='Every invocation regenerates and byte-checks all existing outputs; rerun must be identical.',
        new_model_queries=0,new_fits=0,raw_responses_opened=False,source_or_prepared_records_opened=False,
        activation_arrays_opened=False,generated_holdouts_opened=False)
    outputs[base/'publication_review_v1.json']=json_bytes(review)
    existed=all(path.is_file() for path in outputs)
    for path,data in outputs.items():
        require(not path.is_symlink() and (not path.exists() or path.read_bytes()==data), 'Immutable publication differs before any write: '+str(path))
    for path,data in outputs.items():publish(path,data)
    return dict(status='byte_identical_reproduction' if existed else 'published',models=2,qualified_instruction_gates=comparison['qualified_instruction_gates'],
        form_cell_rows=144,primary_dev_contrast_rows=216,all_contrast_rows=648,publication_review=str((base/'publication_review_v1.json').relative_to(root)))


def synthetic_review():
    review=dict(status='complete_audited',complete=True,evaluation_role=ROLE,generated_holdouts_opened=False,
        instructions=list(VARIANTS),forms=list(FORMS),questions=list(QUESTIONS),n=20100,scored_unique_cases=20100,
        unique_sources=6700,logical_source_views=6912,logical_responses=20736,root_order_clusters=24,
        source_reuse=dict(unique_sources=6700,logical_source_views=6912,additional_logical_memberships=212,
            physical_sources_with_multiple_memberships=116,cross_split_literal_isolated_controls=68),
        root_order_clusters_by_split={'train':12,'development':12},form_cells=[],gate_cells=[],contrasts=[],
        reliability_gate=dict(thresholds=THRESHOLDS,status='passed',instructions={}),
        accounting=dict(scored_responses=20100,scored_model_queries_lower_bound=20100,scored_model_queries_upper_bound=20100,confirmed_warmup_requests=8))
    for variant,form,question,split in product(VARIANTS,FORMS,QUESTIONS,('train','development')):
        n=144 if question in QUESTIONS[:2] else 432
        cell=dict(variant=variant,form=form,question=question,split=split,n=n,correct=n,valid=n,invalid=0,accuracy=1.,invalid_rate=0.,
            unique_source_n=n,unique_prompt_n=n,root_order_clusters=12,
            prompt_tokens=dict(n=n,min=30,max=40,mean=35.),generated_tokens=dict(n=n,min=2,max=2,mean=2.),uncertainty='Dependent synthetic views')
        review['form_cells'].append(cell)
        for operator,sign in product(('add','sub'),(-1,1)):
            review['gate_cells'].append(dict(cell,operator=operator,answer_sign=sign,n=n//4,correct=n//4,valid=n//4,unique_prompt_n=n//4,unique_source_n=n//4))
    for variant in VARIANTS:
        cells=[dict(c,passed=True) for c in review['gate_cells'] if c['variant']==variant and (c['form'],c['question'])!=('literal','arithmetic_only')]
        excluded=[dict(c,gate_exclusion='Synthetic registered exclusion') for c in review['gate_cells'] if c['variant']==variant and (c['form'],c['question'])==('literal','arithmetic_only')]
        review['reliability_gate']['instructions'][variant]=dict(status='passed',training_qualified=True,development_descriptive_passed=True,numeric_development_qualified=True,cells=cells,excluded_literal_isolated_controls=excluded)
    for variant,form,operator,sign,depth,split in product(VARIANTS,FORMS,('add','sub'),(-1,1),(1,2,4),('train','development','all')):
        review['contrasts'].append(dict(variant=variant,form=form,operator=operator,answer_sign=sign,chain_depth=depth,split=split,
            primary=split=='development',name='full_leaf_minus_full_root',mean=0.,exploratory_group_bootstrap_95=[0.,0.],n=72 if split=='all' else 36,
            paired_groups=24 if split=='all' else 12,bootstrap_replicates=2000,bootstrap_seed=913,multiplicity_adjusted=False,
            inference_scope='synthetic',resampling_unit='root_order_cluster'))
    return review


def self_test():
    review=synthetic_review();summary=scientific_summary(review)
    require(len(summary['form_cells'])==72 and len(summary['primary_dev_contrasts'])==108,'Synthetic coverage failed')
    models={model:dict(summary,model=model) for model in MODEL_KEYS}
    form_rows,contrast_rows,fc,cc=tables(models)
    require(len(list(csv.DictReader(io.StringIO(fc.decode()))))==144 and len(list(csv.DictReader(io.StringIO(cc.decode()))))==648,'CSV coverage failed')
    png,svg,_=figure_bytes(models);png2,svg2,_=figure_bytes(models)
    require((png,svg)==(png2,svg2),'Synthetic figure reproducibility failed')
    mutations=[]
    broken=deepcopy(review);broken['form_cells'].pop();mutations.append(broken)
    broken=deepcopy(review);broken['contrasts'][1]=broken['contrasts'][0];mutations.append(broken)
    broken=deepcopy(review);broken['reliability_gate']['instructions'][VARIANTS[0]]['training_qualified']=False;mutations.append(broken)
    broken=deepcopy(review);broken['contrasts'][0]['primary']=True;mutations.append(broken)
    for broken in mutations:
        try:scientific_summary(broken)
        except ValueError:pass
        else:raise ValueError('Malformed synthetic scientific metadata was accepted')
    with tempfile.TemporaryDirectory(prefix='calibration-publisher-') as folder:
        path=Path(folder)/'output.json';publish(path,b'fixed\n');publish(path,b'fixed\n')
        try:publish(path,b'different\n')
        except ValueError:pass
        else:raise ValueError('Immutable output conflict was accepted')
        try:read_json(Path(folder),Path(folder)/'responses.jsonl')
        except ValueError:pass
        else:raise ValueError('Raw scientific record input was accepted')
    return dict(status='passed_synthetic_self_test',scientific_inputs_opened=False,model_queries=0,
        form_rows=len(form_rows),contrast_rows=len(contrast_rows),primary_dev_rows=sum(r['primary'] for r in contrast_rows),repeated_png_svg_identical=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true',help='Only synthetic CPU checks; no scientific inputs or publication')
    args=parser.parse_args()
    try:result=self_test() if args.self_test else publication(workspace())
    except (ValueError,KeyError,OSError) as exc:
        print(json.dumps(dict(status='publication_not_written',error=f'{type(exc).__name__}: {exc}')),file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
