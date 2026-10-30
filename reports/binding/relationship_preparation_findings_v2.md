# Structural and algebraic relationships: preparation status

The user selected **both** data-dependency/version relationships and algebraic relationships. Their targets and source controls are now implemented separately. **No learned relationship decoder has been trained or evaluated yet.** These results qualify preparation, not recovered model representations.

| Target family | Implemented labels | Interpretation |
|---|---|---|
| Structural | Directed versioned def-use, transitive ancestry, assignment succession, current/obsolete versions and explicitly visible output ancestry | Which assignment supplies or depends on which other assignment? |
| Algebraic | Equality, less-than ordering, signed pair differences, `x + y = z` and `x - y = z` on distinct visible slots | What mathematical relations hold between the current values? |

For example, `x = 2; y = x; x = 7` leaves `y` dependent on the obsolete `x@1`, while the current numeric relation is `y < x`. Neither fact is captured merely by reporting that one answer digit is decodable. Structural ancestry, numerical equality and functional influence are kept separate.

The [structural preparation](relationship_preparation_findings.md) found a limitation in the previous banks: their graphs were largely fixed by family/update schedule. The new 1,296-row routing bank contains 81 full graphs and 432 pairs with identical numeric states but different provenance. Its targets preserve old versions and mask hidden outputs.

## Algebraic controls on shared graph structures

The [algebraic source report](algebraic_relationship_preparation_v1.md) records a second discovery bank:

| Numeric sampling stratum | Training rows | Development rows | Total |
|---|---:|---:|---:|
| Four distinct uniform literals | 432 | 216 | 648 |
| Explicit initial additive triple | 432 | 216 | 648 |
| Equal initial pair, different provenance | 432 | 216 | 648 |
| Total | 1,296 | 648 | 1,944 |

It reuses the same 27 routing components, split 18 training/9 development, and the same 81 full definition graphs, split 54/27. This is additional numeric control, **not independent structural replication**. All numeric strata, first-copy variants and lexical relatives remain inside their component. There are 216 equal-state/different-graph pairs in the equal-pair stratum. Independent ordinary Python validates 2,916 distinct canonical/surface programs.

Stratum names do not substitute for actual relation labels. One uniformly sampled numeric group also happens to satisfy the initial additive identity, and later copies can create or remove relations in any stratum. The [algebraic target audit](algebraic_relationship_target_audit_v1.md) therefore recomputes actual values at each visible assignment prefix and checks them with independent Python arithmetic. Across 15,552 prefix views it reports 776 boolean relation cells: 712 have both-class structural-group support and 64 are always false. It reports 136 signed-difference cells separately. These are target-support counts, not model accuracies or independent experiments.

The [structural audit of these same examples](algebraic_structural_target_audit_v1.md) validates versioned graph labels alongside the numeric labels. One future activation capture can therefore support both target families on identical examples. The source projection strips numeric strata, oracle values, answers, graphs and all model outcomes; numeric values are reconstructed only as supervised targets. Hidden outputs and future assignments are never executed by the numeric target oracle.

## Decoder comparisons still to run

The [broader plan](relationship_decoding_plan_v2.md) calls for aligned representation capture, controlled linear relationship heads, and separate value heads. Structural tasks need surface, structural/position and grouped shuffle controls. Algebraic tasks also need the decisive comparison with relations calculated from independently decoded values: direct relation recovery alone would not demonstrate a dedicated relational code.

All-negative accuracy is uninformative for constant relation cells. Report positive/negative support, group-aware precision/recall and whole-graph recovery; keep numeric difference regression separate from boolean classification. Symmetric pairs, commutative triples, numeric relatives and seed variants are not independent replications.

Both banks remain adaptive copy-only discovery diagnostics with a fixed destination order and one final query. Shared early prefix graphs are reported rather than presented as novel structures. No language model/tokenizer was loaded, activation/model response opened, learned relationship model fitted, or reserved model outcome evaluated. Selective causal use and mechanism-based unfamiliar-program error prediction remain unfinished.

The final full regression suite passed **1,370 tests**, with zero failures, errors or skips ([JUnit](../../artifacts/binding/relationships/regression_v3.xml)). The [current inventory](preparation_readiness.md) records 36 ready tasks, nine scientific decisions and three optional deferred tasks. These readiness counts include preparation; they do not mark learned relationship recovery complete.
