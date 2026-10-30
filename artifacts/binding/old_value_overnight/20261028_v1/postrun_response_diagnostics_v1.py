"""Independent saved-response diagnostics; never changes scores or makes model calls."""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
from itertools import zip_longest
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
SUITE = Path('artifacts/binding/old_value_overnight/20261028_v1')
SNAPSHOT = Path('artifacts/binding/sources/4206d21342e20115539c3b55')
VARIANTS = ('old_value_output_v1', 'old_value_execute_v1', 'old_value_history_v1')
INSTRUCTIONS = {
    VARIANTS[0]: 'Read the assignments in order and answer the question. Give only the signed integer value, without explanation.',
    VARIANTS[1]: 'Follow the Python 3 assignments in order. Answer the question with only the signed integer value.',
    VARIANTS[2]: 'Use the complete assignment history to answer the question. Return a signed integer only, without explanation.',
}
INTEGER = re.compile(r'\s*[+-]?\d+\s*', flags=re.ASCII)
ASSIGNMENT = re.compile(r'\s*([A-Za-z_]\w*)\s*=\s*([+-]?\d+)\s*', flags=re.ASCII)
FENCED = re.compile(r'\s*```(?:python)?\s*([+-]?\d+)\s*```\s*', flags=re.ASCII)
PINS = {}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def pin(relative):
    path = ROOT / relative
    require(path.is_file() and not path.is_symlink(), f'Regular input required: {relative}')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''):
            h.update(block)
    item = dict(path=str(relative), bytes=path.stat().st_size, sha256=h.hexdigest())
    require(PINS.setdefault(str(relative), item) == item, f'Input changed: {relative}')
    return item


def metadata(relative):
    pin(relative)
    path = ROOT / relative
    require(path.stat().st_size <= 8 * 1024**2, 'Bounded metadata required')
    return json.loads(path.read_text())


def rows(relative):
    pin(relative)
    with (ROOT / relative).open() as stream:
        for line in stream:
            require(line.endswith('\n') and line.strip(), 'Complete nonempty JSONL lines required')
            yield json.loads(line)


def strict_score(raw, expected):
    prediction = int(raw.strip()) if isinstance(raw, str) and len(raw) <= 128 and INTEGER.fullmatch(raw) else None
    return dict(prediction=prediction, valid=prediction is not None, correct=prediction == expected)


def integer_expr(expr, values):
    if isinstance(expr, ast.Constant) and type(expr.value) is int:
        return expr.value
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, (ast.UAdd, ast.USub)):
        require(isinstance(expr.operand, ast.Constant) and type(expr.operand.value) is int, 'Literal sign required')
        return expr.operand.value * (-1 if isinstance(expr.op, ast.USub) else 1)
    require(isinstance(expr, ast.Name) and expr.id in values, 'Only initialized copies are permitted')
    return values[expr.id]


def independent_trace(body):
    values, last_before, writes = {}, {}, Counter()
    statements = ast.parse(body).body
    require(len(statements) == 8, 'Exactly eight assignments required')
    for statement in statements:
        require(isinstance(statement, ast.Assign) and len(statement.targets) == 1
                and isinstance(statement.targets[0], ast.Name), 'Simple assignment required')
        name = statement.targets[0].id
        if name in values:
            last_before[name] = values[name]
        values[name] = integer_expr(statement.value, values)
        writes[name] += 1
    return values, last_before, writes


def category(row, response, score):
    if score['valid']:
        if score['correct']:
            return 'valid_correct_integer'
        other = row['previous_value'] if row['query_mode'] == 'current' else row['current_value']
        if row['primary_distinct'] and score['prediction'] == other:
            return 'valid_wrong_other_question_integer'
        return 'valid_wrong_other_integer'
    raw = response['raw_response']
    if ASSIGNMENT.fullmatch(raw):
        return 'invalid_assignment_integer'
    if FENCED.fullmatch(raw):
        return 'invalid_fenced_integer'
    if not raw.strip():
        return 'invalid_empty'
    return 'invalid_other'


