# Queried versus unqueried discovery readouts

Adaptive descriptive discovery readouts on one checkpoint and previously consumed structures. The primary site was selected because earlier queried-value recovery was known, not from new results. Queried/unqueried labels have matched aggregate class marginals and identical per-head capacity, but their conditional task difficulty can differ. A gap describes query-dependent accessibility under this decoder; it does not identify tracking, reconstruction, owner coding, a binding register or natural causal use. Canonical current/saved reconstruction only relabels the queried/unqueried predictions using the known input query role; it is postprocessing, not separately trained canonical-slot heads or a replay of the older canonical probes. Those and query-role cells are descriptive. Both identical pre-query twins are retained: their analytic head objectives coincide and contain no information about the future query. Raw heads are not averaged or canonicalized to enforce agreement; floating-point argmax disagreements within the fixed 1e-8 score tolerance are reported as ties. Three seeds vary template weights and grouped shuffle controls, not independent experiments. Primary intervals resample six whole development components after averaging the fixed-seed paired correctness differences; they condition on saved fits without refitting or multiplicity correction. Float64 standardization/fitting differs from possible float32 rounding in older probe fits; new results are not claimed to replay those older fit scores exactly. The captured pre_answer site precedes the later formatting-space correction and is not the later digit boundary. Capture validation reads stored response/score metadata, but no response, correctness, row ID or query-role field becomes a readout feature. No model/tokenizer is loaded or new response generated.

All 9,216 rows, including both query twins, are retained at every site. Neutral training uses 2,304 rows and 18 structural groups; each development naming condition has 768 rows and six groups. Each of four independent heads has 32 classes and 131,104 coefficient/intercept parameters. A shared Cholesky factorization changes computation cost, not per-head capacity or the independent summed ridge objective.

Primary paired accuracy increment: 0.794705; conditional group interval [0.758669704861111, 0.8350694444444445].

