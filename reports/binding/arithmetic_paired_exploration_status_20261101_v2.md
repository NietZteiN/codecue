# Calibration exploration: live status

Status: complete_exploratory. Updated: 2026-11-01T21:41:45.860947+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 488060 |  |
| error_audit | complete | 488070 |  |
| audit_report | complete | 488075 |  |
| llama8b_continuation | complete | 488076 |  |
| codellama34b_continuation | complete | 488077 |  |
| report | complete | 488129 |  |

Full frozen regression gates independent error/scoring diagnostics. The audit gates two checkpoint continuation jobs: only previously truncated calibration responses receive new tokens, up to 1,024 total. Completed responses are reused. Original scores/gates remain unchanged; no formal-cohort inference or fitting. Ten-minute controllers stop at terminal completion; scheduler retries preserve immutable batches.
