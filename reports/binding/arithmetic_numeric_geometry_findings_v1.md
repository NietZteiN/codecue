# Numeric geometry: controlled discovery comparison

Geometry-aware linear output maps on the same full-width definition features. Circular versus permuted-circle pairs match input access and output dimension. All alpha selection uses grouped TRAIN validation; existing DEV remains adaptive discovery.

| Worker | Role | Width | Code geometry | DEV exact | MAE | Family-control exact | Encoded TRAIN prior exact | Parameters |
|---|---|---:|---|---:|---:|---:|---:|---:|
| llama8b_root_definition | root_definition | 4096 | decimal_circle | 100.00% | 0.000 | 7.54% | 7.79% | 28763 |
| llama8b_root_definition | root_definition | 4096 | decimal_permuted | 99.99% | 0.000 | 6.34% | 7.46% | 28763 |
| llama8b_root_definition | root_definition | 4096 | crt_circle | 99.99% | 0.000 | 8.17% | 7.91% | 16436 |
| llama8b_root_definition | root_definition | 4096 | crt_permuted | 99.40% | 0.253 | 0.89% | 0.00% | 16436 |
| llama8b_root_definition | root_definition | 4096 | ordinal | 100.00% | 0.000 | 8.19% | 7.91% | 788928 |
| llama8b_computed_definition | computed_definition | 4096 | decimal_circle | 10.38% | 5.462 | 5.10% | 5.38% | 28763 |
| llama8b_computed_definition | computed_definition | 4096 | decimal_permuted | 7.85% | 10.999 | 4.13% | 2.76% | 28763 |
| llama8b_computed_definition | computed_definition | 4096 | crt_circle | 9.68% | 6.865 | 4.58% | 9.44% | 16436 |
| llama8b_computed_definition | computed_definition | 4096 | crt_permuted | 1.23% | 49.050 | 0.58% | 0.00% | 16436 |
| llama8b_computed_definition | computed_definition | 4096 | ordinal | 12.60% | 3.674 | 7.01% | 9.44% | 788928 |
| codellama34b_root_definition | root_definition | 8192 | decimal_circle | 100.00% | 0.000 | 7.45% | 7.79% | 57435 |
| codellama34b_root_definition | root_definition | 8192 | decimal_permuted | 100.00% | 0.000 | 6.15% | 7.46% | 57435 |
| codellama34b_root_definition | root_definition | 8192 | crt_circle | 99.99% | 0.000 | 8.32% | 7.91% | 32820 |
| codellama34b_root_definition | root_definition | 8192 | crt_permuted | 99.79% | 0.075 | 0.95% | 0.00% | 32820 |
| codellama34b_root_definition | root_definition | 8192 | ordinal | 100.00% | 0.000 | 8.07% | 7.91% | 1575360 |
| codellama34b_computed_definition | computed_definition | 8192 | decimal_circle | 11.20% | 4.026 | 4.69% | 5.38% | 57435 |
| codellama34b_computed_definition | computed_definition | 8192 | decimal_permuted | 9.16% | 12.433 | 4.04% | 2.76% | 57435 |
| codellama34b_computed_definition | computed_definition | 8192 | crt_circle | 10.92% | 6.477 | 4.34% | 9.44% | 32820 |
| codellama34b_computed_definition | computed_definition | 8192 | crt_permuted | 1.16% | 48.783 | 0.74% | 0.00% | 32820 |
| codellama34b_computed_definition | computed_definition | 8192 | ordinal | 14.91% | 3.338 | 6.71% | 9.44% | 1575360 |
| source4096_root_definition | root_definition | 4096 | decimal_circle | 100.00% | 0.000 | 8.26% | 7.79% | 28763 |
| source4096_root_definition | root_definition | 4096 | decimal_permuted | 100.00% | 0.000 | 6.63% | 7.46% | 28763 |
| source4096_root_definition | root_definition | 4096 | crt_circle | 100.00% | 0.000 | 7.86% | 7.91% | 16436 |
| source4096_root_definition | root_definition | 4096 | crt_permuted | 100.00% | 0.000 | 0.80% | 0.00% | 16436 |
| source4096_root_definition | root_definition | 4096 | ordinal | 100.00% | 0.000 | 7.96% | 7.91% | 788928 |
| source4096_computed_definition | computed_definition | 4096 | decimal_circle | 6.06% | 5.281 | 5.16% | 5.38% | 28763 |
| source4096_computed_definition | computed_definition | 4096 | decimal_permuted | 5.21% | 11.208 | 4.31% | 2.76% | 28763 |
| source4096_computed_definition | computed_definition | 4096 | crt_circle | 5.48% | 9.072 | 4.59% | 9.44% | 16436 |
| source4096_computed_definition | computed_definition | 4096 | crt_permuted | 0.72% | 49.239 | 0.49% | 0.00% | 16436 |
| source4096_computed_definition | computed_definition | 4096 | ordinal | 7.66% | 4.843 | 7.17% | 9.44% | 788928 |
| source8192_root_definition | root_definition | 8192 | decimal_circle | 100.00% | 0.000 | 8.26% | 7.79% | 57435 |
| source8192_root_definition | root_definition | 8192 | decimal_permuted | 100.00% | 0.000 | 6.62% | 7.46% | 57435 |
| source8192_root_definition | root_definition | 8192 | crt_circle | 100.00% | 0.000 | 7.88% | 7.91% | 32820 |
| source8192_root_definition | root_definition | 8192 | crt_permuted | 100.00% | 0.000 | 0.80% | 0.00% | 32820 |
| source8192_root_definition | root_definition | 8192 | ordinal | 100.00% | 0.000 | 7.96% | 7.91% | 1575360 |
| source8192_computed_definition | computed_definition | 8192 | decimal_circle | 5.99% | 5.294 | 5.15% | 5.38% | 57435 |
| source8192_computed_definition | computed_definition | 8192 | decimal_permuted | 5.11% | 11.291 | 4.30% | 2.76% | 57435 |
| source8192_computed_definition | computed_definition | 8192 | crt_circle | 5.53% | 9.062 | 4.58% | 9.44% | 32820 |
| source8192_computed_definition | computed_definition | 8192 | crt_permuted | 0.72% | 49.086 | 0.65% | 0.00% | 32820 |
| source8192_computed_definition | computed_definition | 8192 | ordinal | 7.64% | 4.845 | 7.20% | 9.44% | 1575360 |

