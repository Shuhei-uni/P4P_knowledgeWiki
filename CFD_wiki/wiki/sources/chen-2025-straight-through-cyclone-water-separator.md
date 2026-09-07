# Source: Experimental and Simulation Research on Straight-Through Cyclone Water Separator (2025)

## Source Metadata
- Source ID: `chen-2025`
- File: `raw/Chen et al. (2025), Experimental and Simulation Research on Straight-Through Cyclone Water Separator.pdf`
- Authors: Yihan Chen, Xingjuan Zhang, Chao Wang, Han Yang
- Venue: *Processes* 13 (2025) 3732
- Primary tool: ANSYS Fluent 2024 R1

## One-Page Summary
This paper combines experiments and CFD for a straight-through cyclone water separator used in an aircraft air-cycle-system dehumidification context. The study compares `20 deg`, `30 deg`, and `40 deg` swirl-generator angles, varies air mass flow rate and humidification rate, and evaluates pressure loss plus separation efficiency ([chen-2025], p.1, p.5-8, p.17-18).

The most useful transfer point for this wiki is not the aircraft application itself, but the experiment-backed RSM-DPM separator workflow: transient pressure-based Fluent, RSM turbulence closure, DPM droplets with breakup/coalescence/rough-wall submodels, a reported droplet-size distribution, and explicit grid-independence plus experiment-simulation comparison. The paper reports inlet-pressure agreement within `0.01-2.13%` under dry cases and separator-efficiency deviation of `4.1%` for a representative wet case ([chen-2025], p.14-16).

## A) Study Scope
- Objective: quantify how swirl angle, air mass flow rate, humidification rate, and operating pressure affect cyclone water-separator performance ([chen-2025], p.1-3, p.17-18).
- Geometry: straight-through cyclone water separator with upstream flow-conditioning section, swirl generator, collector, and collector outlet ([chen-2025], p.3-5, p.8).
- Outputs: pressure loss, nondimensional pressure-loss coefficient `K`, separation efficiency, internal pressure field, streamlines, and droplet trajectories ([chen-2025], p.6-8, p.10-17).

## B) Physics and Models
- Flow mode: transient, three-dimensional, compressible-air continuous phase using ideal-gas density (`Reported`) ([chen-2025], p.10).
- Turbulence model: Reynolds Stress Model (`Reported`) ([chen-2025], p.8-10).
- Discrete phase model: Euler-Lagrange DPM for liquid-water droplets (`Reported`) ([chen-2025], p.8-10).
- Enabled DPM submodels:
  - KHRT breakup with default parameters (`Reported`) ([chen-2025], p.9-10).
  - Stochastic Collision / coalescence with default parameters (`Reported`) ([chen-2025], p.9-10).
  - Rough-wall interaction model (`Reported`) ([chen-2025], p.10).
- Model-selection rationale: the paper states that RSM-DPM is a widely used and experimentally credible strategy for rotating gas-liquid separator flows (`Reported`) ([chen-2025], p.2, p.8-9).

## C) Material and Operating Conditions
- Working phases: air + liquid water (`Reported`) ([chen-2025], p.3, p.10).
- Characteristic separator diameter used in Reynolds number definition: `38 mm` (`Reported`) ([chen-2025], p.6).
- Upstream conditioning length retained in CFD model: `15 mm` (`Reported`) ([chen-2025], p.8).
- Experimental air mass-flow range: `100-300 kg/h` (`Reported`) ([chen-2025], p.6).
- Experimental humidification-rate range: `5-15 g/kg` (`Reported`) ([chen-2025], p.6).
- Swirl-generator angles: `20 deg`, `30 deg`, `40 deg` (`Reported`) ([chen-2025], p.5-6).
- Swirl-generator shared geometry except pitch (`Reported`, table formatting partly compressed in PDF):
  - outer diameter `38 mm`
  - central shaft diameter `5 mm`
  - axial length `35 mm`
  - vane count `4`
  - pitches: `43.5 mm` at `20 deg`, `69 mm` at `30 deg`, `100 mm` at `40 deg`
  ([chen-2025], p.5-6)
- Low-pressure validation condition highlighted in the paper:
  - air mass flow rate `200 kg/h`
  - humidification rate `10 g/kg`
  - inlet pressure `98.8 kPa` experimental / `98.3 kPa` simulated
  - outlet pressure `93.8 kPa`
  - pressure loss `5.0 kPa` experimental / `4.5 kPa` simulated
  - separation efficiency `29.2%` experimental / `28.0%` simulated
  ([chen-2025], p.14-15)
- High-pressure sensitivity case: back pressure increased by `600 kPa`, giving simulated pressure loss `0.7 kPa` and separation efficiency `36.6%` (`Reported`) ([chen-2025], p.15-17).

## D) Boundary and Initial Conditions
- CFD boundary-condition values were taken from experiment, but the paper does not provide a full standalone Fluent BC table (`Reported`, `Missing`) ([chen-2025], p.8, p.14-15).
- The outer wall of the water collector and the collector outlet were set as DPM `escape` boundaries, and droplets reaching them are counted as separated (`Reported`) ([chen-2025], p.8).
- Droplet injection type: surface injection from inlet surface (`Reported`) ([chen-2025], p.10).
- Validation setup under dry conditions: outlet pressure matched experiment and inlet pressure was compared against simulation output (`Reported`) ([chen-2025], p.14).
- High-pressure comparison was implemented by increasing pipeline back pressure by `600 kPa` (`Reported`) ([chen-2025], p.15).
- Initialization procedure is `Missing`; the paper does not state initialization method or patched field values.

