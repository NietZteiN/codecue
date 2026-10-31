# Results informing the next runs

Generated from the independently audited numeric sweep. Existing DEV remains discovery; three weighting seeds are sensitivity runs, not independent datasets. Arrows compare64-wide and full-width features within the same role-specific assay.

| Measurement | Llama 8B | CodeLlama 34B |
|---|---:|---:|
| Literal categorical exact, full width | 100.00% | 100.00% |
| Computed categorical exact,64 → full | 9.30% → 12.13% | 8.80% → 13.13% |
| Computed scalar MAE,64 → full | 4.830 → 3.841 | 4.839 → 3.527 |
| Computed joint-digit exact, full width | 10.07% | 10.64% |
| Computed categorical TRAIN prior exact | 9.44% | 9.44% |

| Computed-value component, full width: balanced accuracy | Llama 8B | CodeLlama 34B | TRAIN prior |
|---|---:|---:|---:|
| sign | 56.38% | 56.78% | 33.33% |
| magnitude | 47.44% | 47.10% | 33.33% |
| units | 13.99% | 14.41% | 10.00% |
| tens | 29.88% | 28.97% | 25.00% |
| parity | 54.27% | 56.02% | 50.00% |
| mod5 | 22.86% | 21.80% | 20.00% |
| mod10 | 13.93% | 13.97% | 10.00% |

Wider features help, copying is strong, and coarse numeric properties are more accessible than precise computed values. Current exact-value accuracy remains low. Component balanced accuracy and whole-value exact accuracy measure different targets. These definition-level probes do not yet establish a shared all-variable state or natural causal use.

The next priority is the [full-width global-state/direct-relation test, then timing and matched-mechanism runs](arithmetic_next_runs_20261031_plan_v1.md). No new experiment has been submitted by this planning step. The prior low-rank composed-state results remain a separate assay until updated global/pipeline measurements exist.

[Audited review and figure](arithmetic_numeric_postrun_review_v1.md) · [Full panels](arithmetic_numeric_exploration_findings_v1.md).
