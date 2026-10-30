# Computation and routing execution status

All 8 workers completed with exit code 0: full regression, 2 preparations, 2 generations, 2 audits, and reproducible publication. Scientific qualification: 0 of 6 fixed instruction gates passed.

| Stage | Job | State |
|---|---:|---|
| codellama34b_audit | 481072 | COMPLETED, exit 0 |
| codellama34b_prepare | 481068 | COMPLETED, exit 0 |
| codellama34b_run | 481070 | COMPLETED, exit 0 |
| llama8b_audit | 481071 | COMPLETED, exit 0 |
| llama8b_prepare | 481065 | COMPLETED, exit 0 |
| llama8b_run | 481069 | COMPLETED, exit 0 |
| regression | 481034 | COMPLETED, exit 0 |
| publication | 481109 | COMPLETED, exit 0 |

40,200 physical scored responses and 16 warm-up requests give 40,216 total model requests. No probe or language model was fitted.

Source-only schedule preparation produced 2,016 rows across 15 canonical SSA graph families, with a maximum assignment version of 4. These targets require extending the learned readout before model evaluation.

All 1,843 tests passed. The current inventory has 60 tasks: 48 ready, 9 awaiting scientific decisions, and 3 optional tasks deferred.
