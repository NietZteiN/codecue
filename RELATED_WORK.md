# Related work for the code cue-conflict plan, and what is left to claim

*Written 2026-09-14 from the 44 PDFs in [`papers/`](papers/) (indexed with page-cited notes in
[`papers/REFERENCES.md`](papers/REFERENCES.md)). Page numbers refer to the PDF on disk; "(p. N)" is
a claim read from the text of that page. Entries carried over from the arithmetic paper keep the
cites verified there (`../probing/RELATED_WORK.md`, 2026-09-12). Each paragraph ends with the
prediction in `PLAN.md` §2 that it bears on.*

**Short answer to "has this been done?": no.** Three lines come close and must be cited early.
(i) Le, Nguyen and Nguyen (2026) and CodeCrash (2025) show that misleading names and misleading
comments hurt code models and that a chain of thought reduces but does not remove the damage;
neither separates chains that write a variable's value from chains that do not, and neither looks
inside the model. (ii) REval (2024) and CoRE (2026) show that models often get the output right
while getting *intermediate variable values* wrong, which is the behavioural shadow of our claim
that code reasoning does not write values. (iii) Chen et al. (2026, "Brewing") run layer-wise
linear probes on synthetic single-digit code-execution tasks with randomised identifiers, the
closest methodological neighbour, but their identifiers are random by design, so no name ever
competes with a value. Nobody has put a name that *implies a wrong value* into a program and asked,
per instance, whether the model wrote the true value before answering.

---

## 1. Identifier names and code comprehension in LLMs

**The starting point.** Le, Nguyen and Nguyen (2026; `papers/obf2026humans.pdf`, cite in the
third person) measure output prediction on 0.5–8B models across obfuscation tiers. Misleading
renaming (their L1b) hurts the strongest models more than uninformative renaming: DS-R1-Qwen-7B
63.8 → 64.2 → 51.8 for L0 → L1 → L1b and SmolLM3-3B 45.0 → 44.0 → 34.2 (Table II, p. 4), while
human experts *improve* at L1b (pp. 4–5, 7). The "21% / 10%" figures in `PLAN.md` §3.3 are the
n = 80 tail where top-20% semantic displacement and top-20% identifier surprisal co-occur (Table X,
p. 9), not L1b overall. Many identifiers change at once, there is no congruent condition, and
"step-by-step" is a model property (DS-R1 distillation), not a manipulated regime. *For us:* P1 is
their effect restated with one identifier and an executable lure; P3 is what their design cannot ask.

**Renaming can help.** Orvalho and Kwiatkowska (2025) find that renaming to random identifiers
*raises* accuracy for most open models (Qwen2.5-Coder 62.6 → 76.6, Table 2, p. 8) and that 10–55% of
correct answers rest on flawed reasoning (Table 1, p. 7). CRUXEval's own ablation (Gu et al. 2024,
App. C.5, pp. 39–40) replaces variable names with `x1, x2, …` and finds output pass@1 down about two
points for CodeLlama 7B/13B/34B (36.4 → 34.0, 38.3 → 36.1, 41.1 → 39.1) but pass@5 up (+3.4/+5.9/
+6.5; Table 4, p. 40), and the authors flag one GPT-4 error as possibly "misled by the variable name
`prefix`" (Listing 4, p. 13). Le et al. (2025) add the caution that for frontier models a name that
merely *suggests* a wrong behaviour can be the mildest perturbation (GPT-4o LiveCodeBench 82.9 →
82.3 misleading vs 68.7 ambiguous, Table 3, p. 7). *For us:* the neutral twin is Orvalho's
condition and the congruent twin is what none of them ran; P1 predicts congruent > neutral >
misleading, and rule 2 (an executable lure that differs from every intermediate value) is how we
avoid Le et al.'s null.

