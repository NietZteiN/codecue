# Extended conditional penalty path and TRAIN-fold priors

Adaptive discovery on the original archived cohort. All choices use TRAIN structural folds only. Original CV/model files are reused through immutable references with feature/target/weight/ID fingerprints. Fold-local mean, median, computed-family median and fixed zero compete with the ridge path. No new language-model calls or sealed-final access.

| Cell | Ridge alpha | Grid | Overall TRAIN choice | Ridge computed MAE | Overall computed MAE | Overall exact |
|---|---:|---|---|---:|---:|---:|
| source/source1024 | 10000 | interior | ridge(10000) | 5.1647 | 5.1647 | 5.30% |
| source/source2048 | 10000 | interior | ridge(10000) | 5.1790 | 5.1790 | 5.37% |
| llama8b/hidden | 10000 | interior | ridge(10000) | 5.0060 | 5.0060 | 6.42% |
| llama8b/joint | 10000 | interior | ridge(10000) | 4.9863 | 4.9863 | 6.68% |
| llama8b/shuffled_joint | 10000 | interior | ridge(10000) | 5.1703 | 5.1703 | 5.67% |
| codellama34b/hidden | 10000 | interior | ridge(10000) | 4.9726 | 4.9726 | 5.90% |
| codellama34b/joint | 10000 | interior | ridge(10000) | 4.9444 | 4.9444 | 6.00% |
| codellama34b/shuffled_joint | 10000 | interior | ridge(10000) | 5.1830 | 5.1830 | 5.89% |

**New ridge fits: 216; reused fit banks: 240.** Shared priors add 36 four-slot TRAIN statistic estimates; zero is fixed.

## Paired DEV-family contrasts

Differences are selected joint minus comparator computed-value MAE; negative favors joint. Fitting seeds are averaged within families before 2,000 bootstrap replicates. Intervals are descriptive, non-simultaneous and adaptive on an inspected DEV cohort, not confirmation.

| Joint cell | Comparator | Difference | Descriptive 95% interval |
|---|---|---:|---|
| llama8b/joint | source/source1024 | -0.1784 | [-0.2799, -0.0820] |
| llama8b/joint | source/source2048 | -0.1928 | [-0.2923, -0.0950] |
| llama8b/joint | llama8b/hidden | -0.0198 | [-0.0810, 0.0417] |
| llama8b/joint | llama8b/shuffled_joint | -0.1841 | [-0.2899, -0.0783] |
| llama8b/joint | zero | -0.3445 | [-0.5925, -0.1107] |
| llama8b/joint | mean | -0.3486 | [-0.5953, -0.1166] |
| llama8b/joint | median | -0.3445 | [-0.5925, -0.1107] |
| llama8b/joint | computed_median | -0.3445 | [-0.5925, -0.1107] |
| codellama34b/joint | source/source1024 | -0.2203 | [-0.3263, -0.1136] |
| codellama34b/joint | source/source2048 | -0.2346 | [-0.3369, -0.1282] |
| codellama34b/joint | codellama34b/hidden | -0.0281 | [-0.0745, 0.0192] |
| codellama34b/joint | codellama34b/shuffled_joint | -0.2385 | [-0.3492, -0.1243] |
| codellama34b/joint | zero | -0.3863 | [-0.6530, -0.1352] |
| codellama34b/joint | mean | -0.3904 | [-0.6547, -0.1428] |
| codellama34b/joint | median | -0.3863 | [-0.6530, -0.1352] |
| codellama34b/joint | computed_median | -0.3863 | [-0.6530, -0.1352] |

## Penalty continuation versus original selected ridge

| Cell | Computed MAE change | Descriptive 95% interval |
|---|---:|---|
| source/source1024 | 0.0000 | [0.0000, 0.0000] |
| source/source2048 | 0.0000 | [0.0000, 0.0000] |
| llama8b/hidden | 0.0000 | [0.0000, 0.0000] |
| llama8b/joint | 0.0000 | [0.0000, 0.0000] |
| llama8b/shuffled_joint | 0.0000 | [0.0000, 0.0000] |
| codellama34b/hidden | 0.0000 | [0.0000, 0.0000] |
| codellama34b/joint | 0.0000 | [0.0000, 0.0000] |
| codellama34b/shuffled_joint | 0.0000 | [0.0000, 0.0000] |

An interior choice is interior only to this finite grid. Any remaining boundary or constant preference is explicitly reported, not called optimization success. Source2048 matches nominal feature count, not effective rank/inductive bias. Shuffled-hidden conditions select independently. Lower MAE does not imply better exact integer recovery; zero/class priors remain essential. No complete-state, natural causal-use, or cross-protocol representation claim follows.
