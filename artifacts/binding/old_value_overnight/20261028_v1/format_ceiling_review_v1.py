"""Bound format-only repair from immutable saved outcome counts; no rescoring."""
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
SUITE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from codecue.binding.relationship_capture import _put, _publish


def pin(path):
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    comparison_path = SUITE / 'comparison_v1.json'
    completion_path = SUITE / 'completion_review_v1.json'
    before = [pin(comparison_path), pin(completion_path)]
    completion = json.loads(completion_path.read_text())
    assert completion['status'] == 'complete_audited'
    assert before[0] in completion['output_pins']
    comparison = json.loads(comparison_path.read_text())
    assert comparison['total_scored_responses'] == 40320
    cells, groups = [], defaultdict(list)
    original_gates = {}
    for model, value in sorted(comparison['models'].items()):
        review = value['review']
        gate = review['reliability_gate']
        original_gates[model] = gate['status']
        threshold = Fraction(str(gate['thresholds']['minimum_accuracy']))
        assert threshold == Fraction(9, 10)
        assert len(review['gate_cells']) == 24
        identities = set()
        for cell in review['gate_cells']:
            identity = tuple(cell[k] for k in ('variant', 'query_mode', 'old_storage', 'split'))
            assert identity not in identities
            identities.add(identity)
            assert cell['old_storage'] in ('absent_all_current', 'retained_other_current')
            n, correct, invalid = (cell[k] for k in ('n', 'correct', 'invalid'))
            assert all(type(x) is int and x >= 0 for x in (n, correct, invalid))
            assert n > 0 and correct + invalid <= n
            required = (threshold.numerator * n + threshold.denominator - 1) // threshold.denominator
            valid_wrong = n - correct - invalid
            row = dict(model=model, **dict(zip(('variant', 'query_mode', 'old_storage', 'split'), identity)),
                       n=n, original_correct=correct, original_invalid=invalid,
                       original_gate_passed=cell['passed'], valid_wrong=valid_wrong,
                       required_correct=required, optimistic_correct=correct + invalid,
                       optimistic_accuracy=(correct + invalid) / n,
                       impossible_with_format_only_repair=correct + invalid < required)
            assert row['impossible_with_format_only_repair'] == (Fraction(valid_wrong, n) > 1 - threshold)
            cells.append(row)
            groups[model, cell['variant'], cell['query_mode']].append(row)
    summaries = []
    for (model, variant, mode), rows in sorted(groups.items()):
        assert len(rows) == 4
        n = sum(row['n'] for row in rows)
        correct = sum(row['original_correct'] for row in rows)
        invalid = sum(row['original_invalid'] for row in rows)
        summaries.append(dict(model=model, variant=variant, query_mode=mode,
            n=n, original_correct=correct, original_invalid=invalid,
            valid_wrong=n-correct-invalid, optimistic_accuracy=(correct+invalid)/n,
            blocked_cells=sum(row['impossible_with_format_only_repair'] for row in rows), cells=4))
    assert len(cells) == 48 and len(summaries) == 12
    assert sum(row['n'] for row in cells) == 29088
    limitations = [
        'This optimistic bound makes every saved invalid response correct while preserving all already-valid integers.',
        'It is not a relaxed parser, measured corrected accuracy, confidence interval, new experiment or changed gate.',
        'A new prompt or generation protocol can also change valid wrong integers, so this is not a ceiling on model capability.',
        'Equality controls remain excluded exactly as in the original primary gate; all instructions, splits and distinct-value storage strata remain.',
        'Numeric, lexical and rotation relatives remain dependent discovery views. No causal mechanism follows from these counts.'
    ]
    result = dict(evaluation_role='discovery_old_value_format_ceiling_v1', status='complete_audited',
        new_model_queries=0, new_fits=0, response_records_opened=False, arrays_opened=False,
        original_gate_status=original_gates, scores_or_gates_changed=False,
        threshold=dict(numerator=9, denominator=10), cells=cells, summaries=summaries,
        per_model={model: dict(cells=sum(row['model']==model for row in cells),
            blocked_cells=sum(row['model']==model and row['impossible_with_format_only_repair'] for row in cells))
            for model in sorted(original_gates)},
        input_pins=before, limitations=limitations)
    code = result['per_model']['codellama34b']
    llama = result['per_model']['llama8b']
    historical = [row for row in cells if row['query_mode'] == 'previous']
    assert all(row['impossible_with_format_only_repair'] for row in historical)
    assert llama['blocked_cells'] == llama['cells']
    lines = ['# Can formatting repair explain the failed old-value gates?', '',
        f"Even if every invalid saved answer became correct, **{code['blocked_cells']} of {code['cells']} CodeLlama cells** and **all {llama['cells']} Llama cells** would remain below the fixed 90% accuracy threshold. Every historical-question cell across both checkpoints remains below threshold. Wrong valid integers therefore require attention alongside formatting.", '',
        'This is a deliberately optimistic bound on format-only repair of saved outputs. It leaves already-valid integers unchanged and gives full correctness credit to every invalid response without parsing it. It does not change any original score, parser or gate.', '',
        '| Model | Instruction | Question | Correct / primary n | Invalid | Valid wrong | Optimistic accuracy | Fixed cells still below 90% |',
        '|---|---|---|---:|---:|---:|---:|---:|']
    for row in summaries:
        lines.append(f"| {row['model']} | {row['variant']} | {row['query_mode']} | {row['original_correct']:,} / {row['n']:,} | {row['original_invalid']:,} | {row['valid_wrong']:,} | {row['optimistic_accuracy']:.2%} | {row['blocked_cells']} / 4 |")
    lines += ['', 'Each row contains four fixed cells: TRAIN/DEV × absent/retained old numeric value. The aggregate percentage cannot replace those individual gates. The complete 48-cell table is retained in the machine review.', '',
        'The bound uses exact integer arithmetic: minimum correct = ceil(9n/10); optimistic correct = original correct + original invalid. A cell is blocked when its known valid wrong answers alone exceed 10% of n. The published counts, original gate statuses and all source groupings are preserved.', '',
        'For the morning review:', '',
        '- Keep the completed study and its failed gates intact.',
        '- Treat format compliance and numeric selection as separate prospective calibration questions. CodeLlama formatting work alone cannot qualify this saved cohort.',
        '- Any changed wording, generation contract or candidate-answer measurement needs its own pinned discovery protocol and fresh registered sources. Such changes may alter valid wrong answers and are not bounded by this saved-output calculation.',
        '- Select the next discovery design after reviewing all instructions and cells. No model rerun, causal intervention, optional training or sealed evaluation is queued by this review.', '',
        'No new model queries, fits, raw-response parsing, tokenizer/model loads or array reads were required. These are deterministic descriptive bounds, not uncertainty intervals or capability limits.', '',
        '[Original findings](old_value_overnight_findings_v1.md) · [Response diagnostics](old_value_postrun_response_diagnostics_v1.md) · [Operational follow-up](old_value_overnight_followup_v1.md)', '']
    assert [pin(comparison_path), pin(completion_path)] == before
    _publish(ROOT / 'reports/binding/old_value_format_ceiling_v1.md', '\n'.join(lines).encode())
    _put(SUITE / 'format_ceiling_review_v1.json', result)
    print(json.dumps(dict(status=result['status'], per_model=result['per_model'], new_model_queries=0), sort_keys=True))


if __name__ == '__main__':
    main()
