# Repository architecture

## System ownership

- `CFD_wiki/` owns reusable CFD reconstruction knowledge, paper extraction, solver/model patterns, cross-paper synthesis, and generic Fluent guidance.
- `Project/` owns current project-specific scientific truth: the active question, stable assumptions, selected experiments, evidence interpretation, and claim limits.
- `ResearchProject_wiki/` retains the detailed project corpus—progress, blockers, technical notes, and existing V&V records—until each area is deliberately cut over. It is not the default authority for new Project decisions.
- `Setups/` retains concrete case definitions, historical campaign structure, setup lineage, and setup-linked evidence created before the Project experiment cutover.
- `PyAnsys/` owns executable Fluent automation, inspection/rebuild scripts, run orchestration, and machine-readable validation or claim-gate artifacts.

Do not duplicate full pages between systems; link to the owning page and provide only the summary needed by the secondary system.

## Setups architecture

`Setups/` is geometry-first for retained setup/report sources. New selected experiments are co-located under `Project/experiments/`:

- `Project/experiments/` — canonical current selected experiments, with setup and results records together.
- `Setups/full-geometry/` — retained `Full-geomV2` setup programme, organized by physics family and scientific campaign.
- `Setups/purnanto-reference/` — navigation layer for the historical numbered/reference programme.
- `Setups/active/`, `future/`, `past/`, and `reports/` — retained compatibility storage for the numbered corpus and existing cross-links.
- `Setups/templates/` — shared templates.
- `Setups/order-dictionary.md` — historical numbered lineage; not the naming authority for new full-geometry campaigns.

## Top-level map

- [`CFD_wiki/`](../../CFD_wiki/): reusable literature, method, and Fluent-guidance knowledge.
- [`Project/`](../../Project/): current project truth and the selected-experiment contract.
- [`ResearchProject_wiki/`](../../ResearchProject_wiki/): retained project interpretation, progress, technical notes, and `wiki/vnv/` sign-off records.
- [`Setups/`](../../Setups/): retained setup/report sources and historical lineage; do not start new selected experiments here.
- [`PyAnsys/`](../../PyAnsys/): automation code, inspection tools, setup scripts, extracted case knowledge, and machine-readable V&V logic.
- [`PROJECT_TREE.md`](../../PROJECT_TREE.md): orientation tree.
