# Selected experiment — two-start steady implicit VOF pool

**Current disposition after the authorized extension:** closed unqualified at N2000 on 30 September 2026. The endpoint is preserved and Fluent is idle. No further solves are selected; supervision ends after this review. See [results](results.md#completed-n10002000-extension-unqualified) for the combined evidence, interruption limits and next scope recommendation. Earlier authorization and closure text below is historical.

**Human-authorized continuation on 30 September 2026:** Andy requested resumption. Continue the preserved h_i=0.30 m, scale-0.1 endpoint from native N1000 to N2000, with unchanged physics and numerical settings. This explicitly extends the prior stopping allowance by one 1000-iteration block, within the original 12000-iteration/48-hour total budget. A four-hour execution guard bounds this block; earlier stop gates remain active. No endpoint is qualified. Phase 9 supervision was subsequently resumed by Andy for this bounded extension and terminal review; see CONTEXT.md and phase-state.yaml. Compare conservation, inventory drift, routing, all active residuals and spatial changes with N1000 before selecting further work. This single-start continuation cannot establish initial-condition independence or physical validity.


## Reference and controlled change

Fresh rebuild from `brine-outlet-620kcells.msh.h5`, reference SHA-256
`0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`,
620,431 cells, volume 27.0630856948 m³. The mesh and audited material/inlet
settings are references; no Phase 7b solution data is a parent. Live identity,
mesh evidence, host paths and build receipts belong in PyAnsys manifests.

Liquid/vapor density 881.77/5.73 kg/m³, viscosity
145.96e-6/15.188e-6 Pa s. Both pure-phase velocity inlets 27.118 m/s;
expected liquid/vapor feeds 116.921233/80.689903 kg/s. Preserve verified
Phase 7b inlet turbulence (2.11%, hydraulic diameters .01338/.72061 m),
RNG k–ε and wall treatment. Gravity (0,-9.81,0) m/s². Steam exit pressure
1,120,000 Pa; operating pressure zero. No energy, DPM, EWF, phase change,
volumetric sinks or inherited expressions controlling physics.

Steady pressure-based, implicit VOF, shared velocity, two constant-density
phases. Surface tension is omitted in this first macroscopic feasibility model;
capillary wetting, breakup and droplet-size predictions are out of scope.
Use supported steady interface reconstruction, PRESTO! pressure, Coupled /
Global Time Step. Use Compressive volume-fraction reconstruction and implicit body force;
start with automatic pseudo-time scale factor 0.3. Read back exact live choices
and all active equations.

## Downstream assumption and initialization

Specify operating density **5.73 kg/m³**, the vapor density, explicitly rather
than a changing phase-average. The gas-reference modified pressure is then
constant at hydrostatic rest. Set the reference pressure location at the steam
outlet elevation (0, 6.261000156, 0) m, so the declared steam datum is explicit. With a numerical downstream liquid level
`h_d = +0.10 m`, prescribe on the vertical brine face:

`p_brine(y) = 1120000 Pa + (881.77-5.73) kg/m³ * 9.81 m/s² * (0.10 m-y)`.

This is an ideal external reservoir, with no calibrated valve/pipe loss. It
sets a downstream head, not a forced in-vessel pool level. Do not use one
constant pressure over the roughly 0.505 m-high liquid exit. No pressure tuning
or flux feedback is selected. Liquid backflow fraction 1 at brine, 0 at steam;
record signed inflow/outflow separately so imported liquid cannot masquerade
as successful drainage.

Two independent starts: `h_i=+0.10 m` and `+0.30 m`. Both submerge the existing
brine opening and stay below the main inlets. For each, zero velocity and a
matched modified-pressure initial field:
`p_i(y)=1120000 Pa + (881.77-5.73)*9.81*max(h_i-y,0)` with SI units.
Use an explicit centroid-selected binary initial patch with reconstructed
interface patching and automatic volumetric smoothing disabled, so the liquid
selection and piecewise pressure initialization use the same height predicate.
The cell-scale stair-step interface is an initialization approximation.
Patch liquid below h_i, vapor above, verify actual selected cells, phase volume,
pressure and velocities. The second start deliberately changes initial head
while retaining the same downstream head. It is not a second equilibrium BC.

A ≤50-iteration zero-feed rest diagnostic at h_i=h_d may check pressure/phase
initialization; it is never a qualified steady VOF separator solution. For this diagnostic, require after 50 iterations: liquid inventory change
≤0.1%, final brine liquid flow magnitude ≤1% of the intended full liquid feed,
and maximum speed ≤0.5 m/s. These are initialization diagnostics, not the
separator acceptance gates. The pressure/interface implementation must be verified before applying feed.
A 29 September v252 manual check (UG §27.8.1.7) confirms Global Time Step
steady multiphase cannot guarantee conservation without distinct active phase
inflows/outflows. Consequently these rest thresholds remain diagnostic flags,
not a prerequisite or rejection gate for the full-feed question. The full-feed
acceptance criteria below are unchanged. Do not try to tune a zero-feed rest
case into a qualified steady separator. Restore full feed and independently
initialize before any counted separator run.
Build save/reopen and report-write smoke proof must precede long compute.

## Horizon, instruments and acceptance

Run in approximately 1,000-iteration batches after the short instrumentation
smoke. The first h_i=0.10 m run uses N0–50 for instrumentation proof, then
N50–1050 for the first long test of approach to balance, conditional on a
finite, preserved smoke endpoint and verified instruments. Subsequent batches
require an evidence review; shorten the last discovery batch to respect the
4,000-iteration ceiling per start. A completed block is not qualification. Assess final 1,000 iterations, using
two 500-iteration halves; qualification adds a save/reopen continuation of at
least 1,000 and up to 2,000. No physical residence time is inferred from
iterations or pseudo-time. Never sum steady iteration fluxes as stored mass.

Record every iteration: all three phase/native-mixture signed boundary ledgers;
liquid and vapor inventory; liquid mass below y=0.5 m and above it; phase flux
at each inlet and outlet; pressure drop; maximum speed; all active scaled
residuals. Archive native transcript and report files. At gates export phase
fraction, pressure and velocity on axial cuts and full-cell phase/volume fields.
Use independently reduced boundary flux and cell inventories at endpoints.

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
for 20 iterations. Preserve evidence; one numerically safer restart is allowed
inside the total budget. At batch gates stop sustained worsening rather than
consume the budget blindly. Record why the comparison is incomplete.

## Evidence products and defensible claims

E1: phase inflow/outflow and native-mixture closure history, raw residuals,
window statistics and independent endpoint ledger — does drainage conserve?

E2: whole/lower/upper inventory history, axial interface snapshots and vertical
occupancy profiles from both starts — stationary pool or hidden accumulation?

E3: two-start and save/reopen comparison table — same equilibrium or dependence
on initialization/numerical history?

Success establishes only a stationary conservative solution of this coarse-grid
steady VOF model under an assumed hydrostatic external reservoir. Failure
rejects this tested setup/budget, not all pool models or the physical separator.

Version-matched pressure/initialization references: [operating pressure](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_operating.html), [multiphase gravity and implicit body force](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html), [expression patching](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_solve_initialize.html).

Rest-diagnostic restriction: [Fluent 2025 R2 UG §27.8.1.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html). This limits the inference from the zero-feed check; it does not establish why any particular velocity or flux error occurs.

## Selected bounded recovery contrast — automatic scale 0.1

After N1050, use the single allowed smaller-pseudo-time restart: 0.3→0.1,
from the exact fresh h_i=0.10 m N0 pair. All physics, outlet pressure, mesh,
initial fields, feed, discretization and acceptance criteria remain fixed.
Fluent v252 UG §37.14 recommends factors such as 0.3 or 0.1 as convergence
aids. This value is selected over a tenfold reduction to retain useful progress
within the overnight budget; it is not a calibrated physical parameter.

Hypothesis: more conservative pseudo-time stepping can improve simultaneous
phase closure, interface/inventory behaviour and residual convergence. Competing
interpretation: the fixed assumed downstream pressure cannot maintain the
liquid seal under the developed operating flow. An unconverged endpoint cannot
prove this boundary explanation.

Verify the child save/reopen and unchanged initial fields, then a 50-iteration
smoke. If bounded and instrumented, continue to N1000 and review against the
original history. At most 2000 iterations for this numerical contrast, within
the overall budget and 07:30 cutoff. Stop at declared safety gates or persistent
worsening at review. A smaller inventory change at equal iteration count is not
success: smaller pseudo-steps slow numerical evolution. No equivalent physical
time or exact iteration conversion is assumed. Qualification still requires
all original gates, the independent second level and persistence. No further
step-size sweep is authorized after this contrast.

Source: [Fluent v252 pseudo-time method](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_solve_pseudo.html).

## Remaining initial-state contrast after recovery N1000

Do not extend the h_i=0.10 m scale-0.1 trajectory: its second 500-iteration
mean liquid imbalance worsened and inventory continued falling. Use the
predeclared independent h_i=0.30 m start with the same scale 0.1 and all physical
settings unchanged, including downstream h_d=0.10 m. Freshly initialize all
fields; do not inherit the depleted endpoint. Test whether greater initial
submergence avoids the same drainage/routing failure. This is the initial-level
contrast already in the phase contract, not another numerical treatment.

Bound this final overnight comparison to N1000 (50 + verified 950). Charge it
conservatively to the remaining 1000 iterations of the 2000-iteration recovery
allowance as well as the phase total. No further numerical recovery iteration
budget remains afterward. Both levels must independently pass unchanged gates
before any common-equilibrium claim; a better high-level endpoint cannot
qualify the failed low-level endpoint. If both remain draining/unqualified,
stop this bounded route and record the uncompleted qualification limits.
