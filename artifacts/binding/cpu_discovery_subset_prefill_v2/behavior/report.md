# Binding behavioral discovery report

Completed 720 / 720 planned responses across 60 bases and 49 structural templates.

Exact accuracy: 0.028; template-cluster 95% bootstrap interval [0.004545454545454545, 0.05847953216374269]. Invalid outputs: 14; ambiguous diagnostic errors: 21.

Intervals in small cells can be degenerate and do not provide a power analysis. Compatible error labels describe outputs and cannot identify internal causes.

| Split | Control | Naming | Difference from neutral | 95% interval |
|---|---|---|---:|---|
| development | arithmetic_control | informative | 0.000 | [0.0, 0.0] |
| train | arithmetic_control | informative | 0.000 | [0.0, 0.0] |
| development | primary | informative | 0.000 | [0.0, 0.0] |
| train | primary | informative | 0.012 | [0.0, 0.041666666666666664] |
| development | arithmetic_control | misleading | 0.000 | [0.0, 0.0] |
| train | arithmetic_control | misleading | -0.012 | [-0.03409090909090909, 0.0] |
| development | primary | misleading | 0.000 | [0.0, 0.0] |
| train | primary | misleading | 0.024 | [0.0, 0.08333333333333333] |

Wall seconds: 2137.066527544055; CPU forward/generation seconds: 2106.886744476389. Peak allocated GPU bytes: None. Device: cpu.

See summary.json for every factorial cell, raw responses.jsonl for all attempts, and manifest.json for pinned identities.

No mechanistic conclusion or unfamiliar-program prediction is established by behavior alone. Final test data are sealed unless explicitly relabelled as discovery. Select one diagnostic error on development data before a focused intervention study.
