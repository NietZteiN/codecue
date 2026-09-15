# Pre-registration — cue conflict in code

*Fixed 2026-09-14, before any model has seen an instance. Amendments are appended, dated,
never edited in place.*

## Predictions

P1–P7 as in PLAN.md §2, with δ = 2 percentage points (TOST) for every "no effect" claim and
the direct regime as the positive control that the equivalence test can detect an effect.

## Primary contrast (the paper)

**P3 (amended 2026-09-15, before any code data exist).** Within the prose regime, the split by
`value_written` is a CONTROL: after subtracting the matched neutral twin's rate under the same
split, the excess is predicted to be within δ in both halves (as in arithmetic). The claim is
instead over representation: cells whose target value is linearly decodable at the use site
(neutral-trained probe accuracy ≥ .9) have a lure excess within δ; cells where it is not do not.
Sign-consistent across ≥3 prompt variants, pooled CI excluding 0.

Because `value_written` is not randomly assigned, P3 is confirmed only together with **E10**,
the randomised version: the same prose instruction with and without the clause "state each
variable's value as you go". Prediction: the clause removes the lure effect (within δ).

## E10, fixed 2026-09-15 before the runs exist

Three prose instructions differing only in whether the model is told to state each computed
value (`plain`, `state`, `recompute`), level 5, 500 matched sets, three models. On the cell where
the effect lives (a variable computed as `len(xs)` and named like a sum), predicted: written-lure
rate under `state` and `recompute` is lower than under `plain`, and lowest under `recompute`.
Claim requires the ordering to hold in every model and a cluster bootstrap over sets excluding
zero for the `plain` minus `recompute` difference. A null here means the contamination is not
under instructional control and the mechanism section says so.

## Secondary contrasts

- Lure excess (lure rate − pseudo-lure rate on the neutral twin) per regime, per level, per
  target role; facilitation (congruent − neutral accuracy). Claim rule as in the arithmetic
  paper: sign-consistent across ≥3 demonstration seeds, pooled CI excluding 0.
- P6: lure excess in the trace regime as a function of trace accuracy across models and
  levels; predicted positive where trace accuracy < 60%.

## What would refute the mechanism

Lure excess within δ in the prose regime when the value was NOT written (P3 false), or above
δ in the trace regime for a model whose trace accuracy is above 90% (P2 false).

## Fixed analysis choices

1,000 matched sets per target role and level; cluster bootstrap over sets (2,000 draws);
FDR over layer × position for probes; probes trained on neutral only; selectivity control
keyed on the target identifier; positions located by character span of the identifier and of
the statement end, last token of the span.

## Table validation gate (PLAN.md §12)

Before any result is claimed, each model is asked on the neutral twin what a variable named
`<name>` most likely holds; names with < 80% panel agreement with the lure table are dropped
from analysis (kept in the data, flagged). This gate is fixed now so it cannot be tuned later.
