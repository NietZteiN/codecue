# All four values and direct relationships from one query state

Adaptive discovery on the existing cohort. Archived prompts request one variable. This tests access to unrequested slots; it cannot rule out a global representation under an all-variable query. All alphas use TRAIN structural folds. Hidden features have no metadata or oracle pointers. Source is a shared character-hash baseline on the complete source including its print query.

| Features | Width | Scalar slot exact | Scalar MAE | Scalar all four | Categorical slot exact | Categorical all four | Direct relation BA |
|---|---:|---:|---:|---:|---:|---:|---:|
| llama8b | 1024 | 8.29% | 4.165 | 0.03% | 20.61% | 0.18% | 55.05% |
| llama8b | 4096 | 8.61% | 4.130 | 0.00% | 21.56% | 0.15% | 55.25% |
| codellama34b | 1024 | 8.60% | 4.091 | 0.03% | 24.06% | 0.39% | 56.96% |
| codellama34b | 8192 | 9.37% | 3.981 | 0.03% | 27.76% | 0.46% | 56.74% |
| source | 1024 | 8.02% | 4.200 | 0.00% | 37.82% | 1.65% | 54.25% |
| source | 4096 | 8.19% | 4.190 | 0.00% | 38.21% | 1.62% | 54.64% |
| source | 8192 | 8.19% | 4.192 | 0.00% | 38.25% | 1.70% | 54.60% |

## Direct versus externally derived relationships

Each entry averages the three seeds. Derived rows use the separately TRAIN-selected value readout. BA is only shown where all four relation types are supported.

| Features | Width | Direct real BA | Direct shuffled BA | Direct prior BA | Derived scalar BA | Derived categorical BA |
|---|---:|---:|---:|---:|---:|---:|
| llama8b | 1024 | 55.05% | 50.37% | 50.00% | 51.01% | 52.14% |
| llama8b | 4096 | 55.25% | 50.40% | 50.00% | 51.49% | 53.11% |
| codellama34b | 1024 | 56.96% | 50.37% | 50.00% | 51.06% | 52.99% |
| codellama34b | 8192 | 56.74% | 49.64% | 50.00% | 52.27% | 53.83% |
| source | 1024 | 54.25% | 49.72% | 50.00% | 51.56% | 56.92% |
| source | 4096 | 54.64% | 49.57% | 50.00% | 51.45% | 56.86% |
| source | 8192 | 54.60% | 49.59% | 50.00% | 51.48% | 56.93% |

## Paired hidden minus matched-width source contrasts

Seeds are averaged within structural families before 2,000 paired bootstrap replicates. These 95% intervals are descriptive and non-simultaneous on inspected DEV; negative MAE differences favor hidden features.

| Features | Width | Metric | Difference | 95% interval |
|---|---:|---|---:|---:|
| llama8b | 1024 | mae | -0.0352 | [-0.1137, 0.0445] |
| llama8b | 1024 | scalar_all_four | 0.0003 | [0.0000, 0.0008] |
| llama8b | 1024 | categorical_all_four | -0.0147 | [-0.0265, -0.0054] |
| llama8b | 4096 | mae | -0.0600 | [-0.1550, 0.0326] |
| llama8b | 4096 | scalar_all_four | 0.0000 | [0.0000, 0.0000] |
| llama8b | 4096 | categorical_all_four | -0.0147 | [-0.0262, -0.0054] |
| codellama34b | 1024 | mae | -0.1092 | [-0.1860, -0.0310] |
| codellama34b | 1024 | scalar_all_four | 0.0003 | [0.0000, 0.0008] |
| codellama34b | 1024 | categorical_all_four | -0.0126 | [-0.0239, -0.0039] |
| codellama34b | 8192 | mae | -0.2111 | [-0.3112, -0.1140] |
| codellama34b | 8192 | scalar_all_four | 0.0003 | [0.0000, 0.0008] |
| codellama34b | 8192 | categorical_all_four | -0.0123 | [-0.0231, -0.0036] |

Direct relation scores are independent linear outputs, thresholded at weighted fitting prevalence. They are not calibrated probabilities. Equality/order/sum/difference types receive equal weight; each class recall gives equal weight to families containing that class. TRAIN-ineligible heads or evaluation heads lacking either class are explicitly unsupported. Relations computed externally from rounded scalar or categorical values are derived readouts, not additional evidence that the model decodes relations. The saved banks include all 48 cell supports, per-slot values, queried/unqueried and computed/untouched strata, coherent family-shuffled controls, and fitting-prior comparisons. Their alphas are selected using real TRAIN targets, so controls are not independently optimized null upper bounds. This is neither a novel-family confirmation nor a causal-use test. No new model calls or sealed-final access.
