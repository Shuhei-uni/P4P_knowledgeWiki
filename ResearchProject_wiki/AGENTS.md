# AGENTS.md

## Mission
This repository is a personal final-year research wiki for:
**Geothermal steam-water separator design CFD modelling and optimisation**.

The wiki must do four jobs in parallel:
- keep a clear and stable project scope,
- preserve high-detail technical CFD reconstruction knowledge,
- track day-to-day project progress,
- support report writing with traceable evidence.

Primary users are Shuhei Yokkaichi and Andy Tran, plus future-self during modelling, validation, and writing.

## Project Objective Source of Truth
Use `raw/Shuhei Report.docx` as the main source for:
- research aim,
- objectives,
- scope boundaries,
- literature framing and research gap.

Current baseline objective from that report:
- Improve an existing CFD model of a **vertical BOC separator**.
- Replace uniform/idealised inlet assumptions with more realistic two-phase inlet regimes.
- Evaluate effects on internal flow behaviour, separation efficiency, and pressure-drop tradeoffs.

## Core Literature Baseline
Treat `raw/Zarrouk and Purnanto 2014.pdf` as a foundational design reference for:
- separator typologies and design context,
- sizing and efficiency framing,
- practical design tradeoffs,
- CFD relevance in geothermal separators.

Treat `CFD_wiki/raw/informit.366967552564856.pdf` as the key baseline reconstruction source for reproducing older Fluent setup details.

## Working Principles
- Preserve source truth: never modify files in `raw/`.
- Prefer reproducibility over presentation polish.
- Separate `Reported` facts from `Inferred` results and `Assumed` defaults.
- Never hide missing information or uncertainty.
- Keep all setup-critical claims citation-backed.
- Record failures and non-converged runs; do not log only successful runs.

## Repository Contract
- `raw/`: immutable source materials.
- `wiki/`: maintained project knowledge base.
- `template/`: reusable markdown templates.
- `AGENTS.md`: operational protocol (this file).

## Cross-System Boundaries
- `ResearchProject_wiki` owns project interpretation, run progress, technical notes, and human-readable V&V sign-off.
- `CFD_wiki` owns reusable CFD methods, literature extraction, and generic Fluent guidance.
- `Setups/` owns concrete setup-branch identity, ordered lineage, and report-facing setup snapshots.
- `PyAnsys/` owns executable automation, machine-readable validation targets, and claim-gate logic.

Do not duplicate full setup lineage in this wiki. Link to `Setups/` and summarize only what the project needs to remember.

## Knowledge Separation Architecture (Mandatory)
To avoid data dilution, separate information into dedicated layers.

### A. Scope Layer (`wiki/project/`)
Use for project intent and boundaries only:
- objectives,
- research questions,
- phase/milestone decisions,
- what is in scope vs out of scope.

Do not store deep solver/mesh/debug detail here.

### B. Technical Layer (`wiki/technical/` and `wiki/model/`)
Use for deep implementation detail:
- geometry parameters,
- mesh statistics and quality,
- solver and numerics settings,
- boundary/initial conditions,
- convergence diagnostics,
- failure hypotheses and fixes.

Do not store narrative project-management content here.

### C. Progress Layer (`wiki/progress/`)
Use for execution tracking:
- current status,
- run-by-run experiment log,
- blockers and recovery actions,
- milestone checkpoint status.

### D. Verification And Validation Layer (`wiki/vnv/`)
Use for project-owned verification and validation records:
- claim policy and claim classes;
- machine-target interpretation and target selection notes;
- numerical verification reports;
- external validation reports;
- final human sign-off of allowable claim strength.

Do not use this layer for generic CFD method explanations that belong in `CFD_wiki`, and do not use it as a replacement for setup-branch lineage in `Setups/`.

### E. Literature Layer (`wiki/sources/`, `wiki/literature/`, `wiki/synthesis/`)
Use for source extraction and cross-paper synthesis.

## Required Wiki Files
Maintain these as the wiki grows:
- `wiki/index.md`
- `wiki/log.md`
- `wiki/project/objective-and-scope.md`
- `wiki/progress/current-status.md`
- `wiki/progress/experiments.md`
- `wiki/progress/blockers.md`
- `wiki/literature/matrix.md`
- `wiki/sources/<source-id>.md`
- `wiki/technical/sources/<source-id>.md`
- `wiki/model/baseline-cfd.md`
- `wiki/model/inlet-regimes.md`
- `wiki/model/validation.md`
- `wiki/vnv/index.md`
- `wiki/vnv/policy.md`
- `wiki/vnv/signoff-log.md`
- `wiki/gaps/open-questions.md`
- `wiki/synthesis/<topic>.md`

## Initial Source IDs
Use consistent IDs:
- `shuhei-report-2026` -> `raw/Shuhei Report.docx`
- `zarrouk-purnanto-2014` -> `raw/Zarrouk and Purnanto 2014.pdf`
- `purnanto-zarrouk-cater-2013` -> `CFD_wiki/raw/informit.366967552564856.pdf`

