# Project Roadmap

## Purpose
Define the project run sequence from the current state of the separator work. This roadmap now treats `07-pure-phase-split-actual-area.md` as the main complexity-building branch, but it does **not** assume setup `07` is already verified or validated.

The immediate job is:

1. make setup `07` numerically trustworthy enough to use as a baseline candidate;
2. verify it through solution-acceptance and mesh checks;
3. validate it against the strongest available external anchors;
4. only then add new physics or realism one branch at a time.

## Current Starting Point
- Date: `2026-06-11`
- Active setup branch: `../../Setup report/07-pure-phase-split-actual-area.md`
- Branch role: pure liquid / pure steam split-inlet separator branch used as the current baseline candidate for steam-line carryover and separator-flow interpretation.
- Current model-family classification for setup `07`:
  - steady `Mixture` carrier-flow solve;
  - one-way post-convergence `DPM` diagnostic;
  - not a fully coupled `Mixture + DPM` solve;
  - not a wall-film branch;
  - not a transient branch.
- Current status: `07` is **not yet verified** and **not yet validated**.
- `User-specified`: brine-outlet reconstruction and lower-water initialization are no longer active roadmap items for the main project path.
- `User-specified`: brine outlet, water-pool initialization, and related bottom-liquid handling may be revisited only as late-stage exploratory work if time remains after the main branch is complete.

## Scope Decision
- In scope:
  - setup `07` acceptance and cleanup;
  - mesh verification on setup `07`;
  - DPM diagnostic verification on setup `07`;
  - validation/trend comparison using the strongest available anchors;
  - controlled realism increases built from setup `07`.
- Out of scope for the main path:
  - reviving `FFF-2` as the main roadmap driver;
  - brine-outlet optimization;
  - lower-vessel water initialization;
  - interpreting full-vessel liquid inventory closure as the main success criterion for setup `07`.
- `Inferred`: because setup `07` intentionally removes the lower liquid-handling path from the active branch scope, the acceptance gate should focus on whether the steam-path solution is stable and interpretable, not on whether the entire separator liquid inventory is fully represented.

## Operating Rules
1. Do not launch a run unless it has one primary question, one planned comparison, and a written stop condition.
2. Change one major feature at a time: mesh, DPM tracking controls, stochastic/turbulence treatment, coupling, wall fate, wall film, or transient behavior.
3. Do not add higher-realism physics to a weak baseline. First make the simpler branch stable enough to interpret.
4. Do not run mesh verification on a setup that still fails its basic solution-acceptance gate.
5. Save a minimum evidence package for every run:
   - case/data file name,
   - residual history,
   - pressure-drop monitor or equivalent pressure summary,
   - phase mass-flow report at inlet and steam outlet,
   - steam-outlet liquid carryover metric,
   - DPM `escaped`, `trapped`, and `incomplete` counts if DPM is used,
   - short conclusion: `keep`, `reject`, or `needs follow-up`.
6. Keep claim strength explicit:
   - `diagnostic only`,
   - `numerically verified baseline`,
   - `trend supported`,
   - `externally validated`.
7. Brine-outlet and water-initialization work must stay parked unless the main path is already complete enough that extra time can be spent on exploratory side branches.

## Cross-Wiki Method Anchor
- Reusable V&V method authority:
  - `../../CFD_wiki/wiki/synthesis/separator-cfd-verification-and-validation-workflow.md`
- Project-owned V&V report layer:
  - `../vnv/index.md`
- Final project sign-off record:
  - `../vnv/signoff-log.md`
- `Inferred`: this roadmap should name which gate is active for the project branch, while the reusable CFD wiki page remains the method source for verification, validation hierarchy, and uncertainty-retirement logic.

## Baseline Acceptance Gate For Setup 07

### Goal
Before mesh verification or physics escalation, make setup `07` acceptable as a baseline candidate for steam-line carryover interpretation.

### Required Acceptance Checks
1. Inlet phase fluxes match the intended setup `07` targets closely enough to treat the inlet as correctly imposed.
2. Steam-outlet phase fluxes flatten enough to support interpretation.
3. Residuals flatten rather than showing uncontrolled drift.
4. Pressure-drop behavior becomes stable enough to compare across future branches.
5. Steam-outlet liquid carryover monitor becomes stable enough to compare across future branches.
6. Steam-phase imbalance is either reduced to an acceptable level or explicitly bounded and explained.
7. DPM incomplete tracks are not allowed to dominate an efficiency claim without being labeled as a limitation.

### Acceptance Outcome Labels
- `Accepted baseline candidate`:
  - setup `07` is stable enough to enter mesh verification.
- `Diagnostic only`:
  - setup `07` still provides useful trend information, but it is not strong enough for report-facing baseline claims.
- `Rejected baseline`:
  - setup `07` cannot support stable steam-path interpretation and must be repaired before further branching.

## Validation Gate Before Physics Escalation
- Do not escalate complexity until setup `07` has passed:
  - basic solution-acceptance checks;
  - mesh verification at the level needed for the report;
  - at least one external or literature/design comparison gate.
- `Inferred`: a case can be numerically verified before it is externally validated, but it should not become the parent of higher-realism branches if even the numerical baseline is still weak.

## Phase A | Baseline Repair And Acceptance

### Primary Question
Can setup `07` become a trustworthy steady `Mixture` carrier-flow baseline with one-way post-processing `DPM` checks?

### Required Work
- Reconfirm the active interpretation of setup `07`:
  - steam-line carryover branch,
  - not a brine-drainage branch,
  - not a wall-film branch.
