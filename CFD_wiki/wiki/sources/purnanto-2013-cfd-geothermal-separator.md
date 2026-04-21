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
- Initialization: Hybrid Initialization ([purnanto-2013], p.6).
- Other assumptions: smooth wall, gravity in -y, fixed water level, gauge/absolute pressure equivalence assumption ([purnanto-2013], p.5).

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

## G) Reproducibility Risk
### Missing Parameter List
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
3. Particle tracking step limit and injection-distribution sensitivity.

## H) Cross-Paper Linkage (Mandatory)
- Closest related prior papers in this wiki: none yet (first ingest).
- Reuse recommendation: use this source as baseline template for geothermal cyclone separator setup extraction.

## Why Numerical Parameters Matter (Paper-Specific)
This paper itself shows why numerics must be captured explicitly: incomplete particles in DPM tracking changed interpretation of separator efficiency, and authors note potential numerical artifacts requiring mesh refinement ([purnanto-2013], p.8). Without exact numerics, reproduction can match geometry but still miss reported trends.
