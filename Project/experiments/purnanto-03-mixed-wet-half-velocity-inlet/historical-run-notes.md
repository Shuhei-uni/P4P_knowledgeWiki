> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** These excerpts preserve the historical run-note record; no status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical run notes

> **Retired source:** ResearchProject_wiki/wiki/progress/experiments.md
> **Migration note:** Selected run entries are preserved verbatim as historical project memory; they are not a new status or findings system.

### Run MWH-ACTUAL-AREA-2026-05-27
- Run ID: `MWH-ACTUAL-AREA-2026-05-27` (`Assumed` report label until Fluent filename is confirmed)
- Date: 2026-05-27
- Objective: Start a report-facing record for the mixed wet-half velocity-inlet simulation using the actual inlet-half area from the current geometry.
- Geometry: spiral-inlet BOC separator with split inlet; area interpreted as `2.6209e5 mm2 = 0.26209 m2` for each split inlet half.
- Mesh: same current project mesh family; approximately 1.8M nodes from prior user-reported mesh scale unless superseded by a new mesh export.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherited from mixed wet-half velocity-inlet setup; details pending confirmation from final case file.
- Boundary and initial conditions: `inlet_steam_inner` velocity inlet at `26.81 m/s` with liquid VF `0.0`; `inlet_wet_outer` velocity inlet at `26.81 m/s` with liquid VF `0.018656`; calculated total liquid inlet `115.59 kg/s`, total steam inlet `79.77 kg/s`, and total inlet flow `195.36 kg/s`.
- Iteration budget: pending.
- Convergence monitors: pending.
- Outcome: `Setup Calculation Only`.
- Evidence-use label: inlet boundary-condition documentation only; not yet usable for separator efficiency or final performance claims.
- Hypothesized cause (if non-converged): pending actual solve/post-processing evidence.
- Next action: add mass flux interpretation, outlet phase fluxes, separator efficiency, and key contour/vector findings to `../purnanto-04-mixed-wet-half-actual-area/setup.md` and its linked results report.

### Run FFF-2-OP0
- Run ID: `FFF-2-OP0` (`Assumed` temporary label until Fluent filename is confirmed)
- Date: 2026-05-21
- Objective: Test whether `FFF-2` convergence and liquid mass imbalance improve when the pressure reference matches the Purnanto 2013 convention where gauge and absolute pressures are equivalent.
- Geometry: Same as `FFF-2`; full separator model with brine outlet included.
- Mesh: same as `FFF-2`, approximately 1.8M nodes from current project mesh family.
- Physics model: same as `FFF-2`; steady pressure-based `Mixture` multiphase model, primary phase steam/vapor, secondary phase liquid water, `RNG k-epsilon`, energy off.
- Solver settings: same as `FFF-2` except `Operating Pressure = 0 Pa`.
- Boundary and initial conditions: inlet pressure set to `1140000 Pa`; steam outlet pressure outlet set to `1120000 Pa`; brine/liquid outlet pressure outlet set to `1120000 Pa`; all other inlet, outlet, initialization, and model settings retained from `FFF-2`.
- Iteration budget: preliminary diagnostic run just above 100 steady iterations; extend only if phase flux trends become physically plausible.
- Convergence monitors: residuals reported by user as smooth, non-jumpy, and flattening after just above 100 iterations.
- Outcome: `Partially Improved / Stalled`.
- Key flux result: user-reported Fluent flux order is liquid inlet, liquid outlet, steam inlet, steam outlet. Liquid phase fluxes were `109.8065259020202`, `-1.666485038755287e-194`, `-0`, and `-6.176921748322125e-101 kg/s`, so liquid outlet flow was effectively zero while liquid continued entering the domain. Steam phase fluxes were `37.53446178758816`, `-15.11238833163424`, `37.82770891200012`, and `-61.05984355746033 kg/s`, giving an approximate steam net of `-0.81 kg/s` under the reported sign convention.
- Evidence-use label: diagnostic only. Residual behavior improved compared with original `FFF-2`, but the phase fluxes are not physically balanced because liquid is not yet leaving through either outlet.
- Hypothesized cause (if non-converged): pressure-reference parity may improve numerical residual stability, but the current early solution still has liquid inventory accumulation or delayed/blocked brine outlet drainage; brine outlet pressure sensitivity, outlet placement, liquid residence-time development, or initialization history remain possible contributors.
- Next action: inspect liquid volume fraction near the brine outlet and continue only as a short trend test if the liquid front is moving toward drainage; otherwise classify the pressure-reference parity run as residual-improved but liquid-drainage failed and proceed to a brine outlet control.

