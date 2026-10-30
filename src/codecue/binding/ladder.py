"""A fixed training-only assignment/dependency difficulty ladder and its gate."""
from __future__ import annotations

import ast
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from .calibration import parse_completion, VARIANTS
from .datasets import digest, read_jsonl, write_json
from .interpreter import execute, python_oracle

ROLE = 'difficulty_ladder_only'
STYLES = ('reassigned_chain', 'fresh_chain', 'independent_arithmetic')


def load_plan(config):
    calibration = config['calibration']
    path = Path(calibration['ladder_plan'])
    if hashlib.sha256(path.read_bytes()).hexdigest() != calibration['ladder_plan_sha256']:
        raise ValueError('difficulty ladder plan checksum mismatch')
    plan = json.loads(path.read_text())
    if (plan['schema_version'] != 1 or plan['evaluation_role'] != ROLE
            or plan['assignment_counts'] != [1, 2, 4, 8]
            or plan['styles'] != list(STYLES) or plan['positive_targets'] != [2, 5, 8, 11]
            or plan['variants'] != ['print_direct_v3', 'print_trace_long_v1']
            or plan['programs'] != 120 or plan['query_cap'] != 240):
        raise ValueError('unsupported ladder design; version a changed design explicitly')
    return plan


def canonical(source):
    return ast.dump(ast.parse(source), include_attributes=False)


def expression(previous, delta):
    return f'{previous} + {delta}' if delta > 0 else f'{previous} - {-delta}'


def cell_keys(plan):
    return [('computed_baseline', 1)] + [(style, n) for n in plan['assignment_counts'][1:] for style in STYLES]