def aggregate(items):
    n = len(items)
    result = dict(n=n, correct=sum(x['score']['correct'] for x in items),
                  valid=sum(x['score']['valid'] for x in items),
                  categories=dict(sorted(Counter(x['category'] for x in items).items())),
                  finish_reason=dict(sorted(Counter(x['finish_reason'] for x in items).items())),
                  output_token_lengths=dict(sorted(Counter(str(x['output_tokens']) for x in items).items())),
                  eos_last_token=sum(x['eos_last_token'] for x in items),
                  length_limited=sum(x['finish_reason'] == 'length' for x in items),
                  length_limited_invalid=sum(x['finish_reason'] == 'length' and not x['score']['valid'] for x in items),
                  stop_invalid=sum(x['finish_reason'] == 'stop' and not x['score']['valid'] for x in items),
                  unique_native_prompt_ids=len({x['input_ids_sha256'] for x in items}))
    result['invalid'] = n - result['valid']
    result['accuracy'] = result['correct'] / n
    result['invalid_rate'] = result['invalid'] / n
    require(sum(result['categories'].values()) == n, 'Categories must partition every response')
    primary = [x for x in items if x['old_storage'] != 'equal_current']
    result['different_value_subset'] = dict(
        n=len(primary), correct=sum(x['score']['correct'] for x in primary),
        invalid=sum(not x['score']['valid'] for x in primary),
        valid_wrong_other_question=sum(x['category'] == 'valid_wrong_other_question_integer' for x in primary),
        valid_wrong_other=sum(x['category'] == 'valid_wrong_other_integer' for x in primary))
    require(sum(result['different_value_subset'][key] for key in ('correct', 'invalid', 'valid_wrong_other_question', 'valid_wrong_other')) == len(primary), 'Primary outcome partition differs')
    return result


def grouped(items, fields):
    groups = defaultdict(list)
    for item in items:
        groups[tuple(item[field] for field in fields)].append(item)
    return [dict(zip(fields, key), **aggregate(values)) for key, values in sorted(groups.items())]


