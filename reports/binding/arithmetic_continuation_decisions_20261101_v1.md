# Completed continuation: interpretation and next decisions

Both checkpoint runs and their native-token audits completed. All 941 continued responses preserved their exact saved prefixes. Scores, text decoding, EOS/ceiling flags and source-label joins replayed; all 2,592 merged calibration responses are accounted for. No continuation remains truncated. Original pilot scores and output-only competence gates are unchanged.

| Checkpoint | Protocol | Scope | Strict complete | Heading diagnostic |
|---|---|---|---:|---:|
| llama8b | output_only | single | 53.24% | 53.24% |
| llama8b | output_only | all | 48.61% | 48.61% |
| llama8b | intermediate_query | single | 95.37% | 95.37% |
| llama8b | intermediate_query | all | 94.44% | 94.44% |
| llama8b | stepwise | single | 50.00% | 91.20% |
| llama8b | stepwise | all | 80.56% | 88.89% |
| codellama34b | output_only | single | 33.33% | 33.33% |
| codellama34b | output_only | all | 34.72% | 34.72% |
| codellama34b | intermediate_query | single | 48.15% | 48.15% |
| codellama34b | intermediate_query | all | 42.59% | 42.59% |
| codellama34b | stepwise | single | 72.69% | 72.69% |
| codellama34b | stepwise | all | 81.94% | 81.94% |

The early zero for Llama intermediate-query output was a truncation result: its 128-token pilot always stopped before a complete final answer. Continuing those exact prefixes makes correct answers available on most of this finite cohort. Llama stepwise single-value scores also depend strongly on answer-heading grammar. CodeLlama responds differently across protocols, and direct-output errors remain after every response completes. These findings support measurement/protocol sensitivity; they do not establish universal arithmetic competence, preserved hidden values before generation, or an isolated effect of reasoning.

## Compare the same target across query scopes

These rows use the separate heading diagnostic and count every invalid answer as a failure. Both sides score the retained target, rather than comparing one-value accuracy against all-four joint accuracy.

| Checkpoint | Protocol | Paired cases | Single-target accuracy | All-query target accuracy |
|---|---|---:|---:|---:|
| llama8b | intermediate_query | 216 | 95.37% | 95.83% |
| llama8b | output_only | 216 | 53.24% | 63.89% |
| llama8b | stepwise | 216 | 91.20% | 94.44% |
| codellama34b | intermediate_query | 216 | 48.15% | 56.48% |
| codellama34b | output_only | 216 | 33.33% | 50.46% |
| codellama34b | stepwise | 216 | 72.69% | 91.67% |

Query scope and required answer shape change together in this assay; the comparisons do not isolate a pure routing mechanism. Calibration templates/seeds are correlated. Three wording variants are retained and never chosen by best observed accuracy. No significance or fresh-family confirmation claims.

The combined frozen report's matched-scope subsection reproduces ORIGINAL pilot scope diagnostics. The two checkpoint reviews and the table above are the continued-response scope analyses; do not mix their denominators/endpoints.

## Immediate next work

1. Run the new [conditional numeric-prediction suite](arithmetic_conditional_plan_20261101_v1.md) on archived captures. It tests joint source/hidden prediction against independently TRAIN-selected source-only, wider-source, hidden-only and shuffled-hidden controls. This distinguishes predictive complementarity from a simple nominal-capacity increase. It uses no new model calls and makes no causal-use claim.
2. Freeze a new calibration recipe before formal temporal capture. Keep both intermediate-query and stepwise candidates across checkpoints, all wordings, a common declared generation ceiling and a declared answer grammar. Use prospectively generated fresh numeric cases and disclose that protocol candidates were motivated by this pilot. Do not relax the old failed gates retroactively or choose a winning wording.
3. Before any generated-trace hidden capture, implement exact token boundaries and flags for whether the target has already appeared in the model's own trace. Source-prefill, pre-trace, pre-answer and already-emitted-answer states are different measurements. Never teacher-force a gold intermediate.
4. Audit native full-prompt versus prefix-truncated activations and padding tolerance before using the 3.27× potential prefix reuse. Then collect paired compute/overwrite/delay/later-use and binding-twin states under the new frozen protocol.
5. Confirm any selected discovery on fresh structural families before mechanism claims or targeted donor interventions.

![Original versus continued calibration and answer-heading sensitivity](figures/arithmetic_calibration_continuation_v1.png)

[Llama token audit](arithmetic_paired_llama8b_postrun_20261101_v1.md) · [CodeLlama token audit](arithmetic_paired_codellama34b_postrun_20261101_v1.md) · [Frozen combined report](arithmetic_paired_exploration_findings_20261101_v2.md). The new figure uses saved audited counts; its proof pins both input reviews and plotting code.
