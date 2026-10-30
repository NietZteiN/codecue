# October30 morning review and matched prompt control

The [decision record](../reports/binding/arithmetic_graph_morning_decision_v1.md)
links the replay audit, corrected TRAIN/DEV figure and all prompt-control arms.

The independent replay used snapshot`74dd76244e87ac0b062ab285` and applied the
existing36 probe banks to165,888 rows. Reconstructed training inputs matched their
saved hashes, numerical differences were zero, and all decisions matched.
It performed no new fits or language-model calls. The91-test proof is preserved
with the audit. Figure/table publicationv2 corrects presentation only and links
the unchanged raw review and its original source identity.

The matched prompt control used snapshot`5d321f96dcdb4555d85e61b7`. Its70-test
proof and both native preparations passed. All2,304 original baseline prompt/token
identities matched exactly; ordinary Python independently verified the printed
query values. The control generated11,520 new answers and reused2,304 cached
baseline answers. All six arms and invalid rates remain available. No old score,
parser, causal gate or sealed evaluation was changed.

[Incremental publication evidence](arithmetic_morning_publication_20261030_v1.json)
contains source archives, losslessly compressed input/response checksums, and
the list of directly published metadata. Gzip payloads and frozen archive members
were round-trip verified; text inputs were credential-scanned.

```bash
python scripts/export_binding_repository.py restore --match arithmetic_prompt_control
python scripts/export_binding_repository.py restore-sources --match 74dd76244e87ac0b062ab285
python scripts/export_binding_repository.py restore-sources --match 5d321f96dcdb4555d85e61b7
```

The original arithmetic corpus/baseline response banks are restored through the
existing arithmetic-graph catalog entries. Raw captured vectors and fitted arrays
remain local under the existing publication policy. Cluster paths and cached
checkpoint setup follow the project environment.

The next scientific step is a reliable shorter arithmetic calibration under
explicit printed queries, followed by position-aware decoding controls. Neither
the old nor new findings qualify causal interventions or untouched forecasting.
