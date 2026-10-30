# Overnight relationship suite

Status: complete_exploratory. Morning status time: 2026-10-28T08:00:00-05:00.

| Stage | State | Latest job | Reason |
|---|---|---:|---|
| llama8b_prepare | complete | 480511 |  |
| codellama34b_prepare | complete | 480512 |  |
| llama8b_capture | complete | 480520 |  |
| llama8b_behavior | complete | 480535 |  |
| codellama34b_capture | complete | 480521 |  |
| codellama34b_behavior | complete | 480634 |  |
| llama8b_audit | complete | 480650 |  |
| codellama34b_audit | complete | 480651 |  |
| llama8b_numeric_replication | complete | 480682 |  |
| llama8b_query_twins | complete | 480683 |  |
| llama8b_computed_roots | complete | 480732 |  |
| codellama34b_numeric_replication | complete | 480684 |  |
| codellama34b_query_twins | complete | 480685 |  |
| codellama34b_computed_roots | complete | 480745 |  |

Stages use the frozen discovery plan. Failed scientific guards are reported rather than retried. Only resumable scheduler interruptions receive automatic retries; repeated failures with no committed progress stop retrying. Existing jobs outside this suite are never canceled.
