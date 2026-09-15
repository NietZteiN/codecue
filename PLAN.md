# Does a Misleading Identifier Survive the Chain? Cue conflict in code

*Plan v0.1, 2026-09-14. Follow-up to the arithmetic cue-conflict paper in `../probing/`
(ARR October 2026). Separate paper; target ARR December 2026 or February 2027, decide by
2026-11-01. Nothing here starts before the arithmetic paper is submitted on 2026-10-12.*

## 1. The question, and where it comes from

The arithmetic paper finds that a chain of thought removes the effect of a misleading
variable name completely, and shows *why*: the chain writes every intermediate value, and
a written value replaces the name's lexical prior in the residual stream. Without a chain
the model reads the value off the name. The one model that fails to compute the value
(OLMo-2-1B) is the one model whose chain does not protect it.

Code is where this matters and where the mechanism predicts something different.
A program's "chain" is the code itself, and code writes *expressions*, never *values*.
A model that reasons about `count = sum(xs)` never writes "count is 17", so nothing ever
overwrites what the name `count` says. Le, Nguyen and Nguyen (2026) found that misleading
identifiers hurt the strongest code models most (DS-R1-Qwen-7B 64 → 52 points), and that
step-by-step reasoning did not rescue them. That is the behaviour the mechanism predicts,
but it has never been tested as a mechanism.

**Question.** Does a misleading identifier stop influencing a model's answer at the moment
the model writes the variable's concrete value, and not before?

**The one-line claim if the predictions hold.** The chain protects arithmetic and fails
code for the same reason: protection comes from writing the value, and code reasoning does
not write values unless it is made to.

## 1b. What the arithmetic paper found after this plan was written (2026-09-15)

Three results from `../probing` change the predictions below and are folded in:

1. **Writing the value as text does not protect.** Splitting arithmetic instances by whether
   the chain stated the value, against the matched neutral twin under the same split, gives a
   lure excess of +0.1 in both halves. The 20× raw gap was the chance baseline of a broken
   chain. So **P3 as originally worded is refuted in advance** and is reformulated: the
   per-instance split stays as a *control that must come out null after baseline correction*.
2. **What lines up with protection is whether the value is linearly *represented* at the step
   that writes it.** 7 of 8 (model, target) cells with probes are decodable there and null;
   the one that is not (OLMo-2-1B, intermediate, accuracy .22) is the one lured (+3.3), and
   injection moves its answer through a correct chain at layer 5. P3/P5 are therefore
   stated over probe decodability, not over the written token.
3. **A digit inside an identifier (`q4`) is never answered as the value, while a number word
   is.** The lure must be a *word with a meaning*, which the lure table already is
   (`count`, `total`, ...), and the identifier-digit family is dead.

Also: a number word on an *unused* variable is answered ~2 points above chance without a
chain, so P1's pseudo-lure baseline must be the matched twin, and "irrelevant" identifiers are
expected to show a small effect too.

## 2. Predictions, fixed before any data exist

δ = 2 points, TOST, as in paper 1. "Lure" = the answer the misleading name implies.

| | prediction | what it would mean if false |
|---|---|---|
| **P1** direct answering | lure rate above pseudo-lure; congruent name helps | code models do not read values off names; Le et al.'s effect is something else |
| **P2** trace chain (writes values) | lure excess within δ, as in arithmetic | writing the value is not what protects |
| **P3** prose chain ("think step by step") | lure persists relative to the trace regime. Within prose chains, splitting by whether the value was *written* shows **no** excess after the matched-twin baseline (the arithmetic null, expected to replicate); splitting by whether the value is *decodable* at the use site (probes, P5) does | if the written-token split shows an excess after baseline correction, code differs from arithmetic and the mechanism section is rewritten |
| **P4** code generation | lure persists with prose reasoning; removed by trace reasoning | same as P3, in the generation setting |
| **P5** probes | direct: lure decodable at the name and at its use site through the answer. Trace: erased after the value token. Prose: persists to the answer when the value was not written | the representational story from paper 1 does not transfer |
| **P6** weak models | models with low trace accuracy show the lure returning (the OLMo-2-1B pattern) | protection is a property of the format after all |
| **P7** natural code | accuracy drop on renamed CRUXEval is largest under direct, smaller under prose, smallest under trace | synthetic result does not reach real code |

