# Overnight relationship findings: October 27–28, 2026

All 14 stages completed. Copy-parent structure remains accessible under the known scaffold, while computed-root numeric readouts and actual execution are much weaker. These results do not establish that the model has a complete correct scalar state and then fails to use it.

The suite used 32,076 distinct capture-case prefills across two checkpoints and generated 14,580 greedy responses. It saved 270 ridge factorizations, checked 1,574,640 saved-parameter score rows, and made 524,880 literal-to-computed parameter applications without new fitting.
The union has 16,038 distinct source rows. Each panel has 5,832 rows (3,888 TRAIN / 1,944 DEV). Shared literal/query rows were captured once per checkpoint and are not independent examples across panels.

## Algebraic relations after initialization

The metric is the fixed 18-cell, four-family macro balanced accuracy at nominated layer24 for Llama8B and36 for CodeLlama34B. All fixed TRAIN support checks passed.

| Model | Root format | Hidden direct | Hidden values → relations | Source values → relations |
|---|---|---:|---:|---:|
| Llama 3.1 8B | literal | 88.109% | 77.346% | 96.476% |
| Llama 3.1 8B | computed | 54.842% | 51.428% | 50.962% |
| CodeLlama 34B | literal | 84.192% | 83.857% | 95.869% |
| CodeLlama 34B | computed | 56.897% | 53.034% | 51.568% |

The stronger source-value pipeline outperforms direct hidden readouts on literal roots in both models. CodeLlama's literal direct-minus-hidden-values interval includes zero, so the earlier 8B advantage is not a clear two-model result. On computed roots, direct scores are only about55–57%; CodeLlama's comparison with its own value-derived decoder also has an interval crossing zero.

| Model | Format | Direct minus hidden values | Direct minus source values |
|---|---|---|---|
| Llama 3.1 8B | literal | +10.763 pp [+7.675, +13.714] | -8.367 pp [-10.609, -6.071] |
| Llama 3.1 8B | computed | +3.415 pp [+1.169, +6.175] | +3.880 pp [+0.808, +7.815] |
| CodeLlama 34B | literal | +0.335 pp [-3.405, +4.411] | -11.677 pp [-13.254, -10.041] |
| CodeLlama 34B | computed | +3.863 pp [-1.144, +8.884] | +5.329 pp [+0.847, +9.694] |

Intervals are conditional 95% component bootstraps: 2,000 valid draws, nine DEV components, fixed saved fits, no refitting or multiplicity adjustment. The direct18-output and categorical128-output pipelines have different task difficulty and total parameter counts. A hidden/source comparison concerns decoder accessibility, not information absent from the input. Selected sum/subtraction cells encode equivalent events; the relation cells are not independent replications.

## Complete parent graphs and literal-to-computed transfer

| Model | Format | Last assignment | Final prompt |
|---|---|---:|---:|
| Llama 3.1 8B | literal | 85.665% | 23.422% |
| Llama 3.1 8B | computed | 93.124% | 59.739% |
| CodeLlama 34B | literal | 95.628% | 57.305% |
| CodeLlama 34B | computed | 91.855% | 57.493% |

These are exact four-parent reconstructions under supplied node/version identities, not general node/version discovery. Direct source ngram controls remain in the result files; a strong symbolic source parser can recover these explicitly written copies. Graph decodability is not evidence of natural causal use.

| Model | Computed metric | Within-computed fit | Frozen literal parameters on computed inputs | Within minus transfer, conditional95% |
|---|---|---:|---:|---|
| Llama 3.1 8B | initialization algebraic | 54.842% | 50.867% | +3.976 pp [+1.117, +7.144] |
| Llama 3.1 8B | last-assignment graph | 93.124% | 70.490% | +22.634 pp [+6.566, +40.366] |
| Llama 3.1 8B | final-prompt graph | 59.739% | 27.401% | +32.339 pp [+15.446, +52.867] |
| CodeLlama 34B | initialization algebraic | 56.897% | 49.686% | +7.211 pp [+2.494, +12.271] |
| CodeLlama 34B | last-assignment graph | 91.855% | 86.094% | +5.761 pp [-8.368, +24.318] |
| CodeLlama 34B | final-prompt graph | 57.493% | 42.918% | +14.575 pp [-2.471, +31.761] |

