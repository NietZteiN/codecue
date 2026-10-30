# Matched arithmetic prompt control: live status

Status: complete_exploratory. Recorded: 2026-10-30T15:55:59.587781+00:00.

| Stage | State | Job |
|---|---|---:|
| llama8b_prepare | complete | 484427 |
| codellama34b_prepare | complete | 484428 |
| llama8b_behavior | complete | 484443 |
| codellama34b_behavior | complete | 484444 |

Original baseline answers are cached; preparation makes no model calls. New queries and interruptions remain counted in worker manifests. The monitor retries only eligible scheduler interruptions; scientific failures require review.
