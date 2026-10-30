# Discovery-only failure prediction: meta-llama/Llama-3.1-8B-Instruct

Exploratory grouped prediction on previously consumed discovery structures, not mechanism C or unfamiliar-program/final confirmation. All thirteen existing source, neutral, oracle and BF16 next-token confidence tiers are retained unchanged. Five event alternatives use only six scalar summaries of declared finite numeral-plus-EOS token events; no old one-token confidence scalars are added to those alternatives. Comparing B_event with B_confidence compares alternative measurement bundles, not a nested information-only increment: event definition, FP32/no-TF32 versus BF16 numeric execution, checkpoint-specific tokenization rules, encoding and fitted function-class effects can all matter. A gain cannot isolate full-answer scoring from those differences. Event likelihood access is stronger than one-token sign/format confidence: one FP32 prefix prefill plus all 33 candidate numerals and the declared EOS union, spanning 35 prefix states per target. KV reuse does not remove this scientific access cost. Finite-event support mass is separate from support-conditional summaries; other textual answers/tokenizations are outside that support. Source-oracle and scored/raw neutral access remain separately declared. No generated token, token/candidate identity or target response/correctness is a feature. Correctness is only the existing supervised label. Repeated partition seeds are not independent replications; bootstrap intervals condition on saved OOF predictions without refits or multiplicity correction.

6,144 transformed targets, 24 template components, 430 failures. All target IDs remain in every fixed seed's OOF evaluation.

| Evaluation | Predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| seed:17 | prior | 0.065185 | 0.254365 | 6144 | 430 |
| seed:17 | A_input | 0.040056 | 0.139188 | 6144 | 430 |
| seed:17 | A_interactions | 0.039990 | 0.138162 | 6144 | 430 |
| seed:17 | A_interactions_neutral_raw | 0.040224 | 0.138969 | 6144 | 430 |
| seed:17 | A_interactions_neutral_scored | 0.036722 | 0.129914 | 6144 | 430 |
| seed:17 | A_interactions_oracle | 0.038331 | 0.134398 | 6144 | 430 |
| seed:17 | A_interactions_oracle_neutral_raw | 0.037267 | 0.131679 | 6144 | 430 |
| seed:17 | A_interactions_oracle_neutral_scored | 0.035863 | 0.127535 | 6144 | 430 |
| seed:17 | B_input_confidence | 0.039790 | 0.135202 | 6144 | 430 |
| seed:17 | B_interactions_confidence | 0.039634 | 0.133698 | 6144 | 430 |
| seed:17 | B_interactions_neutral_raw_confidence | 0.039745 | 0.134369 | 6144 | 430 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | 0.035537 | 0.124490 | 6144 | 430 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | 0.034881 | 0.121622 | 6144 | 430 |
| seed:17 | B_event_input | 0.039930 | 0.137162 | 6144 | 430 |
| seed:17 | B_event_interactions | 0.039773 | 0.135860 | 6144 | 430 |
| seed:17 | B_event_interactions_neutral_raw | 0.040169 | 0.138125 | 6144 | 430 |
| seed:17 | B_event_interactions_oracle_neutral_raw | 0.035417 | 0.127999 | 6144 | 430 |
| seed:17 | B_event_interactions_oracle_neutral_scored | 0.034498 | 0.124188 | 6144 | 430 |
| seed:29 | prior | 0.065182 | 0.254318 | 6144 | 430 |
| seed:29 | A_input | 0.039799 | 0.138643 | 6144 | 430 |
| seed:29 | A_interactions | 0.039883 | 0.137716 | 6144 | 430 |
| seed:29 | A_interactions_neutral_raw | 0.040341 | 0.139463 | 6144 | 430 |
| seed:29 | A_interactions_neutral_scored | 0.036857 | 0.130029 | 6144 | 430 |
| seed:29 | A_interactions_oracle | 0.038413 | 0.134704 | 6144 | 430 |
| seed:29 | A_interactions_oracle_neutral_raw | 0.037563 | 0.132348 | 6144 | 430 |
| seed:29 | A_interactions_oracle_neutral_scored | 0.036437 | 0.129195 | 6144 | 430 |
| seed:29 | B_input_confidence | 0.039742 | 0.135040 | 6144 | 430 |
| seed:29 | B_interactions_confidence | 0.039660 | 0.133740 | 6144 | 430 |
| seed:29 | B_interactions_neutral_raw_confidence | 0.039904 | 0.134812 | 6144 | 430 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | 0.036151 | 0.126271 | 6144 | 430 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | 0.035378 | 0.123593 | 6144 | 430 |
| seed:29 | B_event_input | 0.039795 | 0.136586 | 6144 | 430 |
| seed:29 | B_event_interactions | 0.039722 | 0.135264 | 6144 | 430 |
| seed:29 | B_event_interactions_neutral_raw | 0.040025 | 0.136954 | 6144 | 430 |
| seed:29 | B_event_interactions_oracle_neutral_raw | 0.035613 | 0.128265 | 6144 | 430 |
| seed:29 | B_event_interactions_oracle_neutral_scored | 0.034998 | 0.125747 | 6144 | 430 |
| seed:43 | prior | 0.065101 | 0.253695 | 6144 | 430 |
| seed:43 | A_input | 0.039505 | 0.137826 | 6144 | 430 |
| seed:43 | A_interactions | 0.039317 | 0.136365 | 6144 | 430 |
| seed:43 | A_interactions_neutral_raw | 0.039865 | 0.138098 | 6144 | 430 |
| seed:43 | A_interactions_neutral_scored | 0.036506 | 0.128908 | 6144 | 430 |
| seed:43 | A_interactions_oracle | 0.037805 | 0.132841 | 6144 | 430 |
| seed:43 | A_interactions_oracle_neutral_raw | 0.037067 | 0.131054 | 6144 | 430 |
| seed:43 | A_interactions_oracle_neutral_scored | 0.036029 | 0.127871 | 6144 | 430 |
| seed:43 | B_input_confidence | 0.039386 | 0.134382 | 6144 | 430 |
| seed:43 | B_interactions_confidence | 0.039183 | 0.132588 | 6144 | 430 |
| seed:43 | B_interactions_neutral_raw_confidence | 0.039511 | 0.133765 | 6144 | 430 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | 0.035939 | 0.125730 | 6144 | 430 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | 0.035182 | 0.122472 | 6144 | 430 |
| seed:43 | B_event_input | 0.039495 | 0.135958 | 6144 | 430 |
| seed:43 | B_event_interactions | 0.039276 | 0.134275 | 6144 | 430 |
| seed:43 | B_event_interactions_neutral_raw | 0.040233 | 0.138274 | 6144 | 430 |
| seed:43 | B_event_interactions_oracle_neutral_raw | 0.035280 | 0.126653 | 6144 | 430 |
| seed:43 | B_event_interactions_oracle_neutral_scored | 0.034717 | 0.124167 | 6144 | 430 |
| ensemble:mean_probability | prior | 0.065153 | 0.254100 | 6144 | 430 |
| ensemble:mean_probability | A_input | 0.039731 | 0.138343 | 6144 | 430 |
| ensemble:mean_probability | A_interactions | 0.039673 | 0.137222 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_neutral_raw | 0.040037 | 0.138487 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_neutral_scored | 0.036599 | 0.129256 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_oracle | 0.038100 | 0.133688 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | 0.037215 | 0.131400 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | 0.036016 | 0.127793 | 6144 | 430 |
| ensemble:mean_probability | B_input_confidence | 0.039576 | 0.134655 | 6144 | 430 |
| ensemble:mean_probability | B_interactions_confidence | 0.039430 | 0.133126 | 6144 | 430 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | 0.039596 | 0.133796 | 6144 | 430 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | 0.035738 | 0.124886 | 6144 | 430 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | 0.034994 | 0.121870 | 6144 | 430 |
| ensemble:mean_probability | B_event_input | 0.039681 | 0.136367 | 6144 | 430 |
| ensemble:mean_probability | B_event_interactions | 0.039524 | 0.134908 | 6144 | 430 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | 0.039940 | 0.137111 | 6144 | 430 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | 0.035287 | 0.126859 | 6144 | 430 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | 0.034585 | 0.123859 | 6144 | 430 |

## All paired template-bootstrap improvements

Positive loss(left) − loss(right) favors the right predictor. These are conditional exploratory intervals with no refitting or multiplicity adjustment.

