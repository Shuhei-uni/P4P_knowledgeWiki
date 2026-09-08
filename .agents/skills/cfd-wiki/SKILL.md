---
name: cfd-wiki
description: "Route reusable CFD knowledge: locate or extract paper evidence, answer or author generic Fluent guidance, or update CFD_wiki sources, setups, concepts, entities, and synthesis. Use when the task concerns transferable CFD method or evidence rather than a selected Project experiment or PyAnsys automation."
---

# CFD Wiki

Use `CFD_wiki/` as the reusable evidence and method library: paper reconstruction, generic Fluent click paths, solver/model patterns, and cross-paper synthesis. Its **boundary** is reusable knowledge.

- Keep selected experiment questions, findings, and claim limits in `Project/`.
- Keep executable implementation, inspection, and generated machine evidence in `PyAnsys/`.
- A project-specific result may enter this wiki only as a clearly labelled reusable lesson; retain a link to its owning project record.

Never edit `CFD_wiki/raw/`.

Before changing the wiki, read `CFD_wiki/AGENTS.md`, then the maintained catalog at `CFD_wiki/wiki/index.md`. The local guide owns page schemas, citation style, uncertainty labels, and the full ingest procedure; do not duplicate or replace it here.

## Choose the branch

Classify the request before opening source material:

| Request concerns | Take this branch |
| --- | --- |
| Where a paper reports a method, model, parameter, validation result, or limitation | **Evidence lookup** |
| How to carry out a reusable action in Fluent, or how to improve generic Fluent guidance | **Fluent guidance** |
| Adding, correcting, connecting, or synthesising transferable CFD knowledge | **Wiki update** |
| A selected experiment's decision, result, setup lineage, or a runnable PyAnsys change | Route to `Project/` or `PyAnsys/`; use this skill only if a separate reusable lesson is needed |

## Evidence lookup

For a paper, model, mesh, validation, separator, annular-flow, DPM, EWF, steam-purity, carryover, ORC, or geofluid-property question:

1. Read `CFD_wiki/paper_lookup/index.md` and search the lookup/catalogue with `rg`.
2. Open only the relevant broad or geothermal lookup chunk, then the smallest relevant maintained page: `wiki/sources/`, `wiki/setups/`, `wiki/concepts/`, `wiki/entities/`, or `wiki/synthesis/`.
3. If precision matters, use those pointers to inspect only the needed raw-paper or guide pages/sections. The lookup accelerates navigation; it never replaces the primary source.
4. State source-backed facts with their page/section citation, and label every non-verbatim conclusion `Reported`, `Inferred`, `Assumed`, `Missing Info`, or `Not Applicable`, as applicable.

Completion criterion: the answer identifies the supporting source location and clearly distinguishes source evidence from inference or an unresolved gap.

## Fluent guidance

For a generic “how do I do this in Fluent?” request:

1. Read `CFD_wiki/wiki/guidance/index.md`, then the smallest matching guidance page. Start with `fluent-general-click-by-click.md` only when no narrower page applies.
2. Verify uncertain terminology, prerequisites, or GUI paths against the relevant official-guide material or a cited maintained source.
3. Give a GUI-first, reusable click path. Explain critical settings in plain language and keep case-specific numerical values out of generic guidance.
4. When values are necessary, identify their source or route to the owning `Project/` setup record; never promote a project's defaults into generic guidance without transferable evidence.

Completion criterion: the response or updated page supplies a reproducible generic procedure, cites its authority, and does not silently assume a case-specific value.

## Wiki update

When adding or correcting reusable CFD knowledge:

1. Choose the smallest existing destination: `sources/`, `setups/`, `guidance/`, `concepts/`, `entities/`, or `synthesis/`. Create a new page only when no existing page can own the knowledge cleanly.
2. Apply the extraction schema, evidence labels, units, citations, and missing-information rules from `CFD_wiki/AGENTS.md`.
3. Link related pages in both directions with a meaningful relation—`supports`, `extends`, `contradicts`, `replaces`, or `reuses`.
4. Update `CFD_wiki/wiki/index.md` and append the required parseable entry to `CFD_wiki/wiki/log.md`.

Completion criterion: every setup-critical value is cited and unit-bearing, uncertainty is visible, related knowledge is bidirectionally linked, and the maintained catalogue/log expose the change.

## Search pattern

Use `rg` first; it keeps lookup scoped before long documents are opened.

```bash
rg -n "term|alternate term" CFD_wiki/wiki CFD_wiki/paper_lookup
```
