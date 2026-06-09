# Source: CFD Modelling of Two-Phase Flow Inside Geothermal Steam-Water Separators (2013)

## Source Metadata
- Source ID: `purnanto-2013`
- File: `raw/informit.366967552564856.pdf`
- Authors: Munggang H. Purnanto, Sadiq J. Zarrouk, John E. Cater
- Venue: IPENZ Transactions, Volume 40 (2013)
- Primary tool: ANSYS Fluent

## One-Page Summary
This paper compares three vertical bottom-outlet cyclone (BOC) separator inlet designs for geothermal steam-water separation and evaluates velocity field, pressure field, and outlet steam quality trends using CFD ([purnanto-2013], p.1-2).

The study uses RANS with RNG k-epsilon turbulence modeling, incompressible/isothermal assumptions, and particle injection for separator efficiency estimation after convergence of the continuous-phase solution ([purnanto-2013], p.1, p.5-6, p.8).

## A) Study Scope
- Objective: assess how geometry and inlet condition changes influence separator performance ([purnanto-2013], p.1-2).
- Cases: Bangma tangential inlet, Lazalde-Crabtree tangential inlet, and spiral-inlet design ([purnanto-2013], p.2, p.6).
- Outputs: velocity profile, pressure distribution, outlet steam quality comparison against empirical reference ([purnanto-2013], p.7-9).

## B) Physics and Models
- Flow assumptions: incompressible, steady-state focus, isothermal, no flashing ([purnanto-2013], p.5).
- Turbulence model: RNG k-epsilon (reported in abstract, methods, and conclusions) ([purnanto-2013], p.1, p.3, p.9).
- Multiphase treatment: text is internally inconsistent.
  - Reported: DPM used for separator efficiency prediction and particle tracking ([purnanto-2013], p.3-4).
  - Reported: mixture model called "most appropriate" for cyclone Stokes number discussion ([purnanto-2013], p.3).
- Practical interpretation (Inferred): likely two-stage workflow: solve continuous field, then DPM injections for carryover estimate.

## C) Material and Operating Conditions
- Two-phase total mass flow: 197.61 kg/s ([purnanto-2013], p.5).
- Base enthalpy: 1600 kJ/kg; swept values include 1440-1760 kJ/kg and one reduced-flow case ([purnanto-2013], p.5).
- Separation pressure: 11.2 bara ([purnanto-2013], p.5).
- Reported fluid properties include liquid/gas density, viscosity, and surface tension at separation condition ([purnanto-2013], p.5).

## D) Boundary and Initial Conditions
- BC types: mass-flow inlet and pressure outlet in final simulation setup ([purnanto-2013], p.6).
- Pressure settings: inlet 11.4 bar, outlet 11.2 bar ([purnanto-2013], p.6).
- Initialization method: Hybrid Initialization ([purnanto-2013], p.6).
- Initialization rationale: authors say Hybrid Initialization was used because the user "did not need to provide additional inputs for initialization" and because it "might improve the convergence robustness for many cases" ([purnanto-2013], p.6).
- Initialization values: Missing. The paper does not report initialized fields for pressure, velocity, turbulence variables, or volume fraction ([purnanto-2013], p.6).
- Other assumptions: smooth wall, gravity in -y, fixed water level, gauge/absolute pressure equivalence assumption ([purnanto-2013], p.5).
- Inlet-state assumptions adjacent to initialization but not equivalent to Fluent field initialization:
  - two-phase inlet is assumed to be mist flow with gas as continuous primary phase and liquid as dispersed secondary phase ([purnanto-2013], p.5).
  - liquid droplets are initially set uniform with average diameter 1e-5 m (10 um) ([purnanto-2013], p.5).
  - steady-state focus, incompressible flow, no flashing, isothermal flow, and constant water level just above brine outlet ([purnanto-2013], p.5).

### Droplet-Size Extraction Note
- Reported: the Harwell equation is used to estimate Sauter mean droplet diameter, and Purnanto states that predicting or measuring the upstream droplet-size distribution entering the separator is almost impossible in this study context ([purnanto-2013], p.3-4).
- Reported: the volume-average/median diameter relation is `x_med = 1.42 x_sa`; the standard pipeline distribution states about `5%` of droplets are `<= 0.3 x_med` and all droplets are `< 2.9 x_med` ([purnanto-2013], p.3-4).
- Inferred: if the reported `10 um` average setup value is treated as Harwell `x_sa`, then `x_med = 14.2 um`, the `5%` lower marker is `4.26 um`, and the upper distribution marker is `41.18 um`.
- Missing: the text says outlet-quality prediction used nine injections with different Harwell-derived droplet diameters, but it does not list the exact nine diameters or their parcel-to-real-mass allocation ([purnanto-2013], p.8).

