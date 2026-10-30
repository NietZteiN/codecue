# Joint next-token and finite-event confidence controls

Exploratory nested grouped prediction on already-consumed discovery targets; not mechanism C or unfamiliar-program/final confirmation. All eighteen existing source, neutral, oracle, next-token confidence and finite-event alternative tiers are retained unchanged. Five fixed joint tiers combine the four existing BF16 next-token scalars and six existing FP32/no-TF32 finite numeral-plus-EOS scalars in each declared context. Those tiers are feature-nested in both corresponding confidence alternatives. No new language-model query is performed; scientific access remains the union of the two measurement contracts: one BF16 next-token prefill plus one FP32 event prefix prefill and 33 numerals with the declared EOS union across 35 prefix states. Saved caches do not remove that scientific cost. A predictive increment can reflect encoding, fitted function class and numerical execution, rather than a pure information or causal mechanism effect. Finite-event support excludes other textual answers and is not task-correctness probability. Source-oracle, raw-neutral and oracle-scored neutral access stay separately declared. No candidate/token identity, generated answer, target response or correctness is a feature; correctness is only the existing supervised label. Repeated partition seeds reuse the same structural groups. Bootstrap intervals condition on saved OOF probabilities without refitting or multiplicity adjustment.

| Checkpoint | Contrast | Left Brier | Joint Brier | Improvement [conditional 95%] | Left log loss | Joint log loss |
|---|---|---:|---:|---|---:|---:|
| codellama34b | B_input_confidence → B_joint_input | 0.125365 | 0.117984 | +0.007381 [+0.002367, +0.012872] | 0.386596 | 0.359848 |
| codellama34b | B_interactions_confidence → B_joint_interactions | 0.116641 | 0.113499 | +0.003142 [+0.000158, +0.006277] | 0.361757 | 0.348948 |
| codellama34b | B_interactions_neutral_raw_confidence → B_joint_interactions_neutral_raw | 0.115091 | 0.112318 | +0.002773 [-0.000012, +0.005795] | 0.357863 | 0.346208 |
| codellama34b | B_interactions_oracle_neutral_raw_confidence → B_joint_interactions_oracle_neutral_raw | 0.087942 | 0.086017 | +0.001925 [-0.000915, +0.004543] | 0.283594 | 0.277467 |
| codellama34b | B_interactions_oracle_neutral_scored_confidence → B_joint_interactions_oracle_neutral_scored | 0.083800 | 0.081426 | +0.002373 [-0.000121, +0.004862] | 0.272258 | 0.265466 |
| codellama34b | B_event_input → B_joint_input | 0.121691 | 0.117984 | +0.003707 [+0.001165, +0.006458] | 0.370051 | 0.359848 |
| codellama34b | B_event_interactions → B_joint_interactions | 0.116667 | 0.113499 | +0.003168 [+0.000907, +0.005784] | 0.357619 | 0.348948 |
| codellama34b | B_event_interactions_neutral_raw → B_joint_interactions_neutral_raw | 0.115220 | 0.112318 | +0.002902 [+0.000680, +0.005446] | 0.354209 | 0.346208 |
| codellama34b | B_event_interactions_oracle_neutral_raw → B_joint_interactions_oracle_neutral_raw | 0.086154 | 0.086017 | +0.000138 [-0.001240, +0.001483] | 0.278165 | 0.277467 |
| codellama34b | B_event_interactions_oracle_neutral_scored → B_joint_interactions_oracle_neutral_scored | 0.081680 | 0.081426 | +0.000254 [-0.001031, +0.001512] | 0.265397 | 0.265466 |
| codellama34b | A_input → B_joint_input | 0.132585 | 0.117984 | +0.014601 [+0.007108, +0.022087] | 0.408816 | 0.359848 |
| codellama34b | A_interactions → B_joint_interactions | 0.123574 | 0.113499 | +0.010075 [+0.004233, +0.016426] | 0.380577 | 0.348948 |
| codellama34b | A_interactions_neutral_raw → B_joint_interactions_neutral_raw | 0.123861 | 0.112318 | +0.011543 [+0.005578, +0.018083] | 0.381025 | 0.346208 |
| codellama34b | A_interactions_oracle_neutral_raw → B_joint_interactions_oracle_neutral_raw | 0.091608 | 0.086017 | +0.005591 [+0.002125, +0.008588] | 0.293049 | 0.277467 |
| codellama34b | A_interactions_oracle_neutral_scored → B_joint_interactions_oracle_neutral_scored | 0.087180 | 0.081426 | +0.005753 [+0.003064, +0.008218] | 0.279734 | 0.265466 |
| llama31_8b | B_input_confidence → B_joint_input | 0.039576 | 0.039731 | -0.000155 [-0.000683, +0.000375] | 0.134655 | 0.134126 |
| llama31_8b | B_interactions_confidence → B_joint_interactions | 0.039430 | 0.039503 | -0.000073 [-0.000586, +0.000423] | 0.133126 | 0.132467 |
| llama31_8b | B_interactions_neutral_raw_confidence → B_joint_interactions_neutral_raw | 0.039596 | 0.039623 | -0.000027 [-0.000776, +0.000657] | 0.133796 | 0.133305 |
| llama31_8b | B_interactions_oracle_neutral_raw_confidence → B_joint_interactions_oracle_neutral_raw | 0.035738 | 0.034883 | +0.000856 [-0.000143, +0.001757] | 0.124886 | 0.122550 |
| llama31_8b | B_interactions_oracle_neutral_scored_confidence → B_joint_interactions_oracle_neutral_scored | 0.034994 | 0.034253 | +0.000741 [-0.000434, +0.001857] | 0.121870 | 0.119813 |
| llama31_8b | B_event_input → B_joint_input | 0.039681 | 0.039731 | -0.000050 [-0.000874, +0.000849] | 0.136367 | 0.134126 |
| llama31_8b | B_event_interactions → B_joint_interactions | 0.039524 | 0.039503 | +0.000021 [-0.000785, +0.000893] | 0.134908 | 0.132467 |
| llama31_8b | B_event_interactions_neutral_raw → B_joint_interactions_neutral_raw | 0.039940 | 0.039623 | +0.000317 [-0.000501, +0.001212] | 0.137111 | 0.133305 |
| llama31_8b | B_event_interactions_oracle_neutral_raw → B_joint_interactions_oracle_neutral_raw | 0.035287 | 0.034883 | +0.000405 [-0.000569, +0.001494] | 0.126859 | 0.122550 |
| llama31_8b | B_event_interactions_oracle_neutral_scored → B_joint_interactions_oracle_neutral_scored | 0.034585 | 0.034253 | +0.000331 [-0.000695, +0.001390] | 0.123859 | 0.119813 |
| llama31_8b | A_input → B_joint_input | 0.039731 | 0.039731 | -0.000000 [-0.001132, +0.001106] | 0.138343 | 0.134126 |
| llama31_8b | A_interactions → B_joint_interactions | 0.039673 | 0.039503 | +0.000170 [-0.000909, +0.001224] | 0.137222 | 0.132467 |
| llama31_8b | A_interactions_neutral_raw → B_joint_interactions_neutral_raw | 0.040037 | 0.039623 | +0.000414 [-0.000603, +0.001423] | 0.138487 | 0.133305 |
| llama31_8b | A_interactions_oracle_neutral_raw → B_joint_interactions_oracle_neutral_raw | 0.037215 | 0.034883 | +0.002333 [+0.000847, +0.003782] | 0.131400 | 0.122550 |
| llama31_8b | A_interactions_oracle_neutral_scored → B_joint_interactions_oracle_neutral_scored | 0.036016 | 0.034253 | +0.001763 [+0.000193, +0.003192] | 0.127793 | 0.119813 |

All 663,552 parent-tier OOF probability values reproduce exactly, as do every saved parent fit, normalizer, penalty, inner curve, group assignment and fallback record.

All 23 tiers and 55 contrasts, every fixed seed, calibration bin and descriptive cell remain in the full comparison and per-checkpoint reports. No checkpoint, seed or context was selected by result.
