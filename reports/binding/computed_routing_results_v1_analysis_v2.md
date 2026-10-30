# Computed-expression routing discovery

All 576 baseline responses are audited (461 correct). The answer-digit boundary and generation-prefill checks passed on every baseline. The registered workload completed 0 intervention forwards. All cases are discovery data; generated final/extrapolation outcomes remain sealed.

| Family | Mapping | Query | Reset | Correct / n | Invalid |
|---|---:|---:|---|---:|---:|
| ownership | 0 | 0 | fixed | 71/72 | 0 |
| ownership | 0 | 1 | fixed | 72/72 | 0 |
| ownership | 1 | 0 | fixed | 65/72 | 0 |
| ownership | 1 | 1 | fixed | 1/72 | 0 |
| versions | 0 | 0 | fixed | 72/72 | 0 |
| versions | 0 | 1 | fixed | 60/72 | 0 |
| versions | 1 | 0 | fixed | 71/72 | 0 |
| versions | 1 | 1 | fixed | 49/72 | 0 |

The reliability gate requires ≥90% accuracy, ≤5% invalid outputs and at least 24 cases in every mapping/query cell of a family. Failed families retain all baseline outcomes and receive no interventions. Eligible families: none. The planned transfer site is an unchanged final operand token after one changed earlier operand. All relevant results are absent from every literal in both programs. This need not isolate an abstract sum representation; the vector could transport operand information for later recomputation.

| Family | Block | Condition | n affected / unchanged | Replacement, affected (%) | Replacement, unchanged (%) |
|---|---:|---|---:|---:|---:|
| ownership | — | skipped: gate failed | 0 | — | — |
| versions | — | skipped: gate failed | 0 | — | — |

No intervention or analytic intervention-control tests ran because the reliability gate failed. The final answer-vector condition is an answer-copy software control. These are next-token interventions, not complete-output intervention accuracy. Numeric variants, directions and two lexical realizations are not independent structural replications. No general binding register, computed-value abstraction or held-out error predictor is established.

Audit: `artifacts/binding/routing_extension/computed_routing/llama31_8b_v1/interventions/audit.json`. [Design](routing_extension_plan.md). Reproduce with `PYTHONPATH=src ../envs/probe-cu129/bin/python scripts/112_binding_routing_extension.py review configs/binding/competition/computed_routing_v1.json`.
