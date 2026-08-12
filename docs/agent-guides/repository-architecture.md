# Repository architecture

## System ownership

- `CFD_wiki/` owns reusable CFD reconstruction knowledge, paper extraction, solver/model patterns, cross-paper synthesis, and generic Fluent guidance.
- `ResearchProject_wiki/` owns geothermal-separator project decisions, experiment progress, blockers, milestones, report-facing evidence, and project-owned V&V records.
- `Setups/` owns ordered concrete case definitions, parent/child variants, setup lineage, and report-facing setup snapshots.
- `PyAnsys/` owns executable Fluent automation, inspection and rebuild scripts, run orchestration, and machine-readable validation or claim-gate artifacts.

Do not duplicate full pages between systems; link to the owning page and provide only the summary needed by the secondary system.

## Top-level map

- [`CFD_wiki/`](../../CFD_wiki/): reusable literature, method, and Fluent-guidance knowledge.
- [`ResearchProject_wiki/`](../../ResearchProject_wiki/): project interpretation, progress, technical notes, and `wiki/vnv/` sign-off records.
- [`Setups/`](../../Setups/): setup lifecycle, lineage, and concrete case history; [`Setups/order-dictionary.md`](../../Setups/order-dictionary.md) controls report lineage.
- [`PyAnsys/`](../../PyAnsys/): automation code, inspection tools, setup scripts, extracted case knowledge, and machine-readable V&V logic.
- [`PROJECT_TREE.md`](../../PROJECT_TREE.md): orientation tree.
