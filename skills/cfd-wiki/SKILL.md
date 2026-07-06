---
name: cfd-wiki
description: "Use when working with CFD_wiki reusable CFD knowledge: searching literature lookup chunks, answering Fluent how-to/setup questions, extracting paper evidence, updating CFD source/setup/guidance/concept/entity/synthesis pages, or deciding what generic CFD knowledge belongs outside the project wiki."
---

# CFD Wiki

## Core Rule

Use `CFD_wiki/` for reusable CFD reconstruction knowledge, paper extraction, Fluent setup guidance, solver/model patterns, and cross-paper synthesis. Do not store project run decisions, setup lineage, or PyAnsys implementation detail here unless the point is to extract a reusable CFD lesson.

Before editing, read:

1. `AGENTS.md` at the repository root for cross-system routing.
2. `CFD_wiki/AGENTS.md` for the local schema and citation rules.
3. `CFD_wiki/wiki/index.md` for the maintained page catalog.

Never edit anything under `CFD_wiki/raw/`.

## Search Workflow

For paper, model, mesh, validation, separator, annular-flow, DPM, EWF, steam-purity, carryover, ORC, or geofluid-property questions:

1. Read `CFD_wiki/paper_lookup/index.md`.
2. Open only the relevant chunk under `CFD_wiki/paper_lookup/broad/` or `CFD_wiki/paper_lookup/geothermal/`.
3. Use the lookup to choose source pages under `CFD_wiki/wiki/sources/`, setup pages under `CFD_wiki/wiki/setups/`, or synthesis pages under `CFD_wiki/wiki/synthesis/`.
4. Inspect raw papers or guide PDFs only at pinpointed pages/sections when source precision matters.
5. Answer or update pages with citations and uncertainty labels: `Reported`, `Inferred`, `Assumed`, `Missing`, or `Not Applicable`.

Use `rg` first when searching:

```bash
rg -n "term|alternate term" CFD_wiki/wiki CFD_wiki/paper_lookup
```

## Fluent Guidance Workflow

For "how do I do this in Fluent" requests:

1. Read `CFD_wiki/wiki/guidance/index.md`.
2. Open the relevant guidance page, especially `CFD_wiki/wiki/guidance/fluent-general-click-by-click.md` for broad GUI navigation.
3. Pull case-specific numbers from `CFD_wiki/wiki/setups/`, `ResearchProject_wiki/`, or `Setup report/` only after the generic click path is established.
4. Keep guidance pages procedural and GUI-first. Do not put project-specific numerical defaults in reusable guidance pages.

## Update Workflow

When adding reusable CFD knowledge:

1. Choose the smallest existing page that fits: `sources/`, `setups/`, `guidance/`, `concepts/`, `entities/`, or `synthesis/`.
2. Use the extraction schema and page style in `CFD_wiki/AGENTS.md`.
3. Preserve units and citations for every setup-critical value.
4. Add `Missing Info`, `Assumptions`, risk labels, confidence, and sensitivity tests when data is incomplete.
5. Link related pages bidirectionally with relation tags such as `supports`, `extends`, `contradicts`, `replaces`, or `reuses`.
6. Update `CFD_wiki/wiki/index.md`.
7. Append one parseable entry to `CFD_wiki/wiki/log.md`.

If the result affects the geothermal separator project specifically, add only a short linked impact summary in `ResearchProject_wiki/` rather than duplicating the CFD page.
