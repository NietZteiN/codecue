# Semantic and software validation

Initial snapshot: October 24, 2026, before model inference. Continuation evidence is listed below and in the generated [pilot report](pilot_report.md).

| Check | Smoke | Pilot |
|---|---:|---:|
| Generated bases | 120 | 600 |
| Primary renderings | 720 | 3,600 |
| Total renderings including two control kinds | 2,160 | 10,800 |
| Primary structural templates | 120 | 120 |
| Independent parent-template clusters | 60 | 60 |
| Unique ordinary-Python programs compared | 5,230 | 26,310 |
| Diagnostic counterfactuals checked | 3,320 | 16,600 |
| Counterfactual alternatives with diagnostic collisions | 1,406 | 6,773 |
| Functionally ineffective substitutions | 140 | 655 |
| Rejected generation proposals | 430 / 550 | 2,467 / 3,067 |

Both validators passed. Each independent Python comparison checks final output and every assignment's state against the restricted AST interpreter. Counterfactual substitutions are independently rendered as executable restricted assignments and their full downstream states checked. Renaming is invertible at the AST level and preserves semantics. Computed swaps preserve the final value multiset and exchange ownership. All live assignment values stay bounded; version uses, direct dependencies and liveness are validated. Syntactic dependence can survive an intervention with no functional effect, as the explicit `x - x` test demonstrates.

No grouped leakage was found by base, primary template, parent cluster, numeric relatives, actual control skeleton or paired/counterfactual group. Identifier strings are disjoint across splits; subwords/roots intentionally overlap. There are 1,800 canonical numeric programs, each with six renderings, and zero canonical ASTs repeated across different base IDs. The pilot has 6,480 training / 2,160 development / 2,160 test rows, with all relatives grouped. Final model outcomes remain unobserved.

The pinned-tokenizer audit covers all 3,600 primary renderings. Both informative-minus-neutral and misleading-minus-neutral have exactly zero prompt-token-count difference in all 1,200 paired comparisons. Candidate identifiers were screened at definitions, operand uses and query contexts, including all split prefixes. Character lengths and lexical meanings still differ; token equality does not eliminate those intended lexical differences.

The complete repository test suite passes: **80 passed in 44.38 seconds**. Tests cover versioned reads, future-assignment leakage, functional counterfactuals, restricted-language rejection, structural/numeric grouping, independent execution, renaming, whole-state masks, numeric parsing, ambiguous diagnoses, frozen-registration changes, probability calibration boundaries, clustered naming interactions and shared GPU reservations.

CPU SLURM job **475158** passed tokenizer/span alignment, exact self-patch equality, hook cleanup, cached-generation safety, complete multi-token candidate scoring, ridge recovery on known synthetic linear data, and temporary end-to-end behavior/extraction/probe/intervention workflows. The latter uses a two-block, 16-hidden-width random Llama network, with fixtures removed afterward. It is **software validation, not a CodeLlama experiment**. The workflow caught and corrected integer-label handling in randomized probe controls. Job **475159** completed the final input/tokenizer audit. SLURM records elapsed 1:51 and 1:23 respectively, each with four allocated CPUs.

Current evidence files:

- `artifacts/binding/smoke_matched.manifest.json` and `.validation.json`
- `artifacts/binding/pilot_matched.manifest.json`, `.validation.json`, `.design_audit.json`, and `.dedup.json`
- `artifacts/binding/smoke_matched.preflight.json` (explicit software-test flag)
- `artifacts/binding/implementation_manifest.json` and `model_manifest.json`
- `artifacts/binding/tests_final.log`
- `log/slurm/475158_binding_workflow_matched.out` and `475159_binding_audit_matched.out`

These initial checks establish software and semantic validity. Actual model evidence is separate.

## October 25 continuation

The expanded generator supports six slots, deeper updates and explicit distance padding in algorithm version 6. Four full reserved cohorts and four smaller structural smoke fixtures pass independent ordinary-Python checks of rendered traces and downstream counterfactual states. Actual primary and control skeletons are disjoint from the main pilot. Each cohort is test-only and the behavior selector refuses it without a frozen registration or explicit discovery relabelling. Model outcomes remain sealed. The full cohort counts and checks are generated from manifests in [pilot_report.md](pilot_report.md).

Version 5 was regenerated to a temporary directory after generalizing the generator and matched the original smoke SHA-256 byte-for-byte. Evidence: `artifacts/binding/version5_regression.json`. Original datasets were not overwritten. Structural smoke and full extrapolation cohorts share templates within their axis; they cannot be treated as independent discovery and confirmation cohorts.

Additional software checks cover immutable-source tampering, snapshot config changes, six-slot semantic renaming and ownership swaps, longer updates and identity padding, late quantity queries preserving assignment prefixes, computed donors checked against ordinary Python, and corrected masked-output ridge intercepts. Reanalysis requires an explicitly pinned upstream cache source and unchanged extraction configuration. Surface baselines use the same visible source prefix as each hidden checkpoint.

The latest complete test result is retained in `artifacts/binding/tests_phase2.log`; phase-one counts above are historical. Empirical CPU run 475207 is distinct from all random-network software workflows. Its full raw responses, exact identities and generated descriptive statistics are retained under `artifacts/binding/cpu_smoke_bf16_prefill_v2/behavior/`. Run 475196 used the earlier output protocol and was interrupted for parsing redesign; its invalid responses are preserved separately. The handoff records current activation, probe, assay, tokenizer-audit and GPU job status.
