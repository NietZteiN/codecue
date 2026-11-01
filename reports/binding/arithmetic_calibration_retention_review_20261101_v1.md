# Exploratory retained-target overwrite contrasts

All 36 calibration source pairs differ only in the destination of one later assignment: overwrite an operand or the matched irrelevant slot with the SAME constant. The retained target is unchanged. Compare that target under both query scopes, all protocols and all three wordings. All predictions come from the completed, native-token-audited continuation outputs. No new model calls or fits. These are correlated calibration cases, not formal-family confirmation or an internal causal mechanism test.

| Model | Grammar | Protocol | Scope | Pairs | Operand correct | Irrelevant correct | Irrelevant-only correct | Correct irrelevant + uniquely recomputed wrong operand |
|---|---|---|---|---:|---:|---:|---:|---:|
| llama8b | diagnostic | intermediate_query | all | 108 | 101 | 106 | 7 | 3 |
| llama8b | diagnostic | intermediate_query | single | 108 | 101 | 105 | 5 | 2 |
| llama8b | diagnostic | output_only | all | 108 | 66 | 72 | 10 | 0 |
| llama8b | diagnostic | output_only | single | 108 | 50 | 65 | 18 | 0 |
| llama8b | diagnostic | stepwise | all | 108 | 101 | 103 | 6 | 3 |
| llama8b | diagnostic | stepwise | single | 108 | 95 | 102 | 9 | 8 |
| llama8b | strict | intermediate_query | all | 108 | 101 | 106 | 7 | 3 |
| llama8b | strict | intermediate_query | single | 108 | 101 | 105 | 5 | 2 |
| llama8b | strict | output_only | all | 108 | 66 | 72 | 10 | 0 |
| llama8b | strict | output_only | single | 108 | 50 | 65 | 18 | 0 |
| llama8b | strict | stepwise | all | 108 | 88 | 96 | 16 | 2 |
| llama8b | strict | stepwise | single | 108 | 45 | 63 | 24 | 6 |
| codellama34b | diagnostic | intermediate_query | all | 108 | 55 | 67 | 16 | 0 |
| codellama34b | diagnostic | intermediate_query | single | 108 | 47 | 57 | 13 | 0 |
| codellama34b | diagnostic | output_only | all | 108 | 45 | 64 | 23 | 3 |
| codellama34b | diagnostic | output_only | single | 108 | 34 | 38 | 6 | 0 |
| codellama34b | diagnostic | stepwise | all | 108 | 95 | 103 | 11 | 0 |
| codellama34b | diagnostic | stepwise | single | 108 | 74 | 83 | 13 | 0 |
| codellama34b | strict | intermediate_query | all | 108 | 55 | 67 | 16 | 0 |
| codellama34b | strict | intermediate_query | single | 108 | 47 | 57 | 13 | 0 |
| codellama34b | strict | output_only | all | 108 | 45 | 64 | 23 | 3 |
| codellama34b | strict | output_only | single | 108 | 34 | 38 | 6 | 0 |
| codellama34b | strict | stepwise | all | 108 | 95 | 103 | 11 | 0 |
| codellama34b | strict | stepwise | single | 108 | 74 | 83 | 13 | 0 |

The last column requires a wrong operand-condition target equal to recomputation from current operands, with no coincidence with the stored stale/opposite-operator/other-current-binding candidates, while the irrelevant partner is correct. This is unique only among this finite candidate list; other explanations remain possible. Copy controls often make recomputation and another-current-binding numerically identical and cannot distinguish them. Every invalid/truncated output remains a failure. JSON also retains accepted-value disagreements, ambiguous matches and kind/depth strata. Original pilot scores, failed output-only gates and formal data remain untouched.
