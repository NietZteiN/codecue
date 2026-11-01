# Extended penalty path: live status

Status: complete_exploratory. Updated: 2026-11-01T23:22:01.267173+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 488331 |  |
| priors | complete | 488375 |  |
| source_source1024 | complete | 488405 |  |
| source_source2048 | complete | 488406 |  |
| llama8b_hidden | complete | 488407 |  |
| llama8b_joint | complete | 488408 |  |
| llama8b_shuffled_joint | complete | 488409 |  |
| codellama34b_hidden | complete | 488410 |  |
| codellama34b_joint | complete | 488411 |  |
| codellama34b_shuffled_joint | complete | 488412 |  |
| audit | complete | 488416 |  |
| report | complete | 488423 |  |

Full frozen regression gates shared TRAIN-fold priors and eight CPU cells. Old CV banks are hash-checked immutable references; new penalties alone are fitted. Ridge and constant-class choices use TRAIN only. A no-refit numerical audit gates the final report. New fits, reused banks and prior estimates remain separate. No new model calls or sealed-final access. Ten-minute checks stop at terminal completion; partial immutable banks resume on scheduler retries.
