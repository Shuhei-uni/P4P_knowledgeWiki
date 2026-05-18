# Work Log

## [2026-04-22] progress-update | Initialise progress-tracking structure
- files created/updated: `AGENTS.md`, `wiki/index.md`, `wiki/log.md`, `wiki/project/objective-and-scope.md`, `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`, `wiki/technical/sources/purnanto-etal-2013.md`, `wiki/literature/matrix.md`, `wiki/model/baseline-cfd.md`, `wiki/model/inlet-regimes.md`, `wiki/model/validation.md`, `wiki/gaps/open-questions.md`
- reason: enforce separation of project scope vs technical CFD detail and start explicit progress tracking.
- assumptions introduced/removed: introduced assumption that current active technical baseline is the Bangma-based two-phase recreation run.
- next action: execute convergence debugging runs and log each run using the experiment schema.

## [2026-04-22] progress-update | Shift focus to result interpretation and KPI-driven iteration
- files created/updated: `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/gaps/open-questions.md`, `wiki/log.md`
- reason: user reported progress in model setup but uncertainty in interpreting CFD outputs and selecting next model-improvement actions.
- assumptions introduced/removed: introduced assumption that a fixed KPI and post-processing template is required before further A/B changes can be judged reliably.
- current status: baseline setup exists; interpretation framework is now the immediate blocker alongside convergence stability.
- blockers: unclear decision metrics for pressure/phase/flow outputs; no fixed mapping from visualization to parameter-change decisions.
- next action: define run-level KPI set and evaluate each run against the same contour/probe/outlet metrics before choosing the next setting change.

## [2026-04-30] query | Clarify Mixture vs Eulerian upgrade path for tangential-inlet report
- files created/updated: `../Setup report/tangential input setup report.md`, `wiki/model/baseline-cfd.md`, `wiki/log.md`
- purpose: document that the source paper selected `Mixture` for the baseline separator case while acknowledging `Eulerian` may be more accurate, then add a project-specific accuracy-upgrade sequence.
- assumptions introduced/removed: introduced project recommendation that `Eulerian` should be tested only after baseline parity, local mesh refinement, and improved inlet realism are established.
- next immediate action: run a controlled baseline `Mixture` case, then perform one-at-a-time sensitivity tests for mesh and inlet realism before any `Eulerian` comparison.

## [2026-04-30] model-update | Define two-zone split-inlet as next realism upgrade
- files created/updated: `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/index.md`, `wiki/log.md`
- purpose: record the next inlet-regime test as a geometry/mesh-level split of the inlet into wall-side liquid and inner-side steam while preserving the baseline solver stack for A/B comparison.
- assumptions introduced/removed: introduced first-pass assumption that the inlet can be split into equal-area outer and inner halves with pure-phase assignment; flagged geometry naming inconsistency and inlet-orientation definition as active blockers.
- current status: split-inlet implementation route is defined, but orientation confirmation is still required before the case build.
- blockers: inconsistent tangential/spiral naming and ambiguous `left/right` wording for actual inlet-face orientation.
- next action: confirm active geometry and side mapping, then split the inlet face, remesh, and run the first controlled comparison.

## [2026-04-30] model-update | Confirm spiral-inlet geometry for split-inlet plan
- files created/updated: `../Setup report/split two-phase inlet setup report.md`, `wiki/model/inlet-regimes.md`, `wiki/progress/current-status.md`, `wiki/progress/blockers.md`, `wiki/log.md`
- purpose: remove the tangential-versus-spiral ambiguity from the split-inlet planning notes after user clarification that the active geometry is the spiral inlet.
- assumptions introduced/removed: removed the geometry-type ambiguity; retained only the remaining orientation ambiguity for outer-wall versus inner-side inlet mapping.
- current status: geometry type is now fixed as spiral inlet; the remaining setup question is exact side mapping on the inlet face.
- blockers: inlet-face side mapping is still unresolved.
- next action: identify the outer-wall half and inner/core half on the actual spiral-inlet face, then split the boundary accordingly.

## [2026-05-06] query | Record mesh-quality implication from CFD synthesis
- files created/updated: `wiki/model/baseline-cfd.md`, `wiki/gaps/open-questions.md`, `wiki/index.md`, `wiki/log.md`
- purpose: add a project-facing note that the current minimum orthogonal quality of 6.73e-2 requires mesh auditing and independence checks before report-quality conclusions.
- assumptions introduced/removed: introduced an `Inferred` project interpretation that the quality value is a warning trigger rather than automatic case rejection.
- next immediate action: locate worst cells, classify whether they are in critical inlet/swirl/outlet regions, then run a controlled mesh refinement comparison.

## [2026-05-06] model-update | Update active mesh scale to 1.8M nodes
- files created/updated: `wiki/progress/current-status.md`, `wiki/model/baseline-cfd.md`, `wiki/gaps/open-questions.md`, `wiki/technical/sources/purnanto-etal-2013.md`, `wiki/log.md`
- purpose: replace the outdated approximately 300k-node active-mesh interpretation with the user-reported approximately 1.8M-node mesh.
- assumptions introduced/removed: retired the assumption that global mesh density is the primary deficiency; retained local mesh quality and worst-cell location as active risks.
- next immediate action: inspect worst-quality cell locations and repair/refine critical regions before using the mesh for report-quality conclusions.

## [2026-05-06] query | Add inflation note to mesh-quality decision
- files created/updated: `wiki/model/baseline-cfd.md`, `wiki/log.md`
- purpose: record that inlet/outlet worst-cell quality should be treated as a local sizing/geometry/inflation interaction rather than a global node-count issue.
- assumptions introduced/removed: introduced an `Inferred` caution that inflation layers can worsen quality if they collapse near sharp inlet/outlet transitions.
- next immediate action: inspect whether worst cells are ordinary tetra/sliver cells or collapsed inflation layers before choosing the next mesh repair.
