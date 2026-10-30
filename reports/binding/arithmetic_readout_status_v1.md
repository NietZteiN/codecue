# Arithmetic composition and readout feasibility status

Status: **complete**. Checked at 2026-10-27T00:50:57.950074+00:00. This command checks saved artifacts and SLURM; it makes no model queries.

| Stage | Saved predictions | Planned | Manifest |
|---|---:|---:|---|
| llama31_8b | 6144 | 6144 | complete |
| codellama34b | 6144 | 6144 | complete |

| Job | ID | State | Reason |
|---|---:|---|---|
| compare | 478445 | COMPLETED | — |
| figure | 478449 | COMPLETED | — |
| preflight_codellama34b | 478433 | COMPLETED | — |
| preflight_llama31_8b | 478432 | COMPLETED | — |
| review_codellama34b | 478444 | COMPLETED | — |
| review_llama31_8b | 478442 | COMPLETED | — |
| run_codellama34b | 478443 | COMPLETED | — |
| run_llama31_8b | 478441 | COMPLETED | — |

GPU usage: 98.68 minutes logged, 0.00 reserved. No cumulative project compute cap; reservations track active job walltime.

Completed comparison report: `reports/binding/arithmetic_readout_results_v1.md`. The report is ready only when the comparison audit has completed. A partial final JSONL append is reported without trimming or modifying it. No failed job, dependency or budget reservation is automatically cleared.

Refresh with `python scripts/101_binding_experiment_status.py configs/binding/arithmetic_readout/status_v1.json`. See [the fixed plan](arithmetic_readout_plan.md) and the JSON status artifact for exact paths.
