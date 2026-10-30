# Discovery-only failure prediction: codellama/CodeLlama-34b-Instruct-hf

Exploratory nested grouped cross-validation on previously consumed discovery data. Scalar next-token confidence is allowed in explicitly labelled B tiers; no mechanism C or unfamiliar-program/final confirmation is claimed. The new Transformers BF16 prefill measurement backend differs from the original vLLM outcome backend. Confidence is next-token sign/format confidence, not complete integer-answer confidence. Its scientific access cost is one target prefill per target, even when cached: no target response, generated token, target correctness or token identity is a feature. Raw neutral tiers separately use one distinct reference query; scored tiers also require reference correctness; source-oracle tiers separately receive the source oracle value. Adding neutral correctness to source-oracle plus raw-neutral features adds an encoding of existing information, not a new observation. Repeated partition seeds reuse the same targets, not independent replications. Template bootstrap intervals condition on saved OOF probabilities without refitting or multiplicity adjustment.

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

Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.