def diagnose(model, source):
    config_path = Path(f'configs/binding/old_value_overnight_20261028_v1/{model}.json')
    config = metadata(config_path)
    preflight = metadata(SUITE / model / 'tokenizer_preflight.json')
    review = metadata(SUITE / model / 'review_v1.json')
    pin(SUITE / model / 'checkpoint_suite/manifest.json')
    pin(SUITE / model / 'checkpoint_suite/audit.json')
    pin(SUITE / model / 'checkpoint_suite/runtime.json')
    prepared_path = SUITE / model / 'prepared_cases.jsonl'
    response_path = SUITE / model / 'checkpoint_suite/responses.jsonl'
    require(pin(prepared_path)['sha256'] == preflight['prepared_cases_sha256'], 'Prepared file differs from native preflight')
    require(pin(response_path)['sha256'] == review['artifacts']['responses']['sha256'], 'Response file differs from published review')
    require(preflight['status'] == 'passed' and preflight['config_hash'] == digest(config), 'Native preflight/config differs')
    seen, items, examples, traces = set(), [], defaultdict(list), {}
    for case, response in zip_longest(rows(prepared_path), rows(response_path)):
        require(case is not None and response is not None, 'Prepared/response lengths differ')
        key = (case['task'], case['id'])
        require(key not in seen and key[0] in VARIANTS, 'Duplicate or unknown response key')
        seen.add(key)
        row = source[case['id']]
        require(case['record'] == row, 'Prepared source record differs from pinned dataset')
        require(all(case[field] == response[field] for field in ('section', 'task', 'id', 'input_token_ids', 'prompt_sha256')), 'Saved native request identity differs')
        require(digest(row) == response['record_sha256'], 'Record identity differs')
        require(digest(case['prompt']) == response['prompt_sha256'], 'Prompt text identity differs')
        require(case['stop'] == ['\n\n'] and case['max_new_tokens'] == 16, 'Frozen stop/token cap differs')
        require(len(response['output_token_ids']) <= 16 and len(response['input_token_ids']) + 16 <= config['context_limit'], 'Token ceiling/context overflow')
        trace = traces.setdefault(row['body'], independent_trace(row['body']))
        current, previous, writes = trace
        target = row['target_name']
        require(writes[target] >= 2 and row['current_value'] == current[target]
                and row['previous_value'] == previous[target], 'Independent historical/current AST truth differs')
        expected = current[target] if row['query_mode'] == 'current' else previous[target]
        require(row['expected_answer'] == expected, 'Question-mode oracle differs')
        question = (f'What is {target} after all assignments?' if row['query_mode'] == 'current'
                    else f'What was {target} immediately before its LAST assignment?')
        require(row['question'] == question and question in case['prompt'] and row['body'] in case['prompt'], 'Question/full body missing from actual prompt')
        if model == 'codellama34b':
            expected_prompt = '<s> [INST] ' + INSTRUCTIONS[case['task']] + '\n\n```python\n' + row['body'] + '\n```\n\n' + question + ' [/INST] Output:\n'
            require(case['prompt'] == expected_prompt, 'CodeLlama rendered complete prompt differs from reviewed wrapper')
            require(response['input_token_ids'][:4] == [1, 518, 25580, 29962], 'CodeLlama native BOS/INST boundary differs')
            require(response['input_token_ids'][-7:] == [518, 29914, 25580, 29962, 10604, 29901, 13], 'CodeLlama native assistant prefill differs')
        score = strict_score(response['raw_response'], expected)
        require(score == response['score'], 'Independent strict score differs from saved score')
        item = dict(variant=case['task'], query_mode=row['query_mode'], split=row['split'],
                    old_storage=row['old_storage'], score=score,
                    category=category(row, response, score), finish_reason=response['finish_reason'],
                    output_tokens=len(response['output_token_ids']),
                    eos_last_token=bool(response['output_token_ids'] and response['output_token_ids'][-1] in config['eos_token_ids']),
                    input_ids_sha256=digest(response['input_token_ids']))
        items.append(item)
        if item['category'] not in ('valid_correct_integer', 'valid_wrong_other_integer') and len(examples[item['category']]) < 2:
            examples[item['category']].append(dict(id=row['id'], variant=case['task'], query_mode=row['query_mode'],
                expected=expected, previous=row['previous_value'], current=row['current_value'],
                raw_response=response['raw_response'], finish_reason=response['finish_reason'],
                output_token_ids=response['output_token_ids']))
    require(len(items) == 20160 and len(seen) == 20160 and len(traces) == 1440, 'Full declared cohort required')
    result = aggregate(items)
    for field in ('n', 'correct', 'valid', 'invalid', 'accuracy', 'invalid_rate'):
        require(result[field] == review[field], f'Published total differs: {field}')
    result['by_instruction_query_mode'] = grouped(items, ('variant', 'query_mode'))
    result['by_instruction_query_mode_split'] = grouped(items, ('variant', 'query_mode', 'split'))
    result['by_instruction_query_mode_split_storage'] = grouped(items, ('variant', 'query_mode', 'split', 'old_storage'))
    result['by_query_mode_storage'] = grouped(items, ('query_mode', 'old_storage'))
    result['by_query_mode'] = grouped(items, ('query_mode',))
    lookup = {(x['variant'], x['query_mode'], x['split'], x['old_storage']): x for x in result['by_instruction_query_mode_split_storage']}
    gate_passed = 0
    for cell in review['gate_cells']:
        found = lookup[tuple(cell[key] for key in ('variant', 'query_mode', 'split', 'old_storage'))]
        for field in ('n', 'correct', 'invalid', 'accuracy', 'invalid_rate'):
            require(found[field] == cell[field], f'Published primary cell differs: {field}')
        passed = found['n'] >= 24 and found['unique_native_prompt_ids'] >= 24 and found['accuracy'] >= .9 and found['invalid_rate'] <= .05
        require(passed == cell['passed'], 'Independent fixed gate result differs')
        gate_passed += passed
    require(len(review['gate_cells']) == 24, 'All fixed primary gate cells required')
    result.update(examples=dict(sorted(examples.items())), independently_reconciled_primary_cells=24,
        primary_gate_cells_passed=gate_passed, independent_body_traces=len(traces),
        strict_score_mismatches=0, oracle_mismatches=0, prepared_response_identity_mismatches=0,
        model=review['model'], model_revision=review['model_revision'],
        eos_token_ids=config['eos_token_ids'], max_new_tokens=16,
        tokenization_mode=config['tokenization_mode'], native_tokenizer_loaded_for_this_review=False)
    return result


