# Discovery-only failure prediction: meta-llama/Llama-3.1-8B-Instruct

Exploratory nested grouped cross-validation on previously consumed discovery data, not M5 confirmation or a frozen unfamiliar-program forecast. No mechanism C, confidence or internal measurement feature is fitted. Repeated fold seeds reuse the same data and are not independent replications. Bootstrap intervals condition on the saved OOF predictions and do not rerun feature collection, model fitting or hyperparameter selection. Raw neutral behavior uses one distinct extra query without its oracle correctness; the scored tier additionally requires the neutral reference oracle. Target response properties and correctness never enter features.

6,144 transformed targets, 24 template components, 430 failures. All target IDs remain in every fixed seed's OOF evaluation.

| Evaluation | Predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| seed:17 | prior | 0.065185 | 0.254365 | 6144 | 430 |
| seed:17 | A_input | 0.040056 | 0.139188 | 6144 | 430 |
| seed:17 | A_neutral_raw | 0.040346 | 0.140086 | 6144 | 430 |
| seed:17 | A_neutral_scored | 0.036803 | 0.130478 | 6144 | 430 |
| seed:29 | prior | 0.065182 | 0.254318 | 6144 | 430 |
| seed:29 | A_input | 0.039799 | 0.138643 | 6144 | 430 |
| seed:29 | A_neutral_raw | 0.040311 | 0.139953 | 6144 | 430 |
| seed:29 | A_neutral_scored | 0.036811 | 0.130698 | 6144 | 430 |
| seed:43 | prior | 0.065101 | 0.253695 | 6144 | 430 |
| seed:43 | A_input | 0.039505 | 0.137826 | 6144 | 430 |
| seed:43 | A_neutral_raw | 0.040118 | 0.139769 | 6144 | 430 |
| seed:43 | A_neutral_scored | 0.036788 | 0.130084 | 6144 | 430 |
| ensemble:mean_probability | prior | 0.065153 | 0.254100 | 6144 | 430 |
| ensemble:mean_probability | A_input | 0.039731 | 0.138343 | 6144 | 430 |
| ensemble:mean_probability | A_neutral_raw | 0.040188 | 0.139721 | 6144 | 430 |
| ensemble:mean_probability | A_neutral_scored | 0.036727 | 0.130138 | 6144 | 430 |

## All paired template-bootstrap improvements

Positive loss(left) − loss(right) favors the right predictor. These are conditional exploratory intervals with no refitting or multiplicity adjustment.

