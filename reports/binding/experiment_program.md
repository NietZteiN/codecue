# Authorized experiment program

This historical table records the original checkpoint's failed prerequisites. The [current full research agenda](research_backlog.md) maps later scoped runs to all ten experiments and the separate extension projects. Historical quota references below have been superseded by uncapped project compute accounting.

Generated 2026-10-25T21:52:09.484853+00:00.

The user authorized all ten proposed experiments. Scientific prerequisites determine which model runs are eligible. The earlier pilot is retained separately. The new checkpoint audit verifies public artifact hashes and discovers a tokenizer boundary discrepancy; the explicit correction is independently checked against raw SentencePiece. Its effect is measured on paired same-GPU runs.

| Experiment | State |
|---|---|
| 1. Checkpoint and official prompt audit | `completed_with_boundary_correction` |
| 2. Arithmetic versus program execution | `completed` |
| 3. Arithmetic-free binding | `completed` |
| 4. Binding and version competition | `not_run_failed_behavioral_prerequisite` |
| 5. Naming by competition by updates | `not_run_failed_behavioral_prerequisite` |
| 6. Tracking versus query-time reconstruction | `not_run_failed_behavioral_prerequisite` |
| 7. Distributed-state probe diagnostics | `not_run_failed_behavioral_prerequisite` |
| 8. Value, ownership and pathway interventions | `not_run_failed_behavioral_prerequisite` |
| 9. Frozen failure prediction | `not_run_failed_behavioral_prerequisite` |
| 10. Second-family replication | `not_run_failed_behavioral_prerequisite` |

## New behavioral diagnostics

Protocol selection uses only training elementary cells at at least 90% exact accuracy and at most 5% invalid outputs, with at least 24 examples per cell. The chosen protocol must independently pass fresh numeric validation. No fallback is allowed after validation failure. These numeric sets share task structures and are not confirmatory structural tests.

### arithmetic_forms

Decision: `no_training_candidate`. Queries: 384/384.

| Protocol | Split | Family | Depth | Correct / n | Invalid |
|---|---|---|---:|---:|---:|
| print_direct_v3 | train | assignment | — | 2/24 | 0 |
| print_direct_v3 | train | dependent | — | 3/24 | 0 |
| print_direct_v3 | train | expression | — | 3/24 | 0 |
| print_direct_v3 | train | independent | — | 10/24 | 0 |
| print_direct_v3 | development | assignment | — | 0/24 | 0 |
| print_direct_v3 | development | dependent | — | 1/24 | 0 |
| print_direct_v3 | development | expression | — | 0/24 | 0 |
| print_direct_v3 | development | independent | — | 12/24 | 0 |
| print_trace_long_v1 | train | assignment | — | 8/24 | 0 |
| print_trace_long_v1 | train | dependent | — | 12/24 | 0 |
| print_trace_long_v1 | train | expression | — | 13/24 | 0 |
| print_trace_long_v1 | train | independent | — | 16/24 | 1 |
| print_trace_long_v1 | development | assignment | — | 10/24 | 0 |
| print_trace_long_v1 | development | dependent | — | 11/24 | 0 |
| print_trace_long_v1 | development | expression | — | 8/24 | 0 |
| print_trace_long_v1 | development | independent | — | 16/24 | 1 |

### arithmetic_free

Decision: `no_training_candidate`. Queries: 768/768.

