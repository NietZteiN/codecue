# Decision after computed-expression and late-reference discovery

This continuation completed 1,008 full greedy baseline responses and 15,120 next-token intervention forwards. Both datasets, tokenizer layouts, full outputs and activation/control audits passed. The full regression suite passed 217 tests; 18 targeted checks passed after the scheduler/profile changes. No language-model training or final/extrapolation evaluation was performed.

The [computed-expression bank](computed_routing_results_v1_analysis_v2.md) scored 461/576. Neither complete family passed the fixed per-cell reliability gate, so no computed interventions or analytic intervention-control tests ran. The weakest ownership cell scored 1/72; saved-version cells scored 60/72 and 49/72. This does not establish absence of computed values. A post-hoc descriptive audit found 95/115 wrong answers compatible with the other computed binding; compatibility is not an internal causal explanation.

The [late-reference study](swap_reset_results_v2.md) changed only the identifier in a final output-irrelevant assignment, preserving the query result, statement count, literal exposure and token length. The earlier failure cell remained weak: 15/54 correct with the reused temporary reset, versus 9/54 when the assignment wrote to a fresh `cache` variable. There were 0 rescues and 6 additional errors; the other three mapping/query cells were 54/54 in both conditions. This contrast does not support removing a late temporary reset as a behavioral repair. Full final states and identifier vocabulary differ, so lexical cues and reset semantics remain confounded.

Interventions at the changed reference did not consistently improve correctness beyond norm-matched unrelated-position/random controls. The table retains every registered block in the previously nominated failure cell (54 cases per direction). Baseline accuracies are 27.78% for the reused-temporary recipient and 16.67% for the fresh-variable recipient. The direction labels identify the source vector and recipient prompt, not a changed oracle answer.

| Block | Fresh → reused: primary (%) | Unrelated (%) | Random range (%) | Reused → fresh: primary (%) | Unrelated (%) | Random range (%) |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 18.52 | 31.48 | 29.63–35.19 | 25.93 | 5.56 | 20.37–24.07 |
| 8 | 22.22 | 22.22 | 24.07–29.63 | 20.37 | 35.19 | 29.63–33.33 |
| 16 | 25.93 | 25.93 | 25.93–27.78 | 22.22 | 22.22 | 16.67–18.52 |
| 24 | 25.93 | 25.93 | 25.93–27.78 | 18.52 | 20.37 | 18.52–20.37 |
| 31 | 27.78 | 27.78 | 27.78–27.78 | 16.67 | 16.67 | 16.67–16.67 |

All 432 final answer-vector transfers copied the donor digit. All 2,160 final-block earlier-token controls and 2,160 identity shams retained the recipient digit. The largest relative effective-norm mismatch was 0.0590% (fixed tolerance 3%). These positive/negative software controls establish measurement integrity, not a selective binding mechanism.

The original anchor inputs were exactly preserved. Across the previous H200/batch-48 run and this A30/batch-144 run, 213/216 parsed predictions matched (176 versus 177 correct). All differences remain in the paired artifact. The reset contrast above uses conditions evaluated together on the A30; the anchor replay is not an isolated hardware or throughput comparison.

The next scientific step is a separately registered causal test of the earlier copy from the temporary into the second variable, with correct-value/owner controls, complete paired outputs and instruction/identifier robustness. Keep the existing failed computed and arithmetic gates. No general binding register, computed-value abstraction, validated explanation of the competition errors or final-test forecast is established.

Batch 96 computed baselines and batch 144 reset interventions fit the A30. A scheduler sample reported 98% utilization during the reset run; this is not a time-average utilization claim. The expanded development-A30/standard-GPU eligibility and backfill request are recorded separately, without changing the frozen scientific cohort or introducing an application compute cap. All jobs in this continuation are complete.

Sources/jobs: `artifacts/binding/routing_extension/source_v1.json`, `swap_source_v2.json`, `analysis_source_v2.json` and `jobs_v2.json`. The corrected computed report explicitly marks its intervention controls as not run; the earlier empty-control wording is preserved in its historical analysis.

To reproduce the corrected computed analysis, use the snapshot in `analysis_source_v2.json` with `scripts/112_binding_routing_extension.py review configs/binding/competition/computed_routing_v1.json --analysis-revision v2`. This changes the report destination, not the recorded model configuration. The exact frozen launcher and configuration paths are recorded with the source pointer.
