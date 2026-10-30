# Arithmetic and readout feasibility comparison

Both cached checkpoints completed the registered cohort: 12,288 responses. Complete execution and passed artifact audits are separate from reliability qualification.

Fresh numeric calibration on repeated arithmetic structures, not structural generalization or a causal mechanism test. One versus three operations also changes intermediate literal exposure; storage forms change assignments, dependencies and token distances. Trace responses change computation and generation allowance and are never pooled with direct answers. Intervals are exploratory without multiplicity adjustment. Historical failed gates and sealed final/extrapolation outcomes remain unchanged.

| Checkpoint | Protocol | Correct / n | Invalid | Training qualified | Numeric development qualified | Reliability |
|---|---|---:|---:|---|---|---|
| codellama34b | print_direct_v3 | 1732/3072 | 11 | False | False | failed |
| codellama34b | print_trace_long_v1 | 2207/3072 | 5 | False | False | failed |
| llama31_8b | print_direct_v3 | 1893/3072 | 0 | False | False | failed |
| llama31_8b | print_trace_long_v1 | 2573/3072 | 6 | False | False | failed |

## All paired arithmetic/storage contrasts

| Checkpoint | Protocol | Split | Contrast | Pairs | Relative groups | Difference | Exploratory 95% interval |
|---|---|---|---|---:|---:|---:|---|
| codellama34b | print_direct_v3 | all | three_literal_minus_one_literal | 384 | 192 | -72.14% | [-76.04%, -67.97%] |
| codellama34b | print_direct_v3 | all | one_bound_minus_literal | 384 | 192 | +3.39% | [-0.26%, +7.03%] |
| codellama34b | print_direct_v3 | all | three_stored_intermediates_minus_literal | 384 | 192 | -4.43% | [-7.29%, -1.56%] |
| codellama34b | print_direct_v3 | all | three_bound_minus_literal | 384 | 192 | -2.34% | [-4.69%, +0.00%] |
| codellama34b | print_direct_v3 | all | one_stored_result_minus_literal | 384 | 192 | -1.04% | [-2.60%, +0.52%] |
| codellama34b | print_direct_v3 | all | zero_stored_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| codellama34b | print_direct_v3 | train | three_literal_minus_one_literal | 192 | 96 | -69.79% | [-76.56%, -63.02%] |
| codellama34b | print_direct_v3 | train | one_bound_minus_literal | 192 | 96 | +5.21% | [+0.00%, +10.42%] |
| codellama34b | print_direct_v3 | train | three_stored_intermediates_minus_literal | 192 | 96 | -7.29% | [-11.46%, -3.12%] |
| codellama34b | print_direct_v3 | train | three_bound_minus_literal | 192 | 96 | -3.12% | [-7.29%, +0.53%] |
| codellama34b | print_direct_v3 | train | one_stored_result_minus_literal | 192 | 96 | -1.56% | [-3.65%, +0.52%] |
| codellama34b | print_direct_v3 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| codellama34b | print_direct_v3 | development | three_literal_minus_one_literal | 192 | 96 | -74.48% | [-79.69%, -69.27%] |
| codellama34b | print_direct_v3 | development | one_bound_minus_literal | 192 | 96 | +1.56% | [-3.65%, +7.29%] |
| codellama34b | print_direct_v3 | development | three_stored_intermediates_minus_literal | 192 | 96 | -1.56% | [-5.73%, +2.08%] |
| codellama34b | print_direct_v3 | development | three_bound_minus_literal | 192 | 96 | -1.56% | [-4.17%, +1.04%] |
| codellama34b | print_direct_v3 | development | one_stored_result_minus_literal | 192 | 96 | -0.52% | [-2.08%, +1.04%] |
| codellama34b | print_direct_v3 | development | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| codellama34b | print_trace_long_v1 | all | three_literal_minus_one_literal | 384 | 192 | -9.90% | [-15.36%, -4.69%] |
| codellama34b | print_trace_long_v1 | all | one_bound_minus_literal | 384 | 192 | +5.47% | [+1.04%, +9.64%] |
| codellama34b | print_trace_long_v1 | all | three_stored_intermediates_minus_literal | 384 | 192 | +19.79% | [+14.32%, +25.26%] |
| codellama34b | print_trace_long_v1 | all | three_bound_minus_literal | 384 | 192 | -57.81% | [-62.50%, -53.12%] |
| codellama34b | print_trace_long_v1 | all | one_stored_result_minus_literal | 384 | 192 | +5.73% | [+1.04%, +10.42%] |
| codellama34b | print_trace_long_v1 | all | zero_stored_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| codellama34b | print_trace_long_v1 | train | three_literal_minus_one_literal | 192 | 96 | -5.73% | [-13.02%, +1.56%] |
| codellama34b | print_trace_long_v1 | train | one_bound_minus_literal | 192 | 96 | +7.81% | [+2.60%, +13.54%] |
| codellama34b | print_trace_long_v1 | train | three_stored_intermediates_minus_literal | 192 | 96 | +16.67% | [+9.90%, +23.44%] |
| codellama34b | print_trace_long_v1 | train | three_bound_minus_literal | 192 | 96 | -61.46% | [-67.71%, -55.21%] |
| codellama34b | print_trace_long_v1 | train | one_stored_result_minus_literal | 192 | 96 | +7.29% | [+1.04%, +13.54%] |
| codellama34b | print_trace_long_v1 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| codellama34b | print_trace_long_v1 | development | three_literal_minus_one_literal | 192 | 96 | -14.06% | [-21.88%, -6.25%] |
| codellama34b | print_trace_long_v1 | development | one_bound_minus_literal | 192 | 96 | +3.12% | [-3.65%, +9.90%] |
| codellama34b | print_trace_long_v1 | development | three_stored_intermediates_minus_literal | 192 | 96 | +22.92% | [+15.10%, +31.25%] |
| codellama34b | print_trace_long_v1 | development | three_bound_minus_literal | 192 | 96 | -54.17% | [-60.94%, -46.88%] |
| codellama34b | print_trace_long_v1 | development | one_stored_result_minus_literal | 192 | 96 | +4.17% | [-2.60%, +10.42%] |
| codellama34b | print_trace_long_v1 | development | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_direct_v3 | all | three_literal_minus_one_literal | 384 | 192 | -57.81% | [-63.80%, -51.82%] |
| llama31_8b | print_direct_v3 | all | one_bound_minus_literal | 384 | 192 | +8.07% | [+5.47%, +10.68%] |
| llama31_8b | print_direct_v3 | all | three_stored_intermediates_minus_literal | 384 | 192 | -22.92% | [-26.82%, -18.75%] |
| llama31_8b | print_direct_v3 | all | three_bound_minus_literal | 384 | 192 | -18.75% | [-22.92%, -14.58%] |
| llama31_8b | print_direct_v3 | all | one_stored_result_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_direct_v3 | all | zero_stored_minus_literal | 384 | 192 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_direct_v3 | train | three_literal_minus_one_literal | 192 | 96 | -56.25% | [-65.10%, -47.38%] |
| llama31_8b | print_direct_v3 | train | one_bound_minus_literal | 192 | 96 | +7.29% | [+4.17%, +10.94%] |
| llama31_8b | print_direct_v3 | train | three_stored_intermediates_minus_literal | 192 | 96 | -23.96% | [-29.69%, -18.23%] |
| llama31_8b | print_direct_v3 | train | three_bound_minus_literal | 192 | 96 | -19.79% | [-25.52%, -14.06%] |
| llama31_8b | print_direct_v3 | train | one_stored_result_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_direct_v3 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_direct_v3 | development | three_literal_minus_one_literal | 192 | 96 | -59.38% | [-68.23%, -50.52%] |
| llama31_8b | print_direct_v3 | development | one_bound_minus_literal | 192 | 96 | +8.85% | [+4.69%, +13.02%] |
| llama31_8b | print_direct_v3 | development | three_stored_intermediates_minus_literal | 192 | 96 | -21.88% | [-28.12%, -16.15%] |
| llama31_8b | print_direct_v3 | development | three_bound_minus_literal | 192 | 96 | -17.71% | [-23.96%, -11.46%] |
| llama31_8b | print_direct_v3 | development | one_stored_result_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_direct_v3 | development | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_trace_long_v1 | all | three_literal_minus_one_literal | 384 | 192 | +22.14% | [+16.41%, +28.12%] |
| llama31_8b | print_trace_long_v1 | all | one_bound_minus_literal | 384 | 192 | +44.27% | [+40.36%, +48.44%] |
| llama31_8b | print_trace_long_v1 | all | three_stored_intermediates_minus_literal | 384 | 192 | +15.10% | [+10.94%, +19.01%] |
| llama31_8b | print_trace_long_v1 | all | three_bound_minus_literal | 384 | 192 | -18.75% | [-23.70%, -13.80%] |
| llama31_8b | print_trace_long_v1 | all | one_stored_result_minus_literal | 384 | 192 | +29.17% | [+24.22%, +34.38%] |
| llama31_8b | print_trace_long_v1 | all | zero_stored_minus_literal | 384 | 192 | -0.52% | [-1.30%, +0.00%] |
| llama31_8b | print_trace_long_v1 | train | three_literal_minus_one_literal | 192 | 96 | +18.75% | [+10.94%, +26.56%] |
| llama31_8b | print_trace_long_v1 | train | one_bound_minus_literal | 192 | 96 | +42.71% | [+36.46%, +48.96%] |
| llama31_8b | print_trace_long_v1 | train | three_stored_intermediates_minus_literal | 192 | 96 | +16.15% | [+10.42%, +21.88%] |
| llama31_8b | print_trace_long_v1 | train | three_bound_minus_literal | 192 | 96 | -17.19% | [-23.96%, -10.42%] |
| llama31_8b | print_trace_long_v1 | train | one_stored_result_minus_literal | 192 | 96 | +27.60% | [+19.79%, +35.42%] |
| llama31_8b | print_trace_long_v1 | train | zero_stored_minus_literal | 192 | 96 | +0.00% | [+0.00%, +0.00%] |
| llama31_8b | print_trace_long_v1 | development | three_literal_minus_one_literal | 192 | 96 | +25.52% | [+17.19%, +33.85%] |
| llama31_8b | print_trace_long_v1 | development | one_bound_minus_literal | 192 | 96 | +45.83% | [+40.10%, +52.08%] |
| llama31_8b | print_trace_long_v1 | development | three_stored_intermediates_minus_literal | 192 | 96 | +14.06% | [+8.33%, +19.79%] |
| llama31_8b | print_trace_long_v1 | development | three_bound_minus_literal | 192 | 96 | -20.31% | [-26.56%, -14.06%] |
| llama31_8b | print_trace_long_v1 | development | one_stored_result_minus_literal | 192 | 96 | +30.73% | [+23.96%, +37.50%] |
| llama31_8b | print_trace_long_v1 | development | zero_stored_minus_literal | 192 | 96 | -1.04% | [-2.60%, +0.00%] |

Complete form × protocol × split × sign cells, including zero-operation controls, appear in each report and the machine-readable comparison.

- [codellama34b](arithmetic_readout_codellama34b_v1.md)
- [llama31_8b](arithmetic_readout_llama31_8b_v1.md)

The same numeric cohort is shared by the two checkpoints. Numeric examples and sign-relative bootstrap groups do not provide independent structural or program-family replications. No protocol/cell winner is selected.
