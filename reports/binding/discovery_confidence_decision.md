# Discovery confidence prediction

The completed analysis adds four label-free next-token confidence statistics to the existing source, neutral-query and oracle-access tiers. **CodeLlama 34B shows a useful discovery association beyond the source-interaction baseline. Llama 3.1 8B has a smaller, uncertain Brier increment in that comparison, while log loss improves.** These are exploratory results on already-consumed discovery data; unfamiliar-program confirmation and mechanism C remain unrun.

Both checkpoints retain all 6,144 transformed targets and 24 structural groups, six outer/five inner folds, partition seeds 17/29/43 and the original penalty grid. Thirteen fixed tiers and all 24 declared comparisons are reported. The 9,072 logistic fits include 5,292 baseline replay fits and 3,780 new confidence-tier fits. Prior-only estimates are additional closed-form fits. No language-model weights were trained.

| Checkpoint | Baseline | Baseline Brier | + confidence Brier | Improvement [conditional 95%] | Baseline log loss | + confidence log loss |
|---|---|---:|---:|---|---:|---:|
| CodeLlama 34B | Source + interactions | 0.123574 | 0.116641 | +0.006933 [0.002194, 0.011878] | 0.380577 | 0.361757 |
| Llama 3.1 8B | Source + interactions | 0.039673 | 0.039430 | +0.000243 [−0.000755, 0.001285] | 0.137222 | 0.133126 |
| CodeLlama 34B | Interactions + source oracle + raw neutral | 0.091608 | 0.087942 | +0.003666 [0.001484, 0.005842] | 0.293049 | 0.283594 |
| Llama 3.1 8B | Interactions + source oracle + raw neutral | 0.037215 | 0.035738 | +0.001477 [0.000134, 0.002940] | 0.131400 | 0.124886 |

For the source-interaction comparison, log-loss improvements are +0.018820 [0.004961, 0.033520] on CodeLlama and +0.004095 [0.001358, 0.006860] on Llama. CodeLlama's five fixed marginal confidence comparisons have positive conditional Brier intervals. Llama's oracle-plus-raw-neutral comparison does too; its other four Brier intervals cross zero. These intervals condition on saved OOF predictions, without refitting or multiplicity correction. Three partition seeds reuse the same targets and are not independent replications.

Source capacity remains consequential. CodeLlama source-only plus confidence has Brier 0.125365, while source interactions without confidence achieve 0.123574. Confidence therefore does not replace a strong source baseline. Oracle tiers also retain their stronger information access; their improvements cannot be presented as oracle-free comparisons.

Exact replay checks passed for all **294,912 baseline OOF probability values** across the two checkpoints. All baseline group assignments, outer/inner models, normalizers, selected penalties, inner curves and fallback records match the earlier eight-tier analysis exactly. The full [comparison](discovery_confidence_results_v1.md), per-checkpoint reports and machine-readable reviews retain every tier, condition/query/load/split cell, calibration bin and fixed contrast.

The four confidence features are entropy, maximum next-token probability, top-two logit margin and EOS mass at the exact saved prompt. Vocabulary size, token identity, target response text and target correctness are excluded from features. Existing correctness appears only as the supervised label. Each B tier receives one target prefill; neutral-query counts and oracle/reference access are separately declared. The new Transformers BF16/SDPA measurement backend differs from the original vLLM outcome backend. Next-token sign/format confidence is distinct from complete integer-answer event confidence.

The full-answer tooling exposed two separate qualification issues. Llama's joint text tokenizer can merge a negative sign across the saved prompt boundary. A CPU diagnostic found 128 such failures among 264 smoke candidates, while all standalone numeral continuations decoded exactly after the unchanged saved prefix. A separately versioned decode-verified continuation rule passed whole-bank validation. CodeLlama's BF16 cached/full-prefix comparisons also vary with batch geometry; even two full-prefix batch sizes disagree. Those failures are preserved, and FP32 with TF32 disabled passed the unchanged per-event/scalar thresholds, and both full banks completed. Failed candidate attempts are measurement diagnostics, not failed scientific reliability gates or changes to the completed next-token prediction results.

The [complete-answer follow-up](candidate_prediction_findings.md) is now complete: its ten matched Brier comparisons have intervals crossing zero. A selected causal explanation, selective intervention, genuine final registration and frozen unfamiliar-program forecasts remain separate scientific prerequisites. Optional language-model training and unlearning have not begun.
