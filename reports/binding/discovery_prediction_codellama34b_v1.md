# Discovery-only failure prediction: codellama/CodeLlama-34b-Instruct-hf

Exploratory nested grouped cross-validation on previously consumed discovery data, not M5 confirmation or a frozen unfamiliar-program forecast. No mechanism C, confidence or internal measurement feature is fitted. Repeated fold seeds reuse the same data and are not independent replications. Bootstrap intervals condition on the saved OOF predictions and do not rerun feature collection, model fitting or hyperparameter selection. Raw neutral behavior uses one distinct extra query without its oracle correctness; the scored tier additionally requires the neutral reference oracle. Target response properties and correctness never enter features.

6,144 transformed targets, 24 template components, 1454 failures. All target IDs remain in every fixed seed's OOF evaluation.

| Evaluation | Predictor | Brier | Log loss | n | Failures |
|---|---|---:|---:|---:|---:|
| seed:17 | prior | 0.180938 | 0.547986 | 6144 | 1454 |
| seed:17 | A_input | 0.133312 | 0.410162 | 6144 | 1454 |
| seed:17 | A_neutral_raw | 0.133041 | 0.408845 | 6144 | 1454 |
| seed:17 | A_neutral_scored | 0.101802 | 0.317086 | 6144 | 1454 |
| seed:29 | prior | 0.181167 | 0.548633 | 6144 | 1454 |
| seed:29 | A_input | 0.133066 | 0.409310 | 6144 | 1454 |
| seed:29 | A_neutral_raw | 0.133397 | 0.411427 | 6144 | 1454 |
| seed:29 | A_neutral_scored | 0.101933 | 0.316963 | 6144 | 1454 |
| seed:43 | prior | 0.180829 | 0.547689 | 6144 | 1454 |
| seed:43 | A_input | 0.132403 | 0.409566 | 6144 | 1454 |
| seed:43 | A_neutral_raw | 0.131854 | 0.407553 | 6144 | 1454 |
| seed:43 | A_neutral_scored | 0.101500 | 0.316274 | 6144 | 1454 |
| ensemble:mean_probability | prior | 0.180960 | 0.548053 | 6144 | 1454 |
| ensemble:mean_probability | A_input | 0.132585 | 0.408816 | 6144 | 1454 |
| ensemble:mean_probability | A_neutral_raw | 0.132397 | 0.408188 | 6144 | 1454 |
| ensemble:mean_probability | A_neutral_scored | 0.101568 | 0.316216 | 6144 | 1454 |

## All paired template-bootstrap improvements

Positive loss(left) − loss(right) favors the right predictor. These are conditional exploratory intervals with no refitting or multiplicity adjustment.

