# Global-state readouts: computed values and queried slots

These are the predeclared evaluation annotations from the completed seven-cell assay. No additional fitting, selection or model calls. Average three fitting seeds after each seed's TRAIN-only alpha selection. Every annotation stays outside the probe inputs. These tables are descriptive adaptive DEV summaries; no additional intervals or mechanism claim.

| Features | Width | Scalar computed exact | Scalar untouched exact | Scalar queried exact | Scalar unqueried exact | Categorical computed exact | Categorical untouched exact |
|---|---:|---:|---:|---:|---:|---:|---:|
| llama8b | 1024 | 6.42% | 11.78% | 11.19% | 7.32% | 8.21% | 41.60% |
| llama8b | 4096 | 6.58% | 12.66% | 11.83% | 7.54% | 8.38% | 44.50% |
| codellama34b | 1024 | 5.90% | 13.43% | 10.65% | 7.91% | 8.60% | 50.16% |
| codellama34b | 8192 | 7.56% | 13.00% | 11.21% | 8.75% | 8.54% | 60.23% |
| source | 1024 | 5.30% | 12.34% | 7.41% | 8.23% | 8.53% | 82.83% |
| source | 4096 | 5.31% | 12.77% | 7.30% | 8.49% | 8.59% | 83.73% |
| source | 8192 | 5.34% | 12.54% | 7.48% | 8.42% | 8.62% | 83.84% |

## Direct relationships involving at least one computed value

| Features | Width | Relation-type macro BA |
|---|---:|---:|
| llama8b | 1024 | 54.71% |
| llama8b | 4096 | 54.85% |
| codellama34b | 1024 | 56.51% |
| codellama34b | 8192 | 56.10% |
| source | 1024 | 54.20% |
| source | 4096 | 54.52% |
| source | 8192 | 54.45% |

Computed means the current definition is an arithmetic update rather than an initial root. Untouched values can remain visible as source literals, so overall slot accuracy can hide weak computation recovery. Queried/unqueried comparisons are observational: query choice and value difficulty can differ. They do not establish a causal query effect; matched query-scope/timing captures are still needed. Family weighting within a stratum can differ from the overall four-slot metric. For direct relationships, the saved banks retain each head's unique-TRAIN-body eligibility and evaluation class counts. Undefined cells are excluded within type, and BA is undefined if a type lacks support. The main report retains direct-versus-external-derived, shuffled/prior controls and matched source contrasts.