**Names redefined versus names that mislead.** Miceli-Barone et al. (2023) prepend `len, print =
print, len` and score which function body the model prefers; every model prefers the body that
ignores the swap, i.e. zero accuracy (p. 3), with inverse scaling in the OPT and GPT-3 families
(Table 1, p. 3) and flat scaling for code models (p. 4). The prior there is the builtin's *meaning*,
which the swap statement contradicts; ours is a variable name whose meaning the definition
contradicts. Gao et al. (2023) give the conceptual split we use, an identifier's direct (spurious)
effect versus its indirect effect through code semantics, and remove the direct one by logit
subtraction (CREAM, Eq. 18, p. 6); Yang et al. (2022) show searched, semantically *close* renamings
flip CodeBERT (53.6%, Table 2, p. 8), nearer our congruent than our incongruent condition. *For us:*
Miceli-Barone's zero-accuracy result is P1 at the limit, and their "code models scale flat" is a
warning that P6's weak-model row may not be a *size* row.

**Names and internal mechanisms.** Lucchetti and Guha (2025) build adversarial type-prediction
prompts by renaming variables and types (pp. 2–3) and ask exactly our question in miniature: does
the model reason about semantics "or merely learn textual features such as the associations between
variable names and their types?" (p. 1). Mean-difference steering vectors in middle layers correct
50–60% of the mispredictions (p. 5), while in-context examples do not (p. 2): the mechanism is
present and the name keeps it from firing. Kou et al. (2024) find model attention over the *task
description* consistently misaligned with programmers' (p. 1; e.g. F1 44.3%, α 0.25 for InCoder,
Table 2, p. 11), but do not look at identifiers inside code. *For us:* Lucchetti's "mechanism exists,
name blocks it" is the P5 story for the direct regime; our injection/removal patches at the
identifier span are the causal version of their steering.

## 2. LLMs predicting program execution and output

**The task and its ceiling.** CRUXEval (Gu et al. 2024) is 800 Python functions of 3–13 lines with
one input–output pair (p. 1). GPT-4 with CoT reaches 81% output pass@1, Code Llama 34B 46% (p. 1).
CoT on output prediction helps Code Llama 34B (41.1 → 46.0) and GPT-3.5 (50.0 → 63.3) but not Code
Llama 13B (38.4 → 39.3; Table 3, p. 33; p. 10). LiveCodeBench (Jain et al. 2024) reuses the setup
with dated problems (511, p. 4) and a 2-shot direct / 1-shot CoT prompt pair (p. 10). *For us:* the
panel's direct accuracy must sit between these floors and ceilings (E2 go/no-go), and CRUXEval is
the P7 material; its own anonymisation ablation is the closest published number to our neutral
condition on natural code.

**Intermediate values are the weak link.** REval (Chen et al. 2024) adds statement-level tasks,
including *program state prediction* (the value and type of a variable) and an incremental-
consistency score (p. 2). Average accuracy is 44.4% and consistency 10.3 (p. 1); for the models on
our panel, CodeLlama-7B-Instruct predicts variable values at 25.1% but outputs at 62.6%,
CodeLlama-34B-Instruct 47.5% vs 65.9%, StarCoder2-15B 43.5% vs 71.5%, Gemma-7B-It 32.1% vs 57.9%
(Table III, p. 9). CoT on CodeLlama-7B-Instruct raises execution-path accuracy 10.8 → 21.4 but
*lowers* output accuracy by 6.8 points (p. 9). CoRE (Gao et al. 2026) names the pattern "superficial
execution": GPT-5 with a direct prompt gets 84.62 strict output accuracy but 18.96 process fidelity,
and CoT lifts fidelity to 64.93 (p. 6; Table 1, p. 7). CodeMind (Liu et al. 2024) scores output
prediction under a step-by-step prompt: CodeLlama-Inst-34b 47.32%, DeepSeekCoder-Inst-33b 60.23%,
GPT-4-Turbo 81.17% (Table I, p. 6), with failures in nested constructs, loop conditions and API
calls (p. 2). Abdollahi et al. (2025) give a nine-way taxonomy of trace errors for reasoning models
that are otherwise at 85–98% (pp. 1, 3). *For us:* a model that returns the right output while
holding the wrong value for a named variable is precisely a model whose answer did not pass through
that value; P3's per-instance "value written" annotation makes this a measured variable rather than
a benchmark gap, and REval's 25% value accuracy for CodeLlama-7B says the trace regime will not be at
ceiling.

