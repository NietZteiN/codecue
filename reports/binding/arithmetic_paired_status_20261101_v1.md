# Paired timing/overwrite/query-scope suite: status

Status: complete_exploratory. Updated: 2026-11-01T20:37:50.854453+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 487727 |  |
| sources | complete | 487731 |  |
| llama8b_native | complete | 487738 |  |
| codellama34b_native | complete | 487739 |  |
| llama8b_calibration | complete | 487742 |  |
| codellama34b_calibration | complete | 487743 |  |
| report | complete | 487935 |  |

Full regression, two independent execution oracles and connected structural closure gate native tokenizer checks. Both native checks gate the two cached-checkpoint GPU calibration jobs. All invalid/truncated generations remain in denominators. Calibration outcomes may fail the competence gate; this does not imply a software failure. No formal-cohort inference or fitting is scheduled by this suite. Large payloads start on scratch; model calls are accounting-only with actual scheduler limits. Ten-minute checks run until terminal; scientific failures stop dependent jobs.