def prior_boundary():
    prior_path = Path('configs/binding/computation_routing_20261028_v1/codellama34b.json')
    prior = metadata(prior_path)
    current = metadata(Path('configs/binding/old_value_overnight_20261028_v1/codellama34b.json'))
    old_receipt = metadata(Path('artifacts/binding/computation_routing/20261028_v1/codellama34b/routing_preflight_v1.json'))
    previous_snapshot = Path(old_receipt['source']['snapshot']).relative_to(ROOT)
    equal_keys = ['model', 'model_revision', 'tokenizer_revision', 'tokenization_mode', 'eos_token_ids',
                  'scorer', 'context_limit', 'runtime_manifest_sha256', 'engine', 'engine_memory_overrides']
    require(all(prior[key] == current[key] for key in equal_keys), 'Previously audited native settings changed')
    require(set(prior['max_new_tokens'].values()) == set(current['max_new_tokens'].values()) == {16}, 'Native token cap changed')
    source_equal = {}
    for filename in ('model_adapter.py', 'checkpoint_suite.py'):
        old = pin(previous_snapshot / 'src/codecue/binding' / filename)
        new = pin(SNAPSHOT / 'src/codecue/binding' / filename)
        source_equal[filename] = old['sha256'] == new['sha256']
    previous = next(rows(Path(prior['prepared_cases'])))
    require(previous['prompt'].startswith('<s> [INST] ') and previous['prompt'].endswith(' [/INST] Output:\n')
            and previous['input_token_ids'][:4] == [1, 518, 25580, 29962]
            and previous['input_token_ids'][-7:] == [518, 29914, 25580, 29962, 10604, 29901, 13]
            and previous['stop'] == ['\n\n'], 'Previous representative native boundary differs')
    return dict(previous_snapshot=str(previous_snapshot), matching_config_fields=equal_keys,
                same_16_token_cap=True, source_file_sha_equality=source_equal,
                previous_representative_prompt_prefix='<s> [INST] ',
                previous_representative_assistant_prefill=' [/INST] Output:\n',
                previous_representative_id=previous['id'], new_protocol=current['protocol'], prior_protocol=prior['protocol'],
                new_complete_prompts_checked=20160, new_native_ids_equal_saved_preparation=20160,
                fresh_native_retokenization_performed=False,
                interpretation='Same audited native boundary, generation backend source and assistant prefill as prior computation calibration; semantic question/instructions and source cohort differ. Saved native preflight verifies complete SentencePiece boundary; this review makes no tokenizer/model load.')


