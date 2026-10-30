# Published benchmark baseline

Checkpoint: `codellama/CodeLlama-7b-Instruct-hf` at `22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed`. Greedy decoding, one completion per question. All released questions and targets are preserved.

Author prompt content is placed inside the native single-user instruction template, with the independently audited CodeLlama token boundary. This is a checkpoint-specific adaptation, not an exact reproduction of the papers' model/decoding setup.

Completion: 10/10 planned queries. Smoke questions overlap the full benchmark and are not independent validation.

| Task | Evaluated / planned | Correct | Accuracy | Invalid | Token limit |
|---|---:|---:|---:|---:|---:|
| cruxeval_o_direct | 2 / 2 | 0 | 0.00% | 2 | 0 |
| bbh_tracking_3 | 2 / 2 | 0 | 0.00% | 0 | 0 |
| bbh_tracking_5 | 2 / 2 | 1 | 50.00% | 0 | 0 |
| bbh_tracking_7 | 2 / 2 | 0 | 0.00% | 0 | 0 |
| cruxeval_o_cot | 2 / 2 | 1 | 50.00% | 0 | 0 |

Invalid answers count as incorrect. CRUXEval uses Python literal equality, including container equality; neither downloaded programs nor model output is executed. This differs from the official execution scorer, which can accept nonliteral expressions. A secondary count with the upstream string postprocessing followed by literal equality is retained in summary.json. BBH requires a final in-range option letter, either alone or after “the answer is” / “Answer:”.

CRUXEval direct/CoT receive the released demonstrations; BBH receives all three released CoT demonstrations after its metadata separator. Generation stops on EOS, the CRUXEval closing answer tag or a new BBH question, or the configured token ceiling. Missing and truncated answers remain in the denominator. No benchmark score selects or changes a prompt.

These are public external behavioral baselines. Existing generated final-test and structural extrapolation outcomes remain sealed; the earlier synthetic mechanism gate is unchanged.

Sources: [CRUXEval, ICML 2024](https://proceedings.mlr.press/v235/gu24c.html), [BBH, Findings of ACL 2023](https://aclanthology.org/2023.findings-acl.824/). Exact commits, file hashes, configuration and source snapshot are recorded alongside the responses.
