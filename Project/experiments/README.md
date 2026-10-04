# Project experiments

## Presentation

| Record | Main content |
| --- | --- |
| `CONTEXT.md` | Tables for current status, question, authority, scope, evidence, candidate contrasts, and decision conditions. |
| `setup.md` | Tables for exact parent, controlled changes, fixed settings, run plan, required evidence, and claim limits. |
| `results.md` | A short answer/status table, selected figures, comparison tables, limitations, and next action. |
| Index, interpretation, and other records | Navigation or comparison tables; figures where useful. |

| Writing rule | Requirement |
| --- | --- |
| Prose | Omit introductions, narrative recaps, and sentences that repeat a table or figure. Do not move whole paragraphs into table cells. |
| Rows | One fact, setting, comparison, or decision per row. Use short phrases, clear units, and meaningful column labels. |
| Figures | Embed existing valid figures beside the relevant comparison. Keep a short caption for source/window and at most two short interpretation sentences. Do not repeat plotted values in prose. |
| Scientific meaning | Retain provenance, exact parent identity, formulas/sign conventions, authority, uncertainty, and claim limits in tables or captions. Separate observation from interpretation. |
| Evidence gaps | State the missing evidence and its effect in a table. Do not invent a figure or a stronger conclusion. |
| Chronology | Keep the current decision visible. Use Git and linked machine artifacts for detailed history. |
| Raw evidence | Leave every `raw/` directory unchanged. |

The retained Project experiment record is grouped by scientific phase. The
phase folders contain executed evidence, including failed, rejected,
non-converged, partial, and inconclusive runs. Setup-only plans and scaffolds
that never produced a solve or substantive executed observation were removed;
their exact history remains recoverable from Git.

- [Phase 1 — Purnanto baseline and inlet exploration](phase-01-purnanto-baseline-and-inlet-exploration/index.md)
- [Phase 2 — parity reset and pre-V2 qualification](phase-02-parity-reset-and-pre-v2-qualification/index.md)
- [Phase 3 — DPM carryover and coupling](phase-03-dpm-carryover-and-coupling/index.md)
- [Phase 4 — EWF wall-film mechanisms](phase-04-ewf-wall-film-mechanisms/index.md)
- [Phase 5 — Full Geometry V2](phase-05-full-geometry-v2/index.md)
- [Phase 6 — Full Geometry with Brine Pool](phase-06-full-geometry-with-brine-pool/index.md)
- [Phase 7 — Simplified Purnanto Liquid-Removal Mechanisms (Shuhei)](phase-07a-simplified-purnanto-liquid-removal/index.md)
- [Phase 7b — Full-Geometry Steady Liquid Removal (Andy)](phase-07b-full-geometry-liquid-removal/index.md)
- [Phase 8 — Storyline reconstruction on the new mesh (Shuhei)](phase-08-storyline-reconstruction/index.md)
- [Legacy reconstruction](legacy/legacy-bangma-reconstruction/historical-run.md)
- [Historical parallel studies from Andy's checkout](parallel-andy-studies/README.md) — enthalpy/DPM replication, liquid-sink diagnostics and resolved-outlet VOF evidence, with explicit identities and recovery provenance.

Each retained experiment keeps its historical descriptive folder name and
internal stage structure. Its setup, results, observations, figures, and
uncertainty labels remain with that experiment; raw Fluent/PyAnsys artifacts
remain with their owning system and are linked where available.

For an active phase being framed or developed, maintain one phase-root
`CONTEXT.md`. It is the current human-approved planning authority: the phase
question, human thinking, approved candidate experiments, decision gates, and
conditional qualification paths. It is not an append-only chat log. Do not
retroactively add one to closed historical phases unless they are actively
reopened. `setup.md` remains the precise runnable contract for a selected
experiment.
