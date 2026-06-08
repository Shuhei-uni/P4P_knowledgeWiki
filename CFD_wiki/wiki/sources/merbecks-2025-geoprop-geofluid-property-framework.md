# Source: GeoProp Thermophysical Property Framework for Geothermal Geofluids (2025)

## Source Metadata
- Source ID: `merbecks-2025`
- File: `raw/1-s2.0-S0375650524002323-main.pdf`
- Authors: Tristan Merbecks, Allan M.M. Leal, Paola Bombarda, Paolo Silva, Dario Alfani, Martin O. Saar
- Venue: Geothermics 125 (2025) 103146
- Type: thermophysical/phase-behavior modeling framework

## One-Page Summary
This paper introduces GeoProp, a coupled framework that combines fluid partitioning/chemical-equilibrium solvers with thermophysical property engines to model geothermal geofluids across single- and two-phase regimes ([merbecks-2025], Abstract, p.1-3).

GeoProp is validated against experimental/benchmark datasets for selected fluids and then used to show that geofluid chemistry materially changes heat-content and design-relevant thermal behavior in geothermal systems ([merbecks-2025], p.6-9).

## A) Study Scope
- Objective: close a modeling gap between phase partitioning and property estimation for geothermal geofluids ([merbecks-2025], Abstract, p.1-2).
- Scope: framework architecture, validation against selected references, and case-study demonstration.
- Outputs: density, enthalpy, phase-quality/partition effects and heat-content behavior.

## B) Physics and Models
- Approach: chemically reactive-system equilibrium + thermophysical property coupling ([merbecks-2025], p.3-5).
- Coupled tools: Reaktoro/ThermoFun/CoolProp style integrations in GeoProp ([merbecks-2025], Abstract, p.2-4).
- EOS and activity models are selected by species/system (e.g., real-gas and electrolyte models where needed) ([merbecks-2025], p.3-6).
- Not a CFD momentum/turbulence solver paper.

## C) Material and Operating Conditions
- Focused on geothermal-relevant water-salt-NCG style compositions and wide thermodynamic ranges.
- Demonstrates that non-pure-water geofluids shift phase behavior and effective heat-content curves versus pure-water approximations ([merbecks-2025], p.8-9).

## D) Boundary and Initial Conditions
- Framework input is composition + pressure + temperature + model choices; no CFD BC/IC tables (`Not Applicable` for CFD setup).

## E) Mesh and Numerics
- No CFD mesh/discretization.
- Numerical workflow is thermodynamic equilibrium and property evaluation pipeline.

## F) Validation and Results
- Benchmark comparisons show close agreement for tested brine/property cases and highlight differences between simplified and chemically informed fluid models ([merbecks-2025], p.6-9).
- Case study confirms that property-model fidelity can materially affect geothermal system design calculations ([merbecks-2025], p.8-9).

## G) Reproducibility Risk
### Missing Parameter List
- Full reproducibility depends on exact model selection and database versions.
- Some benchmark reproduction details require code/config from repository.

### Assumptions Used in This Wiki
- Assume framework-level conclusions transfer to geothermal plant predesign workflows (`Assumed`, `Medium Risk`).

### Confidence Rating
`Medium-High` for model-coupling concept and qualitative impact; `Medium` for exact numeric recreation without identical model/database versions.

### Minimal Sensitivity Tests
1. Composition sensitivity (salinity and NCG fractions).
2. EOS/activity-model sensitivity.
3. Propagated impact on ORC heat-exchanger sizing and pinch constraints.

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages:
  - [montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid](montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid.md)
  - [mubarok-2020-cfd-geothermal-flow-meters](mubarok-2020-cfd-geothermal-flow-meters.md)
- Relations:
  - `supports`: supports need for accurate geofluid properties before downstream simulation/design.
  - `extends`: extends modeling stack upstream of CFD/plant design.
- Reuse recommendation:
  - Use as property-layer foundation before separator CFD or binary-plant optimization.
