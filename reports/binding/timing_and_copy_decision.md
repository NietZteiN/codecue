# Decision after explicit query timing and earlier copy-site discovery

Completed 4,536 full baseline responses and 90,720 intervention forwards. Both studies passed complete semantic, tokenizer, output and activation audits. The final full regression suite passed 223 tests. No optional language-model training, unlearning or separate-paper project was launched, and generated final/extrapolation outcomes remain sealed.

The [timing study](query_timing_results_v1.md) explicitly moved the target cue before or after identical assignments. Every pair preserved the complete token multiset, length and capture positions. All responses parsed. Across the full cohort, early queries were correct on 1022/1296 (78.86%), versus 1201/1296 (92.67%) for late queries. There were 228 late-only correct pairs and 49 early-only correct pairs. These paired counts are descriptive; the numeric and instruction variants are not independent structural replications.

| Instruction | Early correct / n | Late correct / n | Late − early (pp) |
|---:|---:|---:|---:|
| 0 | 326/432 | 397/432 | +16.44 |
| 1 | 323/432 | 404/432 | +18.75 |
| 2 | 373/432 | 400/432 | +6.25 |

The aggregate benefit does not hold in every cell: for instruction 2's swapped second-variable query, early accuracy is 52/54 versus 34/54 late. All 9,720 late-query earlier-site vector comparisons were exactly invariant across future query identity, as required by causal attention. Early cues can change representations even at the initial-literal site, before task values are present. Moving a cue can affect attention, recency or task interpretation. A common-final-query/cue-format control and selective route tests are still needed before identifying tracking versus reconstruction.

The [earlier-copy study](copy_path_results_v1.md) used the original programs, an independent-statement reordering and a consistent temporary rename. Every source form preserves the complete canonical final state, statement count and literal exposure; reordering also preserves the token multiset. The original instruction-0 anchors retain exactly their old prompt IDs. Baseline performance in the previously nominated swapped second-variable cell is:

| Instruction | Original correct / n | Reordered correct / n | Renamed correct / n |
|---:|---:|---:|---:|
| 0 | 14/54 | 33/54 | 0/54 |
| 1 | 0/54 | 35/54 | 0/54 |
| 2 | 20/54 | 50/54 | 23/54 |

Reordering improves the nominated query under every instruction, but harms the other-variable query. The paired-output diagnostic preserves that tradeoff:

| Form (all instructions) | Both queries correct | Both swapped | Duplicate query-0 value | Duplicate query-1 value | Paired groups |
|---|---:|---:|---:|---:|---:|
| anchor | 34 | 0 | 128 | 0 | 162 |
| reordered | 78 | 15 | 29 | 40 | 162 |
| renamed | 23 | 0 | 139 | 0 | 162 |

Duplicating one value across two answers is different from swapping ownership while preserving the value multiset. These are post-hoc behavioral categories; neither is an observed internal stored state or an identified cause.

The intervention matrix contains every registered layer and control. Block 8 at the earlier copy endpoint is an exploratory candidate from these development results, not a confirmed site. The following table includes both quantities and both directions for reordering, pooled descriptively over the three instructions:

| Donor → recipient | Query | Unpatched correct / n | Copy patch correct / n | Unrelated control correct / n |
|---|---:|---:|---:|---:|
| reordered → original | 0 | 162/162 | 162/162 | 162/162 |
| reordered → original | 1 | 34/162 | 47/162 | 40/162 |
| original → reordered | 0 | 107/162 | 137/162 | 110/162 |
| original → reordered | 1 | 118/162 | 71/162 | 118/162 |

A copy-end vector can shift which answer is favored across both queries. The reciprocal effects and the other-variable effects prevent interpreting this as an isolated repair of one binding. Renaming has different, instruction-dependent effects. The full report retains all five blocks, both transformations, all three instructions, both directions and all seven conditions; no favorable layer replaces that matrix.

All 2,592 final answer-vector controls copied the donor digit. All 12,960 final-block earlier-token controls and 12,960 identity shams retained the recipient digit. The largest relative effective-norm mismatch was 2.1978% (allowed 3%). Answer copying is a software control, not evidence of a binding mechanism.

This advances explicit query timing and semantic-transformation robustness within the core study. A calibrated method that distinguishes shared computation, different computation and inconclusive alignment across held-out transformations remains unfinished. The next step is a separately registered fresh test of value-selection bias versus binding ownership at the candidate copy site, with nearby-position, wrong-value/version and reciprocal controls, combined with query-cue controls. No final-test forecast or general mechanism is registered.

Both GPU jobs ran on H200s and completed their finite workloads. Sources, jobs and post-hoc analysis are pinned by `artifacts/binding/timing_and_copy/source_v1.json`, `jobs_v1.json` and `analysis_source_v1.json`. All model jobs are complete. Usage accounting remains uncapped.
