# Ordinary versus alternate program semantics: discovery results

All features were captured from ordinary programs. Ordinary fits are reused from the completed numeric study; alternate fits swap addition/subtraction meanings without changing inputs, captures, rows or splits. Scalar normalized MAE divides by the selected seed's weighted TRAIN target standard deviation. Differences in target difficulty remain explicit; this is not causal-use evidence.

| Features | Width | Target semantics | Scalar exact | Scalar MAE | Normalized MAE | Sign BA | Parity BA | Mod5 BA |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| llama8b | 4096 | ordinary | 9.96% | 3.841 | 0.538 | 56.38% | 54.27% | 22.86% |
| llama8b | 4096 | operator_swap | 9.74% | 3.718 | 0.493 | 54.18% | 54.27% | 22.05% |
| codellama34b | 8192 | ordinary | 11.48% | 3.527 | 0.494 | 56.78% | 56.02% | 21.80% |
| codellama34b | 8192 | operator_swap | 11.54% | 3.452 | 0.458 | 57.14% | 56.02% | 22.32% |
| source4096 | 4096 | ordinary | 6.66% | 4.938 | 0.692 | 41.18% | 54.53% | 21.34% |
| source4096 | 4096 | operator_swap | 7.62% | 4.434 | 0.588 | 43.51% | 54.53% | 20.67% |
| source8192 | 8192 | ordinary | 6.64% | 4.943 | 0.692 | 41.21% | 54.63% | 21.19% |
| source8192 | 8192 | operator_swap | 7.68% | 4.435 | 0.588 | 43.47% | 54.63% | 20.77% |

## Paired family contrasts

Positive differences favor ordinary semantics. Average the three fitting seeds within each family, then bootstrap structural families (2,000 replicates, seed 20261031). Intervals are descriptive, non-simultaneous and use adaptive DEV. A positive difference can reflect target difficulty or surface inductive biases; source contrasts help assess this limitation.

| Features | Contrast | Difference | 95% interval | Families |
|---|---|---:|---:|---:|
| llama8b | alternate minus ordinary normalized MAE | -0.045 | [-0.085, -0.000] | 72 |
| codellama34b | alternate minus ordinary normalized MAE | -0.036 | [-0.071, 0.001] | 72 |
| source4096 | alternate minus ordinary normalized MAE | -0.103 | [-0.155, -0.047] | 72 |
| source8192 | alternate minus ordinary normalized MAE | -0.104 | [-0.156, -0.048] | 72 |
| llama8b | hidden semantic preference minus matched source preference | 0.059 | [0.021, 0.095] | 72 |
| codellama34b | hidden semantic preference minus matched source preference | 0.068 | [0.030, 0.105] | 72 |

## Target difficulty

| Split | Semantics | Rows | Range | Standard deviation | Value entropy (bits) | Values beyond old ±96 domain |
|---|---|---:|---|---:|---:|---:|
| calibration | ordinary | 108 | [-12, 11] | 5.557 | 4.083 | 0 |
| calibration | operator_swap | 108 | [-10, 8] | 4.391 | 3.614 | 0 |
| development | ordinary | 5184 | [-34, 38] | 6.846 | 4.768 | 0 |
| development | operator_swap | 5184 | [-34, 30] | 6.572 | 4.717 | 0 |
| train | ordinary | 15552 | [-48, 45] | 7.587 | 4.894 | 0 |
| train | operator_swap | 15552 | [-56, 60] | 8.131 | 4.944 | 0 |

No rows were clipped, wrapped or removed. Label entropies describe the row distribution, not independent samples. Fixed paired inputs and source controls do not prove equal learnability of the two target semantics. Only one nonidentity permutation exists for this two-operator language. The oracle archive also prepares all-variable/version and pair/triple relation labels; these are not additional decoded results. No misleading-name, trace-format, unfamiliar-family confirmation or neural-intervention claim is established here. Family-shuffled controls and encoded TRAIN priors remain in the saved fit banks; their alphas are selected on real TRAIN targets. Ordinary baseline fits retain their original source and larger independent-column target layout.
