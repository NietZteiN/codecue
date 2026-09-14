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
