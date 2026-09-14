# References: what is on disk, what was read, and how

*Created 2026-09-14 for the code cue-conflict plan (`../PLAN.md`). 44 PDFs. Page numbers refer to
the PDF on disk (arXiv version unless a venue line is printed on page 1). Two reading passes feed
this file: the 17 PDFs copied from `../../probing/papers/` carry the page cites verified by that
project's pass of 2026-09-12 (see `../../probing/RELATED_WORK.md`); the 5 copied from
`../../obtune/papers/` and the 22 new downloads were read in this pass with `pypdf` text, one PDF at
a time. Numbers without a page cite were not read from the PDF and are not used in
`../RELATED_WORK.md`. "(not yet read)" marks entries whose PDF was opened only to page 1–2.*

*Naming:* files keep the names they had in the source folders (so `stroop2026priors.pdf` is
Wang 2026 and `obf2026humans.pdf` is Le, Nguyen & Nguyen 2026). New downloads are
`author-year-keyword.pdf`. `paper2_Le2026_LLMvsHumanObfuscatedCode.pdf` in obtune is byte-identical
to `obf2026humans.pdf` and was not duplicated.

---

## 1. Identifier names and code comprehension

**micelibarone2023swaps** — Miceli-Barone, Barez, Konstas, Cohen (2023). *The Larger They Are, the
Harder They Fail: Language Models do not Recognize Identifier Swaps in Python.* Findings of ACL 2023;
arXiv:2305.15507. `micelibarone2023swaps.pdf` (new).
A statement such as `len, print = print, len` precedes a function; the model must prefer the body
that respects the swap over the body that uses the builtins as usual, scored by likelihood (p. 2).
Every tested model prefers the incorrect body, i.e. zero classification accuracy (p. 3). OPT and
GPT-3 families show inverse scaling (Table 1, p. 3); code models (CodeGen) scale flat, and the
Python-only "mono" variants are worse than the multi-language ones (p. 4); InstructGPT is worse than
base GPT-3 (p. 4). The cue is a *redefined* name, not a misleading one, and there is no chain of
thought.

**gao2023cream** — Gao, Gao, Wang, Sun, Lo, Yu (2023). *Two Sides of the Same Coin: Exploiting the
Impact of Identifiers in Neural Code Comprehension.* ICSE 2023, pp. 1933–1945; arXiv:2207.11104.
`gao2023cream.pdf` (copied, probing).
Splits an identifier's influence into a direct (spurious) effect and an indirect effect through the
code's semantics and removes the direct one by logit subtraction (CREAM, Eq. 18, p. 6); one rename
flips a method-naming model from "sort" to "open" (Fig. 1, p. 1).

**yang2022naturalattack** — Yang, Shi, He, Lo (2022). *Natural Attack for Pre-trained Models of
Code.* ICSE 2022; arXiv:2201.08698. `yang2022naturalattack.pdf` (copied, probing).
Searched, semantically *close* renamings that flip CodeBERT (53.6% success on vulnerability
prediction, Table 2, p. 8). A searched perturbation, not a designed conflict.

**le2025names** — Le, Pham, Van, Phan, Phan, Nguyen (2025). *When Names Disappear: Revealing What
LLMs Actually Understand About Code.* arXiv:2510.03178. `le2025names.pdf` (copied, probing).
Frontier models under four name-only obfuscations. Summarisation collapses (GPT-4o 87.3 → 58.7,
p. 5); on LiveCodeBench execution *misleading* names are the mildest perturbation for GPT-4o
(82.9 → 82.3 vs 68.7 for ambiguous names, Table 3, p. 7); names act as retrieval keys for memorised
outputs (Table 4, p. 9).

