# Overnight relationship suite

Status: running. Morning status time: 2026-10-30T08:00:00-05:00.

| Stage | State | Latest job | Reason |
|---|---|---:|---|
| software_validation | complete | 483447 |  |
| llama8b_prepare | complete | 483448 |  |
| codellama34b_prepare | complete | 483449 |  |
| llama8b_capture | running | 483460 | None |
| llama8b_behavior | planned |  |  |
| codellama34b_capture | pending | 483461 | Priority |
| codellama34b_behavior | planned |  |  |
| llama8b_readouts | planned |  |  |
| codellama34b_readouts | planned |  |  |

Stages use the frozen discovery plan. Failed scientific guards are reported rather than retried. Only resumable scheduler interruptions receive automatic retries; repeated failures with no committed progress stop retrying. Existing jobs outside this suite are never canceled.
