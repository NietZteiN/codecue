# Distinct ungraded stress-query prediction controls

Exploratory nested grouped prediction on already-consumed discovery targets; not mechanism C or unfamiliar-program/final confirmation. All twenty-three existing tiers are retained unchanged. Five new fixed tiers add only five raw scalar properties of one distinct stress-query response to the matching source-context plus BF16 next-token confidence tier. New tiers exclude the six finite-event likelihood scalars. The stress query is an additional observation, with its scientific access cost declared even when responses are cached: one BF16 next-token prefill plus one distinct stress query generating at most 32 tokens. Neutral-query and source-oracle access stay separately declared per context. Stress correctness, original target responses, original correctness and original generated-answer identity are not features; original correctness is only the existing supervised label. Stress validity, raw character/token lengths and parsed signed-integer value/magnitude are features of the additional response without grading it; its parsed response identity is explicitly available. Comparisons with next-token tiers are feature-nested; comparisons with joint finite-event tiers are alternatives with different observations, encoding and access costs. A gain does not identify a pure information increment or causal binding mechanism. Repeated partition seeds reuse the same structures, and bootstrap intervals condition on saved OOF probabilities without refitting or multiplicity correction. The five new stress tiers allow 1000 Newton iterations with the original objective, initialization, normalization, backtracking and 1e-8 stopping tolerance. All twenty-three parent tiers retain their original 100-iteration allowance.

