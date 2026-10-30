# Interpreting the completed grammar diagnostic

All 60 banks and the independent retained-score replay passed. This table uses the fixed hidden layer 24/site 7 endpoint, averaging all three weighting seeds. All-eight accuracy requires every write and parent identity correct.

| Decision rule | Llama 8B | CodeLlama 34B |
|---|---:|---:|
| Original free joint | 6.019% | 13.056% |
| Original free marginal | 8.796% | 27.778% |
| Broad joint-score grammar | 16.204% | 25.093% |
| No-self joint-score grammar (secondary) | 20.648% | 31.944% |
| Broad owner-only grammar | 25.556% | 46.204% |
| No-self owner-only grammar (secondary) | 28.333% | 49.352% |
| Source-owner/TRAIN-version prior + broad joint grammar | 62.222% | 62.222% |
| Source-owner scores + broad owner-only grammar | 100.000% | 100.000% |

Joint-score constraints improve the original free-joint endpoint, whose whole-eight monotonicity is guaranteed on these finite lawful cases. That does not guarantee improvement over the original marginal rule: CodeLlama 34B joint grammar is lower than that reference. The stronger source-owner/TRAIN-version-prior comparator with the same joint grammar also exceeds both hidden joint endpoints.

Owner-only decoding removes version-specific score evidence while the external counter rule supplies versions. Its larger recovery therefore does not require version-sensitive neural scores. Visible source owners plus counters reconstruct all identities at 100% without hidden-state decoding. These outcomes support decoder-assisted reconstruction, with maintained state, natural causal use, old-value retrieval and unfamiliar-program generalization unresolved.

The no-self condition is a separately declared global cohort prior. Sham truth may violate either grammar; its constrained exact ceiling and own-task accuracy remain separate from the same predictions evaluated against real truth. No matched-selectivity claim or new confidence interval is made.

Joint grammar versus original marginal argmax, across three dependent estimator views of 1,440 DEV cases:
- Llama 8B: 532 whole-eight corrections and 212 harms among 4,320 bank-case views. These are repeated views of the same 1,440 cases, not 4,320 independent programs.
- CodeLlama 34B: 424 whole-eight corrections and 540 harms among 4,320 bank-case views. These are repeated views of the same 1,440 cases, not 4,320 independent programs.

All 2,191 tests passed; the exact 106-file test archive verified; all three jobs completed with exit 0:0. There were zero new model calls, fits or parameter applications. The full 960-cell grid, all 60 detailed diagnostics and exact objective pairs remain linked by the [publication proof](../../artifacts/binding/identity_grammar/20261028_v1/publication_review_v1.json). The [summary](identity_grammar_summary_v1.md) and [decision](identity_grammar_decision_v1.md) retain the original declared scope.