**le2026obfuscated** — Le, Nguyen, Nguyen (2026). *Do Machines Struggle Where Humans Do? LLM and
Human Comprehension of Obfuscated Code.* arXiv:2606.31725v1. `obf2026humans.pdf` (copied, probing;
cite in the third person under review).
Output prediction across tiers L0–L3 on 0.5–8B models; L1b is misleading renaming. Strongest models
lose most: DS-R1-Qwen-7B 63.8 → 64.2 → 51.8 (L0 → L1 → L1b), SmolLM3-3B 45.0 → 44.0 → 34.2
(Table II, p. 4); human experts improve at L1b (pp. 4–5, 7). The "21% / 10%" figures are the n = 80
tail where top-20% semantic displacement and top-20% identifier surprisal co-occur (21.25% accuracy,
10.00% high-confidence-incorrect, vs 31.68% baseline subset; Table X, p. 9). Many identifiers change
at once; no congruent condition; behaviour only.

**orvalho2025mutations** — Orvalho, Kwiatkowska (2025). *Are Large Language Models Robust in
Understanding Code Against Semantics-Preserving Mutations?* arXiv:2505.10443v3.
`mutations2025robust.pdf` (copied, probing).
Renaming to random identifiers *raises* accuracy for most open models (Qwen2.5-Coder 62.6 → 76.6,
Table 2, p. 8); 10–55% of correct answers rest on flawed reasoning (Table 1, p. 7).

**lam2025codecrash** — Lam, Wang, Huang, Lyu (2025). *CodeCrash: Exposing LLM Fragility to
Misleading Natural Language in Code Reasoning.* NeurIPS 2025; arXiv:2504.14119v3.
`lam2025codecrash.pdf` (copied, probing).
Misleading comments, prints and hints on CRUXEval/LiveCodeBench, 17 models. Direct inference
−23.2% on average, CoT −13.8%; not eliminated for small open models (Llama-3.1-8B −19.8%,
Qwen2.5-7B −19.7% under CoT; Tables 1–2, pp. 4–5). Renaming alone −4.0% on CRUXEval (Table 10,
p. 17). Failure traces "absorb the misleading messages directly into [the] reasoning" (p. 5).

**lucchetti2025steering** — Lucchetti, Guha (2025). *Understanding How CodeLLMs (Mis)Predict Types
with Activation Steering.* BlackboxNLP 2025; arXiv:2404.01903. `lucchetti2025steering.pdf` (new).
Type prediction in Python/TypeScript; adversarial variants are built by renaming variables or types
and deleting annotations (p. 2–3), which makes a model that was right go wrong (p. 1). The question
asked is ours in miniature: does the model reason about semantics "or merely learn textual features
such as the associations between variable names and their types?" (p. 1). Mean-difference steering
vectors added in middle layers correct 50–60% of the mispredictions (p. 5); in-context examples have
negligible effect where the edit succeeds (p. 2); the mechanism is shared across the two languages
(p. 1).

**kou2024attention** — Kou, Chen, Wang, Ma, Zhang (2024). *Do Large Language Models Pay Similar
Attention Like Human Programmers When Generating Code?* Proc. ACM Softw. Eng. 1 (FSE), Art. 100;
arXiv:2306.01220. `kou2024attention.pdf` (new).
Six LLMs, two code-generation benchmarks; consistent misalignment between model and programmer
attention over the task description (p. 1, 2); 211 incorrect snippets yield five attention patterns
that explain errors (p. 1). Alignment is low in absolute terms (e.g. InCoder, BERT-masking, top-5:
F1 44.3%, Krippendorff's α 0.25; Table 2, p. 11). Attention over *natural language*, not over
identifiers in code.

## 2. Predicting program execution

**gu2024cruxeval** — Gu, Rozière, Leather, Solar-Lezama, Synnaeve, Wang (2024). *CRUXEval: A
Benchmark for Code Reasoning, Understanding and Execution.* arXiv:2401.03065. `gu2024cruxeval.pdf`
(copied, obtune).
800 Python functions of 3–13 lines with an input–output pair; input and output prediction (p. 1).
GPT-4 + CoT 75% / 81% pass@1, Code Llama 34B 50% / 46% (p. 1). CoT on output prediction: Code Llama
13B 38.4 → 39.3, 34B 41.1 → 46.0, GPT-3.5 50.0 → 63.3 (Table 3, p. 33); "CoT helps Code Llama 34B
and GPT-4 on both … Code Llama 13B on neither task" (p. 10). **Anonymisation ablation** (App. C.5,
pp. 39–40): replacing variable names with `x1, x2, …` lowers output pass@1 by about two points for
CodeLlama 7B/13B/34B (36.4 → 34.0, 38.3 → 36.1, 41.1 → 39.1) while raising pass@5 (+3.4/+5.9/+6.5;
Table 4, p. 40). Listing 4 (p. 13) records a GPT-4 error the authors attribute to a variable named
`prefix`.

