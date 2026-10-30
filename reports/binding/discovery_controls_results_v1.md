# Discovery-only failure-prediction comparison

Exploratory nested grouped cross-validation on previously consumed discovery data, not M5 confirmation or a frozen unfamiliar-program forecast. No mechanism C, confidence or internal measurement feature is fitted. Repeated fold seeds reuse the same data and are not independent replications. Bootstrap intervals condition on the saved OOF predictions and do not rerun feature collection, model fitting or hyperparameter selection. Raw neutral behavior uses one distinct extra query without its oracle correctness; the scored tier additionally requires the neutral reference oracle. Target response properties and correctness never enter features. Capacity controls add fixed source-feature interactions. Source-oracle tiers additionally receive the program oracle value and its magnitude/sign without any target language-model response. On a source-oracle plus raw-neutral tier, neutral failure is a deterministic comparison of existing information, not a new observation; an increment can reflect the encoding capacity of the fitted function class.

| Checkpoint | Mean-OOF predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| codellama34b | A_input | 0.132585 | 0.408816 | 6144 | 1454 |
| codellama34b | A_interactions | 0.123574 | 0.380577 | 6144 | 1454 |
| codellama34b | A_interactions_neutral_raw | 0.123861 | 0.381025 | 6144 | 1454 |
| codellama34b | A_interactions_neutral_scored | 0.096350 | 0.303570 | 6144 | 1454 |
| codellama34b | A_interactions_oracle | 0.096237 | 0.305361 | 6144 | 1454 |
| codellama34b | A_interactions_oracle_neutral_raw | 0.091608 | 0.293049 | 6144 | 1454 |
| codellama34b | A_interactions_oracle_neutral_scored | 0.087180 | 0.279734 | 6144 | 1454 |
| codellama34b | prior | 0.180960 | 0.548053 | 6144 | 1454 |
| llama31_8b | A_input | 0.039731 | 0.138343 | 6144 | 430 |
| llama31_8b | A_interactions | 0.039673 | 0.137222 | 6144 | 430 |
| llama31_8b | A_interactions_neutral_raw | 0.040037 | 0.138487 | 6144 | 430 |
| llama31_8b | A_interactions_neutral_scored | 0.036599 | 0.129256 | 6144 | 430 |
| llama31_8b | A_interactions_oracle | 0.038100 | 0.133688 | 6144 | 430 |
| llama31_8b | A_interactions_oracle_neutral_raw | 0.037215 | 0.131400 | 6144 | 430 |
| llama31_8b | A_interactions_oracle_neutral_scored | 0.036016 | 0.127793 | 6144 | 430 |
| llama31_8b | prior | 0.065153 | 0.254100 | 6144 | 430 |

All three fixed seeds, every descriptive condition/query/load/original-split cell, fixed calibration bins and paired template-bootstrap comparisons remain in the per-checkpoint reports and machine-readable comparison. No best seed or checkpoint is selected.

- [codellama34b](discovery_controls_codellama34b_v1.md)
- [llama31_8b](discovery_controls_llama31_8b_v1.md)

Neutral raw and scored tiers use at most one cached distinct reference query per target. Oracle-graded neutral failure additionally requires its ground truth; it is not an oracle-free comparator. No original final/extrapolation outcomes or mechanism C features are used.

Source-oracle tiers require the program oracle value even without a neutral query. On source-oracle plus raw-neutral inputs, the scored failure flag is a deterministic comparison, so gains from adding it describe encoding capacity rather than a new observation. All fixed capacity/access contrasts remain reported.
