# Binding-study reproducibility records

The repository publishes the implementation, tests, configurations, reports,
figures, small scientific metadata and losslessly compressed large text artifacts.
No experiment is rerun to publish this snapshot, and original result bytes are
preserved. Start with [the master research report](../docs/binding/MASTER_REPORT.md).

The [numeric-geometry wave](../reports/binding/arithmetic_numeric_geometry_launch_v1.md)
uses frozen source `a154e0ecd0112622590fa080` and the separate
`arithmetic_numeric_geometry_regression_20261031_v1.tar.gz` test/support mirror.
Its immutable scratch-worker metadata uses the same lossless gzip catalog;
as new results are published, restore them with
`python scripts/export_binding_repository.py restore --match arithmetic_numeric_geometry/20261031_v1`.
Large output arrays are created directly on scratch and remain local.

## Stored artifacts

- `compressed_artifacts.csv` maps each original JSON/JSONL/large-text path to its
  `.gz` storage path, original/stored sizes and both SHA-256 digests. This includes
  generated datasets, prepared prompts, saved responses, fitted predictor JSON and
  detailed result tables. Decompression reproduces the original bytes.
- `frozen_sources.json` lists the content-addressed source/configuration archives.
- `local_payload_inventory.csv` records artifacts retained only on the cluster.
- `experiment_log_snapshot/` captures the experiment index without publishing its
  live SQLite database, locks, scheduler controls or event spool.
- `export_review.json` records export coverage and storage totals.

Small metadata keeps its original path under `artifacts/binding/`. Large text is
stored under `compressed/` because some original files exceed GitHub's regular
Git file limit. Source snapshots are under `frozen_sources/`. These encodings do
not change the logical artifact identities recorded in the scientific receipts.

## Restore without model inference

From the repository root, using Python 3.12 or later:

```bash
python scripts/export_binding_repository.py restore --match old_value_overnight
python scripts/export_binding_repository.py restore-sources --match 4206d21342e20115539c3b55
# Omit --match to restore every published text artifact or source snapshot.
```

Restoration verifies checksums, restricts output to `artifacts/binding/`, rejects
symbolic links and traversal, and refuses to overwrite different existing files.
Historical manifests preserve their original cluster paths and environment;
restoring them does not silently rewrite those scientific identities.

## Local payloads

Large activation/score/parameter array payloads (`.npy`, `.npz`), language-model
weights, the installed vLLM runtime and its wheel, downloaded literature, and live
control/database state remain outside normal Git. Their original data and existing
scientific checksums stay on the cluster; the inventory records the excluded paths.
This is a code/results publication, not a full backup of the approximately 70-GB
working artifact tree. Exact numerical parameter replay still requires the listed
local array payloads; the report summaries and large JSON/JSONL evidence are included.

To prepare a future publication snapshot, run `export` on a suitable CPU allocation
and review its manifest before staging. Publication does not enable automatic Git
pushes or modify the scientific reliability gates.
