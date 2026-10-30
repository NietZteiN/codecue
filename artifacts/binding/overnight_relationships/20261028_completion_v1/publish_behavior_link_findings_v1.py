"""Publish concise interpretation from the immutable score/answer result."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from codecue.binding import relationship_capture as base

folder = ROOT / 'artifacts/binding/overnight_relationships/20261028_score_behavior_v1'
receipt_path = folder / 'completion_manifest_v1.json'
receipt = json.loads(receipt_path.read_text())
entry = receipt['artifacts']['results']
payload = (ROOT / entry['path']).read_bytes()
assert hashlib.sha256(payload).hexdigest() == entry['sha256']
result = json.loads(payload)
assert result['status'] == 'complete_exploratory' and result['development_cases'] == 4860
assert result['new_model_queries'] == result['new_fits'] == result['parameter_replays'] == 0

def pct(metric):
    return f"{100 * metric['point']:.3f}%"

def interval(metric):
    low, high = metric['conditional_group_bootstrap_95']
    return f"[{100 * low:.3f}, {100 * high:.3f}]"

lines = ['# Score/answer follow-up findings', '',
    'The exact-ID DEV join shows that a correctly decoded dependency graph frequently coexists with a wrong generated answer. Queried-value decoding is much weaker, so this does not establish a complete correct binding state that the model fails to use.', '',
    'This is a posthoc analysis selected after inspecting the overnight results. It validates all14,580 original responses and uses4,860 DEV rows,72 fixed saved-score banks and zero new model calls, fits or parameter predictions. Initial-binding values at site3 remain distinct from final-binding values at sites7/8.', '',
    '## Computed programs: the same486DEV cases per checkpoint', '',
    'Values below use the nominated hidden layer at the last-assignment checkpoint. Joint probabilities average binary events within each of the three saved fits before computing component summaries.', '',
    '| Model | Answer correct | Whole graph correct | Queried final value correct | Graph correct and answer wrong | Conditional95% for joint probability |',
    '|---|---:|---:|---:|---:|---|']
labels = {'llama8b': 'Llama3.1 8B', 'codellama34b': 'CodeLlama34B'}
for key, label in labels.items():
    cell = result['models'][key]['panels']['computed']['cells']['hidden/site7']['overall']
    graph = cell['events']['graph']
    joint = graph['decoding_correct_and_answer_wrong']
    lines.append(f"| {label} | {pct(cell['answer_accuracy'])} | {pct(graph['decoding_correct'])} | {pct(cell['events']['queried_value']['decoding_correct'])} | {pct(joint)} | {interval(joint)} |")
lines += ['', 'The graph decoder receives the fixed node/version scaffold. Its correctness concerns the dependency pattern, not all numeric bindings or the model’s naturally used pathway. These rows are a subset of the full computed readout panel; the graph points therefore differ from that panel’s aggregate values.', '',
    '## Matched body and fixed target slot', '',
    'For literal query twins, change only the actual query while scoring the same target head on the same program body. Report the final-prompt effect minus the pre-query site7 placebo, averaged over all four target slots.', '',
    '| Model | Site7 placebo | Site8 minus site7 | Conditional95%, percentage points |',
    '|---|---:|---:|---|']
for key, label in labels.items():
    query = result['models'][key]['panels']['literal']['query_diagnostics']['hidden']
    before = query['sites']['7']['mean_slot_effect']
    effect = query['site8_minus_site7']['mean_slot_effect']
    lines.append(f"| {label} | {100 * before['point']:+.3f}pp | {100 * effect['point']:+.3f}pp | {interval(effect)} |")
lines += ['', 'Both mean-effect intervals include zero. This is not a claim of no query effect at every slot, layer or decoder. Full4×4 matrices, all source controls and individual-slot contrasts remain in the pinned machine result. A slot-difficulty difference before the query is visible cannot establish query modulation; other slots may also be output ancestors.', '',
    'Intervals resample the same nine structural components2,000times, seed117, conditional on the saved fits, with no refitting or multiplicity adjustment. Conditional cells require at least1,900 valid draws; empty or sparse cells remain explicitly unavailable where appropriate. Numeric seeds, weighting seeds, lexical twins and queries are not independent topology replications.', '',
    'The [complete score/answer report](overnight_score_behavior_v1.md), [declared posthoc plan](overnight_score_behavior_plan_v1.md) and [overnight findings](overnight_20261027_findings_v1.md) retain the surrounding comparisons. The [next-experiment decision](relationship_next_experiment_decision_v1.md) keeps root computation, query accessibility and natural causal use as separate open questions.', '']
report = ROOT / 'reports/binding/overnight_score_behavior_findings_v1.md'
base._publish(report, '\n'.join(lines).encode())
out = ROOT / 'artifacts/binding/overnight_relationships/20261028_completion_v1/behavior_link_findings_review_v1.json'
base._put(out, dict(status='passed', evaluation_role='posthoc_relationship_behavior_findings_publication_v1',
    inputs=[dict(path=str(receipt_path.relative_to(ROOT)), sha256=base._sha(receipt_path)), entry],
    report=dict(path=str(report.relative_to(ROOT)), sha256=base._sha(report)),
    publication_script_sha256=base._sha(__file__), new_model_queries=0, new_fits=0,
    generated_holdouts_opened=False))
print(report)
