# CRUXEval serialization comparison

All 800 released questions were evaluated under direct and CoT completion prompts. The native-chat arm reuses the previously completed run on those same questions. Checkpoint, dtype, greedy decoding, batch size, task content, scoring functions and new-token ceilings are matched. The follow-up was planned after observing the earlier formatting gap; it is not an independent confirmatory dataset.

| Protocol | Chat: released processing + literal | Completion: released processing + literal | Chat: answer-block literal | Completion: answer-block literal |
|---|---:|---:|---:|---:|
| cruxeval_o_direct | 3/800 (0.38%) | 295/800 (36.88%) | 290/800 (36.25%) | 295/800 (36.88%) |
| cruxeval_o_cot | 298/800 (37.25%) | 290/800 (36.25%) | 298/800 (37.25%) | 290/800 (36.25%) |

The first metric uses released string postprocessing followed by Python literal equality. The second extracts an explicit answer block and validates the assertion input. Neither executes model output or credits nonliteral expressions, and neither is the paper's sampled execution pass@k. Malformed and missing responses remain in the denominator.

Devices: native baseline on NVIDIA H100 80GB HBM3; completion on NVIDIA H100 80GB HBM3; native replay on NVIDIA H100 80GB HBM3. Jobs were eligible for H100 or H200 after resource unavailability. The native replay tests a small fixed batch; even exact replay does not rule out all numerical device effects on the remaining questions. This is a limitation of interpreting the paired differences as serialization effects.

Completion inputs contain exactly one BOS followed by reference SentencePiece encoding of the unchanged released prompt text. Every recorded input-token sequence matches actual-tokenizer preflight. The generation and prompt/scoring function ASTs were checked against the frozen native baseline; model loading/tokenizer adapter source is identical.

Native replay: all 16 prompt sequences match; 16/16 output-token sequences match; 16/16 correctness decisions match. Smoke/replay questions overlap the full release and are not independent validation.

| Protocol | Chat / completion invalid | Chat / completion token-limited | Chat / completion Python-section echoes |
|---|---:|---:|---:|
| cruxeval_o_direct | 25 / 13 | 8 / 8 | 786 / 0 |
| cruxeval_o_cot | 48 / 45 | 27 / 38 | 793 / 0 |

Paired correctness transitions for both metrics, complete provenance and checksums are in `artifacts/binding/serialization/comparison_v1.json`. Existing generated final-test and extrapolation outcomes remain sealed. This comparison does not identify a binding mechanism or change the earlier synthetic mechanism gates.

See [the fixed plan](serialization_plan.md) and [earlier benchmark results](published_baseline_review.md).