**liu2023codeexecutor** — Liu, Lu, Chen, Jiang, Svyatkovskiy, Fu, Sundaresan, Duan (2023). *Code
Execution with Pre-trained Language Models.* Findings of ACL 2023; arXiv:2305.05383.
`liu2023codeexecutor.pdf` (copied, obtune).
Pre-trains a Transformer to emit the full execution trace as `<line> k <state> var: value; …`
(Fig. 1, p. 2; p. 4), with mutation-based augmentation and a curriculum. Output accuracy 76.42 on
Tutorial vs Codex 13.07, 48.06 on CodeNetMut vs Codex 17.45, 94.03 on SingleLine (Table 3, p. 6).

**nye2021scratchpads** — Nye et al. (2021). *Show Your Work: Scratchpads for Intermediate
Computation with Language Models.* arXiv:2112.00114. `nye2021scratchpads.pdf` (copied, obtune).
Emit the line-by-line trace before the answer. Synthetic Python: direct 11% / 20% vs scratchpad
26.5% / 41.5% (few-shot / fine-tuned; Table 2, p. 6). MBPP: in the very-low-data regime direct wins
(10% vs 5%, p. 7); with sampled-program augmentation plus CodeNet and single-line data, tracing
executes 26.6% of tasks correctly and traces 24.6% perfectly (p. 9).

**ni2024next** — Ni, Allamanis, Cohan, Deng, Shi, Sutton, Yin (2024). *NExT: Teaching Large
Language Models to Reason about Code Execution.* ICML 2024; arXiv:2404.14662. `ni2024next.pdf`
(copied, obtune).
Self-trains PaLM 2 to naturalise execution traces into rationales; fix rate +26.1 (MBPP-R) and
+14.3 (HumanEvalFix+) absolute (p. 1, 3); the gain survives when traces are absent at test time
(44.1, +25.1; Table 3, p. 9).

**ding2024semcoder** — Ding, Peng, Min, Kaiser, Yang, Ray (2024). *SemCoder: Training Code Language
Models with Comprehensive Semantics Reasoning.* NeurIPS 2024; arXiv:2406.01006.
`ding2024semcoder.pdf` (copied, obtune).
"Monologue reasoning": the 6.7B model verbalises execution in prose, deliberately *avoiding*
redundant states and concrete values (p. 5). 63.9% CRUXEval-O vs GPT-3.5-turbo 59.0% (p. 1).
Ablation on CRUXEval-O: few-shot 41.2, scratchpad 50.6, NExT trace 50.9, concise trace 55.6,
monologue 63.5 (Table 2, p. 9).

**ding2024traced** — Ding, Steenhoek, Pei, Kaiser, Le, Ray (2024). *TRACED: Execution-aware
Pre-training for Source Code.* ICSE 2024; arXiv:2306.07487. `ding2024traced.pdf` (new).
Multi-task pre-training on source, program states and coverage (p. 2); relative gains of 12.4% on
execution-path prediction and 25.2% on runtime variable-value prediction over static pre-training
(p. 1); Codex fails a coverage question even with data-flow hints in the prompt (p. 1).

