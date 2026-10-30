# Binding behavioral discovery report

Completed 144 / 144 planned responses across 12 bases and 12 structural templates.

Exact accuracy: 0.188; template-cluster 95% bootstrap interval [0.0625, 0.3333333333333333]. Invalid outputs: 0; ambiguous diagnostic errors: 2.

Intervals in small cells can be degenerate and do not provide a power analysis. Compatible error labels describe outputs and cannot identify internal causes.

| Split | Control | Naming | Difference from neutral | 95% interval |
|---|---|---|---:|---|
| development | arithmetic_control | informative | 0.000 | [0.0, 0.0] |
| train | arithmetic_control | informative | -0.056 | [-0.16666666666666666, 0.0] |
| development | primary | informative | 0.000 | [0.0, 0.0] |
| train | primary | informative | 0.000 | [0.0, 0.0] |
| development | arithmetic_control | misleading | 0.000 | [0.0, 0.0] |
| train | arithmetic_control | misleading | -0.111 | [-0.3333333333333333, 0.0] |
| development | primary | misleading | 0.000 | [0.0, 0.0] |
| train | primary | misleading | 0.000 | [0.0, 0.0] |

Wall seconds: 411.52902444358915; CPU forward/generation seconds: 410.27729883324355. Peak allocated GPU bytes: None. Device: cpu.

See summary.json for every factorial cell, raw responses.jsonl for all attempts, and manifest.json for pinned identities.

No mechanistic conclusion or unfamiliar-program prediction is established by behavior alone. Final test data are sealed unless explicitly relabelled as discovery. Select one diagnostic error on development data before a focused intervention study.
