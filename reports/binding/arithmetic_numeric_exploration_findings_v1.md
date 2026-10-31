# Compression and numeric-encoding discovery

Fixed-layer, role-specific probes on archived captures. Hyperparameters selected only inside structural TRAIN folds. Existing DEV remains adaptive discovery. Source comparator fits are shared across checkpoints at matching widths. No new language-model calls.

| Model/features | Role | Width | Encoding | DEV exact | DEV MAE | Component balanced accuracy | Shuffled exact | Prior exact |
|---|---|---:|---|---:|---:|---:|---:|---:|
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | scalar | 34.86% | 0.972 | n.a. | 8.40% | 7.91% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | categorical | 99.56% | 0.029 | n.a. | 7.80% | 7.47% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | sign | 99.96% | n.a. | 99.97% | 46.37% | 45.83% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | units | 99.99% | n.a. | 99.99% | 15.51% | 16.60% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | parity | 99.96% | n.a. | 99.96% | 51.59% | 54.48% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | mod5 | 89.65% | n.a. | 89.69% | 21.84% | 20.68% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | mod10 | 95.59% | n.a. | 96.73% | 13.67% | 13.58% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 64 | digits_joint | 99.95% | 0.002 | n.a. | 7.83% | 8.10% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | scalar | 70.24% | 0.420 | n.a. | 8.38% | 7.91% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | categorical | 99.94% | 0.004 | n.a. | 7.58% | 7.47% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | sign | 100.00% | n.a. | 100.00% | 46.44% | 45.83% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | units | 100.00% | n.a. | 100.00% | 15.58% | 16.60% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | parity | 100.00% | n.a. | 100.00% | 52.77% | 54.48% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | mod5 | 99.26% | n.a. | 99.26% | 20.65% | 20.68% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | mod10 | 99.74% | n.a. | 99.81% | 12.95% | 13.58% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 256 | digits_joint | 100.00% | 0.000 | n.a. | 8.11% | 8.10% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | scalar | 93.59% | 0.157 | n.a. | 8.75% | 7.91% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | categorical | 100.00% | 0.000 | n.a. | 7.39% | 7.47% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | sign | 100.00% | n.a. | 100.00% | 46.23% | 45.83% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | units | 100.00% | n.a. | 100.00% | 15.19% | 16.60% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | parity | 100.00% | n.a. | 100.00% | 51.74% | 54.48% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | mod5 | 99.99% | n.a. | 99.99% | 20.09% | 20.68% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | mod10 | 99.99% | n.a. | 100.00% | 12.06% | 13.58% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 1024 | digits_joint | 100.00% | 0.000 | n.a. | 7.69% | 8.10% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | scalar | 98.58% | 0.066 | n.a. | 7.75% | 7.91% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | categorical | 100.00% | 0.000 | n.a. | 7.43% | 7.47% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | sign | 100.00% | n.a. | 100.00% | 46.04% | 45.83% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | magnitude | 100.00% | n.a. | 100.00% | 92.08% | 92.09% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | units | 100.00% | n.a. | 100.00% | 15.13% | 16.60% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | parity | 100.00% | n.a. | 100.00% | 51.76% | 54.48% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | mod5 | 100.00% | n.a. | 100.00% | 20.24% | 20.68% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | mod10 | 100.00% | n.a. | 100.00% | 11.80% | 13.58% |
| meta-llama/Llama-3.1-8B-Instruct | root_definition | 4096 | digits_joint | 100.00% | 0.000 | n.a. | 7.65% | 8.10% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | scalar | 7.11% | 4.830 | n.a. | 7.73% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | categorical | 9.30% | 5.159 | n.a. | 7.29% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | sign | 55.76% | n.a. | 40.30% | 46.03% | 42.57% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | magnitude | 77.74% | n.a. | 34.12% | 77.69% | 77.76% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | units | 15.24% | n.a. | 11.74% | 13.21% | 13.50% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | tens | 87.20% | n.a. | 25.00% | 87.20% | 87.20% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | parity | 54.64% | n.a. | 52.52% | 53.07% | 55.05% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | mod5 | 22.37% | n.a. | 21.84% | 20.91% | 21.85% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | mod10 | 13.46% | n.a. | 12.08% | 11.07% | 13.12% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 64 | digits_joint | 5.48% | 5.043 | n.a. | 4.74% | 5.07% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | scalar | 7.68% | 4.533 | n.a. | 6.53% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | categorical | 10.03% | 4.969 | n.a. | 6.51% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | sign | 62.42% | n.a. | 46.47% | 45.17% | 42.57% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | magnitude | 77.53% | n.a. | 37.46% | 77.20% | 77.76% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | units | 16.20% | n.a. | 12.80% | 13.09% | 13.50% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | tens | 87.11% | n.a. | 25.84% | 87.10% | 87.20% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | parity | 55.63% | n.a. | 54.15% | 51.84% | 55.05% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | mod5 | 22.66% | n.a. | 21.99% | 20.92% | 21.85% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | mod10 | 14.02% | n.a. | 12.58% | 10.90% | 13.12% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 256 | digits_joint | 6.97% | 4.906 | n.a. | 4.41% | 5.07% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | scalar | 8.86% | 4.204 | n.a. | 7.28% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | categorical | 10.74% | 4.758 | n.a. | 6.23% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | sign | 68.01% | n.a. | 52.88% | 45.70% | 42.57% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | magnitude | 77.27% | n.a. | 43.17% | 74.32% | 77.76% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | units | 16.88% | n.a. | 13.55% | 12.46% | 13.50% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | tens | 86.19% | n.a. | 27.26% | 85.30% | 87.20% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | parity | 55.57% | n.a. | 54.60% | 51.46% | 55.05% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | mod5 | 22.90% | n.a. | 22.14% | 21.14% | 21.85% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | mod10 | 14.22% | n.a. | 13.00% | 11.12% | 13.12% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 1024 | digits_joint | 9.32% | 4.683 | n.a. | 4.32% | 5.07% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | scalar | 9.96% | 3.841 | n.a. | 7.06% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | categorical | 12.13% | 4.404 | n.a. | 6.54% | 9.44% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | sign | 69.11% | n.a. | 56.38% | 44.88% | 42.57% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | magnitude | 74.46% | n.a. | 47.44% | 68.26% | 77.76% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | units | 17.91% | n.a. | 13.99% | 12.82% | 13.50% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | tens | 81.21% | n.a. | 29.88% | 75.96% | 87.20% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | parity | 55.65% | n.a. | 54.27% | 51.46% | 55.05% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | mod5 | 23.48% | n.a. | 22.86% | 20.69% | 21.85% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | mod10 | 15.63% | n.a. | 13.93% | 11.12% | 13.12% |
| meta-llama/Llama-3.1-8B-Instruct | computed_definition | 4096 | digits_joint | 10.07% | 4.780 | n.a. | 4.30% | 5.07% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | scalar | 27.58% | 1.191 | n.a. | 8.09% | 7.91% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | categorical | 98.99% | 0.064 | n.a. | 7.72% | 7.47% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | sign | 99.87% | n.a. | 99.86% | 45.76% | 45.83% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | magnitude | 99.99% | n.a. | 99.92% | 92.09% | 92.09% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | units | 99.85% | n.a. | 99.86% | 15.48% | 16.60% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | parity | 99.34% | n.a. | 99.33% | 52.36% | 54.48% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | mod5 | 91.47% | n.a. | 91.38% | 21.60% | 20.68% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | mod10 | 97.04% | n.a. | 97.67% | 13.37% | 13.58% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 64 | digits_joint | 99.73% | 0.008 | n.a. | 7.87% | 8.10% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | scalar | 66.15% | 0.465 | n.a. | 8.49% | 7.91% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | categorical | 99.95% | 0.002 | n.a. | 7.57% | 7.47% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | sign | 100.00% | n.a. | 100.00% | 46.06% | 45.83% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | units | 100.00% | n.a. | 100.00% | 15.64% | 16.60% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | parity | 99.99% | n.a. | 99.99% | 51.51% | 54.48% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | mod5 | 99.63% | n.a. | 99.64% | 20.78% | 20.68% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | mod10 | 99.87% | n.a. | 99.90% | 12.47% | 13.58% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 256 | digits_joint | 100.00% | 0.000 | n.a. | 7.86% | 8.10% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | scalar | 92.43% | 0.167 | n.a. | 8.30% | 7.91% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | categorical | 100.00% | 0.000 | n.a. | 7.59% | 7.47% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | sign | 100.00% | n.a. | 100.00% | 45.99% | 45.83% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | units | 100.00% | n.a. | 100.00% | 15.76% | 16.60% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | parity | 100.00% | n.a. | 100.00% | 51.26% | 54.48% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | mod5 | 99.99% | n.a. | 99.99% | 20.18% | 20.68% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | mod10 | 100.00% | n.a. | 100.00% | 13.28% | 13.58% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 1024 | digits_joint | 100.00% | 0.000 | n.a. | 7.88% | 8.10% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | scalar | 99.31% | 0.044 | n.a. | 7.88% | 7.91% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | categorical | 100.00% | 0.000 | n.a. | 7.43% | 7.47% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | sign | 100.00% | n.a. | 100.00% | 45.76% | 45.83% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | magnitude | 100.00% | n.a. | 100.00% | 92.08% | 92.09% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | units | 100.00% | n.a. | 100.00% | 15.14% | 16.60% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | parity | 100.00% | n.a. | 100.00% | 50.78% | 54.48% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | mod5 | 100.00% | n.a. | 100.00% | 20.44% | 20.68% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | mod10 | 100.00% | n.a. | 100.00% | 12.18% | 13.58% |
| codellama/CodeLlama-34b-Instruct-hf | root_definition | 8192 | digits_joint | 100.00% | 0.000 | n.a. | 7.05% | 8.10% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | scalar | 6.96% | 4.839 | n.a. | 7.69% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | categorical | 8.80% | 5.194 | n.a. | 7.18% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | sign | 55.91% | n.a. | 40.64% | 45.25% | 42.57% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | magnitude | 77.68% | n.a. | 33.91% | 77.66% | 77.76% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | units | 14.93% | n.a. | 11.36% | 13.10% | 13.50% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | tens | 87.21% | n.a. | 25.03% | 87.20% | 87.20% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | parity | 55.13% | n.a. | 52.73% | 53.56% | 55.05% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | mod5 | 21.56% | n.a. | 20.71% | 20.58% | 21.85% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | mod10 | 12.45% | n.a. | 11.16% | 11.14% | 13.12% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 64 | digits_joint | 5.00% | 5.000 | n.a. | 4.60% | 5.07% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | scalar | 8.13% | 4.451 | n.a. | 6.72% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | categorical | 9.41% | 4.946 | n.a. | 6.67% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | sign | 63.80% | n.a. | 47.43% | 44.89% | 42.57% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | magnitude | 77.68% | n.a. | 37.09% | 77.27% | 77.76% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | units | 14.87% | n.a. | 12.20% | 12.53% | 13.50% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | tens | 86.96% | n.a. | 25.29% | 87.13% | 87.20% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | parity | 55.04% | n.a. | 53.51% | 51.80% | 55.05% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | mod5 | 22.09% | n.a. | 21.50% | 19.61% | 21.85% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | mod10 | 13.16% | n.a. | 11.99% | 10.77% | 13.12% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 256 | digits_joint | 6.63% | 4.847 | n.a. | 4.13% | 5.07% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | scalar | 9.40% | 4.009 | n.a. | 6.75% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | categorical | 11.18% | 4.544 | n.a. | 6.82% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | sign | 67.31% | n.a. | 51.93% | 44.63% | 42.57% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | magnitude | 77.12% | n.a. | 42.00% | 74.05% | 77.76% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | units | 15.94% | n.a. | 13.22% | 12.03% | 13.50% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | tens | 86.25% | n.a. | 27.29% | 85.49% | 87.20% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | parity | 55.75% | n.a. | 54.61% | 51.82% | 55.05% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | mod5 | 22.40% | n.a. | 21.78% | 20.28% | 21.85% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | mod10 | 14.25% | n.a. | 13.03% | 10.49% | 13.12% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 1024 | digits_joint | 9.07% | 4.694 | n.a. | 4.20% | 5.07% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | scalar | 11.48% | 3.527 | n.a. | 6.55% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | categorical | 13.13% | 4.223 | n.a. | 6.05% | 9.44% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | sign | 73.37% | n.a. | 56.78% | 45.70% | 42.57% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | magnitude | 68.96% | n.a. | 47.10% | 60.97% | 77.76% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | units | 17.82% | n.a. | 14.41% | 12.84% | 13.50% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | tens | 79.44% | n.a. | 28.97% | 75.14% | 87.20% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | parity | 57.49% | n.a. | 56.02% | 51.39% | 55.05% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | mod5 | 21.98% | n.a. | 21.80% | 20.59% | 21.85% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | mod10 | 15.45% | n.a. | 13.97% | 10.89% | 13.12% |
| codellama/CodeLlama-34b-Instruct-hf | computed_definition | 8192 | digits_joint | 10.64% | 4.202 | n.a. | 4.26% | 5.07% |
| shared model-independent source comparator | root_definition | 64 | scalar | 27.03% | 1.284 | n.a. | 8.05% | 7.91% |
| shared model-independent source comparator | root_definition | 64 | categorical | 97.80% | 0.103 | n.a. | 7.37% | 7.47% |
| shared model-independent source comparator | root_definition | 64 | sign | 96.91% | n.a. | 93.74% | 44.28% | 45.83% |
| shared model-independent source comparator | root_definition | 64 | magnitude | 98.72% | n.a. | 93.73% | 92.09% | 92.09% |
| shared model-independent source comparator | root_definition | 64 | units | 94.07% | n.a. | 93.96% | 15.84% | 16.60% |
| shared model-independent source comparator | root_definition | 64 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| shared model-independent source comparator | root_definition | 64 | parity | 92.92% | n.a. | 92.85% | 51.88% | 54.48% |
| shared model-independent source comparator | root_definition | 64 | mod5 | 93.82% | n.a. | 94.01% | 21.53% | 20.68% |
| shared model-independent source comparator | root_definition | 64 | mod10 | 96.03% | n.a. | 96.26% | 13.46% | 13.58% |
| shared model-independent source comparator | root_definition | 64 | digits_joint | 91.79% | 0.257 | n.a. | 7.60% | 8.10% |
| shared model-independent source comparator | root_definition | 256 | scalar | 100.00% | 0.001 | n.a. | 8.15% | 7.91% |
| shared model-independent source comparator | root_definition | 256 | categorical | 100.00% | 0.000 | n.a. | 7.32% | 7.47% |
| shared model-independent source comparator | root_definition | 256 | sign | 100.00% | n.a. | 100.00% | 45.50% | 45.83% |
| shared model-independent source comparator | root_definition | 256 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| shared model-independent source comparator | root_definition | 256 | units | 100.00% | n.a. | 100.00% | 15.26% | 16.60% |
| shared model-independent source comparator | root_definition | 256 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| shared model-independent source comparator | root_definition | 256 | parity | 100.00% | n.a. | 100.00% | 52.09% | 54.48% |
| shared model-independent source comparator | root_definition | 256 | mod5 | 100.00% | n.a. | 100.00% | 20.89% | 20.68% |
| shared model-independent source comparator | root_definition | 256 | mod10 | 100.00% | n.a. | 100.00% | 13.16% | 13.58% |
| shared model-independent source comparator | root_definition | 256 | digits_joint | 100.00% | 0.000 | n.a. | 7.83% | 8.10% |
| shared model-independent source comparator | root_definition | 1024 | scalar | 100.00% | 0.000 | n.a. | 8.15% | 7.91% |
| shared model-independent source comparator | root_definition | 1024 | categorical | 100.00% | 0.000 | n.a. | 7.79% | 7.47% |
| shared model-independent source comparator | root_definition | 1024 | sign | 100.00% | n.a. | 100.00% | 45.50% | 45.83% |
| shared model-independent source comparator | root_definition | 1024 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| shared model-independent source comparator | root_definition | 1024 | units | 100.00% | n.a. | 100.00% | 15.32% | 16.60% |
| shared model-independent source comparator | root_definition | 1024 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| shared model-independent source comparator | root_definition | 1024 | parity | 100.00% | n.a. | 100.00% | 51.85% | 54.48% |
| shared model-independent source comparator | root_definition | 1024 | mod5 | 100.00% | n.a. | 100.00% | 20.86% | 20.68% |
| shared model-independent source comparator | root_definition | 1024 | mod10 | 100.00% | n.a. | 100.00% | 13.12% | 13.58% |
| shared model-independent source comparator | root_definition | 1024 | digits_joint | 100.00% | 0.000 | n.a. | 7.88% | 8.10% |
| shared model-independent source comparator | root_definition | 4096 | scalar | 100.00% | 0.000 | n.a. | 8.15% | 7.91% |
| shared model-independent source comparator | root_definition | 4096 | categorical | 100.00% | 0.000 | n.a. | 7.63% | 7.47% |
| shared model-independent source comparator | root_definition | 4096 | sign | 100.00% | n.a. | 100.00% | 45.21% | 45.83% |
| shared model-independent source comparator | root_definition | 4096 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| shared model-independent source comparator | root_definition | 4096 | units | 100.00% | n.a. | 100.00% | 15.72% | 16.60% |
| shared model-independent source comparator | root_definition | 4096 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| shared model-independent source comparator | root_definition | 4096 | parity | 100.00% | n.a. | 100.00% | 52.46% | 54.48% |
| shared model-independent source comparator | root_definition | 4096 | mod5 | 100.00% | n.a. | 100.00% | 21.36% | 20.68% |
| shared model-independent source comparator | root_definition | 4096 | mod10 | 100.00% | n.a. | 100.00% | 13.61% | 13.58% |
| shared model-independent source comparator | root_definition | 4096 | digits_joint | 100.00% | 0.000 | n.a. | 7.92% | 8.10% |
| shared model-independent source comparator | root_definition | 8192 | scalar | 100.00% | 0.000 | n.a. | 8.15% | 7.91% |
| shared model-independent source comparator | root_definition | 8192 | categorical | 100.00% | 0.000 | n.a. | 7.56% | 7.47% |
| shared model-independent source comparator | root_definition | 8192 | sign | 100.00% | n.a. | 100.00% | 45.19% | 45.83% |
| shared model-independent source comparator | root_definition | 8192 | magnitude | 100.00% | n.a. | 100.00% | 92.09% | 92.09% |
| shared model-independent source comparator | root_definition | 8192 | units | 100.00% | n.a. | 100.00% | 15.67% | 16.60% |
| shared model-independent source comparator | root_definition | 8192 | tens | 100.00% | n.a. | 100.00% | 100.00% | 100.00% |
| shared model-independent source comparator | root_definition | 8192 | parity | 100.00% | n.a. | 100.00% | 52.48% | 54.48% |
| shared model-independent source comparator | root_definition | 8192 | mod5 | 100.00% | n.a. | 100.00% | 21.42% | 20.68% |
| shared model-independent source comparator | root_definition | 8192 | mod10 | 100.00% | n.a. | 100.00% | 13.56% | 13.58% |
| shared model-independent source comparator | root_definition | 8192 | digits_joint | 100.00% | 0.000 | n.a. | 7.89% | 8.10% |
| shared model-independent source comparator | computed_definition | 64 | scalar | 6.23% | 4.904 | n.a. | 6.99% | 9.44% |
| shared model-independent source comparator | computed_definition | 64 | categorical | 8.80% | 5.017 | n.a. | 8.89% | 9.44% |
| shared model-independent source comparator | computed_definition | 64 | sign | 55.85% | n.a. | 41.49% | 44.55% | 42.57% |
| shared model-independent source comparator | computed_definition | 64 | magnitude | 77.54% | n.a. | 34.72% | 77.10% | 77.76% |
| shared model-independent source comparator | computed_definition | 64 | units | 15.20% | n.a. | 12.16% | 13.37% | 13.50% |
| shared model-independent source comparator | computed_definition | 64 | tens | 87.15% | n.a. | 25.10% | 87.08% | 87.20% |
| shared model-independent source comparator | computed_definition | 64 | parity | 56.31% | n.a. | 55.12% | 53.38% | 55.05% |
| shared model-independent source comparator | computed_definition | 64 | mod5 | 20.86% | n.a. | 20.52% | 20.07% | 21.85% |
| shared model-independent source comparator | computed_definition | 64 | mod10 | 12.59% | n.a. | 11.58% | 10.94% | 13.12% |
| shared model-independent source comparator | computed_definition | 64 | digits_joint | 6.31% | 4.972 | n.a. | 4.11% | 5.07% |
| shared model-independent source comparator | computed_definition | 256 | scalar | 6.43% | 4.872 | n.a. | 7.64% | 9.44% |
| shared model-independent source comparator | computed_definition | 256 | categorical | 8.18% | 5.124 | n.a. | 7.59% | 9.44% |
| shared model-independent source comparator | computed_definition | 256 | sign | 56.28% | n.a. | 41.83% | 44.69% | 42.57% |
| shared model-independent source comparator | computed_definition | 256 | magnitude | 77.01% | n.a. | 35.28% | 76.52% | 77.76% |
| shared model-independent source comparator | computed_definition | 256 | units | 15.26% | n.a. | 12.13% | 13.33% | 13.50% |
| shared model-independent source comparator | computed_definition | 256 | tens | 87.00% | n.a. | 25.35% | 86.65% | 87.20% |
| shared model-independent source comparator | computed_definition | 256 | parity | 56.14% | n.a. | 54.99% | 52.41% | 55.05% |
| shared model-independent source comparator | computed_definition | 256 | mod5 | 20.64% | n.a. | 20.31% | 20.83% | 21.85% |
| shared model-independent source comparator | computed_definition | 256 | mod10 | 12.07% | n.a. | 10.97% | 10.86% | 13.12% |
| shared model-independent source comparator | computed_definition | 256 | digits_joint | 6.07% | 4.933 | n.a. | 4.23% | 5.07% |
| shared model-independent source comparator | computed_definition | 1024 | scalar | 6.75% | 4.920 | n.a. | 6.89% | 9.44% |
| shared model-independent source comparator | computed_definition | 1024 | categorical | 8.53% | 5.220 | n.a. | 6.62% | 9.44% |
| shared model-independent source comparator | computed_definition | 1024 | sign | 55.73% | n.a. | 41.44% | 44.67% | 42.57% |
| shared model-independent source comparator | computed_definition | 1024 | magnitude | 77.03% | n.a. | 35.31% | 76.53% | 77.76% |
| shared model-independent source comparator | computed_definition | 1024 | units | 15.06% | n.a. | 12.29% | 12.64% | 13.50% |
| shared model-independent source comparator | computed_definition | 1024 | tens | 87.01% | n.a. | 25.35% | 86.60% | 87.20% |
| shared model-independent source comparator | computed_definition | 1024 | parity | 55.62% | n.a. | 54.54% | 51.86% | 55.05% |
| shared model-independent source comparator | computed_definition | 1024 | mod5 | 21.24% | n.a. | 20.91% | 20.72% | 21.85% |
| shared model-independent source comparator | computed_definition | 1024 | mod10 | 12.21% | n.a. | 11.39% | 10.74% | 13.12% |
| shared model-independent source comparator | computed_definition | 1024 | digits_joint | 6.22% | 4.982 | n.a. | 4.27% | 5.07% |
| shared model-independent source comparator | computed_definition | 4096 | scalar | 6.66% | 4.938 | n.a. | 6.86% | 9.44% |
| shared model-independent source comparator | computed_definition | 4096 | categorical | 8.71% | 5.278 | n.a. | 6.50% | 9.44% |
| shared model-independent source comparator | computed_definition | 4096 | sign | 55.50% | n.a. | 41.18% | 44.45% | 42.57% |
| shared model-independent source comparator | computed_definition | 4096 | magnitude | 77.03% | n.a. | 35.31% | 76.52% | 77.76% |
| shared model-independent source comparator | computed_definition | 4096 | units | 14.86% | n.a. | 12.23% | 12.46% | 13.50% |
| shared model-independent source comparator | computed_definition | 4096 | tens | 87.01% | n.a. | 25.35% | 86.60% | 87.20% |
| shared model-independent source comparator | computed_definition | 4096 | parity | 55.61% | n.a. | 54.53% | 51.87% | 55.05% |
| shared model-independent source comparator | computed_definition | 4096 | mod5 | 21.66% | n.a. | 21.34% | 20.99% | 21.85% |
| shared model-independent source comparator | computed_definition | 4096 | mod10 | 12.14% | n.a. | 11.28% | 10.82% | 13.12% |
| shared model-independent source comparator | computed_definition | 4096 | digits_joint | 6.32% | 5.008 | n.a. | 4.24% | 5.07% |
| shared model-independent source comparator | computed_definition | 8192 | scalar | 6.64% | 4.943 | n.a. | 6.91% | 9.44% |
| shared model-independent source comparator | computed_definition | 8192 | categorical | 8.74% | 5.273 | n.a. | 6.57% | 9.44% |
| shared model-independent source comparator | computed_definition | 8192 | sign | 55.55% | n.a. | 41.21% | 44.46% | 42.57% |
| shared model-independent source comparator | computed_definition | 8192 | magnitude | 77.03% | n.a. | 35.31% | 76.52% | 77.76% |
| shared model-independent source comparator | computed_definition | 8192 | units | 14.77% | n.a. | 12.22% | 12.50% | 13.50% |
| shared model-independent source comparator | computed_definition | 8192 | tens | 87.02% | n.a. | 25.36% | 86.60% | 87.20% |
| shared model-independent source comparator | computed_definition | 8192 | parity | 55.69% | n.a. | 54.63% | 51.86% | 55.05% |
| shared model-independent source comparator | computed_definition | 8192 | mod5 | 21.51% | n.a. | 21.19% | 20.89% | 21.85% |
| shared model-independent source comparator | computed_definition | 8192 | mod10 | 12.10% | n.a. | 11.31% | 10.85% | 13.12% |
| shared model-independent source comparator | computed_definition | 8192 | digits_joint | 6.30% | 5.019 | n.a. | 4.31% | 5.07% |

Scalar exact accuracy rounds to the nearest integer. Categorical and signed-digit reconstruction retain exact/MAE; invalid signed-digit configurations count as incorrect. Component class support, invalid rates, seeds, alpha choices and decoder parameter counts are retained in machine-readable banks. Calibration never enters fitting. A successful readout may recover source-accessible information or learn a calculation; this study alone does not identify natural causal computation.
