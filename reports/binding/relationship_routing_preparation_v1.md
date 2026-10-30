# Varied copy relationship source bank

Prepared 1,296 discovery-only source rows across 27 structural components and 81 directed definition graphs.
Training: 864 rows / 18 components / 54 graphs. Development: 432 rows / 9 components / 27 graphs.
Each component retains 8 numeric draws, all three first-copy parents and both neutral lexical forms.

The 432 lexical pairs with first parent v1 versus v2 have identical numeric states at every checkpoint and identical answers, but distinct versioned graphs.
The v3 first-parent control has a different value and v0 answer. Replacing initial v1 versus v2 with b+1 distinguishes the rewired first-copy descendants; all final variables are also compared without using final survival as the validity criterion.

Cross-split exact source, canonical AST, alpha structure and definition-graph overlap: zero. Independent Python full-trace checks: 3,240 distinct baseline/counterfactual programs.
Dataset SHA256: `7a76b3e7ce1b82c8f1b869c492246cb22e2b7f64f672b1dd89f724f64a56e9dd`. Review: `artifacts/binding/relationships/routing_preparation_review_v1.json`.

## Scope

- Source and oracle-target preparation only: no model responses, activations, probes or decoded graphs.
- Adaptive discovery bank, not confirmatory evidence or qualification of a new model family.
- Copy-only programs with four scalar variables and one final query, v0; no broad query replication.
- Canonical destination order is fixed: four initializations followed by v0, v1, v2, v3 copies.
- Numeric draws and lexical forms repeat a topology; they are not independent graph replications.
- Equal numeric states may occur across components; structural components, not numeric uniqueness, define the split.
- All oracle values, versions, dependencies, topology and counterfactual labels are targets, never readout features.
- Full-program oracle targets include future information; a prefix study must mask unseen definitions and output relevance.
- Syntactic ancestry and functional intervention effects are distinct; descendants can later be overwritten.
