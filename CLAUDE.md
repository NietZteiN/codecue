# Operating rules — `codecue/`

*2026-09-14.* Cue conflict in code: does a misleading identifier survive the chain? Science in
`PLAN.md`, fixed claims in `PREREGISTRATION.md`, ledger in `docs/EXPERIMENTS.md`. Inherits the
cluster rules of `../probing/CLAUDE.md` (login node 8 GB cap; sbatch only; `salloc`+`srun`
does not work; h200/normal are one 4-job budget shared by four projects; env
`envs/probe-cu129`; never source obtune's setup_env.sh). Work does not start before the
arithmetic paper is submitted (2026-10-12).

## Active resource instruction (2026-10-25)

The user explicitly states that this is the only active project and asks to maximize
useful compute for it. This supersedes the initial four-GPU-hour/single-checkpoint
operating defaults and the assumption that capacity must be saved for other projects.
New model work uses `artifacts/binding/gpu_usage_uncapped.json` (no cumulative cap,
multiple cached checkpoints), with authorization in
`artifacts/binding/resource_policy_20261025.json`. Preserve historical ledgers and frozen
run identities; do not reset usage or rerun completed scientific experiments.

Use independent available GPUs and eligible CPU partitions for useful queued work.
Actual scheduler limits still apply: observed partition QoS `juno` permits four active
jobs per user, including normal CPU, A30 and H200 jobs; `juno-dev` permits one. These
observed limits supersede the older inherited comments about A30. CPU preparation may
use `dev,normal` so the dev limit does not serialize independent tokenizer checks.
The current runner ignores legacy `max_gpu_seconds`, cumulative budgets and profiler
timeouts. Its ledger is accounting-only, with no checkpoint restriction or time
reservation. Submission defaults use the cluster's actual 48-hour GPU maximum;
`--gpus` and model tensor parallelism are configurable. Finite jobs exit on completion.
Use `--time-min` for profiled resumable workloads when shorter scheduler backfill
windows can start them sooner; this changes the allocation SLURM may grant, not a
project compute allowance. The submission manifest records both requested bounds.
Historical frozen code/configurations retain their original identity for reproducibility.
Inference jobs retain scheduler-enforced walltimes and resumable outputs. Scientific gates,
sealed final outcomes and the prohibition on automatic optional training still apply.

The `dev-a30` partition is also eligible for short workloads that fit a 24-GiB A30.
Its observed scheduler maximum is two hours and its partition QoS is `juno-dev-a30`;
it allows this account. The combined `dev-a30,a30,h100,h200` submission profile uses
that actual two-hour maximum and a five-minute backfill minimum, without an application
compute cap. For the batch-144 reset-reference assay, the scheduler request was expanded
in place after a measured batch-96 peak fit comfortably; details are preserved in
`artifacts/binding/routing_extension/swap_backfill_eligibility_v2.json`.

## Rules that make a result mean something

1. Exactly one table identifier per instance; twins differ in one identifier (R1). Tested.
2. The lure is executable and never written anywhere in the prompt: not a variable value,
   not an input element, not a constant (R2). Tested.
3. Positions are character spans → token spans (last token). No single-token requirement.
4. Probes train on neutral data only; ≥3 seeds; selectivity control keyed on the identifier.
5. Parse the LAST `Answer:` before a blank line, never the first line.
6. Instance ids carry level, seed and target; datasets carry a content hash the runner checks.
7. ≥3 demonstration seeds (trace/direct) and ≥3 instruction variants (prose) per claim.
8. No number in the paper is hand-typed; the lure-table gate (PREREGISTRATION.md) is applied
   before any claim.
9. Wording: "misleading", never "adversarial"; interference/facilitation in the Stroop sense.
10. Never bulk-delete on scratch without a dry run and approval; caches are hours of GPU time.
