# Uncapped project checkpoint suites

Status: **complete**. Checked at 2026-10-26T04:05:36.653979+00:00. This command checks saved artifacts and SLURM; it makes no model queries.

| Stage | Saved predictions | Planned | Manifest |
|---|---:|---:|---|
| codellama13b | 5038 | 5038 | complete |
| codellama34b | 5038 | 5038 | complete |
| llama32_3b | 5038 | 5038 | complete |
| llama31_8b | 5038 | 5038 | complete |

| Job | ID | State | Reason |
|---|---:|---|---|
| tests | 476923 | COMPLETED | — |
| codellama13b_preflight | 476868 | COMPLETED | — |
| codellama13b_run | 476869 | COMPLETED | — |
| codellama13b_audit | 476870 | COMPLETED | — |
| codellama34b_preflight | 476871 | COMPLETED | — |
| codellama34b_run | 476872 | COMPLETED | — |
| codellama34b_audit | 476873 | COMPLETED | — |
| llama32_3b_preflight | 476924 | COMPLETED | — |
| llama32_3b_run | 476925 | COMPLETED | — |
| llama32_3b_audit | 476926 | COMPLETED | — |
| collect | 476930 | COMPLETED | — |
| llama31_8b_preflight | 476927 | COMPLETED | — |
| llama31_8b_run | 476928 | COMPLETED | — |
| llama31_8b_audit | 476929 | COMPLETED | — |

GPU usage: 27.13 minutes logged, 0.00 reserved. No cumulative project compute cap; reservations track active job walltime.

Completed comparison report: `reports/binding/capacity_results.md`. The report is ready only when the comparison audit has completed. A partial final JSONL append is reported without trimming or modifying it. No failed job, dependency or budget reservation is automatically cleared.

Refresh with `python scripts/101_binding_experiment_status.py configs/binding/capacity/status_v2.json`. See [the fixed plan](capacity_plan.md) and the JSON status artifact for exact paths.
