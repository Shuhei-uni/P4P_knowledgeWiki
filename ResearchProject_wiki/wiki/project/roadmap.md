# Project Roadmap

## Purpose
Define the project run sequence from the current state of the separator work. This roadmap treats setup `08b` as the past reported parity parent; `08c`, `09c`, `09cV2`, and the complete `010V2` EWF family are past reported diagnostics. Active work is the `09cV3` fine-mist PSD rerun.

The immediate job is:

1. extract the live Purnanto Fluent setup as completely as possible through `PyAnsys`;
2. rebuild a parity-first carrier-field branch with only the intended split-inlet change active;
3. verify and validate that rebuilt branch rather than forcing setup `07` to act as the main baseline;
4. only then add new DPM sensitivities or higher-realism physics one branch at a time.

## Current Starting Point
- Date: `2026-07-24`
- Active setup authority: `../../../Setups/active/index.md`
- Active branch role: `09cV3` is the fine-mist PSD rerun. The reported diagnostic records `08c`, `09cV2`, and the `010V2` family retain the inlet-loading, allocation-control, and isolated EWF-mechanism evidence respectively.
- Current model-family classification for setup `08b`:
  - steady `Mixture` carrier-flow solve;
  - observed Purnanto continuous-phase settings treated as primary authority;
  - split inlet treated as the first deliberate project deviation;
  - `DPM` model settings preserved from extraction where present;
  - injection definition added only after extraction and carrier acceptance;
  - not yet a fully coupled `Mixture + DPM` solve;
  - not yet a wall-film branch;
  - not yet a transient branch.
- Current status: setup `08b` has reported numerical screening results but is not externally validated; `08c`, `09cV2`, and all `010V2` records are past reported diagnostics, while `09cV3` remains active.
- Retained comparison branches:
  - `../../../Setups/past/reported/07-pure-phase-split-actual-area.md` remains comparison-only split-inlet context;
  - `../../../Setups/past/archived/08-purnanto-one-inlet-massflow-recreation.md` remains a useful one-inlet automation/parity scaffold;
  - `../../../Setups/past/archived/09-multiphase-separator-sensitivity-family.md` is parked until a stronger parity-reset parent exists.
- `User-specified`: brine-outlet reconstruction and lower-water initialization are no longer active roadmap items for the main project path.
- `User-specified`: the main project risk is now human setup drift away from the real Purnanto case, so extraction-driven parity recovery takes priority over continuing setup `07` V&V.

## Immediate Next Child Branch After Setup 08b

- Past reported child branch: `../../../Setups/past/reported/08c-purnanto-parity-inlet-velocity-sensitivity.md`
- Branch role: test how inlet loading / inlet velocity changes separator efficiency while keeping the same enthalpy basis used by setup `08b`.
- Interpretation rule:
  - keep inlet **specific enthalpy** fixed across the sweep;
  - vary inlet **mass flow rate** on the same split-inlet areas;
  - treat the resulting change in superficial inlet velocity as the controlled variable of interest.
- Current working endpoint choices:
  - low-end sensitivity point `20.00 m/s` (`User-specified` until source-confirmed);
  - high-end sensitivity point `32.14 m/s` (`Observed` as the live-audit reference velocity).
- Reason:
  - supervisor direction is to test velocity effect next;
  - this keeps the next branch to one main change instead of mixing loading sensitivity with a fresh inlet-state assumption.
- Scope warning:
  - if a later test recalculates phase state from a different inlet enthalpy for each loading point, that should be recorded as a separate enthalpy-sensitivity branch rather than folded silently into setup `08c`.

## Scope Decision
- In scope:
  - live-case extraction and parity checklist creation;
  - setup `08b` continuous-phase rebuild and acceptance;
  - mesh verification on setup `08b`;
  - DPM model reconstruction and controlled injection definition on setup `08b`;
  - validation/trend comparison using the strongest available external anchors.
- Out of scope for the main path:
  - forcing setup `07` through full V&V as if it were already a faithful reconstruction;
  - reviving `FFF-2` as the main roadmap driver;
  - brine-outlet optimization;
  - lower-vessel water initialization;
  - interpreting full-vessel liquid inventory closure as the main success criterion for the next baseline.
