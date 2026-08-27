> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run PLS-PRO-2026-06-03-A
- Run ID: `PLS-PRO-2026-06-03-A` (`Assumed` report label until the Fluent case filename is confirmed)
- Date: 2026-06-03
- Objective: Record the professional-license baseline flux result for `setup.md` before running quick DPM droplet-size efficiency checks.
- Geometry: `purnanto` spiral-inlet BOC separator with pure liquid / pure steam split inlet using the actual-area setup from `setup.md`.
- Mesh: `1.3M` nodes and `7.6M` cells (`User-reported`).
- Physics model: inferred continuation of the steady pressure-based `Mixture` model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off unless the saved Fluent case shows otherwise.
- Solver settings: professional-license run; detailed residuals, discretization confirmation, and monitor history not yet captured in this log entry.
- Boundary and initial conditions: same nominal pure-phase split as setup `07`; liquid inlet target approximately `116.92 kg/s`, steam inlet target approximately `80.69 kg/s`.
- Iteration budget: not captured.
- Convergence monitors: phase flux report captured for `liquid inlet`, `steam inlet`, and `steam outlet`; bottom liquid handling is intentionally out of scope for this setup.
- Outcome: `Baseline Flux Diagnostic`.
- Key flux result: liquid phase `116.8522661860914 kg/s` at liquid inlet, `0.03663388722044243 kg/s` at steam outlet; steam phase `81.63946888251938 kg/s` at steam inlet, `-86.29342139251109 kg/s` at steam outlet.
- Calculated metrics: if the steam-outlet liquid value is interpreted as carryover magnitude, liquid carryover fraction is `0.03135 %`, implied liquid-removal efficiency is `99.96865 %`, and steam-outlet dryness is `99.95757 %`.
- Evidence-use label: professional-mesh steam-carryover diagnostic. The tiny steam-line liquid carryover is promising for the scoped project metric, but residual/monitor stability and DPM fate counts are still needed before report-quality efficiency evidence.
- DPM material update: DPM particle density was changed to `881.77 kg/m3` to match the water-droplet density used in setup `07`.
- DPM result set: `5 um` -> escaped `74`, trapped `63`, incomplete `63`; `1 um` -> escaped `23`, trapped `64`, incomplete `113`; `10 um` -> escaped `14`, trapped `53`, incomplete `133`; `41 um` -> escaped `0`, trapped `72`, incomplete `128`; `100 um` -> escaped `0`, trapped `86`, incomplete `114`.
- DPM interpretation: per the current project assumption, treat incomplete as effectively trapped for this branch. That gives scoped DPM removal efficiencies of `63.0 %` at `5 um`, `88.5 %` at `1 um`, `93.0 %` at `10 um`, and `100 %` at `41 um` and `100 um`.
- `5 um` sensitivity checks: deterministic `1000`-track run gave escaped `324`, trapped `325`, incomplete `351` (`67.6 %` scoped efficiency); DRW sensitivity gave escaped `288`, trapped `390`, incomplete `322` (`71.2 %`); rotation sensitivity gave escaped `347`, trapped `360`, incomplete `293` (`65.3 %`).
- `5 um` sensitivity interpretation: DRW and rotation still shift escape by only a few percentage points relative to the deterministic baseline and do not overturn the conclusion that fine droplets are only partially removed in this branch.
- Hypothesized cause (if non-converged): the main residual uncertainty is now whether the high incomplete counts truly correspond to wall-stuck particles and whether the updated water-density droplet surrogate is still sensitive to tracking controls, plus approximately `5.70 %` steam-phase imbalance between steam inlet and steam outlet magnitudes.
- Next action: record residual/monitor stability, then optionally increase DPM max steps to `100,000` and rerun at least the `10 um` case to see whether the `93.0 %` removal result holds with fewer incomplete tracks.

