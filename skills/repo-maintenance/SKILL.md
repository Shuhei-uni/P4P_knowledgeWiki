---
name: repo-maintenance
description: "Use when maintaining the repository itself: cleanup, moving or renaming files, pruning generated outputs, protecting raw sources, repairing indexes/links, and keeping storage use under control without deleting authoritative evidence."
---

# Repository Maintenance

Use this skill for repository housekeeping rather than CFD interpretation or Fluent setup work.

## Core rules

- Treat every `raw/` directory as immutable source material. Do not edit, rewrite, normalize, or delete files there unless the user explicitly asks to replace the source itself.
- Preserve authoritative setup records, result reports, source extractions, and intentional archives. Cleanup should target generated, duplicated, stale, or reproducible artifacts first.
- Before moving or renaming maintained files, search for inbound links and update affected indexes/references in the same change.
- Prefer deleting regenerated clutter over creating another archive of it.

## `PyAnsys/output/`

Treat `PyAnsys/output/` as temporary working/evidence storage, not a permanent data lake.

Keep outputs only when they directly support one of these purposes:

- verification/readback checks;
- post-simulation analysis or a result report;
- plot source data and final plots;
- compact manifests, summaries, or diagnostics needed to reproduce a conclusion;
- a temporary debugging artifact that is still actively needed.

Remove outputs once they are no longer needed, especially:

- repeated live-state snapshots;
- duplicate JSON/CSV exports;
- superseded plots;
- temporary probe or inspection dumps;
- large intermediate field extracts that can be regenerated from the retained case/data source;
- copied case/data files that already have an authoritative Fluent-side or archive location.

When uncertain, keep the smallest artifact that preserves the evidence. Do not delete the only copy of a case/data checkpoint, source document, or result used by a report.

## Cleanup workflow

1. Identify which files are authoritative, derived, temporary, or duplicated.
2. Check whether reports, scripts, or indexes still reference the derived files.
3. Preserve the minimum evidence needed for reproducibility.
4. Delete stale/redundant generated artifacts.
5. Repair links/indexes after moves or removals.
6. Summarize what was retained and why when the cleanup is non-trivial.

## Examples

**PyAnsys analysis cleanup:** keep the final CSV used for a plot, the final PNG, and a small audit JSON; remove ten intermediate snapshots and superseded plot exports after the report is complete.

**Source maintenance:** if a paper in `CFD_wiki/raw/` has incorrect metadata, leave the raw file unchanged and correct the maintained source/extraction page instead.