## E) Mesh and Numerics
- Geometry build: CAD DesignModeler ([purnanto-2013], p.6).
- Mesh: unstructured tetrahedral; "order of millions" nodes; avg element size 5 cm; local faces down to 1 cm ([purnanto-2013], p.6).
- Solver family: pressure-based solver ([purnanto-2013], p.6).
- Pressure-velocity coupling: SIMPLE ([purnanto-2013], p.6).
- Spatial discretization:
  - Gradient: Green-Gauss Node Based
  - Pressure: PRESTO
  - Momentum/turbulent kinetic energy/turbulent dissipation: second-order upwind
  - Volume fraction: QUICK
  ([purnanto-2013], p.6)
- Particle tracking control: maximum Euler time steps reported at 1e5 (tested up to 1e6) ([purnanto-2013], p.8).

## F) Validation and Results
- Velocity and pressure fields are physically plausible for cyclone behavior; geometry-dependent differences are shown ([purnanto-2013], p.7-8).
- Steam quality trends compared against empirical method/data are generally close in magnitude, with some pattern mismatch and unexplained behavior in one spiral-inlet case ([purnanto-2013], p.9).
- Authors explicitly state that further experimental calibration/validation is needed ([purnanto-2013], p.7, p.9).

## Live HDF5 Cross-Check
- The local Fluent 24.2 HDF5 audit in this repo confirms a saved baseline setup with one mass-flow inlet (`80.69 kg/s` vapor, `116.92 kg/s` liquid), one pressure outlet (`1.12e6 Pa`), gravity `(0, -9.81, 0) m/s2`, operating pressure `0 Pa`, and `RNG k-epsilon` / pressure-based / `Mixture` solver settings (`Observed`; see [purnanto-live-setup-reference](../../../ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md)).
- The audited case records `2,964,593` cells, `572,556` nodes, minimum orthogonal quality `0.277635`, and maximum aspect ratio `12.8899` (`Observed`).
- The audited case does not activate DPM injections, so it is best read as a continuous/multiphase baseline snapshot plus solution-warning state rather than a full particle-efficiency run (`Observed`).

## G) Reproducibility Risk
### Missing Parameter List
- Initialized values for all solution variables are not reported.
- Residual target values for convergence are not reported.
- Monitor-based stopping criteria are not reported.
- Under-relaxation factors are not reported.
- Exact mesh counts and mesh quality metrics are not reported.
- Turbulence wall treatment details are not reported.
- Particle injection count/distribution implementation details are incomplete.

### Assumptions Used in This Wiki
- Assumed two-stage solve strategy (continuous field then DPM injections) due mixed wording across sections. Risk: `Medium`.
- Assumed steady-state continuous-phase field for all cases. Risk: `Low`.

### Confidence Rating
`Medium-Low` reproducibility confidence without additional solver-control details.

### Minimal Sensitivity Tests
1. Mesh refinement around inlet, vortex core, and outlet tube.
2. Alternate pressure-velocity coupling/scheme checks (SIMPLE vs SIMPLEC; PRESTO retained).
3. Hybrid Initialization sensitivity versus patched/standard initialization because no initialized field values are reported.
4. Particle tracking step limit and injection-distribution sensitivity.

## H) Cross-Paper Linkage (Mandatory)
- Closest related papers in this wiki:
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
  - [rivas-cruz-2015-geothermal-separator-state-of-art-review](rivas-cruz-2015-geothermal-separator-state-of-art-review.md)
  - [mubarok-2020-cfd-geothermal-flow-meters](mubarok-2020-cfd-geothermal-flow-meters.md)
- Relations:
  - `supported-by`: separator design logic and deployment context are expanded in the 2014/2015 reviews.
  - `extends-to`: two-phase geothermal CFD is extended to metering components in 2020 flow-meter work.
- Reuse recommendation: keep this as the baseline separator CFD extraction sheet and compare all separator variants against it first.

## Why Numerical Parameters Matter (Paper-Specific)
This paper itself shows why numerics must be captured explicitly: incomplete particles in DPM tracking changed interpretation of separator efficiency, and authors note potential numerical artifacts requiring mesh refinement ([purnanto-2013], p.8). Without exact numerics, reproduction can match geometry but still miss reported trends.