**chen2024reval** — Chen, Pan, Hu, Li, Li, Xia (2024). *Reasoning Runtime Behavior of a Program
with LLM: How Far Are We?* ICSE 2025 (per arXiv listing); arXiv:2403.16437v3. `chen2024reval.pdf`
(new).
Four statement-level tasks — coverage (CCP), **program state (PSP: value and type of a variable)**,
execution path (EPP), output (OP) — plus an incremental-consistency score (p. 2); 3,152 problems
(Table I, p. 7). Average accuracy 44.4%, IC 10.3 (p. 1). Table III (p. 9): CodeLlama-7B-Instruct PSP
25.1%, OP 62.6%; CodeLlama-34B-Instruct PSP 47.5%, OP 65.9%; StarCoder2-15B PSP 43.5%, OP 71.5%;
Gemma-7B-It PSP 32.1%, OP 57.9%; GPT-4-Turbo average 75.0. CoT on CodeLlama-7B-Instruct raises EPP
10.8 → 21.4 but lowers OP by 6.8 points (p. 9). IC below 20 for every open model (p. 2, 9).

**liu2024codemind** — Liu, Chen, Jabbarvand (2024/2026). *CodeMind: Evaluating Large Language
Models for Implicit and Explicit Code Execution Reasoning.* IEEE TSE (header dated Jan. 2026);
arXiv:2402.09664. `liu2024codemind.pdf` (new).
Independent execution reasoning (IER = output prediction with a step-by-step CoT prompt, p. 3–4) on
1,450 Python programs, 13 models (p. 2). IER rate: CodeLlama-Inst-34b 47.32%, DeepSeekCoder-Inst-33b
60.23%, SemCoder-S 55.19% (+10.91 over its base), GPT-4-Turbo 81.17%, Claude-Sonnet-4.6 95.93%
(Table I, p. 6); on CRUXEval alone CodeLlama-Inst-34b 48.13%. Failures concentrate in nested
constructs, complex predicates, loop conditions and API calls (p. 2). Renaming variables and functions
is one of the reverse-refactoring transformations in the DSR task (Table IV, pp. 7–8).

**lamalfa2024simulation** — La Malfa et al. (2024). *Code Simulation Challenges for Large Language
Models.* arXiv:2401.09074. `lamalfa2024simulation.pdf` (new).
Six synthetic benchmarks (straight-line code, critical paths, approximate/redundant instructions,
nested loops, sorting; p. 3). Jurassic2-Ultra, LLaMA2-70B and CodeLLaMA-34b-Instruct "are poor code
simulators: their performance significantly downgrades with just 10 instructions" (p. 4); GPT-4 is
more accurate but suffers a sharper drop as the critical path approaches the whole program (p. 5).
Chain of Simulation (CoSm) prompts line-by-line simulation with the trace to suppress memorisation
(pp. 1–2).

**jain2024livecodebench** — Jain et al. (2024). *LiveCodeBench: Holistic and Contamination Free
Evaluation of Large Language Models for Code.* arXiv:2403.07974 (ICLR 2025 — verify, no venue line
in the PDF). `jain2024livecodebench.pdf` (new).
511 problems from LeetCode/AtCoder/CodeForces with release dates (p. 4, 9); the *code execution*
scenario copies CRUXEval's output-prediction setup with a 2-shot direct prompt and a 1-shot CoT
prompt (p. 6, 10); generation–execution correlation 0.89 (p. 11).

**xue2024selfpico** — Xue, Gao, Wang, Hu, Xia, Li (2024). *SelfPiCo: Self-Guided Partial Code
Execution with LLMs.* ISSTA 2024; arXiv:2407.16974. `xue2024selfpico.pdf` (new).
A fine-tuned Code Llama predicts missing definitions so that partial snippets run; executes 72.7% /
83.3% of lines (open-source / Stack Overflow), +37.9 / +33.5 over Lexecutor (p. 1). The model
*guesses values from names and context* for real execution — the opposite direction from ours.

**abdollahi2025errors** — Abdollahi, Tasnia, Saha, Yang, Wang, Hemmati (2025). *Demystifying Errors
in LLM Reasoning Traces: An Empirical Study of Code Execution Simulation.* arXiv:2512.00215.
`abdollahi2025errors.pdf` (new).
427 snippets from HumanEval+ and LiveCodeBench, 12 inputs each; four reasoning LLMs reach 85–98%
(p. 1). A nine-category taxonomy of trace errors (computation, indexing, control flow, skipped
statements, misreported output, input misread, native-API misevaluation, hallucination, lack of
verification; p. 3); tool augmentation fixes 58% of computation errors (p. 1, 3).

