# AGENTS.md

## Mission
This repository is a personal CFD reconstruction wiki.
The goal is to convert complex research papers into a simple, reproducible knowledge base for CFD setup.
Primary user is a complete beginner who needs clear, step-by-step guidance to recreate prior work.
Long-term goal is synthesis: connect multiple papers into a network of reusable CFD design knowledge and combine prior approaches into stronger reconstruction playbooks.

## Working Principles
- Preserve source truth: never modify files in `raw/`.
- Prefer reproducibility over elegance.
- Separate `Reported` facts from `Inferred` estimates and `Assumed` defaults.
- Never hide missing information; surface it clearly.
- Explain technical terms in plain language on first use.

## Repository Contract
- `raw/`: immutable source materials (papers, supplements, figures, external notes).
- `wiki/`: maintained knowledge base pages.
- `wiki/guidance/`: reusable click-by-click Fluent operation guidance distilled from documentation and prior reconstructions.
- `template/`: reusable markdown templates.
- `AGENTS.md`: operational schema for agent behavior (this file).

## Required Wiki Files
Maintain these files as the wiki grows:
- `wiki/index.md`: content catalog by category.
- `wiki/log.md`: append-only chronological activity log.
- `wiki/sources/<paper-id>.md`: per-paper extraction record.
- `wiki/setups/<case-id>.md`: actionable CFD reconstruction sheet.
- `wiki/guidance/index.md`: catalog of reusable Fluent click-path guidance pages.
- `wiki/guidance/<guide-id>.md`: GUI-first procedures for repeated setup operations.
- `wiki/concepts/<concept>.md`: concept explainer pages when needed.
- `wiki/entities/<entity>.md`: canonical pages for recurring items (geometry families, turbulence models, solvers, BC types, validation metrics).
- `wiki/synthesis/<topic>.md`: cross-paper comparison and merged guidance pages.

## Network-Building Objective
The wiki must evolve as a connected knowledge graph, not a pile of summaries.
For every ingest, link new findings to existing pages by relation type:
- `supports`: agrees with prior evidence.
- `extends`: adds conditions, ranges, or implementation detail.
- `contradicts`: conflicts with prior claims.
- `replaces`: supersedes older assumptions or defaults.
- `reuses`: repeats a known setup choice in a new context.

When a relation is identified, update both pages so links are bidirectional.

