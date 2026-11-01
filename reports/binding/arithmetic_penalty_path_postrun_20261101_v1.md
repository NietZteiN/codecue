# Penalty continuation: interpretation and debugging review

All eight conditions kept alpha **10,000**, now an interior point of the six-value finite grid. Every overall TRAIN-fold choice also remained ridge rather than a constant. The continuation therefore resolves the previous upper-boundary concern within the tested range; it does not improve the selected predictions. All 24 selected full-TRAIN banks are the original models, reused unchanged.

The wave added **216 CV fits** and reused **216 CV plus 24 selected banks**. Fold-local and full-TRAIN priors contributed **36 four-slot statistic vectors**, with zero fixed. No new language-model calls, backbone training or sealed-final access occurred. The larger grid remains an adaptive diagnostic on the original inspected cohort, not an independent replication.

Joint computed-value MAE remains **4.9863 / 4.9444** for Llama / CodeLlama. Rounded computed-value exact accuracy remains **6.68% / 6.00%**, below the zero predictor's **8.90%**. Lower numeric error is a supported endpoint here; exact state reconstruction is not. Joint-minus-hidden MAE differences remain small, with descriptive family intervals crossing zero. These finite source/hidden comparisons do not show that information is absent from source code or that the model naturally uses a decoded state.

## Verification

The frozen scientific source passed **43 focused tests** and **2,697 full regression tests** in job **488331**. Shared priors **488375** and all eight workers **488405–488412** completed with exit `0:0`. The no-refit numerical audit **488416** also completed with exit `0:0`:

- All **432 CV banks** and **24 selected banks** checked for original/new ownership, input/target/weight identities and TRAIN partition/donor boundaries.
- **3,763,584 prediction coordinates** replayed with maximum absolute difference **0.0**.
- Maximum relative ridge normal-equation residual **1.1573310908189925e-11**; weighted-intercept residual **2.0663999285735826e-14**.
- TRAIN-only selections, fold-local priors, saved score ordering, family metrics and fixed-block ablations replayed.

The frozen snapshot **98bd03c707756b99c11c0391** and frozen protocol were verified unchanged after the operational fix below. The final report is gated by this audit.

## Operational fix outside the frozen scientific source

Audit startup spent about **168 seconds** in `stamp.py start` waiting for the derived experiment-log index lock. Lifecycle hooks previously used a blocking lock also used by full refreshes. Event emission and job-result sync now try that lock without waiting. The event is durably spooled before indexing, and the automatic reconciler can replay it later. Full refreshes retain serialized blocking access. This removes the observed lock contention from future lifecycle hooks; other bookkeeping work can still take time.

All **77 targeted logging tests passed**, including an actual two-process contention check: one process holds the index lock while another emits and syncs, which must finish within five seconds; refresh must then recover the event and running job. Concurrent event writers, lifecycle ordering, duplicate finishes, scheduler reconciliation, large metadata handling and logging failures also passed. This operational change is outside the frozen scientific snapshot; the 2,697-test receipt describes that snapshot, while the 77-test check describes the logging update.

## Saved-score exact-value diagnostic

The separate [diagnostic](arithmetic_exact_value_diagnostic_20261101_v1.md) replays the saved metrics and adds whole-state accuracy and target-support checks. Both joint probes have **0.00% all-four exact recovery**. Only **24/3,168 computed DEV slots (0.76%)** have labels absent from that slot's full TRAIN support. Most failures therefore involve seen numeric values, while unseen compositions and contexts remain possible. The TRAIN computed-family mode also scores **8.90%** computed exact, matching zero. Two mode vectors per fitting seed add **six prior-statistic vectors**, with no new probe fits and no DEV-based selection. These postrun modes do not replace the frozen TRAIN-fold choices.

## Next work

The [ordered follow-up design](arithmetic_after_penalty_plan_20261101_v1.md) prioritizes an exact-value failure audit, fresh prospective behavior calibration and temporal overwrite contrasts before a small shared-query decoder comparison. Dependencies and algebraic pair/triple relations remain explicit targets. Increasing penalties again is not the first priority after all eight finite-grid optima stayed at 10,000.

[Audited findings](arithmetic_penalty_path_findings_20261101_v1.md) · [Penalty curves](figures/arithmetic_penalty_path_v1.png) · [Exact-value diagnostic](arithmetic_exact_value_diagnostic_20261101_v1.md) · [Execution and frozen identity](arithmetic_penalty_path_launch_20261101_v1.md) · [Live/terminal suite status](arithmetic_penalty_path_status_20261101_v1.md).