### Run FFF-2
- Run ID: `FFF-2`
- Date: unknown; documented before `2026-05-07`
- Objective: Test the mixed wet-half velocity-inlet setup where both inlet halves use `26.81 m/s`, with liquid volume fraction assigned only to the wall-side wet half.
- Geometry: Full separator model with brine outlet included; steam outlet geometry remains a guessed implementation and suspected sensitivity source.
- Mesh: approximately 1.8M nodes from current project mesh family; detailed quality distribution still pending.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: `SIMPLE`, `Green-Gauss Node Based`, `PRESTO!`, second-order momentum/turbulence schemes, higher-order volume-fraction scheme where available; hybrid initialization with no water-pool patch.
- Boundary and initial conditions: `inlet_steam_inner` velocity inlet at `26.81 m/s` with liquid VF `0.0`; `inlet_wet_outer` velocity inlet at `26.81 m/s` with liquid VF `0.018656`; pressure outlets for steam and brine outlets with backflow fractions pending final audit.
- Iteration budget: approximately `1020` steady iterations.
- Convergence monitors: residuals still moving noticeably; mass-flow flux report collected at `1020` iterations.
- Outcome: `Stalled`.
- Key flux result: liquid inlet approximately `109.8065 kg/s`; liquid out through brine outlet approximately `161.0144 kg/s`; liquid out through steam outlet approximately `0.0096 kg/s`; liquid net approximately `-51.2175 kg/s`, so the liquid phase was not balanced.
- Evidence-use label: diagnostic only. This run is above the current `1000`-iteration evidence threshold, but it is not converged and should not be used for final separator efficiency, pressure-drop, or design-comparison claims.
- Hypothesized cause (if non-converged): brine outlet over-removal or continued redistribution of the initialized/hybrid liquid field; outlet backflow setup, brine outlet pressure, and steady dry-start behavior remain possible contributors.
- Next action: retain as the parent diagnostic comparison for `MWH-WP-2026-05-07-A`, but rebuild future design comparisons from a stable reference case.

### Run MWH-WP-2026-05-07-A
- Run ID: `MWH-WP-2026-05-07-A`
- Date: 2026-05-07
- Objective: Test whether initializing a lower water pool improves brine outlet liquid removal for the mixed wet-half velocity-inlet setup.
- Geometry: Full separator model with brine outlet included; steam outlet geometry is a guessed implementation and remains a suspected sensitivity source.
- Mesh: approximately 1.8M nodes from current project mesh family; detailed quality distribution still pending.
- Physics model: steady pressure-based `Mixture` multiphase model; primary phase steam/vapor, secondary phase liquid water; `RNG k-epsilon`; energy off.
- Solver settings: inherited from parent mixed wet-half velocity-inlet setup; pressure-velocity coupling and discretization unchanged from parent.
- Boundary and initial conditions: `inlet_steam_inner` velocity inlet at `26.81 m/s` with liquid VF `0.0`; `inlet_wet_outer` velocity inlet at `26.81 m/s` with liquid VF `0.018656`; steam outlet pressure outlet with backflow liquid VF `0.0`; brine outlet pressure outlet with backflow liquid VF `1.0`; lower water-pool cell register patched to liquid VF `1.0` after hybrid initialization.
- Iteration budget: 3500 steady iterations.
- Convergence monitors: scaled residuals still changing at final iteration, but weak change over the last approximately 1000 iterations; mass-flow flux report collected.
- Outcome: `Partially Converged`.
- Key flux result: liquid inlet `109.8065 kg/s`; liquid out through brine outlet `1413.05 kg/s`; liquid out through steam outlet `1044.35 kg/s`; liquid net approximately `-2347.59 kg/s`, indicating depletion of initialized liquid inventory rather than stable operating balance.
- Evidence-use label: diagnostic only. This is the strongest current qualitative flow-pattern evidence because it reached `3500` iterations, but it is not valid for final quantitative carryover, separator efficiency, or mass-split claims.
- Hypothesized cause (if non-converged): steady solver is draining the patched water inventory; steam outlet geometry/intake flow may be entraining excessive liquid; brine outlet is active but the total liquid mass split is not physically stable.
- Next action: collect liquid-volume-fraction contours, velocity vectors, streamlines/pathlines near steam outlet intake, flux reports at multiple iteration counts, and residual/mass-imbalance history before choosing between transient water-pool test, steam outlet geometry revision, lower water-pool height test, or brine outlet pressure tuning.