| Protocol | Split | Family | Depth | Correct / n | Invalid |
|---|---|---|---:|---:|---:|
| print_direct_v3 | train | copy_depth | 1 | 23/24 | 0 |
| print_direct_v3 | train | copy_depth | 2 | 14/24 | 0 |
| print_direct_v3 | train | copy_depth | 4 | 10/24 | 0 |
| print_direct_v3 | train | copy_depth | 8 | 6/24 | 0 |
| print_direct_v3 | train | overwrite_count | 1 | 12/24 | 0 |
| print_direct_v3 | train | overwrite_count | 2 | 9/24 | 0 |
| print_direct_v3 | train | overwrite_count | 4 | 11/24 | 0 |
| print_direct_v3 | train | overwrite_count | 8 | 6/24 | 0 |
| print_direct_v3 | development | copy_depth | 1 | 18/24 | 0 |
| print_direct_v3 | development | copy_depth | 2 | 14/24 | 0 |
| print_direct_v3 | development | copy_depth | 4 | 5/24 | 0 |
| print_direct_v3 | development | copy_depth | 8 | 8/24 | 0 |
| print_direct_v3 | development | overwrite_count | 1 | 9/24 | 0 |
| print_direct_v3 | development | overwrite_count | 2 | 11/24 | 0 |
| print_direct_v3 | development | overwrite_count | 4 | 10/24 | 0 |
| print_direct_v3 | development | overwrite_count | 8 | 7/24 | 0 |
| print_trace_long_v1 | train | copy_depth | 1 | 21/24 | 0 |
| print_trace_long_v1 | train | copy_depth | 2 | 21/24 | 1 |
| print_trace_long_v1 | train | copy_depth | 4 | 17/24 | 0 |
| print_trace_long_v1 | train | copy_depth | 8 | 15/24 | 1 |
| print_trace_long_v1 | train | overwrite_count | 1 | 21/24 | 0 |
| print_trace_long_v1 | train | overwrite_count | 2 | 17/24 | 1 |
| print_trace_long_v1 | train | overwrite_count | 4 | 14/24 | 0 |
| print_trace_long_v1 | train | overwrite_count | 8 | 11/24 | 0 |
| print_trace_long_v1 | development | copy_depth | 1 | 22/24 | 0 |
| print_trace_long_v1 | development | copy_depth | 2 | 24/24 | 0 |
| print_trace_long_v1 | development | copy_depth | 4 | 18/24 | 0 |
| print_trace_long_v1 | development | copy_depth | 8 | 17/24 | 1 |
| print_trace_long_v1 | development | overwrite_count | 1 | 18/24 | 0 |
| print_trace_long_v1 | development | overwrite_count | 2 | 18/24 | 1 |
| print_trace_long_v1 | development | overwrite_count | 4 | 17/24 | 0 |
| print_trace_long_v1 | development | overwrite_count | 8 | 11/24 | 0 |

## Resources and deferred work

All model weights are existing local checkpoints. GPU work uses the shared four-hour cap; the second-family run needs a global reservation before its separate checkpoint ledger can be used. Stage ceilings do not grant additive budgets. Final outcomes remain sealed until a genuine registration and frozen forecasts exist. No language-model training or unlearning is included.

The machine-readable plan is `configs/binding/phase2/program_plan.json`; current evidence and decisions are in `artifacts/binding/phase2/program_status.json`. Exact stage configurations and source/job pointers are retained.

## Review and unqueried follow-up data

The [post-hoc diagnostic review](diagnostic_review.md) reports paired readout/form counts and identifies a confound: trailing distractors in the consumed binding dataset are tied to nonzero answer magnitude. Those data cannot isolate a trailing-distractor effect. The earlier gate and cell accuracies remain unchanged.

Prepared 384 fresh numeric matched pairs (768 programs), with 768 independent Python trace checks. Each pair shares its assignment prefix and answer, differing by one irrelevant trailing copy. Both levels occur at every answer magnitude. These repeated structures are future calibration candidates; no model inference or confirmatory evaluation has run on them.

![Fresh reference-tokenized diagnostics](experiment_program.png)

Invalid outputs count as incorrect and remain separately tabulated. Training and fresh numeric validation share task structures; these plots do not establish independent structural generalization or a causal mechanism.

Completed model-stage ledger time: 647.08/14400 seconds; active reservations: 0. SLURM allocated elapsed time includes additional batch startup.
