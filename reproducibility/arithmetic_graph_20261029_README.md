# Arithmetic dependency and relationship overnight addition

The [current plan](../reports/binding/arithmetic_graph_overnight_20261029_plan_v3.md)
and [live status](../reports/binding/arithmetic_graph_overnight_20261029_status_v3.md)
describe the October29–30 discovery run. Source-only coverage is recorded in the
[readiness report](../reports/binding/arithmetic_graph_source_readiness_v1.md).
These additions do not alter earlier scientific results or open sealed outcomes.

Revision1 stopped on six sibling-helper test import errors. Revision2 exposed
three existing guard tests whose fixture requires an unfrozen checkout.
Revision3 verifies every source/config byte against its frozen manifest, then
runs the unchanged tests against that source mirror. The scientific source
cohort, labels, model revisions and readout recipe are unchanged. The earlier
failed records remain available; neither failed revision released a model
collector. The original supervisors and morning jobs were canceled when
superseded; unrelated training jobs were preserved.

The compressed-artifact catalog adds the identical4,608-row source cohort for
each revision and every completed native prepared-case bank available at export.
The source catalog adds all three immutable code/config snapshots. The latest
incremental export proof is
[arithmetic_graph_publication_20261029_v3.json](arithmetic_graph_publication_20261029_v3.json);
earlier incremental proofs retain their original bytes. All gzip inputs were
round-trip SHA256 checked, and frozen source archives were checked member by
member. Source and metadata were scanned for credential markers before export.

Restore the added inputs using the existing utility:

```bash
python scripts/export_binding_repository.py restore --match arithmetic_graph
python scripts/export_binding_repository.py restore-sources --match e71af09e675ea7a66cf5c8f1
tar -xzf reproducibility/arithmetic_graph_regression_sources_20261029_v3.tar.gz
```

The last archive contains the exact regression tests and their code/config
support mirrors for all three revisions. The scientific worker source/config
identity for revision3 is snapshot`e71af09e675ea7a66cf5c8f1`, code SHA256
`b2078f7b46daabe6a67e4f4b311b606b8a3ab0fc690eb6604c195915af3fbb9b`.
Cluster paths and cached checkpoints follow the existing project environment.

Inspect current execution without starting another suite:

```bash
PYTHONPATH=src python scripts/170_binding_arithmetic_graph_suite.py status \
  configs/binding/arithmetic_graph_20261029_v3/suite.json
```

Future captures, generated answers and readouts are logged automatically in their
run folders and the existing experiment journal. This publication is a checkpoint
of the submitted run; it does not claim that future outputs are already in Git.
Raw activation and fitted-score arrays remain local under the existing export
policy. No new model queries or fits were performed by publication.
