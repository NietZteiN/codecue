
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

## 2026-09-16 — E10b: the contamination is caused by the trace format, and removed by it

Pre-registered before the runs. `trace` demonstrations write `count = 3`; `trace_expr`
demonstrations write `count = len(xs) = 3`. Nothing else differs: same problems, same three
demonstration seeds, same models, level 5. Paired over instances, bootstrap over matched sets.

| model | wrote the lure, `trace` | `trace_expr` | paired drop [95% CI] |
|---|---|---|---|
| OLMo-2-7B | 58.8% | 3.6% | **+55.2 [49.9, 60.2]** |
| Llama-3.2-3B | 43.5% | 0.4% | **+43.2 [38.2, 47.7]** |
| Llama-3.1-8B | 12.4% | 0.0% | **+12.4 [8.8, 16.0]** |

All three sign-consistent across seeds, all intervals excluding zero: the prediction holds.
Accuracy in the affected cell rises with it, 37.1% → 92.6% (OLMo-2-7B) and 51.0% → 99.4%
(Llama-3.2-3B).

**The control that makes this a mechanism rather than a prompt trick.** `trace_expr` is not a
general accuracy boost. On neutral problems it adds 0.3–2.8 points. On every (operation, name)
pairing OTHER than the affected cell the written-lure rate is already 0.0–0.8% and stays there,
with accuracy moving 92.6% → 99.3%. The 55-point drop is specific to the one cell.

**So the claim is now causal and narrow.** When a demonstration writes only `name = value`, a
model reading `acc = len(xs)` can produce the value the NAME implies without ever committing to
the right-hand side; making the demonstration write `name = expression = value` removes that,
because the expression has to be stated before the value. The identifier wins only where the
format lets the model skip the code. This replaces the earlier "writing the value protects"
account, which the arithmetic paper refuted, with something the arithmetic task could not have
shown: there, every chain step restates the equation already.

Remaining for a paper: probes/patching on the cell (E5/E6, now narrow), and CRUXEval renamed (E8)
to see whether it survives outside synthetic code.

## 2026-09-16 — baseline bug fixed; the effect is a family split, and sum is NOT a default

**Bug.** `value_written` was stored for one role per row: the target for misleading rows, the
QUERIED variable for neutral rows. Every written-lure baseline therefore compared a misleading
row's intermediate against its twin's queried variable. Fixed: rows now carry `values_written`
per role (runner + `61_reparse.py` backfill), and the sweep reads the twin on the same role.
Corrected L5 excess on the intermediate, trace regime: OLMo-2-7B +17.2*, Llama-3.2-3B +12.4*,
CodeLlama-7B +4.4*, Llama-3.1-8B +3.5*, OLMo-2-1B +3.7*, CodeGemma-7B 0.0, Gemma-3-4B 0.0. The
numbers barely moved because neutral v1 accuracy is 94–100%, so the twin baseline is ~0 either
way — but the metric was wrong and would not have been for a weaker model.

**Two design facts a reader needs.** (1) Max- and min-family names can never be lures on a
list-defined variable: `max(xs)` is an element of `xs`, which rule R2 forbids (a lure must not
be copyable from the prompt). The testable name space is therefore {len, sum}. (2) The full
matrix, excess over twin, L3+L5 pooled, three seeds:

| model | len→sum | max→sum | min→sum | sum→len | max→len |
|---|---|---|---|---|---|
| Llama-3.2-3B | **+35.3** | +0.5 | 0 | 0 | 0 |
| OLMo-2-7B | **+41.8** | +1.4 | 0 | +3.0 | 0 |
| Llama-3.1-8B | **+8.0** | +0.4 | 0 | 0 | 0 |
| CodeLlama-7B | +2.6 | **+9.1** | +1.4 | +1.0 | +0.8 |
| CodeGemma-7B | +0.1 | **+5.4** | 0 | 0 | 0 |
| Gemma-3-4B | 0 | 0 | 0 | 0 | 0 |
| OLMo-2-1B | +2.7 | +3.5 | 0 | +10.8 | +8.1 |

**Reading.** The direction is always toward SUM: a sum-named variable gets traced as the sum;
a len-named variable is never traced as the length (sum→len ≈ 0 for every model above floor).
Which code operation the name overrides splits by family: general instruct models override
`len`, the two code models override `max`. Gemma-3-4B shows nothing (its gate reads sum-names
as `len`). OLMo-2-1B is at floor (76% neutral accuracy on this variable) and noisy in every
direction; it should be reported as such, not as evidence.

