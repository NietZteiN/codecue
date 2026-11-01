# Conditional numeric prediction: execution handoff

[Declared plan](arithmetic_conditional_plan_20261101_v1.md) · [Live status](arithmetic_conditional_status_20261101_v1.md) · [Completed continuation interpretation](arithmetic_continuation_decisions_20261101_v1.md).

The new question is whether archived hidden features improve computed-value prediction beyond a finite learned source baseline. Source already determines program outputs; conditional predictive gain is a property of these feature/readout classes, not additional information absent from the program or a causal execution claim.

- Frozen snapshot **b9d058163e86b66ef30c8a1c**; code SHA **f53aa2906d4ca272559e5728084a07c0b490e0d08075ccbbb0dc48a5a9c78d8c**.
- Suite config: `configs/binding/arithmetic_conditional_20261101_v1/suite.json`.
- **42 focused tests passed**, including donor partition boundaries, target-only scope comparisons, nominal feature dimensions, exact TRAIN-mean block ablation and recovery of a known conditional signal.
- Full frozen regression **488131** passed **2,654 tests** in 658 seconds, with scheduler 0:0; all science cells then completed. Initial durable controller **488130** checks every ten minutes on `dev,normal` and stops at terminal completion.
- Reuse **5,292** cases: **3,888 TRAIN rows / 216 families**, **1,296 DEV rows / 72 families**, and **108 calibration rows / six families**. Source dataset SHA **7d4a1261da83e68ce0e95f17bb9be5ad658b728d42c4c8810c03f82f5ae40ca9**. No new language-model queries or backbone training.
- Metadata feasibility verified coherent hidden donors for each of the three TRAIN folds independently: **2,592 fitting rows / 144 families** and **1,296 validation rows / 72 families**, plus full TRAIN, DEV and calibration partitions. Donors never cross a fit/evaluation boundary; source/target alignment is preserved.
- Eight cells: source1024, source2048, and hidden1024/joint2048/shuffled-joint2048 for each checkpoint. Each independently selects alpha 1/100/10,000 on computed-value family-macro MAE using three TRAIN folds and fitting seeds 11/29/47. Each cell commits 27 CV banks and three selected banks, for **240 total CPU fits**.
- Query-state layers 24/36 and existing projection seeds are fixed. No layer, instruction or width sweep. Source2048 matches nominal joint dimension, with different effective rank/inductive bias explicitly acknowledged. Shuffled-hidden controls get their own fitted coefficients and TRAIN selection.

Every selected predictor is saved/reloaded with exact score equality checks. The report replays saved metrics from score arrays before calculating descriptive paired-family contrasts. Fixed-coefficient block diagnostics replace one feature block with its exact fitted TRAIN mean; they are probe ablations, not interventions in the language model. Prior and computed/untouched/query strata remain visible.

Each fit cell requests 16 CPUs / 32GiB on `dev,normal`; QA uses 8 CPUs / 24GiB. Immutable banks resume after scheduler interruptions. Large arrays and fit artifacts start on `/scratch/juno/jvl210002/codecue/arithmetic_conditional/20261101_v1`, linked from the work artifact root. Automatic event logging, source/parameter/score hashes and literature pins remain active. There is no cumulative compute allowance. Existing jobs and the completed GPU continuation evidence are preserved.

Formal temporal hidden-state collection remains a separate gated task. The new continuation results motivate a fresh calibration recipe and generated-trace boundary/visibility implementation; they do not retroactively pass the original output-only competence gate. Fresh-family confirmation and causal-use claims remain unfinished.

All eight workers **488193–488200** completed successfully, committing **216 CV / 24 selected banks**. Report **488221** replayed their saved metrics and completed. The [findings](arithmetic_conditional_findings_20261101_v1.md) show modest joint gains over source and shuffled-hidden controls, with little additional gain over hidden-only and weak computed exact recovery.

The separate [numerical audit](arithmetic_conditional_postrun_review_20261101_v1.md), job **488228**, checked all 240 banks against actual TRAIN input/target/weight hashes, normalizers, donor partitions, ridge normal equations, independent family-first metrics and TRAIN selection. All **2,135,808 prediction coordinates** replayed exactly; no new fits or model calls. Maximum relative normal-equation residual was 1.16e-11. Both owned-controller advances are recorded in `controller_expedite_v1.json` and `controller_expedite_v2.json`. The suite is terminal `complete_exploratory`.

The [postrun prior/boundary diagnostic](arithmetic_conditional_prior_diagnostics_20261101_v1.md), job **488237**, found all eight selected alphas at 10,000. Joint MAE beats zero/median 5.331, while its rounded exact accuracy trails zero 8.90%. No original results changed. The [next-wave design](arithmetic_conditional_next_wave_20261101_v1.md) extends TRAIN-only penalty selection with immutable bank reuse and endpoint-appropriate prior controls; this follow-up is planning only.
