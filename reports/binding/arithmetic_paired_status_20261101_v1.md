# Paired timing/overwrite/query-scope suite: status

Status: running. Updated: 2026-11-01T16:12:51.822188+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 487727 |  |
| sources | complete | 487731 |  |
| llama8b_native | complete | 487738 |  |
| codellama34b_native | complete | 487739 |  |
| llama8b_calibration | pending | 487742 | Priority |
| codellama34b_calibration | pending | 487743 | Priority |
| report | planned |  |  |

Full regression, two independent execution oracles and connected structural closure gate native tokenizer checks. Both native checks gate the two cached-checkpoint GPU calibration jobs. All invalid/truncated generations remain in denominators. Calibration outcomes may fail the competence gate; this does not imply a software failure. No formal-cohort inference or fitting is scheduled by this suite. Large payloads start on scratch; model calls are accounting-only with actual scheduler limits. Ten-minute checks run until terminal; scientific failures stop dependent jobs.
