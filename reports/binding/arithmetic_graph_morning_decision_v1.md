# October30 decision after the overnight review

The08:00 Chicago audit completed without scheduler errors. The subsequent independent CPU audit reconstructed every saved training feature/target/weight hash and replayed165,888 readout rows across36 banks. Numerical scores matched exactly; all decisions matched. There were no new fits or language-model calls in that audit.

| Model | TRAIN whole graph | DEV whole graph | DEV individual parents | TRAIN prior on DEV |
|---|---:|---:|---:|---:|
| llama8b | 99.99% | 0.00% | 24.34% | 25.69% |
| codellama34b | 100.00% | 0.00% | 29.39% | 25.69% |

The problem is a large generalization gap under these global readouts, not missing jobs or a numerical replay error. Individual-parent results are also near the prior, so strict whole-graph scoring is not the sole explanation. This does not establish absence of encoded dependencies. Low numeric-value accuracy also persists on classes represented in TRAIN.

The new matched semantics control reused the original baseline answers and collected11,520 fresh responses. Under original instructionI0:

| Model | Literal bare → printed | Arithmetic bare → printed |
|---|---|---|
| llama8b | 44.44% → 95.83% | 10.19% → 11.11% |
| codellama34b | 50.00% → 97.22% | 10.19% → 11.57% |

Printing changes both syntax and token context. The result supports an interface effect on literal reporting, but does not rescue arithmetic. All three instructions and invalid rates remain reported; Llama is particularly sensitive to instructionI2. These are adaptive discovery controls on familiar program families, not independent confirmation.

Next work is a discovery calibration with explicit printed queries and one/two arithmetic updates, retaining instruction controls and grouped structural splits. In parallel, prepare position-aware source baselines and operand-local readouts. A separately declared archived-layer sweep may diagnose accessibility, but must preserve the nominated-layer negative result and cannot establish causal use. No causal patches or unfamiliar-program forecasts are warranted yet.

[Replay review](arithmetic_graph_morning_review_v2.md) · [TRAIN/DEV figure](figures/arithmetic_graph_train_dev_review_v2.png) · [Prompt-control findings](arithmetic_prompt_control_findings_v1.md) · [Prompt-control figure](figures/arithmetic_prompt_control_v1.png)
