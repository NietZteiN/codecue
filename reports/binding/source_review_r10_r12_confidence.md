# Primary-source context: interference, unlearning, reviewer criteria and confidence

Checked 2026-10-27 against official arXiv, ACL Anthology, PMLR and ICML pages. Metadata and targeted primary-text methods/results sections were read; this note does not claim a line-by-line review of every appendix. The selected references do not establish exhaustive novelty. R10 and R11 provide context for optional branches, which remain unrun.

## R10: associative interference

Kolling, Vo and Toneva's *Large Language Models as Model Organisms for Human Associative Learning* is arXiv v1, submitted 2025-10-24. Its methods present repeated token pairs in context, then cue the associated token. Representation change uses differences in cosine similarity, with token-pair similarity and broader vocabulary overlap controlled. The reported differentiation patterns depend on both similarity and vocabulary interference. [Metadata](https://arxiv.org/abs/2510.21408), [methods §3 and results §4](https://arxiv.org/html/2510.21408v1).

Our inference: this motivates an interference hypothesis and controls for naming similarity. Cosine geometry is symmetric and the repeated-pair task does not supply directed code dependencies, assignment-version specificity or selective causal repair. Our def-use graphs and controlled program interventions must establish those separately. Our completed confidence association supplies no such mechanism evidence.

## R11: reasoning-trace unlearning

Wang and colleagues' *Reasoning Model Unlearning: Forgetting Traces, Not Just Answers, While Preserving Reasoning Skills* is the official EMNLP 2025 paper, pages 4427–4443, DOI 10.18653/v1/2025.emnlp-main.220. Its main argument distinguishes final-answer suppression from information remaining in reasoning traces. The method combines representation misdirection on a forget set with reasoning-oriented retention supervision; the paper evaluates forgetting and retained utility separately. [Official metadata](https://aclanthology.org/2025.emnlp-main.220/), [primary paper, main methodology and experiments](https://aclanthology.org/2025.emnlp-main.220.pdf).

Our inference: any later unlearning proposal would need trace-level and answer-level evaluation plus retention controls. The current binding study changes inputs and measures fixed pretrained models. It has neither trained an unlearning method nor established a novel unlearning contribution. This source review does not start that optional project.

## R12: reviewer guidance

The official ICML 2026 instructions distinguish technical soundness from significance and discuss originality broadly, including new insight from evaluating existing methods. They also require substantiated comparisons to related research and honest limitations. These are review criteria, not empirical evidence or an acceptance prediction. [Official instructions, Main Track Reviewer Form](https://icml.cc/Conferences/2026/ReviewerInstructions).

Our inference: a carefully bounded empirical insight can be evaluated on its merits, but implementation volume, passing tests or a positive discovery metric do not establish significance. Our strongest current claim remains narrower than the proposed general causal binding account; a selected explanation and untouched prediction test remain unfinished.

## Confidence and calibration overlap

Guo, Pleiss, Sun and Weinberger's *On Calibration of Modern Neural Networks* is ICML 2017, PMLR 70:1321–1330. The paper evaluates calibration and post-processing methods, including validation-fitted temperature scaling while network weights remain fixed. Its multiclass formulation distinguishes a model's maximum softmax confidence from observed correctness. [Official publication](https://proceedings.mlr.press/v70/guo17a.html), [§4–5 and Table 1](https://proceedings.mlr.press/v70/guo17a/guo17a.pdf).

Our inference: scalar confidence and post-hoc calibration have substantial prior art. Our source-plus-confidence logistic prediction is an access-controlled baseline comparison, not a new calibration principle. It must retain proper scores, calibration bins, training-only fitting and a separate final evaluation. Lower discovery log loss alone does not prove that every subgroup is calibrated.

Kadavath and colleagues' *Language Models (Mostly) Know What They Know* is arXiv v4, revised 2022-11-21. It studies model self-evaluation of proposed answers and trained question-level knowledge estimates. The primary text reports useful in-distribution self-evaluation while also describing generalization and out-of-distribution calibration limitations. [Version history](https://arxiv.org/abs/2207.05221), [§4–5, including out-of-distribution tests](https://arxiv.org/html/2207.05221v4).

Our inference: predicting correctness from a model's own signals is not itself novel. Their answer-conditioned questioning and learned knowledge estimates also use different information and training from our four label-free next-token scalars. Our 13-tier comparison keeps source, neutral query, oracle and target-prefill access separate. Its consumed-discovery grouped CV does not substitute for unfamiliar-program validation, and next-token sign/format uncertainty remains distinct from complete numeral-plus-EOS confidence.
