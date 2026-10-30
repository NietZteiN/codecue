# Overnight result-index discovery fix

The periodic experiment reconciler previously skipped standalone `results.json`
and `completion_manifest_v1.json` files. The new arithmetic readouts publish these
names, so their saved results needed explicit discovery support in the central
index. Both names are now recognized, and dictionary-valued source metadata
supplies the saved source hash. Textual program source is not interpreted as a
source identity.

All48 focused logging and scheduler tests passed. Four new cases verify discovery
without manual events, status/config/source/metric recovery, exclusion of sealed
results, and textual-source handling. The full2,315-test scientific source proof
remains attached to immutable snapshote71af09e675ea7a66cf5c8f1. This operational
change affects future periodic index scans, not its frozen model collectors,
cohort, parser, readouts or scientific gates. No completed collection was rerun.

The existing ten-minute scheduler remains enabled. Detailed scores, parameters,
reports and integrity receipts continue to be written in their experiment
folders; the central log now finds standalone result/receipt files as well.
