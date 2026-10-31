# Completed local-dependency discovery: saved-result snapshot

All original local-suite jobs completed successfully. Saved dependency model/score checksums and behavioral parsing/counts passed their postrun integrity checks. Independent activation-to-score replay is queued in the follow-up suite; this snapshot summarizes the saved measurements without fitting or querying a language model.

| Model | Features | TRAIN-selected architecture | Parent accuracy | Complete graph | Random-family accuracy |
|---|---|---|---:|---:|---:|
| llama8b | hidden_local | bilinear | 86.72% | 41.46% | 18.86% |
| llama8b | hidden_global | linear | 22.49% | 0.00% | 18.76% |
| llama8b | source_local | bilinear | 77.53% | 26.23% | 20.11% |
| codellama34b | hidden_local | mlp | 83.43% | 34.54% | 18.79% |
| codellama34b | hidden_global | bilinear | 24.03% | 0.00% | 19.51% |
| codellama34b | source_local | bilinear | 77.53% | 26.23% | 20.11% |

These are family-macro parent accuracies on 72 new structural DEV families, averaged over three weighting seeds. Complete graphs contain four/eight/twelve ordered parents at two/four/six arithmetic updates. The answer-query comparison also receives earlier candidate-definition states. Exact source-name/recency parsing solves these labels at 100%; character features are a limited learned comparator. Architectures were selected separately inside TRAIN, so capacity-matched counterparts remain a separate queued sensitivity.

Data diversity, decoder architectures, candidate masks and token access all differ from the initial global study. This result cannot isolate localization as the cause of the gain, and it does not establish a complete numeric state or natural causal use.

| Model | Wording | Split/depth/query | Correct / cases | Invalid |
|---|---:|---|---:|---:|
| llama8b | I0 | calibration / 1 / arithmetic_written | 40/108 | 8 |
| llama8b | I0 | development / 2 / arithmetic_written | 63/240 | 7 |
| llama8b | I0 | development / 2 / untouched_literal | 177/192 | 1 |
| llama8b | I1 | calibration / 1 / arithmetic_written | 70/108 | 6 |
| llama8b | I1 | development / 2 / arithmetic_written | 69/240 | 10 |
| llama8b | I1 | development / 2 / untouched_literal | 178/192 | 1 |
| llama8b | I2 | calibration / 1 / arithmetic_written | 26/108 | 51 |
| llama8b | I2 | development / 2 / arithmetic_written | 54/240 | 93 |
| llama8b | I2 | development / 2 / untouched_literal | 10/192 | 178 |
| codellama34b | I0 | calibration / 1 / arithmetic_written | 82/108 | 0 |
| codellama34b | I0 | development / 2 / arithmetic_written | 75/240 | 0 |
| codellama34b | I0 | development / 2 / untouched_literal | 177/192 | 0 |
| codellama34b | I1 | calibration / 1 / arithmetic_written | 29/108 | 68 |
| codellama34b | I1 | development / 2 / arithmetic_written | 72/240 | 2 |
| codellama34b | I1 | development / 2 / untouched_literal | 170/192 | 1 |
| codellama34b | I2 | calibration / 1 / arithmetic_written | 75/108 | 0 |
| codellama34b | I2 | development / 2 / arithmetic_written | 78/240 | 0 |
| codellama34b | I2 | development / 2 / untouched_literal | 182/192 | 0 |

Computed answers remain unreliable and wording-sensitive. All wording results and invalid responses are retained. Representation captures use I0 only. Calibration families never train a probe.

The [CPU follow-up protocol](arithmetic_state_followup_plan_v2.md) queues independent replay, capacity-matched counterparts, current-definition lookup, role-conditioned numeric decoding and predicted-state algebraic relationships. Its primary composed pipeline uses predicted binding pointers. Oracle routing and arithmetic performed externally on decoded operands are separately labeled ceilings/diagnostics.