### Run PLS-STUDENT-ROUGH-2026-06-01-A
- Run ID: `PLS-STUDENT-ROUGH-2026-06-01-A` (`Assumed` report label until the Fluent case filename is confirmed)
- Date: 2026-06-01
- Objective: Roughly check flux behavior for the pure liquid / pure steam actual-area split using a student-edition mesh and a `2 m` inlet extension before deciding which geometry direction looks more promising.
- Geometry: likely `purnanto` spiral-inlet BOC separator with pure liquid / pure steam split inlet sized from `setup.md`; both inlet legs appear extended upstream in the rough report.
- Mesh: `178k` nodes, `993k` cells, minimum orthogonal quality `0.194`.
- Physics model: inferred continuation of the steady `Mixture`-model separator setup; exact case file settings not fully captured in the report.
- Solver settings: not fully captured; residuals were reported as not converged enough for strong quantitative claims.
- Boundary and initial conditions: pure-phase split sized from the `1600 kJ/kg` actual-area basis; shared velocity `27.118 m/s`; liquid-side area `0.0048896 m2`; steam-side area `0.5192864 m2`.
- Iteration budget: not captured in the rough report.
- Convergence monitors: scaled residuals and phase flux report.
- Outcome: `Diagnostic Only`.
- Key flux result: steam inlet `80.6899 kg/s`, steam outlet `81.3067 kg/s`, liquid inlet `116.9264 kg/s`, liquid through steam outlet `10.6744 kg/s`.
- Calculated metrics: liquid carryover fraction `9.13 %`; implied carryover-based liquid-removal efficiency `90.87 %`; steam-outlet dryness `88.39 %`.
- Evidence-use label: rough student-edition diagnostic only; not valid for final separator efficiency or final setup ranking.
- Hypothesized cause (if non-converged): mesh cap, unresolved inlet behavior, and incomplete convergence likely distort the outlet split.
- Next action: compare against the modified rough geometry case and keep only the direction-of-change signal unless a higher-quality rerun confirms the trend.

### Run PLS-STUDENT-ROUGH-2026-06-01-B
- Run ID: `PLS-STUDENT-ROUGH-2026-06-01-B` (`Assumed` report label until the Fluent case filename is confirmed)
- Date: 2026-06-01
- Objective: Roughly test whether changing the upstream extension arrangement improves the pure-phase split inlet behavior seen in the first student-edition diagnostic case.
- Geometry: spiral-inlet BOC separator with the same pure liquid / pure steam split sizing from `setup.md`; rough report notes that only the steam inlet kept the upstream extension while the liquid inlet was moved closer to the vessel.
- Mesh: `168k` nodes, `937k` cells, minimum orthogonal quality `0.194`.
- Physics model: inferred continuation of the steady `Mixture`-model separator setup; exact case file settings not fully captured in the report.
- Solver settings: rough report notes that the inlet condition was changed from velocity inlet to mass-flow inlet, making this a two-factor comparison rather than a clean one-factor control.
- Boundary and initial conditions: same nominal pure-phase mass split as the prior rough case, but with altered upstream geometry and reported inlet-type change.
- Iteration budget: not captured in the rough report.
- Convergence monitors: scaled residuals and phase flux report.
- Outcome: `Diagnostic Only`.
- Key flux result: steam inlet `80.6900 kg/s`, steam outlet `81.3802 kg/s`, liquid inlet `116.9200 kg/s`, liquid through steam outlet `7.7278 kg/s`.
- Calculated metrics: liquid carryover fraction `6.61 %`; implied carryover-based liquid-removal efficiency `93.39 %`; steam-outlet dryness `91.33 %`.
- Evidence-use label: rough student-edition diagnostic only; useful only as a qualitative comparison against `PLS-STUDENT-ROUGH-2026-06-01-A`.
- Hypothesized cause (if non-converged): the lower carryover trend may reflect the geometry change, the inlet-type change, or both.
- Next action: if this direction is pursued, rerun it as a controlled comparison with the same inlet boundary type as Setup 1 so the geometry effect can be isolated cleanly.

### Run PLS-ACTUAL-AREA-HD-2026-05-28
- Run ID: `PLS-ACTUAL-AREA-HD-2026-05-28` (`Assumed` setup label until Fluent filename is confirmed)
- Date: 2026-05-28
- Objective: Define the active pure liquid / pure steam split-inlet setup using current-area exact-mass velocity and phase-zone hydraulic diameters.
- Geometry: spiral-inlet BOC separator with rectangular `0.724 m x 0.724 m` inlet split into liquid-side width `0.006754 m` and steam-side width `0.717246 m`.
- Mesh: same current project mesh family unless superseded; key pre-run check is resolving the `6.754 mm` liquid strip.
- Physics model: steady pressure-based `Mixture` model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherit from `../purnanto-04-mixed-wet-half-actual-area/setup.md` unless separately changed.
- Boundary and initial conditions: `inlet_liquid_outer` velocity inlet at `27.118 m/s`, liquid VF `1.0`, turbulence intensity `2.10999999 %`, hydraulic diameter `0.01338 m`; `inlet_steam_inner` velocity inlet at `27.118 m/s`, liquid VF `0.0`, turbulence intensity `2.10999999 %`, hydraulic diameter `0.72061 m`.
- Iteration budget: pending Fluent run plan.
- Convergence monitors: residuals, inlet phase fluxes, outlet phase fluxes, liquid-volume-fraction contours, velocity vectors, and near-inlet turbulence quantities if available.
- Outcome: `Setup Defined`.
- Evidence-use label: setup definition only until Fluent run results are available.
- Hypothesized cause (if non-converged): likely risks are under-resolved liquid strip, sharp pure-phase inlet discontinuity, or turbulence-length-scale sensitivity from the small liquid-side hydraulic diameter.
- Next action: create the two named inlet faces, apply the report settings, initialize, and verify inlet fluxes before running long iterations.

