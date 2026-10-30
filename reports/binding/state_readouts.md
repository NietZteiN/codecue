# Discovery linear readouts

Weighted ridge classifiers train only on neutral training cases. Three predeclared positive template-weighting seeds retain all training structures. Normalization uses neutral training data only; regularization is fixed. Hidden and surface features use the same 4,096 dimensions and output-head capacity. Pre-query twins are deduplicated. These are measurement results, not a mechanism claim.

| Features | Block | Site | Development naming | Current accuracy | Saved accuracy |
|---|---:|---|---|---:|---:|
| hidden | 8 | after_query | informative | 8.29% | 11.28% |
| hidden | 8 | after_query | misleading | 7.64% | 11.41% |
| hidden | 8 | after_query | neutral | 7.38% | 10.94% |
| hidden | 8 | pre_query_state | informative | 35.94% | 4.86% |
| hidden | 8 | pre_query_state | misleading | 28.47% | 5.47% |
| hidden | 8 | pre_query_state | neutral | 48.18% | 6.77% |
| hidden | 16 | after_query | informative | 5.08% | 4.17% |
| hidden | 16 | after_query | misleading | 4.56% | 5.51% |
| hidden | 16 | after_query | neutral | 8.72% | 9.90% |
| hidden | 16 | pre_query_state | informative | 44.97% | 6.34% |
| hidden | 16 | pre_query_state | misleading | 44.97% | 5.56% |
| hidden | 16 | pre_query_state | neutral | 50.09% | 9.03% |
| hidden | 24 | after_query | informative | 2.08% | 4.86% |
| hidden | 24 | after_query | misleading | 2.95% | 5.99% |
| hidden | 24 | after_query | neutral | 1.17% | 10.29% |
| hidden | 24 | pre_query_state | informative | 48.44% | 5.99% |
| hidden | 24 | pre_query_state | misleading | 50.00% | 5.82% |
| hidden | 24 | pre_query_state | neutral | 52.95% | 10.94% |
| surface | -1 | after_query | informative | 4.99% | 1.39% |
| surface | -1 | after_query | misleading | 4.43% | 0.74% |
| surface | -1 | after_query | neutral | 5.03% | 3.95% |
| surface | -1 | pre_query_state | informative | 4.17% | 1.82% |
| surface | -1 | pre_query_state | misleading | 3.82% | 1.65% |
| surface | -1 | pre_query_state | neutral | 6.25% | 4.25% |

Full seed-level results include identifier-control accuracy/selectivity, parameter counts, class support and joint accuracy. Identifier-stem controls have few keys; high control accuracy is not evidence of semantic binding. Character-ngram surface features are one capacity-matched comparator, not an exhaustive shortcut audit. Cross-naming failures may reflect harmless representational change. No final outcomes or language-model training were used.
