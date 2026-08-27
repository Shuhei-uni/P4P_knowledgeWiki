> **Legacy source:** ResearchProject_wiki/wiki/progress/experiments.md  
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Raw and machine-generated artifacts remain at their legacy paths.

# Historical run notes

> **Legacy source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run CTP-NBO-2026-05-27
- Run ID: `CTP-NBO-2026-05-27` (`Assumed` setup label until Fluent filename is confirmed)
- Date: 2026-05-27
- Objective: Prepare a complete two-phase full-inlet spiral case with no active brine outlet for a `5000`-iteration diagnostic run.
- Geometry: `purnanto` spiral-inlet BOC separator with one full inlet boundary; brine outlet absent or closed as a wall for this branch.
- Mesh: same current project mesh family unless a new no-brine-outlet mesh export supersedes it; approximately 1.8M nodes from prior user-reported mesh scale remains the working assumption.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherited from the mixed wet-half actual-area setup where applicable: `SIMPLE`, `PRESTO!`, second-order momentum/turbulence schemes, higher-order volume-fraction scheme where available, and hybrid initialization.
- Boundary and initial conditions: one full `Velocity Inlet` at `26.81 m/s`, liquid water volume fraction `0.009328`, steam/vapor volume fraction `0.990672`; calculated full-area inlet flow is liquid `115.59 kg/s`, steam `79.77 kg/s`, total `195.37 kg/s`; steam outlet remains a pressure outlet with steam-dominant backflow; brine outlet inactive.
- Iteration budget: `5000` steady iterations, with recommended saves at `1000`, `3000`, and `5000` iterations.
- Convergence monitors: residuals, global mass imbalance, inlet phase mass flows, steam-outlet steam flow, steam-outlet liquid carryover, liquid-volume-fraction contours, and velocity vectors near the spiral inlet and steam outlet.
- Outcome: `Planned`.
- Evidence-use label: setup calculation only until `5000`-iteration residuals, mass balance, and outlet phase fluxes are checked.
- Hypothesized cause (if non-converged): not yet applicable; main risk is that no active brine outlet may accumulate or carry liquid to the steam outlet, making the run unsuitable for liquid-removal efficiency.
- Next action: create the Fluent case from `../../../Setups/past/archived/05-complete-two-phase-actual-area-no-brine-outlet.md`, confirm the brine outlet is not active, and run the planned checkpoint sequence.
