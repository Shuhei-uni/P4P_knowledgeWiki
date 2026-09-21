# Phase 7b S20 — 20% Collector

## Authority and question

Human-approved [CONTEXT](../CONTEXT.md) candidate E1 (H1/H2), case S20,
gate G1. Lifecycle mode: discovery. PHASE_CONTRACT and DISCOVERY_DESIGN
passed independent review in [phase-state.yaml](../phase-state.yaml).
The human selected in-chat loop launch on 2026-09-08.

Test how collector thickness affects liquid delivery, removal, inventory,
conservation and separation above the collector. This is one of five linked
cases, not a hypothesis qualification or physical separator validation.
Prior collisions, competing explanations and the full non-waivable evidence
contract are in [design.md](../design.md), incorporated into this setup.

## Parent and controlled change

Geometry: resolved-outlet 620,431-cell mesh, source SHA-256
`0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`.
[Geometry proof](../geometry-proof.md) establishes the mapped cap and cells.
Build basis: the Python-only clean reference pair
`p7b-clean-initial-20260912T080713Z.cas.h5` / `.dat.h5`, rebuilt from the
verified mesh and reloaded at N0. Each child receives the same fresh Hybrid
Initialization. Historical probe-bearing preparation cases are not parents.
Runtime paths and observed endpoint are exclusively in run-paths.yaml.

Controlled delta: select owned fluid centroids with
`-1.4845837354660034 <= y <= -1.1836669883728028 m`. No x/z crop.
Use the same source/report predicate. The other four cases change only this
upper elevation. Start independently from the common reference each time.

## Fixed physics and boundaries

- Steady, pressure-based, absolute velocity; Mixture, vapour primary/liquid secondary.
- RNG k-epsilon, standard wall functions, differential viscosity and swirl correction on.
- Energy, DPM interaction/injections and EWF off; no interphase mass transfer.
- Constant liquid/vapour density: 881.77 / 5.73 kg/m3; viscosity 145.96e-6 / 15.188e-6 Pa s.
- Liquid dispersed diameter 10 micrometres, Manninen slip, Schiller-Naumann drag; historical Simonin entry reconciled as inapplicable to shared Mixture/RNG (see CONTEXT).
- Both inlet phase velocities 27.118 m/s normal to their face; secondary volume fraction 1 on liquid inlet, 0 on steam inlet.
- Inlet turbulence intensity 0.0211 (2.11%), hydraulic diameters 0.01338 / 0.72061 m.
- Inlet reference pressure 1,140,000 Pa; operating pressure 0 Pa; gravity (0,-9.81,0) m/s2.
- Steam pressure outlet 1,120,000 Pa; liquid backflow fraction0; backflow intensity0.0211 and hydraulic diameter0.876 m.
- Former brine outlet and other walls stationary, no slip, smooth.
- SIMPLE; PRESTO pressure; Green-Gauss node gradients; second-order momentum/k/epsilon, QUICK phase fraction.
- URFs: pressure0.3, momentum0.7, k/epsilon0.8, phase fraction0.4, drift0.1, density/body-force/turbulent-viscosity1.

## Collector implementation contract

Use Python/PyFluent and native expression sources. Corrected phase velocities
use `Velocity.x(phase="phase-2")` (and y/z); shared k/epsilon fields have no
explicit phase context. Diagnostic save/reopen and 50 iterations passed.
The native expression source entries expose no assigned derivative slot;
no exact Jacobian is claimed. Profile update interval is one iteration.

Split the exact selected cells into a collector fluid zone solely to expose
its true boundary faces. Preserve cell/face/node counts and physical settings;
prove zero disagreement between zone membership and the centroid mask.
Record separate applied source (native per-cell source sum) and recomputed
source at current alpha. The applied source was observed to use the prior
iteration field; use the applied source in discrete closure accounting.
Gross delivery/escape uses phase-2 SV_FLUX over verified owned interface faces,
with orientation proved from adjacent-cell geometry and native flux reports.
The synchronous Python iteration callback preserves PC and local records.

