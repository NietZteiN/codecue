# Serialization experiment status

Status: **complete**. Checked at 2026-10-26T01:18:53.238602+00:00. This command checks saved artifacts and SLURM; it makes no model queries.

| Stage | Saved predictions | Planned | Manifest |
|---|---:|---:|---|
| native_replay_v1 | 16 | 16 | complete |
| completion_smoke_v1 | 16 | 16 | complete |
| completion_full_v1 | 1600 | 1600 | complete |

| Job | ID | State | Reason |
|---|---:|---|---|
| preflight | 476708 | COMPLETED | — |
| tests | 476709 | COMPLETED | — |
| smoke | 476718 | COMPLETED | — |
| full | 476726 | COMPLETED | — |
| finalize | 476727 | COMPLETED | — |
| maintenance_tests | 476762 | COMPLETED | — |

Shared GPU stage budget: 62.87 minutes used, 0.00 reserved, cap 240 minutes.

Completed comparison report: `reports/binding/serialization_comparison.md`. The report is ready only when the comparison audit has completed. A partial final JSONL append is reported without trimming or modifying it. No failed job, dependency or budget reservation is automatically cleared.

Refresh with `python scripts/101_binding_experiment_status.py configs/binding/serialization/status_v1.json`. See [the fixed plan](serialization_plan.md) and the JSON status artifact for exact paths.
