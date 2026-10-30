# Discovery linear readouts

Weighted ridge classifiers train only on neutral training cases. Three predeclared positive template-weighting seeds retain all training structures. Normalization uses neutral training data only; regularization is fixed. Hidden and surface features use the same 4,096 dimensions and output-head capacity. Pre-query twins are deduplicated. These are measurement results, not a mechanism claim.

| Features | Block | Site | Development naming | queried accuracy |
|---|---:|---|---|---:|
| hidden | 8 | after_query | informative | 4.56% |
| hidden | 8 | after_query | misleading | 2.00% |
| hidden | 8 | after_query | neutral | 6.12% |
| hidden | 8 | pre_answer | informative | 4.51% |
| hidden | 8 | pre_answer | misleading | 4.38% |
| hidden | 8 | pre_answer | neutral | 4.64% |
| hidden | 16 | after_query | informative | 3.78% |
| hidden | 16 | after_query | misleading | 4.38% |
| hidden | 16 | after_query | neutral | 4.77% |
| hidden | 16 | pre_answer | informative | 39.54% |
| hidden | 16 | pre_answer | misleading | 53.65% |
| hidden | 16 | pre_answer | neutral | 58.33% |
| hidden | 24 | after_query | informative | 6.34% |
| hidden | 24 | after_query | misleading | 5.16% |
| hidden | 24 | after_query | neutral | 5.60% |
| hidden | 24 | pre_answer | informative | 82.12% |
| hidden | 24 | pre_answer | misleading | 86.46% |
| hidden | 24 | pre_answer | neutral | 88.89% |
| hidden | 31 | after_query | informative | 6.99% |
| hidden | 31 | after_query | misleading | 7.12% |
| hidden | 31 | after_query | neutral | 6.42% |
| hidden | 31 | pre_answer | informative | 83.72% |
| hidden | 31 | pre_answer | misleading | 87.07% |
| hidden | 31 | pre_answer | neutral | 87.89% |
| surface | -1 | after_query | informative | 3.47% |
| surface | -1 | after_query | misleading | 4.38% |
| surface | -1 | after_query | neutral | 8.98% |
| surface | -1 | pre_answer | informative | 3.34% |
| surface | -1 | pre_answer | misleading | 3.69% |
| surface | -1 | pre_answer | neutral | 9.07% |

Full seed-level results include identifier-control accuracy/selectivity, parameter counts, class support and joint accuracy. Identifier-stem controls have few keys; high control accuracy is not evidence of semantic binding. Character-ngram surface features are one capacity-matched comparator, not an exhaustive shortcut audit. Cross-naming failures may reflect harmless representational change. No final outcomes or language-model training were used.
