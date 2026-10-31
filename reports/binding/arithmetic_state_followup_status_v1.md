# Cached-state discovery: live status

Status: running. Updated: 2026-10-31T02:23:00.835680+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 485775 |  |
| llama8b_audit | complete | 485790 |  |
| llama8b_binding | submitted | 485816 |  |
| llama8b_numeric | submitted | 485817 |  |
| llama8b_capacity | submitted | 485818 |  |
| llama8b_compose | planned |  |  |
| codellama34b_audit | complete | 485791 |  |
| codellama34b_binding | submitted | 485819 |  |
| codellama34b_numeric | submitted | 485820 |  |
| codellama34b_capacity | submitted | 485821 |  |
| codellama34b_compose | planned |  |  |
| audit_report | submitted | 485822 |  |
| state_report | planned |  |  |

All work is CPU-only on existing immutable captures. The early validation phase uses CPU allocations. Scientific failures require review; only eligible scheduler interruptions are retried. Completed fits are preserved. Other running work and the editor allocation are preserved.