**Sum is not a default.** On NEUTRAL programs (no misleading name), when the trace gets a
len-variable wrong it writes `max(xs)` (23–44%) or the length ±1 (41–50%), and `sum(xs)` only
5–32%. So the sum appears only when the NAME says sum. This rules out "sum is what the model
computes anyway" and leaves the name as the cause — consistent with E10b, where showing the
expression removes it.

The paper's claim, restated: a sum-family identifier makes a model trace a list aggregate as the
sum, overriding `len` in general models and `max` in code models, only under a format that
lets it write the value without stating the expression.

## 2026-09-16 — probes (E5, three models): the value is intact; the name wins at readout

Neutral-trained linear probes, tested on the affected cell (computed `len(xs)`, named like a
sum), level 5, trace regime. The decision token `pre@v1` is the `=` before the trace writes the
variable's value; the variable is the first traced step, so the state there is identical in
forced and free generation — it is what the model holds when it decides.

| model | best layer | neutral acc | reads CODE (len) | reads NAME (sum) | max "reads name" over all layers | writes the sum (behaviour) |
|---|---|---|---|---|---|---|
| Llama-3.2-3B | 28 | 0.99 | **0.90** | 0.01 | 0.02 | 44% |
| OLMo-2-7B | 32 | 1.00 | **0.85** | 0.01 | 0.02 | 59% |
| Llama-3.1-8B | 16 | 1.00 | **1.00** | 0.00 | 0.02 | 12% |

The name's value is not linearly decodable at ANY layer (≤ 0.02). The code's value is
decodable at 85–100% at the best layer and rises monotonically through the network. Yet the
model writes the sum in 12–59% of these instances. **This is a readout failure, not a
representation failure**: the computation is correct in the residual stream and the output
head produces the name's value anyway.

This is the opposite of the arithmetic paper's exception (OLMo-2-1B: value NOT decodable at
the value step, lured). The two papers therefore do not share a mechanism. Arithmetic: the
chain protects where the value is represented. Code: the value is represented and the chain
still writes the name's value. The bridge between the papers is the contrast, not a common law.

