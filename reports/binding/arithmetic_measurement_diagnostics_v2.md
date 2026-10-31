# Exploratory measurement diagnostics

Saved-result analysis only; no fits or model calls. Intervals resample structural families with fitting seeds averaged inside families. Existing DEV is an adaptive discovery cohort; intervals do not correct for earlier selection.

| Model | Contrast / measurement | Mean | Exploratory 95% interval |
|---|---|---:|---:|
| codellama34b | Local hidden minus matched-source parent accuracy | 4.946% | [3.409, 6.427]% |
| codellama34b | Whole state: anchor_query_decoded_values | 0.026% | [0.000, 0.077]% |
| codellama34b | Whole state: predicted_route_oracle_values | 9.208% | [7.047, 11.703]% |
| codellama34b | Whole state: all_bindings_correct | 7.022% | [5.041, 9.285]% |
| codellama34b | Whole state: correct_state_with_wrong_binding | 0.026% | [0.000, 0.077]% |
| codellama34b | Whole state: oracle_route_decoded_values | 0.129% | [0.026, 0.257]% |
| codellama34b | Computed categorical exact: all | 8.702% | [7.442, 10.025]% |
| codellama34b | Computed categorical exact: matches_initial_literal | 12.614% | [10.253, 15.146]% |
| codellama34b | Computed categorical exact: absent_from_initial_literals | 7.463% | [6.089, 8.907]% |
| codellama34b | Computed categorical exact: depth2 | 11.728% | [9.181, 14.352]% |
| codellama34b | Computed categorical exact: depth4 | 8.565% | [6.848, 10.494]% |
| codellama34b | Computed categorical exact: depth6 | 5.813% | [4.887, 6.803]% |

codellama34b: 20844/20844 computed-definition sites coincide with the right-operand token; 19550 ask for a different value. This motivates a temporal-site experiment, not a conclusion that a result cannot be encoded at that token.

| Model | Contrast / measurement | Mean | Exploratory 95% interval |
|---|---|---:|---:|
| llama8b | Local hidden minus matched-source parent accuracy | 9.185% | [7.690, 10.714]% |
| llama8b | Whole state: anchor_query_decoded_values | 0.077% | [0.000, 0.180]% |
| llama8b | Whole state: predicted_route_oracle_values | 8.359% | [6.301, 10.546]% |
| llama8b | Whole state: all_bindings_correct | 5.967% | [4.192, 7.973]% |
| llama8b | Whole state: correct_state_with_wrong_binding | 0.077% | [0.000, 0.180]% |
| llama8b | Whole state: oracle_route_decoded_values | 0.077% | [0.000, 0.180]% |
| llama8b | Computed categorical exact: all | 9.463% | [8.153, 10.818]% |
| llama8b | Computed categorical exact: matches_initial_literal | 13.308% | [10.399, 16.497]% |
| llama8b | Computed categorical exact: absent_from_initial_literals | 8.347% | [7.012, 9.744]% |
| llama8b | Computed categorical exact: depth2 | 12.963% | [10.340, 15.742]% |
| llama8b | Computed categorical exact: depth4 | 9.279% | [7.215, 11.478]% |
| llama8b | Computed categorical exact: depth6 | 6.147% | [5.195, 7.099]% |

llama8b: 20844/20844 computed-definition sites coincide with the right-operand token; 19550 ask for a different value. This motivates a temporal-site experiment, not a conclusion that a result cannot be encoded at that token.