**gao2026core** — Gao et al. (2026). *CoRE: A Fine-Grained Code Reasoning Benchmark Beyond Output
Prediction.* Findings of ACL 2026; arXiv:2604.25399. `gao2026core.pdf` (new).
60 problems, 255 functionally equivalent implementations (4.1 per problem), 7.8 tests and 4.1
intermediate-state probes per problem (p. 2, 4). "Superficial execution": GPT-5 with a direct
prompt reaches strict output accuracy 84.62 but process fidelity 18.96; CoT raises fidelity to
64.93 (p. 6; Table 1, p. 7). Models score best on code in their own family's style (p. 2, 6).

**hasanov2026dexbench** — Hasanov, Sibat, Karmaker, Yadavally (2026). *The Path Not Taken: Duality
in Reasoning about Program Execution.* ACL 2026; arXiv:2604.20917. `hasanov2026dexbench.pdf` (new).
445 paired instances; forward (execution) and backward (counterfactual-input) reasoning on the same
program, 13 LLMs (p. 1). Dual-path accuracy falls with complexity, CRUXEval < HumanEval < PythonSaga
(p. 5); non-reasoning models beat their reasoning twins on dual-path pass@5 by 63.9% and 47.9% on
average (p. 6).

**roh2025collapse** — Roh, Gandhi, Anilkumar, Garg (2025). *Chain-of-Code Collapse: Reasoning
Failures in LLMs via Adversarial Prompting in Code Generation.* arXiv:2506.06971.
`roh2025collapse.pdf` (new).
700 perturbed LiveCodeBench generations (storytelling, gamification, domain shift, distracting
constraints, negation, numeric perturbation), nine LLMs (p. 2); drops up to −42.1% and gains up to
+35.3% (p. 1). Prompt-level, not identifier-level.

## 3. Chains of thought for code

**li2023chainofcode** — Li et al. (2023). *Chain of Code: Reasoning with a Language
Model-Augmented Code Emulator.* ICML 2024 (oral); arXiv:2312.04474. `li2023chainofcode.pdf` (new).
The model writes pseudocode; an interpreter runs what it can and hands undefined calls to the LM
("LMulator", p. 2), which returns *values* into the program state (Fig. 1, p. 1). BIG-Bench Hard
84%, +12 over CoT (p. 1).

**gao2023pal** — Gao, Madaan, Zhou, Alon, Liu, Yang, Callan, Neubig (2023). *PAL: Program-aided
Language Models.* arXiv:2211.10435 (ICML 2023 — verify, no venue line in the PDF). `gao2023pal.pdf`
(new).
Reasoning is written as a program and executed by an interpreter; GSM8K 72.0 vs CoT-Codex 65.6 and
PaLM-540B CoT 56.9; direct Codex 19.7 (Table 1, p. 5).

**chen2023pot** — Chen, Ma, Wang, Cohen (2023). *Program of Thoughts Prompting: Disentangling
Computation from Reasoning for Numerical Reasoning Tasks.* TMLR 10/2023; arXiv:2211.12588.
`chen2023pot.pdf` (new).
Average gain of about 12% over CoT (p. 1); few-shot GSM8K CoT 63.1 vs PoT 71.6 (p. 3). With PAL:
the two papers in which the chain is code and the values are computed *outside* the model — the
regime in which no value token is ever written by the model.

**li2025codeio** — Li, Guo, Yang, Xu, Wu, He (2025). *CodeI/O: Condensing Reasoning Patterns via
Code Input-Output Prediction.* ICML 2025 (oral); arXiv:2502.07316. `li2025codeio.pdf` (new).
3.5M input/output-prediction samples from 454.9K code files (p. 3), with *natural-language* CoT
rationales generated by DeepSeek-V2.5 (pp. 2, 4); 50% of first-turn rationales are correct and 10%
of the wrong ones are fixed by revision (p. 4); consistent gains across reasoning benchmarks
including CRUXEval (p. 2, 4).

