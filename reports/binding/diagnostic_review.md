# Review of consumed diagnostic results

Exact within-cohort counts only. No population intervals, significance tests, mechanism selection or changes to the completed gate. Protocol comparisons jointly change readout and generation budget. Copy and overwrite families are not matched numerical twins.

This analysis uses completed training and numeric-validation outcomes. It is exploratory and does not reopen the fixed gate or final model outcomes.

## Distractor-design audit

| Absolute oracle answer | Without trailing distractor | With trailing distractor |
|---:|---:|---:|
| 0 | 64 | 64 |
| 1 | 64 | 0 |
| 2 | 0 | 64 |
| 3 | 64 | 0 |
| 4 | 0 | 64 |

The original generator tied trailing distractors to replicate parity. For nonzero answers, parity also determined target magnitude. The completed accuracies and selection decisions remain valid descriptions of their stated mixtures; differences between distractor strata cannot isolate an irrelevant-statement effect.

## Paired readouts on identical programs

| Task | Split | Family | Depth | n | Both correct | Direct only correct | Trace only correct | Neither correct |
|---|---|---|---:|---:|---:|---:|---:|---:|
| arithmetic_forms | development | assignment | — | 24 | 0 | 0 | 10 | 14 |
| arithmetic_forms | development | dependent | — | 24 | 1 | 0 | 10 | 13 |
| arithmetic_forms | development | expression | — | 24 | 0 | 0 | 8 | 16 |
| arithmetic_forms | development | independent | — | 24 | 7 | 5 | 9 | 3 |
| arithmetic_forms | train | assignment | — | 24 | 0 | 2 | 8 | 14 |
| arithmetic_forms | train | dependent | — | 24 | 1 | 2 | 11 | 10 |
| arithmetic_forms | train | expression | — | 24 | 1 | 2 | 12 | 9 |
| arithmetic_forms | train | independent | — | 24 | 6 | 4 | 10 | 4 |
| arithmetic_free | development | copy_depth | 1 | 24 | 16 | 2 | 6 | 0 |
| arithmetic_free | development | copy_depth | 2 | 24 | 14 | 0 | 10 | 0 |
| arithmetic_free | development | copy_depth | 4 | 24 | 3 | 2 | 15 | 4 |
| arithmetic_free | development | copy_depth | 8 | 24 | 5 | 3 | 12 | 4 |
| arithmetic_free | development | overwrite_count | 1 | 24 | 4 | 5 | 14 | 1 |
| arithmetic_free | development | overwrite_count | 2 | 24 | 8 | 3 | 10 | 3 |
| arithmetic_free | development | overwrite_count | 4 | 24 | 8 | 2 | 9 | 5 |
| arithmetic_free | development | overwrite_count | 8 | 24 | 3 | 4 | 8 | 9 |
| arithmetic_free | train | copy_depth | 1 | 24 | 20 | 3 | 1 | 0 |
| arithmetic_free | train | copy_depth | 2 | 24 | 11 | 3 | 10 | 0 |
| arithmetic_free | train | copy_depth | 4 | 24 | 7 | 3 | 10 | 4 |
| arithmetic_free | train | copy_depth | 8 | 24 | 5 | 1 | 10 | 8 |
| arithmetic_free | train | overwrite_count | 1 | 24 | 10 | 2 | 11 | 1 |
| arithmetic_free | train | overwrite_count | 2 | 24 | 7 | 2 | 10 | 5 |
| arithmetic_free | train | overwrite_count | 4 | 24 | 7 | 4 | 7 | 6 |
| arithmetic_free | train | overwrite_count | 8 | 24 | 1 | 5 | 10 | 8 |

## Matched arithmetic-form comparisons

Each row compares exactly the same numeric groups and expected answers. The independent form substitutes an executed intermediate as a literal, so the comparison changes literal cues and functional dependencies. These are descriptive contrasts, not a pure binding intervention.

| Protocol | Split | Left form | Right form | n | Left only correct | Right only correct |
|---|---|---|---|---:|---:|---:|
| print_direct_v3 | train | expression | assignment | 24 | 1 | 0 |
| print_direct_v3 | train | expression | independent | 24 | 0 | 7 |
| print_direct_v3 | train | expression | dependent | 24 | 1 | 1 |
| print_direct_v3 | train | assignment | independent | 24 | 0 | 8 |
| print_direct_v3 | train | assignment | dependent | 24 | 0 | 1 |
| print_direct_v3 | train | independent | dependent | 24 | 7 | 0 |
| print_direct_v3 | development | expression | assignment | 24 | 0 | 0 |
| print_direct_v3 | development | expression | independent | 24 | 0 | 12 |
| print_direct_v3 | development | expression | dependent | 24 | 0 | 1 |
| print_direct_v3 | development | assignment | independent | 24 | 0 | 12 |
| print_direct_v3 | development | assignment | dependent | 24 | 0 | 1 |
| print_direct_v3 | development | independent | dependent | 24 | 11 | 0 |
| print_trace_long_v1 | train | expression | assignment | 24 | 6 | 1 |
| print_trace_long_v1 | train | expression | independent | 24 | 1 | 4 |
| print_trace_long_v1 | train | expression | dependent | 24 | 5 | 4 |
| print_trace_long_v1 | train | assignment | independent | 24 | 1 | 9 |
| print_trace_long_v1 | train | assignment | dependent | 24 | 2 | 6 |
| print_trace_long_v1 | train | independent | dependent | 24 | 6 | 2 |
| print_trace_long_v1 | development | expression | assignment | 24 | 5 | 7 |
| print_trace_long_v1 | development | expression | independent | 24 | 2 | 10 |
| print_trace_long_v1 | development | expression | dependent | 24 | 3 | 6 |
| print_trace_long_v1 | development | assignment | independent | 24 | 5 | 11 |
| print_trace_long_v1 | development | assignment | dependent | 24 | 3 | 4 |
| print_trace_long_v1 | development | independent | dependent | 24 | 10 | 5 |

Full case IDs, invalid counts and binding strata are retained in the review artifact. Oracle answer magnitude is used only for this design audit and is not an eligible forecast feature. A fresh counterbalanced dataset is prepared separately without model inference.
