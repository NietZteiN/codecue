# Exploratory calibration error and length audit

Calibration-only discovery. Original pilot scores and competence gates remain unchanged. Diagnostic extraction accepts explicit Markdown answer headings without consulting gold values. Truncated outputs remain failures in strict and complete-response diagnostic scores. Answer-before-cutoff is reported separately, never used to pass a gate. No formal captures, probe fits, causal interventions or sealed-final access.

| Model | Protocol | Scope | Cases | Original strict | Diagnostic complete | Truncated | Correct answer but truncated | Continued strict |
|---|---|---|---:|---:|---:|---:|---:|---:|
| codellama34b | output_only | single | 216 | 33.33% | 33.33% | 0 | 0 | pending |
| codellama34b | output_only | all | 216 | 29.63% | 29.63% | 50 | 11 | pending |
| codellama34b | intermediate_query | single | 216 | 25.00% | 25.00% | 108 | 0 | pending |
| codellama34b | intermediate_query | all | 216 | 0.46% | 0.46% | 215 | 32 | pending |
| codellama34b | stepwise | single | 216 | 72.69% | 72.69% | 0 | 0 | pending |
| codellama34b | stepwise | all | 216 | 81.02% | 81.02% | 4 | 2 | pending |
| llama8b | output_only | single | 216 | 53.24% | 53.24% | 0 | 0 | pending |
| llama8b | output_only | all | 216 | 31.94% | 31.94% | 80 | 36 | pending |
| llama8b | intermediate_query | single | 216 | 0.00% | 0.00% | 216 | 0 | pending |
| llama8b | intermediate_query | all | 216 | 0.00% | 0.00% | 216 | 0 | pending |
| llama8b | stepwise | single | 216 | 46.30% | 80.56% | 27 | 1 | pending |
| llama8b | stepwise | all | 216 | 72.22% | 77.78% | 25 | 0 | pending |

## Matched query-scope diagnostics

Compare the same retained target, rather than single-value accuracy against the harder all-four joint metric. Every pair has identical source, instruction and protocol. Prefix continuations preserve earlier generated tokens, but are not guaranteed equivalent to one monolithic greedy run because batching/numerical kernels can differ.

| Model | Protocol | Pairs | Single target correct | All-scope target correct | Both accepted | Accepted predictions disagree |
|---|---|---:|---:|---:|---:|---:|
| codellama34b | intermediate_query | 216 | 54 | 1 | 1 | 0 |
| codellama34b | output_only | 216 | 72 | 85 | 165 | 106 |
| codellama34b | stepwise | 216 | 157 | 194 | 164 | 15 |
| llama8b | intermediate_query | 216 | 0 | 0 | 0 | 0 |
| llama8b | output_only | 216 | 115 | 88 | 132 | 47 |
| llama8b | stepwise | 216 | 100 | 166 | 100 | 11 |

Candidate-error matches are retained in the JSON with all coincidences; matching a stale value, current operand recomputation or another binding does not identify an internal mechanism. Cells break down task/depth/instruction/mutation, with structural component counts. No wording is selected, no significance tests are performed, and these finite calibration components cannot support novel-family generalization claims.
