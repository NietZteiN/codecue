# Discovery-only failure-prediction comparison

Exploratory nested grouped prediction on already-consumed discovery targets; not mechanism C or unfamiliar-program/final confirmation. All twenty-three existing tiers are retained unchanged. Five new fixed tiers add only five raw scalar properties of one distinct stress-query response to the matching source-context plus BF16 next-token confidence tier. New tiers exclude the six finite-event likelihood scalars. The stress query is an additional observation, with its scientific access cost declared even when responses are cached: one BF16 next-token prefill plus one distinct stress query generating at most 32 tokens. Neutral-query and source-oracle access stay separately declared per context. Stress correctness, original target responses, original correctness and original generated-answer identity are not features; original correctness is only the existing supervised label. Stress validity, raw character/token lengths and parsed signed-integer value/magnitude are features of the additional response without grading it; its parsed response identity is explicitly available. Comparisons with next-token tiers are feature-nested; comparisons with joint finite-event tiers are alternatives with different observations, encoding and access costs. A gain does not identify a pure information increment or causal binding mechanism. Repeated partition seeds reuse the same structures, and bootstrap intervals condition on saved OOF probabilities without refitting or multiplicity correction. The five new stress tiers allow 1000 Newton iterations with the original objective, initialization, normalization, backtracking and 1e-8 stopping tolerance. All twenty-three parent tiers retain their original 100-iteration allowance.

