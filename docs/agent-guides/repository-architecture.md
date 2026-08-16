# Repository architecture

## System ownership

- `CFD_wiki/` owns reusable CFD reconstruction knowledge, paper extraction, solver/model patterns, cross-paper synthesis, and generic Fluent guidance.
- `ResearchProject_wiki/` owns geothermal-separator project decisions, experiment progress, blockers, milestones, report-facing evidence, and project-owned V&V records.
- `Setups/` owns concrete case definitions, scientific campaign structure, setup lineage, and setup-linked evidence.
- `PyAnsys/` owns executable Fluent automation, inspection/rebuild scripts, run orchestration, and machine-readable validation or claim-gate artifacts.

Do not duplicate full pages between systems; link to the owning page and provide only the summary needed by the secondary system.

## Setups architecture

`Setups/` is geometry-first for new work:

- `Setups/full-geometry/` — canonical current `Full-geomV2` programme, organized by physics family and scientific campaign.
- `Setups/purnanto-reference/` — navigation layer for the historical numbered/reference programme.
- `Setups/active/`, `future/`, `past/`, and `reports/` — retained compatibility storage for the numbered corpus and existing cross-links.
- `Setups/templates/` — shared templates.
- `Setups/order-dictionary.md` — historical numbered lineage; not the naming authority for new full-geometry campaigns.

## Top-level map

- [`CFD_wiki/`](../../CFD_wiki/): reusable literature, method, and Fluent-guidance knowledge.
- [`ResearchProject_wiki/`](../../ResearchProject_wiki/): project interpretation, progress, technical notes, and `wiki/vnv/` sign-off records.
- [`Setups/`](../../Setups/): concrete experiments; route new work by geometry first.
- [`PyAnsys/`](../../PyAnsys/): automation code, inspection tools, setup scripts, extracted case knowledge, and machine-readable V&V logic.
- [`PROJECT_TREE.md`](../../PROJECT_TREE.md): orientation tree.
