# Controlled numeric geometry and global-query preparation

Prospective discovery protocol, October 31, 2026. This addendum puts a small,
mechanistically motivated output-code comparison before the full global-state
fits in the [existing next-run plan](arithmetic_next_runs_20261031_plan_v1.md).
It does not replace the dependency, binding, timing, relations or behavior work.
The [advanced-methods rationale](advanced_methods_20261031_v1.md) separates the
implemented assay from proposed slot models and gated causal work.

## Question and predictions

Did one-hot/scalar targets obscure a smooth or modular numerical code in the
same captured states? Our earlier one-hot digit classifiers did not test circular
digit geometry. Levy and Geva's [NAACL 2025 paper](https://arxiv.org/abs/2410.11781)
fits linear maps to digit sine/cosine coordinates. Here signed, computed values
and joint nearest-template reconstruction adapt that idea; this is not a direct
replication of their positive-literal task or digit-by-digit angular decoder.

- A benefit for natural circles over dimension-matched permuted circles would
  support this geometry as a more useful readout assumption within this assay.
- Equal gains for both would favor dimension/regularization or codebook effects.
- A benefit shared by source features would weaken an interpretation specific
  to model states. Report the hidden-minus-source contrasts at matched widths.
- Literal success with computed failure would retain the computation/timing
  bottleneck. Successful local decoding alone would not establish global state.

These are exploratory comparisons on previously inspected DEV. All panels are
reported; any promising pattern needs a new-family confirmation cohort.

## Fixed output codes

The domain is every integer from -96 through 96, fixed before this run. No
candidate is removed using observed TRAIN or DEV labels. Each linear ridge
map uses the same TRAIN standardization, feature access and family weighting.

| Code | Outputs | Predeclared target |
|---|---:|---|
| Signed decimal circle | 7 | Sign one-hot (3), absolute units circle (2), absolute tens circle (2) |
| Permuted decimal circle | 7 | Identical sign, independent fixed digit permutations before circle encoding |
| Residue circles | 4 | Signed value modulo 17 and 19, each represented by sine/cosine |
| Permuted residue circles | 4 | Same dimensions/radii, independently permuted residue angles |
| Ordinal thresholds | 192 | Indicator that value exceeds each threshold -96 through 95 |

The decimal permutation seeds are 731 and 947; residue seeds are 12017 and
12019. Permutations are data independent. Residue product 323 exceeds the
193-value domain, avoiding aliases. Every code decodes by nearest squared
Euclidean template over the declared domain, including the candidate norm
term (essential for ordinal thresholds). This lookup receives no program
operators, parent pointers or evaluation labels. Scores are not calibrated
probabilities; this run does not estimate NLL or MDL.

## Inputs, controls and selection

Reuse the completed, hash-pinned definition caches for the 5,292-row cohort.
No model forward pass is needed. Keep the nominated Llama layer 24 and Code
Llama layer 36. Full-width hidden features are 4096 and 8192; source character
hash features are shared across models at matching widths. The same 12 public
statement/depth metadata features are appended as in the completed baseline.
Root-definition and computed-definition roles are fit separately.

Eight cells: two checkpoints × two roles, plus two source widths × two roles.
Each cell jointly fits the five target codes: 214 real outputs in CV, and
214 real + 214 coherent-family-control outputs in selected fits. The circle
permutations and coherent-family label derangements answer different questions.
The latter moves entire structural families within split/operator/depth strata.
Encoded weighted TRAIN-mean predictions are reported as a prior comparator.
Existing scalar, 193-class and one-hot digit results are reused, not refitted.

Use seeds 11/29/47, three structural TRAIN folds, alpha 1/100/10000. Each code
selects alpha by mean family-macro exact reconstruction across all nine
seed/fold validations; ties choose larger alpha. Refit selected alphas only,
then score TRAIN, adaptive DEV and calibration separately. Calibration never
enters fitting or selection. Report exact/MAE, every seed and alpha, parameter
counts, depth, initial-literal match and value-support panels. Preserve grouped
family identity; the three seeds are not three independent datasets.

For natural-minus-permuted and width/role-matched hidden-minus-source exact
accuracy, average seeds within each DEV structural family, then resample
families 2,000 times with seed 20261031. Report descriptive 95% percentile
intervals without treating them as simultaneous or independent confirmation.
The single fixed permutation per code is a control, not a population of random
geometries; any promising advantage needs additional permutations and families.

This entails 216 CV factorizations and at most 72 selected factorizations.
Save every parameter bank, selection receipt, score panel and hash; exact
save/reload score equality is required before completion. Do not equate higher
probe accuracy with the model executing arithmetic or naturally using a code.

## Preparation for all-variable decoding

Two additional jobs stream the original native capture chunks and extract
the actual answer point `point_count - 1` for each case, at all four captured
layers. The last padded slot is not used. Verify chunk SHA, ordered metadata,
float32 geometry, coverage, finite values and answer-point descriptors.
The resulting `(cases, layers, hidden)` arrays are prepared inputs only:
this stage does not fit the global four-value/direct-relation probes and does
not claim complete state recovery. No tokenization or generation is added.

## Execution and stop rules

Full frozen binding regression gates every fit and extraction. Large outputs
are created directly on scratch; `/work` contains only directory links and
small protocol/status/source evidence. Fit requests are 16 CPUs / 32 GiB,
based on prior measured peaks below 11 GiB, with the scheduler's 48-hour
maximum. Extraction requests are 8 CPUs / 8 GiB / 2 hours. These CPU-only jobs
use existing captures; no artificial cumulative compute allowance is imposed.

The durable controller checks every ten minutes and installs a successor
before reconciliation. Scientific failures require review; only eligible
scheduler interruptions resume. Preserve other jobs and completed evidence.
Do not reopen sealed final outcomes or start interventions/optional LM
training. The report waits for all eight fits and both extraction jobs.
Publication preserves frozen source/config/test mirrors and immutable metadata;
raw arrays remain local under the established restore/catalog policy.
