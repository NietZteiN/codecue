# Primary-source review: R5–R9

Reviewed 2026-10-27, America/Chicago, against `dependvar.txt` §13. This is a methodological review, not an exhaustive novelty search or experimental replication. Primary full texts were accessible; the reading scope and transport limitations are recorded in [the source record](../../artifacts/binding/literature/r5_r9_review_v1.json). Mathematical results are reported with their assumptions, without claiming independent proof verification. “Project implication” below identifies our inference rather than a finding about CodeCue established by the cited authors.

## R5 — Interpretive equivalence

Alan Sun and Mariya Toneva, *Tracking Equivalent Mechanistic Interpretations Across Neural Networks*, ICLR 2026. The [official proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/412e7a0143cb33d3a7a9b6abe8d90470-Abstract-Conference.html) confirm the citation. The supplied arXiv record has only [v1, submitted 31 March 2026](https://arxiv.org/abs/2603.30002v1).

**Paper findings.** [Sections 2–6 and Appendix A](https://arxiv.org/html/2603.30002v1) compare interpretations through their implementation families. Congruity samples implementation-preserving interventions and compares representation distances. Calibration uses constructed permutation algorithms; further demonstrations concern IOI across model families and a task reduction involving parts of speech. The theoretical bounds depend on alignment classes, representation quality, implementation metrics and compression. Appendix A explicitly distinguishes equivalence testing from identifying an interpretation.

**Project implication.** Our two-checkpoint results, linear decodability and activation similarities do not implement Congruity or establish a shared algorithm. In particular, cross-network equivalence does not automatically establish equivalence between renamed inputs within one network. This paper supplies a possible framework for the separate explanation-transfer branch; it does not qualify that branch, identify a binding mechanism, or justify launching it from the current evidence.

## R6 — Fidelity under distribution shift

Dan Friedman, Andrew Kyle Lampinen, Lucas Dixon, Danqi Chen and Asma Ghandeharioun, *Interpretability Illusions in the Generalization of Simplified Models*, ICML 2024, PMLR 235:14035–14059; conference dates 21–27 July. [Publisher metadata](https://proceedings.mlr.press/v235/friedman24a.html) match the supplied citation. The publisher-linked [25-page PDF](https://raw.githubusercontent.com/mlresearch/v235/main/assets/friedman24a/friedman24a.pdf) was read after the browser rejected its content type; this was not an established 404.

**Paper findings.** Sections 2–6 and the limitations in §8 evaluate simplified forward models on Dyck languages and character-level code completion. SVD/clustering proxies can fit in-distribution behavior yet miss systematic generalization; hard-attention simplification can also overestimate generalization. The authors restrict their conclusions to the studied models, tasks and component-level simplifications.

**Project implication.** This is not a theorem that our probes fail. It requires checking the predictions of an explanatory simplification against the original model on unfamiliar structures. Strong discovery fits, familiar-template interventions and repeated fold partitions cannot replace that comparison. Matching easy examples does not establish faithful failure forecasts.

## R7 — Probe selectivity and matched controls

John Hewitt and Percy Liang, *Designing and Interpreting Probes with Control Tasks*, EMNLP-IJCNLP 2019, pages 2733–2743, November; the [published PDF](https://aclanthology.org/D19-1275.pdf) gives conference dates 3–7 November. The [Anthology entry](https://aclanthology.org/D19-1275/) verifies the full venue and authors.

**Paper findings.** Sections 2–4 construct random, word-type-consistent control behaviors with the task’s output space. Selectivity compares linguistic and control accuracy. High-capacity probes can memorize controls, and layer rankings based on accuracy alone can change when selectivity is considered. Dropout does not reliably repair the problem; other complexity controls help in the tested settings.

**Project implication.** Our [frequency-matched controls](matched_probe_controls_decision.md) improve the earlier two-label comparator by matching class histograms, head capacity and training procedure while preserving program relatives’ assignments. They support the scoped answer-preparation recovery result. They are program-level controls, not a literal replication of word-type controls, and matching frequencies does not equate task difficulty. High training accuracy with low development control accuracy shows memorization without transfer; it does not show that the probe lacked capacity. Recovery still does not establish online binding maintenance or natural causal use.

## R8 — Intervention success and natural computation

The supplied [arXiv v2](https://arxiv.org/abs/2311.17030v2), revised 6 December 2023 after submission on 28 November, lists Aleksandar Makelov, Georg Lange and Neel Nanda and a NeurIPS workshop. The [ICLR 2024 publication](https://proceedings.iclr.cc/paper_files/paper/2024/hash/70b8505ac79e3e131756f793cd80eb8d-Abstract-Conference.html) additionally lists **Atticus Geiger**. The three-author citation therefore identifies the older preprint, not the complete conference author list. Neither link is a wrong-paper link.

**Paper findings.** In the [conference paper](https://proceedings.iclr.cc/paper_files/paper/2024/file/70b8505ac79e3e131756f793cd80eb8d-Paper-Conference.pdf), §§3–5 explain and test how a correlated but disconnected component can activate a dormant causal pathway. The paper also validates a more faithful IOI direction and recommends checks beyond end-to-end intervention effects (§7).

**Project implication.** Our raw-vector patches differ from the optimized subspace interventions studied here; the paper does not demonstrate that our particular effects are illusory. It does invalidate success-alone reasoning. Donor-answer adoption, an answer-vector positive control, or a norm-matched random comparison cannot by themselves establish selective transport of a naturally used binding. Our [ownership and common-query controls](mechanism_followup_decision.md) remain weak/nonselective and instruction-sensitive; they do not qualify the proposed mechanism.

## R9 — Declared counterfactual alignment

Atticus Geiger, Duligur Ibeling, Amir Zur, Maheep Chaudhary, Sonakshi Chauhan, Jing Huang, Aryaman Arora, Zhengxuan Wu, Noah Goodman, Christopher Potts and Thomas Icard, *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability*, [JMLR 26(83):1–64, 2025](https://www.jmlr.org/papers/v26/23-0058.html). The [published PDF](https://www.jmlr.org/papers/volume26/23-0058/23-0058.pdf) records submission January 2023, revision December 2024 and publication May 2025.

**Paper findings.** Sections 2.3–2.5 define exact/approximate transformations, alignments and interchange interventions. Approximate faithfulness depends on a declared intervention distribution, similarity measure and aggregation statistic. Sections 3.3–3.4 distinguish behavioral descriptions from richer internal causal analyses; §§3.6–3.7 explain why probing or successful steering alone does not establish causal use.

**Project implication.** A binding account needs an explicit variable/version alignment and agreement with independently computed substitutions over its stated intervention family. A whole residual-vector replacement is not automatically a single-binding intervention. Output matches on selected pairs are finite, scoped evidence, not universal abstraction or unique-algorithm identification. Unchanged-variable queries, wrong-version donors and counterfactual descendants remain substantive tests rather than software shams.

## Consequences for the confidence baseline and present claims

The [completed next-token confidence analysis](discovery_confidence_decision.md) adds useful discovery associations, particularly on CodeLlama, with declared source, neutral-query and oracle-access tiers. Its features were collected without target correctness, while the forecasters use correctness as supervised training labels. That distinction must remain explicit. Conditional intervals over saved out-of-fold probabilities do not turn repeated partitions into independent model replications or establish unfamiliar-program performance.

Complete integer-plus-EOS measurements likewise require their own event definition, exact prompt boundary, precision and numerical-parity provenance. Entropy conditional on integers −16…16 describes that finite support; it is not confidence over every possible answer or format. Improved prediction from either confidence family would be a stronger behavioral comparator, not evidence that a binding representation is causally used.

The five papers jointly constrain the interpretation of our measurements without resolving the missing scientific gates. Successful software audits establish implementation consistency within a recorded protocol. Matched probes establish a narrower recovery comparison. Neither supplies selective ownership/version transport, an identified natural computation, or a frozen unfamiliar-program forecast. This review therefore leaves the selective-binding account and final prediction unqualified. It makes no novelty or priority claim, opens no reserved outcomes and initiates no optional extension.
