# Can formatting repair explain the failed old-value gates?

Even if every invalid saved answer became correct, **16 of 24 CodeLlama cells** and **all 24 Llama cells** would remain below the fixed 90% accuracy threshold. Every historical-question cell across both checkpoints remains below threshold. Wrong valid integers therefore require attention alongside formatting.

This is a deliberately optimistic bound on format-only repair of saved outputs. It leaves already-valid integers unchanged and gives full correctness credit to every invalid response without parsing it. It does not change any original score, parser or gate.

| Model | Instruction | Question | Correct / primary n | Invalid | Valid wrong | Optimistic accuracy | Fixed cells still below 90% |
|---|---|---|---:|---:|---:|---:|---:|
| codellama34b | old_value_execute_v1 | current | 318 / 2,424 | 1,965 | 141 | 94.18% | 0 / 4 |
| codellama34b | old_value_execute_v1 | previous | 411 / 2,424 | 1,376 | 637 | 73.72% | 4 / 4 |
| codellama34b | old_value_history_v1 | current | 878 / 2,424 | 728 | 818 | 66.25% | 4 / 4 |
| codellama34b | old_value_history_v1 | previous | 751 / 2,424 | 7 | 1,666 | 31.27% | 4 / 4 |
| codellama34b | old_value_output_v1 | current | 334 / 2,424 | 1,950 | 140 | 94.22% | 0 / 4 |
| codellama34b | old_value_output_v1 | previous | 554 / 2,424 | 950 | 920 | 62.05% | 4 / 4 |
| llama8b | old_value_execute_v1 | current | 2,069 / 2,424 | 0 | 355 | 85.35% | 4 / 4 |
| llama8b | old_value_execute_v1 | previous | 884 / 2,424 | 0 | 1,540 | 36.47% | 4 / 4 |
| llama8b | old_value_history_v1 | current | 1,829 / 2,424 | 0 | 595 | 75.45% | 4 / 4 |
| llama8b | old_value_history_v1 | previous | 1,039 / 2,424 | 0 | 1,385 | 42.86% | 4 / 4 |
| llama8b | old_value_output_v1 | current | 2,005 / 2,424 | 0 | 419 | 82.71% | 4 / 4 |
| llama8b | old_value_output_v1 | previous | 936 / 2,424 | 0 | 1,488 | 38.61% | 4 / 4 |

Each row contains four fixed cells: TRAIN/DEV × absent/retained old numeric value. The aggregate percentage cannot replace those individual gates. The complete 48-cell table is retained in the machine review.

The bound uses exact integer arithmetic: minimum correct = ceil(9n/10); optimistic correct = original correct + original invalid. A cell is blocked when its known valid wrong answers alone exceed 10% of n. The published counts, original gate statuses and all source groupings are preserved.

For the morning review:

- Keep the completed study and its failed gates intact.
- Treat format compliance and numeric selection as separate prospective calibration questions. CodeLlama formatting work alone cannot qualify this saved cohort.
- Any changed wording, generation contract or candidate-answer measurement needs its own pinned discovery protocol and fresh registered sources. Such changes may alter valid wrong answers and are not bounded by this saved-output calculation.
- Select the next discovery design after reviewing all instructions and cells. No model rerun, causal intervention, optional training or sealed evaluation is queued by this review.

No new model queries, fits, raw-response parsing, tokenizer/model loads or array reads were required. These are deterministic descriptive bounds, not uncertainty intervals or capability limits.

[Original findings](old_value_overnight_findings_v1.md) · [Response diagnostics](old_value_postrun_response_diagnostics_v1.md) · [Operational follow-up](old_value_overnight_followup_v1.md)
