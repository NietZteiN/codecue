# Arithmetic composition and readout feasibility

Registered before collecting responses on 2026-10-26. This follows the explicit next step in the [computed-retention decision](live_load_decision.md). The earlier fixed gates, model responses and interpretations remain historical evidence. This experiment collects only fresh calibration and numeric-development outcomes; the original final and structural-extrapolation outcomes stay sealed.

## Question and design

Can the two existing instruction checkpoints evaluate three subtractions, and how does performance change when the same answer is exposed through literal, stored-input or stored-intermediate forms? The existing two-operation capacity study and the corrected backend replays already cover generic protocol/backend comparisons. This bank adds matched arithmetic composition and readout contrasts.

Draw distinct positive operands `a,b,c,d` from 1 through 17. Define `r=a-b`, `s=c-d`, and `y=r-s`; exclude zero intermediates and zero answers. Hash-based selection uses a fixed seed and excludes the numeric states used in the previous computed-retention bank. Select one original operand tuple for each distinct folded `(r,s)` pair. Keep its sign-reversed relative `(b,a,d,c)` in the same split and resampling group. The expanded operand range permits distinct folded inputs in every signed cell; it is an explicit change from the earlier single-digit bank.

The six feasible sign combinations of `(r,s,y)` each contain 64 tuples, split equally between training calibration and numeric development. All eight forms of a tuple have the same independently verified integer answer:

| Form | Binary subtractions | Readout |
|---|---:|---|
| Literal output | 0 | Print the oracle answer literal. |
| Stored output | 0 | Assign that literal and print its variable. |
| Literal one-operation | 1 | Print the folded literal expression `r-s`. |
| Bound one-operation | 1 | Assign the folded literal operands, then subtract their variables. |
| Stored-result one-operation | 1 | Assign the folded subtraction result, then print its variable. |
| Literal three-operation | 3 | Print `(a-b)-(c-d)`. |
| Bound three-operation | 3 | Assign the original four operands, then evaluate the expression. |
| Stored-intermediate three-operation | 3 | Compute the two intermediate values, then subtract their variables. |

There are 384 numeric tuples and 3,072 source records. Nonzero-operation forms have distinct inputs across numeric splits. Zero-operation controls necessarily repeat answers/prompts; their repetition and overlap are reported, and they do not count as independent generalization or qualification evidence. Numeric development shares the same task structures as calibration and is not a structural holdout.

Run both existing protocols, `print_direct_v3` (16 completion tokens) and `print_trace_long_v1` (512), separately on the pinned Llama 3.1 8B Instruct and CodeLlama 34B Instruct checkpoints. This yields 6,144 responses per checkpoint and 12,288 total. Reasoning traces change computation and remain separately labeled; they cannot retroactively rescue the prior direct-answer gate. Retain all raw responses, invalids, exact prompt/output token IDs, model revisions and runtime identities.

## Analysis and decision rules

Report every form × protocol × split × sign-stratum cell, including invalid outputs, unique source counts and token lengths. Use the existing strict integer/final-answer parsing contracts. Independent Python execution checks all sources before inference; the post-run audit replays identities and scores without querying models.

Each protocol is assessed independently. Every nonzero-operation form/sign-stratum must have at least 24 distinct source examples, at least 90% accuracy and at most 5% invalid answers in training calibration, followed by the same requirements on numeric development. There is no favorable-cell selection, validation fallback or automatic intervention expansion. Zero-operation controls remain descriptive checks.

Predeclared paired accuracy contrasts are three-operation literal minus one-operation literal; bound one-operation minus literal one-operation; stored-intermediate three-operation minus literal three-operation; bound three-operation minus literal three-operation; stored-result one-operation minus literal one-operation; and stored zero-operation minus literal zero-operation. Group every form and sign-reversed relative together in the numeric-pair bootstrap (2,000 draws, fixed seed). Intervals are exploratory and unadjusted for multiplicity.

These contrasts change literal exposure, computation placement and input length. They diagnose feasibility and do not isolate binding capacity, establish a causal mechanism, or satisfy frozen failure prediction. Even successful calibration would require a separately specified computed discovery design. No checkpoint training, download campaign, or optional extension is launched.

## Execution and logging

The generator, configuration and source are frozen before tokenizer preparation and inference. Existing continuously batched BF16 execution reuses one engine per checkpoint for both complete protocols, with hardware-adaptive batching and uncapped usage accounting. Tokenizer/model loads use SLURM; suitable GPUs run the two checkpoints independently. The ordinary registry, result writer and SLURM lifecycle hooks update the [automatic experiment log](experiment_log.md).

Entry point: `scripts/119_binding_arithmetic_readout.py` with `build`, `preflight`, `run`, `audit`, `review` and `compare`. Exact dataset/configuration/source hashes and job IDs will be retained under `artifacts/binding/arithmetic_readout/` before model responses are collected.