- `Inferred`: because the current risk is setup-fidelity error, the acceptance gate must first ask whether the rebuilt branch actually matches the observed Purnanto setup except for the intentional inlet change.
- Whole-domain liquid or mixture imbalance is an accepted consequence of the simplified Purnanto geometry, which has no modelled lower-liquid discharge path; it is not a blocker or acceptance metric for this phase.

## Operating Rules
1. Do not launch a new V&V run until the extracted-versus-rebuilt setup diff is reviewed.
2. Change one major feature at a time: extraction/parity closure, inlet representation, DPM tracking controls, stochastic/turbulence treatment, coupling, wall fate, wall film, or transient behavior.
3. Do not add higher-realism physics to a branch that still has uncertain baseline setup parity.
4. Do not run mesh verification on a setup that still fails its basic parity and solution-acceptance gate.
5. Save a minimum evidence package for every run:
   - case/data file name,
   - extracted settings snapshot or parity checklist version,
   - residual history,
   - pressure-drop monitor or equivalent pressure summary,
   - phase mass-flow report at inlet and steam outlet,
   - steam-outlet liquid carryover metric,
   - DPM escaped count and represented escaped mass at `steamoutlet` if DPM is used,
   - short conclusion: `keep`, `reject`, or `needs follow-up`.
6. Keep claim strength explicit:
   - `diagnostic only`,
   - `parity-closed baseline`,
   - `numerically verified baseline`,
   - `trend supported`,
   - `externally validated`.
7. Brine-outlet and water-initialization work must stay parked unless the parity-reset branch is already complete enough that extra exploratory work is justified.

## Cross-Wiki Method Anchor
- Reusable V&V method authority:
  - `../../CFD_wiki/wiki/synthesis/separator-cfd-verification-and-validation-workflow.md`
- Project-owned V&V report layer:
  - `../vnv/index.md`
- Final project sign-off record:
  - `../vnv/signoff-log.md`
- Automation/extraction authority:
  - `../../PyAnsys/AGENTS.md`
- `Inferred`: this roadmap should name which setup branch is currently trustworthy enough to enter V&V, while `PyAnsys` owns the machine-readable parity/extraction workflow and the CFD wiki owns the reusable V&V method.

## Baseline Acceptance Gate For Setup 08b

### Goal
Before mesh verification or DPM sensitivity work, make setup `08b` acceptable as a parity-reset baseline candidate.

### Required Acceptance Checks
1. The extracted live Purnanto settings tree is captured well enough to distinguish observed settings from guessed ones.
2. The rebuilt continuous-phase branch matches the observed Purnanto setup everywhere except the explicitly documented split-inlet change.
3. Inlet phase fluxes match the intended setup `08b` targets closely enough to treat the inlet as correctly imposed.
4. Steam-outlet phase fluxes flatten enough to support interpretation.
5. Residuals flatten rather than showing uncontrolled drift.
6. Pressure-drop behavior becomes stable enough to compare across future branches.
7. Any remaining unknown DPM injection detail is labeled as a controlled uncertainty rather than silently assumed.

### Acceptance Outcome Labels
- `Parity-closed baseline`:
  - setup `08b` is trusted enough to enter mesh verification and project V&V.
- `Diagnostic only`:
  - setup `08b` still provides useful parity clues, but the rebuild is not strong enough for report-facing baseline claims.
- `Rejected baseline`:
  - setup `08b` still differs too much from the observed Purnanto setup or fails basic solution acceptance.

## Validation Gate Before Physics Escalation
- Do not activate family `09` until setup `08b` has passed:
  - parity closure;
  - basic solution-acceptance checks;
  - mesh verification at the level needed for the report;
  - at least one external or literature/design comparison gate.
- `Inferred`: a case can be numerically verified before it is externally validated, but it should not become the parent of DPM sensitivity work if even the baseline setup parity is still weak.

## Phase A | Extraction And Parity Closure

### Primary Question
Can the live Purnanto Fluent setup be exported and replayed reliably enough that human reconstruction error is no longer the dominant uncertainty?

### Required Work
- Export the live settings tree through `PyAnsys`.
- Build a machine-readable parity checklist for:
  - models,
  - materials,
  - phases,
  - boundary conditions,
  - numerics,
  - `DPM` model settings.
- Compare setup `07`, setup `08`, and the live audit against that checklist.
- Record which settings were missing or drifted in the older manual reconstruction.

### Deliverable
- One parity-diff summary that states what setup `08b` must preserve and what setup `07` got wrong or left uncertain.

