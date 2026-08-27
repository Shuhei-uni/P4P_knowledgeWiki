# Repository guide

This repository connects reusable CFD knowledge, geothermal-separator project records, ordered simulation setups, and PyFluent automation without conflating their roles.

## Migration safety (#9)

> Repository restructure tracked in #9.
> Once a replacement area is proven, do not create new work in legacy progress/log or mirrored setup/report paths; current authorities remain in use until cutover.
> Do not delete historical content yet.

- For a note move: move through Obsidian → inspect the Git diff → search the old path → fix non-note references explicitly → commit the move batch.
- Treat Obsidian/Wikilinks and Markdown note links separately from Python/YAML/JSON path literals, shell examples, GitHub URLs, and immutable historical artifacts. Do not assume Obsidian updates non-note references.
- Run `python3 scripts/check_stale_paths.py` after a move. It checks active Markdown destinations and reports missing active links, compatibility/archive references, and path-literal cases separately; it is not a migration framework.

The root-vault move check on 2026-08-27 used a disposable Markdown backlink. Obsidian recognised the backlink but did not rewrite the temporary target link after the target moved, so the Git diff and repository search remain required. No `[[Wikilinks]]` were present in the vault.

## Always

- Never edit files in any `raw/` directory.
- Before changing a subsystem, read its local guide: [`CFD_wiki/AGENTS.md`](CFD_wiki/AGENTS.md), [`ResearchProject_wiki/AGENTS.md`](ResearchProject_wiki/AGENTS.md), or [`PyAnsys/AGENTS.md`](PyAnsys/AGENTS.md).
- Keep source citations and uncertainty labels required by the applicable local guide.

## Read the guide for the task

- [Repository architecture](docs/agent-guides/repository-architecture.md) — ownership boundaries and the top-level map.
- [Content routing](docs/agent-guides/content-routing.md) — where to place new knowledge and how to link systems.
- [Setup reports](docs/agent-guides/setup-reports.md) — case definitions, naming, ordering, and lineage.
- [Fluent guidance](docs/agent-guides/fluent-guidance.md) — how-to questions and reusable GUI procedures.
- [Evidence lookup](docs/agent-guides/evidence-lookup.md) — when and how to use the CFD paper lookup layer.
- [Progress reporting](docs/agent-guides/progress-reporting.md) — mandatory handling of progress requests.
- [Wiki change discipline](docs/agent-guides/wiki-change-discipline.md) — scoped, evidence-led edits and completion checks.
- [Delegation](docs/agent-guides/delegation.md) — briefs and main-agent responsibilities for larger cross-system tasks.
