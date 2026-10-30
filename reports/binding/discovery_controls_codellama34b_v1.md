# Discovery-only failure prediction: codellama/CodeLlama-34b-Instruct-hf

Exploratory nested grouped cross-validation on previously consumed discovery data, not M5 confirmation or a frozen unfamiliar-program forecast. No mechanism C, confidence or internal measurement feature is fitted. Repeated fold seeds reuse the same data and are not independent replications. Bootstrap intervals condition on the saved OOF predictions and do not rerun feature collection, model fitting or hyperparameter selection. Raw neutral behavior uses one distinct extra query without its oracle correctness; the scored tier additionally requires the neutral reference oracle. Target response properties and correctness never enter features. Capacity controls add fixed source-feature interactions. Source-oracle tiers additionally receive the program oracle value and its magnitude/sign without any target language-model response. On a source-oracle plus raw-neutral tier, neutral failure is a deterministic comparison of existing information, not a new observation; an increment can reflect the encoding capacity of the fitted function class.

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
| seed:29 | prior | 0.181167 | 0.548633 | 6144 | 1454 |
| seed:29 | A_input | 0.133066 | 0.409310 | 6144 | 1454 |
| seed:29 | A_interactions | 0.124611 | 0.383542 | 6144 | 1454 |
| seed:29 | A_interactions_neutral_raw | 0.124653 | 0.383131 | 6144 | 1454 |
| seed:29 | A_interactions_neutral_scored | 0.097191 | 0.305651 | 6144 | 1454 |
| seed:29 | A_interactions_oracle | 0.097123 | 0.307575 | 6144 | 1454 |
| seed:29 | A_interactions_oracle_neutral_raw | 0.092178 | 0.294428 | 6144 | 1454 |
| seed:29 | A_interactions_oracle_neutral_scored | 0.087765 | 0.281207 | 6144 | 1454 |
| seed:43 | prior | 0.180829 | 0.547689 | 6144 | 1454 |
| seed:43 | A_input | 0.132403 | 0.409566 | 6144 | 1454 |
| seed:43 | A_interactions | 0.123492 | 0.380324 | 6144 | 1454 |
| seed:43 | A_interactions_neutral_raw | 0.123965 | 0.381305 | 6144 | 1454 |
| seed:43 | A_interactions_neutral_scored | 0.096568 | 0.304512 | 6144 | 1454 |
| seed:43 | A_interactions_oracle | 0.096367 | 0.305378 | 6144 | 1454 |
| seed:43 | A_interactions_oracle_neutral_raw | 0.091576 | 0.292635 | 6144 | 1454 |
| seed:43 | A_interactions_oracle_neutral_scored | 0.087214 | 0.279955 | 6144 | 1454 |
| ensemble:mean_probability | prior | 0.180960 | 0.548053 | 6144 | 1454 |
| ensemble:mean_probability | A_input | 0.132585 | 0.408816 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions | 0.123574 | 0.380577 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_neutral_raw | 0.123861 | 0.381025 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_neutral_scored | 0.096350 | 0.303570 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_oracle | 0.096237 | 0.305361 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | 0.091608 | 0.293049 | 6144 | 1454 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | 0.087180 | 0.279734 | 6144 | 1454 |

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

Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.
