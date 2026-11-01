# Conditional numeric prediction from source and hidden states

November 1, 2026. Exploratory follow-up to the weak computed-value and all-variable results. This tests whether archived hidden features improve learned numeric prediction beyond an explicit source-feature baseline. The full program already determines its outputs: a conditional gain here is relative to finite feature/readout classes, not information absent from source text or evidence of native causal execution. This method corresponds to the conditional-prediction branch of the pinned 23-paper review. Existing results and failed competence gates remain unchanged.

## Fixed cohort and feature conditions

Reuse the independently audited 5,292-case arithmetic-local cohort, its 216 TRAIN and 72 DEV structural families and separate calibration rows, with the existing global-state cache. Use all four scalar current values as independent regression heads. Oracle computed/untouched/query annotations define labels, selection/evaluation strata and controls; none enters the design matrix. Old prompts request a single variable, and hidden captures use the existing instruction I0. This is not a new all-variable prompt experiment or fresh-family confirmation.

At the already nominated query-state layers24/36 for Llama8B/CodeLlama34B, reuse the existing 1,024-wide nested projections for fitting seeds11/29/47. Reuse the shared source character3–5gram hash features, folded from8,192 bins into1,024 or2,048. No new layer, instruction, projection-width or checkpoint search.

Eight cells are declared:

| Cell | Inputs | Nominal dimensions |
|---|---|---:|
| source/source1024 | Source hash only | 1,024 |
| source/source2048 | Source hash only, capacity comparator | 2,048 |
| llama8b/hidden | Hidden only | 1,024 |
| llama8b/joint | Source plus matched hidden | 2,048 |
| llama8b/shuffled_joint | Source plus mismatched hidden | 2,048 |
| codellama34b/hidden | Hidden only | 1,024 |
| codellama34b/joint | Source plus matched hidden | 2,048 |
| codellama34b/shuffled_joint | Source plus mismatched hidden | 2,048 |

Nominal dimension does not match effective rank or inductive bias. The source comparator is a finite learned baseline, not an ideal source interpreter. The source2048 cell and the independently optimized shuffled-hidden control distinguish several explanations for a joint gain, without proving a specific internal computation.

## TRAIN selection and partition-local controls

Use the audited independent weighted multioutput ridge solver with unweighted TRAIN-only feature means/scales, weighted centering and an unpenalized intercept. Apply one common penalty to both standardized blocks; no block-penalty grid. Select alpha from1/100/10,000 using three structural TRAIN folds and three existing fitting seeds. The selection objective is family-macro MAE on computed slots only. Average all nine fold/seed losses for each alpha; ties choose the larger alpha. No DEV selection. This objective differs from the earlier all-slot global-state assay, so source and hidden comparators are refitted under the same new policy rather than borrowing differently selected old scores.

For shuffled-joint, keep source rows and target values aligned. Derange complete hidden-state donor families inside each structural stratum, separately within EACH fitting partition, validation partition, full TRAIN, DEV and calibration. Preserve numeric-seed/draw and lexical-relative correspondences. A hidden donor may never cross a fit/validation boundary or data split. Retain IDs and donor hashes to audit the control. Fit coefficients and select alpha independently for shuffled-joint, rather than inheriting the real joint model's optimum.

Each cell runs27 CV fits and3 selected refits: **240 total** new CPU readout fits, **zero** language-model calls. All selected matrices and four-head predictions are saved, with parameter save/reload equality checks. Partial immutable banks resume without recomputing committed fits. No backbone training or sealed-final access.

## Outcomes and interpretation

Primary: computed-slot family-macro MAE. Secondary: rounded exact accuracy, untouched/all-slot/query strata and all four scalar outputs. Calibration never participates in fitting or selection. Values are not clipped. The fixed-coefficient block diagnostics replace either source or hidden features with the exact fitted TRAIN mean, giving a zero standardized block while leaving the other block and fitted coefficients intact. These probe ablations are not language-model interventions or independently retrained source-only baselines.

For each checkpoint compare matched joint against source1024, source2048, hidden-only and shuffled-joint. Report paired DEV-family MAE contrasts with seeds averaged within families before2,000 bootstrap replicates. These intervals are descriptive, non-simultaneous and adaptive on previously inspected DEV. The three fitting seeds do not create independent datasets. A gain supports predictive usability beyond the tested comparator; no gain does not establish representational absence, especially under1,024-feature compression.

## Execution and records

Freeze the source/configuration tree and full binding regression before fitting. Validate hash-pinned old cache/oracle IDs in every worker. Use CPU `dev,normal` allocations, preserving the existing GPU continuation suite and unrelated jobs. Large arrays, parameter banks and score files start on scratch, with linked work paths and immutable completion receipts. A durable ten-minute controller monitors each cell and stops at terminal completion. Publish code, declared recipe, frozen source, compressed metadata and payload inventories to CodeCue; raw arrays stay local. The pinned review/register and automatic experiment journal remain enabled. No cumulative compute allowance is introduced.
