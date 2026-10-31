# Scratch-backed numeric exploration

The original immutable artifact paths for the October31 numeric wave remain valid on the execution workspace. Cache `.npy` files link to checksum-verified copies under `/scratch/juno/jvl210002/codecue/arithmetic_numeric_exploration/20261031_v1/caches/`. Six worker directories link to the corresponding `workers/` subdirectories. The original saved prefixes remain in `saved_work_prefix`; they are historical duplicates and are excluded from publication.

The [recovery report](../reports/binding/arithmetic_numeric_storage_recovery_20261031_v1.md) and its linked machine-readable reviews record the quota failure, file hashes, preserved fit banks and reviewed scheduler retries. The scientific source snapshot remains `8c1bda5687b078517a933459`; these are storage and receipt repairs.

Git cannot store files beneath a directory link. Immutable worker JSON is therefore published as lossless gzip under `reproducibility/compressed/artifacts/binding/arithmetic_numeric_exploration/20261031_v1/`. The existing `compressed_artifacts.csv` records original paths, sizes and both hashes; the publisher verifies decompression before adding an entry. Raw parameters, activations and prediction arrays remain local and are inventoried. Symlinks and mutable run state are not published.

On a fresh checkout, restore the scientific text to ordinary artifact directories with the existing restoration tool:

```bash
python scripts/export_binding_repository.py restore --match arithmetic_numeric_exploration/20261031_v1
```

The live workspace already has those original paths through its scratch links. The restoration tool deliberately refuses to traverse directory links or overwrite differing files. Source and regression archives use the existing frozen-source catalog and the separate `arithmetic_numeric_exploration_regression_20261031_v1.tar.gz` archive.
