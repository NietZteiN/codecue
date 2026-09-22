# Experiment ledger

Status legend: planned · blocked · running · done · not run. Numbers go in results/NOTES.md, never here.

*Statuses reconciled against `results/NOTES.md`, `results/summary/`, `paper/numbers.tex` and the
run directories under `/scratch/juno/jvl210002/codecue` on **2026-09-17**. Every row below says
what has actually run as of that date; rows that never ran say so rather than "planned".*

| id | what | needs | status |
|---|---|---|---|
| E0 | Generator, executor, lure table, rule tests R1–R4; 20 hand-checked instances | — | **generator + tests done 2026-09-14.** The 20-instance sheet (`docs/HAND_CHECK.md`) is generated but **still unticked**; by-eye verification of the lure hits was instead done under E3c |
| E1 | Tokenizer/layout check per model: span positions resolve; ≤1% layout exclusions; single-token-ness of table names recorded (not required) | dev job | **done 2026-09-15**: 11/11 models, 0 unresolved (`results/summary/layout_check.json`) |
| E2 | Pilot: 200 sets × conditions × 4 regimes on codellama-7b-it and llama31-8b-it; go/no-go on accuracy range and on prose `value_written` variance | 1 GPU-h | **done 2026-09-15** (results/NOTES.md); round 2 at level 5 + weak models followed |
| E2b | Lure-table validation gate: each model completes `def f(xs):\n    <name> = ` (`12_lure_gate.py`) | 1 GPU-h | **done 2026-09-15** as **v2** (log-prob scoring; v1 free completion was broken — every model completes `count = ` with `0`). 12 of 25 names pass the 80% bar; sum-family names are read as `len` by 2 of 7 models, which is exactly where the effect is absent. `results/summary/lure_gate_v2.json` |
| E3 | Behaviour, full panel, L3 (then L5), all conditions, direct+trace × 3 demo seeds + prose (codechain dropped) | ~20 GPU-h | **done**: L3 2026-09-15 and L5 2026-09-16, 7 models × 3 demo seeds × {direct, trace, prose}. L5 later extended with repl/comment/trace_expr (R3a) and an 8th model (R3c). `results/summary/sweep_L3.json`, `sweep_L5.json` |
| E4 | Prose annotation (`value_written`) and the P3 logit | CPU | **done 2026-09-15**: prose `value_written` scored per role after the clause-regex fix; written-lure excess 0.0–0.7 for every model and target, so prose carries no contamination. The P3 within-model split (lure rate with vs without the value written) is therefore **vacuous** and was not reported — there is nothing to split on |
| E5 | Caches + probes, 3 models, trace regime, the affected cell | ~3 GPU-h | **done 2026-09-16**: code value decodable 85–100% at the decision token, name value ≤2% at any layer, yet the sum is written 12–59% → readout failure |
| E6 | Patching from the twin at the name's last token and at the decision token, read at the decision token; main + word control + alt-lure control; 3 models, 300 pairs | ~2 GPU-h | **decision-token site done 2026-09-16**: a single-position, single-layer patch from the twin removes 97–100% of lure writes at ~0% damage from L9–L15 on; name site **done**: replacing the name's tokens at L0 removes 97–100% at ≤2% damage, decaying to 0 by L16–18, the mirror of the decision-token curve. Alt-lure control is degenerate in this cell (every sum-family name implies the same value) and is not reported |
| E7 | Code generation task, 300 sets, instruct models | ~10 GPU-h | **not run** — the generator was never written; scope narrowed to output prediction, and no claim in the paper depends on it |
| E8 | Natural code: the 48 CRUXEval functions with `name = len(...)`, rendered original / neutral (`v`) / misleading (`total`), AST-renamed and execution-verified; direct + prose; 7 models | ~1 GPU-h | **done 2026-09-16: null.** Paired accuracy deltas within noise for all 7 models (n=43, CI ±12–16); reasoning writes the sum 0–6% under either name. The trace format where the effect lives has no natural-code analogue here. **Superseded by R3d**, which widened the subset to 89 functions and tightened the bound |
| E9 | Equivalence bounds, seed sweep, self-check | CPU | **done 2026-09-21.** Seed sweep and self-check as before; the equivalence bound is now a TOST rather than an eyeballed margin (`57_equivalence.py`, ported from probing): 192 cells at delta=2, 145 equivalent, 38 with an effect, 9 inconclusive and reported as such. `results/summary/equivalence.json`, paper Measures |
| E10 | Randomised value-forcing clause in the prose instruction | ~10 GPU-h | **done 2026-09-15 — null, and uninformative by construction.** Level 5, 500 sets, 3 models, 3 instructions (`plain`/`state`/`recompute`); written-lure 0.0–1.4% throughout, because prose has no contamination for an instruction to remove. The first run was also buggy (the selector dropped every misleading row; fixed and re-run). Recorded as a design error and **replaced by E10b** |
| E10b | Format manipulation: `trace` demos write `count = 3`, `trace_expr` demos write `count = len(xs) = 3`; same problems, seeds and models, level 5 (pre-registered before the runs) | ~4 GPU-h | **done 2026-09-16**: paired drops of +55.2 / +43.2 / +12.4 points (OLMo-2-7B, Llama-3.2-3B, Llama-3.1-8B), all sign-consistent across seeds with intervals excluding zero. Cell-specific: every other (operation, name) pairing is already 0.0–0.8% and stays there. This is the paper's causal format result |
| E3b | Value-step lure rate in the trace (written value == lure vs the matched twin) | CPU | **done L3+L5, 3 seeds, 7 models (2026-09-15).** Effect is one cell: `len(xs)` named as a sum is traced as the sum (59% OLMo-2-7B, 44% Llama-3.2-3B at L5); all other pairings 0–2% |
| E3c | Validity pass (2026-09-15): `value_written` clause bug fixed and re-scored; hits verified by eye; demos leak-free; parser ≥99.7%; direct pseudo-lure explained (sum is the default wrong answer); `99_selfcheck.py` 0 failures | CPU | **done** |
| R3a | Format manipulation: repl and comment regimes, 3 seeds, 3 models, L5 (PREREGISTRATION.md) | ~6 GPU-h | **done 2026-09-17: refuted for repl** (3–6× weaker than trace, not the predicted factor of two), comment ≈0 in 2/3 models (Llama-3.2-3B +6.8) |
| R3b | Level 6: unary middle step as target, 8 lure families, 7 models | ~8 GPU-h | **done 2026-09-17: null** (overall excess ≤0.6 in reliable models; `results/summary/sweep_L6.json`) |
| R3c | CodeLlama-34B, trace, L5, 3 seeds (h200) | ~6 GPU-h | **done 2026-09-17: refuted** — len→sum +0.0, max→sum +1.8 [+1.0, +2.8] (passes the claim rule but sits inside δ = 2), neutral acc 98.9% |
| R3d | CRUXEval widened to 89 functions (len/counter/max), direct + prose, 7 models | ~2 GPU-h | **done 2026-09-17: null**, every interval covers zero; bound ±10 (direct) / ±13 (prose) |

## Not run, and why

- **E7, code generation** — generator never written; the paper claims nothing about generation.
- **A formal TOST** for the equivalence bound (see E9); the δ = 2 margin is stated and applied
  by hand against bootstrap intervals instead.
- Models of Chinese origin (Qwen, DeepSeek-R1-Distill-Qwen) are out of scope by project rule,
  which is the one gap relative to Le, Nguyen and Nguyen (2026); stated in Limitations.