Caveat to report: the control probe (labels = hash of the variable's name) also scores 1.00 at
`pre@v1` for two models (0.80 for the third), so name identity is trivially decodable there and
Hewitt–Liang selectivity is ~0. The value probe cannot be reading the name, because (a) on
neutral training data name and value are independent, and (b) the misleading test names never
occur in training. But the selectivity number must be stated.

Next: patching (E6). If the value is intact and the name's tokens are the cause, replacing the
name's activations with the neutral twin's at the decision token should restore the output.

## 2026-09-16 — patching (E6), decision-token site: one position, one layer, restores the output

Source = matched neutral twin, destination = the incongruent instance, read = the digit the
model would write at `pre@v1`. Three models, ~285 pairs each in the affected cell.

**Decision token (`pre@v1`), main contrast.** Replacing the residual stream at that single
position with the twin's, at a single layer, removes the lure write almost completely from the
middle of the network on, with ~0% damage to correct instances:

| model | layers | lure removed by single layer (L0 / L6 / L9 / L12 / L15 / L18+) | ALL layers |
|---|---|---|---|
| OLMo-2-7B | 32 | 0 / 4 / 14 / 25 / 84 / 96–97% | 97% removed, 2% damage |
| Llama-3.2-3B | 28 | 1 / 13 / 49 / 91 / 99 / 99–100% | 100% removed, 0% damage |
| Llama-3.1-8B | 32 | 0 / 2 / 100 / 100 / 100 / 100% | 100% removed, 0% damage |

So whatever drives the sum write is present in the decision token's residual stream from
roughly the middle of the network (L9–L15), and it is separable from the code's value: the
probe reads the code's value at those same layers, and swapping in the twin's vector (which
also holds the code's value) removes the sum without touching anything else. Two things live
in one vector; the output head reads the wrong one. This is the readout account, now causal.

**Word control** (`neutral_alt → neutral`, both sites): damage 0.0–1.8%. Swapping one neutral
name's activation for another changes nothing, at either site.

**Alt-lure control is degenerate in this cell** and is not reported: every sum-family name
implies the same value, so `incongruent_alt` has the same lure.

**Name site: first attempt invalid, redone.** Patching only the name's DEFINITION token left
every later use (`ww = total + 3`, `Trace: total =`) unpatched, so at layer 0 (token identity)
the program referred to an undefined variable — damage 75–80% at L0, ~0 at L6+. Two-token
`sum_all` was patched at one token (no neutral name is two tokens), removal 0%. Redone: every
occurrence of the name, every token, token-aligned pairs only (`total`, `acc`; `sum_all` pairs
skipped and counted). Queued. From the first attempt, single early layers already showed
partial removal at ~0 damage (L3: 56% Llama-3.1-8B; L6: 40% OLMo-2-7B, 23% Llama-3.2-3B), so
the name's early representation is at least part of the cause.

## 2026-09-16 — patching, name site (redone): the name's tokens are the origin

Every occurrence of the name (definition, uses, trace prefix), every token, replaced with the
neutral twin's at one layer; token-aligned pairs only (`total`, `acc`: 181 pairs per model;
104 `sum_all` pairs skipped). Read at the decision token.

| model | lure before | removed, single layer L0 / L6 / L10 / L12 / L14 / L16 / L18+ | damage | word control |
|---|---|---|---|---|
| OLMo-2-7B | 44% | 97 / 95 / 67 / 47 / 34 / 11 / ≤1% | 0–2% | 0.7% |
| Llama-3.2-3B | 30% | 100 / 93 / 69 / 58 / 15 / 5 / ≤5% | 0–1% | 1.0% |
| Llama-3.1-8B | 0% | (all of its lure writes are on `sum_all`, which is two tokens — no aligned pairs) | | |

Replacing the name at layer 0 alone removes the effect completely with no damage. Removal
decays with layer and is gone by L16–L18. The decision-token curve is the mirror image: removal
there begins at L9–L12 and is complete by L15–L18. The two curves cross where the information
has moved from the name's tokens into the decision token. That is the causal path:

    name tokens (L0–L12)  →  decision token (L12–L18 onward)  →  output head writes the sum,
    while the code's value sits in the same decision-token vector, probe-decodable at 85–100%.

Three independent measurements now converge on one account: the value is computed (probe), the
name's tokens are the origin (name-site patch), the influence arrives at the readout position
mid-network and is separable from the value there (decision-token patch), and the output head
reads the name's contribution rather than the value. The format manipulation (E10b) removes it
because writing the expression forces the value into the output before the name can.

Limitation to state: `sum_all` (two tokens) could not be patched at the name in a token-aligned
way, and Llama-3.1-8B's lure writes are all on that name; its name-site result is therefore
missing, not null.

## 2026-09-16 — E8, renamed CRUXEval: a null, and a bounded one

48 CRUXEval functions assign a variable from `len(...)`; 43 use it downstream. Each rendered
original / neutral (`v`) / misleading (`total`), AST-renamed, execution-verified. Direct and prose
regimes, seven models. Paired misleading-minus-neutral accuracy on the 43 used-downstream
functions: every model's interval includes zero (e.g. Llama-3.1-8B direct +7.0 [0.0, +16.3];
OLMo-2-7B prose −4.7 [−16.3, +7.0]). The reasoning states the SUM for the length variable in
0–6% of the 16 summable cases under either name.

**Why this is consistent with the synthetic result rather than against it.** The contamination
lives in the terse few-shot TRACE format (`v = 3`). Prose reasoning never showed it on synthetic
code either (0.0–0.7%), and the direct regime's effect there was answer-level and small. CRUXEval
has no trace-format analogue for arbitrary code with loops and strings, so the regime in which
the effect occurs was not testable here. What E8 shows is that in the two regimes people
actually use on real code, renaming a length variable to a sum-like name does not move accuracy
beyond noise on this subset.

**Power.** n = 43, baseline accuracy 8–54%, CI half-width ≈ 12–16 points. A 5-point effect
would not be detectable. So: no evidence of an effect on natural code in these regimes, and no
power to rule out a small one. The paper states it that way and does not claim generality to
real code.

**Scope of the paper, final.** The claim is about the terse worked-example trace on synthetic
programs: a sum-family identifier makes the model write the sum for a variable the code computes
otherwise, the code's value is represented but not read out, the name's tokens are the causal
origin, and showing the expression in the demonstration removes it. External validity beyond
that format is an open question the paper names, not a result it has.

All GPU experiments for this paper are complete as of this entry.

## 2026-09-17 — Round 3: the boundaries of the effect (R3a–R3d, pre-registered)

Four pre-registered follow-ups ran on one h200 worker (80 jobs, 0 failed). Two predictions were
refuted, one partly refuted, one bound tightened. Together they shrink the claim to a specific
format and a specific model size, and they say so cleanly.

**R3a — format. Refuted for the REPL, holds for comments in two of three models.** The
len→sum cell at L5, written-lure excess over the matched twin, three demonstration seeds pooled:

| model | trace | repl | comment | trace_expr |
|---|---|---|---|---|
| OLMo-2-7B | +58.4 | +9.5 [7.6, 11.5] | +0.0 | +3.4 [2.1, 4.7] |
| Llama-3.2-3B | +43.4 | +12.6 [10.4, 14.9] | +6.8 [5.1, 8.4] | +0.4 |
| Llama-3.1-8B | +12.4 | +0.2 | +0.1 | +0.0 |

