# codellama34b: audited continuation and matched query/protocol review

Verified all **377** continuations against exact saved native prefixes, output-token decoding, EOS/ceiling flags, source labels and independently reconstructed strict scores. Reused **919** completed responses. This review made no model calls or fits. Only this completed checkpoint is reported; other jobs remain separate. Original pilot scores and failed output-only gates are unchanged.

| Protocol | Scope | Cases | Strict complete | Heading-grammar complete | Truncated |
|---|---|---:|---:|---:|---:|
| output_only | single | 216 | 33.33% | 33.33% | 0 |
| output_only | all | 216 | 34.72% | 34.72% | 0 |
| intermediate_query | single | 216 | 48.15% | 48.15% | 0 |
| intermediate_query | all | 216 | 42.59% | 42.59% | 0 |
| stepwise | single | 216 | 72.69% | 72.69% | 0 |
| stepwise | all | 216 | 81.94% | 81.94% | 0 |

## Same target under single/all query scope

Both columns score the retained target, including incomplete/invalid responses as failures. The heading diagnostic is target-blind and does not change official scores.

| Grammar | Protocol | Pairs | Single correct | All-query target correct | All-only correct | Single-only correct |
|---|---|---:|---:|---:|---:|---:|
| strict | output_only | 216 | 72 | 109 | 56 | 19 |
| strict | intermediate_query | 216 | 104 | 122 | 45 | 27 |
| strict | stepwise | 216 | 157 | 198 | 52 | 11 |
| diagnostic | output_only | 216 | 72 | 109 | 56 | 19 |
| diagnostic | intermediate_query | 216 | 104 | 122 | 45 | 27 |
| diagnostic | stepwise | 216 | 157 | 198 | 52 | 11 |

## Matched protocol contrasts

| Grammar | Scope | Other protocol | Pairs | Output-only correct | Other correct | Other-only correct | Output-only exclusive correct |
|---|---|---|---:|---:|---:|---:|---:|
| strict | single | intermediate_query | 216 | 72 | 104 | 47 | 15 |
| strict | single | stepwise | 216 | 72 | 157 | 100 | 15 |
| strict | all | intermediate_query | 216 | 75 | 92 | 45 | 28 |
| strict | all | stepwise | 216 | 75 | 177 | 116 | 14 |
| diagnostic | single | intermediate_query | 216 | 72 | 104 | 47 | 15 |
| diagnostic | single | stepwise | 216 | 72 | 157 | 100 | 15 |
| diagnostic | all | intermediate_query | 216 | 75 | 92 | 45 | 28 |
| diagnostic | all | stepwise | 216 | 75 | 177 | 116 | 14 |

All conditions have a1,024-token total ceiling after continuation, while completed EOS outputs are reused. Fixed generated prefixes, instructions, assistant answer prefixes and requested behavior differ across protocols. This is not a monolithic rerun, an isolated effect of reasoning, a hidden-state readout or a causal mechanism result. Finite calibration templates/seeds are correlated; no significance tests or novel-family claims. The original output-only competence gate remains failed. Before formal collection with a revised protocol, freeze its generation/parsing/site rules and check prospectively declared fresh calibration without selecting a best wording.
