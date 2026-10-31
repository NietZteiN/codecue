# Numeric geometry and final-query preparation: live status

Status: running. Updated: 2026-10-31T21:48:56.235530+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | complete | 486855 |  |
| llama8b_root_definition | running | 486869 | None |
| llama8b_computed_definition | running | 486870 | None |
| codellama34b_root_definition | pending | 486871 | QOSMaxJobsPerUserLimit |
| codellama34b_computed_definition | pending | 486872 | QOSMaxJobsPerUserLimit |
| source4096_root_definition | pending | 486873 | QOSMaxJobsPerUserLimit |
| source4096_computed_definition | pending | 486874 | QOSMaxJobsPerUserLimit |
| source8192_root_definition | pending | 486875 | QOSMaxJobsPerUserLimit |
| source8192_computed_definition | pending | 486876 | QOSMaxJobsPerUserLimit |
| llama8b_query_cache | pending | 486877 | QOSMaxJobsPerUserLimit |
| codellama34b_query_cache | pending | 486878 | QOSMaxJobsPerUserLimit |
| report | planned |  |  |

CPU-only cached-state work; full frozen regression gates all fits and extraction. Circular and permuted codes share dimensionality; source/prior/family controls remain explicit. Query caches prepare global-state work without fitting global-state probes. The controller checks every ten minutes; scientific failures require review.