The prediction was that a REPL transcript (`>>> total` / value) would show an excess within a
factor of two of the trace. It shows 3–60× less. The comment format (`total = len(xs)  # 3`)
was predicted within 2 points of zero: true for OLMo-2-7B and Llama-3.1-8B, false for
Llama-3.2-3B (+6.8, claimable). The ordering trace > repl > comment ≈ trace_expr holds in every
model, which is what the mechanism predicts (the closer the expression sits to the value, the
less room the name has), but the magnitudes fall off far faster than "any value-only format".
Neutral accuracy: repl is the LEAST accurate format (86 / 92 / 98%), comment and trace_expr the
most (96–100%), so the REPL's smaller excess is not greater care; the transcript form simply
does not read the value off the name the way the assignment-list form does.

**R3b — level 6, a unary middle step. Null.** 3,000 incongruent instances per model on `v2`
(`//2`, `*2`, `+c`, `-c`), lure families double/half/succ/pred/sum/len/max/min. Overall excess
on v2: OLMo-2-7B +0.3, Llama-3.2-3B +0.1, Llama-3.1-8B +0.0, CodeLlama-7B +0.6, CodeGemma
+0.2, Gemma-3-4B +0.0; OLMo-2-1B +2.3 at 38% neutral accuracy (not interpretable). The largest
single (op, family) cell in a reliable model is CodeLlama-7B `//2` with a `len` name, +7.1
(n ≈ 100); nothing in the sum family moves. The contamination is a property of the list
aggregate step, not of "a strong-prior name on any step".

**R3c — CodeLlama-34B. Refuted.** Trace, L5, three seeds: len→sum +0.0 (n = 855), max→sum +1.8
[1.0, 2.8] (n = 831), every other (op, family) 0.0; neutral trace accuracy 98.9%. The max→sum
residue is sign-consistent across seeds and its interval excludes zero, so it passes the claim
rule, but it sits inside the pre-registered equivalence margin (δ = 2), which is the refutation
criterion. The prediction was that the 34B code model would behave like the 7B code models
(CodeLlama-7B max→sum +9). It shows at most a fifth of that. In this
panel the effect is a ≤8B phenomenon; two 7B-class models (CodeGemma, Gemma-3-4B) were already
near zero, so size is a sufficient but not the only condition for immunity.

**R3d — CRUXEval widened to 89 functions (48 `len`, 38 loop counters, 3 `max`; 84 used
downstream). Null, tighter.** Paired misleading − neutral accuracy, direct: OLMo-2-7B +1.2
[0.0, 3.6], Llama-3.2-3B +1.2 [−2.4, 4.8], Llama-3.1-8B −3.6 [−9.5, 2.4], CodeLlama +2.4
[0.0, 7.1], CodeGemma +0.0, Gemma-3-4B −2.4 [−6.0, 0.0], OLMo-2-1B −3.6 [−8.3, 0.0]. Prose:
−1.2 to +6.0, every interval covering zero. By kind, one of 28 intervals excludes zero
(Llama-3.1-8B direct, counters, −10.5 [−21.1, −2.6]) — one nominal exclusion in 28 uncorrected
tests, not claimed. Reasoning writes the sum for the renamed variable in ≤5% of summable cases
under either name. Bound: ±5 points (direct), ±10 (prose), against ±12–16 before.

**What the paper can now say.** A sum-family identifier makes small (≤8B) models write the sum
for a list aggregate in a terse `name = value` trace; the value is computed and not read out;
the name's tokens are the causal origin. The effect is largely specific to that trace format
(3–60× weaker as a REPL transcript, ≈0 as code comments), specific to the aggregate step (null
on a unary step), reduced to ≤2 points at 34B, and undetectable on real code in the direct and prose regimes to
within ±5/±10 points. That is a located, format-dependent unfaithfulness with a measured
mechanism and measured boundaries — a short paper, not a general vulnerability claim.

GPU worker released 2026-09-17 (job 409808). No further runs planned.

## Verification after the manuscript rewrite (2026-10-02)

This entry supersedes stronger causal and equivalence interpretations in the earlier ledger.
The main numerical effects remain, with corrected inference and explicit protocol limits.

- Initial number/table regeneration was identical. Behavioral dataset/run checks pass with
  46 warnings, all in archived 200-instance pilot datasets. Level 6 is now checked too.
  The final self-check has **3 failures** from the newly added probe split audit (below).
