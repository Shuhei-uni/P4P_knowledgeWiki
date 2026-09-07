# Setup: Three-Field Annular Flow UDF Workflow (Fluent Thesis Reproduction, 2020)

## Purpose
Reproduce the `skoog-2020` implementation-level three-field model and compare against Okawa-based trends.

## Source
- Primary: [skoog-2020-annular-flow-three-field-cfd-thesis](../sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)

## Step-by-Step Build Order
1. Build cylindrical annular surrogate geometry and mesh.
2. Enable EWF + DPM and coupled source transfer.
3. Implement UDFs for entrainment, film-source coupling, and injection controls.
4. Set annular onset split (film vs droplet fractions).
5. Run mass-flux cases (around 750, 1250, 1750 kg/m^2/s).
6. Compare deposition/entrainment and three-field mass flows to reference trends.

## Key Inputs
- Mass flux cases include 750, 1250, 1750 kg/m^2/s (`Reported`) ([skoog-2020], p.20-24).
- Entrainment based on Okawa-style formulation (`Reported`) ([skoog-2020], p.11-12, Appendix A/B).
- Transverse droplet velocity option tested (`Reported`) ([skoog-2020], Abstract, Appendix B).

## Missing Info
- Canonical single BC table for all runs.
- Full residual/monitor stopping criteria.
- Exhaustive turbulence-wall model variants.

## Assumptions
- Use tested transverse-velocity correction when baseline underpredicts deposition dynamics (`Assumed`, `Medium Risk`).
- Use outlet equilibrium check as run-completion criterion (`Assumed`, `Medium Risk`).

## Sensitivity Plan
1. Onset split sweep.
2. Transverse velocity factor sweep.
3. Parcel-size/injection-rate sensitivity.

## Common Failure Modes
- Excessive deposition if transverse velocity is over-tuned.
- Nonphysical outlet split due to insufficient sampling window.
- High noise in parcel-driven source terms.

## Quick Diagnostics
- Plot field-wise mass-flow trajectories (film/droplet/vapor).
- Compare deposition curve vs Okawa-style estimate.
- Check if outlet reaches quasi-steady entrainment/deposition balance.
