# Published benchmark results and audit

All 1,600 planned predictions completed on `codellama/CodeLlama-7b-Instruct-hf` at `22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed`. One greedy completion per question/protocol; no training or prompt selection.

| Evaluation | Correct / questions | Literal / letter accuracy | Invalid | Token limit | Upstream postprocessing + literal correct |
|---|---:|---:|---:|---:|---:|
| cruxeval_o_direct | 295 / 800 | 36.88% | 13 | 8 | 295 |
| cruxeval_o_cot | 290 / 800 | 36.25% | 45 | 38 | 290 |

CRUXEval numbers use a literal-only scorer without executing model output. The secondary count applies the exact upstream string postprocessing, then literal equality. Neither count reproduces the official execution evaluator or sampled pass@k. Serialization: released CRUXEval prompt content as a completion prefix; one BOS plus reference SentencePiece encoding. Greedy decoding and new-token ceilings differ from sampled paper settings.

Malformed and missing answers remain in the full denominator. A token-limited response can still be correct if it contains an accepted complete answer. Smoke questions overlap the full release and are not independent validation. The previously smoke-discovered direct answer-block parser bug was fixed and tested before full inference; its original artifacts and separate corrected scores remain available.

## Output diagnostics

| Task | Mean generated tokens | Begins a new question | Contains a Python section |
|---|---:|---:|---:|
| cruxeval_o_direct | 38.0 | 0 | 0 |
| cruxeval_o_cot | 291.4 | 0 | 0 |

A response beginning a new question or copying a demonstration may still end in a format-valid letter. Format validity is not evidence that the requested task was solved faithfully. These flags are descriptive observations, not post hoc exclusions or changes to the score.

On the same 800 CRUXEval questions, both protocols are correct on 207; only direct on 88; only CoT on 83; both are incorrect on 422. This jointly compares prompting and generation budget, not an isolated causal effect of reasoning.

## Verification and resources

The audit checked the completed run identity, immutable response hash, source/data hashes, exact planned IDs and record hashes, all recomputed scores, and the aggregate hash of every recorded input-token sequence against the full actual-tokenizer preflight. Only process-specific AST object addresses inside parse-error text are normalized during comparison; every decision field must match exactly. No model inference or downloaded-program execution occurs during review.

Measured model-stage time: 1144.80 seconds; peak allocated GPU memory: 18.65 GiB. Stage time excludes framework startup before the registry opens; SLURM allocation time is recorded separately in the job logs. The shared ledger remains capped at four GPU-hours.

Run identity: `129b71377ea3c139a4235b3e4bee9f794c25d2bb99d5bdb7235ac530a8228ca6`. Input-token aggregate: `fb3e6eeaabb9a49657b1f89cb1647210c4e262467a845d64737149ac90f93299`. Raw responses: `artifacts/binding/serialization/completion_full_v1/published_behavior/responses.jsonl`. Audit: `artifacts/binding/serialization/completion_full_v1_review.json`.

Existing generated final-test and structural-extrapolation outcomes remain sealed. These published benchmarks establish external behavioral baselines; their scores alone do not identify a binding mechanism or establish a new scientific contribution.

See [the evaluation plan and parser correction](published_evaluation_plan.md), [dataset/source details](published_datasets.md), [CRUXEval, ICML 2024](https://proceedings.mlr.press/v235/gu24c.html), and [BBH, Findings of ACL 2023](https://aclanthology.org/2023.findings-acl.824/).
