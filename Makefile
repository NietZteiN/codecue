# Everything here is safe on the login node (8 GB virtual-memory cap); GPU stages go through sbatch.
PY ?= /work/jvl210002/migration/envs/probe-cu129/bin/python
export PYTHONPATH := $(CURDIR)/src

.PHONY: test data check
check: test
	@echo OK
test:
	$(PY) -m pytest tests/ -q
## every level's neutral probe-train set and matched test sets (CPU, seconds)
data:
	$(PY) scripts/10_build_dataset.py

TECTONIC ?= /work/jvl210002/migration/envs/tex/bin/tectonic
.PHONY: paper numbers
## build paper/main.pdf and print the body page count against the 4-page limit
paper:
	@$(MAKE) -C paper TECTONIC="$(TECTONIC)" PY="$(PY)" paper

.PHONY: paper-check paper-submission
paper-check:
	@$(MAKE) -C paper PY="$(PY)" check

paper-submission:
	@$(MAKE) -C paper TECTONIC="$(TECTONIC)" PY="$(PY)" submission

## list every number still unfilled in the draft
numbers:
	@sed 's/%.*//' paper/main.tex | grep -o '\\NUM{[^}]*}' | sort | uniq -c | sort -rn
