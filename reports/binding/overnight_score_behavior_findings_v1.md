# Score/answer follow-up findings

The exact-ID DEV join shows that a correctly decoded dependency graph frequently coexists with a wrong generated answer. Queried-value decoding is much weaker, so this does not establish a complete correct binding state that the model fails to use.

This is a posthoc analysis selected after inspecting the overnight results. It validates all14,580 original responses and uses4,860 DEV rows,72 fixed saved-score banks and zero new model calls, fits or parameter predictions. Initial-binding values at site3 remain distinct from final-binding values at sites7/8.

## Computed programs: the same486DEV cases per checkpoint

Values below use the nominated hidden layer at the last-assignment checkpoint. Joint probabilities average binary events within each of the three saved fits before computing component summaries.

| Model | Answer correct | Whole graph correct | Queried final value correct | Graph correct and answer wrong | Conditional95% for joint probability |
|---|---:|---:|---:|---:|---|
| Llama3.1 8B | 11.728% | 94.719% | 7.133% | 83.265% | [76.200, 89.575] |
| CodeLlama34B | 2.881% | 92.730% | 6.241% | 89.849% | [82.371, 96.296] |

The graph decoder receives the fixed node/version scaffold. Its correctness concerns the dependency pattern, not all numeric bindings or the model’s naturally used pathway. These rows are a subset of the full computed readout panel; the graph points therefore differ from that panel’s aggregate values.

## Matched body and fixed target slot

For literal query twins, change only the actual query while scoring the same target head on the same program body. Report the final-prompt effect minus the pre-query site7 placebo, averaged over all four target slots.

| Model | Site7 placebo | Site8 minus site7 | Conditional95%, percentage points |
|---|---:|---:|---|
| Llama3.1 8B | +0.000pp | +0.857pp | [-0.303, 1.938] |
| CodeLlama34B | +0.000pp | -0.400pp | [-0.995, 0.234] |

Both mean-effect intervals include zero. This is not a claim of no query effect at every slot, layer or decoder. Full4×4 matrices, all source controls and individual-slot contrasts remain in the pinned machine result. A slot-difficulty difference before the query is visible cannot establish query modulation; other slots may also be output ancestors.

Intervals resample the same nine structural components2,000times, seed117, conditional on the saved fits, with no refitting or multiplicity adjustment. Conditional cells require at least1,900 valid draws; empty or sparse cells remain explicitly unavailable where appropriate. Numeric seeds, weighting seeds, lexical twins and queries are not independent topology replications.

The [complete score/answer report](overnight_score_behavior_v1.md), [declared posthoc plan](overnight_score_behavior_plan_v1.md) and [overnight findings](overnight_20261027_findings_v1.md) retain the surrounding comparisons. The [next-experiment decision](relationship_next_experiment_decision_v1.md) keeps root computation, query accessibility and natural causal use as separate open questions.
