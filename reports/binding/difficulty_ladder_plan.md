# Fixed training difficulty ladder

This is the single follow-up calibration proposed in the [decision memo](decision_memo.md), after the original task gate failed and the independent decoder reproduced its failures. The new question is whether a simpler assignment/dependency regime on this checkpoint supports reliable arithmetic and both successes and semantic errors. The original conditional calibration-bank decisions remain skipped. Final-test outcomes remain sealed.

The machine-readable plan is `configs/binding/difficulty_ladder_plan.json`. Its byte hash is pinned in `configs/binding/difficulty_ladder.json`, the generated dataset manifest, the immutable source snapshot and the eventual selection artifact. Plan, data, gate and query cap are saved before collecting these model outcomes.

## Dataset and contrasts

The dataset has 120 unique programs: twelve computed one-assignment baselines, and twelve programs in each of three styles at two, four and eight assignments. Every cell has four negative, four zero and four positive answers. Nonzero target magnitudes are two, five, eight and eleven. All programs are training calibration data. Ordinary Python independently verifies every complete state trace.

Each nonbaseline group contains three programs with exactly the same sequence of assignment-result values, answer, arithmetic operators and operation count:

- `reassigned_chain` repeatedly updates `v0`.
- `fresh_chain` carries the same computation through fresh variables.
- `independent_arithmetic` substitutes the preceding oracle value as a literal in each right-hand side, so assignments are independent.

The chains have dependency depth equal to assignment count. The independent control has depth one with the same assignment count. Its substituted literals and dead earlier computations change surface cues and functional dependencies; it is an arithmetic/calibration control, not a semantics-preserving rewrite or a clean isolation of memory load. Reassignment and fresh-variable programs also differ in identifier count and subwords. No misleading-name manipulation or binding-interference claim is made here.

There are 48 matched computation paths and twelve answer-target groups shared across depths. Numeric programs repeat structural templates. These counts do not imply 120 independent structural examples. Canonical ASTs are deduplicated within the ladder and against the eight fixed primitive fixtures and the earlier unqueried calibration bank. Structural overlap with prior tasks is expected and documented.

## Inference and fixed selection

Use the existing pinned CodeLlama checkpoint on GPU BF16 with greedy batch-four decoding. Both existing protocols run on every program: `print_direct_v3` with sixteen tokens and blank-line stopping, and `print_trace_long_v1` with 512 tokens and the explicit final-answer-line parser. No new prompt or parser is introduced. Precision differs from the earlier FP32 prompt calibration; those outcomes stay separate.

The cap is 240 model queries and 1,800 GPU stage seconds, within the existing shared four-hour cap. The SLURM allocation has a 35-minute wall limit to accommodate startup and the bounded stage. Partial output remains partial and cannot select a regime. All raw responses, token IDs, prompts, rendered source and generation settings are retained.

For each protocol and assignment count above one, a regime is eligible only if:

- The one-assignment computed baseline has at least ten of twelve correct.
- The independent-arithmetic cell at that count has at least ten of twelve correct.
- Each chain style has between six and eleven of twelve correct.
- Every output in those four cells parses as required.

Selection occurs only after all 240 planned responses exist. Prefer the direct protocol, then the smallest qualifying assignment count. All cells and both protocols are reported, including sign breakdowns and invalid outputs. This small training gate is a feasibility rule rather than a significance test, population interval or established mechanism.

If no regime qualifies, stop this checkpoint/protocol feasibility pilot. Do not launch another prompt search or automatically run the old conditional bank, interventions, another checkpoint or final-test inference. A qualifying regime permits only the design of a separately frozen discovery cohort; it does not transfer previous probes or establish a causal account.

## Reproduction

```bash
python -m codecue.binding build-difficulty-ladder --config configs/binding/difficulty_ladder.json
python scripts/slurm/submit.py --name binding_difficulty_ladder --partition a30 --time 00:35:00 --mem 64G -- python scripts/95_binding_difficulty_ladder.py configs/binding/difficulty_ladder.json
```

The scheduled experiment uses the verified immutable launcher rather than the live source shown for readability. Source pointers and job IDs are recorded in `artifacts/binding/difficulty_ladder_jobs.json`; inspect them before submitting anything. Dataset and decision outputs refuse overwrites. Software tests use temporary fake responses and never enter the empirical report.
