# Binding competition and interface follow-up status

Status: **complete**. Checked at 2026-10-26T13:28:51.335247+00:00. This command checks saved artifacts and SLURM; it makes no model queries.

| Stage | Saved predictions | Planned | Manifest |
|---|---:|---:|---|
| codellama34b_competition | 9984 | 9984 | complete |
| llama31_8b_competition | 9984 | 9984 | complete |
| llama31_8b_completion | 1600 | 1600 | complete |
| llama32_3b_completion | 1600 | 1600 | complete |

| Job | ID | State | Reason |
|---|---:|---|---|
| tests | 477359 | COMPLETED | — |
| codellama34b_competition_preflight | 477360 | COMPLETED | — |
| codellama34b_competition_run | 477361 | COMPLETED | — |
| codellama34b_competition_audit | 477362 | COMPLETED | — |
| llama31_8b_competition_preflight | 477363 | COMPLETED | — |
| llama31_8b_competition_run | 477364 | COMPLETED | — |
| llama31_8b_competition_audit | 477365 | COMPLETED | — |
| llama31_8b_serialization_preflight | 477330 | COMPLETED | — |
| llama31_8b_serialization_run | 477331 | COMPLETED | — |
| llama31_8b_serialization_audit | 477332 | COMPLETED | — |
| llama32_3b_serialization_preflight | 477333 | COMPLETED | — |
| llama32_3b_serialization_run | 477334 | COMPLETED | — |
| llama32_3b_serialization_audit | 477335 | COMPLETED | — |
| competition_review | 477366 | COMPLETED | — |
| serialization_review | 477354 | COMPLETED | — |

GPU usage: 42.16 minutes logged, 0.00 reserved. No cumulative project compute cap; reservations track active job walltime.

Completed comparison report: `reports/binding/competition_results.md`. The report is ready only when the comparison audit has completed. A partial final JSONL append is reported without trimming or modifying it. No failed job, dependency or budget reservation is automatically cleared.

Refresh with `python scripts/101_binding_experiment_status.py configs/binding/competition/status_v2.json`. See [the fixed plan](competition_plan.md) and the JSON status artifact for exact paths.
