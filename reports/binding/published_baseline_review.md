# Published benchmark results and audit

All 2,350 planned predictions completed on `codellama/CodeLlama-7b-Instruct-hf` at `22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed`. One greedy completion per question/protocol; no training or prompt selection.

| Evaluation | Correct / questions | Literal / letter accuracy | Invalid | Token limit | Upstream postprocessing + literal correct |
|---|---:|---:|---:|---:|---:|
| cruxeval_o_direct | 290 / 800 | 36.25% | 25 | 8 | 3 |
| bbh_tracking_3 | 90 / 250 | 36.00% | 0 | 0 | — |
| bbh_tracking_5 | 63 / 250 | 25.20% | 1 | 0 | — |
| bbh_tracking_7 | 39 / 250 | 15.60% | 8 | 0 | — |
| cruxeval_o_cot | 298 / 800 | 37.25% | 48 | 27 | 298 |

CRUXEval numbers use a literal-only scorer without executing model output. The secondary count applies the exact upstream string postprocessing, then literal equality. Neither count reproduces the official execution evaluator or sampled pass@k. The unchanged released prompt content is inside the checkpoint native chat wrapper; this serialization differs from the release's raw completion harness.

Malformed and missing answers remain in the full denominator. A token-limited response can still be correct if it contains an accepted complete answer. The ten smoke queries overlap the full release and are not independent validation. The smoke-discovered direct answer-block parser bug was fixed and tested before full inference; its original artifacts and separate corrected scores remain available.

## Output diagnostics

| Task | Mean generated tokens | Begins a new question | Contains a Python section |
|---|---:|---:|---:|
| cruxeval_o_direct | 131.6 | 0 | 786 |
| bbh_tracking_3 | 134.5 | 2 | 0 |
| bbh_tracking_5 | 264.3 | 18 | 0 |
| bbh_tracking_7 | 412.3 | 56 | 0 |
| cruxeval_o_cot | 262.6 | 0 | 793 |

A response beginning a new question or copying a demonstration may still end in a format-valid letter. Format validity is not evidence that the requested task was solved faithfully. These flags are descriptive observations, not post hoc exclusions or changes to the score.

On the same 800 CRUXEval questions, both protocols are correct on 249; only direct on 41; only CoT on 49; both are incorrect on 461. This jointly compares prompting and generation budget, not an isolated causal effect of reasoning.

## Verification and resources

The audit checked the completed run identity, immutable response hash, source/data hashes, exact planned IDs and record hashes, all recomputed scores, and the aggregate hash of every recorded input-token sequence against the full actual-tokenizer preflight. Only process-specific AST object addresses inside parse-error text are normalized during comparison; every decision field must match exactly. No model inference or downloaded-program execution occurs during review.

Measured model-stage time: 1876.71 seconds; peak allocated GPU memory: 19.95 GiB. Stage time excludes framework startup before the registry opens; SLURM allocation time is recorded separately in the job logs. The shared ledger remains capped at four GPU-hours.

Run identity: `c66705be15fc7dd0c51843000a2ffd453ec6015f769ab7bee1307b5fdb548ba5`. Input-token aggregate: `0fe3ba3aa3bdf09d60ce909bee43cfa882829286ce426b7d659a2e4119317553`. Raw responses: `artifacts/binding/published/full_v2/published_behavior/responses.jsonl`. Audit: `artifacts/binding/published/full_v2_review.json`.

Existing generated final-test and structural-extrapolation outcomes remain sealed. These published benchmarks establish external behavioral baselines; their scores alone do not identify a binding mechanism or establish a new scientific contribution.

See [the evaluation plan and parser correction](published_evaluation_plan.md), [dataset/source details](published_datasets.md), [CRUXEval, ICML 2024](https://proceedings.mlr.press/v235/gu24c.html), and [BBH, Findings of ACL 2023](https://aclanthology.org/2023.findings-acl.824/).