- Cell intervals previously treated demonstration repeats independently. They now resample
  matched sets with all their repeats together; cached deterministic cell estimates keep
  narrative macros and tables identical. Regression tests cover clustering and unequal
  cluster sizes; all 33 CPU tests pass. `cell_inference.json` records cell and format inference.
- Main written-lure excess remains +58.4, +43.4 and +12.4 points. Corrected 95% intervals
  are [53.0, 63.5], [38.5, 48.1] and [8.8, 16.0]. All retain consistent signs across three
  demonstration sets. Paired format reductions also retain positive intervals in all models.
- Equivalence now uses actual 90% cluster intervals from raw observations, while reliable
  effects use 95%. Of 192 contrasts, 150 are equivalent, 36 have reliable effects without
  equivalence, and 6 are inconclusive. Earlier summaries used conservative 95% equivalence.
- CodeLlama-34B maximum-to-sum is +1.8 [0.7, 3.1] points: a reliable positive effect outside
  the equivalence criterion. It supports the registered pairing and reliable-effect
  criterion; the earlier claim that this prediction was refuted was incorrect.
- CRUXEval neutral accuracies cover all 89 functions; paired contrasts use the 84 functions
  whose renamed target is used downstream. The manuscript now distinguishes those denominators.
- The runs retained identifiers that failed the planned 80% panel meaning gate. This is a
  protocol deviation, now disclosed in the methods, appendix and limitations. It remains a
  substantive limit on interpreting the groups as meanings shared by every model.
- Removed an editorial instruction from the printed bibliography. Both papers anonymously
  cite their companion and distinguish their tasks. Strict builds and PDF review are logged
  in `log/verification_2026-10-02/`. No fresh GPU run was performed during the audit.
- **Blocking probe finding:** each saved probe trained on 2,000 neutral programs from
  `test_sets.jsonl`. All 587 neutral and 285 misleading-name evaluation programs overlap
  training in each of the three models. Unseen identifiers do not make the programs held out.
  The 85/90/100% readouts cannot support the claimed held-out decodability.
- The selector now reads `train_neutral.jsonl`, excludes canonical test computations, and
  training/self-check guards reject shared matched-set IDs or program keys. Regression tests
  cover renamed copies and saved-cache overlap. Fresh outputs go to `probecache_disjoint/`
  and `probes_disjoint/`, preserving the original caches and results for the audit.
- **Required rerun:** OLMo-2-7B, Llama-3.2-3B and Llama-3.1-8B, level 5, trace, queried role v1,
  three probe seeds plus controls, independent neutral training. Recompute probe numbers and
  figures from the validated new outputs before restoring any decodability claim. Patching
  uses matched neutral interventions rather than a fitted probe and is unaffected by this
  training-pool error. The manuscript labels all current probe scores provisional.

## Readability and experiment follow-up (2026-10-02)

Both manuscripts received a readability pass: concrete opening questions, simpler definitions
of probes and controls, shorter claims, and explicit separation of aggregate associations
from causal explanations. Both strict builds retain a four-page body. The author authorized
the blockers and additional experiments with one or two GPUs for about a day. Two 24-hour
H100/H200 workers were requested (439652, 439653); A30/H100 cards were occupied. The workers remain pending. The fixed task
list and analysis rules are in `../probing/log/round4_2026-10-02/manifest.json`. This pass
includes disjoint code probes under all three demonstration sets, six additional arithmetic
model-variable pairs, and a Gemma per-token sweep. Results remain pending; existing caches
are preserved, and no scientific claim is restored on the strength of submission alone.

Preflight now passes 62 arithmetic CPU tests, four tokenizer/probe checks in CPU job
439688, and 42 code CPU tests. CPU job 439757 validates 2,464 sampled layouts across all
five tokenizers: no pre-value token contains the supplied digit. New caches enforce this
per row, and collectors require that validation flag. An initial preflight job (439735)
used the wrong arithmetic training filename; that path was corrected before the successful
rerun. Both rendered bodies have no out-of-page text. Layout-only builds with synthetic
values confirm the added appendix fits without expanding either four-page body; those
files live under the explicitly marked `layout_dryrun/` folder and never supply results.
CPU collector 439676 will audit completed experiments and rebuild both papers after the
workers exit. Current code probe claims remain provisional pending the disjoint reruns.

### Disjoint probe collection

Split validation passed for all nine reruns. Build status: True. Current scores and demonstration-set repeats are in `summary/disjoint_probes.json`. The original overlapping caches are historical and no longer supply paper numbers.

### Reviewer follow-ups (2026-10-03)

