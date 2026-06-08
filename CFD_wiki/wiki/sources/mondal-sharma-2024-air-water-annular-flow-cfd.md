# Source: CFD Simulation of Upward Air-Water Annular Flow in Vertical Tube (2024)

## Source Metadata
- Source ID: `mondal-2024`
- File: `raw/1-s2.0-S1738573324002365-main.pdf`
- Authors: Anadi Mondal, Subash L. Sharma
- Venue: Nuclear Engineering and Technology 56 (2024) 2881-2892
- Primary tool: ANSYS Fluent 19.2

## One-Page Summary
This paper builds a three-field annular-flow CFD workflow using DPM (gas-core droplets) and Eulerian Wall Film (wall film), with entrainment correlations implemented through UDFs and compared against experimental entrainment-fraction data ([mondal-2024], p.2881-2884, p.2886-2889).

The authors report that Bertodano entrainment correlation performs best for their cases, with entrainment-fraction predictions generally within ±30% of reference experimental data ([mondal-2024], p.2886-2890).

## A) Study Scope
- Objective: predict annular-flow film behavior and entrainment/deposition/entrainment-fraction trends in vertical upflow ([mondal-2024], p.2881-2883).
- Geometry: 9.4 mm tube diameter, annular section around 210D for fully developed outlet condition ([mondal-2024], p.2883).
- Outputs: film thickness, film velocity, film mass flow, entrainment rate, deposition rate, equilibrium entrainment fraction ([mondal-2024], p.2881-2882, p.2888-2889).

## B) Physics and Models
- Flow model: transient, turbulent annular gas-liquid upflow ([mondal-2024], p.2883-2884).
- Turbulence model: SST k-omega ([mondal-2024], p.2883).
- Gas core/droplet model: DPM (Eulerian-Lagrangian) ([mondal-2024], p.2883-2884).
- Liquid film model: Eulerian Wall Film ([mondal-2024], p.2883-2884).
- Entrainment models compared via UDF: Bertodano, Okawa, and Hewitt-Govan style formulations ([mondal-2024], p.2885-2887).

## C) Material and Operating Conditions
- Test envelope from reference data: superficial air velocity about 24-95 m/s; liquid Reynolds numbers 450, 950, 1400; pressure 1.2, 4, and 6 bar ([mondal-2024], Table 1, p.2883).
- Air-water properties and droplet-size assumptions follow cited annular-flow datasets/correlations ([mondal-2024], p.2886-2890).

## D) Boundary and Initial Conditions
- Domain partition: injection zone + annular zone; EWF injection wall used to create inlet film ([mondal-2024], p.2883).
- Outlet metric: entrainment fraction computed from outlet film flow vs inlet total liquid flow ([mondal-2024], Eq. 2, p.2883).
- Full tabulation of every BC primitive value and initialization field is `Missing`.

## E) Mesh and Numerics
- Mesh: multi-block hexahedral, wall-refined ([mondal-2024], p.2883).
- Mesh study reported across three meshes; EF sensitivity used for adequacy check ([mondal-2024], p.2886-2887).
- Solver mode: transient coupled solution, with DPM + EWF coupling ([mondal-2024], p.2883-2884).

## F) Validation and Results
- Best-performing entrainment model in tested set: Bertodano correlation in this framework ([mondal-2024], p.2886-2887, p.2890).
- Model reproduces EF trends with many cases within ±30% versus experimental data ([mondal-2024], p.2889-2890).
- Higher gas velocity increases entrainment and mean film velocity while reducing film thickness ([mondal-2024], p.2888-2889).

## G) Reproducibility Risk
### Missing Parameter List
- Detailed time-step table and run-time convergence policy are incomplete.
- Exact droplet injection spectra and parcel controls across all cases are not fully specified.
- Full turbulence near-wall controls are not exhaustively tabulated.

### Assumptions Used in This Wiki
- Assume spherical droplets with representative diameter correlations as configured by authors (`Inferred`, `Medium Risk`).
- Assume outlet at 210D is sufficient for equilibrium for similar operating windows (`Inferred`, `Medium Risk`).

### Confidence Rating
`Medium` for workflow transfer; `Medium-High` for qualitative trend replication.

### Minimal Sensitivity Tests
1. Droplet-size distribution sensitivity.
2. Entrainment-correlation swap (Bertodano vs Okawa vs Hewitt-Govan).
3. Mesh and time-step sensitivity near equilibrium outlet section.

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages:
  - [skoog-2020-annular-flow-three-field-cfd-thesis](skoog-2020-annular-flow-three-field-cfd-thesis.md)
  - [mubarok-2020-cfd-geothermal-flow-meters](mubarok-2020-cfd-geothermal-flow-meters.md)
- Relations:
  - `supports`: supports three-field annular CFD decomposition for two-phase risk metrics.
  - `extends`: extends prior model-building by broader entrainment-correlation benchmarking.
- Reuse recommendation:
  - Copy for annular-flow safety/entrainment studies; adapt only after local calibration data exists.
