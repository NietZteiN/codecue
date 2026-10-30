# Discovery-only failure-prediction comparison

Exploratory nested grouped cross-validation on previously consumed discovery data, not M5 confirmation or a frozen unfamiliar-program forecast. No mechanism C, confidence or internal measurement feature is fitted. Repeated fold seeds reuse the same data and are not independent replications. Bootstrap intervals condition on the saved OOF predictions and do not rerun feature collection, model fitting or hyperparameter selection. Raw neutral behavior uses one distinct extra query without its oracle correctness; the scored tier additionally requires the neutral reference oracle. Target response properties and correctness never enter features.

| Checkpoint | Mean-OOF predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| codellama34b | A_input | 0.132585 | 0.408816 | 6144 | 1454 |
| codellama34b | A_neutral_raw | 0.132397 | 0.408188 | 6144 | 1454 |
| codellama34b | A_neutral_scored | 0.101568 | 0.316216 | 6144 | 1454 |
| codellama34b | prior | 0.180960 | 0.548053 | 6144 | 1454 |
| llama31_8b | A_input | 0.039731 | 0.138343 | 6144 | 430 |
| llama31_8b | A_neutral_raw | 0.040188 | 0.139721 | 6144 | 430 |
| llama31_8b | A_neutral_scored | 0.036727 | 0.130138 | 6144 | 430 |
| llama31_8b | prior | 0.065153 | 0.254100 | 6144 | 430 |

All three fixed seeds, every descriptive condition/query/load/original-split cell, fixed calibration bins and paired template-bootstrap comparisons remain in the per-checkpoint reports and machine-readable comparison. No best seed or checkpoint is selected.

- [codellama34b](discovery_prediction_codellama34b_v1.md)
- [llama31_8b](discovery_prediction_llama31_8b_v1.md)

Neutral raw and scored tiers use at most one cached distinct reference query per target. Oracle-graded neutral failure additionally requires its ground truth; it is not an oracle-free comparator. No original final/extrapolation outcomes or mechanism C features are used.
