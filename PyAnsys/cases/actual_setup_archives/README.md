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

Relationship to the current records:
- `Project/experiments/` owns the human-authored setup contracts and scientific
  interpretation.
- `PyAnsys/cases/actual_setup_archives/` holds small machine-exported evidence
  for what Fluent actually contained.
- Keep an archive only when it preserves unique live readback that cannot be
  reconstructed from Project records or Git history. Do not use this directory
  as a second setup tree.