The nine disjoint probe reruns pass split validation and now supply the manuscript. All 2,565 generated prefixes match the cached pre-value state. Pooled true-digit probe accuracy on lure writes is 96.4%, 95.7% and 99.7% for OLMo-7B, Llama-3B and Llama-8B, respectively; intervals cluster programs across demonstrations. None of total/sum_all/acc passes the original 80% panel gate; its estimate is unavailable. Model-specific and per-name sensitivities are exploratory, preserving the deviation. Both new format controls have completed and passed validation for both models and all three demonstration sets. All 3,420 annotation evaluation prompts match expression prompt token counts. Paired pooled excess remains 56.6/49.6 points under annotations, versus 41.3/14.9 under numeric elaboration (OLMo/Llama). Summary and appendix tables retain clustered intervals and differences relative to trace/expression baselines. Final strict build passes with a four-page body; PDF tables were inspected.

### Disjoint probe collection

Split validation passed for all nine reruns. Build status: True. Current scores and demonstration-set repeats are in `summary/disjoint_probes.json`. The original overlapping caches are historical and no longer supply paper numbers.

### Disjoint probe collection

Split validation passed for all nine reruns. Build status: True. Current scores and demonstration-set repeats are in `summary/disjoint_probes.json`. The original overlapping caches are historical and no longer supply paper numbers.

### Final manuscript integration (2026-10-03)

The abstract, main results, conclusion and limitations now incorporate the error-conditioned
probes, identifier-gate audit and both format controls. Correct-digit accuracy on actual lure
writes is 96.4/95.7/99.7% for OLMo-7B/Llama-3B/Llama-8B. The verified pre-value prefixes and
name-control limitations accompany that result. Neutral annotations retain 56.6/49.6 points
of excess, while numeric elaborations reduce it to 41.3/14.9 (OLMo/Llama). The paper states
that none of the main identifiers passes the original panel gate and its filtered estimate
is unavailable. All quoted follow-up values are generated from the collected summaries.
The selfcheck and strict anonymous ACL ARR build pass: four-page body, 133-word abstract,
no missing assets or unresolved references. Rendered pages were inspected. Logs are in
`../log/paper_update_2026-10-03/`; the joint verification record is in the arithmetic repository.

### Targeted validation launch (2026-10-03)

Round-six independent layer selection has completed in all nine model/demo cells. Five-fold cross-fitting groups canonical computations, selects layers from neutral validation folds only and evaluates each program in its held-out fold. Pooled correct-digit accuracy on lure writes is 96.4% (OLMo-7B), 95.5% (Llama-3B), 99.7% (Llama-8B); conditional canonical-program intervals and paired changes are in `summary/round6_crossfit_probes.json`. The independent name replication has a fixed 16-name candidate list, the original seven-model 80% panel gate, and 200 fresh computations excluding old training/test/demo programs. Screened names will freeze before behavioral evaluation in three affected models and CodeGemma-7B control, two formats, three demo sets. Empty qualifying sets are unavailable. Two GPU workers (440673/440674) are pending priority; collection follows as 440686. All 47 code tests and three updated selection tests pass. Protocol and provenance: `../../probing/log/round6_2026-10-03/manifest.json`. Current manuscript numbers remain unchanged.

### Targeted validation completed (2026-10-03)

The original seven-model meaning gate selects sum_of_values, sum_of_items and sum_of_elements from the fixed fresh candidate list. All 24 replication cells on 200 fresh computations validate. Pooled trace/expression excess in points is 91.1/0.8 (OLMo-7B), 61.5/0.0 (Llama-3B), 16.7/0.0 (Llama-8B), and 0.0/0.0 (CodeGemma-7B); canonical-program clustered intervals, per-name and per-seed results are in `summary/round6_identifier_replication.json`. A collector tuple/list comparison was repaired through JSON normalization; the dataset and behavioral results are unchanged. Four regression checks and all three joint analyses validate. The round-six outputs are separate from current manuscript numbers.

### Round-six manuscript integration (2026-10-03)

The current draft now uses cross-fitted error readouts: 96.4/95.5/99.7% correct-digit
accuracy in OLMo-7B/Llama-3B/Llama-8B. The earlier full-neutral readouts remain explicitly
labeled in the appendix. The main results and new appendix report all 16 screened names,
the three frozen selections, and their replication on 200 fresh computations. The original
gate deviation remains disclosed; new probes and patches were not run on the screened
names. Conditional bootstrap intervals and empirical-zero limitations accompany the
results. `scripts/80_round6_tables.py` supplies numbers and four new tables through
`scripts/51_numbers.py`. Selfcheck: zero failures, 49 existing warnings. Strict anonymous
build: four-page body, 12 pages total, 146-word abstract; rendered body and new tables
inspected. Logs: `../log/paper_update_round6_2026-10-03/`; joint verification:
`../../probing/log/paper_update_round6_2026-10-03/verification.json`.

