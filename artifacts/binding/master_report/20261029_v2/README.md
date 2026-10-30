# Master report, October 29, 2026

Current user entry point: reports/binding/MASTER_REPORT.md.

The published Markdown and HTML editions are reports/binding/master_research_report_v2.md and master_research_report_v2.html. HTML embeds every PNG and the complete original dependvar.txt. External report/artifact links resolve within the project workspace.

To reproduce without model calls or fits:

    /work/jvl210002/migration/envs/probe-cu129/bin/python artifacts/binding/master_report/20261029_v2/reproduce_master_report_v2_frozen_catalog.py

The reproduction helper fixes CSV field ordering after JSON snapshot reload, regenerates deterministic figures/documents, checks byte equality with the published outputs, and preserves publication_review_v1.json. build_master_report.py records the initial build and is retained unchanged. input_snapshot/ freezes the source reports and plan for this edition; archive_snapshot_v1.json fixes the report index at publication time. The v1 draft is superseded after a milestone-connector correction; its figures and files remain labeled historical.

For a future update, create a new versioned edition, refresh its source snapshots and template deliberately, validate local links/anchors/embedded figures and scientific claims, reproduce identical bytes, then update MASTER_REPORT.md and the README links. Do not mutate original experiment outputs, retired figures or frozen science sources. The document is a dated evidence synthesis, not a live stream of scheduler state.

The frozen-catalog helper preserves this edition’s figure list even after later conceptual figures are added. The earlier helper remains archived.
