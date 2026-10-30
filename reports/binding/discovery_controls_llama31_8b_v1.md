# Discovery-only failure prediction: meta-llama/Llama-3.1-8B-Instruct

Exploratory nested grouped cross-validation on previously consumed discovery data, not M5 confirmation or a frozen unfamiliar-program forecast. No mechanism C, confidence or internal measurement feature is fitted. Repeated fold seeds reuse the same data and are not independent replications. Bootstrap intervals condition on the saved OOF predictions and do not rerun feature collection, model fitting or hyperparameter selection. Raw neutral behavior uses one distinct extra query without its oracle correctness; the scored tier additionally requires the neutral reference oracle. Target response properties and correctness never enter features. Capacity controls add fixed source-feature interactions. Source-oracle tiers additionally receive the program oracle value and its magnitude/sign without any target language-model response. On a source-oracle plus raw-neutral tier, neutral failure is a deterministic comparison of existing information, not a new observation; an increment can reflect the encoding capacity of the fitted function class.

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
| seed:29 | prior | 0.065182 | 0.254318 | 6144 | 430 |
| seed:29 | A_input | 0.039799 | 0.138643 | 6144 | 430 |
| seed:29 | A_interactions | 0.039883 | 0.137716 | 6144 | 430 |
| seed:29 | A_interactions_neutral_raw | 0.040341 | 0.139463 | 6144 | 430 |
| seed:29 | A_interactions_neutral_scored | 0.036857 | 0.130029 | 6144 | 430 |
| seed:29 | A_interactions_oracle | 0.038413 | 0.134704 | 6144 | 430 |
| seed:29 | A_interactions_oracle_neutral_raw | 0.037563 | 0.132348 | 6144 | 430 |
| seed:29 | A_interactions_oracle_neutral_scored | 0.036437 | 0.129195 | 6144 | 430 |
| seed:43 | prior | 0.065101 | 0.253695 | 6144 | 430 |
| seed:43 | A_input | 0.039505 | 0.137826 | 6144 | 430 |
| seed:43 | A_interactions | 0.039317 | 0.136365 | 6144 | 430 |
| seed:43 | A_interactions_neutral_raw | 0.039865 | 0.138098 | 6144 | 430 |
| seed:43 | A_interactions_neutral_scored | 0.036506 | 0.128908 | 6144 | 430 |
| seed:43 | A_interactions_oracle | 0.037805 | 0.132841 | 6144 | 430 |
| seed:43 | A_interactions_oracle_neutral_raw | 0.037067 | 0.131054 | 6144 | 430 |
| seed:43 | A_interactions_oracle_neutral_scored | 0.036029 | 0.127871 | 6144 | 430 |
| ensemble:mean_probability | prior | 0.065153 | 0.254100 | 6144 | 430 |
| ensemble:mean_probability | A_input | 0.039731 | 0.138343 | 6144 | 430 |
| ensemble:mean_probability | A_interactions | 0.039673 | 0.137222 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_neutral_raw | 0.040037 | 0.138487 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_neutral_scored | 0.036599 | 0.129256 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_oracle | 0.038100 | 0.133688 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_oracle_neutral_raw | 0.037215 | 0.131400 | 6144 | 430 |
| ensemble:mean_probability | A_interactions_oracle_neutral_scored | 0.036016 | 0.127793 | 6144 | 430 |

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

Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.