| Evaluation | Left baseline | Right predictor | Brier improvement [95%] | Log-loss improvement [95%] |
|---|---|---|---|---|
| seed:17 | prior | A_input | +0.025130 [+0.019033, +0.031386] | +0.115177 [+0.094567, +0.135065] |
| seed:17 | prior | A_interactions | +0.025195 [+0.018949, +0.031619] | +0.116203 [+0.096371, +0.135181] |
| seed:17 | prior | A_interactions_neutral_raw | +0.024961 [+0.018780, +0.031263] | +0.115396 [+0.096114, +0.134277] |
| seed:17 | prior | A_interactions_neutral_scored | +0.028463 [+0.022222, +0.034718] | +0.124451 [+0.105074, +0.143278] |
| seed:17 | prior | A_interactions_oracle | +0.026855 [+0.020756, +0.032932] | +0.119967 [+0.100375, +0.138934] |
| seed:17 | prior | A_interactions_oracle_neutral_raw | +0.027919 [+0.021970, +0.033889] | +0.122686 [+0.103224, +0.141935] |
| seed:17 | prior | A_interactions_oracle_neutral_scored | +0.029323 [+0.022975, +0.035594] | +0.126830 [+0.107631, +0.145859] |
| seed:17 | A_input | A_interactions | +0.000065 [-0.000391, +0.000542] | +0.001026 [-0.001497, +0.003699] |
| seed:17 | A_interactions | A_interactions_neutral_raw | -0.000234 [-0.000692, +0.000196] | -0.000807 [-0.001866, +0.000268] |
| seed:17 | A_interactions | A_interactions_neutral_scored | +0.003268 [+0.000832, +0.005804] | +0.008247 [+0.002235, +0.014337] |
| seed:17 | A_interactions | A_interactions_oracle | +0.001660 [+0.000358, +0.002931] | +0.003764 [+0.000660, +0.006866] |
| seed:17 | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.001064 [-0.000069, +0.002294] | +0.002719 [-0.000093, +0.005792] |
| seed:17 | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.001404 [-0.000021, +0.002786] | +0.004145 [+0.000295, +0.007988] |
| seed:17 | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.003502 [+0.001061, +0.006164] | +0.009055 [+0.003031, +0.015131] |
| seed:17 | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.002957 [+0.001071, +0.005136] | +0.007289 [+0.002839, +0.012269] |
| seed:17 | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.000859 [+0.000314, +0.001387] | +0.002380 [+0.000544, +0.004304] |
| seed:17 | A_input | B_input_confidence | +0.000265 [-0.000752, +0.001348] | +0.003986 [+0.001336, +0.006711] |
| seed:17 | A_interactions | B_interactions_confidence | +0.000356 [-0.000630, +0.001399] | +0.004464 [+0.001664, +0.007247] |
| seed:17 | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.000479 [-0.000482, +0.001533] | +0.004599 [+0.001732, +0.007503] |
| seed:17 | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.001730 [+0.000268, +0.003368] | +0.007189 [+0.002426, +0.012439] |
| seed:17 | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.000981 [-0.000472, +0.002486] | +0.005912 [+0.001203, +0.010919] |
| seed:17 | B_input_confidence | B_interactions_confidence | +0.000156 [-0.000326, +0.000643] | +0.001504 [-0.000740, +0.003982] |
| seed:17 | B_interactions_confidence | B_interactions_neutral_raw_confidence | -0.000111 [-0.000682, +0.000347] | -0.000672 [-0.002142, +0.000616] |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.000655 [-0.000696, +0.001885] | +0.002868 [-0.000894, +0.006404] |
| seed:17 | A_input | B_event_input | +0.000125 [-0.000388, +0.000632] | +0.002026 [+0.000534, +0.003602] |
| seed:17 | A_interactions | B_event_interactions | +0.000217 [-0.000329, +0.000758] | +0.002302 [+0.000741, +0.003844] |
| seed:17 | A_interactions_neutral_raw | B_event_interactions_neutral_raw | +0.000056 [-0.000558, +0.000639] | +0.000844 [-0.001135, +0.002797] |
| seed:17 | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.001850 [+0.000471, +0.003082] | +0.003681 [-0.001119, +0.008212] |
| seed:17 | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.001364 [+0.000115, +0.002498] | +0.003347 [-0.000928, +0.007378] |
| seed:17 | B_input_confidence | B_event_input | -0.000140 [-0.001197, +0.000810] | -0.001960 [-0.004834, +0.000648] |
| seed:17 | B_interactions_confidence | B_event_interactions | -0.000139 [-0.001149, +0.000814] | -0.002162 [-0.005015, +0.000443] |
| seed:17 | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | -0.000423 [-0.001665, +0.000657] | -0.003756 [-0.007162, -0.000744] |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.000120 [-0.001813, +0.001827] | -0.003508 [-0.011122, +0.003097] |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.000383 [-0.001446, +0.002002] | -0.002565 [-0.009357, +0.003739] |
| seed:17 | B_event_input | B_event_interactions | +0.000157 [-0.000306, +0.000685] | +0.001302 [-0.000892, +0.003617] |
| seed:17 | B_event_interactions | B_event_interactions_neutral_raw | -0.000395 [-0.001094, +0.000186] | -0.002265 [-0.004271, -0.000474] |
| seed:17 | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.000919 [-0.000469, +0.002240] | +0.003811 [-0.000170, +0.007969] |
| seed:29 | prior | A_input | +0.025383 [+0.019258, +0.031745] | +0.115675 [+0.095257, +0.136205] |
| seed:29 | prior | A_interactions | +0.025300 [+0.019013, +0.031858] | +0.116602 [+0.097089, +0.135897] |
| seed:29 | prior | A_interactions_neutral_raw | +0.024842 [+0.018648, +0.031194] | +0.114855 [+0.096035, +0.133642] |
| seed:29 | prior | A_interactions_neutral_scored | +0.028326 [+0.022150, +0.034644] | +0.124289 [+0.105649, +0.142869] |
| seed:29 | prior | A_interactions_oracle | +0.026769 [+0.020734, +0.032827] | +0.119614 [+0.100518, +0.138114] |
| seed:29 | prior | A_interactions_oracle_neutral_raw | +0.027620 [+0.021776, +0.033518] | +0.121970 [+0.102886, +0.140887] |
| seed:29 | prior | A_interactions_oracle_neutral_scored | +0.028745 [+0.022532, +0.035087] | +0.125123 [+0.105965, +0.144721] |
| seed:29 | A_input | A_interactions | -0.000083 [-0.000540, +0.000336] | +0.000926 [-0.001586, +0.003691] |
| seed:29 | A_interactions | A_interactions_neutral_raw | -0.000458 [-0.001020, +0.000025] | -0.001747 [-0.003111, -0.000383] |
| seed:29 | A_interactions | A_interactions_neutral_scored | +0.003026 [+0.000583, +0.005715] | +0.007687 [+0.001730, +0.013837] |
| seed:29 | A_interactions | A_interactions_oracle | +0.001469 [+0.000167, +0.002822] | +0.003012 [-0.000313, +0.006249] |
| seed:29 | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.000851 [-0.000290, +0.002116] | +0.002356 [-0.000516, +0.005567] |
| seed:29 | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.001125 [-0.000467, +0.002606] | +0.003154 [-0.001469, +0.007393] |
| seed:29 | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.003484 [+0.000983, +0.006199] | +0.009434 [+0.003286, +0.015787] |
| seed:29 | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.002778 [+0.000876, +0.004962] | +0.007115 [+0.002573, +0.012261] |
| seed:29 | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.000419 [-0.000245, +0.001061] | +0.000835 [-0.001290, +0.002978] |
| seed:29 | A_input | B_input_confidence | +0.000058 [-0.001080, +0.001211] | +0.003602 [+0.000813, +0.006508] |
| seed:29 | A_interactions | B_interactions_confidence | +0.000223 [-0.000812, +0.001315] | +0.003976 [+0.001192, +0.006767] |
| seed:29 | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.000437 [-0.000593, +0.001489] | +0.004651 [+0.001519, +0.007824] |
| seed:29 | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.001412 [+0.000158, +0.002735] | +0.006078 [+0.002105, +0.010232] |
| seed:29 | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.001059 [-0.000349, +0.002498] | +0.005602 [+0.000869, +0.010366] |
| seed:29 | B_input_confidence | B_interactions_confidence | +0.000082 [-0.000344, +0.000506] | +0.001300 [-0.000970, +0.003797] |
| seed:29 | B_interactions_confidence | B_interactions_neutral_raw_confidence | -0.000244 [-0.000893, +0.000338] | -0.001071 [-0.002884, +0.000512] |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.000773 [-0.000886, +0.002131] | +0.002678 [-0.002451, +0.007186] |
| seed:29 | A_input | B_event_input | +0.000004 [-0.000536, +0.000550] | +0.002056 [+0.000394, +0.003699] |
| seed:29 | A_interactions | B_event_interactions | +0.000161 [-0.000374, +0.000685] | +0.002452 [+0.000878, +0.004017] |
| seed:29 | A_interactions_neutral_raw | B_event_interactions_neutral_raw | +0.000316 [-0.000229, +0.000864] | +0.002510 [+0.000799, +0.004359] |
| seed:29 | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.001949 [+0.000528, +0.003251] | +0.004084 [-0.001931, +0.009309] |
| seed:29 | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.001439 [+0.000155, +0.002607] | +0.003448 [-0.002472, +0.008606] |
| seed:29 | B_input_confidence | B_event_input | -0.000053 [-0.001252, +0.000997] | -0.001546 [-0.004635, +0.001096] |
| seed:29 | B_interactions_confidence | B_event_interactions | -0.000062 [-0.001156, +0.000955] | -0.001524 [-0.004456, +0.001092] |
| seed:29 | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | -0.000121 [-0.001300, +0.000935] | -0.002142 [-0.005717, +0.001058] |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.000538 [-0.001229, +0.002133] | -0.001994 [-0.009983, +0.004867] |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.000380 [-0.001595, +0.002113] | -0.002154 [-0.010496, +0.005042] |
| seed:29 | B_event_input | B_event_interactions | +0.000073 [-0.000386, +0.000541] | +0.001322 [-0.000727, +0.003623] |
| seed:29 | B_event_interactions | B_event_interactions_neutral_raw | -0.000303 [-0.001005, +0.000333] | -0.001689 [-0.003403, +0.000032] |
| seed:29 | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.000615 [-0.000807, +0.001882] | +0.002518 [-0.001426, +0.006293] |
| seed:43 | prior | A_input | +0.025595 [+0.019466, +0.031847] | +0.115869 [+0.095557, +0.135452] |
| seed:43 | prior | A_interactions | +0.025783 [+0.019442, +0.032308] | +0.117330 [+0.097769, +0.136410] |
| seed:43 | prior | A_interactions_neutral_raw | +0.025236 [+0.018884, +0.031628] | +0.115597 [+0.096420, +0.134241] |
| seed:43 | prior | A_interactions_neutral_scored | +0.028594 [+0.022413, +0.034826] | +0.124787 [+0.105718, +0.143178] |
| seed:43 | prior | A_interactions_oracle | +0.027295 [+0.021191, +0.033373] | +0.120855 [+0.101720, +0.139038] |
| seed:43 | prior | A_interactions_oracle_neutral_raw | +0.028033 [+0.022036, +0.034004] | +0.122641 [+0.103453, +0.141063] |
| seed:43 | prior | A_interactions_oracle_neutral_scored | +0.029072 [+0.022720, +0.035461] | +0.125825 [+0.106473, +0.144636] |
| seed:43 | A_input | A_interactions | +0.000188 [-0.000377, +0.000766] | +0.001461 [-0.000980, +0.004071] |
| seed:43 | A_interactions | A_interactions_neutral_raw | -0.000548 [-0.001170, +0.000000] | -0.001733 [-0.003156, -0.000397] |
| seed:43 | A_interactions | A_interactions_neutral_scored | +0.002811 [+0.000608, +0.005032] | +0.007457 [+0.002317, +0.012627] |
| seed:43 | A_interactions | A_interactions_oracle | +0.001512 [+0.000102, +0.002841] | +0.003524 [+0.000036, +0.006767] |
| seed:43 | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.000738 [-0.000418, +0.001940] | +0.001786 [-0.001156, +0.004835] |
| seed:43 | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.001039 [-0.000394, +0.002368] | +0.003183 [-0.000611, +0.006894] |
| seed:43 | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.003359 [+0.001137, +0.005667] | +0.009190 [+0.003856, +0.014586] |
| seed:43 | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.002798 [+0.000995, +0.004833] | +0.007044 [+0.002797, +0.011647] |
| seed:43 | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.000478 [-0.000171, +0.001096] | +0.001037 [-0.000772, +0.002871] |
| seed:43 | A_input | B_input_confidence | +0.000119 [-0.000912, +0.001156] | +0.003444 [+0.000747, +0.006204] |
| seed:43 | A_interactions | B_interactions_confidence | +0.000134 [-0.000880, +0.001138] | +0.003777 [+0.000959, +0.006517] |
| seed:43 | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.000354 [-0.000743, +0.001481] | +0.004333 [+0.001184, +0.007421] |
| seed:43 | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.001128 [-0.000229, +0.002602] | +0.005324 [+0.001083, +0.009727] |
| seed:43 | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.000847 [-0.000537, +0.002199] | +0.005399 [+0.001038, +0.009646] |
| seed:43 | B_input_confidence | B_interactions_confidence | +0.000204 [-0.000301, +0.000727] | +0.001794 [-0.000463, +0.004291] |
| seed:43 | B_interactions_confidence | B_interactions_neutral_raw_confidence | -0.000328 [-0.000988, +0.000183] | -0.001177 [-0.002798, +0.000190] |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.000757 [-0.000687, +0.002017] | +0.003258 [-0.000844, +0.006925] |
| seed:43 | A_input | B_event_input | +0.000010 [-0.000609, +0.000585] | +0.001868 [+0.000115, +0.003575] |
| seed:43 | A_interactions | B_event_interactions | +0.000041 [-0.000549, +0.000588] | +0.002090 [+0.000479, +0.003699] |
| seed:43 | A_interactions_neutral_raw | B_event_interactions_neutral_raw | -0.000368 [-0.001263, +0.000445] | -0.000176 [-0.002760, +0.002016] |
| seed:43 | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.001787 [+0.000706, +0.002780] | +0.004401 [+0.000168, +0.008125] |
| seed:43 | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.001311 [+0.000205, +0.002376] | +0.003704 [-0.000676, +0.007582] |
| seed:43 | B_input_confidence | B_event_input | -0.000109 [-0.001131, +0.000799] | -0.001575 [-0.004396, +0.000740] |
| seed:43 | B_interactions_confidence | B_event_interactions | -0.000094 [-0.001108, +0.000840] | -0.001687 [-0.004421, +0.000643] |
| seed:43 | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | -0.000722 [-0.002309, +0.000585] | -0.004509 [-0.008994, -0.000720] |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.000659 [-0.001082, +0.002156] | -0.000923 [-0.007744, +0.004947] |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.000465 [-0.001259, +0.002015] | -0.001695 [-0.008443, +0.004334] |
| seed:43 | B_event_input | B_event_interactions | +0.000219 [-0.000296, +0.000760] | +0.001682 [-0.000520, +0.004019] |
| seed:43 | B_event_interactions | B_event_interactions_neutral_raw | -0.000957 [-0.001978, -0.000096] | -0.003999 [-0.006730, -0.001684] |
| seed:43 | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.000563 [-0.000635, +0.001656] | +0.002486 [-0.000752, +0.005672] |
| ensemble:mean_probability | prior | A_input | +0.025422 [+0.019283, +0.031704] | +0.115758 [+0.095231, +0.135725] |
| ensemble:mean_probability | prior | A_interactions | +0.025480 [+0.019173, +0.031959] | +0.116878 [+0.097286, +0.136000] |
| ensemble:mean_probability | prior | A_interactions_neutral_raw | +0.025116 [+0.018828, +0.031443] | +0.115614 [+0.096442, +0.134429] |
| ensemble:mean_probability | prior | A_interactions_neutral_scored | +0.028554 [+0.022338, +0.034863] | +0.124844 [+0.105885, +0.143487] |
| ensemble:mean_probability | prior | A_interactions_oracle | +0.027053 [+0.020985, +0.033111] | +0.120412 [+0.101211, +0.139062] |
| ensemble:mean_probability | prior | A_interactions_oracle_neutral_raw | +0.027938 [+0.021951, +0.033911] | +0.122701 [+0.103411, +0.141520] |
| ensemble:mean_probability | prior | A_interactions_oracle_neutral_scored | +0.029137 [+0.022850, +0.035453] | +0.126307 [+0.107071, +0.145456] |
| ensemble:mean_probability | A_input | A_interactions | +0.000058 [-0.000431, +0.000529] | +0.001121 [-0.001357, +0.003776] |
| ensemble:mean_probability | A_interactions | A_interactions_neutral_raw | -0.000364 [-0.000899, +0.000100] | -0.001265 [-0.002463, -0.000098] |
| ensemble:mean_probability | A_interactions | A_interactions_neutral_scored | +0.003073 [+0.000728, +0.005558] | +0.007966 [+0.002350, +0.013678] |
| ensemble:mean_probability | A_interactions | A_interactions_oracle | +0.001573 [+0.000236, +0.002884] | +0.003534 [+0.000263, +0.006675] |
| ensemble:mean_probability | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.000885 [-0.000238, +0.002097] | +0.002288 [-0.000572, +0.005256] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.001199 [-0.000267, +0.002593] | +0.003606 [-0.000326, +0.007471] |
| ensemble:mean_probability | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.003437 [+0.001098, +0.005983] | +0.009230 [+0.003413, +0.015125] |
| ensemble:mean_probability | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.002822 [+0.000957, +0.004949] | +0.007087 [+0.002700, +0.011982] |
| ensemble:mean_probability | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.000583 [-0.000010, +0.001156] | +0.001463 [-0.000316, +0.003336] |
| ensemble:mean_probability | A_input | B_input_confidence | +0.000154 [-0.000888, +0.001227] | +0.003687 [+0.001082, +0.006407] |
| ensemble:mean_probability | A_interactions | B_interactions_confidence | +0.000243 [-0.000755, +0.001285] | +0.004095 [+0.001358, +0.006860] |
| ensemble:mean_probability | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.000441 [-0.000556, +0.001515] | +0.004690 [+0.001750, +0.007695] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.001477 [+0.000134, +0.002940] | +0.006513 [+0.002368, +0.010982] |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.001022 [-0.000405, +0.002435] | +0.005923 [+0.001328, +0.010513] |
| ensemble:mean_probability | B_input_confidence | B_interactions_confidence | +0.000147 [-0.000288, +0.000611] | +0.001529 [-0.000694, +0.004021] |
| ensemble:mean_probability | B_interactions_confidence | B_interactions_neutral_raw_confidence | -0.000166 [-0.000773, +0.000317] | -0.000670 [-0.002197, +0.000657] |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.000744 [-0.000730, +0.001993] | +0.003016 [-0.001170, +0.006857] |
| ensemble:mean_probability | A_input | B_event_input | +0.000050 [-0.000500, +0.000568] | +0.001976 [+0.000361, +0.003575] |
| ensemble:mean_probability | A_interactions | B_event_interactions | +0.000149 [-0.000411, +0.000681] | +0.002314 [+0.000724, +0.003865] |
| ensemble:mean_probability | A_interactions_neutral_raw | B_event_interactions_neutral_raw | +0.000097 [-0.000531, +0.000684] | +0.001375 [-0.000519, +0.003173] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.001928 [+0.000658, +0.003059] | +0.004541 [-0.000271, +0.008714] |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.001432 [+0.000288, +0.002499] | +0.003935 [-0.000562, +0.007965] |
| ensemble:mean_probability | B_input_confidence | B_event_input | -0.000104 [-0.001191, +0.000838] | -0.001712 [-0.004609, +0.000731] |
| ensemble:mean_probability | B_interactions_confidence | B_event_interactions | -0.000094 [-0.001131, +0.000858] | -0.001781 [-0.004574, +0.000671] |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | -0.000344 [-0.001645, +0.000760] | -0.003315 [-0.006938, -0.000181] |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.000451 [-0.001330, +0.001998] | -0.001972 [-0.009193, +0.004088] |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.000410 [-0.001401, +0.002021] | -0.001989 [-0.008884, +0.004109] |
| ensemble:mean_probability | B_event_input | B_event_interactions | +0.000157 [-0.000311, +0.000665] | +0.001459 [-0.000672, +0.003747] |
| ensemble:mean_probability | B_event_interactions | B_event_interactions_neutral_raw | -0.000417 [-0.001154, +0.000211] | -0.002203 [-0.004029, -0.000598] |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.000703 [-0.000639, +0.001912] | +0.003000 [-0.000621, +0.006606] |

