# Previous versus current value retrieval calibration

Fresh adaptive historical-versus-current retrieval calibration on familiar literal/copy graphs, using three fixed direct-answer instructions. Previous means the target value immediately before its last assignment, not the current Python output. Old/current questions share their entire body. Equal old/current answers are controls outside the fixed reliability gate. An old numeric value can survive elsewhere or be absent from every final slot; these primary strata remain separate. Literal rereading can solve history questions, so accuracy does not establish maintained neural state or causal use. Related numeric, lexical, rotation and query views are not independent structural replication. No instruction is selected, no new interval is computed, and no causal intervention automatically follows a passing gate. Historical failures and sealed outcomes remain unchanged.

20,160 scored responses; 12,272 correct and 0 invalid. Confirmed warm-up requests: 8.

Each instruction × question mode × different-value storage category × split cell requires at least 24 responses and 24 unique prompts, accuracy at least 90%, and invalid rate at most 5%. Equality controls remain separate. All instructions stay visible; a passing gate triggers morning design review only.

| Instruction | Training qualified | DEV descriptive pass | Behavioral calibration qualified |
|---|---|---|---|
| old_value_output_v1 | False | False | False |
| old_value_execute_v1 | False | False | False |
| old_value_history_v1 | False | False | False |

| Instruction | Mode | Old numeric value | Split | Correct / n | Unique prompts | Invalid |
|---|---|---|---|---:|---:|---:|
| old_value_execute_v1 | current | absent_all_current | development | 269/360 | 360 | 0 |
| old_value_execute_v1 | current | absent_all_current | train | 1070/1248 | 1248 | 0 |
| old_value_execute_v1 | current | retained_other_current | development | 214/240 | 240 | 0 |
| old_value_execute_v1 | current | retained_other_current | train | 516/576 | 576 | 0 |
| old_value_execute_v1 | previous | absent_all_current | development | 73/360 | 360 | 0 |
| old_value_execute_v1 | previous | absent_all_current | train | 424/1248 | 1248 | 0 |
| old_value_execute_v1 | previous | retained_other_current | development | 123/240 | 240 | 0 |
| old_value_execute_v1 | previous | retained_other_current | train | 264/576 | 576 | 0 |
| old_value_history_v1 | current | absent_all_current | development | 210/360 | 360 | 0 |
| old_value_history_v1 | current | absent_all_current | train | 936/1248 | 1248 | 0 |
| old_value_history_v1 | current | retained_other_current | development | 205/240 | 240 | 0 |
| old_value_history_v1 | current | retained_other_current | train | 478/576 | 576 | 0 |
| old_value_history_v1 | previous | absent_all_current | development | 128/360 | 360 | 0 |
| old_value_history_v1 | previous | absent_all_current | train | 528/1248 | 1248 | 0 |
| old_value_history_v1 | previous | retained_other_current | development | 113/240 | 240 | 0 |
| old_value_history_v1 | previous | retained_other_current | train | 270/576 | 576 | 0 |
| old_value_output_v1 | current | absent_all_current | development | 251/360 | 360 | 0 |
| old_value_output_v1 | current | absent_all_current | train | 1029/1248 | 1248 | 0 |
| old_value_output_v1 | current | retained_other_current | development | 213/240 | 240 | 0 |
| old_value_output_v1 | current | retained_other_current | train | 512/576 | 576 | 0 |
| old_value_output_v1 | previous | absent_all_current | development | 88/360 | 360 | 0 |
| old_value_output_v1 | previous | absent_all_current | train | 496/1248 | 1248 | 0 |
| old_value_output_v1 | previous | retained_other_current | development | 109/240 | 240 | 0 |
| old_value_output_v1 | previous | retained_other_current | train | 243/576 | 576 | 0 |
| old_value_execute_v1 | current | equal_current | development | 188/240 | 240 | 0 |
| old_value_execute_v1 | current | equal_current | train | 579/696 | 696 | 0 |
| old_value_execute_v1 | previous | equal_current | development | 155/240 | 240 | 0 |
| old_value_execute_v1 | previous | equal_current | train | 379/696 | 696 | 0 |
| old_value_history_v1 | current | equal_current | development | 163/240 | 240 | 0 |
| old_value_history_v1 | current | equal_current | train | 523/696 | 696 | 0 |
| old_value_history_v1 | previous | equal_current | development | 115/240 | 240 | 0 |
| old_value_history_v1 | previous | equal_current | train | 268/696 | 696 | 0 |
| old_value_output_v1 | current | equal_current | development | 159/240 | 240 | 0 |
| old_value_output_v1 | current | equal_current | train | 532/696 | 696 | 0 |
| old_value_output_v1 | previous | equal_current | development | 133/240 | 240 | 0 |
| old_value_output_v1 | previous | equal_current | train | 316/696 | 696 | 0 |

| Instruction | Split | Old numeric value | Paired n | Previous minus current | Previous answered current | Current answered previous |
|---|---|---|---:|---:|---:|---:|
| old_value_execute_v1 | development | absent_all_current | 360 | -54.444 pp | 212 | 48 |
| old_value_execute_v1 | development | equal_current | 240 | -13.750 pp | 0 | 0 |
| old_value_execute_v1 | development | retained_other_current | 240 | -37.917 pp | 58 | 18 |
| old_value_execute_v1 | train | absent_all_current | 1248 | -51.763 pp | 537 | 86 |
| old_value_execute_v1 | train | equal_current | 696 | -28.736 pp | 0 | 0 |
| old_value_execute_v1 | train | retained_other_current | 576 | -43.750 pp | 172 | 37 |
| old_value_history_v1 | development | absent_all_current | 360 | -22.778 pp | 146 | 92 |
| old_value_history_v1 | development | equal_current | 240 | -20.000 pp | 0 | 0 |
| old_value_history_v1 | development | retained_other_current | 240 | -38.333 pp | 47 | 17 |
| old_value_history_v1 | train | absent_all_current | 1248 | -32.692 pp | 423 | 184 |
| old_value_history_v1 | train | equal_current | 696 | -36.638 pp | 0 | 0 |
| old_value_history_v1 | train | retained_other_current | 576 | -36.111 pp | 135 | 53 |
| old_value_output_v1 | development | absent_all_current | 360 | -45.278 pp | 192 | 53 |
| old_value_output_v1 | development | equal_current | 240 | -10.833 pp | 0 | 0 |
| old_value_output_v1 | development | retained_other_current | 240 | -43.333 pp | 49 | 16 |
| old_value_output_v1 | train | absent_all_current | 1248 | -42.708 pp | 437 | 97 |
| old_value_output_v1 | train | equal_current | 696 | -31.034 pp | 0 | 0 |
| old_value_output_v1 | train | retained_other_current | 576 | -46.701 pp | 169 | 40 |

Current target assignment version is overwrite-count plus 1; previous target assignment version equals overwrite-count. These version cells are retained through question mode and the overwrite-count strata.

All per-graph, owner, overwrite-count, recency, lexical, numeric-seed and profile strata, paired question differences and exact prompt/output token geometry remain in the machine review. Old-value questions can be solved by rereading the visible literals; these results do not establish retained latent state or causal use. No confidence interval or independent-trial claim is assigned to related views.
