# Native capture preparation: potential prefix reuse

Metadata-only audit of the existing paired native layouts. No model calls or fits. Exact native token-prefix pins and assignment-result label consistency are checked. Reusing a prefix computationally does not merge examples, change family weights or turn shared prefixes into independent evidence. RHS labels describe the assignment result; they do not establish that the write has already occurred internally.

| Model | Formal requested site rows | Unique causal prefixes | Potential reuse factor | Four-layer FP32 requested / unique GiB |
|---|---:|---:|---:|---:|
| llama8b | 165888 | 50688 | 3.27 | 10.12 / 3.09 |
| codellama34b | 165888 | 50688 | 3.27 | 20.25 / 6.19 |

These are output-vector storage estimates, not total storage or GPU-runtime savings. A shared-prefill implementation could capture multiple sites per source; separate-prefix counts do not establish the fastest batching strategy. Generation-prefix rows here cover only formal output-only layouts. Generated-trace answer states remain unimplemented. Before using this plan, compare full-prompt versus truncated-prefix states with matched padding/native tokens and explicit numerical tolerance; retain versioned-label semantics and site masks. Shared TRAIN/DEV prefixes are reported in JSON and do not justify fitting on DEV or weakening structural closure.