| Checkpoint | Mean-OOF predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| codellama34b | A_input | 0.132585 | 0.408816 | 6144 | 1454 |
| codellama34b | A_interactions | 0.123574 | 0.380577 | 6144 | 1454 |
| codellama34b | A_interactions_neutral_raw | 0.123861 | 0.381025 | 6144 | 1454 |
| codellama34b | A_interactions_neutral_scored | 0.096350 | 0.303570 | 6144 | 1454 |
| codellama34b | A_interactions_oracle | 0.096237 | 0.305361 | 6144 | 1454 |
| codellama34b | A_interactions_oracle_neutral_raw | 0.091608 | 0.293049 | 6144 | 1454 |
| codellama34b | A_interactions_oracle_neutral_scored | 0.087180 | 0.279734 | 6144 | 1454 |
| codellama34b | B_event_input | 0.121691 | 0.370051 | 6144 | 1454 |
| codellama34b | B_event_interactions | 0.116667 | 0.357619 | 6144 | 1454 |
| codellama34b | B_event_interactions_neutral_raw | 0.115220 | 0.354209 | 6144 | 1454 |
| codellama34b | B_event_interactions_oracle_neutral_raw | 0.086154 | 0.278165 | 6144 | 1454 |
| codellama34b | B_event_interactions_oracle_neutral_scored | 0.081680 | 0.265397 | 6144 | 1454 |
| codellama34b | B_input_confidence | 0.125365 | 0.386596 | 6144 | 1454 |
| codellama34b | B_interactions_confidence | 0.116641 | 0.361757 | 6144 | 1454 |
| codellama34b | B_interactions_neutral_raw_confidence | 0.115091 | 0.357863 | 6144 | 1454 |
| codellama34b | B_interactions_oracle_neutral_raw_confidence | 0.087942 | 0.283594 | 6144 | 1454 |
| codellama34b | B_interactions_oracle_neutral_scored_confidence | 0.083800 | 0.272258 | 6144 | 1454 |
| codellama34b | B_joint_input | 0.117984 | 0.359848 | 6144 | 1454 |
| codellama34b | B_joint_interactions | 0.113499 | 0.348948 | 6144 | 1454 |
| codellama34b | B_joint_interactions_neutral_raw | 0.112318 | 0.346208 | 6144 | 1454 |
| codellama34b | B_joint_interactions_oracle_neutral_raw | 0.086017 | 0.277467 | 6144 | 1454 |
| codellama34b | B_joint_interactions_oracle_neutral_scored | 0.081426 | 0.265466 | 6144 | 1454 |
| codellama34b | B_stress_input | 0.122131 | 0.375329 | 6144 | 1454 |
| codellama34b | B_stress_interactions | 0.115368 | 0.355816 | 6144 | 1454 |
| codellama34b | B_stress_interactions_neutral_raw | 0.115093 | 0.355540 | 6144 | 1454 |
| codellama34b | B_stress_interactions_oracle_neutral_raw | 0.087080 | 0.279280 | 6144 | 1454 |
| codellama34b | B_stress_interactions_oracle_neutral_scored | 0.082525 | 0.265984 | 6144 | 1454 |
| codellama34b | prior | 0.180960 | 0.548053 | 6144 | 1454 |
| llama31_8b | A_input | 0.039731 | 0.138343 | 6144 | 430 |
| llama31_8b | A_interactions | 0.039673 | 0.137222 | 6144 | 430 |
| llama31_8b | A_interactions_neutral_raw | 0.040037 | 0.138487 | 6144 | 430 |
| llama31_8b | A_interactions_neutral_scored | 0.036599 | 0.129256 | 6144 | 430 |
| llama31_8b | A_interactions_oracle | 0.038100 | 0.133688 | 6144 | 430 |
| llama31_8b | A_interactions_oracle_neutral_raw | 0.037215 | 0.131400 | 6144 | 430 |
| llama31_8b | A_interactions_oracle_neutral_scored | 0.036016 | 0.127793 | 6144 | 430 |
| llama31_8b | B_event_input | 0.039681 | 0.136367 | 6144 | 430 |
| llama31_8b | B_event_interactions | 0.039524 | 0.134908 | 6144 | 430 |
| llama31_8b | B_event_interactions_neutral_raw | 0.039940 | 0.137111 | 6144 | 430 |
| llama31_8b | B_event_interactions_oracle_neutral_raw | 0.035287 | 0.126859 | 6144 | 430 |
| llama31_8b | B_event_interactions_oracle_neutral_scored | 0.034585 | 0.123859 | 6144 | 430 |
| llama31_8b | B_input_confidence | 0.039576 | 0.134655 | 6144 | 430 |
| llama31_8b | B_interactions_confidence | 0.039430 | 0.133126 | 6144 | 430 |
| llama31_8b | B_interactions_neutral_raw_confidence | 0.039596 | 0.133796 | 6144 | 430 |
| llama31_8b | B_interactions_oracle_neutral_raw_confidence | 0.035738 | 0.124886 | 6144 | 430 |
| llama31_8b | B_interactions_oracle_neutral_scored_confidence | 0.034994 | 0.121870 | 6144 | 430 |
| llama31_8b | B_joint_input | 0.039731 | 0.134126 | 6144 | 430 |
| llama31_8b | B_joint_interactions | 0.039503 | 0.132467 | 6144 | 430 |
| llama31_8b | B_joint_interactions_neutral_raw | 0.039623 | 0.133305 | 6144 | 430 |
| llama31_8b | B_joint_interactions_oracle_neutral_raw | 0.034883 | 0.122550 | 6144 | 430 |
| llama31_8b | B_joint_interactions_oracle_neutral_scored | 0.034253 | 0.119813 | 6144 | 430 |
| llama31_8b | B_stress_input | 0.039651 | 0.134431 | 6144 | 430 |
| llama31_8b | B_stress_interactions | 0.039446 | 0.132791 | 6144 | 430 |
| llama31_8b | B_stress_interactions_neutral_raw | 0.039710 | 0.134196 | 6144 | 430 |
| llama31_8b | B_stress_interactions_oracle_neutral_raw | 0.034288 | 0.122141 | 6144 | 430 |
| llama31_8b | B_stress_interactions_oracle_neutral_scored | 0.033648 | 0.118404 | 6144 | 430 |
| llama31_8b | prior | 0.065153 | 0.254100 | 6144 | 430 |

All three fixed seeds, every descriptive condition/query/load/original-split cell, fixed calibration bins and paired template-bootstrap comparisons remain in the per-checkpoint reports and machine-readable comparison. No best seed or checkpoint is selected.

- [codellama34b](stress_prediction_codellama34b_v2.md)
- [llama31_8b](stress_prediction_llama31_8b_v2.md)

Neutral raw and scored tiers use at most one cached distinct reference query per target. Oracle-graded neutral failure additionally requires its ground truth; it is not an oracle-free comparator. No original final/extrapolation outcomes or mechanism C features are used.

Source-oracle tiers require the program oracle value even without a neutral query. On source-oracle plus raw-neutral inputs, the scored failure flag is a deterministic comparison, so gains from adding it describe encoding capacity rather than a new observation. All fixed capacity/access contrasts remain reported.
