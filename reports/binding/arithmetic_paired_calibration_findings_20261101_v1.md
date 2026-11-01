# Paired timing/overwrite/query-scope calibration

Discovery calibration only; formal-cohort inference remains unscheduled. All wording variants are retained. No best wording is selected from DEV or calibration. Accuracy includes every invalid/truncated response in its denominator. Finite template/seed cases are correlated and are not confirmation evidence.

| Model | Protocol | Scope | Cases | Joint accuracy | Per-slot accuracy | Invalid/truncated |
|---|---|---|---:|---:|---:|---:|
| meta-llama/Llama-3.1-8B-Instruct | output_only | single | 216 | 53.24% | 53.24% | 4 |
| meta-llama/Llama-3.1-8B-Instruct | output_only | all | 216 | 31.94% | 51.74% | 80 |
| meta-llama/Llama-3.1-8B-Instruct | intermediate_query | single | 216 | 0.00% | 0.00% | 216 |
| meta-llama/Llama-3.1-8B-Instruct | intermediate_query | all | 216 | 0.00% | 0.00% | 216 |
| meta-llama/Llama-3.1-8B-Instruct | stepwise | single | 216 | 46.30% | 46.30% | 104 |
| meta-llama/Llama-3.1-8B-Instruct | stepwise | all | 216 | 72.22% | 77.66% | 43 |
| codellama/CodeLlama-34b-Instruct-hf | output_only | single | 216 | 33.33% | 33.33% | 0 |
| codellama/CodeLlama-34b-Instruct-hf | output_only | all | 216 | 29.63% | 61.34% | 51 |
| codellama/CodeLlama-34b-Instruct-hf | intermediate_query | single | 216 | 25.00% | 25.00% | 108 |
| codellama/CodeLlama-34b-Instruct-hf | intermediate_query | all | 216 | 0.46% | 0.46% | 215 |
| codellama/CodeLlama-34b-Instruct-hf | stepwise | single | 216 | 72.69% | 72.69% | 43 |
| codellama/CodeLlama-34b-Instruct-hf | stepwise | all | 216 | 81.02% | 90.39% | 13 |

## Frozen output-only competence gates

Each scope and instruction must separately pass literal ≥95%, copy ≥90%, and one-hop arithmetic ≥70% joint accuracy on depth-zero calibration cases. These are feasibility thresholds, not significance tests. Stepwise and intermediate-query protocols remain separate diagnostics.

| Model | Scope | Task | Instruction | Cases | Accuracy | Required | Pass |
|---|---|---|---:|---:|---:|---:|---|
| meta-llama/Llama-3.1-8B-Instruct | single | literal | 0 | 6 | 100.00% | 95% | True |
| meta-llama/Llama-3.1-8B-Instruct | single | literal | 1 | 6 | 100.00% | 95% | True |
| meta-llama/Llama-3.1-8B-Instruct | single | literal | 2 | 6 | 100.00% | 95% | True |
| meta-llama/Llama-3.1-8B-Instruct | single | copy | 0 | 6 | 33.33% | 90% | False |
| meta-llama/Llama-3.1-8B-Instruct | single | copy | 1 | 6 | 66.67% | 90% | False |
| meta-llama/Llama-3.1-8B-Instruct | single | copy | 2 | 6 | 33.33% | 90% | False |
| meta-llama/Llama-3.1-8B-Instruct | single | arithmetic | 0 | 12 | 50.00% | 70% | False |
| meta-llama/Llama-3.1-8B-Instruct | single | arithmetic | 1 | 12 | 75.00% | 70% | True |
| meta-llama/Llama-3.1-8B-Instruct | single | arithmetic | 2 | 12 | 66.67% | 70% | False |
| meta-llama/Llama-3.1-8B-Instruct | all | literal | 0 | 6 | 100.00% | 95% | True |
| meta-llama/Llama-3.1-8B-Instruct | all | literal | 1 | 6 | 0.00% | 95% | False |
| meta-llama/Llama-3.1-8B-Instruct | all | literal | 2 | 6 | 100.00% | 95% | True |
| meta-llama/Llama-3.1-8B-Instruct | all | copy | 0 | 6 | 100.00% | 90% | True |
| meta-llama/Llama-3.1-8B-Instruct | all | copy | 1 | 6 | 0.00% | 90% | False |
| meta-llama/Llama-3.1-8B-Instruct | all | copy | 2 | 6 | 100.00% | 90% | True |
| meta-llama/Llama-3.1-8B-Instruct | all | arithmetic | 0 | 12 | 83.33% | 70% | True |
| meta-llama/Llama-3.1-8B-Instruct | all | arithmetic | 1 | 12 | 0.00% | 70% | False |
| meta-llama/Llama-3.1-8B-Instruct | all | arithmetic | 2 | 12 | 75.00% | 70% | True |
| codellama/CodeLlama-34b-Instruct-hf | single | literal | 0 | 6 | 83.33% | 95% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | literal | 1 | 6 | 66.67% | 95% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | literal | 2 | 6 | 83.33% | 95% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | copy | 0 | 6 | 83.33% | 90% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | copy | 1 | 6 | 83.33% | 90% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | copy | 2 | 6 | 83.33% | 90% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | arithmetic | 0 | 12 | 16.67% | 70% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | arithmetic | 1 | 12 | 25.00% | 70% | False |
| codellama/CodeLlama-34b-Instruct-hf | single | arithmetic | 2 | 12 | 16.67% | 70% | False |
| codellama/CodeLlama-34b-Instruct-hf | all | literal | 0 | 6 | 100.00% | 95% | True |
| codellama/CodeLlama-34b-Instruct-hf | all | literal | 1 | 6 | 66.67% | 95% | False |
| codellama/CodeLlama-34b-Instruct-hf | all | literal | 2 | 6 | 100.00% | 95% | True |
| codellama/CodeLlama-34b-Instruct-hf | all | copy | 0 | 6 | 50.00% | 90% | False |
| codellama/CodeLlama-34b-Instruct-hf | all | copy | 1 | 6 | 0.00% | 90% | False |
| codellama/CodeLlama-34b-Instruct-hf | all | copy | 2 | 6 | 50.00% | 90% | False |
| codellama/CodeLlama-34b-Instruct-hf | all | arithmetic | 0 | 12 | 41.67% | 70% | False |
| codellama/CodeLlama-34b-Instruct-hf | all | arithmetic | 1 | 12 | 8.33% | 70% | False |
| codellama/CodeLlama-34b-Instruct-hf | all | arithmetic | 2 | 12 | 16.67% | 70% | False |

Passing calibration alone does not validate global readouts or causal use. Any protocol revision retains this pilot and must be frozen before formal collection. Pre-trace generation boundaries are not pre-answer states for stepwise/intermediate protocols. No gold intermediate is teacher-forced. Native RHS/newline collapse and value visibility remain explicit in preflight records.
