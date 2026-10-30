# Local arithmetic discovery: live status

Status: running. Updated: 2026-10-30T19:55:20.967892+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 484973 |  |
| llama8b_prepare | complete | 484974 |  |
| llama8b_capture | submitted | 484990 |  |
| llama8b_behavior | planned |  |  |
| codellama34b_prepare | complete | 484975 |  |
| codellama34b_capture | submitted | 484991 |  |
| codellama34b_behavior | planned |  |  |
| llama8b_probes | planned |  |  |
| codellama34b_probes | planned |  |  |

Whole structural families stay grouped. Scientific failures require review. Only resumable scheduler interruptions are retried; repeated interruptions without committed progress stop retries. Existing jobs outside the suite are preserved.
