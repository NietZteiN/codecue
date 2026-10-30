# Complete-answer confidence follow-up: findings

The finite candidate-event bundle does **not show a clear Brier advantage over next-token confidence in any of the ten fixed matched comparisons**. Every conditional 95% interval crosses zero. This is a useful null result after qualifying the measurement implementation; it does not establish that complete-answer information is universally unhelpful.

| Checkpoint | Shared source context | Next-token Brier | Candidate-event Brier | Improvement [conditional 95%] |
|---|---|---:|---:|---|
| CodeLlama 34B | Source + interactions | 0.116641 | 0.116667 | −0.000026 [−0.002814, 0.002933] |
| Llama 3.1 8B | Source + interactions | 0.039430 | 0.039524 | −0.000094 [−0.001131, 0.000858] |

CodeLlama's source-only comparison has a positive conditional log-loss interval, while its four stronger-context log-loss intervals cross zero. Llama's event bundle worsens log loss in all five contexts by point estimate; the raw-neutral context's conditional interval favors next-token confidence. The [complete table](candidate_prediction_decision.md), [full comparison](candidate_prediction_results_v1.md) and [figure](candidate_prediction_alternatives_v1.svg) preserve all contexts, tiers, calibration bins, partition seeds and contrasts.

The earlier [next-token analysis](discovery_confidence_decision.md) still supports a CodeLlama discovery association beyond source interactions: Brier 0.123574 to 0.116641. Llama's corresponding Brier increment remains uncertain. The event alternative changes the finite numeral-plus-EOS definition, precision, tokenization and feature encoding; the comparisons do not isolate any one of those factors. Combining both bundles or conditioning event likelihood on the source oracle was not tested here.

## Completed scope and qualification

Both full event banks contain 6,144 audited prompts: 12,288 total, 33 canonical signed-integer candidates per prompt, and each checkpoint's declared EOS union. This represents 811,008 explicit event variants and 430,080 distinct prefix states. No answer was generated and no correctness value was exported as a measurement feature. Conditional confidence summaries cover only the declared finite event support, not every valid textual answer or the probability of task correctness.

The first attempts exposed real issues. EOS validation was corrected to recognize tokens explicitly marked special when a tokenizer convenience list omits them. Llama joint tokenization merged across the original boundary, so a separate versioned contract uses standalone numeral tokens with exact decoded concatenation after the unchanged saved prefix. BF16 batch geometry changed event probabilities even without caching; the original parity checks were retained, and the accepted measurements use FP32 SDPA with TF32 disabled. Eight-prompt per-event/scalar smoke comparisons passed on both checkpoints before full collection. Full audits check every prompt, scalar domain, input identity, chunk, precision contract and checksum.

GPU utilization averaged 97.2% for Llama and 99.2% for CodeLlama on two H200 GPUs. Collection-stage wall time was 549 and 2,562 seconds, respectively, excluding earlier Python/input startup and later auditing. The cached trie shares one prompt prefill and evaluates only continuation nodes, preserving the full declared event definition.

The 18-tier analysis completed 12,852 logistic fits across both checkpoints. All 479,232 parent-tier OOF probability values, fitted parameters, training normalizers, penalty selections, inner curves, group assignments and fallback records reproduced exactly. The 13-tier precursor completed another 9,072 logistic fits with exact eight-tier replay. Both analyses reuse the same consumed discovery targets and 24 structural groups per checkpoint; the three partition seeds are not independent experiments. Intervals condition on saved OOF predictions without refitting or multiplicity correction.

These results qualify stronger output-confidence comparators before any mechanistic prediction claim. They do not repair the failed computed-program gates, establish a selective binding mechanism, fit mechanism C, or evaluate untouched unfamiliar programs. Language-model training, unlearning and additional checkpoint downloads were not performed.

The later [joint-bundle follow-up](joint_confidence_findings.md) tests complementarity by retaining both feature bundles. CodeLlama improves in two of five fixed contexts by its conditional Brier intervals; all five Llama intervals cross zero. That nested comparison addresses a different question from the alternatives reported here, whose results remain unchanged.
