# Varied-schedule decoding job graph

The finite suite was submitted on October 28, 2026. This is a submission record; current states and completion evidence are in the automatic experiment log and per-stage receipts.

| Stage | SLURM job | Requires |
|---|---:|---|
| regression | 481259 | — |
| llama8b_prepare | 481260 | — |
| codellama34b_prepare | 481263 | — |
| llama8b_capture | 481261 | 481260 |
| codellama34b_capture | 481264 | 481263 |
| llama8b_readouts | 481262 | 481261 and 481259 |
| codellama34b_readouts | 481265 | 481264 and 481259 |
| independent review and publication | 481283 | 481262 and 481265 |

Each readout worker first audits its capture, then runs readout preflight, fitting and full parameter/metric replay. Passing receipts are required before publication. The source is frozen as `20ff6812f33085b298163a26` (code SHA `a42b01fa7f1fa201639287c5b0761f2cdeaf0a84163c662e7e986b3fbf555f99`).

The final CPU worker independently verifies all receipts and job exits, runs the publisher twice with byte-identical output checks, writes the completed 63-task readiness snapshot, checks logging guards and saves a pinned handoff. It performs no model calls or fitting. It updates the shared readiness report only if that report still matches this suite's queue checkpoint, preserving a newer continuation's report.

The complete binding regression passed 1,922 tests. Both tokenizer preparations completed successfully. The remaining model stages are queued by cluster priority; their current state is recorded in the automatic experiment log.

The source-only audit supports 2,016 rows, 232 target columns, 10 training and 5 development graph families. No learned outcome is claimed in this submission record. Existing unrelated jobs, including `480098` and the `a27p4fmt` jobs, are preserved.
