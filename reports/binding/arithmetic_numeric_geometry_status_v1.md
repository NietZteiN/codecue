# Numeric geometry and final-query preparation: live status

Status: complete_exploratory. Updated: 2026-10-31T22:18:44.674730+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 486855 |  |
| llama8b_root_definition | complete | 486869 |  |
| llama8b_computed_definition | complete | 486870 |  |
| codellama34b_root_definition | complete | 486871 |  |
| codellama34b_computed_definition | complete | 486872 |  |
| source4096_root_definition | complete | 486873 |  |
| source4096_computed_definition | complete | 486874 |  |
| source8192_root_definition | complete | 486875 |  |
| source8192_computed_definition | complete | 486876 |  |
| llama8b_query_cache | complete | 486877 |  |
| codellama34b_query_cache | complete | 486878 |  |
| report | complete | 486981 |  |

CPU-only cached-state work; full frozen regression gates all fits and extraction. Circular and permuted codes share dimensionality; source/prior/family controls remain explicit. Query caches prepare global-state work without fitting global-state probes. The controller checks every ten minutes; scientific failures require review.
