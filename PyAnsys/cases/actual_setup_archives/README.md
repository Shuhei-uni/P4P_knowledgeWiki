# Actual Setup Archives

This directory stores machine-exported Fluent setup bundles.

Purpose:
- keep an exact-or-near-exact archive of what was actually saved in Fluent;
- separate raw exported setup state from the human-written setup reports;
- give the rebuild scripts a stable reference bundle when a setup report and a live case differ.

Recommended pattern:
- one subdirectory per archived setup;
- use the setup-report number in the folder name when there is a matching report;
- keep the export raw and additive rather than hand-editing it later.

Expected bundle contents:
- `README.md`: quick human summary of the exported setup
- `metadata.json`: source paths, capture time, and archive label
- `settings_snapshot.json`: PyFluent-reachable settings tree
- `scheme_snapshot.json`: Scheme-side runtime values
- `notes.txt`: capture gaps and API misses

Example naming:
- `07-pure-phase-split-actual-area-live-fff-1-2`
- `00a-purnanto-live-baseline-5000`

Relationship to the main wiki:
- `Setups/` remains the human-authored, report-facing setup lineage.
- `PyAnsys/cases/actual_setup_archives/` holds the machine-exported source of truth for what Fluent actually contained.
