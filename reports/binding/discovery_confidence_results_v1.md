# Discovery-only failure-prediction comparison

Exploratory nested grouped cross-validation on previously consumed discovery data. Scalar next-token confidence is allowed in explicitly labelled B tiers; no mechanism C or unfamiliar-program/final confirmation is claimed. The new Transformers BF16 prefill measurement backend differs from the original vLLM outcome backend. Confidence is next-token sign/format confidence, not complete integer-answer confidence. Its scientific access cost is one target prefill per target, even when cached: no target response, generated token, target correctness or token identity is a feature. Raw neutral tiers separately use one distinct reference query; scored tiers also require reference correctness; source-oracle tiers separately receive the source oracle value. Adding neutral correctness to source-oracle plus raw-neutral features adds an encoding of existing information, not a new observation. Repeated partition seeds reuse the same targets, not independent replications. Template bootstrap intervals condition on saved OOF probabilities without refitting or multiplicity adjustment.

| Checkpoint | Mean-OOF predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| codellama34b | A_input | 0.132585 | 0.408816 | 6144 | 1454 |
| codellama34b | A_interactions | 0.123574 | 0.380577 | 6144 | 1454 |
| codellama34b | A_interactions_neutral_raw | 0.123861 | 0.381025 | 6144 | 1454 |
| codellama34b | A_interactions_neutral_scored | 0.096350 | 0.303570 | 6144 | 1454 |
| codellama34b | A_interactions_oracle | 0.096237 | 0.305361 | 6144 | 1454 |
| codellama34b | A_interactions_oracle_neutral_raw | 0.091608 | 0.293049 | 6144 | 1454 |
| codellama34b | A_interactions_oracle_neutral_scored | 0.087180 | 0.279734 | 6144 | 1454 |
| codellama34b | B_input_confidence | 0.125365 | 0.386596 | 6144 | 1454 |
| codellama34b | B_interactions_confidence | 0.116641 | 0.361757 | 6144 | 1454 |
| codellama34b | B_interactions_neutral_raw_confidence | 0.115091 | 0.357863 | 6144 | 1454 |
| codellama34b | B_interactions_oracle_neutral_raw_confidence | 0.087942 | 0.283594 | 6144 | 1454 |
| codellama34b | B_interactions_oracle_neutral_scored_confidence | 0.083800 | 0.272258 | 6144 | 1454 |
| codellama34b | prior | 0.180960 | 0.548053 | 6144 | 1454 |
| llama31_8b | A_input | 0.039731 | 0.138343 | 6144 | 430 |
| llama31_8b | A_interactions | 0.039673 | 0.137222 | 6144 | 430 |
| llama31_8b | A_interactions_neutral_raw | 0.040037 | 0.138487 | 6144 | 430 |
| llama31_8b | A_interactions_neutral_scored | 0.036599 | 0.129256 | 6144 | 430 |
| llama31_8b | A_interactions_oracle | 0.038100 | 0.133688 | 6144 | 430 |
| llama31_8b | A_interactions_oracle_neutral_raw | 0.037215 | 0.131400 | 6144 | 430 |
| llama31_8b | A_interactions_oracle_neutral_scored | 0.036016 | 0.127793 | 6144 | 430 |
| llama31_8b | B_input_confidence | 0.039576 | 0.134655 | 6144 | 430 |
| llama31_8b | B_interactions_confidence | 0.039430 | 0.133126 | 6144 | 430 |
| llama31_8b | B_interactions_neutral_raw_confidence | 0.039596 | 0.133796 | 6144 | 430 |
| llama31_8b | B_interactions_oracle_neutral_raw_confidence | 0.035738 | 0.124886 | 6144 | 430 |
| llama31_8b | B_interactions_oracle_neutral_scored_confidence | 0.034994 | 0.121870 | 6144 | 430 |
| llama31_8b | prior | 0.065153 | 0.254100 | 6144 | 430 |

All three fixed seeds, every descriptive condition/query/load/original-split cell, fixed calibration bins and paired template-bootstrap comparisons remain in the per-checkpoint reports and machine-readable comparison. No best seed or checkpoint is selected.

- [codellama34b](discovery_confidence_codellama34b_v1.md)
- [llama31_8b](discovery_confidence_llama31_8b_v1.md)

Neutral raw and scored tiers use at most one cached distinct reference query per target. Oracle-graded neutral failure additionally requires its ground truth; it is not an oracle-free comparator. No original final/extrapolation outcomes or mechanism C features are used.

Source-oracle tiers require the program oracle value even without a neutral query. On source-oracle plus raw-neutral inputs, the scored failure flag is a deterministic comparison, so gains from adding it describe encoding capacity rather than a new observation. All fixed capacity/access contrasts remain reported.
