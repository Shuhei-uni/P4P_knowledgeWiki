---
name: cfd-wiki
description: "Use the CFD wiki for model rationale, literature comparisons, assumptions, reusable Fluent guidance, source ingest and wiki health. Retrieve existing knowledge before researching transferable CFD questions externally."
---

# CFD Wiki

Use `CFD_wiki/` as the reusable evidence and method library: paper reconstruction, generic Fluent click paths, solver/model patterns, and cross-paper synthesis. Its **boundary** is reusable knowledge.

- Keep selected experiment questions, findings, and claim limits in `Project/`.
- Keep executable implementation, inspection, and generated machine evidence in `PyAnsys/`.
- A project-specific result may enter this wiki only as a clearly labelled reusable lesson; retain a link to its owning project record.

Never edit `CFD_wiki/raw/`.

Before changing the wiki, read `CFD_wiki/AGENTS.md`, then the maintained catalog at `CFD_wiki/wiki/index.md`. The local guide owns page schemas, citation style, uncertainty labels, and the full ingest procedure; do not duplicate or replace it here.

For a decision-support lookup, read [focused lookup
delegation](../references/focused-lookup.md). Run each applicable lookup branch
in its own focused subagent. For **Evidence lookup**, ask one reusable-CFD
question and name the reported fact, contradiction, or limitation that could
matter. For **Fluent guidance**, ask one generic procedure/model-use question
and name the prerequisite, restriction, recommendation, or uncertainty that
could matter. Each subagent returns the compact evidence packet; the parent
agent synthesizes it with the other applicable research paths. An explicit
wiki update remains in the owning agent because it changes durable knowledge.

## Choose the branch

Classify the request before opening source material:

| Request concerns | Take this branch |
| --- | --- |
| Explaining physics, comparing models/papers, or challenging a reusable assumption | **Knowledge Q&A** |
| Where a paper reports a method, model, parameter, validation result, or limitation | **Evidence lookup** |
| How to carry out a reusable action in Fluent, or how to improve generic Fluent guidance | **Fluent guidance** |
| Adding, correcting, connecting, or synthesising transferable CFD knowledge | **Wiki update** |
| Discoverability, broken links, source availability, or stale/contradictory knowledge | **Wiki health** |
| A selected experiment's decision, result, setup lineage, or a runnable PyAnsys change | Route to `Project/` or `PyAnsys/`; use this skill only if a separate reusable lesson is needed |

## Evidence lookup

For a paper, model, mesh, validation, separator, annular-flow, DPM, EWF, steam-purity, carryover, ORC, or geofluid-property question:

1. Read `CFD_wiki/paper_lookup/index.md` and search the lookup/catalogue with `rg`.
2. Open only the relevant broad or geothermal lookup chunk, then the smallest relevant maintained page: `wiki/sources/`, `wiki/setups/`, `wiki/concepts/`, `wiki/entities/`, or `wiki/synthesis/`.
3. If precision matters, use those pointers to inspect only the needed raw-paper or guide pages/sections. The lookup accelerates navigation; it never replaces the primary source.
4. State source-backed facts with their page/section citation, and label every non-verbatim conclusion `Reported`, `Inferred`, `Assumed`, `Missing Info`, or `Not Applicable`, as applicable.

Completion criterion: the answer identifies the supporting source location and clearly distinguishes source evidence from inference or an unresolved gap.

## Knowledge Q&A

1. Use the question routes in `CFD_wiki/wiki/index.md`. Search unfamiliar wording
   with `python CFD_wiki/tools/wiki.py search "<question terms>" --json` from the
   repository root, or use `rg` for exact terms.
2. Read the closest physics/concept or synthesis page and its supporting source
   records. When comparing studies, name differences in geometry, fluid system,
   models and validation that constrain transfer.
3. Follow source-page pointers for critical values or a disputed claim. If the
   original is unavailable, state that the maintained extraction is the evidence
   used and preserve the unresolved verification gap.
4. Answer the question first, then provide evidence locations, material
   disagreements, missing information and the implication for the user's question.
   Keep reported findings, inference and assumptions distinguishable.
5. Apply the local guide's query writeback rule if the answer adds reusable
   knowledge; otherwise keep the answer in chat.

Completion criterion: the answer uses relevant existing knowledge, names its
evidence and transfer limits, and identifies what remains unanswered. A search
excerpt alone is not evidence review.

## Wiki health

1. Run `python CFD_wiki/tools/wiki.py health --json`. Inspect broken file links,
   uncatalogued pages, absent content backlinks and unavailable source references.
2. Repair navigation against actual files. Add backlinks only where the relation
   is useful. Original source availability is a separate gap from broken wiki links.
3. For scientific health, choose a concrete topic or conflicting claim, compare
   its maintained pages and inspect the primary evidence. Follow the local guide's
   lint rules; structural checks cannot certify citation quality or scientific truth.
4. Correct the owning page, related links and catalog/log, then rerun the checks.

Completion criterion: repaired items are verified; unresolved source-access or
scientific gaps are reported explicitly. Health checks never fill missing facts
with unsupported values.

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