**jung2025grounded** — Jung, Zhou, Chen (2025). *Code Execution as Grounded Supervision for LLM
Reasoning.* EMNLP 2025 (Anthology 2025.emnlp-main.1260); arXiv:2506.10343v2.
`jung2025grounded.pdf` (new).
Debugger (Snoop) traces with variable values are translated by an LLM into prose CoT (p. 2). Qwen3-4B
average: no training 56.7, raw trace 36.4, CodeI/O 56.9, translated trace 58.5 (Table 1, p. 4);
intermediate-step correctness 91.5 vs 73.0 for CodeI/O (Table 2, p. 4).

**turpin2023unfaithful** — Turpin, Michael, Perez, Bowman (2023). *Language Models Don't Always
Say What They Think.* NeurIPS 2023; arXiv:2305.04388. `turpin2023unfaithful.pdf` (copied, probing).
Unverbalised biasing features move answers: of 426 explanations supporting biased predictions one
mentions the bias (p. 3); zero-shot CoT accuracy drops up to 36.3 points (p. 6); almost all of the
drop is bias-consistent (App. F.5).

**lanham2023measuring** — Lanham et al. (2023). *Measuring Faithfulness in Chain-of-Thought
Reasoning.* arXiv:2307.13702. `lanham2023measuring.pdf` (copied, probing).
Truncation and corruption of the model's own chain; faithfulness worsens with size from 13B to
175B (p. 7); on synthetic addition, same-answer-without-CoT rises with size and ease (p. 8); they
lack "a separate way … to understand the model's real internal reasoning process" (p. 9).

**arcuschin2025wild** — Arcuschin et al. (2025). *Chain-of-Thought Reasoning In The Wild Is Not
Always Faithful.* arXiv:2503.08679. `arcuschin2025wild.pdf` (copied, probing; appendix reference,
no page cites used).

## 4. Internals of code and state-tracking models

**jin2024emergent** — Jin, Rinard (2024). *Emergent Representations of Program Semantics in
Language Models Trained on Programs.* ICML 2024 (PMLR 235); arXiv:2305.11169. `jin2024emergent.pdf`
(new).
A from-scratch LM on Karel programs (92.4% generative accuracy, p. 3); probes on hidden states
recover the abstract program state: linear 63.2%, 1-layer MLP 79.1%, 2-layer MLP 82.3% for the
current state (Table 1, p. 6); semantic content tracks generative accuracy (R² 0.878, p. 6). An
interventional baseline with alternative semantics separates what the LM represents from what the
probe learns (p. 2).