def render(review):
    models = review['models']
    lines = ['# Post-run old/current response diagnostics', '',
        'Independent discovery-only review of the saved outputs. Strict whole-response ASCII integer scores, all 48 primary cells across both models, saved native request identity and historical/current AST truth reconcile exactly with the immutable publication. This report changes no parser, score, gate, instruction or cohort.', '',
        '| Model | Responses | Correct | Accuracy | Invalid | Length-limited | Invalid EOS/stop |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for name, model in models.items():
        lines.append(f'| {name} | {model["n"]:,} | {model["correct"]:,} | {100*model["accuracy"]:.2f}% | {model["invalid"]:,} | {model["length_limited"]:,} | {model["stop_invalid"]:,} |')
    lines += ['', 'Both models fail all 24 fixed reliability cells. Failed behavior is preserved as a completed measurement.', '',
        '## CodeLlama formatting and stopping', '',
        '| Instruction | Question | Correct / n | Invalid | Assignment wrapper | Fenced integer | Other invalid | Length-limited |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for cell in models['codellama34b']['by_instruction_query_mode']:
        cats=cell['categories'];other=sum(v for k,v in cats.items() if k in ('invalid_empty','invalid_other'))
        lines.append(f'| {cell["variant"]} | {cell["query_mode"]} | {cell["correct"]:,}/{cell["n"]:,} | {cell["invalid"]:,} | {cats.get("invalid_assignment_integer",0):,} | {cats.get("invalid_fenced_integer",0):,} | {other:,} | {cell["length_limited"]:,} |')
    code=models['codellama34b'];cats=code['categories']
    lines += ['', f'CodeLlama emits {cats.get("invalid_assignment_integer",0):,} complete `name = integer` responses and {cats.get("invalid_fenced_integer",0):,} fenced integers. These violate the fixed integer-only response contract. {code["stop_invalid"]:,} invalid outputs stop before the token ceiling; {code["length_limited"]:,} total outputs reach the 16-token limit. Length truncation therefore cannot explain most invalid responses. The saved `finish_reason` distinguishes stop from length; it does not save the engine’s more specific stop reason. The EOS-last-token counts in the JSON provide direct token evidence without inventing a stop reason.', '',
        'The same model/tokenizer revisions, official BOS/INST boundary, EOS 2, assistant `Output:` prefill, strict scorer, 16-token ceiling and backend source were used in the prior computation calibration. All 20,160 current CodeLlama prompts have the reviewed wrapper and saved input IDs equal preparation. This pass finds no identity, oracle, context, scoring or boundary regression in those saved artifacts. It cannot independently reproduce inference or prove that alternative wording/token limits would help. No alternative parser is evaluated.', '',
        '## Llama current-value intrusion on historical questions', '',
        'These rows include only different old/current values. “Other question” means the exact current value on a previous-value question, or the exact previous value on a current-value question. Correct, other-question, other wrong and invalid categories partition each row.', '',
        '| Instruction | Question | Distinct-value n | Correct | Answered other question | Other wrong | Invalid |',
        '|---|---|---:|---:|---:|---:|---:|']
    for cell in models['llama8b']['by_instruction_query_mode']:
        d=cell['different_value_subset']
        lines.append(f'| {cell["variant"]} | {cell["query_mode"]} | {d["n"]:,} | {d["correct"]:,} | {d["valid_wrong_other_question"]:,} | {d["valid_wrong_other"]:,} | {d["invalid"]:,} |')
    lines += ['', 'Storage-separated totals retain the absent-from-all-current-slots versus retained-in-another-current-slot distinction:', '',
        '| Question | Old numeric value | n | Correct | Answered other question | Other wrong |',
        '|---|---|---:|---:|---:|---:|']
    for cell in models['llama8b']['by_query_mode_storage']:
        if cell['old_storage']=='equal_current':continue
        d=cell['different_value_subset']
        lines.append(f'| {cell["query_mode"]} | {cell["old_storage"]} | {d["n"]:,} | {d["correct"]:,} | {d["valid_wrong_other_question"]:,} | {d["valid_wrong_other"]:,} |')
    lines += ['', '## Limited saved examples', '', '| Model / category | Question | Previous / current / expected | Raw response (JSON escaped) | Finish |', '|---|---|---|---|---|']
    for name, model in models.items():
        for cat, examples in model['examples'].items():
            example=examples[0]
            raw=json.dumps(example['raw_response']).replace('|','\\|')
            lines.append(f'| {name}: {cat} | {example["query_mode"]} | {example["previous"]} / {example["current"]} / {example["expected"]} | `{raw}` | {example["finish_reason"]} |')
    lines += ['', '## Scope and next decisions', '',
        'Output format failures and wrong integer answers are observed model behavior under the fixed protocol. Input IDs, scores and task truth reconcile, so this evidence does not identify an implementation defect requiring a change to the completed study. The small set of length-limited continuations remains separately visible.', '',
        'Current-value intrusions show which numeric answer the model returned; they do not identify a neural mechanism. Full source history remains visible, old/current equality controls are separate, and dependent numeric/lexical/rotation views are not independent structural replications. These adaptive TRAIN/DEV observations cannot establish retained latent state, causal use, or held-out generalization. No confidence interval, best-instruction selection, intervention or automatic model rerun follows this diagnostic.', '',
        'Any longer-generation or formatting study would require a separately pinned discovery protocol retaining these failed gates. The independent morning check remains the next scheduled review.', '',
        'Reproduction: run the adjacent artifact helper with the pinned project Python. It streams saved JSONL, checks all input SHA pins again after analysis, and atomically verifies identical output bytes on a second execution. No tokenizer/model load, model query, fit or array file read is used.', '']
    return '\n'.join(lines)


def main():
    self_path=Path(__file__).resolve().relative_to(ROOT)
    pin(self_path)
    source_path=SUITE/'sources.jsonl'
    source={}
    for row in rows(source_path):
        require(row['id'] not in source, 'Source IDs must be unique')
        source[row['id']]=row
    require(len(source)==6720, 'Declared source row count differs')
    models={name:diagnose(name,source) for name in ('llama8b','codellama34b')}
    boundary=prior_boundary()
    pointer=metadata(SUITE/'execution_source_v1.json')
    pin(SNAPSHOT/'src/codecue/binding/old_value_programs.py')
    pin(SNAPSHOT/'src/codecue/binding/old_value_run.py')
    original_completion=pin(SUITE/'completion_review_v1.json')
    original_comparison=pin(SUITE/'comparison_v1.json')
    for entry in list(PINS.values()):
        require(pin(Path(entry['path']))==entry, 'Input pin changed during review')
    review=dict(status='passed_independent_saved_response_reconciliation',
        evaluation_role='discovery_old_value_postrun_response_diagnostics_v1',
        source=pointer, models=models, prior_codellama_boundary=boundary,
        total_saved_responses=40320, strict_scores_independently_checked=40320,
        primary_gate_cells_independently_checked=48, original_completion=original_completion,
        original_comparison=original_comparison, input_pins=sorted(PINS.values(),key=lambda x:x['path']),
        input_pins_reverified_after_analysis=True, new_model_queries=0,new_fits=0,
        model_or_tokenizer_loaded=False, arrays_opened=False, generated_holdouts_opened=False,
        scores_or_gates_changed=False, causal_qualification=False,
        categories_are_mutually_exclusive=True,
        category_precedence=['valid correct integer','valid wrong integer equal to the other question answer (only distinct-value pairs)',
            'other valid wrong integer','invalid complete ASCII name=integer assignment','invalid complete fenced integer',
            'empty invalid response','all other invalid responses'],
        stop_evidence='Saved finish_reason and output token IDs; no engine stop_reason field. EOS-last-token counts are direct token evidence; length limit is 16.',
        limitations=['Discovery TRAIN/DEV only; no sealed outcomes opened.',
            'Dependent numeric, lexical, rotation and instruction views remain descriptive.',
            'Visible full source history permits rereading; numeric intrusions do not reveal a neural mechanism.',
            'No fresh model inference or retokenization was performed; native IDs reconcile to passed preparation.',
            'Assignment/fence categories describe invalid syntax only; no permissive rescoring or rescued gate was computed.'])
    sys.path.insert(0,str(ROOT/SNAPSHOT/'src'))
    from codecue.binding.relationship_capture import _publish
    out_json=ROOT/SUITE/'postrun_response_diagnostics_v1.json'
    out_md=ROOT/'reports/binding/old_value_postrun_response_diagnostics_v1.md'
    _publish(out_json,(json.dumps(review,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
    _publish(out_md,render(review).encode())
    print(json.dumps(dict(status=review['status'],responses=review['total_saved_responses'],
        strict_score_mismatches=0,oracle_mismatches=0,primary_cells=48,
        models={name:{key:value[key] for key in ('n','correct','invalid','length_limited','categories')}
                for name,value in models.items()},json=str(out_json.relative_to(ROOT)),report=str(out_md.relative_to(ROOT))),sort_keys=True))


if __name__=='__main__':main()
