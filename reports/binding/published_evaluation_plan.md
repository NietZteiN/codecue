# Published benchmark evaluation plan

Fixed before benchmark model inference on October 25, 2026. This continuation measures behavior on cited external datasets; it does not change the earlier synthetic mechanism gates or open the generated final-test or extrapolation outcomes.

Use the already cached `codellama/CodeLlama-7b-Instruct-hf`, model and tokenizer revision `22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed`, BF16, eager attention, and the audited `codellama_official_boundary_v1` serialization. No checkpoint training or new checkpoint download is needed. The released prompt content is inside a single user message in the checkpoint's chat template. The CRUXEval reference harness does not support instruction tokens; this wrapper is therefore an explicit checkpoint adaptation, not an exact reproduction of its inference harness.

| Evaluation | Released examples | Prompt | Maximum new tokens |
|---|---:|---|---:|
| CRUXEval-O direct | 800 | Exact released `make_direct_output_prompt` | 512 |
| BBH Tracking Shuffled Objects, three objects | 250 | Released three CoT demonstrations | 1,024 |
| BBH Tracking Shuffled Objects, five objects | 250 | Released three CoT demonstrations | 1,024 |
| BBH Tracking Shuffled Objects, seven objects | 250 | Released three CoT demonstrations | 1,024 |
| CRUXEval-O CoT | 800 | Exact released `make_cot_output_prompt` | 1,024 |

This is 2,350 planned full-run predictions on 1,550 released questions. Use release order, one greedy completion per question/protocol, batch size eight, and no accuracy-based prompt selection. Remove BBH's canary/metadata header at its separator, preserve its demonstration content, and append the question and `A: Let's think step by step.`. Do not truncate prompts. The CPU tokenizer preflight verifies all prompt lengths against a 4,096-token context ceiling, checks the complete prompt against reference SentencePiece tokenization, and roundtrips every gold answer through the scorer. Both the source and configuration hashes must match at inference time.

At the pinned BBH commit, the three downloaded tracking prompt files have identical SHA-256 hashes and contain three-object demonstrations. The five- and seven-object evaluations intentionally retain that released demonstration content; no size-specific examples are invented or substituted. This is another reason not to treat differences between the released sets as a matched causal manipulation of binding load.

The smoke run uses the first two release-order examples of each of the five evaluations: ten queries total, selected before outcomes. It verifies runtime, output handling and resource needs. It is not a validation set and overlaps the full run. Its scores do not decide whether the full benchmark runs or which prompts it uses. If a harness defect is found, document the revision and use a new immutable run identity.

Generation stops on EOS, the CRUXEval closing answer tag, the next BBH question marker, or the token ceiling. The initial scorer was `python_literal_equality_and_bbh_final_letter_v1`, corrected to `v2` after the smoke and before any full-run inference as documented below. CRUXEval accepts a literal or one equality assertion with the unchanged released function input; CoT requires an answer tag. It compares the literal against the released output with Python equality, covering strings, containers, numbers, booleans, bytes and None. No downloaded program or generated code is executed. This literal-only metric differs from the official execution evaluator, which can credit nonliteral expressions. Also retain a secondary literal-only count after the exact upstream string postprocessing; its naive equality-string split has a known edge case. Do not call either count the official execution score or a reproduction of published sampled pass@k.

BBH accepts a final in-range `(A)`–`(G)` answer alone or after `the answer is` / `Answer:`. No answer recovery from intermediate prose or option frequencies. Malformed, absent and token-limited missing answers count as incorrect; publish invalid and token-limit counts. Report full benchmark accuracy only after complete coverage; a partial run reports its evaluated count and evaluated accuracy explicitly.

All GPU stage time is charged to the existing shared four-hour ledger, with a 1,200-second smoke ceiling and a 10,000-second full-run ceiling, subject to the shared remaining budget. Leave a conservative final-batch margin. Record exact source/data/prompt hashes, input and output token IDs, raw responses, model/runtime configuration, stop reasons, scoring, SLURM jobs and budget usage. Raw releases stay unchanged and all compiled records carry their source paths and original IDs or release-order indices. Partial runs may resume only under the identical source/config/data/environment identity.

Primary sources and pinned downloads are listed in [published_datasets.md](published_datasets.md). Data, prompt and evaluator commits and hashes are under `artifacts/binding/benchmarks/`. The original configurations are `configs/binding/published/{smoke,full}_v1.json`; only the smoke ran under v1. The executed full-run configuration is `full_v2.json`.

## Smoke-discovered parser correction

SLURM job 476575 completed all ten smoke queries. It used 41.349 stage seconds (82 seconds of GPU allocation including framework startup) and a peak of 15,428,782,592 allocated GPU bytes. The direct-mode responses included an echoed `[PYTHON]` section followed by a legitimate line-start `[ANSWER]` block. Version 1 only extracted that later block in CoT mode and incorrectly marked both direct responses invalid. Version 2 recognizes a line-start answer block in either mode, while retaining literal parsing and exact assertion-input validation. A regression test covers this response form. This is a parser correction; prompts, checkpoint, decoding, ceilings, example selection and task order remain fixed.

Preserve the original v1 smoke responses, scoring, source snapshot and manifest. Recompute scores in a separate provenance-checked `smoke_v1_rescored_v2.json` artifact without repeating inference. Freeze corrected source and `full_v2.json`, rerun complete tokenizer/gold-scorer QA and relevant tests, and then run all 2,350 full predictions. No full benchmark outcomes were available when this correction was made. The exact upstream-postprocessing literal count remains separate and unchanged.

## Audit error-text stability

During the frozen full run, audit development identified that Python's `ast.literal_eval` includes a process-specific AST object address in some invalid-expression error messages. Recomputing the same invalid score can therefore produce different diagnostic text. The audit normalizes only this address and requires every other field, including validity and correctness, to match. A regression test verifies that it cannot hide a changed scoring decision or a different AST error type.

The active inference snapshot remains unchanged. The current working implementation also canonicalizes these addresses when recording future scores so legitimate future resumes are deterministic. That bookkeeping fix changes no prediction, parsing decision or accuracy. Historical inference and audit source snapshots remain separately pinned; reproduce this run using `published_source_v2.json` and its audit using `published_review_source_v3.json`. For a new run under the updated implementation, choose fresh run/preflight/report paths, freeze source, and perform tokenizer QA before inference.
