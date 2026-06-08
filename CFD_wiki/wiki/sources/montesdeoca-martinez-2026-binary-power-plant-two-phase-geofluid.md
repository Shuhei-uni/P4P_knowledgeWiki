# Source: Techno-Economic Binary Power Plant Design for Two-Phase Geothermal Fluids (2026)

## Source Metadata
- Source ID: `montesdeoca-2026`
- File: `raw/1-s2.0-S0196890426000191-main.pdf`
- Authors: Fernando Montesdeoca-Martinez, Sergio Velazquez-Medina, Stefan Kranz
- Venue: Energy Conversion and Management 351 (2026) 121050
- Type: techno-economic system modeling (not a CFD paper)

## One-Page Summary
This paper proposes and optimizes a binary geothermal plant layout for two-phase wellhead resources, including an additional evaporator that condenses separated steam and improves cycle heat recovery ([montesdeoca-2026], p.1-4).

Compared to reference single-flash and flash-binary configurations under equal resource conditions, the proposed configuration reports higher specific power output and competitive CAPEX behavior ([montesdeoca-2026], Abstract, p.13-14).

## A) Study Scope
- Objective: optimize two-phase geothermal binary-plant concept and quantify techno-economic performance ([montesdeoca-2026], p.2-4).
- Scope: separator + ORC process integration, parametric optimization, and economic comparison.
- Outputs: net power, specific power output, efficiency and CAPEX metrics.

## B) Physics and Models
- Core models: thermodynamic process and component models in EES; not a CFD Navier-Stokes workflow (`Reported`).
- Cycle elements: separator, dual evaporators, preheater, recuperator, condenser, dry-cooling loop ([montesdeoca-2026], p.3-4).
- Working fluids evaluated: n-pentane, isopentane, n-butane ([montesdeoca-2026], Abstract, p.2-3).

## C) Material and Operating Conditions
- Reported best case (from abstract): n-pentane, turbine inlet temperature 175 C, wellhead pressure 13 bar, dry-cooler approach 16 K ([montesdeoca-2026], Abstract).
- Geothermal case study context: high-temperature, liquid-dominated resource.

## D) Boundary and Initial Conditions
- System-level boundary conditions are process design variables (wellhead pressure, TIT, pinch-point, approach temperatures), not CFD BCs ([montesdeoca-2026], p.3-4).
- Field-calibrated multiphase pipeline BC tables are not provided (`Missing` for CFD-style replication).

## E) Mesh and Numerics
- No CFD mesh or discretization stack (not applicable).
- Numerical optimization: parametric and optimization routines in EES context ([montesdeoca-2026], p.4+).

## F) Validation and Results
- Reported maximum net power in tested envelope: 13.59 MW in stated optimal condition ([montesdeoca-2026], Abstract).
- Comparative results indicate significantly better specific power vs single-flash and meaningful gain vs flash-binary with lower CAPEX vs flash-binary reference in their scenario ([montesdeoca-2026], Abstract, conclusions).

## G) Reproducibility Risk
### Missing Parameter List
- Full component-level sizing constants and all assumed cost factors are spread across full manuscript.
- Reservoir productivity and uncertainty assumptions are scenario-dependent.

### Assumptions Used in This Wiki
- Treat as process-integration evidence for two-phase resource utilization, not CFD solver guidance (`Assumed`, `Low Risk`).

### Confidence Rating
`Medium-High` for comparative system insights within modeled scenario; `Low` for direct separator CFD reconstruction.

### Minimal Sensitivity Tests
1. Re-run with local cost index and financing assumptions.
2. Sweep resource chemistry and NCG uncertainty.
3. Check off-design operation sensitivity for ambient temperature.

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages:
  - [merbecks-2025-geoprop-geofluid-property-framework](merbecks-2025-geoprop-geofluid-property-framework.md)
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
- Relations:
  - `extends`: extends separator-centric thinking into whole-plant integration.
  - `supports`: supports the value of accurate two-phase geofluid treatment in design.
- Reuse recommendation:
  - Use this as downstream process-design layer after fluid property and separator behavior are characterized.
