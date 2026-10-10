# Responsible NLP answers

Prepared October 10, 2026 for the current manuscript. Labels paraphrase the
[official questions](https://aclrollingreview.org/responsibleNLPresearch/); enter the
answers in the live form after author review. Use section titles below if appendix letters
change when formatting the paper.

| Item | Answer and evidence |
| --- | --- |
| A1 Limitations | Yes. Limitations follows Section 5; covers synthetic traces, model scope, probe interpretation and mixed-feature interventions. |
| A2 Potential risks | No separate societal-risk discussion. This is a diagnostic study, without personal records or a deployed system. Limitations bounds generalization; the implications concern trace reliability within the tested formats. Compute is reported in Reproducibility and model terms. |
| B Artifacts | Yes. Generated Python tasks, pretrained models, CRUXEval functions, probes and scientific software. |
| B1 Attribution | Yes. Kudo et al. in Sections 1–2, CRUXEval in Scope checks, and model/software creators in Reproducibility and model terms. |
| B2 Terms | Yes for existing artifacts. Reproducibility and model terms names the Llama/CodeLlama Community Licenses, Gemma Terms, Apache 2.0 and CRUXEval MIT license. Model weights are not redistributed. A distribution license for our research code/data has not been assigned; no such release is included in this package. |
| B3 Intended use | Yes, with scope. Research inference and synthetic-task scope are described in Reproducibility and model terms and Limitations; model weights retain their original access terms. |
| B4 Identifying content | Not applicable to personal-data processing. Synthetic tasks contain digits, generated identifiers and Python statements. The CRUXEval subset comprises program snippets rather than participant records; no human records are collected. |
| B5 Documentation | Yes. Section 2 and Task levels and identifiers describe task families, English identifiers, naming contrasts and generation. Demonstration formats gives output examples. |
| B6 Data sizes and splits | Yes. Reproducibility and model terms gives 1,000 matched problems per target, three demonstration sets and the independent replication size; Probe and patching details and Independent probe layer selection document computation-disjoint training/evaluation. |
| C Experiments | Yes. |
| C1 Compute | Yes. Model sizes, hardware and the shared allocation upper bound are in Reproducibility and model terms. |
| C2 Setup and selection | Yes. Section 2, Probe and patching details, Independent probe layer selection and Independent replication with screened names describe the recipe, independent layer selection, screening and fresh tests. Identifier meanings discloses the original gate deviation. |
| C3 Statistics | Yes. Section 2 and Effect and equivalence checks define confidence levels, clustered demonstration repeats and the sign rule. Main Table 1 conditions on actual incorrect writes; Figure 2 separates this cohort from the independent-name behavioral replication. |
| C4 Software | Yes. Reproducibility and model terms gives package citations and installed versions, including PyTorch 2.11.0/CUDA 12.9 and Transformers 5.14.1. |
| D Human participants | No. D1–D5 are not applicable; all experiments evaluate models or execute generated/benchmark programs. |
| E AI assistants | Yes. |
| E1 Disclosure | Claude/Claude Code and OpenAI Codex assisted with experiment and analysis code, job orchestration, and manuscript drafting/editing. Results come from executable scripts; automated checks compare executable values, disjoint computations, generated prefixes, raw outputs, summaries and manuscript quantities. The human authors retain responsibility for the final content and must review this disclosure before submission. |