**Simulation is fragile and pattern-driven.** La Malfa et al. (2024) find CodeLLaMA-34b-Instruct,
LLaMA2-70B and Jurassic2 "poor code simulators" whose accuracy collapses at ten straight-line
instructions (p. 4), and GPT-4 more accurate but less robust as the critical path lengthens (p. 5);
their Chain of Simulation prompt forces line-by-line tracing to suppress memorisation (pp. 1–2).
DexBench (Hasanov et al. 2026) pairs forward execution with backward counterfactual reasoning on 445
instances and finds non-reasoning models beating their reasoning twins on the joint task (p. 6).
SelfPiCo (Xue et al. 2024) goes the other way, using a fine-tuned Code Llama to *guess* values for
undefined names so that partial code can actually run (72.7% / 83.3% of lines, p. 1). *For us:* level
(number of intermediate assignments) is our La Malfa axis; SelfPiCo is evidence that code models do
read plausible values off names, which is what P1 needs and P2 must overcome.

**Training on traces.** The line from Scratchpads (Nye et al. 2021; synthetic Python direct 11% /
20% vs trace 26.5% / 41.5%, Table 2, p. 6) through CodeExecutor (Liu et al. 2023; trace format
`<line> k <state> var: value`, p. 4; output accuracy 76.42 vs Codex 13.07, Table 3, p. 6) and TRACED
(Ding et al. 2024; +25.2% relative on runtime variable values, p. 1) to NExT (Ni et al. 2024; +26.1
fix rate, p. 1, surviving without traces at test time, Table 3, p. 9) makes execution explicit by
*writing values*. SemCoder (Ding et al. 2024) is the exception that proves the point: its monologue
format deliberately avoids "concrete values" (p. 5) yet beats the scratchpad and NExT trace formats
on CRUXEval-O (63.5 vs 50.6 and 50.9, Table 2, p. 9). CodeI/O (Li et al. 2025) and Jung et al.
(2025) turn traces into prose rationales at scale (3.5M samples, p. 3; translated debugger traces
lifting Qwen3-4B from 56.7 to 58.5 average with 91.5% correct intermediate steps, Tables 1–2, p. 4).
*For us:* this literature says value-writing formats work but never tests them against a competing
name. P2 (trace chain) is Scratchpads with a lure; SemCoder's prose monologue is the format P3 predicts
to be vulnerable exactly when it omits the value; E10 (the single instruction "state each variable's
value") is the minimal version of what NExT trains.

## 3. Chains of thought for code and their faithfulness

**Chains that compute outside the model.** PAL (Gao et al. 2023; GSM8K 72.0 vs CoT 65.6, Table 1,
p. 5) and Program of Thoughts (Chen et al. 2023; ≈12% over CoT, p. 1) write the reasoning as code
and let an interpreter produce every value; Chain of Code (Li et al. 2023) lets the interpreter run
what it can and hands the rest to the LM as an "LMulator" that returns values into the program state
(p. 2; BBH 84%, p. 1). *For us:* these are the regimes in which the model writes *expressions* and
never a value, which is the code-chain regime of `PLAN.md` §4 and the case P3 predicts gives no
protection; Chain of Code's LMulator is the place where a name-derived value would enter the state.

**Faithfulness measured from outside.** Turpin et al. (2023) show unverbalised biasing features move
answers (one of 426 explanations mentions the bias, p. 3; up to 36.3 points lost, p. 6) and point to
interpretability tools to check whether the model registers the cue (p. 9). Lanham et al. (2023) find
faithfulness falls with size from 13B to 175B (p. 7) and lack "a separate way … to understand the
model's real internal reasoning process" (p. 9). Arcuschin et al. (2025) document the same in the
wild. CodeCrash (Lam et al. 2025) is the code instance: misleading comments and hints cost −23.2%
direct and −13.8% with CoT on average, with Llama-3.1-8B still −19.8% under CoT (Tables 1–2,
pp. 4–5), and failure traces "absorb the misleading messages directly into [the] reasoning" (p. 5).
Roh et al. (2025) show prompt-level rewrites of LiveCodeBench problems swing accuracy by −42.1% to
+35.3% (p. 1). *For us:* the "value written" annotation of P3 is a faithfulness measure Turpin and
Lanham could not define, because it asks not whether the chain mentions the cue but whether it
writes the quantity that would make the cue irrelevant; CodeCrash's "reduces but does not remove"
at 7–8B is the behavioural shape P3 has to explain instance by instance.

## 4. Internals of code models

**Probing program state.** Jin and Rinard (2024) probe a from-scratch Karel model and recover the
abstract program state (linear 63.2%, 2-layer MLP 82.3%, Table 1, p. 6) with an interventional
baseline that separates what the model represents from what the probe learns (p. 2). Chen et al.
(2026, "Brewing") is the closest design to ours: six synthetic execution families with single-digit
answers 0–9 (p. 6) and randomised identifiers (p. 20), layer-wise linear probes paired with
context-stripped decoding on 16 models (pp. 4, 7); the answer is linearly recoverable ≈38% of depth
before the model can use it (p. 9), and re-injecting an earlier state repairs 47.8% of cases that
had the answer and lost it (p. 10). Their CRUXEval-O numbers put CodeLlama-7B at 36.5% on a 200-item
subset (Table 3, p. 26). *For us:* their probe target, digit range and matched-program design are
ours; the difference is that with random identifiers a decoded digit has one possible source,
whereas P5 requires two (the name and the computation), which is the same gap the arithmetic paper
opened in Kudo et al.

**State tracking without incremental state.** Li, Guo and Andreas (2025) show permutation-tracking
models learn an associative-scan mechanism, read off probe-accuracy and prefix-patching signatures
across layers (pp. 1–2). Tang et al. (2026) find that in box-world entity tracking LMs "do not
incrementally track world states across tokens … but simply aggregate relevant information in
parallel at the last token when the query becomes evident" (p. 1). Lucchetti and Guha (2025) show a
type-prediction mechanism that exists but fails to fire under adversarial names (p. 2, 5). *For us:*
Tang's parallel-aggregation result is what P5 predicts for the direct regime (the lure decodable at
the name and at its use site through to the answer, never overwritten), and Lucchetti's is the
mechanism P5's injection patch would activate.

