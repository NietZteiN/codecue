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

## E10b, fixed 2026-09-15 after E10 came out uninformative

E10 randomised the PROSE instruction, but prose shows no contamination to begin with (written-lure
0.0–1.4%, accuracy at ceiling), so the null there says nothing. The contamination lives in the
terse few-shot trace. E10b therefore randomises the TRACE FORMAT instead: `trace` demonstrations
write `count = 3`, `trace_expr` demonstrations write `count = len(xs) = 3`. Nothing else differs —
same problems, same three demonstration seeds, same models (OLMo-2-7B, Llama-3.2-3B,
Llama-3.1-8B), level 5.

Prediction: on the cell where the effect lives (computed as `len(xs)`, named like a sum), the
written-lure rate under `trace_expr` is lower than under `trace` for all three models, with the
paired difference's bootstrap interval excluding zero. A null means the contamination is not
removed by pointing the demonstration at the code, and the mechanism is not "the format lets the
model skip reading the right-hand side".

## Round 3, fixed 2026-09-16 before any of these runs exist

The mechanism found so far: in the terse trace, a sum-family name on a `len(xs)` variable makes
the model write the sum although the code's value is represented; the name's tokens cause it;
showing the expression removes it. Four tests of that account's boundaries.

**R3a. Format.** Same cell, level 5, three models (OLMo-2-7B, Llama-3.2-3B, Llama-3.1-8B), three
demonstration seeds, two further formats: `repl` (`>>> total` / `2`: a value without its
expression) and `comment` (`total = len(xs)  # 2`: expression and value on one line).
Prediction: written-lure excess under `repl` is comparable to `trace` (within a factor of two)
and under `comment` is within δ = 2 points of zero, for every model that shows the effect under
`trace`. Refuted if `repl` is null (the effect is specific to our format) or `comment` is not
(the expression on the line does not protect).

**R3b. Other names, a middle step.** Level 6 = the level-5 program with the middle unary step
as target; congruent names are `double`/`half`/`succ`/`pred` (gate 100%), lures are unary names
of other families and list names. Seven models, three seeds, trace. Prediction: at least one
unary lure family shows a claimable written-lure excess on at least two models. Refuted if none
does — then the effect is specific to sum-names on list aggregates and the paper says so.

**R3c. Scale.** CodeLlama-34B-Instruct, level 5, the cell, trace, three seeds. Prediction: it
behaves like the other code models (max→sum rather than len→sum) with a claimable excess on at
least one of the two. Refuted if both are within δ — then the failure diminishes with scale.

**R3d. Real code, more power.** The CRUXEval subset widened to 89 functions (48 length, 38 loop
counters, 3 max), all renamed to `total`. No prediction of an effect: this tightens the bound.
Reported as the paired misleading-minus-neutral accuracy with its interval, used-downstream only.

**Outcomes (2026-09-17, results/NOTES.md):** R3a refuted for the REPL format (3–60× weaker than the trace) and
partly for comments (≈0 in two models, +6.8 in Llama-3.2-3B). R3b null. R3c refuted (34B: len→sum +0.0, max→sum +1.8 [1.0, 2.8], inside δ).
R3d null with the bound tightened to ±5/±10 points.

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
