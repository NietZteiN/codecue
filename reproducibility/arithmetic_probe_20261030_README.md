# October 30 probe-improvement evidence

The [launch record](../reports/binding/arithmetic_probe_improvement_launch_v1.md) links the declared protocols, job IDs and software checks. The new dataset excludes every original arithmetic structure and has216 TRAIN/72 development families plus six one-update calibration families. All outcomes are adaptive discovery. The initial archived-feature workers preserved completed CV but stopped at a reserved filename; recovery uses unchanged mathematics and the original locked selections.

Frozen sources:

- `e6a5d626220a4e24b09d3576`: first archived-feature analysis and its successful2,378-test validation.
- `58d9ed00fe8655447e2f177f`: publication repair, verified CV reuse and the new local capture/behavior/probe DAG.

The [source catalog](frozen_sources.json) records normalized archive SHA256 values. Restore source snapshots with:

```bash
python scripts/export_binding_repository.py restore-sources --match e6a5d626220a4e24b09d3576
python scripts/export_binding_repository.py restore-sources --match 58d9ed00fe8655447e2f177f
```

The complete byte-pinned regression mirrors are preserved separately:

```bash
tar -xzf reproducibility/arithmetic_probe_regression_selection_20261030_v1.tar.gz
tar -xzf reproducibility/arithmetic_probe_regression_local_20261030_v1.tar.gz
```

Restore the new source bank and any published native layouts through the existing lossless text catalog:

```bash
python scripts/export_binding_repository.py restore --match arithmetic_local/20261030_v1
```

Invoke captured entrypoints through script91. The local experiment can be inspected without starting duplicate workers:

```bash
../envs/probe-cu129/bin/python scripts/91_binding_frozen_run.py \
  artifacts/binding/sources/58d9ed00fe8655447e2f177f \
  scripts/180_binding_arithmetic_local_suite.py status \
  configs/binding/arithmetic_local_20261030_v1/suite.json
```

The environment path is relative to the CodeCue checkout on the original cluster; adjust it on another installation. Model/tokenizer loads and scientific workers require SLURM. `submit` is for a fresh run directory; an existing suite uses `watch`/`status`. The source-only setup command is script181, invoked from the live checkout with `PYTHONPATH=src`. It requires the original completed CV banks for its verified recovery manifests and refuses different existing publications.

Raw activation/score/parameter arrays remain local under the repository's existing payload policy; they are hashed in scientific receipts and listed in `local_payload_inventory.csv` as they become available. A clean clone needs those arrays or a separately authorized recapture to rerun archived-feature selection. Publishing source and metadata does not imply that large arrays are in Git.

Script182 incrementally publishes only these run roots, adding source archives and losslessly compressed JSONL without re-exporting older studies. Each invocation requires a new publication edition. Its proof records immutable payload hashes, credential scans and roundtrip checks. Mutable live manifests/progress and experiment-log state are excluded. A publication snapshot may precede completion of queued jobs; later evidence requires another edition.
