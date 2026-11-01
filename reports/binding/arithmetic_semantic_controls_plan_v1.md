# Alternate semantics on fixed code states: prospective discovery protocol

October 31, 2026, America/Chicago. This is E1 of the
[23-paper literature review](probing_literature_review_20261031_v1.md), with
reading scope and primary sources in the
[source register](../../artifacts/binding/literature/probing_methods_20261031_review_v1.json).
Both files are pinned in every scientific configuration and their hashes are
verified at setup, label preparation, fitting and reporting.

## Connection to the paper

The [existing CodeCue argument](../../paper/ARGUMENT.md) shows that a correct
digit can remain recoverable before an incorrect name-suggested trace write.
The [extension plan](../../docs/binding/dependvar_20261025.txt) asks whether
values are attached to the right variables and versions and used downstream.
This experiment qualifies the value readout: can a probe recover ordinary
semantics preferentially, or learn another computation from the same states?
It does not itself test misleading names, trace-format repairs, causal neural
binding or unfamiliar-program forecasts. Those remain the paper's later tests.

The control is inspired by Jin and Rinard's
[semantic intervention experiment](https://proceedings.mlr.press/v235/jin24e.html).
Their [latent causal probing framework](https://arxiv.org/html/2407.13765v2)
requires assumptions about the training-data causal model and baseline validity
that are not established for our pretrained checkpoints. We use the comparison
as a discovery diagnostic, not an identified causal effect of pretraining.

## Fixed comparison and analytic bound

Use every row of the existing 5,292-case local cohort and its original ordinary
captures, source features, structural TRAIN/DEV/calibration membership and
case order. No extra LM calls or tokenization are needed. The program text
given to the model remains unchanged.

Two target semantics:

- **Ordinary:** `+` computes addition and `-` computes subtraction.
- **Operator swap:** `+` computes subtraction and `-` computes addition.

Unary negative literals keep their meanings. Operands retain their order, and
updates read previous versions before assigning new versions. With only two
binary operators, there is exactly one nonidentity operator permutation. This
is not a population of many independent alternate languages.

All four initial values have magnitude at most 6 and there are at most six
binary updates. Every update increases the maximum possible magnitude by at
most a factor of two, giving a conservative bound of `6 * 2**6 = 384` for both
semantics. Retain the complete cohort, including alternate values beyond the
old ±96 domain: no clipping, wrapping, rejection or performance-based exclusion.
Root assignments have identical labels under both semantics and are preserved
in the label archive; new fits concern computed definitions only.

## Label validation and future structured targets

Rewrite validated generated AST operators and run the restricted interpreter.
Verify ordinary values and answers against the archived oracle. Require
assignment versions, read-time uses and dependency edges to agree between
semantics. Independently execute both validated sources through the existing
isolated Python subprocess oracle in batches of at most 256 sources. Any
disagreement stops the stage.

Save ordinary/alternate definition values and all current values after each
assignment, with versions and defined-slot masks. Undefined slots use zero
padding only with an explicit mask. Save final four-variable states and exact
oracle labels for 12 directed `<` pairs, six unordered equality pairs and
24 ordered distinct-variable triples satisfying `z = x + y`. Coordinate
conventions and case-ID order are recorded. These prepare E4's structured
readouts; no relationship decoder is fitted or claimed in this wave.

Report label histograms, range, magnitude, standard deviation, row-level entropy,
changed-value counts and alternate values outside ±96 separately by split.
These diagnose target difficulty; histogram rows are not independent families.

## Fits and reuse

Reuse the completed ordinary full-width computed-definition fits from
`arithmetic_numeric_exploration/20261031_v1`, retaining their original frozen
source and selection. Ordinary targets were fit jointly with other independent
ridge columns; only scalar, sign, parity and mod5 are used for this comparison.
The ridge estimator solves target columns independently, so this reuse does
not change the per-target fitting objective. No completed ordinary bank is
refit or overwritten.

Four alternate-fit cells:

| Cell | Features | Width |
|---|---|---:|
| Llama 8B | Captured definition state, nominated layer 24 | 4096 |
| CodeLlama 34B | Captured definition state, nominated layer 36 | 8192 |
| Shared source | Original character-hash definition prefix | 4096 |
| Shared source | Original character-hash definition prefix | 8192 |

Every cell appends the same 12 public statement/depth features as the ordinary
baseline. Alternate feature-cache views borrow the old hash-pinned arrays;
their example identities differ only in explicitly declared target labels.
No true value, oracle parent or relation label enters the features.

The target layout is scalar (1), sign (3), parity (2), mod5 (5): 11 outputs.
Use the same three fitting/weighting seeds 11/29/47, three structural TRAIN
folds and alpha grid 1/100/10000. Select scalar by family-macro validation MAE,
components by supported-class macro recall; ties prefer larger alpha. This
matches the original per-target criteria. Selected fits jointly fit real and
coherently deranged family-control labels at the selected alpha. Control tasks
do not select their own alpha; retain that interpretation limit.

This requests 108 CV factorizations and at most 36 selected factorizations.
Keep all parameters, metadata, score banks, IDs, selection receipts, controls
and encoded TRAIN priors. Every saved fit must reproduce its scores exactly
when reloaded. Calibration and DEV labels never enter fitting or selection.

## Reporting and interpretation

Replay the scalar/component DEV metrics for selected ordinary and alternate
banks from their saved scores, checking exact IDs and truth arrays first.
Require the recomputed metrics to equal the recorded ones. For scalar errors,
also divide by the corresponding seed's weighted TRAIN target standard
deviation; fit no scale using evaluation labels.

For each feature cell report ordinary versus alternate exact reconstruction,
raw MAE, normalized MAE and component balanced accuracy. Bootstrap the paired
family-level normalized-MAE difference, averaging the three fitting seeds
within each family before 2,000 resamples with seed 20261031. Positive
`alternate error - ordinary error` indicates an ordinary-semantic preference.
Also report that preference minus its width-matched source preference.
Intervals are descriptive and non-simultaneous; DEV is adaptive discovery.

Scale normalization and source controls do not ensure equal task learnability.
A normal-semantic advantage might reflect source statistics, operator-specific
priors or decoder inductive bias. A null does not establish that the model has
no semantics. Neither outcome establishes all-variable state recovery, an
assignment-version mechanism, native causal use, or independent confirmation.

## Execution and monitoring

Full frozen binding regression precedes label preparation and all fits. Label
preparation is followed by four independent CPU workers and a report. Large
outputs are created on scratch from the outset; `/work` holds small metadata
and directory links. Requests: 8 CPUs / 8 GiB / 2 hours for preparation,
16 CPUs / 32 GiB / the scheduler's 48-hour maximum for fits, and 4 CPUs /
8 GiB / 2 hours for reporting. There is no cumulative compute allowance.

The durable supervisor schedules ten-minute checks subject to scheduler QoS,
preserves other jobs, resumes eligible scheduler interruptions and stops on
scientific failures. Automatic lifecycle/SLURM result logging stays enabled.
Sealed final outcomes and optional training/intervention branches remain
outside this run. Publish frozen sources, configurations, test/support mirrors
and immutable metadata under the existing raw-array exclusion policy.