P3 is the paper, in its revised form: the arithmetic paper showed that the written token is
not what protects; code is where the *represented* value and the *written* value come apart
most, because code reasoning names variables without stating their values.

## 3. Task

### 3.1 Output prediction (main task)

Given a Python function and an input, predict the return value. This is CRUXEval's task and
the task of Le et al., so results connect to both. It is the code analogue of "compute the
answer": a fixed, executable ground truth, and a *lure* that is also executable.

Running example, level 2 (two intermediate variables), incongruent on the queried variable:

```python
def f(xs):
    total = sum(xs)          # intermediate, neutral name
    count = total - min(xs)  # queried variable; name says "count", value is a difference
    return count
f([4, 1, 3])
```

True value 8 − 1 = 7. The lure is what the name asserts: `count` → `len(xs)` = 3.
Congruent twin: `count` renamed `diff`. Neutral twin: renamed `v`. Alternative-lure twin:
renamed `first` → lure `xs[0]` = 4. The twins are byte-identical up to the one identifier.

### 3.2 The lure is a program, not a word

Each misleading name comes from a fixed table of (name, implied operation) pairs. The lure
answer for an instance is computed by **executing the program with the implied operation
substituted** for the variable's real definition. This is rule 2 from paper 1 made
executable: the lure must differ from the true output on the chosen input (enforced by
running both), and must differ from every other intermediate value, so a lure answer can
only come from the name.

Initial table (extend after the pilot; keep every implied value in the answer range):

| name | implies | name | implies |
|---|---|---|---|
| `count`, `n`, `length` | `len(xs)` | `total`, `sum_`, `acc` | `sum(xs)` |
| `largest`, `max_val`, `peak` | `max(xs)` | `smallest`, `min_val`, `low` | `min(xs)` |
| `first`, `head` | `xs[0]` | `last`, `tail` | `xs[-1]` |
| `half` | `x // 2` | `double`, `twice` | `2 * x` |
| `neg` | `-x` | `succ`, `next_` | `x + 1` |

Inputs are short integer lists with distinct elements in 1–9; all values, intermediate and
final, are kept in 0–9 so the probe target is a 10-way classification as in paper 1.
Operations available to the generator: `sum`, `len`, `max`, `min`, indexing, `+ - *` with a
small constant, `// 2`. Levels = number of intermediate assignments (1, 2, 3), each level
with the misleading name on the queried or on an intermediate variable, plus a level with a
distractor variable that is never used (the irrelevant-lure control of paper 1).

### 3.3 Code generation (second task, P4)

Given a function prefix that defines a variable with a misleading name and a docstring that
states what the function must return, complete the function. Scored by hidden tests. The
lure is "use the variable as its name says": the tests are chosen so that the lure
completion fails a specific test and the correct completion passes. Smaller: 300 matched
sets, instruct models only. This is the setting of Le et al.'s tail result (21% accuracy
where displacement and surprisal are both high) and of the user's original motivation.

### 3.4 Natural code (P7)

CRUXEval (cached in `hf_home`) with **one** identifier renamed per function using the
obtune L1b tier machinery: neutral (`v1`), congruent (a synonym), misleading (a name from
the table whose implied operation type-checks in context), plus CRUXEval's own `x1, x2, …`
anonymisation of *every* identifier (their App. C.5 ablation, about −2 points for CodeLlama)
as the published reference point. No executable lure here; report
accuracy only, three regimes. This is the external-validity row, not the mechanism.

## 4. Regimes

| regime | prompt | writes values? |
|---|---|---|
| **direct** | return value only | no |
| **trace** | three fixed worked examples that trace execution line by line, `total = 8`, `count = 7`, then the answer | yes, by construction |
| **prose** | "Think step by step, then give the answer" with no worked examples; free text | sometimes — **measured per instance** |
| **code-chain** | model rewrites/annotates the program before answering (comments, no values) | no, by instruction |

