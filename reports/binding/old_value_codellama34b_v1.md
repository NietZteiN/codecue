# Previous versus current value retrieval calibration

Fresh adaptive historical-versus-current retrieval calibration on familiar literal/copy graphs, using three fixed direct-answer instructions. Previous means the target value immediately before its last assignment, not the current Python output. Old/current questions share their entire body. Equal old/current answers are controls outside the fixed reliability gate. An old numeric value can survive elsewhere or be absent from every final slot; these primary strata remain separate. Literal rereading can solve history questions, so accuracy does not establish maintained neural state or causal use. Related numeric, lexical, rotation and query views are not independent structural replication. No instruction is selected, no new interval is computed, and no causal intervention automatically follows a passing gate. Historical failures and sealed outcomes remain unchanged.

20,160 scored responses; 4,739 correct and 9,864 invalid. Confirmed warm-up requests: 8.

Each instruction × question mode × different-value storage category × split cell requires at least 24 responses and 24 unique prompts, accuracy at least 90%, and invalid rate at most 5%. Equality controls remain separate. All instructions stay visible; a passing gate triggers morning design review only.

| Instruction | Training qualified | DEV descriptive pass | Behavioral calibration qualified |
|---|---|---|---|
| old_value_output_v1 | False | False | False |
| old_value_execute_v1 | False | False | False |
| old_value_history_v1 | False | False | False |

| Instruction | Mode | Old numeric value | Split | Correct / n | Unique prompts | Invalid |
|---|---|---|---|---:|---:|---:|
| old_value_execute_v1 | current | absent_all_current | development | 40/360 | 360 | 291 |
| old_value_execute_v1 | current | absent_all_current | train | 183/1248 | 1248 | 999 |
| old_value_execute_v1 | current | retained_other_current | development | 41/240 | 240 | 186 |
| old_value_execute_v1 | current | retained_other_current | train | 54/576 | 576 | 489 |
| old_value_execute_v1 | previous | absent_all_current | development | 67/360 | 360 | 216 |
| old_value_execute_v1 | previous | absent_all_current | train | 211/1248 | 1248 | 674 |
| old_value_execute_v1 | previous | retained_other_current | development | 38/240 | 240 | 137 |
| old_value_execute_v1 | previous | retained_other_current | train | 95/576 | 576 | 349 |
| old_value_history_v1 | current | absent_all_current | development | 102/360 | 360 | 93 |
| old_value_history_v1 | current | absent_all_current | train | 519/1248 | 1248 | 327 |
| old_value_history_v1 | current | retained_other_current | development | 109/240 | 240 | 64 |
| old_value_history_v1 | current | retained_other_current | train | 148/576 | 576 | 244 |
| old_value_history_v1 | previous | absent_all_current | development | 135/360 | 360 | 0 |
| old_value_history_v1 | previous | absent_all_current | train | 365/1248 | 1248 | 5 |
| old_value_history_v1 | previous | retained_other_current | development | 61/240 | 240 | 0 |
| old_value_history_v1 | previous | retained_other_current | train | 190/576 | 576 | 2 |
| old_value_output_v1 | current | absent_all_current | development | 38/360 | 360 | 286 |
| old_value_output_v1 | current | absent_all_current | train | 198/1248 | 1248 | 986 |
| old_value_output_v1 | current | retained_other_current | development | 45/240 | 240 | 182 |
| old_value_output_v1 | current | retained_other_current | train | 53/576 | 576 | 496 |
| old_value_output_v1 | previous | absent_all_current | development | 89/360 | 360 | 151 |
| old_value_output_v1 | previous | absent_all_current | train | 273/1248 | 1248 | 463 |
| old_value_output_v1 | previous | retained_other_current | development | 54/240 | 240 | 91 |
| old_value_output_v1 | previous | retained_other_current | train | 138/576 | 576 | 245 |
| old_value_execute_v1 | current | equal_current | development | 26/240 | 240 | 210 |
| old_value_execute_v1 | current | equal_current | train | 104/696 | 696 | 579 |
| old_value_execute_v1 | previous | equal_current | development | 56/240 | 240 | 149 |
| old_value_execute_v1 | previous | equal_current | train | 188/696 | 696 | 423 |
| old_value_history_v1 | current | equal_current | development | 56/240 | 240 | 98 |
| old_value_history_v1 | current | equal_current | train | 257/696 | 696 | 259 |
| old_value_history_v1 | previous | equal_current | development | 70/240 | 240 | 0 |
| old_value_history_v1 | previous | equal_current | train | 269/696 | 696 | 2 |
| old_value_output_v1 | current | equal_current | development | 19/240 | 240 | 214 |
| old_value_output_v1 | current | equal_current | train | 93/696 | 696 | 584 |
| old_value_output_v1 | previous | equal_current | development | 83/240 | 240 | 100 |
| old_value_output_v1 | previous | equal_current | train | 272/696 | 696 | 270 |

| Instruction | Split | Old numeric value | Paired n | Previous minus current | Previous answered current | Current answered previous |
|---|---|---|---:|---:|---:|---:|
| old_value_execute_v1 | development | absent_all_current | 360 | 7.500 pp | 63 | 17 |
| old_value_execute_v1 | development | equal_current | 240 | 12.500 pp | 0 | 0 |
| old_value_execute_v1 | development | retained_other_current | 240 | -1.250 pp | 46 | 10 |
| old_value_execute_v1 | train | absent_all_current | 1248 | 2.244 pp | 290 | 40 |
| old_value_execute_v1 | train | equal_current | 696 | 12.069 pp | 0 | 0 |
| old_value_execute_v1 | train | retained_other_current | 576 | 7.118 pp | 78 | 25 |
| old_value_history_v1 | development | absent_all_current | 360 | 9.167 pp | 118 | 98 |
| old_value_history_v1 | development | equal_current | 240 | 5.833 pp | 0 | 0 |
| old_value_history_v1 | development | retained_other_current | 240 | -20.000 pp | 103 | 31 |
| old_value_history_v1 | train | absent_all_current | 1248 | -12.340 pp | 505 | 229 |
| old_value_history_v1 | train | equal_current | 696 | 1.724 pp | 0 | 0 |
| old_value_history_v1 | train | retained_other_current | 576 | 7.292 pp | 129 | 92 |
| old_value_output_v1 | development | absent_all_current | 360 | 14.167 pp | 89 | 22 |
| old_value_output_v1 | development | equal_current | 240 | 26.667 pp | 0 | 0 |
| old_value_output_v1 | development | retained_other_current | 240 | 3.750 pp | 69 | 7 |
| old_value_output_v1 | train | absent_all_current | 1248 | 6.010 pp | 393 | 33 |
| old_value_output_v1 | train | equal_current | 696 | 25.718 pp | 0 | 0 |
| old_value_output_v1 | train | retained_other_current | 576 | 14.757 pp | 111 | 19 |

Current target assignment version is overwrite-count plus 1; previous target assignment version equals overwrite-count. These version cells are retained through question mode and the overwrite-count strata.

All per-graph, owner, overwrite-count, recency, lexical, numeric-seed and profile strata, paired question differences and exact prompt/output token geometry remain in the machine review. Old-value questions can be solved by rereading the visible literals; these results do not establish retained latent state or causal use. No confidence interval or independent-trial claim is assigned to related views.
