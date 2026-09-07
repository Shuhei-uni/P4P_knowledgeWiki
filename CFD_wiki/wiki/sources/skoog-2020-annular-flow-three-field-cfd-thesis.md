# Source: CFD Annular Flow Modelling Based on a Three-Field Approach (2020 Thesis)

## Source Metadata
- Source ID: `skoog-2020`
- File: `raw/FULLTEXT02.pdf`
- Author: Erik Skoog
- Institution: Lulea University of Technology (Master thesis)
- Industrial context: Westinghouse BWR annular-flow modeling workflow
- Primary tool: ANSYS Fluent

## One-Page Summary
This thesis continues prior annular-flow CFD work and implements a three-field framework (steam core, wall film, droplets) in Fluent using EWF + DPM, with entrainment modeled via Okawa-style correlation and deposition from Lagrangian droplet tracking ([skoog-2020], Abstract, p.7-12).

The work focuses on improving automation, numerical robustness, and agreement with empirical/experimental trend lines, including adding entrained-droplet transverse velocity to improve model behavior ([skoog-2020], Abstract, p.19-25, Appendix B).

## A) Study Scope
- Objective: support BWR annular-flow prediction in transition to higher-fidelity CFD tools from 1D correlations ([skoog-2020], p.7-8).
- Geometry simplification: cylindrical pipe approximation of rod-subchannel annular section ([skoog-2020], Abstract, p.13-15).
- Outputs: film mass flow, droplet mass flow, deposition/entrainment balance, and sensitivity to inlet split assumptions ([skoog-2020], p.20-25).

## B) Physics and Models
- Three fields: vapor core, liquid film, liquid droplets ([skoog-2020], p.7-11).
- DPM: Lagrangian droplet tracking for deposition behavior ([skoog-2020], p.10-12, Appendix B).
- EWF: wall film transport and source coupling ([skoog-2020], p.11-12, Appendix B).
- Entrainment model: Okawa-based correlation implementation through UDF ([skoog-2020], p.11-12, Appendix A/B).

## C) Material and Operating Conditions
- Simulated representative mass flux cases include approximately 750, 1250, and 1750 kg/m^2/s for comparison studies ([skoog-2020], figure list p.3-4, results p.20-24).
- Steam quality targets and onset allocation are varied for sensitivity analyses ([skoog-2020], p.22-25).

## D) Boundary and Initial Conditions
- Onset of annular-flow initialization uses Wallis transition criterion in the setup logic ([skoog-2020], p.8-9, Appendix A).
- Entrained droplets injected from interface with user-defined sources/velocities; transverse-velocity variants tested ([skoog-2020], Abstract, Appendix B).
- Complete canonical BC table for all runs is partially `Missing`.

## E) Mesh and Numerics
- 3D mesh with cross-sectional resolution documented (example around 1300 cells in sectioned view) ([skoog-2020], figure list p.3).
- Uses Fluent UDF-based coupling for film mass/momentum sources and entrainment injections (Appendix B).
- Full convergence thresholds and all solver control values are not centralized in one table (`Missing`).

## F) Validation and Results
- Model trends are compared against empirical correlations and experimental references; transverse droplet velocity improves correlation with target behavior ([skoog-2020], Abstract, p.25-27).
- Sensitivity to droplet/film split at annular onset is explicitly demonstrated ([skoog-2020], p.22-25).

## G) Reproducibility Risk
### Missing Parameter List
- Not all numerical controls are consolidated in thesis main text.
- Detailed parcel-count controls and statistical sampling windows are incomplete.
- Local turbulence modeling options beyond baseline are not exhaustively compared.

### Assumptions Used in This Wiki
- Assume cylindrical surrogate geometry captures first-order annular behavior for calibration phase (`Assumed`, `Medium Risk`).
- Assume Okawa entrainment framework remains acceptable within tested mass-flux window (`Assumed`, `Medium Risk`).

### Confidence Rating
`Medium` for reproducibility and trend replication.

### Minimal Sensitivity Tests
1. Transverse droplet velocity sweep.
2. Droplet diameter and parcel-rate sensitivity.
3. Onset split sensitivity (film vs droplet initial partition).

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages:
  - [mondal-sharma-2024-air-water-annular-flow-cfd](mondal-sharma-2024-air-water-annular-flow-cfd.md)
  - [purnanto-2013-cfd-geothermal-separator](purnanto-2013-cfd-geothermal-separator.md)
- Relations:
  - `extends`: extends three-field annular modeling implementation detail (UDF-level).
  - `reuses`: reuses entrainment/deposition decomposition logic used in broader two-phase CFD practice.
- Reuse recommendation:
  - Use as implementation playbook when building Fluent three-field annular models with custom UDF control.