The prose regime is scored twice: the answer, and whether the misleading variable's true
value appears as a written number anywhere before the answer (`count = 7`, `count is 7`,
`count: 7`, or the bare digit after the name within the same sentence). P3 compares lure
rate between prose chains with and without that value written, within model and condition,
with a clustered logit `lure ~ value_written × condition`. Demonstration sets: ≥3 seeds for
the trace regime (paper 1's lesson: the fixed examples are the largest single factor).

## 5. Validity rules (carried from paper 1, with two changes)

1. Exactly one misleading identifier per instance; twins differ in one identifier only.
2. Lure output ≠ true output ≠ any intermediate value, enforced by execution.
3. No identifier in the table appears anywhere else in the program (no `len` in a name
   when `len` is called).
4. **Positions are span-based, not absolute.** Code tokenizers split identifiers
   unpredictably and single-token names cannot be required across a code panel. Every
   position (name definition, end of defining statement, use site, pre-value token in the
   trace, answer) is located by character span → token span, last token of the span.
   `cueconf.prompts.layout` already does this for the arithmetic format; the runner's layout
   guard becomes a per-span check instead of a whole-prompt check.
5. **Probes are trained on neutral data only**, tested on every condition; selectivity
   control keyed on the identifier; ≥3 seeds.
6. Answer parsing takes the last `output:`/`return` value before a blank line, never the
   first line (the bug found 2026-09-14).
7. Instance ids carry the scheme and level; no number in the paper is hand-typed.
8. Wording: "misleading", never "adversarial"; interference and facilitation in the
   Stroop sense.

## 6. Models

All cached in `/scratch/juno/jvl210002/hf_home` (Qwen excluded by the project's scope rule;
DeepSeek-R1-Distill-Qwen therefore excluded too, which is the one gap relative to Le et al.).

| family | model | role |
|---|---|---|
| CodeLlama | 7B, 13B, 34B Instruct | code-tuned, three sizes for P6 |
| StarCoder2 | 15B Instruct | second code family |
| CodeGemma | 7B it | third code family |
| Llama-3 | 3.2-3B Inst., 3.1-8B Inst. | general models, link to paper 1 |
| Gemma-3 | 4B it, 12B it | general |
| OLMo-2 | 1B, 7B Instruct | the weak-model row (P6) |

Granite-3.1-8B and Phi-3.5-mini were unusable in paper 1 (chat-template and echo
problems); re-check under the code prompt before excluding. Internals (probes, patching)
on CodeLlama-7B, Llama-3.1-8B-Instruct and CodeGemma-7B; behaviour on the whole panel.

## 7. Internals

Same recipe as paper 1: neutral-trained linear probes per (position, layer, seed) for the
queried and intermediate values; lure mass and margin at the use site and at the answer;
per-token probe curves over the whole trace with the running example's real tokens on the
axis (the figure the user asked for in paper 1). Patching: neutral → misleading at the
identifier's tokens (removal), misleading → neutral (injection), with the word-control and
alternative-lure controls, span × layer-window grid. New: for prose chains, the per-token
probe curve split by whether the value was written, which is P5's picture.

## 8. Experiments

| id | what | size | needed for |
|---|---|---|---|
| E0 | Generator + executor + lure table; rule tests; 20 hand-checked instances | CPU | everything |
| E1 | Tokenizer/layout check per model: span positions resolve, ≤1% layout exclusions | dev | rule 4 |
| E2 | Pilot: 200 sets × 4 conditions × 4 regimes on CodeLlama-7B and Llama-3.1-8B-It | 1 GPU-h | go/no-go on the task (direct accuracy must be off floor and off ceiling) |
| E3 | Behaviour, full panel, levels 1–3, all conditions, 4 regimes, 3 demo seeds | ~40 GPU-h | P1, P2, P3, P6 |
| E4 | Prose-chain annotation: value written or not, per instance; P3 logit | CPU | P3 |
| E5 | Caches + probes, three models, direct/trace/prose | ~30 GPU-h, ~1 TB | P5 |
| E6 | Patching removal/injection + controls, three models | ~10 GPU-h | P5 |
| E7 | Code generation, 300 sets, instruct models | ~10 GPU-h | P4 |
| E8 | Natural code: CRUXEval renamed, three regimes, full panel | ~15 GPU-h | P7 |
| E9 | Equivalence bounds on every chain cell; seed sweep; self-check | CPU | claim rule |
| E10 | Free-form value-forcing: prose regime with the single instruction "state each variable's value" — the minimal intervention that should close the gap | ~10 GPU-h | the applied message |

Expected difficulty (from the literature, see RELATED_WORK.md): REval reports CodeLlama-7B-Instruct
at 25% on statement-level *variable value* prediction against 63% on output prediction, and
a chain of thought that *lowers* output accuracy by 7 points. So the trace regime is not a
free lunch for code models; E2 measures where each model sits before the design is frozen.

Go/no-go after E2: if direct accuracy on CodeLlama-7B is above 90% at level 3 the task is
too easy and levels go to 4–5; if below 20% the value range or list length shrinks. If the
lure rate under direct is not above pseudo-lure at all on any model (P1 false), the paper
becomes a null result about code models and the plan is revised before E3.

## 9. What is reused from `probing/`

`src/cueconf` generator scaffolding (matched sets, twins, rules as tests), runner (caching,
layout guard, behaviour rows now store the queried role), `BatchedProbes`, patching and
`patch_summary`, `stats.bootstrap_ci`, `56_seed_sweep`, `57_equivalence`, `99_selfcheck`,
the worker queue and `submit.py`, `display.py` conventions, and the paper's Kudo-style
figure scripts. New code: the Python program generator and executor, the lure table, the
span-based layout, the prose-chain value annotator, the test harness for generation, the
CRUXEval renamer (from obtune's tier code).

## 10. Storage and compute

Code instances are 150–300 tokens against 50 for arithmetic, so all-token caches are 3–6×
larger per instance (≈10 MB). Budget: 1,000 test instances per group, layer stride 2,
labelled positions only for the full panel, all tokens only for the three internals models.
Keep under 1.5 TB on scratch at any time; delete alt-condition caches once summaries exist.
Two h200 workers as now; behaviour for the panel fits in a weekend.

## 11. Timeline

| when | what |
|---|---|
| 2026-10-12 | arithmetic paper submitted; this project starts |
| 2026-10-19 | E0–E2 done; go/no-go on the task |
| 2026-11-01 | E3, E4 done → P1–P3, P6 known; decide ARR cycle |
| 2026-11-15 | E5–E7 done |
| 2026-11-29 | E8–E10 done; draft |
| 2026-12-15 or 2027-02-15 | submit |

## 12. Risks

- **The lure table is the paper's weak point.** A reviewer will ask whether `count` really
  "implies" `len`. Answer with data: on the neutral twin, ask the model directly what a
  variable named `count` most likely holds, and keep only names where ≥80% of the panel
  agrees with the table. Report that check as a table.
- **Prose chains may almost always or almost never write values**, leaving P3 without
  variance. The pilot measures this; if needed, vary the instruction to move the rate to
  the middle, and E10 is the deliberate manipulation.
- **Code models are strongest exactly where the effect is predicted to vanish.** If every
  code model traces perfectly and the general models do not, model and regime are confounded.
  The level manipulation (harder programs) keeps every model off ceiling.
- **The arithmetic mechanism may not be right.** The weak-model test in paper 1 (running
  this week) is the check; if it fails there, P2 and P3 are rewritten before E3.

## 13. Related work to add beyond paper 1's list

Le, Nguyen, Nguyen (2026) as the starting point; CRUXEval (Gu et al. 2024); Orvalho and
Kwiatkowska (2025) on renaming raising accuracy; Gao et al. (ICSE 2023) on direct vs
indirect identifier effects; Miceli-Barone et al. on identifier surprisal; the
CoT-faithfulness line (Turpin et al. 2023; Lanham et al. 2023) for the "value written"
analysis; Kudo et al. (2026) for the probe recipe.
