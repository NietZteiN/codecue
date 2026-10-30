# Cached-checkpoint feasibility and capacity comparisons

Complete published cohorts and discovery/calibration programs. No generated final outcomes were opened. The original seven-billion-parameter checkpoint gates and scores are unchanged. CRUXEval uses literal-only equality without code execution; these are not official execution pass@k scores.

| Checkpoint | Section | Protocol/task | Correct / n | Parseable |
|---|---|---|---:|---:|
| codellama13b | cruxeval | cruxeval_o_direct | 340/800 | 786 |
| codellama13b | cruxeval | cruxeval_o_cot | 335/800 | 748 |
| codellama13b | bbh | bbh_tracking_3 | 86/250 | 248 |
| codellama13b | bbh | bbh_tracking_5 | 71/250 | 250 |
| codellama13b | bbh | bbh_tracking_7 | 52/250 | 241 |
| codellama13b | arithmetic_forms | print_direct_v3 | 34/192 | 191 |
| codellama13b | arithmetic_forms | print_trace_long_v1 | 115/192 | 179 |
| codellama13b | arithmetic_free | print_direct_v3 | 171/384 | 384 |
| codellama13b | arithmetic_free | print_trace_long_v1 | 313/384 | 324 |
| codellama13b | counterbalanced | print_direct_v3 | 339/768 | 768 |
| codellama13b | counterbalanced | print_trace_long_v1 | 622/768 | 637 |
| codellama34b | cruxeval | cruxeval_o_direct | 333/800 | 792 |
| codellama34b | cruxeval | cruxeval_o_cot | 385/800 | 778 |
| codellama34b | bbh | bbh_tracking_3 | 142/250 | 248 |
| codellama34b | bbh | bbh_tracking_5 | 119/250 | 243 |
| codellama34b | bbh | bbh_tracking_7 | 77/250 | 185 |
| codellama34b | arithmetic_forms | print_direct_v3 | 57/192 | 192 |
| codellama34b | arithmetic_forms | print_trace_long_v1 | 148/192 | 192 |
| codellama34b | arithmetic_free | print_direct_v3 | 267/384 | 383 |
| codellama34b | arithmetic_free | print_trace_long_v1 | 341/384 | 384 |
| codellama34b | counterbalanced | print_direct_v3 | 559/768 | 768 |
| codellama34b | counterbalanced | print_trace_long_v1 | 678/768 | 768 |
| llama31_8b | cruxeval | cruxeval_o_direct | 21/800 | 28 |
| llama31_8b | cruxeval | cruxeval_o_cot | 48/800 | 89 |
| llama31_8b | bbh | bbh_tracking_3 | 211/250 | 247 |
| llama31_8b | bbh | bbh_tracking_5 | 214/250 | 244 |
| llama31_8b | bbh | bbh_tracking_7 | 219/250 | 248 |
| llama31_8b | arithmetic_forms | print_direct_v3 | 163/192 | 191 |
| llama31_8b | arithmetic_forms | print_trace_long_v1 | 176/192 | 192 |
| llama31_8b | arithmetic_free | print_direct_v3 | 358/384 | 384 |
| llama31_8b | arithmetic_free | print_trace_long_v1 | 356/384 | 356 |
| llama31_8b | counterbalanced | print_direct_v3 | 695/768 | 768 |
| llama31_8b | counterbalanced | print_trace_long_v1 | 719/768 | 720 |
| llama32_3b | cruxeval | cruxeval_o_direct | 0/800 | 0 |
| llama32_3b | cruxeval | cruxeval_o_cot | 18/800 | 30 |
| llama32_3b | bbh | bbh_tracking_3 | 204/250 | 250 |
| llama32_3b | bbh | bbh_tracking_5 | 150/250 | 250 |
| llama32_3b | bbh | bbh_tracking_7 | 142/250 | 250 |
| llama32_3b | arithmetic_forms | print_direct_v3 | 109/192 | 192 |
| llama32_3b | arithmetic_forms | print_trace_long_v1 | 170/192 | 192 |
| llama32_3b | arithmetic_free | print_direct_v3 | 262/384 | 384 |
| llama32_3b | arithmetic_free | print_trace_long_v1 | 357/384 | 381 |
| llama32_3b | counterbalanced | print_direct_v3 | 534/768 | 768 |
| llama32_3b | counterbalanced | print_trace_long_v1 | 703/768 | 759 |

CodeLlama CRUXEval runs use the audited released completion boundary. The Llama instruction checkpoints use their native chat templates around identical released content; that comparison changes both checkpoint and serialization. BBH and generated calibration use native chat templates. Precision, exact revisions, prompts, token IDs, responses, GPU device, rates and hashes are retained separately for every checkpoint.

| Checkpoint | Diagnostic | Training choice | Passed numeric validation |
|---|---|---|---|
| codellama13b | arithmetic_forms | None | None |
| codellama13b | arithmetic_free | None | None |
| codellama34b | arithmetic_forms | None | None |
| codellama34b | arithmetic_free | print_direct_v3 | print_direct_v3 |
| llama31_8b | arithmetic_forms | print_direct_v3 | None |
| llama31_8b | arithmetic_free | print_direct_v3 | print_direct_v3 |
| llama32_3b | arithmetic_forms | None | None |
| llama32_3b | arithmetic_free | None | None |

Calibration selects direct before trace using only elementary training cells at ≥90% accuracy and ≤5% invalid with at least 24 examples per cell, then tests that choice on numeric validation. There is no fallback after validation failure. These familiar task structures do not establish structural generalization or a causal binding mechanism.

| Checkpoint | Protocol | Pairs | Without-only correct | With-only correct |
|---|---|---:|---:|---:|
| codellama13b | print_direct_v3 | 384 | 45 | 4 |
| codellama13b | print_trace_long_v1 | 384 | 40 | 30 |
| codellama34b | print_direct_v3 | 384 | 18 | 5 |
| codellama34b | print_trace_long_v1 | 384 | 26 | 10 |
| llama31_8b | print_direct_v3 | 384 | 21 | 8 |
| llama31_8b | print_trace_long_v1 | 384 | 13 | 16 |
| llama32_3b | print_direct_v3 | 384 | 47 | 19 |
| llama32_3b | print_trace_long_v1 | 384 | 44 | 15 |

The counterbalanced follow-up removes the previous answer-magnitude/distractor confound. These are exact descriptive within-cohort comparisons; adding a dead statement also changes length and context. The results alone do not identify an internal cause.

Compute accounting is uncapped under the user’s explicit project-priority instruction. Per-job walltimes keep jobs resumable; actual scheduler limits still apply.
