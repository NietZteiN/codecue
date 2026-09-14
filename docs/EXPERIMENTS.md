# Experiment ledger

Status legend: planned · blocked · running · done. Numbers go in results/NOTES.md, never here.

| id | what | needs | status |
|---|---|---|---|
| E0 | Generator, executor, lure table, rule tests R1–R4; 20 hand-checked instances | — | **generator + tests done 2026-09-14**; hand check pending |
| E1 | Tokenizer/layout check per model: span positions resolve; ≤1% layout exclusions; single-token-ness of table names recorded (not required) | dev job | planned |
| E2 | Pilot: 200 sets × conditions × 4 regimes on codellama-7b-it and llama31-8b-it; go/no-go on accuracy range and on prose `value_written` variance | 1 GPU-h | planned |
| E2b | Lure-table validation gate: ask each model what `<name>` most likely holds | 1 GPU-h | planned |
| E3 | Behaviour, full panel, L1–L5, all conditions, 4 regimes, 3 demo seeds / 3 prose variants | ~40 GPU-h | planned |
| E4 | Prose annotation (`value_written`) and the P3 logit | CPU | planned |
| E5 | Caches + probes, 3 internals models, direct/trace/prose | ~30 GPU-h, ~1 TB | planned |
| E6 | Patching removal/injection + controls, 3 models | ~10 GPU-h | planned |
| E7 | Code generation task, 300 sets, instruct models | ~10 GPU-h | planned (generator not written) |
| E8 | Natural code: CRUXEval with one identifier renamed, 3 regimes | ~15 GPU-h | planned (renamer not written) |
| E9 | Equivalence bounds, seed sweep, self-check | CPU | planned |
| E10 | Randomised value-forcing clause in the prose instruction | ~10 GPU-h | planned |
