# One paper, not two: a narrative for the merged cue-conflict study

*Drafted 2026-09-18. **Superseded 2026-09-19: the experiment this plan required was run and it
refutes the plan.** Kept as the record of what was tried and why it failed.*

> **Outcome.** E31, the arithmetic value-only chain, was run on eight models with three
> demonstration seeds (probing/results/NOTES.md, 2026-09-19). Both pre-registered predictions
> failed. Behaviourally the format does not reliably let the name in: Llama-3.1-8B is +0.15 on
> the intermediate, inside the equivalence margin, and Llama-3.2-3B's +9.2 is one demonstration
> seed out of three. Internally it fails in the wrong way: the true value is decodable at the
> step that writes it at 0.81/0.59 for the 8B and 0.58/0.38 for OLMo-2-1B, against 0.99–1.00
> under the full chain. Dropping the equations degrades the computation rather than leaving it
> intact and breaking the readout.
>
> The ladder below therefore does not hold, and its empty bottom-left quadrant is not the only
> empty one: arithmetic supplies no readout-failure point at all. The two tasks do not share a
> mechanism across the format ladder. **Recommendation: do not merge.** Submit the two short
> papers as they stand; neither depends on any number from E31.

## The thesis in one paragraph

A misleading variable name supplies a second value for a variable, in competition with the
value the computation produces. A chain of thought overrides the name only when two
conditions hold at the step that writes the variable: the computed value must be
**represented** there, and the written step must be **committed to the expression** that
produced it. The arithmetic study isolates the first condition: with a chain whose every step
restates the equation, the name loses in 33 of 34 cells, and the one exception is a model whose
value is not decodable at the writing step. The code study isolates the second: with a trace
that writes each value without its expression, the name wins at the list-aggregate step even
though the computed value is decodable there at 85–100%, and writing the expression back into
the trace removes it. Two tasks, one design, two failure modes: one of representation, one of
readout.

## Why the two studies are halves of one thing

The arithmetic chain format is `Y=7 - 6, Y=1, S=2 + 1, S=3`: expression, then value. In the
code study's terms, that is `trace_expr`. The code study's `trace` format (`v = 3`) has no
arithmetic counterpart in the data so far. Kudo et al.'s "Simple CoT" (`Y=1, S=3`, Table 6 of
their paper; row E31 in probing/docs/EXPERIMENTS.md, **not run**) is that counterpart.

So the two studies fill five of six cells of one ladder:

| format of the written step        | arithmetic                       | code                              |
|-----------------------------------|----------------------------------|-----------------------------------|
| no chain (answer only)            | name wins (+1 to +20)            | name wins (+1 to +7)              |
| value only (`Y=1` / `v = 3`)      | **not run** (E31)                | name wins at the aggregate (+12 to +58) |
| expression then value             | name loses (33/34); exception is a representation failure | name loses (`trace_expr`: 0–3) |

The paper is the ladder plus the two internals results that explain its two failing rows:

- **Representation failure** (arithmetic, OLMo-2-1B): the value is not decodable at the step
  that writes it (0.22), and injecting the name into a correct forced chain moves the answer.
  The name wins because nothing else is there.
- **Readout failure** (code, three models): the value is decodable at the decision token
  (0.85–1.00); the name's tokens are the causal origin at layer 0; the influence arrives at the
  decision token mid-network; a single-layer patch there removes it. The name wins although
  the value is there, because the format lets the output head skip the expression.

## The figure that makes it one paper

One scatter: x = probe accuracy for the true value at the step that writes it; y = lure
excess at that step. Every (task, model, format) cell is a point, shape by task, colour by
format. Three regions:

- bottom-right: computed and protected (arithmetic chains, code `trace_expr`);
- top-left: not computed and lured (arithmetic OLMo-2-1B);
- top-right: computed and lured (code `trace`; predicted: arithmetic simple chain).

