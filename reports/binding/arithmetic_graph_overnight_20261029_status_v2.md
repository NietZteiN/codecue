# Overnight relationship suite

Status: needs_attention. Morning status time: 2026-10-30T08:00:00-05:00.

| Stage | State | Latest job | Reason |
|---|---|---:|---|
| software_validation | failed | 483437 | None |
| llama8b_prepare | complete | 483438 |  |
| codellama34b_prepare | complete | 483439 |  |
| llama8b_capture | blocked |  |  |
| llama8b_behavior | blocked |  |  |
| codellama34b_capture | blocked |  |  |
| codellama34b_behavior | blocked |  |  |
| llama8b_readouts | blocked |  |  |
| codellama34b_readouts | blocked |  |  |

Stages use the frozen discovery plan. Failed scientific guards are reported rather than retried. Only resumable scheduler interruptions receive automatic retries; repeated failures with no committed progress stop retrying. Existing jobs outside this suite are never canceled.