## Progress Tracking Workflow (Mandatory)
When any modelling work is performed:
1. Update `wiki/progress/current-status.md`.
2. Add one run entry to `wiki/progress/experiments.md`.
3. If blocked, update `wiki/progress/blockers.md` with ranked hypotheses.
4. Link the run to technical pages containing settings and evidence.
5. If the run affects claim strength, update or create the matching record under `wiki/vnv/`.
6. If automation produced machine-readable targets or claim-gate outputs, link to the relevant `PyAnsys` path from the human-readable V&V record.
7. Append one entry in `wiki/log.md`.

## Experiment Log Schema (Mandatory)
Each run entry in `wiki/progress/experiments.md` must include:
- Run ID and date.
- Objective of the run.
- Geometry variant.
- Mesh stats (node/cell count and notable quality values).
- Physics model assumptions.
- Solver settings (coupling, discretization, URFs, initialization).
- Boundary/initial condition values.
- Iteration or timestep budget.
- Convergence indicators (residuals and physical monitors).
- Outcome (`Converged`, `Partially Converged`, `Diverged`, `Stalled`).
- Hypothesized cause if not converged.
- Next action.

## Ingest Workflow
For each new source:
1. Read fully and identify relevance to design, CFD, inlet regimes, optimisation, or validation.
2. Extract using the Research Extraction Schema.
3. Create or update `wiki/sources/<source-id>.md`.
4. If source is implementation-heavy, also update `wiki/technical/sources/<source-id>.md`.
5. Update `wiki/literature/matrix.md`.
6. Update affected model/synthesis/gap pages.
7. Update index and append log entry.

## Research Extraction Schema (Mandatory)
Capture these fields for each source.

### A. Bibliographic Context
- Full citation.
- Source type (`journal`, `conference`, `report`, `thesis`, `internal note`).
- Domain relevance (design, operation, CFD, optimisation, validation).

### B. Problem and Scope
- Problem statement.
- System boundary.
- Applicability to this project.

### C. Separator Design Knowledge
- Configuration/type.
- Geometry/proportion rules.
- Operating envelope (pressure, enthalpy, flow ranges).
- Efficiency and pressure-drop claims.

### D. Inlet Regime Knowledge
- Regimes discussed.
- Regime-performance relationships.
- Entrainment/re-entrainment mechanisms.

### E. CFD and Numerics
- Multiphase model type.
- Turbulence model and wall treatment.
- Mesh strategy and quality.
- Solver setup and convergence settings.
- Boundary and initialization details.

### F. Validation and Evidence Quality
- Validation targets.
- Agreement quality/error.
- Missing data affecting reproducibility.

### G. Reproducibility Risk
- Missing parameter list.
- Assumptions with rationale.
- Risk label (`Low`, `Medium`, `High`).
- Confidence rating (`High`, `Medium`, `Low`).

### H. Project Integration
- Impact on baseline modelling decisions.
- Linked wiki pages.
- Next actions.

## Citation Rules
- Every setup-critical value must include a citation.
- Preferred format: `([source-id], p.<page>)`.
- If from table/figure/equation, state that explicitly.
- Evidence labels:
  - `Reported`
  - `Inferred`
  - `Assumed`

## Missing Information Rules
When source detail is incomplete:
1. Add `Missing Info`.
2. Add `Assumptions` with one-line justification.
3. Add risk label per assumption.
4. Add `Sensitivity Plan` prioritizing high-risk assumptions.

Never present assumptions as reported facts.

## Cross-Source Synthesis Rules
Use relation tags:
- `supports`
- `extends`
- `contradicts`
- `replaces`
- `reuses`
- `gap-for-project`

When relations are found, update both linked pages.

## Query Workflow
When answering project questions:
1. Read `wiki/index.md` first.
2. Read only relevant pages.
3. Prefer cross-source synthesis over single-source claims.
4. Answer with citations and uncertainty labels.
5. Save reusable answers back into wiki and update log.

## Lint Workflow (Wiki Health Check)
Periodically check for:
- uncited technical claims,
- numerical values without units,
- contradictions between project, technical, and progress layers,
- orphan pages with no inbound references,
- stale assumptions not revisited after new evidence,
- blocked experiments with no documented next action.

## Log Format
Use parseable headings in `wiki/log.md`:
`## [YYYY-MM-DD] <operation> | <short-title>`

`<operation>` must be one of:
- `ingest`
- `model-update`
- `progress-update`
- `synthesis`
- `query`
- `lint`
- `refactor`

Each entry must include:
- files created or updated,
- one-line purpose,
- assumptions introduced or retired,
- next immediate action.

## Definition of Done (Per Source)
A source ingest is complete only when:
- source page exists and follows schema,
- implementation-relevant content is added to technical layer,
- matrix and linked pages are updated,
- assumptions and confidence are explicit,
- index and log are updated.

## Definition of Done (Per Modelling Iteration)
A modelling iteration is complete only when:
- run is logged in `wiki/progress/experiments.md`,
- outcome and convergence status are explicit,
- blockers are updated if convergence failed,
- technical settings used in the run are recorded,
- next action is identified.

## Definition of Done (Objective Alignment)
A change is complete only when:
- it maps to at least one project objective,
- inlet-regime representation is documented,
- expected efficiency/pressure-drop effect is stated,
- validation path is identified,
- residual uncertainty and gap are recorded.
