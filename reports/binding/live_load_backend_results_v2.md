# Corrected cross-backend and cache diagnostic

This post-hoc software check replays 396 exact inputs per model: one complete sign pair in training and one in development, with every naming/update/order/frontier and arithmetic-control relative retained. Selection used fixed hashes rather than response accuracy. These two structural components do not estimate full-cohort accuracy or provide independent replication.

The first CodeLlama Transformers diagnostic was truncated by a stop-string match spanning the prompt and first generated newline. Its original responses remain preserved. The corrected harness checks stop strings only in generated text; the original 76,032-response vLLM study already used generated-text stopping and remains unchanged.

| Model | Transformers correct / 396 | vLLM correct / 396 | Parsed predictions matching | HF invalid | vLLM invalid |
|---|---:|---:|---:|---:|---:|
| codellama34b | 53 | 54 | 375/396 | 1 | 1 |
| llama31_8b | 9 | 10 | 358/396 | 0 | 0 |

| Model | Uncached controls | Raw decoded text matching cached generation | Valid parsed predictions matching | Uncached invalid |
|---|---:|---:|---:|---:|
| codellama34b | 12 | 12 | 11 | 1 |
| llama31_8b | 12 | 12 | 12 | 0 |

Raw agreement and valid parsed-answer agreement are different: two identical malformed responses count as raw agreement, but never as a valid prediction match. First-token agreement and every raw response are retained in the machine-readable audits.

Both full-cohort models failed the fixed arithmetic/clean-program reliability gate. These diagnostics report backend and cache sensitivity without altering those gates or selecting a favorable subset as the scientific result. See the [full study comparison](live_load_results_v2.md). No selective binding mechanism, final-test forecast or language-model training is claimed.
