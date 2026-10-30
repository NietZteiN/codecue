# Decision from source-oracle-assisted identity diagnostics

Both analysis and closure completed with exit 0:0. This independent review verified all 211 handoff pins, all 90 fixed cells and their category, graph/profile and scalar/definition joint denominators. The completed prediction replay proof covers 129,600 DEV prediction rows. This review streamed hashes and read JSON/report metadata; it did not load score/prediction arrays or rerun analysis.

The phase supports a descriptive error taxonomy for existing decoders. A source-oracle map supplies owner/version meaning after fixed statement-index predictions. It does not establish independently learned full bindings or a causal mechanism. The original layer 24/site 7 endpoint and weighting seeds 17/29/43 remain fixed.

| Model | Features/method | Target | Exact statement/scalar | Owner correct | Version number equal |
|---|---|---|---:|---:|---:|
| Llama 3.1 8B | hidden | current_definition | 86.782% | 92.315% | 88.750% |
| Llama 3.1 8B | hidden | current_version | 69.097% | undefined | 69.097% |
| Llama 3.1 8B | hidden | copy_parent | 76.250% | 78.495% | 88.565% |
| Llama 3.1 8B | prefix text | current_definition | 58.310% | 77.801% | 67.060% |
| Llama 3.1 8B | prefix text | current_version | 58.657% | undefined | 58.657% |
| Llama 3.1 8B | prefix text | copy_parent | 42.546% | 55.069% | 68.032% |
| Llama 3.1 8B | TRAIN prior | current_definition | 41.667% | 100.000% | 41.667% |
| Llama 3.1 8B | TRAIN prior | current_version | 41.667% | undefined | 41.667% |
| Llama 3.1 8B | TRAIN prior | copy_parent | 26.806% | 27.778% | 53.889% |
| CodeLlama 34B | hidden | current_definition | 91.227% | 96.250% | 92.060% |
| CodeLlama 34B | hidden | current_version | 76.458% | undefined | 76.458% |
| CodeLlama 34B | hidden | copy_parent | 81.898% | 83.866% | 91.204% |
| CodeLlama 34B | prefix text | current_definition | 58.356% | 77.708% | 66.968% |
| CodeLlama 34B | prefix text | current_version | 58.495% | undefined | 58.495% |
| CodeLlama 34B | prefix text | copy_parent | 42.407% | 54.931% | 67.986% |
| CodeLlama 34B | TRAIN prior | current_definition | 41.667% | 100.000% | 41.667% |
| CodeLlama 34B | TRAIN prior | current_version | 41.667% | undefined | 41.667% |
| CodeLlama 34B | TRAIN prior | copy_parent | 26.806% | 27.778% | 53.889% |

Each point averages three seed-specific rates on 5,760 defined target-head decisions per seed: four supplied-slot or copy-event heads on 1,440 DEV cases. These pooled-head rates are distinct from joint four-head whole-state recovery. Each of 15 families contributes 96 rows, so row and equal-family means agree. Scalar-version heads do not predict owners; their owner field is undefined.

The strongest caution is the prior: current-definition owner correctness is 100%, while exact statement/version recovery is 41.667%. Supplied slots, fixed initialization order and the source map can identify an owner even when the chosen defining statement is obsolete. Hidden-owner accuracy therefore does not isolate a learned owner code. The full source determines every target; character n-grams are a limited source encoding.

| Model, hidden direct | Definition: same owner, wrong version | Different owner, current | Different owner, obsolete | Parent: same owner, wrong version | Parent: different owner, current at read time | Parent: different owner, obsolete at read time |
|---|---:|---:|---:|---:|---:|---:|
| Llama 3.1 8B | 5.532% | 5.255% | 2.431% | 2.245% | 19.213% | 2.292% |
| CodeLlama 34B | 5.023% | 2.616% | 1.134% | 1.968% | 15.694% | 0.440% |

Current-definition status is evaluated at the capture checkpoint; each parent is evaluated immediately before its consumer. A correct read-time parent may become obsolete later. Wrong owners can nevertheless match the target ordinal version, so version-number equality can exceed exact identity. These are decoder mistakes, not identified causes of language-model answer errors.

| Model, hidden direct | Scalar right, definition wrong | Scalar wrong, definition right | Both right | Both wrong | Scalar and mapped version agree while scalar is wrong |
|---|---:|---:|---:|---:|---:|
| Llama 3.1 8B | 4.931% | 22.616% | 64.167% | 8.287% | 6.366% |
| CodeLlama 34B | 3.356% | 18.125% | 73.102% | 5.417% | 5.139% |

The joint tables retain every slot, graph and seed. Correct scalar versions can accompany incorrect definitions; scalar/definition agreement can be jointly wrong. Percentages use the same 5,760 target-head decisions per seed. Initial-site parent heads remain undefined rather than counted correct; sham accuracy stays on its separate original task.

Completion covers 90 saved-score banks, 518,400 original saved-score rows checked, 129,600 prediction rows and 2,088 passing regression tests. The 69-task inventory is refreshed to 57 ready / 9 scientific / 3 optional. There are no new model prefills, answers, fits or parameter applications. No confidence interval, significance claim, reliability-gate rescue, state-tracking mechanism or unfamiliar-program prediction is established.

All-slot versions 1–4 and novel overwrite graphs broaden support, but the language remains four literal roots and four copies with supplied slots and fixed initialization. Fifteen DEV families, dependent numeric/rotation/lexical/query relatives, estimator seeds and source-oracle assistance bound interpretation. General owner/version, causal and predictive research decisions remain open.

See the [fixed plan](diversity_identity_review_plan_v1.md), [completed diagnostic report](diversity_identity_review_findings_v1.md), [two-model diversity findings](diversity_decoding_findings_v1.md) and [independent metadata review](../../artifacts/binding/diversity_identity_review/20261028_v1/independent_findings_review_v1.json).
