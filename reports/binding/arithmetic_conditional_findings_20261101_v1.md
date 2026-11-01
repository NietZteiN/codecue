# Conditional numeric prediction beyond source features

Adaptive discovery on archived single-variable query states; no new model calls. All four scalar heads use TRAIN-only normalization and structural-fold selection on computed-value MAE. A conditional gain is relative to these finite source features/readout classes: the complete source determines the answer. It does not establish additional information beyond the program, native model execution or causal use.

| Features | Width | Computed MAE | Computed exact | Untouched MAE | All-slot MAE |
|---|---:|---:|---:|---:|---:|
| source/source1024 | 1024 | 5.1647 | 5.30% | 2.4345 | 4.2001 |
| source/source2048 | 2048 | 5.1790 | 5.37% | 2.3948 | 4.1935 |
| llama8b/hidden | 1024 | 5.0060 | 6.42% | 2.5189 | 4.1649 |
| llama8b/joint | 2048 | 4.9863 | 6.68% | 2.4070 | 4.0946 |
| llama8b/shuffled_joint | 2048 | 5.1703 | 5.67% | 2.5320 | 4.2444 |
| codellama34b/hidden | 1024 | 4.9726 | 5.90% | 2.3768 | 4.0908 |
| codellama34b/joint | 2048 | 4.9444 | 6.00% | 2.2869 | 4.0283 |
| codellama34b/shuffled_joint | 2048 | 5.1830 | 5.89% | 2.5122 | 4.2438 |

## Paired family contrasts

Joint minus comparator computed-value MAE; negative favors the joint predictor. Seeds are averaged inside families before 2,000 bootstrap replicates. Intervals are descriptive, non-simultaneous and based on inspected DEV. Three fitting seeds are not three independent datasets.

| Model | Comparator | MAE difference | Descriptive 95% interval |
|---|---|---:|---|
| llama8b | source/source1024 | -0.1784 | [-0.2799, -0.0820] |
| llama8b | source/source2048 | -0.1928 | [-0.2923, -0.0950] |
| llama8b | llama8b/hidden | -0.0198 | [-0.0810, 0.0417] |
| llama8b | llama8b/shuffled_joint | -0.1841 | [-0.2899, -0.0783] |
| codellama34b | source/source1024 | -0.2203 | [-0.3263, -0.1136] |
| codellama34b | source/source2048 | -0.2346 | [-0.3369, -0.1282] |
| codellama34b | codellama34b/hidden | -0.0281 | [-0.0745, 0.0192] |
| codellama34b | codellama34b/shuffled_joint | -0.2385 | [-0.3492, -0.1243] |

Source1024 plus hidden1024 has2,048 nominal features. Source2048 controls nominal feature count, not identical inductive bias or effective rank. Hidden-only1024 is also independently selected. Shuffled-joint controls move the entire hidden block between structural families within each fold/split, preserving source/target alignment and numeric/lexical relatives. Their coefficients and alphas are fitted separately. Fixed-coefficient TRAIN-mean block ablations are saved as probe diagnostics, not interventions in the language model. The old pure global-state results remain unchanged; this edition changes the inputs and TRAIN selection objective. No layer, wording or feature-width search is performed here. No novel-family confirmation or sealed-final access.