The empty quadrant, bottom-left, is what the design cannot produce. If the arithmetic
simple-chain points land top-right, the figure is symmetric and the story is complete. If they
land bottom-right, the paper says the value-only format is dangerous in code and not in
arithmetic, and has to explain why; that is a weaker but still honest paper.

## What already refutes the easy version of the story

The arithmetic value-written control refuted "the chain protects by writing the value": lure
excess +0.11 when the chain wrote the value, +0.07 when it did not. This is not in tension
with the thesis; it sharpens it. Writing the *value* protects nothing. Writing the
*expression* before the value is what binds the output to the computation, and the arithmetic
chain always does that, so the control could not have found a difference. The merged paper
states this as the reason the code study was needed.

## Section plan (8 pages)

1. **Introduction.** The Stroop framing; one running example from each task side by side; the
   two conditions; the ladder table as Table 1.
2. **A single design.** Twins that differ in one identifier; executable lures; the
   pseudo-lure baseline from the matched twin; the demonstration-seed claim rule; the
   equivalence margin; probes trained on neutral data with the control task; patching with
   the neutral-for-neutral control. Written once. Everything borrowed from Kudo et al. named
   once, here.
3. **The arithmetic half: the first condition.** No chain, name wins; chain, name loses;
   the exception; the value-written control; the probe and injection evidence that the
   exception is a representation failure.
4. **The code half: the second condition.** Terse trace, name wins at the aggregate step;
   sum is not a default; `trace_expr` removes it; probes show the value present; two patching
   sites give the causal path.
5. **The bridge.** The ladder completed with the arithmetic simple chain; the scatter figure;
   the two failure modes stated as one rule. This section is the paper's reason to exist and
   must contain results from both tasks in every paragraph.
6. **Boundaries.** Format (REPL, comment), scale (34B), step type (level 6), natural code
   (CRUXEval null), identifier-style names, word class, irrelevant lures.
7. **Related work. Conclusion. Limitations.**

Test for "two papers stapled together": if a section could be deleted without changing the
claim of Section 5, it is appendix material. Sections 3 and 4 survive only because Section 5
needs a representation-failure point and a readout-failure point.

## The one experiment the merge needs

**Arithmetic simple chain** (probing E31): demonstrations write `Y=1, S=3`, the model does the
same. Behaviour on the eight-model panel at level 3 with three demonstration seeds (≈ 0.5
GPU-h per model, ≈ 4 GPU-h); probes at the value step for the three models with caches
(≈ 3 GPU-h); patching at the value step for one model (≈ 1.5 GPU-h). One GPU, about a day.
Pre-register two predictions before running: (i) written-lure excess at the value step above
the equivalence margin for at least the two Llama models; (ii) the value decodable at that
step at ≥ 0.85, so the failure is readout, not representation.

Optional second cell: a code model that fails the first condition. OLMo-2-1B at level 5 is at
38% neutral accuracy, too noisy; level 3 may serve. Not required for the story.

## Venue and timing

- The merged paper is a long paper. It cannot be under ARR review at the same time as the
  arithmetic short. Choosing the merge means **not** submitting the short on 2026-10-12, or
  withdrawing it before the merged submission.
- Realistic target: the ARR cycle after October (December). The new experiment is a day of
  GPU; the writing is two to three weeks because the Setup section must be rewritten once
  for both tasks and every appendix table regenerated under one numbering.
- Everything else already exists: two verified number generators, two self-checks, two
  figure pipelines. The merge is a writing job with one experiment in front of it.

## Risks

1. The arithmetic simple chain protects anyway. Then the bridge is asymmetric; the paper
   becomes "two conditions, one shown per task" without the completed ladder. Still one paper,
   less clean.
2. Reviewers read the code effect as narrow (one name family, one step, ≤ 8B). The merge
   helps here: the code half is no longer the whole claim, it is the readout-failure point.
3. Length pressure: two full appendices. Keep the arithmetic and code appendices as they are,
   under one numbering, and let the body carry only what Section 5 needs.
