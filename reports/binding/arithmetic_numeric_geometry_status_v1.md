# Numeric geometry and final-query preparation: live status

Status: running. Updated: 2026-10-31T21:37:33.067980+00:00.

| Stage | State | Job | Reason |
|---|---|---:|---|
| software_validation | pending | 486855 | None |
| llama8b_root_definition | planned |  |  |
| llama8b_computed_definition | planned |  |  |
| codellama34b_root_definition | planned |  |  |
| codellama34b_computed_definition | planned |  |  |
| source4096_root_definition | planned |  |  |
| source4096_computed_definition | planned |  |  |
| source8192_root_definition | planned |  |  |
| source8192_computed_definition | planned |  |  |
| llama8b_query_cache | planned |  |  |
| codellama34b_query_cache | planned |  |  |
| report | planned |  |  |

CPU-only cached-state work; full frozen regression gates all fits and extraction. Circular and permuted codes share dimensionality; source/prior/family controls remain explicit. Query caches prepare global-state work without fitting global-state probes. The controller checks every ten minutes; scientific failures require review.
