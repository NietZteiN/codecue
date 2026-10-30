# Post-run old/current response diagnostics

Independent discovery-only review of the saved outputs. Strict whole-response ASCII integer scores, all 48 primary cells across both models, saved native request identity and historical/current AST truth reconcile exactly with the immutable publication. This report changes no parser, score, gate, instruction or cohort.

| Model | Responses | Correct | Accuracy | Invalid | Length-limited | Invalid EOS/stop |
|---|---:|---:|---:|---:|---:|---:|
| llama8b | 20,160 | 12,272 | 60.87% | 0 | 0 | 0 |
| codellama34b | 20,160 | 4,739 | 23.51% | 9,864 | 166 | 9,698 |

Both models fail all 24 fixed reliability cells. Failed behavior is preserved as a completed measurement.

## CodeLlama formatting and stopping

| Instruction | Question | Correct / n | Invalid | Assignment wrapper | Fenced integer | Other invalid | Length-limited |
|---|---|---:|---:|---:|---:|---:|---:|
| old_value_execute_v1 | current | 448/3,360 | 2,754 | 2,734 | 4 | 16 | 16 |
| old_value_execute_v1 | previous | 655/3,360 | 1,948 | 1,863 | 0 | 85 | 85 |
| old_value_history_v1 | current | 1,191/3,360 | 1,085 | 793 | 280 | 12 | 3 |
| old_value_history_v1 | previous | 1,090/3,360 | 9 | 5 | 4 | 0 | 0 |
| old_value_output_v1 | current | 446/3,360 | 2,748 | 2,739 | 0 | 9 | 9 |
| old_value_output_v1 | previous | 909/3,360 | 1,320 | 1,263 | 3 | 54 | 53 |

CodeLlama emits 9,397 complete `name = integer` responses and 291 fenced integers. These violate the fixed integer-only response contract. 9,698 invalid outputs stop before the token ceiling; 166 total outputs reach the 16-token limit. Length truncation therefore cannot explain most invalid responses. The saved `finish_reason` distinguishes stop from length; it does not save the engine’s more specific stop reason. The EOS-last-token counts in the JSON provide direct token evidence without inventing a stop reason.

The same model/tokenizer revisions, official BOS/INST boundary, EOS 2, assistant `Output:` prefill, strict scorer, 16-token ceiling and backend source were used in the prior computation calibration. All 20,160 current CodeLlama prompts have the reviewed wrapper and saved input IDs equal preparation. This pass finds no identity, oracle, context, scoring or boundary regression in those saved artifacts. It cannot independently reproduce inference or prove that alternative wording/token limits would help. No alternative parser is evaluated.

## Llama current-value intrusion on historical questions

These rows include only different old/current values. “Other question” means the exact current value on a previous-value question, or the exact previous value on a current-value question. Correct, other-question, other wrong and invalid categories partition each row.

| Instruction | Question | Distinct-value n | Correct | Answered other question | Other wrong | Invalid |
|---|---|---:|---:|---:|---:|---:|
| old_value_execute_v1 | current | 2,424 | 2,069 | 189 | 166 | 0 |
| old_value_execute_v1 | previous | 2,424 | 884 | 979 | 561 | 0 |
| old_value_history_v1 | current | 2,424 | 1,829 | 346 | 249 | 0 |
| old_value_history_v1 | previous | 2,424 | 1,039 | 751 | 634 | 0 |
| old_value_output_v1 | current | 2,424 | 2,005 | 206 | 213 | 0 |
| old_value_output_v1 | previous | 2,424 | 936 | 847 | 641 | 0 |

Storage-separated totals retain the absent-from-all-current-slots versus retained-in-another-current-slot distinction:

| Question | Old numeric value | n | Correct | Answered other question | Other wrong |
|---|---|---:|---:|---:|---:|
| current | absent_all_current | 4,824 | 3,765 | 560 | 499 |
| current | retained_other_current | 2,448 | 2,138 | 181 | 129 |
| previous | absent_all_current | 4,824 | 1,737 | 1,947 | 1,140 |
| previous | retained_other_current | 2,448 | 1,122 | 630 | 696 |

## Limited saved examples

| Model / category | Question | Previous / current / expected | Raw response (JSON escaped) | Finish |
|---|---|---|---|---|
| llama8b: valid_wrong_other_question_integer | previous | -7 / 4 / -7 | `" 4"` | stop |
| codellama34b: invalid_assignment_integer | current | -7 / 4 / 4 | `"\nitem_0 = 4"` | stop |
| codellama34b: invalid_fenced_integer | previous | 8 / 2 / 8 | `"\n```\n2\n```"` | stop |
| codellama34b: invalid_other | previous | 11 / -6 / 11 | `"\nitem_0 = 11\nitem_1 = -6\n"` | length |
| codellama34b: valid_wrong_other_question_integer | current | -7 / 4 / 4 | `"\n-7"` | stop |

## Scope and next decisions

Output format failures and wrong integer answers are observed model behavior under the fixed protocol. Input IDs, scores and task truth reconcile, so this evidence does not identify an implementation defect requiring a change to the completed study. The small set of length-limited continuations remains separately visible.

Current-value intrusions show which numeric answer the model returned; they do not identify a neural mechanism. Full source history remains visible, old/current equality controls are separate, and dependent numeric/lexical/rotation views are not independent structural replications. These adaptive TRAIN/DEV observations cannot establish retained latent state, causal use, or held-out generalization. No confidence interval, best-instruction selection, intervention or automatic model rerun follows this diagnostic.

Any longer-generation or formatting study would require a separately pinned discovery protocol retaining these failed gates. The independent morning check remains the next scheduled review.

Reproduction: run the adjacent artifact helper with the pinned project Python. It streams saved JSONL, checks all input SHA pins again after analysis, and atomically verifies identical output bytes on a second execution. No tokenizer/model load, model query, fit or array file read is used.
