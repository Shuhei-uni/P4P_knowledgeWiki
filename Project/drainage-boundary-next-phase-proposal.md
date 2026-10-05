# Proposed direction after Phase 9 — drainage-boundary verification

Status: Andy authorized the initial bounded hydraulic diagnostic on 30 September 2026 ("Sounds good. do that"). Its execution contract is [here](experiments/drainage-boundary-verification/CONTEXT.md). No numbered separator phase or new full-geometry run is selected. Phase 9 is closed unqualified; Phase 7b and all previous endpoints retain their dispositions.

## Recommendation

Keep the intended separator investigation steady and full geometry. First verify a physically explicit drain pressure-loss model in a small steady liquid-only benchmark, then consider one predeclared resistance contrast in full-geometry VOF. Do not fit downstream pressure or resistance to the unconverged N2000 discharge. Do not resume unchanged numerical iteration.

The proposed liquid-only benchmark is a temporary diagnostic simplification: it isolates the boundary's pressure/head/flow behaviour from the difficult VOF interface. It cannot qualify separator performance. A small separate test mesh does not replace or alter the separator geometry. The eventual separator test retains the standing pool already agreed for Phase 9 and remains steady; physical transient is not proposed.

## Verified evidence and unresolved assumptions

The live N2000 geometry audit found brine opening area 0.199362 m² and vertical extent y=-0.506731 to -0.001558 m. Both initial free-surface coordinates +0.10/+0.30 m cover the opening. These coordinates are not pool depths above the vessel floor. Liquid feed 116.921 kg/s at density 881.77 kg/m³ corresponds to 0.132598 m³/s, average liquid-filled opening speed 0.665112 m/s and dynamic pressure 195.036 Pa. These are geometric/algebraic reference values, not a predicted discharge or fitted loss coefficient.

Phase 9 imposes an assumed reservoir level +0.10 m with no calibrated external pipe or valve loss. Internal resolved geometry already has losses: “no external resistance” does not mean frictionless geometry. Version-252 operating-pressure documentation supports the existing modified hydrostatic-pressure convention; no specific sign/gravity error was identified. The failed solution does not prove this boundary caused the failure.

Purnanto (2013), §3.1 p.5 excludes water flow into the bottom brine pipe and assumes a fixed liquid level; §3.3 p.6 gives generic outlet pressure. These do not supply a measured brine downstream pressure, valve law or operating level for the new resolved-outlet model. Actual drain length/diameter/fittings, downstream pressure/elevation and valve/control characteristics remain missing.

## Distinct options

| Option | Value and evidence | Feasibility/cost | Recommendation |
|---|---|---|---|
| More unchanged full-geometry iterations | Little new discrimination after continued inventory loss and worsening residuals | Easy, recurring compute | Reject |
| Verify head/loss boundary, then one resistance contrast | Separates implementation and hydraulic assumptions from interface behaviour | Small steady benchmark first; full CFD only after it passes | Preferred |
| Resolve an actual downstream pipe/valve | Most physical when dimensions and conditions are available | Remeshing and more cells; currently missing inputs | Defer until supported |

## Smallest decisive experiment and bounds

Scientific question: does the declared boundary produce the expected conservative steady head-to-flow relation before it is coupled to the separator? Hypothesis: a passive, independently specified loss relation reproduces known steady hydraulic behaviour without imposing discharge.

Use a fresh separate liquid-only pressure-driven benchmark with documented dimensions and pressure datum. Compare zero additional loss and one declared nonzero loss at two driving heads; account for ordinary domain friction rather than comparing against a boundary-only formula blindly. A simple low-friction domain permits an analytical pressure-loss check. Choose coefficients from real data if supplied; otherwise declare an idealized mechanism test before solving. No parameter may be inferred from an unconverged Phase 9 endpoint. Fluent 2025 R2 documents outlet vents for VOF, spatial pressure profiles through the pressure-outlet specification, and secondary-phase backflow fractions. Prefer this outlet-vent loss relation: it needs no separator CAD change. Exact named-expression/API attachment and saved/reopened readback remain implementation checks; a documented profile route is available. A porous jump would require downstream cells and is not the first choice.

