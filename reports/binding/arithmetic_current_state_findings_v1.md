# Current bindings, numeric states and derived relationships

Adaptive follow-up on the already inspected structural development families. Primary pipeline: variable-anchor query -> predicted current definition -> role-conditioned regression -> derived algebraic relations. Independent models are composed without new fitting. Source node/slot scaffolds remain supplied; exact execution is a 100% source ceiling.

| Model | Route | Numeric decoder | Binding accuracy | Whole numeric state | Value MAE | Derived relation balanced accuracy |
|---|---|---|---:|---:|---:|---:|
| llama8b | anchor_query | hidden/categorical | 45.39% | 0.69% | 4.130 | 53.48% |
| llama8b | anchor_query | hidden/regression | 45.39% | 0.08% | 4.170 | 52.28% |
| llama8b | anchor_query_operands | hidden/regression | 45.39% | 0.10% | 4.038 | 52.55% |
| llama8b | answer_query | hidden/regression | 49.06% | 0.05% | 4.089 | 52.25% |
| llama8b | oracle_route | hidden/regression | supplied | 0.08% | 3.672 | 53.99% |
| llama8b | pure_answer_state | hidden/regression | n.a. | 0.00% | 4.369 | 50.50% |
| llama8b | pure_answer_state | source/regression | n.a. | 0.03% | 4.341 | 50.22% |
| llama8b | source_query | source/regression | 94.85% | 0.03% | 3.817 | 54.52% |
| codellama34b | anchor_query | hidden/categorical | 45.52% | 0.46% | 4.230 | 53.11% |
| codellama34b | anchor_query | hidden/regression | 45.52% | 0.03% | 4.190 | 52.36% |
| codellama34b | anchor_query_operands | hidden/regression | 45.52% | 0.03% | 4.114 | 52.90% |
| codellama34b | answer_query | hidden/regression | 51.83% | 0.00% | 4.092 | 52.71% |
| codellama34b | oracle_route | hidden/regression | supplied | 0.13% | 3.649 | 54.40% |
| codellama34b | pure_answer_state | hidden/regression | n.a. | 0.05% | 4.314 | 50.57% |
| codellama34b | pure_answer_state | source/regression | n.a. | 0.00% | 4.327 | 50.41% |
| codellama34b | source_query | source/regression | 94.85% | 0.08% | 4.079 | 53.29% |

All declared routes, encodings, layers selected within TRAIN, control tasks and priors remain in machine-readable results. Relation cells require TRAIN support and both evaluation classes; undefined cells are retained. The oracle route supplies correct binding pointers and is not end-to-end decoding. Operand composition supplies source operators and performs external arithmetic on decoded read operands; it is not evidence that a neural computed result was decoded. Version accuracy annotates predicted definition nodes rather than independently probing version labels. Pure answer-state numeric heads use one final state; answer-query routing additionally sees earlier candidate states. Calibration scores remain separate and never train a probe.

| Model | Numeric features/encoding | Computed-write MAE | Computed-write exact | Read-computed-operand MAE | Root exact | Prior write MAE | Shuffled write MAE |
|---|---|---:|---:|---:|---:|---:|---:|
| llama8b | hidden/categorical | 5.040 | 9.46% | 4.855 | 98.03% | 5.053 | 5.216 |
| llama8b | hidden/regression | 4.831 | 7.17% | 4.564 | 30.17% | 5.055 | 5.102 |
| llama8b | source/categorical | 4.985 | 8.85% | 4.795 | 65.10% | 5.053 | 5.137 |
| llama8b | source/regression | 4.908 | 6.10% | 4.458 | 20.97% | 5.055 | 5.152 |
| codellama34b | hidden/categorical | 5.099 | 8.70% | 4.823 | 98.91% | 5.053 | 5.310 |
| codellama34b | hidden/regression | 4.733 | 7.25% | 4.576 | 31.93% | 5.055 | 5.106 |
| codellama34b | source/categorical | 4.960 | 8.96% | 4.751 | 76.66% | 5.053 | 5.158 |
| codellama34b | source/regression | 4.882 | 6.40% | 4.498 | 15.77% | 5.055 | 5.099 |

Numeric layers/alphas are selected separately per encoding from TRAIN computed-write MAE. Read and write roles have independent feature blocks even when they share a token. The numeric source comparator and conditional TRAIN priors remain explicit.

| Model | Matched architecture | Counterpart features | Real dependency accuracy | Random-family control |
|---|---|---|---:|---:|
| llama8b | bilinear | hidden_global | 23.79% | 18.95% |
| llama8b | bilinear | source_local | 77.53% | 20.11% |
| codellama34b | mlp | hidden_global | 22.84% | 19.84% |
| codellama34b | mlp | source_local | 78.48% | 19.25% |

Counterpart architecture is fixed to the original TRAIN-selected local method; this follow-up makes no additional model selection. Original primary decoder selections remain preserved. All results here are adaptive discovery, with no causal-use or untouched-confirmation claim.