| Checkpoint | Contrast | Left Brier | Stress Brier | Improvement [conditional 95%] | Left log loss | Stress log loss |
|---|---|---:|---:|---|---:|---:|
| codellama34b | B_input_confidence → B_stress_input | 0.125365 | 0.122131 | +0.003233 [+0.001398, +0.005083] | 0.386596 | 0.375329 |
| codellama34b | B_interactions_confidence → B_stress_interactions | 0.116641 | 0.115368 | +0.001273 [-0.000948, +0.003224] | 0.361757 | 0.355816 |
| codellama34b | B_interactions_neutral_raw_confidence → B_stress_interactions_neutral_raw | 0.115091 | 0.115093 | -0.000002 [-0.001693, +0.001435] | 0.357863 | 0.355540 |
| codellama34b | B_interactions_oracle_neutral_raw_confidence → B_stress_interactions_oracle_neutral_raw | 0.087942 | 0.087080 | +0.000862 [-0.001142, +0.002452] | 0.283594 | 0.279280 |
| codellama34b | B_interactions_oracle_neutral_scored_confidence → B_stress_interactions_oracle_neutral_scored | 0.083800 | 0.082525 | +0.001275 [-0.000341, +0.002760] | 0.272258 | 0.265984 |
| codellama34b | B_joint_input → B_stress_input | 0.117984 | 0.122131 | -0.004147 [-0.010102, +0.001370] | 0.359848 | 0.375329 |
| codellama34b | B_joint_interactions → B_stress_interactions | 0.113499 | 0.115368 | -0.001869 [-0.005338, +0.001387] | 0.348948 | 0.355816 |
| codellama34b | B_joint_interactions_neutral_raw → B_stress_interactions_neutral_raw | 0.112318 | 0.115093 | -0.002775 [-0.005959, +0.000246] | 0.346208 | 0.355540 |
| codellama34b | B_joint_interactions_oracle_neutral_raw → B_stress_interactions_oracle_neutral_raw | 0.086017 | 0.087080 | -0.001063 [-0.003696, +0.001445] | 0.277467 | 0.279280 |
| codellama34b | B_joint_interactions_oracle_neutral_scored → B_stress_interactions_oracle_neutral_scored | 0.081426 | 0.082525 | -0.001098 [-0.003683, +0.001363] | 0.265466 | 0.265984 |
| codellama34b | A_input → B_stress_input | 0.132585 | 0.122131 | +0.010453 [+0.004978, +0.016090] | 0.408816 | 0.375329 |
| codellama34b | A_interactions → B_stress_interactions | 0.123574 | 0.115368 | +0.008206 [+0.003279, +0.014084] | 0.380577 | 0.355816 |
| codellama34b | A_interactions_neutral_raw → B_stress_interactions_neutral_raw | 0.123861 | 0.115093 | +0.008768 [+0.003619, +0.014632] | 0.381025 | 0.355540 |
| codellama34b | A_interactions_oracle_neutral_raw → B_stress_interactions_oracle_neutral_raw | 0.091608 | 0.087080 | +0.004528 [+0.001500, +0.007343] | 0.293049 | 0.279280 |
| codellama34b | A_interactions_oracle_neutral_scored → B_stress_interactions_oracle_neutral_scored | 0.087180 | 0.082525 | +0.004655 [+0.002332, +0.006811] | 0.279734 | 0.265984 |
| llama31_8b | B_input_confidence → B_stress_input | 0.039576 | 0.039651 | -0.000075 [-0.000538, +0.000351] | 0.134655 | 0.134431 |
| llama31_8b | B_interactions_confidence → B_stress_interactions | 0.039430 | 0.039446 | -0.000016 [-0.000448, +0.000366] | 0.133126 | 0.132791 |
| llama31_8b | B_interactions_neutral_raw_confidence → B_stress_interactions_neutral_raw | 0.039596 | 0.039710 | -0.000114 [-0.001066, +0.000580] | 0.133796 | 0.134196 |
| llama31_8b | B_interactions_oracle_neutral_raw_confidence → B_stress_interactions_oracle_neutral_raw | 0.035738 | 0.034288 | +0.001450 [+0.000145, +0.002599] | 0.124886 | 0.122141 |
| llama31_8b | B_interactions_oracle_neutral_scored_confidence → B_stress_interactions_oracle_neutral_scored | 0.034994 | 0.033648 | +0.001346 [-0.000060, +0.002560] | 0.121870 | 0.118404 |
| llama31_8b | B_joint_input → B_stress_input | 0.039731 | 0.039651 | +0.000080 [-0.000569, +0.000758] | 0.134126 | 0.134431 |
| llama31_8b | B_joint_interactions → B_stress_interactions | 0.039503 | 0.039446 | +0.000057 [-0.000572, +0.000682] | 0.132467 | 0.132791 |
| llama31_8b | B_joint_interactions_neutral_raw → B_stress_interactions_neutral_raw | 0.039623 | 0.039710 | -0.000086 [-0.000883, +0.000608] | 0.133305 | 0.134196 |
| llama31_8b | B_joint_interactions_oracle_neutral_raw → B_stress_interactions_oracle_neutral_raw | 0.034883 | 0.034288 | +0.000594 [-0.000762, +0.001783] | 0.122550 | 0.122141 |
| llama31_8b | B_joint_interactions_oracle_neutral_scored → B_stress_interactions_oracle_neutral_scored | 0.034253 | 0.033648 | +0.000605 [-0.000765, +0.001870] | 0.119813 | 0.118404 |
| llama31_8b | A_input → B_stress_input | 0.039731 | 0.039651 | +0.000080 [-0.000921, +0.001162] | 0.138343 | 0.134431 |
| llama31_8b | A_interactions → B_stress_interactions | 0.039673 | 0.039446 | +0.000227 [-0.000693, +0.001241] | 0.137222 | 0.132791 |
| llama31_8b | A_interactions_neutral_raw → B_stress_interactions_neutral_raw | 0.040037 | 0.039710 | +0.000327 [-0.000945, +0.001456] | 0.138487 | 0.134196 |
| llama31_8b | A_interactions_oracle_neutral_raw → B_stress_interactions_oracle_neutral_raw | 0.037215 | 0.034288 | +0.002927 [+0.000950, +0.004758] | 0.131400 | 0.122141 |
| llama31_8b | A_interactions_oracle_neutral_scored → B_stress_interactions_oracle_neutral_scored | 0.036016 | 0.033648 | +0.002368 [+0.000394, +0.004127] | 0.127793 | 0.118404 |

All 847,872 parent-tier OOF probability values reproduce exactly, as do every saved parent fit, normalizer, penalty, inner curve, group assignment and fallback record.

All 28 tiers and 70 contrasts, fixed seeds, calibration bins and descriptive cells remain in the full comparison and per-checkpoint reports. Original target outcomes were already consumed discovery labels; no untouched final score or mechanism C was fitted.
