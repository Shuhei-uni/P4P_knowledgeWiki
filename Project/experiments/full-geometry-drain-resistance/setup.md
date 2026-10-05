# Selected first block — full-geometry fixed K=9

Retain the physical and numerical contract in CONTEXT.md. Reuse the saved verified Phase 9 low-pool scale-0.1 N0 setup as configuration, explicitly reinitialize every field using centroid binary phase patch and matching modified hydrostatic pressure. Mesh identity: 620431 cells, volume 27.0630856948 m³; reference mesh SHA256 0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394. Initial h=+0.10m, zero velocity; later independent h=+0.30m. Both are coordinates, not depths above floor.

Brine outlet-vent mixture momentum: K=9, ambient gauge pressure expression P9BrinePressure = 1120000 Pa + (881.77-5.73) kg/m³ *9.81 m/s²*(0.10m-y); operating pressure 0, density5.73. Backflow static-pressure specification, direction from neighboring cell and phase2 backflow fraction1; steam backflow phase2 fraction0. Read back exact live tree and pressure expression; preserve turbulence settings. The loss applies per Fluent mixture boundary convention, not a phase-selective liquid-only drain. Readback/save-reopen and fresh field identity are required before solve.

Initial block exactly1000 iterations; callback captures native progress, gross/net phase/mixture face fluxes and finite/bounds/speed/deadline guards every iteration. Native reports and residual transcript each iteration. N0/N1000 full-cell fields and axial sections support spatial/inventory checks; preserve case/data on Fluent local disk. Source identifiers P9 in expressions/reports are implementation names only; their reuse does not reopen Phase9.

Acceptance window final1000 with half-window comparison. At first gate compare last500 to first500 plus endpoint spatial/inventory evidence. Stop this trajectory if liquid inventory falls >1% in each half and final500 mean absolute liquid imbalance exceeds1% with failed routing; also stop sustained worsening in closure/residuals despite the budget. Improvement alone never qualifies. The planner may select the independent second start inside scope; no automatic batch extension.

Predeclared simultaneous gates (numerical study tolerances, not plant specs):

- Each phase mean absolute imbalance ≤0.5% of its actual feed, maximum ≤1%;
  native mixture similarly normalized by total feed. Sum phase ledgers and
  compare with native mixture; discrepancies >0.1% total feed require audit.
- Total and lower-region liquid inventory range ≤1% of window mean; change
  between half-window means ≤0.25%. No systematic increasing/decreasing tail.
  Report above-pool inventory separately; liquid must not merely migrate there.
- Connected pool interface and occupancy profiles stable between snapshots;
  representative interface-height change ≤0.02 m or one local vertical cell
  spacing, whichever is larger, with mesh dependence explicitly reported.
- ≥99% of liquid feed leaves through brine and ≥99% of vapor feed through steam;
  each outlet's reverse phase inflow <0.1% corresponding inlet feed in the
  acceptance window. Boundary backflow cannot offset a spurious overdrain.
- Every active scaled flow/turbulence/VOF residual ≤1e-3 throughout the final
  window; preserve oscillations and any native residual normalization. No
  persistent clipping, limit saturation, divergence or nonfinite fields.
- Both independent starts meet all gates and agree in liquid inventory within
  1%, mean outlet phase fluxes within 0.5% of feed and pressure drop within 2%.
  Same model/order/BCs and actual full feed required. Repeat persistence gates
  after save/reopen before any stationary-solution claim.

Stop an individual run on solver FPE/nonfinite data, loss of valid mesh/phase
bounds, maximum speed >500 m/s, or |phase boundary net| >10× phase feed sustained
for 20 iterations. Preserve evidence; no numerical-settings contrast is allowed; technical recovery may resume only a preserved equivalent state
inside the total budget. At batch gates stop sustained worsening rather than
consume the budget blindly. Record why the comparison is incomplete.


Artifacts: exact build and run manifests; per-iteration native histories and gross/net face evidence; residual coverage; N0 and terminal full fields; axial sections; saved native case/data. Independently reduce inventory and boundary flux. Analysis must separate observation, interpretation, missing evidence. Single-block or single-start success is not qualification.

Version evidence: Fluent 2025 R2 UG §27.2.11.3.1 Table27.4 lists outlet-vent VOF compatibility and secondary-phase backflow fractions; §8.4.12 describes bidirectional normal-velocity pressure loss and imported pressure-outlet specification. [Boundary conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_bound_cond.html), [multiphase setup](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html). Exact face-density interpolation remains undocumented here; do not claim a phase-specific valve law.

## Selected second start

Following low-start failure, select fresh h_i=+0.30m for exactly1000 iterations with unchanged physical/numerical settings. Preserve low N1000 pair before replacement. Use same gate evidence and deterministic stop limits. No automatic extension. A repeated failure closes the tested fixed-K/head route; stronger high-start behavior requires scientific review and still cannot establish initial-condition independence.
