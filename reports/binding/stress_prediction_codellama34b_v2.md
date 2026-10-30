# Discovery-only failure prediction: codellama/CodeLlama-34b-Instruct-hf

Exploratory nested grouped prediction on already-consumed discovery targets; not mechanism C or unfamiliar-program/final confirmation. All twenty-three existing tiers are retained unchanged. Five new fixed tiers add only five raw scalar properties of one distinct stress-query response to the matching source-context plus BF16 next-token confidence tier. New tiers exclude the six finite-event likelihood scalars. The stress query is an additional observation, with its scientific access cost declared even when responses are cached: one BF16 next-token prefill plus one distinct stress query generating at most 32 tokens. Neutral-query and source-oracle access stay separately declared per context. Stress correctness, original target responses, original correctness and original generated-answer identity are not features; original correctness is only the existing supervised label. Stress validity, raw character/token lengths and parsed signed-integer value/magnitude are features of the additional response without grading it; its parsed response identity is explicitly available. Comparisons with next-token tiers are feature-nested; comparisons with joint finite-event tiers are alternatives with different observations, encoding and access costs. A gain does not identify a pure information increment or causal binding mechanism. Repeated partition seeds reuse the same structures, and bootstrap intervals condition on saved OOF probabilities without refitting or multiplicity correction. The five new stress tiers allow 1000 Newton iterations with the original objective, initialization, normalization, backtracking and 1e-8 stopping tolerance. All twenty-three parent tiers retain their original 100-iteration allowance.

6,144 transformed targets, 24 template components, 1454 failures. All target IDs remain in every fixed seed's OOF evaluation.

| Evaluation | Predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| seed:17 | prior | 0.180938 | 0.547986 | 6144 | 1454 |
| seed:17 | A_input | 0.133312 | 0.410162 | 6144 | 1454 |
| seed:17 | A_interactions | 0.123616 | 0.380847 | 6144 | 1454 |
| seed:17 | A_interactions_neutral_raw | 0.123825 | 0.381249 | 6144 | 1454 |
| seed:17 | A_interactions_neutral_scored | 0.096241 | 0.303531 | 6144 | 1454 |
| seed:17 | A_interactions_oracle | 0.096424 | 0.306944 | 6144 | 1454 |
| seed:17 | A_interactions_oracle_neutral_raw | 0.092108 | 0.295424 | 6144 | 1454 |
| seed:17 | A_interactions_oracle_neutral_scored | 0.087546 | 0.281243 | 6144 | 1454 |
| seed:17 | B_input_confidence | 0.125981 | 0.388214 | 6144 | 1454 |
| seed:17 | B_interactions_confidence | 0.116739 | 0.362366 | 6144 | 1454 |
| seed:17 | B_interactions_neutral_raw_confidence | 0.115069 | 0.358304 | 6144 | 1454 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | 0.088140 | 0.285238 | 6144 | 1454 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | 0.083889 | 0.272829 | 6144 | 1454 |
| seed:17 | B_event_input | 0.122954 | 0.374031 | 6144 | 1454 |
| seed:17 | B_event_interactions | 0.117510 | 0.360475 | 6144 | 1454 |
| seed:17 | B_event_interactions_neutral_raw | 0.115881 | 0.356216 | 6144 | 1454 |
| seed:17 | B_event_interactions_oracle_neutral_raw | 0.087175 | 0.281774 | 6144 | 1454 |
| seed:17 | B_event_interactions_oracle_neutral_scored | 0.082839 | 0.269713 | 6144 | 1454 |
| seed:17 | B_joint_input | 0.118326 | 0.361068 | 6144 | 1454 |
| seed:17 | B_joint_interactions | 0.113764 | 0.350067 | 6144 | 1454 |
| seed:17 | B_joint_interactions_neutral_raw | 0.112816 | 0.348245 | 6144 | 1454 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | 0.087156 | 0.282505 | 6144 | 1454 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | 0.082501 | 0.269512 | 6144 | 1454 |
| seed:17 | B_stress_input | 0.121840 | 0.375030 | 6144 | 1454 |
| seed:17 | B_stress_interactions | 0.115101 | 0.355921 | 6144 | 1454 |
| seed:17 | B_stress_interactions_neutral_raw | 0.115314 | 0.356986 | 6144 | 1454 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | 0.086993 | 0.280469 | 6144 | 1454 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | 0.082466 | 0.267216 | 6144 | 1454 |
| seed:29 | prior | 0.181167 | 0.548633 | 6144 | 1454 |
| seed:29 | A_input | 0.133066 | 0.409310 | 6144 | 1454 |
| seed:29 | A_interactions | 0.124611 | 0.383542 | 6144 | 1454 |
| seed:29 | A_interactions_neutral_raw | 0.124653 | 0.383131 | 6144 | 1454 |
| seed:29 | A_interactions_neutral_scored | 0.097191 | 0.305651 | 6144 | 1454 |
| seed:29 | A_interactions_oracle | 0.097123 | 0.307575 | 6144 | 1454 |
| seed:29 | A_interactions_oracle_neutral_raw | 0.092178 | 0.294428 | 6144 | 1454 |
| seed:29 | A_interactions_oracle_neutral_scored | 0.087765 | 0.281207 | 6144 | 1454 |
| seed:29 | B_input_confidence | 0.125890 | 0.387270 | 6144 | 1454 |
| seed:29 | B_interactions_confidence | 0.117435 | 0.364214 | 6144 | 1454 |
| seed:29 | B_interactions_neutral_raw_confidence | 0.116051 | 0.360706 | 6144 | 1454 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | 0.088872 | 0.285908 | 6144 | 1454 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | 0.084401 | 0.273872 | 6144 | 1454 |
| seed:29 | B_event_input | 0.122207 | 0.371228 | 6144 | 1454 |
| seed:29 | B_event_interactions | 0.117140 | 0.358879 | 6144 | 1454 |
| seed:29 | B_event_interactions_neutral_raw | 0.116034 | 0.356447 | 6144 | 1454 |
| seed:29 | B_event_interactions_oracle_neutral_raw | 0.087054 | 0.280647 | 6144 | 1454 |
| seed:29 | B_event_interactions_oracle_neutral_scored | 0.082316 | 0.267820 | 6144 | 1454 |
| seed:29 | B_joint_input | 0.118200 | 0.360284 | 6144 | 1454 |
| seed:29 | B_joint_interactions | 0.114015 | 0.350513 | 6144 | 1454 |
| seed:29 | B_joint_interactions_neutral_raw | 0.113285 | 0.348917 | 6144 | 1454 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | 0.087322 | 0.281207 | 6144 | 1454 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | 0.082298 | 0.268292 | 6144 | 1454 |
| seed:29 | B_stress_input | 0.122698 | 0.376456 | 6144 | 1454 |
| seed:29 | B_stress_interactions | 0.116313 | 0.358698 | 6144 | 1454 |
| seed:29 | B_stress_interactions_neutral_raw | 0.116046 | 0.358479 | 6144 | 1454 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | 0.088475 | 0.282987 | 6144 | 1454 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | 0.083690 | 0.269362 | 6144 | 1454 |
| seed:43 | prior | 0.180829 | 0.547689 | 6144 | 1454 |
| seed:43 | A_input | 0.132403 | 0.409566 | 6144 | 1454 |
| seed:43 | A_interactions | 0.123492 | 0.380324 | 6144 | 1454 |
| seed:43 | A_interactions_neutral_raw | 0.123965 | 0.381305 | 6144 | 1454 |
| seed:43 | A_interactions_neutral_scored | 0.096568 | 0.304512 | 6144 | 1454 |
| seed:43 | A_interactions_oracle | 0.096367 | 0.305378 | 6144 | 1454 |
| seed:43 | A_interactions_oracle_neutral_raw | 0.091576 | 0.292635 | 6144 | 1454 |
| seed:43 | A_interactions_oracle_neutral_scored | 0.087214 | 0.279955 | 6144 | 1454 |
| seed:43 | B_input_confidence | 0.125137 | 0.386757 | 6144 | 1454 |
| seed:43 | B_interactions_confidence | 0.116510 | 0.361066 | 6144 | 1454 |
| seed:43 | B_interactions_neutral_raw_confidence | 0.115148 | 0.357648 | 6144 | 1454 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | 0.088113 | 0.284165 | 6144 | 1454 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | 0.084256 | 0.273760 | 6144 | 1454 |
| seed:43 | B_event_input | 0.121001 | 0.367978 | 6144 | 1454 |
| seed:43 | B_event_interactions | 0.116175 | 0.356281 | 6144 | 1454 |
| seed:43 | B_event_interactions_neutral_raw | 0.114609 | 0.352671 | 6144 | 1454 |
| seed:43 | B_event_interactions_oracle_neutral_raw | 0.085599 | 0.276494 | 6144 | 1454 |
| seed:43 | B_event_interactions_oracle_neutral_scored | 0.081244 | 0.264264 | 6144 | 1454 |
| seed:43 | B_joint_input | 0.118203 | 0.360417 | 6144 | 1454 |
| seed:43 | B_joint_interactions | 0.113669 | 0.349417 | 6144 | 1454 |
| seed:43 | B_joint_interactions_neutral_raw | 0.111846 | 0.344672 | 6144 | 1454 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | 0.085221 | 0.274967 | 6144 | 1454 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | 0.080753 | 0.263663 | 6144 | 1454 |
| seed:43 | B_stress_input | 0.122643 | 0.376770 | 6144 | 1454 |
| seed:43 | B_stress_interactions | 0.115810 | 0.356587 | 6144 | 1454 |
| seed:43 | B_stress_interactions_neutral_raw | 0.115275 | 0.355663 | 6144 | 1454 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | 0.087160 | 0.279038 | 6144 | 1454 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | 0.082804 | 0.266484 | 6144 | 1454 |
| ensemble:mean_probability | prior | 0.180960 | 0.548053 | 6144 | 1454 |
| ensemble:mean_probability | A_input | 0.132585 | 0.408816 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions | 0.123574 | 0.380577 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_neutral_raw | 0.123861 | 0.381025 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_neutral_scored | 0.096350 | 0.303570 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_oracle | 0.096237 | 0.305361 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | 0.091608 | 0.293049 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | 0.087180 | 0.279734 | 6144 | 1454 |
| ensemble:mean_probability | B_input_confidence | 0.125365 | 0.386596 | 6144 | 1454 |
| ensemble:mean_probability | B_interactions_confidence | 0.116641 | 0.361757 | 6144 | 1454 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | 0.115091 | 0.357863 | 6144 | 1454 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | 0.087942 | 0.283594 | 6144 | 1454 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | 0.083800 | 0.272258 | 6144 | 1454 |
| ensemble:mean_probability | B_event_input | 0.121691 | 0.370051 | 6144 | 1454 |
| ensemble:mean_probability | B_event_interactions | 0.116667 | 0.357619 | 6144 | 1454 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | 0.115220 | 0.354209 | 6144 | 1454 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | 0.086154 | 0.278165 | 6144 | 1454 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | 0.081680 | 0.265397 | 6144 | 1454 |
| ensemble:mean_probability | B_joint_input | 0.117984 | 0.359848 | 6144 | 1454 |
| ensemble:mean_probability | B_joint_interactions | 0.113499 | 0.348948 | 6144 | 1454 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | 0.112318 | 0.346208 | 6144 | 1454 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | 0.086017 | 0.277467 | 6144 | 1454 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | 0.081426 | 0.265466 | 6144 | 1454 |
| ensemble:mean_probability | B_stress_input | 0.122131 | 0.375329 | 6144 | 1454 |
| ensemble:mean_probability | B_stress_interactions | 0.115368 | 0.355816 | 6144 | 1454 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | 0.115093 | 0.355540 | 6144 | 1454 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | 0.087080 | 0.279280 | 6144 | 1454 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | 0.082525 | 0.265984 | 6144 | 1454 |

## All paired template-bootstrap improvements

Positive loss(left) − loss(right) favors the right predictor. These are conditional exploratory intervals with no refitting or multiplicity adjustment.