## All condition, query, load and original-split cells

Calibration-bin counts, means and observed failure rates are retained in the machine-readable review for every cell. Original train/development labels are descriptive strata; the new template folds define the statistical training boundaries.

| Evaluation | Predictor | Axis | Cell | n | Failures | Brier | Log loss |
|---|---|---|---|---:|---:|---:|---:|
| seed:17 | prior | available_bindings | 2 | 3072 | 185 | 0.056789 | 0.229108 |
| seed:17 | prior | available_bindings | 4 | 3072 | 245 | 0.073582 | 0.279622 |
| seed:17 | prior | condition | informative | 3072 | 239 | 0.071867 | 0.274288 |
| seed:17 | prior | condition | misleading | 3072 | 191 | 0.058504 | 0.234442 |
| seed:17 | prior | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.082151 | 0.304866 |
| seed:17 | prior | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.129351 | 0.447719 |
| seed:17 | prior | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.139905 | 0.481810 |
| seed:17 | prior | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.167496 | 0.561746 |
| seed:17 | prior | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.005076 | 0.073892 |
| seed:17 | prior | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.006511 | 0.077015 |
| seed:17 | prior | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.004604 | 0.070173 |
| seed:17 | prior | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.004982 | 0.073148 |
| seed:17 | prior | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.082269 | 0.305764 |
| seed:17 | prior | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.094168 | 0.342294 |
| seed:17 | prior | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.133321 | 0.462659 |
| seed:17 | prior | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.112531 | 0.397002 |
| seed:17 | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.008447 | 0.084090 |
| seed:17 | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.021733 | 0.123315 |
| seed:17 | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.004604 | 0.070173 |
| seed:17 | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.011696 | 0.093325 |
| seed:17 | prior | original_split | development | 1536 | 86 | 0.053193 | 0.218503 |
| seed:17 | prior | original_split | train | 4608 | 344 | 0.069183 | 0.266319 |
| seed:17 | prior | query_role | current | 3072 | 413 | 0.120678 | 0.421647 |
| seed:17 | prior | query_role | saved | 3072 | 17 | 0.009692 | 0.087083 |
| seed:17 | A_input | available_bindings | 2 | 3072 | 185 | 0.040227 | 0.140377 |
| seed:17 | A_input | available_bindings | 4 | 3072 | 245 | 0.039884 | 0.137998 |
| seed:17 | A_input | condition | informative | 3072 | 239 | 0.038123 | 0.128569 |
| seed:17 | A_input | condition | misleading | 3072 | 191 | 0.041988 | 0.149807 |
| seed:17 | A_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064584 | 0.198477 |
| seed:17 | A_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082277 | 0.262504 |
| seed:17 | A_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.074870 | 0.240493 |
| seed:17 | A_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.074558 | 0.256838 |
| seed:17 | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000062 | 0.005011 |
| seed:17 | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001942 | 0.012959 |
| seed:17 | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000104 | 0.006712 |
| seed:17 | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000205 | 0.009086 |
| seed:17 | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.069461 | 0.213845 |
| seed:17 | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068799 | 0.226654 |
| seed:17 | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.078037 | 0.230729 |
| seed:17 | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078404 | 0.260198 |
| seed:17 | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003939 | 0.040342 |
| seed:17 | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019323 | 0.111309 |
| seed:17 | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000051 | 0.004599 |
| seed:17 | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007662 | 0.039763 |
| seed:17 | A_input | original_split | development | 1536 | 86 | 0.035763 | 0.116490 |
| seed:17 | A_input | original_split | train | 4608 | 344 | 0.041486 | 0.146754 |
| seed:17 | A_input | query_role | current | 3072 | 413 | 0.074588 | 0.243237 |
| seed:17 | A_input | query_role | saved | 3072 | 17 | 0.005523 | 0.035139 |
| seed:17 | A_interactions | available_bindings | 2 | 3072 | 185 | 0.040628 | 0.139987 |
| seed:17 | A_interactions | available_bindings | 4 | 3072 | 245 | 0.039353 | 0.136337 |
| seed:17 | A_interactions | condition | informative | 3072 | 239 | 0.037638 | 0.125989 |
| seed:17 | A_interactions | condition | misleading | 3072 | 191 | 0.042343 | 0.150335 |
| seed:17 | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064278 | 0.198167 |
| seed:17 | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083299 | 0.268898 |
| seed:17 | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.074358 | 0.240327 |
| seed:17 | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071856 | 0.247895 |
| seed:17 | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000022 | 0.003216 |
| seed:17 | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001954 | 0.013447 |
| seed:17 | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001650 |
| seed:17 | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.002026 |
| seed:17 | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.070221 | 0.219027 |
| seed:17 | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069904 | 0.229442 |
| seed:17 | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.076767 | 0.228039 |
| seed:17 | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079045 | 0.266863 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004230 | 0.039847 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019234 | 0.098003 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000050 | 0.004809 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007748 | 0.042669 |
| seed:17 | A_interactions | original_split | development | 1536 | 86 | 0.035724 | 0.116278 |
| seed:17 | A_interactions | original_split | train | 4608 | 344 | 0.041413 | 0.145456 |
| seed:17 | A_interactions | query_role | current | 3072 | 413 | 0.074477 | 0.244579 |
| seed:17 | A_interactions | query_role | saved | 3072 | 17 | 0.005504 | 0.031744 |
| seed:17 | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040955 | 0.140823 |
| seed:17 | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039493 | 0.137114 |
| seed:17 | A_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.037713 | 0.126362 |
| seed:17 | A_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.042735 | 0.151575 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065155 | 0.199055 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083781 | 0.271197 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.076894 | 0.247550 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.070979 | 0.246188 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000021 | 0.003190 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001951 | 0.013271 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001684 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.002032 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.070212 | 0.219088 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070961 | 0.232531 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075792 | 0.226844 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080262 | 0.270041 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004223 | 0.039424 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019234 | 0.097563 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000054 | 0.004961 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007766 | 0.043680 |
| seed:17 | A_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.035997 | 0.116879 |
| seed:17 | A_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041633 | 0.146332 |
| seed:17 | A_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.074941 | 0.246114 |
| seed:17 | A_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005507 | 0.031823 |
| seed:17 | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034856 | 0.125351 |
| seed:17 | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.038588 | 0.134477 |
| seed:17 | A_interactions_neutral_scored | condition | informative | 3072 | 239 | 0.032562 | 0.112907 |
| seed:17 | A_interactions_neutral_scored | condition | misleading | 3072 | 191 | 0.040882 | 0.146922 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.043893 | 0.148898 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.069941 | 0.234166 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.066687 | 0.219214 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.067817 | 0.234011 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000019 | 0.003107 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001991 | 0.015430 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000068 | 0.004771 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000020 | 0.002665 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055072 | 0.179949 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.066381 | 0.218978 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075632 | 0.231766 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081107 | 0.272463 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004210 | 0.039486 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019226 | 0.097814 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000069 | 0.005807 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007788 | 0.044038 |
| seed:17 | A_interactions_neutral_scored | original_split | development | 1536 | 86 | 0.029070 | 0.100370 |
| seed:17 | A_interactions_neutral_scored | original_split | train | 4608 | 344 | 0.039273 | 0.139762 |
| seed:17 | A_interactions_neutral_scored | query_role | current | 3072 | 413 | 0.067923 | 0.227234 |
| seed:17 | A_interactions_neutral_scored | query_role | saved | 3072 | 17 | 0.005521 | 0.032594 |
| seed:17 | A_interactions_oracle | available_bindings | 2 | 3072 | 185 | 0.037185 | 0.132295 |
| seed:17 | A_interactions_oracle | available_bindings | 4 | 3072 | 245 | 0.039476 | 0.136501 |
| seed:17 | A_interactions_oracle | condition | informative | 3072 | 239 | 0.034870 | 0.118670 |
| seed:17 | A_interactions_oracle | condition | misleading | 3072 | 191 | 0.041791 | 0.150126 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.053780 | 0.176530 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.074034 | 0.244988 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.078287 | 0.242964 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.069391 | 0.240045 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000027 | 0.003326 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001957 | 0.013315 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000007 | 0.001576 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000012 | 0.002078 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.061109 | 0.196257 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068071 | 0.223798 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.081494 | 0.246044 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080345 | 0.271267 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004315 | 0.042890 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019432 | 0.102171 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000059 | 0.004605 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007767 | 0.042776 |
| seed:17 | A_interactions_oracle | original_split | development | 1536 | 86 | 0.033193 | 0.111100 |
| seed:17 | A_interactions_oracle | original_split | train | 4608 | 344 | 0.040043 | 0.142164 |
| seed:17 | A_interactions_oracle | query_role | current | 3072 | 413 | 0.071111 | 0.236095 |
| seed:17 | A_interactions_oracle | query_role | saved | 3072 | 17 | 0.005550 | 0.032701 |
| seed:17 | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.035310 | 0.128042 |
| seed:17 | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039224 | 0.135317 |
| seed:17 | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.032878 | 0.113754 |
| seed:17 | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.041655 | 0.149605 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.045128 | 0.156915 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.069804 | 0.235132 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.080288 | 0.248151 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.066276 | 0.231075 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000024 | 0.003289 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001956 | 0.013419 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001502 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002092 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055952 | 0.187681 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068020 | 0.224055 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.083370 | 0.252656 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081475 | 0.271922 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004287 | 0.042093 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019382 | 0.100654 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000048 | 0.004372 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007769 | 0.043098 |
| seed:17 | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.031208 | 0.107220 |
| seed:17 | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.039286 | 0.139833 |
| seed:17 | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.068995 | 0.230906 |
| seed:17 | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005539 | 0.032453 |
| seed:17 | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.033812 | 0.122796 |
| seed:17 | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.037913 | 0.132274 |
| seed:17 | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.030969 | 0.107975 |
| seed:17 | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.040756 | 0.147094 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.040237 | 0.140389 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.066057 | 0.222036 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.067320 | 0.219787 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.064660 | 0.225927 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000022 | 0.003190 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001958 | 0.013672 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001480 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000012 | 0.002101 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.053100 | 0.176738 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.066671 | 0.219719 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.077572 | 0.240307 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080526 | 0.269933 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004250 | 0.041227 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019383 | 0.100574 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000045 | 0.004284 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007797 | 0.043780 |
| seed:17 | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.028347 | 0.099079 |
| seed:17 | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.038368 | 0.137020 |
| seed:17 | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.066184 | 0.222528 |
| seed:17 | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005542 | 0.032541 |
| seed:17 | B_input_confidence | available_bindings | 2 | 3072 | 185 | 0.039875 | 0.136406 |
| seed:17 | B_input_confidence | available_bindings | 4 | 3072 | 245 | 0.039705 | 0.133997 |
| seed:17 | B_input_confidence | condition | informative | 3072 | 239 | 0.038055 | 0.125723 |
| seed:17 | B_input_confidence | condition | misleading | 3072 | 191 | 0.041525 | 0.144680 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063172 | 0.195955 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.081422 | 0.255370 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072849 | 0.228023 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075767 | 0.250567 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000036 | 0.003702 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002048 | 0.015226 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000103 | 0.006649 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000250 | 0.009629 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.065836 | 0.202051 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070161 | 0.225458 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075862 | 0.223163 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077096 | 0.250493 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003932 | 0.039529 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019133 | 0.101762 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000046 | 0.004309 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007700 | 0.040070 |
| seed:17 | B_input_confidence | original_split | development | 1536 | 86 | 0.034568 | 0.112051 |
| seed:17 | B_input_confidence | original_split | train | 4608 | 344 | 0.041531 | 0.142918 |
| seed:17 | B_input_confidence | query_role | current | 3072 | 413 | 0.074057 | 0.236492 |
| seed:17 | B_input_confidence | query_role | saved | 3072 | 17 | 0.005523 | 0.033911 |
| seed:17 | B_interactions_confidence | available_bindings | 2 | 3072 | 185 | 0.040228 | 0.135685 |
| seed:17 | B_interactions_confidence | available_bindings | 4 | 3072 | 245 | 0.039040 | 0.131710 |
| seed:17 | B_interactions_confidence | condition | informative | 3072 | 239 | 0.037441 | 0.122716 |
| seed:17 | B_interactions_confidence | condition | misleading | 3072 | 191 | 0.041827 | 0.144679 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063140 | 0.195599 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082704 | 0.262235 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073501 | 0.230129 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071971 | 0.239428 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000011 | 0.002298 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002009 | 0.015287 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001503 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000013 | 0.002108 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066671 | 0.206478 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070716 | 0.226199 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075065 | 0.220336 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077931 | 0.257324 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004175 | 0.038227 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.018943 | 0.089088 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000036 | 0.004015 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007756 | 0.042153 |
| seed:17 | B_interactions_confidence | original_split | development | 1536 | 86 | 0.034717 | 0.111766 |
| seed:17 | B_interactions_confidence | original_split | train | 4608 | 344 | 0.041273 | 0.141008 |
| seed:17 | B_interactions_confidence | query_role | current | 3072 | 413 | 0.073807 | 0.237171 |
| seed:17 | B_interactions_confidence | query_role | saved | 3072 | 17 | 0.005461 | 0.030224 |
| seed:17 | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.040539 | 0.136790 |
| seed:17 | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.038951 | 0.131949 |
| seed:17 | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.037524 | 0.122969 |
| seed:17 | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.041967 | 0.145770 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064983 | 0.199975 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083010 | 0.263162 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073004 | 0.229740 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071482 | 0.238367 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000011 | 0.002280 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002015 | 0.015153 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001536 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000012 | 0.002073 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066435 | 0.205790 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.071369 | 0.229620 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072441 | 0.215740 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078609 | 0.259808 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004172 | 0.037888 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019041 | 0.089839 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000041 | 0.004289 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007764 | 0.042844 |
| seed:17 | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.034724 | 0.111931 |
| seed:17 | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.041419 | 0.141849 |
| seed:17 | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.074011 | 0.238292 |
| seed:17 | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005480 | 0.030447 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.034425 | 0.124340 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.036648 | 0.124641 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.030900 | 0.105291 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.040174 | 0.143690 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.041746 | 0.145780 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.066540 | 0.220575 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.067972 | 0.213518 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.063186 | 0.213113 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000003 | 0.000855 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002004 | 0.017226 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000000 | 0.000379 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000002 | 0.000611 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.050397 | 0.166788 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070269 | 0.231164 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.076311 | 0.231529 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076141 | 0.254231 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004357 | 0.038352 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019488 | 0.101187 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000045 | 0.004050 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007714 | 0.040427 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.028111 | 0.096085 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.038012 | 0.133959 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.065519 | 0.217244 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005555 | 0.031737 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 185 | 0.033607 | 0.119946 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 245 | 0.036156 | 0.123299 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 239 | 0.029813 | 0.101188 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 191 | 0.039950 | 0.142057 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.038222 | 0.131574 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.064391 | 0.209953 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.060198 | 0.195259 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.062650 | 0.210330 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000003 | 0.001063 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002006 | 0.017826 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000377 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000006 | 0.000968 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.049232 | 0.160173 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069948 | 0.227847 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.073096 | 0.230028 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076473 | 0.252790 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004289 | 0.040220 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019426 | 0.097533 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000036 | 0.003594 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007753 | 0.041897 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 86 | 0.026402 | 0.091276 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 344 | 0.037708 | 0.131738 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 413 | 0.064215 | 0.211482 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 17 | 0.005547 | 0.031763 |
| seed:17 | B_event_input | available_bindings | 2 | 3072 | 185 | 0.040078 | 0.138288 |
| seed:17 | B_event_input | available_bindings | 4 | 3072 | 245 | 0.039783 | 0.136036 |
| seed:17 | B_event_input | condition | informative | 3072 | 239 | 0.038413 | 0.127930 |
| seed:17 | B_event_input | condition | misleading | 3072 | 191 | 0.041448 | 0.146394 |
| seed:17 | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064053 | 0.198306 |
| seed:17 | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083322 | 0.262035 |
| seed:17 | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.076387 | 0.243625 |
| seed:17 | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.074971 | 0.253430 |
| seed:17 | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000039 | 0.003932 |
| seed:17 | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001961 | 0.013269 |
| seed:17 | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000119 | 0.006735 |
| seed:17 | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000246 | 0.009424 |
| seed:17 | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.065901 | 0.204828 |
| seed:17 | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068965 | 0.225261 |
| seed:17 | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.079913 | 0.237446 |
| seed:17 | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076779 | 0.252539 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003939 | 0.039989 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019253 | 0.105633 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000048 | 0.004274 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007668 | 0.039165 |
| seed:17 | B_event_input | original_split | development | 1536 | 86 | 0.035361 | 0.115516 |
| seed:17 | B_event_input | original_split | train | 4608 | 344 | 0.041454 | 0.144377 |
| seed:17 | B_event_input | query_role | current | 3072 | 413 | 0.074338 | 0.240265 |
| seed:17 | B_event_input | query_role | saved | 3072 | 17 | 0.005523 | 0.034058 |
| seed:17 | B_event_interactions | available_bindings | 2 | 3072 | 185 | 0.040399 | 0.137737 |
| seed:17 | B_event_interactions | available_bindings | 4 | 3072 | 245 | 0.039147 | 0.133983 |
| seed:17 | B_event_interactions | condition | informative | 3072 | 239 | 0.037762 | 0.124935 |
| seed:17 | B_event_interactions | condition | misleading | 3072 | 191 | 0.041784 | 0.146785 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063851 | 0.197598 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.084206 | 0.268525 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.076195 | 0.243934 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071529 | 0.242871 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000013 | 0.002537 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001957 | 0.013515 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001501 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002044 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.067014 | 0.210023 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069491 | 0.226245 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.079131 | 0.235997 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077548 | 0.259517 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004173 | 0.038414 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019216 | 0.093850 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000034 | 0.003800 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007743 | 0.041641 |
| seed:17 | B_event_interactions | original_split | development | 1536 | 86 | 0.035456 | 0.115198 |
| seed:17 | B_event_interactions | original_split | train | 4608 | 344 | 0.041212 | 0.142747 |
| seed:17 | B_event_interactions | query_role | current | 3072 | 413 | 0.074051 | 0.241091 |
| seed:17 | B_event_interactions | query_role | saved | 3072 | 17 | 0.005495 | 0.030629 |
| seed:17 | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040966 | 0.139828 |
| seed:17 | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039371 | 0.136422 |
| seed:17 | B_event_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.038085 | 0.126823 |
| seed:17 | B_event_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.042252 | 0.149427 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065252 | 0.200034 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.085315 | 0.272160 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.080595 | 0.260297 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.070694 | 0.241968 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000014 | 0.002566 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001995 | 0.015262 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000068 | 0.004882 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000028 | 0.002770 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.067232 | 0.209919 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070872 | 0.230350 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.079646 | 0.245384 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078421 | 0.263916 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004182 | 0.038562 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019272 | 0.095658 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000059 | 0.005192 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007767 | 0.043019 |
| seed:17 | B_event_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.036144 | 0.118160 |
| seed:17 | B_event_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041510 | 0.144780 |
| seed:17 | B_event_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.074814 | 0.244377 |
| seed:17 | B_event_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005523 | 0.031873 |
| seed:17 | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.032803 | 0.121710 |
| seed:17 | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.038031 | 0.134288 |
| seed:17 | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.031441 | 0.108611 |
| seed:17 | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.039394 | 0.147387 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.039683 | 0.141489 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.064765 | 0.218238 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.082612 | 0.263889 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.065127 | 0.224113 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000014 | 0.002317 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001958 | 0.013307 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001017 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000008 | 0.001480 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.046645 | 0.159520 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065208 | 0.219879 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.086664 | 0.304546 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.075787 | 0.261868 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004233 | 0.039684 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019600 | 0.107330 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000034 | 0.003387 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007764 | 0.042552 |
| seed:17 | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.029205 | 0.104905 |
| seed:17 | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.037488 | 0.135697 |
| seed:17 | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.065267 | 0.223034 |
| seed:17 | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005568 | 0.032963 |
| seed:17 | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.032005 | 0.117628 |
| seed:17 | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.036992 | 0.130748 |
| seed:17 | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.030110 | 0.104307 |
| seed:17 | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.038887 | 0.144069 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.035955 | 0.128029 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.062665 | 0.210653 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.069632 | 0.227293 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.064500 | 0.221551 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000012 | 0.002205 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001964 | 0.013856 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001510 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.001662 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.045675 | 0.152473 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.064943 | 0.217662 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.081013 | 0.275138 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.075115 | 0.259814 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004180 | 0.038567 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019545 | 0.102957 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000040 | 0.003820 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007798 | 0.043013 |
| seed:17 | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.026861 | 0.095859 |
| seed:17 | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.037044 | 0.133631 |
| seed:17 | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.063434 | 0.215980 |
| seed:17 | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005563 | 0.032396 |
| seed:29 | prior | available_bindings | 2 | 3072 | 185 | 0.056794 | 0.229129 |
| seed:29 | prior | available_bindings | 4 | 3072 | 245 | 0.073571 | 0.279508 |
| seed:29 | prior | condition | informative | 3072 | 239 | 0.071863 | 0.274239 |
| seed:29 | prior | condition | misleading | 3072 | 191 | 0.058502 | 0.234397 |
| seed:29 | prior | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.082180 | 0.305096 |
| seed:29 | prior | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.129334 | 0.447513 |
| seed:29 | prior | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.139282 | 0.476801 |
| seed:29 | prior | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.167606 | 0.562585 |
| seed:29 | prior | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.005062 | 0.073738 |
| seed:29 | prior | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.006518 | 0.077097 |
| seed:29 | prior | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.004860 | 0.072262 |
| seed:29 | prior | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.004930 | 0.072730 |
| seed:29 | prior | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.082360 | 0.306483 |
| seed:29 | prior | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.094128 | 0.341919 |
| seed:29 | prior | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.132527 | 0.456311 |
| seed:29 | prior | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.112623 | 0.397656 |
| seed:29 | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.008447 | 0.084045 |
| seed:29 | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.021763 | 0.123561 |
| seed:29 | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.004860 | 0.072262 |
| seed:29 | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.011674 | 0.093138 |
| seed:29 | prior | original_split | development | 1536 | 86 | 0.053135 | 0.218030 |
| seed:29 | prior | original_split | train | 4608 | 344 | 0.069198 | 0.266414 |
| seed:29 | prior | query_role | current | 3072 | 413 | 0.120661 | 0.421467 |
| seed:29 | prior | query_role | saved | 3072 | 17 | 0.009703 | 0.087169 |
| seed:29 | A_input | available_bindings | 2 | 3072 | 185 | 0.039919 | 0.139782 |
| seed:29 | A_input | available_bindings | 4 | 3072 | 245 | 0.039680 | 0.137504 |
| seed:29 | A_input | condition | informative | 3072 | 239 | 0.037754 | 0.127931 |
| seed:29 | A_input | condition | misleading | 3072 | 191 | 0.041844 | 0.149355 |
| seed:29 | A_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063926 | 0.198411 |
| seed:29 | A_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.081383 | 0.259541 |
| seed:29 | A_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.071478 | 0.231921 |
| seed:29 | A_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.074403 | 0.257107 |
| seed:29 | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000072 | 0.005397 |
| seed:29 | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001951 | 0.013029 |
| seed:29 | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000121 | 0.007300 |
| seed:29 | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000232 | 0.009538 |
| seed:29 | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.068762 | 0.214220 |
| seed:29 | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068509 | 0.225455 |
| seed:29 | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.073440 | 0.217633 |
| seed:29 | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079169 | 0.262106 |
| seed:29 | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003945 | 0.039608 |
| seed:29 | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019320 | 0.111849 |
| seed:29 | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000064 | 0.005261 |
| seed:29 | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007637 | 0.038844 |
| seed:29 | A_input | original_split | development | 1536 | 86 | 0.034876 | 0.114782 |
| seed:29 | A_input | original_split | train | 4608 | 344 | 0.041440 | 0.146596 |
| seed:29 | A_input | query_role | current | 3072 | 413 | 0.074072 | 0.242119 |
| seed:29 | A_input | query_role | saved | 3072 | 17 | 0.005527 | 0.035166 |
| seed:29 | A_interactions | available_bindings | 2 | 3072 | 185 | 0.040294 | 0.139007 |
| seed:29 | A_interactions | available_bindings | 4 | 3072 | 245 | 0.039471 | 0.136425 |
| seed:29 | A_interactions | condition | informative | 3072 | 239 | 0.037505 | 0.125800 |
| seed:29 | A_interactions | condition | misleading | 3072 | 191 | 0.042260 | 0.149633 |
| seed:29 | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063708 | 0.197397 |
| seed:29 | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082662 | 0.266127 |
| seed:29 | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.071715 | 0.234368 |
| seed:29 | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072484 | 0.250501 |
| seed:29 | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000021 | 0.003197 |
| seed:29 | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001957 | 0.013690 |
| seed:29 | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001574 |
| seed:29 | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000010 | 0.002059 |
| seed:29 | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.069646 | 0.219197 |
| seed:29 | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069111 | 0.226121 |
| seed:29 | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075521 | 0.220647 |
| seed:29 | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079766 | 0.267543 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004258 | 0.040235 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019220 | 0.098092 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000041 | 0.004432 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007743 | 0.042535 |
| seed:29 | A_interactions | original_split | development | 1536 | 86 | 0.035212 | 0.115090 |
| seed:29 | A_interactions | original_split | train | 4608 | 344 | 0.041439 | 0.145259 |
| seed:29 | A_interactions | query_role | current | 3072 | 413 | 0.074262 | 0.243642 |
| seed:29 | A_interactions | query_role | saved | 3072 | 17 | 0.005503 | 0.031790 |
| seed:29 | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040725 | 0.140610 |
| seed:29 | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039956 | 0.138316 |
| seed:29 | A_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.037869 | 0.127381 |
| seed:29 | A_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.042813 | 0.151545 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065240 | 0.201595 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083413 | 0.270648 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072504 | 0.236323 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072860 | 0.251801 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000058 | 0.005018 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001903 | 0.011828 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001566 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000036 | 0.003424 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.070680 | 0.224868 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069774 | 0.228157 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074764 | 0.219754 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081656 | 0.272309 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004193 | 0.039092 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019177 | 0.097743 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000044 | 0.004483 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007772 | 0.043957 |
| seed:29 | A_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.035638 | 0.116939 |
| seed:29 | A_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041908 | 0.146971 |
| seed:29 | A_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.075185 | 0.246866 |
| seed:29 | A_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005496 | 0.032061 |
| seed:29 | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034372 | 0.123930 |
| seed:29 | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.039342 | 0.136128 |
| seed:29 | A_interactions_neutral_scored | condition | informative | 3072 | 239 | 0.032399 | 0.112019 |
| seed:29 | A_interactions_neutral_scored | condition | misleading | 3072 | 191 | 0.041315 | 0.148039 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.044105 | 0.148558 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.068022 | 0.227868 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.061609 | 0.204366 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.069549 | 0.240290 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000019 | 0.003102 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001958 | 0.013935 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001501 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000010 | 0.002122 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055722 | 0.183311 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.064952 | 0.215009 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.071929 | 0.219833 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.084766 | 0.280409 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004247 | 0.040140 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019254 | 0.099215 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000037 | 0.004175 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007798 | 0.044619 |
| seed:29 | A_interactions_neutral_scored | original_split | development | 1536 | 86 | 0.028480 | 0.098342 |
| seed:29 | A_interactions_neutral_scored | original_split | train | 4608 | 344 | 0.039649 | 0.140592 |
| seed:29 | A_interactions_neutral_scored | query_role | current | 3072 | 413 | 0.068194 | 0.227622 |
| seed:29 | A_interactions_neutral_scored | query_role | saved | 3072 | 17 | 0.005519 | 0.032436 |
| seed:29 | A_interactions_oracle | available_bindings | 2 | 3072 | 185 | 0.036784 | 0.131191 |
| seed:29 | A_interactions_oracle | available_bindings | 4 | 3072 | 245 | 0.040043 | 0.138216 |
| seed:29 | A_interactions_oracle | condition | informative | 3072 | 239 | 0.034914 | 0.118866 |
| seed:29 | A_interactions_oracle | condition | misleading | 3072 | 191 | 0.041913 | 0.150542 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.053083 | 0.174715 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.073019 | 0.240809 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.076233 | 0.239397 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071104 | 0.246352 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000022 | 0.002926 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001955 | 0.013102 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001454 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.001848 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.060352 | 0.195483 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067321 | 0.221326 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.079271 | 0.236370 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.082205 | 0.276382 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004383 | 0.043482 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019488 | 0.103609 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000046 | 0.004093 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007773 | 0.042593 |
| seed:29 | A_interactions_oracle | original_split | development | 1536 | 86 | 0.032603 | 0.109544 |
| seed:29 | A_interactions_oracle | original_split | train | 4608 | 344 | 0.040350 | 0.143091 |
| seed:29 | A_interactions_oracle | query_role | current | 3072 | 413 | 0.071262 | 0.236599 |
| seed:29 | A_interactions_oracle | query_role | saved | 3072 | 17 | 0.005565 | 0.032809 |
| seed:29 | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.035111 | 0.127706 |
| seed:29 | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.040014 | 0.136990 |
| seed:29 | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.033047 | 0.114225 |
| seed:29 | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.042078 | 0.150472 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.044859 | 0.156280 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.069136 | 0.232800 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.078068 | 0.242891 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.068173 | 0.236458 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000022 | 0.003259 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001956 | 0.013444 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001360 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000012 | 0.002159 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.056644 | 0.191798 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067286 | 0.221848 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.081984 | 0.245571 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.084092 | 0.277093 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004307 | 0.042216 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019373 | 0.101370 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000036 | 0.003823 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007773 | 0.043114 |
| seed:29 | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.030980 | 0.106729 |
| seed:29 | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.039757 | 0.140888 |
| seed:29 | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.069586 | 0.232124 |
| seed:29 | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005539 | 0.032573 |
| seed:29 | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.033453 | 0.121876 |
| seed:29 | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.039422 | 0.136514 |
| seed:29 | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.031256 | 0.108896 |
| seed:29 | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.041619 | 0.149493 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.039998 | 0.138987 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.065174 | 0.217917 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.065998 | 0.217008 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.067110 | 0.235357 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000021 | 0.003211 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001952 | 0.013137 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000003 | 0.000921 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002037 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.053302 | 0.179097 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065350 | 0.216627 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.076984 | 0.238238 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.085719 | 0.282850 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004287 | 0.041712 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019439 | 0.102070 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000030 | 0.003376 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007782 | 0.043112 |
| seed:29 | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.028186 | 0.098796 |
| seed:29 | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.039188 | 0.139327 |
| seed:29 | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.067326 | 0.225860 |
| seed:29 | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005549 | 0.032530 |
| seed:29 | B_input_confidence | available_bindings | 2 | 3072 | 185 | 0.039586 | 0.135736 |
| seed:29 | B_input_confidence | available_bindings | 4 | 3072 | 245 | 0.039897 | 0.134344 |
| seed:29 | B_input_confidence | condition | informative | 3072 | 239 | 0.037794 | 0.125020 |
| seed:29 | B_input_confidence | condition | misleading | 3072 | 191 | 0.041690 | 0.145061 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.062736 | 0.195922 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.079787 | 0.251552 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072219 | 0.224749 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.076133 | 0.251181 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000037 | 0.003875 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002003 | 0.014521 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000105 | 0.006801 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000271 | 0.009828 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066079 | 0.204702 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070232 | 0.225018 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.073664 | 0.217819 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078201 | 0.253497 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003933 | 0.037781 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019100 | 0.102187 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000054 | 0.004759 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007694 | 0.039522 |
| seed:29 | B_input_confidence | original_split | development | 1536 | 86 | 0.034301 | 0.111557 |
| seed:29 | B_input_confidence | original_split | train | 4608 | 344 | 0.041555 | 0.142868 |
| seed:29 | B_input_confidence | query_role | current | 3072 | 413 | 0.073969 | 0.236395 |
| seed:29 | B_input_confidence | query_role | saved | 3072 | 17 | 0.005514 | 0.033686 |
| seed:29 | B_interactions_confidence | available_bindings | 2 | 3072 | 185 | 0.040040 | 0.135213 |
| seed:29 | B_interactions_confidence | available_bindings | 4 | 3072 | 245 | 0.039280 | 0.132268 |
| seed:29 | B_interactions_confidence | condition | informative | 3072 | 239 | 0.037445 | 0.123020 |
| seed:29 | B_interactions_confidence | condition | misleading | 3072 | 191 | 0.041874 | 0.144460 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.062667 | 0.195740 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082112 | 0.260651 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.070741 | 0.224439 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.073227 | 0.243409 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000010 | 0.002282 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001982 | 0.015046 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001477 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000013 | 0.002140 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066823 | 0.209297 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070488 | 0.224875 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072185 | 0.211591 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078946 | 0.258735 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004177 | 0.037710 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.018818 | 0.088191 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000035 | 0.003779 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007762 | 0.042345 |
| seed:29 | B_interactions_confidence | original_split | development | 1536 | 86 | 0.034193 | 0.110945 |
| seed:29 | B_interactions_confidence | original_split | train | 4608 | 344 | 0.041482 | 0.141339 |
| seed:29 | B_interactions_confidence | query_role | current | 3072 | 413 | 0.073882 | 0.237455 |
| seed:29 | B_interactions_confidence | query_role | saved | 3072 | 17 | 0.005437 | 0.030025 |
| seed:29 | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.040254 | 0.136530 |
| seed:29 | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.039555 | 0.133093 |
| seed:29 | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.037646 | 0.123725 |
| seed:29 | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.042162 | 0.145898 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064758 | 0.203757 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082600 | 0.262332 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.069187 | 0.220157 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.073282 | 0.243908 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000009 | 0.002036 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001978 | 0.014571 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001482 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000010 | 0.001807 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066273 | 0.210144 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070353 | 0.226927 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.070994 | 0.209853 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080763 | 0.263476 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004218 | 0.034238 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.018962 | 0.090264 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000036 | 0.003906 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007762 | 0.042578 |
| seed:29 | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.034228 | 0.111312 |
| seed:29 | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.041796 | 0.142645 |
| seed:29 | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.074345 | 0.239657 |
| seed:29 | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005463 | 0.029967 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.034206 | 0.123791 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.038096 | 0.128750 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.031292 | 0.106354 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.041010 | 0.146188 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.041421 | 0.147351 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.065846 | 0.218907 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.068905 | 0.213377 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.065603 | 0.221921 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000004 | 0.001300 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001960 | 0.012902 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000383 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000004 | 0.000917 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.051113 | 0.173528 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069503 | 0.229186 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.076732 | 0.230832 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080403 | 0.264682 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004307 | 0.036949 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019507 | 0.102186 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000026 | 0.003335 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007717 | 0.040896 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.028279 | 0.097182 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.038775 | 0.135967 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.066755 | 0.221307 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005547 | 0.031235 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 185 | 0.033057 | 0.118898 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 245 | 0.037699 | 0.128288 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 239 | 0.030082 | 0.103072 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 191 | 0.040675 | 0.144114 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.037364 | 0.131925 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.063393 | 0.207675 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.060254 | 0.194615 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.065098 | 0.221806 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000002 | 0.000812 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001975 | 0.017557 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000381 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000003 | 0.000659 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.048125 | 0.160573 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068664 | 0.224735 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.071751 | 0.224707 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081725 | 0.267804 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004355 | 0.037748 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019389 | 0.097888 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000022 | 0.003008 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007727 | 0.040970 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 86 | 0.025976 | 0.090402 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 344 | 0.038512 | 0.134656 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 413 | 0.065222 | 0.215917 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 17 | 0.005535 | 0.031268 |
| seed:29 | B_event_input | available_bindings | 2 | 3072 | 185 | 0.039840 | 0.137371 |
| seed:29 | B_event_input | available_bindings | 4 | 3072 | 245 | 0.039751 | 0.135802 |
| seed:29 | B_event_input | condition | informative | 3072 | 239 | 0.038291 | 0.127597 |
| seed:29 | B_event_input | condition | misleading | 3072 | 191 | 0.041299 | 0.145576 |
| seed:29 | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063360 | 0.196958 |
| seed:29 | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082820 | 0.260158 |
| seed:29 | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.074245 | 0.238404 |
| seed:29 | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075479 | 0.254692 |
| seed:29 | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000043 | 0.004184 |
| seed:29 | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001961 | 0.013239 |
| seed:29 | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000129 | 0.007026 |
| seed:29 | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000254 | 0.009513 |
| seed:29 | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.065542 | 0.205384 |
| seed:29 | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068651 | 0.224268 |
| seed:29 | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.076910 | 0.229565 |
| seed:29 | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077147 | 0.253011 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003940 | 0.038590 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019162 | 0.104004 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000057 | 0.004638 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007654 | 0.038706 |
| seed:29 | B_event_input | original_split | development | 1536 | 86 | 0.034759 | 0.114155 |
| seed:29 | B_event_input | original_split | train | 4608 | 344 | 0.041474 | 0.144064 |
| seed:29 | B_event_input | query_role | current | 3072 | 413 | 0.074082 | 0.239536 |
| seed:29 | B_event_input | query_role | saved | 3072 | 17 | 0.005508 | 0.033637 |
| seed:29 | B_event_interactions | available_bindings | 2 | 3072 | 185 | 0.040134 | 0.136491 |
| seed:29 | B_event_interactions | available_bindings | 4 | 3072 | 245 | 0.039309 | 0.134038 |
| seed:29 | B_event_interactions | condition | informative | 3072 | 239 | 0.037792 | 0.125045 |
| seed:29 | B_event_interactions | condition | misleading | 3072 | 191 | 0.041651 | 0.145483 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063108 | 0.196076 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083976 | 0.266713 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.074078 | 0.239080 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072578 | 0.246233 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000015 | 0.002642 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001959 | 0.013713 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001437 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002054 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066382 | 0.210259 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069015 | 0.223898 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.078316 | 0.229144 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077868 | 0.258848 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004198 | 0.038191 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019002 | 0.091036 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000030 | 0.003554 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007742 | 0.041604 |
| seed:29 | B_event_interactions | original_split | development | 1536 | 86 | 0.034986 | 0.113963 |
| seed:29 | B_event_interactions | original_split | train | 4608 | 344 | 0.041300 | 0.142365 |
| seed:29 | B_event_interactions | query_role | current | 3072 | 413 | 0.073982 | 0.240364 |
| seed:29 | B_event_interactions | query_role | saved | 3072 | 17 | 0.005461 | 0.030164 |
| seed:29 | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040281 | 0.137455 |
| seed:29 | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039768 | 0.136452 |
| seed:29 | B_event_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.037941 | 0.126041 |
| seed:29 | B_event_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.042109 | 0.147866 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064373 | 0.200205 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083801 | 0.267171 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.074354 | 0.238575 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072870 | 0.248489 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000046 | 0.004421 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001910 | 0.011899 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001540 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000038 | 0.003377 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.067250 | 0.214450 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069027 | 0.224996 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.077954 | 0.231992 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079746 | 0.265017 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004187 | 0.038339 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019022 | 0.091957 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000039 | 0.003897 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007764 | 0.042885 |
| seed:29 | B_event_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.035339 | 0.115903 |
| seed:29 | B_event_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041587 | 0.143970 |
| seed:29 | B_event_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.074581 | 0.243170 |
| seed:29 | B_event_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005469 | 0.030737 |
| seed:29 | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.032415 | 0.120013 |
| seed:29 | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.038812 | 0.136516 |
| seed:29 | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.031705 | 0.109677 |
| seed:29 | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.039522 | 0.146852 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.038628 | 0.137656 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.064404 | 0.217868 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.082429 | 0.266643 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.067141 | 0.230215 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000018 | 0.002487 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001959 | 0.013473 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000292 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.001719 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.046917 | 0.161225 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.063821 | 0.217763 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.086831 | 0.316378 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077526 | 0.263461 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004268 | 0.039300 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019390 | 0.100642 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000016 | 0.002091 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007766 | 0.042801 |
| seed:29 | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.029078 | 0.105562 |
| seed:29 | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.037792 | 0.135832 |
| seed:29 | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.065691 | 0.224654 |
| seed:29 | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005536 | 0.031876 |
| seed:29 | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.031550 | 0.115959 |
| seed:29 | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.038447 | 0.135534 |
| seed:29 | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.030621 | 0.106123 |
| seed:29 | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.039376 | 0.145370 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.034882 | 0.123666 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.062180 | 0.208936 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072496 | 0.240827 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.067201 | 0.231048 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000016 | 0.002373 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001959 | 0.013547 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000271 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.001723 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.045624 | 0.152962 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.063439 | 0.215601 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.082404 | 0.301052 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078576 | 0.266274 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004222 | 0.038477 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019349 | 0.098933 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000012 | 0.001856 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007777 | 0.042717 |
| seed:29 | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.027033 | 0.098247 |
| seed:29 | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.037653 | 0.134913 |
| seed:29 | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.064470 | 0.219995 |
| seed:29 | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005527 | 0.031498 |
| seed:43 | prior | available_bindings | 2 | 3072 | 185 | 0.056716 | 0.228538 |
| seed:43 | prior | available_bindings | 4 | 3072 | 245 | 0.073485 | 0.278852 |
| seed:43 | prior | condition | informative | 3072 | 239 | 0.071823 | 0.273931 |
| seed:43 | prior | condition | misleading | 3072 | 191 | 0.058378 | 0.233459 |
| seed:43 | prior | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.082124 | 0.304651 |
| seed:43 | prior | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.129298 | 0.447211 |
| seed:43 | prior | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.139154 | 0.475817 |
| seed:43 | prior | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.167501 | 0.561686 |
| seed:43 | prior | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.005046 | 0.073680 |
| seed:43 | prior | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.006523 | 0.077177 |
| seed:43 | prior | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.005025 | 0.073522 |
| seed:43 | prior | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.004888 | 0.072473 |
| seed:43 | prior | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.082110 | 0.304547 |
| seed:43 | prior | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.093952 | 0.340557 |
| seed:43 | prior | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.132472 | 0.455888 |
| seed:43 | prior | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.112386 | 0.395802 |
| seed:43 | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.008394 | 0.083703 |
| seed:43 | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.021685 | 0.122994 |
| seed:43 | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.005025 | 0.073522 |
| seed:43 | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.011620 | 0.092780 |
| seed:43 | prior | original_split | development | 1536 | 86 | 0.053085 | 0.217659 |
| seed:43 | prior | original_split | train | 4608 | 344 | 0.069106 | 0.265707 |
| seed:43 | prior | query_role | current | 3072 | 413 | 0.120522 | 0.420359 |
| seed:43 | prior | query_role | saved | 3072 | 17 | 0.009679 | 0.087032 |
| seed:43 | A_input | available_bindings | 2 | 3072 | 185 | 0.039388 | 0.138349 |
| seed:43 | A_input | available_bindings | 4 | 3072 | 245 | 0.039623 | 0.137304 |
| seed:43 | A_input | condition | informative | 3072 | 239 | 0.037973 | 0.128448 |
| seed:43 | A_input | condition | misleading | 3072 | 191 | 0.041038 | 0.147204 |
| seed:43 | A_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063479 | 0.196808 |
| seed:43 | A_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.081952 | 0.261710 |
| seed:43 | A_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073371 | 0.235721 |
| seed:43 | A_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.074812 | 0.257877 |
| seed:43 | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000091 | 0.005980 |
| seed:43 | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001941 | 0.012847 |
| seed:43 | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000160 | 0.008056 |
| seed:43 | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000209 | 0.009159 |
| seed:43 | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066116 | 0.205317 |
| seed:43 | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.066324 | 0.222032 |
| seed:43 | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074775 | 0.222652 |
| seed:43 | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077810 | 0.257470 |
| seed:43 | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003948 | 0.037613 |
| seed:43 | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019294 | 0.110645 |
| seed:43 | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000075 | 0.005519 |
| seed:43 | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007681 | 0.040162 |
| seed:43 | A_input | original_split | development | 1536 | 86 | 0.034637 | 0.113615 |
| seed:43 | A_input | original_split | train | 4608 | 344 | 0.041128 | 0.145897 |
| seed:43 | A_input | query_role | current | 3072 | 413 | 0.073481 | 0.240597 |
| seed:43 | A_input | query_role | saved | 3072 | 17 | 0.005529 | 0.035056 |
| seed:43 | A_interactions | available_bindings | 2 | 3072 | 185 | 0.039789 | 0.138127 |
| seed:43 | A_interactions | available_bindings | 4 | 3072 | 245 | 0.038845 | 0.134603 |
| seed:43 | A_interactions | condition | informative | 3072 | 239 | 0.037456 | 0.125669 |
| seed:43 | A_interactions | condition | misleading | 3072 | 191 | 0.041178 | 0.147061 |
| seed:43 | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063688 | 0.197166 |
| seed:43 | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083119 | 0.268732 |
| seed:43 | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073682 | 0.237316 |
| seed:43 | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071497 | 0.247219 |
| seed:43 | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000031 | 0.003776 |
| seed:43 | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001954 | 0.013470 |
| seed:43 | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000007 | 0.001775 |
| seed:43 | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.002038 |
| seed:43 | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066494 | 0.210025 |
| seed:43 | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067145 | 0.222821 |
| seed:43 | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072396 | 0.215489 |
| seed:43 | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077974 | 0.262046 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004389 | 0.041156 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019213 | 0.097677 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000092 | 0.006489 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007742 | 0.042579 |
| seed:43 | A_interactions | original_split | development | 1536 | 86 | 0.034615 | 0.113776 |
| seed:43 | A_interactions | original_split | train | 4608 | 344 | 0.040884 | 0.143895 |
| seed:43 | A_interactions | query_role | current | 3072 | 413 | 0.073119 | 0.240822 |
| seed:43 | A_interactions | query_role | saved | 3072 | 17 | 0.005515 | 0.031908 |
| seed:43 | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040424 | 0.139957 |
| seed:43 | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039306 | 0.136239 |
| seed:43 | A_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.037961 | 0.127421 |
| seed:43 | A_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.041769 | 0.148775 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065254 | 0.199481 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083983 | 0.272726 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.078417 | 0.251886 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071655 | 0.248542 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000030 | 0.003728 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001955 | 0.013524 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000008 | 0.001781 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000010 | 0.002059 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.068657 | 0.215712 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068257 | 0.226472 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072676 | 0.217993 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079003 | 0.264069 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004378 | 0.040485 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019190 | 0.097315 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000098 | 0.006567 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007761 | 0.043631 |
| seed:43 | A_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.035653 | 0.116420 |
| seed:43 | A_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041269 | 0.145324 |
| seed:43 | A_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.074215 | 0.244171 |
| seed:43 | A_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005515 | 0.032024 |
| seed:43 | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034870 | 0.125267 |
| seed:43 | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.038143 | 0.132549 |
| seed:43 | A_interactions_neutral_scored | condition | informative | 3072 | 239 | 0.032574 | 0.112651 |
| seed:43 | A_interactions_neutral_scored | condition | misleading | 3072 | 191 | 0.040439 | 0.145166 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.045535 | 0.153279 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.069816 | 0.233736 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.065604 | 0.215777 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.067580 | 0.234219 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000027 | 0.003613 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001959 | 0.013960 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000007 | 0.001707 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000010 | 0.002094 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055762 | 0.181631 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065363 | 0.216134 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.071504 | 0.218697 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080286 | 0.267512 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004348 | 0.040637 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019247 | 0.098192 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000083 | 0.006119 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007770 | 0.043952 |
| seed:43 | A_interactions_neutral_scored | original_split | development | 1536 | 86 | 0.029045 | 0.100052 |
| seed:43 | A_interactions_neutral_scored | original_split | train | 4608 | 344 | 0.038994 | 0.138527 |
| seed:43 | A_interactions_neutral_scored | query_role | current | 3072 | 413 | 0.067490 | 0.225518 |
| seed:43 | A_interactions_neutral_scored | query_role | saved | 3072 | 17 | 0.005523 | 0.032299 |
| seed:43 | A_interactions_oracle | available_bindings | 2 | 3072 | 185 | 0.036405 | 0.130373 |
| seed:43 | A_interactions_oracle | available_bindings | 4 | 3072 | 245 | 0.039205 | 0.135308 |
| seed:43 | A_interactions_oracle | condition | informative | 3072 | 239 | 0.034699 | 0.118269 |
| seed:43 | A_interactions_oracle | condition | misleading | 3072 | 191 | 0.040911 | 0.147412 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.052847 | 0.173611 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.073782 | 0.244443 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.079474 | 0.246978 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.068908 | 0.239218 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000035 | 0.003507 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001955 | 0.013166 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001006 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.001942 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.057313 | 0.185831 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065847 | 0.218894 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.078847 | 0.237363 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079836 | 0.267811 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004547 | 0.044139 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019477 | 0.102189 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000080 | 0.005384 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007749 | 0.042362 |
| seed:43 | A_interactions_oracle | original_split | development | 1536 | 86 | 0.032324 | 0.108742 |
| seed:43 | A_interactions_oracle | original_split | train | 4608 | 344 | 0.039632 | 0.140873 |
| seed:43 | A_interactions_oracle | query_role | current | 3072 | 413 | 0.070037 | 0.232988 |
| seed:43 | A_interactions_oracle | query_role | saved | 3072 | 17 | 0.005574 | 0.032693 |
| seed:43 | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.035196 | 0.128046 |
| seed:43 | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.038938 | 0.134062 |
| seed:43 | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.033094 | 0.114755 |
| seed:43 | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.041041 | 0.147353 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.045010 | 0.156294 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.070693 | 0.238666 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.081139 | 0.253023 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.066472 | 0.231954 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000033 | 0.003765 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001959 | 0.013630 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001488 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002109 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.054819 | 0.184430 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067038 | 0.222166 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.079252 | 0.238735 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080573 | 0.266950 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004427 | 0.042710 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019344 | 0.100217 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000070 | 0.005402 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007754 | 0.042755 |
| seed:43 | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.030754 | 0.106087 |
| seed:43 | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.039172 | 0.139377 |
| seed:43 | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.068592 | 0.229627 |
| seed:43 | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005543 | 0.032481 |
| seed:43 | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034138 | 0.123883 |
| seed:43 | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.037919 | 0.131858 |
| seed:43 | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.031487 | 0.109885 |
| seed:43 | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.040570 | 0.145857 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.040978 | 0.142282 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.067838 | 0.227702 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.069475 | 0.227680 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.064991 | 0.227889 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000029 | 0.003669 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001960 | 0.013866 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001470 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002093 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.053150 | 0.176399 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.066408 | 0.219391 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074494 | 0.227975 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080440 | 0.267250 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004382 | 0.042002 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019352 | 0.100165 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000065 | 0.005315 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007763 | 0.043199 |
| seed:43 | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.028427 | 0.099262 |
| seed:43 | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.038563 | 0.137407 |
| seed:43 | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.066515 | 0.223212 |
| seed:43 | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005542 | 0.032530 |
| seed:43 | B_input_confidence | available_bindings | 2 | 3072 | 185 | 0.039303 | 0.135202 |
| seed:43 | B_input_confidence | available_bindings | 4 | 3072 | 245 | 0.039470 | 0.133563 |
| seed:43 | B_input_confidence | condition | informative | 3072 | 239 | 0.038007 | 0.125767 |
| seed:43 | B_input_confidence | condition | misleading | 3072 | 191 | 0.040766 | 0.142998 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.061365 | 0.191811 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082161 | 0.258111 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073126 | 0.228721 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075647 | 0.250534 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000043 | 0.004161 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002009 | 0.014555 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000148 | 0.007863 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000231 | 0.009313 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.062536 | 0.193726 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068566 | 0.222999 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074030 | 0.220584 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076397 | 0.248561 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003932 | 0.035888 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019144 | 0.102756 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000066 | 0.005111 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007705 | 0.040239 |
| seed:43 | B_input_confidence | original_split | development | 1536 | 86 | 0.033594 | 0.109454 |
| seed:43 | B_input_confidence | original_split | train | 4608 | 344 | 0.041317 | 0.142692 |
| seed:43 | B_input_confidence | query_role | current | 3072 | 413 | 0.073254 | 0.235012 |
| seed:43 | B_input_confidence | query_role | saved | 3072 | 17 | 0.005519 | 0.033753 |
| seed:43 | B_interactions_confidence | available_bindings | 2 | 3072 | 185 | 0.039577 | 0.134347 |
| seed:43 | B_interactions_confidence | available_bindings | 4 | 3072 | 245 | 0.038788 | 0.130830 |
| seed:43 | B_interactions_confidence | condition | informative | 3072 | 239 | 0.037478 | 0.122991 |
| seed:43 | B_interactions_confidence | condition | misleading | 3072 | 191 | 0.040887 | 0.142185 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.061761 | 0.192322 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083285 | 0.264544 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.074860 | 0.232819 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071984 | 0.239782 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000013 | 0.002545 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001984 | 0.015048 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001633 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002066 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.062752 | 0.197046 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068937 | 0.222619 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072398 | 0.213993 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076971 | 0.253230 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004215 | 0.037522 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.018885 | 0.089154 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000065 | 0.005280 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007751 | 0.042159 |
| seed:43 | B_interactions_confidence | original_split | development | 1536 | 86 | 0.033735 | 0.109383 |
| seed:43 | B_interactions_confidence | original_split | train | 4608 | 344 | 0.040999 | 0.140323 |
| seed:43 | B_interactions_confidence | query_role | current | 3072 | 413 | 0.072915 | 0.234969 |
| seed:43 | B_interactions_confidence | query_role | saved | 3072 | 17 | 0.005451 | 0.030207 |
| seed:43 | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.040180 | 0.136393 |
| seed:43 | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.038842 | 0.131138 |
| seed:43 | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.037902 | 0.124115 |
| seed:43 | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.041120 | 0.143416 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064447 | 0.197752 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083953 | 0.268230 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072610 | 0.230284 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072870 | 0.241791 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000009 | 0.001883 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001979 | 0.014508 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001117 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000008 | 0.001635 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.064283 | 0.199698 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069668 | 0.227102 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.071864 | 0.212143 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076890 | 0.253347 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004342 | 0.039392 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.018940 | 0.089153 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000065 | 0.005205 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007763 | 0.042940 |
| seed:43 | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.034225 | 0.110516 |
| seed:43 | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.041273 | 0.141515 |
| seed:43 | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.073551 | 0.237264 |
| seed:43 | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005471 | 0.030266 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.034708 | 0.125421 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.037171 | 0.126039 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.031610 | 0.107887 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.040269 | 0.143574 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.040786 | 0.141795 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.069328 | 0.229378 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.069495 | 0.220803 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.064456 | 0.217428 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000004 | 0.001062 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001987 | 0.018249 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000407 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000005 | 0.000941 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.049644 | 0.164405 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069972 | 0.230581 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074362 | 0.224777 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077436 | 0.255492 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004502 | 0.039893 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019492 | 0.100743 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000055 | 0.004676 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007741 | 0.040993 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.027815 | 0.095415 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.038647 | 0.135835 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.066307 | 0.219267 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005571 | 0.032193 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 185 | 0.033910 | 0.120925 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 245 | 0.036455 | 0.124019 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 239 | 0.030468 | 0.103860 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 191 | 0.039896 | 0.141084 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.037403 | 0.129936 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.067878 | 0.220571 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.061709 | 0.203009 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.063046 | 0.213203 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000003 | 0.001017 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001983 | 0.018505 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000408 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000006 | 0.000998 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.047572 | 0.155257 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069497 | 0.226962 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.070144 | 0.217867 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077799 | 0.254691 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004433 | 0.038957 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019393 | 0.096930 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000044 | 0.004261 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007752 | 0.041290 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 86 | 0.025893 | 0.089657 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 344 | 0.038278 | 0.133410 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 413 | 0.064814 | 0.213369 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 17 | 0.005550 | 0.031575 |
| seed:43 | B_event_input | available_bindings | 2 | 3072 | 185 | 0.039403 | 0.136341 |
| seed:43 | B_event_input | available_bindings | 4 | 3072 | 245 | 0.039588 | 0.135575 |
| seed:43 | B_event_input | condition | informative | 3072 | 239 | 0.038391 | 0.128209 |
| seed:43 | B_event_input | condition | misleading | 3072 | 191 | 0.040600 | 0.143707 |
| seed:43 | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.062549 | 0.195386 |
| seed:43 | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083965 | 0.264327 |
| seed:43 | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.075094 | 0.239278 |
| seed:43 | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075203 | 0.254718 |
| seed:43 | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000059 | 0.004821 |
| seed:43 | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001952 | 0.012942 |
| seed:43 | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000186 | 0.008238 |
| seed:43 | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000241 | 0.009283 |
| seed:43 | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.062625 | 0.196514 |
| seed:43 | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.066740 | 0.221152 |
| seed:43 | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.076710 | 0.229582 |
| seed:43 | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076495 | 0.251498 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003945 | 0.036931 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019169 | 0.102796 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000065 | 0.004967 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007673 | 0.038850 |
| seed:43 | B_event_input | original_split | development | 1536 | 86 | 0.034201 | 0.112447 |
| seed:43 | B_event_input | original_split | train | 4608 | 344 | 0.041260 | 0.143795 |
| seed:43 | B_event_input | query_role | current | 3072 | 413 | 0.073478 | 0.238569 |
| seed:43 | B_event_input | query_role | saved | 3072 | 17 | 0.005513 | 0.033347 |
| seed:43 | B_event_interactions | available_bindings | 2 | 3072 | 185 | 0.039673 | 0.135719 |
| seed:43 | B_event_interactions | available_bindings | 4 | 3072 | 245 | 0.038880 | 0.132832 |
| seed:43 | B_event_interactions | condition | informative | 3072 | 239 | 0.037767 | 0.125126 |
| seed:43 | B_event_interactions | condition | misleading | 3072 | 191 | 0.040786 | 0.143425 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.062779 | 0.195096 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.084664 | 0.269866 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.075811 | 0.240874 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071687 | 0.243936 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000019 | 0.003016 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001959 | 0.013687 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000008 | 0.001680 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000012 | 0.002069 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.063384 | 0.201181 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067127 | 0.220690 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075391 | 0.223869 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076941 | 0.256036 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004299 | 0.039011 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019044 | 0.090920 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000065 | 0.005226 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007732 | 0.041222 |
| seed:43 | B_event_interactions | original_split | development | 1536 | 86 | 0.034353 | 0.112355 |
| seed:43 | B_event_interactions | original_split | train | 4608 | 344 | 0.040918 | 0.141582 |
| seed:43 | B_event_interactions | query_role | current | 3072 | 413 | 0.073076 | 0.238307 |
| seed:43 | B_event_interactions | query_role | saved | 3072 | 17 | 0.005477 | 0.030243 |
| seed:43 | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040426 | 0.139452 |
| seed:43 | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.040041 | 0.137096 |
| seed:43 | B_event_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.038835 | 0.129562 |
| seed:43 | B_event_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.041631 | 0.146986 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065695 | 0.201051 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.086154 | 0.278259 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.083780 | 0.264430 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072811 | 0.248968 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000016 | 0.002588 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001962 | 0.014265 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001157 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000062 | 0.004337 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.065600 | 0.205356 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067352 | 0.223720 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.080347 | 0.246806 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078740 | 0.259100 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004363 | 0.039556 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019247 | 0.096194 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000057 | 0.004554 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007744 | 0.042265 |
| seed:43 | B_event_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.036295 | 0.117837 |
| seed:43 | B_event_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041546 | 0.145086 |
| seed:43 | B_event_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.074937 | 0.244679 |
| seed:43 | B_event_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005529 | 0.031869 |
| seed:43 | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.032892 | 0.121371 |
| seed:43 | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.037669 | 0.131935 |
| seed:43 | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.031696 | 0.110262 |
| seed:43 | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.038865 | 0.143044 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.040208 | 0.143572 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.067063 | 0.225389 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.083368 | 0.268877 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.064141 | 0.223054 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000020 | 0.002705 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001965 | 0.014327 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001095 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.001923 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.046126 | 0.159583 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.063440 | 0.213600 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.084028 | 0.284094 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.075430 | 0.255572 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004478 | 0.041241 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019466 | 0.101359 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000057 | 0.004353 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007738 | 0.041054 |
| seed:43 | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.029094 | 0.104385 |
| seed:43 | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.037343 | 0.134076 |
| seed:43 | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.064997 | 0.221182 |
| seed:43 | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005564 | 0.032124 |
| seed:43 | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.032483 | 0.118404 |
| seed:43 | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.036951 | 0.129930 |
| seed:43 | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.030677 | 0.106707 |
| seed:43 | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.038758 | 0.141627 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.037085 | 0.132086 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.065703 | 0.218336 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073438 | 0.246818 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.063576 | 0.220825 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000017 | 0.002589 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001964 | 0.014212 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001030 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000010 | 0.001893 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.046070 | 0.154772 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.063997 | 0.213150 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.080600 | 0.273021 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.075220 | 0.254832 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004412 | 0.040328 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019444 | 0.099837 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000049 | 0.004087 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007742 | 0.041125 |
| seed:43 | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.027438 | 0.098709 |
| seed:43 | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.037144 | 0.132653 |
| seed:43 | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.063880 | 0.216574 |
| seed:43 | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005554 | 0.031760 |
| ensemble:mean_probability | prior | available_bindings | 2 | 3072 | 185 | 0.056764 | 0.228905 |
| ensemble:mean_probability | prior | available_bindings | 4 | 3072 | 245 | 0.073543 | 0.279295 |
| ensemble:mean_probability | prior | condition | informative | 3072 | 239 | 0.071848 | 0.274125 |
| ensemble:mean_probability | prior | condition | misleading | 3072 | 191 | 0.058458 | 0.234075 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.082150 | 0.304851 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.129324 | 0.447432 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.139442 | 0.478044 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.167531 | 0.561945 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.005059 | 0.073769 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.006514 | 0.077095 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.004825 | 0.071983 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.004930 | 0.072782 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.082244 | 0.305574 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.094080 | 0.341551 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.132768 | 0.458181 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.112510 | 0.396775 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.008427 | 0.083943 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.021724 | 0.123284 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.004825 | 0.071983 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.011660 | 0.093079 |
| ensemble:mean_probability | prior | original_split | development | 1536 | 86 | 0.053135 | 0.218039 |
| ensemble:mean_probability | prior | original_split | train | 4608 | 344 | 0.069159 | 0.266121 |
| ensemble:mean_probability | prior | query_role | current | 3072 | 413 | 0.120618 | 0.421109 |
| ensemble:mean_probability | prior | query_role | saved | 3072 | 17 | 0.009689 | 0.087092 |
| ensemble:mean_probability | A_input | available_bindings | 2 | 3072 | 185 | 0.039793 | 0.139286 |
| ensemble:mean_probability | A_input | available_bindings | 4 | 3072 | 245 | 0.039668 | 0.137399 |
| ensemble:mean_probability | A_input | condition | informative | 3072 | 239 | 0.037895 | 0.128149 |
| ensemble:mean_probability | A_input | condition | misleading | 3072 | 191 | 0.041566 | 0.148536 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063885 | 0.197626 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.081780 | 0.260903 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073115 | 0.235510 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.074475 | 0.256978 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000072 | 0.005461 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001943 | 0.012934 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000123 | 0.007353 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000211 | 0.009259 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.068002 | 0.210712 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067772 | 0.224466 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075299 | 0.223098 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078343 | 0.259599 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003943 | 0.038954 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019311 | 0.111036 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000061 | 0.005125 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007657 | 0.039463 |
| ensemble:mean_probability | A_input | original_split | development | 1536 | 86 | 0.035034 | 0.114716 |
| ensemble:mean_probability | A_input | original_split | train | 4608 | 344 | 0.041296 | 0.146218 |
| ensemble:mean_probability | A_input | query_role | current | 3072 | 413 | 0.073937 | 0.241652 |
| ensemble:mean_probability | A_input | query_role | saved | 3072 | 17 | 0.005524 | 0.035033 |
| ensemble:mean_probability | A_interactions | available_bindings | 2 | 3072 | 185 | 0.040180 | 0.138840 |
| ensemble:mean_probability | A_interactions | available_bindings | 4 | 3072 | 245 | 0.039166 | 0.135603 |
| ensemble:mean_probability | A_interactions | condition | informative | 3072 | 239 | 0.037487 | 0.125670 |
| ensemble:mean_probability | A_interactions | condition | misleading | 3072 | 191 | 0.041858 | 0.148774 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063764 | 0.197231 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082934 | 0.267545 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.073151 | 0.237026 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071872 | 0.248323 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000024 | 0.003396 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001955 | 0.013532 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001666 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.002041 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.068672 | 0.215637 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068611 | 0.225837 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074757 | 0.220542 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078778 | 0.265082 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004279 | 0.040340 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019209 | 0.097827 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000057 | 0.005241 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007742 | 0.042556 |
| ensemble:mean_probability | A_interactions | original_split | development | 1536 | 86 | 0.035121 | 0.114807 |
| ensemble:mean_probability | A_interactions | original_split | train | 4608 | 344 | 0.041190 | 0.144694 |
| ensemble:mean_probability | A_interactions | query_role | current | 3072 | 413 | 0.073842 | 0.242661 |
| ensemble:mean_probability | A_interactions | query_role | saved | 3072 | 17 | 0.005503 | 0.031783 |
| ensemble:mean_probability | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040593 | 0.140061 |
| ensemble:mean_probability | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039480 | 0.136912 |
| ensemble:mean_probability | A_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.037741 | 0.126704 |
| ensemble:mean_probability | A_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.042333 | 0.150269 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064979 | 0.199490 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083489 | 0.270818 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.075764 | 0.244662 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071644 | 0.248333 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000033 | 0.003977 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001934 | 0.012542 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001677 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000015 | 0.002503 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.069689 | 0.219294 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069479 | 0.228458 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074165 | 0.220593 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080085 | 0.268159 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004247 | 0.039582 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019184 | 0.097378 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000061 | 0.005335 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007763 | 0.043728 |
| ensemble:mean_probability | A_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.035658 | 0.116413 |
| ensemble:mean_probability | A_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041497 | 0.145844 |
| ensemble:mean_probability | A_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.074574 | 0.245100 |
| ensemble:mean_probability | A_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005500 | 0.031873 |
| ensemble:mean_probability | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034607 | 0.124505 |
| ensemble:mean_probability | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.038592 | 0.134008 |
| ensemble:mean_probability | A_interactions_neutral_scored | condition | informative | 3072 | 239 | 0.032420 | 0.112241 |
| ensemble:mean_probability | A_interactions_neutral_scored | condition | misleading | 3072 | 191 | 0.040779 | 0.146271 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.044366 | 0.149927 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.069023 | 0.231077 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.064479 | 0.212642 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.068160 | 0.235717 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000021 | 0.003274 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001965 | 0.014433 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000018 | 0.002655 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000012 | 0.002293 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055384 | 0.181194 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065413 | 0.216042 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072731 | 0.221888 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081831 | 0.272573 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004257 | 0.040023 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019225 | 0.098266 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000059 | 0.005365 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007782 | 0.044144 |
| ensemble:mean_probability | A_interactions_neutral_scored | original_split | development | 1536 | 86 | 0.028779 | 0.099282 |
| ensemble:mean_probability | A_interactions_neutral_scored | original_split | train | 4608 | 344 | 0.039206 | 0.139247 |
| ensemble:mean_probability | A_interactions_neutral_scored | query_role | current | 3072 | 413 | 0.067684 | 0.226113 |
| ensemble:mean_probability | A_interactions_neutral_scored | query_role | saved | 3072 | 17 | 0.005515 | 0.032400 |
| ensemble:mean_probability | A_interactions_oracle | available_bindings | 2 | 3072 | 185 | 0.036710 | 0.131025 |
| ensemble:mean_probability | A_interactions_oracle | available_bindings | 4 | 3072 | 245 | 0.039490 | 0.136351 |
| ensemble:mean_probability | A_interactions_oracle | condition | informative | 3072 | 239 | 0.034756 | 0.118362 |
| ensemble:mean_probability | A_interactions_oracle | condition | misleading | 3072 | 191 | 0.041444 | 0.149013 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.053096 | 0.174609 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.073457 | 0.242932 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.077858 | 0.242620 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.069665 | 0.241349 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000027 | 0.003253 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001955 | 0.013190 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001345 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.001956 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.059441 | 0.191997 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.066924 | 0.220927 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.079725 | 0.238839 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080588 | 0.271144 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004398 | 0.043384 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019440 | 0.102478 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000058 | 0.004692 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007759 | 0.042538 |
| ensemble:mean_probability | A_interactions_oracle | original_split | development | 1536 | 86 | 0.032631 | 0.109499 |
| ensemble:mean_probability | A_interactions_oracle | original_split | train | 4608 | 344 | 0.039923 | 0.141751 |
| ensemble:mean_probability | A_interactions_oracle | query_role | current | 3072 | 413 | 0.070644 | 0.234690 |
| ensemble:mean_probability | A_interactions_oracle | query_role | saved | 3072 | 17 | 0.005556 | 0.032685 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.035132 | 0.127658 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039299 | 0.135141 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.032940 | 0.114048 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.041491 | 0.148752 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.044890 | 0.156252 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.069742 | 0.235061 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.079703 | 0.247520 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.066834 | 0.232797 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000026 | 0.003437 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001956 | 0.013492 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001450 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002120 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055668 | 0.187508 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067287 | 0.222131 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.081316 | 0.244496 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081812 | 0.271194 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004328 | 0.042251 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019349 | 0.100540 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000049 | 0.004531 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007762 | 0.042968 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.030908 | 0.106408 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.039318 | 0.139730 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.068895 | 0.230344 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005535 | 0.032455 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.033721 | 0.122530 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.038311 | 0.133057 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.031164 | 0.108633 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.040869 | 0.146954 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.040279 | 0.140292 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.066214 | 0.221915 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.067419 | 0.220876 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.065433 | 0.229097 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000023 | 0.003356 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001955 | 0.013551 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001290 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002077 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.053028 | 0.176937 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065975 | 0.217894 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.076082 | 0.233764 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081962 | 0.272128 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004295 | 0.041571 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019371 | 0.100742 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000044 | 0.004324 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007777 | 0.043319 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.028233 | 0.098714 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.038611 | 0.137487 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.066494 | 0.223103 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005539 | 0.032484 |
| ensemble:mean_probability | B_input_confidence | available_bindings | 2 | 3072 | 185 | 0.039530 | 0.135544 |
| ensemble:mean_probability | B_input_confidence | available_bindings | 4 | 3072 | 245 | 0.039622 | 0.133766 |
| ensemble:mean_probability | B_input_confidence | condition | informative | 3072 | 239 | 0.037888 | 0.125317 |
| ensemble:mean_probability | B_input_confidence | condition | misleading | 3072 | 191 | 0.041264 | 0.143994 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.062332 | 0.194289 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.081005 | 0.254619 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072510 | 0.226397 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075726 | 0.250452 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000038 | 0.003912 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.002017 | 0.014755 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000116 | 0.007103 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000247 | 0.009588 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.064718 | 0.199786 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069526 | 0.224150 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.074339 | 0.220016 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077113 | 0.250522 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003932 | 0.037415 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019124 | 0.102040 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000055 | 0.004726 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007697 | 0.039868 |
| ensemble:mean_probability | B_input_confidence | original_split | development | 1536 | 86 | 0.034088 | 0.110754 |
| ensemble:mean_probability | B_input_confidence | original_split | train | 4608 | 344 | 0.041406 | 0.142622 |
| ensemble:mean_probability | B_input_confidence | query_role | current | 3072 | 413 | 0.073636 | 0.235605 |
| ensemble:mean_probability | B_input_confidence | query_role | saved | 3072 | 17 | 0.005516 | 0.033706 |
| ensemble:mean_probability | B_interactions_confidence | available_bindings | 2 | 3072 | 185 | 0.039888 | 0.134860 |
| ensemble:mean_probability | B_interactions_confidence | available_bindings | 4 | 3072 | 245 | 0.038972 | 0.131393 |
| ensemble:mean_probability | B_interactions_confidence | condition | informative | 3072 | 239 | 0.037402 | 0.122737 |
| ensemble:mean_probability | B_interactions_confidence | condition | misleading | 3072 | 191 | 0.041457 | 0.143516 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.062410 | 0.194209 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082594 | 0.262092 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072889 | 0.228692 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072303 | 0.240581 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000011 | 0.002375 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001990 | 0.015123 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000005 | 0.001538 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000012 | 0.002105 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.065296 | 0.203809 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069929 | 0.224214 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.073061 | 0.214527 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077797 | 0.255995 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004181 | 0.037710 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.018863 | 0.088679 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000043 | 0.004357 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007753 | 0.042183 |
| ensemble:mean_probability | B_interactions_confidence | original_split | development | 1536 | 86 | 0.034150 | 0.110443 |
| ensemble:mean_probability | B_interactions_confidence | original_split | train | 4608 | 344 | 0.041190 | 0.140688 |
| ensemble:mean_probability | B_interactions_confidence | query_role | current | 3072 | 413 | 0.073415 | 0.236140 |
| ensemble:mean_probability | B_interactions_confidence | query_role | saved | 3072 | 17 | 0.005445 | 0.030113 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.040197 | 0.135964 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.038995 | 0.131628 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.037570 | 0.123118 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.041621 | 0.144474 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064529 | 0.199323 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082888 | 0.263471 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.071381 | 0.225631 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.072335 | 0.240607 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000009 | 0.002066 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001988 | 0.014736 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000004 | 0.001378 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.001838 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.065470 | 0.204145 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070230 | 0.227119 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.071485 | 0.211557 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078490 | 0.258170 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004225 | 0.036437 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.018959 | 0.089471 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000044 | 0.004465 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007757 | 0.042594 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.034282 | 0.110581 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.041367 | 0.141534 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.073728 | 0.237516 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005464 | 0.030077 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 185 | 0.034304 | 0.123807 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 245 | 0.037173 | 0.125965 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 239 | 0.031143 | 0.105912 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 191 | 0.040334 | 0.143860 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.041197 | 0.144654 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.066881 | 0.221922 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.068659 | 0.215159 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.064180 | 0.216699 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000003 | 0.001072 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001981 | 0.014900 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000390 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000003 | 0.000823 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.050200 | 0.167627 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069606 | 0.229062 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075582 | 0.227776 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077671 | 0.257029 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004362 | 0.038293 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019474 | 0.101137 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000039 | 0.004019 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007719 | 0.040614 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 86 | 0.027984 | 0.095886 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 344 | 0.038323 | 0.134553 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 413 | 0.065927 | 0.218336 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 17 | 0.005550 | 0.031436 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 185 | 0.033379 | 0.119308 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 245 | 0.036610 | 0.124432 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 239 | 0.029988 | 0.102167 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 191 | 0.040001 | 0.141573 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.037534 | 0.130582 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.064878 | 0.211562 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.060603 | 0.197018 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.063313 | 0.213825 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000003 | 0.000964 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001986 | 0.017938 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000001 | 0.000389 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000004 | 0.000875 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.048138 | 0.157995 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069024 | 0.225132 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.071460 | 0.222829 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078251 | 0.256606 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004337 | 0.038385 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019382 | 0.097253 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000032 | 0.003620 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007739 | 0.041196 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 86 | 0.026010 | 0.089975 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 344 | 0.037989 | 0.132501 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 413 | 0.064452 | 0.212331 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 17 | 0.005537 | 0.031409 |
| ensemble:mean_probability | B_event_input | available_bindings | 2 | 3072 | 185 | 0.039717 | 0.137110 |
| ensemble:mean_probability | B_event_input | available_bindings | 4 | 3072 | 245 | 0.039644 | 0.135624 |
| ensemble:mean_probability | B_event_input | condition | informative | 3072 | 239 | 0.038306 | 0.127745 |
| ensemble:mean_probability | B_event_input | condition | misleading | 3072 | 191 | 0.041055 | 0.144988 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063194 | 0.196578 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083272 | 0.261832 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.075102 | 0.239908 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075095 | 0.253988 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000046 | 0.004312 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001957 | 0.013145 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000142 | 0.007331 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000244 | 0.009405 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.064580 | 0.201862 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068000 | 0.223282 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.077730 | 0.231737 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.076683 | 0.252040 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003940 | 0.038236 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019194 | 0.103907 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000056 | 0.004626 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007663 | 0.038841 |
| ensemble:mean_probability | B_event_input | original_split | development | 1536 | 86 | 0.034713 | 0.113798 |
| ensemble:mean_probability | B_event_input | original_split | train | 4608 | 344 | 0.041337 | 0.143890 |
| ensemble:mean_probability | B_event_input | query_role | current | 3072 | 413 | 0.073848 | 0.239130 |
| ensemble:mean_probability | B_event_input | query_role | saved | 3072 | 17 | 0.005513 | 0.033604 |
| ensemble:mean_probability | B_event_interactions | available_bindings | 2 | 3072 | 185 | 0.040002 | 0.136421 |
| ensemble:mean_probability | B_event_interactions | available_bindings | 4 | 3072 | 245 | 0.039045 | 0.133394 |
| ensemble:mean_probability | B_event_interactions | condition | informative | 3072 | 239 | 0.037715 | 0.124859 |
| ensemble:mean_probability | B_event_interactions | condition | misleading | 3072 | 191 | 0.041332 | 0.144956 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.063085 | 0.195851 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.084175 | 0.267977 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.075252 | 0.240900 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071824 | 0.244058 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000015 | 0.002732 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001958 | 0.013634 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000006 | 0.001539 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000011 | 0.002056 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.065475 | 0.206724 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068416 | 0.223279 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.077466 | 0.228676 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.077292 | 0.257681 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004211 | 0.038436 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019070 | 0.091767 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000040 | 0.004192 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007736 | 0.041436 |
| ensemble:mean_probability | B_event_interactions | original_split | development | 1536 | 86 | 0.034861 | 0.113566 |
| ensemble:mean_probability | B_event_interactions | original_split | train | 4608 | 344 | 0.041078 | 0.142022 |
| ensemble:mean_probability | B_event_interactions | query_role | current | 3072 | 413 | 0.073574 | 0.239519 |
| ensemble:mean_probability | B_event_interactions | query_role | saved | 3072 | 17 | 0.005473 | 0.030297 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040351 | 0.138223 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.039530 | 0.135999 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | condition | informative | 3072 | 239 | 0.038052 | 0.126811 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | condition | misleading | 3072 | 191 | 0.041828 | 0.147411 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.064797 | 0.199740 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.084455 | 0.270882 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.079182 | 0.253002 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071729 | 0.245377 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000021 | 0.003189 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001947 | 0.013555 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000017 | 0.002522 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000032 | 0.003489 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.066527 | 0.209400 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068761 | 0.225196 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.078935 | 0.239205 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078593 | 0.261402 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004225 | 0.038712 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019155 | 0.094186 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000048 | 0.004546 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007754 | 0.042673 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | original_split | development | 1536 | 86 | 0.035777 | 0.116780 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | original_split | train | 4608 | 344 | 0.041328 | 0.143888 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | query_role | current | 3072 | 413 | 0.074385 | 0.242862 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | query_role | saved | 3072 | 17 | 0.005495 | 0.031360 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.032575 | 0.120339 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.038000 | 0.133379 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 239 | 0.031480 | 0.108968 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 191 | 0.039095 | 0.144750 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.039251 | 0.140578 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.065176 | 0.219204 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.082566 | 0.265349 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.065166 | 0.224566 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000016 | 0.002503 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001960 | 0.013684 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000003 | 0.000801 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.001707 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.046396 | 0.159721 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.063870 | 0.215245 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.085394 | 0.297748 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.075876 | 0.258653 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004305 | 0.039967 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019459 | 0.102516 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000032 | 0.003275 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007752 | 0.041856 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 86 | 0.028994 | 0.104392 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 344 | 0.037385 | 0.134347 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 413 | 0.065027 | 0.221566 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 17 | 0.005548 | 0.032151 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.031886 | 0.116659 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.037284 | 0.131058 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 239 | 0.030334 | 0.105071 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 191 | 0.038836 | 0.142647 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.035728 | 0.127596 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.063289 | 0.211361 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.071563 | 0.236301 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.064782 | 0.222962 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000014 | 0.002388 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001961 | 0.013860 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000003 | 0.000936 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000009 | 0.001759 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.045630 | 0.153013 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.063831 | 0.213497 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.080955 | 0.279068 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.075894 | 0.258440 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.004252 | 0.039029 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019421 | 0.100224 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000030 | 0.003252 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007766 | 0.042007 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 86 | 0.026983 | 0.096968 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 344 | 0.037119 | 0.132822 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 413 | 0.063629 | 0.215960 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 17 | 0.005540 | 0.031758 |

Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.
