# Discovery-only failure-prediction comparison

Exploratory grouped prediction on previously consumed discovery structures, not mechanism C or unfamiliar-program/final confirmation. All thirteen existing source, neutral, oracle and BF16 next-token confidence tiers are retained unchanged. Five event alternatives use only six scalar summaries of declared finite numeral-plus-EOS token events; no old one-token confidence scalars are added to those alternatives. Comparing B_event with B_confidence compares alternative measurement bundles, not a nested information-only increment: event definition, FP32/no-TF32 versus BF16 numeric execution, checkpoint-specific tokenization rules, encoding and fitted function-class effects can all matter. A gain cannot isolate full-answer scoring from those differences. Event likelihood access is stronger than one-token sign/format confidence: one FP32 prefix prefill plus all 33 candidate numerals and the declared EOS union, spanning 35 prefix states per target. KV reuse does not remove this scientific access cost. Finite-event support mass is separate from support-conditional summaries; other textual answers/tokenizations are outside that support. Source-oracle and scored/raw neutral access remain separately declared. No generated token, token/candidate identity or target response/correctness is a feature. Correctness is only the existing supervised label. Repeated partition seeds are not independent replications; bootstrap intervals condition on saved OOF predictions without refits or multiplicity correction.

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
| llama31_8b | prior | 0.065153 | 0.254100 | 6144 | 430 |

All three fixed seeds, every descriptive condition/query/load/original-split cell, fixed calibration bins and paired template-bootstrap comparisons remain in the per-checkpoint reports and machine-readable comparison. No best seed or checkpoint is selected.

- [codellama34b](candidate_prediction_codellama34b_v1.md)
- [llama31_8b](candidate_prediction_llama31_8b_v1.md)

Neutral raw and scored tiers use at most one cached distinct reference query per target. Oracle-graded neutral failure additionally requires its ground truth; it is not an oracle-free comparator. No original final/extrapolation outcomes or mechanism C features are used.

Source-oracle tiers require the program oracle value even without a neutral query. On source-oracle plus raw-neutral inputs, the scored failure flag is a deterministic comparison, so gains from adding it describe encoding capacity rather than a new observation. All fixed capacity/access contrasts remain reported.