### Run PTS-FV-2026-05-28
- Run ID: `PTS-FV-2026-05-28` (`Assumed` setup-calculation label; not a Fluent solve)
- Date: 2026-05-28
- Objective: Create a pure-liquid/pure-steam split-inlet setup that preserves Purnanto's reported spiral-inlet velocity `26.81 m/s` for the `1600 kJ/kg` case using the current `0.724 m x 0.724 m` inlet.
- Geometry: spiral-inlet BOC separator inlet face, treated as a rectangular `0.724 m x 0.724 m` face split along `x`.
- Mesh: not run; immediate mesh risk is resolving a `6.754 mm` liquid-side strip.
- Physics model: setup calculation for later steady pressure-based `Mixture` model run; primary phase steam/vapor, secondary phase liquid water.
- Solver settings: not run.
- Boundary and initial conditions: `inlet_liquid_outer` velocity inlet at `26.81 m/s`, liquid VF `1.0`; `inlet_steam_inner` velocity inlet at `26.81 m/s`, liquid VF `0.0`; liquid-side width `0.006754 m`; steam-side width `0.717246 m`.
- Iteration budget: not applicable.
- Convergence monitors: not applicable.
- Outcome: `Setup Calculation Only`.
- Evidence-use label: valid for boundary setup. Expected inlet flows are liquid `115.59 kg/s`, steam `79.77 kg/s`, total `195.37 kg/s`, which is `1.14 %` below Purnanto's `197.61 kg/s` target because the current inlet area is smaller than the area implied by `26.81 m/s`.
- Hypothesized cause (if non-converged): not applicable; main pre-run risks are wrong physical side mapping and under-resolved narrow liquid strip.
- Next action: create the two named inlet faces from the historical purnanto-06 pure-phase fixed-velocity setup, then verify Fluent flux reports before interpreting outlet behavior.

### Run PTS-AREA-2026-05-28
- Run ID: `PTS-AREA-2026-05-28` (`Assumed` setup-calculation label; not a Fluent solve)
- Date: 2026-05-28
- Objective: Calculate the inlet split for a pure-liquid/pure-steam two-zone velocity inlet that preserves Purnanto's `1600 kJ/kg` phase mass-flow targets using the current `0.724 m x 0.724 m` inlet area.
- Geometry: spiral-inlet BOC separator inlet face, treated as a rectangular `0.724 m x 0.724 m` area for the split calculation.
- Mesh: not run; immediate mesh risk is whether a `6.754 mm` liquid-side strip can be resolved cleanly.
- Physics model: setup calculation for later steady pressure-based `Mixture` model run; primary phase steam/vapor, secondary phase liquid water.
- Solver settings: not run.
- Boundary and initial conditions: future pure liquid inlet uses liquid VF `1.0`; future pure steam inlet uses liquid VF `0.0`; shared velocity `27.118 m/s`; calculated liquid area `0.0048896 m2`, steam area `0.5192864 m2`, split line `0.006754 m` from the liquid-side edge if split along `x`.
- Iteration budget: not applicable.
- Convergence monitors: not applicable.
- Outcome: `Setup Calculation Only`.
- Evidence-use label: valid for boundary-area setup; not valid as separator performance evidence until a Fluent run is completed.
- Hypothesized cause (if non-converged): not applicable; main pre-run risk is under-resolving the narrow liquid strip or mapping the liquid side to the wrong physical edge.
- Current decision: selected as the active next pure-phase split setup over the fixed-velocity `26.81 m/s` alternate.
- Next action: confirm the outer-wall liquid edge in CAD/meshing, create two named inlet zones with the calculated split, set both inlets to `27.118 m/s`, and verify inlet phase mass-flow reports before judging outlet behavior.