## Phase B | Setup 08b Carrier Acceptance And Mesh Verification

### Primary Question
Can the parity-reset split-inlet branch run stably enough to become the project's verified baseline?

### Rules
- Hold the extracted continuous-phase setup fixed.
- Introduce only the split-inlet change required for the project question.
- Keep mesh verification separate from DPM injection reconstruction.

### Comparison Metrics
- pressure drop;
- steam-outlet liquid carryover;
- outlet dryness or steam quality proxy;
- any separator-flow metric judged important enough to report, such as vortex structure or tangential velocity pattern.

### Deliverable
- One production-mesh decision and one accepted/rejected baseline statement for setup `08b`.

## Phase C | DPM Injection Reconstruction On Setup 08b

### Primary Question
Can the DPM layer be rebuilt from extracted evidence and then extended with a justified steam-inlet injection definition?

### DPM Priorities
1. Preserve observed `DPM` model settings from the live case first.
2. Do not pretend the original injection set is known, because the saved case has no active injections.
3. Add steam-side inlet injections as a controlled project layer only after the carrier field is accepted.
4. Use a justified droplet-size sweep rather than a single-size claim.

### Minimum Outputs
- extracted `DPM` model-state summary;
- injection location and definition used;
- `escaped`;
- observed escaped count/mass at `steamoutlet`;
- droplet size;
- scoped carryover interpretation.

### Decision
- If the branch still depends mainly on guessed injection details, keep `DPM` as bounded diagnostic evidence only.
- If the `DPM` behavior stabilizes across reasonable settings, promote it to stronger support for the setup `08b` baseline.

## Phase D | Validation And Trend Comparison

### Primary Question
How strong is the evidence for setup `08b` once parity and numerical acceptance are established?

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
- likely claim classes for setup `08b` are:
  - `parity-closed baseline`,
  - `numerically verified baseline`, or
  - `trend supported`.
- `Inferred`: setup `08b` should not be called `externally validated` unless a stronger direct comparison target is actually available and matched.

## Phase E | Controlled Physics Escalation After Setup 08b

### Rule
Add one realism feature at a time. Each new branch must answer one new physics question without changing several other things at once.

### Recommended Escalation Order
1. DPM stochastic/turbulence sensitivity branch
   - goal: check whether DRW or related turbulence dispersion materially changes carryover.
2. Two-way DPM coupling branch
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

### Future Setup 10/11 Direction

The next wall-film work is recorded in [setup 10](../../../Setups/future/10-wall-film-reentrainment-and-dpm-interaction-plan.md) as independently runnable children rather than a single combined jump. [Setup 11](../../../Setups/future/11-combined-wallfilm-dpm-plan.md) is reserved for combinations after the individual mechanisms are readable.

Recommended order:

1. complete the `08c` low/reference/high inlet-loading cases;
2. prepare and run `09c` as a DPM-only two-way coupling comparison;
3. launch `10a` EWF deposition/drainage, `10b` wall-return sensitivity, and `10c` custom DPM/material sensitivity independently when the long-run window is available, even if their interpretation gate remains open;
4. combine selected stable mechanisms in `11a` EWF + re-entrainment;
5. add the selected `10c` change in `11b` only after `11a` is stable.

`Inferred` from Rizaldy et al. 2016 and the annular-flow EWF-DPM literature: inlet loading/velocity is the lower-cost experiment that should establish whether the wall-film mechanism is likely to matter, while EWF and custom interaction laws require transient balances and additional closure assumptions. The air-water annular-flow correlations are transferable as modelling patterns, not as geothermal validation. Because the long runs are time-limited, diagnostic `10` runs may proceed before all parent evidence is closed, but combined `11` cases require bounded film inventory and conserved returned mass.

## Parked Future Work
- Brine outlet reconstruction.
- Lower-water initialization.
- Bottom-liquid pool or drainage behavior studies.
- Full-vessel liquid inventory closure studies.

`User-specified`: these are not abandoned forever, but they are explicitly parked until the main setup `08b` path is complete enough that extra exploratory work is justified.

## Immediate Priority
1. Build the `PyAnsys` extraction-first parity workflow for the live Purnanto case.
2. Record the settings drift between the live case and setup `07`.
3. Rebuild setup `08b` with only the intended split-inlet change active.
4. Run mesh verification and V&V only after that parity-reset branch is numerically defensible.
