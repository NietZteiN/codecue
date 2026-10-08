# Rebuilding the main figures

Run from the repository root after sourcing `scripts/env.sh`, using the probe Python
environment. These scripts use existing data and run on the CPU; they do not load models.

- `python scripts/70_idea_figure.py`: observed program, full assignment outputs and
  final answers. `idea_data.json` records the exact selected program and generations.
- `python scripts/84_story_figure.py`: error-conditioned correct-digit readouts and the
  independent screened-name replication. Its panels use separate cohorts.
- `python scripts/71_mechanism_figure.py`: the appendix's detailed layer curves.

Then run `make paper-submission`. Main figure titles state findings; each figure explains
its task, comparison, measure and interval convention. Keep internal predictor accuracy
separate from the model's written answers. Keep patch removal separate from recovery of
correct answers. Use percentage points for added errors and percentages for accuracy.