## Ingest Workflow
For each new source:
1. Read the source fully and identify the simulation objective, geometry, physics, and outputs.
2. Extract parameters using the CFD Extraction Schema below.
3. Create or update `wiki/sources/<paper-id>.md`.
4. If source is a case/paper, create or update `wiki/setups/<case-id>.md` with beginner-oriented setup steps.
5. If source is a tool/manual (for example Fluent User's Guide), create or update `wiki/guidance/<guide-id>.md` with click-by-click paths and uncertainty labels.
6. Update or create entity pages for recurring CFD components and explicitly link to prior papers.
7. Update or create concept pages when a concept is new, contradictory, or clarified.
8. If two or more papers overlap on the same design topic, update `wiki/synthesis/<topic>.md`.
9. Update `wiki/index.md`.
10. Append one entry to `wiki/log.md`.

## Fluent Guidance Layer Rules
- Treat `wiki/guidance/` as the first-stop reference for Fluent GUI setup questions.
- Keep guidance pages procedural and click-by-click.
- Distinguish:
  - `Reported`: directly supported by documentation terminology/sections.
  - `Inferred`: practical UI sequence assembled from multiple sections.
- Do not place project-specific numerical defaults in guidance pages; link to `wiki/setups/` for case values.

## CFD Extraction Schema (Mandatory)
Capture all fields below for each case:

### A. Study Scope
- Problem statement and objective.
- Geometry and domain scope (what is in model vs out of model).
- Target outputs used for evaluation.

### B. Physics and Models
- Flow regime assumptions (compressible/incompressible, steady/transient, isothermal/non-isothermal).
- Governing equation set solved.
- Turbulence model and near-wall treatment.
- Multiphase model (if any) and phase definitions.
- Particle model settings (if DPM or equivalent is used).

### C. Material and Operating Conditions
- Fluid properties with units and reference state.
- Operating pressure/temperature/enthalpy ranges.
- Gravity and reference frame settings.

### D. Boundary and Initial Conditions
- Boundary type per boundary (inlet, outlet, wall, symmetry, etc.).
- Numerical values with units and sign conventions.
- Initialization method and initialization values.

### E. Mesh and Numerics
- Mesh type/topology and local refinement strategy.
- Mesh size/count and quality metrics (if provided).
- Solver family and pressure-velocity coupling.
- Spatial discretization schemes per equation.
- Temporal discretization/time-step/CFL (if transient).
- Under-relaxation factors (if provided).
- Convergence criteria (residual thresholds, monitor criteria, stopping rules).

### F. Validation and Results
- Validation target(s) and comparison method.
- Key trends and figures supporting conclusions.
- Reported uncertainty and known limitations.

### G. Reproducibility Risk
- Missing parameter list.
- Assumptions list with rationale.
- Confidence rating: `High`, `Medium`, or `Low`.
- Minimal sensitivity tests to run first.

### H. Cross-Paper Linkage (Mandatory)
- Closest related prior papers and setup pages.
- What matches previous work exactly.
- What differs and why it may differ.
- Whether differences are physical, numerical, or reporting gaps.
- Reuse recommendation: when to copy, adapt, or avoid this setup in future builds.

## Numerical Parameters Policy
Numerical parameters are critical because they can change outcomes even when geometry and physics look identical.
Always capture the full numerical stack, including:
- Solver type and coupling algorithm.
- Discretization choices per variable.
- Initialization strategy.
- Convergence definition (not just "converged").
- Mesh resolution and refinement logic.
- Particle tracking controls (e.g., step limits, injection setup) when applicable.

If any of these are missing, mark them as `Missing` and add an explicit `Assumed` fallback with risk label.

## Missing Information Rules
When a paper is incomplete:
1. Create a `Missing Info` section.
2. Add `Assumptions` with one-line justification each.
3. Label each assumption: `Low Risk`, `Medium Risk`, `High Risk`.
4. Add a `Sensitivity Plan` prioritizing high-risk assumptions first.

Never present assumptions as paper-reported values.

## Citation Rules
- Every setup-critical value must include a citation.
- Prefer citation format: `([source-id], p.<page>)`.
- If extracted from tables/figures, say so explicitly.
- Use labels:
  - `Reported`: directly stated in source.
  - `Inferred`: derived from reported data.
  - `Assumed`: chosen to fill gaps.

## Page Style Rules
- Use units for every numerical value.
- Keep setup instructions step-wise and executable.
- Include a short `Why this matters` note for critical settings.
- Include `Common failure modes` and `Quick diagnostics` in setup pages.

## Query Workflow
When answering questions:
1. Read `wiki/index.md` first.
2. If the question is "how to do this in Fluent", read `wiki/guidance/` pages first.
3. Then read only relevant source/setup/concept pages.
4. Prefer synthesis over single-paper answers whenever multiple sources exist.
5. Answer with citations and uncertainty labels.
6. If the answer is generally useful, save it as a reusable wiki page and update index/log.

## Synthesis Workflow
When there are at least two relevant papers:
1. Build a side-by-side comparison of geometry, physics models, BCs, numerics, and validation quality.
2. Identify stable patterns that consistently work across papers.
3. Identify sensitive choices where outcomes depend on case details.
4. Produce a merged recommendation with `Core defaults` (safe starting point), `When to switch` rules, `Failure signals`, and `Validation checks`.
5. Store this in `wiki/synthesis/<topic>.md` and link all contributing pages.

## Lint Workflow (Wiki Health Check)
Periodically check for:
- Claims without citations.
- Setup pages without units.
- Contradictions across pages.
- Orphan pages with no inbound references.
- Missing concept pages for repeated technical terms.
- Stale assumptions that newer sources can now replace.
- Duplicate concepts/entities with different names that should be merged.
- Synthesis pages that are stale after new ingest.

## Log Format
Use parseable headings in `wiki/log.md`:
`## [YYYY-MM-DD] <operation> | <short-title>`

Where `<operation>` is one of:
- `ingest`
- `query`
- `lint`
- `refactor`

Each entry should include:
- files created/updated
- one-line reason
- notable assumptions introduced or removed

## Definition of Done (Per Source)
A source ingest is complete only when:
- source page exists and is fully extracted
- setup page is actionable for a beginner
- missing info and assumptions are explicit
- confidence rating is assigned
- cross-paper relations are added to existing pages where applicable
- index and log are updated
