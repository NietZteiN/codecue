# Overnight relationship suite

Status: complete_exploratory. Morning status time: 2026-10-30T08:00:00-05:00.

| Stage | State | Latest job | Reason |
|---|---|---:|---|
| software_validation | complete | 483447 |  |
| llama8b_prepare | complete | 483448 |  |
| codellama34b_prepare | complete | 483449 |  |
| llama8b_capture | complete | 483460 |  |
| llama8b_behavior | complete | 483472 |  |
| codellama34b_capture | complete | 483461 |  |
| codellama34b_behavior | complete | 483473 |  |
| llama8b_readouts | complete | 483484 |  |
| codellama34b_readouts | complete | 483485 |  |

Stages use the frozen discovery plan. Failed scientific guards are reported rather than retried. Only resumable scheduler interruptions receive automatic retries; repeated failures with no committed progress stop retrying. Existing jobs outside this suite are never canceled.