**chen2026brewing** — Chen et al. (2026). *From Brewing into Resolution: Tracing Internal
Reasoning Trajectories in LLMs.* arXiv:2606.17648 (arXiv listing title: "From Brewing to
Resolution: Tracing the Internal Lifecycle of Code Reasoning in LLMs"). `chen2026brewing.pdf` (new).
Six synthetic code-execution task families (value tracking, computing, conditional, function call,
loop, loop-unrolled; Table 1, p. 18) with **single-digit answers 0–9** (p. 6) and **randomised
identifiers** (p. 20); 24,300 programs, 16 models, anchor Qwen2.5-Coder-7B (pp. 6–7). Layer-wise
linear probes ("Availability") are paired with context-stripped decoding ("Readiness") (p. 4, 7).
"Brewing" between the two lasts 10.7 layers ≈ 38% of depth in the anchor (p. 9); transferring the
hidden state into a neutral prompt succeeds 3–18% before and 20–44% at the first joint-correct layer
(p. 10); re-injecting an earlier state restores 47.8% of "overprocessed" cases (p. 10). CRUXEval-O
on a 200-item subset: CodeLlama-7B 36.5%, DeepSeek-Coder-6.7B 45.5% (Table 3, p. 26).

**li2025statetracking** — Li, Guo, Andreas (2025). *(How) Do Language Models Track State?* ICML
2025; arXiv:2503.02854v3. `li2025statetracking.pdf` (new).
Permutation composition as a proxy for state tracking; models learn either an associative-scan
algorithm or a parity-then-scan variant (p. 1), diagnosed by probe-accuracy and prefix-patching
signatures across layers (p. 2).

**tang2026entities** — Tang, Zhao, Franco, Wijaya, Mueller, Schuster, Kim (2026). *Do Language
Models Track Entities Across State Changes?* ICML 2026 (per icml.cc listing); arXiv:2605.30233.
`tang2026entities.pdf` (new; not yet read beyond the abstract and §2).
Box-world entity tracking with PUT/REMOVE/MOVE; LMs "do not incrementally track world states across
tokens … but simply aggregate relevant information in parallel at the last token when the query
becomes evident" (p. 1); global 8-way and local binary probes test the two hypotheses (p. 2).

**kudo2026faithful** — Kudo et al. (2026). *LLMs Faithfully and Iteratively Compute Answers During
CoT.* Findings of EACL 2026, pp. 1114–1153. `kudo2026faithful.pdf` (copied, probing; read in full
there). Synthetic `A=1+B` problems at five levels (Table 1, p. 3); one linear probe per (position,
layer, variable); every computed sub-answer becomes decodable only after the chain begins (Table 2,
p. 4; Table 3, p. 6); patching shows the answer depends on the chain, barely on the input (Fig. 5,
p. 7) with recency bias (Fig. 6, p. 8); implicit format 77.8% with no position above τ (Table 6,
p. 13); Llama-3.2-3B 93.2 / 90.9 / 38.5% at levels 3–5 (Table 7, p. 13).

**hewitt2019control** — Hewitt, Liang (2019). *Designing and Interpreting Probes with Control
Tasks.* EMNLP 2019; arXiv:1909.03368. `hewitt2019control.pdf` (copied, probing). Control task =
random label per word type (§2, p. 3); selectivity = task − control accuracy (p. 2); linear probes
still memorise (71.2% control accuracy on PoS, Table 1, p. 5).

**zhang2024patching** — Zhang, Nanda (2024). *Towards Best Practices of Activation Patching in
Language Models.* ICLR 2024; arXiv:2309.16042v2. `zhang2024patching.pdf` (copied, probing). Corrupt
with an in-distribution equal-length token swap (p. 3, 8); report normalised logit difference
(p. 8); single layers before windows (p. 9); try alternative corruptions (p. 9).

## 5. Cue conflict, shortcuts, distraction

**wang2026stroop** — Wang (2026). *Persistent Priors, Preserved Targets: A Stroop-Style Paradigm for
Lexical Override.* arXiv:2606.07555v5. `stroop2026priors.pdf` (copied, probing). Interference Δ
1.31–2.71 nats across eleven settings (p. 4; Table 8, p. 12); neutral-into-conflict patching
restores the margin, R = 0.92–1.06 (Table 2, p. 6); no chain, no accuracy.

**hu2026conflict** — Hu et al. (2026). *Conflict and Congruency Effects in Large Language Models.*
arXiv:2608.11510. `stroop2026conflict.pdf` (copied, probing). Congruency effect 0.397 in
Δ-probability with 100% accuracy in both conditions (p. 11); short-range vs long-range pathways
(pp. 12–13).

**geirhos2019texture** — Geirhos et al. (2019). *ImageNet-trained CNNs are biased towards texture.*
ICLR 2019. `geirhos2019texture.pdf` (copied, probing). Cue-conflict stimuli pre-selected to be
classified correctly alone (p. 4; App. A.6, p. 15); shape bias computed only over trials whose
answer matches one of the two cues (Fig. 4, p. 6).

**shi2023distracted** — Shi et al. (2023). *Large Language Models Can Be Easily Distracted by
Irrelevant Context.* ICML 2023. `shi2023distracted.pdf` (copied, probing). One irrelevant sentence
drops macro accuracy to 6% (Table 3, p. 6); lexical overlap matters more than the distractor's
number (p. 2; Table 4, p. 8).

**yang2025shortcuts** — Yang, Kassner, Gribovskaya, Riedel, Geva (2025). *Do Large Language Models
Perform Latent Multi-Hop Reasoning without Exploiting Shortcuts?* Findings of ACL 2025;
arXiv:2411.16679. `yang2025shortcuts.pdf` (copied, probing; appendix reference, no page cites used).

---

## Verification table

| bib key | file | verified from PDF | venue source | flag |
|---|---|---|---|---|
| micelibarone2023swaps | micelibarone2023swaps.pdf | title, authors | ACL Anthology 2023.findings-acl.19 | — |
| chen2024reval | chen2024reval.pdf | title, authors, arXiv 2403.16437v3 | arXiv comment (ICSE 2025) | verify proceedings pages |
| liu2024codemind | liu2024codemind.pdf | title, authors, TSE header "Jan 2026" | PDF | volume/pages not printed |
| li2023chainofcode | li2023chainofcode.pdf | title, authors | icml.cc 2024 oral | PDF is arXiv version |
| xue2024selfpico | xue2024selfpico.pdf | title, authors, ISSTA 2024 | PDF | — |
| gao2023pal | gao2023pal.pdf | title, authors | — | **venue to verify** (ICML 2023 from memory) |
| chen2023pot | chen2023pot.pdf | title, authors, TMLR 10/2023 | PDF | — |
| jain2024livecodebench | jain2024livecodebench.pdf | title, authors | — | **venue to verify** (ICLR 2025 from memory) |
| ding2024traced | ding2024traced.pdf | title, authors, ICSE 2024 | PDF | — |
| jin2024emergent | jin2024emergent.pdf | title, authors | PMLR v235 | PDF is arXiv v3 |
| lamalfa2024simulation | lamalfa2024simulation.pdf | title, authors | arXiv | no venue found |
| li2025codeio | li2025codeio.pdf | title, authors | PMLR v267 | PDF is arXiv version |
| jung2025grounded | jung2025grounded.pdf | title, authors, arXiv v2 | ACL Anthology 2025.emnlp-main.1260 | — |
| chen2026brewing | chen2026brewing.pdf | title (differs from arXiv listing), 12 authors | arXiv | title mismatch; cite the on-disk title |
| abdollahi2025errors | abdollahi2025errors.pdf | title, authors | arXiv | no venue |
| gao2026core | gao2026core.pdf | title, authors | ACL Anthology 2026.findings-acl.460 | — |
| hasanov2026dexbench | hasanov2026dexbench.pdf | title, authors | ACL Anthology 2026.acl-long.735 | — |
| li2025statetracking | li2025statetracking.pdf | title, authors, arXiv v3 | icml.cc 2025 | — |
| roh2025collapse | roh2025collapse.pdf | title, authors, arXiv v2 | arXiv | no venue |
| kou2024attention | kou2024attention.pdf | title, authors, PACMSE/FSE 2024 | PDF | — |
| lucchetti2025steering | lucchetti2025steering.pdf | title, authors | ACL Anthology 2025.blackboxnlp-1.22 | PDF is arXiv version |
| tang2026entities | tang2026entities.pdf | title, authors | icml.cc 2026 | **not yet read** |
| gu2024cruxeval | gu2024cruxeval.pdf | title, authors | arXiv | — |
| liu2023codeexecutor | liu2023codeexecutor.pdf | title, authors | obtune refs (Findings ACL 2023) | — |
| ding2024semcoder | ding2024semcoder.pdf | title, authors | obtune refs (NeurIPS 2024) | — |
| ni2024next | ni2024next.pdf | title, authors | obtune refs (ICML 2024) | — |
| nye2021scratchpads | nye2021scratchpads.pdf | title | arXiv | — |
| (17 probing copies) | as named above | see `../../probing/papers/REFERENCES.md` | — | flags carried over unchanged |

## Downloaded and deliberately excluded (not in this folder)

Read to page 1 and judged off-topic for this plan: 2605.06184 (symbolic-execution traces for C
verification), 2510.17868 (UniCode), 2601.21894 (code complexity and reasoning), 2603.03332 (CoT
perturbations, not code), 2510.02917 / 2606.14530 / 2608.08266 (probing *code correctness*, not
execution), 2504.04372 (resolved to a fault-localisation paper, not the "How accurately do LLMs
understand code" title the search returned). The last is the one search hit that did not resolve to
the paper it advertised.