- Re-run or record the missing baseline evidence:
  - residual history,
  - pressure-drop trend,
  - phase fluxes,
  - steam-outlet liquid carryover metric,
  - DPM fate counts if DPM is included in the check.
- Reduce the current steam-phase imbalance if practical, or explicitly classify it as a bounded limitation if it cannot be reduced without leaving the current branch scope.
- Decide whether setup `07` is:
  - acceptable baseline candidate,
  - diagnostic only,
  - or not yet usable.

### Deliverable
- One accepted baseline statement for setup `07`, including:
  - active limitations,
  - what can be claimed,
  - what cannot yet be claimed.

## Phase B | Mesh Verification Of Setup 07

### Primary Question
Does the setup `07` conclusion survive mesh refinement?

### Run Family
- `07C` = coarse
- `07M` = medium
- `07F` = fine

### Rules
- Same geometry, BCs, solver family, and DPM settings across the mesh family.
- Mesh is the only major variable.
- Do not introduce new physics here.

### Comparison Metrics
- pressure drop;
- steam-outlet liquid carryover;
- outlet dryness or steam quality proxy;
- steam-phase mass imbalance;
- DPM `escaped`, `trapped`, and `incomplete` fractions if DPM is part of the compared output;
- any separator-flow metric judged important enough to report, such as vortex structure or tangential velocity pattern.

### Decision
- If `medium -> fine` changes are small enough, accept the production mesh.
- If results reverse or move materially with refinement, downgrade the branch and repair the setup before stronger claims are made.

### Deliverable
- A production-mesh decision and a mesh-verification summary for setup `07`.

## Phase C | Baseline DPM Verification

### Primary Question
Can one-way DPM on the accepted setup `07` carrier field produce bounded, interpretable carryover trends?

### DPM Verification Priorities
1. Reduce or bound incomplete tracks before using DPM as strong carryover evidence.
2. Keep one-way DPM first; do not turn on source feedback yet.
3. Use a justified droplet-size sweep rather than a single-size claim.

### Baseline DPM Checks
- test max steps increase such as `50,000 -> 100,000`;
- test step-length tightening if incomplete fractions stay high;
- increase particle count if needed for cleaner fate statistics;
- keep injection location, particle density, and boundary fate rules fixed unless the sensitivity itself is the question.

### Minimum Outputs
- `escaped`;
- `trapped`;
- `incomplete`;
- droplet size;
- scoped efficiency or carryover interpretation, if still justified after incomplete-track review.

### Decision
- If incomplete fractions remain high, keep DPM as a bounded diagnostic rather than final efficiency proof.
- If DPM trends stabilize across reasonable tracking settings, promote DPM to stronger support for the setup `07` baseline.

## Phase D | Validation And Trend Comparison

### Primary Question
How strong is the evidence for setup `07` once it is numerically acceptable?

### Validation Hierarchy
1. same-geometry or closest available operating/test data;
2. design-correlation or analytical anchor;
3. separator CFD literature trend;
4. internal A/B comparison only.

### Candidate Anchors
- `../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
- `../../CFD_wiki/wiki/sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md`
- `../../CFD_wiki/wiki/sources/mubarok-2020-cfd-geothermal-flow-meters.md`
- `../../CFD_wiki/wiki/setups/geothermal-separator-design-screening-2014-overview.md`

### Expected Outcome
- likely claim classes for setup `07` are:
  - `numerically verified baseline`, or
  - `trend supported`.
- `Inferred`: setup `07` should not be called `externally validated` unless a stronger direct comparison target is actually available and matched.

## Phase E | Controlled Physics Escalation From Setup 07

### Rule
Add one realism feature at a time. Each new branch must answer one new physics question without changing several other things at once.

### Recommended Escalation Order
1. DPM tracking cleanup branch
   - goal: reduce or bound incomplete tracks.
2. DPM stochastic/turbulence sensitivity branch
   - goal: check whether DRW or related turbulence dispersion materially changes carryover.
3. Two-way DPM coupling branch
   - goal: test whether droplet loading changes the carrier flow.
   - gate: only after one-way DPM is stable and a physically meaningful droplet mass loading is defined.
4. Wall-fate sensitivity branch
   - goal: compare reflect/trap or other bounded wall assumptions before wall film is introduced.
5. Eulerian wall-film branch
   - goal: test whether wall deposition/drainage materially changes carryover.
   - gate: only after the simpler DPM branches are understood.
6. Re-entrainment or film-stripping branch
   - goal: test whether deposited liquid can re-enter the steam path.
   - gate: only after wall-film deposition/drainage is stable.
7. Transient carrier-flow branch, if still needed
   - goal: test whether steady assumptions are masking important separator behavior.

### Branching Principle
- Every new branch must start from the last accepted simpler branch, not from an already uncertain or mixed-change case.

## Parked Future Work
- Brine outlet reconstruction.
- Lower-water initialization.
- Bottom-liquid pool or drainage behavior studies.
- Full-vessel liquid inventory closure studies.

`User-specified`: these are not abandoned forever, but they are explicitly parked until the main setup `07` path is complete enough that extra exploratory work is justified.

## Immediate Priority
1. Finish setup `07` baseline acceptance checks.
2. Decide whether setup `07` is acceptable as the parent baseline candidate.
3. Run mesh verification only after that acceptance gate is passed.
4. Keep wall film, re-entrainment, and other higher-complexity branches off until the baseline is numerically defensible.
