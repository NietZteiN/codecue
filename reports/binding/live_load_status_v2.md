# Computed retention-frontier study status

Status: **complete**. Checked at 2026-10-26T22:51:22.982141+00:00. This command checks saved artifacts and SLURM; it makes no model queries.

| Stage | Saved predictions | Planned | Manifest |
|---|---:|---:|---|
| llama31_8b | 38016 | 38016 | complete |
| codellama34b | 38016 | 38016 | complete |

| Job | ID | State | Reason |
|---|---:|---|---|
| codellama34b_audit | 478140 | COMPLETED | — |
| codellama34b_gpu | 478139 | COMPLETED | — |
| codellama34b_qa | 478138 | COMPLETED | — |
| codellama34b_review | 478141 | COMPLETED | — |
| llama31_8b_audit | 478136 | COMPLETED | — |
| llama31_8b_gpu | 478135 | COMPLETED | — |
| llama31_8b_qa | 478134 | COMPLETED | — |
| llama31_8b_review | 478137 | COMPLETED | — |
| comparison | 478148 | COMPLETED | — |

GPU usage: 86.28 minutes logged, 0.00 reserved. No cumulative project compute cap; reservations track active job walltime.

Completed comparison report: `reports/binding/live_load_results_v2.md`. The report is ready only when the comparison audit has completed. A partial final JSONL append is reported without trimming or modifying it. No failed job, dependency or budget reservation is automatically cleared.

Refresh with `python scripts/101_binding_experiment_status.py configs/binding/competition/live_load_status_v2.json`. See [the fixed plan](live_load_plan.md) and the JSON status artifact for exact paths.
