# Operating rules — `codecue/`

*2026-09-14.* Cue conflict in code: does a misleading identifier survive the chain? Science in
`PLAN.md`, fixed claims in `PREREGISTRATION.md`, ledger in `docs/EXPERIMENTS.md`. Inherits the
cluster rules of `../probing/CLAUDE.md` (login node 8 GB cap; sbatch only; `salloc`+`srun`
does not work; h200/normal are one 4-job budget shared by four projects; env
`envs/probe-cu129`; never source obtune's setup_env.sh). Work does not start before the
arithmetic paper is submitted (2026-10-12).

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
