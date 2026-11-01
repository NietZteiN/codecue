# llama8b: audited continuation and matched query/protocol review

Verified all **564** continuations against exact saved native prefixes, output-token decoding, EOS/ceiling flags, source labels and independently reconstructed strict scores. Reused **732** completed responses. This review made no model calls or fits. Only this completed checkpoint is reported; other jobs remain separate. Original pilot scores and failed output-only gates are unchanged.

| Protocol | Scope | Cases | Strict complete | Heading-grammar complete | Truncated |
|---|---|---:|---:|---:|---:|
| output_only | single | 216 | 53.24% | 53.24% | 0 |
| output_only | all | 216 | 48.61% | 48.61% | 0 |
| intermediate_query | single | 216 | 95.37% | 95.37% | 0 |
| intermediate_query | all | 216 | 94.44% | 94.44% | 0 |
| stepwise | single | 216 | 50.00% | 91.20% | 0 |
| stepwise | all | 216 | 80.56% | 88.89% | 0 |

## Same target under single/all query scope

Both columns score the retained target, including incomplete/invalid responses as failures. The heading diagnostic is target-blind and does not change official scores.

| Grammar | Protocol | Pairs | Single correct | All-query target correct | All-only correct | Single-only correct |
|---|---|---:|---:|---:|---:|---:|
| strict | output_only | 216 | 115 | 138 | 30 | 7 |
| strict | intermediate_query | 216 | 206 | 207 | 8 | 7 |
| strict | stepwise | 216 | 108 | 184 | 86 | 10 |
| diagnostic | output_only | 216 | 115 | 138 | 30 | 7 |
| diagnostic | intermediate_query | 216 | 206 | 207 | 8 | 7 |
| diagnostic | stepwise | 216 | 197 | 204 | 15 | 8 |

## Matched protocol contrasts

| Grammar | Scope | Other protocol | Pairs | Output-only correct | Other correct | Other-only correct | Output-only exclusive correct |
|---|---|---|---:|---:|---:|---:|---:|
| strict | single | intermediate_query | 216 | 115 | 206 | 94 | 3 |
| strict | single | stepwise | 216 | 115 | 108 | 40 | 47 |
| strict | all | intermediate_query | 216 | 105 | 204 | 102 | 3 |
| strict | all | stepwise | 216 | 105 | 174 | 78 | 9 |
| diagnostic | single | intermediate_query | 216 | 115 | 206 | 94 | 3 |
| diagnostic | single | stepwise | 216 | 115 | 197 | 85 | 3 |
| diagnostic | all | intermediate_query | 216 | 105 | 204 | 102 | 3 |
| diagnostic | all | stepwise | 216 | 105 | 192 | 91 | 4 |

All conditions have a1,024-token total ceiling after continuation, while completed EOS outputs are reused. Fixed generated prefixes, instructions, assistant answer prefixes and requested behavior differ across protocols. This is not a monolithic rerun, an isolated effect of reasoning, a hidden-state readout or a causal mechanism result. Finite calibration templates/seeds are correlated; no significance tests or novel-family claims. The original output-only competence gate remains failed. Before formal collection with a revised protocol, freeze its generation/parsing/site rules and check prospectively declared fresh calibration without selecting a best wording.
