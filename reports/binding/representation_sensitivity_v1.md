# Discovery representation rank and alignment sensitivity

Adaptive discovery sensitivity on already consumed structures, not final confirmation or a causal mechanism. A common 64-dimensional training PCA projection is fitted separately at each fixed site and feature backend, using all three naming conditions equally. This changes the earlier neutral-only fitting contract explicitly. Within-condition ceilings and retained variance describe projection loss; failure in this projection cannot reject harmless change elsewhere in the 4096-dimensional space. Train-only orthogonal alignment has full anchor rank in the projected space but is a fitted descriptive map, not a causal correspondence. Both canonical current and saved targets are always predicted together. Linear class scores are not calibrated probabilities. Frequency-matched shuffles preserve labels but do not equate all task complexity. Three shuffle seeds are controls, not independent replications. The pre_answer site precedes the later formatting-space correction and is not the actual digit boundary used by subsequent interventions. No ownership-control capture exists in this bank, so these results cannot isolate owner coding from value recovery or show natural use.

The recipe was fixed before new scores were read, after earlier discovery readouts were known. Complete 64-column one-hot current/saved targets, alpha 100 and ranks 1/2/4/8/16/32/64 are fixed. PCA uses pooled TRAIN rows only; alignments use exact paired TRAIN relatives only. Within-condition fits provide ceilings in the same common projected space. Surface features use 4,096 character-ngram features and their own common TRAIN PCA64.

| Backend | Site | PCA retained training variance | Training anchors per alignment |
|---|---|---:|---:|
| hidden | pre_query_state | 0.9524 | 1152 |
| surface | pre_query_state | 0.9968 | 1152 |
| hidden | pre_answer | 0.9286 | 2304 |
| surface | pre_answer | 0.9957 | 2304 |

Full rank 64 is the fixed reference in this projection; all ranks and control cells are retained in JSON/CSV.

| Backend | Site | Training condition | Development condition | Mode | Rows | Structural groups | Current accuracy | Saved accuracy | Joint accuracy |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| hidden | pre_query_state | neutral | neutral | within_condition | 384 | 6 | 0.4115 | 0.0651 | 0.0339 |
| hidden | pre_query_state | neutral | informative | neutral_transfer_unaligned | 384 | 6 | 0.3776 | 0.0365 | 0.0156 |
| hidden | pre_query_state | neutral | informative | neutral_transfer_aligned | 384 | 6 | 0.4062 | 0.0443 | 0.0365 |
| hidden | pre_query_state | neutral | misleading | neutral_transfer_unaligned | 384 | 6 | 0.3854 | 0.0469 | 0.0286 |
| hidden | pre_query_state | neutral | misleading | neutral_transfer_aligned | 384 | 6 | 0.3958 | 0.0521 | 0.0286 |
| hidden | pre_query_state | informative | informative | within_condition | 384 | 6 | 0.4271 | 0.0573 | 0.0443 |
| hidden | pre_query_state | misleading | misleading | within_condition | 384 | 6 | 0.4036 | 0.0521 | 0.0234 |
| surface | pre_query_state | neutral | neutral | within_condition | 384 | 6 | 0.0365 | 0.0208 | 0.0000 |
| surface | pre_query_state | neutral | informative | neutral_transfer_unaligned | 384 | 6 | 0.0208 | 0.0104 | 0.0000 |
| surface | pre_query_state | neutral | informative | neutral_transfer_aligned | 384 | 6 | 0.0104 | 0.1667 | 0.0000 |
| surface | pre_query_state | neutral | misleading | neutral_transfer_unaligned | 384 | 6 | 0.0365 | 0.0182 | 0.0000 |
| surface | pre_query_state | neutral | misleading | neutral_transfer_aligned | 384 | 6 | 0.0208 | 0.1250 | 0.0000 |
| surface | pre_query_state | informative | informative | within_condition | 384 | 6 | 0.0026 | 0.1250 | 0.0000 |
| surface | pre_query_state | misleading | misleading | within_condition | 384 | 6 | 0.0000 | 0.1250 | 0.0000 |
| hidden | pre_answer | neutral | neutral | within_condition | 768 | 6 | 0.2643 | 0.3203 | 0.0078 |
| hidden | pre_answer | neutral | informative | neutral_transfer_unaligned | 768 | 6 | 0.2083 | 0.2839 | 0.0104 |
| hidden | pre_answer | neutral | informative | neutral_transfer_aligned | 768 | 6 | 0.2370 | 0.3542 | 0.0130 |
| hidden | pre_answer | neutral | misleading | neutral_transfer_unaligned | 768 | 6 | 0.1901 | 0.3034 | 0.0078 |
| hidden | pre_answer | neutral | misleading | neutral_transfer_aligned | 768 | 6 | 0.2539 | 0.3568 | 0.0156 |
| hidden | pre_answer | informative | informative | within_condition | 768 | 6 | 0.2969 | 0.3581 | 0.0286 |
| hidden | pre_answer | misleading | misleading | within_condition | 768 | 6 | 0.2786 | 0.3802 | 0.0182 |
| surface | pre_answer | neutral | neutral | within_condition | 768 | 6 | 0.0651 | 0.0391 | 0.0052 |
| surface | pre_answer | neutral | informative | neutral_transfer_unaligned | 768 | 6 | 0.0547 | 0.0182 | 0.0026 |
| surface | pre_answer | neutral | informative | neutral_transfer_aligned | 768 | 6 | 0.1250 | 0.0000 | 0.0000 |
| surface | pre_answer | neutral | misleading | neutral_transfer_unaligned | 768 | 6 | 0.0417 | 0.0182 | 0.0000 |
| surface | pre_answer | neutral | misleading | neutral_transfer_aligned | 768 | 6 | 0.0508 | 0.0000 | 0.0000 |
| surface | pre_answer | informative | informative | within_condition | 768 | 6 | 0.0195 | 0.1068 | 0.0000 |
| surface | pre_answer | misleading | misleading | within_condition | 768 | 6 | 0.0742 | 0.0951 | 0.0000 |