**Methods we follow.** Hewitt and Liang (2019): control task keyed on the identifier, selectivity =
task − control (§2, p. 3; p. 2), linear probes still memorise (Table 1, p. 5). Zhang and Nanda
(2024): in-distribution equal-length corruption (p. 3, 8), normalised logit difference (p. 8),
single layers before windows and alternative corruptions (p. 9). Both are already rules 4–5 of
`PLAN.md` §5; the span-based positions replace the single-token requirement because code tokenizers
split identifiers unpredictably. *For us:* P5's selectivity control is Hewitt's with the variable
name as the type.

## 5. The arithmetic cue-conflict paper and Kudo et al. (probe recipe)

**Kudo et al. (2026).** Synthetic `A=1+B, B=2+3` problems at five levels (Table 1, p. 3), single-digit
values, one linear probe per (position, layer, variable). Every computed sub-answer becomes decodable
only after the chain begins (Table 2, p. 4; Table 3, p. 6); patching shows the answer depends on the
chain and barely on the input (Fig. 5, p. 7) with recency bias (Fig. 6, p. 8); the no-chain format
reaches 77.8% with no position above threshold (Table 6, p. 13); Llama-3.2-3B is the weak model
(38.5% at level 5, Table 7, p. 13). Every variable is a letter, so a decoded value has one source.