### Terminology (2026-10-06)

The abstract and opening example now define name errors: a trace writes the name-suggested
value rather than the computed value. The main metric is excess name errors relative to
the matched neutral baseline. All prose and generated table labels use this wording; the
companion arithmetic citation uses its new title. Main tables remain alongside the results.
Number macros and result summaries are unchanged. The strict build and rendered-page
review pass with a four-page main body. Verification: `../log/terminology_2026-10-06/`.

### Abstract clarity (2026-10-07)

Rewrote the abstract around a length-versus-sum example, explained what a code trace writes,
and identified the extension of Kudo et al.'s arithmetic analysis. The naming effect compares
the rate of incorrect name-suggested writes against ordinary names. Internal measurements
and the worked-expression intervention are explained in plain language. Abstract: 192 words.
Strict build and visual review pass with all main content inside four pages. Only the
abstract changed in the LaTeX source; number macros and result summaries are unchanged.
Before/after evidence: `../log/abstracts_2026-10-07/`.

### Introduction and explanation (2026-10-07)

Rewrote the opening around a length-computed variable named `sum_all`: the model writes
8 instead of 2 for `[5, 3]`. Changing worked examples to include the computation changes
this trace, motivating the behavioral study before introducing internal measurements.
Linear probes predict the true digit from activations immediately before the model writes
the value. Recovering 2 while the model writes 8 establishes recoverable information,
not its use. The abstract uses the same explanation (199 words). The screened-name
replication remains in the body and appendix. Strict checks and visual review of all four
main pages pass. Number macros and result summaries are unchanged; LaTeX edits are confined
to the abstract and introduction. Evidence: `../log/narrative_2026-10-07/`.

### Four-page text including limitations (2026-10-07)

Shortened the main figure/table captions, a repeated probe explanation and related work.
The abstract, introduction narrative and numerical results remain unchanged. Limitations
now use three bullets for scope, internal measurements and design deviations, preserving
the identifier-selection deviation, unsupported REPL prediction and limits of the screened
replication. All text through Limitations fits four pages; References starts on page five.
Number-macro occurrences, generated numbers, result summaries and figure assets are unchanged.
The appendix source is unchanged. Strict checks and visual review of pages 1--4 pass.
Evidence: `../log/concise_2026-10-07/`.

### Abstract narrative (2026-10-07)

The abstract now follows the 2-versus-8 trace through the behavioral comparison, error-case
probe readouts, patches, and worked-example intervention. It describes incorrect sum writes
directly and includes the independently screened-name replication on 200 fresh programs.
The ending states that showing the operation helps the trace follow the code rather than
the name. The body and limitations retain the decodability-versus-use distinction, patching
caveats and original identifier-selection deviation. Only the abstract changed; all numerical
inputs and figure assets are unchanged. Evidence: `../log/abstract_story_2026-10-07/`.

### Contribution and implication (2026-10-07)

The abstract connects the misleading trace to the question of whether the correct digit
can be recovered immediately before the wrong write. The observed separation motivates
the demonstration-format intervention; the ending explains how showing the operation
helps traces report computed values. The argument guide reflects this connection.
LaTeX edits are confined to the abstract. Decodability-versus-use, patching caveats and
identifier-selection deviations remain in the unchanged body and limitations.
Numerical inputs and figures are unchanged. Evidence: `../log/contribution_2026-10-07/`.

### Direct introduction ending and code abstract (2026-10-08)

The abstract now explains what a trace reports before introducing the 2-versus-8 example.
It follows that conflict through the correct digit predicted immediately before wrong
writes and the worked-example intervention. The demonstration change is described in
words, avoiding a second numeric example; secondary result lists are omitted. The
introduction keeps the opening on the same 2-versus-8 example and ends with the observed
probe/write contrast and the effect of showing the
operation. Decodability-versus-use, patching and scope caveats remain in the unchanged
Results and Limitations. Evidence: `../log/direct_story_2026-10-08/`.

### 2026-10-08 — Direct scientific abstract

Rewrote the abstract to lead with the main result, summarize its experimental evidence,
and state the implication directly. Illustrative examples remain in the introduction;
secondary results remain in the body. No scientific results or numerical inputs changed.
Build and layout verification: `log/result_first_abstracts_2026-10-08/verification.json`.

### 2026-10-08 — Abstracts for readers outside the project

