# Cached-state follow-up: active release

The original local suite completed successfully. Its [saved-result snapshot](arithmetic_local_completion_snapshot_v1.md) preserves every selected backend and all three behavioral wording variants. Numeric-state recovery and natural causal use remain open.

The active CPU follow-up uses frozen source `82aa60555d1e9b67df97b706` and the [revision 2 protocol](arithmetic_state_followup_plan_v2.md). The full source regression passed **2,433 tests**. Both independent audits reapplied all 54 saved dependency readouts per checkpoint with zero score difference, covering 4,478,976 operand-score applications in total. The audits cache all four archived layers for later readouts without new language-model calls.

The supervised DAG releases current-definition lookup, role-conditioned numeric decoding and capacity-matched counterparts as each model’s audit completes. It then composes predicted bindings with decoded values and algebraic relationships, retaining explicit oracle-routing and external-arithmetic diagnostics. Early audited local results and final composed-state reports are generated automatically.

- Validation job:485775, completed successfully.
- Llama audit: 485790, completed successfully.
- CodeLlama audit: 485791, completed successfully.
- Readout jobs: 485816–485821, submitted and queued.
- Audited local-results report: 485822, [report and figure generated](arithmetic_local_dependency_findings_v1.md).
- Successor supervisor: 485815, scheduled.

A legacy audit compared two reordered TRAIN floating means exactly and rejected differences below1e-16. The repair permits only1e-12 roundoff in rate fields while requiring exact counts, identities, parsing and correctness. Original answers/summaries and the superseded first-edition source remain preserved. No state readout had begun in the stopped edition.

[Machine-readable release](../../artifacts/binding/arithmetic_state_followup/20261030_v2/suite/validated_release_review_v1.json) · [DAG configuration](../../configs/binding/arithmetic_state_followup_20261030_v2/suite.json) · [Reproduction](../../reproducibility/arithmetic_state_20261030_README.md).