**Paper 1 (`../probing/`).** Adds the disagreement: a variable whose *name* is a number word that
differs from its defined value, with neutral, congruent and alternative-lure twins, and finds (as of
2026-09-13) that the chain replaces the lure because it writes every intermediate value, and that
the direct regime reads the value off the name; OLMo-2-1B, which cannot compute the value, is not
protected. The cue-conflict lineage it sits in — Stroop-style interference in LMs (Wang 2026, Δ
1.31–2.71 nats, p. 4, with neutral-into-conflict patching, Table 2, p. 6; Hu et al. 2026, 100%
accuracy in both conditions, p. 11), Geirhos et al. (2019) for the design and the lure index
(Fig. 4, p. 6), Shi et al. (2023) for distraction by lexical overlap (Table 3, p. 6; Table 4, p. 8),
Yang et al. (2025) for shortcuts — carries over unchanged. *For us:* this project keeps the levels,
the probe recipe, the twins and the claim rule (δ = 2, TOST), and changes one thing: in code the
chain the model writes on its own does not always contain the value. P2 says a chain that does
protects; P3 says a chain that does not, does not; P6 says a model that cannot compute the value is
the OLMo-2-1B row again; P4 and P7 carry the result to generation and to natural code.

## 6. Positioning table

| area | representative | this paper differs by |
|---|---|---|
| misleading names in code | Le et al. 2026; CodeCrash; Le et al. 2025; Orvalho & Kwiatkowska 2025 | one identifier, an executable lure, congruent/neutral/alt-lure twins, regime as a manipulation |
| identifier mechanisms | Miceli-Barone 2023; Gao et al. 2023; Lucchetti & Guha 2025 | probes and patches at the identifier span across a reasoning chain |
| execution prediction | CRUXEval; REval; CoRE; CodeMind; La Malfa 2024 | intermediate values are the *manipulated* variable, scored per instance, not a benchmark gap |
| trace training | Scratchpads; CodeExecutor; NExT; SemCoder; CodeI/O; Jung 2025 | value-writing tested as *protection against a cue*, not as accuracy |
| code-as-chain | PAL; PoT; Chain of Code | a regime in which no value is written, predicted to fail |
| CoT faithfulness | Turpin 2023; Lanham 2023; Arcuschin 2025 | "value written" as an instance-level faithfulness variable, checked inside the model |
| code-model internals | Jin & Rinard 2024; Brewing 2026; Tang 2026; Li et al. 2025 | a decoded value with two possible sources |
| arithmetic lineage | Kudo et al. 2026; paper 1 | same recipe; the chain no longer writes values by construction |

## 7. Consequences for the experiments

- **E2 pilot** must report REval-style *value* accuracy alongside output accuracy for the trace
  regime, so that P2's "within δ" is not an artefact of a model that cannot trace (REval, p. 9).
- **E3** should report a Geirhos-style lure index beside accuracy (carried from paper 1).
- **E4** annotation of "value written" should distinguish the SemCoder monologue style (properties,
  no values) from the scratchpad style, since both count as prose chains.
- **E8** should include CRUXEval's `x1, x2, …` anonymisation as a fourth naming condition, so the
  P7 row connects to a published number (Table 4, p. 40).
- **Citation flags before submission:** venues of PAL (ICML 2023?) and LiveCodeBench (ICLR 2025?)
  are not printed in the PDFs; REval's ICSE 2025 pages; CodeMind's TSE volume; the on-disk title of
  Chen et al. 2026 differs from its arXiv listing; Tang et al. 2026 not yet read past §2.