## E) Mesh and Numerics
- Solver family: three-dimensional pressure-based transient solver (`Reported`) ([chen-2025], p.10).
- Pressure-velocity coupling: SIMPLE (`Reported`) ([chen-2025], p.10).
- Spatial discretization:
  - continuity: Second-Order Upwind
  - all remaining transport equations: First-Order Upwind
  ([chen-2025], p.10)
- Residual target: all scaled residuals below `1e-4` (`Reported`) ([chen-2025], p.10).
- DPM inlet droplet distribution:
  - Rosin-Rammler
  - distribution index `4.5`
  - main diameter `1.5e-5 m`
  - minimum diameter `6e-6 m`
  - maximum diameter `2.5e-5 m`
  (`Reported`) ([chen-2025], p.10)
- Rough-wall calibration values:
  - `Ra = 6.4 um`
  - `Rq = 7.9 um`
  - `Rsm = 75 um`
  (`Reported`) ([chen-2025], p.10)
- Grid-independence study meshes:
  - `0.42M`
  - `4.0M`
  - `7.26M`
  cells (`Reported`) ([chen-2025], p.10-11)
- Selected production mesh: `4,000,181` cells with minimum mesh quality `> 0.2` (`Reported`) ([chen-2025], p.10-11).

## F) Validation and Results
- Dry-case inlet-pressure validation error range: `0.01-2.13%` (`Reported`) ([chen-2025], p.14).
- Representative wet-case separation-efficiency deviation: `4.1%` (`Reported`) ([chen-2025], p.14-15).
- Grid-independence deltas from `4.0M` to `7.26M` mesh:
  - separation efficiency difference `4.23%`
  - pressure-loss difference `0.44%`
  (`Reported`) ([chen-2025], p.10-11)
- Air-mass-flow trend: separation efficiency follows a non-monotonic `rise-fall-rise` behavior rather than a simple monotonic improvement with stronger swirl (`Reported`) ([chen-2025], p.11-13, p.17-18).
- Swirl-angle interpretation:
  - `20 deg` gives stronger initial swirl and earlier low-flow efficiency peak.
  - `40 deg` gives the best overall performance across a wider flow-rate range.
  - Stronger swirl also raises pressure loss and can intensify instability or re-entrainment.
  (`Reported`) ([chen-2025], p.11-13, p.17-18)
- Pressure effect:
  - low pressure creates a stronger high-speed core but worsens gas carry-under and droplet breakup
  - higher pressure makes the flow field more uniform, reduces pressure loss, and improves separation
  (`Reported`) ([chen-2025], p.15-18)

## G) Reproducibility Risk
### Missing Parameter List
- Full Fluent boundary-condition table is not provided.
- Time-step size, time-step count, and iterations per step are not reported.
- Detailed continuous-phase outlet/backflow treatment is not reported.
- Parcel count, stochastic tracking controls beyond named submodels, and drag-law specifics are not tabulated.
- Exact geometry of the full separator body outside the summarized swirl-generator dimensions is incomplete in text-only form.

### Assumptions Used in This Wiki
- Treat the tabulated swirl-generator dimensions as shared geometry with pitch as the only angle-dependent dimension because the PDF table formatting compresses repeated values. Risk: `Low-Medium`.
- Treat the reported `escape` collector surfaces as the practical collection criterion for efficiency accounting. Risk: `Low`.

### Confidence Rating
`Medium-High` for workflow transfer and qualitative trend reuse; `Medium` for exact reconstruction unless the full geometry and transient control details are recovered from figures or supplementary data.

### Minimal Sensitivity Tests
1. Repeat the low-pressure case with one finer mesh near collector/escape surfaces.
2. Test time-step sensitivity because the paper omits transient marching controls.
3. Compare RSM-DPM against a cheaper RNG `k-epsilon` or SST baseline only after matching the low-pressure validation condition.
4. Check whether permanent collector `escape` logic remains valid if wall-film re-entrainment becomes important.

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages in this wiki:
  - [purnanto-2013-cfd-geothermal-separator](purnanto-2013-cfd-geothermal-separator.md)
  - [pointon-2009-geothermal-separator-sizing-cfd-validation](pointon-2009-geothermal-separator-sizing-cfd-validation.md)
  - [straight-through-cyclone-water-separator-rsm-dpm-2025](../setups/straight-through-cyclone-water-separator-rsm-dpm-2025.md)
  - [fluent-separator-efficiency-methods](../synthesis/fluent-separator-efficiency-methods.md)
- Relations:
  - `supports`: supports RSM-DPM as a defensible separator workflow when strong swirl and droplet fate matter.
  - `extends`: extends separator-efficiency methodology with experiment-backed droplet-size distribution, breakup/coalescence, and rough-wall modelling.
  - `contradicts`: contradicts any simplistic assumption that stronger swirl always improves separation; the flow-rate window matters.
  - `reuses`: reuses cyclone-style DPM collection accounting in a modern Fluent stack.
- Reuse recommendation: copy the validation discipline, droplet-distribution structure, and RSM-DPM logic for separator sensitivity studies, but do not copy the air-water operating values directly into geothermal work without relabeling them as analogy only.