| Evaluation | Left baseline | Right predictor | Brier improvement [95%] | Log-loss improvement [95%] |
|---|---|---|---|---|
| seed:17 | prior | A_input | +0.025130 [+0.019033, +0.031386] | +0.115177 [+0.094567, +0.135065] |
| seed:17 | prior | A_neutral_raw | +0.024840 [+0.018932, +0.030729] | +0.114279 [+0.094441, +0.133582] |
| seed:17 | prior | A_neutral_scored | +0.028383 [+0.022272, +0.034482] | +0.123887 [+0.104256, +0.143001] |
| seed:17 | A_input | A_neutral_raw | -0.000290 [-0.000844, +0.000252] | -0.000899 [-0.002190, +0.000393] |
| seed:17 | A_input | A_neutral_scored | +0.003253 [+0.000756, +0.005812] | +0.008710 [+0.002744, +0.014538] |
| seed:17 | A_neutral_raw | A_neutral_scored | +0.003543 [+0.001087, +0.006231] | +0.009608 [+0.003598, +0.015782] |
| seed:29 | prior | A_input | +0.025383 [+0.019258, +0.031745] | +0.115675 [+0.095257, +0.136205] |
| seed:29 | prior | A_neutral_raw | +0.024871 [+0.018919, +0.030944] | +0.114365 [+0.094954, +0.134024] |
| seed:29 | prior | A_neutral_scored | +0.028372 [+0.022329, +0.034481] | +0.123620 [+0.104449, +0.142487] |
| seed:29 | A_input | A_neutral_raw | -0.000512 [-0.001170, +0.000072] | -0.001310 [-0.002834, +0.000131] |
| seed:29 | A_input | A_neutral_scored | +0.002989 [+0.000428, +0.005605] | +0.007944 [+0.002116, +0.013826] |
| seed:29 | A_neutral_raw | A_neutral_scored | +0.003500 [+0.000994, +0.006171] | +0.009255 [+0.003322, +0.015327] |
| seed:43 | prior | A_input | +0.025595 [+0.019466, +0.031847] | +0.115869 [+0.095557, +0.135452] |
| seed:43 | prior | A_neutral_raw | +0.024983 [+0.018947, +0.031107] | +0.113926 [+0.094412, +0.133150] |
| seed:43 | prior | A_neutral_scored | +0.028313 [+0.022456, +0.034263] | +0.123611 [+0.104776, +0.142106] |
| seed:43 | A_input | A_neutral_raw | -0.000612 [-0.001276, -0.000015] | -0.001943 [-0.003560, -0.000481] |
| seed:43 | A_input | A_neutral_scored | +0.002718 [+0.000412, +0.005014] | +0.007742 [+0.002582, +0.012727] |
| seed:43 | A_neutral_raw | A_neutral_scored | +0.003330 [+0.001000, +0.005699] | +0.009684 [+0.004253, +0.015074] |
| ensemble:mean_probability | prior | A_input | +0.025422 [+0.019283, +0.031704] | +0.115758 [+0.095231, +0.135725] |
| ensemble:mean_probability | prior | A_neutral_raw | +0.024965 [+0.018991, +0.031008] | +0.114380 [+0.094925, +0.133618] |
| ensemble:mean_probability | prior | A_neutral_scored | +0.028426 [+0.022395, +0.034412] | +0.123962 [+0.104820, +0.142593] |
| ensemble:mean_probability | A_input | A_neutral_raw | -0.000458 [-0.001061, +0.000084] | -0.001378 [-0.002739, -0.000065] |
| ensemble:mean_probability | A_input | A_neutral_scored | +0.003003 [+0.000565, +0.005517] | +0.008204 [+0.002640, +0.013660] |
| ensemble:mean_probability | A_neutral_raw | A_neutral_scored | +0.003461 [+0.001071, +0.006029] | +0.009583 [+0.003781, +0.015363] |

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
| seed:17 | A_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040613 | 0.141244 |
| seed:17 | A_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.040079 | 0.138929 |
| seed:17 | A_neutral_raw | condition | informative | 3072 | 239 | 0.038364 | 0.129441 |
| seed:17 | A_neutral_raw | condition | misleading | 3072 | 191 | 0.042327 | 0.150732 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065283 | 0.199843 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082781 | 0.264125 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.077094 | 0.247163 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.074548 | 0.256905 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000069 | 0.005174 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001947 | 0.013247 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000141 | 0.007656 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000231 | 0.009544 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.069369 | 0.214354 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.070320 | 0.230821 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075293 | 0.225322 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079377 | 0.262170 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003943 | 0.039894 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019295 | 0.109639 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000068 | 0.005265 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007705 | 0.041157 |
| seed:17 | A_neutral_raw | original_split | development | 1536 | 86 | 0.035827 | 0.116995 |
| seed:17 | A_neutral_raw | original_split | train | 4608 | 344 | 0.041852 | 0.147784 |
| seed:17 | A_neutral_raw | query_role | current | 3072 | 413 | 0.075155 | 0.244835 |
| seed:17 | A_neutral_raw | query_role | saved | 3072 | 17 | 0.005537 | 0.035338 |
| seed:17 | A_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034349 | 0.124956 |
| seed:17 | A_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.039257 | 0.136001 |
| seed:17 | A_neutral_scored | condition | informative | 3072 | 239 | 0.032802 | 0.114104 |
| seed:17 | A_neutral_scored | condition | misleading | 3072 | 191 | 0.040804 | 0.146853 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.043511 | 0.148846 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.067780 | 0.224139 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.065573 | 0.212541 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.070894 | 0.242805 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000065 | 0.005392 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001966 | 0.014104 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000089 | 0.006139 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000194 | 0.008867 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.054257 | 0.175463 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.066133 | 0.217874 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.075384 | 0.230653 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081406 | 0.268796 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003938 | 0.038592 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019327 | 0.109471 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000039 | 0.003996 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007724 | 0.041669 |
| seed:17 | A_neutral_scored | original_split | development | 1536 | 86 | 0.028719 | 0.099160 |
| seed:17 | A_neutral_scored | original_split | train | 4608 | 344 | 0.039498 | 0.140918 |
| seed:17 | A_neutral_scored | query_role | current | 3072 | 413 | 0.068069 | 0.225745 |
| seed:17 | A_neutral_scored | query_role | saved | 3072 | 17 | 0.005537 | 0.035212 |
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
| seed:29 | A_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040365 | 0.140812 |
| seed:29 | A_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.040257 | 0.139094 |
| seed:29 | A_neutral_raw | condition | informative | 3072 | 239 | 0.038180 | 0.129030 |
| seed:29 | A_neutral_raw | condition | misleading | 3072 | 191 | 0.042443 | 0.150877 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065020 | 0.199228 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082098 | 0.262425 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.072771 | 0.235859 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075158 | 0.258483 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000071 | 0.005363 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001956 | 0.013284 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000148 | 0.007856 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000240 | 0.009713 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.070586 | 0.219310 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.069063 | 0.227643 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072500 | 0.217882 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081029 | 0.264960 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003944 | 0.038926 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019264 | 0.110106 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000079 | 0.005715 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007707 | 0.041034 |
| seed:29 | A_neutral_raw | original_split | development | 1536 | 86 | 0.035395 | 0.116080 |
| seed:29 | A_neutral_raw | original_split | train | 4608 | 344 | 0.041950 | 0.147911 |
| seed:29 | A_neutral_raw | query_role | current | 3072 | 413 | 0.075086 | 0.244513 |
| seed:29 | A_neutral_raw | query_role | saved | 3072 | 17 | 0.005536 | 0.035393 |
| seed:29 | A_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034040 | 0.124650 |
| seed:29 | A_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.039582 | 0.136747 |
| seed:29 | A_neutral_scored | condition | informative | 3072 | 239 | 0.032623 | 0.113862 |
| seed:29 | A_neutral_scored | condition | misleading | 3072 | 191 | 0.040999 | 0.147535 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.043818 | 0.149909 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.066684 | 0.221291 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.061060 | 0.201939 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071659 | 0.245012 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000075 | 0.005844 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001972 | 0.014048 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000111 | 0.007016 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000214 | 0.009162 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055121 | 0.180008 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.064782 | 0.214955 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.069378 | 0.214737 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.084265 | 0.274738 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003943 | 0.037721 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019323 | 0.110864 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000056 | 0.004938 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007733 | 0.041747 |
| seed:29 | A_neutral_scored | original_split | development | 1536 | 86 | 0.028043 | 0.097966 |
| seed:29 | A_neutral_scored | original_split | train | 4608 | 344 | 0.039733 | 0.141609 |
| seed:29 | A_neutral_scored | query_role | current | 3072 | 413 | 0.068075 | 0.225844 |
| seed:29 | A_neutral_scored | query_role | saved | 3072 | 17 | 0.005546 | 0.035553 |
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
| seed:43 | A_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040166 | 0.140557 |
| seed:43 | A_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.040069 | 0.138981 |
| seed:43 | A_neutral_raw | condition | informative | 3072 | 239 | 0.038683 | 0.130720 |
| seed:43 | A_neutral_raw | condition | misleading | 3072 | 191 | 0.041553 | 0.148817 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065050 | 0.199951 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.083281 | 0.266786 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.078426 | 0.250480 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.075490 | 0.259863 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000096 | 0.006191 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001947 | 0.013077 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000194 | 0.008818 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000221 | 0.009387 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.068441 | 0.212037 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.067724 | 0.226285 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.073142 | 0.221578 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.078532 | 0.259048 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003951 | 0.037121 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019276 | 0.109541 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000094 | 0.006102 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007719 | 0.041415 |
| seed:43 | A_neutral_raw | original_split | development | 1536 | 86 | 0.035578 | 0.116465 |
| seed:43 | A_neutral_raw | original_split | train | 4608 | 344 | 0.041631 | 0.147537 |
| seed:43 | A_neutral_raw | query_role | current | 3072 | 413 | 0.074695 | 0.244286 |
| seed:43 | A_neutral_raw | query_role | saved | 3072 | 17 | 0.005541 | 0.035251 |
| seed:43 | A_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034453 | 0.125112 |
| seed:43 | A_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.039123 | 0.135057 |
| seed:43 | A_neutral_scored | condition | informative | 3072 | 239 | 0.033175 | 0.115263 |
| seed:43 | A_neutral_scored | condition | misleading | 3072 | 191 | 0.040400 | 0.144906 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.045226 | 0.153836 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.068152 | 0.225203 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.066711 | 0.215186 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071468 | 0.244548 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000092 | 0.006407 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001968 | 0.013932 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000131 | 0.007197 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000184 | 0.008832 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.055315 | 0.178009 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065004 | 0.215706 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.073088 | 0.222635 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.080420 | 0.263203 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003944 | 0.035902 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019305 | 0.108755 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000056 | 0.004735 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007722 | 0.041739 |
| seed:43 | A_neutral_scored | original_split | development | 1536 | 86 | 0.029095 | 0.099838 |
| seed:43 | A_neutral_scored | original_split | train | 4608 | 344 | 0.039352 | 0.140166 |
| seed:43 | A_neutral_scored | query_role | current | 3072 | 413 | 0.068039 | 0.225163 |
| seed:43 | A_neutral_scored | query_role | saved | 3072 | 17 | 0.005537 | 0.035006 |
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
| ensemble:mean_probability | A_neutral_raw | available_bindings | 2 | 3072 | 185 | 0.040319 | 0.140640 |
| ensemble:mean_probability | A_neutral_raw | available_bindings | 4 | 3072 | 245 | 0.040058 | 0.138801 |
| ensemble:mean_probability | A_neutral_raw | condition | informative | 3072 | 239 | 0.038339 | 0.129552 |
| ensemble:mean_probability | A_neutral_raw | condition | misleading | 3072 | 191 | 0.042038 | 0.149890 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.065005 | 0.199395 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.082597 | 0.264095 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.075884 | 0.243898 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.074919 | 0.258079 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000077 | 0.005575 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001949 | 0.013196 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000159 | 0.008109 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000228 | 0.009547 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.069361 | 0.214821 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.068896 | 0.227893 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.073457 | 0.221130 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.079504 | 0.261680 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003945 | 0.038407 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019277 | 0.109560 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000079 | 0.005694 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007709 | 0.041173 |
| ensemble:mean_probability | A_neutral_raw | original_split | development | 1536 | 86 | 0.035530 | 0.116269 |
| ensemble:mean_probability | A_neutral_raw | original_split | train | 4608 | 344 | 0.041741 | 0.147538 |
| ensemble:mean_probability | A_neutral_raw | query_role | current | 3072 | 413 | 0.074840 | 0.244175 |
| ensemble:mean_probability | A_neutral_raw | query_role | saved | 3072 | 17 | 0.005536 | 0.035266 |
| ensemble:mean_probability | A_neutral_scored | available_bindings | 2 | 3072 | 185 | 0.034219 | 0.124655 |
| ensemble:mean_probability | A_neutral_scored | available_bindings | 4 | 3072 | 245 | 0.039236 | 0.135621 |
| ensemble:mean_probability | A_neutral_scored | condition | informative | 3072 | 239 | 0.032794 | 0.114181 |
| ensemble:mean_probability | A_neutral_scored | condition | misleading | 3072 | 191 | 0.040661 | 0.146095 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 23 | 0.044061 | 0.150625 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 74 | 0.067420 | 0.223093 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 20 | 0.064297 | 0.209247 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 121 | 0.071172 | 0.243617 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 0 | 0.000075 | 0.005880 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 1 | 0.001966 | 0.014020 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 0 | 0.000108 | 0.006783 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 0 | 0.000194 | 0.008952 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 23 | 0.054768 | 0.177440 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 53 | 0.065188 | 0.215774 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 19 | 0.072412 | 0.221784 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 80 | 0.081868 | 0.268243 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 1 | 0.003941 | 0.037188 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 10 | 0.019317 | 0.109475 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 0 | 0.000049 | 0.004556 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 5 | 0.007724 | 0.041697 |
| ensemble:mean_probability | A_neutral_scored | original_split | development | 1536 | 86 | 0.028546 | 0.098720 |
| ensemble:mean_probability | A_neutral_scored | original_split | train | 4608 | 344 | 0.039454 | 0.140611 |
| ensemble:mean_probability | A_neutral_scored | query_role | current | 3072 | 413 | 0.067917 | 0.225080 |
| ensemble:mean_probability | A_neutral_scored | query_role | saved | 3072 | 17 | 0.005538 | 0.035196 |

Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.