`S_l=-chi*rho_l*alpha_l/tau`, `S_g=0`, common `tau=0.0024095893 s`.
Use bounded alpha; no inlet-flow forcing or inventory controller.
Liquid mass sink only on liquid phase; no duplicate mixture mass term.
Mixture momentum source `S_l*u_l`, including phase drift, and shared
turbulence removal `S_l*k`, `S_l*epsilon`. Energy is off.
Document implemented Jacobians and prove phase-velocity access against native
fields at nonzero slip; unallocated storage or mixture-velocity fallback is
not an accepted implementation. Common coefficient is a numerical convention
with the reference-crossing basis in design.md; it does not guarantee capture.

**Build status:** implementation verification pending. No planned screen
solve until source scopes, phase velocity, mask boundary fluxes, persistence
and every required evidence stream pass smoke checks.

## Initialization and run intent

Identical reference Hybrid Initialization for every case:10 hybrid passes,
explicit URFs[1,1], averaged turbulence parameters, no external-aerodynamics
or constant-velocity option, no deliberately patched standing pool. Archive
initial field/inventory; reconcile nonzero pool/different initialization.
After source and instrumentation proof, planned horizon is5,000 steady
iterations. Use a50-iteration instrumented smoke segment followed by4,950
if that segment faithfully uses the final setup and initial state; otherwise
reset from the approved fresh reference and label prior diagnostic work
separately. No case may exceed5,000 scientific-screen iterations.
Poor residuals or disappointing balances are observations, not tuning or
early-stop authority. Fatal/initialization/save/evidence failures block.

Save matching initial, prepared/reopened, recovery and terminal case/data.
Recovery at each500 iterations; retain at least last two plus initial/final.
Server working storage is LOCAL_ONLY until a verified independent copy exists.
No approved OneDrive destination is inferred. Remain attached through discovery.

## Required evidence and figures

Every iteration: whole/collector/above-collector liquid volume and mass;
independent sink integral; individual liquid/vapour/mixture boundary fluxes;
source-inclusive closure reconstructed with the sink counted once; gross
liquid delivery/escape across actual mask boundary without partition duplicates;
steam recovery/liquid carryover; area-weighted static pressure at each inlet
and outlet, each pressure drop, fluid pressure extrema and maximum mixture
speed; native scaled residuals for all active equations. Geometric mask
counts/volumes must match the source. Retain native iteration coordinates.

File-backed reports and residual transcript must write before main solve;
reconnect cannot erase evidence. Neither inventory change per iteration nor
Fluent phase Net may be misused as a second physical source/storage rate.

| Figure | Question and axes | Evidence and comparison |
| --- | --- | --- |
| F1 Inventory/removal | Does coverage change accumulation/removal? N vs volume[m3] and removal[kg/s], separate panels | Raw five-case histories and fixed final-window summaries |
| F2 Conservation/routing | Is apparent capture mass-closed? N vs phase/total closure[% inlet], steam recovery, carryover | Boundary-only fluxes + independently integrated sink once |
| F3 Above-cap fields | Does collection distort upper separation? Liquid fraction and mixture/phase velocities on y=0.5,1.5,3,5m fluid sections | Matching case/data, same planes and colour scales; verify nonempty sections |

All-equation residual plots are required supporting numerical evidence.
Use windows4001-4500 and4501-5000 for mean, extrema, SD, slope and mean change;
label incomplete-case windows separately. Numerical indicators: final-window
mean absolute phase/total closure <=1% respective measured feed, inventory
window-mean change <=1% (denominator floor1e-6m3), all active scaled residuals
<=1e-3 throughout final window. These are screening conventions, not physical
validation or independent continuation permission.

## Return and claim limit

Document Observed/Inferred/Missing Info in results.md and compare all five
dispositions at G1. Missing required evidence is not a pass. Return to human
for further cases, altered physics/source coefficient or longer qualification.
Finite-strength capture, mesh discretization and bounded horizon limit claims.