| Evaluation | Left baseline | Right predictor | Brier improvement [95%] | Log-loss improvement [95%] |
|---|---|---|---|---|
| seed:17 | prior | A_input | +0.047625 [+0.033718, +0.061716] | +0.137823 [+0.107712, +0.168297] |
| seed:17 | prior | A_interactions | +0.057321 [+0.043862, +0.072332] | +0.167139 [+0.136852, +0.201474] |
| seed:17 | prior | A_interactions_neutral_raw | +0.057112 [+0.043495, +0.071855] | +0.166737 [+0.135633, +0.200929] |
| seed:17 | prior | A_interactions_neutral_scored | +0.084696 [+0.069184, +0.100277] | +0.244455 [+0.208851, +0.280157] |
| seed:17 | prior | A_interactions_oracle | +0.084514 [+0.066099, +0.103731] | +0.241042 [+0.196593, +0.286506] |
| seed:17 | prior | A_interactions_oracle_neutral_raw | +0.088829 [+0.070531, +0.107253] | +0.252562 [+0.208185, +0.296794] |
| seed:17 | prior | A_interactions_oracle_neutral_scored | +0.093391 [+0.075383, +0.111245] | +0.266743 [+0.224689, +0.310259] |
| seed:17 | A_input | A_interactions | +0.009696 [+0.004953, +0.015502] | +0.029316 [+0.015241, +0.044604] |
| seed:17 | A_interactions | A_interactions_neutral_raw | -0.000209 [-0.001218, +0.000740] | -0.000402 [-0.003153, +0.002133] |
| seed:17 | A_interactions | A_interactions_neutral_scored | +0.027375 [+0.020281, +0.034407] | +0.077315 [+0.057531, +0.097175] |
| seed:17 | A_interactions | A_interactions_oracle | +0.027193 [+0.018254, +0.036970] | +0.073903 [+0.047689, +0.102488] |
| seed:17 | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.004315 [+0.001703, +0.006846] | +0.011520 [+0.004593, +0.018415] |
| seed:17 | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.004562 [+0.002307, +0.006822] | +0.014181 [+0.007841, +0.020820] |
| seed:17 | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.027584 [+0.020629, +0.034530] | +0.077718 [+0.058009, +0.097311] |
| seed:17 | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.031717 [+0.023135, +0.041266] | +0.085825 [+0.059283, +0.112984] |
| seed:17 | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.008695 [+0.003385, +0.013487] | +0.022288 [+0.006369, +0.036630] |
| seed:17 | A_input | B_input_confidence | +0.007332 [+0.002446, +0.012251] | +0.021948 [+0.007606, +0.036650] |
| seed:17 | A_interactions | B_interactions_confidence | +0.006877 [+0.002036, +0.012031] | +0.018480 [+0.004462, +0.033663] |
| seed:17 | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.008756 [+0.003457, +0.014483] | +0.022944 [+0.006889, +0.039720] |
| seed:17 | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.003968 [+0.001838, +0.006125] | +0.010186 [+0.002801, +0.017766] |
| seed:17 | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.003658 [+0.001767, +0.005461] | +0.008414 [+0.002318, +0.014297] |
| seed:17 | B_input_confidence | B_interactions_confidence | +0.009242 [+0.004962, +0.014056] | +0.025848 [+0.012185, +0.040234] |
| seed:17 | B_interactions_confidence | B_interactions_neutral_raw_confidence | +0.001669 [-0.000488, +0.004221] | +0.004062 [-0.001512, +0.010462] |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.004251 [+0.002364, +0.006165] | +0.012409 [+0.005958, +0.019098] |
| seed:17 | A_input | B_event_input | +0.010358 [+0.004627, +0.016500] | +0.036131 [+0.022047, +0.050825] |
| seed:17 | A_interactions | B_event_interactions | +0.006106 [+0.001607, +0.011119] | +0.020372 [+0.007974, +0.033621] |
| seed:17 | A_interactions_neutral_raw | B_event_interactions_neutral_raw | +0.007944 [+0.002811, +0.013632] | +0.025033 [+0.011204, +0.039871] |
| seed:17 | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.004933 [+0.001555, +0.007904] | +0.013649 [+0.002844, +0.023367] |
| seed:17 | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.004707 [+0.001712, +0.007450] | +0.011529 [+0.000709, +0.021375] |
| seed:17 | B_input_confidence | B_event_input | +0.003026 [-0.001247, +0.007750] | +0.014183 [+0.001794, +0.027961] |
| seed:17 | B_interactions_confidence | B_event_interactions | -0.000771 [-0.003822, +0.002321] | +0.001892 [-0.007313, +0.010706] |
| seed:17 | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | -0.000812 [-0.003751, +0.002160] | +0.002089 [-0.006498, +0.011215] |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.000965 [-0.002121, +0.003983] | +0.003464 [-0.004931, +0.011334] |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.001050 [-0.001948, +0.003952] | +0.003115 [-0.005747, +0.011636] |
| seed:17 | B_event_input | B_event_interactions | +0.005445 [+0.002158, +0.008635] | +0.013557 [+0.001491, +0.023719] |
| seed:17 | B_event_interactions | B_event_interactions_neutral_raw | +0.001629 [-0.000826, +0.004285] | +0.004259 [-0.001932, +0.010935] |
| seed:17 | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.004336 [+0.002432, +0.006376] | +0.012061 [+0.006419, +0.017829] |
| seed:17 | B_input_confidence | B_joint_input | +0.007654 [+0.002656, +0.013114] | +0.027146 [+0.014170, +0.041554] |
| seed:17 | B_interactions_confidence | B_joint_interactions | +0.002975 [-0.000076, +0.006275] | +0.012300 [+0.003727, +0.021227] |
| seed:17 | B_interactions_neutral_raw_confidence | B_joint_interactions_neutral_raw | +0.002253 [-0.000643, +0.005423] | +0.010059 [+0.001993, +0.018242] |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | B_joint_interactions_oracle_neutral_raw | +0.000985 [-0.002046, +0.003752] | +0.002733 [-0.007521, +0.011433] |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | B_joint_interactions_oracle_neutral_scored | +0.001388 [-0.001647, +0.004212] | +0.003317 [-0.007175, +0.012325] |
| seed:17 | B_event_input | B_joint_input | +0.004628 [+0.001991, +0.007478] | +0.012963 [+0.004936, +0.021476] |
| seed:17 | B_event_interactions | B_joint_interactions | +0.003746 [+0.001592, +0.006326] | +0.010408 [+0.003986, +0.017381] |
| seed:17 | B_event_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.003065 [+0.000873, +0.005609] | +0.007970 [+0.001179, +0.015093] |
| seed:17 | B_event_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | +0.000020 [-0.001600, +0.001533] | -0.000731 [-0.006176, +0.003827] |
| seed:17 | B_event_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.000339 [-0.001021, +0.001628] | +0.000202 [-0.004016, +0.004073] |
| seed:17 | A_input | B_joint_input | +0.014986 [+0.007320, +0.022581] | +0.049094 [+0.029691, +0.068693] |
| seed:17 | A_interactions | B_joint_interactions | +0.009853 [+0.003891, +0.016485] | +0.030780 [+0.014721, +0.048380] |
| seed:17 | A_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.011009 [+0.004792, +0.018032] | +0.033003 [+0.015869, +0.051797] |
| seed:17 | A_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | +0.004953 [+0.000968, +0.008238] | +0.012918 [-0.001729, +0.025026] |
| seed:17 | A_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.005046 [+0.001655, +0.008039] | +0.011731 [-0.000941, +0.022872] |
| seed:17 | B_joint_input | B_joint_interactions | +0.004563 [+0.001303, +0.007556] | +0.011002 [+0.000174, +0.020850] |
| seed:17 | B_joint_interactions | B_joint_interactions_neutral_raw | +0.000947 [-0.001451, +0.003616] | +0.001821 [-0.004622, +0.008832] |
| seed:17 | B_joint_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_scored | +0.004655 [+0.002932, +0.006465] | +0.012993 [+0.007466, +0.018837] |
| seed:17 | B_input_confidence | B_stress_input | +0.004140 [+0.002190, +0.006219] | +0.013185 [+0.008154, +0.018438] |
| seed:17 | B_interactions_confidence | B_stress_interactions | +0.001638 [-0.000770, +0.003777] | +0.006445 [+0.000328, +0.011970] |
| seed:17 | B_interactions_neutral_raw_confidence | B_stress_interactions_neutral_raw | -0.000244 [-0.001905, +0.001175] | +0.001319 [-0.003115, +0.005399] |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | B_stress_interactions_oracle_neutral_raw | +0.001148 [-0.000873, +0.002728] | +0.004769 [-0.001114, +0.009874] |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | B_stress_interactions_oracle_neutral_scored | +0.001423 [-0.000511, +0.003157] | +0.005613 [-0.001104, +0.012101] |
| seed:17 | B_joint_input | B_stress_input | -0.003514 [-0.009230, +0.001912] | -0.013961 [-0.029891, +0.000869] |
| seed:17 | B_joint_interactions | B_stress_interactions | -0.001337 [-0.005091, +0.002198] | -0.005855 [-0.016475, +0.004061] |
| seed:17 | B_joint_interactions_neutral_raw | B_stress_interactions_neutral_raw | -0.002497 [-0.005606, +0.000448] | -0.008740 [-0.016887, -0.000944] |
| seed:17 | B_joint_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | +0.000163 [-0.002749, +0.002955] | +0.002036 [-0.006375, +0.010417] |
| seed:17 | B_joint_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | +0.000034 [-0.002949, +0.002786] | +0.002296 [-0.006221, +0.010277] |
| seed:17 | A_input | B_stress_input | +0.011472 [+0.006118, +0.017246] | +0.035133 [+0.019485, +0.051870] |
| seed:17 | A_interactions | B_stress_interactions | +0.008516 [+0.003294, +0.014507] | +0.024925 [+0.008877, +0.042126] |
| seed:17 | A_interactions_neutral_raw | B_stress_interactions_neutral_raw | +0.008512 [+0.003013, +0.014593] | +0.024263 [+0.007353, +0.042014] |
| seed:17 | A_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | +0.005116 [+0.001827, +0.008042] | +0.014955 [+0.004103, +0.025375] |
| seed:17 | A_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | +0.005080 [+0.002315, +0.007646] | +0.014027 [+0.003470, +0.024242] |
| seed:29 | prior | A_input | +0.048101 [+0.033731, +0.062435] | +0.139323 [+0.107927, +0.170934] |
| seed:29 | prior | A_interactions | +0.056556 [+0.042934, +0.071315] | +0.165091 [+0.134802, +0.199281] |
| seed:29 | prior | A_interactions_neutral_raw | +0.056514 [+0.042608, +0.071280] | +0.165502 [+0.134594, +0.200171] |
| seed:29 | prior | A_interactions_neutral_scored | +0.083976 [+0.067300, +0.100416] | +0.242982 [+0.204804, +0.280362] |
| seed:29 | prior | A_interactions_oracle | +0.084044 [+0.064565, +0.103526] | +0.241057 [+0.196359, +0.287608] |
| seed:29 | prior | A_interactions_oracle_neutral_raw | +0.088989 [+0.070442, +0.107791] | +0.254205 [+0.210679, +0.298682] |
| seed:29 | prior | A_interactions_oracle_neutral_scored | +0.093402 [+0.075287, +0.111644] | +0.267426 [+0.225113, +0.310547] |
| seed:29 | A_input | A_interactions | +0.008455 [+0.004107, +0.013381] | +0.025768 [+0.012382, +0.039627] |
| seed:29 | A_interactions | A_interactions_neutral_raw | -0.000042 [-0.001294, +0.001189] | +0.000412 [-0.003239, +0.004198] |
| seed:29 | A_interactions | A_interactions_neutral_scored | +0.027420 [+0.019962, +0.035205] | +0.077891 [+0.058378, +0.098030] |
| seed:29 | A_interactions | A_interactions_oracle | +0.027488 [+0.018238, +0.037477] | +0.075967 [+0.050170, +0.104273] |
| seed:29 | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.004944 [+0.002176, +0.007745] | +0.013147 [+0.005912, +0.020548] |
| seed:29 | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.004413 [+0.001844, +0.006885] | +0.013221 [+0.006554, +0.020114] |
| seed:29 | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.027461 [+0.019682, +0.035188] | +0.077480 [+0.056776, +0.098466] |
| seed:29 | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.032475 [+0.023785, +0.041974] | +0.088703 [+0.063954, +0.114621] |
| seed:29 | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.009426 [+0.004254, +0.014103] | +0.024444 [+0.009515, +0.038047] |
| seed:29 | A_input | B_input_confidence | +0.007177 [+0.002312, +0.012086] | +0.022040 [+0.008088, +0.036342] |
| seed:29 | A_interactions | B_interactions_confidence | +0.007176 [+0.002270, +0.012313] | +0.019329 [+0.004860, +0.034348] |
| seed:29 | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.008602 [+0.003565, +0.014045] | +0.022425 [+0.008139, +0.038427] |
| seed:29 | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.003306 [+0.001181, +0.005375] | +0.008520 [+0.001490, +0.015513] |
| seed:29 | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.003364 [+0.001311, +0.005311] | +0.007335 [+0.001200, +0.013246] |
| seed:29 | B_input_confidence | B_interactions_confidence | +0.008455 [+0.004126, +0.013507] | +0.023057 [+0.008946, +0.038294] |
| seed:29 | B_interactions_confidence | B_interactions_neutral_raw_confidence | +0.001384 [-0.000539, +0.003195] | +0.003507 [-0.001478, +0.008220] |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.004471 [+0.002098, +0.006785] | +0.012036 [+0.005228, +0.019097] |
| seed:29 | A_input | B_event_input | +0.010860 [+0.005310, +0.016177] | +0.038082 [+0.024399, +0.051813] |
| seed:29 | A_interactions | B_event_interactions | +0.007472 [+0.002628, +0.012433] | +0.024663 [+0.012465, +0.037393] |
| seed:29 | A_interactions_neutral_raw | B_event_interactions_neutral_raw | +0.008619 [+0.003467, +0.013858] | +0.026684 [+0.013527, +0.040514] |
| seed:29 | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.005125 [+0.002298, +0.007930] | +0.013781 [+0.004148, +0.023253] |
| seed:29 | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.005449 [+0.003054, +0.007945] | +0.013387 [+0.004965, +0.022023] |
| seed:29 | B_input_confidence | B_event_input | +0.003683 [-0.000441, +0.008182] | +0.016042 [+0.004175, +0.028864] |
| seed:29 | B_interactions_confidence | B_event_interactions | +0.000295 [-0.002700, +0.003463] | +0.005335 [-0.003933, +0.015346] |
| seed:29 | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | +0.000017 [-0.002677, +0.002902] | +0.004259 [-0.004145, +0.013196] |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.001819 [-0.001085, +0.004707] | +0.005261 [-0.003166, +0.013544] |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.002085 [-0.000666, +0.004804] | +0.006052 [-0.001860, +0.014233] |
| seed:29 | B_event_input | B_event_interactions | +0.005067 [+0.001565, +0.008592] | +0.012349 [-0.000361, +0.023471] |
| seed:29 | B_event_interactions | B_event_interactions_neutral_raw | +0.001106 [-0.000791, +0.002979] | +0.002432 [-0.002789, +0.007361] |
| seed:29 | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.004738 [+0.002872, +0.006588] | +0.012826 [+0.007487, +0.018443] |
| seed:29 | B_input_confidence | B_joint_input | +0.007690 [+0.002682, +0.013119] | +0.026986 [+0.013825, +0.041421] |
| seed:29 | B_interactions_confidence | B_joint_interactions | +0.003420 [+0.000309, +0.006590] | +0.013700 [+0.005072, +0.022680] |
| seed:29 | B_interactions_neutral_raw_confidence | B_joint_interactions_neutral_raw | +0.002765 [+0.000056, +0.005591] | +0.011789 [+0.004303, +0.019672] |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | B_joint_interactions_oracle_neutral_raw | +0.001550 [-0.001052, +0.003962] | +0.004701 [-0.003935, +0.012680] |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | B_joint_interactions_oracle_neutral_scored | +0.002103 [-0.000319, +0.004555] | +0.005580 [-0.002658, +0.013749] |
| seed:29 | B_event_input | B_joint_input | +0.004007 [+0.001238, +0.006918] | +0.010944 [+0.002579, +0.019359] |
| seed:29 | B_event_interactions | B_joint_interactions | +0.003124 [+0.000954, +0.005646] | +0.008365 [+0.001523, +0.015436] |
| seed:29 | B_event_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.002748 [+0.000596, +0.005164] | +0.007529 [+0.000918, +0.014305] |
| seed:29 | B_event_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | -0.000268 [-0.001458, +0.000898] | -0.000560 [-0.004203, +0.002781] |
| seed:29 | B_event_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.000018 [-0.001146, +0.001195] | -0.000472 [-0.003839, +0.002629] |
| seed:29 | A_input | B_joint_input | +0.014866 [+0.007278, +0.022199] | +0.049026 [+0.029988, +0.068805] |
| seed:29 | A_interactions | B_joint_interactions | +0.010596 [+0.004531, +0.017117] | +0.033029 [+0.017051, +0.049945] |
| seed:29 | A_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.011368 [+0.005150, +0.017858] | +0.034213 [+0.017233, +0.051814] |
| seed:29 | A_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | +0.004856 [+0.001796, +0.007710] | +0.013221 [+0.001907, +0.023721] |
| seed:29 | A_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.005467 [+0.002802, +0.008045] | +0.012915 [+0.002939, +0.022633] |
| seed:29 | B_joint_input | B_joint_interactions | +0.004185 [+0.000838, +0.007422] | +0.009771 [-0.001856, +0.020198] |
| seed:29 | B_joint_interactions | B_joint_interactions_neutral_raw | +0.000730 [-0.001170, +0.002623] | +0.001596 [-0.003652, +0.006853] |
| seed:29 | B_joint_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_scored | +0.005024 [+0.003236, +0.006829] | +0.012914 [+0.007516, +0.018371] |
| seed:29 | B_input_confidence | B_stress_input | +0.003192 [+0.001387, +0.005068] | +0.010815 [+0.005844, +0.015862] |
| seed:29 | B_interactions_confidence | B_stress_interactions | +0.001122 [-0.001619, +0.003293] | +0.005516 [-0.001841, +0.011219] |
| seed:29 | B_interactions_neutral_raw_confidence | B_stress_interactions_neutral_raw | +0.000005 [-0.001982, +0.001703] | +0.002227 [-0.002511, +0.006547] |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | B_stress_interactions_oracle_neutral_raw | +0.000397 [-0.001669, +0.002143] | +0.002921 [-0.002335, +0.007531] |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | B_stress_interactions_oracle_neutral_scored | +0.000712 [-0.000797, +0.002117] | +0.004510 [-0.000319, +0.008818] |
| seed:29 | B_joint_input | B_stress_input | -0.004498 [-0.010479, +0.001100] | -0.016171 [-0.032560, -0.001102] |
| seed:29 | B_joint_interactions | B_stress_interactions | -0.002298 [-0.005897, +0.001235] | -0.008185 [-0.018095, +0.001240] |
| seed:29 | B_joint_interactions_neutral_raw | B_stress_interactions_neutral_raw | -0.002760 [-0.006445, +0.000658] | -0.009561 [-0.019466, -0.000309] |
| seed:29 | B_joint_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | -0.001153 [-0.003972, +0.001401] | -0.001780 [-0.009662, +0.005710] |
| seed:29 | B_joint_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | -0.001391 [-0.004183, +0.001200] | -0.001069 [-0.008625, +0.005997] |
| seed:29 | A_input | B_stress_input | +0.010369 [+0.005033, +0.015890] | +0.032855 [+0.017586, +0.049575] |
| seed:29 | A_interactions | B_stress_interactions | +0.008298 [+0.003417, +0.014083] | +0.024844 [+0.010469, +0.041047] |
| seed:29 | A_interactions_neutral_raw | B_stress_interactions_neutral_raw | +0.008607 [+0.003616, +0.014371] | +0.024652 [+0.009441, +0.040853] |
| seed:29 | A_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | +0.003703 [+0.000811, +0.006398] | +0.011441 [+0.002011, +0.020610] |
| seed:29 | A_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | +0.004076 [+0.001867, +0.006088] | +0.011845 [+0.004008, +0.019134] |
| seed:43 | prior | A_input | +0.048426 [+0.034920, +0.061588] | +0.138123 [+0.109077, +0.166437] |
| seed:43 | prior | A_interactions | +0.057338 [+0.044160, +0.072012] | +0.167365 [+0.137779, +0.200135] |
| seed:43 | prior | A_interactions_neutral_raw | +0.056865 [+0.043531, +0.071632] | +0.166384 [+0.136158, +0.199744] |
| seed:43 | prior | A_interactions_neutral_scored | +0.084261 [+0.068285, +0.100522] | +0.243177 [+0.206939, +0.279264] |
| seed:43 | prior | A_interactions_oracle | +0.084462 [+0.065814, +0.103808] | +0.242311 [+0.197989, +0.287252] |
| seed:43 | prior | A_interactions_oracle_neutral_raw | +0.089253 [+0.071006, +0.107643] | +0.255055 [+0.212157, +0.298436] |
| seed:43 | prior | A_interactions_oracle_neutral_scored | +0.093615 [+0.075689, +0.111793] | +0.267735 [+0.227595, +0.309850] |
| seed:43 | A_input | A_interactions | +0.008911 [+0.004063, +0.014505] | +0.029243 [+0.014241, +0.044967] |
| seed:43 | A_interactions | A_interactions_neutral_raw | -0.000473 [-0.001421, +0.000379] | -0.000981 [-0.003524, +0.001309] |
| seed:43 | A_interactions | A_interactions_neutral_scored | +0.026923 [+0.018706, +0.034945] | +0.075812 [+0.053837, +0.097802] |
| seed:43 | A_interactions | A_interactions_oracle | +0.027124 [+0.017921, +0.037118] | +0.074946 [+0.048627, +0.103900] |
| seed:43 | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.004791 [+0.002098, +0.007467] | +0.012743 [+0.005295, +0.020070] |
| seed:43 | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.004363 [+0.001455, +0.006986] | +0.012680 [+0.005186, +0.019965] |
| seed:43 | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.027396 [+0.019257, +0.035425] | +0.076793 [+0.054785, +0.098625] |
| seed:43 | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.032388 [+0.023577, +0.042049] | +0.088670 [+0.062238, +0.115498] |
| seed:43 | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.009355 [+0.004052, +0.014068] | +0.024557 [+0.009396, +0.038909] |
| seed:43 | A_input | B_input_confidence | +0.007266 [+0.002587, +0.012076] | +0.022810 [+0.008930, +0.037172] |
| seed:43 | A_interactions | B_interactions_confidence | +0.006981 [+0.002325, +0.011980] | +0.019258 [+0.005944, +0.033726] |
| seed:43 | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.008817 [+0.003700, +0.014293] | +0.023657 [+0.009306, +0.039196] |
| seed:43 | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.003463 [+0.001056, +0.005910] | +0.008470 [+0.000780, +0.016257] |
| seed:43 | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.002958 [+0.000914, +0.004895] | +0.006195 [+0.000214, +0.011949] |
| seed:43 | B_input_confidence | B_interactions_confidence | +0.008627 [+0.004020, +0.014023] | +0.025691 [+0.010912, +0.040925] |
| seed:43 | B_interactions_confidence | B_interactions_neutral_raw_confidence | +0.001363 [-0.000251, +0.003029] | +0.003418 [-0.001050, +0.007980] |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.003857 [+0.001484, +0.006198] | +0.010405 [+0.002600, +0.018155] |
| seed:43 | A_input | B_event_input | +0.011402 [+0.005876, +0.017176] | +0.041589 [+0.027464, +0.055525] |
| seed:43 | A_interactions | B_event_interactions | +0.007316 [+0.002874, +0.012026] | +0.024043 [+0.012226, +0.036843] |
| seed:43 | A_interactions_neutral_raw | B_event_interactions_neutral_raw | +0.009355 [+0.004512, +0.014584] | +0.028634 [+0.016236, +0.042050] |
| seed:43 | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.005978 [+0.003291, +0.008523] | +0.016140 [+0.006999, +0.024960] |
| seed:43 | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.005969 [+0.003723, +0.008191] | +0.015691 [+0.007977, +0.023689] |
| seed:43 | B_input_confidence | B_event_input | +0.004136 [-0.000037, +0.009160] | +0.018779 [+0.007041, +0.032415] |
| seed:43 | B_interactions_confidence | B_event_interactions | +0.000335 [-0.002461, +0.003279] | +0.004785 [-0.004024, +0.013357] |
| seed:43 | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | +0.000538 [-0.002158, +0.003491] | +0.004976 [-0.003451, +0.014048] |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.002514 [-0.000607, +0.005562] | +0.007671 [-0.000950, +0.016279] |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.003012 [+0.000185, +0.005557] | +0.009496 [+0.001520, +0.017087] |
| seed:43 | B_event_input | B_event_interactions | +0.004826 [+0.001372, +0.008079] | +0.011697 [-0.000503, +0.022395] |
| seed:43 | B_event_interactions | B_event_interactions_neutral_raw | +0.001566 [-0.000209, +0.003341] | +0.003609 [-0.001339, +0.008433] |
| seed:43 | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.004354 [+0.002308, +0.006386] | +0.012230 [+0.006015, +0.018616] |
| seed:43 | B_input_confidence | B_joint_input | +0.006934 [+0.001736, +0.012597] | +0.026340 [+0.012952, +0.040981] |
| seed:43 | B_interactions_confidence | B_joint_interactions | +0.002842 [-0.000127, +0.005991] | +0.011648 [+0.003292, +0.020455] |
| seed:43 | B_interactions_neutral_raw_confidence | B_joint_interactions_neutral_raw | +0.003301 [+0.000442, +0.006439] | +0.012976 [+0.004689, +0.021664] |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | B_joint_interactions_oracle_neutral_raw | +0.002892 [+0.000041, +0.005630] | +0.009197 [+0.000206, +0.017304] |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | B_joint_interactions_oracle_neutral_scored | +0.003503 [+0.001172, +0.005762] | +0.010097 [+0.002374, +0.017595] |
| seed:43 | B_event_input | B_joint_input | +0.002798 [+0.000320, +0.005609] | +0.007560 [-0.000027, +0.015644] |
| seed:43 | B_event_interactions | B_joint_interactions | +0.002507 [-0.000050, +0.005401] | +0.006863 [-0.001435, +0.015516] |
| seed:43 | B_event_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.002763 [+0.000423, +0.005426] | +0.007999 [+0.000704, +0.015665] |
| seed:43 | B_event_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | +0.000377 [-0.001178, +0.001908] | +0.001527 [-0.003079, +0.005998] |
| seed:43 | B_event_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.000492 [-0.000880, +0.001843] | +0.000601 [-0.003346, +0.004132] |
| seed:43 | A_input | B_joint_input | +0.014200 [+0.007055, +0.021636] | +0.049149 [+0.031390, +0.068609] |
| seed:43 | A_interactions | B_joint_interactions | +0.009823 [+0.004220, +0.016194] | +0.030906 [+0.015527, +0.048273] |
| seed:43 | A_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.012118 [+0.006260, +0.018746] | +0.036633 [+0.020602, +0.054561] |
| seed:43 | A_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | +0.006355 [+0.003142, +0.009425] | +0.017667 [+0.006454, +0.028698] |
| seed:43 | A_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.006461 [+0.004266, +0.008556] | +0.016292 [+0.007718, +0.024935] |
| seed:43 | B_joint_input | B_joint_interactions | +0.004534 [+0.000926, +0.007726] | +0.011000 [-0.000664, +0.020984] |
| seed:43 | B_joint_interactions | B_joint_interactions_neutral_raw | +0.001822 [-0.000022, +0.003683] | +0.004746 [-0.000238, +0.009871] |
| seed:43 | B_joint_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_scored | +0.004469 [+0.002354, +0.006596] | +0.011305 [+0.004440, +0.017783] |
| seed:43 | B_input_confidence | B_stress_input | +0.002494 [+0.000545, +0.004524] | +0.009987 [+0.004313, +0.015706] |
| seed:43 | B_interactions_confidence | B_stress_interactions | +0.000701 [-0.001484, +0.002629] | +0.004479 [-0.001406, +0.009621] |
| seed:43 | B_interactions_neutral_raw_confidence | B_stress_interactions_neutral_raw | -0.000127 [-0.001870, +0.001323] | +0.001985 [-0.002469, +0.006012] |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | B_stress_interactions_oracle_neutral_raw | +0.000953 [-0.000993, +0.002570] | +0.005126 [-0.000840, +0.010665] |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | B_stress_interactions_oracle_neutral_scored | +0.001452 [-0.000236, +0.003005] | +0.007276 [+0.001287, +0.012957] |
| seed:43 | B_joint_input | B_stress_input | -0.004440 [-0.010678, +0.001389] | -0.016352 [-0.033274, -0.000683] |
| seed:43 | B_joint_interactions | B_stress_interactions | -0.002141 [-0.005440, +0.000987] | -0.007169 [-0.016264, +0.001418] |
| seed:43 | B_joint_interactions_neutral_raw | B_stress_interactions_neutral_raw | -0.003428 [-0.006579, -0.000433] | -0.010991 [-0.019323, -0.003200] |
| seed:43 | B_joint_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | -0.001939 [-0.004374, +0.000495] | -0.004071 [-0.011242, +0.002847] |
| seed:43 | B_joint_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | -0.002051 [-0.004469, +0.000436] | -0.002821 [-0.009471, +0.003647] |
| seed:43 | A_input | B_stress_input | +0.009760 [+0.004237, +0.015709] | +0.032797 [+0.015494, +0.050377] |
| seed:43 | A_interactions | B_stress_interactions | +0.007682 [+0.002592, +0.013623] | +0.023737 [+0.008830, +0.040633] |
| seed:43 | A_interactions_neutral_raw | B_stress_interactions_neutral_raw | +0.008690 [+0.003486, +0.014617] | +0.025642 [+0.010222, +0.042308] |
| seed:43 | A_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | +0.004416 [+0.001245, +0.007437] | +0.013596 [+0.003112, +0.023667] |
| seed:43 | A_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | +0.004410 [+0.002095, +0.006611] | +0.013471 [+0.004925, +0.021494] |
| ensemble:mean_probability | prior | A_input | +0.048375 [+0.034307, +0.062247] | +0.139238 [+0.109210, +0.169413] |
| ensemble:mean_probability | prior | A_interactions | +0.057386 [+0.044035, +0.072102] | +0.167476 [+0.137714, +0.200895] |
| ensemble:mean_probability | prior | A_interactions_neutral_raw | +0.057099 [+0.043612, +0.071953] | +0.167028 [+0.136752, +0.200799] |
| ensemble:mean_probability | prior | A_interactions_neutral_scored | +0.084610 [+0.068560, +0.100557] | +0.244483 [+0.208251, +0.280836] |
| ensemble:mean_probability | prior | A_interactions_oracle | +0.084723 [+0.065895, +0.104065] | +0.242692 [+0.198398, +0.288371] |
| ensemble:mean_probability | prior | A_interactions_oracle_neutral_raw | +0.089352 [+0.070905, +0.107850] | +0.255004 [+0.212072, +0.298961] |
| ensemble:mean_probability | prior | A_interactions_oracle_neutral_scored | +0.093780 [+0.075613, +0.111874] | +0.268319 [+0.226692, +0.310961] |
| ensemble:mean_probability | A_input | A_interactions | +0.009011 [+0.004334, +0.014778] | +0.028239 [+0.013848, +0.043269] |
| ensemble:mean_probability | A_interactions | A_interactions_neutral_raw | -0.000287 [-0.001259, +0.000583] | -0.000448 [-0.003207, +0.002110] |
| ensemble:mean_probability | A_interactions | A_interactions_neutral_scored | +0.027224 [+0.019635, +0.034768] | +0.077007 [+0.056885, +0.097783] |
| ensemble:mean_probability | A_interactions | A_interactions_oracle | +0.027336 [+0.018460, +0.037211] | +0.075216 [+0.049461, +0.103564] |
| ensemble:mean_probability | A_interactions_oracle | A_interactions_oracle_neutral_raw | +0.004629 [+0.002014, +0.007164] | +0.012313 [+0.005490, +0.019363] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | A_interactions_oracle_neutral_scored | +0.004428 [+0.001863, +0.006908] | +0.013315 [+0.006581, +0.020185] |
| ensemble:mean_probability | A_interactions_neutral_raw | A_interactions_neutral_scored | +0.027511 [+0.019774, +0.035021] | +0.077455 [+0.056764, +0.098082] |
| ensemble:mean_probability | A_interactions_neutral_raw | A_interactions_oracle_neutral_raw | +0.032253 [+0.023493, +0.041874] | +0.087976 [+0.062590, +0.114261] |
| ensemble:mean_probability | A_interactions_neutral_scored | A_interactions_oracle_neutral_scored | +0.009171 [+0.003850, +0.013950] | +0.023836 [+0.008639, +0.037905] |
| ensemble:mean_probability | A_input | B_input_confidence | +0.007220 [+0.002424, +0.011953] | +0.022220 [+0.008411, +0.036229] |
| ensemble:mean_probability | A_interactions | B_interactions_confidence | +0.006933 [+0.002194, +0.011878] | +0.018820 [+0.004961, +0.033520] |
| ensemble:mean_probability | A_interactions_neutral_raw | B_interactions_neutral_raw_confidence | +0.008770 [+0.003782, +0.014211] | +0.023162 [+0.008603, +0.038989] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | B_interactions_oracle_neutral_raw_confidence | +0.003666 [+0.001484, +0.005842] | +0.009455 [+0.002283, +0.016825] |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | B_interactions_oracle_neutral_scored_confidence | +0.003380 [+0.001404, +0.005188] | +0.007477 [+0.001579, +0.013112] |
| ensemble:mean_probability | B_input_confidence | B_interactions_confidence | +0.008724 [+0.004375, +0.013744] | +0.024839 [+0.010891, +0.039471] |
| ensemble:mean_probability | B_interactions_confidence | B_interactions_neutral_raw_confidence | +0.001550 [-0.000212, +0.003347] | +0.003894 [-0.000633, +0.008523] |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | B_interactions_oracle_neutral_scored_confidence | +0.004142 [+0.001885, +0.006335] | +0.011336 [+0.004343, +0.018457] |
| ensemble:mean_probability | A_input | B_event_input | +0.010894 [+0.005351, +0.016717] | +0.038764 [+0.025055, +0.052770] |
| ensemble:mean_probability | A_interactions | B_event_interactions | +0.006907 [+0.002434, +0.011772] | +0.022958 [+0.010989, +0.035524] |
| ensemble:mean_probability | A_interactions_neutral_raw | B_event_interactions_neutral_raw | +0.008641 [+0.003700, +0.013880] | +0.026816 [+0.013825, +0.040762] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_raw | +0.005453 [+0.002496, +0.008122] | +0.014883 [+0.004908, +0.024115] |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | B_event_interactions_oracle_neutral_scored | +0.005499 [+0.003110, +0.007918] | +0.014337 [+0.006231, +0.022852] |
| ensemble:mean_probability | B_input_confidence | B_event_input | +0.003674 [-0.000439, +0.008519] | +0.016545 [+0.004880, +0.029728] |
| ensemble:mean_probability | B_interactions_confidence | B_event_interactions | -0.000026 [-0.002814, +0.002933] | +0.004137 [-0.004755, +0.013040] |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | B_event_interactions_neutral_raw | -0.000129 [-0.002829, +0.002764] | +0.003653 [-0.004461, +0.012186] |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | B_event_interactions_oracle_neutral_raw | +0.001788 [-0.001261, +0.004740] | +0.005428 [-0.003104, +0.013618] |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | B_event_interactions_oracle_neutral_scored | +0.002119 [-0.000633, +0.004746] | +0.006860 [-0.000839, +0.014429] |
| ensemble:mean_probability | B_event_input | B_event_interactions | +0.005024 [+0.001649, +0.008197] | +0.012432 [+0.000484, +0.022839] |
| ensemble:mean_probability | B_event_interactions | B_event_interactions_neutral_raw | +0.001447 [-0.000591, +0.003430] | +0.003410 [-0.001868, +0.008705] |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | B_event_interactions_oracle_neutral_scored | +0.004474 [+0.002609, +0.006384] | +0.012768 [+0.007101, +0.018615] |
| ensemble:mean_probability | B_input_confidence | B_joint_input | +0.007381 [+0.002367, +0.012872] | +0.026748 [+0.013646, +0.041021] |
| ensemble:mean_probability | B_interactions_confidence | B_joint_interactions | +0.003142 [+0.000158, +0.006277] | +0.012809 [+0.004267, +0.021599] |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | B_joint_interactions_neutral_raw | +0.002773 [-0.000012, +0.005795] | +0.011655 [+0.003859, +0.019562] |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | B_joint_interactions_oracle_neutral_raw | +0.001925 [-0.000915, +0.004543] | +0.006127 [-0.003127, +0.014245] |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | B_joint_interactions_oracle_neutral_scored | +0.002373 [-0.000121, +0.004862] | +0.006792 [-0.001444, +0.014763] |
| ensemble:mean_probability | B_event_input | B_joint_input | +0.003707 [+0.001165, +0.006458] | +0.010203 [+0.002404, +0.018305] |
| ensemble:mean_probability | B_event_interactions | B_joint_interactions | +0.003168 [+0.000907, +0.005784] | +0.008671 [+0.001532, +0.016255] |
| ensemble:mean_probability | B_event_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.002902 [+0.000680, +0.005446] | +0.008001 [+0.001293, +0.015077] |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | +0.000138 [-0.001240, +0.001483] | +0.000699 [-0.003601, +0.004607] |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.000254 [-0.001031, +0.001512] | -0.000068 [-0.004041, +0.003509] |
| ensemble:mean_probability | A_input | B_joint_input | +0.014601 [+0.007108, +0.022087] | +0.048968 [+0.030230, +0.068494] |
| ensemble:mean_probability | A_interactions | B_joint_interactions | +0.010075 [+0.004233, +0.016426] | +0.031629 [+0.015995, +0.048631] |
| ensemble:mean_probability | A_interactions_neutral_raw | B_joint_interactions_neutral_raw | +0.011543 [+0.005578, +0.018083] | +0.034817 [+0.018336, +0.052895] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_raw | +0.005591 [+0.002125, +0.008588] | +0.015582 [+0.003194, +0.026786] |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | B_joint_interactions_oracle_neutral_scored | +0.005753 [+0.003064, +0.008218] | +0.014269 [+0.004371, +0.023907] |
| ensemble:mean_probability | B_joint_input | B_joint_interactions | +0.004486 [+0.001217, +0.007529] | +0.010900 [-0.000366, +0.020883] |
| ensemble:mean_probability | B_joint_interactions | B_joint_interactions_neutral_raw | +0.001181 [-0.000764, +0.003243] | +0.002740 [-0.002652, +0.008316] |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | B_joint_interactions_oracle_neutral_scored | +0.004590 [+0.002690, +0.006445] | +0.012001 [+0.006027, +0.017989] |
| ensemble:mean_probability | B_input_confidence | B_stress_input | +0.003233 [+0.001398, +0.005083] | +0.011267 [+0.006258, +0.016193] |
| ensemble:mean_probability | B_interactions_confidence | B_stress_interactions | +0.001273 [-0.000948, +0.003224] | +0.005941 [+0.000118, +0.011041] |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | B_stress_interactions_neutral_raw | -0.000002 [-0.001693, +0.001435] | +0.002322 [-0.001814, +0.006229] |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | B_stress_interactions_oracle_neutral_raw | +0.000862 [-0.001142, +0.002452] | +0.004314 [-0.000973, +0.008982] |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | B_stress_interactions_oracle_neutral_scored | +0.001275 [-0.000341, +0.002760] | +0.006274 [+0.000772, +0.011440] |
| ensemble:mean_probability | B_joint_input | B_stress_input | -0.004147 [-0.010102, +0.001370] | -0.015481 [-0.031877, -0.000184] |
| ensemble:mean_probability | B_joint_interactions | B_stress_interactions | -0.001869 [-0.005338, +0.001387] | -0.006868 [-0.016496, +0.002188] |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | B_stress_interactions_neutral_raw | -0.002775 [-0.005959, +0.000246] | -0.009332 [-0.017851, -0.001304] |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | -0.001063 [-0.003696, +0.001445] | -0.001813 [-0.009149, +0.005697] |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | -0.001098 [-0.003683, +0.001363] | -0.000518 [-0.007668, +0.006318] |
| ensemble:mean_probability | A_input | B_stress_input | +0.010453 [+0.004978, +0.016090] | +0.033487 [+0.017852, +0.050236] |
| ensemble:mean_probability | A_interactions | B_stress_interactions | +0.008206 [+0.003279, +0.014084] | +0.024761 [+0.009952, +0.041167] |
| ensemble:mean_probability | A_interactions_neutral_raw | B_stress_interactions_neutral_raw | +0.008768 [+0.003619, +0.014632] | +0.025485 [+0.009791, +0.042098] |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | B_stress_interactions_oracle_neutral_raw | +0.004528 [+0.001500, +0.007343] | +0.013769 [+0.003754, +0.023501] |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | B_stress_interactions_oracle_neutral_scored | +0.004655 [+0.002332, +0.006811] | +0.013750 [+0.005280, +0.021871] |

