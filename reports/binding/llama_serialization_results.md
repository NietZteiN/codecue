# Llama CRUXEval completion-interface follow-up

This follow-up was motivated by the observed chat-wrapper program echoes. It keeps the checkpoint, released question content, greedy BF16 decoding, token ceilings and literal-only scorers fixed. Only the completion boundary changes. Existing native-chat results are preserved.

| Model | Task | Native correct | Completion correct | Native parseable | Completion parseable |
|---|---|---:|---:|---:|---:|
| llama31_8b | cruxeval_o_direct | 21/800 | 305/800 | 28 | 786 |
| llama31_8b | cruxeval_o_cot | 48/800 | 364/800 | 89 | 785 |
| llama32_3b | cruxeval_o_direct | 0/800 | 239/800 | 0 | 781 |
| llama32_3b | cruxeval_o_cot | 18/800 | 262/800 | 30 | 752 |

The JSON artifact retains both scoring methods, paired correctness overlap and program-echo counts. A gain after fixing output format does not measure an equivalent gain in underlying reasoning. No downloaded programs or model outputs were executed. These remain literal-equality baselines, not official sampled execution pass@k. No generated final outcomes were opened.
