# Repository guide

This repository connects reusable CFD knowledge, geothermal-separator project records, ordered simulation setups, and PyFluent automation without conflating their roles.

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