def validate_rows(rows, plan):
    if len(rows) != plan['programs'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('ladder must contain every unique planned program')
    if any(r['split'] != 'train' or r['evaluation_role'] != ROLE for r in rows):
        raise ValueError('difficulty ladder is training-only')
    counts = Counter((r['style'], r['assignment_count'], r['answer_sign']) for r in rows)
    if counts != Counter({(style, n, sign): 4 for style, n in cell_keys(plan) for sign in (-1, 0, 1)}):
        raise ValueError('ladder cells must be complete and sign-balanced')
    if len({canonical(r['source']) for r in rows}) != len(rows):
        raise ValueError('duplicate ladder program')
    groups = {}
    for row in rows:
        trace = execute(row['source'])
        if (trace['expected_answer'] != row['expected_answer']
                or (row['expected_answer'] > 0) - (row['expected_answer'] < 0) != row['answer_sign']
                or len(trace['execution_trace']) != row['assignment_count']
                or trace['dependency_depth'] != row['dependency_depth']
                or trace['execution_trace'] != row['execution_trace']):
            raise ValueError('ladder oracle metadata mismatch')
        expected_depth = 1 if row['style'] in ('computed_baseline', 'independent_arithmetic') else row['assignment_count']
        if row['dependency_depth'] != expected_depth:
            raise ValueError('ladder dependency depth mismatch')
        groups.setdefault(row['paired_group_id'], []).append(row)
    for group in groups.values():
        if len(group) != (1 if group[0]['assignment_count'] == 1 else 3):
            raise ValueError('matched ladder group incomplete')
        paths = {tuple(p['value'] for p in r['execution_trace']) for r in group}
        if len(paths) != 1 or len({r['expected_answer'] for r in group}) != 1:
            raise ValueError('matched ladder computation differs')
    return rows


def build(config):
    plan = load_plan(config)
    path = Path(config['dataset'])
    if path.exists() or path.with_suffix('.manifest.json').exists():
        raise ValueError('difficulty ladder dataset is immutable')
    rng = random.Random(plan['seed'])
    from .diagnostics import cases
    excluded = {canonical(r['source']) for r in cases([])}
    upstream = {}
    for name in config['calibration'].get('exclude_datasets', []):
        exclusion = Path(name)
        excluded.update(canonical(r['source']) for r in read_jsonl(exclusion))
        upstream[name] = hashlib.sha256(exclusion.read_bytes()).hexdigest()
    seen = set(excluded)
    rows = []
    proposals = 0
    for n in plan['assignment_counts']:
        for sign in (-1, 0, 1):
            for replicate, magnitude in enumerate(plan['positive_targets']):
                target = sign * magnitude
                while True:
                    proposals += 1
                    if proposals > 100000:
                        raise ValueError('bounded ladder generation exhausted')
                    values = [rng.randint(-12, 12) for _ in range(n-1)] + [target]
                    deltas = [b-a for a, b in zip(values, values[1:])]
                    if any(not 1 <= abs(d) <= 9 for d in deltas):
                        continue
                    operator = '+' if replicate % 2 == 0 else '-'
                    a = rng.choice([i for i in range(-12, 13) if i])
                    b = values[0] - a if operator == '+' else a - values[0]
                    if not b or abs(b) > 12 or values[0] in (a, b):
                        continue
                    initial = f'v0 = {a} {operator} {b}'
                    sources = {}
                    for style in (('computed_baseline',) if n == 1 else STYLES):
                        statements = [initial]
                        for step, delta in enumerate(deltas, 1):
                            target_name = 'v0' if style == 'reassigned_chain' else f'v{step}'
                            previous = ('v0' if style == 'reassigned_chain' else f'v{step-1}')
                            if style == 'independent_arithmetic':
                                previous = str(values[step-1])
                            statements.append(f'{target_name} = {expression(previous, delta)}')
                        final_name = 'v0' if style == 'reassigned_chain' or n == 1 else f'v{n-1}'
                        sources[style] = '\n'.join(statements + [final_name])
                    keys = [canonical(source) for source in sources.values()]
                    if len(keys) != len(set(keys)) or any(key in seen for key in keys):
                        continue
                    seen.update(keys)
                    break
                paired = f'ladder:{n}:{sign}:{replicate}'
                for style, source in sources.items():
                    trace = execute(source)
                    rows.append(dict(id='ladder:'+digest(source)[:24], split='train', evaluation_role=ROLE,
                                     family=style, style=style, assignment_count=n, answer_sign=sign,
                                     numeric_target_group=f'{sign}:{replicate}', paired_group_id=paired,
                                     source=source, seed=plan['seed'], expected_answer=target,
                                     dependency_depth=trace['dependency_depth'], execution_trace=trace['execution_trace']))
    validate_rows(rows, plan)
    oracle = python_oracle([r['source'] for r in rows])
    if any(r['expected_answer'] != o['answer'] or [p['values'] for p in r['execution_trace']] != o['trace']
           for r, o in zip(rows, oracle)):
        raise ValueError('independent ladder Python mismatch')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in rows))
    result = dict(status='validated', schema_version=1, evaluation_role=ROLE, split='train', rows=len(rows),
                  sha256=hashlib.sha256(path.read_bytes()).hexdigest(), seed=plan['seed'], proposals=proposals,
                  plan_sha256=config['calibration']['ladder_plan_sha256'], plan=plan,
                  independent_python_programs=len(rows), excluded_datasets=upstream,
                  excluded_fixed_fixtures=8, numeric_target_groups=12, matched_path_groups=48,
                  limitations='Repeated structures and shared targets; training-only calibration, not independent confirmation')
    write_json(path.with_suffix('.manifest.json'), result)
    return result


