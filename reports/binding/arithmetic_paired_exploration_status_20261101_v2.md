# Calibration exploration: live status

Status: running. Updated: 2026-11-01T21:01:40.877858+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 488060 |  |
| error_audit | complete | 488070 |  |
| audit_report | complete | 488075 |  |
| llama8b_continuation | pending | 488076 | Priority |
| codellama34b_continuation | pending | 488077 | Priority |
| report | planned |  |  |

Full frozen regression gates independent error/scoring diagnostics. The audit gates two checkpoint continuation jobs: only previously truncated calibration responses receive new tokens, up to 1,024 total. Completed responses are reused. Original scores/gates remain unchanged; no formal-cohort inference or fitting. Ten-minute controllers stop at terminal completion; scheduler retries preserve immutable batches.