Rank-64 alignment increments use the same neutral decoder before and after alignment. Conditional 95% intervals resample whole development components without refitting; all sites/backends/endpoints are descriptive and have no multiplicity adjustment.

| Backend | Site | Development condition | Endpoint | Aligned minus unaligned | Conditional group interval |
|---|---|---|---|---:|---|
| hidden | pre_query_state | informative | current_accuracy | 0.0286 | [-0.0260, 0.0833] |
| hidden | pre_query_state | informative | saved_accuracy | 0.0078 | [-0.0234, 0.0312] |
| hidden | pre_query_state | informative | joint_accuracy | 0.0208 | [-0.0026, 0.0417] |
| hidden | pre_query_state | misleading | current_accuracy | 0.0104 | [-0.0417, 0.0573] |
| hidden | pre_query_state | misleading | saved_accuracy | 0.0052 | [-0.0182, 0.0286] |
| hidden | pre_query_state | misleading | joint_accuracy | 0.0000 | [-0.0156, 0.0104] |
| surface | pre_query_state | informative | current_accuracy | -0.0104 | [-0.0521, 0.0260] |
| surface | pre_query_state | informative | saved_accuracy | 0.1562 | [0.0833, 0.2188] |
| surface | pre_query_state | informative | joint_accuracy | 0.0000 | [0.0000, 0.0000] |
| surface | pre_query_state | misleading | current_accuracy | -0.0156 | [-0.0573, 0.0417] |
| surface | pre_query_state | misleading | saved_accuracy | 0.1068 | [0.0260, 0.1797] |
| surface | pre_query_state | misleading | joint_accuracy | 0.0000 | [0.0000, 0.0000] |
| hidden | pre_answer | informative | current_accuracy | 0.0286 | [-0.0078, 0.0677] |
| hidden | pre_answer | informative | saved_accuracy | 0.0703 | [0.0430, 0.0964] |
| hidden | pre_answer | informative | joint_accuracy | 0.0026 | [-0.0208, 0.0208] |
| hidden | pre_answer | misleading | current_accuracy | 0.0638 | [0.0208, 0.1068] |
| hidden | pre_answer | misleading | saved_accuracy | 0.0534 | [0.0130, 0.0898] |
| hidden | pre_answer | misleading | joint_accuracy | 0.0078 | [-0.0091, 0.0234] |
| surface | pre_answer | informative | current_accuracy | 0.0703 | [0.0169, 0.1172] |
| surface | pre_answer | informative | saved_accuracy | -0.0182 | [-0.0443, 0.0000] |
| surface | pre_answer | informative | joint_accuracy | -0.0026 | [-0.0078, 0.0000] |
| surface | pre_answer | misleading | current_accuracy | 0.0091 | [-0.0404, 0.0625] |
| surface | pre_answer | misleading | saved_accuracy | -0.0182 | [-0.0287, -0.0078] |
| surface | pre_answer | misleading | joint_accuracy | 0.0000 | [0.0000, 0.0000] |

Saved fits: 336; exact saved-parameter row replays: 2322432.

The original final/extrapolation outcomes remain sealed. No language model was loaded, trained or queried.
