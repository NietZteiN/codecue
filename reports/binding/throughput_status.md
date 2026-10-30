# GPU throughput tuning status

Status: **complete**. Checked at 2026-10-26T03:13:14.289303+00:00. This command checks saved artifacts and SLURM; it makes no model queries.

| Stage | Saved predictions | Planned | Manifest |
|---|---:|---:|---|
| continuous_batching_v4 | 1600 | 1600 | complete |

Completed profiling trials: 3; full-workload candidates: 3. Best profile requests/s: 32.61712097241299; full validation requests/s: 40.219507984494875.


| Job | ID | State | Reason |
|---|---:|---|---|
| preflight | 476839 | COMPLETED | — |
| tests | 476840 | COMPLETED | — |
| profile | 476841 | COMPLETED | — |
| audit | 476865 | COMPLETED | — |

GPU usage: 0.00 minutes logged, 0.00 reserved. No cumulative project compute cap; reservations track active job walltime.

Completed comparison report: `reports/binding/throughput_results.md`. The report is ready only when the comparison audit has completed. A partial final JSONL append is reported without trimming or modifying it. No failed job, dependency or budget reservation is automatically cleared.

Refresh with `python scripts/101_binding_experiment_status.py configs/binding/throughput/status_v4.json`. See [the fixed plan](throughput_plan.md) and the JSON status artifact for exact paths.
