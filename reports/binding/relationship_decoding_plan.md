# Variable relationships and directed dependency decoding

The user has prioritized the original plan's relationship-decoding branch. Existing value probes do not satisfy it. This is an adaptive discovery follow-up; it does not change the original failed computed-program gates or open reserved model outcomes.

For example:

```python
x = 2
y = x
x = 7
z = y - x
```

The direct relations are `x@1 → y@1`, `y@1 → z@1` and `x@2 → z@1`. `x@1` is an indirect ancestor of `z@1`; it is obsolete as the current definition of `x` but still supplies the value stored in `y`. `x@1 → x@2` is version succession, not a data dependency. Recovering the integer 2 alone does not identify these relationships.

## Separate prediction targets

| Target | Meaning | Important distinction |
|---|---|---|
| Directed def-use edge | Which defining assignment supplies a particular use? | Keep assignment versions, including obsolete definitions. |
| Transitive ancestry | Can one assignment reach another through a dependency chain? | Report separately from immediate edges. |
| Version succession and current status | Which assignments belong to the same variable, and which is current at this prefix? | Reassignment need not read the previous value. |
| Output ancestry | Which visible definitions are ancestors of the selected output? | Unavailable before the query/output is visible. |
| Functional influence | Does changing one defining result change a specified descendant? | Syntax alone does not imply influence: `y = x - x` cancels. |

The first preparation step builds structural labels and audits variation. It does not fit a decoder or demonstrate what the model represents. Every label is limited to the visible assignment prefix. Output-conditioned liveness and future dependencies must not be exported as pre-query labels. Numeric values, oracle answers and model outcomes are excluded from the audit projection.

## Why the older banks are insufficient

A source-only review of the original main pilot found one definition graph for each family × update-count cell across numeric draws and structural splits. Including output edges adds variation determined by load. Parallel and accumulator assignments have no cross-variable edges; snapshots have one. Restricting the final graph to current definitions erases the snapshot's obsolete-parent edge entirely.

The later Llama competition capture also uses a fixed copy/update scaffold. Successful graph classification on either bank could primarily recognize the family or schedule. The older CodeLlama cache remains useful for verifying alignment to assignment endpoints, but does not provide broad graph variation. A family/schedule prior must be an explicit comparator whenever those data are used.

## Varied copy-routing discovery bank

Use the existing arithmetic-free assignment/copy setting to vary the actual graph. Four variables are initialized as `v0=a, v1=b, v2=b, v3=c`, with distinct small `a`, `b`, `c`. Each variable is then overwritten once by copying another current variable. All three parent choices are varied for each overwrite.

The 27 components defined by the final three parent choices each contain all three first-copy alternatives. Eighteen components are training and nine are development; numeric and lexical relatives and the three first-copy variants stay together. There are no final-test rows. Two neutral naming vocabularies are rendered, with a separate development prefix. Canonical AST/alpha-structure checks must find no cross-split duplicate structures.

Choosing `v1` or `v2` for the first copy gives identical values and complete execution states but different provenance, because their initial values are equal. These pairs separate graph labels from numeric-value recovery. The third parent is a different-value control. Independent ordinary-Python execution validates the source traces. Assignment-result substitutions check functional propagation at visible descendants without requiring every relation to survive to the final answer.

This bank has a fixed canonical destination order, one final output query and copy-only operations. It is an exploratory routing diagnostic, not independent replication, a new-family qualification, or a rescue of the computed-program gate.

## Decoder study to run after preparation

Capture assignment endpoints and a pre-query summary position, retaining correspondence to every visible version node. Start with capacity-controlled linear relation heads; distinguish a shared checkpoint-to-graph decoder from any pair-conditioned decoder using two endpoint vectors. Declare the feature access and parameter counts before fitting. Oracle edges, family, update count and version labels are targets or explicit baseline metadata, never hidden-probe inputs.

Compare hidden features against matched surface features, structural/position priors and grouped shuffled relations. Fit preprocessing and decoders on training only. Evaluate held-out routing combinations and names, with every layer/site curve and positive/negative support retained. Report edge precision, recall and prevalence-aware precision–recall metrics, per-relation results and exact whole-graph recovery. Pooling graph edges or numeric relatives as independent experimental replications is not valid.

Decoding success would establish accessible relational information. Selective interventions on the predicted descendants, with unrelated-variable controls, are a separate test of causal use. A learned relational measurement has not yet been validated for the mechanism-based error predictor.