def select_regime(rows, observed, plan):
    validate_rows(rows, plan)
    records = {r['id']: r for r in rows}
    expected = {(r['id'], variant) for r in rows for variant in plan['variants']}
    keys = [(r['id'], r['variant']) for r in observed]
    if len(set(keys)) != len(keys) or not set(keys) <= expected:
        raise ValueError('unknown or duplicate ladder response')
    for row in observed:
        original = records[row['id']]
        variant = row['variant']
        prediction = parse_completion(row['raw_response'], VARIANTS[variant]['answer_mode'])
        if (row['split'] != 'train' or row['evaluation_role'] != ROLE
                or any(row[k] != original[k] for k in ('source', 'expected_answer', 'style', 'assignment_count', 'answer_sign'))
                or row['prediction'] != prediction or row['invalid'] != (prediction is None)
                or row['correct'] != (prediction == original['expected_answer'])):
            raise ValueError('ladder response oracle or score mismatch')
    cells = []
    for variant in plan['variants']:
        for style, n in cell_keys(plan):
            group = [r for r in observed if r['variant'] == variant
                     and records[r['id']]['style'] == style and records[r['id']]['assignment_count'] == n]
            cells.append(dict(variant=variant, style=style, assignment_count=n, n=len(group),
                              correct=sum(r['correct'] for r in group), invalid=sum(r['invalid'] for r in group),
                              by_sign={str(sign): dict(n=sum(r['answer_sign'] == sign for r in group),
                                  correct=sum(r['answer_sign'] == sign and r['correct'] for r in group))
                                  for sign in (-1, 0, 1)}))
    complete = set(keys) == expected
    eligible = []
    gate = plan['gate']
    by_cell = {(r['variant'], r['style'], r['assignment_count']): r for r in cells}
    if complete:
        for variant in plan['variants']:
            baseline = by_cell[(variant, 'computed_baseline', 1)]
            if baseline['correct'] < gate['minimum_baseline_correct'] or baseline['invalid'] > gate['maximum_invalid_per_cell']:
                continue
            for n in plan['assignment_counts'][1:]:
                control = by_cell[(variant, 'independent_arithmetic', n)]
                chains = [by_cell[(variant, style, n)] for style in STYLES[:2]]
                if (control['correct'] >= gate['minimum_independent_correct']
                        and control['invalid'] <= gate['maximum_invalid_per_cell']
                        and all(gate['minimum_chain_correct'] <= r['correct'] <= gate['maximum_chain_correct']
                                and r['invalid'] <= gate['maximum_invalid_per_cell'] for r in chains)):
                    eligible.append(dict(variant=variant, assignment_count=n))
    return dict(status=('selected_for_fresh_discovery_design' if eligible else
                        'stop_no_usable_regime' if complete else 'incomplete_no_selection'),
                complete=complete, selected=eligible[0] if eligible else None, eligible=eligible,
                queries_completed=len(keys), queries_planned=len(expected), cells=cells,
                heldout_outcomes_opened=False, gate=gate, stopping_rule=plan['stopping_rule'],
                interpretation='Training calibration gate only; no causal conclusion, population interval or final-test authorization')


def analyze(config):
    plan = load_plan(config)
    out = Path(config['run_dir'])/'protocol_calibration'
    output = out/'ladder_decision.json'
    if output.exists():
        raise ValueError('ladder decision is immutable')
    manifest = json.loads((out/'manifest.json').read_text())
    identity = manifest['identity']
    if manifest['identity_hash'] != digest(identity) or identity['config'] != config:
        raise ValueError('ladder run identity differs')
    rows = read_jsonl(config['dataset'])
    if hashlib.sha256(Path(config['dataset']).read_bytes()).hexdigest() != identity['dataset_manifest']['sha256']:
        raise ValueError('ladder dataset changed')
    observed_path = out/'responses.jsonl'
    observed = read_jsonl(observed_path) if observed_path.exists() else []
    result = select_regime(rows, observed, plan)
    if result['complete'] and manifest['status'] != 'complete':
        raise ValueError('complete ladder outcomes require a complete run')
    result.update(plan_sha256=config['calibration']['ladder_plan_sha256'], identity_hash=manifest['identity_hash'],
                  responses_sha256=hashlib.sha256(observed_path.read_bytes()).hexdigest() if observed_path.exists() else None)
    write_json(output, result)
    return result
