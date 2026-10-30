# Discovery failure-prediction decision

Completed empirical predictive baselines on **12,288 previously observed target examples** across both cached checkpoints. This is nested structural-group cross-validation within consumed discovery data, not frozen final validation. All collection, fitting, comparison and figure jobs completed successfully.

Input features improve prediction over the fitted training-prior baseline. Raw neutral-query properties add no clear Brier-score improvement in either checkpoint. Scoring that distinct neutral query against its oracle adds predictive information, with the stronger oracle-access contract explicitly separated. These results establish exploratory baselines, not a mechanism C model or a causal explanation.

## Complete mean-OOF ensemble scores

Lower Brier/log loss is better within each checkpoint. Failure prevalence differs between checkpoints, so their absolute scores do not rank the language models. The ensemble averages the three predeclared partition seeds; no favorable seed is selected.

| Checkpoint | Targets | Failures | Predictor | Brier | Log loss |
|---|---:|---:|---|---:|---:|
| Llama 3.1 8B | 6144 | 430 | prior | 0.065153 | 0.254100 |
| Llama 3.1 8B | 6144 | 430 | A_input | 0.039731 | 0.138343 |
| Llama 3.1 8B | 6144 | 430 | A_neutral_raw | 0.040188 | 0.139721 |
| Llama 3.1 8B | 6144 | 430 | A_neutral_scored | 0.036727 | 0.130138 |
| CodeLlama 34B | 6144 | 1454 | prior | 0.180960 | 0.548053 |
| CodeLlama 34B | 6144 | 1454 | A_input | 0.132585 | 0.408816 |
| CodeLlama 34B | 6144 | 1454 | A_neutral_raw | 0.132397 | 0.408188 |
| CodeLlama 34B | 6144 | 1454 | A_neutral_scored | 0.101568 | 0.316216 |

![Discovery baseline scores](discovery_prediction_results_v2.svg)

## Incremental neutral-query information

Positive improvement is loss(left) minus loss(right). Intervals resample whole structural components and condition on the saved OOF probabilities; they do not refit the training procedure and are unadjusted for multiplicity.

| Checkpoint | Left | Right | Brier improvement [95%] | Log-loss improvement [95%] |
|---|---|---|---|---|
| Llama 3.1 8B | A_input | A_neutral_raw | -0.000458 [-0.001061, +0.000084] | -0.001378 [-0.002739, -0.000065] |
| Llama 3.1 8B | A_input | A_neutral_scored | +0.003003 [+0.000565, +0.005517] | +0.008204 [+0.002640, +0.013660] |
| Llama 3.1 8B | A_neutral_raw | A_neutral_scored | +0.003461 [+0.001071, +0.006029] | +0.009583 [+0.003781, +0.015363] |
| CodeLlama 34B | A_input | A_neutral_raw | +0.000188 [-0.001003, +0.001409] | +0.000628 [-0.002797, +0.003862] |
| CodeLlama 34B | A_input | A_neutral_scored | +0.031017 [+0.024468, +0.037954] | +0.092600 [+0.074598, +0.110826] |
| CodeLlama 34B | A_neutral_raw | A_neutral_scored | +0.030829 [+0.023979, +0.037513] | +0.091972 [+0.074045, +0.109148] |

## Information, grouping and costs

Targets are informative/misleading version-family programs. Each is paired with a distinct neutral query using base, updates, tail placement, query role, ownership status and lexical realization. Ownership-only records are excluded prospectively because they have no transformed counterpart. All numeric, naming, lexical and query relatives remain in the same structural component.

The input tier has 19 fixed source-only features. Five raw-reference features use the neutral answer, validity and response lengths without checking its correctness. The scored tier adds one reference-failure indicator and requires the reference oracle, which shares the target semantic answer. Target model answers, validity and correctness never enter feature vectors. No confidence, activation or mechanism-derived feature is present.

Maximum prediction-time access is one extra neutral query per target. Each checkpoint uses 3,072 distinct cached references for 6,144 targets (0.5 amortized queries per target in this paired cohort). This analysis made zero new language-model queries. The scored tier additionally needs reference ground truth and is not an oracle-free deployment comparator.

## Limits and next work

All 24 components were previously observed discovery data. The new folds combine original training and development components; they do not preserve the original identifier-vocabulary boundary. Source features are fixed additive logistic inputs, not an exhaustive class of input-only predictors. Fixed interactions or more flexible input baselines, and oracle-access-matched controls, remain useful before interpreting additional information from costly measurements.

Repeated partition seeds are sensitivity analyses on the same data, not independent scientific replications. Conditional OOF bootstrap intervals omit feature-selection and refitting uncertainty. No supported causal account, empirical mechanism C, prospectively frozen final forecast or original final/extrapolation score is produced. The earlier arithmetic reliability failures remain unchanged.

The completed result advances empirical discovery A/behavioral baselines. It does not complete M5. Remaining work includes appropriate confidence measurements, an evidence-supported internal measurement account, capacity/access controls and genuinely frozen unfamiliar-program validation.

## Software and reproduction

The full regression suite passed **385 tests**. The fixed analysis performed **2,268 regularized logistic fits** and 216 smoothed training-prior estimates, including all inner candidate fits and outer refits; no single-class fallback was needed. Every fold identity, inner curve, normalizer, weight, OOF probability and calibration bin is retained. These statistical fits do not train a language-model checkpoint.

[Full comparison and per-checkpoint reports](discovery_prediction_results_v1.md) · [Fixed analysis plan](discovery_prediction_plan.md) · [Automatic log](experiment_log.md)
