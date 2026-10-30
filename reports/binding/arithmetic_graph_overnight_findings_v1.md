# Two-input arithmetic relationship discovery: completed first suite

Both checkpoints completed4,608 captures,1,152 generated answers and18 readout fits. All jobs exited successfully. The table reports the nominated layer at every captured site, averaged across three weighting seeds; no best layer/site is selected. Numeric, lexical and query relatives stay grouped in36 TRAIN /12 DEV structural families.

| Model | Site | Features | Parent accuracy | All eight parents | Value accuracy | Whole state | Direct relations | Value-derived relations |
|---|---|---|---:|---:|---:|---:|---:|---:|
| llama8b | initialization | hidden |  |  | 75.88% | 37.99% | 79.36% | 75.43% |
| llama8b | initialization | source |  |  | 100.00% | 100.00% | 61.35% | 100.00% |
| llama8b | last assignment | hidden | 29.76% | 0.00% | 8.10% | 0.00% | 53.14% | 49.88% |
| llama8b | last assignment | source | 19.99% | 0.00% | 20.57% | 0.46% | 51.11% | 53.10% |
| llama8b | answer preparation | hidden | 24.34% | 0.00% | 15.37% | 0.64% | 54.61% | 54.33% |
| llama8b | answer preparation | source | 22.16% | 0.00% | 20.47% | 0.35% | 50.83% | 52.57% |
| codellama34b | initialization | hidden |  |  | 79.89% | 39.24% | 78.89% | 77.42% |
| codellama34b | initialization | source |  |  | 100.00% | 100.00% | 61.47% | 100.00% |
| codellama34b | last assignment | hidden | 29.08% | 0.00% | 9.20% | 0.00% | 51.93% | 50.19% |
| codellama34b | last assignment | source | 21.05% | 0.00% | 20.60% | 0.46% | 51.62% | 52.49% |
| codellama34b | answer preparation | hidden | 29.39% | 0.00% | 16.23% | 0.06% | 54.04% | 52.02% |
| codellama34b | answer preparation | source | 22.29% | 0.00% | 20.20% | 0.35% | 50.44% | 52.29% |

Direct relation scores are four-family macro balanced accuracies;50% is the constant-prediction reference when both classes exist. Arithmetic-written values and whole graphs are poorly recovered under these global linear readouts. The eight ordered-parent metric is harder than the earlier four-copy-parent task and is not directly comparable. Failure here does not establish representational absence. Source AST tracking and source execution remain100% oracle ceilings; character readouts are a limited source comparator.

| Model | DEV query type | Cases | Correct | Accuracy | Invalid | Families |
|---|---|---:|---:|---:|---:|---:|
| llama8b | all | 288 | 54 | 18.75% | 8 | 12 |
| llama8b | untouched_literal | 72 | 32 | 44.44% | 3 | 9 |
| llama8b | arithmetic_written | 216 | 22 | 10.19% | 5 | 12 |
| codellama34b | all | 288 | 58 | 20.14% | 0 | 12 |
| codellama34b | untouched_literal | 72 | 36 | 50.00% | 0 | 9 |
| codellama34b | arithmetic_written | 216 | 22 | 10.19% | 0 | 12 |

The arithmetic-written and untouched-literal strata were required for interpretation in revision3 before model collection. These are descriptive row accuracies; they do not treat relatives as independent trials or claim new significance. The original full results retain fixed-fit family intervals for graph/value contrasts.

Next decisions: inspect per-operand/version errors before interpreting zero whole-graph accuracy; compare the other archived layers under a separately declared follow-up; evaluate position-conditioned readouts and stronger source parsing controls; seek a reliable computed regime before causal patching or unfamiliar-program forecasts. Preserve these nominated-layer negative findings. Do not turn a layer search into untouched confirmation.

[Plan](arithmetic_graph_overnight_20261029_plan_v3.md) · [Validation](arithmetic_graph_overnight_debug_v1.md) · [Source coverage](arithmetic_graph_source_readiness_v1.md) · [Execution](arithmetic_graph_overnight_20261029_status_v3.md)