| Backend | Layer | Site | Development naming | Queried | Unqueried | Shuffled queried | Shuffled unqueried | Whole pair |
|---|---:|---|---|---:|---:|---:|---:|---:|
| hidden | 8 | after_query | informative | 0.0456 | 0.0547 | 0.0226 | 0.0317 | 0.0004 |
| hidden | 8 | after_query | misleading | 0.0200 | 0.0408 | 0.0334 | 0.0247 | 0.0013 |
| hidden | 8 | after_query | neutral | 0.0612 | 0.0647 | 0.0412 | 0.0334 | 0.0048 |
| hidden | 8 | pre_answer | informative | 0.0447 | 0.0282 | 0.0217 | 0.0278 | 0.0000 |
| hidden | 8 | pre_answer | misleading | 0.0438 | 0.0286 | 0.0226 | 0.0330 | 0.0004 |
| hidden | 8 | pre_answer | neutral | 0.0464 | 0.0412 | 0.0195 | 0.0269 | 0.0017 |
| hidden | 8 | pre_query_state | informative | 0.0985 | 0.0985 | 0.0260 | 0.0260 | 0.0000 |
| hidden | 8 | pre_query_state | misleading | 0.0846 | 0.0846 | 0.0321 | 0.0321 | 0.0000 |
| hidden | 8 | pre_query_state | neutral | 0.2010 | 0.2010 | 0.0308 | 0.0308 | 0.0000 |
| hidden | 16 | after_query | informative | 0.0378 | 0.0503 | 0.0243 | 0.0260 | 0.0017 |
| hidden | 16 | after_query | misleading | 0.0438 | 0.0516 | 0.0243 | 0.0239 | 0.0030 |
| hidden | 16 | after_query | neutral | 0.0477 | 0.0668 | 0.0191 | 0.0221 | 0.0030 |
| hidden | 16 | pre_answer | informative | 0.3954 | 0.0460 | 0.0273 | 0.0221 | 0.0217 |
| hidden | 16 | pre_answer | misleading | 0.5365 | 0.0417 | 0.0326 | 0.0252 | 0.0221 |
| hidden | 16 | pre_answer | neutral | 0.5833 | 0.0734 | 0.0234 | 0.0191 | 0.0477 |
| hidden | 16 | pre_query_state | informative | 0.1523 | 0.1523 | 0.0269 | 0.0269 | 0.0000 |
| hidden | 16 | pre_query_state | misleading | 0.1502 | 0.1502 | 0.0321 | 0.0321 | 0.0000 |
| hidden | 16 | pre_query_state | neutral | 0.2357 | 0.2357 | 0.0230 | 0.0230 | 0.0000 |
| hidden | 24 | after_query | informative | 0.0634 | 0.0217 | 0.0304 | 0.0230 | 0.0017 |
| hidden | 24 | after_query | misleading | 0.0516 | 0.0365 | 0.0256 | 0.0230 | 0.0013 |
| hidden | 24 | after_query | neutral | 0.0560 | 0.0590 | 0.0260 | 0.0226 | 0.0043 |
| hidden | 24 | pre_answer | informative | 0.8212 | 0.0781 | 0.0252 | 0.0286 | 0.0612 |
| hidden | 24 | pre_answer | misleading | 0.8646 | 0.0825 | 0.0234 | 0.0352 | 0.0694 |
| hidden | 24 | pre_answer | neutral | 0.8889 | 0.0942 | 0.0234 | 0.0356 | 0.0825 |
| hidden | 24 | pre_query_state | informative | 0.1710 | 0.1710 | 0.0239 | 0.0239 | 0.0000 |
| hidden | 24 | pre_query_state | misleading | 0.1727 | 0.1727 | 0.0304 | 0.0304 | 0.0000 |
| hidden | 24 | pre_query_state | neutral | 0.2474 | 0.2474 | 0.0247 | 0.0247 | 0.0000 |
| hidden | 31 | after_query | informative | 0.0699 | 0.0417 | 0.0326 | 0.0352 | 0.0000 |
| hidden | 31 | after_query | misleading | 0.0712 | 0.0204 | 0.0330 | 0.0330 | 0.0000 |
| hidden | 31 | after_query | neutral | 0.0642 | 0.0330 | 0.0330 | 0.0226 | 0.0000 |
| hidden | 31 | pre_answer | informative | 0.8372 | 0.0894 | 0.0339 | 0.0326 | 0.0790 |
| hidden | 31 | pre_answer | misleading | 0.8707 | 0.0786 | 0.0317 | 0.0317 | 0.0720 |
| hidden | 31 | pre_answer | neutral | 0.8789 | 0.0981 | 0.0278 | 0.0295 | 0.0898 |
| hidden | 31 | pre_query_state | informative | 0.0816 | 0.0816 | 0.0260 | 0.0260 | 0.0000 |
| hidden | 31 | pre_query_state | misleading | 0.0786 | 0.0786 | 0.0204 | 0.0204 | 0.0000 |
| hidden | 31 | pre_query_state | neutral | 0.1406 | 0.1406 | 0.0239 | 0.0239 | 0.0000 |
| surface | -1 | after_query | informative | 0.0347 | 0.0356 | 0.0230 | 0.0239 | 0.0004 |
| surface | -1 | after_query | misleading | 0.0438 | 0.0412 | 0.0208 | 0.0226 | 0.0000 |
| surface | -1 | after_query | neutral | 0.0898 | 0.0885 | 0.0308 | 0.0299 | 0.0000 |
| surface | -1 | pre_answer | informative | 0.0334 | 0.0330 | 0.0347 | 0.0343 | 0.0000 |
| surface | -1 | pre_answer | misleading | 0.0369 | 0.0365 | 0.0291 | 0.0286 | 0.0000 |
| surface | -1 | pre_answer | neutral | 0.0907 | 0.0877 | 0.0321 | 0.0312 | 0.0000 |
| surface | -1 | pre_query_state | informative | 0.0386 | 0.0386 | 0.0365 | 0.0365 | 0.0000 |
| surface | -1 | pre_query_state | misleading | 0.0408 | 0.0408 | 0.0252 | 0.0252 | 0.0000 |
| surface | -1 | pre_query_state | neutral | 0.0764 | 0.0764 | 0.0256 | 0.0256 | 0.0000 |

The table averages three fixed weighting fits. Full training/development, query-role, class-support, canonical-slot and numerical symmetry cells remain in JSON and CSV.

45 shared factorizations fit 180 independent heads. All 414720 saved-model row replays passed exactly.

No original final/extrapolation outcome was evaluated, and no language model was loaded or trained.