## Paired structural-family contrasts

Exact-accuracy differences in percentage points. Average fitting seeds within each family, then bootstrap families (2,000 replicates, fixed seed 20261031). These descriptive 95% percentile intervals are not simultaneous, do not include new-cohort uncertainty and do not correct adaptive DEV selection.

| Comparison | Difference | 95% interval | Families |
|---|---:|---:|---:|
| llama8b_root_definition: decimal_circle minus decimal_permuted | 0.01 | [0.00, 0.02] | 72 |
| llama8b_root_definition: crt_circle minus crt_permuted | 0.59 | [0.34, 0.91] | 72 |
| llama8b_root_definition: decimal_circle hidden minus source | 0.00 | [0.00, 0.00] | 72 |
| llama8b_root_definition: decimal_permuted hidden minus source | -0.01 | [-0.02, 0.00] | 72 |
| llama8b_root_definition: crt_circle hidden minus source | -0.01 | [-0.04, 0.00] | 72 |
| llama8b_root_definition: crt_permuted hidden minus source | -0.60 | [-0.94, -0.34] | 72 |
| llama8b_root_definition: ordinal hidden minus source | 0.00 | [0.00, 0.00] | 72 |
| llama8b_computed_definition: decimal_circle minus decimal_permuted | 2.54 | [1.63, 3.40] | 72 |
| llama8b_computed_definition: crt_circle minus crt_permuted | 8.45 | [7.40, 9.61] | 72 |
| llama8b_computed_definition: decimal_circle hidden minus source | 4.32 | [2.79, 5.90] | 72 |
| llama8b_computed_definition: decimal_permuted hidden minus source | 2.64 | [1.16, 4.20] | 72 |
| llama8b_computed_definition: crt_circle hidden minus source | 4.21 | [2.93, 5.49] | 72 |
| llama8b_computed_definition: crt_permuted hidden minus source | 0.52 | [0.08, 0.97] | 72 |
| llama8b_computed_definition: ordinal hidden minus source | 4.94 | [3.32, 6.74] | 72 |
| codellama34b_root_definition: decimal_circle minus decimal_permuted | 0.00 | [0.00, 0.00] | 72 |
| codellama34b_root_definition: crt_circle minus crt_permuted | 0.20 | [0.09, 0.33] | 72 |
| codellama34b_root_definition: decimal_circle hidden minus source | 0.00 | [0.00, 0.00] | 72 |
| codellama34b_root_definition: decimal_permuted hidden minus source | 0.00 | [0.00, 0.00] | 72 |
| codellama34b_root_definition: crt_circle hidden minus source | -0.01 | [-0.02, 0.00] | 72 |
| codellama34b_root_definition: crt_permuted hidden minus source | -0.21 | [-0.34, -0.09] | 72 |
| codellama34b_root_definition: ordinal hidden minus source | 0.00 | [0.00, 0.00] | 72 |
| codellama34b_computed_definition: decimal_circle minus decimal_permuted | 2.04 | [0.96, 3.16] | 72 |
| codellama34b_computed_definition: crt_circle minus crt_permuted | 9.77 | [8.54, 11.18] | 72 |
| codellama34b_computed_definition: decimal_circle hidden minus source | 5.21 | [3.80, 6.83] | 72 |
| codellama34b_computed_definition: decimal_permuted hidden minus source | 4.05 | [2.35, 5.85] | 72 |
| codellama34b_computed_definition: crt_circle hidden minus source | 5.40 | [3.98, 6.87] | 72 |
| codellama34b_computed_definition: crt_permuted hidden minus source | 0.43 | [0.03, 0.90] | 72 |
| codellama34b_computed_definition: ordinal hidden minus source | 7.27 | [5.45, 9.27] | 72 |
| source4096_root_definition: decimal_circle minus decimal_permuted | 0.00 | [0.00, 0.00] | 72 |
| source4096_root_definition: crt_circle minus crt_permuted | 0.00 | [0.00, 0.00] | 72 |
| source4096_computed_definition: decimal_circle minus decimal_permuted | 0.85 | [-0.09, 1.87] | 72 |
| source4096_computed_definition: crt_circle minus crt_permuted | 4.76 | [4.09, 5.50] | 72 |
| source8192_root_definition: decimal_circle minus decimal_permuted | 0.00 | [0.00, 0.00] | 72 |
| source8192_root_definition: crt_circle minus crt_permuted | 0.00 | [0.00, 0.00] | 72 |
| source8192_computed_definition: decimal_circle minus decimal_permuted | 0.88 | [-0.05, 1.87] | 72 |
| source8192_computed_definition: crt_circle minus crt_permuted | 4.80 | [4.10, 5.54] | 72 |

The geometric permutation controls preserve code dimension, candidate identities and circular radii while changing numerical adjacency. Coherent-family controls are a separate label-assignment test. Signed decimal and residue/template decoding are adaptations, not a direct replication of the positive-literal paper. Neither smooth-code performance nor a stronger nonlinear readout establishes native execution. Compare all planned panels, old categorical/one-hot-digit baselines and independent-family transfer before claiming a representational mechanism. The decoder enumerates the predeclared integer label domain; it receives no program operators or gold routing pointers. Probabilistic calibration/MDL and causal interventions are not measured by this fit.
