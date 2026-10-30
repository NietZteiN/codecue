# Joint confidence follow-up

Combining the saved next-token and finite candidate-event statistics improves CodeLlama discovery prediction in two of the five fixed source contexts by the conditional Brier intervals. With source interactions, Brier falls from **0.116641 to 0.113499**, an improvement of **0.003142 [0.000158, 0.006277]**. All five Llama intervals cross zero. These intervals condition on existing out-of-fold predictions; they do not establish an independently confirmed gain.

| Checkpoint | Shared context | Next-token Brier | Joint Brier | Improvement [conditional 95%] |
|---|---|---:|---:|---|
| CodeLlama 34B | Source | 0.125365 | 0.117984 | 0.007381 [0.002367, 0.012872] |
| CodeLlama 34B | Source + interactions | 0.116641 | 0.113499 | 0.003142 [0.000158, 0.006277] |
| CodeLlama 34B | Interactions + raw neutral | 0.115091 | 0.112318 | 0.002773 [−0.000012, 0.005795] |
| CodeLlama 34B | Interactions + oracle + raw neutral | 0.087942 | 0.086017 | 0.001925 [−0.000915, 0.004543] |
| CodeLlama 34B | Interactions + oracle + scored neutral | 0.083800 | 0.081426 | 0.002373 [−0.000121, 0.004862] |
| Llama 3.1 8B | Source | 0.039576 | 0.039731 | −0.000155 [−0.000683, 0.000375] |
| Llama 3.1 8B | Source + interactions | 0.039430 | 0.039503 | −0.000073 [−0.000586, 0.000423] |
| Llama 3.1 8B | Interactions + raw neutral | 0.039596 | 0.039623 | −0.000027 [−0.000776, 0.000657] |
| Llama 3.1 8B | Interactions + oracle + raw neutral | 0.035738 | 0.034883 | 0.000856 [−0.000143, 0.001757] |
| Llama 3.1 8B | Interactions + oracle + scored neutral | 0.034994 | 0.034253 | 0.000741 [−0.000434, 0.001857] |

The [earlier event-alternative study](candidate_prediction_findings.md) changed the measurement bundle and found no clear matched Brier gain. This follow-up adds both bundles to the same predictor, so it tests their complementarity within the fitted feature class. It retains all 18 parent tiers unchanged and adds five joint tiers. The [full decision table](joint_confidence_decision.md) also preserves every event-to-joint and source-to-joint comparison; the [complete analysis](joint_confidence_results_v1.md) retains all 23 tiers and 55 contrasts. The [fixed primary figure](joint_confidence_increments_v1.svg) shows both proper losses for every context and checkpoint.

The two runs completed **16,632 logistic fits**: 12,852 exact parent replays and 3,780 joint-tier fits. All **663,552** parent out-of-fold probability values reproduced exactly, along with fitted parameters, normalizers, selected penalties, inner curves, fold groups and fallback records. The parent feature bytes are unchanged. Both checkpoints still use 6,144 consumed discovery targets and 24 structural groups each; partition seeds 17, 29 and 43 are repeated partitions of those same targets.

The [protocol declaration](../../artifacts/binding/joint_confidence/protocol_registration_v1.json) preceded these fits, after the earlier discovery results were known. It is an adaptive discovery follow-up, not a confirmatory preregistration. The fitting source is [pinned separately](../../artifacts/binding/joint_confidence/source_v1.json). Conditional intervals use 2,000 structural-group bootstrap draws without refitting or multiplicity adjustment.

The joint tier requires both original measurements: one BF16 next-token prefill plus FP32 finite-event scoring over 33 numerals and the declared EOS union. The existing banks were reused; no new language-model query occurred. The finite support excludes other valid answer strings, and the exported features contain no winning token/candidate identity or target response/correctness. This provides a stronger observational comparator for a future mechanism study. It does not repair the failed computed-program gates, qualify mechanism C, or open original final/extrapolation outcomes.
