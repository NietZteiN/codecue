# Decision after the published benchmark run

The completed external baseline contains 2,350 predictions on 1,550 released questions, using the same cached checkpoint. The [audited results](published_baseline_review.md) provide a cited behavioral reference without opening the generated final-test or extrapolation outcomes.

CRUXEval-O literal accuracy is 290/800 (36.25%) for direct and 298/800 (37.25%) for CoT. The net difference is only 1.00 percentage points. Both solve 249 questions; direct alone solves 41; CoT alone solves 49. Prompting and token budgets change jointly, so these counts do not isolate a reasoning mechanism.

Formatting is the substantial qualification. Direct falls to 3/800 after exact released string postprocessing followed by literal scoring, while CoT retains 298/800. Direct responses commonly echo a Python section before their explicit answer block. The native chat wrapper and robust answer-block extraction therefore matter greatly. Report both metrics; the larger direct count is not an official execution score or a reproduction of the published inference setup.

BBH tracking accuracy is 36.00% for 3 objects, 25.20% for 5 objects, 15.60% for 7 objects. Uniform guessing references are 1/3, 1/5 and 1/7. These descriptive benchmark counts do not establish a reliable tracking mechanism. The released sizes contain different questions and all use the same three-object demonstrations, so their differences are not a matched causal test of binding load. The audit retains answer-letter distributions and question-copy flags rather than excluding inconvenient outputs.

Use CRUXEval as an external code-output baseline and BBH as complementary arithmetic-free tracking evidence. Keep the released evaluations intact and label any later filtered, renamed or counterfactual derivatives separately. The next useful experiment is a fixed comparison of the released raw-completion serialization with the native chat wrapper on the same CRUXEval questions, retaining both postprocessing counts. Freeze that plan before new inference and do not select prompts by their scores. This should precede claims of reproducing published scores or selecting a new mechanism-study protocol.

The previous synthetic mechanism gates and their failures remain unchanged. No binding mechanism, held-out mechanistic forecast, second-family replication, training or unlearning result is established by these behavioral baselines. Existing conditional experiments 4–10 remain unexecuted under their saved rules.

Full inference used 31.93 GPU-allocation minutes (31.28 registered stage minutes), with 19.95 GiB peak allocated GPU memory. Across the initial study, the shared stage ledger records 42.75 of 240 allowed minutes, with no active leases. Framework startup outside registered stages is recorded in the SLURM allocation logs. No new checkpoint was downloaded.

The completed-run audit verifies every question ID, record hash, score, response-file hash and input-token sequence aggregate against actual-tokenizer preflight. The full regression job passed 133 tests; the final benchmark/audit/snapshot checks passed 49 tests after the error-text stability fix. Exact source pointers, commands, job IDs and limitations are in `artifacts/binding/published/continuation_handoff.json`.
