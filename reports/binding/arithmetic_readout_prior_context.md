# Prior arithmetic capacity context

Post-hoc description of previously consumed training/numeric-development data. These values, signs, forms, operand range and data-generation rules differ from the new arithmetic/readout bank. This comparison cannot isolate an effect of two versus three operations or establish a causal mechanism. Trace prompting also changes computation and generation allowance. Historical gates are unchanged; no original final/extrapolation outcomes or new model responses are used.

This analysis reproduces the already completed two-operation arithmetic-form section. Its 192 distinct sources comprise four forms, two first-operator labels, three output signs and training/development splits. Every source has two syntactic binary operations. In the independent form the first computed assignment is dead for the final answer; the second expression substitutes an oracle intermediate literal. The operator column labels the first operation only. Signs here describe the expected output; the new study also stratifies intermediate signs.

| Checkpoint | Protocol | Correct / n | Invalid | Unique sources |
|---|---|---:|---:|---:|
| llama31_8b | print_direct_v3 | 163/192 | 1 | 192 |
| llama31_8b | print_trace_long_v1 | 176/192 | 0 | 192 |
| codellama34b | print_direct_v3 | 57/192 | 0 | 192 |
| codellama34b | print_trace_long_v1 | 148/192 | 0 | 192 |

## Complete prior cells

Each cell contains four numeric cases. Exact source uniqueness does not make repeated structures independent replications. These are descriptive counts without hypothesis selection or inferential intervals.

| Checkpoint | Protocol | Form | First operator | Output sign | Split | Correct / n | Invalid | Unique sources |
|---|---|---|---|---:|---|---:|---:|---:|
| llama31_8b | print_direct_v3 | assignment | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | + | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | + | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | + | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | + | +1 | development | 3/4 | 1 | 4 |
| llama31_8b | print_direct_v3 | assignment | + | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | - | -1 | development | 2/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | - | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | - | +0 | development | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | - | +0 | train | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | - | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | assignment | - | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | + | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | + | +0 | development | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | + | +0 | train | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | + | +1 | development | 0/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | + | +1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | - | -1 | development | 1/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | - | -1 | train | 2/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | - | +0 | development | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | - | +0 | train | 2/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | - | +1 | development | 2/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | dependent | - | +1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | + | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | + | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | + | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | + | +1 | development | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | + | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | - | -1 | development | 2/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | - | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | - | +0 | development | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | - | +0 | train | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | - | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | expression | - | +1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | + | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | + | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | + | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | + | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | + | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | - | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | - | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | - | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | - | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | - | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_direct_v3 | independent | - | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | + | -1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | + | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | + | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | + | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | + | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | - | -1 | development | 2/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | - | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | - | +0 | development | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | - | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | - | +1 | development | 2/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | assignment | - | +1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | + | -1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | + | +0 | development | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | + | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | + | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | + | +1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | - | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | - | -1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | - | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | - | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | - | +1 | development | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | dependent | - | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | + | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | + | +0 | development | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | + | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | + | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | + | +1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | - | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | - | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | - | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | - | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | - | +1 | development | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | expression | - | +1 | train | 3/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | + | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | + | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | + | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | + | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | + | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | + | +1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | - | -1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | - | -1 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | - | +0 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | - | +0 | train | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | - | +1 | development | 4/4 | 0 | 4 |
| llama31_8b | print_trace_long_v1 | independent | - | +1 | train | 4/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | + | -1 | development | 3/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | + | -1 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | + | +0 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | + | +0 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | + | +1 | development | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | + | +1 | train | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | - | -1 | development | 2/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | - | -1 | train | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | - | +0 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | - | +0 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | - | +1 | development | 2/4 | 0 | 4 |
| codellama34b | print_direct_v3 | assignment | - | +1 | train | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | + | -1 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | + | -1 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | + | +0 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | + | +0 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | + | +1 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | + | +1 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | - | -1 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | - | -1 | train | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | - | +0 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | - | +0 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | - | +1 | development | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | dependent | - | +1 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | + | -1 | development | 3/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | + | -1 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | + | +0 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | + | +0 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | + | +1 | development | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | + | +1 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | - | -1 | development | 2/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | - | -1 | train | 2/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | - | +0 | development | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | - | +0 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | - | +1 | development | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | expression | - | +1 | train | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | + | -1 | development | 4/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | + | -1 | train | 3/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | + | +0 | development | 2/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | + | +0 | train | 1/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | + | +1 | development | 3/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | + | +1 | train | 3/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | - | -1 | development | 4/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | - | -1 | train | 4/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | - | +0 | development | 3/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | - | +0 | train | 0/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | - | +1 | development | 4/4 | 0 | 4 |
| codellama34b | print_direct_v3 | independent | - | +1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | + | -1 | development | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | + | -1 | train | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | + | +0 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | + | +0 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | + | +1 | development | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | + | +1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | - | -1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | - | -1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | - | +0 | development | 0/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | - | +0 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | - | +1 | development | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | assignment | - | +1 | train | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | + | -1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | + | -1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | + | +0 | development | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | + | +0 | train | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | + | +1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | + | +1 | train | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | - | -1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | - | -1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | - | +0 | development | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | - | +0 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | - | +1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | dependent | - | +1 | train | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | + | -1 | development | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | + | -1 | train | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | + | +0 | development | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | + | +0 | train | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | + | +1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | + | +1 | train | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | - | -1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | - | -1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | - | +0 | development | 1/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | - | +0 | train | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | - | +1 | development | 2/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | expression | - | +1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | + | -1 | development | 1/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | + | -1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | + | +0 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | + | +0 | train | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | + | +1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | + | +1 | train | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | - | -1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | - | -1 | train | 3/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | - | +0 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | - | +0 | train | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | - | +1 | development | 4/4 | 0 | 4 |
| codellama34b | print_trace_long_v1 | independent | - | +1 | train | 4/4 | 0 | 4 |

All original run manifests, tokenizer proofs, responses, source snapshots, scores and gates remain unchanged. The new study differs in numeric range, matched final answers, operation/storage forms, sign strata and grouping. Cross-bank accuracy differences therefore do not identify an operation-count effect.
