# Decision after slot-complete overwrite decoding

The completed study supports scoped recovery of statement-based relationships and scalar versions from hidden states on new discovery graph families. Recovery remains incomplete, and these readouts do not establish full variable/version binding or natural causal use.

At the nominated layer 24/final-assignment site 7, whole-task accuracy requires all four target heads to be correct. Every point below averages the three fixed weighting seeds; all other layers, sites and controls remain in the [published findings](diversity_decoding_findings_v1.md) and complete CSV.

| Model | Task | Hidden | Character baseline | TRAIN prior |
|---|---|---:|---:|---:|
| CodeLlama 34B | Current defining statements | 69.815% | 6.481% | 0.000% |
| CodeLlama 34B | Current version numbers | 35.093% | 9.537% | 0.000% |
| CodeLlama 34B | Copy-parent defining statements | 37.222% | 7.963% | 1.111% |
| Llama 3.1 8B | Current defining statements | 56.389% | 6.296% | 0.000% |
| Llama 3.1 8B | Current version numbers | 22.870% | 9.630% | 0.000% |
| Llama 3.1 8B | Copy-parent defining statements | 30.370% | 7.963% | 1.111% |

Hidden readouts exceed the declared character and prior baselines on all three tasks for both checkpoints. This compares these decoder pipelines; it does not show that the source lacks the information or that the model naturally uses a recovered relation. The source-keyed sham task has different class marginals and may not define a lawful graph; its low whole-task accuracy is a separate control result.

The source bank contains 60 canonical families, with 45 TRAIN and 15 DEV families. Each DEV family contributes 96 related rows, so row-weighted and equal-family whole-task accuracies agree. All four final version classes occur in every slot. Fifteen families, related source variants and three dependent weighting seeds support descriptive discovery; no confidence interval, new bootstrap or significance claim is added.

Current-definition and parent heads predict statement indices. Scalar-version heads predict ordinal versions separately. Mapping a statement prediction to a natural variable@version identity requires a source-oracle map and must be labeled as an assisted postmetric. The prepared identity diagnostic can characterize errors under that qualification; it is not a new learned binding decoder. Parent identities must use the referent at consumer read time, rather than its later status.

Graph families, version coverage, TRAIN sample size and effective regularization changed together. Comparisons with earlier banks cannot isolate which change improved or weakened recovery. Definition age, position and dependency depth also remain coupled. Novelty is relative to the two named graph-exclusion banks.

Execution is complete: 11,520 distinct and attempted prefills, no generated answers, 90 readout factorizations, 518,400 exact saved-parameter replay case rows and 2,044 passing software tests. Both numerical replay proofs and the independent metadata review passed. The publisher reproduced its outputs byte for byte. These facts complete execution and reproducibility work, while the original behavioral gates, causal-mechanism decisions and frozen unfamiliar-program evaluation remain open.