Kept the direct result–evidence–implication structure and reduced terminology. Explained
what the models report, what changes between the two problem versions, and how the
internal predictions are measured. Preserved the main result numbers and scientific
scope; no experimental results changed.
Verification: `log/accessible_abstracts_2026-10-08/verification.json`.

### 2026-10-08 — Figure readability and shorter limitations

Removed the Design deviations limitations bullet. Figure 1 now places the real program
and both complete generated assignment sequences side by side, with correct length,
name-suggested sum and final answers labeled. Figure 2 separates incorrect sum writes
removed by activation replacement, correct-digit prediction and damage to correct writes.
The damage panel uses an explicit 0–5% scale. All eight plotted numerical series and
the selected real example are unchanged; methods and appendix retain the design disclosures.
Verification: `log/figure_clarity_2026-10-08/verification.json`.

### 2026-10-08 — NAACL review revisions and queued comparison

The main evidence table now combines correct-digit readouts on actual wrong writes,
95% intervals and independent computation counts with the independently screened-name
replication. Its two panels label the separate cohorts; the full behavioral model panel
is retained in the appendix. The introduction distinguishes the contribution from known
identifier sensitivity and from the companion arithmetic study. Existing results, abstract
and figures are unchanged. Both the body and Limitations fit within four pages.

The prospective prompt-end versus pre-write design was committed as `68b64f2` before
submission. It reuses the original 2,000-row neutral training split, the nine model/demo
combinations, three probe seeds and observed outcome cohorts, with independently selected
layers and paired canonical-computation intervals. Added boundary/cohort/prediction guards
pass seven tests; the full CPU suite passes 55 tests. All nine input dry runs pass.

GPU job 449113 (a30) started on g-02-01 at 21:11 UTC; extraction is progressing
without an error in the observed training batches. Job 449114 (h100) is queued. CPU release
job 449115 depends on both succeeding. No validated comparison has been released or
added to the paper. Integration remains pending; `make evidence` adds the comparison only
after a validated release. Protocol and submission records are in
`docs/PROMPT_PROBE_COMPARISON.md` and `docs/PROMPT_COMPARISON_STATUS.json`.
Verification of the current revision: `log/naacl_revisions_2026-10-08/verification.json`.

### 2026-10-08 — Accuracy pass, then readability pass

Regenerated all numerical inputs and checked them against the saved summaries. Existing
number values and all 17 result summaries are unchanged; three added keys display the
same control accuracies as percentages at greater precision. The reported ordinary-name
accuracy is now explicitly final-answer accuracy. The methods identify the two fully
evaluated program levels. Main error-conditioned results pool three demonstration sets;
Figure 2 and the separate name controls use the full-neutral analysis, now labeled.

Fixed the appendix's broken reference to the moved behavioral table. The former PDF
checker missed LaTeX's `??` placeholder; both papers' checkers now inspect the PDF and
compiler log. The new guard fails on the original broken code PDF and passes after repair.
Related work now distinguishes general conflict tasks from language-model lexical-response
studies, checked against the locally archived primary papers. Figure and table descriptions
identify their outcomes, denominators and paired-change direction.

The readability pass explains the task, meaning check, error measure and name-identity
control in direct language. Both body and Limitations fit on four pages. Data self-check:
zero failures (49 historical warnings). Strict submission build passes. Audit artifacts:
`log/accuracy_readability_2026-10-08/`.

Prompt-position comparison: Llama-3.2-3B completed all three demonstration sets in job
449113 (exit 0). Job 449114 remains queued and release 449115 waits for it. No validated
comparison is available or included in the paper.


### 2026-10-08 — Figures that explain the paper

Rebuilt the main figures around the task, comparison and finding, with plain-language
labels and the necessary definitions inside the image. The code paper shows the actual
length-versus-sum program and complete generated assignment values, then separates
original-name error readouts from the independent screened-name format replication.
The arithmetic paper shows the unchanged equations, compares requested response formats,
and summarizes the broad name-error result separately from its two-operation plot.
Its second figure shows all generated-calculation readout checks in the two tested models.
Detailed layer curves and patching controls remain in the appendices; arithmetic full-size
captions now explain how to read each plot type. Numerical summaries and abstracts are
unchanged. Companion figure JSON files record the displayed data. Four-page text through
Limitations and strict submission checks were verified; artifacts:
`log/figure_understandability_2026-10-08/`.


### 2026-10-08 — Prompt-position comparison released

Both GPU allocations and the dependent release job completed with exit 0. The validated
summary `round7_prompt_comparison.json` contains all three models and nine demonstration
runs. Before committing, checked the reference hash, observation identities, all stratum
counts and the unchanged pre-write estimates against the earlier validated release.
The result summary is available; manuscript integration and its strict build remain pending.
