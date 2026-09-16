
## 2026-09-15 — E1 and E2 (pilot) on one h200 worker

E1: spans resolve for all 11 tokenizers in every regime (0 unresolved). Seven lure names are two
tokens on some tokenizers; span positions absorb that.

E2 pilot, level 3, 200 sets per target, four regimes, two models (~30 min of GPU in total).
Two bugs found and fixed from the stored generations, no rerun needed:
1. CodeLlama's trace continued past the blank line into invented problems, and the parser took
   the last `Answer:` — the same bug class as the arithmetic parser. Few-shot parsing now always
   cuts at the first blank line; a stopping criterion on the decoded tail ends generation there
   (Llama-2 tokenizers emit a blank line as two tokens, so no eos id catches it). CodeLlama trace
   accuracy 10% → 95%.
2. The codechain regime was truncated at 200 tokens for Llama-3.1-8B (parse rate 31–74%); now 448.

After the fix (lure excess = lure rate minus the matched neutral twin's rate of that digit):

| model | regime | target | acc (neutral) | lure | pseudo | excess |
|---|---|---|---|---|---|---|
| llama31-8b-it | direct | queried | 26.5 (29.5) | 14.5% | 12.0% | +2.5 |
| llama31-8b-it | direct | intermediate | 37.0 (38.0) | 23.0% | 20.5% | +2.5 |
| llama31-8b-it | trace | queried | 99.5 (99.5) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | trace | intermediate | 99.0 (99.5) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | prose | queried | 100.0 (100.0) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | prose | intermediate | 100.0 (100.0) | 0.0% | 0.0% | +0.0 |
| llama31-8b-it | codechain | queried | 15.0 (21.5) | 5.5% | 10.0% | -4.5 |
| llama31-8b-it | codechain | intermediate | 18.0 (30.5) | 5.0% | 16.0% | -11.0 |
| codellama-7b-it | direct | queried | 19.5 (20.5) | 12.5% | 11.0% | +1.5 |
| codellama-7b-it | direct | intermediate | 26.0 (26.0) | 19.5% | 23.0% | -3.5 |
| codellama-7b-it | trace | queried | 96.0 (96.0) | 0.0% | 0.0% | +0.0 |
| codellama-7b-it | trace | intermediate | 81.5 (95.0) | 2.0% | 0.0% | +2.0 |
| codellama-7b-it | prose | queried | 96.0 (93.5) | 0.5% | 0.5% | +0.0 |
| codellama-7b-it | prose | intermediate | 90.0 (94.0) | 0.5% | 1.5% | -1.0 |
| codellama-7b-it | codechain | queried | 24.0 (21.5) | 11.5% | 11.5% | +0.0 |
| codellama-7b-it | codechain | intermediate | 27.0 (28.5) | 19.0% | 22.0% | -3.0 |

Reading: (a) without a chain both models are near the floor (20–34%) and the **pseudo-lure is
high (11–23%)** because the implied quantities (len, sum, max, min of xs) are exactly the wrong
answers a failing model produces anyway — the matched-twin baseline is essential here, more than
in arithmetic, and the direct-regime excess is small (+1.5 to +2.5, CodeLlama intermediate −3.5).
(b) Trace and prose are at or near ceiling for both models, with zero lure: no variance for P3
at level 3 on these models. (c) **CodeLlama, trace regime, misleading name on the intermediate:
accuracy 81.5% against 95.5% neutral**, a 14-point interference under a chain that writes every
value — the first sign that code differs from arithmetic; needs the lure/pseudo split and more
seeds before it is a claim. (d) codechain (comments, no values) does not protect CodeLlama:
same accuracy and lure as direct.

Round 2 queued: level 5 for both pilot models; levels 3 and 5 for OLMo-2-1B and Llama-3.2-3B
(weak models, to get cells off the ceiling); codechain rerun for Llama-8B at 448 tokens.

## 2026-09-15 — round 2 (levels 3 and 5, four models): the lure enters the TRACE at the value step

The answer-level lure excess is small in every regime (direct +1 to +4 against a pseudo-lure of
5–23%; trace/prose ≈ 0 for the strong models). What moves is different from arithmetic:

| model | L | acc neutral→incongruent (intermediate, trace) | trace writes the LURE at the value step: incongruent / twin | answer-level lure excess |
|---|---|---|---|---|
| llama31-8b-it | 3 | 99.5 → 99.0 | 0.5% / 0.0% (excess +0.5) | +0.0 |
| llama31-8b-it | 5 | 99.5 → 97.5 | 2.0% / 0.0% (excess +2.0) | +0.5 |
| codellama-7b-it | 3 | 95.0 → 81.5 | 5.0% / 0.0% (excess +5.0) | +2.0 |
| codellama-7b-it | 5 | 91.0 → 80.5 | 4.0% / 0.5% (excess +3.5) | +2.0 |
| llama32-3b-it | 3 | 96.5 → 87.0 | 6.5% / 0.5% (excess +6.0) | +0.0 |
| llama32-3b-it | 5 | 96.0 → 82.0 | 15.0% / 0.0% (excess +15.0) | +1.5 |
| olmo2-1b-it | 3 | 34.5 → 40.5 | 3.5% / 10.0% (excess -6.5) | +4.5 |
| olmo2-1b-it | 5 | 33.0 → 27.5 | 6.5% / 5.5% (excess +1.0) | +3.5 |

With a misleading name on a list-defined intermediate (`count = sum(xs)`), the trace writes the
name's implied value (`count = 3`, i.e. len) instead of computing it, 3.5–15 points more often than
the matched twin, and accuracy falls 10–14 points. The final answer is then wrong but is not the
lure (it is v1 op v2 with a wrong v1), which is why the answer-level metric misses it. In
arithmetic the free chain wrote the lure 0.0–0.15% of the time. **In code the chain itself is
contaminated at the step that writes the value.** No such effect on the queried (binary) variable
(0% written lure): the lure substitutes for a list computation, not for a combination of known
values. Prose chains are near ceiling for the 3B–8B models; OLMo-2-1B is off-ceiling everywhere
(direct +3.5/+4.0; trace on the queried variable writes the lure +8.5 above twin).

Codechain (comments, no values) never protects and is unparsable for Llama-3.2-3B (21%); dropped
from the full runs, kept in the pilot record.

Queued next on the single worker: full level-3 behaviour (1,000 sets/target, direct+trace with
three demonstration seeds, prose) for seven models; the lure-table gate (E2b) per model.

## 2026-09-15 — full level 3, seven models, three demonstration seeds (E3, level 3)

1,000 sets per target. Claim rule: same sign in all three seeds and cluster-bootstrap CI
excluding zero (`*`). Lure and written-lure are excesses over the matched neutral twin.

| model | direct: lure excess (queried / intermediate) | trace: written-lure excess, intermediate | trace: accuracy interference, intermediate |
|---|---|---|---|
| codellama-7b-it | +1.6* / +0.4 | +2.3 | -4.5 |
| codegemma-7b-it | +2.9* / +2.2* | +3.0* | -2.3* |
| llama32-3b-it | +3.3* / +3.8* | +4.9* | -6.3* |
| llama31-8b-it | +2.0* / +3.3* | +0.5 | +0.2 |
| gemma3-4b-it | +0.9* / +4.8* | +0.0 | -0.1 |
| olmo2-7b-it | +2.3* / +3.2* | +2.6 | -6.4* |
| olmo2-1b-it | +6.6* / +5.7* | -4.1* | -1.7 |

- **P1 holds across the panel:** without a chain every model answers the name's implied value
  above its twin's rate on at least one target (+0.9 to +6.6, all claimable).
- **The value-step contamination survives the seed rule for two of seven models** (CodeGemma
  +3.0, Llama-3.2-3B +4.9, both with accuracy interference); OLMo-2-7B shows the accuracy drop
  (−6.4) without a claimable written-lure excess; CodeLlama's pilot effect (+5.0 at seed 7) is
  not sign-consistent across seeds. **The demonstration set moves this effect as much as it
  moved arithmetic accuracy** (Llama-3.2-3B: +7.2 / +1.3 / +6.1 by seed).
- OLMo-2-1B is lured in every regime, including at the trace's value step for the queried
  variable (+5.2).
- Llama-3.1-8B and Gemma-3-4B: trace at ceiling, nothing claimable on the intermediate.

**Gate v1 was broken:** every model completes `count = ` with `0` (a counter), so free
completion cannot reveal which list operation a name evokes. Gate v2 scores the candidate
expressions' log-probabilities instead (queued).

**Prose (free reasoning, chat template), level 3, seed 7 only:** written-lure excess is 0.0 to
+0.7 for every model and both targets after the `value_written` fix (the regex had been taking
the first operand of `count = 2 + 1 + 5 = 8`). So the contamination at the value step is specific
to the terse few-shot trace; a model reasoning in its own words is not contaminated even where its
trace is (Llama-3.2-3B: trace +4.9, prose +0.7). Prose accuracy is at ceiling for the 3B–8B
models and 69% for OLMo-2-1B.

## 2026-09-15 (validity pass, on request) — what checked out, what was wrong, what the finding really is

**Bug found and fixed:** `value_written` took the last `= <int>` in the clause, which in the
trace format `count = 5, zz = 1, vv = 4` is ANOTHER variable's value. The clause now also ends at
the next assignment (`, name =`); regression test added; every run re-scored. The level-3 numbers
did not change (the sweep had been reading rows the earlier re-parse had left intact), but the
metric was wrong in principle and would have produced false hits on any line ending in the lure.

**Verified by eye (not by metric):** random written-lure hits at levels 3 and 5, both models.
`sum_all = len(xs)` on `[5, 4]` is traced as `sum_all = 9` — the sum — and the rest of the chain
is computed faithfully from that wrong start (`zz = 14, vv = 28`). The name wins over the code
at the step that writes the value. Demos contain no table name (checked all seeds, both levels).
Parser: ≥99.7% parsed in every (model, regime); spot checks agree with a human reading.
Direct-regime pseudo-lure is high (11–23%) because a failing model's default wrong answer is
often `sum(xs)`: twins hit sum-family lures 30–40%, len-family 5–11%. The matched baseline handles
it; report per family. `99_selfcheck.py`: 0 failures over datasets, runs and sweeps.

**The finding, stated precisely.** Level 5, trace regime, pooled over 3 seeds, written-lure
excess over the matched twin on the first intermediate:

| model | excess | by seed | accuracy interference |
|---|---|---|---|
| OLMo-2-7B | +16.8* | +19.4 / +15.5 / +15.5 | −18.3* |
| Llama-3.2-3B | +12.3* | +14.3 / +7.8 / +14.8 | −12.9* |
| Llama-3.1-8B | +3.5* | +4.2 / +3.6 / +2.7 | −3.3* |
| CodeLlama-7B | +3.5* | +3.1 / +5.2 / +2.1 | −12.2* |
| CodeGemma-7B | −0.2 | | −0.4 |
| OLMo-2-1B | +0.2 | | −3.0* |

**It is one cell.** By (true operation → name family), pooled over seeds: `len(xs)` named as a
sum (`total`, `sum_all`, `acc`) is traced as the sum in 59% (OLMo-2-7B), 44% (Llama-3.2-3B),
12% (Llama-3.1-8B) of instances. Every other pairing — max→sum, min→sum, sum→len, max→len,
min→len — is 0–2%. So the claim is not "names contaminate chains"; it is: **when a variable is
computed as the length of a list but named as its sum, models trace it as the sum**, as if
repairing a perceived bug from the identifier. The `incongruent_alt` twin (same variable, a
non-sum name) shows ~0%, so it is the name family, not the variable. At level 3 the same cell
carries the effect but with 30× seed variation for CodeGemma; level 5 is seed-stable.

Prose chains: 0.0–0.7 everywhere. Direct: P1 holds panel-wide (+0.9 to +6.6).

Still needed: the lure-table gate v2 (queued) to confirm sum-family names carry the strongest
prior; per-family reporting in the sweep; the mechanism section of PLAN.md must be rewritten
around this one cell.

## 2026-09-15 (night) — the lure-table gate, and a bug in E10

**E2b gate (log-prob scoring, 7 models).** Only 12 of 25 names pass the pre-registered 80%
agreement bar. What passes: the arithmetic families — `double`/`twice`, `half`, `succ`, `diff`,
`gap`, `product`, and `count`/`n_items`/`length` (len, 6 of 7 models). What fails: **every
min/max name** (`smallest` 0.29, `low` 0.43, `peak` 0.43, `largest`/`max_val` 0.71), the
predecessor names (`prev_val` 0.14, `pred` 0.43), `scaled` (0.29, models read it as subtraction),
and — importantly — **the sum family** (`total`, `sum_all`, `acc` all 0.71, failed by Gemma-3-4B
and OLMo-2-1B, which read them as `len`).

This matters for the headline. The effect lives in the cell "computed as `len(xs)`, named like a
sum", and the gate says models do NOT uniformly read `total`/`sum_all`/`acc` as a sum; two of
seven read them as a length. Under the pre-registered rule those three names are dropped from
analysis, which would delete the cell. Two readings, to settle before the paper claims anything:
(a) the gate's context (`def f(xs):\n    total = `) is not the context the effect occurs in, so
the gate is mis-specified; (b) the effect is driven by the models for which the names DO evoke a
sum, and the gate correctly identifies where it should and should not appear. Test: recompute the
written-lure rate per model, restricted to sum-family names, and check it is near zero exactly for
Gemma-3-4B and OLMo-2-1B. If it is, (b) holds and the gate supports the finding rather than
killing it.

**E10 bug.** The first run produced only `neutral` and `neutral_alt` groups. The selector kept
sets whose instances had `target in (None, "v1")`, which every set satisfies through its neutral
twin, and then filtered instances to the same predicate, dropping each set's misleading rows.
Fixed to select sets by the role the misleading name sits on, with a guard that raises if no
misleading group is selected. Output deleted and re-enqueued; no analysis had been run on it.

**E10 (randomised prose instruction) is a null, and an uninformative one.** Level 5, 500 sets,
three models, three instructions (`plain` / `state` / `recompute`). Written-lure in the target
cell: OLMo-2-7B 1.4% → 0.0% / 0.0%; Llama-3.2-3B and Llama-3.1-8B 0.0% throughout. Prose accuracy
is 87–99%, so there was nothing for the instruction to remove. My pre-registered prediction
assumed prose carried the effect; it does not, and the experiment as designed could not have
failed to come out null. Recorded as a design error rather than a finding.

**E10b replaces it:** randomise the trace FORMAT, not a prose instruction. `trace` demos write
`count = 3`; `trace_expr` demos write `count = len(xs) = 3`. Same problems, seeds and models.
Prediction fixed in PREREGISTRATION.md before the runs. Enqueued.