Algebraic transfer is near the constant-predictor balanced-accuracy baseline of50%, while graph transfer is substantially stronger. CodeLlama's within-computed minus transferred graph intervals cross zero at both sites; do not claim a clear adaptation gain there. Root formats differ in arithmetic operations, token counts, positions and visible operands.

At the computed final prompt, queried categorical-value accuracy is only7.493% for8B and6.927% for34B, against a6.173% TRAIN prior in both. The corresponding source points are6.550% and7.596%. Strong routing readouts therefore do not imply that all necessary numeric quantities were correctly decoded.

## Query conditioning

PanelB uses the same bodies with all four queries, but fewer unique numeric draws than panelA. Before the query is visible (sites3/7), whole-graph and algebraic results are identical across future query slots. Per-slot queried/other accuracy differences at those sites measure which slot is scored, not modulation by a future query.

| Model | Query | Final whole graph | Queried value | Other values | Queried parent | Other parents |
|---|---:|---:|---:|---:|---:|---:|
| Llama 3.1 8B | v0 | 51.783% | 14.815% | 19.342% | 98.011% | 80.567% |
| Llama 3.1 8B | v1 | 39.438% | 25.514% | 22.542% | 90.192% | 78.601% |
| Llama 3.1 8B | v2 | 43.141% | 24.074% | 22.245% | 76.680% | 80.887% |
| Llama 3.1 8B | v3 | 62.071% | 25.857% | 22.702% | 80.727% | 91.198% |
| CodeLlama 34B | v0 | 66.461% | 16.667% | 31.436% | 97.874% | 88.272% |
| CodeLlama 34B | v1 | 64.952% | 33.813% | 26.520% | 97.462% | 88.089% |
| CodeLlama 34B | v2 | 64.335% | 28.052% | 26.543% | 84.088% | 92.433% |
| CodeLlama 34B | v3 | 63.649% | 29.698% | 25.332% | 90.261% | 88.294% |

Averaged over all four query choices and nine components, final queried-minus-other value accuracy is+0.857pp for8B and−0.400pp for34B; parent differences are+3.589pp and+3.149pp. These are descriptive point summaries with no query-effect interval. Individual slot contrasts can reflect slot difficulty, and other slots may be ancestors of the queried output. Same-body, fixed-slot effects require a separate matched analysis.

## Actual generated answers on matched DEV query-v0 programs

Each model generated7,290 responses, but this predeclared root-format contrast uses exactly486 matched DEV query-v0 pairs across nine components. The literal rates below use those same pairs, not all-query or pooled TRAIN/DEV literal rates.

| Model | Matched literal accuracy | Computed accuracy | Computed minus literal, conditional95% | Literal invalid | Computed invalid |
|---|---:|---:|---|---:|---:|
| Llama 3.1 8B | 48.560% | 11.728% | -36.831 pp [-45.885, -28.189] | 0.412% | 6.173% |
| CodeLlama 34B | 45.062% | 2.881% | -42.181 pp [-54.938, -30.864] | 0.000% | 0.000% |

The format penalty is large under both checkpoints. CodeLlama's computed responses are valid integers yet mostly wrong; this is not solely a response-format failure. The literal baseline is also unreliable. Arithmetic difficulty, operation count and context/position changes remain confounded with root format; these results do not isolate a binding mechanism.

## Evidence and scope

The frozen overnight execution used snapshot`5cf1471e56f5b3de779c8fbe` and source`acb67fad8bd960496c3d7163de924f0540ad37bf126010735417928617c5013d`. Its full binding regression passed1,733tests with no failures, errors or skips. That count describes the original execution; later fixes and follow-up tests are tracked separately.

All evidence remains adaptive discovery on the reused27structural components and81graphs. Three numeric seeds, three weighting seeds, lexical relatives, query siblings and paired formats are not independent structural replications. No sealed final outcomes were opened. No causal intervention, mechanism-C error predictor, broad ownership/version resolution or new-family confirmation is established.

The reproducible [publication script](../../artifacts/binding/overnight_relationships/20261028_completion_v1/publish_overnight_results_v1.py), [exact summary JSON](../../artifacts/binding/overnight_relationships/20261028_completion_v1/results_summary_v1.json), [CSV](../../artifacts/binding/overnight_relationships/20261028_completion_v1/results_summary_v1.csv) and [publication manifest](../../artifacts/binding/overnight_relationships/20261028_completion_v1/publication_review_v1.json) retain input checksums and output identities.

![Overnight relationship results](figures/overnight_relationships_v1.png)