| Evaluation | Left baseline | Right predictor | Brier improvement [95%] | Log-loss improvement [95%] |
|---|---|---|---|---|
| seed:17 | prior | A_input | +0.047625 [+0.033718, +0.061716] | +0.137823 [+0.107712, +0.168297] |
| seed:17 | prior | A_neutral_raw | +0.047897 [+0.033960, +0.061974] | +0.139141 [+0.108893, +0.170322] |
| seed:17 | prior | A_neutral_scored | +0.079136 [+0.062346, +0.095046] | +0.230900 [+0.193124, +0.266629] |
| seed:17 | A_input | A_neutral_raw | +0.000272 [-0.000971, +0.001482] | +0.001317 [-0.002248, +0.004819] |
| seed:17 | A_input | A_neutral_scored | +0.031510 [+0.024640, +0.038534] | +0.093076 [+0.074642, +0.111380] |
| seed:17 | A_neutral_raw | A_neutral_scored | +0.031239 [+0.024345, +0.037884] | +0.091759 [+0.073191, +0.109425] |
| seed:29 | prior | A_input | +0.048101 [+0.033731, +0.062435] | +0.139323 [+0.107927, +0.170934] |
| seed:29 | prior | A_neutral_raw | +0.047770 [+0.034137, +0.061417] | +0.137206 [+0.107187, +0.167919] |
| seed:29 | prior | A_neutral_scored | +0.079234 [+0.061974, +0.095608] | +0.231670 [+0.195378, +0.267060] |
| seed:29 | A_input | A_neutral_raw | -0.000331 [-0.001868, +0.001415] | -0.002116 [-0.006542, +0.002326] |
| seed:29 | A_input | A_neutral_scored | +0.031134 [+0.024660, +0.037989] | +0.092347 [+0.074940, +0.110401] |
| seed:29 | A_neutral_raw | A_neutral_scored | +0.031465 [+0.024550, +0.038182] | +0.094464 [+0.076769, +0.111805] |
| seed:43 | prior | A_input | +0.048426 [+0.034920, +0.061588] | +0.138123 [+0.109077, +0.166437] |
| seed:43 | prior | A_neutral_raw | +0.048975 [+0.035649, +0.062241] | +0.140137 [+0.111563, +0.169212] |
| seed:43 | prior | A_neutral_scored | +0.079329 [+0.062644, +0.095067] | +0.231415 [+0.194795, +0.266364] |
| seed:43 | A_input | A_neutral_raw | +0.000548 [-0.000504, +0.001524] | +0.002014 [-0.001482, +0.005608] |
| seed:43 | A_input | A_neutral_scored | +0.030903 [+0.024045, +0.038093] | +0.093293 [+0.074397, +0.112902] |
| seed:43 | A_neutral_raw | A_neutral_scored | +0.030354 [+0.023627, +0.037224] | +0.091279 [+0.073326, +0.108945] |
| ensemble:mean_probability | prior | A_input | +0.048375 [+0.034307, +0.062247] | +0.139238 [+0.109210, +0.169413] |
| ensemble:mean_probability | prior | A_neutral_raw | +0.048563 [+0.034940, +0.062261] | +0.139865 [+0.110263, +0.170296] |
| ensemble:mean_probability | prior | A_neutral_scored | +0.079392 [+0.062438, +0.095433] | +0.231837 [+0.195399, +0.267553] |
| ensemble:mean_probability | A_input | A_neutral_raw | +0.000188 [-0.001003, +0.001409] | +0.000628 [-0.002797, +0.003862] |
| ensemble:mean_probability | A_input | A_neutral_scored | +0.031017 [+0.024468, +0.037954] | +0.092600 [+0.074598, +0.110826] |
| ensemble:mean_probability | A_neutral_raw | A_neutral_scored | +0.030829 [+0.023979, +0.037513] | +0.091972 [+0.074045, +0.109148] |

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
| seed:17 | A_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.121272 | 0.378554 |
| seed:17 | A_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.144809 | 0.439136 |
| seed:17 | A_neutral_raw | condition | informative | 3072 | 431 | 0.112734 | 0.356532 |
| seed:17 | A_neutral_raw | condition | misleading | 3072 | 1023 | 0.153347 | 0.461159 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014785 | 0.070089 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048592 | 0.186780 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.048227 | 0.171096 |
| seed:17 | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053036 | 0.188889 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.154873 | 0.483958 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.130024 | 0.436179 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.218432 | 0.627700 |
| seed:17 | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.223998 | 0.642717 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.048419 | 0.186038 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.081876 | 0.272953 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.152095 | 0.465348 |
| seed:17 | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.082224 | 0.289778 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.243679 | 0.676435 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.236261 | 0.667154 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.163387 | 0.507556 |
| seed:17 | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.219397 | 0.632127 |
| seed:17 | A_neutral_raw | original_split | development | 1536 | 374 | 0.125471 | 0.383728 |
| seed:17 | A_neutral_raw | original_split | train | 4608 | 1080 | 0.135564 | 0.417217 |
| seed:17 | A_neutral_raw | query_role | current | 3072 | 236 | 0.063538 | 0.224207 |
| seed:17 | A_neutral_raw | query_role | saved | 3072 | 1218 | 0.202543 | 0.593483 |
| seed:17 | A_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.088456 | 0.278167 |
| seed:17 | A_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.115147 | 0.356005 |
| seed:17 | A_neutral_scored | condition | informative | 3072 | 431 | 0.088318 | 0.273560 |
| seed:17 | A_neutral_scored | condition | misleading | 3072 | 1023 | 0.115285 | 0.360612 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014845 | 0.067871 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040626 | 0.143895 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.032565 | 0.113364 |
| seed:17 | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.043705 | 0.150462 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.110527 | 0.338933 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.103103 | 0.311659 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.169070 | 0.499608 |
| seed:17 | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.174763 | 0.512868 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.032500 | 0.128643 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.047665 | 0.155776 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.131689 | 0.416752 |
| seed:17 | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.063051 | 0.227747 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.151668 | 0.468847 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.184575 | 0.555527 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.125936 | 0.391994 |
| seed:17 | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.179335 | 0.533402 |
| seed:17 | A_neutral_scored | original_split | development | 1536 | 374 | 0.089862 | 0.285859 |
| seed:17 | A_neutral_scored | original_split | train | 4608 | 1080 | 0.105782 | 0.327495 |
| seed:17 | A_neutral_scored | query_role | current | 3072 | 236 | 0.047745 | 0.167203 |
| seed:17 | A_neutral_scored | query_role | saved | 3072 | 1218 | 0.155858 | 0.466969 |
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
| seed:29 | A_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.121888 | 0.380763 |
| seed:29 | A_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.144907 | 0.442091 |
| seed:29 | A_neutral_raw | condition | informative | 3072 | 431 | 0.112872 | 0.357624 |
| seed:29 | A_neutral_raw | condition | misleading | 3072 | 1023 | 0.153923 | 0.465229 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014843 | 0.070569 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048477 | 0.185116 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.048459 | 0.172992 |
| seed:29 | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053501 | 0.193394 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.153793 | 0.481052 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.132125 | 0.442819 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.222211 | 0.635831 |
| seed:29 | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.222214 | 0.638441 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.047839 | 0.182926 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.082461 | 0.280294 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.155075 | 0.502091 |
| seed:29 | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.083062 | 0.295492 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.242018 | 0.672982 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.239018 | 0.672581 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.173878 | 0.534878 |
| seed:29 | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.216851 | 0.625550 |
| seed:29 | A_neutral_raw | original_split | development | 1536 | 374 | 0.126384 | 0.388404 |
| seed:29 | A_neutral_raw | original_split | train | 4608 | 1080 | 0.135735 | 0.419101 |
| seed:29 | A_neutral_raw | query_role | current | 3072 | 236 | 0.063978 | 0.228673 |
| seed:29 | A_neutral_raw | query_role | saved | 3072 | 1218 | 0.202817 | 0.594181 |
| seed:29 | A_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.089135 | 0.279085 |
| seed:29 | A_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.114730 | 0.354841 |
| seed:29 | A_neutral_scored | condition | informative | 3072 | 431 | 0.088345 | 0.273136 |
| seed:29 | A_neutral_scored | condition | misleading | 3072 | 1023 | 0.115520 | 0.360790 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014687 | 0.067544 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040479 | 0.139950 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.034151 | 0.119863 |
| seed:29 | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.043721 | 0.150476 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.109643 | 0.337146 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.104847 | 0.315482 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.171475 | 0.505458 |
| seed:29 | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.173220 | 0.509290 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.031970 | 0.127135 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.048438 | 0.159659 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.125249 | 0.399099 |
| seed:29 | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.063077 | 0.226798 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.149260 | 0.462091 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.188268 | 0.562463 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.127300 | 0.395892 |
| seed:29 | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.179051 | 0.532609 |
| seed:29 | A_neutral_scored | original_split | development | 1536 | 374 | 0.089108 | 0.284012 |
| seed:29 | A_neutral_scored | original_split | train | 4608 | 1080 | 0.106207 | 0.327947 |
| seed:29 | A_neutral_scored | query_role | current | 3072 | 236 | 0.047599 | 0.166380 |
| seed:29 | A_neutral_scored | query_role | saved | 3072 | 1218 | 0.156266 | 0.467546 |
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
| seed:43 | A_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.119352 | 0.374269 |
| seed:43 | A_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.144357 | 0.440836 |
| seed:43 | A_neutral_raw | condition | informative | 3072 | 431 | 0.111405 | 0.353917 |
| seed:43 | A_neutral_raw | condition | misleading | 3072 | 1023 | 0.152304 | 0.461188 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014910 | 0.072952 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048627 | 0.187253 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.049409 | 0.176510 |
| seed:43 | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053661 | 0.194143 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.152901 | 0.478704 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.127233 | 0.426591 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.218819 | 0.628681 |
| seed:43 | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.219623 | 0.631885 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.047978 | 0.187759 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.081132 | 0.270985 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.159277 | 0.515812 |
| seed:43 | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.084408 | 0.296845 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.238964 | 0.667446 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.231743 | 0.657356 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.179525 | 0.547752 |
| seed:43 | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.213816 | 0.619389 |
| seed:43 | A_neutral_raw | original_split | development | 1536 | 374 | 0.126378 | 0.390206 |
| seed:43 | A_neutral_raw | original_split | train | 4608 | 1080 | 0.133680 | 0.413335 |
| seed:43 | A_neutral_raw | query_role | current | 3072 | 236 | 0.064327 | 0.229235 |
| seed:43 | A_neutral_raw | query_role | saved | 3072 | 1218 | 0.199382 | 0.585870 |
| seed:43 | A_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.087730 | 0.275919 |
| seed:43 | A_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.115271 | 0.356628 |
| seed:43 | A_neutral_scored | condition | informative | 3072 | 431 | 0.088993 | 0.274901 |
| seed:43 | A_neutral_scored | condition | misleading | 3072 | 1023 | 0.114007 | 0.357647 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014617 | 0.066357 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.041250 | 0.143549 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.034808 | 0.121948 |
| seed:43 | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.044012 | 0.151117 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.109566 | 0.338654 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.102813 | 0.309952 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.169761 | 0.500279 |
| seed:43 | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.177316 | 0.519156 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.031356 | 0.127942 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.048054 | 0.156367 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.130863 | 0.423679 |
| seed:43 | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.063295 | 0.228793 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.150817 | 0.465785 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.181082 | 0.546276 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.127216 | 0.398812 |
| seed:43 | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.176147 | 0.523807 |
| seed:43 | A_neutral_scored | original_split | development | 1536 | 374 | 0.089613 | 0.286850 |
| seed:43 | A_neutral_scored | original_split | train | 4608 | 1080 | 0.105462 | 0.326082 |
| seed:43 | A_neutral_scored | query_role | current | 3072 | 236 | 0.047974 | 0.168060 |
| seed:43 | A_neutral_scored | query_role | saved | 3072 | 1218 | 0.155027 | 0.464487 |
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
| ensemble:mean_probability | A_neutral_raw | available_bindings | 2 | 3072 | 519 | 0.120584 | 0.376947 |
| ensemble:mean_probability | A_neutral_raw | available_bindings | 4 | 3072 | 935 | 0.144210 | 0.439429 |
| ensemble:mean_probability | A_neutral_raw | condition | informative | 3072 | 431 | 0.112119 | 0.355329 |
| ensemble:mean_probability | A_neutral_raw | condition | misleading | 3072 | 1023 | 0.152675 | 0.461047 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014816 | 0.071143 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.048542 | 0.185964 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.048496 | 0.172819 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.053304 | 0.191876 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.153611 | 0.480491 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.129486 | 0.433816 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.219365 | 0.629839 |
| ensemble:mean_probability | A_neutral_raw | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.221499 | 0.636693 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.047870 | 0.185356 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.081650 | 0.273276 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.154193 | 0.487498 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.082644 | 0.292754 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.240852 | 0.670765 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.235250 | 0.664746 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.171059 | 0.527481 |
| ensemble:mean_probability | A_neutral_raw | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.216138 | 0.624410 |
| ensemble:mean_probability | A_neutral_raw | original_split | development | 1536 | 374 | 0.125618 | 0.386095 |
| ensemble:mean_probability | A_neutral_raw | original_split | train | 4608 | 1080 | 0.134657 | 0.415552 |
| ensemble:mean_probability | A_neutral_raw | query_role | current | 3072 | 236 | 0.063690 | 0.226393 |
| ensemble:mean_probability | A_neutral_raw | query_role | saved | 3072 | 1218 | 0.201103 | 0.589983 |
| ensemble:mean_probability | A_neutral_scored | available_bindings | 2 | 3072 | 519 | 0.088291 | 0.277217 |
| ensemble:mean_probability | A_neutral_scored | available_bindings | 4 | 3072 | 935 | 0.114845 | 0.355214 |
| ensemble:mean_probability | A_neutral_scored | condition | informative | 3072 | 431 | 0.088394 | 0.273408 |
| ensemble:mean_probability | A_neutral_scored | condition | misleading | 3072 | 1023 | 0.114742 | 0.359024 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 2, "development"] | 256 | 4 | 0.014680 | 0.067132 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 2, "train"] | 512 | 27 | 0.040764 | 0.142145 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 4, "development"] | 128 | 8 | 0.033709 | 0.118006 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "current", 4, "train"] | 640 | 40 | 0.043769 | 0.150518 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 2, "development"] | 256 | 49 | 0.109683 | 0.337755 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 2, "train"] | 512 | 75 | 0.103415 | 0.311880 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 4, "development"] | 128 | 45 | 0.169686 | 0.500817 |
| ensemble:mean_probability | A_neutral_scored | joint | ["informative", "saved", 4, "train"] | 640 | 183 | 0.174755 | 0.512901 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 2, "development"] | 256 | 14 | 0.031829 | 0.127640 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 2, "train"] | 512 | 52 | 0.047947 | 0.156935 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 4, "development"] | 128 | 26 | 0.128887 | 0.411547 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "current", 4, "train"] | 640 | 65 | 0.063043 | 0.227375 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 2, "development"] | 256 | 122 | 0.150351 | 0.464975 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 2, "train"] | 512 | 176 | 0.184348 | 0.553593 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 4, "development"] | 128 | 106 | 0.126316 | 0.394596 |
| ensemble:mean_probability | A_neutral_scored | joint | ["misleading", "saved", 4, "train"] | 640 | 462 | 0.177968 | 0.529242 |
| ensemble:mean_probability | A_neutral_scored | original_split | development | 1536 | 374 | 0.089307 | 0.284997 |
| ensemble:mean_probability | A_neutral_scored | original_split | train | 4608 | 1080 | 0.105655 | 0.326622 |
| ensemble:mean_probability | A_neutral_scored | query_role | current | 3072 | 236 | 0.047688 | 0.166870 |
| ensemble:mean_probability | A_neutral_scored | query_role | saved | 3072 | 1218 | 0.155447 | 0.465562 |

Every fallback, inner validation curve, training normalizer and fitted weight is retained separately in fold_fits.json. Single-class training uses a Jeffreys prior; failed convergence raises visibly and never drops a template.
