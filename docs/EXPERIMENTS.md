# Experiment ledger

Status legend: planned · blocked · running · done. Numbers go in results/NOTES.md, never here.

| id | what | needs | status |
|---|---|---|---|
| E0 | Generator, executor, lure table, rule tests R1–R4; 20 hand-checked instances | — | **generator + tests done 2026-09-14**; hand check pending |
| E1 | Tokenizer/layout check per model: span positions resolve; ≤1% layout exclusions; single-token-ness of table names recorded (not required) | dev job | **done 2026-09-15**: 11/11 models, 0 unresolved |
| E2 | Pilot: 200 sets × conditions × 4 regimes on codellama-7b-it and llama31-8b-it; go/no-go on accuracy range and on prose `value_written` variance | 1 GPU-h | **done 2026-09-15** (results/NOTES.md); round 2 at level 5 + weak models queued |
| E2b | Lure-table validation gate: each model completes `def f(xs):\n    <name> = ` (`12_lure_gate.py`) | 1 GPU-h | queued 2026-09-15 |
| E3 | Behaviour, full panel, L3 (then L5), all conditions, direct+trace × 3 demo seeds + prose (codechain dropped) | ~20 GPU-h | L3 queued 2026-09-15 for 7 models |
| E4 | Prose annotation (`value_written`) and the P3 logit | CPU | planned |
| E5 | Caches + probes, 3 models, trace regime, the affected cell | ~3 GPU-h | **done 2026-09-16**: code value decodable 85–100% at the decision token, name value ≤2% at any layer, yet the sum is written 12–59% → readout failure |
| E6 | Patching from the twin at the name's last token and at the decision token, read at the decision token; main + word control + alt-lure control; 3 models, 300 pairs | ~2 GPU-h | queued 2026-09-16 (span-to-span: twins do not share layouts; `sum_all` is 2 tokens, patched at its last) |
| E7 | Code generation task, 300 sets, instruct models | ~10 GPU-h | planned (generator not written) |
| E8 | Natural code: CRUXEval with one identifier renamed, 3 regimes | ~15 GPU-h | planned (renamer not written) |
| E9 | Equivalence bounds, seed sweep, self-check | CPU | planned |
| E10 | Randomised value-forcing clause in the prose instruction | ~10 GPU-h | planned |

| E3b | Value-step lure rate in the trace (written value == lure vs the matched twin) | CPU | **done L3+L5, 3 seeds, 7 models (2026-09-15).** Effect is one cell: `len(xs)` named as a sum is traced as the sum (59% OLMo-2-7B, 44% Llama-3.2-3B at L5); all other pairings 0–2% |

| E3c | Validity pass (2026-09-15): `value_written` clause bug fixed and re-scored; hits verified by eye; demos leak-free; parser ≥99.7%; direct pseudo-lure explained (sum is the default wrong answer); `99_selfcheck.py` 0 failures | CPU | **done** |
