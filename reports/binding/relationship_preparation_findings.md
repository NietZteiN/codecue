# Relationship decoding: targets and varied routing sources

The user has prioritized relationships between variables as a distinct branch of the original plan. Value decoding is not a substitute for recovering those relationships. This round prepares and validates the targets and data; **no learned relationship decoder has been fitted yet**.

The new [prefix-label implementation](../../src/codecue/binding/relationships.py) distinguishes directed def-use edges, strict transitive ancestry, succession between assignments of the same variable, and current versus obsolete versions. It includes output ancestry only in an explicitly output-visible view. It preserves repeated operand uses and old definitions, excludes numeric values from structural labels, and checks the visible graph against an independently constructed prefix passed to the existing interpreter. The hidden output is replaced by a constant sentinel for that check.

For example, after `x = 2; y = x; x = 7`, `y@1` depends on `x@1`, although `x@2` is now current. The overwrite succession `x@1 → x@2` is a different relation from a data dependency. Syntactic ancestry is also separate from functional influence: `y = x - x` reads `x` but cancels its effect.

## A gap in the previous datasets

A source-only review found that the original three program families largely fix their assignment graph once family and update count are known. Parallel and accumulator programs have no cross-variable assignment edges; snapshots add one cross-variable copy. A graph restricted to final current definitions erases that snapshot's obsolete-parent relation entirely. Counting statement-position changes as new graphs would overstate semantic variation.

The newer Llama competition bank also uses a fixed copy/update scaffold. These sources remain useful for checking prefix alignment and version labels, but a successful classifier could mostly recognize a family or schedule. They are insufficient for the broader relationship claim.

The [original-source target audit](relationship_target_audit_v1.md) checks 2,880 value-free discovery records, including every visible assignment checkpoint and a separate final output-visible view. The projection strips oracle values, answers and all model outcomes. Structural group boundaries are checked before labels are generated.

## New copy-routing bank

The [source-bank report](relationship_routing_preparation_v1.md) records **1,296 programs, 81 directed definition graphs and 27 structural components**:

| Split | Rows | Components | Full definition graphs |
|---|---:|---:|---:|
| Training | 864 | 18 | 54 |
| Development | 432 | 9 | 27 |

Each component contains eight numeric draws, three first-copy alternatives and two neutral lexical forms. Rewiring, numeric and lexical relatives remain together. All four variables are overwritten through copies, so immediate parents and indirect ancestry vary while arithmetic is absent.

There are **432 paired examples with identical numeric states at every checkpoint and identical final answers, but different provenance graphs**. Their first copy reads one of two equally valued variables. A third parent provides a different-value control. Assignment-result substitutions distinguish the rewired descendants without requiring the difference to survive every later overwrite. Independent ordinary Python validates 3,240 distinct baseline/counterfactual programs.

Exact source, canonical AST, alpha structure and full definition-graph overlap across the two splits are zero. Shared early prefix graphs are expected and explicitly reported; they are not new independent structures. The [routing target audit](relationship_routing_target_audit_v1.md) checks the value-free projection using the same label and consistency rules as the older bank.

## What remains

The [relationship study plan](relationship_decoding_plan.md) makes learned decoding the next stage: capture aligned representations, fit controlled relation heads, and compare them with surface, structural/position-prior and grouped shuffled-label baselines. Report positive-edge precision/recall and whole-graph recovery, rather than an accuracy dominated by absent edges.

This source bank has a fixed destination order, copy-only operations and one final query. It is adaptive discovery preparation, not a new-family qualification, independent confirmation, or a repair of the failed computed-program gates. Oracle topology and version labels must not become probe inputs. Successful decoding would establish accessible relational information; selective downstream interventions and useful unfamiliar-program error prediction remain separate milestones. No language model or tokenizer was loaded, no activation array or model response was opened, and reserved model outcomes remain sealed.

Validation: **1,302 tests passed**, with no failures, errors or skips ([JUnit](../../artifacts/binding/relationships/regression_v2.xml)). The [current readiness report](preparation_readiness.md) records 35 ready tasks, nine scientific decisions and three optional deferred tasks. The learned-decoder milestone remains unchecked.
