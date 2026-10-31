# Cached-state discovery: live status

Status: complete_exploratory. Updated: 2026-10-31T05:13:02.039023+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 485775 |  |
| llama8b_audit | complete | 485790 |  |
| llama8b_binding | complete | 485816 |  |
| llama8b_numeric | complete | 485817 |  |
| llama8b_capacity | complete | 485818 |  |
| llama8b_compose | complete | 485865 |  |
| codellama34b_audit | complete | 485791 |  |
| codellama34b_binding | complete | 485819 |  |
| codellama34b_numeric | complete | 485820 |  |
| codellama34b_capacity | complete | 485821 |  |
| codellama34b_compose | complete | 485994 |  |
| audit_report | complete | 485822 |  |
| state_report | complete | 486004 |  |

All work is CPU-only on existing immutable captures. The early validation phase uses CPU allocations. Scientific failures require review; only eligible scheduler interruptions are retried. Completed fits are preserved. Other running work and the editor allocation are preserved.