## All condition, query, load and original-split cells

Calibration-bin counts, means and observed failure rates are retained in the machine-readable review for every cell. Original train/development labels are descriptive strata; the new template folds define the statistical training boundaries.

| Evaluation | Predictor | Axis | Cell | n | Failures | Brier | Log loss |
|---|---|---|---|---:|---:|---:|---:|
| seed:17 | prior | available_bindings | 2 | 3072 | 519 | 0.145335 | 0.468842 |
| seed:17 | prior | available_bindings | 4 | 3072 | 935 | 0.216540 | 0.627129 |
| seed:17 | prior | condition | informative | 3072 | 431 | 0.130204 | 0.435164 |
| seed:17 | prior | condition | misleading | 3072 | 1023 | 0.231671 | 0.660807 |
| seed:17 | prior | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.064135 | 0.287997 |
| seed:17 | prior | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.083792 | 0.331803 |
| seed:17 | prior | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.089103 | 0.343731 |
| seed:17 | prior | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.088713 | 0.342618 |
| seed:17 | prior | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.157369 | 0.495706 |
| seed:17 | prior | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.133915 | 0.443669 |
| seed:17 | prior | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.240920 | 0.681074 |
| seed:17 | prior | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.207493 | 0.607350 |
| seed:17 | prior | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.084880 | 0.334230 |
| seed:17 | prior | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.109507 | 0.388988 |
| seed:17 | prior | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.163411 | 0.509091 |
| seed:17 | prior | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.109379 | 0.388630 |
| seed:17 | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.307408 | 0.829334 |
| seed:17 | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.237903 | 0.674959 |
| seed:17 | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.491301 | 1.237478 |
| seed:17 | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.436858 | 1.117348 |
| seed:17 | prior | original_split | development | 1536 | 374 | 0.184360 | 0.555492 |
| seed:17 | prior | original_split | train | 4608 | 1080 | 0.179797 | 0.545483 |
| seed:17 | prior | query_role | current | 3072 | 236 | 0.096425 | 0.359862 |
| seed:17 | prior | query_role | saved | 3072 | 1218 | 0.265450 | 0.736110 |
| seed:17 | A_input | available_bindings | 2 | 3072 | 519 | 0.121499 | 0.379074 |
| seed:17 | A_input | available_bindings | 4 | 3072 | 935 | 0.145126 | 0.441251 |
| seed:17 | A_input | condition | informative | 3072 | 431 | 0.113016 | 0.356897 |
| seed:17 | A_input | condition | misleading | 3072 | 1023 | 0.153608 | 0.463428 |
| seed:17 | A_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014837 | 0.070719 |
| seed:17 | A_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048517 | 0.183761 |
| seed:17 | A_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.047913 | 0.164981 |
| seed:17 | A_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053426 | 0.190207 |
| seed:17 | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.155793 | 0.491590 |
| seed:17 | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.128894 | 0.431680 |
| seed:17 | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.218808 | 0.628481 |
| seed:17 | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.225526 | 0.646930 |
| seed:17 | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.048580 | 0.187349 |
| seed:17 | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.081089 | 0.271069 |
| seed:17 | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.161460 | 0.519661 |
| seed:17 | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083091 | 0.291470 |
| seed:17 | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.250626 | 0.695459 |
| seed:17 | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.235574 | 0.665375 |
| seed:17 | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.158162 | 0.496966 |
| seed:17 | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.217292 | 0.627382 |
| seed:17 | A_input | original_split | development | 1536 | 374 | 0.127168 | 0.391693 |
| seed:17 | A_input | original_split | train | 4608 | 1080 | 0.135360 | 0.416319 |
| seed:17 | A_input | query_role | current | 3072 | 236 | 0.064051 | 0.226187 |
| seed:17 | A_input | query_role | saved | 3072 | 1218 | 0.202574 | 0.594138 |
| seed:17 | A_interactions | available_bindings | 2 | 3072 | 519 | 0.116622 | 0.359229 |
| seed:17 | A_interactions | available_bindings | 4 | 3072 | 935 | 0.130610 | 0.402464 |
| seed:17 | A_interactions | condition | informative | 3072 | 431 | 0.102601 | 0.323853 |
| seed:17 | A_interactions | condition | misleading | 3072 | 1023 | 0.144631 | 0.437841 |
| seed:17 | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.021884 | 0.089023 |
| seed:17 | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.045108 | 0.158698 |
| seed:17 | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042904 | 0.150550 |
| seed:17 | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051031 | 0.173975 |
| seed:17 | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.150095 | 0.469807 |
| seed:17 | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.123306 | 0.406125 |
| seed:17 | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.224513 | 0.641992 |
| seed:17 | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.184449 | 0.546618 |
| seed:17 | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.055632 | 0.192856 |
| seed:17 | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.075367 | 0.243005 |
| seed:17 | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157424 | 0.526538 |
| seed:17 | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.076613 | 0.263730 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.247634 | 0.688090 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.218330 | 0.627655 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.145408 | 0.465344 |
| seed:17 | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.200786 | 0.590621 |
| seed:17 | A_interactions | original_split | development | 1536 | 374 | 0.126728 | 0.388665 |
| seed:17 | A_interactions | original_split | train | 4608 | 1080 | 0.122579 | 0.378241 |
| seed:17 | A_interactions | query_role | current | 3072 | 236 | 0.061478 | 0.209841 |
| seed:17 | A_interactions | query_role | saved | 3072 | 1218 | 0.185754 | 0.551852 |
| seed:17 | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.116687 | 0.359597 |
| seed:17 | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.130963 | 0.402900 |
| seed:17 | A_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.102565 | 0.323995 |
| seed:17 | A_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.145086 | 0.438502 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.021626 | 0.088102 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.045520 | 0.161783 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042152 | 0.149226 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050310 | 0.170956 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.147564 | 0.460822 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.124829 | 0.412003 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.225651 | 0.644789 |
| seed:17 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.184483 | 0.546821 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.055842 | 0.193588 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.075707 | 0.243527 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.154769 | 0.514530 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.076452 | 0.261592 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.241869 | 0.671899 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.220616 | 0.633065 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.148661 | 0.475382 |
| seed:17 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.203131 | 0.597768 |
| seed:17 | A_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.125420 | 0.384396 |
| seed:17 | A_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.123294 | 0.380200 |
| seed:17 | A_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.061274 | 0.208796 |
| seed:17 | A_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.186376 | 0.553701 |
| seed:17 | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.085486 | 0.268601 |
| seed:17 | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.106997 | 0.338461 |
| seed:17 | A_interactions_neutral_scored | condition | informative | 3072 | 431 | 0.081864 | 0.255723 |
| seed:17 | A_interactions_neutral_scored | condition | misleading | 3072 | 1023 | 0.110618 | 0.351339 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023093 | 0.089349 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033256 | 0.122083 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028254 | 0.106357 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.042358 | 0.146505 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.105328 | 0.322808 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.100274 | 0.301131 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.176846 | 0.515649 |
| seed:17 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.151376 | 0.453131 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.037206 | 0.135306 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.044382 | 0.143322 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.130562 | 0.427580 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.057202 | 0.212722 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.150646 | 0.468700 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.176866 | 0.536989 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.112064 | 0.344190 |
| seed:17 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.173102 | 0.533500 |
| seed:17 | A_interactions_neutral_scored | original_split | development | 1536 | 374 | 0.090023 | 0.285508 |
| seed:17 | A_interactions_neutral_scored | original_split | train | 4608 | 1080 | 0.098314 | 0.309539 |
| seed:17 | A_interactions_neutral_scored | query_role | current | 3072 | 236 | 0.045324 | 0.160042 |
| seed:17 | A_interactions_neutral_scored | query_role | saved | 3072 | 1218 | 0.147159 | 0.447021 |
| seed:17 | A_interactions_oracle | available_bindings | 2 | 3072 | 519 | 0.091371 | 0.291584 |
| seed:17 | A_interactions_oracle | available_bindings | 4 | 3072 | 935 | 0.101476 | 0.322303 |
| seed:17 | A_interactions_oracle | condition | informative | 3072 | 431 | 0.079280 | 0.254667 |
| seed:17 | A_interactions_oracle | condition | misleading | 3072 | 1023 | 0.113567 | 0.359220 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.033380 | 0.117683 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041488 | 0.155790 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.035479 | 0.127689 |
| seed:17 | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.046295 | 0.156237 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.104417 | 0.320327 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.091594 | 0.292783 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.157446 | 0.467974 |
| seed:17 | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.134080 | 0.412973 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.058010 | 0.189910 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.059327 | 0.194142 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.120532 | 0.398673 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.061682 | 0.215000 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.158541 | 0.487123 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.178643 | 0.549270 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.108028 | 0.349547 |
| seed:17 | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.160732 | 0.494068 |
| seed:17 | A_interactions_oracle | original_split | development | 1536 | 374 | 0.094182 | 0.297831 |
| seed:17 | A_interactions_oracle | original_split | train | 4608 | 1080 | 0.097171 | 0.309981 |
| seed:17 | A_interactions_oracle | query_role | current | 3072 | 236 | 0.053414 | 0.183227 |
| seed:17 | A_interactions_oracle | query_role | saved | 3072 | 1218 | 0.139433 | 0.430660 |
| seed:17 | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.085750 | 0.276913 |
| seed:17 | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.098466 | 0.313934 |
| seed:17 | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.075231 | 0.244903 |
| seed:17 | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.108986 | 0.345945 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.032188 | 0.111817 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.038227 | 0.148957 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028942 | 0.115448 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.041732 | 0.142582 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.096318 | 0.295902 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087411 | 0.288019 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.132053 | 0.410997 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.135263 | 0.414994 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.043561 | 0.151312 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.053181 | 0.171753 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.117449 | 0.378146 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.055291 | 0.198941 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.145421 | 0.453111 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.176936 | 0.546681 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.111459 | 0.348429 |
| seed:17 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.162372 | 0.499762 |
| seed:17 | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.085407 | 0.273109 |
| seed:17 | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.094342 | 0.302862 |
| seed:17 | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.047860 | 0.167096 |
| seed:17 | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.136356 | 0.423751 |
| seed:17 | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.080906 | 0.259517 |
| seed:17 | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.094187 | 0.302969 |
| seed:17 | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.072247 | 0.231902 |
| seed:17 | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.102846 | 0.330583 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.031061 | 0.106155 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.034692 | 0.130579 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.027348 | 0.108624 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.039420 | 0.134610 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.091618 | 0.284077 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087126 | 0.272192 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.133480 | 0.410917 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.128673 | 0.396304 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.037099 | 0.133092 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.044106 | 0.137662 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.119352 | 0.381654 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.050951 | 0.188665 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.135726 | 0.427949 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.171763 | 0.541032 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.095773 | 0.306476 |
| seed:17 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.157861 | 0.493137 |
| seed:17 | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.080580 | 0.259185 |
| seed:17 | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.089869 | 0.288595 |
| seed:17 | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.043753 | 0.152421 |
| seed:17 | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.131340 | 0.410064 |
| seed:17 | B_input_confidence | available_bindings | 2 | 3072 | 519 | 0.111069 | 0.348508 |
| seed:17 | B_input_confidence | available_bindings | 4 | 3072 | 935 | 0.140893 | 0.427921 |
| seed:17 | B_input_confidence | condition | informative | 3072 | 431 | 0.103019 | 0.327071 |
| seed:17 | B_input_confidence | condition | misleading | 3072 | 1023 | 0.148942 | 0.449358 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.015132 | 0.076581 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.047988 | 0.179907 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046337 | 0.161200 |
| seed:17 | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053590 | 0.191011 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.142902 | 0.442552 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.107220 | 0.354960 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.201496 | 0.585216 |
| seed:17 | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.203956 | 0.594099 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.050983 | 0.185171 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.076790 | 0.253296 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.163426 | 0.512195 |
| seed:17 | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083058 | 0.280710 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.232530 | 0.663819 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.213641 | 0.618822 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.175820 | 0.533037 |
| seed:17 | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.218264 | 0.629871 |
| seed:17 | B_input_confidence | original_split | development | 1536 | 374 | 0.122514 | 0.377324 |
| seed:17 | B_input_confidence | original_split | train | 4608 | 1080 | 0.127136 | 0.391844 |
| seed:17 | B_input_confidence | query_role | current | 3072 | 236 | 0.063514 | 0.220347 |
| seed:17 | B_input_confidence | query_role | saved | 3072 | 1218 | 0.188447 | 0.556082 |
| seed:17 | B_interactions_confidence | available_bindings | 2 | 3072 | 519 | 0.105303 | 0.326444 |
| seed:17 | B_interactions_confidence | available_bindings | 4 | 3072 | 935 | 0.128175 | 0.398289 |
| seed:17 | B_interactions_confidence | condition | informative | 3072 | 431 | 0.093563 | 0.296740 |
| seed:17 | B_interactions_confidence | condition | misleading | 3072 | 1023 | 0.139915 | 0.427993 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028735 | 0.109401 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.044191 | 0.155396 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046281 | 0.155159 |
| seed:17 | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053279 | 0.186557 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.134151 | 0.405955 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.097202 | 0.321241 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.212175 | 0.613767 |
| seed:17 | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.165863 | 0.496557 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.062254 | 0.205397 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.070863 | 0.230677 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157129 | 0.522266 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.076694 | 0.266083 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.225826 | 0.639517 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.194078 | 0.571213 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.163405 | 0.504522 |
| seed:17 | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.203605 | 0.603449 |
| seed:17 | B_interactions_confidence | original_split | development | 1536 | 374 | 0.123410 | 0.376354 |
| seed:17 | B_interactions_confidence | original_split | train | 4608 | 1080 | 0.114515 | 0.357704 |
| seed:17 | B_interactions_confidence | query_role | current | 3072 | 236 | 0.062311 | 0.213104 |
| seed:17 | B_interactions_confidence | query_role | saved | 3072 | 1218 | 0.171166 | 0.511628 |
| seed:17 | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.100495 | 0.315095 |
| seed:17 | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.129644 | 0.401514 |
| seed:17 | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.091278 | 0.292049 |
| seed:17 | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.138861 | 0.424560 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027798 | 0.107184 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043220 | 0.153730 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042932 | 0.149231 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051903 | 0.182911 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.122812 | 0.374482 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.092920 | 0.313297 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.198658 | 0.584006 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.168756 | 0.505988 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053448 | 0.185542 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.069487 | 0.223710 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157547 | 0.505245 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.074749 | 0.259737 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.206951 | 0.596343 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.191836 | 0.568059 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.174886 | 0.530502 |
| seed:17 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.212078 | 0.624833 |
| seed:17 | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.116337 | 0.358007 |
| seed:17 | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.114647 | 0.358404 |
| seed:17 | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.060294 | 0.206789 |
| seed:17 | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.169844 | 0.509820 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.082417 | 0.270572 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.093864 | 0.299904 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.069295 | 0.229660 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.106986 | 0.340816 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028545 | 0.099012 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.035794 | 0.149067 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.030078 | 0.112627 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.033943 | 0.115744 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.087584 | 0.281357 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.085152 | 0.278670 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.132345 | 0.410089 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.122980 | 0.387743 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.042654 | 0.147086 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.049832 | 0.167680 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.109067 | 0.355075 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.047250 | 0.168085 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.141971 | 0.450473 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.173347 | 0.539053 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.117600 | 0.372432 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.168554 | 0.517921 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.082550 | 0.267173 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.090004 | 0.291260 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.042917 | 0.151918 |
| seed:17 | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.133363 | 0.418558 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 519 | 0.077982 | 0.254648 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 935 | 0.089796 | 0.291010 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 431 | 0.066874 | 0.218594 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 1023 | 0.100904 | 0.327064 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026772 | 0.092840 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033207 | 0.131928 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028508 | 0.106146 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031918 | 0.110283 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.085387 | 0.273600 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.083863 | 0.261923 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.137341 | 0.417799 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.117386 | 0.372521 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.036178 | 0.128384 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.041943 | 0.135179 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.113403 | 0.360491 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.043569 | 0.159750 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.135193 | 0.434443 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.167113 | 0.534224 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.098916 | 0.325980 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.162514 | 0.512210 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 374 | 0.078769 | 0.255746 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 1080 | 0.085596 | 0.278523 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 236 | 0.039410 | 0.138653 |
| seed:17 | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 1218 | 0.128368 | 0.407005 |
| seed:17 | B_event_input | available_bindings | 2 | 3072 | 519 | 0.111048 | 0.340214 |
| seed:17 | B_event_input | available_bindings | 4 | 3072 | 935 | 0.134861 | 0.407849 |
| seed:17 | B_event_input | condition | informative | 3072 | 431 | 0.094015 | 0.297357 |
| seed:17 | B_event_input | condition | misleading | 3072 | 1023 | 0.151894 | 0.450706 |
| seed:17 | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.016832 | 0.074962 |
| seed:17 | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.045202 | 0.155628 |
| seed:17 | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042610 | 0.151102 |
| seed:17 | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.055476 | 0.190621 |
| seed:17 | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.134803 | 0.419768 |
| seed:17 | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.108866 | 0.346538 |
| seed:17 | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.197241 | 0.576014 |
| seed:17 | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.163917 | 0.491644 |
| seed:17 | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.050515 | 0.176717 |
| seed:17 | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.077257 | 0.252319 |
| seed:17 | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.158562 | 0.491958 |
| seed:17 | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.078212 | 0.257220 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.235018 | 0.663683 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.216376 | 0.619235 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.196738 | 0.581577 |
| seed:17 | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.230697 | 0.658059 |
| seed:17 | B_event_input | original_split | development | 1536 | 374 | 0.122457 | 0.372576 |
| seed:17 | B_event_input | original_split | train | 4608 | 1080 | 0.123120 | 0.374517 |
| seed:17 | B_event_input | query_role | current | 3072 | 236 | 0.062256 | 0.209059 |
| seed:17 | B_event_input | query_role | saved | 3072 | 1218 | 0.183653 | 0.539004 |
| seed:17 | B_event_interactions | available_bindings | 2 | 3072 | 519 | 0.106854 | 0.326863 |
| seed:17 | B_event_interactions | available_bindings | 4 | 3072 | 935 | 0.128166 | 0.394087 |
| seed:17 | B_event_interactions | condition | informative | 3072 | 431 | 0.090171 | 0.285816 |
| seed:17 | B_event_interactions | condition | misleading | 3072 | 1023 | 0.144849 | 0.435133 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024784 | 0.095978 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043909 | 0.154437 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042621 | 0.144373 |
| seed:17 | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.055028 | 0.191881 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.129663 | 0.392590 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.104474 | 0.332318 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.206082 | 0.599265 |
| seed:17 | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.147565 | 0.446479 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.057380 | 0.194769 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.072674 | 0.231289 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.149665 | 0.469745 |
| seed:17 | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075027 | 0.256417 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.230120 | 0.645613 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.199093 | 0.578659 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.184156 | 0.549657 |
| seed:17 | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.221071 | 0.644229 |
| seed:17 | B_event_interactions | original_split | development | 1536 | 374 | 0.122201 | 0.368412 |
| seed:17 | B_event_interactions | original_split | train | 4608 | 1080 | 0.115946 | 0.357829 |
| seed:17 | B_event_interactions | query_role | current | 3072 | 236 | 0.061384 | 0.207500 |
| seed:17 | B_event_interactions | query_role | saved | 3072 | 1218 | 0.173635 | 0.513449 |
| seed:17 | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.102029 | 0.313910 |
| seed:17 | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.129732 | 0.398522 |
| seed:17 | B_event_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.088035 | 0.280240 |
| seed:17 | B_event_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.143727 | 0.432192 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024951 | 0.094281 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043576 | 0.150090 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.041979 | 0.146703 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053781 | 0.189548 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.117518 | 0.359717 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.098869 | 0.318547 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.192572 | 0.570038 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.150934 | 0.455746 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053321 | 0.182846 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.071264 | 0.225440 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.149456 | 0.454802 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075370 | 0.256257 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.213928 | 0.607112 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.193610 | 0.567403 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.193592 | 0.576779 |
| seed:17 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.227111 | 0.661689 |
| seed:17 | B_event_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.116419 | 0.353020 |
| seed:17 | B_event_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.115701 | 0.357281 |
| seed:17 | B_event_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.060545 | 0.203621 |
| seed:17 | B_event_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.171216 | 0.508810 |
| seed:17 | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.080527 | 0.265184 |
| seed:17 | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.093824 | 0.298364 |
| seed:17 | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.067507 | 0.225461 |
| seed:17 | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.106844 | 0.338088 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024818 | 0.090055 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.034721 | 0.147272 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.026239 | 0.102912 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031706 | 0.112201 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.085717 | 0.270666 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084591 | 0.275182 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.124773 | 0.394647 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.122460 | 0.388247 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.042125 | 0.146357 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.049964 | 0.167430 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.100770 | 0.313252 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.044433 | 0.157035 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.145433 | 0.468139 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.164837 | 0.513615 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.110862 | 0.346456 |
| seed:17 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.179229 | 0.543214 |
| seed:17 | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.079902 | 0.258975 |
| seed:17 | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.089600 | 0.289374 |
| seed:17 | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040847 | 0.145582 |
| seed:17 | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.133504 | 0.417967 |
| seed:17 | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.076339 | 0.251011 |
| seed:17 | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.089340 | 0.288416 |
| seed:17 | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.064837 | 0.215687 |
| seed:17 | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.100842 | 0.323740 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023513 | 0.084421 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.031884 | 0.137268 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.024027 | 0.093422 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.029887 | 0.107547 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.082850 | 0.261698 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084461 | 0.263658 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.127930 | 0.397466 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.115316 | 0.370385 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.036218 | 0.128648 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.041456 | 0.133887 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.104621 | 0.318912 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.041813 | 0.149207 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.139038 | 0.452393 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.159420 | 0.507674 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.091958 | 0.300868 |
| seed:17 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.172109 | 0.535122 |
| seed:17 | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.075981 | 0.247082 |
| seed:17 | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.085126 | 0.277257 |
| seed:17 | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.037499 | 0.133619 |
| seed:17 | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.128180 | 0.405808 |
| seed:17 | B_joint_input | available_bindings | 2 | 3072 | 519 | 0.107060 | 0.329123 |
| seed:17 | B_joint_input | available_bindings | 4 | 3072 | 935 | 0.129593 | 0.393014 |
| seed:17 | B_joint_input | condition | informative | 3072 | 431 | 0.089977 | 0.285523 |
| seed:17 | B_joint_input | condition | misleading | 3072 | 1023 | 0.146676 | 0.436614 |
| seed:17 | B_joint_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.019117 | 0.086076 |
| seed:17 | B_joint_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043556 | 0.150666 |
| seed:17 | B_joint_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043732 | 0.154786 |
| seed:17 | B_joint_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049898 | 0.170781 |
| seed:17 | B_joint_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.129283 | 0.397367 |
| seed:17 | B_joint_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.100992 | 0.324288 |
| seed:17 | B_joint_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.205022 | 0.598948 |
| seed:17 | B_joint_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.157241 | 0.475641 |
| seed:17 | B_joint_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053143 | 0.175599 |
| seed:17 | B_joint_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.074621 | 0.241565 |
| seed:17 | B_joint_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.161849 | 0.501798 |
| seed:17 | B_joint_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069881 | 0.228983 |
| seed:17 | B_joint_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.236835 | 0.673588 |
| seed:17 | B_joint_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.203999 | 0.591901 |
| seed:17 | B_joint_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.180901 | 0.543158 |
| seed:17 | B_joint_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.226727 | 0.651324 |
| seed:17 | B_joint_input | original_split | development | 1536 | 374 | 0.122355 | 0.371996 |
| seed:17 | B_joint_input | original_split | train | 4608 | 1080 | 0.116984 | 0.357426 |
| seed:17 | B_joint_input | query_role | current | 3072 | 236 | 0.059238 | 0.197820 |
| seed:17 | B_joint_input | query_role | saved | 3072 | 1218 | 0.177415 | 0.524317 |
| seed:17 | B_joint_interactions | available_bindings | 2 | 3072 | 519 | 0.102878 | 0.316057 |
| seed:17 | B_joint_interactions | available_bindings | 4 | 3072 | 935 | 0.124649 | 0.384077 |
| seed:17 | B_joint_interactions | condition | informative | 3072 | 431 | 0.086803 | 0.275948 |
| seed:17 | B_joint_interactions | condition | misleading | 3072 | 1023 | 0.140725 | 0.424185 |
| seed:17 | B_joint_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027077 | 0.102605 |
| seed:17 | B_joint_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042392 | 0.146511 |
| seed:17 | B_joint_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044687 | 0.151165 |
| seed:17 | B_joint_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050078 | 0.173886 |
| seed:17 | B_joint_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.126857 | 0.379378 |
| seed:17 | B_joint_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.093819 | 0.306828 |
| seed:17 | B_joint_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.213159 | 0.623962 |
| seed:17 | B_joint_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.144464 | 0.440177 |
| seed:17 | B_joint_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.061177 | 0.200264 |
| seed:17 | B_joint_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.069055 | 0.219860 |
| seed:17 | B_joint_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156355 | 0.487617 |
| seed:17 | B_joint_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069753 | 0.237356 |
| seed:17 | B_joint_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.231177 | 0.650138 |
| seed:17 | B_joint_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.188859 | 0.556950 |
| seed:17 | B_joint_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.170758 | 0.517684 |
| seed:17 | B_joint_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.217029 | 0.636063 |
| seed:17 | B_joint_interactions | original_split | development | 1536 | 374 | 0.123128 | 0.370433 |
| seed:17 | B_joint_interactions | original_split | train | 4608 | 1080 | 0.110642 | 0.343278 |
| seed:17 | B_joint_interactions | query_role | current | 3072 | 236 | 0.059271 | 0.198592 |
| seed:17 | B_joint_interactions | query_role | saved | 3072 | 1218 | 0.168257 | 0.501541 |
| seed:17 | B_joint_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.098716 | 0.306225 |
| seed:17 | B_joint_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.126917 | 0.390266 |
| seed:17 | B_joint_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.085773 | 0.274322 |
| seed:17 | B_joint_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.139860 | 0.422169 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026122 | 0.098911 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042035 | 0.147281 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043905 | 0.150425 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049717 | 0.174541 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.116249 | 0.351001 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.091811 | 0.303688 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.200115 | 0.595987 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.149162 | 0.452180 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054132 | 0.183234 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068252 | 0.216375 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156267 | 0.474869 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069438 | 0.237188 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.209580 | 0.597926 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.187153 | 0.554474 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.181308 | 0.544997 |
| seed:17 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.224565 | 0.656109 |
| seed:17 | B_joint_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.116147 | 0.352368 |
| seed:17 | B_joint_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.111706 | 0.346871 |
| seed:17 | B_joint_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.058234 | 0.195952 |
| seed:17 | B_joint_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.167399 | 0.500539 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.079586 | 0.263197 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.094725 | 0.301814 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.066177 | 0.223493 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.108135 | 0.341517 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025249 | 0.091414 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.035157 | 0.157601 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.024784 | 0.097581 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031212 | 0.109911 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.081975 | 0.262719 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084125 | 0.272517 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.136317 | 0.424799 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.115901 | 0.372634 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.041443 | 0.141957 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.048417 | 0.160077 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.098911 | 0.308914 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.042881 | 0.148967 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.141584 | 0.460148 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.164691 | 0.510868 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.124947 | 0.390444 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.187695 | 0.572846 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.080455 | 0.261184 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.089389 | 0.289612 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040077 | 0.143264 |
| seed:17 | B_joint_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.134235 | 0.421747 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.074921 | 0.247541 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.090080 | 0.291483 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.063200 | 0.212504 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.101801 | 0.326519 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023929 | 0.085916 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032141 | 0.141603 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.022992 | 0.091442 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.029136 | 0.105490 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.080481 | 0.257162 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.081674 | 0.256200 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.139336 | 0.425474 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.108942 | 0.355674 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.035625 | 0.125267 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.039215 | 0.127173 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.104363 | 0.318895 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.040273 | 0.141576 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.135584 | 0.446591 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.158686 | 0.502799 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.106956 | 0.343493 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.179305 | 0.560519 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.077074 | 0.250765 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.084309 | 0.275761 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036622 | 0.130964 |
| seed:17 | B_joint_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.128379 | 0.408060 |
| seed:17 | B_stress_input | available_bindings | 2 | 3072 | 519 | 0.105484 | 0.330926 |
| seed:17 | B_stress_input | available_bindings | 4 | 3072 | 935 | 0.138197 | 0.419134 |
| seed:17 | B_stress_input | condition | informative | 3072 | 431 | 0.095996 | 0.307929 |
| seed:17 | B_stress_input | condition | misleading | 3072 | 1023 | 0.147685 | 0.442130 |
| seed:17 | B_stress_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.015709 | 0.076423 |
| seed:17 | B_stress_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.047232 | 0.179529 |
| seed:17 | B_stress_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042877 | 0.146353 |
| seed:17 | B_stress_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050828 | 0.179050 |
| seed:17 | B_stress_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.126006 | 0.391029 |
| seed:17 | B_stress_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.100127 | 0.328525 |
| seed:17 | B_stress_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.167308 | 0.512969 |
| seed:17 | B_stress_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.193343 | 0.573723 |
| seed:17 | B_stress_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.045112 | 0.160708 |
| seed:17 | B_stress_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.073142 | 0.238401 |
| seed:17 | B_stress_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157043 | 0.485007 |
| seed:17 | B_stress_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.074638 | 0.254113 |
| seed:17 | B_stress_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.228385 | 0.651104 |
| seed:17 | B_stress_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.204796 | 0.599467 |
| seed:17 | B_stress_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.193168 | 0.569241 |
| seed:17 | B_stress_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.232459 | 0.662243 |
| seed:17 | B_stress_input | original_split | development | 1536 | 374 | 0.115902 | 0.356008 |
| seed:17 | B_stress_input | original_split | train | 4608 | 1080 | 0.123820 | 0.381370 |
| seed:17 | B_stress_input | query_role | current | 3072 | 236 | 0.059599 | 0.205965 |
| seed:17 | B_stress_input | query_role | saved | 3072 | 1218 | 0.184081 | 0.544095 |
| seed:17 | B_stress_interactions | available_bindings | 2 | 3072 | 519 | 0.101587 | 0.316420 |
| seed:17 | B_stress_interactions | available_bindings | 4 | 3072 | 935 | 0.128615 | 0.395422 |
| seed:17 | B_stress_interactions | condition | informative | 3072 | 431 | 0.089226 | 0.286691 |
| seed:17 | B_stress_interactions | condition | misleading | 3072 | 1023 | 0.140975 | 0.425152 |
| seed:17 | B_stress_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029158 | 0.109363 |
| seed:17 | B_stress_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043178 | 0.159981 |
| seed:17 | B_stress_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.047776 | 0.155256 |
| seed:17 | B_stress_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049534 | 0.174396 |
| seed:17 | B_stress_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.121138 | 0.367711 |
| seed:17 | B_stress_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.092199 | 0.304628 |
| seed:17 | B_stress_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.181300 | 0.544298 |
| seed:17 | B_stress_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.164517 | 0.499290 |
| seed:17 | B_stress_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053642 | 0.180302 |
| seed:17 | B_stress_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.069223 | 0.221756 |
| seed:17 | B_stress_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.149048 | 0.465360 |
| seed:17 | B_stress_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.070352 | 0.241643 |
| seed:17 | B_stress_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.223308 | 0.634327 |
| seed:17 | B_stress_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.191296 | 0.566305 |
| seed:17 | B_stress_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.180876 | 0.543361 |
| seed:17 | B_stress_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.221148 | 0.641043 |
| seed:17 | B_stress_interactions | original_split | development | 1536 | 374 | 0.117791 | 0.357640 |
| seed:17 | B_stress_interactions | original_split | train | 4608 | 1080 | 0.114204 | 0.355348 |
| seed:17 | B_stress_interactions | query_role | current | 3072 | 236 | 0.058811 | 0.200295 |
| seed:17 | B_stress_interactions | query_role | saved | 3072 | 1218 | 0.171390 | 0.511547 |
| seed:17 | B_stress_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.100645 | 0.314916 |
| seed:17 | B_stress_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.129982 | 0.399055 |
| seed:17 | B_stress_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.089589 | 0.288216 |
| seed:17 | B_stress_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.141038 | 0.425755 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029103 | 0.108974 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043601 | 0.162919 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.045217 | 0.152716 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049583 | 0.174723 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.117431 | 0.357025 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.093548 | 0.310323 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.179492 | 0.541048 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.167172 | 0.504967 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.051648 | 0.176543 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068982 | 0.220287 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.150323 | 0.462732 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.070547 | 0.242873 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.210435 | 0.603719 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.193430 | 0.572837 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.184345 | 0.552792 |
| seed:17 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.224739 | 0.651044 |
| seed:17 | B_stress_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.114717 | 0.350151 |
| seed:17 | B_stress_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.115512 | 0.359264 |
| seed:17 | B_stress_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.058667 | 0.200303 |
| seed:17 | B_stress_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.171960 | 0.513668 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.082340 | 0.269920 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.091645 | 0.291017 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.066580 | 0.222931 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.107405 | 0.338007 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028665 | 0.098865 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.036377 | 0.153133 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029526 | 0.107771 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.029949 | 0.105452 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.081000 | 0.258222 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.086448 | 0.278989 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.118490 | 0.380170 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.117907 | 0.378494 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.038533 | 0.134055 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.050318 | 0.166915 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.095696 | 0.299192 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.042898 | 0.152049 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.142241 | 0.454478 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.175675 | 0.547675 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.124012 | 0.396303 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.175599 | 0.524201 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.079050 | 0.256223 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.089640 | 0.288551 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040443 | 0.143354 |
| seed:17 | B_stress_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.133542 | 0.417583 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.076874 | 0.252565 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.088058 | 0.281867 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.064569 | 0.213946 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.100363 | 0.320486 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027073 | 0.094017 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033664 | 0.141365 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.026475 | 0.096774 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.028689 | 0.099839 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.078628 | 0.251736 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084408 | 0.261532 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.121916 | 0.382792 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.114828 | 0.370569 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.030027 | 0.110056 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.041234 | 0.132751 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.097405 | 0.298447 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.039577 | 0.141552 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.132701 | 0.430562 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.167724 | 0.536557 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.103440 | 0.344736 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.169739 | 0.516451 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.073841 | 0.241291 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.085341 | 0.275858 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036625 | 0.129450 |
| seed:17 | B_stress_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.128307 | 0.404982 |
| seed:29 | prior | available_bindings | 2 | 3072 | 519 | 0.145598 | 0.469568 |
| seed:29 | prior | available_bindings | 4 | 3072 | 935 | 0.216736 | 0.627697 |
| seed:29 | prior | condition | informative | 3072 | 431 | 0.130407 | 0.435721 |
| seed:29 | prior | condition | misleading | 3072 | 1023 | 0.231927 | 0.661545 |
| seed:29 | prior | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.063059 | 0.284993 |
| seed:29 | prior | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.084442 | 0.333565 |
| seed:29 | prior | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.087638 | 0.339585 |
| seed:29 | prior | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.089214 | 0.343983 |
| seed:29 | prior | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.156856 | 0.494284 |
| seed:29 | prior | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.134773 | 0.446052 |
| seed:29 | prior | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.241560 | 0.682893 |
| seed:29 | prior | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.207560 | 0.607577 |
| seed:29 | prior | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.083950 | 0.331640 |
| seed:29 | prior | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.110046 | 0.390447 |
| seed:29 | prior | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.164399 | 0.511865 |
| seed:29 | prior | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.110035 | 0.390431 |
| seed:29 | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.308549 | 0.832530 |
| seed:29 | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.238122 | 0.675622 |
| seed:29 | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.495695 | 1.249926 |
| seed:29 | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.435664 | 1.114101 |
| seed:29 | prior | original_split | development | 1536 | 374 | 0.184510 | 0.555930 |
| seed:29 | prior | original_split | train | 4608 | 1080 | 0.180053 | 0.546200 |
| seed:29 | prior | query_role | current | 3072 | 236 | 0.096677 | 0.360535 |
| seed:29 | prior | query_role | saved | 3072 | 1218 | 0.265657 | 0.736731 |
| seed:29 | A_input | available_bindings | 2 | 3072 | 519 | 0.121707 | 0.379148 |
| seed:29 | A_input | available_bindings | 4 | 3072 | 935 | 0.144426 | 0.439473 |
| seed:29 | A_input | condition | informative | 3072 | 431 | 0.113196 | 0.357161 |
| seed:29 | A_input | condition | misleading | 3072 | 1023 | 0.152936 | 0.461460 |
| seed:29 | A_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014890 | 0.069530 |
| seed:29 | A_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048361 | 0.182547 |
| seed:29 | A_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.047478 | 0.164629 |
| seed:29 | A_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053585 | 0.190865 |
| seed:29 | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.153778 | 0.485259 |
| seed:29 | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.130686 | 0.438250 |
| seed:29 | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.220549 | 0.632233 |
| seed:29 | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.225448 | 0.645580 |
| seed:29 | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.047406 | 0.179314 |
| seed:29 | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.080508 | 0.270051 |
| seed:29 | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.158784 | 0.511916 |
| seed:29 | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083700 | 0.292646 |
| seed:29 | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.245278 | 0.684278 |
| seed:29 | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.240010 | 0.674849 |
| seed:29 | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.157531 | 0.495815 |
| seed:29 | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.213644 | 0.619459 |
| seed:29 | A_input | original_split | development | 1536 | 374 | 0.125587 | 0.386780 |
| seed:29 | A_input | original_split | train | 4608 | 1080 | 0.135560 | 0.416820 |
| seed:29 | A_input | query_role | current | 3072 | 236 | 0.063865 | 0.225091 |
| seed:29 | A_input | query_role | saved | 3072 | 1218 | 0.202268 | 0.593530 |
| seed:29 | A_interactions | available_bindings | 2 | 3072 | 519 | 0.116826 | 0.359352 |
| seed:29 | A_interactions | available_bindings | 4 | 3072 | 935 | 0.132396 | 0.407732 |
| seed:29 | A_interactions | condition | informative | 3072 | 431 | 0.103930 | 0.326999 |
| seed:29 | A_interactions | condition | misleading | 3072 | 1023 | 0.145292 | 0.440085 |
| seed:29 | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.021109 | 0.088424 |
| seed:29 | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.044612 | 0.153189 |
| seed:29 | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044191 | 0.154728 |
| seed:29 | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051040 | 0.174250 |
| seed:29 | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.148069 | 0.463287 |
| seed:29 | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.125373 | 0.412724 |
| seed:29 | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.230177 | 0.653977 |
| seed:29 | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.189291 | 0.560191 |
| seed:29 | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054083 | 0.187189 |
| seed:29 | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.076059 | 0.245724 |
| seed:29 | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.155143 | 0.524955 |
| seed:29 | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.078364 | 0.268962 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.241862 | 0.676324 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.222349 | 0.636866 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.147539 | 0.472451 |
| seed:29 | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.201397 | 0.592488 |
| seed:29 | A_interactions | original_split | development | 1536 | 374 | 0.125608 | 0.386380 |
| seed:29 | A_interactions | original_split | train | 4608 | 1080 | 0.124279 | 0.382596 |
| seed:29 | A_interactions | query_role | current | 3072 | 236 | 0.061643 | 0.210109 |
| seed:29 | A_interactions | query_role | saved | 3072 | 1218 | 0.187580 | 0.556975 |
| seed:29 | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.117109 | 0.360125 |
| seed:29 | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.132197 | 0.406136 |
| seed:29 | A_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.103320 | 0.325174 |
| seed:29 | A_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.145985 | 0.441087 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.020824 | 0.087604 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.045241 | 0.158543 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043430 | 0.151089 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050560 | 0.171504 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.145791 | 0.455484 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.127263 | 0.417727 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.230861 | 0.655611 |
| seed:29 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.185871 | 0.549741 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054278 | 0.187486 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.076378 | 0.246230 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.154308 | 0.515381 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.078181 | 0.266757 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.236704 | 0.661511 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.224971 | 0.642207 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.150965 | 0.484473 |
| seed:29 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.204021 | 0.600142 |
| seed:29 | A_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.124563 | 0.382560 |
| seed:29 | A_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.124683 | 0.383321 |
| seed:29 | A_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.061588 | 0.209460 |
| seed:29 | A_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.187717 | 0.556801 |
| seed:29 | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.086908 | 0.271256 |
| seed:29 | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.107475 | 0.340046 |
| seed:29 | A_interactions_neutral_scored | condition | informative | 3072 | 431 | 0.082675 | 0.257037 |
| seed:29 | A_interactions_neutral_scored | condition | misleading | 3072 | 1023 | 0.111707 | 0.354265 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024155 | 0.087975 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032040 | 0.115170 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029706 | 0.111133 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.041823 | 0.143110 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.107907 | 0.329733 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.103880 | 0.310461 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.180979 | 0.524967 |
| seed:29 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.151321 | 0.455858 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.036524 | 0.131998 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.045234 | 0.147401 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.127121 | 0.415057 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.057804 | 0.213465 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.147532 | 0.459184 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.182233 | 0.550060 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.116615 | 0.354099 |
| seed:29 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.174049 | 0.538736 |
| seed:29 | A_interactions_neutral_scored | original_split | development | 1536 | 374 | 0.090555 | 0.285253 |
| seed:29 | A_interactions_neutral_scored | original_split | train | 4608 | 1080 | 0.099404 | 0.312450 |
| seed:29 | A_interactions_neutral_scored | query_role | current | 3072 | 236 | 0.045226 | 0.158304 |
| seed:29 | A_interactions_neutral_scored | query_role | saved | 3072 | 1218 | 0.149157 | 0.452998 |
| seed:29 | A_interactions_oracle | available_bindings | 2 | 3072 | 519 | 0.091892 | 0.290880 |
| seed:29 | A_interactions_oracle | available_bindings | 4 | 3072 | 935 | 0.102354 | 0.324271 |
| seed:29 | A_interactions_oracle | condition | informative | 3072 | 431 | 0.079600 | 0.255300 |
| seed:29 | A_interactions_oracle | condition | misleading | 3072 | 1023 | 0.114645 | 0.359851 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029607 | 0.112347 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040961 | 0.145972 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.038848 | 0.141183 |
| seed:29 | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.045847 | 0.155882 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.103504 | 0.317653 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.096179 | 0.302877 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.164428 | 0.488479 |
| seed:29 | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.132620 | 0.412545 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.055705 | 0.184731 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.059172 | 0.192351 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.116088 | 0.376083 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.063069 | 0.218630 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.158087 | 0.485904 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.181586 | 0.553760 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.124042 | 0.379659 |
| seed:29 | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.161080 | 0.492363 |
| seed:29 | A_interactions_oracle | original_split | development | 1536 | 374 | 0.094768 | 0.298890 |
| seed:29 | A_interactions_oracle | original_split | train | 4608 | 1080 | 0.097908 | 0.310471 |
| seed:29 | A_interactions_oracle | query_role | current | 3072 | 236 | 0.052945 | 0.180720 |
| seed:29 | A_interactions_oracle | query_role | saved | 3072 | 1218 | 0.141301 | 0.434431 |
| seed:29 | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.085570 | 0.274456 |
| seed:29 | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.098787 | 0.314400 |
| seed:29 | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.074611 | 0.242672 |
| seed:29 | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.109746 | 0.346185 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028586 | 0.106208 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.037338 | 0.136640 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.032803 | 0.128437 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.041533 | 0.142279 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.095213 | 0.293475 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.089645 | 0.291156 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.136797 | 0.426306 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.131571 | 0.409486 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.042795 | 0.149719 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.053194 | 0.171659 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.111413 | 0.351242 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.056479 | 0.201280 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.144727 | 0.450412 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.177581 | 0.547376 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.125644 | 0.375780 |
| seed:29 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.163262 | 0.499721 |
| seed:29 | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.085775 | 0.273449 |
| seed:29 | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.094313 | 0.301421 |
| seed:29 | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.047465 | 0.164272 |
| seed:29 | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.136891 | 0.424584 |
| seed:29 | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.080874 | 0.258320 |
| seed:29 | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.094657 | 0.304094 |
| seed:29 | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.071766 | 0.230118 |
| seed:29 | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.103765 | 0.332296 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027615 | 0.099633 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033249 | 0.119588 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029943 | 0.119111 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.039153 | 0.133300 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.090351 | 0.281432 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.089971 | 0.277769 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.139006 | 0.423443 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.125772 | 0.392445 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.035856 | 0.129936 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.043955 | 0.139731 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.113145 | 0.355929 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.051418 | 0.189113 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.133545 | 0.422985 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.174387 | 0.545841 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.107057 | 0.329374 |
| seed:29 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.160178 | 0.499223 |
| seed:29 | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.080324 | 0.257986 |
| seed:29 | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.090246 | 0.288948 |
| seed:29 | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.042988 | 0.149313 |
| seed:29 | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.132543 | 0.413101 |
| seed:29 | B_input_confidence | available_bindings | 2 | 3072 | 519 | 0.110590 | 0.345946 |
| seed:29 | B_input_confidence | available_bindings | 4 | 3072 | 935 | 0.141189 | 0.428595 |
| seed:29 | B_input_confidence | condition | informative | 3072 | 431 | 0.103015 | 0.326401 |
| seed:29 | B_input_confidence | condition | misleading | 3072 | 1023 | 0.148764 | 0.448140 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.015197 | 0.076746 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.047614 | 0.175241 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046165 | 0.163392 |
| seed:29 | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053537 | 0.191532 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.139945 | 0.434935 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.107285 | 0.353099 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.204068 | 0.593487 |
| seed:29 | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.204915 | 0.596472 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.050227 | 0.181976 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.076437 | 0.252005 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157122 | 0.494129 |
| seed:29 | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083749 | 0.281610 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.229706 | 0.655627 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.214669 | 0.620690 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.180939 | 0.543853 |
| seed:29 | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.217846 | 0.628669 |
| seed:29 | B_input_confidence | original_split | development | 1536 | 374 | 0.121537 | 0.374453 |
| seed:29 | B_input_confidence | original_split | train | 4608 | 1080 | 0.127340 | 0.391543 |
| seed:29 | B_input_confidence | query_role | current | 3072 | 236 | 0.063199 | 0.218736 |
| seed:29 | B_input_confidence | query_role | saved | 3072 | 1218 | 0.188580 | 0.555805 |
| seed:29 | B_interactions_confidence | available_bindings | 2 | 3072 | 519 | 0.105375 | 0.326510 |
| seed:29 | B_interactions_confidence | available_bindings | 4 | 3072 | 935 | 0.129494 | 0.401917 |
| seed:29 | B_interactions_confidence | condition | informative | 3072 | 431 | 0.094575 | 0.299789 |
| seed:29 | B_interactions_confidence | condition | misleading | 3072 | 1023 | 0.140295 | 0.428638 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026438 | 0.105218 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043311 | 0.150447 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.047984 | 0.160260 |
| seed:29 | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.052891 | 0.185655 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.132295 | 0.403303 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.100834 | 0.330578 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.218706 | 0.632436 |
| seed:29 | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.168921 | 0.506566 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.058215 | 0.194936 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.070642 | 0.230011 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.155818 | 0.521733 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.077634 | 0.267213 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.222256 | 0.630864 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.197862 | 0.580864 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.168994 | 0.516287 |
| seed:29 | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.203826 | 0.603626 |
| seed:29 | B_interactions_confidence | original_split | development | 1536 | 374 | 0.122493 | 0.374947 |
| seed:29 | B_interactions_confidence | original_split | train | 4608 | 1080 | 0.115749 | 0.360636 |
| seed:29 | B_interactions_confidence | query_role | current | 3072 | 236 | 0.061731 | 0.211186 |
| seed:29 | B_interactions_confidence | query_role | saved | 3072 | 1218 | 0.173139 | 0.517241 |
| seed:29 | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.101928 | 0.317190 |
| seed:29 | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.130173 | 0.404222 |
| seed:29 | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.091579 | 0.292664 |
| seed:29 | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.140522 | 0.428749 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026347 | 0.103596 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042551 | 0.146587 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043893 | 0.154311 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051425 | 0.181084 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.125507 | 0.382924 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.096206 | 0.321001 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.201355 | 0.592546 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.167357 | 0.505652 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054390 | 0.183354 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.070160 | 0.224726 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156649 | 0.505665 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.076642 | 0.263639 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.206805 | 0.595725 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.196126 | 0.578028 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.179830 | 0.541698 |
| seed:29 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.213062 | 0.631045 |
| seed:29 | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.117319 | 0.360452 |
| seed:29 | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.115628 | 0.360791 |
| seed:29 | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.060550 | 0.205948 |
| seed:29 | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.171551 | 0.515464 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.083565 | 0.271621 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.094180 | 0.300195 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.069400 | 0.228833 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.108345 | 0.342982 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026554 | 0.095598 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.035675 | 0.137305 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.035611 | 0.126918 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.034198 | 0.116152 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.090500 | 0.290625 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.086635 | 0.280822 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.135795 | 0.421999 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.119970 | 0.383474 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.043609 | 0.149630 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.050649 | 0.169794 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.101610 | 0.321849 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.049348 | 0.173152 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.144198 | 0.454361 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.176002 | 0.546697 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.126345 | 0.383870 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.168674 | 0.517230 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.084090 | 0.269589 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.090466 | 0.291347 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.043357 | 0.150589 |
| seed:29 | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.134388 | 0.421226 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 519 | 0.078873 | 0.256338 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 935 | 0.089929 | 0.291406 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 431 | 0.067005 | 0.217560 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 1023 | 0.101797 | 0.330185 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024890 | 0.088548 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032142 | 0.119154 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.031454 | 0.115741 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031694 | 0.108940 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.083965 | 0.270111 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.088561 | 0.273429 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.140646 | 0.424803 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.115407 | 0.369707 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.035038 | 0.125873 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.042061 | 0.138243 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.109216 | 0.342698 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.044418 | 0.161064 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.133076 | 0.431479 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.171990 | 0.549195 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.104703 | 0.333967 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.162938 | 0.515598 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 374 | 0.078330 | 0.254102 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 1080 | 0.086425 | 0.280462 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 236 | 0.039079 | 0.136120 |
| seed:29 | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 1218 | 0.129723 | 0.411624 |
| seed:29 | B_event_input | available_bindings | 2 | 3072 | 519 | 0.110632 | 0.337828 |
| seed:29 | B_event_input | available_bindings | 4 | 3072 | 935 | 0.133782 | 0.404629 |
| seed:29 | B_event_input | condition | informative | 3072 | 431 | 0.093546 | 0.295560 |
| seed:29 | B_event_input | condition | misleading | 3072 | 1023 | 0.150868 | 0.446896 |
| seed:29 | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.017153 | 0.075621 |
| seed:29 | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.045148 | 0.154320 |
| seed:29 | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.045133 | 0.158337 |
| seed:29 | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.054878 | 0.188482 |
| seed:29 | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.129655 | 0.401827 |
| seed:29 | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.107855 | 0.344377 |
| seed:29 | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.201837 | 0.587906 |
| seed:29 | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.163623 | 0.491020 |
| seed:29 | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.050374 | 0.172221 |
| seed:29 | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.076514 | 0.248365 |
| seed:29 | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156748 | 0.487817 |
| seed:29 | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.076967 | 0.252101 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.234657 | 0.661279 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.218356 | 0.624430 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.200881 | 0.591243 |
| seed:29 | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.225764 | 0.645554 |
| seed:29 | B_event_input | original_split | development | 1536 | 374 | 0.122356 | 0.370600 |
| seed:29 | B_event_input | original_split | train | 4608 | 1080 | 0.122157 | 0.371438 |
| seed:29 | B_event_input | query_role | current | 3072 | 236 | 0.061784 | 0.206479 |
| seed:29 | B_event_input | query_role | saved | 3072 | 1218 | 0.182630 | 0.535978 |
| seed:29 | B_event_interactions | available_bindings | 2 | 3072 | 519 | 0.106433 | 0.324247 |
| seed:29 | B_event_interactions | available_bindings | 4 | 3072 | 935 | 0.127846 | 0.393511 |
| seed:29 | B_event_interactions | condition | informative | 3072 | 431 | 0.089498 | 0.283046 |
| seed:29 | B_event_interactions | condition | misleading | 3072 | 1023 | 0.144781 | 0.434712 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024008 | 0.092691 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043492 | 0.145975 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044357 | 0.150723 |
| seed:29 | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053868 | 0.187365 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.127940 | 0.387095 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.102251 | 0.328460 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.211396 | 0.614290 |
| seed:29 | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.147200 | 0.446790 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.057013 | 0.189538 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.072119 | 0.228642 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.150564 | 0.474894 |
| seed:29 | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075132 | 0.254854 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.229304 | 0.644094 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.201605 | 0.585696 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.188658 | 0.562776 |
| seed:29 | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.218465 | 0.639305 |
| seed:29 | B_event_interactions | original_split | development | 1536 | 374 | 0.122625 | 0.369127 |
| seed:29 | B_event_interactions | original_split | train | 4608 | 1080 | 0.115311 | 0.355463 |
| seed:29 | B_event_interactions | query_role | current | 3072 | 236 | 0.061017 | 0.204152 |
| seed:29 | B_event_interactions | query_role | saved | 3072 | 1218 | 0.173262 | 0.513606 |
| seed:29 | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.102982 | 0.315245 |
| seed:29 | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.129085 | 0.397648 |
| seed:29 | B_event_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.087438 | 0.278380 |
| seed:29 | B_event_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.144629 | 0.434513 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023775 | 0.090377 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043152 | 0.147035 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043710 | 0.150867 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.052457 | 0.184646 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.116769 | 0.357146 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.100728 | 0.322892 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.198363 | 0.586454 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.147511 | 0.449164 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053895 | 0.180092 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.071414 | 0.225218 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.152074 | 0.464074 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075243 | 0.253982 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.212427 | 0.603774 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.199167 | 0.580630 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.199667 | 0.594150 |
| seed:29 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.225635 | 0.661811 |
| seed:29 | B_event_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.117295 | 0.354860 |
| seed:29 | B_event_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.115613 | 0.356975 |
| seed:29 | B_event_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.060329 | 0.201585 |
| seed:29 | B_event_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.171739 | 0.511309 |
| seed:29 | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.080272 | 0.263227 |
| seed:29 | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.093836 | 0.298067 |
| seed:29 | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.067476 | 0.223579 |
| seed:29 | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.106632 | 0.337714 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023992 | 0.087717 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033482 | 0.135585 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.036159 | 0.124785 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031310 | 0.109888 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.088655 | 0.279619 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.085576 | 0.273541 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.128094 | 0.405506 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.119417 | 0.382998 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.042509 | 0.146356 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.048704 | 0.162251 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.095681 | 0.288592 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.044708 | 0.157278 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.145913 | 0.470849 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.163334 | 0.515712 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.128196 | 0.383872 |
| seed:29 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.177351 | 0.540006 |
| seed:29 | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.082522 | 0.264320 |
| seed:29 | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.088564 | 0.286089 |
| seed:29 | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040570 | 0.142029 |
| seed:29 | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.133538 | 0.419265 |
| seed:29 | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.075864 | 0.248859 |
| seed:29 | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.088768 | 0.286782 |
| seed:29 | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.064113 | 0.211932 |
| seed:29 | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.100519 | 0.323709 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.021127 | 0.080295 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.030629 | 0.122704 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029253 | 0.107668 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.029341 | 0.104261 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.081136 | 0.257216 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.085757 | 0.266572 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.130381 | 0.403002 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.112462 | 0.364454 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.034583 | 0.125196 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.040110 | 0.132517 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.101736 | 0.307228 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.042048 | 0.149151 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.137787 | 0.448068 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.161373 | 0.515971 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.104833 | 0.330463 |
| seed:29 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.168995 | 0.529017 |
| seed:29 | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.076289 | 0.247493 |
| seed:29 | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.084325 | 0.274596 |
| seed:29 | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036763 | 0.129743 |
| seed:29 | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.127869 | 0.405898 |
| seed:29 | B_joint_input | available_bindings | 2 | 3072 | 519 | 0.106809 | 0.327247 |
| seed:29 | B_joint_input | available_bindings | 4 | 3072 | 935 | 0.129591 | 0.393322 |
| seed:29 | B_joint_input | condition | informative | 3072 | 431 | 0.090001 | 0.285018 |
| seed:29 | B_joint_input | condition | misleading | 3072 | 1023 | 0.146399 | 0.435551 |
| seed:29 | B_joint_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.018673 | 0.085772 |
| seed:29 | B_joint_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043065 | 0.146839 |
| seed:29 | B_joint_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046088 | 0.160442 |
| seed:29 | B_joint_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049994 | 0.170598 |
| seed:29 | B_joint_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.125687 | 0.386328 |
| seed:29 | B_joint_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.099957 | 0.320525 |
| seed:29 | B_joint_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.208280 | 0.608923 |
| seed:29 | B_joint_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.158976 | 0.480883 |
| seed:29 | B_joint_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.051927 | 0.171394 |
| seed:29 | B_joint_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.073780 | 0.237996 |
| seed:29 | B_joint_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.160203 | 0.498328 |
| seed:29 | B_joint_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069154 | 0.226863 |
| seed:29 | B_joint_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.234682 | 0.667854 |
| seed:29 | B_joint_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.208568 | 0.602446 |
| seed:29 | B_joint_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.188615 | 0.562208 |
| seed:29 | B_joint_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.223275 | 0.643622 |
| seed:29 | B_joint_input | original_split | development | 1536 | 374 | 0.122094 | 0.371050 |
| seed:29 | B_joint_input | original_split | train | 4608 | 1080 | 0.116902 | 0.356696 |
| seed:29 | B_joint_input | query_role | current | 3072 | 236 | 0.058776 | 0.195823 |
| seed:29 | B_joint_input | query_role | saved | 3072 | 1218 | 0.177624 | 0.524746 |
| seed:29 | B_joint_interactions | available_bindings | 2 | 3072 | 519 | 0.102878 | 0.315074 |
| seed:29 | B_joint_interactions | available_bindings | 4 | 3072 | 935 | 0.125153 | 0.385953 |
| seed:29 | B_joint_interactions | condition | informative | 3072 | 431 | 0.087129 | 0.276580 |
| seed:29 | B_joint_interactions | condition | misleading | 3072 | 1023 | 0.140901 | 0.424447 |
| seed:29 | B_joint_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025075 | 0.098460 |
| seed:29 | B_joint_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041454 | 0.140149 |
| seed:29 | B_joint_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046538 | 0.156635 |
| seed:29 | B_joint_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049939 | 0.172582 |
| seed:29 | B_joint_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.125426 | 0.375587 |
| seed:29 | B_joint_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094997 | 0.308967 |
| seed:29 | B_joint_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.217522 | 0.639115 |
| seed:29 | B_joint_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.146108 | 0.446940 |
| seed:29 | B_joint_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.058838 | 0.191586 |
| seed:29 | B_joint_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068230 | 0.217235 |
| seed:29 | B_joint_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156646 | 0.491259 |
| seed:29 | B_joint_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.070119 | 0.237611 |
| seed:29 | B_joint_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.228709 | 0.645475 |
| seed:29 | B_joint_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.193563 | 0.568538 |
| seed:29 | B_joint_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.177148 | 0.532950 |
| seed:29 | B_joint_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.214994 | 0.631448 |
| seed:29 | B_joint_interactions | original_split | development | 1536 | 374 | 0.122829 | 0.370181 |
| seed:29 | B_joint_interactions | original_split | train | 4608 | 1080 | 0.111077 | 0.343957 |
| seed:29 | B_joint_interactions | query_role | current | 3072 | 236 | 0.058752 | 0.196187 |
| seed:29 | B_joint_interactions | query_role | saved | 3072 | 1218 | 0.169279 | 0.504840 |
| seed:29 | B_joint_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.099936 | 0.307471 |
| seed:29 | B_joint_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.126635 | 0.390363 |
| seed:29 | B_joint_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.085496 | 0.273139 |
| seed:29 | B_joint_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.141075 | 0.424695 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024846 | 0.096749 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041270 | 0.141385 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.045889 | 0.156128 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049069 | 0.171280 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.114929 | 0.346333 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094427 | 0.308228 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.204187 | 0.610577 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.146828 | 0.449525 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.055166 | 0.181854 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.067688 | 0.213637 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.158483 | 0.482481 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.070103 | 0.236883 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.209616 | 0.598827 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.193951 | 0.569696 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.187483 | 0.560984 |
| seed:29 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.222638 | 0.654022 |
| seed:29 | B_joint_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.117096 | 0.354808 |
| seed:29 | B_joint_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.112015 | 0.346954 |
| seed:29 | B_joint_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.058170 | 0.194030 |
| seed:29 | B_joint_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.168400 | 0.503805 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.079805 | 0.261350 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.094839 | 0.301064 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.066495 | 0.221115 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.108150 | 0.341298 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023575 | 0.088661 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.034381 | 0.139542 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.034915 | 0.122277 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031057 | 0.107579 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.084471 | 0.270418 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084926 | 0.271233 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.136318 | 0.427293 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.115206 | 0.371608 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.040800 | 0.141006 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.047581 | 0.158057 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.091932 | 0.277519 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.043645 | 0.151211 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.144091 | 0.462548 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.165473 | 0.517949 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.143880 | 0.429435 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.183911 | 0.563402 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.082743 | 0.265149 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.088848 | 0.286559 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.039873 | 0.139312 |
| seed:29 | B_joint_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.134771 | 0.423102 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.075005 | 0.246888 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.089591 | 0.289696 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.062973 | 0.209227 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.101623 | 0.327358 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.021411 | 0.081731 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.031010 | 0.124319 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.027906 | 0.105388 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.028528 | 0.101591 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.077998 | 0.251643 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084456 | 0.261816 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.140165 | 0.428442 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.107991 | 0.353675 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.033569 | 0.121516 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.038662 | 0.128739 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.100473 | 0.301722 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.040752 | 0.141887 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.134607 | 0.443867 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.162111 | 0.517076 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.118043 | 0.366315 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.175447 | 0.553016 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.076813 | 0.249949 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.084126 | 0.274407 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.035976 | 0.126801 |
| seed:29 | B_joint_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.128620 | 0.409784 |
| seed:29 | B_stress_input | available_bindings | 2 | 3072 | 519 | 0.106034 | 0.331200 |
| seed:29 | B_stress_input | available_bindings | 4 | 3072 | 935 | 0.139362 | 0.421712 |
| seed:29 | B_stress_input | condition | informative | 3072 | 431 | 0.096832 | 0.309656 |
| seed:29 | B_stress_input | condition | misleading | 3072 | 1023 | 0.148563 | 0.443256 |
| seed:29 | B_stress_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.015655 | 0.077267 |
| seed:29 | B_stress_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.046919 | 0.175635 |
| seed:29 | B_stress_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043787 | 0.152938 |
| seed:29 | B_stress_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051020 | 0.180388 |
| seed:29 | B_stress_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.123944 | 0.385332 |
| seed:29 | B_stress_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.101560 | 0.330925 |
| seed:29 | B_stress_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.173824 | 0.529836 |
| seed:29 | B_stress_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.195630 | 0.579117 |
| seed:29 | B_stress_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.044378 | 0.159427 |
| seed:29 | B_stress_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.072797 | 0.236531 |
| seed:29 | B_stress_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.144967 | 0.437151 |
| seed:29 | B_stress_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075973 | 0.257619 |
| seed:29 | B_stress_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.226451 | 0.646670 |
| seed:29 | B_stress_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.209714 | 0.609759 |
| seed:29 | B_stress_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.201472 | 0.588366 |
| seed:29 | B_stress_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.233504 | 0.665434 |
| seed:29 | B_stress_input | original_split | development | 1536 | 374 | 0.115409 | 0.353807 |
| seed:29 | B_stress_input | original_split | train | 4608 | 1080 | 0.125127 | 0.384005 |
| seed:29 | B_stress_input | query_role | current | 3072 | 236 | 0.059277 | 0.204257 |
| seed:29 | B_stress_input | query_role | saved | 3072 | 1218 | 0.186119 | 0.548654 |
| seed:29 | B_stress_interactions | available_bindings | 2 | 3072 | 519 | 0.102756 | 0.317260 |
| seed:29 | B_stress_interactions | available_bindings | 4 | 3072 | 935 | 0.129871 | 0.400136 |
| seed:29 | B_stress_interactions | condition | informative | 3072 | 431 | 0.090424 | 0.289072 |
| seed:29 | B_stress_interactions | condition | misleading | 3072 | 1023 | 0.142202 | 0.428324 |
| seed:29 | B_stress_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027145 | 0.105695 |
| seed:29 | B_stress_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042413 | 0.147637 |
| seed:29 | B_stress_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.049195 | 0.162004 |
| seed:29 | B_stress_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049535 | 0.173942 |
| seed:29 | B_stress_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.121438 | 0.369658 |
| seed:29 | B_stress_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.097034 | 0.316661 |
| seed:29 | B_stress_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.186024 | 0.558724 |
| seed:29 | B_stress_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.166468 | 0.507877 |
| seed:29 | B_stress_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.051805 | 0.174067 |
| seed:29 | B_stress_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.069618 | 0.221677 |
| seed:29 | B_stress_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.147836 | 0.467733 |
| seed:29 | B_stress_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.072023 | 0.245642 |
| seed:29 | B_stress_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.222508 | 0.632120 |
| seed:29 | B_stress_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.196024 | 0.576814 |
| seed:29 | B_stress_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.186780 | 0.557684 |
| seed:29 | B_stress_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.221386 | 0.643964 |
| seed:29 | B_stress_interactions | original_split | development | 1536 | 374 | 0.117969 | 0.359102 |
| seed:29 | B_stress_interactions | original_split | train | 4608 | 1080 | 0.115761 | 0.358563 |
| seed:29 | B_stress_interactions | query_role | current | 3072 | 236 | 0.058785 | 0.198518 |
| seed:29 | B_stress_interactions | query_role | saved | 3072 | 1218 | 0.173842 | 0.518878 |
| seed:29 | B_stress_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.101757 | 0.314876 |
| seed:29 | B_stress_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.130334 | 0.402081 |
| seed:29 | B_stress_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.090103 | 0.288618 |
| seed:29 | B_stress_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.141988 | 0.428339 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025647 | 0.103308 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042705 | 0.148602 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.045820 | 0.158318 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049573 | 0.174619 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.118326 | 0.359299 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.099238 | 0.322753 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.181314 | 0.548480 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.166353 | 0.507264 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.049974 | 0.170605 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.069774 | 0.221071 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.150270 | 0.469805 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.072469 | 0.247538 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.210421 | 0.602852 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.196642 | 0.578801 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.189285 | 0.564816 |
| seed:29 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.223872 | 0.652285 |
| seed:29 | B_stress_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.114619 | 0.351129 |
| seed:29 | B_stress_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.116521 | 0.360929 |
| seed:29 | B_stress_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.058644 | 0.198559 |
| seed:29 | B_stress_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.173447 | 0.518398 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.083343 | 0.269355 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.093608 | 0.296619 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.067549 | 0.224129 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.109401 | 0.341845 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026673 | 0.095853 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.035770 | 0.137802 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.035054 | 0.121537 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.030546 | 0.107317 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.080923 | 0.262658 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.089262 | 0.282847 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.123010 | 0.394278 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.119014 | 0.385414 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.037982 | 0.132348 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.050495 | 0.166021 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.094357 | 0.293401 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.045706 | 0.160024 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.146200 | 0.459463 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.178643 | 0.554298 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.135740 | 0.415395 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.176419 | 0.526092 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.080976 | 0.260438 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.090975 | 0.290503 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.041043 | 0.142639 |
| seed:29 | B_stress_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.135907 | 0.423334 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.077799 | 0.252025 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.089580 | 0.286699 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.065124 | 0.212690 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.102255 | 0.326033 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025000 | 0.089250 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032381 | 0.120490 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.031218 | 0.110683 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.028508 | 0.098929 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.077526 | 0.252344 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.086576 | 0.265479 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.125623 | 0.392032 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.116542 | 0.376027 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.029382 | 0.109061 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.041280 | 0.134485 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.095180 | 0.290696 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.040972 | 0.146389 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.134863 | 0.435676 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.173169 | 0.548530 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.113350 | 0.361887 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.170889 | 0.523748 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.074910 | 0.243997 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.086616 | 0.277817 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036550 | 0.126854 |
| seed:29 | B_stress_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.130829 | 0.411870 |
| seed:43 | prior | available_bindings | 2 | 3072 | 519 | 0.145128 | 0.468275 |
| seed:43 | prior | available_bindings | 4 | 3072 | 935 | 0.216530 | 0.627104 |
| seed:43 | prior | condition | informative | 3072 | 431 | 0.130036 | 0.434712 |
| seed:43 | prior | condition | misleading | 3072 | 1023 | 0.231623 | 0.660666 |
| seed:43 | prior | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.063857 | 0.287260 |
| seed:43 | prior | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.084015 | 0.332429 |
| seed:43 | prior | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.087751 | 0.339978 |
| seed:43 | prior | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.089522 | 0.344870 |
| seed:43 | prior | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.156856 | 0.494302 |
| seed:43 | prior | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.133257 | 0.441854 |
| seed:43 | prior | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.241917 | 0.683841 |
| seed:43 | prior | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.206613 | 0.604934 |
| seed:43 | prior | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.084768 | 0.333942 |
| seed:43 | prior | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.109819 | 0.389855 |
| seed:43 | prior | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.162902 | 0.507683 |
| seed:43 | prior | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.109930 | 0.390167 |
| seed:43 | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.307584 | 0.829786 |
| seed:43 | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.237145 | 0.672866 |
| seed:43 | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.496113 | 1.250834 |
| seed:43 | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.435544 | 1.113659 |
| seed:43 | prior | original_split | development | 1536 | 374 | 0.184568 | 0.556076 |
| seed:43 | prior | original_split | train | 4608 | 1080 | 0.179583 | 0.544893 |
| seed:43 | prior | query_role | current | 3072 | 236 | 0.096687 | 0.360599 |
| seed:43 | prior | query_role | saved | 3072 | 1218 | 0.264971 | 0.734779 |
| seed:43 | A_input | available_bindings | 2 | 3072 | 519 | 0.120263 | 0.376577 |
| seed:43 | A_input | available_bindings | 4 | 3072 | 935 | 0.144543 | 0.442556 |
| seed:43 | A_input | condition | informative | 3072 | 431 | 0.112216 | 0.355912 |
| seed:43 | A_input | condition | misleading | 3072 | 1023 | 0.152590 | 0.463221 |
| seed:43 | A_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014936 | 0.072946 |
| seed:43 | A_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048592 | 0.184840 |
| seed:43 | A_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.050859 | 0.180694 |
| seed:43 | A_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053358 | 0.191034 |
| seed:43 | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.153559 | 0.484253 |
| seed:43 | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.127923 | 0.430518 |
| seed:43 | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.224540 | 0.640952 |
| seed:43 | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.221588 | 0.637847 |
| seed:43 | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.048571 | 0.189117 |
| seed:43 | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.080592 | 0.267993 |
| seed:43 | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.166074 | 0.568605 |
| seed:43 | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083238 | 0.293460 |
| seed:43 | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.243904 | 0.681607 |
| seed:43 | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.233986 | 0.662151 |
| seed:43 | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.177004 | 0.541701 |
| seed:43 | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.211926 | 0.615536 |
| seed:43 | A_input | original_split | development | 1536 | 374 | 0.128368 | 0.398983 |
| seed:43 | A_input | original_split | train | 4608 | 1080 | 0.133748 | 0.413094 |
| seed:43 | A_input | query_role | current | 3072 | 236 | 0.064319 | 0.229468 |
| seed:43 | A_input | query_role | saved | 3072 | 1218 | 0.200487 | 0.589665 |
| seed:43 | A_interactions | available_bindings | 2 | 3072 | 519 | 0.115436 | 0.355664 |
| seed:43 | A_interactions | available_bindings | 4 | 3072 | 935 | 0.131547 | 0.404983 |
| seed:43 | A_interactions | condition | informative | 3072 | 431 | 0.103000 | 0.323723 |
| seed:43 | A_interactions | condition | misleading | 3072 | 1023 | 0.143983 | 0.436924 |
| seed:43 | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.022839 | 0.092544 |
| seed:43 | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043601 | 0.150345 |
| seed:43 | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043650 | 0.147959 |
| seed:43 | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051282 | 0.174165 |
| seed:43 | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.151067 | 0.474398 |
| seed:43 | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.122323 | 0.402281 |
| seed:43 | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.227352 | 0.647540 |
| seed:43 | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.186615 | 0.551729 |
| seed:43 | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.056353 | 0.193622 |
| seed:43 | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.074014 | 0.239334 |
| seed:43 | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.159663 | 0.540371 |
| seed:43 | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.078302 | 0.269057 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.242342 | 0.677634 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.216381 | 0.622927 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.144996 | 0.467488 |
| seed:43 | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.200093 | 0.588297 |
| seed:43 | A_interactions | original_split | development | 1536 | 374 | 0.126739 | 0.389980 |
| seed:43 | A_interactions | original_split | train | 4608 | 1080 | 0.122409 | 0.377105 |
| seed:43 | A_interactions | query_role | current | 3072 | 236 | 0.061670 | 0.209812 |
| seed:43 | A_interactions | query_role | saved | 3072 | 1218 | 0.185313 | 0.550835 |
| seed:43 | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.115772 | 0.356748 |
| seed:43 | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.132158 | 0.405862 |
| seed:43 | A_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.103225 | 0.324587 |
| seed:43 | A_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.144705 | 0.438023 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.022987 | 0.093193 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.044110 | 0.153495 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042569 | 0.146316 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050760 | 0.171866 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.148957 | 0.469140 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.124121 | 0.407747 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.224924 | 0.642166 |
| seed:43 | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.187857 | 0.554527 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.057440 | 0.196471 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.074531 | 0.240470 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156494 | 0.526037 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.078310 | 0.267136 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.236684 | 0.662005 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.218833 | 0.628373 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.146318 | 0.473158 |
| seed:43 | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.203369 | 0.597071 |
| seed:43 | A_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.125203 | 0.385775 |
| seed:43 | A_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.123552 | 0.379815 |
| seed:43 | A_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.061660 | 0.209273 |
| seed:43 | A_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.186270 | 0.553337 |
| seed:43 | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.085921 | 0.268628 |
| seed:43 | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.107216 | 0.340396 |
| seed:43 | A_interactions_neutral_scored | condition | informative | 3072 | 431 | 0.083181 | 0.257742 |
| seed:43 | A_interactions_neutral_scored | condition | misleading | 3072 | 1023 | 0.109956 | 0.351282 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025546 | 0.091573 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.031505 | 0.113030 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028175 | 0.104193 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.042410 | 0.145121 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.111194 | 0.339050 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.100349 | 0.300010 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.177820 | 0.517747 |
| seed:43 | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.155478 | 0.464972 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.038422 | 0.137087 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.043822 | 0.142283 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.129831 | 0.446890 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.057644 | 0.216100 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.150126 | 0.465904 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.177205 | 0.539637 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.106607 | 0.330846 |
| seed:43 | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.170617 | 0.527772 |
| seed:43 | A_interactions_neutral_scored | original_split | development | 1536 | 374 | 0.091084 | 0.288909 |
| seed:43 | A_interactions_neutral_scored | original_split | train | 4608 | 1080 | 0.098396 | 0.309713 |
| seed:43 | A_interactions_neutral_scored | query_role | current | 3072 | 236 | 0.045313 | 0.159823 |
| seed:43 | A_interactions_neutral_scored | query_role | saved | 3072 | 1218 | 0.147823 | 0.449201 |
| seed:43 | A_interactions_oracle | available_bindings | 2 | 3072 | 519 | 0.091625 | 0.289700 |
| seed:43 | A_interactions_oracle | available_bindings | 4 | 3072 | 935 | 0.101110 | 0.321056 |
| seed:43 | A_interactions_oracle | condition | informative | 3072 | 431 | 0.079778 | 0.252768 |
| seed:43 | A_interactions_oracle | condition | misleading | 3072 | 1023 | 0.112957 | 0.357987 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.035676 | 0.120780 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040368 | 0.145084 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.035194 | 0.122020 |
| seed:43 | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.046381 | 0.154262 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.111435 | 0.332650 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.092276 | 0.292032 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.155740 | 0.463486 |
| seed:43 | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.133406 | 0.410859 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.062485 | 0.200268 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.058216 | 0.189072 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.122904 | 0.416221 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.063357 | 0.219772 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.156633 | 0.483462 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.175773 | 0.543431 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.099499 | 0.326490 |
| seed:43 | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.159517 | 0.490530 |
| seed:43 | A_interactions_oracle | original_split | development | 1536 | 374 | 0.095483 | 0.300211 |
| seed:43 | A_interactions_oracle | original_split | train | 4608 | 1080 | 0.096662 | 0.307100 |
| seed:43 | A_interactions_oracle | query_role | current | 3072 | 236 | 0.054060 | 0.182797 |
| seed:43 | A_interactions_oracle | query_role | saved | 3072 | 1218 | 0.138674 | 0.427958 |
| seed:43 | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.084957 | 0.272356 |
| seed:43 | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.098196 | 0.312914 |
| seed:43 | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.074726 | 0.241564 |
| seed:43 | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.108427 | 0.343705 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.031067 | 0.112008 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.036663 | 0.134053 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029261 | 0.112713 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.042251 | 0.143041 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.096482 | 0.295162 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087230 | 0.284910 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.133569 | 0.412978 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.133733 | 0.413289 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.047115 | 0.159128 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.052239 | 0.167110 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.119138 | 0.389721 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.056759 | 0.201219 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.144272 | 0.450165 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.174141 | 0.539828 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.107293 | 0.338087 |
| seed:43 | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.160747 | 0.493738 |
| seed:43 | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.085594 | 0.273869 |
| seed:43 | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.093570 | 0.298890 |
| seed:43 | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.048142 | 0.165444 |
| seed:43 | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.135011 | 0.419825 |
| seed:43 | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.080093 | 0.256285 |
| seed:43 | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.094334 | 0.303624 |
| seed:43 | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.071896 | 0.229693 |
| seed:43 | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.102532 | 0.330216 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029892 | 0.105388 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032854 | 0.118267 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028195 | 0.107915 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.039725 | 0.134895 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.091943 | 0.284412 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087156 | 0.268942 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.135966 | 0.416799 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.127801 | 0.397001 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.039301 | 0.137314 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.042879 | 0.135090 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.120919 | 0.398122 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.052264 | 0.191134 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.135248 | 0.426420 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.169479 | 0.538646 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.093129 | 0.298628 |
| seed:43 | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.157372 | 0.490072 |
| seed:43 | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.080915 | 0.260711 |
| seed:43 | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.089313 | 0.286369 |
| seed:43 | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.043766 | 0.151459 |
| seed:43 | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.130662 | 0.408450 |
| seed:43 | B_input_confidence | available_bindings | 2 | 3072 | 519 | 0.109835 | 0.345589 |
| seed:43 | B_input_confidence | available_bindings | 4 | 3072 | 935 | 0.140439 | 0.427925 |
| seed:43 | B_input_confidence | condition | informative | 3072 | 431 | 0.102402 | 0.326307 |
| seed:43 | B_input_confidence | condition | misleading | 3072 | 1023 | 0.147872 | 0.447206 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.015350 | 0.074666 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048117 | 0.180579 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.047226 | 0.165212 |
| seed:43 | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053251 | 0.192332 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.137191 | 0.428927 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.110093 | 0.362499 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.199760 | 0.581553 |
| seed:43 | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.201296 | 0.588691 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.047267 | 0.177436 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.077442 | 0.254241 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.161534 | 0.508894 |
| seed:43 | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083992 | 0.285569 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.217748 | 0.626562 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.214580 | 0.622419 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.188693 | 0.561369 |
| seed:43 | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.216126 | 0.624041 |
| seed:43 | B_input_confidence | original_split | development | 1536 | 374 | 0.119360 | 0.369351 |
| seed:43 | B_input_confidence | original_split | train | 4608 | 1080 | 0.127063 | 0.392559 |
| seed:43 | B_input_confidence | query_role | current | 3072 | 236 | 0.063435 | 0.221129 |
| seed:43 | B_input_confidence | query_role | saved | 3072 | 1218 | 0.186839 | 0.552385 |
| seed:43 | B_interactions_confidence | available_bindings | 2 | 3072 | 519 | 0.104519 | 0.323427 |
| seed:43 | B_interactions_confidence | available_bindings | 4 | 3072 | 935 | 0.128502 | 0.398705 |
| seed:43 | B_interactions_confidence | condition | informative | 3072 | 431 | 0.093594 | 0.295787 |
| seed:43 | B_interactions_confidence | condition | misleading | 3072 | 1023 | 0.139427 | 0.426345 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029760 | 0.111945 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043064 | 0.147253 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044558 | 0.148296 |
| seed:43 | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053237 | 0.184629 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.131399 | 0.400689 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.098431 | 0.323636 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.210124 | 0.610258 |
| seed:43 | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.167420 | 0.501673 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.061299 | 0.201885 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.069935 | 0.226816 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157224 | 0.530238 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.077144 | 0.267716 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.218928 | 0.623143 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.194991 | 0.574028 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.161735 | 0.498077 |
| seed:43 | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.204280 | 0.602390 |
| seed:43 | B_interactions_confidence | original_split | development | 1536 | 374 | 0.121368 | 0.371850 |
| seed:43 | B_interactions_confidence | original_split | train | 4608 | 1080 | 0.114891 | 0.357471 |
| seed:43 | B_interactions_confidence | query_role | current | 3072 | 236 | 0.061992 | 0.211008 |
| seed:43 | B_interactions_confidence | query_role | saved | 3072 | 1218 | 0.171029 | 0.511124 |
| seed:43 | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.101032 | 0.314946 |
| seed:43 | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.129263 | 0.400349 |
| seed:43 | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.091103 | 0.290474 |
| seed:43 | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.139193 | 0.424822 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029229 | 0.111042 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041599 | 0.144712 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.040322 | 0.140407 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051661 | 0.180571 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.124890 | 0.383063 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094980 | 0.316904 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.194475 | 0.575859 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.167762 | 0.503515 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.055374 | 0.187138 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068647 | 0.219281 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156594 | 0.508386 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075737 | 0.262133 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.204327 | 0.589502 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.194057 | 0.573407 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.172028 | 0.523090 |
| seed:43 | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.212621 | 0.625910 |
| seed:43 | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.115922 | 0.357436 |
| seed:43 | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.114890 | 0.357718 |
| seed:43 | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.060170 | 0.204777 |
| seed:43 | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.170125 | 0.510519 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.082974 | 0.270322 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.093253 | 0.298008 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.069632 | 0.228252 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.106594 | 0.340078 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029990 | 0.102516 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.034772 | 0.138637 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.030618 | 0.110788 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.034157 | 0.115435 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.090305 | 0.286648 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087112 | 0.281068 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.131040 | 0.405484 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.122120 | 0.385490 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.048080 | 0.159723 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.049348 | 0.165367 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.110535 | 0.368145 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.048052 | 0.168385 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.141763 | 0.449340 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.171540 | 0.537743 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.115039 | 0.362162 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.165837 | 0.511812 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.083959 | 0.270253 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.089498 | 0.288802 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.043534 | 0.151605 |
| seed:43 | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.132692 | 0.416724 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 519 | 0.078526 | 0.254927 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 935 | 0.089986 | 0.292593 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 431 | 0.067795 | 0.218400 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 1023 | 0.100717 | 0.329120 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027906 | 0.094399 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.031710 | 0.117260 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029361 | 0.103595 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031663 | 0.109478 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.087673 | 0.277946 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.086540 | 0.265815 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.138288 | 0.419920 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.119392 | 0.378743 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.039456 | 0.135223 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.040598 | 0.132073 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.113255 | 0.375158 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.045027 | 0.161943 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.135140 | 0.435343 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.167217 | 0.542961 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.098562 | 0.319084 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.159959 | 0.510730 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 374 | 0.079985 | 0.258632 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 1080 | 0.085680 | 0.278803 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 236 | 0.039584 | 0.137185 |
| seed:43 | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 1218 | 0.128928 | 0.410336 |
| seed:43 | B_event_input | available_bindings | 2 | 3072 | 519 | 0.109486 | 0.334115 |
| seed:43 | B_event_input | available_bindings | 4 | 3072 | 935 | 0.132516 | 0.401840 |
| seed:43 | B_event_input | condition | informative | 3072 | 431 | 0.092003 | 0.291339 |
| seed:43 | B_event_input | condition | misleading | 3072 | 1023 | 0.149999 | 0.444616 |
| seed:43 | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.017616 | 0.076184 |
| seed:43 | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.045705 | 0.158817 |
| seed:43 | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044474 | 0.155900 |
| seed:43 | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053720 | 0.185862 |
| seed:43 | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.124957 | 0.384304 |
| seed:43 | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.107629 | 0.341336 |
| seed:43 | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.202780 | 0.588777 |
| seed:43 | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.158746 | 0.479311 |
| seed:43 | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.051055 | 0.171997 |
| seed:43 | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.077137 | 0.247649 |
| seed:43 | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.158284 | 0.492327 |
| seed:43 | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075906 | 0.248975 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.233903 | 0.659407 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.212682 | 0.610944 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.200535 | 0.587359 |
| seed:43 | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.226490 | 0.649810 |
| seed:43 | B_event_input | original_split | development | 1536 | 374 | 0.121761 | 0.367346 |
| seed:43 | B_event_input | original_split | train | 4608 | 1080 | 0.120748 | 0.368188 |
| seed:43 | B_event_input | query_role | current | 3072 | 236 | 0.061650 | 0.206027 |
| seed:43 | B_event_input | query_role | saved | 3072 | 1218 | 0.180352 | 0.529929 |
| seed:43 | B_event_interactions | available_bindings | 2 | 3072 | 519 | 0.105042 | 0.321039 |
| seed:43 | B_event_interactions | available_bindings | 4 | 3072 | 935 | 0.127308 | 0.391522 |
| seed:43 | B_event_interactions | condition | informative | 3072 | 431 | 0.089064 | 0.281492 |
| seed:43 | B_event_interactions | condition | misleading | 3072 | 1023 | 0.143287 | 0.431069 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026193 | 0.098405 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042704 | 0.143963 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.040222 | 0.137238 |
| seed:43 | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.054049 | 0.186678 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.122850 | 0.372810 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.101518 | 0.326758 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.207493 | 0.602670 |
| seed:43 | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.148919 | 0.451437 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.057616 | 0.193744 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.071634 | 0.226911 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.148766 | 0.470195 |
| seed:43 | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.074950 | 0.255295 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.224563 | 0.633357 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.198786 | 0.579443 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.178179 | 0.535262 |
| seed:43 | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.218229 | 0.636823 |
| seed:43 | B_event_interactions | original_split | development | 1536 | 374 | 0.119759 | 0.361833 |
| seed:43 | B_event_interactions | original_split | train | 4608 | 1080 | 0.114981 | 0.354430 |
| seed:43 | B_event_interactions | query_role | current | 3072 | 236 | 0.060790 | 0.203545 |
| seed:43 | B_event_interactions | query_role | saved | 3072 | 1218 | 0.171561 | 0.509016 |
| seed:43 | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.101411 | 0.311967 |
| seed:43 | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.127808 | 0.393376 |
| seed:43 | B_event_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.086619 | 0.276103 |
| seed:43 | B_event_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.142600 | 0.429239 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025904 | 0.096368 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041989 | 0.143742 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.038116 | 0.135281 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.052609 | 0.183399 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.113228 | 0.348327 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.098980 | 0.319516 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.191226 | 0.567345 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.148867 | 0.452886 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054093 | 0.183554 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.070736 | 0.223016 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.146815 | 0.450416 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.074674 | 0.252800 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.209977 | 0.598332 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.195160 | 0.572236 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.187677 | 0.561711 |
| seed:43 | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.224561 | 0.656168 |
| seed:43 | B_event_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.114187 | 0.347326 |
| seed:43 | B_event_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.114750 | 0.354453 |
| seed:43 | B_event_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.059677 | 0.199732 |
| seed:43 | B_event_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.169542 | 0.505610 |
| seed:43 | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.078928 | 0.258959 |
| seed:43 | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.092269 | 0.294029 |
| seed:43 | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.066137 | 0.219002 |
| seed:43 | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.105061 | 0.333986 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025344 | 0.088687 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033144 | 0.134068 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.026741 | 0.099044 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.030271 | 0.106919 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.083321 | 0.262239 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.082254 | 0.266169 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.126295 | 0.395311 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.120793 | 0.384859 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.044753 | 0.152354 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.048080 | 0.160822 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.099977 | 0.315372 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.043640 | 0.154053 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.145105 | 0.468836 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.160830 | 0.506640 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.105619 | 0.329344 |
| seed:43 | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.176460 | 0.537693 |
| seed:43 | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.079640 | 0.256942 |
| seed:43 | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.087585 | 0.283012 |
| seed:43 | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040057 | 0.140872 |
| seed:43 | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.131141 | 0.412117 |
| seed:43 | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.075123 | 0.245669 |
| seed:43 | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.087366 | 0.282859 |
| seed:43 | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.063746 | 0.209072 |
| seed:43 | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.098743 | 0.319456 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023841 | 0.083041 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.030579 | 0.117807 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.025939 | 0.094818 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.028996 | 0.104017 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.080173 | 0.252420 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.081536 | 0.255254 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.130119 | 0.400998 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.114473 | 0.367732 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.038993 | 0.133767 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.039310 | 0.128612 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.104841 | 0.329807 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.042402 | 0.148856 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.137911 | 0.451856 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.158855 | 0.511797 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.088314 | 0.287162 |
| seed:43 | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.163641 | 0.514560 |
| seed:43 | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.075921 | 0.246246 |
| seed:43 | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.083019 | 0.270270 |
| seed:43 | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.037208 | 0.129512 |
| seed:43 | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.125281 | 0.399016 |
| seed:43 | B_joint_input | available_bindings | 2 | 3072 | 519 | 0.107174 | 0.328040 |
| seed:43 | B_joint_input | available_bindings | 4 | 3072 | 935 | 0.129232 | 0.392794 |
| seed:43 | B_joint_input | condition | informative | 3072 | 431 | 0.089543 | 0.284119 |
| seed:43 | B_joint_input | condition | misleading | 3072 | 1023 | 0.146863 | 0.436715 |
| seed:43 | B_joint_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.019387 | 0.085928 |
| seed:43 | B_joint_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043783 | 0.150757 |
| seed:43 | B_joint_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046599 | 0.160984 |
| seed:43 | B_joint_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.048640 | 0.166347 |
| seed:43 | B_joint_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.123143 | 0.377406 |
| seed:43 | B_joint_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.102482 | 0.328072 |
| seed:43 | B_joint_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.213856 | 0.623378 |
| seed:43 | B_joint_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.155052 | 0.472157 |
| seed:43 | B_joint_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.052243 | 0.171372 |
| seed:43 | B_joint_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.075102 | 0.240627 |
| seed:43 | B_joint_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.162900 | 0.509014 |
| seed:43 | B_joint_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069078 | 0.227147 |
| seed:43 | B_joint_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.232703 | 0.661198 |
| seed:43 | B_joint_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.207938 | 0.600834 |
| seed:43 | B_joint_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.190331 | 0.563886 |
| seed:43 | B_joint_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.224807 | 0.648308 |
| seed:43 | B_joint_input | original_split | development | 1536 | 374 | 0.122387 | 0.370756 |
| seed:43 | B_joint_input | original_split | train | 4608 | 1080 | 0.116808 | 0.356971 |
| seed:43 | B_joint_input | query_role | current | 3072 | 236 | 0.059037 | 0.196567 |
| seed:43 | B_joint_input | query_role | saved | 3072 | 1218 | 0.177369 | 0.524268 |
| seed:43 | B_joint_interactions | available_bindings | 2 | 3072 | 519 | 0.102424 | 0.314694 |
| seed:43 | B_joint_interactions | available_bindings | 4 | 3072 | 935 | 0.124913 | 0.384141 |
| seed:43 | B_joint_interactions | condition | informative | 3072 | 431 | 0.087046 | 0.275832 |
| seed:43 | B_joint_interactions | condition | misleading | 3072 | 1023 | 0.140291 | 0.423003 |
| seed:43 | B_joint_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027389 | 0.101958 |
| seed:43 | B_joint_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040919 | 0.142544 |
| seed:43 | B_joint_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043197 | 0.144465 |
| seed:43 | B_joint_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049248 | 0.168771 |
| seed:43 | B_joint_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.125059 | 0.373710 |
| seed:43 | B_joint_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094898 | 0.308469 |
| seed:43 | B_joint_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.218478 | 0.639776 |
| seed:43 | B_joint_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.146606 | 0.447299 |
| seed:43 | B_joint_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.059359 | 0.195318 |
| seed:43 | B_joint_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.067780 | 0.216881 |
| seed:43 | B_joint_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157352 | 0.495698 |
| seed:43 | B_joint_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069105 | 0.235382 |
| seed:43 | B_joint_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.225238 | 0.638097 |
| seed:43 | B_joint_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.192425 | 0.565731 |
| seed:43 | B_joint_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.161875 | 0.494275 |
| seed:43 | B_joint_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.218445 | 0.637581 |
| seed:43 | B_joint_interactions | original_split | development | 1536 | 374 | 0.121249 | 0.366031 |
| seed:43 | B_joint_interactions | original_split | train | 4608 | 1080 | 0.111142 | 0.343879 |
| seed:43 | B_joint_interactions | query_role | current | 3072 | 236 | 0.058359 | 0.195549 |
| seed:43 | B_joint_interactions | query_role | saved | 3072 | 1218 | 0.168979 | 0.503286 |
| seed:43 | B_joint_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.098560 | 0.304334 |
| seed:43 | B_joint_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.125133 | 0.385009 |
| seed:43 | B_joint_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.084327 | 0.269328 |
| seed:43 | B_joint_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.139366 | 0.420015 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026983 | 0.101472 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040466 | 0.139033 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.040713 | 0.140488 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.048580 | 0.167770 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.112154 | 0.339297 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.092449 | 0.303677 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.198992 | 0.593854 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.146261 | 0.447661 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054601 | 0.182660 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.066994 | 0.211951 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.154297 | 0.473113 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.068597 | 0.232454 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.207036 | 0.593101 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.191063 | 0.563077 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.173725 | 0.526632 |
| seed:43 | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.223656 | 0.653343 |
| seed:43 | B_joint_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.114106 | 0.347262 |
| seed:43 | B_joint_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.111093 | 0.343808 |
| seed:43 | B_joint_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.057246 | 0.191122 |
| seed:43 | B_joint_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.166447 | 0.498222 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.078381 | 0.256437 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.092061 | 0.293497 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.064734 | 0.215253 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.105709 | 0.334682 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025321 | 0.090722 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033736 | 0.137346 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.025022 | 0.096138 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.030671 | 0.106817 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.079481 | 0.253937 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.082807 | 0.266535 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.136677 | 0.420479 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.112555 | 0.362106 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.042262 | 0.144267 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.046813 | 0.156149 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.101848 | 0.323764 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.041404 | 0.144252 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.140013 | 0.453320 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.163393 | 0.507472 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.117157 | 0.366208 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.181124 | 0.554294 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.079572 | 0.257590 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.087105 | 0.280760 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.039359 | 0.138300 |
| seed:43 | B_joint_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.131084 | 0.411634 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.073896 | 0.243092 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.087609 | 0.284233 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.061900 | 0.205133 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.099606 | 0.322193 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024585 | 0.085604 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.030520 | 0.122886 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.025721 | 0.094326 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.027860 | 0.101360 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.076552 | 0.244536 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.081087 | 0.252090 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.139270 | 0.421974 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.106521 | 0.347981 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.037368 | 0.127769 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.037957 | 0.125694 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.104046 | 0.325243 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.039861 | 0.137592 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.133218 | 0.443015 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.157952 | 0.507422 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.099923 | 0.317532 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.172491 | 0.545571 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.076034 | 0.246744 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.082326 | 0.269302 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036091 | 0.126475 |
| seed:43 | B_joint_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.125415 | 0.400851 |
| seed:43 | B_stress_input | available_bindings | 2 | 3072 | 519 | 0.105831 | 0.331142 |
| seed:43 | B_stress_input | available_bindings | 4 | 3072 | 935 | 0.139454 | 0.422398 |
| seed:43 | B_stress_input | condition | informative | 3072 | 431 | 0.096347 | 0.308825 |
| seed:43 | B_stress_input | condition | misleading | 3072 | 1023 | 0.148938 | 0.444714 |
| seed:43 | B_stress_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.016118 | 0.075743 |
| seed:43 | B_stress_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.047022 | 0.179057 |
| seed:43 | B_stress_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043633 | 0.149328 |
| seed:43 | B_stress_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050613 | 0.179193 |
| seed:43 | B_stress_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.121744 | 0.379709 |
| seed:43 | B_stress_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.103301 | 0.335945 |
| seed:43 | B_stress_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.172316 | 0.523518 |
| seed:43 | B_stress_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.193263 | 0.574413 |
| seed:43 | B_stress_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.043999 | 0.157478 |
| seed:43 | B_stress_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.073092 | 0.234915 |
| seed:43 | B_stress_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.152183 | 0.470179 |
| seed:43 | B_stress_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075979 | 0.256362 |
| seed:43 | B_stress_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.222999 | 0.640085 |
| seed:43 | B_stress_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.209143 | 0.610424 |
| seed:43 | B_stress_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.207135 | 0.600536 |
| seed:43 | B_stress_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.234472 | 0.668828 |
| seed:43 | B_stress_input | original_split | development | 1536 | 374 | 0.115416 | 0.354132 |
| seed:43 | B_stress_input | original_split | train | 4608 | 1080 | 0.125052 | 0.384315 |
| seed:43 | B_stress_input | query_role | current | 3072 | 236 | 0.059561 | 0.204984 |
| seed:43 | B_stress_input | query_role | saved | 3072 | 1218 | 0.185724 | 0.548555 |
| seed:43 | B_stress_interactions | available_bindings | 2 | 3072 | 519 | 0.102438 | 0.316102 |
| seed:43 | B_stress_interactions | available_bindings | 4 | 3072 | 935 | 0.129181 | 0.397072 |
| seed:43 | B_stress_interactions | condition | informative | 3072 | 431 | 0.089533 | 0.285539 |
| seed:43 | B_stress_interactions | condition | misleading | 3072 | 1023 | 0.142086 | 0.427635 |
| seed:43 | B_stress_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.030715 | 0.113215 |
| seed:43 | B_stress_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042079 | 0.146436 |
| seed:43 | B_stress_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044802 | 0.147534 |
| seed:43 | B_stress_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049484 | 0.172413 |
| seed:43 | B_stress_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.123099 | 0.375882 |
| seed:43 | B_stress_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094269 | 0.309333 |
| seed:43 | B_stress_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.183382 | 0.550915 |
| seed:43 | B_stress_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.164033 | 0.498230 |
| seed:43 | B_stress_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054278 | 0.179426 |
| seed:43 | B_stress_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068194 | 0.216712 |
| seed:43 | B_stress_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.148688 | 0.466953 |
| seed:43 | B_stress_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.071823 | 0.245699 |
| seed:43 | B_stress_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.220900 | 0.628525 |
| seed:43 | B_stress_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.195590 | 0.575605 |
| seed:43 | B_stress_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.178300 | 0.537840 |
| seed:43 | B_stress_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.223695 | 0.648956 |
| seed:43 | B_stress_interactions | original_split | development | 1536 | 374 | 0.117763 | 0.358112 |
| seed:43 | B_stress_interactions | original_split | train | 4608 | 1080 | 0.115158 | 0.356079 |
| seed:43 | B_stress_interactions | query_role | current | 3072 | 236 | 0.058796 | 0.197622 |
| seed:43 | B_stress_interactions | query_role | saved | 3072 | 1218 | 0.172823 | 0.515552 |
| seed:43 | B_stress_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.101104 | 0.313293 |
| seed:43 | B_stress_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.129445 | 0.398033 |
| seed:43 | B_stress_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.089266 | 0.285199 |
| seed:43 | B_stress_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.141283 | 0.426126 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.030516 | 0.112637 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041754 | 0.146601 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043865 | 0.146169 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049480 | 0.172690 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.120810 | 0.369942 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094569 | 0.311200 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.178944 | 0.540906 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.164847 | 0.499578 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053218 | 0.177522 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.067965 | 0.214990 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.148857 | 0.464230 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.072349 | 0.247187 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.208461 | 0.598654 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.195837 | 0.577588 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.180198 | 0.543169 |
| seed:43 | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.224288 | 0.652207 |
| seed:43 | B_stress_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.114823 | 0.350999 |
| seed:43 | B_stress_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.115425 | 0.357217 |
| seed:43 | B_stress_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.058675 | 0.197353 |
| seed:43 | B_stress_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.171874 | 0.513973 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.082723 | 0.267610 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.091597 | 0.290467 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.067861 | 0.223812 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.106459 | 0.334265 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.031031 | 0.104993 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.034693 | 0.135332 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.030336 | 0.106595 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.030624 | 0.107171 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.086490 | 0.275746 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.086332 | 0.275784 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.122121 | 0.386384 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.120789 | 0.387342 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.041667 | 0.140588 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.048382 | 0.160597 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.097265 | 0.309830 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.044582 | 0.155830 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.146524 | 0.461203 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.174077 | 0.542681 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.123227 | 0.385350 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.169080 | 0.506267 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.082031 | 0.262768 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.088870 | 0.284462 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040889 | 0.141930 |
| seed:43 | B_stress_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.133432 | 0.416147 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.077292 | 0.250478 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.088316 | 0.282490 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.065860 | 0.213562 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.099747 | 0.319406 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029006 | 0.098302 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.031810 | 0.118745 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028515 | 0.100183 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.028708 | 0.100244 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.082800 | 0.263911 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084214 | 0.257687 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.126784 | 0.392163 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.118820 | 0.380355 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.032725 | 0.115532 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.039406 | 0.128717 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.099578 | 0.314080 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.041061 | 0.145591 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.137369 | 0.441202 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.167370 | 0.538246 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.105145 | 0.340331 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.163322 | 0.500411 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.076985 | 0.248721 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.084743 | 0.272405 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036886 | 0.127540 |
| seed:43 | B_stress_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.128721 | 0.405428 |
| ensemble:mean_probability | prior | available_bindings | 2 | 3072 | 519 | 0.145339 | 0.468864 |
| ensemble:mean_probability | prior | available_bindings | 4 | 3072 | 935 | 0.216581 | 0.627243 |
| ensemble:mean_probability | prior | condition | informative | 3072 | 431 | 0.130197 | 0.435165 |
| ensemble:mean_probability | prior | condition | misleading | 3072 | 1023 | 0.231723 | 0.660941 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.063664 | 0.286730 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.084070 | 0.332584 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.088152 | 0.341081 |
| ensemble:mean_probability | prior | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.089127 | 0.343794 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.157008 | 0.494722 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.133969 | 0.443834 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.241453 | 0.682557 |
| ensemble:mean_probability | prior | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.207200 | 0.606555 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.084513 | 0.333247 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.109777 | 0.389743 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.163558 | 0.509510 |
| ensemble:mean_probability | prior | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.109759 | 0.389704 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.307828 | 0.830462 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.237710 | 0.674441 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.494357 | 1.245985 |
| ensemble:mean_probability | prior | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.436000 | 1.114886 |
| ensemble:mean_probability | prior | original_split | development | 1536 | 374 | 0.184462 | 0.555788 |
| ensemble:mean_probability | prior | original_split | train | 4608 | 1080 | 0.179793 | 0.545475 |
| ensemble:mean_probability | prior | query_role | current | 3072 | 236 | 0.096579 | 0.360306 |
| ensemble:mean_probability | prior | query_role | saved | 3072 | 1218 | 0.265341 | 0.735801 |
| ensemble:mean_probability | A_input | available_bindings | 2 | 3072 | 519 | 0.120925 | 0.377573 |
| ensemble:mean_probability | A_input | available_bindings | 4 | 3072 | 935 | 0.144245 | 0.440058 |
| ensemble:mean_probability | A_input | condition | informative | 3072 | 431 | 0.112601 | 0.356148 |
| ensemble:mean_probability | A_input | condition | misleading | 3072 | 1023 | 0.152568 | 0.461483 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014857 | 0.071020 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048472 | 0.183609 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.048624 | 0.169634 |
| ensemble:mean_probability | A_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053348 | 0.190492 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.154146 | 0.486398 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.128916 | 0.432651 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.220865 | 0.632992 |
| ensemble:mean_probability | A_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.223728 | 0.642520 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.047926 | 0.184914 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.080593 | 0.268608 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.161420 | 0.528873 |
| ensemble:mean_probability | A_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.082647 | 0.291219 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.245863 | 0.685518 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.236172 | 0.666648 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.163170 | 0.509697 |
| ensemble:mean_probability | A_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.213835 | 0.619807 |
| ensemble:mean_probability | A_input | original_split | development | 1536 | 374 | 0.126639 | 0.391408 |
| ensemble:mean_probability | A_input | original_split | train | 4608 | 1080 | 0.134567 | 0.414618 |
| ensemble:mean_probability | A_input | query_role | current | 3072 | 236 | 0.063827 | 0.226158 |
| ensemble:mean_probability | A_input | query_role | saved | 3072 | 1218 | 0.201343 | 0.591473 |
| ensemble:mean_probability | A_interactions | available_bindings | 2 | 3072 | 519 | 0.116081 | 0.357287 |
| ensemble:mean_probability | A_interactions | available_bindings | 4 | 3072 | 935 | 0.131066 | 0.403867 |
| ensemble:mean_probability | A_interactions | condition | informative | 3072 | 431 | 0.102852 | 0.323866 |
| ensemble:mean_probability | A_interactions | condition | misleading | 3072 | 1023 | 0.144296 | 0.437288 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.021862 | 0.089908 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.044358 | 0.152856 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043308 | 0.150522 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051020 | 0.173905 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.149324 | 0.467433 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.123497 | 0.406473 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.226980 | 0.647056 |
| ensemble:mean_probability | A_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.185853 | 0.550738 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.055239 | 0.190891 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.075037 | 0.242128 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157151 | 0.528711 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.077585 | 0.266658 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.243401 | 0.679450 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.218683 | 0.628425 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.145769 | 0.467688 |
| ensemble:mean_probability | A_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.200019 | 0.588464 |
| ensemble:mean_probability | A_interactions | original_split | development | 1536 | 374 | 0.126072 | 0.387445 |
| ensemble:mean_probability | A_interactions | original_split | train | 4608 | 1080 | 0.122741 | 0.378288 |
| ensemble:mean_probability | A_interactions | query_role | current | 3072 | 236 | 0.061470 | 0.209316 |
| ensemble:mean_probability | A_interactions | query_role | saved | 3072 | 1218 | 0.185678 | 0.551838 |
| ensemble:mean_probability | A_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.116261 | 0.358020 |
| ensemble:mean_probability | A_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.131461 | 0.404029 |
| ensemble:mean_probability | A_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.102767 | 0.323783 |
| ensemble:mean_probability | A_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.144955 | 0.438267 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.021708 | 0.089517 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.044865 | 0.157302 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042500 | 0.148451 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050448 | 0.171179 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.147009 | 0.460097 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.125187 | 0.411824 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.226754 | 0.646619 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.185455 | 0.548818 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.055699 | 0.192102 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.075412 | 0.242738 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.154955 | 0.516915 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.077468 | 0.264497 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.237804 | 0.663755 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.220995 | 0.633523 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.148449 | 0.476885 |
| ensemble:mean_probability | A_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.203109 | 0.597072 |
| ensemble:mean_probability | A_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.124758 | 0.383318 |
| ensemble:mean_probability | A_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.123562 | 0.380261 |
| ensemble:mean_probability | A_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.061373 | 0.208631 |
| ensemble:mean_probability | A_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.186349 | 0.553419 |
| ensemble:mean_probability | A_interactions_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.085835 | 0.268587 |
| ensemble:mean_probability | A_interactions_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.106865 | 0.338553 |
| ensemble:mean_probability | A_interactions_neutral_scored | condition | informative | 3072 | 431 | 0.082194 | 0.255802 |
| ensemble:mean_probability | A_interactions_neutral_scored | condition | misleading | 3072 | 1023 | 0.110507 | 0.351338 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024158 | 0.089436 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032106 | 0.115558 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028438 | 0.106632 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.042115 | 0.144649 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.107387 | 0.328723 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.101245 | 0.303171 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.178159 | 0.518363 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.151798 | 0.455955 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.037270 | 0.134549 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.044331 | 0.143835 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.128867 | 0.427184 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.057408 | 0.213420 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.149040 | 0.463483 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.178401 | 0.540863 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.111415 | 0.342153 |
| ensemble:mean_probability | A_interactions_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.172257 | 0.532165 |
| ensemble:mean_probability | A_interactions_neutral_scored | original_split | development | 1536 | 374 | 0.090216 | 0.285560 |
| ensemble:mean_probability | A_interactions_neutral_scored | original_split | train | 4608 | 1080 | 0.098395 | 0.309574 |
| ensemble:mean_probability | A_interactions_neutral_scored | query_role | current | 3072 | 236 | 0.045147 | 0.158738 |
| ensemble:mean_probability | A_interactions_neutral_scored | query_role | saved | 3072 | 1218 | 0.147554 | 0.448403 |
| ensemble:mean_probability | A_interactions_oracle | available_bindings | 2 | 3072 | 519 | 0.091302 | 0.289520 |
| ensemble:mean_probability | A_interactions_oracle | available_bindings | 4 | 3072 | 935 | 0.101173 | 0.321203 |
| ensemble:mean_probability | A_interactions_oracle | condition | informative | 3072 | 431 | 0.079161 | 0.253008 |
| ensemble:mean_probability | A_interactions_oracle | condition | misleading | 3072 | 1023 | 0.113314 | 0.357715 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.032646 | 0.116527 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040808 | 0.147005 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.035657 | 0.128677 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.046058 | 0.155075 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.105507 | 0.321136 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.093079 | 0.295283 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.158402 | 0.471584 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.132730 | 0.410415 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.058477 | 0.190896 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.058758 | 0.191078 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.119040 | 0.393380 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.062486 | 0.217076 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.157314 | 0.484429 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.178193 | 0.547262 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.109775 | 0.349871 |
| ensemble:mean_probability | A_interactions_oracle | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.159782 | 0.490505 |
| ensemble:mean_probability | A_interactions_oracle | original_split | development | 1536 | 374 | 0.094230 | 0.297457 |
| ensemble:mean_probability | A_interactions_oracle | original_split | train | 4608 | 1080 | 0.096907 | 0.307996 |
| ensemble:mean_probability | A_interactions_oracle | query_role | current | 3072 | 236 | 0.053247 | 0.181249 |
| ensemble:mean_probability | A_interactions_oracle | query_role | saved | 3072 | 1218 | 0.139228 | 0.429474 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.085171 | 0.273595 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.098044 | 0.312502 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.074537 | 0.242033 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.108679 | 0.344064 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.030409 | 0.109644 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.037260 | 0.138173 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029472 | 0.117553 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.041744 | 0.142219 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.095646 | 0.294051 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087865 | 0.287377 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.133206 | 0.414519 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.132974 | 0.411206 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.044292 | 0.152865 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.052724 | 0.169458 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.115230 | 0.369615 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.055973 | 0.199681 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.144534 | 0.450507 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.175740 | 0.543029 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.114080 | 0.352178 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.161525 | 0.496131 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.085146 | 0.272333 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.093762 | 0.299954 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.047609 | 0.164676 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.135607 | 0.421422 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.080376 | 0.257108 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.093984 | 0.302361 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.071634 | 0.229598 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.102726 | 0.329870 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.029360 | 0.103374 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033421 | 0.121246 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.027847 | 0.110713 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.039341 | 0.133897 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.090927 | 0.282541 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087860 | 0.272361 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.135299 | 0.415077 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.126731 | 0.393763 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.037260 | 0.133023 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.043484 | 0.136957 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.117199 | 0.375202 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.051365 | 0.188846 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.134555 | 0.425013 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.171440 | 0.540105 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.098069 | 0.309883 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.158001 | 0.492649 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.080218 | 0.258232 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.089500 | 0.286902 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.043310 | 0.150218 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.131050 | 0.409250 |
| ensemble:mean_probability | B_input_confidence | available_bindings | 2 | 3072 | 519 | 0.110254 | 0.345866 |
| ensemble:mean_probability | B_input_confidence | available_bindings | 4 | 3072 | 935 | 0.140475 | 0.427326 |
| ensemble:mean_probability | B_input_confidence | condition | informative | 3072 | 431 | 0.102587 | 0.325972 |
| ensemble:mean_probability | B_input_confidence | condition | misleading | 3072 | 1023 | 0.148142 | 0.447220 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.015191 | 0.075408 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.047897 | 0.178329 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046469 | 0.162889 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053382 | 0.191343 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.139686 | 0.434768 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.107980 | 0.356165 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.201249 | 0.585594 |
| ensemble:mean_probability | B_input_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.202840 | 0.591960 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.049215 | 0.181092 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.076813 | 0.252490 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.160250 | 0.503830 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083219 | 0.281978 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.225879 | 0.645857 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.213849 | 0.619647 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.181220 | 0.544866 |
| ensemble:mean_probability | B_input_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.217003 | 0.626449 |
| ensemble:mean_probability | B_input_confidence | original_split | development | 1536 | 374 | 0.120761 | 0.372619 |
| ensemble:mean_probability | B_input_confidence | original_split | train | 4608 | 1080 | 0.126899 | 0.391255 |
| ensemble:mean_probability | B_input_confidence | query_role | current | 3072 | 236 | 0.063224 | 0.219566 |
| ensemble:mean_probability | B_input_confidence | query_role | saved | 3072 | 1218 | 0.187506 | 0.553625 |
| ensemble:mean_probability | B_interactions_confidence | available_bindings | 2 | 3072 | 519 | 0.104838 | 0.324704 |
| ensemble:mean_probability | B_interactions_confidence | available_bindings | 4 | 3072 | 935 | 0.128444 | 0.398810 |
| ensemble:mean_probability | B_interactions_confidence | condition | informative | 3072 | 431 | 0.093662 | 0.296700 |
| ensemble:mean_probability | B_interactions_confidence | condition | misleading | 3072 | 1023 | 0.139620 | 0.426814 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028208 | 0.108666 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043426 | 0.150229 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.045962 | 0.154063 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053002 | 0.185262 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.132186 | 0.401807 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.098604 | 0.324527 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.213222 | 0.617855 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.166957 | 0.500518 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.060449 | 0.200308 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.070356 | 0.228496 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156399 | 0.523387 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.076994 | 0.266425 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.221906 | 0.630012 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.195264 | 0.574575 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.164532 | 0.505683 |
| ensemble:mean_probability | B_interactions_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.203557 | 0.601885 |
| ensemble:mean_probability | B_interactions_confidence | original_split | development | 1536 | 374 | 0.122135 | 0.373548 |
| ensemble:mean_probability | B_interactions_confidence | original_split | train | 4608 | 1080 | 0.114810 | 0.357827 |
| ensemble:mean_probability | B_interactions_confidence | query_role | current | 3072 | 236 | 0.061866 | 0.211197 |
| ensemble:mean_probability | B_interactions_confidence | query_role | saved | 3072 | 1218 | 0.171416 | 0.512317 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.100890 | 0.314822 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.129292 | 0.400903 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.090999 | 0.290769 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.139183 | 0.424956 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.027656 | 0.107051 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042339 | 0.146886 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042061 | 0.147524 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.051549 | 0.181166 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.124008 | 0.378553 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094450 | 0.316482 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.197730 | 0.583241 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.167189 | 0.503436 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054267 | 0.184959 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.069267 | 0.221731 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156621 | 0.505071 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075530 | 0.261197 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.205650 | 0.592895 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.193496 | 0.572107 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.175406 | 0.531104 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.211967 | 0.625146 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.116248 | 0.357821 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.114705 | 0.357876 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.060181 | 0.205121 |
| ensemble:mean_probability | B_interactions_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.170001 | 0.510604 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | available_bindings | 2 | 3072 | 519 | 0.082652 | 0.269484 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | available_bindings | 4 | 3072 | 935 | 0.093232 | 0.297703 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | condition | informative | 3072 | 431 | 0.069031 | 0.227595 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | condition | misleading | 3072 | 1023 | 0.106853 | 0.339593 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028116 | 0.098606 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.035270 | 0.139346 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.031171 | 0.115189 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.033980 | 0.115376 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.088579 | 0.284411 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.086001 | 0.279314 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.131990 | 0.410197 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.121040 | 0.383868 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.044530 | 0.151562 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.049775 | 0.166707 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.106131 | 0.343038 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.047965 | 0.169151 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.142153 | 0.450028 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.173175 | 0.539235 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.118847 | 0.370748 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.166903 | 0.512748 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | original_split | development | 1536 | 374 | 0.082908 | 0.267366 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | original_split | train | 4608 | 1080 | 0.089620 | 0.289003 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | query_role | current | 3072 | 236 | 0.043021 | 0.150225 |
| ensemble:mean_probability | B_interactions_oracle_neutral_raw_confidence | query_role | saved | 3072 | 1218 | 0.132863 | 0.416962 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | available_bindings | 2 | 3072 | 519 | 0.078120 | 0.254130 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | available_bindings | 4 | 3072 | 935 | 0.089479 | 0.290385 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | condition | informative | 3072 | 431 | 0.066831 | 0.217059 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | condition | misleading | 3072 | 1023 | 0.100768 | 0.327456 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026354 | 0.091531 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032177 | 0.120947 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.029411 | 0.107718 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.031661 | 0.109203 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.084636 | 0.271867 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.086055 | 0.266426 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.138118 | 0.419378 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.116642 | 0.372001 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.036695 | 0.129392 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.041311 | 0.134458 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.111540 | 0.356845 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.044122 | 0.160236 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.134022 | 0.432523 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.168324 | 0.540294 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.100189 | 0.325121 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.161223 | 0.510594 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | original_split | development | 1536 | 374 | 0.078556 | 0.254974 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | original_split | train | 4608 | 1080 | 0.085547 | 0.278019 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | query_role | current | 3072 | 236 | 0.039163 | 0.136468 |
| ensemble:mean_probability | B_interactions_oracle_neutral_scored_confidence | query_role | saved | 3072 | 1218 | 0.128436 | 0.408047 |
| ensemble:mean_probability | B_event_input | available_bindings | 2 | 3072 | 519 | 0.110139 | 0.336590 |
| ensemble:mean_probability | B_event_input | available_bindings | 4 | 3072 | 935 | 0.133243 | 0.403513 |
| ensemble:mean_probability | B_event_input | condition | informative | 3072 | 431 | 0.092905 | 0.293935 |
| ensemble:mean_probability | B_event_input | condition | misleading | 3072 | 1023 | 0.150476 | 0.446167 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.017122 | 0.075371 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.045331 | 0.155800 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043938 | 0.154912 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.054534 | 0.187619 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.129327 | 0.400563 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.107960 | 0.343516 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.199962 | 0.582728 |
| ensemble:mean_probability | B_event_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.161420 | 0.485915 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.050514 | 0.173291 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.076900 | 0.248640 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.157595 | 0.489940 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.076646 | 0.251863 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.233782 | 0.659721 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.215271 | 0.617110 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.198873 | 0.585497 |
| ensemble:mean_probability | B_event_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.226892 | 0.648848 |
| ensemble:mean_probability | B_event_input | original_split | development | 1536 | 374 | 0.121821 | 0.369247 |
| ensemble:mean_probability | B_event_input | original_split | train | 4608 | 1080 | 0.121647 | 0.370319 |
| ensemble:mean_probability | B_event_input | query_role | current | 3072 | 236 | 0.061734 | 0.206556 |
| ensemble:mean_probability | B_event_input | query_role | saved | 3072 | 1218 | 0.181647 | 0.533546 |
| ensemble:mean_probability | B_event_interactions | available_bindings | 2 | 3072 | 519 | 0.105881 | 0.323179 |
| ensemble:mean_probability | B_event_interactions | available_bindings | 4 | 3072 | 935 | 0.127452 | 0.392059 |
| ensemble:mean_probability | B_event_interactions | condition | informative | 3072 | 431 | 0.089361 | 0.282616 |
| ensemble:mean_probability | B_event_interactions | condition | misleading | 3072 | 1023 | 0.143972 | 0.432623 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024917 | 0.095598 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043281 | 0.146417 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.042038 | 0.143509 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.054210 | 0.188280 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.126486 | 0.383137 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.102520 | 0.328513 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.207935 | 0.604524 |
| ensemble:mean_probability | B_event_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.147527 | 0.447231 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.057221 | 0.192376 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.072019 | 0.228227 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.149287 | 0.470227 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.074829 | 0.254875 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.227545 | 0.640001 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.199382 | 0.580364 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.183349 | 0.547807 |
| ensemble:mean_probability | B_event_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.218683 | 0.638285 |
| ensemble:mean_probability | B_event_interactions | original_split | development | 1536 | 374 | 0.121246 | 0.365691 |
| ensemble:mean_probability | B_event_interactions | original_split | train | 4608 | 1080 | 0.115141 | 0.354929 |
| ensemble:mean_probability | B_event_interactions | query_role | current | 3072 | 236 | 0.060917 | 0.204335 |
| ensemble:mean_probability | B_event_interactions | query_role | saved | 3072 | 1218 | 0.172417 | 0.510904 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.101886 | 0.312975 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.128554 | 0.395444 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.087118 | 0.277496 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.143322 | 0.430923 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024737 | 0.093429 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042797 | 0.146171 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.040980 | 0.143908 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.052831 | 0.185330 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.115442 | 0.354015 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.099308 | 0.319788 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.193652 | 0.573749 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.148652 | 0.451372 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053611 | 0.181732 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.070978 | 0.223840 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.149093 | 0.455346 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.074867 | 0.253524 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.211671 | 0.602066 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.195501 | 0.572428 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.193401 | 0.576168 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.225285 | 0.658069 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.115670 | 0.350971 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.115070 | 0.355289 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.060015 | 0.200996 |
| ensemble:mean_probability | B_event_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.170425 | 0.507423 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.079518 | 0.261083 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.092790 | 0.295248 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.066640 | 0.221506 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.105669 | 0.334825 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024567 | 0.088579 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.033624 | 0.137700 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028841 | 0.107359 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.030970 | 0.109241 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.084959 | 0.268841 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.083793 | 0.270598 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.125037 | 0.395421 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.120384 | 0.383828 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.042894 | 0.147743 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.048708 | 0.162425 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.097492 | 0.300746 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.044047 | 0.155434 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.144930 | 0.467541 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.162311 | 0.509423 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.113955 | 0.350802 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.176928 | 0.537822 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.080002 | 0.258311 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.088205 | 0.284784 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040236 | 0.141859 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.132073 | 0.414472 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.075374 | 0.246655 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.087986 | 0.284140 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.063837 | 0.210450 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.099524 | 0.320345 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.022678 | 0.082288 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.030826 | 0.122007 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.026083 | 0.097906 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.029287 | 0.104833 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.080550 | 0.255344 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.083476 | 0.260715 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.128802 | 0.398835 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.113421 | 0.364747 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.036377 | 0.128692 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.040051 | 0.130819 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.103291 | 0.316546 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.041890 | 0.148407 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.137750 | 0.448982 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.159216 | 0.508733 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.094405 | 0.304519 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.167221 | 0.522324 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.075608 | 0.245702 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.083705 | 0.271963 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036953 | 0.129747 |
| ensemble:mean_probability | B_event_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.126408 | 0.401048 |
| ensemble:mean_probability | B_joint_input | available_bindings | 2 | 3072 | 519 | 0.106807 | 0.327492 |
| ensemble:mean_probability | B_joint_input | available_bindings | 4 | 3072 | 935 | 0.129161 | 0.392203 |
| ensemble:mean_probability | B_joint_input | condition | informative | 3072 | 431 | 0.089645 | 0.284303 |
| ensemble:mean_probability | B_joint_input | condition | misleading | 3072 | 1023 | 0.146323 | 0.435393 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.019034 | 0.085828 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.043443 | 0.149157 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.045347 | 0.158469 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049407 | 0.168893 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.125770 | 0.386293 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.101006 | 0.323801 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.208385 | 0.608452 |
| ensemble:mean_probability | B_joint_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.156661 | 0.475161 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.052388 | 0.172657 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.074434 | 0.239386 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.161384 | 0.502179 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069197 | 0.227198 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.234132 | 0.665952 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.206296 | 0.597243 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.185996 | 0.555328 |
| ensemble:mean_probability | B_joint_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.224486 | 0.646438 |
| ensemble:mean_probability | B_joint_input | original_split | development | 1536 | 374 | 0.121980 | 0.370491 |
| ensemble:mean_probability | B_joint_input | original_split | train | 4608 | 1080 | 0.116652 | 0.356300 |
| ensemble:mean_probability | B_joint_input | query_role | current | 3072 | 236 | 0.058921 | 0.196344 |
| ensemble:mean_probability | B_joint_input | query_role | saved | 3072 | 1218 | 0.177047 | 0.523352 |
| ensemble:mean_probability | B_joint_interactions | available_bindings | 2 | 3072 | 519 | 0.102445 | 0.314263 |
| ensemble:mean_probability | B_joint_interactions | available_bindings | 4 | 3072 | 935 | 0.124552 | 0.383633 |
| ensemble:mean_probability | B_joint_interactions | condition | informative | 3072 | 431 | 0.086722 | 0.275168 |
| ensemble:mean_probability | B_joint_interactions | condition | misleading | 3072 | 1023 | 0.140275 | 0.422728 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026420 | 0.100887 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041469 | 0.141620 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044510 | 0.150270 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049622 | 0.171286 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.125175 | 0.374162 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094344 | 0.307443 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.215904 | 0.633170 |
| ensemble:mean_probability | B_joint_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.145272 | 0.443562 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.059647 | 0.195250 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068190 | 0.217160 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156437 | 0.490273 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069444 | 0.236137 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.227880 | 0.643087 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.191108 | 0.562664 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.169565 | 0.513710 |
| ensemble:mean_probability | B_joint_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.216228 | 0.632969 |
| ensemble:mean_probability | B_joint_interactions | original_split | development | 1536 | 374 | 0.122055 | 0.367849 |
| ensemble:mean_probability | B_joint_interactions | original_split | train | 4608 | 1080 | 0.110646 | 0.342648 |
| ensemble:mean_probability | B_joint_interactions | query_role | current | 3072 | 236 | 0.058627 | 0.196044 |
| ensemble:mean_probability | B_joint_interactions | query_role | saved | 3072 | 1218 | 0.168370 | 0.501852 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.098780 | 0.305136 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.125855 | 0.387280 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.084913 | 0.271385 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.139722 | 0.421032 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.025864 | 0.098765 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041119 | 0.141719 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043234 | 0.148585 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.048977 | 0.170624 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.114055 | 0.344518 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.092650 | 0.304564 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.200649 | 0.599168 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.146846 | 0.448131 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.054457 | 0.181941 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.067455 | 0.213144 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.156021 | 0.475595 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.069146 | 0.234689 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.208242 | 0.595222 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.190149 | 0.561168 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.180552 | 0.542972 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.223044 | 0.652234 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.115474 | 0.350601 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.111265 | 0.344744 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.057700 | 0.192984 |
| ensemble:mean_probability | B_joint_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.166935 | 0.499432 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.078809 | 0.258417 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.093224 | 0.296516 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.065329 | 0.218213 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.106705 | 0.336720 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.024518 | 0.089958 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.034242 | 0.141745 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.027082 | 0.103168 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.030833 | 0.107440 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.080870 | 0.260293 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.083566 | 0.268907 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.135057 | 0.420550 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.113917 | 0.366615 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.041213 | 0.141702 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.047366 | 0.156977 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.096096 | 0.297377 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.042339 | 0.147371 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.141128 | 0.455881 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.163818 | 0.508954 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.127216 | 0.391077 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.183298 | 0.559417 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.080076 | 0.258987 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.087997 | 0.283626 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.039456 | 0.138867 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.132578 | 0.416066 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.074223 | 0.244180 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.088630 | 0.286751 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.062327 | 0.207513 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.100526 | 0.323418 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.023133 | 0.084099 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.031017 | 0.126522 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.025195 | 0.096235 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.028381 | 0.102263 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.077362 | 0.249255 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.082123 | 0.255895 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.138975 | 0.423529 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.107244 | 0.350572 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.035268 | 0.124244 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.038360 | 0.126320 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.102572 | 0.313510 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.040062 | 0.139644 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.133959 | 0.442552 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.158977 | 0.506270 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.107516 | 0.339845 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.174886 | 0.549301 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.076142 | 0.247785 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.083188 | 0.271359 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036012 | 0.126972 |
| ensemble:mean_probability | B_joint_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.126841 | 0.403959 |
| ensemble:mean_probability | B_stress_input | available_bindings | 2 | 3072 | 519 | 0.105576 | 0.330404 |
| ensemble:mean_probability | B_stress_input | available_bindings | 4 | 3072 | 935 | 0.138686 | 0.420253 |
| ensemble:mean_probability | B_stress_input | condition | informative | 3072 | 431 | 0.096188 | 0.308257 |
| ensemble:mean_probability | B_stress_input | condition | misleading | 3072 | 1023 | 0.148074 | 0.442400 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.015799 | 0.076277 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.047047 | 0.177752 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.043342 | 0.149326 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.050770 | 0.179293 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.123665 | 0.384790 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.101433 | 0.331044 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.170555 | 0.521079 |
| ensemble:mean_probability | B_stress_input | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.193584 | 0.574797 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.044409 | 0.158957 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.072914 | 0.235740 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.151024 | 0.461161 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.075273 | 0.255547 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.225448 | 0.644759 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.207401 | 0.605496 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.199934 | 0.584639 |
| ensemble:mean_probability | B_stress_input | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.233097 | 0.664337 |
| ensemble:mean_probability | B_stress_input | original_split | development | 1536 | 374 | 0.115292 | 0.353814 |
| ensemble:mean_probability | B_stress_input | original_split | train | 4608 | 1080 | 0.124411 | 0.382500 |
| ensemble:mean_probability | B_stress_input | query_role | current | 3072 | 236 | 0.059369 | 0.204547 |
| ensemble:mean_probability | B_stress_input | query_role | saved | 3072 | 1218 | 0.184894 | 0.546110 |
| ensemble:mean_probability | B_stress_interactions | available_bindings | 2 | 3072 | 519 | 0.101976 | 0.315424 |
| ensemble:mean_probability | B_stress_interactions | available_bindings | 4 | 3072 | 935 | 0.128760 | 0.396208 |
| ensemble:mean_probability | B_stress_interactions | condition | informative | 3072 | 431 | 0.089377 | 0.285851 |
| ensemble:mean_probability | B_stress_interactions | condition | misleading | 3072 | 1023 | 0.141359 | 0.425781 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028896 | 0.109224 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042436 | 0.148999 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.046858 | 0.154216 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049384 | 0.173255 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.121446 | 0.369139 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.094176 | 0.309431 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.183049 | 0.550371 |
| ensemble:mean_probability | B_stress_interactions | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.164219 | 0.499825 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.053137 | 0.177561 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068850 | 0.219204 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.148136 | 0.465196 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.071203 | 0.243722 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.221824 | 0.630593 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.193744 | 0.571655 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.181730 | 0.545342 |
| ensemble:mean_probability | B_stress_interactions | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.221287 | 0.641972 |
| ensemble:mean_probability | B_stress_interactions | original_split | development | 1536 | 374 | 0.117532 | 0.357346 |
| ensemble:mean_probability | B_stress_interactions | original_split | train | 4608 | 1080 | 0.114647 | 0.355306 |
| ensemble:mean_probability | B_stress_interactions | query_role | current | 3072 | 236 | 0.058631 | 0.197945 |
| ensemble:mean_probability | B_stress_interactions | query_role | saved | 3072 | 1218 | 0.172105 | 0.513688 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.100820 | 0.312950 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.129366 | 0.398130 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | condition | informative | 3072 | 431 | 0.089198 | 0.285802 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | condition | misleading | 3072 | 1023 | 0.140988 | 0.425279 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028240 | 0.107947 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.042546 | 0.149957 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.044696 | 0.151961 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.049426 | 0.173672 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.118325 | 0.359986 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.095385 | 0.313722 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.179206 | 0.542139 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.164974 | 0.501240 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.051448 | 0.174333 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.068716 | 0.217751 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.149498 | 0.463167 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.071574 | 0.245228 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.209290 | 0.600571 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.194623 | 0.574854 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.184195 | 0.552233 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.223462 | 0.648983 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | original_split | development | 1536 | 374 | 0.114350 | 0.349598 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | original_split | train | 4608 | 1080 | 0.115340 | 0.357521 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | query_role | current | 3072 | 236 | 0.058484 | 0.197709 |
| ensemble:mean_probability | B_stress_interactions_neutral_raw | query_role | saved | 3072 | 1218 | 0.171702 | 0.513371 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.082379 | 0.267382 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.091781 | 0.291177 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | condition | informative | 3072 | 431 | 0.066897 | 0.222223 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | condition | misleading | 3072 | 1023 | 0.107264 | 0.336336 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.028483 | 0.099237 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.035459 | 0.139917 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.031061 | 0.110951 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.030285 | 0.106370 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.081396 | 0.262518 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.087041 | 0.278335 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.120486 | 0.385413 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.118559 | 0.381727 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.039110 | 0.134964 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.049520 | 0.163551 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.095207 | 0.299051 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.044155 | 0.155381 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.144249 | 0.456141 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.175638 | 0.546060 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.126963 | 0.396921 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.172806 | 0.515706 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | original_split | development | 1536 | 374 | 0.080016 | 0.258171 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | original_split | train | 4608 | 1080 | 0.089435 | 0.286316 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | query_role | current | 3072 | 236 | 0.040565 | 0.141710 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_raw | query_role | saved | 3072 | 1218 | 0.133595 | 0.416850 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.076900 | 0.249887 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.088150 | 0.282081 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | condition | informative | 3072 | 431 | 0.064707 | 0.211607 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | condition | misleading | 3072 | 1023 | 0.100343 | 0.320361 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.026778 | 0.093210 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.032444 | 0.123215 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.028254 | 0.101700 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.028560 | 0.099422 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.078185 | 0.252908 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.084758 | 0.260680 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.124118 | 0.387566 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.115813 | 0.372874 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.030492 | 0.111061 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.040398 | 0.131238 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.096919 | 0.299164 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.040337 | 0.143969 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.134409 | 0.434295 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.168869 | 0.538454 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.106537 | 0.346827 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.167244 | 0.510670 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | original_split | development | 1536 | 374 | 0.074630 | 0.243184 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | original_split | train | 4608 | 1080 | 0.085157 | 0.273584 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | query_role | current | 3072 | 236 | 0.036482 | 0.126841 |
| ensemble:mean_probability | B_stress_interactions_oracle_neutral_scored | query_role | saved | 3072 | 1218 | 0.128568 | 0.405127 |

Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.
