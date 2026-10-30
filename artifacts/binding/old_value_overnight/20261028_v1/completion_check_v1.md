# Old-value overnight check

Checked: 2026-10-29T01:06:37.760728+00:00. Execution: **complete**. Behavioral gate: **gate_failed**.

| Stage | Job | State | Reason |
|---|---:|---|---|
| regression | 481692 | completed | None |
| llama8b_preflight | 481693 | completed | QOSMaxJobsPerUserLimit |
| codellama34b_preflight | 481694 | completed | QOSMaxJobsPerUserLimit |
| llama8b_behavior | 481704 | completed | None |
| codellama34b_behavior | 481705 | completed | QOSMaxJobsPerUserLimit |
| publication | 481706 | completed | Dependency |
| morning | 481707 | waiting | BeginTime |

| Model | Committed / planned | Gate |
|---|---:|---|
| codellama34b | 20160 / 20160 | gate_failed |
| llama8b | 20160 / 20160 | gate_failed |

Logging enabled: True; pending guards: 2; last successful export age: 101.335709 seconds; fresh within two intervals: True.

Job completion and behavioral gate qualification are separate. This check never qualifies a causal mechanism or starts another experiment. Existing overview-document hashes are historical; the immutable scientific handoff is checked separately.
