# Selected run: fresh K9 low pool, SIMPLE/pseudo Off

Reference exact build: PyAnsys/output/full-geometry-drain-resistance/drain-k9-h0p1-scale0p1-20260930T064024Z/manifest.json. Reference outcome: low-start-n1000-receipt.json in that output root. Reuse only the saved N0 configuration/mesh, freshly initialize all fields, prove alpha/pressure/zero velocities match the reference. Cellcount620431, volume27.0630856948m³; original meshSHA2560d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394.

Retain steady implicit VOF/RNG k-epsilon, PRESTO!, compressive volume fraction and second-order momentum/turbulence; implicit bodyforce, full feed27.118m/s through both pure-phase inlets, material densities881.77/5.73kg/m³, viscosities145.96e-6/15.188e-6Pa s, gravity(0,-9.81,0), operatingpressure0 and density5.73. Preserve K9 vent pressure expression P9BrinePressure, backflow fractions and downstream head+0.10m. No changes to surface tension/energy/DPM/EWF/source absence. Initialpool+0.10m with matched hydrostatic pressure and zero velocity.

Numerical delta: SIMPLE, pseudo-time Off; standard active under-relaxation factors all0.3, exactly enumerated in build receipt. Coupled-specific explicit relaxations and global dt disappear from active tree; record algorithm-dependent AMG changes as part of treatment. Keep linear-solver defaults unless an automatic change occurs with scheme selection; no manual tuning. Save/reopen equality and field comparison required.

First and only block N0–1000. Deadline enforced each iteration. Stop on FPE/nonfinite, phase bounds outside[-1e-6,1+1e-6], speed>500m/s, net liquid/vapor rate>10 times feed for20 consecutive iterations, or budget/deadline. Preserve partial endpoints; no diagnosis from an unverified configuration.

Core E1: raw phase/native-mixture mass errors normalized by actual feed, first/last500 summaries and gross/net outlet routing, paired with low-Coupled reference. E2: whole/lower/upper inventory, alpha/pressure/velocity N0/N1000 and x0/z0 sections. E3: every active residual and clipping history. Report material method improvement only if late500 liquid AND mixture mean absolute imbalance each reduce at least50% relative to Coupled reference, absolute closure is reported, and inventory drift/routing do not deteriorate; threshold is diagnostic, not qualification. If metrics conflict, classify mixed/inconclusive. If any full-study gate fails the result remains unqualified.

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



Sources: Fluent2025R2 UG §§27.8.1.2–1.3,27.8.1.7,27.8.2.1.7 support SIMPLE with VOF and recommend steady implicit VOF URFs0.2–0.5: https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html . §37.14 excludes multiphase from segregated Local Time Step, hence pseudo Off: https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_solve_pseudo.html . These support compatibility, not a cure. The closed-domain global-pseudo conservation warning does not establish the cause in this open two-inlet case.

Instrumentation smoke: deliberately interrupt at the first completed iteration, verify actual native N1/idle, callback and native report write, then continue the same fields for the remaining999. This is inside the1000 cap, with no reinitialization or setting changes. Failure to prove instrumentation stops and preserves the partial case.
