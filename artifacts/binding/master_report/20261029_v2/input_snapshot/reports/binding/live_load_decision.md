# Decision after computed retention-frontier discovery

The full study completed and passed its data/response audits: **76,032 predictions** across Llama 3.1 8B Instruct and CodeLlama 34B Instruct. Both models failed the fixed arithmetic/clean-program reliability gate. All **247 regression tests pass**. The corrected cross-backend/cache diagnostics are also complete. This closes the registered behavioral experiment with an unfavorable feasibility result; it does not establish a binding-capacity mechanism.

## What was built and checked

The revised bank has 38,016 prompts per model: 36,864 main programs, 384 direct-literal arithmetic controls and 768 decomposed arithmetic controls. There are 384 distinct numeric states in sign-reversed pairs and 24 initialization-order structural components. Every relative stays within its assigned component; calibration controls are explicitly separate from structural generalization.

Across the irrelevant block, exactly 2, 3 or 4 current bindings can affect the output, while all eight variables remain defined. Scheduling preserves full final states, answers, three subtractions, statement/literal multisets and full input-token multisets/lengths within matched contrasts. Independent Python execution validates the rendered traces and canonical checkpoint interventions. Those interventions replace state at the checkpoint, preserving computations already completed. The frozen generator reproduces the complete dataset byte for byte.

Both tokenizer preflights passed: 9,216 schedule groups, 12,288 naming groups and 18,432 reassignment groups per model. Informative/misleading and reassignment lengths match; neutral naming may have different token lengths. Computed magnitudes are absent from numeric literal values, without claiming that every digit subtoken is absent.

Version 1 was retired before any model inference because deferred schedules had fewer defined variables. Version 2 initializes both result slots uniformly. The first native-Llama position check also exposed a token that includes a statement's trailing newline; the corrected check permits only trailing whitespace and rejects any token containing later code. Original data, sources, failed preflight and canceled jobs remain preserved.

## Main results

| Task | Llama 3.1 8B | CodeLlama 34B |
|---|---:|---:|
| Direct-literal three-subtraction control | 130/384 (33.85%) | 44/384 (11.46%) |
| Decomposed arithmetic control | 65/768 (8.46%) | 22/768 (2.86%) |
| Full retention-frontier program cohort | 2,883/36,864 (7.82%) | 2,163/36,864 (5.87%) |
| Entire evaluated cohort | 3,078/38,016 | 2,229/38,016 |
| Invalid responses | 0 | 16 |
| Fixed reliability gate | Failed | Failed |

The gate requires at least 90% accuracy, at most 5% invalid outputs and at least 24 examples in every registered calibration and neutral clean-program split/update/order cell. All behavioral cases were evaluated regardless of the outcome. Most errors are wrong integer answers, rather than unparseable responses; CodeLlama's 16 invalid answers occur in the direct-literal calibration cell.

For example, the recorded Llama response to `r0 = 9 - 7; r1 = 1 - 3; print(r0 - r1)` is `2`, while independent Python gives `4`. This example is from the full corpus, rather than a claim about the diagnostic sample or an identified internal cause.

The predeclared primary exploratory contrasts are retained below. Each uses 1,536 paired observations grouped into 24 structural components; intervals use 2,000 component-bootstrap draws without multiplicity adjustment.

| Model | Contrast | Difference | Exploratory 95% interval |
|---|---|---:|---:|
| Llama 8B | Four minus two live bindings, neutral, three updates | −1.37 percentage points | [−2.86, +0.26] |
| CodeLlama 34B | Same contrast | −0.91 points | [−2.02, +0.07] |
| Llama 8B | Naming × live load × updates interaction | +0.33 points | [−2.08, +2.54] |
| CodeLlama 34B | Same interaction | −0.20 points | [−1.04, +0.65] |

All 56 fixed contrasts per model and all split/naming/order/update cells appear in the [combined comparison](live_load_results_v2.md) and individual reports. Low clean/arithmetic reliability limits interpretation of the load contrasts. The measured intervals also do not identify an absent mechanism.

Scheduling and distance remain coupled despite the matching. In neutral three-update programs, total prompt length is constant within model, but checkpoint-to-query distances are 70/82/94 tokens for Llama's 2/3/4-live schedules and 85/100/115 for CodeLlama. Live-definition ages also differ. Program liveness alone is not a transformer memory lower bound or an isolated capacity manipulation.

## Debugging and independent replay

Post-hoc diagnostics replayed 396 exact inputs per model, retaining all relatives of one sign pair in training and one in development. Fixed hashes selected the groups without model scores. Twelve arithmetic controls per model also received independent full-prefix, uncached greedy decoding.

The first CodeLlama Transformers diagnostic stopped after one newline because `StopStringCriteria` matched the prompt-final newline plus the first generated newline. The corrected harness applies stop strings only to generated tokens, with an explicit regression test. The original vLLM study already used generated-text stopping and is unchanged. The initial diagnostic outputs remain archived as an invalid method for that comparison.

| Corrected diagnostic | Llama 8B | CodeLlama 34B |
|---|---:|---:|
| Transformers correct | 9/396 | 53/396 |
| vLLM correct on the same inputs | 10/396 | 54/396 |
| Matching valid parsed predictions | 358/396 | 375/396 |
| Transformers / vLLM invalid | 0 / 0 | 1 / 1 |
| Cached/uncached raw text matches on controls | 12/12 | 12/12 |
| Matching valid cached/uncached answers | 12/12 | 11/12 |

CodeLlama's remaining control has identical malformed text in both decoding paths, so it counts as raw agreement and not as a valid-answer match. Backend differences are preserved; these two components do not estimate global accuracy. The selected-group results show little accuracy improvement from switching backend, and the uncached checks reproduce the cached text. They do not establish correct computation or universal implementation equivalence. See the [corrected diagnostic report](live_load_backend_results_v2.md).

## Resources and consequence

| Main model job | Allocated elapsed time | Generation time | Generation throughput | Mean GPU utilization during monitored generation |
|---|---:|---:|---:|---:|
| Llama 8B | 359 s | 80.81 s | 470.4 requests/s | 88.75% |
| CodeLlama 34B | 790 s | 496.32 s | 76.6 requests/s | 98.01% |

Both used H200s, BF16, continuous batching and prefix caching. Generation throughput excludes startup; load/warmup alone took 179.42 and 192.51 seconds, and allocated elapsed time also includes imports/prepared-data loading. These figures describe this short-answer workload, rather than a cross-benchmark performance claim. Project accounting remains uncapped. Every finite workload, audit and report has completed.

The next feasibility step should separately register fresh arithmetic/readout diagnostics—for example, one-operation versus three-operation programs, literal versus stored intermediates and signed cases. A reasoning-trace protocol would be a separate experiment because it changes the model's computation. The current direct-answer gates and outcomes must remain preserved. The reliable computed regime, selective causal account and empirical frozen unfamiliar-program forecasts remain unfinished. No original final/extrapolation outcomes, optional model training, separate explanation-transfer project or unlearning extension were opened.

The [plan](live_load_plan.md), [main comparison](live_load_results_v2.md), [corrected backend report](live_load_backend_results_v2.md), source/job pointers and `artifacts/binding/live_load/` contain the complete reproduction and handoff record.