Initial diagnostic budget: at most four small benchmark cases, 2000 total steady iterations or two solver-hours, whichever comes first. Numerical settings, mesh and pressure/loss targets must be fixed in the benchmark setup before execution. Fresh initialization and saved/reopened boundary readback required; Phase 9 data is reference evidence only.

Proposed diagnostic success: inlet/outlet closure within 0.1%, all active residuals <=1e-6, flow and pressure-drop variation <=0.1% over the final 100 iterations, expected monotonic head/flow response, and agreement within 2% with an independent calculation that includes domain loss. If this is not achieved within the cap, stop and diagnose the boundary/benchmark; do not progress to full VOF or retune a coefficient to conceal the discrepancy. These are implementation gates, not separator acceptance.

After this gate, frame the full-geometry candidate with one fixed loss law and two fresh initial levels. Retain Phase 9's conservation, inventory, routing, active-residual, spatial stationarity, initial-condition independence and persistence requirements. Set its separate compute envelope before launch; the initial benchmark authorization must not silently authorize a new full-geometry campaign. Without apparatus data, even a successful full-geometry result would establish only feasibility for the declared idealized drainage system.

## Sources

- [Live geometry and outlet-state audit](../PyAnsys/output/phase09-preflight/downstream-boundary-audit.json)
- [Phase 9 extension evidence](experiments/phase-09-steady-vof-pool/results.md)
- [Historical unresolved drain conditions](experiments/parallel-andy-studies/resolved-brine-outlet.md)
- [Fluent 2025 R2 operating conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_operating.html)
- [Fluent 2025 R2 boundary conditions, outlet vents and porous jumps](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_bound_cond.html)
- [Fluent 2025 R2 multiphase boundary compatibility](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html)
- [Purnanto et al. 2013 primary-paper text](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS)

## Concrete full-geometry follow-on for discussion (not launched)

Readiness update (30 September 2026): the corrected four-control repeat passed terminal analytical, conservation, residual, stability and per-iteration guard checks, with exactly 2000 repeat / 4000 combined diagnostic iterations. The benchmark prerequisite is complete. This verifies only the single-liquid slip-duct implementation, not multiphase separator drainage. The full-geometry follow-on below remains a proposal awaiting scientific-scope agreement; see [diagnostic results](experiments/drainage-boundary-verification/results.md).

If the four hydraulic controls pass, the next mechanism test would retain Phase 9's geometry, full feed, materials, gravity, steady implicit VOF, fixed reservoir h_d=+0.10 m and scale=0.1, and change only the brine boundary to a passive outlet vent with fixed K=9. K=9 is an explicit idealized resistance, not a fitted valve coefficient or a proven suitable setting. A uniform-liquid estimate at the intended brine throughput gives added loss about 1.76 kPa; actual mixed/reversing flow is governed by Fluent's documented mixture boundary treatment and need not follow that estimate. No one-way valve or phase-selective outlet is implied.

Before solves, verify spatial ambient-pressure profile, loss coefficient, operating-density convention and phase-backflow readback, then save/reopen. Build fresh +0.10/+0.30 m initial states from the mesh, not Phase 9 endpoint data. Preserve all existing pairs. No CAD change, controller, sink, phase change or transient. The first new full-geometry run would be a bounded 1000-iteration discovery block. Stop if its terminal evidence still shows sustained inventory depletion and major conservation/routing failure; do not simply spend the remaining cap. If the combined trend justifies more work, allow up to 2000 discovery iterations for each independent start, then up to 1000 save/reopen persistence iterations for each candidate: at most 6000 total solves or 14 solver-hours including retries. Record a fresh deadline before launch. Keep the original simultaneous qualification gates; passing the liquid-only controls cannot relax them.

A favorable result establishes numerical feasibility for this declared idealized drainage model only. A negative result rejects this K/head combination within its finite budget, not every resistance or steady separator model. Any further resistance/head sweep, downstream geometry, feedback controller or transient study requires a separately framed scope.
