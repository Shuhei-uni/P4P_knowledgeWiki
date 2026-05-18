# Technical Source Note: Purnanto, Zarrouk, Cater (2013)

## Source
- Source ID: `purnanto-zarrouk-cater-2013`
- File: `CFD_wiki/raw/informit.366967552564856.pdf`
- Citation: Purnanto, M. H., Zarrouk, S. J., and Cater, J. E. (2013). *CFD Modelling of Two-Phase Flow inside Geothermal Steam-Water Separators*.

## Why This Source Matters
This is a key reconstruction reference for legacy Fluent setup choices, including multiphase assumptions, turbulence model selection, boundary-condition style, and particle-tracking method.

## Extracted Technical Setup (Reported)
- Turbulence model used: RNG `k-epsilon` for high-swirl separator flow (`Reported`, `purnanto-zarrouk-cater-2013`, p.1-3).
- Boundary condition style: mass-flow inlet and pressure outlet (`Reported`, `purnanto-zarrouk-cater-2013`, p.5).
- Pressure context: inlet around 11.4 bara and outlet around 11.2 bar (`Reported`, `purnanto-zarrouk-cater-2013`, p.5).
- Solver family: pressure-based solver with SIMPLE pressure-velocity coupling (`Reported`, `purnanto-zarrouk-cater-2013`, p.6).
- Spatial discretization: PRESTO for pressure, second-order upwind for momentum and turbulence quantities, QUICK for volume fraction (`Reported`, `purnanto-zarrouk-cater-2013`, p.6).
- Initialization: Hybrid Initialization (`Reported`, `purnanto-zarrouk-cater-2013`, p.6).
- Meshing approach: unstructured tetrahedral mesh, typical target in the order of millions of nodes, local 1 cm face refinement mention (`Reported`, `purnanto-zarrouk-cater-2013`, p.6).
- Modelling assumptions include incompressible two-phase within separator, inlet mist representation, no flashing, isothermal treatment, smooth walls, and constant water level approximation (`Reported`, `purnanto-zarrouk-cater-2013`, p.5).

## Droplet Tracking Notes (Reported)
- Droplet tracking performed after converged continuous-phase solution.
- DPM-based injection workflow used with Harwell droplet-size estimation.
- Incomplete particles were observed even after increasing step limit, and authors note possible need for mesh refinement.
(`Reported`, `purnanto-zarrouk-cater-2013`, p.8)

## Reconstruction Gap For Current Project
- Earlier team run stalled at 1000 iterations on approximately 300k-node case.
- Current user-reported mesh is approximately 1.8M nodes, which matches the source's order-of-millions scale; the active concern is now quality and worst-cell location.
- Source indicates meshes in the order of millions were preferred for adequate resolution in large vessel geometry.
- Before changing only mesh size, verify full numerics and BC parity with the published baseline.

## Practical Audit Checklist For Next Run
1. Confirm BC type and values match chosen baseline test condition.
2. Confirm solver and discretization stack is exactly defined and recorded.
3. Confirm initialization method and any relaxation/stabilization settings are captured.
4. Check mesh quality metrics and local refinement at high-gradient regions.
5. Run a short controlled test matrix with one variable changed per run.
