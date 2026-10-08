# Prompt-end versus pre-write comparison

Fixed on 2026-10-08 before extracting states or fitting the new probes. This follow-up
tests whether correct digits are already linearly readable from the full prompt, before
any trace is generated. It does not test whether the model uses a probe-readable digit.

Use OLMo-2-7B, Llama-3.2-3B and Llama-3.1-8B, demonstration sets 7, 11 and 13, and exactly
the training/evaluation computations and observed writes in the validated round-six
release. Retain 2,000 neutral training rows, three probe seeds, the unstandardized SGD
recipe (learning rate 0.001; 10,000 epochs), and the original cached layer grid.

The new position is the last token of the entire prompt ending in `Trace:`, before any
generated identifier or value. Verify that its token prefix is unchanged when the
original trace is appended. Keep new caches and fits separate from the original artifacts.

Select each position's layer independently using the same five canonical-computation
folds: each held-out fold's selector sees only other folds' neutral labels. Average three
probe seeds. Compare positions on identical actual wrong writes, using the existing
generated-prefix audit and frozen outcome strata. Report paired accuracy differences and
95% intervals from 4,000 canonical-computation bootstrap draws, retaining demonstration
repeats together. Intervals condition on fixed fold selectors. Report neutral, correct-write
and other-error strata, coverage, selected layers, and prompt-position name-identity controls.

If prompt-end accuracy is already high, report that correct-value information is available
before the trace. If it is lower, report the measured change at the writing position.
Neither outcome identifies a causal feature or establishes use of that information.

Execution: `scripts/81_prompt_end_probe.py` extracts/fits; `scripts/82_prompt_comparison.py`
validates and releases the paired summary. GPU partitions are currently occupied; request
two batch allocations on a30 and h100, keeping h200's shared account pool free.

Submitted GPU jobs: 449113 (Llama-3.2-3B, a30, 8-hour limit) and 449114
(OLMo-2-7B followed by Llama-3.1-8B, h100, 12-hour limit). Llama-3.2-3B started on g-02-01 at
2026-10-08 21:11 UTC and completed at 21:30 UTC (exit 0); the second allocation is queued. CPU release job 449115 depends on both succeeding. Request
metadata are recorded in `docs/PROMPT_COMPARISON_STATUS.json`; job outputs go to
`log/slurm/<job-id>_<name>.out`.

After the release validates, run `make evidence` to add both positions to the main
evidence table and the paired differences and controls to the appendix. Then run
`make paper-submission`, inspect the PDF and interpret the measured differences
before committing the results. Pending experiments contribute no numbers to the paper.

The dependent-assignment extension discussed in the review is a subsequent study, rather
than part of this fixed comparison; no new model sweep is included.
