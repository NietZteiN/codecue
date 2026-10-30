# Discovery linear readouts

Weighted ridge classifiers train only on neutral training cases. Three predeclared positive template-weighting seeds retain all training structures. Normalization uses neutral training data only; regularization is fixed. Hidden and surface features use the same 4,096 dimensions and output-head capacity. Pre-query twins are deduplicated. These are measurement results, not a mechanism claim.

| Features | Block | Site | Development naming | current accuracy | saved accuracy |
|---|---:|---|---|---:|---:|
| hidden | 8 | after_query | informative | 6.34% | 11.50% |
| hidden | 8 | after_query | misleading | 5.86% | 9.55% |
| hidden | 8 | after_query | neutral | 8.20% | 8.98% |
| hidden | 8 | pre_answer | informative | 2.39% | 7.90% |
| hidden | 8 | pre_answer | misleading | 1.74% | 8.33% |
| hidden | 8 | pre_answer | neutral | 4.56% | 6.03% |
| hidden | 8 | pre_query_state | informative | 34.81% | 5.21% |
| hidden | 8 | pre_query_state | misleading | 27.52% | 5.64% |
| hidden | 8 | pre_query_state | neutral | 48.78% | 7.03% |
| hidden | 16 | after_query | informative | 5.56% | 3.60% |
| hidden | 16 | after_query | misleading | 4.21% | 4.51% |
| hidden | 16 | after_query | neutral | 8.55% | 9.11% |
| hidden | 16 | pre_answer | informative | 3.65% | 30.16% |
| hidden | 16 | pre_answer | misleading | 6.47% | 28.60% |
| hidden | 16 | pre_answer | neutral | 14.15% | 38.41% |
| hidden | 16 | pre_query_state | informative | 45.83% | 6.77% |
| hidden | 16 | pre_query_state | misleading | 44.97% | 5.90% |
| hidden | 16 | pre_query_state | neutral | 50.00% | 9.64% |
| hidden | 24 | after_query | informative | 1.65% | 4.51% |
| hidden | 24 | after_query | misleading | 2.17% | 4.73% |
| hidden | 24 | after_query | neutral | 1.04% | 8.98% |
| hidden | 24 | pre_answer | informative | 35.81% | 33.59% |
| hidden | 24 | pre_answer | misleading | 36.59% | 34.51% |
| hidden | 24 | pre_answer | neutral | 41.06% | 44.53% |
| hidden | 24 | pre_query_state | informative | 48.70% | 6.42% |
| hidden | 24 | pre_query_state | misleading | 49.39% | 6.16% |
| hidden | 24 | pre_query_state | neutral | 52.78% | 10.94% |
| hidden | 31 | after_query | informative | 6.73% | 4.25% |
| hidden | 31 | after_query | misleading | 6.34% | 4.21% |
| hidden | 31 | after_query | neutral | 5.30% | 4.17% |
| hidden | 31 | pre_answer | informative | 31.08% | 39.15% |
| hidden | 31 | pre_answer | misleading | 30.60% | 39.67% |
| hidden | 31 | pre_answer | neutral | 35.33% | 47.79% |
| hidden | 31 | pre_query_state | informative | 35.94% | 3.73% |
| hidden | 31 | pre_query_state | misleading | 37.67% | 3.73% |
| hidden | 31 | pre_query_state | neutral | 43.92% | 2.86% |
| surface | -1 | after_query | informative | 4.99% | 1.39% |
| surface | -1 | after_query | misleading | 4.43% | 0.74% |
| surface | -1 | after_query | neutral | 5.03% | 3.95% |
| surface | -1 | pre_answer | informative | 3.95% | 1.26% |
| surface | -1 | pre_answer | misleading | 4.04% | 0.69% |
| surface | -1 | pre_answer | neutral | 4.95% | 3.78% |
| surface | -1 | pre_query_state | informative | 4.17% | 1.82% |
| surface | -1 | pre_query_state | misleading | 3.82% | 1.65% |
| surface | -1 | pre_query_state | neutral | 6.25% | 4.25% |

Full seed-level results include identifier-control accuracy/selectivity, parameter counts, class support and joint accuracy. Identifier-stem controls have few keys; high control accuracy is not evidence of semantic binding. Character-ngram surface features are one capacity-matched comparator, not an exhaustive shortcut audit. Cross-naming failures may reflect harmless representational change. No final outcomes or language-model training were used.
