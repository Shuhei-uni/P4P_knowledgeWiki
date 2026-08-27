---
name: cfd-wiki
description: Search or update reusable CFD, Fluent, separator, and literature knowledge in CFD_wiki.
---

# CFD wiki

Use `CFD_wiki/` for reusable CFD knowledge, literature evidence, generic Fluent
method guidance, setup reconstruction, and cross-case/cross-paper synthesis.

Do not store project experiment state, project findings, or PyAnsys
implementation history here.

## Find evidence

Search narrowly from the relevant CFD_wiki lookup/index and open only the pages
needed for the question. Inspect raw papers or PDFs only when source precision
requires it. Preserve citations, units, and evidence labels such as:

```text
Reported | Inferred | Assumed | Missing | Not Applicable
```

Follow `CFD_wiki/AGENTS.md` when editing content.

## Update knowledge

Edit the smallest existing page that owns the reusable idea. Link project
consequences from `Project/` instead of duplicating them here. Leave the
internal `CFD_wiki/` structure alone unless a concrete routing problem requires
a minimal edit; the Project/PyAnsys restructure is not a CFD wiki redesign.
